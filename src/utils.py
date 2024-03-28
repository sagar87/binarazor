import os

import numpy as np
import streamlit as st
from dotenv import load_dotenv

load_dotenv(".env")

HTML_PATH = os.getenv("HTML_PATH")


def read_html():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
    ) as fh:
        return fh.read()


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
