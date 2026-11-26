"""Unit tests that run WITHOUT downloading the model.

Run from the project root:   pytest -v
"""

import pytest
from PIL import Image

from src.recommender import (
    build_recommendation,
    confidence_tier,
    find_confusion_warning,
    load_knowledge_base,
    normalize_label,
    to_markdown,
)
from src.validation import InvalidImageError, validate_image

KB = load_knowledge_base()

# The 12 labels listed on the model card. Spelling of the model's own config may differ,
# which normalize_label handles.
CARD_LABELS = [
    "Battery", "Biological", "Brown-grass", "Cardboard", "Clothes", "Green-Glass",
    "Metal", "Paper", "Plastic", "Shoes", "Trash", "White-Glass",
]


# ---------- validation ----------
def test_none_image_rejected():
    with pytest.raises(InvalidImageError):
        validate_image(None)


def test_non_image_rejected():
    with pytest.raises(InvalidImageError):
        validate_image("not an image")


def test_tiny_image_rejected():
    with pytest.raises(InvalidImageError):
        validate_image(Image.new("RGB", (10, 10)))


def test_rgba_and_grey_converted_to_rgb():
    assert validate_image(Image.new("RGBA", (64, 64))).mode == "RGB"
    assert validate_image(Image.new("L", (64, 64))).mode == "RGB"


# ---------- recommender ----------
@pytest.mark.parametrize("p,expected", [(0.95, "high"), (0.80, "high"), (0.65, "medium"),
                                        (0.50, "medium"), (0.49, "low"), (0.10, "low")])
def test_confidence_tiers(p, expected):
    assert confidence_tier(p) == expected


@pytest.mark.parametrize("label", CARD_LABELS)
def test_every_model_card_label_has_advice(label):
    assert normalize_label(label) in KB


def test_normalize_label_variants():
    assert normalize_label("Green_Glass") == "green-glass"
    assert normalize_label(" green glass ") == "green-glass"
    assert normalize_label("Brown-grass") == "brown-glass"


def test_unknown_label_uses_fallback():
    rec = build_recommendation([("Spaceship", 0.9)], KB)
    assert rec["entry"]["display_name"] == "Unknown item"


def test_low_confidence_hides_advice():
    rec = build_recommendation([("Plastic", 0.30), ("Trash", 0.2), ("Metal", 0.1)], KB)
    assert rec["tier"] == "low" and rec["show_advice"] is False
    assert "not sure" in to_markdown(rec)


def test_high_confidence_shows_advice():
    rec = build_recommendation([("Metal", 0.97), ("Trash", 0.02), ("Plastic", 0.01)], KB)
    text = to_markdown(rec)
    assert "Disposal guidance" in text and "double-check" not in text


def test_medium_confidence_adds_double_check():
    rec = build_recommendation([("Paper", 0.6), ("Cardboard", 0.3), ("Trash", 0.1)], KB)
    assert "double-check" in to_markdown(rec)


def test_confusion_warning_for_known_pair():
    assert find_confusion_warning([("Paper", 0.5), ("Cardboard", 0.4)])
    assert not find_confusion_warning([("Paper", 0.9), ("Cardboard", 0.05)])
    assert not find_confusion_warning([("Paper", 0.5), ("Battery", 0.4)])


def test_empty_predictions_raise():
    with pytest.raises(ValueError):
        build_recommendation([], KB)
