import streamlit as st

st.set_page_config(page_title="MultiRazor", page_icon=":bar_chart:", layout="wide")

from math import isnan

import cv2
import spatialproteomics as sp
from bokeh.models import WheelZoomTool
from bokeh.plotting import figure
from streamlit import session_state as state

from config import App, Bucket, Vars
from container import _get_status
from database import get_entry, get_reviewers
from drive import get_zarr_dict, read_zarr_full_sample
from handler import handle_update
from utils import _get_icon


def handle_multirazor(sample, reviewer, slider_values, classified, status):

    for k, v in slider_values.items():
        if isinstance(status, str):
            if k not in classified.la:
                cells = []
            else:
                cells = classified.la[k].cells.values.tolist()
        else:
            cells = float("nan")

        handle_update(
            sample,
            channel=k,
            reviewer=reviewer,
            threshold=v,
            lower=float("nan"),
            upper=float("nan"),
            cells=cells,
            status=status,
            toast=False,
        )

    st.toast(
        f"{reviewer} annotated {sample} as {status}!"
        if isinstance(status, str)
        else f"Reseted {sample}!",
        icon=f"{_get_icon(status, single_char=True)}",
    )


def handle_form():
    """Handles session state after form input"""
    reviewer = state[Vars.REVIEWER]
    sample = state[Vars.SAMPLE]
    channel = state[Vars.CHANNELS]
    downsample = state[Vars.DOWNSAMPLE]
    height = state[Vars.HEIGHT]
    linewidth = state[Vars.LINEWIDTH]
    radius = state[Vars.RADIUS]

    # dot_neg = state[Vars.DOTSIZE_NEG]
    # slider = state[Vars.SLIDER]
    # positive = state[Vars.POSITIVE]
    # status = state[Vars.STATUS]

    state[Vars._REVIEWER] = reviewer
    state[Vars.REVIEWER] = reviewer
    state[Vars._SAMPLE] = sample
    state[Vars.SAMPLE] = sample
    state[Vars._CHANNELS] = channel
    state[Vars.CHANNELS] = channel
    state[Vars._DOWNSAMPLE] = downsample
    state[Vars.DOWNSAMPLE] = downsample
    state[Vars._HEIGHT] = height
    state[Vars.HEIGHT] = height
    state[Vars._LINEWIDTH] = linewidth
    state[Vars.LINEWIDTH] = linewidth
    state[Vars._RADIUS] = radius
    state[Vars.RADIUS] = radius


if Bucket.MULTI_PATH == "":
    st.header("MultiRazor not activated")
else:
    DOWNSAMPLE = [1, 2, 4, 8]
    REVIEWERS = get_reviewers()
    ZARR_DICT = get_zarr_dict(Bucket.MULTI_PATH)

    COLORS = {
        "PAX5": sp.Red,
        "CD3": sp.Green,
        "CD11b": sp.Yellow,
        "CD11c": sp.Blue,
        "CD68": sp.Orange,
        "CD31": sp.Purple,
        "CD34": sp.Pink,
        "CD56": sp.Teal,
        "CD90": sp.Cyan,
        "Podoplanin": sp.Apricot,
        "CD15": sp.Olive,
        "CD4": sp.Yellow,
        "CD8": sp.Red,
    }

    CHANNELS = [
        "PAX5",
        "CD3",
        "CD11b",
        "CD11c",
        "CD31",
        "CD34",
        "CD68",
        "CD56",
        "CD90",
        "Podoplanin",
        "CD15",
        # "CD4",
        # "CD8",
    ]

    DEFAULTS = {
        "PAX5": 0.8,
        "CD3": 0.7,
        "CD11b": 0.8,
        "CD31": 0.95,
        "CD34": 0.95,
        "CD68": 0.9,
        "CD90": 0.95,
        "Podoplanin": 0.95,
        "CD15": 0.99,
    }

    if Vars._CHANNELS not in state:
        state[Vars._CHANNELS] = [
            "PAX5",
            "CD3",
            "CD11b",
            "CD11c",
            "CD68",
            "CD56",
            "CD31",
            "CD34",
            "CD90",
            "Podoplanin",
        ]

    state[Vars.CHANNELS] = state[Vars._CHANNELS]

    # st.write(ZARR_DICT)
    if Vars._REVIEWER not in state:
        state[Vars._REVIEWER] = REVIEWERS[0]

    state[Vars.REVIEWER] = state[Vars._REVIEWER]

    if Vars._SAMPLE not in state:
        state[Vars._SAMPLE] = list(ZARR_DICT.keys())[0]

    state[Vars.SAMPLE] = state[Vars._SAMPLE]

    if Vars._LINEWIDTH not in state:
        state[Vars._LINEWIDTH] = 2

    state[Vars.LINEWIDTH] = state[Vars._LINEWIDTH]

    if Vars._RADIUS not in state:
        state[Vars._RADIUS] = 5

    state[Vars.RADIUS] = state[Vars._RADIUS]

    if Vars._DOWNSAMPLE not in state:
        state[Vars._DOWNSAMPLE] = App.DEFAULT_SCALE

    state[Vars.DOWNSAMPLE] = state[Vars._DOWNSAMPLE]

    if Vars._HEIGHT not in state:
        state[Vars._HEIGHT] = 800

    state[Vars.HEIGHT] = state[Vars._HEIGHT]

    with st.sidebar:
        with st.form("settings"):
            _ = st.radio(
                "Downsample", App.DOWNSAMPLE, key=Vars.DOWNSAMPLE, horizontal=True
            )
            _ = st.selectbox("Select reviewer", REVIEWERS, key=Vars.REVIEWER)
            _ = st.selectbox("Select sample", list(ZARR_DICT.keys()), key=Vars.SAMPLE)
            _ = st.multiselect("Select channels", CHANNELS, key=Vars.CHANNELS)
            c1, c2, c3 = st.columns(3)
            with c1:
                _ = st.number_input(
                    "Linewidth", min_value=0, max_value=5, key=Vars.LINEWIDTH
                )
            with c2:
                _ = st.number_input(
                    "Radius", min_value=0, max_value=10, key=Vars.RADIUS
                )

            with c3:
                _ = st.number_input(
                    "Height", min_value=0, max_value=1600, key=Vars.HEIGHT
                )

            st.form_submit_button(
                "Apply changes",
                on_click=handle_form,
            )

    data = read_zarr_full_sample(ZARR_DICT[state[Vars.SAMPLE]])

    if len(state[Vars.CHANNELS]) == 0:
        st.write("Select marker")

    else:
        status = get_entry
        slider_values = {}

        with st.container(border=True):
            slider_cols = st.columns(len(state[Vars.CHANNELS]))

            for i, marker in enumerate(state[Vars.CHANNELS]):
                marker_threshold = get_entry(state[Vars.SAMPLE], marker, "threshold")
                marker_status = _get_status(state[Vars.SAMPLE], marker)
                # st.write(marker_status)

                # col_idx = i % 2
                with slider_cols[i]:

                    val = st.slider(
                        f"{marker}",
                        value=DEFAULTS.get(marker, 0.9)
                        if isnan(marker_threshold)
                        else marker_threshold,
                        min_value=0.6,
                        max_value=1.0,
                        step=0.01,
                        disabled=True if marker_status == "reviewed" else False,
                    )  # key=f'{marker}_slider', on_change=handle_slider, args=(f'{marker}_slider',)
                    # state[f'{marker}_slider'] = val
                    slider_values[marker] = val
        # st.write(state)
        filtered = [slider_values[marker] for marker in state[Vars.CHANNELS]]

        filtered_data = data.pp[state[Vars.CHANNELS]].pp.filter(filtered)

    with st.status("Filtering data"):
        img = (
            filtered_data.pp.downsample(state[Vars.DOWNSAMPLE])
            .pl.colorize([COLORS[marker] for marker in state[Vars.CHANNELS]])
            ._plot.values
        )
        img = cv2.normalize(img, None, 255, 0, cv2.NORM_MINMAX, cv2.CV_8U)
        img = img.view("uint32").reshape(img.shape[:2])
    with st.status("Computing predictions"):
        classified = (
            filtered_data.pp.add_quantification(func=sp.arcsinh_median_intensity)
            .la.predict_cell_types_argmax(
                dict(zip(state[Vars.CHANNELS], state[Vars.CHANNELS]))
            )
            .la.set_label_colors(list(COLORS.keys()), list(COLORS.values()))
        )

    with st.container(border=True):
        bc1, bc2 = st.columns(2)
        with bc1:
            st.button(
                ":white_check_mark: Good",
                on_click=handle_multirazor,
                kwargs={
                    "sample": state[Vars.SAMPLE],
                    "reviewer": state[Vars.REVIEWER],
                    "slider_values": slider_values,
                    "classified": classified,
                    "status": "reviewed",
                },
                disabled=True if marker_status == "reviewed" else False,
            )
        with bc2:
            st.button(
                ":face_with_monocle: Reset",
                on_click=handle_multirazor,
                kwargs={
                    "sample": state[Vars.SAMPLE],
                    "reviewer": float("nan"),
                    "slider_values": {k: float("nan") for k in slider_values.keys()},
                    "classified": classified,
                    "status": float("nan"),
                },
                # key=f"reset_{sample}_{channel}",
                disabled=True if (status in ["not reviewed"]) else False,
            )

    col1, col2 = st.columns(2)
    with col1:

        with st.container(border=True):
            p = figure(match_aspect=True, sizing_mode="stretch_both")

            p.image_rgba(
                image=[img],
                x=[0],
                y=[0],
                dw=[state[Vars.DOWNSAMPLE] * img.shape[1]],
                dh=[state[Vars.DOWNSAMPLE] * img.shape[0]],
            )
            p.x_range.range_padding = 0
            p.y_range.range_padding = 0
            p.toolbar.active_scroll = p.select_one(WheelZoomTool)
            p.plot_height = state[Vars.HEIGHT]
            st.bokeh_chart(p, use_container_width=True)

    with col2:

        with st.container(border=True):

            # import pdb;pdb.set_trace()
            p = figure(match_aspect=True, sizing_mode="stretch_both")
            p.image_rgba(
                image=[img],
                x=[0],
                y=[0],
                dw=[state[Vars.DOWNSAMPLE] * img.shape[1]],
                dh=[state[Vars.DOWNSAMPLE] * img.shape[0]],
            )
            p.x_range.range_padding = 0
            p.y_range.range_padding = 0
            p.toolbar.active_scroll = p.select_one(WheelZoomTool)
            for cell_id in classified.labels:
                sub = classified.la[cell_id.item()]
                x = sub._obs.sel(features="centroid-1").values
                y = sub._obs.sel(features="centroid-0").values
                c = sub._properties.sel(props="_color").item()
                n = sub._properties.sel(props="_name").item()

                p.circle(
                    x,
                    y,
                    radius=state[Vars.RADIUS],
                    fill_color=c,
                    legend_label=n,
                    fill_alpha=0.0,
                    line_width=state[Vars.LINEWIDTH],
                    line_color=c,
                )

                # print(cell_id.item())
            p.plot_height = state[Vars.HEIGHT]
            st.bokeh_chart(p, use_container_width=True)

    dol1, dol2 = st.columns(2)
    with dol1:

        with st.container(border=True):
            total = []
            names = []
            colors = []
            for cell_id in classified.labels:
                sub = classified.la[cell_id.item()]
                # x = sub._obs.sel(features="centroid-1").values
                # y = sub._obs.sel(features="centroid-0").values
                t = len(sub.cells.values.tolist())
                c = sub._properties.sel(props="_color").item()
                n = sub._properties.sel(props="_name").item()
                total.append(t)
                names.append(n)
                colors.append(c)

            p = figure(
                x_range=names, title="Cell counts", toolbar_location=None, tools=""
            )
            p.vbar(x=names, top=total, color=colors, width=0.9)
            p.xgrid.grid_line_color = None
            p.y_range.start = 0
            st.bokeh_chart(p, use_container_width=True)

    with dol2:
        with st.container(border=True):
            p = figure(match_aspect=True, sizing_mode="stretch_both")
            p.toolbar.active_scroll = p.select_one(WheelZoomTool)
            for cell_id in classified.labels:
                sub = classified.la[cell_id.item()]
                x = sub._obs.sel(features="centroid-1").values
                y = sub._obs.sel(features="centroid-0").values
                c = sub._properties.sel(props="_color").item()
                n = sub._properties.sel(props="_name").item()

                p.circle(
                    x,
                    y,
                    radius=state[Vars.RADIUS],
                    fill_color=c,
                    legend_label=n,
                    fill_alpha=1.0,
                    line_width=state[Vars.LINEWIDTH],
                    line_color=c,
                )

                # print(cell_id.item())
            # p.plot_height = height
            st.bokeh_chart(p, use_container_width=True)

        # for k, v in slider_values.items():
        #     st.write(k)
