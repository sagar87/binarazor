import streamlit as st
from streamlit import session_state as state

from config import App

st.set_page_config(
    page_title=f"{App.PROJECT} | Binarazor", page_icon=f"{App.PAGE_ICON}", layout="wide"
)


from math import ceil

from constants import Data, Vars
from container import show_channel_status, show_sample
from database import (
    get_all_samples,
    get_channels,
    get_reviewers,
    get_statistics,
    get_total_samples,
    paginated_samples,
)
from drive import get_zarr_dict

# To preserve global session state
if Vars._REVIEWER not in state:
    state[Vars._REVIEWER] = Data.REVIEWERS[0]

if Vars._CHANNEL not in state:
    state[Vars._CHANNEL] = Data.CHANNELS[0]

if Vars._DOTSIZE_NEG not in state:
    state[Vars._DOTSIZE_NEG] = App.DEFAULT_DOTSIZE_NEG

if Vars._DOTSIZE_POS not in state:
    state[Vars._DOTSIZE_POS] = App.DEFAULT_DOTSIZE_POS

if Vars._POSITIVE not in state:
    state[Vars._POSITIVE] = True


state[Vars.REVIEWER] = state[Vars._REVIEWER]
state[Vars.CHANNEL] = state[Vars._CHANNEL]
state[Vars.DOTSIZE_NEG] = state[Vars._DOTSIZE_NEG]
state[Vars.DOTSIZE_POS] = state[Vars._DOTSIZE_POS]
state[Vars.POSITIVE] = state[Vars._POSITIVE]

if Vars.PAGE not in state:
    state[Vars.PAGE] = App.DEFAULT_PAGE

if Vars.SAMPLES not in state:
    state[Vars.SAMPLES] = paginated_samples(state[Vars.PAGE] + 1, App.DEFAULT_PAGE_SIZE)

if Vars.STATISTICS not in state:
    state[Vars.STATISTICS] = get_statistics(state[Vars.CHANNEL])

if Vars.LOWER_QUANTILE not in state:
    state[Vars.LOWER_QUANTILE] = App.DEFAULT_LOWER_QUANTILE

if Vars.UPPER_QUANTILE not in state:
    state[Vars.UPPER_QUANTILE] = App.DEFAULT_UPPER_QUANTILE

if Vars.SLIDER not in state:
    state[Vars.SLIDER] = App.DEFAULT_SLIDER_VALUE


if App.ENV == "development":
    with st.container(border=False):
        with st.expander("session_state"):
            tcols = st.columns(4)

            for i, var in enumerate(sorted(state)):
                with tcols[i % 4]:
                    st.write(var, state[var])


with st.container():

    st.header(
        f"Page number {state[Vars.PAGE]} | Use CMD/STRG + :heavy_plus_sign: / :heavy_minus_sign: to zoom in/out."
    )
    # st.write(state.samples[state.min_idx:state.max_idx])

    for sample in state[Vars.SAMPLES]:
        show_sample(
            sample,
            state[Vars.CHANNEL],
            state[Vars.REVIEWER],
            state[Vars.DOTSIZE_POS],
            state[Vars.DOTSIZE_NEG],
            state[Vars.POSITIVE],
        )


def _change_callback(page, page_size):
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

    state[Vars.LOWER_QUANTILE] = lower
    state[Vars.UPPER_QUANTILE] = upper
    state[Vars.SLIDER] = slider

    state.page = page
    state.samples = paginated_samples(page + 1, page_size)
    st.success(
        f"Changed settings: Reviewer {reviewer} | Channel {channel} | Page {page+1} ...",
        icon="✅",
    )


with st.sidebar:
    show_channel_status(state[Vars.CHANNEL])

    with st.form("settings_form"):
        st.toggle("Positive cells only", key=Vars.POSITIVE)

        reviewer = st.selectbox(
            "Select Reviewer:",
            Data.REVIEWERS,
            index=0,
            key=Vars.REVIEWER,
            placeholder="Select a reviewer ...",
        )

        channel = st.selectbox(
            "Select Primary channel",
            Data.CHANNELS,
            key=Vars.CHANNEL,
            placeholder="Select primary channel ...",
            # on_change=handle_primary_channel_select,
            # disabled=state.primary_channel_fixed,
        )

        num_pages = ceil(Data.NUM_SAMPLES / App.DEFAULT_PAGE_SIZE)

        page = st.selectbox(
            "Select page",
            range(num_pages),
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
            kwargs={"page": page, "page_size": App.DEFAULT_PAGE_SIZE},
        )
