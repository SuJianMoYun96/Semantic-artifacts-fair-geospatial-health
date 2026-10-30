"""Shared project configuration.

Set the OUTPUT_DIR environment variable to choose an output folder.
By default, generated files are saved in a CSVs folder next to this file.
"""

import os
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent

# Change this path to the folder containing the CSV files
user_output_dir = os.environ.get("OUTPUT_DIR")

OUTPUT_DIR = (
    Path(user_output_dir).expanduser()
    if user_output_dir
    else PROJECT_DIR / "CSVs"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
