# Function consistency audit

`common_functions.py` now contains code that is genuinely reused across multiple scripts. Dataset-specific parsing, variable selection, URL parameters, and transformation logic remain in the dataset script where they are easiest to understand.

## 1. Repeated functions
| Function | Original file formats|
|---|---|
| `download()` | GeoPackage, GeoTIFF, TXT, XLSX, XML |
| `save_csv()` | All file formats|
| `get_json()` | TXT, and KNMI weather API |
| `latest_file_url()` | GeoPackage, GeoTIFF, XML |
| `unzip_file()` | GeoTIFF, TXT, GeoPackage (CBS administrative areas) |
| `find_file()` | GeoPackage, GeoTIFF, TXT |
| `export_gpkg_to_csv()` | GeoPackage |
| `strip_xml_namespace()` | XML|


## 2. Functions that remain dataset-specific
These functions are not moved into `common_functions.py` because they are tied to one source format or one dataset workflow:

- `gpkg_from_zip()` — CBS administrative districts and neighbourhoods only (GeoPackage).
- `export_latest_raster_zip_to_csv()` — RIVM data sources about area proportion of green space and NDVI in 10-meter grids only (GeoTIFF).
- `clean_text_columns()`, `latest_ndw_zip_url()`, `txt_to_filtered_dataframe()` — NDW traffic safety only (TXT).
- `export_excel_points()` — NDOV taxi stop only (XLSX).
- `flatten_xml()`, `read_nested_xml_gz()` — NDOV bus, ferry, metro, rail, and tram stops only (XML).
- `latest_wfs_layers()` — RIVM data sources about area proportion of green space in administrative districts and neighbourhoods only (XML).
- `shannon_entropy()`, `calculate_land_use_diversity()` — CBS data sources for area proportion of inland water, area proportion of residential areas, and land-use diversity (CSV).