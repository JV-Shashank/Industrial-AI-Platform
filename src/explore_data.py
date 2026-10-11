
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split

# --------------------------------------------------
# 1. Set project paths
# --------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "raw" / "ai4i2020.csv"
REPORTS_PATH = ROOT / "reports"
REPORTS_PATH.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# 2. Load data
# --------------------------------------------------
df = pd.read_csv(DATA_PATH)

print("=" * 55)
print("INDUSTRIAL AI PLATFORM - DATA EXPLORATION")
print("=" * 55)

print("\nDataset shape:", df.shape)
print("\nColumn names:\n", df.columns.tolist())
print("\nFirst five records:\n", df.head())
print("\nData types:\n", df.dtypes)
print("\nMissing values:\n", df.isnull().sum())
print("\nDuplicate rows:", df.duplicated().sum())

# --------------------------------------------------
# 3. Understand the target variable
# --------------------------------------------------
target = "Machine failure"

print("\nFailure counts:")
print(df[target].value_counts().sort_index())

print("\nFailure percentages:")
print((df[target].value_counts(normalize=True) * 100).round(2))

failure_counts = df[target].value_counts().sort_index()

plt.figure(figsize=(7, 5))
sns.barplot(x=failure_counts.index, y=failure_counts.values)
plt.title("Machine Failure Distribution")
plt.xlabel("Machine failure (0 = No, 1 = Yes)")
plt.ylabel("Number of records")
plt.tight_layout()
plt.savefig(REPORTS_PATH / "failure_distribution.png", dpi=150)
plt.close()

# --------------------------------------------------
# 4. Explore sensor measurements
# --------------------------------------------------
sensor_columns = [
    "Air temperature [K]",
    "Process temperature [K]",
    "Rotational speed [rpm]",
    "Torque [Nm]",
    "Tool wear [min]",
]

print("\nSensor summary:")
print(df[sensor_columns].describe().round(2))

for column in sensor_columns:
    plt.figure(figsize=(8, 5))
    sns.histplot(data=df, x=column, hue=target, bins=30)
    plt.title(f"{column} by Machine Failure")
    plt.tight_layout()

    filename = column.replace(" ", "_").replace("[", "").replace("]", "")
    plt.savefig(REPORTS_PATH / f"{filename}.png", dpi=150)
    plt.close()

# --------------------------------------------------
# 5. Compare sensor values by failure status
# --------------------------------------------------
print("\nMean sensor readings by failure status:")
print(df.groupby(target)[sensor_columns].mean().round(2))

# --------------------------------------------------
# 6. Examine feature correlations
# --------------------------------------------------
correlation = df[sensor_columns + [target]].corr()

plt.figure(figsize=(10, 7))
sns.heatmap(correlation, annot=True, fmt=".2f", cmap="coolwarm")
plt.title("Sensor and Machine Failure Correlations")
plt.tight_layout()
plt.savefig(REPORTS_PATH / "correlation_heatmap.png", dpi=150)
plt.close()

# --------------------------------------------------
# 7. Prepare features and target
# --------------------------------------------------
# Remove identifiers and failure-type labels.
# Failure-type labels reveal information about the target
# and must not be used as prediction features.


# --------------------------------------------------
# 7. Prepare features and target
# --------------------------------------------------
# Inspect the actual columns before excluding them.
print("\nColumns available for feature preparation:")
print(df.columns.tolist())

# Remove identifiers and failure-type labels only when present.
# Failure-type labels would cause target leakage.
excluded_columns = [
    "UDI",
    "UID",
    "Product ID",
    "Machine failure",
    "TWF",
    "HDF",
    "PWF",
    "OSF",
    "RNF",
]

columns_to_drop = [
    column for column in excluded_columns
    if column in df.columns
]

X = df.drop(columns=columns_to_drop)
y = df[target]

# Convert categorical product type into numeric indicator columns.
if "Type" in X.columns:
    X = pd.get_dummies(X, columns=["Type"], dtype=int)

# Split data while preserving the failure/no-failure ratio.
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y,
)

print("\nExcluded columns:", columns_to_drop)

print("\n--- TRAINING DATA ---")
print("X_train:", X_train.shape)
print("y_train:", y_train.shape)

print("\n--- TEST DATA ---")
print("X_test:", X_test.shape)
print("y_test:", y_test.shape)


# --------------------------------------------------
# 8. Save prepared datasets
# --------------------------------------------------
processed_path = ROOT / "data" / "processed"
processed_path.mkdir(parents=True, exist_ok=True)

X_train.to_csv(processed_path / "X_train.csv", index=False)
X_test.to_csv(processed_path / "X_test.csv", index=False)
y_train.to_csv(processed_path / "y_train.csv", index=False)
y_test.to_csv(processed_path / "y_test.csv", index=False)

print("\nCharts saved in:", REPORTS_PATH)
print("Prepared datasets saved in:", processed_path)
print("\nSTEP 2 COMPLETED SUCCESSFULLY!")
