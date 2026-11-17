import gradio as gr
from src.sentiment import predict_sentiment


def analyze_text(text):
    try:
        result = predict_sentiment(text)

        sentiment = result["sentiment"]
        confidence = result["confidence"]
        scores = result["scores"]

        return (
            f"## {sentiment}\n"
            f"**Confidence: {confidence}%**",
            scores
        )

    except ValueError as error:
        return str(error), None

    except Exception as error:
        return f"Analysis failed: {error}", None


with gr.Blocks(title="SmartFeel AI") as app:

    gr.Markdown(
        """
        # SmartFeel AI
        ### Intelligent Sentiment & Customer Experience Platform

        Analyze text and understand people's feelings using Artificial Intelligence.
        """
    )

    with gr.Tab("SmartFeel"):
        gr.Markdown("### General Sentiment Analysis")

        text_input = gr.Textbox(
            label="Enter your text",
            placeholder="Write something here...",
            lines=5
        )

        analyze_button = gr.Button("Analyze Sentiment", variant="primary")

        result_output = gr.Markdown()
        scores_output = gr.Label(label="Sentiment Probabilities")

        analyze_button.click(
            fn=analyze_text,
            inputs=text_input,
            outputs=[result_output, scores_output]
        )

    gr.Markdown(
        """
        ---
        **SmartFeel AI | Powered by RoBERTa**
        """
    )


if __name__ == "__main__":
    app.launch()
    
import gradio as gr
import pandas as pd

from src.sentiment import predict_sentiment, analyze_batch
from src.utils import calculate_distribution, create_history_record


history = []


def analyze_single(text, section):
    if not text or not text.strip():
        raise gr.Error("Please enter some text first.")

    result = predict_sentiment(text)
    record = create_history_record(text, result)
    record["section"] = section
    history.insert(0, record)

    scores = pd.DataFrame({
        "Sentiment": list(result["scores"].keys()),
        "Probability (%)": list(result["scores"].values())
    })

    return (
        result["sentiment"],
        f"{result['confidence']}%",
        scores,
        history_dataframe()
    )


def analyze_social(comments):
    if not comments or not comments.strip():
        raise gr.Error("Please enter some comments.")

    texts = [line.strip() for line in comments.splitlines() if line.strip()]
    results = analyze_batch(texts)

    for result in results:
        record = create_history_record(result["text"], result)
        record["section"] = "SocialMind"
        history.insert(0, record)

    distribution = calculate_distribution(results)

    results_df = pd.DataFrame([
        {
            "Comment": item["text"],
            "Sentiment": item["sentiment"],
            "Confidence (%)": item["confidence"]
        }
        for item in results
    ])

    distribution_df = pd.DataFrame({
        "Sentiment": list(distribution.keys()),
        "Percentage (%)": list(distribution.values())
    })

    return results_df, distribution_df, history_dataframe()


def history_dataframe():
    return pd.DataFrame(history)


custom_css = """
.gradio-container {
    max-width: 1200px !important;
    margin: auto !important;
}
#main-title {
    text-align: center;
    padding: 25px;
}
"""


with gr.Blocks(
    title="SmartFeel AI",
    theme=gr.themes.Soft(primary_hue="indigo"),
    css=custom_css
) as app:

    gr.Markdown(
        """
        # SmartFeel AI
        ### Intelligent Sentiment & Customer Experience Platform

        Understand opinions, analyze customer feedback, and monitor social sentiment.
        """,
        elem_id="main-title"
    )

    with gr.Tab("SmartFeel"):
        gr.Markdown("### General Sentiment Analysis")

        smart_text = gr.Textbox(
            label="Enter text",
            placeholder="Write your text here...",
            lines=5
        )

        smart_button = gr.Button("Analyze Text", variant="primary")

        smart_sentiment = gr.Textbox(label="Predicted Sentiment")
        smart_confidence = gr.Textbox(label="Confidence")
        smart_scores = gr.Dataframe(label="Sentiment Probabilities")

        smart_button.click(
            analyze_single,
            inputs=[smart_text, gr.State("SmartFeel")],
            outputs=[
                smart_sentiment,
                smart_confidence,
                smart_scores,
                gr.State()
            ]
        )

    with gr.Tab("ReviewAI"):
        gr.Markdown("### Customer Review Analysis")

        review_text = gr.Textbox(
            label="Customer Review",
            placeholder="Enter a product or service review...",
            lines=5
        )

        review_button = gr.Button("Analyze Review", variant="primary")

        review_sentiment = gr.Textbox(label="Customer Sentiment")
        review_confidence = gr.Textbox(label="Confidence")
        review_scores = gr.Dataframe(label="Sentiment Probabilities")

        review_button.click(
            analyze_single,
            inputs=[review_text, gr.State("ReviewAI")],
            outputs=[
                review_sentiment,
                review_confidence,
                review_scores,
                gr.State()
            ]
        )

    with gr.Tab("SocialMind"):
        gr.Markdown("### Social Media Sentiment Monitoring")

        social_text = gr.Textbox(
            label="Social Media Comments",
            placeholder="Enter one comment per line...",
            lines=8
        )

        social_button = gr.Button("Analyze All Comments", variant="primary")

        social_results = gr.Dataframe(label="Individual Results")
        social_distribution = gr.Dataframe(label="Sentiment Distribution")

        social_button.click(
            analyze_social,
            inputs=social_text,
            outputs=[
                social_results,
                social_distribution,
                gr.State()
            ]
        )

    with gr.Tab("History"):
        gr.Markdown("### Recent Analysis History")

        history_table = gr.Dataframe(
            label="Analysis Records",
            interactive=False
        )

        refresh_button = gr.Button("Refresh History")

        refresh_button.click(
            history_dataframe,
            inputs=None,
            outputs=history_table
        )

    gr.Markdown(
        """
        ---
        **SmartFeel AI** | Powered by RoBERTa

        *An academic AI sentiment analysis project.*
        """
    )


if __name__ == "__main__":
    app.launch()

import gradio as gr
import pandas as pd
import plotly.express as px
from datetime import datetime

from src.sentiment import predict_sentiment, analyze_batch
from src.utils import calculate_distribution, create_history_record


# ==========================================
# APPLICATION DATA
# ==========================================

history = []

COLORS = {
    "Positive": "#22c55e",
    "Neutral": "#f59e0b",
    "Negative": "#ef4444"
}


# ==========================================
# ANALYSIS FUNCTIONS
# ==========================================

def analyze_single(text, section):
    if not text or not text.strip():
        raise gr.Error("Please enter some text.")

    result = predict_sentiment(text)

    record = create_history_record(text, result)
    record["section"] = section
    history.insert(0, record)

    scores = result["scores"]

    chart = px.bar(
        x=list(scores.values()),
        y=list(scores.keys()),
        orientation="h",
        color=list(scores.keys()),
        color_discrete_map=COLORS,
        title="Sentiment Probability"
    )

    chart.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        height=300,
        xaxis_title="Probability (%)",
        yaxis_title=""
    )

    return (
        result["sentiment"],
        f"{result['confidence']}%",
        chart,
        history_dataframe()
    )


def analyze_social(comments):
    if not comments or not comments.strip():
        raise gr.Error("Please enter comments.")

    texts = [
        line.strip()
        for line in comments.splitlines()
        if line.strip()
    ]

    results = analyze_batch(texts)

    for result in results:
        record = create_history_record(result["text"], result)
        record["section"] = "SocialMind"
        history.insert(0, record)

    distribution = calculate_distribution(results)

    results_df = pd.DataFrame([
        {
            "Comment": item["text"],
            "Sentiment": item["sentiment"],
            "Confidence": item["confidence"]
        }
        for item in results
    ])

    chart = px.pie(
        names=list(distribution.keys()),
        values=list(distribution.values()),
        color=list(distribution.keys()),
        color_discrete_map=COLORS,
        hole=0.65,
        title="Social Sentiment Distribution"
    )

    chart.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        height=400
    )

    return results_df, chart, history_dataframe()


def history_dataframe():
    if not history:
        return pd.DataFrame(
            columns=["section", "text", "sentiment", "confidence", "time"]
        )

    return pd.DataFrame(history)


def dashboard_stats():
    total = len(history)

    if total == 0:
        return 0, 0, 0, 0

    positive = sum(
        item["sentiment"] == "Positive" for item in history
    )

    negative = sum(
        item["sentiment"] == "Negative" for item in history
    )

    neutral = sum(
        item["sentiment"] == "Neutral" for item in history
    )

    positive_rate = round(positive / total * 100, 1)

    return total, positive, negative, positive_rate


def make_dashboard():
    total, positive, negative, positive_rate = dashboard_stats()

    df = history_dataframe()

    if total == 0:
        distribution = {
            "Positive": 0,
            "Neutral": 0,
            "Negative": 0
        }
    else:
        distribution = df["sentiment"].value_counts().to_dict()

    chart = px.pie(
        names=list(distribution.keys()),
        values=list(distribution.values()),
        color=list(distribution.keys()),
        color_discrete_map=COLORS,
        hole=0.7
    )

    chart.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=350,
        showlegend=True
    )

    return (
        total,
        positive,
        negative,
        f"{positive_rate}%",
        chart,
        df.head(10)
    )


# ==========================================
# CUSTOM DESIGN
# ==========================================

CSS = """
body {
    background: #080b16 !important;
}

.gradio-container {
    background: #080b16 !important;
    max-width: 1450px !important;
    margin: auto !important;
    color: #f8fafc !important;
}

#header {
    padding: 25px;
    border-radius: 18px;
    background: linear-gradient(120deg, #151a35, #24204a, #101c3c);
    border: 1px solid #34345e;
    margin-bottom: 20px;
}

#header h1 {
    font-size: 36px;
    font-weight: 800;
    background: linear-gradient(90deg, #a78bfa, #38bdf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

#header p {
    color: #a5b4fc;
}

.stat-card {
    background: #12182b;
    border: 1px solid #29334f;
    border-radius: 15px;
    padding: 20px;
    text-align: center;
}

.stat-card h2 {
    color: #94a3b8;
    font-size: 14px;
}

.stat-card p {
    color: #a78bfa;
    font-size: 30px;
    font-weight: 800;
}

button.primary {
    background: linear-gradient(90deg, #7c3aed, #2563eb) !important;
    border: none !important;
}

footer {
    display: none !important;
}
"""


# ==========================================
# GRADIO APPLICATION
# ==========================================

with gr.Blocks(
    title="SmartFeel AI | Intelligence Platform",
    theme=gr.themes.Base(
        primary_hue="violet",
        secondary_hue="blue",
        neutral_hue="slate"
    ),
    css=CSS
) as app:

    gr.HTML("""
    <div id="header">
        <h1>SMARTFEEL AI</h1>
        <p>INTELLIGENT SENTIMENT & CUSTOMER EXPERIENCE PLATFORM</p>
        <p>Understand opinions. Discover emotions. Make smarter decisions.</p>
    </div>
    """)

    # ======================================
    # DASHBOARD
    # ======================================

    with gr.Tab("Dashboard"):

        gr.Markdown("## Platform Overview")
        gr.Markdown("Your sentiment intelligence at a glance.")

        with gr.Row():
            total_output = gr.Number(
                label="Total Analyses",
                value=0,
                interactive=False
            )

            positive_output = gr.Number(
                label="Positive Results",
                value=0,
                interactive=False
            )

            negative_output = gr.Number(
                label="Negative Results",
                value=0,
                interactive=False
            )

            positive_rate_output = gr.Textbox(
                label="Positive Rate",
                value="0%",
                interactive=False
            )

        with gr.Row():
            dashboard_chart = gr.Plot(label="Sentiment Overview")

        dashboard_history = gr.Dataframe(
            label="Recent Activity",
            interactive=False
        )

        refresh_dashboard = gr.Button(
            "Refresh Dashboard",
            variant="primary"
        )

        refresh_dashboard.click(
            make_dashboard,
            outputs=[
                total_output,
                positive_output,
                negative_output,
                positive_rate_output,
                dashboard_chart,
                dashboard_history
            ]
        )

    # ======================================
    # SMARTFEEL
    # ======================================

    with gr.Tab("SmartFeel"):

        gr.Markdown("## AI Text Intelligence")
        gr.Markdown(
            "Analyze any English text using your fine-tuned RoBERTa model."
        )

        smart_text = gr.Textbox(
            label="Your Text",
            placeholder="Enter a sentence, message, or paragraph...",
            lines=6
        )

        smart_button = gr.Button(
            "Analyze Sentiment",
            variant="primary"
        )

        with gr.Row():
            smart_sentiment = gr.Textbox(label="Predicted Sentiment")
            smart_confidence = gr.Textbox(label="Confidence")

        smart_chart = gr.Plot(label="Probability Analysis")

        smart_button.click(
            lambda text: analyze_single(text, "SmartFeel"),
            inputs=smart_text,
            outputs=[
                smart_sentiment,
                smart_confidence,
                smart_chart,
                dashboard_history
            ]
        )

    # ======================================
    # REVIEW AI
    # ======================================

    with gr.Tab("ReviewAI"):

        gr.Markdown("## Customer Experience Intelligence")
        gr.Markdown(
            "Discover how customers feel about products and services."
        )

        review_text = gr.Textbox(
            label="Customer Review",
            placeholder="Example: The product is excellent, but delivery was slow...",
            lines=6
        )

        review_button = gr.Button(
            "Analyze Customer Review",
            variant="primary"
        )

        with gr.Row():
            review_sentiment = gr.Textbox(label="Customer Sentiment")
            review_confidence = gr.Textbox(label="Confidence")

        review_chart = gr.Plot(label="Review Sentiment Analysis")

        review_button.click(
            lambda text: analyze_single(text, "ReviewAI"),
            inputs=review_text,
            outputs=[
                review_sentiment,
                review_confidence,
                review_chart,
                dashboard_history
            ]
        )

    # ======================================
    # SOCIAL MIND
    # ======================================

    with gr.Tab("SocialMind"):

        gr.Markdown("## Social Media Intelligence")
        gr.Markdown(
            "Analyze multiple comments and discover public sentiment."
        )

        social_text = gr.Textbox(
            label="Social Media Comments",
            placeholder="Enter one comment per line...",
            lines=9
        )

        social_button = gr.Button(
            "Analyze All Comments",
            variant="primary"
        )

        social_results = gr.Dataframe(
            label="Individual Comment Analysis"
        )

        social_chart = gr.Plot(
            label="Social Sentiment Distribution"
        )

        social_button.click(
            analyze_social,
            inputs=social_text,
            outputs=[
                social_results,
                social_chart,
                dashboard_history
            ]
        )

    # ======================================
    # HISTORY
    # ======================================

    with gr.Tab("History"):

        gr.Markdown("## Analysis History")
        gr.Markdown("Review previous analyses from this application session.")

        history_table = gr.Dataframe(
            value=history_dataframe(),
            label="All Analysis Records",
            interactive=False
        )

        history_refresh = gr.Button("Refresh History")

        history_refresh.click(
            history_dataframe,
            outputs=history_table
        )

    # ======================================
    # FOOTER
    # ======================================

    gr.HTML("""
    <div style="
        text-align:center;
        padding:25px;
        color:#64748b;
        border-top:1px solid #29334f;
        margin-top:25px;
    ">
        <h3 style="color:#a78bfa;">SMARTFEEL AI</h3>
        <p>Powered by Fine-Tuned RoBERTa | Academic AI Project</p>
        <p>Built with Python, PyTorch, Transformers and Gradio</p>
    </div>
    """)


if __name__ == "__main__":
    app.launch()
