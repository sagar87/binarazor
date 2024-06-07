import sys
from pathlib import Path

import streamlit as st

from config import App

st.set_page_config(
    page_title=f"{App.PROJECT} | Binarazor", page_icon=f"{App.PAGE_ICON}", layout="wide"
)


sys.path.append(str(Path(__file__).resolve().parent.parent))
import pandas as pd

from container import show_full_channel_status, show_reviewer_stats
from database import get_channels, get_thresholds_by_channel
from utils import _get_icon


def get_data():
    data = []
    channels = get_channels()
    for channel in channels:
        df = get_thresholds_by_channel(channel)
        data.append(df)

    return pd.concat(data)


def get_overview(df):
    df["status_new"] = df.apply(
        lambda row: f"{_get_icon(row['status'], single_char=True)} | {row['reviewer'][0] if isinstance(row['reviewer'], str) else 'NA' } | {len(row['cells']) if isinstance(row['cells'], list) else 'NA' }",
        1,
    )

    return df.pivot(index="sample", columns="channel", values="status_new")


def get_threholds(df):
    return df.drop(["cells", "_id"], 1).to_csv(index=False).encode("utf-8")


def get_cell_list(df):
    return (
        df[df.status == "reviewed"]
        .drop(["upper", "lower", "_id", "status", "threshold", "reviewer"], 1)
        .explode("cells")
        .to_csv(index=False)
        .encode("utf-8")
    )


df = get_data()
overview = get_overview(df.copy())
thresholds = get_threholds(df.copy())
cell_lists = get_cell_list(df.copy())

st.header("Summary")
with st.expander("All Samples: Status | Reviewer | # Cells", expanded=True):
    # st.subheader("All sampless")
    st.table(overview)


with st.sidebar:
    show_full_channel_status()
    show_reviewer_stats()
    with st.container(border=True):
        st.subheader("Download annotations")

        st.download_button(
            "Download Tresholds",
            data=thresholds,
            file_name="threholds.csv",
            mime="text/csv",
        )

        st.download_button(
            "Download cell list",
            data=cell_lists,
            file_name="cell_list.csv",
            mime="text/csv",
        )
