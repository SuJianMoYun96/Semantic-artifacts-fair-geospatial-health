
"""Finds the latest GeoPackage link in the Atom feed,
   downloads it,
   selects fields,
   replaces the supplied missing-value codes with `NaN`,
   and converts geometric information to WKT."""

"""Selected fields: 
        1: postcode (e.g., 1095 in Amsterdam);
        2: geometry (area coordinates);
        3: address density within the postcode area."""

import sys
from pathlib import Path

import time
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from common_functions import download, export_gpkg_to_csv, latest_file_url
from config import OUTPUT_DIR

POSTCODE4_ATOM_URL = (
    "https://service.pdok.nl/cbs/postcode4/atom/postcode4_numeriek_deel.xml"
)


def main():
    start = time.time()

    """Find the download URL for the most recent year's GeoPackage file containing postcode areas."""
    postcode4_url = latest_file_url(
        base_url=POSTCODE4_ATOM_URL,
        suffix=".gpkg",
    )

    gpkg_path = OUTPUT_DIR / "postcode4_latest.gpkg"
    download(postcode4_url, gpkg_path)

    export_gpkg_to_csv(
        gpkg_path=gpkg_path,
        output_dir=OUTPUT_DIR,
        layer=None,
        columns=["omgevingsadressendichtheid","postcode"],
        rename={"omgevingsadressendichtheid": "addressdensity"},
        replace_values={"address_density": {-99995: np.nan, -99997: np.nan}},
        filename="postcode4_data_not_WGS84.csv",
    )

    print(f"Finished postcode-4 processing in {time.time() - start:.2f} s")


if __name__ == "__main__":
    main()