import argparse
import sys
from pathlib import Path

sys.path.append("/home/voehring/voehring/opt/spatialproteomics")
import numpy as np
import pandas as pd
import spatialproteomics as sp
import xarray as xr
import zarr
from tqdm import tqdm


def parse_arguments():
    parser = argparse.ArgumentParser(description="Prepare data script.")
    parser.add_argument(
        "--input-folder", type=str, required=True, help="Path to the input folder."
    )
    parser.add_argument(
        "--output-folder", type=str, required=True, help="Path to the output folder."
    )
    return parser.parse_args()


def create_expression_matrix(sprot):
    all_expression = []

    for k, v in tqdm(sprot.items()):
        # v = v.pp.drop_layers(['_labels', '_obs']).pp.add_observations()
        #
        # data = v
        data = v.pp.add_quantification(func=sp.arcsinh_median_intensity)
        dfa = pd.DataFrame(
            data._obs.sel(features=["centroid-1", "centroid-0"]).values,
            columns=["X", "Y"],
            index=data.coords["cells"].values.tolist(),
        )
        dfb = pd.DataFrame(
            data._intensity.values,
            columns=[
                ch.replace("/", "-") for ch in data.coords["channels"].values.tolist()
            ],
            index=data.coords["cells"].values.tolist(),
        )
        dfc = (
            dfa.merge(dfb, left_index=True, right_index=True)
            .assign(sample=k)
            .reset_index()
            .rename(columns={"index": "cell"})
        )
        all_expression.append(dfc)

    final_df = pd.concat(all_expression)
    return final_df


def create_threshold_matrix(expression_df):
    threshold = (
        expression_df.drop(columns=["cell", "X", "Y"])
        .melt("sample")
        .drop(columns="value")
        .rename(columns={"variable": "channel"})
        .assign(threshold=float("nan"))
        .assign(status=float("nan"))
        .assign(reviewer=float("nan"))
        .assign(lower=float("nan"))
        .assign(upper=float("nan"))
        .assign(cells=float("nan"))
        .drop_duplicates()
        .reset_index(drop=True)
    )
    return threshold


def prepare_zarrs(sprot, base_path):
    channels = list(sprot.values())[0].coords["channels"].values.tolist()
    compressor = zarr.Blosc(cname="zstd", clevel=3, shuffle=2)

    for ch in tqdm(channels):
        # print('processing', ch)
        image_array = []
        sample_array = []
        for sname, sdata in sprot.items():
            image_data = sdata._image.sel(channels=ch).values
            image_array.append(np.expand_dims(image_data, 0))
            sample_array.append(sname)

        image_array = np.concatenate(image_array, 0)
        sdata_plot = sp.load_image_data(image_array, channel_coords=sample_array)
        sdata_plot["_image"] = sdata_plot["_image"].chunk(
            {"channels": 1, "x": sdata_plot.sizes["x"], "y": sdata_plot.sizes["y"]}
        )
        enc = {x: {"compressor": compressor} for x in sdata_plot}
        sdata_plot.to_zarr(base_path / f'{ch.replace("/", "-")}.zarr', encoding=enc)

    image_array = []
    sample_array = []
    for sname, sdata in sprot.items():
        image_data = sdata._segmentation.values.squeeze()
        image_array.append(np.expand_dims(image_data, 0))
        sample_array.append(sname.split("/")[-1].replace(".zarr", ""))

    image_array = np.concatenate(image_array, 0)
    sdata_plot = sp.load_image_data(image_array, channel_coords=sample_array)
    sdata_plot["_image"] = sdata_plot["_image"].chunk(
        {"channels": 1, "x": sdata_plot.sizes["x"], "y": sdata_plot.sizes["y"]}
    )
    enc = {x: {"compressor": compressor} for x in sdata_plot}
    sdata_plot.to_zarr(base_path / "segmentation.zarr", encoding=enc)


def main(input_folder, output_folder):
    # Example logic: Create the output folder if it doesn't exist

    input_path = Path(input_folder)
    output_path = Path(output_folder)

    zarrs = input_path.glob("*.zarr")
    images = {zarr.stem: xr.open_zarr(zarr) for zarr in zarrs}

    expression_matrix = create_expression_matrix(images)
    thresholds_matrix = create_threshold_matrix(expression_matrix)

    expression_matrix.to_csv(output_path / "expression.csv")
    thresholds_matrix.to_csv(output_path / "thresholds.csv")

    prepare_zarrs(images, output_path)


if __name__ == "__main__":
    args = parse_arguments()
    input_folder = args.input_folder
    output_folder = args.output_folder
    main(input_folder, output_folder)
