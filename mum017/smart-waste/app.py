"""Smart Waste AI"""

import gradio as gr
import torch
from PIL import Image
from starlette.responses import FileResponse as _FileResponseBase
import starlette.responses as _sr_mod

class _NoContentLengthFileResponse(_FileResponseBase):
    def set_stat_headers(self, stat_result):
        last_modified = _sr_mod.formatdate(stat_result.st_mtime, usegmt=True)
        etag_base = str(stat_result.st_mtime) + "-" + str(stat_result.st_size)
        import hashlib
        etag = '"' + hashlib.md5(etag_base.encode(), usedforsecurity=False).hexdigest() + '"'
        self.headers.setdefault("last-modified", last_modified)
        self.headers.setdefault("etag", etag)

_sr_mod.FileResponse = _NoContentLengthFileResponse

import gradio.route_utils as _ru_mod
if hasattr(_ru_mod, 'FileResponse'):
    _ru_mod.FileResponse = _NoContentLengthFileResponse

import gradio.routes as _rt_mod
if hasattr(_rt_mod, 'FileResponse'):
    _rt_mod.FileResponse = _NoContentLengthFileResponse

import gradio.static_server as _ss_mod
if hasattr(_ss_mod, 'FileResponse'):
    _ss_mod.FileResponse = _NoContentLengthFileResponse



# IMPORTANT:
# Do not monkey-patch Starlette/Gradio FileResponse here.
# Gradio uses FileResponse to serve uploaded image previews and cached files.
# Altering its headers can cause broken image previews and HTTP protocol errors.

from src.classifier import WasteClassifier
from src.config import MODEL_ID, TOP_K
from src.recommender import (
    build_recommendation,
    load_knowledge_base,
    to_markdown,
)
from src.validation import InvalidImageError, validate_image

# ==========================================
# MODEL INITIALIZATION & PRELOADING
# ==========================================
print("Loading Smart Waste AI model into memory...")

# Loading the model here ensures it is preloaded before the UI starts
classifier = WasteClassifier()
knowledge_base = load_knowledge_base()

print("Smart Waste AI is ready and preloaded!")


EMPTY_STATE = """
<div class="empty-result">
    <div class="empty-leaf">🌱</div>
    <h3>Your results will appear here</h3>
    <p>
        Upload a waste image to discover its category
        and recycling possibilities.
    </p>
</div>
"""

# IMAGE ANALYSIS FUNCTION
def analyze(image):

    if image is None:
        return {}, "Please upload a waste image first."

    try:
        clean_image = validate_image(image)

        predictions = classifier.predict(
            clean_image,
            top_k=TOP_K
        )

        recommendation = build_recommendation(
            predictions,
            knowledge_base
        )

        confidence = {
            label: float(prob)
            for label, prob in predictions
        }

        return confidence, to_markdown(recommendation)

    except InvalidImageError as err:
        return {}, f"⚠️ **Invalid image:** {err}"

    except Exception as err:
        print(f"Analysis error: {err}")
        return {}, (
            "⚠️ **Analysis failed.** "
            "Please check your model and connection.\n\n"
            f"Details: `{err}`"
        )


# ==========================================
# CLEAR FUNCTION
# ==========================================
def clear_all():
    return None, {}, EMPTY_STATE


# ==========================================
# ABOUT SECTION
# ==========================================
ABOUT_MD = f"""
# About Smart Waste AI

Smart Waste AI is an intelligent waste classification and recycling
assistant designed to encourage responsible waste management.

### Technology

| Component | Description |
|---|---|
| AI Model | `{MODEL_ID}` |
| Architecture | Vision Transformer (ViT) |
| Categories | 12 waste classes |
| Prediction | Top-{TOP_K} results |
| Recommendation | Rule-based recycling guidance |

### How it works

1. Upload an image of a waste item.
2. The image is validated and converted to RGB.
3. The Vision Transformer analyzes the image.
4. The system predicts the most likely waste categories.
5. The recommendation engine generates recycling guidance.

### Limitations

- Cluttered images may reduce classification accuracy.
- Only the trained waste categories are supported.
- Recycling guidelines may differ by location.
"""

# ==========================================
# CSS (DARK MODE & LAYOUT FIXES)
# ==========================================
CSS = """
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Playfair+Display:wght@500;600;700&display=swap');

:root {
    color-scheme: dark;
    --page: #101914;
    --surface: #1b2921;
    --surface-soft: #26382d;
    --ink: #f0f5ed;
    --muted: #b2c2b4;
    --green: #a9d0a8;
    --green-dark: #c0dfb9;
    --border: #3a4d3e;
    --shadow: 0 12px 35px rgba(0,0,0,.20);
}

html, body, #root, gradio-app, .gradio-container {
    background: var(--page) !important;
    background-color: var(--page) !important;
    color: var(--ink) !important;
    font-family: 'DM Sans', sans-serif !important;
}

.gradio-container {
    max-width: 1240px !important;
    padding: 24px !important;
    margin: auto !important;
    min-height: 100vh;
    
    --body-background-fill: #101914 !important;
    --background-fill-primary: #101914 !important;
    --background-fill-secondary: #1b2921 !important;
    --block-background-fill: #1b2921 !important;
    --input-background-fill: #26382d !important;
    
    --body-text-color: #f1f5ed !important;
    --block-label-text-color: #eaf2e8 !important;
    --block-title-text-color: #ffffff !important;
    --input-text-color: #f1f5ed !important;
}

footer { display: none !important; }

.gradio-container h1, .gradio-container h2, .gradio-container h3, .gradio-container h4,
.gradio-container p, .gradio-container label, .gradio-container span, .gradio-container strong,
.gradio-container li, .gradio-container .prose, .gradio-container .markdown,
.gradio-container td, .gradio-container th, .gradio-container .wrap, .gradio-container .label-wrap {
    color: var(--ink) !important;
}

.gradio-container small, .gradio-container .panel-description,
.gradio-container .empty-result p, .gradio-container .info-card span {
    color: var(--muted) !important;
}

.gradio-container hr { border-color: var(--border) !important; }
.gradio-container a { color: var(--green) !important; }

/* Topbar */
#topbar {
    display: flex; align-items: center;
    padding: 12px 4px 24px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 30px;
}
.brand {
    display: flex; align-items: center; gap: 11px;
    color: var(--ink); font-weight: 800; font-size: 18px; letter-spacing: -.5px;
}
.brand-symbol {
    width: 39px; height: 39px;
    background: #286044; color: #ffffff !important;
    border-radius: 13px; display: grid; place-items: center; font-size: 22px;
}
.brand-small {
    color: var(--muted) !important; font-size: 10px; letter-spacing: 2px;
    display: block; font-weight: 700;
}

/* Hero Section */
#hero {
    background: linear-gradient(125deg, #173d2b 0%, #24583e 65%, #356b48 100%);
    color: #ffffff !important;
    border-radius: 25px; padding: 65px 55px;
    position: relative; overflow: hidden; min-height: 340px;
    display: flex; align-items: center;
    box-shadow: 0 18px 45px rgba(24,62,42,.15);
}
.hero-content { max-width: 650px; position: relative; z-index: 2; }
.hero-eyebrow {
    color: #c8dfc4 !important; font-size: 11px; font-weight: 700;
    letter-spacing: 3px; margin-bottom: 20px;
}
#hero h1 {
    color: #ffffff !important; font-family: 'Playfair Display', serif !important;
    font-size: clamp(40px, 6vw, 65px) !important; line-height: 1.08 !important;
    letter-spacing: -1.8px; margin: 0 0 19px !important;
}
#hero p { color: #e0eadf !important; font-size: 15px; line-height: 1.9; max-width: 520px; }
.hero-decoration {
    position: absolute; right: 5%; top: 50%; transform: translateY(-50%);
    font-size: 170px; opacity: .16; pointer-events: none;
}
.hero-note {
    display: inline-block; margin-top: 14px; padding: 9px 15px;
    border: 1px solid rgba(255,255,255,.3); border-radius: 30px;
    color: #e2efdc !important; font-size: 11px; letter-spacing: 1px;
}

/* Intro & Workspace */
.intro { padding: 43px 4px 22px; }
.eyebrow { color: var(--green) !important; font-size: 11px !important; font-weight: 800 !important; letter-spacing: 2.5px !important; }
.intro h2, .workspace-heading h2 {
    font-family: 'Playfair Display', serif !important; font-size: 34px !important;
    margin: 8px 0 !important; color: var(--ink) !important;
}
.intro p { color: var(--muted) !important; font-size: 14px; line-height: 1.8; }
.workspace-heading { padding: 38px 4px 18px; }
.workspace-heading h2 { font-size: 32px !important; }
.workspace-heading p { color: var(--muted) !important; font-size: 13px; line-height: 1.8; }

/* Feature Cards */
.info-card {
    background: var(--surface) !important; border: 1px solid var(--border) !important;
    border-radius: 17px !important; padding: 22px !important; min-height: 135px;
    box-shadow: var(--shadow); transition: .25s ease;
}
.info-card:hover { transform: translateY(-4px); border-color: var(--green) !important; }
.info-icon { font-size: 25px; margin-bottom: 12px; }
.info-card strong { color: var(--ink) !important; display: block; font-size: 14px; margin-bottom: 7px; }
.info-card span { color: var(--muted) !important; font-size: 12px; line-height: 1.7; }

/* Panels */
.panel {
    background: var(--surface) !important; border: 1px solid var(--border) !important;
    border-radius: 20px !important; padding: 22px !important;
    box-shadow: var(--shadow); overflow: hidden !important; 
}
.panel h3 { font-family: 'Playfair Display', serif !important; font-size: 21px !important; color: var(--ink) !important; }
.panel-description { color: var(--muted) !important; font-size: 12px !important; line-height: 1.7; }

/* Inputs & Buttons */
.gradio-container input, .gradio-container textarea, .gradio-container select {
    background: var(--surface-soft) !important; color: #ffffff !important; border-color: #506653 !important;
}
.gradio-container input::placeholder, .gradio-container textarea::placeholder {
    color: var(--muted) !important; opacity: 1 !important;
}
.gradio-container button { border-radius: 12px !important; transition: .2s ease !important; }
#classify-button button {
    background: #286044 !important; color: #ffffff !important; border: none !important;
    font-weight: 700 !important; min-height: 48px !important;
}
#classify-button button:hover { background: #1c4933 !important; transform: translateY(-2px); }
#clear-button button {
    background: var(--surface-soft) !important; color: #ffffff !important;
    border: 1px solid var(--border) !important; min-height: 48px !important;
}
#clear-button button:hover { border-color: var(--green) !important; }

/* Image Upload Fix */
.gradio-container .image-container {
    background: var(--surface-soft) !important; border: 1px solid var(--border) !important;
    border-radius: 14px !important; overflow: hidden !important;
}
.gradio-container .image-container > div { background: transparent !important; }
.gradio-container .image-container button {
    background: var(--surface) !important; color: var(--ink) !important; border: 1px solid var(--border) !important;
}

/* Tabs */
.gradio-container button[role="tab"] {
    color: #dce8da !important; background: transparent !important;
    border-radius: 10px !important; font-weight: 700 !important;
}
.gradio-container button[role="tab"][aria-selected="true"] {
    color: #b9dfa9 !important; border-color: var(--green) !important; background: var(--surface) !important;
}

/* Recommendation & Empty State */
#recommendation-panel { margin-top: 18px; }
#recommendation-panel .prose, #recommendation-panel .markdown { color: var(--ink) !important; line-height: 1.8 !important; }
#recommendation-panel h1, #recommendation-panel h2, #recommendation-panel h3, #recommendation-panel h4 { color: #b9dfa9 !important; }
#recommendation-panel li, #recommendation-panel p, #recommendation-panel strong { color: var(--ink) !important; }
#recommendation-panel code { background: var(--surface-soft) !important; color: var(--green) !important; padding: 3px 6px; border-radius: 5px; }

.empty-result { text-align: center; padding: 55px 15px; }
.empty-leaf { font-size: 52px; margin-bottom: 12px; }
.empty-result h3 { font-family: 'Playfair Display', serif !important; font-size: 21px !important; color: var(--ink) !important; }
.empty-result p { color: var(--muted) !important; font-size: 12px; line-height: 1.8; }

/* Tables & Footer */
.gradio-container table { width: 100%; border-collapse: collapse !important; border-color: var(--border) !important; }
.gradio-container th { background: #293d30 !important; color: #d5edc9 !important; font-weight: 700 !important; padding: 12px !important; }
.gradio-container td { background: var(--surface) !important; color: var(--ink) !important; padding: 12px !important; }
#footer {
    margin-top: 45px; border-top: 1px solid var(--border);
    padding: 25px 5px; text-align: center;
    color: var(--muted) !important; font-size: 11px; letter-spacing: .5px; line-height: 1.7;
}

@media (max-width: 700px) {
    .gradio-container { padding: 12px !important; }
    #hero { padding: 38px 24px; min-height: 300px; }
    #hero h1 { font-size: 40px !important; }
    .hero-decoration { font-size: 100px; right: 0; }
    .panel, .info-card { padding: 15px !important; }
    .intro h2, .workspace-heading h2 { font-size: 28px !important; }
}
"""

# ==========================================
# GRADIO THEME
# ==========================================
THEME = gr.themes.Soft(
    primary_hue="green",
    secondary_hue="lime",
    neutral_hue="stone",
)

# ==========================================
# WEBSITE INTERFACE
# ==========================================
with gr.Blocks(
    title="Smart Waste AI | Sustainable Living",
    delete_cache=None # Prevents Gradio from deleting cached images
) as demo:

    # Top Navigation
    with gr.Row():
        with gr.Column(scale=5):
            gr.HTML("""
            <div id="topbar">
                <div class="brand">
                    <div class="brand-symbol">♻</div>
                    <div>
                        SMART WASTE
                        <span class="brand-small">AI FOR A GREENER WORLD</span>
                    </div>
                </div>
            </div>
            """)

    # Hero Section
    gr.HTML("""
    <section id="hero">
        <div class="hero-content">
            <div class="hero-eyebrow">INTELLIGENCE MEETS SUSTAINABILITY</div>
            <h1>A better future<br>starts with waste.</h1>
            <p>Discover a smarter way to manage waste. Identify materials with AI and find meaningful ways to recycle, reuse and protect our planet.</p>
            <div class="hero-note">♻ AI-POWERED WASTE CLASSIFICATION</div>
        </div>
        <div class="hero-decoration">🌿</div>
    </section>
    """)

    # Introduction
    gr.HTML("""
    <section class="intro">
        <div class="eyebrow">A SMALL STEP. A BIG IMPACT.</div>
        <h2>Make every item count.</h2>
        <p>Smart technology to help you make more responsible waste decisions.</p>
    </section>
    """)

    # Feature Cards
    with gr.Row():
        with gr.Column(elem_classes=["info-card"]):
            gr.HTML("""
            <div class="info-icon">📷</div>
            <strong>Upload an image</strong>
            <span>Share a photo of a household waste item.</span>
            """)
        with gr.Column(elem_classes=["info-card"]):
            gr.HTML("""
            <div class="info-icon">🧠</div>
            <strong>AI identification</strong>
            <span>Let computer vision identify its category.</span>
            """)
        with gr.Column(elem_classes=["info-card"]):
            gr.HTML("""
            <div class="info-icon">🌱</div>
            <strong>Recycle smarter</strong>
            <span>Get practical guidance for responsible disposal.</span>
            """)

    # Workspace Heading
    gr.HTML("""
    <section class="workspace-heading">
        <div class="eyebrow">YOUR RECYCLING WORKSPACE</div>
        <h2>Discover what's in your waste.</h2>
        <p>Upload a clear image and let our AI do the analysis.</p>
    </section>
    """)

    # Application Tabs
    with gr.Tabs():
        with gr.Tab("♻ Waste Classifier"):
            with gr.Row():
                # Upload Panel
                with gr.Column(scale=1, elem_classes=["panel"]):
                    gr.Markdown("### Upload your image")
                    gr.Markdown("Choose a clear photo of a single waste item.", elem_classes=["panel-description"])
                    
                    image_input = gr.Image(
                        type="pil",
                        label="Waste photograph",
                        height=280,
                    )
                    
                    with gr.Row():
                        classify_button = gr.Button("✦ Analyse my waste", variant="primary", elem_id="classify-button", scale=3)
                        clear_button = gr.Button("Clear", elem_id="clear-button", scale=1)

                # Classification Results Panel
                with gr.Column(scale=1, elem_classes=["panel"]):
                    gr.Markdown("### Classification results")
                    gr.Markdown("Your AI predictions will appear below.", elem_classes=["panel-description"])
                    label_output = gr.Label(num_top_classes=TOP_K, label="Top predictions")

            # Recommendation Panel
            with gr.Column(elem_classes=["panel"], elem_id="recommendation-panel"):
                gr.Markdown("### 🌿 Your recycling guide")
                advice_output = gr.Markdown(EMPTY_STATE)

            # Button Events
            classify_button.click(fn=analyze, inputs=image_input, outputs=[label_output, advice_output])
            clear_button.click(fn=clear_all, inputs=None, outputs=[image_input, label_output, advice_output])

        with gr.Tab("📖 About Smart Waste AI"):
            with gr.Column(elem_classes=["panel"]):
                gr.Markdown(ABOUT_MD)

    # Footer
    gr.HTML("""
    <div id="footer">
        SMART WASTE AI &nbsp;·&nbsp; THINK GREEN. LIVE CLEAN.
        <br><br>
        Designed for a more sustainable tomorrow.
    </div>
    """)

    # Force Dark Mode
    demo.load(fn=None, js="() => { document.documentElement.classList.add('dark'); }")


# ==========================================
# LAUNCH APPLICATION
# ==========================================
if __name__ == "__main__":
    # Queue requests without modifying Gradio/Starlette file responses.
    demo.queue()
    
    demo.launch(
        theme=THEME,
        css=CSS,
        show_error=True,
        share=False,
        debug=True
    ) 