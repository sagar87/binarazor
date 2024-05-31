import numpy as np
import streamlit as st
from streamlit import session_state as state
from constants import Data, Vars
from config import App
from database import get_sample_expression, get_status
from drive import read_zarr_sample
from handler import handle_slider, handle_update
from plots import bokeh_scatter
from utils import merge_results, normalise_image, regionprops


@st.experimental_fragment
def show_sample(sample, channel, reviewer, dotsize_pos, dotsize_neg,  positive):

    status_dict = get_status(sample, channel)

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
        lower_key = f"low_{sample}_{channel}"
        upper_key = f"high_{sample}_{channel}"
        slider_key = f"slider_{sample}_{channel}"

        if status == "not reviewed":
            seg = read_zarr_sample(Data.ZARR_DICT["segmentation"], sample)
            img = read_zarr_sample(
                Data.ZARR_DICT[channel],
                sample,
            )

            if np.isnan(status_dict["lower"]):
                state[lower_key] = np.quantile(
                    img, state.lower_quantile
                )
            else:
                state[lower_key] = status_dict["lower"]

            if np.isnan(status_dict["upper"]):
                state[upper_key] = np.quantile(
                    img, state.upper_quantile
                )
            else:
                state[upper_key] = status_dict["upper"]

            if np.isnan(status_dict["threshold"]):
                state[slider_key] = state.slider
            else:
                state[slider_key] = status_dict["threshold"]
                
            
            with st.container(border=True):
                sli1, sli2 = st.columns(2)
                with sli1:
                    lower, upper = st.slider(
                        "Select a values for filtering",
                        min_value=0.0,
                        max_value=255.0,
                        value=(
                            state[lower_key],
                            state[upper_key],
                        ),
                        step=1.0,
                        key=f"intensity_{sample}_{channel}",
                        on_change=handle_slider,
                        kwargs={
                            "kl": lower_key,
                            "kh": upper_key,
                            "new_l": state[lower_key],
                            "new_h": state[upper_key],
                        },
                        disabled=False if status == "not reviewed" else True,
                    )
                with sli2:
                    slider = st.slider(
                        "Select Threshold",
                        min_value=0.0,
                        max_value=1.0,
                        value=state[slider_key],
                        step=App.DEFAULT_SLIDER_STEPSIZE,
                        key=f"threshold_{sample}_{channel}",
                        disabled=False if status == "not reviewed" else True,
                    )

            img_filtered = (img - lower).clip(min=0).astype("int32")


            col1, col2 = st.columns(2)
            with col1:
                with st.container(border=True):
                    img_norm = normalise_image(img)
                    st.image(
                        img_norm,
                        use_column_width=True,
                    )
            # st.write(res)

            data = get_sample_expression(
                sample, channel, "CD3"
            )
            res = regionprops(seg, img_filtered, slider)
            df = merge_results(data, res)

            with col2:
                with st.container(border=True):
                    img_norm = normalise_image(
                        img_filtered,
                        lower=lower,
                        upper=upper,
                        func=lambda img, val: val,
                    )
                    st.bokeh_chart(
                        bokeh_scatter(df, img_norm, dotsize_pos, dotsize_neg, positive), use_container_width=True
                    )

            with st.container(border=True):
                but1, but2 = st.columns(2)
                with but1:
                    st.button(
                        "Save thresholds",
                        on_click=handle_update,
                        kwargs={
                            "sample": sample,
                            "channel": channel,
                            "reviewer": reviewer,
                            "threshold": slider,
                            "lower": lower,
                            "upper": upper,
                            "cells": df[df.is_positive].label.tolist(),
                            "status": "reviewed",
                        },
                        key=f"update_{sample}_{channel}",
                    )

                with but2:
                    st.button(
                        "Mark as bad",
                        on_click=handle_update,
                        kwargs={
                            "sample": sample,
                            "channel": channel,
                            "reviewer": reviewer,
                            "threshold": float("nan"),
                            "lower": float("nan"),
                            "upper": float("nan"),
                            "cells": float("nan"),
                            "status": "bad",
                        },
                        key=f"bad_{sample}_{channel}",
                    )
        else:

            st.button(
                "Reset",
                on_click=handle_update,
                kwargs={
                    "sample": sample,
                    "channel": channel,
                    "reviewer": float("nan"),
                    "threshold": status_dict["threshold"],
                    "lower": status_dict["lower"],
                    "upper": status_dict["upper"],
                    "cells": float("nan"),
                    "status": float("nan"),
                },
                key=f"reset_{sample}_{channel}",
            )
