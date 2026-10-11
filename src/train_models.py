
from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    average_precision_score,
    roc_auc_score,
    precision_score,
    recall_score,
    f1_score,
    accuracy_score,
    confusion_matrix,
    classification_report,
)

from xgboost import XGBClassifier


# --------------------------------------------------
# 1. Paths and reproducibility
# --------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "processed"
MODEL_DIR = ROOT / "models"
REPORT_DIR = ROOT / "reports"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

RANDOM_STATE = 42


# --------------------------------------------------
# 2. Load the prepared datasets
# --------------------------------------------------
X_train = pd.read_csv(DATA_DIR / "X_train.csv")
X_test = pd.read_csv(DATA_DIR / "X_test.csv")

y_train = pd.read_csv(DATA_DIR / "y_train.csv").iloc[:, 0]
y_test = pd.read_csv(DATA_DIR / "y_test.csv").iloc[:, 0]

y_train = y_train.astype(int)
y_test = y_test.astype(int)

print("Training features:", X_train.shape)
print("Testing features:", X_test.shape)
print("Training failure rate:", round(y_train.mean(), 4))
print("Testing failure rate:", round(y_test.mean(), 4))


# --------------------------------------------------
# 3. Create a validation split
#    The test set stays untouched until final evaluation.
# --------------------------------------------------
X_fit, X_val, y_fit, y_val = train_test_split(
    X_train,
    y_train,
    test_size=0.20,
    random_state=RANDOM_STATE,
    stratify=y_train,
)


# Clean feature names for XGBoost compatibility
def clean_feature_names(X):
    X = X.copy()
    X.columns = (
        X.columns.astype(str)
        .str.replace("[", "_", regex=False)
        .str.replace("]", "_", regex=False)
        .str.replace("<", "_", regex=False)
    )
    return X

X_train = clean_feature_names(X_train)
X_test = clean_feature_names(X_test)
X_fit = clean_feature_names(X_fit)
X_val = clean_feature_names(X_val)


negative_count = int((y_fit == 0).sum())
positive_count = int((y_fit == 1).sum())

scale_pos_weight = negative_count / positive_count

print("\nModel-fitting records:", len(X_fit))
print("Validation records:", len(X_val))
print("Positive class weight ratio:", round(scale_pos_weight, 2))


# --------------------------------------------------
# 4. Define three candidate models
# --------------------------------------------------
models = {
    "Logistic Regression": Pipeline([
        ("scaler", StandardScaler()),
        ("model", LogisticRegression(
            class_weight="balanced",
            max_iter=2000,
            random_state=RANDOM_STATE,
        )),
    ]),

    "Random Forest": RandomForestClassifier(
        n_estimators=300,
        max_depth=12,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    ),

    "XGBoost": XGBClassifier(
        n_estimators=300,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        scale_pos_weight=scale_pos_weight,
        eval_metric="logloss",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    ),
}


# --------------------------------------------------
# 5. Train each model and evaluate on validation data
# --------------------------------------------------
validation_results = {}
thresholds = {}

for name, model in models.items():
    print(f"\nTraining {name}...")

    model.fit(X_fit, y_fit)

    probabilities = model.predict_proba(X_val)[:, 1]

    # Find a threshold maximizing validation F1.
    # This threshold is selected without using test labels.
    candidate_thresholds = np.arange(0.05, 0.96, 0.01)

    threshold_scores = []

    for threshold in candidate_thresholds:
        predictions = (probabilities >= threshold).astype(int)

        score = f1_score(
            y_val,
            predictions,
            zero_division=0,
        )

        threshold_scores.append(score)

    best_index = int(np.argmax(threshold_scores))
    best_threshold = float(candidate_thresholds[best_index])

    validation_ap = average_precision_score(
        y_val, probabilities
    )

    validation_roc_auc = roc_auc_score(
        y_val, probabilities
    )

    validation_results[name] = {
        "model": model,
        "average_precision": validation_ap,
        "roc_auc": validation_roc_auc,
    }

    thresholds[name] = best_threshold

    print("Validation PR-AUC (average precision):",
          round(validation_ap, 4))
    print("Validation ROC-AUC:", round(validation_roc_auc, 4))
    print("Selected threshold:", round(best_threshold, 2))
    print("Validation F1:",
          round(threshold_scores[best_index], 4))


# --------------------------------------------------
# 6. Select the model using validation PR-AUC
# --------------------------------------------------
best_name = max(
    validation_results,
    key=lambda name: validation_results[name]["average_precision"],
)

best_model = validation_results[best_name]["model"]
best_threshold = thresholds[best_name]

print("\nSelected model:", best_name)
print("Selection criterion: validation PR-AUC")


# --------------------------------------------------
# 7. Evaluate all candidates on the untouched test set
# --------------------------------------------------
comparison = []

for name, result in validation_results.items():
    model = result["model"]
    threshold = thresholds[name]

    probabilities = model.predict_proba(X_test)[:, 1]
    predictions = (probabilities >= threshold).astype(int)

    row = {
        "model": name,
        "threshold": threshold,
        "accuracy": accuracy_score(y_test, predictions),
        "precision": precision_score(
            y_test, predictions, zero_division=0
        ),
        "recall": recall_score(
            y_test, predictions, zero_division=0
        ),
        "f1_score": f1_score(
            y_test, predictions, zero_division=0
        ),
        "pr_auc": average_precision_score(
            y_test, probabilities
        ),
        "roc_auc": roc_auc_score(
            y_test, probabilities
        ),
    }

    comparison.append(row)

    print(f"\n--- {name}: TEST RESULTS ---")
    print(pd.Series(row).to_string())

    print("\nConfusion matrix:")
    print(confusion_matrix(y_test, predictions))

    print("\nClassification report:")
    print(classification_report(
        y_test,
        predictions,
        target_names=["No failure", "Failure"],
        zero_division=0,
    ))

comparison_df = pd.DataFrame(comparison)
comparison_df = comparison_df.sort_values(
    "pr_auc", ascending=False
)

comparison_path = REPORT_DIR / "model_comparison.csv"
comparison_df.to_csv(comparison_path, index=False)

print("\n--- MODEL COMPARISON ---")
print(comparison_df.round(4).to_string(index=False))


# --------------------------------------------------
# 8. Save the selected model and threshold
# --------------------------------------------------
model_path = MODEL_DIR / "machine_failure_model.joblib"
joblib.dump(best_model, model_path)

metadata = {
    "model_name": best_name,
    "decision_threshold": best_threshold,
    "selection_metric": "validation average precision (PR-AUC)",
    "random_state": RANDOM_STATE,
    "features": X_train.columns.tolist(),
    "dataset": "UCI AI4I 2020 Predictive Maintenance Dataset",
}

metadata_path = MODEL_DIR / "model_metadata.json"
metadata_path.write_text(
    json.dumps(metadata, indent=2),
    encoding="utf-8",
)

print("\nSaved model:", model_path)
print("Saved metadata:", metadata_path)
print("Saved comparison:", comparison_path)
print("\nSTEP 3 COMPLETED SUCCESSFULLY!")
