import html
import os

import gradio as gr
from transformers import pipeline


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------
APP_TITLE = "ContextAI"
MODEL_NAME = "distilbert/distilbert-base-cased-distilled-squad"
SERVER_PORT = int(os.getenv("GRADIO_SERVER_PORT", "7862"))

EXAMPLE_CONTEXT = (
    "Artificial Intelligence is a branch of computer science. "
    "Machine learning allows computers to learn from data. "
    "Python is a popular programming language for AI development. "
    "AI is used in healthcare, education, transportation, and business."
)

print("Loading Question Answering AI model...")
qa_model = pipeline("question-answering", model=MODEL_NAME)
print("AI model loaded successfully!")


# ------------------------------------------------------------
# Application logic
# ------------------------------------------------------------
def answer_question(context, question, history):
    context = context or ""
    question = question or ""
    history = history or []

    if not context.strip():
        return (
            "Please enter some context text or upload a TXT file.",
            "0%",
            confidence_html(0),
            history_table(history),
            history,
        )

    if not question.strip():
        return (
            "Please enter a question.",
            "0%",
            confidence_html(0),
            history_table(history),
            history,
        )

    try:
        result = qa_model(
            question=question.strip(),
            context=context.strip(),
            max_seq_len=384,
            doc_stride=128,
            max_question_len=64,
            handle_impossible_answer=False,
        )

        answer = (result.get("answer") or "").strip()
        score = float(result.get("score", 0.0))
        score = max(0.0, min(score, 1.0))
        confidence = f"{score:.2%}"

        if score < 0.05 or not answer:
            answer = (
                "I couldn't find a confident answer in the provided text. "
                "Try rephrasing your question or adding more context."
            )

        history.append([question.strip(), answer, confidence])
        history = history[-10:]  # Keep the latest 10 entries.

        return answer, confidence, confidence_html(score), history_table(history), history

    except Exception as error:
        message = f"System error: {error}"
        return message, "0%", confidence_html(0), history_table(history), history


def confidence_html(score):
    """Return a styled confidence bar for the estimated model score."""
    score = max(0.0, min(float(score), 1.0))
    percent = score * 100

    if percent >= 70:
        color = "#5CA3C5"
        label = "High"
    elif percent >= 35:
        color = "#8ABAD3"
        label = "Moderate"
    else:
        color = "#800020"
        label = "Low"

    return f"""
    <div class="confidence-wrap">
        <div class="confidence-top">
            <span class="confidence-caption">Model confidence estimate</span>
            <span class="confidence-value" style="color:{color}">{percent:.1f}% · {label}</span>
        </div>
        <div class="confidence-track">
            <div class="confidence-fill"
                 style="width:{percent:.1f}%; background:{color};"></div>
        </div>
        <p class="confidence-note">
            Confidence is an estimate from the model, not a guarantee of correctness.
        </p>
    </div>
    """


def history_table(history):
    if not history:
        return [["No questions asked yet.", "", ""]]
    return history


def load_txt_file(file_path):
    if not file_path:
        return gr.update()

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        if not content.strip():
            return "The uploaded TXT file is empty."

        return content
    except UnicodeDecodeError:
        return "Could not read this file as UTF-8 text. Please upload a UTF-8 TXT file."
    except Exception as error:
        return f"Could not load file: {error}"


def clear_all():
    return (
        "",
        "",
        "",
        "0%",
        confidence_html(0),
        [["No questions asked yet.", "", ""]],
        [],
        None,
    )


# ------------------------------------------------------------
# Custom CSS
# ------------------------------------------------------------
custom_css = """
:root {
    --bg: #102431;
    --panel: #f8fcff;
    --panel-soft: #eaf5fb;
    --border: #c6deeb;
    --text: #173244;
    --muted: #5d7d91;
    --blue: #8ABAD3;
    --purple: #800020;
}

body {
    background: radial-gradient(ellipse at top, #d8edf7 0%, #f7fbfe 62%) !important;
    font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
    color: var(--text) !important;
}

.gradio-container {
    max-width: 1420px !important;
    width: 100% !important;
    margin: 0 auto !important;
    padding: 28px clamp(14px, 3vw, 42px) 30px !important;
    background: transparent !important;
}

.gradio-container, .gradio-container .main, .gradio-container .wrap {
    background: transparent !important;
}

#hero {
    text-align: center;
    padding: 10px 0 28px;
}

#hero h1 {
    font-size: clamp(34px, 4vw, 48px) !important;
    font-weight: 850 !important;
    letter-spacing: -1.4px;
    margin: 0 0 8px !important;
    background: linear-gradient(90deg, #8ABAD3, #5CA3C5, #800020);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

#hero .subtitle {
    color: #173244;
    font-size: 17px;
    font-weight: 650;
    margin-bottom: 8px;
}

#hero .description {
    color: var(--muted);
    font-size: 15px;
}

.panel {
    background: rgba(255, 255, 255, 0.96) !important;
    border: 1px solid var(--border) !important;
    border-radius: 20px !important;
    padding: 22px !important;
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.18) !important;
}

.panel h2, .section-heading {
    color: #173244 !important;
    font-size: 23px !important;
    font-weight: 750 !important;
    margin: 0 0 8px !important;
}

.panel-description {
    color: var(--muted);
    font-size: 14px;
    margin-bottom: 18px;
}

label span, .label {
    color: #31566b !important;
    font-weight: 650 !important;
}

textarea, input, .input-container {
    background: #ffffff !important;
    border: 1px solid #bfd9e7 !important;
    color: #173244 !important;
    border-radius: 10px !important;
}

textarea:focus, input:focus {
    border-color: #8ABAD3 !important;
    box-shadow: 0 0 0 2px rgba(138, 186, 211, 0.24) !important;
}

textarea::placeholder, input::placeholder {
    color: #8aa5b5 !important;
}

#context-box textarea {
    min-height: 245px !important;
    line-height: 1.65 !important;
}

#answer-box textarea {
    min-height: 245px !important;
    font-size: 18px !important;
    font-weight: 600 !important;
    line-height: 1.7 !important;
    color: #800020 !important;
}

button.primary {
    background: linear-gradient(100deg, #8ABAD3, #5CA3C5) !important;
    border: 0 !important;
    color: white !important;
    font-weight: 750 !important;
    border-radius: 10px !important;
    min-height: 48px !important;
    transition: transform .18s ease, box-shadow .18s ease !important;
}

button.primary:hover {
    transform: translateY(-1px);
    box-shadow: 0 7px 20px rgba(92, 163, 197, .30) !important;
}

button.secondary {
    background: #800020 !important;
    border: 1px solid #6f1731 !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    border-radius: 10px !important;
    min-height: 48px !important;
}

#button-row {
    align-items: stretch !important;
    flex-wrap: nowrap !important;
    margin-top: 12px !important;
}

#upload-area {
    background: rgba(234, 245, 251, .85) !important;
    border: 1px dashed #8ABAD3 !important;
    border-radius: 12px !important;
}

#confidence-panel {
    background: #eaf5fb !important;
    border: 1px solid #bfd9e7 !important;
    border-radius: 12px !important;
    padding: 12px 14px !important;
}

.confidence-wrap { padding: 2px 0 0; }
.confidence-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    margin-bottom: 10px;
}
.confidence-caption { color: #5d7d91; font-size: 13px; font-weight: 600; }
.confidence-value { font-size: 15px; font-weight: 800; white-space: nowrap; }
.confidence-track {
    height: 10px;
    background: #ffffff;
    border: 1px solid #bfd9e7;
    border-radius: 999px;
    overflow: hidden;
}
.confidence-fill {
    height: 100%;
    border-radius: 999px;
    transition: width .25s ease;
}
.confidence-note {
    color: #6e8a9d;
    font-size: 12px;
    margin: 10px 0 0;
}

#examples-section {
    margin-top: 28px !important;
}
#history-panel {
    margin-top: 28px !important;
}
#history-table {
    border: 1px solid #bfd9e7 !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}
#history-table table {
    background: #ffffff !important;
}
#history-table th {
    background: #dceef7 !important;
    color: #173244 !important;
}
#history-table td {
    color: #31566b !important;
}

#about-box {
    border: 1px solid #2e405a !important;
    border-radius: 14px !important;
    background: rgba(255, 255, 255, .88) !important;
    margin-top: 22px !important;
}

#footer {
    text-align: center;
    color: #5d7d91;
    font-size: 13px;
    padding: 24px 0 6px;
}
#footer .brand {
    color: #800020;
    font-weight: 750;
}

@media (max-width: 850px) {
    .gradio-container {
        padding: 18px 12px 24px !important;
    }
    .panel {
        padding: 16px !important;
        border-radius: 16px !important;
    }
    #context-box textarea, #answer-box textarea {
        min-height: 190px !important;
    }
    #button-row {
        flex-wrap: wrap !important;
    }
}
"""


# ------------------------------------------------------------
# Gradio interface
# ------------------------------------------------------------
with gr.Blocks(theme=gr.themes.Soft(), css=custom_css, title="ContextAI | Question Answering") as app:
    history_state = gr.State([])

    gr.HTML(
        """
        <div id="hero">
            <h1>🤖 ContextAI</h1>
            <div class="subtitle">Intelligent Question Answering System</div>
            <div class="description">
                Ask questions and discover answers directly from your text.
            </div>
        </div>
        """
    )

    with gr.Row(equal_height=False):
        # Context / input panel
        with gr.Column(scale=1, elem_classes=["panel"]):
            gr.Markdown("## 📄 Context Input")
            gr.Markdown(
                '<div class="panel-description">Paste a paragraph or upload a TXT document.</div>'
            )

            context_input = gr.Textbox(
                label="Your Context",
                placeholder=(
                    "Paste your paragraph here...\n\n"
                    "Example: Artificial Intelligence is a branch of computer science."
                ),
                lines=10,
                elem_id="context-box",
                show_copy_button=True,
            )

            file_input = gr.File(
                label="📁 Upload TXT File",
                file_types=[".txt"],
                type="filepath",
                elem_id="upload-area",
            )
            gr.Markdown(
                '<div class="panel-description">TXT files only · UTF-8 recommended</div>'
            )

            question_input = gr.Textbox(
                label="❓ Your Question",
                placeholder="Ask a question about your text...",
                lines=2,
            )

            with gr.Row(elem_id="button-row"):
                submit_button = gr.Button(
                    "🔍 Find Answer", variant="primary", scale=3
                )
                clear_button = gr.Button(
                    "🧹 Clear All", variant="secondary", scale=1
                )

        # Answer / output panel
        with gr.Column(scale=1, elem_classes=["panel"]):
            gr.Markdown("## 💡 AI Response")
            gr.Markdown(
                '<div class="panel-description">Your answer and estimated model confidence.</div>'
            )

            answer_output = gr.Textbox(
                label="AI Answer",
                placeholder="Your answer will appear here after you click Find Answer.",
                lines=10,
                interactive=False,
                elem_id="answer-box",
                show_copy_button=True,
            )

            confidence_output = gr.Textbox(
                label="📊 Estimated Confidence",
                value="0%",
                interactive=False,
            )

            confidence_indicator = gr.HTML(
                value=confidence_html(0),
                elem_id="confidence-panel",
            )

    gr.Markdown("## 💡 Try an Example", elem_id="examples-section")
    gr.Markdown(
        '<div class="panel-description">Select an example to automatically fill the context and question.</div>'
    )

    gr.Examples(
        examples=[
            [EXAMPLE_CONTEXT, "What is machine learning?"],
            [EXAMPLE_CONTEXT, "Which programming language is popular for AI development?"],
            [EXAMPLE_CONTEXT, "Where is AI used?"],
            [EXAMPLE_CONTEXT, "What is Artificial Intelligence?"],
        ],
        inputs=[context_input, question_input],
        label="Example Questions",
    )

    with gr.Column(elem_classes=["panel"], elem_id="history-panel"):
        gr.Markdown("## 📚 Question History")
        gr.Markdown(
            '<div class="panel-description">Your latest 10 questions and answers during this session.</div>'
        )

        history_output = gr.Dataframe(
            headers=["Question", "AI Answer", "Confidence"],
            value=[["No questions asked yet.", "", ""]],
            datatype=["str", "str", "str"],
            interactive=False,
            wrap=True,
            row_count=(1, "dynamic"),
            col_count=(3, "fixed"),
            elem_id="history-table",
        )

    with gr.Accordion("ℹ️ About ContextAI | How It Works", open=False, elem_id="about-box"):
        gr.Markdown(
            """
            **ContextAI** uses a DistilBERT transformer model fine-tuned for
            extractive question answering.

            1. Enter or upload text that contains the information.
            2. Ask a question about that text.
            3. The model selects a likely answer span from the context.
            4. The confidence score is the model's estimated likelihood—not a
               guarantee that the answer is correct.

            **Technology:** Python · Hugging Face Transformers · Gradio
            """
        )

    gr.HTML(
        """
        <div id="footer">
            <span class="brand">🤖 ContextAI</span>
            <span> · Powered by DistilBERT Transformer</span>
            <div>Built with Python, Hugging Face and Gradio</div>
        </div>
        """
    )

    submit_button.click(
        fn=answer_question,
        inputs=[context_input, question_input, history_state],
        outputs=[
            answer_output,
            confidence_output,
            confidence_indicator,
            history_output,
            history_state,
        ],
    )

    question_input.submit(
        fn=answer_question,
        inputs=[context_input, question_input, history_state],
        outputs=[
            answer_output,
            confidence_output,
            confidence_indicator,
            history_output,
            history_state,
        ],
    )

    file_input.change(
        fn=load_txt_file,
        inputs=[file_input],
        outputs=[context_input],
    )

    clear_button.click(
        fn=clear_all,
        inputs=[],
        outputs=[
            context_input,
            question_input,
            answer_output,
            confidence_output,
            confidence_indicator,
            history_output,
            history_state,
            file_input,
        ],
    )


if __name__ == "__main__":
    app.launch(
    server_name="127.0.0.1",
    server_port=7863,
    share=False,
    show_error=True,
)