# Resume Optimization System

## Project Overview

The Resume Optimization System is a Python application that compares a resume (CV) with a job description (JD). It uses a pre-trained SentenceTransformer model to compare the meaning of the two texts and a skill dictionary to identify matching and missing skills.

The application is built with Gradio. It is intended to help job seekers review how closely their resume relates to a particular vacancy. It can also provide basic resume checks and preparation suggestions.

The score is a guide for reviewing a resume. It should not be treated as a hiring decision or a guarantee of getting an interview.

## Main Features

The application has three main sections.

### 1. Resume Analyzer

- Accepts resume text or a text-based PDF.
- Compares the resume with a job description.
- Displays a match score and a match category.
- Lists matched and missing skills.
- Shows a skill-gap pie chart.
- Displays frequently used words in the job description.
- Provides basic ATS-related checks.
- Shows possible warning signs in a job advertisement.
- Generates interview questions and learning suggestions.
- Displays a resume preview with matched skills highlighted.

### 2. Cover Letter Generator

The user provides resume text and a job description. The application compares them and uses the matched skills to prepare a cover letter draft. Users can also enter extra skills they want to highlight.

The generated letter is a starting draft. It should be reviewed and edited before being sent to an employer.

### 3. Recruiter Mode

Recruiter Mode accepts multiple text-based PDF resumes and compares them with one job description. It displays a candidate ranking table and a bar chart of the calculated match scores.

## Machine Learning Model

The project uses the following pre-trained model:

- **Model:** `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- **Source:** Hugging Face Model Hub
- **Model type:** SentenceTransformer
- **Main use:** Text embedding and semantic similarity

The model converts the resume and job description into numerical vector representations called embeddings. The application then calculates cosine similarity between these embeddings.

The final score combines two parts:

- 60% semantic similarity
- 40% exact skill match ratio

The skill match ratio is calculated from the number of recognized job-description skills that are also found in the resume.

If the job description contains no skills from the predefined dictionary, the application uses the semantic score as the skill score as well.

The final result is limited to the range from 0 to 100.

### Match Categories

- **Strong match:** 75% or higher
- **Moderate match:** 50% to below 75%
- **Low match:** Below 50%

These categories are project-defined thresholds, not official hiring standards.

## Other Processing Methods

Some features do not use a trained machine learning classifier. They use predefined rules or keyword lists.

- Skill extraction uses a fixed dictionary and regular expressions.
- ATS-related checks look for contact information, resume word count and missing job skills.
- The job warning feature searches for selected suspicious phrases and email patterns.
- Interview questions and learning suggestions are selected from predefined rules.
- Keyword frequency is calculated using word counts.

These features are intended as basic assistance. They do not replace a professional ATS platform, a recruitment investigation or human review.

## Project Structure

```text
Resume-Optimization-System/
│
├── app.py
├── model_utils.py
├── nlp_features.py
├── evaluation.py
├── requirements.txt
├── README.md
└── evaluation_results.csv   # Created after running evaluation.py
```

## Requirements

- Python 3.10 or a compatible newer Python version
- pip
- Internet connection for the first model download
- Sufficient memory to load the SentenceTransformer model

The Python packages used by the project are listed in `requirements.txt`.

## Installation

Open a terminal in the project folder.

### 1. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can use this command for the current terminal session:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Linux or macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Download the model before the first run

The application is configured to load the model in offline mode. Therefore, the model must already exist in the local Hugging Face cache.

Run this command once while you have an internet connection:

```bash
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')"
```

Wait until the model has finished downloading. After that, the application can load it from the local cache.

If the model is not cached, the application will not be able to download it automatically because offline mode is enabled.

## Running the Application

After installing the dependencies and downloading the model, run:

```bash
python app.py
```

Open the following address in your browser if it does not open automatically:

```text
http://127.0.0.1:7860
```

## Running Model Evaluation

The evaluation script checks the main text-processing functions using a small set of manually labelled examples.

Run:

```bash
python evaluation.py
```

The evaluation includes:

- Skill extraction checks against manually specified expected skills.
- Candidate matching checks for strong, partial and low skill matches.
- Fake-job warning checks using selected positive and negative examples.
- Precision, Recall and F1-score for skill extraction and fake-job warning tests.
- Candidate match scores and categories.

The script creates:

```text
evaluation_results.csv
```

This file contains the individual test results.

The evaluation examples are limited and manually prepared. The reported metrics should not be interpreted as general accuracy on real resumes or job advertisements. A larger independently labelled dataset would be needed for a stronger performance evaluation.

## Input Notes

- Resume text can be pasted directly into the application.
- PDF upload is supported for PDFs that contain selectable text.
- Image-only or scanned PDFs may not produce extractable text because OCR is not included.
- For batch comparison, upload text-based PDF resumes.
- The job description should contain clear role requirements for more useful skill comparison.

## Limitations

1. **Fixed skill dictionary:** The application only recognizes skills included in its predefined list. New, specialized or differently written skills may be missed.
2. **Exact skill matching:** Skill extraction is based on keyword patterns. It may not understand every synonym or equivalent skill description.
3. **Semantic score:** Similarity between two text embeddings does not prove that a candidate is qualified for a job.
4. **ATS checks:** The ATS score is a small set of heuristic checks. It is not a real ATS compatibility test and does not fully inspect resume formatting.
5. **Job warning feature:** The detector identifies selected warning signs. It cannot confirm whether a job is genuine or fraudulent.
6. **Generated content:** Cover letters, interview questions and learning recommendations should be checked by the user.
7. **PDF extraction:** Scanned PDFs are not supported because the project does not include OCR.
8. **Evaluation data:** The current evaluation uses a small set of manually prepared examples. It is not a large benchmark.

## Acknowledgements

- The pre-trained SentenceTransformer model is provided through the Hugging Face Model Hub.
- Gradio is used to build the application interface.
- Matplotlib is used for charts.
- pypdf is used to extract text from PDF resumes.
- pandas is used to organize candidate comparison results.

## Responsible Use

This application is a resume review aid. It should not be used as the only basis for hiring, rejecting or ranking real people. Users and recruiters should review the original resume and job requirements before making decisions.