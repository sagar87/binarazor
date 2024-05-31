import sys
from pathlib import Path

import streamlit as st

from config import App

st.set_page_config(
    page_title=f"{App.PROJECT} | Binarazor", page_icon=f"{App.PAGE_ICON}", layout="wide"
)


sys.path.append(str(Path(__file__).resolve().parent.parent))
import pandas as pd

from database import get_channels, get_thresholds_by_channel


def get_data():
    data = []
    channels = get_channels()
    for channel in channels:
        df = get_thresholds_by_channel(channel)
        df["status_new"] = df.status.map(
            {"reviewed": "✅", "bad": "❌", None: "❓"}
        ).fillna("❓")
        data.append(df)

    df = pd.concat(data)
    return df.pivot(index="sample", columns="channel", values="status_new")


df = get_data()
st.table(df)
