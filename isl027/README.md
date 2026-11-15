# Smart CV - Job Description Matcher

## Project Overview
This is an interactive Machine Learning application that compares a Curriculum Vitae (CV) with a Job Description (JD). It uses Natural Language Processing (NLP) to calculate a semantic match score and identify skill gaps. The app also highlights the matched skills directly within the CV text.

## Machine Learning Model
- **Model:** sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
- **Source:** Hugging Face Model Hub
- **Architecture:** Transformer-based SentenceTransformer (MiniLM-L12)
- **Operation:** The text from the CV and JD is converted into dense vector embeddings. Cosine similarity is calculated between these embeddings to generate a match score (0-100%). A predefined dictionary is used for skill extraction.

## Features
- **Semantic Matching:** Goes beyond simple keyword matching by understanding the context.
- **Skill Gap Analysis:** Identifies which required skills are missing from the CV.
- **Explainable AI:** Highlights the matched skills in green within the CV text.
- **PDF Support:** Allows users to upload their CV as a PDF file.
- **Multilingual Support:** Supports over 50 languages.

## Capabilities and Limitations
**Capabilities:**
- Fast inference on CPU.
- Handles both English and Bengali text effectively (thanks to the multilingual model).
- Provides a user-friendly interface using Gradio.

**Limitations:**
- The match score is a decision-support metric, not a real hiring decision.
- The skill extraction relies on a predefined list; domain-specific skills might be missed.
- Image-based/scanned PDFs are not supported for text extraction.

## Installation and Setup
1. Clone the repository and navigate to the project folder.
2. Create a virtual environment and activate it.
3. Install the required dependencies: pip install -r requirements.txt

## How to Run
python app.py

The application will automatically open in your default web browser.

## Usage
1. Paste the CV text (or upload a PDF) on the left.
2. Paste the Job Description on the right.
3. Click Analyze Match.
4. Review the Match Score, Matched Skills, Missing Skills, and the highlighted CV text.

## Acknowledgements
- Pre-trained model provided by Hugging Face.
- UI built with Gradio.
