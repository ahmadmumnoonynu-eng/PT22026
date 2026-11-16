import os
import re
import threading
import webbrowser
from typing import List
import pandas as pd

import gradio as gr

os.environ["NO_PROXY"] = "localhost,127.0.0.1"
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

from model_utils import analyze_match, extract_text_from_pdf, load_model
from nlp_features import (
    check_ats_compatibility, extract_top_keywords, generate_cover_letter,
    generate_feedback, get_learning_recommendations, create_keyword_chart,
    generate_interview_questions, detect_fake_job, create_skill_gap_chart,
    create_comparison_chart
)

print("Loading NLP models from local cache, please wait...")
load_model()
print("Models loaded successfully! Starting app...")

def highlight_skills(text: str, skills: List[str]) -> str:
    if not text:
        return ""
    highlighted = text
    for skill in skills:
        pattern = re.compile(r"(?<!\w)(" + re.escape(skill) + r")(?!\w)", re.IGNORECASE)
        highlighted = pattern.sub(
            r'<span style="background-color: #d4edda; color: #155724; font-weight: bold; padding: 2px 4px; border-radius: 4px;">\1</span>',
            highlighted
        )
    return highlighted

def run_analysis(cv_text: str, jd_text: str, cv_file) -> tuple:
    try:
        if cv_file is not None:
            pdf_text = extract_text_from_pdf(cv_file.name)
            cv_text = (cv_text or "") + "\n" + pdf_text

        if not cv_text or not jd_text:
            # Fixed: Return None for plot components instead of empty strings
            return "Please provide both a CV and a Job Description.", "", "", None, "", "", "", None, "", "", "", ""

        result = analyze_match(cv_text, jd_text)
        
        score_md = f"""
        <div style='text-align: center; padding: 20px; background: rgba(37, 99, 235, 0.1); border-radius: 10px; border: 1px solid #2563eb;'>
            <p style='margin: 0; font-size: 1.1rem; color: #94a3b8; font-weight: 600; text-transform: uppercase;'>Match Score</p>
            <h1 style='margin: 10px 0; font-size: 4rem; color: #3b82f6; font-weight: 800;'>{result['score']}%</h1>
            <p style='margin: 0; font-size: 1.2rem; color: #e2e8f0; font-weight: bold;'>{result['level']}</p>
        </div>
        """
        
        matched_html = "".join([f"<span style='display:inline-block; background: #10b981; color: white; padding: 4px 10px; border-radius: 15px; margin: 4px; font-size: 0.9rem; font-weight: 600;'>{s.capitalize()}</span>" for s in result['matched']])
        missing_html = "".join([f"<span style='display:inline-block; background: #ef4444; color: white; padding: 4px 10px; border-radius: 15px; margin: 4px; font-size: 0.9rem; font-weight: 600;'>{s.capitalize()}</span>" for s in result['missing']])
        
        matched_md = f"### Matched Skills\n<div>{matched_html if matched_html else 'None found'}</div>"
        missing_md = f"### Missing Skills\n<div>{missing_html if missing_html else 'None detected'}</div>"
        
        gap_chart_fig = create_skill_gap_chart(result['matched'], result['missing'])
        scam_md = detect_fake_job(jd_text)
        ats_md = check_ats_compatibility(cv_text, result['missing'], result['matched'])
        keyword_md = extract_top_keywords(jd_text)
        keyword_chart_fig = create_keyword_chart(jd_text)
        questions_md = generate_interview_questions(result['matched'])
        
        feedback_md = f"### Automated Feedback\n{generate_feedback(result['score'], result['missing'])}"
        learning_md = f"### Skill Gap Learning Path\n{get_learning_recommendations(result['missing'])}"
        
        hl_text = highlight_skills(cv_text, result['matched'])
        highlight_md = (
            "### Document Preview\n"
            f"<div style='max-height: 300px; overflow-y: auto; padding: 15px; border: 1px solid #475569; "
            f"background-color: #1e293b; border-radius: 8px; white-space: pre-wrap; font-size: 14px; line-height: 1.6; color: #cbd5e1;'>{hl_text}</div>"
        )
        
        return score_md, matched_md, missing_md, gap_chart_fig, scam_md, ats_md, keyword_md, keyword_chart_fig, questions_md, feedback_md, learning_md, highlight_md
        
    except Exception as e:
        return f"Error: {str(e)}", "", "", None, "", "", "", None, "", "", "", ""

def run_batch_analysis(jd_text: str, files: list):
    if not jd_text or not files:
        return None, pd.DataFrame([["Error", "Please provide JD and at least one CV", ""]], columns=["Candidate", "Score", "Details"])
    
    results = []
    names = []
    scores = []
    
    for file in files:
        try:
            pdf_text = extract_text_from_pdf(file.name)
            result = analyze_match(pdf_text, jd_text)
            
            candidate_name = os.path.basename(file.name).replace(".pdf", "")
            names.append(candidate_name)
            scores.append(result['score'])
            
            matched_str = ", ".join(result['matched']) if result['matched'] else "None"
            results.append([candidate_name, result['score'], matched_str, result['level']])
        except Exception as e:
            results.append([os.path.basename(file.name), 0.0, "Error reading file", "Error"])
            
    results.sort(key=lambda x: x[1], reverse=True)
    df = pd.DataFrame(results, columns=["Candidate Name", "Match Score (%)", "Matched Skills", "Level"])
    chart_fig = create_comparison_chart(names, scores)
    
    return chart_fig, df

theme = gr.themes.Soft(primary_hue="blue", secondary_hue="slate")

# Moved theme to launch() to fix the warning
with gr.Blocks(title="Resume Optimization System") as demo:
    
    gr.Markdown("# Resume Optimization System\n**Advanced NLP Analysis for Job Seekers and Professionals**")
    
    with gr.Tabs():
        # TAB 1: Resume Analyzer
        with gr.TabItem("Resume Analyzer"):
            with gr.Row():
                with gr.Column(scale=1):
                    with gr.Group():
                        gr.Markdown("### 1. Input Data")
                        cv_text = gr.Textbox(label="Resume Text", lines=6, placeholder="Paste your full CV text here...")
                        cv_file = gr.File(label="Or upload Resume as PDF", file_types=[".pdf"])
                        jd_text = gr.Textbox(label="Job Description", lines=6, placeholder="Paste the target job description here...")
                        
                    with gr.Row():
                        btn = gr.Button("Analyze Match", variant="primary", size="lg")
                        stop1 = gr.Button("Clear", variant="secondary", size="lg")

                with gr.Column(scale=1):
                    with gr.Group():
                        out_score = gr.HTML() 
                        with gr.Row():
                            out_matched = gr.Markdown()
                            out_missing = gr.Markdown()
                        out_gap_chart = gr.Plot(show_label=False)
                    
                    with gr.Group():
                        out_scam = gr.Markdown()
                    
                    with gr.Group():
                        gr.Markdown("### Keyword Frequency Chart")
                        out_keyword_chart = gr.Plot(show_label=False)
                    
                    with gr.Accordion("ATS Compatibility & Keyword List", open=False):
                        with gr.Group():
                            out_ats = gr.Markdown()
                            out_keywords = gr.Markdown()
                    
                    with gr.Accordion("Interview Preparation", open=False):
                        out_questions = gr.Markdown()

                    with gr.Accordion("Feedback & Learning Recommendations", open=False):
                        with gr.Group():
                            out_feedback = gr.Markdown()
                            out_learning = gr.Markdown()

                    with gr.Accordion("Document Preview (Highlighted Skills)", open=False):
                        out_highlight = gr.Markdown()

            event1 = btn.click(
                fn=run_analysis, 
                inputs=[cv_text, jd_text, cv_file], 
                outputs=[out_score, out_matched, out_missing, out_gap_chart, out_scam, out_ats, out_keywords, out_keyword_chart, out_questions, out_feedback, out_learning, out_highlight]
            )
            # Fixed: Return None for plots on Clear
            stop1.click(fn=lambda: ("", "", "", None, "", "", "", None, "", "", "", ""), inputs=None, outputs=[out_score, out_matched, out_missing, out_gap_chart, out_scam, out_ats, out_keywords, out_keyword_chart, out_questions, out_feedback, out_learning, out_highlight])

        # TAB 2: Cover Letter Generator
        with gr.TabItem("Cover Letter Generator"):
            with gr.Row():
                with gr.Column(scale=1):
                    with gr.Group():
                        gr.Markdown("### Letter Details")
                        cl_cv = gr.Textbox(label="Resume Text", lines=5)
                        cl_jd = gr.Textbox(label="Job Description", lines=5)
                        cl_skills = gr.Textbox(label="Key Skills to Highlight (comma separated)", lines=2, placeholder="e.g., Python, SQL, Machine Learning")
                        
                        with gr.Row():
                            cl_btn = gr.Button("Generate Letter", variant="primary", size="lg")
                            stop2 = gr.Button("Clear", variant="secondary", size="lg")
                
                with gr.Column(scale=1):
                    with gr.Group():
                        cl_output = gr.Textbox(label="Generated Cover Letter Draft", lines=16)
            
            event2 = cl_btn.click(
                fn=lambda cv, jd, skills: generate_cover_letter([s.strip() for s in skills.split(",") if s.strip()]), 
                inputs=[cl_cv, cl_jd, cl_skills], 
                outputs=[cl_output]
            )
            stop2.click(fn=lambda: ("",), inputs=None, outputs=[cl_output])

        # TAB 3: Recruiter Mode (Batch Compare)
        with gr.TabItem("Recruiter Mode"):
            gr.Markdown("### Batch Candidate Analysis\nUpload multiple PDF resumes against a single Job Description to instantly rank candidates and visualize their match scores.")
            with gr.Row():
                with gr.Column(scale=1):
                    batch_jd = gr.Textbox(label="Job Description", lines=8, placeholder="Paste the JD here...")
                    batch_files = gr.File(label="Upload Multiple Resumes (PDF)", file_count="multiple", file_types=[".pdf"])
                    with gr.Row():
                        batch_btn = gr.Button("Compare Candidates", variant="primary", size="lg")
                        stop3 = gr.Button("Clear", variant="secondary", size="lg")
                
                with gr.Column(scale=2):
                    with gr.Group():
                        gr.Markdown("### Comparison Chart")
                        batch_chart = gr.Plot(show_label=False)
                    
                    with gr.Group():
                        gr.Markdown("### Candidate Ranking Table")
                        batch_table = gr.Dataframe(
                            headers=["Candidate Name", "Match Score (%)", "Matched Skills", "Level"],
                            datatype=["str", "number", "str", "str"],
                            label=""
                        )

            batch_btn.click(fn=run_batch_analysis, inputs=[batch_jd, batch_files], outputs=[batch_chart, batch_table])
            stop3.click(fn=lambda: (None, pd.DataFrame()), inputs=None, outputs=[batch_chart, batch_table])

if __name__ == "__main__":
    def open_browser():
        webbrowser.open_new("http://127.0.0.1:7860")
    
    threading.Timer(2, open_browser).start()
    # Fixed: Pass theme to launch() for Gradio 6.0 compatibility
    demo.launch(theme=theme, server_name="127.0.0.1", server_port=7860)
