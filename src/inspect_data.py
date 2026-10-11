
from pathlib import Path

import pandas as pd

# Locate the project and dataset
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "raw" / "ai4i2020.csv"

# Check that the file exists
if not DATA_PATH.exists():
    raise FileNotFoundError(
        f"Dataset not found at: {DATA_PATH}\n"
        "Download ai4i2020.csv and place it in data/raw/."
    )

# Load the dataset
df = pd.read_csv(DATA_PATH)

print("\n--- DATASET SHAPE ---")
print(df.shape)

print("\n--- FIRST 5 ROWS ---")
print(df.head())

print("\n--- COLUMN NAMES ---")
print(df.columns.tolist())

print("\n--- DATA TYPES ---")
print(df.dtypes)

print("\n--- MISSING VALUES ---")
print(df.isnull().sum())

print("\n--- DUPLICATE ROWS ---")
print(df.duplicated().sum())

print("\n--- FAILURE DISTRIBUTION ---")
print(df["Machine failure"].value_counts())

print("\n--- SUMMARY STATISTICS ---")
print(df.describe())
