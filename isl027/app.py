import os
os.environ["HF_HUB_OFFLINE"] = "1"
import re
os.environ["NO_PROXY"] = "localhost,127.0.0.1"

import gradio as gr
from model_utils import analyze_match, extract_text_from_pdf, load_model

# Pre-load the model so the first click is fast
load_model()

def highlight_skills(text, skills):
    if not text:
        return ""
    highlighted = text
    for skill in skills:
        pattern = re.compile(r"(?<!\w)(" + re.escape(skill) + r")(?!\w)", re.IGNORECASE)
        highlighted = pattern.sub(r'<span style="background-color: #d4edda; color: #155724; font-weight: bold; padding: 2px 4px; border-radius: 4px;">\1</span>', highlighted)
    return highlighted

def run_analysis(cv_text, jd_text, cv_file):
    try:
        if cv_file is not None:
            pdf_text = extract_text_from_pdf(cv_file.name)
            cv_text = (cv_text or "") + "\n" + pdf_text

        if not cv_text or not jd_text:
            return "### Missing Input\nPlease provide both a CV and a Job Description.", "", "", ""

        result = analyze_match(cv_text, jd_text)
        
        score_md = f"## Match Score: **{result['score']} / 100**\n**{result['level']}**\nCosine similarity: {result['similarity']:.3f}"
        matched_md = "### Matched Skills\n" + ("\n".join(f"- {s}" for s in result['matched']) if result['matched'] else "- None found")
        missing_md = "### Missing Skills\n" + ("\n".join(f"- {s}" for s in result['missing']) if result['missing'] else "- None detected")
        
        hl_text = highlight_skills(cv_text, result['matched'])
        rec_md = f"### Recommendation\n{result['recommendation']}\n\n### How your CV looks with matched skills highlighted:\n<div style='max-height: 300px; overflow-y: auto; padding: 10px; border: 1px solid #ccc; border-radius: 5px; white-space: pre-wrap; font-size: 14px;'>{hl_text}</div>"
        
        return score_md, matched_md, missing_md, rec_md
        
    except Exception as e:
        return f"### Error\n{str(e)}", "", "", ""

with gr.Blocks(title="Smart CV Matcher") as demo:
    gr.Markdown(
        "# Smart CV-Job Description Matcher\n"
        "Optimize your resume by matching it with job requirements using AI."
    )
    
    with gr.Row():
        with gr.Column():
            cv_text = gr.Textbox(label="Paste CV Text", lines=8, placeholder="Paste your CV here...")
            cv_file = gr.File(label="Or upload CV as PDF", file_types=[".pdf"])
        with gr.Column():
            jd_text = gr.Textbox(label="Paste Job Description", lines=8, placeholder="Paste the job requirements here...")
    
    btn = gr.Button("Analyze Match", variant="primary", size="lg")
    
    out_score = gr.Markdown()
    with gr.Row():
        out_matched = gr.Markdown()
        out_missing = gr.Markdown()
    out_rec = gr.Markdown()

    btn.click(fn=run_analysis, inputs=[cv_text, jd_text, cv_file], outputs=[out_score, out_matched, out_missing, out_rec])

if __name__ == "__main__":
    # Theme moved to launch() for Gradio 6.0 compatibility
    theme = gr.themes.Soft(primary_hue="blue", secondary_hue="slate")
    demo.launch(inbrowser=True, theme=theme)

