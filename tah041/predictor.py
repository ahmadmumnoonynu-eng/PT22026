"""Model loading, input validation and prediction logic.

Shared by app.py (Gradio interface) and test_cases.py so the tests
exercise exactly the same code the application uses.
"""

from pathlib import Path

import joblib
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "house_price_model.joblib"
PIPELINE_PATH = BASE_DIR / "models" / "preprocessing_pipeline.joblib"

FEATURES = [
    "longitude", "latitude", "housing_median_age", "total_rooms",
    "total_bedrooms", "population", "households", "median_income",
    "ocean_proximity",
]
OCEAN_CATEGORIES = ["<1H OCEAN", "INLAND", "ISLAND", "NEAR BAY", "NEAR OCEAN"]

_cache = {}


def load_artifacts():
    """Load the model and preprocessing pipeline once and return both."""
    if not _cache:
        missing = [p.name for p in (MODEL_PATH, PIPELINE_PATH) if not p.exists()]
        if missing:
            raise FileNotFoundError(
                f"Missing model file(s): {', '.join(missing)}. "
                "Run `python download_model.py` first."
            )
        _cache["model"] = joblib.load(MODEL_PATH)
        _cache["pipeline"] = joblib.load(PIPELINE_PATH)
    return _cache["model"], _cache["pipeline"]


def validate_inputs(data):
    """Raise ValueError if the input dictionary is incomplete or unrealistic."""
    for name in FEATURES:
        if data.get(name) is None:
            raise ValueError(f"Please provide a value for '{name}'.")

    if data["ocean_proximity"] not in OCEAN_CATEGORIES:
        raise ValueError("Unknown ocean proximity category.")

    if min(data["total_rooms"], data["total_bedrooms"],
           data["population"], data["households"]) <= 0:
        raise ValueError("Room and population values must be positive.")

    if data["median_income"] <= 0:
        raise ValueError("Median income must be positive.")

    if data["total_bedrooms"] > data["total_rooms"]:
        raise ValueError("Bedrooms cannot exceed total rooms.")

    if data["households"] > data["population"]:
        raise ValueError("Households cannot exceed population.")


def predict_price(data):
    """Validate the inputs and return the predicted house price in USD."""
    validate_inputs(data)
    model, pipeline = load_artifacts()
    processed = pipeline.transform(pd.DataFrame([data], columns=FEATURES))
    return float(model.predict(processed)[0])