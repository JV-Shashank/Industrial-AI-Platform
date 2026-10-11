
from fastapi.testclient import TestClient
from sqlalchemy import delete

from src.api import app
from src.database import Base, SessionLocal, engine
from src.db_models import MachinePrediction

# Create tables in the configured database before running tests.
Base.metadata.create_all(bind=engine)

SAMPLE_READINGS = {
    "air_temperature": 300.0,
    "process_temperature": 310.0,
    "rotational_speed": 1500,
    "torque": 40.0,
    "tool_wear": 100,
    "product_type": "M",
}


def fake_prediction(readings):
    """Return a deterministic prediction for API tests."""
    return {
        "model_name": "TestModel",
        "failure_probability": 0.12,
        "decision_threshold": 0.35,
        "predicted_failure": 0,
        "status": "No failure predicted",
        "risk_level": "Low",
    }


def setup_function():
    """Prepare and clear the isolated test database."""
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        db.execute(delete(MachinePrediction))
        db.commit()


def test_health_endpoint():
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_predict_saves_record(monkeypatch):
    monkeypatch.setattr(
        "src.api.predict_failure",
        fake_prediction,
    )

    with TestClient(app) as client:
        response = client.post(
            "/predict",
            json=SAMPLE_READINGS,
        )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] > 0
    assert data["model_name"] == "TestModel"
    assert data["predicted_failure"] == 0
    assert data["failure_probability"] == 0.12


def test_prediction_history():
    monkeypatch_result = fake_prediction(SAMPLE_READINGS)

    from unittest.mock import patch

    with patch(
        "src.api.predict_failure",
        return_value=monkeypatch_result,
    ):
        with TestClient(app) as client:
            create_response = client.post(
                "/predict",
                json=SAMPLE_READINGS,
            )

            history_response = client.get("/predictions")

    assert create_response.status_code == 200
    assert history_response.status_code == 200

    data = history_response.json()

    assert data["count"] == 1
    assert data["predictions"][0]["model_name"] == "TestModel"


def test_invalid_sensor_input():
    invalid_readings = SAMPLE_READINGS.copy()
    invalid_readings["rotational_speed"] = -10

    with TestClient(app) as client:
        response = client.post(
            "/predict",
            json=invalid_readings,
        )

    assert response.status_code == 422


def test_missing_prediction_returns_404():
    with TestClient(app) as client:
        response = client.get("/predictions/99999999")

    assert response.status_code == 404


def test_analytics_endpoint(monkeypatch):
    monkeypatch.setattr(
        "src.api.predict_failure",
        fake_prediction,
    )

    with TestClient(app) as client:
        client.post("/predict", json=SAMPLE_READINGS)
        response = client.get("/analytics/summary")

    assert response.status_code == 200

    data = response.json()

    assert data["total_predictions"] == 1
    assert data["predicted_normal"] == 1
    assert data["predicted_failures"] == 0
