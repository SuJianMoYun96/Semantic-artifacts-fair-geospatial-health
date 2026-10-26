"""Export the latest RIVM green-space percentages for Dutch administrative areas."""

import re
import time
import xml.etree.ElementTree as ET

import geopandas as gpd
import pandas as pd
import requests
import shapely
from pathlib import Path
import sys
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
from common_functions import save_csv, strip_xml_namespace
from config import OUTPUT_DIR




def latest_wfs_layers(base_url, keyword, levels):
    """Find the newest matching WFS layer for each requested administrative level."""
    capabilities_url = f"{base_url}?service=WFS&request=GetCapabilities"
    response = requests.get(capabilities_url, timeout=30)
    response.raise_for_status()
    root = ET.fromstring(response.content)

    layer_names = [
        elem.text
        for elem in root.iter()
        if strip_xml_namespace(elem.tag) == "Name" and elem.text
    ]

    latest = {}
    for layer in layer_names:
        layer_lower = layer.lower()
        if keyword.lower() not in layer_lower:
            continue

        year_match = re.search(r"20\d{2}", layer)
        if not year_match:
            continue
        year = int(year_match.group())

        for level in levels:
            if level.lower() in layer_lower:
                if level not in latest or year > latest[level]["year"]:
                    latest[level] = {"layer": layer, "year": year}
                break

    return latest


WFS_BASE_URL = "https://data.rivm.nl/geo/ank/wfs"
KEYWORD = "groenpercentage"
LEVELS = [ "wijk", "buurt"]
# "gemeente": ["gm_code", "gm_naam", "_mean", "_stdev", "_min", "_max"],
COLUMNS_BY_LEVEL = {

    "wijk": ["wk_code", "wk_naam", "gm_code", "_mean", "_stdev", "_min", "_max"],
    "buurt": ["bu_code", "bu_naam", "wk_code", "gm_code", "_mean", "_stdev", "_min", "_max"],
}
PERCENT_COLUMNS = ["_mean", "_stdev", "_min", "_max"]


def main():
    start = time.time()
    latest_layers = latest_wfs_layers(WFS_BASE_URL, KEYWORD, LEVELS)

    missing_levels = [level for level in LEVELS if level not in latest_layers]
    if missing_levels:
        raise ValueError(f"No matching WFS layers found for: {missing_levels}")

    for level, info in latest_layers.items():
        url = (
            f"{WFS_BASE_URL}?service=WFS&request=GetFeature&version=1.1.0"
            f"&typeName={info['layer']}"
        )
        gdf = gpd.read_file(url)

        existing_percent_columns = [
            column for column in PERCENT_COLUMNS if column in gdf.columns
        ]
        gdf[existing_percent_columns] = (
                gdf[existing_percent_columns].apply(pd.to_numeric, errors="coerce") / 100
        )

        selected = COLUMNS_BY_LEVEL[level]
        missing = [column for column in selected if column not in gdf.columns]
        if missing:
            raise KeyError(f"Missing columns in WFS layer {info['layer']}: {missing}")

        gdf["geometry"] = shapely.force_2d(gdf.geometry).to_wkt()
        gdf = gdf[selected + ["geometry"]].copy()

        output_path = save_csv(
            gdf,
            OUTPUT_DIR,
            f"area_proportion_green_space_{level}.csv",
        )
        print(f"Saved {level} ({info['year']}):", output_path)

    print(f"Finished administrative green-space processing in {time.time() - start:.2f} s")


if __name__ == "__main__":
    main()
