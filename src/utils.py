import os

import cv2
import numpy as np
import pandas as pd
import streamlit as st
from skimage.measure import regionprops_table


def read_html():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
    ) as fh:
        return fh.read()


@st.cache_data
def regionprops(seg, img_filtered, slider):
    def is_positive(x, y, slider_value=slider):
        return is_positive_individual(x, y, slider_value=slider_value)

    res = regionprops_table(
        seg,
        intensity_image=img_filtered,
        properties=("label",),
        extra_properties=(
            is_positive,
            percentage_positive,
        ),
    )
    # res ['is_positive'] = res["<lambda>"]
    return res


def merge_results(data, results):
    # df = subsample_data(data, subsample)
    results = pd.DataFrame(results)
    return data.merge(results, left_on="cell", right_on="label", how="left").fillna(False)


def is_positive(regionmask: np.ndarray, intensity_image: np.ndarray) -> float:
    """
    Computes whether the cell is positive or not
    """
    # regionmask

    return (intensity_image[regionmask] > 0).sum() / (
        regionmask == 1
    ).sum() > st.session_state.slider_value


def is_positive_individual(
    regionmask: np.ndarray, intensity_image: np.ndarray, slider_value=0.5
) -> float:
    """
    Computes whether the cell is positive or not
    """
    # regionmask

    return (intensity_image[regionmask] > 0).sum() / (
        regionmask == 1
    ).sum() > slider_value


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
