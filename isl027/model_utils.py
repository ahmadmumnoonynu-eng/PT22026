import os
import re
from functools import lru_cache
from typing import Dict, List

from sentence_transformers import SentenceTransformer, util

# Force offline mode for fast, reproducible local execution
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# Predefined skill dictionary for keyword extraction
SKILLS: List[str] = [
    "python", "java", "javascript", "typescript", "c++", "c#", "sql",
    "html", "css", "react", "node.js", "django", "flask", "fastapi",
    "machine learning", "ml", "deep learning", "nlp", "computer vision",
    "data analysis", "data analytics", "data science", "pandas", "numpy",
    "scikit-learn", "tensorflow", "pytorch", "keras",
    "power bi", "tableau", "excel", "git", "github", "version control",
    "aws", "azure", "gcp", "docker", "kubernetes", "linux",
    "communication", "teamwork", "leadership", "problem solving",
    "project management", "agile", "scrum",
]


@lru_cache(maxsize=1)
def load_model() -> SentenceTransformer:
    """
    Load and cache the pre-trained SentenceTransformer model.
    Using lru_cache ensures the model is only loaded into memory once.
    """
    return SentenceTransformer(MODEL_NAME, local_files_only=True)


def normalize_text(text: str) -> str:
    """Converts text to lowercase and removes extra whitespaces."""
    return re.sub(r"\s+", " ", text.lower()).strip()


def extract_skills(text: str) -> List[str]:
    """
    Extracts known skills from the given text using regular expressions.
    Returns a sorted list of unique skills found.
    """
    text_norm = normalize_text(text)
    found_skills = []
    
    for skill in SKILLS:
        # Regex ensures exact word matches (e.g., 'java' won't match 'javascript')
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"
        if re.search(pattern, text_norm):
            found_skills.append(skill)
            
    return sorted(set(found_skills))


def extract_text_from_pdf(path: str) -> str:
    """Extracts raw text content from an uploaded PDF file."""
    try:
        from pypdf import PdfReader
    except ImportError:
        raise RuntimeError("pypdf is not installed. Run: pip install pypdf")
        
    reader = PdfReader(path)
    text = "\n".join([page.extract_text() or "" for page in reader.pages]).strip()
    
    if not text:
        raise ValueError("Could not extract text from the PDF. It might be an image-based PDF.")
    return text


def analyze_match(cv_text: str, jd_text: str) -> Dict:
    """
    Compares the CV and Job Description to calculate a reliable match score.
    Uses a blended metric: 60% Semantic Similarity + 40% Skill Match Ratio.
    """
    cv_text = (cv_text or "").strip()
    jd_text = (jd_text or "").strip()
    
    if not cv_text or not jd_text:
        raise ValueError("Both CV and Job Description are required.")

    model = load_model()
    
    # 1. Semantic Similarity (Contextual meaning)
    cv_emb = model.encode(cv_text, convert_to_tensor=True, normalize_embeddings=True)
    jd_emb = model.encode(jd_text, convert_to_tensor=True, normalize_embeddings=True)
    raw_similarity = float(util.cos_sim(cv_emb, jd_emb)[0][0])
    semantic_score = raw_similarity * 100

    # 2. Skill Match Ratio (Exact keyword matches)
    cv_skills = set(extract_skills(cv_text))
    jd_skills = set(extract_skills(jd_text))
    
    matched_skills = sorted(cv_skills & jd_skills)
    missing_skills = sorted(jd_skills - cv_skills)
    
    # Avoid division by zero if JD has no recognizable skills
    if len(jd_skills) > 0:
        skill_match_ratio = (len(matched_skills) / len(jd_skills)) * 100
    else:
        skill_match_ratio = semantic_score 

    # 3. Blended Final Score
    final_score = (semantic_score * 0.6) + (skill_match_ratio * 0.4)
    score = round(min(100.0, max(0.0, final_score)), 1)

    # Determine qualitative match level
    if score >= 75:
        level = "Strong match"
    elif score >= 50:
        level = "Moderate match"
    else:
        level = "Low match"

    return {
        "score": score,
        "similarity": raw_similarity,
        "level": level,
        "matched": matched_skills,
        "missing": missing_skills
    }
