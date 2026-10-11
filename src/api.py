
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Literal
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database import Base, engine, get_db
from src.db_models import MachinePrediction
from src.predict import predict_failure
from sqlalchemy import func, select

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure tables exist when the API starts.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Industrial AI Intelligence Platform",
    description="Machine-failure prediction and history API",
    version="1.1.0",
    lifespan=lifespan,
)


class MachineReadings(BaseModel):
    air_temperature: float = Field(gt=0, le=1000)
    process_temperature: float = Field(gt=0, le=1000)
    rotational_speed: float = Field(gt=0, le=100000)
    torque: float = Field(ge=0, le=100000)
    tool_wear: float = Field(ge=0, le=100000)
    product_type: Literal["L", "M", "H"]


class PredictionResponse(BaseModel):
    id: int
    model_name: str
    failure_probability: float
    decision_threshold: float
    predicted_failure: int
    status: str
    risk_level: str
    created_at: datetime


def serialize_prediction(record: MachinePrediction):
    return {
        "id": record.id,
        "model_name": record.model_name,
        "failure_probability": record.failure_probability,
        "decision_threshold": record.decision_threshold,
        "predicted_failure": record.predicted_failure,
        "status": record.status,
        "risk_level": record.risk_level,
        "created_at": record.created_at,
    }


@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "service": "industrial-ai-platform",
    }


@app.post(
    "/predict",
    response_model=PredictionResponse,
    tags=["Machine Prediction"],
)
def predict(
    readings: MachineReadings,
    db: Session = Depends(get_db),
):
    try:
        input_data = readings.model_dump()
        result = predict_failure(input_data)

        record = MachinePrediction(
            **input_data,
            model_name=result["model_name"],
            failure_probability=result["failure_probability"],
            decision_threshold=result["decision_threshold"],
            predicted_failure=result["predicted_failure"],
            status=result["status"],
            risk_level=result["risk_level"],
        )

        db.add(record)
        db.commit()
        db.refresh(record)

        return serialize_prediction(record)

    except FileNotFoundError as exc:
        db.rollback()
        raise HTTPException(
            status_code=503,
            detail="Trained model is unavailable.",
        ) from exc

    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Prediction or database operation failed.",
        ) from exc


@app.get(
    "/predictions",
    tags=["Prediction History"],
)
def get_predictions(
    limit: int = 20,
    db: Session = Depends(get_db),
):
    if not 1 <= limit <= 100:
        raise HTTPException(
            status_code=422,
            detail="limit must be between 1 and 100.",
        )

    statement = (
        select(MachinePrediction)
        .order_by(MachinePrediction.created_at.desc())
        .limit(limit)
    )

    records = db.scalars(statement).all()

    return {
        "count": len(records),
        "predictions": [
            serialize_prediction(record)
            for record in records
        ],
    }


@app.get(
    "/predictions/{prediction_id}",
    tags=["Prediction History"],
)
def get_prediction(
    prediction_id: int,
    db: Session = Depends(get_db),
):
    record = db.get(MachinePrediction, prediction_id)

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Prediction record not found.",
        )

    return serialize_prediction(record)



@app.get("/analytics/summary", tags=["Analytics"])
def analytics_summary(
    db: Session = Depends(get_db),
):
    total = db.scalar(
        select(func.count()).select_from(MachinePrediction)
    ) or 0

    predicted_failures = db.scalar(
        select(func.count())
        .select_from(MachinePrediction)
        .where(MachinePrediction.predicted_failure == 1)
    ) or 0

    average_probability = db.scalar(
        select(func.avg(MachinePrediction.failure_probability))
    )

    risk_distribution = db.execute(
        select(
            MachinePrediction.risk_level,
            func.count().label("count"),
        ).group_by(MachinePrediction.risk_level)
    ).all()

    recent = db.scalars(
        select(MachinePrediction)
        .order_by(MachinePrediction.created_at.desc())
        .limit(100)
    ).all()

    recent = list(reversed(recent))

    return {
        "total_predictions": total,
        "predicted_failures": predicted_failures,
        "predicted_normal": total - predicted_failures,
        "average_failure_probability": (
            float(average_probability)
            if average_probability is not None
            else 0.0
        ),
        "risk_distribution": [
            {"risk_level": level, "count": count}
            for level, count in risk_distribution
        ],
        "recent_predictions": [
            {
                "id": item.id,
                "created_at": item.created_at,
                "failure_probability": item.failure_probability,
                "predicted_failure": item.predicted_failure,
                "risk_level": item.risk_level,
            }
            for item in recent
        ],
    }
