"""In the Netherlands, haltetaxi refers to a demand-responsive taxi service that picks up and drops off passengers at designated stops, complementing regular public transport services."""
"""Reads all valid Excel sheets, 
   identifies the actual header using the haltenr keyword, 
   keeps the selected fields, 
   converts x/y coordinates to WKT, 
   and optionally removes duplicate geometries."""
"""The URL is a fixed workbook URL in the supplied code rather than a dynamic “latest file” endpoint. If NDOV changes the workbook name, update TAXI_URL in this script."""

import time
import geopandas as gpd
import pandas as pd
from pathlib import Path
import sys
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
from common_functions import download, save_csv
from config import OUTPUT_DIR


TAXI_URL = (
    "https://data.ndovloket.nl/htz/"
    "Rittenplanning%20haltetaxi%20ingang%204%20nov%209292%20format%20versie%2046.42.xlsx"
)


def export_excel_points(
    excel_path,
    output_filename,
    columns,
    x_col,
    y_col,
    header_keyword,
    header_search_col=0,
    sheet_name_col="sheet",
    drop_duplicate_geometry=True,
):
    """Read valid Excel sheets, create POINT WKT, and save a combined CSV."""
    workbook = pd.ExcelFile(excel_path)
    tables = []

    for sheet in workbook.sheet_names:
        raw = pd.read_excel(excel_path, sheet_name=sheet, header=None)
        header_rows = raw[
            raw.iloc[:, header_search_col]
            .astype(str)
            .str.contains(header_keyword, case=False, na=False)
        ]
        if header_rows.empty:
            continue

        df = pd.read_excel(
            excel_path,
            sheet_name=sheet,
            header=header_rows.index[0],
        )
        existing_columns = [column for column in columns if column in df.columns]
        df = df[existing_columns].copy()
        df = df.dropna(subset=[header_keyword])
        df[sheet_name_col] = sheet
        tables.append(df)

    if not tables:
        raise ValueError("No valid sheets found in the haltetaxi workbook.")

    result = pd.concat(tables, ignore_index=True)
    geometry = gpd.GeoSeries(
        gpd.points_from_xy(
            pd.to_numeric(result[x_col], errors="coerce"),
            pd.to_numeric(result[y_col], errors="coerce"),
        )
    )
    result["geometry"] = geometry.to_wkt()

    if drop_duplicate_geometry:
        result = result.drop_duplicates(subset=["geometry"])

    output_path = save_csv(result, OUTPUT_DIR, output_filename)
    return result, output_path


def main():
    start = time.time()
    taxi_file = OUTPUT_DIR / "downloads" / "taxi.xlsx"
    download(TAXI_URL, taxi_file)

    _, output_path = export_excel_points(
        excel_path=taxi_file,
        output_filename="clean_taxi.csv",
        columns=["haltenr", "coord x", "coord y", "plaats, halte"],
        x_col="coord x",
        y_col="coord y",
        header_keyword="haltenr",
    )

    print("Saved:", output_path)
    print(f"Finished haltetaxi processing in {time.time() - start:.2f} s")


if __name__ == "__main__":
    main()
