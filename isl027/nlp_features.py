import re
import os
from collections import Counter
from typing import List
import matplotlib.pyplot as plt

STOPWORDS = set([
    "the", "and", "to", "of", "in", "a", "is", "for", "with", "on", "that", 
    "this", "an", "as", "are", "be", "by", "or", "from", "at", "it", "we", 
    "you", "will", "your", "our", "have", "has", "must", "should", "can"
])

def get_filtered_words(text: str) -> List[str]:
    words = re.findall(r'\b[a-z]{3,}\b', text.lower())
    return [w for w in words if w not in STOPWORDS]

def extract_top_keywords(text: str, top_n: int = 8) -> str:
    top_words = Counter(get_filtered_words(text)).most_common(top_n)
    if not top_words:
        return "No significant keywords found."
    result = "### Top Keywords in JD\n"
    for word, count in top_words:
        result += f"- **{word.capitalize()}** (appears {count} times)\n"
    return result

def create_keyword_chart(text: str):
    top_words = Counter(get_filtered_words(text)).most_common(7)
    if not top_words:
        return None
    labels = [word[0].capitalize() for word in top_words]
    counts = [word[1] for word in top_words]
    
    fig, ax = plt.subplots(figsize=(6, 3.5))
    fig.patch.set_facecolor('#1e293b') 
    ax.set_facecolor('#1e293b')
    ax.bar(labels, counts, color='#3b82f6', width=0.5) 
    
    ax.spines['bottom'].set_color('#475569')
    ax.spines['left'].set_color('#475569')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(axis='x', colors='#cbd5e1', labelsize=10)
    ax.tick_params(axis='y', colors='#cbd5e1', labelsize=10)
    ax.set_title("Top Keywords Frequency", color='#f8fafc', pad=15, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    return fig

def create_skill_gap_chart(matched: List[str], missing: List[str]):
    """Generates a pie chart showing the ratio of matched vs missing skills."""
    if not matched and not missing:
        return None
        
    labels = ['Matched Skills', 'Missing Skills']
    sizes = [len(matched), len(missing)]
    colors = ['#10b981', '#ef4444']  # Green for matched, Red for missing
    
    fig, ax = plt.subplots(figsize=(4, 3.5))
    fig.patch.set_facecolor('#1e293b')
    ax.set_facecolor('#1e293b')
    
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, colors=colors, autopct='%1.0f%%', 
        startangle=90, textprops={'color': '#cbd5e1', 'fontweight': 'bold'}
    )
    
    for autotext in autotexts:
        autotext.set_color('white')
        
    ax.axis('equal')
    ax.set_title("Skill Gap Analysis", color='#f8fafc', pad=15, fontweight='bold')
    plt.tight_layout()
    return fig

def generate_interview_questions(matched_skills: List[str]) -> str:
    if not matched_skills:
        return "### Mock Interview Questions\nNo specific technical skills matched to generate questions."
    question_bank = {
        "python": "Can you explain the difference between lists and tuples in Python?",
        "sql": "What is the difference between INNER JOIN and LEFT JOIN?",
        "machine learning": "How do you handle overfitting in machine learning models?",
        "ml": "How do you handle overfitting in machine learning models?",
        "docker": "What is the difference between a Docker image and a container?",
        "git": "How do you resolve a merge conflict in Git?",
        "aws": "Can you explain the difference between EC2 and S3 in AWS?",
        "react": "What is the difference between state and props in React?",
        "django": "What is the purpose of middleware in Django?",
    }
    result = "### Mock Interview Questions\nBased on your matched skills, prepare for these questions:\n\n"
    for skill in matched_skills:
        q = question_bank.get(skill.lower(), f"Can you describe a challenging project where you used {skill.capitalize()}?")
        result += f"- **{skill.capitalize()}**: {q}\n"
    return result

def detect_fake_job(jd_text: str) -> str:
    jd_lower = jd_text.lower()
    red_flags = []
    scam_keywords = {
        "registration fee": "Legitimate companies never ask for money for registration.",
        "pay a fee": "Never pay money to get a job.",
        "deposit": "Asking for a deposit is a common scam tactic.",
        "whatsapp": "Interviews conducted purely via WhatsApp are highly suspicious.",
        "telegram": "Recruiters using Telegram for hiring are often scammers.",
        "no experience needed": "Unrealistic promises like 'no experience, high pay' are red flags.",
        "easy money": "Too-good-to-be-true promises are usually scams.",
        "earn \$": "High daily/weekly earnings for basic work is a major red flag.",
        "western union": "Scammers often use untraceable payment methods.",
        "bitcoin": "Crypto payments for jobs are a common scam.",
    }
    for keyword, reason in scam_keywords.items():
        if keyword in jd_lower:
            red_flags.append(f"- **Detected '{keyword}'**: {reason}")
            
    emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', jd_text)
    for email in emails:
        if "@gmail.com" in email or "@yahoo.com" in email or "@hotmail.com" in email:
            red_flags.append(f"- **Suspicious Email ({email})**: Legitimate companies use corporate email addresses.")
    
    if not red_flags:
        return "### Job Authenticity Check\n✅ **Looks Safe**: No common scam patterns detected."
    
    result = "### Job Authenticity Check\n⚠️ **Warning: Potential Red Flags Detected**\n\n"
    result += "\n".join(red_flags)
    result += "\n\n*Note: Always verify the company independently.*"
    return result

def check_ats_compatibility(cv_text: str, missing_skills: List[str], matched_skills: List[str]) -> str:
    score = 100
    issues = []
    if not re.search(r'[\w\.-]+@[\w\.-]+\.\w+', cv_text):
        score -= 15
        issues.append("- **Missing Email**: ATS requires a valid email.")
    if not re.search(r'\+?\d[\d -]{8,12}\d', cv_text):
        score -= 15
        issues.append("- **Missing Phone Number**: Add a contact number.")
    word_count = len(cv_text.split())
    if word_count < 100:
        score -= 10
        issues.append(f"- **Too Short**: {word_count} words. Add more details.")
    elif word_count > 1200:
        score -= 10
        issues.append("- **Too Long**: Keep it concise.")
    if missing_skills:
        total_jd_skills = len(missing_skills) + len(matched_skills)
        if total_jd_skills > 0 and (len(missing_skills) / total_jd_skills) > 0.6:
            score -= 10
            issues.append("- **Low Keyword Density**: Missing many required keywords.")
    final_score = max(0, score)
    if not issues:
        return f"### ATS Score: {final_score}/100 (Pass)\nYour CV passes basic ATS checks."
    issues_str = "\n".join(issues)
    return f"### ATS Score: {final_score}/100\n**Issues found:**\n{issues_str}"

def generate_feedback(score: float, missing_skills: List[str]) -> str:
    if score >= 75:
        return "Excellent match! Your CV aligns very well with the job description."
    elif score >= 50:
        feedback = "Moderate match. Your CV covers some key areas, but you should strengthen it."
        if missing_skills:
            feedback += f" Consider adding these missing skills: {', '.join(missing_skills)}."
        return feedback
    else:
        return "Low match. Your CV does not seem to meet the core requirements."

def get_learning_recommendations(missing_skills: List[str]) -> str:
    if not missing_skills:
        return "No missing skills detected. Your CV looks strong!"
    resources = {
        "python": "Try 'Python for Everybody' on Coursera.",
        "sql": "Practice on LeetCode Database or W3Schools.",
        "machine learning": "Take Andrew Ng's ML Specialization on Coursera.",
        "ml": "Take Andrew Ng's ML Specialization on Coursera.",
        "docker": "Read Docker's official 'Get Started' guide.",
        "git": "Check GitHub's Git Handbook.",
        "data analysis": "Google Data Analytics Certificate on Coursera.",
        "data science": "Google Data Analytics Certificate on Coursera.",
        "communication": "Practice with Toastmasters.",
        "aws": "AWS Cloud Practitioner Essentials.",
        "react": "Follow the official React tutorial (react.dev).",
    }
    recs = ["Here are recommended resources:"]
    for skill in missing_skills:
        res = resources.get(skill, "Search for free tutorials on YouTube.")
        recs.append(f"- **{skill.capitalize()}**: {res}")
    return "\n".join(recs)

def generate_cover_letter(matched_skills: List[str]) -> str:
    skills_str = ", ".join(matched_skills) if matched_skills else "relevant skills"
    letter = "Dear Hiring Manager,\n\n"
    letter += "I am writing to express my strong interest in the position described in your recent job posting. "
    letter += "With my background and expertise, I am confident that I can make a significant contribution to your team.\n\n"
    letter += f"As highlighted in my CV, I possess strong skills in {skills_str}, which directly align with your requirements. "
    letter += "I have consistently delivered results in my previous roles and am eager to bring this same level of dedication to your company.\n\n"
    letter += "Thank you for considering my application. I look forward to discussing how my skills align with your team's needs.\n\n"
    letter += "Sincerely,\n[Your Name]"
    return letter
