import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Weather Prediction System",
    page_icon="🌦️",
    layout="wide",
)

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "ML" / "models"
MODEL_PATH = MODEL_DIR / "weather_prediction_model.joblib"
METADATA_PATH = MODEL_DIR / "model_metadata.json"

DEFAULT_CATEGORICAL_VALUES = {
    "Location": "Sydney",
    "WindGustDir": "N",
    "WindDir9am": "N",
    "WindDir3pm": "N",
    "RainToday": "No",
}
NUMERIC_RANGES = {
    "MinTemp": (-10.0, 35.0),
    "MaxTemp": (0.0, 50.0),
    "Rainfall": (0.0, 100.0),
    "Evaporation": (0.0, 25.0),
    "Sunshine": (0.0, 14.0),
    "WindGustSpeed": (0.0, 150.0),
    "WindSpeed9am": (0.0, 100.0),
    "WindSpeed3pm": (0.0, 100.0),
    "Humidity9am": (0.0, 100.0),
    "Humidity3pm": (0.0, 100.0),
    "Pressure9am": (970.0, 1050.0),
    "Pressure3pm": (970.0, 1050.0),
    "Cloud9am": (0.0, 8.0),
    "Cloud3pm": (0.0, 8.0),
    "Temp9am": (-5.0, 40.0),
    "Temp3pm": (0.0, 50.0),
}
INTEGER_NUMERIC_FEATURES = {"Cloud9am", "Cloud3pm"}
RANDOM_CATEGORICAL_VALUES = {
    "Location": [
        "Adelaide",
        "Brisbane",
        "Canberra",
        "Darwin",
        "Hobart",
        "Melbourne",
        "Perth",
        "Sydney",
    ],
    "WindGustDir": [
        "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
        "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW",
    ],
    "WindDir9am": [
        "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
        "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW",
    ],
    "WindDir3pm": [
        "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
        "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW",
    ],
    "RainToday": ["No", "Yes"],
}


@st.cache_resource
def load_model_and_metadata():
    if not MODEL_PATH.is_file():
        raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")
    if not METADATA_PATH.is_file():
        raise FileNotFoundError(f"Metadata file not found: {METADATA_PATH}")

    with METADATA_PATH.open("r", encoding="utf-8") as file:
        metadata = json.load(file)

    if not isinstance(metadata, dict):
        raise ValueError("Model metadata must be a JSON object.")

    required = ("numeric_features", "categorical_features", "feature_columns")
    missing = [key for key in required if key not in metadata]
    if missing:
        raise KeyError(
            "The metadata file is missing these keys: " + ", ".join(missing)
        )

    numeric_features = metadata["numeric_features"]
    categorical_features = metadata["categorical_features"]
    feature_columns = metadata["feature_columns"]
    if not all(
        isinstance(features, list)
        and all(isinstance(feature, str) for feature in features)
        for features in (numeric_features, categorical_features, feature_columns)
    ):
        raise ValueError("Feature definitions in model metadata must be lists of strings.")

    expected_features = numeric_features + categorical_features
    if (
        len(feature_columns) != len(set(feature_columns))
        or len(expected_features) != len(set(expected_features))
        or set(feature_columns) != set(expected_features)
    ):
        raise ValueError(
            "Metadata feature_columns must contain each numeric and categorical "
            "feature exactly once."
        )

    # Joblib artifacts use pickle serialization; only load trusted model files.
    model = joblib.load(MODEL_PATH)
    if not callable(getattr(model, "predict_proba", None)):
        raise TypeError("The saved model must support predict_proba().")

    classes = getattr(model, "classes_", None)
    if classes is None:
        raise ValueError("The saved model does not expose its trained classes.")

    positive_class = str(metadata.get("positive_class", "Yes"))
    if positive_class not in [str(value) for value in classes]:
        raise ValueError(
            f"Positive class {positive_class!r} is not present in the model classes."
        )

    threshold = float(metadata.get("threshold", 0.5))
    if not np.isfinite(threshold) or not 0 <= threshold <= 1:
        raise ValueError("The prediction threshold must be between 0 and 1.")

    return model, metadata, threshold


def randomize_weather_values(numeric_features, categorical_features):
    rng = np.random.default_rng()

    for feature in numeric_features:
        if feature not in NUMERIC_RANGES:
            raise ValueError(f"No random value range is configured for {feature}.")
        lower, upper = NUMERIC_RANGES[feature]
        if feature in INTEGER_NUMERIC_FEATURES:
            value = float(rng.integers(int(lower), int(upper) + 1))
        else:
            value = round(float(rng.uniform(lower, upper)), 2)
        st.session_state[f"weather_{feature}"] = value

    for feature in categorical_features:
        key = f"weather_{feature}"
        if feature == "Month":
            st.session_state[key] = int(rng.integers(1, 13))
        elif feature in RANDOM_CATEGORICAL_VALUES:
            options = RANDOM_CATEGORICAL_VALUES[feature]
            st.session_state[key] = options[int(rng.integers(0, len(options)))]
        else:
            raise ValueError(f"No random values are configured for {feature}.")


st.markdown(
    """
    <style>
    .main-title {
        text-align: center;
        font-size: 2.35rem;
        font-weight: 800;
        color: #1677b8;
        margin-bottom: 0.15rem;
    }
    .sub-title {
        text-align: center;
        color: #64748b;
        margin-bottom: 1.8rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="main-title">🌦️ Weather Prediction System</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sub-title">Predict whether it will rain tomorrow using a Random Forest model.</div>',
    unsafe_allow_html=True,
)

try:
    model, metadata, threshold = load_model_and_metadata()
except Exception as exc:
    st.error("The model could not be loaded.")
    st.exception(exc)
    st.info(
        "Check that ML/models contains weather_prediction_model.joblib and "
        "model_metadata.json, and that the joblib file is a trusted Random Forest "
        "pipeline matching this metadata."
    )
    st.stop()
    raise

numeric_features = metadata["numeric_features"]
categorical_features = metadata["categorical_features"]
feature_columns = metadata["feature_columns"]
positive_class = str(metadata.get("positive_class", "Yes"))
model_classes = [str(value) for value in model.classes_]
negative_class = next(
    (value for value in model_classes if value != positive_class),
    "No",
)

with st.sidebar:
    st.header("About this project")
    st.write(f"**Model:** {metadata.get('model_name', 'Random Forest')}")
    st.write(f"**Target:** {metadata.get('target_column', 'RainTomorrow')}")
    st.write(f"**Input features:** {len(feature_columns)}")
    st.write("**Output:** Rain probability")
    st.divider()
    st.caption(
        "This is an educational prediction tool. Its output is an estimate, "
        "not an official meteorological forecast."
    )
    st.caption("Only use trusted joblib model files; loading them can execute code.")

st.header("Enter today's weather observations")
st.write(
    "Enter the available weather measurements and conditions. "
    "The saved model pipeline handles its trained preprocessing."
)

for feature in numeric_features:
    st.session_state.setdefault(f"weather_{feature}", 0.0)
for feature in categorical_features:
    default = 1 if feature == "Month" else DEFAULT_CATEGORICAL_VALUES.get(feature, "")
    st.session_state.setdefault(f"weather_{feature}", default)

st.button(
    "🎲 Fill with random values",
    on_click=randomize_weather_values,
    args=(numeric_features, categorical_features),
)
st.caption("Random values are for demonstration; adjust them to match actual observations.")

user_values = {}
with st.form("weather_form"):
    numeric_columns = st.columns(3)
    for index, feature in enumerate(numeric_features):
        with numeric_columns[index % 3]:
            user_values[feature] = st.number_input(
                feature,
                format="%.2f",
                key=f"weather_{feature}",
            )

    st.divider()
    st.subheader("Categorical weather information")
    categorical_columns = st.columns(2)
    for index, feature in enumerate(categorical_features):
        with categorical_columns[index % 2]:
            if feature == "Month":
                user_values[feature] = st.selectbox(
                    feature,
                    options=range(1, 13),
                    key=f"weather_{feature}",
                )
            else:
                user_values[feature] = st.text_input(
                    feature,
                    key=f"weather_{feature}",
                )

    submitted = st.form_submit_button(
        "🔍 Predict tomorrow's weather",
        type="primary",
        width="stretch",
    )

if submitted:
    try:
        input_frame = pd.DataFrame(
            [{feature: user_values[feature] for feature in feature_columns}],
            columns=feature_columns,
        )
        probabilities = np.asarray(model.predict_proba(input_frame))
        if (
            probabilities.ndim != 2
            or probabilities.shape[0] != 1
            or probabilities.shape[1] != len(model_classes)
        ):
            raise ValueError("The model returned probabilities in an unexpected shape.")

        positive_index = model_classes.index(positive_class)
        rain_probability = float(probabilities[0, positive_index])
        if not np.isfinite(rain_probability) or not 0 <= rain_probability <= 1:
            raise ValueError("The model returned an invalid rain probability.")

        prediction = (
            positive_class
            if rain_probability >= threshold
            else negative_class
        )

        st.divider()
        st.header("Prediction result")
        left, right = st.columns(2)
        with left:
            if prediction == positive_class:
                st.error(f"🌧️ Prediction: {prediction}")
                st.write("The model predicts rain tomorrow.")
            else:
                st.success(f"☀️ Prediction: {prediction}")
                st.write("The model predicts no rain tomorrow.")

        with right:
            st.metric("Estimated probability of rain", f"{rain_probability * 100:.2f}%")
            st.metric("Decision threshold", f"{threshold * 100:.2f}%")
            st.progress(float(np.clip(rain_probability, 0.0, 1.0)))

        with st.expander("View submitted weather information"):
            st.dataframe(
                pd.DataFrame(
                    {
                        "Feature": list(user_values),
                        "Value": [str(value) for value in user_values.values()],
                    }
                ),
                hide_index=True,
                alt="Submitted weather inputs",
            )

    except Exception as exc:
        st.error("Prediction failed.")
        st.exception(exc)

st.divider()
st.caption("Weather Prediction System | Python • Random Forest • Streamlit")
