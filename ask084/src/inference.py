"""Model loading and prediction helpers for the NER app."""
from functools import lru_cache
from transformers import pipeline

MODEL_NAME = "dslim/bert-base-NER"


@lru_cache(maxsize=1)
def get_ner():
    """Load the model once and reuse it for every request."""
    return pipeline("ner", model=MODEL_NAME, aggregation_strategy="simple")


def predict(text):
    """Return a list of entities: label, text, confidence score, character span."""
    results = get_ner()(text)
    return [
        {
            "label": r["entity_group"],
            "text": text[r["start"]:r["end"]],
            "score": float(r["score"]),
            "start": int(r["start"]),
            "end": int(r["end"]),
        }
        for r in results
    ]