"""Gradio app: NER Studio (analyzer + model arena)."""
import os
os.environ["HF_HUB_OFFLINE"] = "1"  # use the cached model (network blocks HF checks)

"""Gradio app: NER Studio (analyzer + model arena)."""
import os
if os.environ.get("NER_OFFLINE") == "1":  # set on networks that block Hugging Face
    os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["NO_PROXY"] = "localhost,127.0.0.1,0.0.0.0"
os.environ["no_proxy"] = "localhost,127.0.0.1,0.0.0.0"
import csv
import tempfile

import gradio as gr

from src.arena import compare, to_segments
from src.inference import predict

MAX_CHARS = 1500
LABELS = ["PER", "ORG", "LOC", "MISC"]
COLORS = {"PER": "#4C9AFF", "ORG": "#FFAB00", "LOC": "#36B37E", "MISC": "#B37FEB"}

ANALYZER_EXAMPLES = [
    ["Elon Musk visited Google headquarters in California last Monday.", 0.5, LABELS],
    ["Angela Merkel met Emmanuel Macron in Paris to discuss the European Union budget.", 0.5, LABELS],
    ["Apple released the iPhone in San Francisco, and Tim Cook thanked Microsoft.", 0.5, LABELS],
    ["Jordan scored 40 points for the Chicago Bulls against the Lakers.", 0.5, LABELS],
]
ARENA_EXAMPLES = [
    ["Elon Musk visited Google headquarters in California last Monday."],
    ["Apple released the iPhone in San Francisco, and Tim Cook thanked Microsoft."],
    ["Washington signed the agreement with Jordan in Paris."],
    ["Jordan scored 40 points for the Chicago Bulls against the Lakers."],
]


def check_text(text):
    if not text or not text.strip():
        raise gr.Error("Please enter some text first.")
    if len(text) > MAX_CHARS:
        raise gr.Error(f"Text is too long ({len(text)} characters). Keep it under {MAX_CHARS}.")


def analyze(text, threshold, selected_labels):
    check_text(text)
    entities = [e for e in predict(text)
                if e["score"] >= threshold and e["label"] in selected_labels]
    entities.sort(key=lambda e: e["start"])
    segments = to_segments(text, entities)

    rows = [[e["text"], e["label"], round(e["score"], 3)] for e in entities]
    if rows:
        counts = {l: sum(1 for e in entities if e["label"] == l) for l in LABELS}
        parts = [f"{n} {l}" for l, n in counts.items() if n]
        summary = f"**Found {len(rows)} entities:** " + ", ".join(parts)
    else:
        summary = "**No entities found** with the current settings. Try lowering the confidence threshold."

    csv_path = None
    if rows:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="w", newline="", encoding="utf-8")
        writer = csv.writer(tmp)
        writer.writerow(["entity", "label", "confidence"])
        writer.writerows(rows)
        tmp.close()
        csv_path = tmp.name
    return segments, summary, rows, csv_path


def run_arena(text, threshold):
    check_text(text)
    bert, sp, rows = compare(text, threshold)
    agree = sum(1 for r in rows if r[3] == "Agree")
    if rows:
        summary = f"**{len(rows)} entity spans compared:** {agree} agreed, {len(rows) - agree} disagreements."
    else:
        summary = "**Neither model found entities.**"
    return to_segments(text, bert), to_segments(text, sp), summary, rows


with gr.Blocks(title="NER Studio") as demo:
    gr.Markdown("# NER Studio\nDetect people, organizations, locations and misc. entities in English text.")

    with gr.Tab("Analyzer"):
        with gr.Row():
            with gr.Column(scale=1):
                text_in = gr.Textbox(label="Input text", lines=7, placeholder="Paste or type English text here...")
                threshold = gr.Slider(0.0, 1.0, value=0.5, step=0.05, label="Confidence threshold")
                labels = gr.CheckboxGroup(LABELS, value=LABELS, label="Entity types to show")
                run_btn = gr.Button("Analyze", variant="primary")
            with gr.Column(scale=1):
                highlighted = gr.HighlightedText(label="Detected entities", color_map=COLORS, show_legend=True)
                summary_md = gr.Markdown()
                table = gr.Dataframe(headers=["Entity", "Type", "Confidence"], interactive=False, label="Entity table")
                csv_file = gr.File(label="Download results (CSV)")
        gr.Examples(examples=ANALYZER_EXAMPLES, inputs=[text_in, threshold, labels], label="Try an example")
        run_btn.click(analyze, inputs=[text_in, threshold, labels],
                      outputs=[highlighted, summary_md, table, csv_file])

    with gr.Tab("Model Arena"):
        gr.Markdown("**Same text, two models.** BERT (dslim/bert-base-NER, trained on CoNLL-2003) vs "
                    "spaCy (en_core_web_sm). Disagreements are classified as label conflicts, "
                    "boundary conflicts, or entities found by only one model.")
        arena_in = gr.Textbox(label="Input text", lines=4, placeholder="Paste or type English text here...")
        arena_thr = gr.Slider(0.0, 1.0, value=0.5, step=0.05, label="BERT confidence threshold")
        arena_btn = gr.Button("Compare models", variant="primary")
        with gr.Row():
            out_bert = gr.HighlightedText(label="BERT NER", color_map=COLORS, show_legend=True)
            out_spacy = gr.HighlightedText(label="spaCy", color_map=COLORS, show_legend=True)
        arena_summary = gr.Markdown()
        arena_table = gr.Dataframe(headers=["Text", "BERT", "spaCy", "Status"], interactive=False,
                                   label="Comparison")
        gr.Examples(examples=ARENA_EXAMPLES, inputs=[arena_in], label="Try an example")
        arena_btn.click(run_arena, inputs=[arena_in, arena_thr],
                        outputs=[out_bert, out_spacy, arena_summary, arena_table])

    if __name__ == "__main__":
     demo.launch(share=True)