import streamlit as st

st.set_page_config(page_title="MultiRazor", page_icon=":bar_chart:", layout="wide")
from glob import glob

import cv2
import numpy as np
import spatialproteomics as sp
import xarray as xr
from bokeh.models import WheelZoomTool
from bokeh.plotting import figure
from streamlit import session_state as state

from drive import get_zarr_dict, read_zarr_full_sample

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
]
SAMPLES = get_zarr_dict('voehring/ricover-multirazor')
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
    ]

st.write(SAMPLES)
if "sample" not in state:
    state.sample = list(SAMPLES.keys())[0]

if "linewidth" not in state:
    state.linewidth = 2

if "radius" not in state:
    state.radius = 5

if "downsample" not in state:
    state.downsample = 2
# st.write(state)
#         state[f'{marker}_slider'] = state[f'{_marker}_slider']


def handle_slider(key):
    print("lalal", state[key], state[f"_{key}"])
    state[f"_{key}"] = state[key]
    state[key] = state[key]
    # state[f"_{key}"] = state[f'_{key}']
    print("lalal", state[key], state[f"_{key}"])


with st.sidebar:
    sample = st.selectbox("Select samples", list(SAMPLES.keys()), key="selected_samples")
    downsample = st.radio("Downsample", DOWNSAMPLE, key="downsample", horizontal=True)
    c1, c2 = st.columns(2)
    with c1:
        linewidth = st.number_input(
            "Linewidth", min_value=0, max_value=5, key="linewidth"
        )
    with c2:
        radius = st.number_input("Radius", min_value=0, max_value=10, key="radius")

with st.container():
    st.multiselect("Select channels", MARKER, key="marker")

data = read_zarr_full_sample(SAMPLES[sample])

if len(state.marker) == 0:
    st.write("Select marker")

else:
    slider_values = {}
    # for marker in state.marker:
    #     # for _marker in MARKER:
    #     if marker not in state:
    #         state[f'_{marker}_slider'] = 0.8

    #     state[f'{marker}_slider'] = state[f'_{marker}_slider']
    DEFAULTS = {
        "PAX5": 0.8,
        "CD3": 0.7,
        "CD11b": 0.8,
        "CD31": 0.95,
        "CD34": 0.95,
        "CD68": 0.7,
        "CD90": 0.95,
        "Podoplanin": 0.95,
    }

    with st.container(border=True):
        slider_cols = st.columns(2)

        for i, marker in enumerate(state.marker):
            col_idx = i % 2
            with slider_cols[col_idx]:
                val = st.slider(
                    f"{marker}",
                    value=DEFAULTS.get(marker, 0.9),
                    min_value=0.6,
                    max_value=1.0,
                    step=0.01,
                )  # key=f'{marker}_slider', on_change=handle_slider, args=(f'{marker}_slider',)
                # state[f'{marker}_slider'] = val
                slider_values[marker] = val
    # st.write(state)
    filtered = [slider_values[marker] for marker in state.marker]

    # st.write(state.marker, filtered)

    filtered_data = data.pp[state.marker].pp.filter(filtered)


col1, col2 = st.columns(2)
with col1:
    with st.status("Filtering data"):
        img = (
            filtered_data.pp.downsample(downsample)
            .pl.colorize([COLORS[marker] for marker in state.marker])
            ._plot.values
        )
        img = cv2.normalize(img, None, 255, 0, cv2.NORM_MINMAX, cv2.CV_8U)
        img = img.view("uint32").reshape(img.shape[:2])

    with st.container(border=True):
        # fig = plt.figure(facecolor='k')
        # ax = plt.gca()
        # filtered_data.pp.downsample(2).pl.colorize([COLORS[marker] for marker in state.marker]).pl.imshow(ax=ax)
        # st.write(img.dtype, img.shape)
        # ax.imshow(img)

        # fig = px.imshow(filtered_data.pp.downsample(1).pl.colorize([COLORS[marker] for marker in state.marker])._plot.values, binary_string=True,)
        # ax.axis('off')
        # st.pyplot(fig)
        # st.plotly_chart(fig)

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
        st.bokeh_chart(p, use_container_width=True)

with col2:
    with st.status("Computing predictions"):
        classified = (
            filtered_data.pp.add_quantification(func=sp.arcsinh_median_intensity)
            .la.predict_cell_types_argmax(dict(zip(state.marker, state.marker)))
            .la.set_label_colors(list(COLORS.keys()), list(COLORS.values()))
        )
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

            print(cell_id.item())
        st.bokeh_chart(p, use_container_width=True)

        # fig = plt.figure(facecolor='k')
        # ax = plt.gca()
        # classified.pl.scatter_labels(ax=ax, legend_kwargs={'fontsize':8, 'ncols':2 }, size=.1)
        # ax.axis('off')
        # ax.set_aspect('equal')
        # st.pyplot(fig)

        # st.write(state)

        # image = data_img._plot.values

        # ax.imshow(image.sum(0))
        # import
        # info = np.finfo(image.dtype)
        # st.write(image.shape, image.dtype, info.max)

        # st.pyplot(fig)

        # x = [1, 2, 3, 4, 5]
        # y = [6, 7, 2, 4, 5]

        # p = figure(
        #     title='simple line example',
        #     x_axis_label='x',
        #     y_axis_label='y')

        # p.line(x, y, legend_label='Trend', line_width=2)#

        # import pdb;pdb.set_trace()

        # N = 20
        # img = np.empty((N,N), dtype=np.uint32)
        # view = img.view(dtype=np.uint8).reshape((N, N, 4))
        # for i in range(N):
        #     for j in range(N):
        #         view[i, j, 0] = int(i/N*255)
        #         view[i, j, 1] = 158
        #         view[i, j, 2] = int(j/N*255)
        #         view[i, j, 3] = 255

        # p = figure(tooltips=[("x", "$x"), ("y", "$y"), ("value", "@image")])
        # p.x_range.range_padding = p.y_range.range_padding = 0

        # # must give a vector of images
        # p.image_rgba(image=[image.astype(np.uint8)], x=0, y=0, dw=10, dh=10)


# with st.sidebar:
