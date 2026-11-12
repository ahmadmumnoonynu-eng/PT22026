import gradio as gr
from transformers import pipeline

# ==========================================================
# 1. CONFIGURATION
# ==========================================================

APP_TITLE = "ContextAI"
MODEL_NAME = "distilbert/distilbert-base-cased-distilled-squad"

CONFIDENCE_THRESHOLD = 0.05
MAX_SEQ_LENGTH = 512
DOC_STRIDE = 128


# ==========================================================
# 2. LOAD AI MODEL
# ==========================================================

print("Loading Question Answering AI model...")

qa_model = pipeline(
    "question-answering",
    model=MODEL_NAME
)

print("AI model loaded successfully!")


# ==========================================================
# 3. EXAMPLE CONTEXT
# ==========================================================

example_context = """
Artificial Intelligence is a branch of computer science.
Machine learning allows computers to learn from data.
Python is a popular programming language for AI development.
AI is used in healthcare, education, transportation, and business.
"""


# ==========================================================
# 4. QUESTION ANSWERING FUNCTION
# ==========================================================

def answer_question(context, question, history):

    # Initialize session history if needed
    if history is None:
        history = []

    # Validate context
    if not context or not context.strip():
        return (
            "⚠️ Please enter some context text.",
            "0%",
            0,
            history,
            history
        )

    # Validate question
    if not question or not question.strip():
        return (
            "⚠️ Please enter a question.",
            "0%",
            0,
            history,
            history
        )

    try:

        # Get answer from the model
        result = qa_model(
            question=question.strip(),
            context=context.strip(),
            max_seq_len=MAX_SEQ_LENGTH,
            doc_stride=DOC_STRIDE
        )

        answer = result["answer"]
        confidence = float(result["score"])

        confidence_percentage = confidence * 100

        confidence_text = f"{confidence_percentage:.2f}%"

        # Check confidence threshold
        if confidence < CONFIDENCE_THRESHOLD:

            answer = (
                "🤔 The AI couldn't find a confident answer "
                "in the provided text."
            )

        # Add the question and answer to session history
        history = history.copy()

        history.append([
            question.strip(),
            answer,
            confidence_text
        ])

        return (
            answer,
            confidence_text,
            confidence_percentage,
            history,
            history
        )

    except Exception as e:

        error_message = f"⚠️ System Error: {str(e)}"

        return (
            error_message,
            "0%",
            0,
            history,
            history
        )


# ==========================================================
# 5. LOAD TXT FILE
# ==========================================================

def load_text_file(file_path):

    if file_path is None:
        return ""

    try:

        with open(file_path, "r", encoding="utf-8") as file:
            text_content = file.read()

        if not text_content.strip():
            return "⚠️ The uploaded file is empty."

        return text_content

    except UnicodeDecodeError:

        return "⚠️ Unable to read the file. Please upload a UTF-8 TXT file."

    except Exception as e:

        return f"⚠️ File Error: {str(e)}"


# ==========================================================
# 6. CUSTOM CSS
# ==========================================================

custom_css = """

/* =========================================
   GLOBAL DESIGN
========================================= */

body {
    background:
        radial-gradient(
            circle at top left,
            #1e293b 0%,
            #0f172a 45%,
            #020617 100%
        ) !important;

    font-family: 'Inter', system-ui, sans-serif !important;
}

.gradio-container {
    max-width: 1400px !important;
    width: 96% !important;
    margin: auto !important;
    padding: 25px !important;

    background: transparent !important;
}

.gradio-container > .main,
.gradio-container > .wrap {
    background: transparent !important;
}


/* =========================================
   HEADER
========================================= */

#main-header {
    text-align: center;
    margin-bottom: 25px;
}

#main-header h1 {
    background: linear-gradient(
        90deg,
        #60a5fa,
        #a78bfa,
        #c084fc
    );

    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;

    font-size: 38px !important;
    font-weight: 800 !important;
    margin-bottom: 8px !important;
}

#main-header p {
    color: #94a3b8 !important;
    font-size: 16px !important;
}


/* =========================================
   INPUT AND OUTPUT PANELS
========================================= */

.input-panel,
.output-panel,
.history-panel {

    background: rgba(30, 41, 59, 0.70) !important;

    border: 1px solid #334155 !important;

    border-radius: 18px !important;

    padding: 20px !important;

    box-shadow:
        0 8px 32px rgba(0, 0, 0, 0.25) !important;

}


/* =========================================
   TEXTBOXES
========================================= */

textarea,
input {

    background: #0f172a !important;

    border: 1px solid #334155 !important;

    color: #e2e8f0 !important;

    border-radius: 10px !important;

    font-size: 15px !important;

}

textarea:focus,
input:focus {

    border-color: #60a5fa !important;

    box-shadow:
        0 0 0 2px rgba(96, 165, 250, 0.20) !important;

}


/* =========================================
   ANSWER BOX
========================================= */

#answer-box textarea {

    font-size: 18px !important;

    font-weight: 600 !important;

    color: #c4b5fd !important;

    line-height: 1.7 !important;

}


/* =========================================
   LABELS
========================================= */

label span {

    color: #cbd5e1 !important;

    font-weight: 600 !important;

}


/* =========================================
   PRIMARY BUTTON
========================================= */

button.primary {

    background: linear-gradient(
        90deg,
        #3b82f6,
        #6366f1,
        #8b5cf6
    ) !important;

    border: none !important;

    color: white !important;

    font-weight: 700 !important;

    border-radius: 10px !important;

    transition: all 0.25s ease !important;

}

button.primary:hover {

    transform: translateY(-2px);

    box-shadow:
        0 5px 15px rgba(99, 102, 241, 0.35) !important;

}


/* =========================================
   SECONDARY BUTTON
========================================= */

button.secondary {

    background: #334155 !important;

    color: #e2e8f0 !important;

    border: 1px solid #475569 !important;

    border-radius: 10px !important;

    transition: all 0.25s ease !important;

}

button.secondary:hover {

    background: #475569 !important;

}


/* =========================================
   BUTTON ROW
========================================= */

#button-row {

    flex-wrap: wrap !important;

    gap: 10px !important;

}


/* =========================================
   CONFIDENCE SLIDER
========================================= */

#confidence-slider {

    margin-top: 10px !important;

}


/* =========================================
   HISTORY TABLE
========================================= */

.history-panel {

    margin-top: 20px !important;

}

table {

    border-radius: 10px !important;

}


/* =========================================
   ABOUT SECTION
========================================= */

#about-section {

    background: rgba(15, 23, 42, 0.55) !important;

    border: 1px solid #334155 !important;

    border-radius: 14px !important;

    margin-top: 20px !important;

}


/* =========================================
   FOOTER
========================================= */

#footer {

    text-align: center;

    color: #64748b !important;

    font-size: 13px !important;

    margin-top: 25px !important;

}


/* =========================================
   RESPONSIVE DESIGN
========================================= */

@media (max-width: 768px) {

    .gradio-container {

        width: 100% !important;

        padding: 12px !important;

    }

    #main-header h1 {

        font-size: 28px !important;

    }

    #main-header p {

        font-size: 14px !important;

    }

    .input-panel,
    .output-panel,
    .history-panel {

        padding: 12px !important;

    }

    #answer-box textarea {

        font-size: 16px !important;

    }

}

"""


# ==========================================================
# 7. CREATE GRADIO INTERFACE
# ==========================================================

with gr.Blocks(
    theme=gr.themes.Soft(
        primary_hue="indigo",
        secondary_hue="blue",
        neutral_hue="slate"
    ),
    css=custom_css,
    title=APP_TITLE
) as app:


    # =========================================
    # HEADER
    # =========================================

    gr.Markdown(
        """
        # 🤖 ContextAI

        **Intelligent Question Answering System**

        Ask questions and discover answers directly from your text.
        """,
        elem_id="main-header"
    )


    # =========================================
    # SESSION HISTORY
    # =========================================

    history_state = gr.State([])


    # =========================================
    # MAIN INTERFACE
    # =========================================

    with gr.Row(equal_height=False):


        # =====================================
        # LEFT COLUMN - INPUT
        # =====================================

        with gr.Column(
            scale=1,
            elem_classes=["input-panel"]
        ):

            gr.Markdown("## 📄 Context Input")

            gr.Markdown(
                "Enter a paragraph or upload a TXT document."
            )


            # Context textbox
            context_input = gr.Textbox(
                label="Your Context",
                lines=10,
                placeholder=(
                    "Paste your paragraph here...\n\n"
                    "Example: Artificial Intelligence is "
                    "a branch of computer science."
                ),
                show_label=True
            )


            # File upload
            file_input = gr.File(
                label="📁 Upload TXT File",
                file_types=[".txt"],
                type="filepath"
            )


            # Automatically load uploaded file
            file_input.change(
                fn=load_text_file,
                inputs=file_input,
                outputs=context_input
            )


            # Question textbox
            question_input = gr.Textbox(
                label="❓ Your Question",
                placeholder="Ask a question about your text...",
                lines=2
            )


            # Buttons
            with gr.Row(elem_id="button-row"):

                submit_button = gr.Button(
                    "🔍 Find Answer",
                    variant="primary",
                    scale=3
                )

                clear_button = gr.Button(
                    "🧹 Clear All",
                    variant="secondary",
                    scale=1
                )


        # =====================================
        # RIGHT COLUMN - OUTPUT
        # =====================================

        with gr.Column(
            scale=1,
            elem_classes=["output-panel"]
        ):

            gr.Markdown("## 💡 AI Response")

            gr.Markdown(
                "Your answer and estimated model confidence."
            )


            # AI Answer
            answer_output = gr.Textbox(
                label="AI Answer",
                lines=8,
                placeholder=(
                    "Your answer will appear here "
                    "after you click Find Answer."
                ),
                elem_id="answer-box",
                interactive=False,
                show_copy_button=True
            )


            # Confidence text
            confidence_output = gr.Textbox(
                label="📊 Estimated Confidence",
                value="0%",
                interactive=False
            )


            # Visual confidence indicator
            confidence_slider = gr.Slider(
                minimum=0,
                maximum=100,
                value=0,
                step=0.1,
                label="Confidence Indicator",
                interactive=False,
                elem_id="confidence-slider"
            )


            gr.Markdown(
                """
                <div style="
                    color: #94a3b8;
                    font-size: 12px;
                    text-align: center;
                    margin-top: 5px;
                ">
                    Confidence is an estimate from the model,
                    not a guarantee of correctness.
                </div>
                """
            )


    # =========================================
    # EXAMPLE QUESTIONS
    # =========================================

    gr.Markdown("## 💡 Try an Example")

    gr.Markdown(
        "Select an example to automatically fill the context and question."
    )


    gr.Examples(
        examples=[
            [
                example_context,
                "What is machine learning?"
            ],

            [
                example_context,
                "Which programming language is popular for AI development?"
            ],

            [
                example_context,
                "Where is AI used?"
            ],

            [
                example_context,
                "What is Artificial Intelligence?"
            ]
        ],

        inputs=[
            context_input,
            question_input
        ],

        label="Example Questions"
    )


    # =========================================
    # QUESTION HISTORY
    # =========================================

    with gr.Column(
        elem_classes=["history-panel"]
    ):

        gr.Markdown("## 📚 Question History")

        gr.Markdown(
            "Previously asked questions and their answers "
            "during this session."
        )


        history_table = gr.Dataframe(
            headers=[
                "Question",
                "AI Answer",
                "Confidence"
            ],

            datatype=[
                "str",
                "str",
                "str"
            ],

            value=[],

            interactive=False,

            wrap=True,

            label="Previous Questions"
        )


    # =========================================
    # ABOUT / HOW IT WORKS
    # =========================================

    with gr.Accordion(
        "ℹ️ About ContextAI | How It Works",
        open=False,
        elem_id="about-section"
    ):

        gr.Markdown(
            """
            ## About ContextAI

            ContextAI is an intelligent Question Answering System
            that uses Natural Language Processing (NLP) to extract
            answers from user-provided text.

            ### 🧠 AI Model

            The application uses:

            **DistilBERT Base Cased Distilled SQuAD**

            Model:
            `distilbert/distilbert-base-cased-distilled-squad`

            ### ⚙️ How It Works

            **Step 1 — Enter Context**

            Paste a paragraph or upload a TXT document.

            **Step 2 — Ask a Question**

            Enter a question related to the provided context.

            **Step 3 — AI Processing**

            The DistilBERT model analyzes the context and question
            to locate the most relevant answer.

            **Step 4 — Display Results**

            The application displays the extracted answer and
            estimated confidence score.

            ### 🛠 Technologies Used

            - Python
            - Gradio
            - Hugging Face Transformers
            - DistilBERT
            - Natural Language Processing (NLP)

            ### 🎓 Project Purpose

            This project demonstrates how transformer-based
            Question Answering models can be integrated into
            an interactive web application.
            """
        )


    # =========================================
    # FOOTER
    # =========================================

    gr.Markdown(
        """
        <div id="footer">

            🤖 ContextAI

            <br>

            Powered by DistilBERT Transformer

            <br>

            Built with Python, Hugging Face and Gradio

        </div>
        """
    )


    # =========================================
    # FIND ANSWER EVENT
    # =========================================

    submit_button.click(
        fn=answer_question,

        inputs=[
            context_input,
            question_input,
            history_state
        ],

        outputs=[
            answer_output,
            confidence_output,
            confidence_slider,
            history_table,
            history_state
        ]
    )


    # =========================================
    # CLEAR ALL EVENT
    # =========================================

    clear_button.click(
        fn=lambda: (
            None,   # Context
            None,   # Question
            None,   # Uploaded file
            "",     # Answer
            "0%",   # Confidence text
            0,      # Confidence slider
            [],     # History table
            []      # History state
        ),

        inputs=[],

        outputs=[
            context_input,
            question_input,
            file_input,
            answer_output,
            confidence_output,
            confidence_slider,
            history_table,
            history_state
        ]
    )


# ==========================================================
# 8. LAUNCH APPLICATION
# ==========================================================

if __name__ == "__main__":
    app.launch(
        server_name="127.0.0.1",
        server_port=7863,
        share=False,
        show_error=True
    )