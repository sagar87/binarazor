from math import isnan

import cv2
import numpy as np
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Binarazor", page_icon=":bar_chart:", layout="wide")

from database import get_reviewers
from drive import get_image, get_samples
from handler import (
    decrement_value,
    handle_bad_channel,
    handle_image_controls,
    handle_next_channel,
    handle_next_sample,
    handle_previous_channel,
    handle_previous_sample,
    handle_primary_channel_select,
    handle_sample_select,
    handle_secondary_channel_select,
    handle_slider,
    handle_update_threshold,
    increment_value,
)
from plots import plot_hist, plotly_scatter_gl, plotly_scatter_marker_gl
from utils import format_sample, read_html

# Session state
if "reviewers" not in st.session_state:
    st.session_state.reviewers = get_reviewers()

if "selected_reviewer" not in st.session_state:
    st.session_state.selected_reviewer = st.session_state.reviewers[0]

if "samples" not in st.session_state:
    st.session_state.samples = get_samples()  # pull samples from S3

if "selected_sample" not in st.session_state:
    st.session_state.selected_sample = None

if "selected_sample_index" not in st.session_state:
    st.session_state.selected_sample_index = None

if "data" not in st.session_state:
    st.session_state.data = None

if "images" not in st.session_state:
    st.session_state.images = None

if "channels" not in st.session_state:
    st.session_state.channels = None

if "primary_channel" not in st.session_state:
    st.session_state.primary_channel = None

if "primary_channel_index" not in st.session_state:
    st.session_state.primary_channel_index = None

if "secondary_channel" not in st.session_state:
    st.session_state.secondary_channel = None

if "slider_value" not in st.session_state:
    st.session_state.slider_value = 2.0

if "subsample" not in st.session_state:
    st.session_state.subsample = 5000

if "dotsize" not in st.session_state:
    st.session_state.dotsize = 8

if "image_controls" not in st.session_state:
    st.session_state.image_controls = False

if "downscale_options" not in st.session_state:
    st.session_state.downscale_options = [1, 2, 4, 8, 16]

if "downscale" not in st.session_state:
    st.session_state.downscale = 1

if "lower_quantile" not in st.session_state:
    st.session_state.lower_quantile = 0.03

if "upper_quantile" not in st.session_state:
    st.session_state.upper_quantile = 0.998

if "status" not in st.session_state:
    st.session_state.status = None

with st.container():
    if st.session_state.data is not None and st.session_state.slider_value is not None:
        if st.session_state.status == "not reviewed":
            icon = ":question:"
        elif st.session_state.status == "bad":
            icon = ":x:"
        else:
            icon = ":white_check_mark:"
        st.header(
            f"{format_sample(st.session_state.selected_sample)} | {st.session_state.primary_channel} | {icon}"
        )

        # st.dataframe(st.session_state.data)

        with st.container(border=True):
            channel_index = st.session_state.channels.index(
                st.session_state.primary_channel
            )

            (
                ccol_1,
                ccol_2,
                ccol_3,
                ccol_4,
                ccol_5,
                ccol_6,
                ccol_7,
                ccol_8,
            ) = st.columns(8)

            with ccol_1:
                st.button(
                    "Prev Channel",
                    on_click=handle_previous_channel,
                    disabled=True
                    if (st.session_state.primary_channel_index == 0)
                    else False,
                )

            with ccol_2:
                st.button(
                    "Next Channel",
                    on_click=handle_next_channel,
                    disabled=True
                    if (
                        st.session_state.primary_channel_index
                        == (len(st.session_state.channels) - 1)
                    )
                    else False,
                )

            with ccol_3:
                st.button(
                    "Next graph",
                    on_click=handle_next_sample,
                    disabled=True
                    if st.session_state.selected_sample_index
                    == (len(st.session_state.samples) - 1)
                    else False,
                )

            with ccol_4:
                st.button(
                    "Prev graph",
                    on_click=handle_previous_sample,
                    disabled=True
                    if st.session_state.selected_sample_index == 0
                    else False,
                )

            with ccol_5:
                st.button("Increment value", on_click=increment_value)

            with ccol_6:
                st.button("Decrement value", on_click=decrement_value)

            with ccol_7:
                st.button("Update Threshold", on_click=handle_update_threshold)

            with ccol_8:
                st.button("Mark as bad", on_click=handle_bad_channel)

        with st.container(border=True):
            slider_col1, slider_col2 = st.columns(2)
            with slider_col1:
                slider = st.slider(
                    "Threshold",
                    min_value=0.0,
                    max_value=4.0,
                    value=2.0,
                    step=0.05,
                    key="slider_value",
                )
            with slider_col2:
                if st.session_state.image_controls:
                    img = get_image(
                        st.session_state.images[st.session_state.primary_channel]
                    )
                    # downscale
                    img = np.array(img).astype(np.int32)[
                        :: st.session_state.downscale, :: st.session_state.downscale
                    ]
                    img = img[::-1, :]

                    k_low = f"low_{st.session_state.lower_quantile}_{st.session_state.selected_sample}_{st.session_state.primary_channel}"
                    k_high = f"high_{st.session_state.upper_quantile}_{st.session_state.selected_sample}_{st.session_state.primary_channel}"

                    if k_low in st.session_state:
                        low = st.session_state[k_low]
                        high = st.session_state[k_high]
                    else:
                        low = np.quantile(img, st.session_state.lower_quantile)
                        high = np.quantile(img, st.session_state.upper_quantile)

                    k = "intensity"
                    l, h = st.slider(
                        "Select a values for thresholding",
                        min_value=0.0,
                        max_value=255.0,
                        value=(low, high),
                        step=0.1,
                        key=k,
                        on_change=handle_slider,
                        kwargs={"kl": k_low, "kh": k_high, "new_l": low, "new_h": high},
                        # disabled=st.session_state.image_controls
                    )

        # read in control elements via html
        components.html(read_html(), height=0, width=0)

        with st.container():
            col1, col2, col3 = st.columns([0.4, 0.4, 0.2])

            with col1:
                with st.expander("Raw channel", expanded=True):
                    if st.session_state.image_controls:
                        img = (img - l).clip(min=0)
                        alpha = 255.0 / ((h - l) + 1e-6)
                        st.image(
                            cv2.convertScaleAbs(img, alpha=alpha), use_column_width=True
                        )

                    else:
                        st.image(
                            st.session_state.images[st.session_state.primary_channel],
                            use_column_width=True,
                        )

            with col2:
                with st.expander("spatial_scatter", expanded=True):
                    st.plotly_chart(plotly_scatter_gl(), use_container_width=True)

            with col3:
                with st.expander("spatial_scatter", expanded=True):
                    if st.session_state.secondary_channel is not None:
                        st.plotly_chart(
                            plotly_scatter_marker_gl(), use_container_width=True
                        )

                with st.expander("Histogram", expanded=True):
                    st.plotly_chart(plot_hist(), use_container_width=True)


with st.sidebar:

    reviewer = st.selectbox(
        "Select Reviewer",
        st.session_state.reviewers,
        index=0,
        key="selected_reviewer",
        placeholder="Select a Reviewer...",
    )

    option = st.selectbox(
        "Select Sample",
        st.session_state.samples,
        index=None,
        format_func=format_sample,
        key="selected_sample",
        on_change=handle_sample_select,
        placeholder="Select Sample...",
    )

    st.write(
        "You selected:",
        format_sample(st.session_state.selected_sample)
        if st.session_state.selected_sample is not None
        else st.session_state.selected_sample,
    )

    if st.session_state.data is not None:
        sub_option = st.selectbox(
            "Select Primary channel",
            st.session_state.channels,
            index=0,
            key="primary_channel",
            # format_func=format_graph,
            on_change=handle_primary_channel_select,
            placeholder="Primary Channel",
        )
        sub_option = st.selectbox(
            "Select Secondary channel",
            st.session_state.channels,
            index=0,
            key="secondary_channel",
            # format_func=format_graph,
            on_change=handle_secondary_channel_select,
            placeholder="Secondary Channel",
        )

        st.markdown("""---""")
        st.write("Image Controls")
        st.toggle("Enable image controls", on_change=handle_image_controls)
        st.write("Image controls", st.session_state.image_controls)

        if st.session_state.image_controls:
            downscale = st.radio(
                "Downscale",
                st.session_state.downscale_options,
                index=st.session_state.downscale_options.index(
                    st.session_state.downscale
                ),
                key="downscale",
                horizontal=True,
            )
            st.write("Selected", st.session_state.downscale)
            percentile_col1, percentile_col2 = st.columns(2)
            with percentile_col1:
                _ = st.number_input(
                    "Lower percentile",
                    value=st.session_state.lower_quantile,
                    key="lower_quantile",
                    format="%.3f",
                    max_value=st.session_state.upper_quantile,
                    min_value=0.0,
                    step=0.05,
                )
                st.write(st.session_state.lower_quantile)
            with percentile_col2:
                _ = st.number_input(
                    "Upper percentile",
                    value=st.session_state.upper_quantile,
                    key="upper_quantile",
                    format="%.3f",
                    min_value=st.session_state.lower_quantile,
                    max_value=1.0,
                    step=0.05,
                )
                st.write(st.session_state.upper_quantile)

        st.markdown("""---""")

        number = st.number_input(
            "Subsample Data (for faster plotting, 0 no subsampling)",
            value=st.session_state.subsample,
            key="subsample",
            format="%d",
            min_value=0,
            step=1000,
        )
        st.write(
            f"You are viewing {st.session_state.subsample if st.session_state.subsample != 0 else st.session_state.data.shape[0]} cells."
        )

        number = st.number_input(
            "Dot size (spatial)",
            value=st.session_state.dotsize,
            key="dotsize",
            format="%d",
        )
