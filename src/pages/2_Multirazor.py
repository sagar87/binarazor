import streamlit as st

st.set_page_config(page_title="MultiRazor", page_icon=":bar_chart:", layout="wide")
from glob import glob
from math import isnan

import cv2
import numpy as np
import spatialproteomics as sp
import xarray as xr
from bokeh.models import WheelZoomTool
from bokeh.plotting import figure
from streamlit import session_state as state

from container import _get_status
from database import get_entry
from drive import get_zarr_dict, read_zarr_full_sample
from handler import handle_update

two_col = True
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
}
MARKER = [
    "PAX5",
    "CD3",
    "CD11b",
    "CD31",
    "CD34",
    "CD68",
    "CD56",
    "CD90",
    "CD11c",
    "Podoplanin",
    "CD15",
]
SAMPLES = get_zarr_dict("voehring/ricover-multirazor")
# _MARKER = [ f#'_{marker}' for marker in MARKER ]
DOWNSAMPLE = [1, 2, 4, 8]

if "marker" not in state:
    state.marker = [
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
        "CD15",
    ]

# st.write(SAMPLES)
if "sample" not in state:
    state.sample = list(SAMPLES.keys())[0]

if "linewidth" not in state:
    state.linewidth = 2

if "radius" not in state:
    state.radius = 5

if "downsample" not in state:
    state.downsample = 2

if "height" not in state:
    state.height = 800
# st.write(state)
#         state[f'{marker}_slider'] = state[f'{_marker}_slider']


def handle_multirazor(sample, slider_values, classified, status):

    for k, v in slider_values.items():
        if k not in classified.la:
            cells = []
        else:
            cells = classified.la[k].cells.values.tolist()
        handle_update(
            sample,
            channel=k,
            reviewer="Harald",
            threshold=v,
            lower=float("nan"),
            upper=float("nan"),
            cells=cells,
            status=status,
        )


def handle_slider(key):
    print("lalal", state[key], state[f"_{key}"])
    state[f"_{key}"] = state[key]
    state[key] = state[key]
    # state[f"_{key}"] = state[f'_{key}']
    print("lalal", state[key], state[f"_{key}"])


with st.sidebar:
    sample = st.selectbox(
        "Select samples", list(SAMPLES.keys()), key="selected_samples"
    )
    downsample = st.radio("Downsample", DOWNSAMPLE, key="downsample", horizontal=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        linewidth = st.number_input(
            "Linewidth", min_value=0, max_value=5, key="linewidth"
        )
    with c2:
        radius = st.number_input("Radius", min_value=0, max_value=10, key="radius")

    with c3:
        height = st.number_input("Height", min_value=0, max_value=1600, key="height")

# with st.container():
# st.multiselect("Select channels", MARKER, key="marker")

data = read_zarr_full_sample(SAMPLES[sample])

if len(state.marker) == 0:
    st.write("Select marker")

else:
    status = get_entry
    slider_values = {}
    DEFAULTS = {
        "PAX5": 0.8,
        "CD3": 0.7,
        "CD11b": 0.8,
        "CD31": 0.95,
        "CD34": 0.95,
        "CD68": 0.9,
        "CD90": 0.95,
        "Podoplanin": 0.95,
    }

    with st.container(border=True):
        slider_cols = st.columns(2)

        for i, marker in enumerate(state.marker):
            marker_threshold = get_entry(sample, marker, "threshold")
            marker_status = _get_status(sample, marker)
            # st.write(marker_status)

            col_idx = i % 2
            with slider_cols[col_idx]:

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
    filtered = [slider_values[marker] for marker in state.marker]

    # st.write(state.marker, filtered)

    filtered_data = data.pp[state.marker].pp.filter(filtered)

with st.status("Filtering data"):
    img = (
        filtered_data.pp.downsample(downsample)
        .pl.colorize([COLORS[marker] for marker in state.marker])
        ._plot.values
    )
    img = cv2.normalize(img, None, 255, 0, cv2.NORM_MINMAX, cv2.CV_8U)
    img = img.view("uint32").reshape(img.shape[:2])
with st.status("Computing predictions"):
    classified = (
        filtered_data.pp.add_quantification(func=sp.arcsinh_median_intensity)
        .la.predict_cell_types_argmax(dict(zip(state.marker, state.marker)))
        .la.set_label_colors(list(COLORS.keys()), list(COLORS.values()))
    )


col1, col2 = st.columns(2)
with col1:

    with st.container(border=True):
        p = figure(match_aspect=True, sizing_mode="stretch_both")

        p.image_rgba(
            image=[img],
            x=[0],
            y=[0],
            dw=[downsample * img.shape[1]],
            dh=[downsample * img.shape[0]],
        )
        p.x_range.range_padding = 0
        p.y_range.range_padding = 0
        p.toolbar.active_scroll = p.select_one(WheelZoomTool)
        p.plot_height = height
        st.bokeh_chart(p, use_container_width=True)

with col2:

    with st.container(border=True):

        # import pdb;pdb.set_trace()
        p = figure(match_aspect=True, sizing_mode="stretch_both")
        p.image_rgba(
            image=[img],
            x=[0],
            y=[0],
            dw=[downsample * img.shape[1]],
            dh=[downsample * img.shape[0]],
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
                radius=radius,
                fill_color=c,
                legend_label=n,
                fill_alpha=0.0,
                line_width=linewidth,
                line_color=c,
            )

            # print(cell_id.item())
        p.plot_height = height
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

        p = figure(x_range=names, title="Cell counts", toolbar_location=None, tools="")
        p.vbar(x=names, top=total, color=colors, width=0.9)
        p.xgrid.grid_line_color = None
        p.y_range.start = 0
        st.bokeh_chart(p)

with dol2:
    pass

with st.container():
    bc1, bc2 = st.columns(2)
    with bc1:
        st.button(
            ":white_check_mark: Good",
            on_click=handle_multirazor,
            kwargs={
                "sample": sample,
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
                "sample": sample,
                "slider_values": {k: float("nan") for k in slider_values.keys()},
                "classified": classified,
                "status": float("nan"),
            },
            # key=f"reset_{sample}_{channel}",
            disabled=True if (status in ["not reviewed"]) else False,
        )
    # for k, v in slider_values.items():
    #     st.write(k)
