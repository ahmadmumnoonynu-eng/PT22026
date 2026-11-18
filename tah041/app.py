
import gradio as gr
import joblib
import pandas as pd

from pathlib import Path
from math import isfinite


BASE_DIR = Path(__file__).resolve().parent

model = joblib.load(BASE_DIR / "models" / "house_price_model.joblib")
pipeline = joblib.load(BASE_DIR / "models" / "preprocessing_pipeline.joblib")


def make_prediction(
    longitude,
    latitude,
    housing_median_age,
    total_rooms,
    total_bedrooms,
    population,
    households,
    median_income,
    ocean_proximity
):
    values = [
        longitude,
        latitude,
        housing_median_age,
        total_rooms,
        total_bedrooms,
        population,
        households,
        median_income
    ]

    if any(v is None for v in values):
        return "Please complete all the fields."

    if not all(isfinite(float(v)) for v in values):
        return "Please enter valid numbers."

    if total_rooms <= 0:
        return "Total rooms must be greater than zero."

    if total_bedrooms <= 0:
        return "Total bedrooms must be greater than zero."

    if total_bedrooms > total_rooms:
        return "Bedrooms cannot exceed total rooms."

    if population <= 0:
        return "Population must be greater than zero."

    if households <= 0:
        return "Households must be greater than zero."

    if households > population:
        return "Households cannot exceed population."

    if housing_median_age <= 0:
        return "Housing age must be greater than zero."

    if median_income <= 0:
        return "Median income must be greater than zero."

    if ocean_proximity not in [
        "<1H OCEAN",
        "INLAND",
        "ISLAND",
        "NEAR BAY",
        "NEAR OCEAN"
    ]:
        return "Please select a valid ocean proximity."

    data = pd.DataFrame([{
        "longitude": longitude,
        "latitude": latitude,
        "housing_median_age": housing_median_age,
        "total_rooms": total_rooms,
        "total_bedrooms": total_bedrooms,
        "population": population,
        "households": households,
        "median_income": median_income,
        "ocean_proximity": ocean_proximity
    }])

    transformed_data = pipeline.transform(data)
    prediction = model.predict(transformed_data)[0]

    return f"${prediction:,.2f}"


custom_css = """
.gradio-container {
    background: #fff8fa !important;
    font-family: Arial, sans-serif !important;
}

.main-title {
    text-align: center;
    color: #c76d91;
    font-size: 38px;
    font-weight: 700;
    margin-bottom: 5px;
}

.subtitle {
    text-align: center;
    color: #987d87;
    font-size: 15px;
    margin-bottom: 25px;
}

.section-title {
    color: #bd7290;
    font-size: 19px;
    font-weight: 600;
}

.input-box {
    background: #ffffff;
    border-radius: 15px !important;
}

.predict-button {
    background: #d889a7 !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    font-size: 17px !important;
    font-weight: 600 !important;
    padding: 14px !important;
}

.predict-button:hover {
    background: #c77595 !important;
}

.result-box {
    background: #fff0f5 !important;
    border: 1px solid #f0cbd9 !important;
    border-radius: 15px !important;
}

.menu-button {
    background: #f8e3eb !important;
    color: #b86d8b !important;
    border: none !important;
    border-radius: 12px !important;
    font-size: 25px !important;
    min-width: 48px !important;
}

.sidebar {
    background: #fff0f5;
    border: 1px solid #f1d2de;
    border-radius: 18px;
    padding: 18px;
}

.sidebar-heading {
    color: #bd7290;
    font-weight: 700;
    font-size: 20px;
}

.sidebar-text {
    color: #78636d;
    font-size: 14px;
    line-height: 1.7;
}

.footer-text {
    text-align: center;
    color: #aa8996;
    font-size: 12px;
    margin-top: 20px;
}
"""


with gr.Blocks() as demo:

    menu_state = gr.State(False)

    with gr.Row():
        gr.HTML(
            """
            <div style="flex:1">
                <div class="main-title">DreamHome ♡</div>
                <div class="subtitle">
                    Discover the estimated value of your dream home
                </div>
            </div>
            """
        )

        menu_button = gr.Button(
            "⋮",
            elem_classes=["menu-button"],
            scale=0,
            min_width=48
        )

    with gr.Column(visible=False, elem_classes=["sidebar"]) as sidebar:

        gr.HTML(
            """
            <div class="sidebar-heading">
                ♡ About DreamHome
            </div>
            <div class="sidebar-text">
                DreamHome is a Machine Learning application
                designed to estimate house prices using
                housing information from California.
            </div>
            """
        )

        with gr.Accordion("Model Information", open=False):
            gr.Markdown(
                """
                **Algorithm:** Random Forest Regressor

                **Number of Trees:** 30

                **Prediction Target:** Median House Value

                **Model Type:** Supervised Machine Learning

                **Task:** Regression
                """
            )

        with gr.Accordion("Libraries Used", open=False):
            gr.Markdown(
                """
                - **Python:** Main programming language
                - **Pandas:** Data handling
                - **NumPy:** Numerical operations
                - **Scikit-learn:** Machine Learning and preprocessing
                - **Joblib:** Model loading and saving
                - **Gradio:** User interface
                """
            )

        with gr.Accordion("Dataset Information", open=False):
            gr.Markdown(
                """
                **Dataset:** California Housing Dataset

                **Records:** 20,640

                **Input Features:** 9

                **Target:** Median House Value

                **Source:** California Housing data
                """
            )

        with gr.Accordion("Model Evaluation", open=False):
            gr.Markdown(
                """
                | Metric | Result |
                |---|---:|
                | MAE | $31,678.01 |
                | RMSE | $47,859.54 |
                | R² Score | 0.8243 |

                These are the evaluation results from
                the project's reconstructed test split.
                """
            )

        with gr.Accordion("How It Works", open=False):
            gr.Markdown(
                """
                1. Enter the housing information.
                2. The preprocessing pipeline prepares the data.
                3. The Random Forest model processes the features.
                4. The application displays the estimated price.
                """
            )

        with gr.Accordion("Limitations", open=False):
            gr.Markdown(
                """
                - Predictions are estimates, not official market prices.
                - The model is trained on California housing data.
                - Real prices may change with market conditions.
                - The model may not represent every property accurately.
                """
            )

        gr.Markdown(
            """
            **DreamHome ♡**

            Machine Learning Project · 2026
            """
        )

    menu_button.click(
        lambda is_open: (
            not is_open,
            gr.update(visible=not is_open)
        ),
        inputs=menu_state,
        outputs=[menu_state, sidebar]
    )

    gr.Markdown(
        """
        <div class="section-title">Find Your Home Value</div>
        Enter the details below to get an estimated house price.
        """
    )

    with gr.Row():

        with gr.Column():
            gr.Markdown("### 📍 Location Details")

            longitude = gr.Number(
                label="Longitude",
                value=-122.23
            )

            latitude = gr.Number(
                label="Latitude",
                value=37.88
            )

            ocean_proximity = gr.Dropdown(
                choices=[
                    "<1H OCEAN",
                    "INLAND",
                    "ISLAND",
                    "NEAR BAY",
                    "NEAR OCEAN"
                ],
                value="NEAR BAY",
                label="Ocean Proximity"
            )

        with gr.Column():
            gr.Markdown("### 🏡 Property Details")

            housing_median_age = gr.Number(
                label="Housing Median Age",
                value=30
            )

            total_rooms = gr.Number(
                label="Total Rooms",
                value=2000
            )

            total_bedrooms = gr.Number(
                label="Total Bedrooms",
                value=400
            )

    with gr.Row():

        with gr.Column():
            gr.Markdown("### 👥 Population Details")

            population = gr.Number(
                label="Population",
                value=1000
            )

            households = gr.Number(
                label="Households",
                value=350
            )

        with gr.Column():
            gr.Markdown("### 💰 Income Details")

            median_income = gr.Number(
                label="Median Income",
                value=5.0
            )

    predict_button = gr.Button(
        "Estimate House Price ♡",
        elem_classes=["predict-button"]
    )

    prediction_output = gr.Textbox(
        label="Estimated House Price",
        placeholder="Your estimated house price will appear here...",
        interactive=False,
        elem_classes=["result-box"]
    )

    predict_button.click(
        fn=make_prediction,
        inputs=[
            longitude,
            latitude,
            housing_median_age,
            total_rooms,
            total_bedrooms,
            population,
            households,
            median_income,
            ocean_proximity
        ],
        outputs=prediction_output
    )

    gr.HTML(
        """
        <div class="footer-text">
            DreamHome ♡ | Powered by Machine Learning
        </div>
        """
    )


if __name__ == "__main__":
    demo.launch(
        theme=gr.themes.Soft(
            primary_hue="pink",
            secondary_hue="rose",
            neutral_hue="stone"
        ),
        css=custom_css
    )
