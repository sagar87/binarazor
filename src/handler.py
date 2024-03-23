import numpy as np
import streamlit as st

from database import (
    get_channel_names,
    get_sample_expression,
    get_status,
    get_threshold,
    update_status,
)
from drive import get_data, get_image_dict
from utils import format_sample


# handler
def handle_sample_select():
    if st.session_state.selected_sample is None:
        # reset session state
        st.session_state.selected_sample_index = None
        st.session_state.data = None
        st.session_state.channels = None
        st.session_state.primary_channel = None
        st.session_state.secondary_channel = None
        st.session_state.primary_channel_index = None
        st.session_state.images = None
    else:
        # df = get_data(st.session_state.selected_sample)
        # store data frame and channels
        st.session_state.selected_sample_index = st.session_state.samples.index(
            st.session_state.selected_sample
        )
        # get sample name
        sample = format_sample(st.session_state.selected_sample)
        # st.session_state.channels = [
        #     channel
        #     for channel in st.session_state.data.columns.values.tolist()
        #     if channel not in ["X", "Y"]
        # ]
        st.session_state.channels = get_channel_names(sample)
        # change channel iff None is preselected
        if (
            st.session_state.primary_channel is None
            or st.session_state.primary_channel not in st.session_state.channels
        ):
            st.session_state.primary_channel = st.session_state.channels[0]
            st.session_state.secondary_channel = st.session_state.channels[0]

        st.session_state.primary_channel_index = st.session_state.channels.index(
            st.session_state.primary_channel
        )

        st.session_state.data = get_sample_expression(
            sample, st.session_state.primary_channel, st.session_state.secondary_channel
        )

        st.session_state.images = get_image_dict(
            format_sample(st.session_state.selected_sample),
            prefix=True if not st.session_state.image_controls else False,
        )

        st.session_state.slider_value = get_threshold(
            sample, st.session_state.primary_channel
        )
        st.session_state.status = get_status(sample, st.session_state.primary_channel)


def handle_next_sample():
    if st.session_state.selected_sample_index == (len(st.session_state.samples) - 1):
        st.info("Last graph")
    else:
        st.session_state.selected_sample_index += 1
        if st.session_state.selected_sample_index == (
            len(st.session_state.samples) - 1
        ):
            st.info("Last graph")

        st.session_state.selected_sample = st.session_state.samples[
            st.session_state.selected_sample_index
        ]
        handle_sample_select()
        # reset_init()


def handle_previous_sample():
    if st.session_state.selected_sample_index == 0:
        st.info("Last graph")
    else:
        st.session_state.selected_sample_index -= 1
        if st.session_state.selected_sample_index == 0:
            st.info("Last graph")

        st.session_state.selected_sample = st.session_state.samples[
            st.session_state.selected_sample_index
        ]
        handle_sample_select()


def handle_next_channel():
    if st.session_state.primary_channel_index == (len(st.session_state.channels) - 1):
        st.info("Last init")
    else:
        st.session_state.primary_channel_index += 1
        last_channel = (
            True
            if st.session_state.primary_channel_index
            == (len(st.session_state.channels) - 1)
            else False
        )
        sample = format_sample(st.session_state.selected_sample)
        channel = st.session_state.channels[st.session_state.primary_channel_index]
        st.session_state.primary_channel = channel
        st.session_state.data = get_sample_expression(
            sample, channel, st.session_state.secondary_channel
        )
        st.session_state.slider_value = get_threshold(
            sample, st.session_state.primary_channel
        )
        st.session_state.status = get_status(sample, st.session_state.primary_channel)
        st.toast(f"Switched to {channel}. {'Last channel' if last_channel else ''}")


def handle_previous_channel():
    if st.session_state.primary_channel_index == 0:
        st.toast("First init")
    else:
        st.session_state.primary_channel_index -= 1
        first_channel = True if st.session_state.primary_channel_index == 0 else False
        sample = format_sample(st.session_state.selected_sample)
        channel = st.session_state.channels[st.session_state.primary_channel_index]
        st.session_state.primary_channel = st.session_state.channels[
            st.session_state.primary_channel_index
        ]
        st.session_state.data = get_sample_expression(
            sample, channel, st.session_state.secondary_channel
        )
        st.session_state.slider_value = get_threshold(
            sample, st.session_state.primary_channel
        )
        st.session_state.status = get_status(sample, st.session_state.primary_channel)
        st.toast(f"Switched to {channel}. {'Last channel' if first_channel else ''} ")


def handle_primary_channel_select():
    st.session_state.primary_channel_index = st.session_state.channels.index(
        st.session_state.primary_channel
    )
    sample = format_sample(st.session_state.selected_sample)
    st.session_state.data = get_sample_expression(
        sample, st.session_state.primary_channel, st.session_state.secondary_channel
    )
    st.session_state.slider_value = get_threshold(
        sample, st.session_state.primary_channel
    )
    st.session_state.status = get_status(sample, st.session_state.primary_channel)


def handle_secondary_channel_select():
    sample = format_sample(st.session_state.selected_sample)
    st.session_state.data = get_sample_expression(
        sample, st.session_state.primary_channel, st.session_state.secondary_channel
    )


def handle_image_controls():
    st.session_state.image_controls = False if st.session_state.image_controls else True
    st.session_state.images = get_image_dict(
        format_sample(st.session_state.selected_sample),
        prefix=True if not st.session_state.image_controls else False,
    )


def handle_slider(kl, kh, new_l, new_h):
    st.session_state[kl] = new_l
    st.session_state[kh] = new_h
    # np.mean(s.to_numpy() <= q)


def increment_value():
    st.session_state.slider_value += 0.1


def decrement_value():
    st.session_state.slider_value -= 0.1


def handle_update_threshold():
    st.session_state.status = "reviewed"
    update_status(
        format_sample(st.session_state.selected_sample),
        st.session_state.primary_channel,
    )


def handle_bad_channel():
    st.session_state.status = "bad"
    update_status(
        format_sample(st.session_state.selected_sample),
        st.session_state.primary_channel,
    )