
import gradio as gr
from html import escape
from predictor import predict_price as predict_model


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
    data = {
        "longitude": longitude,
        "latitude": latitude,
        "housing_median_age": housing_median_age,
        "total_rooms": total_rooms,
        "total_bedrooms": total_bedrooms,
        "population": population,
        "households": households,
        "median_income": median_income,
        "ocean_proximity": ocean_proximity
    }

    try:
        price = predict_model(data)

        return f"""
        <div class="price-result">
            <p class="result-label">YOUR ESTIMATED HOUSE VALUE</p>
            <h2>${price:,.2f}</h2>
            <p class="result-note">Estimated value in US dollars</p>
        </div>
        """
    except Exception as error:
        return f"""
        <div class="error-result">
            <strong>Please check your information</strong>
            <p>{escape(str(error))}</p>
        </div>
        """


custom_css = """
:root {
    color-scheme: light !important;
}

html, body {
    background: #fff9fb !important;
}

.gradio-container {
    background: #fff9fb !important;
    color: #382d35 !important;
    font-family: 'Segoe UI', Arial, sans-serif !important;
    max-width: 1100px !important;
    margin: auto !important;
}

.gradio-container .prose,
.gradio-container label,
.gradio-container p,
.gradio-container h1,
.gradio-container h2,
.gradio-container h3 {
    color: #493b44 !important;
}

.main-title {
    background: linear-gradient(135deg, #f9e5ed, #fff1f5);
    border: 1px solid #f0d5e0;
    border-radius: 22px;
    padding: 32px 20px;
    text-align: center;
    margin-bottom: 24px;
}

.main-title h1 {
    color: #a64f75 !important;
    font-size: 38px;
    font-weight: 700;
    margin-bottom: 8px;
}

.main-title p {
    color: #806274 !important;
    font-size: 15px;
    margin: 5px;
}

.input-card {
    background: #ffffff !important;
    border: 1px solid #f0dce5 !important;
    border-radius: 18px !important;
    padding: 22px !important;
    box-shadow: 0 5px 18px rgba(120, 65, 90, 0.06);
}

.section-title {
    color: #a64f75 !important;
    font-weight: 700 !important;
    margin-bottom: 12px !important;
}

.input-card label {
    color: #695361 !important;
    font-weight: 500 !important;
}

.input-card input,
.input-card textarea,
.input-card select,
.input-card [role="listbox"] {
    background: #ffffff !important;
    color: #382d35 !important;
    border: 1px solid #e8cbd8 !important;
    border-radius: 10px !important;
}

.input-card input:focus {
    border-color: #bd7193 !important;
    box-shadow: 0 0 0 2px rgba(189, 113, 147, 0.12) !important;
}

.primary-btn {
    background: #ae5c80 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 12px !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    min-height: 52px !important;
    margin-top: 12px !important;
}

.primary-btn:hover {
    background: #95476b !important;
}

#prediction-output {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    margin-top: 16px !important;
}

.price-result {
    background: #fff0f5;
    border: 1px solid #edcbd9;
    border-radius: 18px;
    padding: 25px;
    text-align: center;
}

.price-result .result-label {
    color: #93647b !important;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1.5px;
}

.price-result h2 {
    color: #a64f75 !important;
    font-size: 34px;
    margin: 12px 0;
}

.price-result .result-note {
    color: #806274 !important;
    font-size: 13px;
}

.error-result {
    background: #fff1f0;
    border: 1px solid #f0c7c3;
    border-radius: 14px;
    padding: 18px;
    color: #873f3b !important;
}

.footer-text {
    text-align: center;
    color: #987d8c !important;
    font-size: 12px;
    margin-top: 28px;
    padding: 15px;
}

@media (max-width: 650px) {
    .main-title h1 {
        font-size: 30px;
    }

    .input-card {
        padding: 15px !important;
    }
}
"""


with gr.Blocks(
    theme=gr.themes.Soft(
        primary_hue="pink",
        secondary_hue="rose",
        neutral_hue="slate"
    ),
    css=custom_css,
    title="DreamHome | House Price Prediction"
) as demo:

    gr.HTML("""
    <div class="main-title">
        <h1>DreamHome</h1>
        <p>House Price Prediction</p>
        <p>A simple way to estimate your property's value</p>
    </div>
    """)

    with gr.Row():

        with gr.Column(elem_classes="input-card"):
            gr.Markdown(
                "### Location Details",
                elem_classes="section-title"
            )

            longitude = gr.Slider(
                -124.5, -114.0,
                value=-122.23,
                step=0.01,
                label="Longitude"
            )

            latitude = gr.Slider(
                32.5, 42.0,
                value=37.88,
                step=0.01,
                label="Latitude"
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

        with gr.Column(elem_classes="input-card"):
            gr.Markdown(
                "### Property Details",
                elem_classes="section-title"
            )

            housing_median_age = gr.Slider(
                1, 52,
                value=41,
                step=1,
                label="Housing Median Age"
            )

            total_rooms = gr.Number(
                value=880,
                label="Total Rooms"
            )

            total_bedrooms = gr.Number(
                value=129,
                label="Total Bedrooms"
            )

    with gr.Row():

        with gr.Column(elem_classes="input-card"):
            gr.Markdown(
                "### Population Details",
                elem_classes="section-title"
            )

            population = gr.Number(
                value=322,
                label="Population"
            )

            households = gr.Number(
                value=126,
                label="Households"
            )

        with gr.Column(elem_classes="input-card"):
            gr.Markdown(
                "### Income Details",
                elem_classes="section-title"
            )

            median_income = gr.Slider(
                0.5, 15,
                value=8.3252,
                step=0.01,
                label="Median Income"
            )

    predict_button = gr.Button(
        "Predict House Price",
        variant="primary",
        elem_classes="primary-btn"
    )

    prediction_output = gr.HTML(
        value="",
        elem_id="prediction-output"
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

    gr.HTML("""
    <div class="footer-text">
        DreamHome | Powered by Random Forest Machine Learning
        <br>
        California Housing Dataset · Educational Project
    </div>
    """)


if __name__ == "__main__":
    demo.launch()
