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
from drive import get_zarr_dict, read_zarr_sample

REVIEWERS = get_reviewers()
CHANNELS = get_channels()
ZARR_DICT = get_zarr_dict()

# To preserve global session state
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
    state[Vars._STATUS] = Vars.ALL

state[Vars.STATUS] = state[Vars._STATUS]

if Vars._NUM_SAMPLES not in state:
    state[Vars._NUM_SAMPLES] = get_sample_status_num(
        channel=state[Vars.CHANNEL], status=state[Vars.STATUS]
    )

state[Vars.NUM_SAMPLES] = state[Vars._NUM_SAMPLES]

if Vars._PAGE not in state:
    state[Vars._PAGE] = App.DEFAULT_PAGE

state[Vars.PAGE] = state[Vars._PAGE]


if Vars._NUM_PAGES not in state:
    state[Vars._NUM_PAGES] = ceil(state[Vars.NUM_SAMPLES] / App.DEFAULT_PAGE_SIZE)

state[Vars.NUM_PAGES] = state[Vars._NUM_PAGES]

if Vars._SAMPLES not in state:
    state[Vars._SAMPLES] = paginated_samples(
        state[Vars._PAGE] + 1,
        App.DEFAULT_PAGE_SIZE,
        channel=state[Vars.CHANNEL],
        status=state[Vars.STATUS],
    )

state[Vars.SAMPLES] = state[Vars._SAMPLES]


if App.ENV == "development":
    with st.container(border=False):
        with st.expander("session_state"):
            tcols = st.columns(4)

            for i, var in enumerate(sorted(state)):
                with tcols[i % 4]:
                    st.write(var, state[var])


with st.container():

    st.header(
        f"Viewing channel {state[Vars.CHANNEL]} ({state[Vars.STATUS]})| Page {state[Vars.PAGE] + 1} / {state[Vars.NUM_PAGES] + 1} "
    )
    st.subheader(
        "Use CMD/STRG + :heavy_plus_sign: / :heavy_minus_sign: to zoom in/out."
    )
    # st.write(state.samples[state.min_idx:state.max_idx])

    for sample in state[Vars.SAMPLES]:
        seg = read_zarr_sample(ZARR_DICT["segmentation"], sample)
        img = read_zarr_sample(ZARR_DICT[state[Vars.CHANNEL]], sample)
        show_sample(
            img,
            seg,
            sample,
            state[Vars.CHANNEL],
            state[Vars.REVIEWER],
            state[Vars.DOTSIZE_POS],
            state[Vars.DOTSIZE_NEG],
            state[Vars.LOWER_QUANTILE],
            state[Vars.UPPER_QUANTILE],
            state[Vars.POSITIVE],
        )


def _change_callback():
    # unpack values
    page = state[Vars.PAGE]
    reviewer = state[Vars.REVIEWER]
    channel = state[Vars.CHANNEL]
    lower = state[Vars.LOWER_QUANTILE]
    upper = state[Vars.UPPER_QUANTILE]
    dot_pos = state[Vars.DOTSIZE_POS]
    dot_neg = state[Vars.DOTSIZE_NEG]
    slider = state[Vars.SLIDER]
    positive = state[Vars.POSITIVE]
    status = state[Vars.STATUS]

    state[Vars._REVIEWER] = reviewer
    state[Vars.REVIEWER] = reviewer
    state[Vars._CHANNEL] = channel
    state[Vars.CHANNEL] = channel
    state[Vars._DOTSIZE_NEG] = dot_neg
    state[Vars.DOTSIZE_NEG] = dot_neg
    state[Vars._DOTSIZE_POS] = dot_pos
    state[Vars.DOTSIZE_POS] = dot_neg
    state[Vars._POSITIVE] = positive
    state[Vars.POSITIVE] = positive

    state[Vars._LOWER_QUANTILE] = lower
    state[Vars.LOWER_QUANTILE] = lower
    state[Vars._UPPER_QUANTILE] = upper
    state[Vars.UPPER_QUANTILE] = upper
    state[Vars._SLIDER] = slider
    state[Vars.SLIDER] = slider
    st.toast(f"{state[Vars._STATUS]} {state[Vars.STATUS]}")

    if status != state[Vars._STATUS]:
        # if the status has changed reset to first page
        page = 0
        num_samples = get_sample_status_num(channel, status)
        num_pages = ceil(num_samples / App.DEFAULT_PAGE_SIZE)
        state[Vars._NUM_SAMPLES] = num_samples
        state[Vars.NUM_SAMPLES] = num_samples
        state[Vars._NUM_PAGES] = num_pages
        state[Vars.NUM_PAGES] = num_pages

    state[Vars._PAGE] = page
    state[Vars.PAGE] = page

    state[Vars._SAMPLES] = paginated_samples(
        page + 1, App.DEFAULT_PAGE_SIZE, channel=channel, status=status
    )
    state[Vars.SAMPLES] = state[Vars._SAMPLES]

    st.success(
        f"Changed settings: Reviewer {reviewer} | Channel {channel} | Page {page+1} | Status {status} ...",
        icon="✅",
    )


with st.sidebar:
    show_channel_status(state[Vars.CHANNEL])

    with st.form("settings_form"):
        st.toggle("Positive cells only", key=Vars.POSITIVE)

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
            # on_change=handle_primary_channel_select,
            # disabled=state.primary_channel_fixed,
        )

        _ = st.selectbox(
            "Select status",
            ["all", "bad"],
            key=Vars.STATUS,
            placeholder="Select status ...",
            # on_change=handle_primary_channel_select,
            # disabled=state.primary_channel_fixed,
        )

        _ = st.selectbox(
            "Select page",
            range(state[Vars.NUM_PAGES]),
            format_func=lambda i: f"Page {i+1}",
            key="page",
            # on_change=handle_page_change,
            # kwargs={"page_size": page_size}
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
            # st.write(state.lower_quantile)
        with quantile_col2:
            _ = st.number_input(
                "Upper quantile",
                key=Vars.UPPER_QUANTILE,
                format="%.4f",
                min_value=0.0,
                max_value=1.0,
                step=0.01,
            )

        dot_col1, dot_col2 = st.columns(2)
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

        st.form_submit_button(
            "Apply changes",
            on_click=_change_callback,
        )
