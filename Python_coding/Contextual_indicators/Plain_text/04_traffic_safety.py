
"""BRON registered traffic accidents:"""
"""Queries the NDW data source API,
       selects the latest BRON archive by year,
       extracts the accident TXT file,
       retains the fields required for the traffic-accident observations."""
"""Selected accident fields:    
    VKL_NUMMER: Unique identifier of the traffic accident.
    DATUM_VKL: Accident date.
    JAAR_VKL: Year in which the accident occurred.
    TIJDSTIP: Time of the accident.
    DDL_ID: Part of the day in which the accident occurred.
    JTE_ID: Unique identifier of the junction where the accident occurred.
    WVK_ID: Unique identifier of the road segment where the accident occurred.
    HECTOMETER: Hectometre marker value at the accident location.
    FK_VELD5: Link field used to connect the accident record to the Point Locations dataset.
    HUISNUMMER: House number at the accident location.
    GME_ID: Unique identifier of the municipality in which the accident occurred.
    GME_NAAM: Name of the municipality in which the accident occurred.
    PVE_CODE: Province code.
    PVE_NAAM: Province name.
    KDD_NAAM: Name of the framework act area in which the accident occurred.
    PLT_NAAM: Name of the police district in which the accident occurred.
    DIENSTCODE: Code of the sub-region within the region.
    DIENSTNAAM: Name of the sub-region within the region.
    DISTRCODE: District code.
    DISTRNAAM: District name.
    DAGTYPE: Indicates whether the accident occurred on a weekday or weekend.
"""

"""BRON traffic-accident point locations:"""
"""Extracts the `puntlocaties` TXT file from the same BRON archive, 
   selects the location identifier and coordinate fields, 
   and converts the x/y coordinates to point WKT.
"""

import time
from pathlib import Path

import pandas as pd
from shapely.geometry import Point
import sys
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
from common_functions import download, find_file, get_json, save_csv, unzip_file
from config import OUTPUT_DIR


def clean_text_columns(df):
    """Strip whitespace from text columns while preserving non-text columns."""
    df = df.fillna("")
    return df.apply(lambda col: col.str.strip() if col.dtype == "object" else col)


def latest_ndw_zip_url(api_url, params, base_url):
    """Find the latest ZIP dataset in the NDW API response."""
    data = get_json(api_url, **params)
    downloads = data["docs"][0]["downloads"]["downloads"]

    zip_files = [
        item["dataset"]
        for item in downloads
        if item.get("dataset", {}).get("filename", "").lower().endswith(".zip")
    ]
    if not zip_files:
        raise ValueError("No ZIP dataset found in the NDW API response.")

    latest = max(zip_files, key=lambda item: item.get("year") or 0)
    return base_url + latest["url"], latest["filename"]


def txt_to_filtered_dataframe(txt_path, columns, encoding="utf-8"):
    """Read a comma-delimited TXT file and retain only requested columns."""
    df = pd.read_csv(
        txt_path,
        dtype=str,
        sep=",",
        quotechar='"',
        encoding=encoding,
        low_memory=False,
    )
    df.columns = df.columns.str.lstrip("\ufeff").str.strip()

    existing = [column for column in columns if column in df.columns]
    missing = [column for column in columns if column not in df.columns]
    if missing:
        print("Missing columns:", missing)

    return clean_text_columns(df[existing].copy())

def main():
    start = time.time()

    NDW_BASE = "https://verkeersveiligheid.ndw.nu"
    NDW_API = f"{NDW_BASE}/cms/api/dataset"
    params = {
        "where[slug][equals]": "bestand-geregistreerde-ongevallen-in-nederland-bron",
        "depth": 5,
        "sort": "-createdAt",
        "limit": 1,
        "page": 1,
    }

    download_url, filename = latest_ndw_zip_url(NDW_API, params, NDW_BASE)
    zip_path = OUTPUT_DIR / "downloads" / "traffic_safety" / filename
    extract_dir = OUTPUT_DIR / "downloads" / "traffic_safety" / Path(filename).stem

    download(download_url, zip_path)
    unzip_file(zip_path, extract_dir)

    accident_path = find_file(extract_dir, keyword="ongevallen", suffix=".txt")
    location_path = find_file(extract_dir, keyword="puntlocaties", suffix=".txt")

    accident_columns = [
        "VKL_NUMMER", "DATUM_VKL", "JAAR_VKL", "TIJDSTIP", "DDL_ID", "JTE_ID",
        "WVK_ID", "HECTOMETER", "FK_VELD5", "HUISNUMMER", "GME_ID", "GME_NAAM",
        "PVE_CODE", "PVE_NAAM", "KDD_NAAM", "PLT_NAAM", "DIENSTCODE", "DIENSTNAAM",
        "DISTRCODE", "DISTRNAAM", "DAGTYPE",
    ]
    traffic_safety_df = txt_to_filtered_dataframe(accident_path, accident_columns)
    accident_output = save_csv(traffic_safety_df, OUTPUT_DIR, "traffic_safety_filter.csv")

    location_columns = ["FK_VELD5", "X_COORD", "Y_COORD"]
    location_df = txt_to_filtered_dataframe(location_path, location_columns)
    location_df["coordinates_wkt"] = location_df.apply(
        lambda row: Point(
            float(row["X_COORD"]),
            float(row["Y_COORD"])
        ).wkt,
        axis=1,
    )
    location_output = save_csv(
        location_df,
        OUTPUT_DIR,
        "traffic_safety_location_filter.csv",
    )

    print("Saved:", accident_output)
    print("Saved:", location_output)
    print(f"Finished traffic-safety processing in {time.time() - start:.2f} s")


if __name__ == "__main__":
    main()