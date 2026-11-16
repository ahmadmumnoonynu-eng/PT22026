"""
Evaluation script for the Resume Optimization System.

This script performs:
1. Skill extraction evaluation using manually labelled examples.
2. Candidate skill-match checks against expected results.
3. Fake-job detector checks using rule-based test examples.
4. Precision, Recall and F1-score calculations.
5. CSV export of the evaluation results.

Note:
These are small functional tests, not a large real-world benchmark.
"""

import csv
from model_utils import analyze_match, extract_skills
from nlp_features import detect_fake_job


def calculate_metrics(true_positive, false_positive, false_negative):
    precision = (
        true_positive / (true_positive + false_positive)
        if true_positive + false_positive else 0.0
    )
    recall = (
        true_positive / (true_positive + false_negative)
        if true_positive + false_negative else 0.0
    )
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall else 0.0
    )

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4)
    }


def evaluate_skill_extraction():
    print("\n" + "=" * 75)
    print("SKILL EXTRACTION EVALUATION")
    print("=" * 75)

    # Gold labels are manually specified for these test examples.
    test_cases = [
        {
            "name": "Software Developer",
            "text": "Python, SQL, Django, AWS and Machine Learning",
            "gold": {"python", "sql", "django", "aws", "machine learning"}
        },
        {
            "name": "Frontend Developer",
            "text": "HTML, CSS, React, JavaScript and basic Python",
            "gold": {"html", "css", "react", "javascript", "python"}
        },
        {
            "name": "Data Analyst",
            "text": "Python, pandas, numpy, Excel and Power BI",
            "gold": {"python", "pandas", "numpy", "excel", "power bi"}
        },
        {
            "name": "Unrelated Profile",
            "text": "Laundry supervisor with fabric sorting and hygiene experience",
            "gold": set()
        },
        {
            "name": "Cloud Developer",
            "text": "Docker, Kubernetes, Linux, AWS and Git",
            "gold": {"docker", "kubernetes", "linux", "aws", "git"}
        }
    ]

    tp = fp = fn = 0
    rows = []

    for case in test_cases:
        predicted = set(extract_skills(case["text"]))
        gold = case["gold"]

        case_tp = len(predicted & gold)
        case_fp = len(predicted - gold)
        case_fn = len(gold - predicted)

        tp += case_tp
        fp += case_fp
        fn += case_fn

        rows.append({
            "Test Type": "Skill Extraction",
            "Test Name": case["name"],
            "Expected": ", ".join(sorted(gold)) or "None",
            "Predicted": ", ".join(sorted(predicted)) or "None",
            "Score": "",
            "Level": "",
            "Result": "PASS" if predicted == gold else "CHECK"
        })

        print(f"\n{case['name']}")
        print(f"Expected:  {sorted(gold)}")
        print(f"Predicted: {sorted(predicted)}")
        print("Result:", "PASS" if predicted == gold else "CHECK")

    metrics = calculate_metrics(tp, fp, fn)

    print("\nSkill Extraction Metrics")
    print("-" * 45)
    print(f"True Positives : {tp}")
    print(f"False Positives: {fp}")
    print(f"False Negatives: {fn}")
    print(f"Precision      : {metrics['precision']:.4f}")
    print(f"Recall         : {metrics['recall']:.4f}")
    print(f"F1-score       : {metrics['f1']:.4f}")

    return metrics, rows


def evaluate_candidate_matching():
    print("\n" + "=" * 75)
    print("CV AND JOB DESCRIPTION MATCHING TEST")
    print("=" * 75)

    job_description = (
        "We need a Python Developer with expertise in "
        "Python, SQL, Django, AWS, and Machine Learning."
    )

    cases = [
        {
            "name": "Candidate A - Strong Skill Match",
            "cv": (
                "Python Developer with Python, SQL, Django, AWS "
                "and Machine Learning experience."
            ),
            "expected_matched": {
                "python", "sql", "django", "aws", "machine learning"
            },
            "expected_missing": set()
        },
        {
            "name": "Candidate B - Partial Skill Match",
            "cv": (
                "Frontend Developer with HTML, CSS, React, "
                "JavaScript and basic Python knowledge."
            ),
            "expected_matched": {"python"},
            "expected_missing": {"sql", "django", "aws", "machine learning"}
        },
        {
            "name": "Candidate C - Low Skill Match",
            "cv": (
                "Laundry Supervisor with experience in fabric "
                "sorting, ironing and hygiene management."
            ),
            "expected_matched": set(),
            "expected_missing": {
                "python", "sql", "django", "aws", "machine learning"
            }
        }
    ]

    rows = []

    for case in cases:
        result = analyze_match(case["cv"], job_description)

        actual_matched = set(result["matched"])
        actual_missing = set(result["missing"])

        matched_ok = actual_matched == case["expected_matched"]
        missing_ok = actual_missing == case["expected_missing"]
        test_status = "PASS" if matched_ok and missing_ok else "CHECK"

        print(f"\n{case['name']}")
        print(f"Match Score: {result['score']}%")
        print(f"Match Level: {result['level']}")
        print(f"Matched Skills: {sorted(actual_matched)}")
        print(f"Missing Skills: {sorted(actual_missing)}")
        print(f"Expected Skill Check: {test_status}")

        rows.append({
            "Test Type": "Candidate Matching",
            "Test Name": case["name"],
            "Expected": ", ".join(sorted(case["expected_matched"])) or "None",
            "Predicted": ", ".join(sorted(actual_matched)) or "None",
            "Score": result["score"],
            "Level": result["level"],
            "Result": test_status
        })

    return rows


def evaluate_fake_job_detector():
    print("\n" + "=" * 75)
    print("FAKE JOB DETECTOR EVALUATION")
    print("=" * 75)

    test_cases = [
        {
            "name": "Registration Fee Request",
            "text": "Pay a registration fee before joining this job.",
            "expected": 1
        },
        {
            "name": "Suspicious Payment Method",
            "text": "Send the payment through Western Union to get hired.",
            "expected": 1
        },
        {
            "name": "Crypto Job Offer",
            "text": "Pay a deposit in Bitcoin to receive your job offer.",
            "expected": 1
        },
        {
            "name": "Suspicious Messaging Recruitment",
            "text": "Contact our recruiter on WhatsApp for an easy money offer.",
            "expected": 1
        },
        {
            "name": "Normal Company Application",
            "text": "Apply through our official company careers page. "
                    "The role requires Python and SQL experience.",
            "expected": 0
        },
        {
            "name": "Normal Technical Job",
            "text": "We are hiring a software developer. "
                    "Please submit your CV and attend a technical interview.",
            "expected": 0
        },
        {
            "name": "Normal Internship",
            "text": "The internship includes training, project work "
                    "and an interview with the engineering team.",
            "expected": 0
        },
        {
            "name": "Normal Data Analyst Vacancy",
            "text": "Candidates should have experience with Excel, SQL "
                    "and data analysis. Apply on the company website.",
            "expected": 0
        }
    ]

    tp = fp = fn = tn = 0
    rows = []

    for case in test_cases:
        output = detect_fake_job(case["text"])
        predicted = 1 if "Potential Red Flags Detected" in output else 0
        expected = case["expected"]

        if expected == 1 and predicted == 1:
            tp += 1
        elif expected == 0 and predicted == 1:
            fp += 1
        elif expected == 1 and predicted == 0:
            fn += 1
        else:
            tn += 1

        status = "PASS" if predicted == expected else "CHECK"

        print(f"\n{case['name']}")
        print(f"Expected: {'Suspicious' if expected else 'Normal'}")
        print(f"Predicted: {'Suspicious' if predicted else 'No red flags found'}")
        print(f"Result: {status}")

        rows.append({
            "Test Type": "Fake Job Detector",
            "Test Name": case["name"],
            "Expected": expected,
            "Predicted": predicted,
            "Score": "",
            "Level": "",
            "Result": status
        })

    metrics = calculate_metrics(tp, fp, fn)

    accuracy = (
        (tp + tn) / (tp + tn + fp + fn)
        if tp + tn + fp + fn else 0.0
    )

    print("\nFake Job Detector Metrics")
    print("-" * 45)
    print(f"True Positives : {tp}")
    print(f"False Positives: {fp}")
    print(f"False Negatives: {fn}")
    print(f"True Negatives : {tn}")
    print(f"Accuracy       : {accuracy:.4f}")
    print(f"Precision      : {metrics['precision']:.4f}")
    print(f"Recall         : {metrics['recall']:.4f}")
    print(f"F1-score       : {metrics['f1']:.4f}")

    return metrics, rows


def save_results(rows):
    filename = "evaluation_results.csv"
    fieldnames = [
        "Test Type", "Test Name", "Expected",
        "Predicted", "Score", "Level", "Result"
    ]

    with open(filename, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nDetailed results saved to: {filename}")


def run_evaluation():
    print("\nRESUME OPTIMIZATION SYSTEM - MODEL EVALUATION")

    skill_metrics, skill_rows = evaluate_skill_extraction()
    candidate_rows = evaluate_candidate_matching()
    fake_metrics, fake_rows = evaluate_fake_job_detector()

    all_rows = skill_rows + candidate_rows + fake_rows
    save_results(all_rows)

    print("\n" + "=" * 75)
    print("EVALUATION SUMMARY")
    print("=" * 75)
    print(
        "Skill Extraction - "
        f"Precision: {skill_metrics['precision']:.4f}, "
        f"Recall: {skill_metrics['recall']:.4f}, "
        f"F1: {skill_metrics['f1']:.4f}"
    )
    print(
        "Fake Job Detector - "
        f"Precision: {fake_metrics['precision']:.4f}, "
        f"Recall: {fake_metrics['recall']:.4f}, "
        f"F1: {fake_metrics['f1']:.4f}"
    )
    print("\nEvaluation completed.")
    print(
        "These results describe only the included test examples. "
        "They are not a measure of performance on all real-world CVs or job posts."
    )


if __name__ == "__main__":
    run_evaluation()