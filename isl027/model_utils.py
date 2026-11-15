import re
from functools import lru_cache
from sentence_transformers import SentenceTransformer, util
import os

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# Path to the locally cached model
LOCAL_MODEL_PATH = os.path.expanduser("~/.cache/huggingface/hub/models--sentence-transformers--paraphrase-multilingual-MiniLM-L12-v2/snapshots")

SKILLS = [
    "python", "java", "javascript", "typescript", "c++", "c#", "sql",
    "html", "css", "react", "node.js", "django", "flask", "fastapi",
    "machine learning", "deep learning", "nlp", "computer vision",
    "data analysis", "data visualization", "pandas", "numpy",
    "scikit-learn", "tensorflow", "pytorch", "keras",
    "power bi", "tableau", "excel",
    "aws", "azure", "gcp", "docker", "kubernetes", "git", "linux",
    "communication", "teamwork", "leadership", "problem solving",
    "project management", "agile", "scrum",
]

@lru_cache(maxsize=1)
def load_model():
    # Find the exact snapshot folder dynamically
    snapshot_dir = os.listdir(LOCAL_MODEL_PATH)[0]
    exact_path = os.path.join(LOCAL_MODEL_PATH, snapshot_dir)
    return SentenceTransformer(exact_path)

def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()

def extract_skills(text: str) -> list:
    text_norm = normalize_text(text)
    found = []
    for skill in SKILLS:
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"
        if re.search(pattern, text_norm):
            found.append(skill)
    return sorted(set(found))

def extract_text_from_pdf(path: str) -> str:
    try:
        from pypdf import PdfReader
    except ImportError:
        raise RuntimeError("pypdf is not installed.")
        
    reader = PdfReader(path)
    text = "\n".join([page.extract_text() or "" for page in reader.pages]).strip()
    if not text:
        raise ValueError("Could not extract text from the PDF.")
    return text

def analyze_match(cv_text: str, jd_text: str) -> dict:
    cv_text = (cv_text or "").strip()
    jd_text = (jd_text or "").strip()
    
    if not cv_text or not jd_text:
        raise ValueError("Both CV and Job Description are required.")

    model = load_model()
    cv_emb = model.encode(cv_text, convert_to_tensor=True, normalize_embeddings=True)
    jd_emb = model.encode(jd_text, convert_to_tensor=True, normalize_embeddings=True)
    
    similarity = float(util.cos_sim(cv_emb, jd_emb)[0][0])
    score = round(max(0.0, min(1.0, similarity)) * 100, 1)

    cv_skills = set(extract_skills(cv_text))
    jd_skills = set(extract_skills(jd_text))

    matched = sorted(cv_skills & jd_skills)
    missing = sorted(jd_skills - cv_skills)

    if score >= 75:
        level = "Strong match"
    elif score >= 50:
        level = "Moderate match"
    else:
        level = "Low match"

    if missing:
        rec = f"The CV matches at a {level.lower()} level. Consider adding these skills: {', '.join(missing)}."
    else:
        rec = f"The CV matches at a {level.lower()} level. No major skill gaps found."

    return {
        "score": score, 
        "similarity": similarity, 
        "level": level, 
        "matched": matched, 
        "missing": missing, 
        "recommendation": rec
    }
