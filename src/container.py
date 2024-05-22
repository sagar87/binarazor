import numpy as np
import streamlit as st

from database import get_sample_expression, get_status
from drive import read_zarr_sample
from handler import handle_slider, handle_update
from plots import bokeh_scatter
from utils import merge_results, normalise_image, regionprops


@st.experimental_fragment
def show_sample(sample):

    status_dict = get_status(sample, st.session_state.primary_channel)

    status = (
        status_dict["status"]
        if isinstance(status_dict["status"], str)
        else "not reviewed"
    )

    if status == "not reviewed":
        icon = ":question:"
    elif status == "bad":
        icon = ":x:"
    else:
        icon = ":white_check_mark:"

    header_string = f"{icon} | {sample}"

    if status != "not reviewed":
        header_string += f' | reviewed by {status_dict["reviewer"]}'

    with st.expander(header_string, True if status == "not reviewed" else False):

        seg = read_zarr_sample(st.session_state.zarr_dict["segmentation"], sample)
        img = read_zarr_sample(
            st.session_state.zarr_dict[st.session_state.primary_channel],
            sample,
        )

        lower_key = f"low_{sample}_{st.session_state.primary_channel}"
        upper_key = f"high_{sample}_{st.session_state.primary_channel}"
        slider_key = f"slider_{sample}_{st.session_state.primary_channel}"

        if np.isnan(status_dict["lower"]):
            st.session_state[lower_key] = np.quantile(
                img, st.session_state.lower_quantile
            )
        else:
            st.session_state[lower_key] = status_dict["lower"]

        if np.isnan(status_dict["upper"]):
            st.session_state[upper_key] = np.quantile(
                img, st.session_state.upper_quantile
            )
        else:
            st.session_state[upper_key] = status_dict["upper"]

        if np.isnan(status_dict["threshold"]):
            st.session_state[slider_key] = st.session_state.slider
        else:
            st.session_state[slider_key] = status_dict["threshold"]

        with st.container(border=True):
            sli1, sli2 = st.columns(2)
            with sli1:
                lower, upper = st.slider(
                    "Select a values for filtering",
                    min_value=0.0,
                    max_value=255.0,
                    value=(
                        st.session_state[lower_key],
                        st.session_state[upper_key],
                    ),
                    step=1.0,
                    key=f"intensity_{sample}_{st.session_state.primary_channel}",
                    on_change=handle_slider,
                    kwargs={
                        "kl": lower_key,
                        "kh": upper_key,
                        "new_l": st.session_state[lower_key],
                        "new_h": st.session_state[upper_key],
                    },
                    disabled=False if status == "not reviewed" else True,
                )
            with sli2:
                slider = st.slider(
                    "Select Threshold",
                    min_value=0.0,
                    max_value=1.0,
                    value=st.session_state[slider_key],
                    step=st.session_state.stepsize,
                    key=f"threshold_{sample}_{st.session_state.primary_channel}",
                    disabled=False if status == "not reviewed" else True,
                )

        img_filtered = (img - lower).clip(min=0).astype("int32")
        if st.session_state.two_columns:
            col1, col2 = st.columns(2)
            with col1:
                with st.container(border=True):
                    img_norm = normalise_image(img)
                    st.image(
                        img_norm,
                        use_column_width=True,
                    )
            # st.write(res)
            
            data = get_sample_expression(sample, st.session_state.primary_channel, "CD3")
            res = regionprops(seg, img_filtered, slider)
            df = merge_results(data, st.session_state.subsample, res) 
                                
            with col2:
                with st.container(border=True):
                    img_norm = normalise_image(
                            img_filtered,
                            lower=lower,
                            upper=upper,
                            func=lambda img, val: val,
                        )
                    st.bokeh_chart(bokeh_scatter(df, img_norm), use_container_width=True)
        else:
            
            col1, col2, col3 = st.columns(3)
            with col1:
                with st.container(border=True):
                    img_norm = normalise_image(img)
                    st.image(
                        img_norm,
                        use_column_width=True,
                    )
            with col2:
                with st.container(border=True):
                    st.image(
                        normalise_image(
                            img_filtered,
                            lower=lower,
                            upper=upper,
                            func=lambda img, val: val,
                        ),
                        use_column_width=True,
                    )
            # st.write(res)
            data = get_sample_expression(sample, st.session_state.primary_channel, "CD3")
            res = regionprops(seg, img_filtered, slider)
            df = merge_results(data, st.session_state.subsample, res)

            with col3:
                with st.container(border=True):
                    st.bokeh_chart(bokeh_scatter(df), use_container_width=True)
                    # st.plotly_chart(plotly_scatter_gl(df), use_container_width=True)

            with st.container(border=True):
                but1, but2 = st.columns(2)
                with but1:
                    st.button(
                        "Save thresholds",
                        on_click=handle_update,
                        kwargs={
                            "sample": sample,
                            "channel": st.session_state.primary_channel,
                            "reviewer": st.session_state.selected_reviewer,
                            "threshold": slider,
                            "lower": lower,
                            "upper": upper,
                            "cells": df[df.is_positive].label.tolist(),
                            "status": "reviewed",
                        },
                        key=f"update_{sample}_{st.session_state.primary_channel}",
                    )

                with but2:
                    st.button(
                        "Mark as bad",
                        on_click=handle_update,
                        kwargs={
                            "sample": sample,
                            "channel": st.session_state.primary_channel,
                            "reviewer": st.session_state.selected_reviewer,
                            "threshold": float("nan"),
                            "lower": float("nan"),
                            "upper": float("nan"),
                            "cells": float("nan"),
                            "status": "bad",
                        },
                        key=f"bad_{sample}_{st.session_state.primary_channel}",
                    )
