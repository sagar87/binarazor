import streamlit as st

from config import App

st.set_page_config(
    page_title=f"{App.PROJECT} | Binarazor", page_icon=f"{App.PAGE_ICON}", layout="wide"
)


from container import show_sample
from database import get_all_samples, get_channels, get_reviewers, get_statistics
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

if "statistics" not in st.session_state:
    st.session_state.statistics = get_statistics(st.session_state.primary_channel)

if "size" not in st.session_state:
    st.session_state.size = App.DEFAULT_PAGE_SIZE

if "page" not in st.session_state:
    st.session_state.page = App.DEFAULT_PAGE

if "min_idx" not in st.session_state:
    st.session_state.min_idx = st.session_state.page * st.session_state.size

if "max_idx" not in st.session_state:
    st.session_state.max_idx = st.session_state.min_idx + st.session_state.size

if "lower_quantile" not in st.session_state:
    st.session_state.lower_quantile = App.DEFAULT_LOWER_QUANTILE

if "upper_quantile" not in st.session_state:
    st.session_state.upper_quantile = App.DEFAULT_UPPER_QUANTILE

if "slider" not in st.session_state:
    st.session_state.slider = App.DEFAULT_SLIDER_VALUE

if "stepsize" not in st.session_state:
    st.session_state.stepsize = App.DEFAULT_SLIDER_STEPSIZE

if "subsample" not in st.session_state:
    st.session_state.subsample = 0

if "dotsize_neg" not in st.session_state:
    st.session_state.dotsize_neg = App.DEFAULT_DOTSIZE_NEG

if "dotsize_pos" not in st.session_state:
    st.session_state.dotsize_pos = App.DEFAULT_DOTSIZE_POS

if "postive_cells" not in st.session_state:
    st.session_state.postive_cells = False

if "two_columns" not in st.session_state:
    st.session_state.two_columns = True

if App.ENV == "development":
    with st.container(border=False):
        with st.expander("session_state"):
            tcols = st.columns(4)

            for i, var in enumerate(sorted(st.session_state)):
                with tcols[i % 4]:
                    st.write(var, st.session_state[var])


with st.container():

    st.header(
        f"Page number {st.session_state.page} | Use CMD/STRG + :heavy_plus_sign: / :heavy_minus_sign: to zoom in/out."
    )
    # st.write(st.session_state.samples[st.session_state.min_idx:st.session_state.max_idx])

    for sample in st.session_state.samples[
        st.session_state.min_idx : st.session_state.max_idx
    ]:
        show_sample(sample)


with st.sidebar:

    st.write(
        "Completed :tada: :",
        st.session_state.statistics["completed"],
        "/",
        st.session_state.statistics["total"],
    )
    st.write(
        "Reviewed :white_check_mark: :",
        st.session_state.statistics["reviewed"],
        "/",
        st.session_state.statistics["total"],
    )
    st.write(
        "Bad :x: :",
        st.session_state.statistics["bad"],
        "/",
        st.session_state.statistics["total"],
    )

    st.toggle("Two column layout (beta)", value=False, key="two_columns")

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

    _ = st.number_input(
        "Threshold",
        key="slider",
        format="%.2f",
        step=0.01,
        min_value=0.0,
        max_value=1.0,
    )

    quantile_col1, quantile_col2 = st.columns(2)
    with quantile_col1:
        _ = st.number_input(
            "Lower quantile",
            key="lower_quantile",
            format="%.4f",
            min_value=0.0,
            max_value=1.0,
            step=0.01,
        )
        # st.write(st.session_state.lower_quantile)
    with quantile_col2:
        _ = st.number_input(
            "Upper quantile",
            key="upper_quantile",
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
            key="dotsize_neg",
            format="%d",
            disabled=st.session_state.two_columns,
        )
    with dot_col2:
        _ = st.number_input(
            "Dot size (+)",
            min_value=0,
            max_value=10,
            key="dotsize_pos",
            format="%d",
        )
