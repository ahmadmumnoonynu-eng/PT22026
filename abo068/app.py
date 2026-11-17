import csv
from pathlib import Path
from html import escape

import gradio as gr
import plotly.graph_objects as go

from src.sentiment import predict_sentiment
from src.history import add_history_record, get_history, clear_history


# =========================================================
# CONFIGURATION
# =========================================================

COLORS = {
    "Positive": "#16a36a",
    "Neutral": "#d99a24",
    "Negative": "#e05252"
}

SAMPLES = {
    "Positive": (
        "I absolutely love this product! "
        "The quality is excellent and the service was amazing."
    ),
    "Neutral": (
        "The product arrived yesterday. "
        "It has the features described on the website."
    ),
    "Negative": (
        "I am very disappointed with this product. "
        "The quality is terrible and customer service was unhelpful."
    )
}

EMPTY_PLAYGROUND = """
<div class="empty-state">
    <div class="empty-symbol">✦</div>
    <h3>Ready when you are</h3>
    <p>Enter text to discover its sentiment.</p>
</div>
"""

EMPTY_REVIEW = """
<div class="empty-state">
    <div class="empty-symbol">◈</div>
    <h3>Waiting for a review</h3>
    <p>Enter a product and customer review to see its sentiment.</p>
</div>
"""

EMPTY_SOCIAL = """
<div class="empty-state">
    <div class="empty-symbol">◎</div>
    <h3>Waiting for comments</h3>
    <p>Paste social media comments to start your analysis.</p>
</div>
"""


# =========================================================
# SHARED RESULT DISPLAY
# =========================================================

def create_result_html(result, heading="Analysis result"):
    sentiment = result["sentiment"]
    confidence = result["confidence"]
    scores = result["scores"]
    color = COLORS.get(sentiment, "#64748b")

    bars = ""
    for label in ["Positive", "Neutral", "Negative"]:
        score = scores[label]
        bars += f"""
        <div class="score-item">
            <div class="score-header">
                <span><span class="dot" style="background:{COLORS[label]}"></span>{label}</span>
                <strong>{score:.2f}%</strong>
            </div>
            <div class="bar-background">
                <div class="bar-fill" style="width:{max(0, min(100, score))}%;background:{COLORS[label]}"></div>
            </div>
        </div>
        """

    return f"""
    <div class="result-content">
        <div class="result-status">✓ ANALYSIS COMPLETED</div>
        <div class="result-heading">{escape(heading)}</div>
        <div class="prediction" style="color:{color}">{escape(sentiment)}</div>
        <div class="confidence-card">
            <div class="confidence-label">MODEL CONFIDENCE</div>
            <div class="confidence-number">{confidence:.2f}%</div>
            <div class="confidence-description">Highest predicted class probability</div>
        </div>
        <div class="breakdown-title">Sentiment probability</div>
        {bars}
        <div class="result-explanation">
            <strong>Understanding the result</strong>
            <p>The model selects the sentiment with the highest probability. Confidence is a model score, not a guarantee of correctness.</p>
        </div>
    </div>
    """


# =========================================================
# AI PLAYGROUND
# =========================================================

def analyze_text(text):
    if not text or not text.strip():
        raise gr.Error("Please enter some text before analyzing.")

    try:
        result = predict_sentiment(text.strip())
        add_history_record("AI Playground", text.strip(), result)
        return create_result_html(result)
    except gr.Error:
        raise
    except Exception as error:
        raise gr.Error(f"Analysis failed: {str(error)}")


def clear_workspace():
    return "", EMPTY_PLAYGROUND


# =========================================================
# REVIEWAI
# =========================================================

def analyze_review(product_name, review_text):
    if not product_name or not product_name.strip():
        raise gr.Error("Please enter the product name.")
    if not review_text or not review_text.strip():
        raise gr.Error("Please enter a customer review.")

    try:
        result = predict_sentiment(review_text.strip())
        saved_text = f"Product: {product_name.strip()}\nReview: {review_text.strip()}"
        add_history_record("ReviewAI", saved_text, result)

        return f"""
        <div class="review-product-card">
            <div class="review-product-label">PRODUCT</div>
            <div class="review-product-name">{escape(product_name.strip())}</div>
            <div class="review-product-label">CUSTOMER REVIEW</div>
            <div class="review-quote">"{escape(review_text.strip())}"</div>
        </div>
        {create_result_html(result, "Customer review sentiment")}
        """
    except gr.Error:
        raise
    except Exception as error:
        raise gr.Error(f"Review analysis failed: {str(error)}")


def clear_review():
    return "", "", EMPTY_REVIEW


# =========================================================
# SOCIALMIND
# =========================================================

def analyze_social_comments(comments_text):
    if not comments_text or not comments_text.strip():
        raise gr.Error("Please paste some social media comments.")

    comments = [line.strip() for line in comments_text.splitlines() if line.strip()]
    if len(comments) < 2:
        raise gr.Error("Please enter at least 2 comments.")
    if len(comments) > 30:
        raise gr.Error("Please enter no more than 30 comments at a time.")

    results = []
    try:
        for comment in comments:
            prediction = predict_sentiment(comment)
            results.append({
                "text": comment,
                "sentiment": prediction["sentiment"],
                "confidence": prediction["confidence"]
            })
            add_history_record("SocialMind", comment, prediction)
    except Exception as error:
        raise gr.Error(f"Social analysis failed: {str(error)}")

    total = len(results)
    counts = {"Positive": 0, "Neutral": 0, "Negative": 0}
    for result in results:
        counts[result["sentiment"]] += 1

    percentages = {label: counts[label] / total * 100 for label in counts}
    overall = max(counts, key=counts.get)

    summary_cards = ""
    for label in ["Positive", "Neutral", "Negative"]:
        percentage = percentages[label]
        summary_cards += f"""
        <div class="social-summary-card">
            <div class="social-summary-label">
                <span class="dot" style="background:{COLORS[label]}"></span>{label.upper()}
            </div>
            <div class="social-summary-number">{percentage:.1f}%</div>
            <div class="social-summary-count">{counts[label]} of {total} comments</div>
            <div class="bar-background">
                <div class="bar-fill" style="width:{percentage}%;background:{COLORS[label]}"></div>
            </div>
        </div>
        """

    comment_rows = ""
    for index, result in enumerate(results, start=1):
        sentiment = result["sentiment"]
        color = COLORS[sentiment]
        comment_rows += f"""
        <div class="comment-result">
            <div class="comment-number">{index:02d}</div>
            <div class="comment-content">
                <div class="comment-text">{escape(result["text"])}</div>
                <div class="comment-confidence">Confidence: {result["confidence"]:.2f}%</div>
            </div>
            <div class="comment-sentiment" style="color:{color};background:{color}16;border:1px solid {color}35">
                {escape(sentiment)}
            </div>
        </div>
        """

    return f"""
    <div class="social-results">
        <div class="social-complete">✓ BATCH ANALYSIS COMPLETED</div>
        <div class="social-overall">
            <div>
                <div class="social-overall-label">MOST COMMON SENTIMENT</div>
                <div class="social-overall-value" style="color:{COLORS[overall]}">{overall}</div>
            </div>
            <div class="social-total">
                <div class="social-total-number">{total}</div>
                <div class="social-total-label">COMMENTS ANALYZED</div>
            </div>
        </div>
        <div class="social-section-title">Sentiment distribution</div>
        <div class="social-summary-grid">{summary_cards}</div>
        <div class="social-section-title">Individual comment analysis</div>
        {comment_rows}
        <div class="result-explanation">
            <strong>How to understand this summary</strong>
            <p>The overall sentiment is the most frequent predicted category among the submitted comments. Each comment is classified independently.</p>
        </div>
    </div>
    """


def clear_social():
    return "", EMPTY_SOCIAL


# =========================================================
# HISTORY
# =========================================================

def render_history(sentiment_filter="All", source_filter="All", search_text=""):
    records = get_history()
    filtered = []

    for record in records:
        if sentiment_filter != "All" and record.get("sentiment") != sentiment_filter:
            continue
        if source_filter != "All" and record.get("source") != source_filter:
            continue
        if search_text and search_text.strip().lower() not in record.get("text", "").lower():
            continue
        filtered.append(record)

    total = len(records)
    positive = sum(1 for r in records if r.get("sentiment") == "Positive")
    neutral = sum(1 for r in records if r.get("sentiment") == "Neutral")
    negative = sum(1 for r in records if r.get("sentiment") == "Negative")

    stats_html = f"""
    <div class="history-stats">
        <div class="history-stat"><span>TOTAL ANALYSES</span><strong>{total}</strong></div>
        <div class="history-stat"><span>POSITIVE</span><strong style="color:{COLORS['Positive']}">{positive}</strong></div>
        <div class="history-stat"><span>NEUTRAL</span><strong style="color:{COLORS['Neutral']}">{neutral}</strong></div>
        <div class="history-stat"><span>NEGATIVE</span><strong style="color:{COLORS['Negative']}">{negative}</strong></div>
    </div>
    """

    if not filtered:
        return stats_html + """
        <div class="history-empty">
            <div style="font-size:30px;margin-bottom:12px">◷</div>
            <h3>No analyses found</h3>
            <p>Try changing your filters or run a new analysis.</p>
        </div>
        """

    rows = ""
    for record in filtered:
        sentiment = record.get("sentiment", "Unknown")
        color = COLORS.get(sentiment, "#64748b")
        confidence = float(record.get("confidence", 0))
        rows += f"""
        <div class="history-record">
            <div class="history-record-top">
                <span class="history-source">{escape(record.get("source", "Unknown"))}</span>
                <span class="history-time">{escape(record.get("time", ""))}</span>
            </div>
            <div class="history-text">{escape(record.get("text", ""))}</div>
            <div class="history-record-bottom">
                <span class="history-sentiment" style="color:{color};background:{color}15">{escape(sentiment)}</span>
                <span class="history-confidence">Confidence: {confidence:.2f}%</span>
            </div>
        </div>
        """

    return stats_html + f"""
    <div class="history-results-label">Showing {len(filtered)} of {total} saved analyses</div>
    {rows}
    """


def refresh_history(sentiment_filter, source_filter, search_text):
    return render_history(sentiment_filter, source_filter, search_text)


def clear_history_page():
    clear_history()
    return render_history("All", "All", ""), None


def export_history():
    records = get_history()
    if not records:
        raise gr.Error("There is no history to export.")

    data_folder = Path(__file__).resolve().parent / "data"
    data_folder.mkdir(parents=True, exist_ok=True)
    export_path = data_folder / "history_export.csv"

    with open(export_path, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow(["Source", "Text", "Sentiment", "Confidence", "Time"])
        for record in records:
            writer.writerow([
                record.get("source", ""),
                record.get("text", ""),
                record.get("sentiment", ""),
                record.get("confidence", ""),
                record.get("time", "")
            ])
    return str(export_path)


# =========================================================
# DASHBOARD CHART
# =========================================================

def create_dashboard_chart():
    records = get_history()
    counts = {"Positive": 0, "Neutral": 0, "Negative": 0}

    for record in records:
        sentiment = record.get("sentiment")
        if sentiment in counts:
            counts[sentiment] += 1

    labels = list(counts.keys())
    values = list(counts.values())
    total = len(records)

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.68,
                marker=dict(colors=[COLORS[label] for label in labels]),
                textinfo="label+percent",
                textposition="outside",
                hovertemplate="%{label}<br>Analyses: %{value}<br>Percentage: %{percent}<extra></extra>"
            )
        ]
    )

    fig.update_layout(
        title={"text": "Sentiment Distribution", "x": 0.04, "font": {"size": 17, "color": "#26344c"}},
        annotations=[{
            "text": f"<b>{total}</b><br>Analyses",
            "x": 0.5,
            "y": 0.5,
            "font": {"size": 19, "color": "#26344c"},
            "showarrow": False
        }],
        height=380,
        showlegend=True,
        legend={"orientation": "h", "yanchor": "bottom", "y": -0.15, "xanchor": "center", "x": 0.5},
        margin={"t": 65, "b": 45, "l": 30, "r": 30},
        paper_bgcolor="white",
        plot_bgcolor="white"
    )
    return fig


# =========================================================
# NAVIGATION
# =========================================================

def show_page(selected_page):
    pages = ["playground", "dashboard", "review", "social", "history"]
    return tuple(gr.update(visible=(page == selected_page)) for page in pages)


# =========================================================
# DESIGN
# =========================================================

CSS = """
.gradio-container{max-width:100%!important;padding:0!important;margin:0!important;background:#f5f6fa!important;color:#19243a!important;font-family:Inter,Arial,sans-serif!important}
footer{display:none!important}
#application-layout{gap:0!important;align-items:stretch!important;min-height:100vh}
#sidebar{background:#14213a!important;min-width:245px!important;max-width:245px!important;padding:25px 17px!important;min-height:100vh}
.sidebar-brand{display:flex;align-items:center;gap:12px;padding:4px 8px 35px}
.sidebar-logo{width:41px;height:41px;border-radius:12px;display:flex;justify-content:center;align-items:center;background:linear-gradient(135deg,#9176ff,#624bd2);color:white;font-size:23px;font-weight:850}
.sidebar-name{font-size:18px;font-weight:850;color:white}.sidebar-caption{font-size:9px;color:#8e9db7;letter-spacing:1.2px;margin-top:3px}
.sidebar-label{font-size:9px;font-weight:800;letter-spacing:1.6px;color:#72829e;padding:0 12px;margin:18px 0 11px}
#nav-playground button,#nav-dashboard button,#nav-review button,#nav-social button,#nav-history button{width:100%;min-height:43px;justify-content:flex-start;text-align:left;border-radius:9px;font-size:12px;font-weight:650;margin-bottom:6px;background:transparent;border:1px solid transparent;color:#aab7cc}
#nav-playground button:hover,#nav-dashboard button:hover,#nav-review button:hover,#nav-social button:hover,#nav-history button:hover{background:#34315f;color:white}
.sidebar-bottom{margin-top:65px;border-top:1px solid #2c3a53;padding:20px 9px 0}.sidebar-bottom p{font-size:10px;line-height:1.8;color:#8292ad}
#main-content,#dashboard-page,#review-page,#social-page,#history-page{background:#f5f6fa!important;padding:32px 42px!important;min-width:0}
.topbar{display:flex;justify-content:space-between;align-items:center;padding-bottom:24px;border-bottom:1px solid #e6e9f0;margin-bottom:35px}
.breadcrumb{font-size:11px;color:#8994a8}.breadcrumb strong{color:#53617a}
.engine-badge{display:flex;align-items:center;gap:8px;background:white;border:1px solid #e2e9e4;border-radius:30px;padding:8px 13px;color:#18834e;font-size:10px;font-weight:750}
.engine-dot{width:7px;height:7px;background:#22b573;border-radius:50%}
.page-eyebrow{font-size:10px;font-weight:800;color:#7559dc;letter-spacing:1.8px;margin-bottom:11px}
.page-title{font-size:32px;line-height:1.2;letter-spacing:-1.1px;font-weight:850;color:#19243a;margin:0}
.page-description{font-size:13px;color:#7d899e;line-height:1.8;max-width:620px;margin:11px 0 28px}
#workspace-row{gap:19px!important;align-items:stretch!important}
#input-panel,#output-panel,#review-input-panel,#review-output-panel,#social-input-panel,#social-output-panel{background:white!important;border:1px solid #e7eaf1!important;border-radius:15px!important;padding:23px!important;box-shadow:0 5px 20px rgba(27,42,68,.035);min-height:530px}
.panel-title{font-size:16px;color:#1d2940;font-weight:800;margin-bottom:6px}.panel-description{color:#8b96a9;font-size:11px;line-height:1.7;margin-bottom:21px}
textarea,input{background:#fbfcfe!important;border:1px solid #dfe4ee!important;border-radius:10px!important;color:#253149!important;font-size:13px!important}
textarea:focus,input:focus{border-color:#8972e8!important;box-shadow:0 0 0 3px #8972e81c!important}
.example-label{font-size:10px;color:#7d899e;font-weight:800;letter-spacing:1px;margin:17px 0 9px}
#positive-example button{background:#edf9f2!important;color:#16834e!important;border:1px solid #d3eddd!important;font-size:10px!important}
#neutral-example button{background:#fff8e9!important;color:#a66d0d!important;border:1px solid #f0e2bf!important;font-size:10px!important}
#negative-example button{background:#fff0f0!important;color:#c44444!important;border:1px solid #f2d4d4!important;font-size:10px!important}
#analyze-button,#review-analyze-button,#social-analyze-button{background:linear-gradient(110deg,#7659df,#5a62d7)!important;color:white!important;border:0!important;border-radius:9px!important;min-height:46px!important;font-weight:800!important;font-size:12px!important}
#clear-button,#review-clear-button,#social-clear-button{background:#f2f4f8!important;border:1px solid #e3e7ef!important;color:#59677e!important;border-radius:9px!important;min-height:46px!important;font-size:12px!important}
.empty-state{min-height:390px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}
.empty-symbol{width:61px;height:61px;background:#f0edff;color:#7659df;border-radius:18px;display:flex;align-items:center;justify-content:center;font-size:28px;margin-bottom:18px}
.empty-state h3{font-size:16px;color:#28354c;margin:0 0 8px}.empty-state p{font-size:11px;line-height:1.8;color:#8b96a9;max-width:230px}
.result-status{color:#16834e;font-size:9px;letter-spacing:1px;font-weight:800;margin-bottom:25px}.result-heading{font-size:12px;color:#7e8ba0;font-weight:700}
.prediction{font-size:35px;font-weight:850;margin:7px 0 20px}
.confidence-card{background:#f7f8fc;border:1px solid #e8ebf2;border-radius:11px;padding:17px;margin-bottom:25px}
.confidence-label{font-size:9px;font-weight:800;letter-spacing:1px;color:#8792a5}.confidence-number{font-size:27px;font-weight:850;color:#26344c;margin-top:7px}.confidence-description{font-size:10px;color:#8c97aa;margin-top:3px}
.breakdown-title{color:#26344b;font-size:13px;font-weight:800;margin-bottom:19px}.score-item{margin-bottom:18px}
.score-header{display:flex;justify-content:space-between;color:#536079;font-size:11px;margin-bottom:8px}.score-header strong{color:#29354a}
.dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:7px}
.bar-background{height:8px;background:#edf0f5;border-radius:20px;overflow:hidden}.bar-fill{height:100%;border-radius:20px}
.result-explanation{background:#f3f1ff;border:1px solid #e7e2ff;border-radius:10px;padding:13px;margin-top:24px}
.result-explanation strong{font-size:10px;color:#624fbd}.result-explanation p{font-size:10px;color:#797590;line-height:1.7;margin-top:5px}
.review-product-card{background:#f7f8fc;border:1px solid #e8ebf2;border-radius:11px;padding:16px;margin-bottom:22px}
.review-product-label{color:#8994a8;font-size:9px;font-weight:800;letter-spacing:1px;margin-bottom:7px}
.review-product-name{font-size:17px;font-weight:800;color:#26344c;margin-bottom:17px}.review-quote{color:#59677e;font-size:12px;line-height:1.8}
.dashboard-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:17px;margin:25px 0}
.dashboard-card,.dashboard-section{background:white;border:1px solid #e7eaf1;border-radius:14px;padding:23px;box-shadow:0 5px 20px rgba(27,42,68,.035)}
.dashboard-card-label{color:#8792a5;font-size:10px;font-weight:800;letter-spacing:1px}.dashboard-number{font-size:30px;font-weight:850;color:#26344c;margin:15px 0 7px}.dashboard-note{font-size:11px;color:#8994a8}
.dashboard-section{margin-top:19px}.dashboard-section h2{font-size:16px;color:#26344c;margin:0 0 10px}.dashboard-section p{color:#7d899e;font-size:12px;line-height:1.8}
.performance-row{display:flex;justify-content:space-between;padding:14px 0;border-bottom:1px solid #edf0f5;font-size:12px;color:#59677e}.performance-row strong{color:#29354a}
.social-complete{color:#16834e;font-size:10px;font-weight:800;letter-spacing:1px;margin-bottom:22px}
.social-overall{display:flex;justify-content:space-between;align-items:center;background:#f7f8fc;border:1px solid #e8ebf2;border-radius:12px;padding:19px;margin-bottom:24px}
.social-overall-label,.social-total-label{font-size:9px;color:#8994a8;font-weight:800;letter-spacing:1px}.social-overall-value{font-size:25px;font-weight:850;margin-top:7px}
.social-total{text-align:right}.social-total-number{font-size:27px;font-weight:850;color:#26344c}.social-total-label{margin-top:4px}
.social-section-title{font-size:14px;color:#26344c;font-weight:850;margin:24px 0 15px}
.social-summary-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}
.social-summary-card{border:1px solid #e8ebf2;border-radius:11px;padding:13px;background:white;min-width:0}
.social-summary-label{font-size:9px;color:#78859a;font-weight:800}.social-summary-number{font-size:22px;font-weight:850;color:#26344c;margin:10px 0 4px}
.social-summary-count{color:#8994a8;font-size:9px;margin-bottom:12px}
.comment-result{display:flex;align-items:flex-start;gap:12px;padding:15px 0;border-bottom:1px solid #edf0f5}
.comment-number{color:#9aa4b5;font-size:10px;font-weight:800;padding-top:3px}.comment-content{flex:1;min-width:0}
.comment-text{font-size:11px;line-height:1.7;color:#45536b;overflow-wrap:anywhere}.comment-confidence{color:#929db0;font-size:9px;margin-top:6px}
.comment-sentiment{font-size:9px;font-weight:800;padding:6px 9px;border-radius:20px;white-space:nowrap}
.history-stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin:25px 0}
.history-stat{background:white;border:1px solid #e7eaf1;border-radius:13px;padding:20px}
.history-stat span{display:block;color:#8792a5;font-size:9px;font-weight:800;letter-spacing:1px}
.history-stat strong{display:block;font-size:27px;color:#26344c;margin-top:12px}
.history-empty{background:white;border:1px solid #e7eaf1;border-radius:14px;padding:55px 20px;text-align:center;color:#8994a8}
.history-empty h3{color:#26344c;font-size:16px}.history-empty p{font-size:11px}
.history-results-label{color:#8792a5;font-size:11px;margin:20px 0 12px}
.history-record{background:white;border:1px solid #e7eaf1;border-radius:12px;padding:18px;margin-bottom:12px}
.history-record-top,.history-record-bottom{display:flex;justify-content:space-between;align-items:center;gap:10px}
.history-source{color:#7057d8;font-size:10px;font-weight:800}.history-time{color:#929db0;font-size:10px}
.history-text{color:#45536b;font-size:12px;line-height:1.8;margin:16px 0;white-space:pre-wrap;overflow-wrap:anywhere}
.history-sentiment{font-size:10px;font-weight:800;padding:6px 10px;border-radius:20px}.history-confidence{color:#7d899e;font-size:10px}
.bottom-footer{border-top:1px solid #e4e8f0;margin-top:35px;padding:20px 0;color:#9aa4b5;font-size:10px}
@media(max-width:850px){.dashboard-grid,.social-summary-grid{grid-template-columns:1fr}.history-stats{grid-template-columns:repeat(2,minmax(0,1fr))}#main-content,#dashboard-page,#review-page,#social-page,#history-page{padding:25px 20px!important}}
@media(max-width:700px){#application-layout{flex-direction:column!important}#sidebar{min-height:auto!important;min-width:100%!important;max-width:100%!important}#main-content,#dashboard-page,#review-page,#social-page,#history-page{padding:22px 15px!important}.page-title{font-size:26px}}
"""


# =========================================================
# APPLICATION INTERFACE
# =========================================================

with gr.Blocks(
    title="SmartFeel AI | Intelligence Platform",
    theme=gr.themes.Soft(
        primary_hue="violet",
        secondary_hue="slate",
        neutral_hue="slate"
    ),
    css=CSS
) as app:

    with gr.Row(elem_id="application-layout"):

        # SIDEBAR
        with gr.Column(scale=0, min_width=245, elem_id="sidebar"):
            gr.HTML("""
            <div class="sidebar-brand">
                <div class="sidebar-logo">S</div>
                <div>
                    <div class="sidebar-name">SmartFeel AI</div>
                    <div class="sidebar-caption">INTELLIGENCE PLATFORM</div>
                </div>
            </div>
            <div class="sidebar-label">WORKSPACE</div>
            """)
            playground_btn = gr.Button("✦   AI Playground", elem_id="nav-playground")
            gr.HTML('<div class="sidebar-label">ANALYTICS</div>')
            dashboard_btn = gr.Button("▦   Dashboard", elem_id="nav-dashboard")
            review_btn = gr.Button("◈   ReviewAI", elem_id="nav-review")
            social_btn = gr.Button("◎   SocialMind", elem_id="nav-social")
            history_btn = gr.Button("◷   History", elem_id="nav-history")
            gr.HTML("""
            <div class="sidebar-bottom">
                <p>SMARTFEEL AI<br>Powered by Fine-Tuned RoBERTa<br>Version 1.0</p>
            </div>
            """)

        # AI PLAYGROUND
        with gr.Column(scale=1, elem_id="main-content") as main_content:
            gr.HTML("""
            <div class="topbar">
                <div class="breadcrumb">Workspace / <strong>AI Playground</strong></div>
                <div class="engine-badge"><span class="engine-dot"></span>AI ENGINE ONLINE</div>
            </div>
            <div class="page-eyebrow">SENTIMENT INTELLIGENCE</div>
            <h1 class="page-title">Understand what people feel.</h1>
            <div class="page-description">Explore opinions with your own AI sentiment model. Enter a message, test an example, and discover the emotion behind the words.</div>
            """)
            with gr.Row(elem_id="workspace-row"):
                with gr.Column(scale=11, elem_id="input-panel"):
                    gr.HTML('<div class="panel-title">Text analysis</div><div class="panel-description">Write or paste your text below.</div>')
                    text_input = gr.Textbox(label="YOUR TEXT", placeholder="Start typing here...", lines=9, max_lines=14)
                    gr.HTML('<div class="example-label">TRY A SAMPLE</div>')
                    with gr.Row():
                        positive_btn = gr.Button("Positive", elem_id="positive-example")
                        neutral_btn = gr.Button("Neutral", elem_id="neutral-example")
                        negative_btn = gr.Button("Negative", elem_id="negative-example")
                    positive_btn.click(lambda: SAMPLES["Positive"], outputs=text_input)
                    neutral_btn.click(lambda: SAMPLES["Neutral"], outputs=text_input)
                    negative_btn.click(lambda: SAMPLES["Negative"], outputs=text_input)
                    with gr.Row():
                        analyze_btn = gr.Button("✦  Analyze sentiment", elem_id="analyze-button")
                        clear_btn = gr.Button("Clear", elem_id="clear-button")
                with gr.Column(scale=9, elem_id="output-panel"):
                    gr.HTML('<div class="panel-title">Analysis results</div><div class="panel-description">Your AI prediction and confidence breakdown.</div>')
                    result_output = gr.HTML(EMPTY_PLAYGROUND)
            gr.HTML('<div class="bottom-footer"><strong>SMARTFEEL AI</strong> · Fine-Tuned RoBERTa</div>')
            analyze_btn.click(analyze_text, inputs=text_input, outputs=result_output)
            clear_btn.click(clear_workspace, outputs=[text_input, result_output])

        # DASHBOARD
        with gr.Column(scale=1, elem_id="dashboard-page", visible=False) as dashboard_page:
            gr.HTML("""
            <div class="topbar">
                <div class="breadcrumb">Workspace / <strong>Dashboard</strong></div>
                <div class="engine-badge"><span class="engine-dot"></span>AI ENGINE ONLINE</div>
            </div>
            <div class="page-eyebrow">SMARTFEEL OVERVIEW</div>
            <h1 class="page-title">Your intelligence overview.</h1>
            <div class="page-description">Explore the performance and capabilities of your AI sentiment analysis system.</div>
            <div class="dashboard-grid">
                <div class="dashboard-card"><div class="dashboard-card-label">MODEL TEST ACCURACY</div><div class="dashboard-number">73.05%</div><div class="dashboard-note">Final calibrated model</div></div>
                <div class="dashboard-card"><div class="dashboard-card-label">MACRO F1 SCORE</div><div class="dashboard-number">0.728</div><div class="dashboard-note">Test dataset performance</div></div>
                <div class="dashboard-card"><div class="dashboard-card-label">SENTIMENT CLASSES</div><div class="dashboard-number">03</div><div class="dashboard-note">Positive · Neutral · Negative</div></div>
            </div>
            <div class="dashboard-section">
                <h2>Model performance</h2>
                <p>Fine-tuned RoBERTa trained for English sentiment classification.</p>
                <div class="performance-row"><span>Negative sentiment F1</span><strong>0.74</strong></div>
                <div class="performance-row"><span>Neutral sentiment F1</span><strong>0.73</strong></div>
                <div class="performance-row"><span>Positive sentiment F1</span><strong>0.71</strong></div>
            </div>
            <div class="dashboard-section">
                <h2>About the model</h2>
                <p>The model was fine-tuned using the CardiffNLP TweetEval sentiment dataset. It predicts three sentiment categories from English text.</p>
                <p>These are offline test results, not live customer activity statistics.</p>
            </div>
            """)
            with gr.Column(elem_classes=["dashboard-section"]):
                gr.HTML("""
                <h2>Sentiment analytics</h2>
                <p>Distribution of positive, neutral and negative predictions from your saved analyses.</p>
                """)
                dashboard_chart = gr.Plot(value=create_dashboard_chart(), show_label=False)
            gr.HTML('<div class="bottom-footer"><strong>SMARTFEEL AI</strong> · Model overview</div>')

        # REVIEWAI
        with gr.Column(scale=1, elem_id="review-page", visible=False) as review_page:
            gr.HTML("""
            <div class="topbar"><div class="breadcrumb">Analytics / <strong>ReviewAI</strong></div><div class="engine-badge"><span class="engine-dot"></span>AI ENGINE ONLINE</div></div>
            <div class="page-eyebrow">CUSTOMER EXPERIENCE INTELLIGENCE</div>
            <h1 class="page-title">Understand every customer review.</h1>
            <div class="page-description">Analyze product feedback and discover whether customers are satisfied, neutral, or disappointed.</div>
            """)
            with gr.Row(elem_id="workspace-row"):
                with gr.Column(scale=11, elem_id="review-input-panel"):
                    gr.HTML('<div class="panel-title">Review analysis</div><div class="panel-description">Enter the product and paste its customer review.</div>')
                    product_input = gr.Textbox(label="PRODUCT NAME", placeholder="Example: Wireless Headphones")
                    review_input = gr.Textbox(label="CUSTOMER REVIEW", placeholder="Paste a customer review here...", lines=10, max_lines=15)
                    gr.HTML('<div class="panel-description">ReviewAI currently analyzes English reviews.</div>')
                    with gr.Row():
                        review_analyze_btn = gr.Button("✦  Analyze review", elem_id="review-analyze-button")
                        review_clear_btn = gr.Button("Clear", elem_id="review-clear-button")
                with gr.Column(scale=9, elem_id="review-output-panel"):
                    gr.HTML('<div class="panel-title">Review insights</div><div class="panel-description">Sentiment prediction for your customer review.</div>')
                    review_output = gr.HTML(EMPTY_REVIEW)
            gr.HTML('<div class="bottom-footer"><strong>SMARTFEEL AI</strong> · ReviewAI</div>')
            review_analyze_btn.click(analyze_review, inputs=[product_input, review_input], outputs=review_output)
            review_clear_btn.click(clear_review, outputs=[product_input, review_input, review_output])

        # SOCIALMIND
        with gr.Column(scale=1, elem_id="social-page", visible=False) as social_page:
            gr.HTML("""
            <div class="topbar"><div class="breadcrumb">Analytics / <strong>SocialMind</strong></div><div class="engine-badge"><span class="engine-dot"></span>AI ENGINE ONLINE</div></div>
            <div class="page-eyebrow">SOCIAL MEDIA INTELLIGENCE</div>
            <h1 class="page-title">Listen to what people are saying.</h1>
            <div class="page-description">Analyze multiple social media comments together. Discover the overall sentiment and inspect every individual prediction.</div>
            <div class="dashboard-grid">
                <div class="dashboard-card"><div class="dashboard-card-label">ANALYSIS MODE</div><div class="dashboard-number" style="font-size:22px">Batch AI</div><div class="dashboard-note">Multiple comments at once</div></div>
                <div class="dashboard-card"><div class="dashboard-card-label">MAXIMUM COMMENTS</div><div class="dashboard-number">30</div><div class="dashboard-note">Per analysis</div></div>
                <div class="dashboard-card"><div class="dashboard-card-label">SENTIMENT TYPES</div><div class="dashboard-number">03</div><div class="dashboard-note">Positive · Neutral · Negative</div></div>
            </div>
            """)
            with gr.Row(elem_id="workspace-row"):
                with gr.Column(scale=10, elem_id="social-input-panel"):
                    gr.HTML('<div class="panel-title">Social media comments</div><div class="panel-description">Paste your comments below. Put each comment on a separate line.</div>')
                    social_input = gr.Textbox(label="COMMENTS", placeholder="I love this new product!\nThe delivery was very slow.\nIt is okay, nothing special.\nAmazing quality, I recommend it!", lines=12, max_lines=18)
                    gr.HTML('<div class="panel-description">Maximum 30 comments per analysis. Empty lines are ignored.</div>')
                    with gr.Row():
                        social_analyze_btn = gr.Button("✦  Analyze all comments", elem_id="social-analyze-button")
                        social_clear_btn = gr.Button("Clear", elem_id="social-clear-button")
                with gr.Column(scale=12, elem_id="social-output-panel"):
                    gr.HTML('<div class="panel-title">Social intelligence results</div><div class="panel-description">Overall sentiment distribution and individual comment predictions.</div>')
                    social_output = gr.HTML(EMPTY_SOCIAL)
            gr.HTML('<div class="bottom-footer"><strong>SMARTFEEL AI</strong> · SocialMind</div>')
            social_analyze_btn.click(analyze_social_comments, inputs=social_input, outputs=social_output)
            social_clear_btn.click(clear_social, outputs=[social_input, social_output])

        # HISTORY
        with gr.Column(scale=1, elem_id="history-page", visible=False) as history_page:
            gr.HTML("""
            <div class="topbar"><div class="breadcrumb">Workspace / <strong>History</strong></div><div class="engine-badge"><span class="engine-dot"></span>HISTORY STORAGE ACTIVE</div></div>
            <div class="page-eyebrow">YOUR PREVIOUS ANALYSES</div>
            <h1 class="page-title">Analysis history.</h1>
            <div class="page-description">Review your previous sentiment analyses, search saved results, and export your records.</div>
            """)
            with gr.Row():
                history_sentiment = gr.Dropdown(choices=["All", "Positive", "Neutral", "Negative"], value="All", label="Filter by sentiment")
                history_source = gr.Dropdown(choices=["All", "AI Playground", "ReviewAI", "SocialMind", "Test"], value="All", label="Filter by source")
            history_search = gr.Textbox(label="SEARCH HISTORY", placeholder="Search for words in previous analyses...")
            with gr.Row():
                history_refresh_btn = gr.Button("Refresh history")
                history_export_btn = gr.Button("Export CSV")
                history_clear_btn = gr.Button("Clear history", variant="stop")
            history_download = gr.File(label="Your CSV export", interactive=False)
            history_output = gr.HTML(render_history())
            history_refresh_btn.click(refresh_history, inputs=[history_sentiment, history_source, history_search], outputs=history_output)
            history_sentiment.change(refresh_history, inputs=[history_sentiment, history_source, history_search], outputs=history_output)
            history_source.change(refresh_history, inputs=[history_sentiment, history_source, history_search], outputs=history_output)
            history_search.submit(refresh_history, inputs=[history_sentiment, history_source, history_search], outputs=history_output)
            history_export_btn.click(export_history, outputs=history_download)
            history_clear_btn.click(clear_history_page, outputs=[history_output, history_download])

    # NAVIGATION
    page_outputs = [main_content, dashboard_page, review_page, social_page, history_page]

    playground_btn.click(lambda: show_page("playground"), outputs=page_outputs)
    dashboard_btn.click(
        lambda: show_page("dashboard"),
        outputs=page_outputs
    ).then(
        create_dashboard_chart,
        outputs=dashboard_chart
    )
    review_btn.click(lambda: show_page("review"), outputs=page_outputs)
    social_btn.click(lambda: show_page("social"), outputs=page_outputs)
    history_btn.click(
        lambda: show_page("history"),
        outputs=page_outputs
    ).then(
        lambda: render_history("All", "All", ""),
        outputs=history_output
    )


# =========================================================
# LAUNCH
# =========================================================

if __name__ == "__main__":
    app.launch()
