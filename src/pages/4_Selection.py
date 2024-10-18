import streamlit as st
from streamlit import session_state as state

from config import App, Vars

st.set_page_config(
    page_title=f"{App.PROJECT} | Binarazor", page_icon=f"{App.PAGE_ICON}", layout="wide"
)


from math import ceil
import numpy as np
from config import Bucket

from container import show_channel_status, select_sample
from database import get_channels, get_reviewers, get_sample_status_num
from drive import get_zarr_dict, read_zarr_channel
from handler import handle_single_form, handle_selection
from utils import _get_icon


REVIEWERS = get_reviewers()
CHANNELS = get_channels()
ZARR_DICT = get_zarr_dict(Bucket.MULTI_PATH)

if Vars._REVIEWER not in state:
    state[Vars._REVIEWER] = REVIEWERS[0]

state[Vars.REVIEWER] = state[Vars._REVIEWER]

if Vars._CHANNEL not in state:
    state[Vars._CHANNEL] = CHANNELS[0]

state[Vars.CHANNEL] = state[Vars._CHANNEL]

if Vars._DOTSIZE_NEG not in state:
    state[Vars._DOTSIZE_NEG] = App.DEFAULT_DOTSIZE_NEG

state[Vars.DOTSIZE_NEG] = state[Vars._DOTSIZE_NEG]

if Vars._DOTSIZE_POS not in state:
    state[Vars._DOTSIZE_POS] = App.DEFAULT_DOTSIZE_POS

state[Vars.DOTSIZE_POS] = state[Vars._DOTSIZE_POS]

if Vars._POSITIVE not in state:
    state[Vars._POSITIVE] = True

state[Vars.POSITIVE] = state[Vars._POSITIVE]

if Vars._LOWER_QUANTILE not in state:
    state[Vars._LOWER_QUANTILE] = App.DEFAULT_LOWER_QUANTILE

state[Vars.LOWER_QUANTILE] = state[Vars._LOWER_QUANTILE]

if Vars._UPPER_QUANTILE not in state:
    state[Vars._UPPER_QUANTILE] = App.DEFAULT_UPPER_QUANTILE

state[Vars.UPPER_QUANTILE] = state[Vars._UPPER_QUANTILE]

if Vars._SLIDER not in state:
    state[Vars._SLIDER] = App.DEFAULT_SLIDER_VALUE

state[Vars.SLIDER] = state[Vars._SLIDER]

if Vars._STATUS not in state:
    state[Vars._STATUS] = Vars.NOT_REVIEWED

state[Vars.STATUS] = state[Vars._STATUS]

if Vars._PAGE_SIZE not in state:
    state[Vars._PAGE_SIZE] = App.DEFAULT_PAGE_SIZE

state[Vars.PAGE_SIZE] = state[Vars._PAGE_SIZE]

if Vars._NUM_SAMPLES not in state:
    state[Vars._NUM_SAMPLES] = get_sample_status_num(
        channel=state[Vars.CHANNEL], status=state[Vars.STATUS]
    )

state[Vars.NUM_SAMPLES] = state[Vars._NUM_SAMPLES]

if Vars._PAGE not in state:
    state[Vars._PAGE] = App.DEFAULT_PAGE

state[Vars.PAGE] = state[Vars._PAGE]

if Vars._SAMPLE not in state:
    state[Vars._SAMPLE] = list(ZARR_DICT.keys())[0]

state[Vars.SAMPLE] = state[Vars._SAMPLE]

if Vars._DOWNSAMPLE not in state:
    state[Vars._DOWNSAMPLE] = App.DEFAULT_SCALE

state[Vars.DOWNSAMPLE] = state[Vars._DOWNSAMPLE]


if Vars._HEIGHT not in state:
    state[Vars._HEIGHT] = 800

state[Vars.HEIGHT] = state[Vars._HEIGHT]

# For future use => display polygons
if Vars._SELECTION not in state:
    state[Vars._SELECTION] = dict()

state[Vars.SELECTION] = state[Vars._SELECTION]


if App.ENV == "development":
    with st.container(border=False):
        with st.expander("session_state"):
            tcols = st.columns(4)

            for i, var in enumerate(sorted(state)):
                with tcols[i % 4]:
                    st.write(var, state[var])


REVIEWERS = get_reviewers()
CHANNELS = get_channels()
ZARR_DICT = get_zarr_dict(Bucket.MULTI_PATH)
# ZARR_DICT = get_zarr_dict()
st.write('Something')

with st.container():

    st.header(f"Viewing channel {state[Vars.CHANNEL]} ({state[Vars.STATUS]})")
    st.subheader(
        "Use CMD/STRG + :heavy_plus_sign: / :heavy_minus_sign: to zoom in/out."
    )

    sample = state[Vars.SAMPLE]
    show = "not reviewed" if state[Vars.STATUS] == "all" else state[Vars.STATUS]

    select_sample(
        sample,
        state[Vars.CHANNEL],
        state[Vars.REVIEWER],
        state[Vars.DOTSIZE_POS],
        state[Vars.DOTSIZE_NEG],
        state[Vars.LOWER_QUANTILE],
        state[Vars.UPPER_QUANTILE],
        state[Vars.SLIDER],
        state[Vars.POSITIVE],
        state[Vars.HEIGHT],
        state[Vars.DOWNSAMPLE],
        state[Vars.SELECTION],
        show=show,
    )


with st.sidebar:
    # show_channel_status(state[Vars.CHANNEL])

    with st.form("settings_form"):
        st.subheader("Global settings")

        _ = st.selectbox(
            "Select Reviewer",
            REVIEWERS,
            index=0,
            key=Vars.REVIEWER,
            placeholder="Select a reviewer ...",
        )

        _ = st.selectbox(
            "Select Sample",
            ZARR_DICT.keys(),
            # format_func=lambda i: f"Page {i+1}",
            key=Vars.SAMPLE,
        )

        _ = st.selectbox(
            "Select channel",
            CHANNELS,
            key=Vars.CHANNEL,
            placeholder="Select channel ...",
        )

        _ = st.number_input(
            "Threshold",
            key=Vars.SLIDER,
            format="%.2f",
            step=0.05,
            min_value=0.0,
            max_value=1.0,
        )

        quantile_col1, quantile_col2 = st.columns(2)
        with quantile_col1:
            _ = st.number_input(
                "Lower quantile",
                key=Vars.LOWER_QUANTILE,
                format="%.4f",
                min_value=0.0,
                max_value=1.0,
                step=0.01,
            )

        with quantile_col2:
            _ = st.number_input(
                "Upper quantile",
                key=Vars.UPPER_QUANTILE,
                format="%.4f",
                min_value=0.0,
                max_value=1.0,
                step=0.01,
            )

        dot_col1, dot_col2, dot_col3 = st.columns(3)
        with dot_col1:
            _ = st.number_input(
                "Dot size (-)",
                min_value=0,
                max_value=10,
                key=Vars.DOTSIZE_NEG,
                format="%d",
                disabled=state[Vars.POSITIVE],
            )
        with dot_col2:
            _ = st.number_input(
                "Dot size (+)",
                min_value=0,
                max_value=10,
                key=Vars.DOTSIZE_POS,
                format="%d",
            )
        with dot_col3:
            _ = st.number_input("Height", min_value=0, max_value=1600, key=Vars.HEIGHT)

        st.form_submit_button(
            "Apply changes",
            on_click=handle_single_form,
        )