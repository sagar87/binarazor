import streamlit as st

st.set_page_config(page_title="Binarazor", page_icon="👋", layout="wide")


from container import show_sample
from database import get_all_samples, get_channels, get_reviewers
from drive import get_zarr_dict
from pagination import paginator

# Session state
if "reviewers" not in st.session_state:
    st.session_state.reviewers = get_reviewers()

if "selected_reviewer" not in st.session_state:
    st.session_state.selected_reviewer = st.session_state.reviewers[0]

if "zarr_dict" not in st.session_state:
    st.session_state.zarr_dict = get_zarr_dict()

if "primary_channels" not in st.session_state:
    st.session_state.primary_channels = get_channels()

if "primary_channel" not in st.session_state:
    st.session_state.primary_channel = st.session_state.primary_channels[0]

if "samples" not in st.session_state:
    st.session_state.samples = get_all_samples()

if "size" not in st.session_state:
    st.session_state.size = 30

if "page" not in st.session_state:
    st.session_state.page = 0

if "min_idx" not in st.session_state:
    st.session_state.min_idx = st.session_state.page * st.session_state.size

if "max_idx" not in st.session_state:
    st.session_state.max_idx = st.session_state.min_idx + st.session_state.size

if "lower_quantile" not in st.session_state:
    st.session_state.lower_quantile = 0.990

if "upper_quantile" not in st.session_state:
    st.session_state.upper_quantile = 0.998

if "slider" not in st.session_state:
    st.session_state.slider = 0.5

if "stepsize" not in st.session_state:
    st.session_state.stepsize = 0.05

if "subsample" not in st.session_state:
    st.session_state.subsample = 0

if "dotsize_neg" not in st.session_state:
    st.session_state.dotsize_neg = 3

if "dotsize_pos" not in st.session_state:
    st.session_state.dotsize_pos = 5

if "postive_cells" not in st.session_state:
    st.session_state.postive_cells = False

with st.container(border=False):
    with st.expander("session_state"):
        tcols = st.columns(4)

        for i, var in enumerate(sorted(st.session_state)):
            with tcols[i % 4]:
                st.write(var, st.session_state[var])


with st.container():

    st.header(f"Page number {st.session_state.page}")
    # st.write(st.session_state.samples[st.session_state.min_idx:st.session_state.max_idx])

    for sample in st.session_state.samples[
        st.session_state.min_idx : st.session_state.max_idx
    ]:
        show_sample(sample)


with st.sidebar:

    _ = st.selectbox(
        "Select Reviewer:",
        st.session_state.reviewers,
        index=0,
        key="selected_reviewer",
        placeholder="Select a reviewer ...",
    )

    _ = st.selectbox(
        "Select Primary channel",
        st.session_state.primary_channels,
        key="primary_channel",
        placeholder="Select primary channel ...",
        # on_change=handle_primary_channel_select,
        # disabled=st.session_state.primary_channel_fixed,
    )

    paginator(
        "Select page",
        st.session_state.samples,
        items_per_page=st.session_state.size,
        on_sidebar=True,
        page_number_key="page",
    )

    dot_col1, dot_col2 = st.columns(2)
    with dot_col1:
        _ = st.number_input(
            "Dot size (-)",
            value=st.session_state.dotsize_neg,
            key="dotsize_neg",
            format="%d",
        )
    with dot_col2:
        _ = st.number_input(
            "Dot size (+)",
            value=st.session_state.dotsize_pos,
            key="dotsize_pos",
            format="%d",
        )
