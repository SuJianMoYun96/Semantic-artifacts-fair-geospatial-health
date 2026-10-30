"""Functions reused by more than one dataset-processing script."""

from pathlib import Path
import re
import zipfile
from urllib.parse import urljoin

import geopandas as gpd
import requests
import shapely
from bs4 import BeautifulSoup


def download(url, path, timeout=120, chunk_size=1024 * 1024):
    """Download a URL to *path* using streaming I/O.

    The destination folder is created automatically. A 1 MiB default chunk size
    is used so the same helper is suitable for both small and large files.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    response = requests.get(url, stream=True, timeout=timeout)
    response.raise_for_status()

    with path.open("wb") as file:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                file.write(chunk)

    return path


def save_csv(df, output_dir, filename):
    """Save a pandas/GeoPandas DataFrame as UTF-8 CSV."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / filename
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    return output_path


def get_json(base_url, endpoint="", headers=None, timeout=30, **params):
    """Send a GET request and return the decoded JSON response."""
    url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}" if endpoint else base_url
    response = requests.get(
        url,
        headers=headers,
        params=params or None,
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()


def latest_file_url(base_url, pattern=None, suffix=None, timeout=30):
    """Find the lexicographically latest matching file URL on a page/feed.

    Use either a regular-expression *pattern* or a filename *suffix*.
    Relative links are converted to absolute URLs with ``urljoin``.
    """
    if not pattern and not suffix:
        raise ValueError("Either pattern or suffix must be provided.")

    response = requests.get(base_url, timeout=timeout)
    response.raise_for_status()
    text = response.text

    if pattern:
        files = re.findall(pattern, text)
    else:
        soup = BeautifulSoup(text, "html.parser")
        files = [
            link["href"]
            for link in soup.find_all(["a", "link"], href=True)
            if link["href"].lower().endswith(suffix.lower())
        ]

    if not files:
        raise ValueError(f"No matching file found at {base_url}")

    return urljoin(base_url, sorted(files)[-1])


def unzip_file(zip_path, extract_dir):
    """Extract a ZIP archive and return the extraction folder."""
    zip_path = Path(zip_path)
    extract_dir = Path(extract_dir)
    extract_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as archive:
        archive.extractall(extract_dir)

    return extract_dir


def find_file(folder, keyword=None, suffix=None):
    """Find the first recursive file matching an optional keyword and suffix."""
    folder = Path(folder)

    for path in folder.rglob("*"):
        if not path.is_file():
            continue

        name = path.name.lower()
        keyword_match = keyword is None or keyword.lower() in name
        suffix_match = suffix is None or name.endswith(suffix.lower())

        if keyword_match and suffix_match:
            return path

    raise FileNotFoundError(
        f"No file found in {folder} with keyword={keyword!r} and suffix={suffix!r}"
    )


def strip_xml_namespace(tag):
    """Return the local XML tag name without its namespace prefix."""
    return tag.rsplit("}", 1)[-1]


def export_gpkg_to_csv(
    gpkg_path,
    output_dir,
    filename,
    columns,
    layer=None,
    rename=None,
    replace_values=None,
    extra_columns=None,
):
    """Select GeoPackage columns, convert geometry to 2D WKT, and save CSV.

    This helper is shared by the postcode-area and CBS administrative-area
    scripts. ``rename`` maps source column names to output column names.
    """
    gdf = gpd.read_file(gpkg_path, layer=layer)
    source_columns = list(columns)
    extra_columns = extra_columns or {}
    rename = rename or {}

    for column, value in extra_columns.items():
        gdf[column] = value

    required = source_columns + ["geometry"]
    missing = [column for column in required if column not in gdf.columns]
    if missing:
        raise KeyError(f"Missing columns in {gpkg_path}: {missing}")

    keep_before_rename = list(extra_columns) + source_columns + ["geometry"]
    gdf = gdf[keep_before_rename].copy()
    gdf = gdf.rename(columns=rename)

    if replace_values:
        gdf = gdf.replace(replace_values)

    output_columns = list(extra_columns) + [rename.get(c, c) for c in source_columns]
    gdf["geometry"] = shapely.force_2d(gdf.geometry).to_wkt()
    gdf = gdf[output_columns + ["geometry"]]

    output_path = save_csv(gdf, output_dir, filename)
    print("Saved:", output_path)
    return gdf