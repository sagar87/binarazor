import os

import cv2
import numpy as np
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv(".env")

HTML_PATH = os.getenv("HTML_PATH")


def read_html():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
    ) as fh:
        return fh.read()


@st.cache_data
def subsample_data(data, subsample):
    if subsample != 0:
        df = data.loc[
            data.sample(
                min(data.shape[0], int(subsample)),
                random_state=42,
            ).index
        ]
    else:
        df = data
    return df


def merge_results(data, subsample, results):
    df = subsample_data(data, subsample)
    results = pd.DataFrame(results)
    return df.merge(results, left_on="cell", right_on="label", how="left")


def is_positive(regionmask: np.ndarray, intensity_image: np.ndarray) -> float:
    """
    Computes whether the cell is positive or not
    """
    # regionmask

    return (intensity_image[regionmask] > 0).sum() / (
        regionmask == 1
    ).sum() > st.session_state.slider_value


def percentage_positive(regionmask: np.ndarray, intensity_image: np.ndarray) -> float:
    """
    Computes whether the cell is positive or not
    """
    # regionmask

    return (intensity_image[regionmask] > 0).sum() / (regionmask == 1).sum()


def normalise_image(img, lower=0.03, upper=0.998, func=np.quantile):
    low = func(img, lower)
    high = func(img, upper)
    alpha = 255.0 / ((high - low) + 1e-6)
    return cv2.convertScaleAbs(img[::-1], alpha=alpha)
