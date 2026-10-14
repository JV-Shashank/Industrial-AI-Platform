# Industrial AI Platform

A machine learning project that uses industrial sensor data to predict potential machine failures. The goal is to identify machines that may need attention before an unexpected breakdown occurs.

I built this project to get practical experience with machine learning, API development, and connecting a model to a web application.

## What does it do?

The application uses machine operating data to estimate the risk of machine failure. It takes sensor readings as input, sends them to a trained machine learning model, and returns a prediction through an API.

## Features

- Predicts potential machine failures using sensor data.
- Uses a Random Forest classifier for failure prediction.
- Provides a REST API built with FastAPI.
- Includes a React and TypeScript frontend.
- Supports API testing and input validation.
- Uses PostgreSQL and SQLAlchemy for database integration.

## Technologies Used

- **Programming:** Python, TypeScript
- **Machine Learning:** Pandas, scikit-learn, Random Forest
- **Backend:** FastAPI
- **Frontend:** React, Vite
- **Database:** PostgreSQL, SQLAlchemy
- **Testing:** Pytest
- **Tools:** Git, GitHub

## Dataset

The project uses the AI4I 2020 Predictive Maintenance dataset, which contains industrial machine data and failure labels.

The model uses features such as:
- Air temperature
- Process temperature
- Rotational speed
- Torque
- Tool wear

## Model Performance

The Random Forest model achieved the following validation results during development:

| Metric | Score |
|---|---:|
| ROC-AUC | 0.9599 |
| PR-AUC | 0.6461 |

The dataset has an imbalanced target, with approximately 3.4% of samples associated with machine failure. For this reason, PR-AUC is also useful when evaluating the model's ability to identify failures.

These are validation results from the available dataset, not a guarantee of performance on real industrial equipment.

## How to Run

### 1. Clone the repository

```bash
git clone https://github.com/JV-Shashank/Industrial-AI-Platform.git
cd Industrial-AI-Platform
```

### 2. Set up the Python environment

```bash
python -m venv .venv
```

Activate the environment:

**Windows**
```bash
.venv\Scripts\activate
```

**Linux/macOS**
```bash
source .venv/bin/activate
```

Install the Python dependencies:

```bash
pip install -r requirements.txt
```

### 3. Start the backend

Run the FastAPI application using the actual Python module path configured in the project. For example, if the application is exposed as `app` in `src.api`:

```bash
uvicorn src.api:app --reload
```

Open `http://127.0.0.1:8000/docs` to explore the API.

The API includes a health-check endpoint and a prediction endpoint.

### 4. Run the frontend

Open a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

Use the local URL displayed by Vite to access the frontend.

### 5. Run backend tests

From the project root:

```bash
pytest
```

**Note:** The backend module path, database configuration, and frontend commands should match the current repository setup. Configure the required environment variables before running features that depend on PostgreSQL.

## What I Learned

While building this project, I gained practical experience with:

- Preparing and analysing structured datasets.
- Training and evaluating a classification model.
- Working with imbalanced data and evaluation metrics.
- Building REST APIs with FastAPI.
- Connecting backend services with a frontend application.
- Testing API endpoints and debugging application issues.

## Future Improvements

- Compare additional machine learning models.
- Improve failure detection using precision, recall, and threshold tuning.
- Add model monitoring and retraining workflows.
- Improve the dashboard with more detailed machine-condition insights.

## Disclaimer

This is a learning project built using a public dataset. Its predictions should not be used as the sole basis for real industrial maintenance decisions without further testing and validation.
