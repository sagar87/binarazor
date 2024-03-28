import streamlit as st

from database import (
    get_all_channels,
    get_channels,
    get_reviewers,
    get_sample_expression,
    get_samples,
    get_statistics,
    get_status,
    update_status,
)
from drive import get_image_dict, get_zarr_dict, read_zarr_sample

# Session state
if "reviewers" not in st.session_state:
    st.session_state.reviewers = get_reviewers()

if "selected_reviewer" not in st.session_state:
    st.session_state.selected_reviewer = None

if "primary_channels" not in st.session_state:
    st.session_state.primary_channels = None

if "primary_channel" not in st.session_state:
    st.session_state.primary_channel = None

if "primary_channel_index" not in st.session_state:
    st.session_state.primary_channel_index = None

if "primary_channel_fixed" not in st.session_state:
    st.session_state.primary_channel_fixed = False

if "show_samples" not in st.session_state:
    st.session_state.show_samples = False

if "samples" not in st.session_state:
    st.session_state.samples = None

if "selected_sample" not in st.session_state:
    st.session_state.selected_sample = None

if "statistics" not in st.session_state:
    st.session_state.statistics = None

if "selected_sample_index" not in st.session_state:
    st.session_state.selected_sample_index = None

if "data" not in st.session_state:
    st.session_state.data = None

if "zarr_dict" not in st.session_state:
    st.session_state.zarr_dict = None

if "zarr" not in st.session_state:
    st.session_state.zarr = None

if "segmentation" not in st.session_state:
    st.session_state.segmentation = None

if "secondary_channels" not in st.session_state:
    st.session_state.secondary_channels = None

if "secondary_channel" not in st.session_state:
    st.session_state.secondary_channel = None

if "slider_value" not in st.session_state:
    st.session_state.slider_value = 0.5

if "stepsize" not in st.session_state:
    st.session_state.stepsize = 0.05

if "subsample" not in st.session_state:
    st.session_state.subsample = 0

if "dotsize" not in st.session_state:
    st.session_state.dotsize = 2

if "lower_quantile" not in st.session_state:
    st.session_state.lower_quantile = 0.990

if "upper_quantile" not in st.session_state:
    st.session_state.upper_quantile = 0.998

if "status" not in st.session_state:
    st.session_state.status = None

if "plot_height" not in st.session_state:
    st.session_state.plot_height = 1000


# handler
def reset_session_state(keys, value=None):
    if isinstance(keys, str):
        keys = [keys]
    for key in keys:
        st.session_state[key] = value


def handle_reviewer_select():
    if st.session_state.selected_reviewer is None:
        reset_session_state(["primary_channels", "primary_channel"])
    else:
        st.session_state.primary_channels = get_channels()

    handle_primary_channel_select()


def handle_primary_channel_select():
    if st.session_state.primary_channel is None:
        reset_session_state(
            [
                "primary_channel",
                "samples",
                "selected_sample",
                "selected_sample_index",
                "statistics",
                "zarr",
                "zarr_dict",
                "segmentation",
            ]
        )

    else:
        st.session_state.primary_channel_index = (
            st.session_state.primary_channels.index(st.session_state.primary_channel)
        )
        # samples = get_samples(st.session_state.primary_channel)
        print("IN PRIMARY CHANNEL", st.session_state.primary_channel)

        st.session_state.samples = get_samples(
            st.session_state.primary_channel,
            filter_samples=False if st.session_state.show_samples else True,
        )
        st.session_state.zarr_dict = get_zarr_dict()
        st.session_state.statistics = get_statistics(st.session_state.primary_channel)
        print()
        print()
        print()
        print("IN PRIMARY CHANNEL", st.session_state.samples)
        print()
        print()
        print()

        if (
            len(st.session_state.samples) > 0
            and st.session_state.selected_sample not in st.session_state.samples
        ):
            st.session_state.selected_sample = None
        elif (
            len(st.session_state.samples) > 0
            and st.session_state.selected_sample in st.session_state.samples
        ):
            st.session_state.selected_sample = st.session_state.selected_sample
        else:
            st.session_state.selected_sample = None
        print()
        print()
        print()
        print("IN PRIMARY CHANNEL 2", st.session_state.selected_sample)
        print()
        print()
        print()
        # st.session_state.selected_sample_index = st.session_state.samples.index(
        #     st.session_state.selected_sample
        # )
    handle_sample_select()
    # st.session_state.secondary_channels = get_all_channels(
    #     st.session_state.selected_sample
    # )
    # st.session_state.secondary_channel = st.session_state.secondary_channels[0]

    # if (st.session_state.primary_channel is None or st.session_state.primary_channel not in st.session_state.primary_channels):
    # st.session_state.primary_channel = st.session_state.primary_channels[0]

    # populate image dict
    # st.session_state.images = get_image_dict(st.session_state.selected_sample)

    # st.session_state.data = get_sample_expression(
    #     st.session_state.selected_sample,
    #     st.session_state.primary_channel,
    #     st.session_state.secondary_channel,
    # )

    # sample = st.session_state.selected_sample
    # st.session_state.data = get_sample_expression(
    # sample, st.session_state.primary_channel, st.session_state.secondary_channel
    # )
    # st.session_state.slider_value = get_threshold(
    # sample, st.session_state.primary_channel
    # )
    # st.session_state.status = get_status(sample, st.session_state.primary_channel)
    # st.session_state.statistics = get_statistics(
    # sample, st.session_state.primary_channel
    # )


def handle_sample_select():
    if st.session_state.selected_sample is None:
        # reset session state
        # reset_session_state(
        #     [
        #         "primary_channel",
        #         "samples",
        #         "selected_sample",
        #         "selected_sample_index",
        #     ]
        # )
        print("RESETTING SAMPLE SELECT!")
        reset_session_state(
            [
                "selected_sample_index",
                "secondary_channels",
                "secondary_channel",
                "images",
                "data",
                "slider_value",
                "status",
            ]
        )
        # st.session_state.primary_channels = None
        # st.session_state.primary_channel = None
        # st.session_state.secondary_channel = None
        # st.session_state.primary_channel_index = None
    else:
        st.session_state.selected_sample = st.session_state.selected_sample
        print("In handle select", st.session_state.selected_sample)
        if st.session_state.selected_sample in st.session_state.samples:
            st.session_state.selected_sample_index = st.session_state.samples.index(
                st.session_state.selected_sample
            )
        else:
            st.session_state.selected_sample = None
            st.session_state.selected_sample_index = None
            reset_session_state(
                [
                    "selected_sample_index",
                    "secondary_channels",
                    "secondary_channel",
                    "data",
                    "slider_value",
                    "status",
                    "zarr" "segmentation",
                ]
            )
            return

        # get sample name
        # st.session_state.primary_channels = get_all_channels(
        #     st.session_state.selected_sample
        # )
        # change channel iff None is preselected
        # if (
        #     st.session_state.primary_channel is None
        #     or st.session_state.primary_channel not in st.session_state.primary_channels
        # ):
        #     st.session_state.primary_channel = st.session_state.primary_channels[0]
        # st.session_state.secondary_channel = st.session_state.primary_channels[0]

        # st.session_state.primary_channel_index = (
        #     st.session_state.primary_channels.index(st.session_state.primary_channel)
        # )

        st.session_state.secondary_channels = get_all_channels(
            st.session_state.selected_sample
        )
        if (
            st.session_state.secondary_channel is None
            or st.session_state.secondary_channel
            not in st.session_state.secondary_channels
        ):
            st.session_state.secondary_channel = st.session_state.secondary_channels[0]

        st.session_state.data = get_sample_expression(
            st.session_state.selected_sample,
            st.session_state.primary_channel,
            st.session_state.secondary_channel,
        )

        # st.session_state.images = get_image_dict(
        #     st.session_state.selected_sample,
        # )

        st.session_state.zarr = read_zarr_sample(
            st.session_state.zarr_dict[st.session_state.primary_channel],
            st.session_state.selected_sample,
        )

        st.session_state.segmentation = read_zarr_sample(
            st.session_state.zarr_dict["segmentation"],
            st.session_state.selected_sample,
        )
        st.session_state.slider_value = 0.5
        st.session_state.status = get_status(
            st.session_state.selected_sample, st.session_state.primary_channel
        )

        print("out handle selected sample", st.session_state.selected_sample)


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
    if st.session_state.primary_channel_index == (
        len(st.session_state.primary_channels) - 1
    ):
        st.info("Last init")
    else:
        st.session_state.primary_channel_index += 1
        last_channel = (
            True
            if st.session_state.primary_channel_index
            == (len(st.session_state.primary_channels) - 1)
            else False
        )
        sample = st.session_state.selected_sample
        channel = st.session_state.primary_channels[
            st.session_state.primary_channel_index
        ]
        st.session_state.primary_channel = channel
        st.session_state.data = get_sample_expression(
            sample, channel, st.session_state.secondary_channel
        )
        # st.session_state.slider_value = get_threshold(
        #     sample, st.session_state.primary_channel
        # )
        st.session_state.slider_value = 0.5
        st.session_state.status = get_status(sample, st.session_state.primary_channel)

        st.session_state.zarr = read_zarr_sample(
            st.session_state.zarr_dict[st.session_state.primary_channel],
            st.session_state.selected_sample,
        )

        st.session_state.segmentation = read_zarr_sample(
            st.session_state.zarr_dict["segmentation"],
            st.session_state.selected_sample,
        )
        # st.session_state.statistics = get_statistics(
        #     sample, st.session_state.primary_channel
        # )
        st.toast(f"Switched to {channel}. {'Last channel' if last_channel else ''}")


def handle_previous_channel():
    if st.session_state.primary_channel_index == 0:
        st.toast("First init")
    else:
        st.session_state.primary_channel_index -= 1
        first_channel = True if st.session_state.primary_channel_index == 0 else False
        sample = st.session_state.selected_sample
        channel = st.session_state.primary_channels[
            st.session_state.primary_channel_index
        ]
        st.session_state.primary_channel = st.session_state.primary_channels[
            st.session_state.primary_channel_index
        ]
        st.session_state.data = get_sample_expression(
            sample, channel, st.session_state.secondary_channel
        )
        # st.session_state.slider_value = get_threshold(
        #     sample, st.session_state.primary_channel
        # )
        st.session_state.slider_value = 0.5
        st.session_state.status = get_status(sample, st.session_state.primary_channel)
        # st.session_state.statistics = get_statistics(
        #     sample, st.session_state.primary_channel
        # )
        st.session_state.zarr = read_zarr_sample(
            st.session_state.zarr_dict[st.session_state.primary_channel],
            st.session_state.selected_sample,
        )

        st.session_state.segmentation = read_zarr_sample(
            st.session_state.zarr_dict["segmentation"],
            st.session_state.selected_sample,
        )
        st.toast(f"Switched to {channel}. {'Last channel' if first_channel else ''} ")


def handle_secondary_channel_select():

    st.session_state.data = get_sample_expression(
        st.session_state.selected_sample,
        st.session_state.primary_channel,
        st.session_state.secondary_channel,
    )


def handle_image_controls():
    st.session_state.image_controls = False if st.session_state.image_controls else True
    st.session_state.images = get_image_dict(st.session_state.selected_sample)


def handle_slider(kl, kh, new_l, new_h):
    st.session_state[kl] = new_l
    st.session_state[kh] = new_h


def increment_value():
    st.session_state.slider_value = min(
        [1.0, st.session_state.slider_value + st.session_state.stepsize]
    )


def decrement_value():
    st.session_state.slider_value = max(
        [0.0, st.session_state.slider_value - st.session_state.stepsize]
    )


def handle_update_threshold():
    st.session_state.status = "reviewed"
    update_status(
        st.session_state.selected_sample,
        st.session_state.primary_channel,
    )
    handle_primary_channel_select()
    st.info("Switched sample")


def handle_bad_channel():
    st.session_state.status = "bad"
    update_status(
        st.session_state.selected_sample,
        st.session_state.primary_channel,
    )
    handle_primary_channel_select()
    st.info("Switched sample")


def handle_toggle_all_samples():
    print(st.session_state.selected_sample, st.session_state.show_samples)

    # st.session_state.samples = get_samples(st.session_state.primary_channel, filter_samples=False if st.session_state.show_samples else True)
    handle_primary_channel_select()
    st.info("Showing all samples")
