# Industrial AI Platform

This project is about using machine learning to predict machine failures from industrial data.

I built this project to learn how machine learning can be used in real-world applications. I worked with the AI4I 2020 Predictive Maintenance dataset, trained a model to predict machine failures, and built a FastAPI backend with a React frontend.

## What I Built

- A machine failure prediction model using Random Forest.
- A FastAPI backend to make predictions through an API.
- A React and TypeScript frontend.
- API tests using Pytest.
- Database integration using PostgreSQL and SQLAlchemy.

## Tech Stack

- Python
- Pandas
- Scikit-learn
- FastAPI
- React
- TypeScript
- PostgreSQL
- SQLAlchemy
- Pytest

## Dataset

I used the AI4I 2020 Predictive Maintenance dataset. It contains information about machine operating conditions, including air temperature, process temperature, rotational speed, torque, and tool wear.

The model uses these features to predict whether a machine failure may occur.

## Model Results

During development, my Random Forest model achieved:

- ROC-AUC: 0.9599
- PR-AUC: 0.6461

Since machine failures are relatively rare in this dataset, I also looked at PR-AUC to evaluate the model.

These results are from my development experiments and may differ on other data.

## Running the Project

Clone the repository:

```bash
git clone https://github.com/JV-Shashank/Industrial-AI-Platform.git
cd Industrial-AI-Platform
```

Create and activate a Python virtual environment, then install the dependencies:

```bash
python -m venv .venv
pip install -r requirements.txt
```

Start the backend using the FastAPI entry point configured in the project. Once it is running, open:

`http://127.0.0.1:8000/docs`

To run the backend tests:

```bash
pytest
```

For the frontend, go to its directory, install the npm dependencies, and start the Vite development server.

## What I Want to Improve Next

- Try other machine learning models and compare their results.
- Improve failure detection by tuning the prediction threshold.
- Add more useful information to the dashboard.
- Explore model monitoring and retraining.

This is a personal learning project using a public dataset. The predictions have not been validated for real industrial use.
