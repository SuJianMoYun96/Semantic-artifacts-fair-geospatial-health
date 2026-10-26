
"""dynamically locates the latest compressed XML export from NDOV,
   downloads and decompresses it,
   parses stopplace elements and flattens selected nested fields into columns;
   and creates point WKT from RD x/y coordinates."""
import gzip
import time
import xml.etree.ElementTree as ET
import geopandas as gpd
import pandas as pd
from pathlib import Path
import sys
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
from common_functions import download, latest_file_url, save_csv, strip_xml_namespace
from config import OUTPUT_DIR


def flatten_xml(node, prefix=""):
    row = {}
    for child in node:
        key = prefix + strip_xml_namespace(child.tag)
        if len(child):
            row.update(flatten_xml(child, key + "."))
        else:
            row[key] = child.text.strip() if child.text else ""
    return row


def read_nested_xml_gz(path, target_tag, columns):
    """Parse selected nested XML elements from a local XML.GZ file."""
    rows = []
    with gzip.open(path, "rb") as stream:
        for _, elem in ET.iterparse(stream, events=("end",)):
            if strip_xml_namespace(elem.tag) == target_tag:
                row = flatten_xml(elem)
                rows.append({column: row.get(column, "") for column in columns})
                elem.clear()

    df = pd.DataFrame(rows).fillna("")
    text_columns = df.select_dtypes(include="object").columns
    df[text_columns] = df[text_columns].apply(lambda col: col.str.strip())
    return df

TRANSPORT_BASE_URL = "https://data.ndovloket.nl/haltes/"
TRANSPORT_PATTERN = r"ExportCHB_\d{4}-\d{2}-\d{2}\.xml\.gz"

TRANSPORT_COLUMNS = [
    "ID",
    "stopplacename.publicname",
    "stopplacename.validfrom",
    "stopplacetype",
    "stopplacecode",
    "stopplacelocation.rd-x",
    "stopplacelocation.rd-y",
    "stopplacename.street",
    "stopplacename.town",
    "quays.quay.ID",
    "quays.quay.quaylocationdata.validfrom",
    "quays.quay.validfrom",
    "quays.quay.quaycode",
    "quays.quay.quaynamedata.quayname",
    "quays.quay.quaytransportmodes.transportmodedata.transportmode",
    "quays.quay.quaylocationdata.rd-x",
    "quays.quay.quaylocationdata.rd-y",
    "quays.quay.quaylocationdata.street",
    "quays.quay.quaylocationdata.town",
    "quays.quay.quaymunicipality.municipalitycode",
]
def main():
    start = time.time()
    transport_url = latest_file_url(
        base_url=TRANSPORT_BASE_URL,
        pattern=TRANSPORT_PATTERN,
    )
    source_path = OUTPUT_DIR / "downloads" / transport_url.rsplit("/", 1)[-1]
    download(transport_url, source_path)

    public_transport = read_nested_xml_gz(
        source_path,
        target_tag="stopplace",
        columns=TRANSPORT_COLUMNS,
    )

    geometry = gpd.GeoSeries(
        gpd.points_from_xy(
            pd.to_numeric(public_transport["stopplacelocation.rd-x"], errors="coerce"),
            pd.to_numeric(public_transport["stopplacelocation.rd-y"], errors="coerce"),
        )
    )
    public_transport["geometry"] = geometry.to_wkt()

    keep = TRANSPORT_COLUMNS + ["geometry"]
    public_transport = public_transport[keep].copy()
    output_path = save_csv(
        public_transport,
        OUTPUT_DIR,
        "public_transport_stops_not_WGS84.csv",
    )

    print("Saved:", output_path)
    print(f"Finished public-transport processing in {time.time() - start:.2f} s")


if __name__ == "__main__":
    main()
