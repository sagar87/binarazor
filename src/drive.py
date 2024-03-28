import os

import pandas as pd
import s3fs
import streamlit as st
import xarray as xr
from dotenv import load_dotenv
from natsort import natsorted
from PIL import Image

load_dotenv(".env")

AWS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_KEY_SECRET = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_URL = os.getenv("AWS_URL")
AWS_PATH = os.getenv("AWS_PATH")

fs = s3fs.S3FileSystem(anon=False, client_kwargs={"endpoint_url": AWS_URL})


@st.cache_data
def get_zarr_dict():
    file_dict = {
        f.split("/")[-1].split(".")[0]: f
        for f in fs.ls(AWS_PATH)
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
    for path in natsorted([f for f in fs.glob(f"{AWS_PATH}/*/*.csv")]):
        sample_dict[path.split("/")[-2]] = path
    return sample_dict


def get_image_dict(sample):
    """Returns image dict."""
    image_paths = natsorted([f for f in fs.glob(f"{AWS_PATH}/{sample}/*.tiff")])
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


# def get_data(path):
# return pd.read_csv(path)


# @st.cache_data
# def get_graphs(path):
#     paths = []
#     for f in natsorted(fs.ls(path)):
#         # print(f)
#         graph = "_".join(f.split("_")[:-1])
#         # print('FILE', f.split("_"))
#         if graph not in paths:
#             paths.append(graph)

#     return paths


# @st.cache_data
# def get_inits(path, graph):
#     return natsorted([f for f in fs.ls(path) if f.startswith(graph)])


# @st.cache_data
# def get_files(path):
#     paths = natsorted([f for f in fs.ls(path)])
#     file_dict = defaultdict(list)
#     for p in paths:
#         fname = p.split("/")[-1]
#         url = AWS_URL + "/" + p
#         file_dict["_".join(fname.split("_")[1:-1])].append(url)

#     return file_dict


# @st.cache_data
# def get_long_files(path, graph):
#     # print(path)
#     paths = natsorted([f for f in fs.ls(path) if f.startswith(graph)])
#     # print(paths)
#     file_dict = dict()
#     for p in paths:
#         init = p.split("/")[-1].split('_')[-1]
#         files = natsorted([f for f in fs.ls(p)])
#         file_dict[init] = [ AWS_URL + "/" + n for n in files ]
#         # print(init, files)
#     return file_dict

# def get_sub_dirs(path):
#     """Returns sample paths dict."""

#     sample_data = defaultdict(OrderedDict)
#     for path in natsorted(fs.glob(os.path.join(path, "*"))):
#         file = os.path.basename(os.path.normpath(path))
#         name, ext = os.path.splitext(file)
#         if ext:
#             continue

#         splitted = file.split("_")
#         sub, source_node, init = "_".join(splitted[:-2]), splitted[-2], splitted[-1]
#         sample_data[sub][int(init)] = path

#     return sample_data

if __name__ == "__main__":
    import pdb

    pdb.set_trace()
