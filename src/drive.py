import pandas as pd
import s3fs
import streamlit as st
import xarray as xr
from natsort import natsorted
from PIL import Image

from config import Bucket

fs = s3fs.S3FileSystem(anon=False, client_kwargs={"endpoint_url": Bucket.AWS_URL})


@st.cache_data
def get_zarr_dict():
    file_dict = {
        f.split("/")[-1].split(".")[0]: f
        for f in fs.ls(Bucket.AWS_PATH)
        if f.endswith(".zarr")
    }
    return file_dict


@st.cache_data
def read_zarr(filename):
    store = s3fs.S3Map(root=filename, s3=fs, check=False)
    return xr.open_zarr(store=store, consolidated=True)


@st.cache_data
def read_zarr_sample(filename, sample):
    store = s3fs.S3Map(root=filename, s3=fs, check=False)
    zarr = xr.open_zarr(store=store, consolidated=True)
    array = zarr._image.sel(channels=sample).values.squeeze()
    return array


@st.cache_data
def get_samples():
    """Returns sample paths dict."""
    sample_dict = {}
    for path in natsorted([f for f in fs.glob(f"{Bucket.AWS_PATH}/*/*.csv")]):
        sample_dict[path.split("/")[-2]] = path
    return sample_dict


def get_image_dict(sample):
    """Returns image dict."""
    image_paths = natsorted([f for f in fs.glob(f"{Bucket.AWS_PATH}/{sample}/*.tiff")])
    image_dict = {img.split("/")[-1].split(".")[0]: img for img in image_paths}

    # print(image_dict)
    return image_dict


@st.cache_data(ttl=3600)
def get_data(filename):
    df = pd.read_csv(fs.open(filename, mode="rb"), index_col=0)
    return df


@st.cache_data(ttl=3600)
def get_image(filename):
    img = Image.open(fs.open(filename, mode="rb"))
    return img


if __name__ == "__main__":
    import pdb

    pdb.set_trace()
