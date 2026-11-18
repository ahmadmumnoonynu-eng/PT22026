"""Model arena: compare the BERT NER model with spaCy on the same text."""
from functools import lru_cache

import spacy

from src.inference import predict

# spaCy uses OntoNotes labels; map them onto the 4 CoNLL labels.
# Labels with no CoNLL equivalent (DATE, MONEY, CARDINAL, ...) are ignored.
SPACY_MAP = {
    "PERSON": "PER",
    "ORG": "ORG",
    "GPE": "LOC", "LOC": "LOC", "FAC": "LOC",
    "NORP": "MISC", "EVENT": "MISC", "LANGUAGE": "MISC",
    "WORK_OF_ART": "MISC", "PRODUCT": "MISC", "LAW": "MISC",
}


@lru_cache(maxsize=1)
def get_spacy():
    return spacy.load("en_core_web_sm")


def predict_spacy(text):
    doc = get_spacy()(text)
    out = []
    for ent in doc.ents:
        label = SPACY_MAP.get(ent.label_)
        if label:
            out.append({"label": label, "text": ent.text,
                        "start": ent.start_char, "end": ent.end_char})
    return out


def to_segments(text, entities):
    """Convert entities into (text, label) segments for gr.HighlightedText."""
    segments, pos = [], 0
    for e in sorted(entities, key=lambda e: e["start"]):
        if e["start"] < pos:
            continue
        if e["start"] > pos:
            segments.append((text[pos:e["start"]], None))
        segments.append((text[e["start"]:e["end"]], e["label"]))
        pos = e["end"]
    if pos < len(text):
        segments.append((text[pos:], None))
    return segments


def _overlaps(a, others):
    return any(a["start"] < o["end"] and o["start"] < a["end"] for o in others)


def compare(text, threshold=0.5):
    """Return BERT entities, spaCy entities and a comparison table."""
    bert = [e for e in predict(text) if e["score"] >= threshold]
    sp = predict_spacy(text)
    b = {(e["start"], e["end"]): e for e in bert}
    s = {(e["start"], e["end"]): e for e in sp}

    rows = []
    for span in sorted(set(b) | set(s)):
        eb, es = b.get(span), s.get(span)
        if eb and es:
            status = "Agree" if eb["label"] == es["label"] else "Label conflict"
        elif eb:
            status = "Boundary conflict" if _overlaps(eb, sp) else "Only BERT"
        else:
            status = "Boundary conflict" if _overlaps(es, bert) else "Only spaCy"
        shown = (eb or es)["text"]
        rows.append([shown, eb["label"] if eb else "-", es["label"] if es else "-", status])
    return bert, sp, rows