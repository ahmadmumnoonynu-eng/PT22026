"""Gradio app for Named Entity Recognition."""
import os
os.environ["NO_PROXY"] = "localhost,127.0.0.1,0.0.0.0"
os.environ["no_proxy"] = "localhost,127.0.0.1,0.0.0.0"
os.environ["HF_HUB_OFFLINE"] = "1"
import csv
import tempfile

import gradio as gr

from src.inference import predict

MAX_CHARS = 1500
LABELS = ["PER", "ORG", "LOC", "MISC"]
COLORS = {"PER": "#4C9AFF", "ORG": "#FFAB00", "LOC": "#36B37E", "MISC": "#B37FEB"}

EXAMPLES = [
    ["Elon Musk visited Google headquarters in California last Monday.", 0.5, LABELS],
    ["Angela Merkel met Emmanuel Macron in Paris to discuss the European Union budget.", 0.5, LABELS],
    ["Apple released the iPhone in San Francisco, and Tim Cook thanked Microsoft.", 0.5, LABELS],
    ["Jordan scored 40 points for the Chicago Bulls against the Lakers.", 0.5, LABELS],
]


def analyze(text, threshold, selected_labels):
    # Input validation
    if not text or not text.strip():
        raise gr.Error("Please enter some text first.")
    if len(text) > MAX_CHARS:
        raise gr.Error(f"Text is too long ({len(text)} characters). Keep it under {MAX_CHARS}.")

    # Predict, then filter by confidence and entity type
    entities = [
        e for e in predict(text)
        if e["score"] >= threshold and e["label"] in selected_labels
    ]
    entities.sort(key=lambda e: e["start"])

    # Build highlighted segments: (text, label or None)
    segments, pos = [], 0
    for e in entities:
        if e["start"] < pos:
            continue
        if e["start"] > pos:
            segments.append((text[pos:e["start"]], None))
        segments.append((text[e["start"]:e["end"]], e["label"]))
        pos = e["end"]
    if pos < len(text):
        segments.append((text[pos:], None))

    # Table rows and summary
    rows = [[e["text"], e["label"], round(e["score"], 3)] for e in entities]
    if rows:
        counts = {l: sum(1 for e in entities if e["label"] == l) for l in LABELS}
        parts = [f"{n} {l}" for l, n in counts.items() if n]
        summary = f"**Found {len(rows)} entities:** " + ", ".join(parts)
    else:
        summary = "**No entities found** with the current settings. Try lowering the confidence threshold."

    # CSV export
    csv_path = None
    if rows:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="w", newline="", encoding="utf-8")
        writer = csv.writer(tmp)
        writer.writerow(["entity", "label", "confidence"])
        writer.writerows(rows)
        tmp.close()
        csv_path = tmp.name

    return segments, summary, rows, csv_path


with gr.Blocks(title="NER Studio") as demo:
    gr.Markdown("# NER Studio\nDetect people, organizations, locations and misc. entities in English text.")

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

    gr.Examples(examples=EXAMPLES, inputs=[text_in, threshold, labels], label="Try an example")

    run_btn.click(analyze, inputs=[text_in, threshold, labels],
                  outputs=[highlighted, summary_md, table, csv_file])

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860, share=False)