from math import ceil

import streamlit as st
from streamlit import session_state as state

from config import App, Vars
from database import get_sample_status_num, paginated_samples, update_status, create_annotation
from utils import _get_icon


def handle_single_form():
    """Handles session state after form input"""
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
    downsample = state[Vars.DOWNSAMPLE]
    height = state[Vars.HEIGHT]
    sample = state[Vars.SAMPLE]
    page_size = state[Vars.PAGE_SIZE]

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
    state[Vars._DOWNSAMPLE] = downsample
    state[Vars.DOWNSAMPLE] = downsample
    state[Vars._HEIGHT] = height
    state[Vars.HEIGHT] = height
    state[Vars._SAMPLE] = sample
    state[Vars.SAMPLE] = sample

    state[Vars._PAGE_SIZE] = page_size
    state[Vars.PAGE_SIZE] = page_size

    # st.toast(f"{state[Vars._STATUS]} {state[Vars.STATUS]}")

    num_samples = get_sample_status_num(
        channel, float("nan") if status == "not reviewed" else status
    )
    num_pages = ceil(num_samples / App.DEFAULT_PAGE_SIZE)

    if num_pages is None:
        num_pages = 0

    if page is None:
        page = 0

    state[Vars._NUM_SAMPLES] = num_samples
    state[Vars.NUM_SAMPLES] = num_samples
    state[Vars._NUM_PAGES] = num_pages
    state[Vars.NUM_PAGES] = num_pages

    state[Vars._STATUS] = status
    state[Vars.STATUS] = status

    if page >= num_pages:
        page = 0
    state[Vars._PAGE] = page
    state[Vars.PAGE] = page

    samples = paginated_samples(
        page + 1,
        App.DEFAULT_PAGE_SIZE,
        channel=channel,
        status=float("nan") if status == "not reviewed" else status,
    )
    state[Vars._SAMPLES] = samples
    state[Vars.SAMPLES] = samples

    st.toast(
        "Changed global settings.",
        icon="🎉",
    )


def handle_form():
    """Handles session state after form input"""
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
    downsample = state[Vars.DOWNSAMPLE]
    height = state[Vars.HEIGHT]
    page_size = state[Vars.PAGE_SIZE]

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
    state[Vars._DOWNSAMPLE] = downsample
    state[Vars.DOWNSAMPLE] = downsample
    state[Vars._HEIGHT] = height
    state[Vars.HEIGHT] = height
    # st.toast(f"{state[Vars._STATUS]} {state[Vars.STATUS]}")

    state[Vars._PAGE_SIZE] = page_size
    state[Vars.PAGE_SIZE] = page_size

    num_samples = get_sample_status_num(
        channel, float("nan") if status == "not reviewed" else status
    )
    num_pages = ceil(num_samples / state[Vars.PAGE_SIZE])

    if num_pages is None:
        num_pages = 0

    if page is None:
        page = 0

    state[Vars._NUM_SAMPLES] = num_samples
    state[Vars.NUM_SAMPLES] = num_samples
    state[Vars._NUM_PAGES] = num_pages
    state[Vars.NUM_PAGES] = num_pages

    state[Vars._STATUS] = status
    state[Vars.STATUS] = status

    if page >= num_pages:
        page = 0
    state[Vars._PAGE] = page
    state[Vars.PAGE] = page

    samples = paginated_samples(
        page + 1,
        state[Vars.PAGE_SIZE],
        channel=channel,
        status=float("nan") if status == "not reviewed" else status,
    )
    state[Vars._SAMPLES] = samples
    state[Vars.SAMPLES] = samples

    st.toast(
        "Changed global settings.",
        icon="🎉",
    )


def handle_slider(key, value):
    state[key] = value


def increment_value():
    st.session_state.slider_value = min(
        [1.0, st.session_state.slider_value + st.session_state.stepsize]
    )


def decrement_value():
    st.session_state.slider_value = max(
        [0.0, st.session_state.slider_value - st.session_state.stepsize]
    )


def handle_update(
    sample, channel, reviewer, threshold, lower, upper, cells, status, toast=True
):
    res = update_status(sample, channel, status, threshold, lower, upper, reviewer, cells)

    if toast:
        st.toast(
            f"{reviewer} annotated {sample} as {status}!"
            if isinstance(status, str)
            else f"Reseted {sample}!",
            icon=f"{_get_icon(status, single_char=True)}",
        )


def handle_page_change(page_size):
    st.session_state.page = st.session_state.page
    st.session_state.samples = paginated_samples(st.session_state.page + 1, page_size)
    # st.session_state.min_idx = st.session_state.page * st.session_state.size
    # st.session_state.max_idx = st.session_state.min_idx + st.session_state.size


def handle_selection(sample, channel, reviewer, threshold, lower, upper, cells, status, toast=True):
    res = create_annotation(sample, channel, status, threshold, lower, upper, reviewer, cells)

    if toast:
        st.toast(
            f"{reviewer} annotated {status}!",
            icon=f"🎉",
        )