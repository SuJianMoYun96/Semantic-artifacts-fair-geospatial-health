import numpy as np
import pandas as pd
from pathlib import Path
import sys
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
from config import OUTPUT_DIR

# This Python script is used to download the required CSV files from the source website and to calculate land-use diversity based on the downloaded data.
# ============================================================
# Define the functions for calculationg land-use diversity
# ============================================================

# Calculate normalized Shannon entropy for one row.
# This is used as the land-use diversity indicator.
def shannon_entropy(row, landuse_cols, total_col):
    areas = pd.to_numeric(row[landuse_cols], errors="coerce")
    areas = areas.dropna()
    areas = areas[areas > 0]

    # If no valid land-use area exists, return missing value.
    if areas.empty:
        return None

    total = pd.to_numeric(row[total_col], errors="coerce")

    # If total area is missing or zero, entropy cannot be calculated.
    if pd.isna(total) or total <= 0:
        return None

    # Convert land-use areas to proportions of the total area.
    proportions = (areas / total).astype(float).to_numpy()

    # If only one land-use category exists, diversity is zero.
    if len(proportions) == 1:
        return 0

    # Normalized Shannon entropy.
    return -np.sum(proportions * np.log(proportions)) / np.log(len(proportions))


# Read a CSV file, convert selected land-use columns to numeric values,
# calculate land-use diversity, and save the result to a new CSV file.
def calculate_land_use_diversity(
    input_path,
    output_path,
    landuse_cols,
    total_area_col,
    diversity_method=shannon_entropy,
    id_col=None,
    repeated_header_value=None,
    sep=";",
    encoding="utf-8-sig",
):
    df = pd.read_csv(
        input_path,
        sep=sep,
        encoding=encoding,
    )

    # Remove repeated header rows if they exist inside the CSV.
    if id_col and repeated_header_value and id_col in df.columns:
        df = df[df[id_col] != repeated_header_value].copy()

    # Convert all columns required for the calculation to numeric values.
    required_numeric_cols = [*landuse_cols, total_area_col]
    existing_numeric_cols = [col for col in required_numeric_cols if col in df.columns]

    df[existing_numeric_cols] = (
        df[existing_numeric_cols]
        .astype(str)
        .replace(",", ".", regex=True)
        .apply(pd.to_numeric, errors="coerce")
    )

    # Keep only land-use columns that actually exist in the dataset.
    existing_landuse_cols = [col for col in landuse_cols if col in df.columns]

    # Calculate land-use diversity for each row.
    df["land_use_diversity"] = df.apply(
        diversity_method,
        axis=1,
        landuse_cols=existing_landuse_cols,
        total_col=total_area_col,
    )

    # Save the dataset with the new land-use diversity column.
    df.to_csv(output_path, index=False, encoding="utf-8-sig")

    return df


# Input and output CSV files
input_path = OUTPUT_DIR / "CBS data no calculation.csv"
output_path = OUTPUT_DIR / "CBS data calculation.csv"

# Column containing the total land and water area.
total_area_col = "TotaalLandEnWater_4"

# Land-use area columns used to calculate land-use diversity.
landuse_cols = [
    "TotaalRecreatiefTerrein_27",
    "Woonterrein_15",
    "DetailhandelEnHoreca_16",
    "SociaalCultureleVoorziening_18",
    "OpenbareVoorziening_17",
]


# Run the calculation.
df = calculate_land_use_diversity(
    input_path=input_path,
    output_path=output_path,
    landuse_cols=landuse_cols,
    total_area_col=total_area_col,
    diversity_method=shannon_entropy,
    sep=";",
)