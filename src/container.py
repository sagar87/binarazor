import numpy as np
import spatialproteomics
import streamlit as st

from config import App
from database import (
    get_channel_stats,
    get_channels,
    get_entry,
    get_reviewer_stats,
    get_sample_expression,
    get_annotations,
    update_status,
    delete_annotation
)
from drive import get_zarr_dict, read_zarr_channel
from handler import handle_update, handle_selection
from plots import bokeh_scatter
from utils import _get_icon, merge_results, normalise_image, regionprops
from lasso import plotly_lasso, plotly_polygons
ZARR_DICT = get_zarr_dict()


@st.experimental_fragment(run_every="5s")
def show_channel_status(channel):
    statistics = get_channel_stats(channel)
    with st.container(border=True):
        st.subheader(f"{channel} summary")
        for state in ["not reviewed", "reviewed", "unsure", "bad"]:
            st.write(
                f"{state.capitalize()} {_get_icon(state)}:",
                statistics.get(state, 0),
                "/",
                sum(list(statistics.values())),
            )


@st.experimental_fragment(run_every="5s")
def show_full_channel_status():
    channels = get_channels()

    with st.container(border=True):
        st.subheader("Channel summary")
        # string = ""
        for ch in channels:
            statistics = get_channel_stats(ch)
            string = f"{ch: <6}:"
            for state in ["reviewed", "unsure", "bad", "not reviewed"]:
                string += f" {_get_icon(state)} : {statistics.get(state, 0)} |"
            # string += "\n"
            st.write(string.rstrip("|"))


def show_reviewer_stats(run_every="5s"):
    statistics = get_reviewer_stats()
    with st.container(border=True):
        st.subheader("Reviewer stats")
        for k, v in statistics.items():
            st.write(f"{k}: ", v)


def _get_status(sample, channel):
    status = get_entry(sample, channel, "status")
    return status if isinstance(status, str) else "not reviewed"


def get_slider_values(img, sample, channel, global_lower, global_upper, global_slider):
    # lower_key = f"low_{sample}_{channel}"
    # upper_key = f"high_{sample}_{channel}"
    # slider_key = f"slider_{sample}_{channel}"

    lower_value = get_entry(sample, channel, "lower")
    upper_value = get_entry(sample, channel, "upper")
    slider_value = get_entry(sample, channel, "threshold")

    lower_value = (
        np.quantile(img, global_lower) if np.isnan(lower_value) else lower_value
    )
    upper_value = (
        np.quantile(img, global_upper) if np.isnan(upper_value) else upper_value
    )
    slider_value = global_slider if np.isnan(slider_value) else slider_value
    return lower_value, upper_value, slider_value


@st.experimental_fragment
def show_sample(
    sample,
    channel,
    reviewer,
    dotsize_pos,
    dotsize_neg,
    global_lower,
    global_upper,
    global_slider,
    positive,
    height,
    downsample,
    show="not reviewed",
):
    status = _get_status(sample, channel)
    icon = _get_icon(status)
    header_string = f"{icon} | {sample}"

    if status != "not reviewed":
        header_string += f" | reviewed by {reviewer if status == 'not reviewed' else get_entry(sample, channel, 'reviewer')}"

    expand = True if (status == show) or (status == "not reviewed") else False

    if not expand:
        with st.expander(header_string, expand):
            lower_value = get_entry(sample, channel, "lower")
            upper_value = get_entry(sample, channel, "upper")
            slider_value = get_entry(sample, channel, "threshold")
            # with st.container(border=True):
            #     st.subheader(
            #         f"Current thresholds {lower_value}, {upper_value}"
            #     )
            with st.container():
                rcol1, rcol2 = st.columns(2)
                with rcol1:
                    st.button(
                        ":face_with_monocle: Reset",
                        on_click=handle_update,
                        kwargs={
                            "sample": sample,
                            "channel": channel,
                            "reviewer": float("nan"),
                            "threshold": slider_value,
                            "lower": lower_value,
                            "upper": upper_value,
                            "cells": float("nan"),
                            "status": float("nan"),
                        },
                        key=f"reset_{sample}_{channel}",
                        disabled=True if (status in ["not reviewed"]) else False,
                    )
                with rcol2:
                    st.button(
                        ":bomb: Hard Reset",
                        on_click=handle_update,
                        kwargs={
                            "sample": sample,
                            "channel": channel,
                            "reviewer": float("nan"),
                            "threshold": float("nan"),
                            "lower": float("nan"),
                            "upper": float("nan"),
                            "cells": float("nan"),
                            "status": float("nan"),
                        },
                        key=f"hard_{sample}_{channel}",
                        disabled=True if (status in ["not reviewed"]) else False,
                    )

    else:
        with st.expander(header_string, expand):
            seg = read_zarr_channel(ZARR_DICT["segmentation"], sample)
            img = read_zarr_channel(ZARR_DICT[channel], sample)

            lower_value, upper_value, slider_value = get_slider_values(
                img._image.values.squeeze(),
                sample,
                channel,
                global_lower,
                global_upper,
                global_slider,
            )

            with st.container(border=True):
                sli1, sli2 = st.columns(2)
                with sli1:
                    lower, upper = st.slider(
                        "Select a values for filtering",
                        min_value=0.0,
                        max_value=float(App.DEFAULT_DTYPE),
                        value=(
                            lower_value,
                            upper_value,
                        ),
                        step=1.0,
                        key=f"intensity_{sample}_{channel}",
                        disabled=False if status == "not reviewed" else True,
                    )
                with sli2:
                    slider = st.slider(
                        "Select Threshold",
                        min_value=0.0,
                        max_value=1.0,
                        value=slider_value,
                        step=App.DEFAULT_SLIDER_STEPSIZE,
                        key=f"threshold_{sample}_{channel}",
                        disabled=False if status == "not reviewed" else True,
                    )

            # images
            with st.container():
                # st.write(img)

                # img_filtered = (img - lower).clip(min=0).astype("int32")
                img_filtered = img.pp.filter(intensity=lower)
                # st.write(img_filtered._image.values)

                col1, col2 = st.columns(2)
                with col1:
                    with st.container(border=True):
                        img_norm = normalise_image(
                            img.pp.downsample(downsample)._image.values.squeeze()
                        )
                        st.image(
                            img_norm,
                            use_column_width=True,
                        )
                # prepare bokeh plot
                data = get_sample_expression(sample, channel, "CD3")
                res = regionprops(
                    seg._image.values.squeeze(),
                    img_filtered._image.values.squeeze(),
                    slider,
                )
                df = merge_results(data, res)

                with col2:
                    with st.container(border=True):
                        img_norm = normalise_image(
                            img_filtered.pp.downsample(
                                downsample
                            )._image.values.squeeze(),
                            lower=lower,
                            upper=upper,
                            func=lambda img, val: val,
                        )
                        st.bokeh_chart(
                            bokeh_scatter(
                                df,
                                img_norm,
                                height,
                                dotsize_pos,
                                dotsize_neg,
                                positive,
                                downsample,
                            ),
                            use_container_width=True,
                        )

            # buttons
            with st.container(border=True):
                but0, but1, but2, but3, but4, but5, but6 = st.columns(7)
                with but0:
                    st.button(
                        ":white_check_mark: Good",
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
                        disabled=True
                        if (status in ["reviewed", "unsure", "bad"])
                        else False,
                    )

                with but1:
                    st.button(
                        ":sparkle: 0 cells",
                        on_click=handle_update,
                        kwargs={
                            "sample": sample,
                            "channel": channel,
                            "reviewer": reviewer,
                            "threshold": 1.0,
                            "lower": lower,
                            "upper": upper,
                            "cells": [],
                            "status": "reviewed",
                        },
                        key=f"zero_{sample}_{channel}",
                        disabled=True
                        if (status in ["reviewed", "unsure", "bad"])
                        else False,
                    )

                with but2:
                    st.button(
                        ":warning: Unsure",
                        on_click=handle_update,
                        kwargs={
                            "sample": sample,
                            "channel": channel,
                            "reviewer": reviewer,
                            "threshold": slider,
                            "lower": lower,
                            "upper": upper,
                            "cells": df[df.is_positive].label.tolist(),
                            "status": "unsure",
                        },
                        key=f"unsure_{sample}_{channel}",
                        disabled=True
                        # if (status in ["reviewed", "unsure", "bad"])
                        # else False,
                    )
                with but3:
                    st.button(
                        ":x: Bad",
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
                        disabled=True
                        if (status in ["reviewed", "unsure", "bad"])
                        else False,
                    )
                with but4:
                    st.button(
                        ":face_with_monocle: Reset",
                        on_click=handle_update,
                        kwargs={
                            "sample": sample,
                            "channel": channel,
                            "reviewer": float("nan"),
                            "threshold": slider,
                            "lower": lower,
                            "upper": upper,
                            "cells": float("nan"),
                            "status": float("nan"),
                        },
                        key=f"reset_{sample}_{channel}",
                        disabled=True if (status in ["not reviewed"]) else False,
                    )

                with but5:
                    st.button(
                        ":bomb: Hard Reset",
                        on_click=handle_update,
                        kwargs={
                            "sample": sample,
                            "channel": channel,
                            "reviewer": float("nan"),
                            "threshold": float("nan"),
                            "lower": float("nan"),
                            "upper": float("nan"),
                            "cells": float("nan"),
                            "status": float("nan"),
                        },
                        key=f"hard_reset_{sample}_{channel}",
                        disabled=True if (status in ["not reviewed"]) else False,
                    )
                with but6:
                    st.subheader(
                        f"{df.is_positive.sum()} / {df.shape[0]} ({100 * df.is_positive.sum() / df.shape[0]:.2f} %)"
                    )


@st.experimental_fragment
def select_sample(
    sample,
    channel,
    reviewer,
    dotsize_pos,
    dotsize_neg,
    global_lower,
    global_upper,
    global_slider,
    positive,
    height,
    downsample,
    selection,
    show="not reviewed",
):
    status = _get_status(sample, channel)
    icon = _get_icon(status)
    header_string = f"{icon} | {sample}"
    


    if status != "not reviewed":
        header_string += f" | reviewed by {reviewer if status == 'not reviewed' else get_entry(sample, channel, 'reviewer')}"

    expand = True 

    with st.expander(header_string, expand):
        seg = read_zarr_channel(ZARR_DICT["segmentation"], sample)
        img = read_zarr_channel(ZARR_DICT[channel], sample)
        res = get_annotations(sample)
        # st.write(res)

        lower_value, upper_value, slider_value = get_slider_values(
            img._image.values.squeeze(),
            sample,
            channel,
            global_lower,
            global_upper,
            global_slider,
        )

        with st.container(border=True):
            sli1, sli2 = st.columns(2)
            with sli1:
                lower, upper = st.slider(
                    "Select a values for filtering",
                    min_value=0.0,
                    max_value=float(App.DEFAULT_DTYPE),
                    value=(
                        lower_value,
                        upper_value,
                    ),
                    step=1.0,
                    key=f"intensity_{sample}_{channel}",
                    disabled=False if status == "not reviewed" else True,
                )
            with sli2:
                slider = st.slider(
                    "Select Threshold",
                    min_value=0.0,
                    max_value=1.0,
                    value=slider_value,
                    step=App.DEFAULT_SLIDER_STEPSIZE,
                    key=f"threshold_{sample}_{channel}",
                    disabled=False if status == "not reviewed" else True,
                )

        # images
        with st.container():
            img_filtered = img.pp.filter(intensity=lower)
            selection_col, view_col =  st.columns(2)
            img_norm = normalise_image(
                img._image.values.squeeze()
            )
            with selection_col:
                with st.container(border=True):
                    
                    fig = plotly_lasso(img_norm, height=height)
                    event_data = st.plotly_chart(
                        fig,
                        on_select='rerun', # do_function,
                        selection_mode="lasso",
                        config={"displayModeBar": False}
                    )

                    if event_data:
                        if len(event_data["selection"]['lasso']) != 0:
                            x = event_data["selection"]['lasso'][0]['x']
                            y = event_data["selection"]['lasso'][0]['y']
                            data = [ (x_i, y_i) for x_i, y_i in zip(x,y) ]
                        else: 
                            data = []
            with view_col:
                with st.container(border=True):
                    # st.write ("Here comes the sun")                    
                    fig_poly = plotly_polygons(img_norm, height, res)
                    _ = st.plotly_chart(
                        fig_poly,
                        # on_select='rerun', # do_function,
                        # selection_mode="lasso",
                        config={"displayModeBar": False}
                    )                    

                    
        # buttons
        with st.container(border=True):
            but0, but1, but2 = st.columns(3)
            with but0:
                text_input = st.text_input(
                "Enter some text 👇",
                # label_visibility=st.session_state.visibility,
                disabled=True if len(event_data["selection"]['lasso'] ) == 0  else False
                # placeholder=st.session_state.placeholder,
            )
            with but1:
                st.button(
                    ":white_check_mark: Good",
                    on_click=handle_selection,
                    kwargs={
                        "sample": sample,
                        "channel": "ANNOTATION",
                        "reviewer": reviewer,
                        "threshold": float("nan"),
                        "lower": float("nan"),
                        "upper": float("nan"),
                        "cells": data,
                        "status": f"{text_input} | {channel}",
                    },
                    key=f"update_{sample}_{channel}",
                    disabled=True if len(event_data["selection"]['lasso'] ) ==0 or len(text_input) == 0 else False
                )

            with but2:
                st.subheader(
                    f"{len(data)} dots"
                )
        
        with st.container(border=True):            
            if len(res) != 0:
                for i, r in enumerate(res):
                    col1, col2, col3, col4, col5 = st.columns((1, 2, 2, 1, 1))
                    col1.write(r['status'])
                    col2.write(r['reviewer'])
                    col3.write(len(r['cells']))  # unique ID
                    button_phold = col5.empty()  # create a placeholder
                    do_action = button_phold.button(
                        "Delete", 
                        key=f'{sample}_delete_{i}',
                        on_click=delete_annotation,
                        kwargs={
                            'sample': sample,
                            'status': r['status']
                        }
                        
                        )
                    
