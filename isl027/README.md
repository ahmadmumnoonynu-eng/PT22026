# Resume Optimization System

## Project Overview
This is an interactive Machine Learning and NLP-based application designed to help job seekers optimize their resumes. The system compares a Curriculum Vitae (CV) against a Job Description (JD) using pre-trained Transformer models and rule-based logic to provide highly reliable insights, skill gap analysis, and application preparation tools.

## Motivation and Justification
According to the course guidelines, students are encouraged to explore innovative applications beyond standard examples. This project addresses a real-world NLP problem: semantic text similarity combined with information extraction. By providing a blended scoring mechanism, ATS compatibility checks, and a fake job detector, the system serves as a comprehensive "Career Coach" rather than a simple keyword matcher.

## Machine Learning Model & Architecture
- **Model:** `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (Hugging Face)
- **Architecture:** Transformer-based SentenceTransformer.
- **Operation:** The system converts CVs and JDs into dense vector embeddings. It calculates Cosine Similarity for contextual understanding. To ensure realistic scoring, it uses a **Blended Score**: 60% Semantic Similarity + 40% Exact Skill Match Ratio.

## Key Features
1. **Semantic CV-JD Matcher:** Calculates a realistic match score and highlights matched skills directly in the CV text.
2. **Skill Gap Analysis (Pie Chart):** Visualizes the ratio of matched vs. missing skills.
3. **ATS Compatibility Checker:** Evaluates CV formatting (email, phone, word count, keyword density) to ensure it passes Applicant Tracking Systems.
4. **Scam / Fake Job Detector:** Analyzes the JD for suspicious keywords (e.g., "registration fee", "WhatsApp") and free email domains to warn users about potential job scams.
5. **Keyword Frequency Chart (Bar Chart):** Extracts and visualizes the most important keywords from the Job Description.
6. **Interview Preparation:** Generates mock interview questions based on the candidate's matched skills.
7. **Learning Recommendations:** Provides curated learning resources for missing skills.
8. **Cover Letter Generator:** Automatically drafts a professional cover letter based on matched skills.

## Limitations
- The match score is a decision-support metric, not a replacement for human recruiters.
- The skill extraction relies on a predefined dictionary; highly niche skills might be missed.
- Scanned/image-based PDFs do not support text extraction.

## Installation and Setup
1. Clone the repository and navigate to the project folder.
2. Create and activate a virtual environment:
   `python -m venv .venv`
   `.venv\Scripts\activate` (Windows)
3. Install the required dependencies:
   `pip install -r requirements.txt`

## How to Run
Run the following command in the terminal:
`python app.py`
The application will automatically open in your default web browser at `http://127.0.0.1:7860`.

## Acknowledgements
- Pre-trained model provided by [Hugging Face](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2).
- UI built using [Gradio](https://gradio.app/).
- Data visualization using Matplotlib.
