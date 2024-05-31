from enum import Enum

from database import (
    get_all_samples,
    get_channels,
    get_reviewers,
    get_statistics,
    get_total_samples,
    paginated_samples,
)
from drive import get_zarr_dict


class Data:
    REVIEWERS = get_reviewers()
    NUM_SAMPLES = get_total_samples()
    CHANNELS = get_channels()
    ZARR_DICT = get_zarr_dict()


class Vars:
    _REVIEWER = "_reviewer"
    REVIEWER = "reviewer"
    _CHANNEL = "_channel"
    CHANNEL = "channel"
    _PAGE = "_page"
    PAGE = "page"
    _DOTSIZE_NEG = "_dotsize_neg"
    DOTSIZE_NEG = "dotsize_neg"
    _DOTSIZE_POS = "_dotsize_pos"
    DOTSIZE_POS = "dotsize_pos"
    _POSITIVE = "positive"
    POSITIVE = "positive"
    SAMPLES = "samples"
    STATISTICS = "statistics"
    LOWER_QUANTILE = "lower_quantile"
    UPPER_QUANTILE = "upper_quantile"
    SLIDER = "slider"
