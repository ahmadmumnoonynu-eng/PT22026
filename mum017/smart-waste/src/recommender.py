"""Turns model predictions into recycling advice.

This is the "smart" layer on top of the classifier. It decides:
  1. how confident we are (HIGH / MEDIUM / LOW tier),
  2. which knowledge-base entry matches the predicted label,
  3. whether the top two predictions form a commonly confused pair.
"""

import json
from typing import Dict, List, Tuple

from src.config import (
    CONFUSION_MIN_SECOND,
    HIGH_CONFIDENCE,
    KNOWLEDGE_BASE_PATH,
    MEDIUM_CONFIDENCE,
)

# The model card spells one class "Brown-grass" but the original dataset class
# is brown glass. Aliases let both spellings reach the same advice.
LABEL_ALIASES = {
    "brown-grass": "brown-glass",
}

# Pairs the model (and people) often mix up. Order does not matter.
CONFUSABLE_PAIRS = [
    {"green-glass", "white-glass"},
    {"green-glass", "brown-glass"},
    {"white-glass", "brown-glass"},
    {"cardboard", "paper"},
    {"plastic", "trash"},
    {"clothes", "shoes"},
    {"metal", "trash"},
]

# White glass has no separate entry of its own wording, so it reuses a template.
_FALLBACK_ENTRY = {
    "display_name": "Unknown item",
    "category": "Unknown",
    "bin": "Check local waste guidance",
    "prepare": ["Check the item for recycling symbols or markings."],
    "dispose": "No specific guidance is stored for this category. Please check your local recycling rules.",
    "avoid": [],
    "tip": "Try a clearer photo of a single item on a plain background.",
    "environment": "Sorting waste correctly helps materials get reused instead of landfilled.",
}


def normalize_label(label: str) -> str:
    """'Green_Glass' / 'green glass' / 'Green-Glass' -> 'green-glass'."""
    key = label.strip().lower().replace("_", "-").replace(" ", "-")
    return LABEL_ALIASES.get(key, key)


def load_knowledge_base(path=KNOWLEDGE_BASE_PATH) -> Dict[str, dict]:
    """Read the JSON file and key every entry by its normalised label."""
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    kb = {normalize_label(k): v for k, v in raw.items() if not k.startswith("_")}
    # White glass shares guidance with the other glass colours.
    if "white-glass" not in kb and "green-glass" in kb:
        entry = dict(kb["green-glass"])
        entry["display_name"] = "White / clear glass"
        entry["bin"] = "Glass recycling (clear / mixed glass bank)"
        entry["dispose"] = (
            "Place in the glass bank or glass bin. Where colours are separated, use the clear section."
        )
        entry["tip"] = "Clear glass is the most valuable colour to recycle, so keep it free of other colours."
        kb["white-glass"] = entry
    return kb


def confidence_tier(probability: float) -> str:
    """Map the top probability to 'high', 'medium' or 'low'."""
    if probability >= HIGH_CONFIDENCE:
        return "high"
    if probability >= MEDIUM_CONFIDENCE:
        return "medium"
    return "low"


def find_confusion_warning(predictions: List[Tuple[str, float]]) -> str:
    """Warn if the top two predictions are a commonly confused pair."""
    if len(predictions) < 2:
        return ""
    (first, _), (second, p2) = predictions[0], predictions[1]
    pair = {normalize_label(first), normalize_label(second)}
    if p2 >= CONFUSION_MIN_SECOND and pair in CONFUSABLE_PAIRS:
        return (
            f"'{first}' and '{second}' are easy to mix up. "
            "Check the item yourself before choosing a bin."
        )
    return ""


def build_recommendation(predictions: List[Tuple[str, float]], kb: Dict[str, dict]) -> dict:
    """Combine predictions + knowledge base into one result dictionary."""
    if not predictions:
        raise ValueError("predictions must not be empty")

    top_label, top_prob = predictions[0]
    tier = confidence_tier(top_prob)
    entry = kb.get(normalize_label(top_label), _FALLBACK_ENTRY)

    return {
        "label": top_label,
        "probability": top_prob,
        "tier": tier,
        "entry": entry,
        "confusion_warning": find_confusion_warning(predictions),
        # Low confidence -> do not present advice as if it were certain.
        "show_advice": tier != "low",
    }


def to_markdown(rec: dict) -> str:
    """Format a recommendation as Markdown for the Gradio interface."""
    e = rec["entry"]
    pct = rec["probability"] * 100
    tier = rec["tier"]
    badge = {
        "high": "🟢 High confidence",
        "medium": "🟡 Medium confidence",
        "low": "🔴 Low confidence",
    }[tier]

    lines = [f"## {e['display_name']}", f"**{badge}** — {pct:.1f}%", ""]

    if tier == "low":
        lines += [
            "⚠️ **The model is not sure about this image.** "
            "Try a clearer photo of a single item on a plain background. "
            f"Best guess: *{e['display_name']}*.",
        ]
        if rec["confusion_warning"]:
            lines += ["", f"ℹ️ {rec['confusion_warning']}"]
        return "\n".join(lines)

    if tier == "medium":
        lines += ["🟡 *Please double-check that this matches your item.*", ""]
    if rec["confusion_warning"]:
        lines += [f"ℹ️ {rec['confusion_warning']}", ""]

    lines += [
        f"**Category:** {e['category']}",
        f"**Which bin:** {e['bin']}",
        "",
        "### ♻️ How to prepare it",
        *[f"- {step}" for step in e["prepare"]],
        "",
        "### 🗑️ Disposal guidance",
        e["dispose"],
    ]
    if e["avoid"]:
        lines += ["", "### 🚫 Please avoid", *[f"- {a}" for a in e["avoid"]]]
    lines += [
        "",
        "### 💡 Tip",
        e["tip"],
        "",
        "### 🌍 Environmental note",
        e["environment"],
        "",
        "---",
        "*General guidance only. Recycling rules vary by location, so check your local council's rules.*",
    ]
    return "\n".join(lines)
