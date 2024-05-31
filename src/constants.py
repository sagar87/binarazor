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
