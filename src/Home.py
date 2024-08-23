import streamlit as st
from streamlit import session_state as state

from config import App, Vars

st.set_page_config(
    page_title=f"{App.PROJECT} | Binarazor", page_icon=f"{App.PAGE_ICON}", layout="wide"
)


from math import ceil

from container import show_channel_status, show_sample
from database import (
    get_channels,
    get_reviewers,
    get_sample_status_num,
    paginated_samples,
)
from handler import handle_form
from utils import _get_icon

REVIEWERS = get_reviewers()
CHANNELS = get_channels()


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

if Vars._NUM_SAMPLES not in state:
    state[Vars._NUM_SAMPLES] = get_sample_status_num(
        channel=state[Vars.CHANNEL], status=state[Vars.STATUS]
    )

state[Vars.NUM_SAMPLES] = state[Vars._NUM_SAMPLES]


if Vars._PAGE_SIZE not in state:
    state[Vars._PAGE_SIZE] = App.DEFAULT_PAGE_SIZE

state[Vars.PAGE_SIZE] = state[Vars._PAGE_SIZE]

if Vars._PAGE not in state:
    state[Vars._PAGE] = App.DEFAULT_PAGE

state[Vars.PAGE] = state[Vars._PAGE]


if Vars._NUM_PAGES not in state:
    state[Vars._NUM_PAGES] = ceil(state[Vars.NUM_SAMPLES] / state[Vars.PAGE_SIZE])

state[Vars.NUM_PAGES] = state[Vars._NUM_PAGES]

if Vars._SAMPLES not in state:
    state[Vars._SAMPLES] = paginated_samples(
        state[Vars._PAGE] + 1,
        state[Vars.PAGE_SIZE],
        channel=state[Vars.CHANNEL],
        status=state[Vars.STATUS],
    )

state[Vars.SAMPLES] = state[Vars._SAMPLES]

if Vars._DOWNSAMPLE not in state:
    state[Vars._DOWNSAMPLE] = App.DEFAULT_SCALE

state[Vars.DOWNSAMPLE] = state[Vars._DOWNSAMPLE]


if Vars._HEIGHT not in state:
    state[Vars._HEIGHT] = 800

state[Vars.HEIGHT] = state[Vars._HEIGHT]

if App.ENV == "development":
    with st.container(border=False):
        with st.expander("session_state"):
            tcols = st.columns(4)

            for i, var in enumerate(sorted(state)):
                with tcols[i % 4]:
                    st.write(var, state[var])


with st.container():

    st.header(
        f"Viewing channel {state[Vars.CHANNEL]} ({state[Vars.STATUS]}) | Page {state[Vars.PAGE] + 1} / {state[Vars.NUM_PAGES] + 1} "
    )
    st.subheader(
        "Use CMD/STRG + :heavy_plus_sign: / :heavy_minus_sign: to zoom in/out."
    )
    # st.write(state.samples[state.min_idx:state.max_idx])

    for sample in state[Vars.SAMPLES]:
        show = "not reviewed" if state[Vars.STATUS] == "all" else state[Vars.STATUS]

        # st.write(f'{state[lower_key]}, {state[upper_key]}')
        # status_dict = get_status(sample, state[Vars.CHANNEL])
        # st.write(status_dict)
        show_sample(
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
            show=show,
        )


with st.sidebar:
    show_channel_status(state[Vars.CHANNEL])

    with st.form("settings_form"):
        st.subheader("Global settings")
        st.toggle("Positive cells only", key=Vars.POSITIVE)

        _ = st.radio(
            "Select status",
            [
                "not reviewed",
                "reviewed",
                "unsure",
                "bad",
                "all",
            ],
            key=Vars.STATUS,
            format_func=lambda x: f"{_get_icon(x)}",  # {x.capitalize()}
            horizontal=True
            # placeholder="Select status ...",
        )
        # _ = st.radio("Downsample", App.DOWNSAMPLE, key=Vars.DOWNSAMPLE, horizontal=True)
        _ = st.radio("Downsample", App.DOWNSAMPLE, key=Vars.DOWNSAMPLE, horizontal=True)
        _ = st.radio(
            "Cores per page",
            sorted([10, App.DEFAULT_PAGE_SIZE, 50, 100]),
            key=Vars.PAGE_SIZE,
            horizontal=True,
        )

        _ = st.selectbox(
            "Select Reviewer",
            REVIEWERS,
            index=0,
            key=Vars.REVIEWER,
            placeholder="Select a reviewer ...",
        )

        _ = st.selectbox(
            "Select channel",
            CHANNELS,
            key=Vars.CHANNEL,
            placeholder="Select channel ...",
        )

        _ = st.selectbox(
            "Select page",
            range(state[Vars.NUM_PAGES]),
            format_func=lambda i: f"Page {i+1}",
            key="page",
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
            on_click=handle_form,
        )
