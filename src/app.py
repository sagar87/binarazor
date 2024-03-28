import numpy as np
import streamlit as st

st.set_page_config(page_title="Binarazor", page_icon=":bar_chart:", layout="wide")
import streamlit.components.v1 as components
from skimage.measure import regionprops_table

from database import get_reviewers
from handler import (
    decrement_value,
    handle_bad_channel,
    handle_next_channel,
    handle_next_sample,
    handle_previous_channel,
    handle_previous_sample,
    handle_primary_channel_select,
    handle_reviewer_select,
    handle_sample_select,
    handle_secondary_channel_select,
    handle_slider,
    handle_toggle_all_samples,
    handle_update_threshold,
    increment_value,
)
from plots import plot_hist, plotly_scatter_gl, plotly_scatter_marker_gl, strip_plot
from utils import (
    is_positive,
    merge_results,
    normalise_image,
    percentage_positive,
    read_html,
)

# Session state
if "reviewers" not in st.session_state:
    st.session_state.reviewers = get_reviewers()

if "selected_reviewer" not in st.session_state:
    st.session_state.selected_reviewer = None

if "primary_channels" not in st.session_state:
    st.session_state.primary_channels = None

if "primary_channel" not in st.session_state:
    st.session_state.primary_channel = None

if "primary_channel_index" not in st.session_state:
    st.session_state.primary_channel_index = None

if "primary_channel_fixed" not in st.session_state:
    st.session_state.primary_channel_fixed = False

if "show_samples" not in st.session_state:
    st.session_state.show_samples = False

if "samples" not in st.session_state:
    st.session_state.samples = None

if "selected_sample" not in st.session_state:
    st.session_state.selected_sample = None

if "statistics" not in st.session_state:
    st.session_state.statistics = None

if "selected_sample_index" not in st.session_state:
    st.session_state.selected_sample_index = None

if "data" not in st.session_state:
    st.session_state.data = None

if "zarr_dict" not in st.session_state:
    st.session_state.zarr_dict = None

if "zarr" not in st.session_state:
    st.session_state.zarr = None

if "segmentation" not in st.session_state:
    st.session_state.segmentation = None

if "secondary_channels" not in st.session_state:
    st.session_state.secondary_channels = None

if "secondary_channel" not in st.session_state:
    st.session_state.secondary_channel = None

if "slider_value" not in st.session_state:
    st.session_state.slider_value = 0.5

if "stepsize" not in st.session_state:
    st.session_state.stepsize = 0.05

if "subsample" not in st.session_state:
    st.session_state.subsample = 0

if "dotsize_neg" not in st.session_state:
    st.session_state.dotsize_neg = 3
    
if "dotsize_pos" not in st.session_state:
    st.session_state.dotsize_pos = 6

if "lower_quantile" not in st.session_state:
    st.session_state.lower_quantile = 0.990

if "upper_quantile" not in st.session_state:
    st.session_state.upper_quantile = 0.998

if "status" not in st.session_state:
    st.session_state.status = None

if "plot_height" not in st.session_state:
    st.session_state.plot_height = 1000


with st.container(border=False):
    with st.expander("session_state"):
        tcols = st.columns(4)

        for i, var in enumerate(sorted(st.session_state)):
            with tcols[i % 4]:
                st.write(var, st.session_state[var])

with st.container():
    if st.session_state.selected_sample is not None:
        if st.session_state.status == "not reviewed":
            icon = ":question:"
        elif st.session_state.status == "bad":
            icon = ":x:"
        else:
            icon = ":white_check_mark:"
        st.header(
            f"{st.session_state.selected_sample} | {st.session_state.primary_channel} | {icon}"
        )

        # st.dataframe(st.session_state.data)

        with st.container(border=True):
            (
                bcol1,
                bcol2,
                bcol3,
                bcol4,
                bcol5,
                bcol6,
                bcol7,
                bcol8,
            ) = st.columns(8)

            with bcol1:
                st.button(
                    "Prev Channel",
                    on_click=handle_previous_channel,
                    disabled=True
                    if (st.session_state.primary_channel_index == 0)
                    or st.session_state.primary_channel_fixed
                    or not st.session_state.show_samples
                    else False,
                )

            with bcol2:
                st.button(
                    "Next Channel",
                    on_click=handle_next_channel,
                    disabled=True
                    if (
                        st.session_state.primary_channel_index
                        == (len(st.session_state.primary_channels) - 1)
                        or st.session_state.primary_channel_fixed
                        or not st.session_state.show_samples
                    )
                    else False,
                )

            with bcol3:
                st.button(
                    "Next Sample (S)",
                    on_click=handle_next_sample,
                    disabled=True
                    if st.session_state.selected_sample_index
                    == (len(st.session_state.samples) - 1)
                    else False,
                )

            with bcol4:
                st.button(
                    "Prev Sample (W)",
                    on_click=handle_previous_sample,
                    disabled=True
                    if st.session_state.selected_sample_index == 0
                    else False,
                )

            with bcol5:
                st.button("Increment threshold (D)", on_click=increment_value)

            with bcol6:
                st.button("Decrement threshold (A)", on_click=decrement_value)

            with bcol7:
                st.button("Update Threshold", on_click=handle_update_threshold)

            with bcol8:
                st.button("Mark as bad", on_click=handle_bad_channel)

        with st.container(border=True):
            # slider_col1, slider_col2 = st.columns(2)
            # with slider_col1:
            slider = st.slider(
                "Threshold",
                min_value=0.0,
                max_value=1.0,
                step=st.session_state.stepsize,
                key="slider_value",
                disabled=True if st.session_state.status == "bad" else False,
            )
            # with slider_col2:
        with st.container(border=True):
            img = st.session_state.zarr
            seg = st.session_state.segmentation

            # img = img[::-1, :]

            lower_key = f"low_{st.session_state.lower_quantile}_{st.session_state.selected_sample}_{st.session_state.primary_channel}"
            upper_key = f"high_{st.session_state.upper_quantile}_{st.session_state.selected_sample}_{st.session_state.primary_channel}"

            if lower_key in st.session_state:
                low = st.session_state[lower_key]
                high = st.session_state[upper_key]
            else:
                low = np.quantile(img, st.session_state.lower_quantile)
                high = np.quantile(img, st.session_state.upper_quantile)

            l, h = st.slider(
                "Select a values for thresholding",
                min_value=0.0,
                max_value=255.0,
                value=(low, high),
                step=0.1,
                key="intensity",
                on_change=handle_slider,
                kwargs={"kl": lower_key, "kh": upper_key, "new_l": low, "new_h": high},
                # disabled=st.session_state.image_controls
            )
            img_filtered = (img - l).clip(min=0).astype("int32")

            res = regionprops_table(
                seg,
                intensity_image=img_filtered,
                properties=("label",),
                extra_properties=(
                    is_positive,
                    percentage_positive,
                ),
            )
            df = merge_results(st.session_state.data, st.session_state.subsample, res)

        # read in control elements via html
        components.html(read_html(), height=0, width=0)

        with st.container():
            col1, col2, col3 = st.columns(3)
            with col1:
                with st.expander("Raw Data", expanded=True):
                    st.image(
                        normalise_image(img),
                        use_column_width=True,
                    )
            with col2:
                with st.expander("Filtered data", expanded=True):
                    st.image(
                        normalise_image(
                            img_filtered, lower=l, upper=h, func=lambda img, val: val
                        ),
                        use_column_width=True,
                    )

            with col3:
                with st.expander("spatial_scatter", expanded=True):
                    st.plotly_chart(
                        plotly_scatter_gl(df),
                        use_container_width=True,
                    )

        with st.container():
            col4, col5, col6 = st.columns(3)
            with col4:
                with st.expander("spatial_scatter", expanded=True):
                    if st.session_state.secondary_channel is not None:
                        st.plotly_chart(
                            plotly_scatter_marker_gl(df),
                            use_container_width=True,
                        )
            with col5:
                with st.expander("Histogram", expanded=True):
                    st.plotly_chart(plot_hist(df), use_container_width=True)
            with col6:
                with st.expander("is positive", expanded=True):
                    st.plotly_chart(strip_plot(df), use_container_width=True)


with st.sidebar:

    _ = st.selectbox(
        "Select Reviewer:",
        st.session_state.reviewers,
        index=None,
        key="selected_reviewer",
        on_change=handle_reviewer_select,
        placeholder="Select a reviewer ...",
    )

    if st.session_state.selected_reviewer is not None:
        _ = st.selectbox(
            "Select Primary channel",
            st.session_state.primary_channels,
            index=None,
            key="primary_channel",
            placeholder="Select primary channel ...",
            on_change=handle_primary_channel_select,
            disabled=st.session_state.primary_channel_fixed,
        )

        st.toggle("Fix primary channel", key="primary_channel_fixed")
        st.toggle(
            "Show all samples", key="show_samples", on_change=handle_toggle_all_samples
        )

    if st.session_state.primary_channel is not None:
        st.write(
            "Completed :tada: :",
            st.session_state.statistics["completed"],
            "/",
            st.session_state.statistics["total"],
        )
        st.write(
            "Reviewed :white_check_mark: :",
            st.session_state.statistics["reviewed"],
            "/",
            st.session_state.statistics["total"],
        )
        st.write(
            "Bad :x: :",
            st.session_state.statistics["bad"],
            "/",
            st.session_state.statistics["total"],
        )
        if len(st.session_state.samples) != 0:
            # if not st.session_state.show_samples:
            # current_sample = st.session_state.selected_sample
            _ = st.selectbox(
                "Select Sample:",
                st.session_state.samples,
                index=st.session_state.selected_sample_index,
                # format_func=format_sample,
                key="selected_sample",
                on_change=handle_sample_select,
                placeholder="Select Sample...",
            )

            st.write(
                "You selected:",
                st.session_state.selected_sample
                if st.session_state.selected_sample is not None
                else st.session_state.selected_sample,
            )

        # st.write("Primary channel fixed", st.session_state.primary_channel_fixed)

    if st.session_state.selected_sample is not None:

        st.write(
            "Positive cells", res["is_positive"].sum(), "/", res["is_positive"].shape[0]
        )

        _ = st.selectbox(
            "Select Secondary channel",
            st.session_state.secondary_channels,
            index=0,
            key="secondary_channel",
            # format_func=format_graph,
            on_change=handle_secondary_channel_select,
            placeholder="Secondary Channel",
        )

        percentile_col1, percentile_col2 = st.columns(2)
        with percentile_col1:
            _ = st.number_input(
                "Lower percentile",
                value=st.session_state.lower_quantile,
                key="lower_quantile",
                format="%.4f",
                max_value=st.session_state.upper_quantile,
                min_value=0.0,
                step=0.05,
            )
            # st.write(st.session_state.lower_quantile)
        with percentile_col2:
            _ = st.number_input(
                "Upper percentile",
                value=st.session_state.upper_quantile,
                key="upper_quantile",
                format="%.4f",
                min_value=st.session_state.lower_quantile,
                max_value=1.0,
                step=0.05,
            )
            # st.write(st.session_state.upper_quantile)

        _ = st.number_input(
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
        dot_col1, dot_col2 = st.columns(2)
        with dot_col1:
            _ = st.number_input(
                "Dot size (-)",
                value=st.session_state.dotsize_neg,
                key="dotsize_neg",
                format="%d",
            )
        with dot_col2:
            _ = st.number_input(
                "Dot size (+)",
                value=st.session_state.dotsize_pos,
                key="dotsize_pos",
                format="%d",
            )
            
        _ = st.number_input(
            "Step size",
            value=st.session_state.stepsize,
            key="stepsize",
            format="%.2f",
            step=0.01,
            min_value=0.0,
            max_value=0.5,
        )

        _ = st.number_input(
            "Plot height",
            value=st.session_state.plot_height,
            key="plot_height",
            format="%d",
            step=1,
            min_value=0,
            max_value=2000,
        )
