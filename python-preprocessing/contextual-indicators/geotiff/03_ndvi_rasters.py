
""" Normalized Difference Vegetation Index (NDVI) data source:
       Finds the latest available ZIP containing `ndvi`,
       extracts the GeoTIFF, processes it block by block,
       and converts valid raster cells to polygon WKT.
       NDVI values are retained unchanged."""
""" Data source for area proportion of green space in 10-meter raster: 
       Finds the latest available ZIP containing `groenkaart`, 
       extracts the GeoTIFF, 
       processes it block by block, 
       converts valid raster cells to polygon WKT, 
       and divides values by 100."""
import zipfile
import time
import numpy as np
import pandas as pd
import rasterio
from rasterio.features import shapes
from shapely.geometry import shape
from pathlib import Path
import sys
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from common_functions import download, find_file, latest_file_url, unzip_file
from config import OUTPUT_DIR




def unzip_tif_only(zip_path, extract_dir):
    extract_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as archive:
        tif_files = [
            name for name in archive.namelist()
            if name.lower().endswith(".tif")
        ]

        if not tif_files:
            raise FileNotFoundError(
                f"No .tif file found in ZIP archive: {zip_path}"
            )

        for tif_file in tif_files:
            archive.extract(tif_file, extract_dir)
def export_latest_raster_zip_to_csv(
    base_url,
    pattern,
    zip_filename,
    extract_folder,
    tif_keyword,
    output_prefix,
    value_col="value",
    geometry_col="geometry",
    divide_value_by_100=False,
    skip_values=None,
):
    """Convert the selected raster to polygon WKT in block-wise CSV writes."""
    skip_values = set(skip_values or [])
    """Download latest raster ZIP, extract selected TIF, convert raster to polygon WKT, and save CSV."""
    url = latest_file_url(base_url=base_url, pattern=pattern)
    """Values in this list will be skipped when converting raster cells to polygons"""
    zip_path = OUTPUT_DIR / "downloads" / zip_filename
    extract_dir = OUTPUT_DIR / "downloads" / extract_folder

    download(url, zip_path)

    unzip_tif_only(zip_path, extract_dir)

    """Find the TIF file inside the extracted folder."""
    tif_path = find_file(extract_dir, keyword=tif_keyword, suffix=".tif")

    output_path = OUTPUT_DIR / f"{output_prefix}.csv"
    """Used to write the CSV header only once when appending chunks."""
    first_write = True

    with rasterio.open(tif_path) as src:
        for _, window in src.block_windows(1):
            band = src.read(1, window=window)
            """Get the spatial transform for the current block."""
            transform = src.window_transform(window)
            """Get the NoData value defined in the raster."""
            nodata = src.nodata
            """If no NoData value is defined, keep all non-NaN cells."""
            """Otherwise, keep cells that are not NoData and not NaN."""
            if nodata is None or (isinstance(nodata, float) and np.isnan(nodata)):
                mask = ~np.isnan(band)
            else:
                mask = (band != nodata) & (~np.isnan(band))
            """Store polygon-value records for this raster block."""
            records = []
            """Convert raster regions with the same value into polygon geometries."""
            """Convert the polygon geometry to WKT and store it with its raster value."""
            for geometry, value in shapes(band, mask=mask, transform=transform):
                if value in skip_values:
                    continue
                records.append(
                    {
                        geometry_col: shape(geometry).wkt,
                        value_col: value,
                    }
                )
            """Skip this block if it produced no valid polygons"""
            if not records:
                continue
            """Convert records from the current block to a DataFrame."""
            df = pd.DataFrame(records)
            """Convert percentage values to proportions if needed."""
            if divide_value_by_100:
                df[value_col] = pd.to_numeric(df[value_col], errors="coerce") / 100

            df[[geometry_col, value_col]].to_csv(
                output_path,
                mode="w" if first_write else "a",
                index=False,
                header=first_write,
                encoding="utf-8-sig",
            )
            first_write = False

    if first_write:
        raise ValueError(f"No valid raster values were written from {tif_path}")

    return output_path
"""Base URL for RIVM raster datasets"""
RIVM_DATA_URL = "https://data.rivm.nl/data/ank/"

"""Configuration for downloading and processing the latest RIVM raster datasets."""
RASTER_DATASETS = [
     {
        "name": "ndvi_raster",
        "base_url": RIVM_DATA_URL,
        "pattern": r'href="([^"]*ndvi[^"]*\.zip)"',
        "zip_filename": "ndvi_latest.zip",
        "extract_folder": "ndvi_latest",
        "tif_keyword": "ndvi",
        "output_prefix": "raster_ndvi",
        "divide_value_by_100": False,
        "skip_values": [],
    },
]

def main():
    start = time.time()

    for dataset in RASTER_DATASETS:
        print(f"Processing {dataset['name']}...")
        settings = {key: value for key, value in dataset.items() if key != "name"}
        output_path = export_latest_raster_zip_to_csv(**settings)
        print("Saved:", output_path)

    print(f"Finished raster processing in {time.time() - start:.2f} s")


if __name__ == "__main__":
    main()
