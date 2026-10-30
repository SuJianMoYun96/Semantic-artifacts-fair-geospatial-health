"""Shared project configuration.

Edit OUTPUT_DIR here if you want generated files to be written elsewhere.
The default keeps all generated files in a local ./CSVs folder next to the scripts.
"""

from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
# Change this path to the folder containing the CSV files
OUTPUT_DIR = Path(
    r"D:\4 interoperiablity layer\ontop mapping\mapping_CSVs_9.29"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)