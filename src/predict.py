
from pathlib import Path
import json

import joblib
import pandas as pd


# --------------------------------------------------
# 1. Locate the trained model
# --------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]

MODEL_PATH = ROOT / "models" / "machine_failure_model.joblib"
METADATA_PATH = ROOT / "models" / "model_metadata.json"


def load_model():
    """Load the trained model and its metadata."""
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Trained model not found: {MODEL_PATH}. "
            "Run src/train_models.py first."
        )

    if not METADATA_PATH.exists():
        raise FileNotFoundError(
            f"Model metadata not found: {METADATA_PATH}"
        )

    model = joblib.load(MODEL_PATH)

    metadata = json.loads(
        METADATA_PATH.read_text(encoding="utf-8")
    )

    return model, metadata


# --------------------------------------------------
# 2. Validate incoming sensor readings
# --------------------------------------------------
def validate_readings(readings: dict) -> None:
    """Validate sensor inputs before making a prediction."""

    required_fields = [
        "air_temperature",
        "process_temperature",
        "rotational_speed",
        "torque",
        "tool_wear",
        "product_type",
    ]

    missing = [
        field for field in required_fields
        if field not in readings
    ]

    if missing:
        raise ValueError(
            f"Missing required fields: {missing}"
        )

    numeric_fields = [
        "air_temperature",
        "process_temperature",
        "rotational_speed",
        "torque",
        "tool_wear",
    ]

    for field in numeric_fields:
        value = readings[field]

        # Reject booleans, strings, NaN and infinity.
        if isinstance(value, bool):
            raise ValueError(f"{field} must be numeric.")

        try:
            numeric_value = float(value)
        except (TypeError, ValueError):
            raise ValueError(
                f"{field} must be numeric."
            ) from None

        if not pd.notna(numeric_value) or numeric_value in (
            float("inf"), float("-inf")
        ):
            raise ValueError(
                f"{field} must be a finite number."
            )

        if numeric_value < 0:
            raise ValueError(
                f"{field} cannot be negative."
            )

    if readings["product_type"] not in ("L", "M", "H"):
        raise ValueError(
            "product_type must be L, M or H."
        )

    if readings["rotational_speed"] <= 0:
        raise ValueError(
            "rotational_speed must be greater than zero."
        )


# --------------------------------------------------
# 3. Convert readings into model features
# --------------------------------------------------



# --------------------------------------------------
# 3. Convert readings into model features
# --------------------------------------------------
def prepare_features(readings: dict, feature_names: list) -> pd.DataFrame:
    """Create a row with the exact feature schema used during training."""

    validate_readings(readings)

    row = {
        "Air temperature _K_": float(readings["air_temperature"]),
        "Process temperature _K_": float(readings["process_temperature"]),
        "Rotational speed _rpm_": float(readings["rotational_speed"]),
        "Torque _Nm_": float(readings["torque"]),
        "Tool wear _min_": float(readings["tool_wear"]),
        "Type_H": int(readings["product_type"] == "H"),
        "Type_L": int(readings["product_type"] == "L"),
        "Type_M": int(readings["product_type"] == "M"),
    }

    features = pd.DataFrame([row])

    missing_features = set(feature_names) - set(features.columns)

    if missing_features:
        raise ValueError(
            f"Missing model features: {missing_features}"
        )

    return features.reindex(columns=feature_names)


# --------------------------------------------------
# 4. Predict machine-failure risk
# --------------------------------------------------
def predict_failure(readings: dict) -> dict:
    """
    Return the model's estimated failure probability
    and threshold-based prediction.
    """

    model, metadata = load_model()

    features = prepare_features(
        readings,
        metadata["features"],
    )

    probability = float(
        model.predict_proba(features)[0, 1]
    )

    threshold = float(
        metadata["decision_threshold"]
    )

    prediction = int(probability >= threshold)

    return {
        "model_name": metadata["model_name"],
        "failure_probability": round(probability, 4),
        "decision_threshold": round(threshold, 4),
        "predicted_failure": prediction,
        "status": (
            "Potential failure detected"
            if prediction == 1
            else "No failure predicted"
        ),
        "risk_level": (
            "High"
            if probability >= 0.70
            else "Medium"
            if probability >= 0.30
            else "Low"
        ),
    }


# --------------------------------------------------
# 5. Run a local example
# --------------------------------------------------
if __name__ == "__main__":
    sample_readings = {
        "air_temperature": 300.0,
        "process_temperature": 310.0,
        "rotational_speed": 1500,
        "torque": 40.0,
        "tool_wear": 100,
        "product_type": "M",
    }

    result = predict_failure(sample_readings)

    print("\n--- MACHINE FAILURE PREDICTION ---")

    for key, value in result.items():
        print(f"{key}: {value}")
