
"""
- Downloads and extracts the ZIP archive,
- Extracts the archive to the configured output directory,
- Finds the GeoPackage (`.gpkg`) file in the extracted folder,
- Reads the district (`wijken`) and neighbourhood (`buurten`) layers,
- Selects fields;
- Adds a `jaar` column containing the corresponding data source year,
- Converts geometric information to 2D WKT, removing any Z dimension if present,
- Exports each administrative level as a separate CSV file.
"""

"""Selected fields: `jaar` (year), `geometry`, and the following year-specific attributes:
2024:
- `wijken`: `wijknaam`, `wijkcode`, `gemeentecode`, `gemeentenaam`
- `buurten`: `buurtcode`, `buurtnaam`, `wijkcode`, `gemeentecode`, `gemeentenaam`

2026:
- `wijken`: `wk_code`, `wk_naam`, `gm_code`, `gm_naam`
- `buurten`: `bu_code`, `bu_naam`, `wk_code`, `gm_code`, `gm_naam`"""

import time
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from common_functions import download, export_gpkg_to_csv, find_file, unzip_file
from config import OUTPUT_DIR


CBS_URLS = {
    2024: "https://geodata.cbs.nl/files/Wijkenbuurtkaart/WijkBuurtkaart_2024_v2.zip",
    2026: "https://geodata.cbs.nl/files/Wijkenbuurtkaart/WijkBuurtkaart_2026_v0.zip",
}

"""Keep the original CBS source column names for each year.
   No renaming is applied between the 2024 and 2026 schemas.
   2024 {"gemeenten": ["gemeentecode","gemeentenaam"]
   2026 {"gemeenten": ["gm_code","gm_naam"]"""
CBS_LAYERS = {
    2024: {
        "wijken": ["wijknaam", "wijkcode", "gemeentecode", "gemeentenaam"],
        "buurten": ["buurtcode", "buurtnaam", "wijkcode", "gemeentecode", "gemeentenaam"],
    },
    2026: {
        "wijken": ["wk_code", "wk_naam", "gm_code", "gm_naam"],
        "buurten": ["bu_code", "bu_naam", "wk_code", "gm_code", "gm_naam"],
    },
}

def gpkg_from_zip(url, year):
    zip_path = OUTPUT_DIR / f"WijkBuurtkaart_{year}.zip"
    extract_dir = OUTPUT_DIR / f"WijkBuurtkaart_{year}"
    download(url, zip_path)
    unzip_file(zip_path, extract_dir)
    return find_file(extract_dir, suffix=".gpkg")


def main():
    start = time.time()

    for year, url in CBS_URLS.items():
        gpkg_path = gpkg_from_zip(url, year)

        for layer, columns in CBS_LAYERS[year].items():
            export_gpkg_to_csv(
                gpkg_path=gpkg_path,
                output_dir=OUTPUT_DIR,
                layer=layer,
                columns=columns,
                filename=f"{layer}_{year}.csv",
                extra_columns={"jaar": year},
            )

    print(f"Finished administrative-area processing in {time.time() - start:.2f} s")


if __name__ == "__main__":
    main()