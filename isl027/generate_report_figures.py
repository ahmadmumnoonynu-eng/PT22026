from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Ellipse, Circle

OUT = Path("report_figures")
OUT.mkdir(exist_ok=True)

NAVY = "#243B53"
BLUE = "#477B9C"
TEAL = "#438F89"
GOLD = "#C28B3C"
GREY = "#667788"
LIGHT_BLUE = "#EAF2F7"
LIGHT_TEAL = "#E8F3F0"
LIGHT_GOLD = "#F8F0E2"
LIGHT_GREY = "#F1F3F5"
WHITE = "#FFFFFF"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 9,
    "figure.facecolor": WHITE,
    "savefig.facecolor": WHITE
})


def canvas(title, subtitle):
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    ax.text(4, 95, title, fontsize=18, weight="bold",
            color=NAVY, va="top")
    ax.text(4, 89, subtitle, fontsize=9, color=GREY, va="top")
    return fig, ax


def box(ax, x, y, w, h, title, detail="",
        face=LIGHT_BLUE, edge=BLUE, size=9):
    p = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.5,rounding_size=1.5",
        linewidth=1.4, edgecolor=edge, facecolor=face
    )
    ax.add_patch(p)
    if detail:
        ax.text(x+w/2, y+h*0.62, title, ha="center",
                va="center", fontsize=size, weight="bold",
                color=NAVY, wrap=True)
        ax.text(x+w/2, y+h*0.29, detail, ha="center",
                va="center", fontsize=7.2, color=GREY,
                wrap=True)
    else:
        ax.text(x+w/2, y+h/2, title, ha="center",
                va="center", fontsize=size, weight="bold",
                color=NAVY, wrap=True)


def arrow(ax, start, end, color=GREY, rad=0):
    ax.add_patch(FancyArrowPatch(
        start, end, arrowstyle="-|>", mutation_scale=12,
        linewidth=1.35, color=color,
        connectionstyle=f"arc3,rad={rad}",
        shrinkA=2, shrinkB=2
    ))


def save(fig, name):
    fig.savefig(OUT / name, dpi=300, bbox_inches="tight",
                pad_inches=0.25)
    fig.savefig(OUT / name.replace(".png", ".svg"),
                bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)
    print("Created:", OUT / name)


# FIGURE 1: SYSTEM ARCHITECTURE

def architecture():
    fig, ax = canvas(
        "System Architecture",
        "Logical architecture of the Resume Optimization System"
    )

    layers = [
        (75, "USER INTERFACE",
         ["Resume Analyzer", "Cover Letter Generator", "Recruiter Mode"],
         LIGHT_BLUE, BLUE),
        (59, "APPLICATION LOGIC",
         ["Input Handling", "PDF Text Extraction",
          "Analysis Coordination", "Candidate Comparison"],
         LIGHT_TEAL, TEAL),
        (43, "NLP AND ANALYSIS",
         ["Text Processing", "Skill Extraction",
          "Sentence Transformer", "Similarity and Skill Scoring"],
         LIGHT_GOLD, GOLD),
        (27, "RESULTS AND SUPPORT",
         ["Match Score and Skill Gap", "ATS-related Checks",
          "Job Warning Indicators", "Cover Letter and Suggestions"],
         LIGHT_GREY, GREY),
        (11, "EVALUATION",
         ["Prepared Test Cases", "Expected / Predicted Comparison",
          "Evaluation Results"],
         LIGHT_BLUE, BLUE)
    ]

    for y, label, items, face, edge in layers:
        ax.text(5, y+8, label, fontsize=9,
                weight="bold", color=edge)
        gap = 1.5
        w = (90-gap*(len(items)-1))/len(items)
        for i, item in enumerate(items):
            box(ax, 5+i*(w+gap), y-5, w, 9,
                item, face=face, edge=edge, size=7.4)

    for y in [75, 59, 43, 27]:
        arrow(ax, (50, y-6), (50, y-10))

    save(fig, "figure_01_system_architecture.png")


# FIGURE 2: RESUME ANALYSIS PROCESS

def analysis_process():
    fig, ax = canvas(
        "Resume Analysis Process",
        "Processing stages used to compare a CV with a job description"
    )

    box(ax, 5, 72, 40, 11, "CV INPUT",
        "Pasted text or text-based PDF", LIGHT_BLUE, BLUE)
    box(ax, 55, 72, 40, 11, "JOB DESCRIPTION",
        "Required role and skills", LIGHT_TEAL, TEAL)

    box(ax, 5, 54, 40, 10, "CV TEXT PREPARATION",
        "PDF extraction when applicable; text normalization",
        LIGHT_GOLD, GOLD)
    box(ax, 55, 54, 40, 10, "JD TEXT PREPARATION",
        "Text normalization", LIGHT_GOLD, GOLD)

    arrow(ax, (25, 72), (25, 64), BLUE)
    arrow(ax, (75, 72), (75, 64), TEAL)

    box(ax, 5, 36, 40, 10, "SKILL EXTRACTION",
        "Predefined skill dictionary and regular expressions",
        LIGHT_BLUE, BLUE)
    box(ax, 55, 36, 40, 10, "SEMANTIC EMBEDDINGS",
        "Pretrained multilingual Sentence Transformer",
        LIGHT_TEAL, TEAL)

    arrow(ax, (25, 54), (25, 46), BLUE)
    arrow(ax, (75, 54), (75, 46), TEAL)

    box(ax, 5, 18, 40, 10, "SKILL MATCH RATIO",
        "Matched required skills / recognized required skills",
        LIGHT_BLUE, BLUE)
    box(ax, 55, 18, 40, 10, "SEMANTIC SIMILARITY",
        "Cosine similarity between text embeddings",
        LIGHT_TEAL, TEAL)

    arrow(ax, (25, 36), (25, 28), BLUE)
    arrow(ax, (75, 36), (75, 28), TEAL)

    box(ax, 25, 3, 50, 10, "WEIGHTED FINAL MATCH SCORE",
        "0.60 × Semantic Similarity + 0.40 × Skill Match Ratio",
        LIGHT_GOLD, GOLD)

    arrow(ax, (25, 18), (40, 13), BLUE)
    arrow(ax, (75, 18), (60, 13), TEAL)

    ax.text(50, 0,
            "The implementation uses the semantic score when no required skills are recognized.",
            ha="center", va="top", fontsize=6.5, color=GREY)

    save(fig, "figure_02_resume_analysis_process.png")


# FIGURE 3: OVERALL APPLICATION WORKFLOW

def overall_workflow():
    fig, ax = canvas(
        "Overall Application Workflow",
        "Main user journey and the three application modes"
    )

    box(ax, 34, 75, 32, 10, "OPEN APPLICATION",
        "Gradio user interface", LIGHT_BLUE, BLUE)
    box(ax, 34, 59, 32, 10, "SELECT APPLICATION MODE",
        "Choose the required function", LIGHT_GOLD, GOLD)
    arrow(ax, (50, 75), (50, 69), BLUE)

    modes = [
        (3, "RESUME ANALYZER",
         "One CV and one job description", LIGHT_BLUE, BLUE),
        (35.5, "COVER LETTER GENERATOR",
         "CV, job description and optional skills", LIGHT_TEAL, TEAL),
        (68, "RECRUITER MODE",
         "Multiple PDF CVs and one job description", LIGHT_GOLD, GOLD)
    ]

    for x, title, detail, face, edge in modes:
        box(ax, x, 39, 29, 12, title, detail, face, edge)

    arrow(ax, (50, 59), (17.5, 51), BLUE, 0.08)
    arrow(ax, (50, 59), (50, 51), TEAL)
    arrow(ax, (50, 59), (82.5, 51), GOLD, -0.08)

    outputs = [
        (3, "ANALYSIS RESULTS",
         "Score, matched and missing skills, checks", LIGHT_BLUE, BLUE),
        (35.5, "COVER LETTER DRAFT",
         "Generated from matched and optional skills", LIGHT_TEAL, TEAL),
        (68, "CANDIDATE COMPARISON",
         "Ranking table and score chart", LIGHT_GOLD, GOLD)
    ]

    for x, title, detail, face, edge in outputs:
        box(ax, x, 17, 29, 12, title, detail, face, edge)

    arrow(ax, (17.5, 39), (17.5, 29), BLUE)
    arrow(ax, (50, 39), (50, 29), TEAL)
    arrow(ax, (82.5, 39), (82.5, 29), GOLD)

    ax.text(50, 7,
            "Outputs are presented through the Gradio interface.",
            ha="center", fontsize=8, color=GREY)

    save(fig, "figure_03_overall_workflow.png")


# FIGURE 4: USE CASE DIAGRAM

def use_case():
    fig, ax = canvas(
        "Use Case Diagram",
        "Main interactions supported by the application"
    )

    boundary = FancyBboxPatch(
        (25, 12), 70, 70,
        boxstyle="round,pad=0.6,rounding_size=1.5",
        linewidth=1.5, edgecolor=BLUE, facecolor="#FAFCFD"
    )
    ax.add_patch(boundary)
    ax.text(60, 78, "Resume Optimization System",
            ha="center", fontsize=11, weight="bold", color=NAVY)

    def actor(x, y, label):
        ax.add_patch(Circle((x, y+5), 2.2, fill=False,
                            linewidth=1.5, edgecolor=NAVY))
        ax.plot([x, x], [y+2.8, y-4], color=NAVY, lw=1.5)
        ax.plot([x-4, x+4], [y, y], color=NAVY, lw=1.5)
        ax.plot([x, x-3], [y-4, y-9], color=NAVY, lw=1.5)
        ax.plot([x, x+3], [y-4, y-9], color=NAVY, lw=1.5)
        ax.text(x, y-12, label, ha="center",
                fontsize=8, weight="bold", color=NAVY)

    actor(10, 52, "Job Seeker")
    actor(10, 25, "Recruiter")

    cases = [
        (43, 64, "Analyze Resume"),
        (76, 64, "View Match Score"),
        (43, 43, "Review Skill Gaps"),
        (76, 43, "Generate Cover Letter"),
        (43, 22, "Compare Candidates"),
        (76, 22, "View Candidate Ranking")
    ]

    for x, y, label in cases:
        ax.add_patch(Ellipse(
            (x, y), 27, 10,
            linewidth=1.3, edgecolor=TEAL,
            facecolor=LIGHT_TEAL
        ))
        ax.text(x, y, label, ha="center", va="center",
                fontsize=7.5, color=NAVY)

    arrow(ax, (14, 52), (29, 64))
    arrow(ax, (14, 52), (62, 64))
    arrow(ax, (14, 52), (29, 43))
    arrow(ax, (14, 52), (62, 43))
    arrow(ax, (14, 25), (29, 22))
    arrow(ax, (14, 25), (62, 22))

    ax.text(50, 5,
            "Actors represent user roles interacting with the application.",
            ha="center", fontsize=7, color=GREY)

    save(fig, "figure_04_use_case_diagram.png")


if __name__ == "__main__":
    architecture()
    analysis_process()
    overall_workflow()
    use_case()
    print("\nAll four figures have been generated.")
    print("Output folder:", OUT.resolve())
