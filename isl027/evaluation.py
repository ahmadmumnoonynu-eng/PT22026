"""
Evaluation Script for Resume Optimization System.
This script tests the core matching logic against predefined test cases 
to validate the reliability of the blended scoring algorithm.
"""

from model_utils import analyze_match
from nlp_features import detect_fake_job

def run_evaluation():
    # Define test cases representing different levels of match
    test_cases = [
        {
            "name": "Candidate A (Perfect Match)",
            "cv": "I am a Python Developer with strong skills in Python, SQL, Django, AWS, and Machine Learning.",
            "jd": "We need a Python Developer with expertise in Python, SQL, Django, AWS, and Machine Learning."
        },
        {
            "name": "Candidate B (Partial Match)",
            "cv": "I am a Frontend Developer with skills in HTML, CSS, React, and JavaScript. I have basic knowledge of Python.",
            "jd": "We need a Python Developer with expertise in Python, SQL, Django, AWS, and Machine Learning."
        },
        {
            "name": "Candidate C (Low Match)",
            "cv": "I am a Laundry Supervisor with experience in Fabric Sorting, Ironing, and Hygiene Management.",
            "jd": "We need a Python Developer with expertise in Python, SQL, Django, AWS, and Machine Learning."
        }
    ]

    print("=" * 90)
    print(f"{'AUTOMATED EVALUATION RESULTS':^90}")
    print("=" * 90)
    print(f"{'Candidate Profile':<30} | {'Score':<8} | {'Level':<15} | {'Matched Skills'}")
    print("-" * 90)

    # Iterate through test cases and print results
    for case in test_cases:
        result = analyze_match(case["cv"], case["jd"])
        matched = ", ".join(result["matched"]) if result["matched"] else "None"
        
        # Format the output row
        print(f"{case['name']:<30} | {result['score']:>5}%   | {result['level']:<15} | {matched}")

    print("-" * 90)
    print("\n--- Fake Job Detection Test ---")
    
    # Test case for Scam Detector
    fake_jd = "Urgent hiring! No experience needed. Pay a registration fee via Western Union. Contact us on WhatsApp: 017XXXXX."
    scam_result = detect_fake_job(fake_jd)
    
    print(f"Testing Fake JD: {fake_jd[:50]}...")
    print(f"Result:\n{scam_result}")
    print("=" * 90)

if __name__ == "__main__":
    run_evaluation()
