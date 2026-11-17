"""Entity-level evaluation (seqeval) of BERT NER and spaCy on a CoNLL-2003 test sample.

Usage (from the ask084 folder):  python -m src.evaluate 500
"""
import os
if os.environ.get("NER_OFFLINE") == "1":
    os.environ["HF_HUB_OFFLINE"] = "1"

import json
import random
import sys
import time

import spacy
from spacy.tokens import Doc
from seqeval.metrics import classification_report, f1_score, precision_score, recall_score
from seqeval.metrics.sequence_labeling import get_entities

from src.arena import SPACY_MAP
from src.inference import get_ner

N = int(sys.argv[1]) if len(sys.argv) > 1 else 500
TAGS = ["O", "B-PER", "I-PER", "B-ORG", "I-ORG", "B-LOC", "I-LOC", "B-MISC", "I-MISC"]

rows = [json.loads(line) for line in open("data/conll2003_test.jsonl", encoding="utf-8")]
random.Random(42).shuffle(rows)
rows = rows[:N]
print(f"Evaluating on {len(rows)} test sentences")


def bert_tags(tokens):
    """Run the BERT pipeline on the joined sentence and map entities back to word tags."""
    text = " ".join(tokens)
    offsets, pos = [], 0
    for t in tokens:
        offsets.append((pos, pos + len(t)))
        pos += len(t) + 1
    tags = ["O"] * len(tokens)
    for ent in get_ner()(text):
        idx = [i for i, (s, e) in enumerate(offsets) if s < ent["end"] and e > ent["start"]]
        for k, i in enumerate(idx):
            tags[i] = ("B-" if k == 0 else "I-") + ent["entity_group"]
    return tags


nlp = spacy.load("en_core_web_sm")


def spacy_tags(tokens):
    """Run spaCy on the gold tokenization so tags line up word by word."""
    doc = nlp(Doc(nlp.vocab, words=tokens))
    tags = []
    for tok in doc:
        label = SPACY_MAP.get(tok.ent_type_) if tok.ent_iob_ != "O" else None
        if label is None:
            tags.append("O")
        else:
            tags.append(("I-" if tok.ent_iob_ == "I" else "B-") + label)
    return tags


gold = [[TAGS[i] for i in r["ner_tags"]] for r in rows]
models = {"BERT (dslim/bert-base-NER)": bert_tags, "spaCy en_core_web_sm (mapped labels)": spacy_tags}
preds, results = {}, {}

for name, fn in models.items():
    start = time.time()
    preds[name] = [fn(r["tokens"]) for r in rows]
    rep = classification_report(gold, preds[name], output_dict=True)
    results[name] = {
        "precision": precision_score(gold, preds[name]),
        "recall": recall_score(gold, preds[name]),
        "f1": f1_score(gold, preds[name]),
        "per_class": {k: rep[k] for k in ["PER", "ORG", "LOC", "MISC"]},
    }
    print(f"\n=== {name}  ({time.time() - start:.0f}s) ===")
    print(classification_report(gold, preds[name], digits=3))

# --- results table for the report ---
os.makedirs("docs", exist_ok=True)
lines = [f"# Results on {len(rows)} random CoNLL-2003 test sentences (seed 42)", "",
         "| Model | Precision | Recall | F1 |", "|---|---|---|---|"]
for name, r in results.items():
    lines.append(f"| {name} | {r['precision']:.3f} | {r['recall']:.3f} | {r['f1']:.3f} |")
lines += ["", "## Per-entity F1", "", "| Model | PER | ORG | LOC | MISC |", "|---|---|---|---|---|"]
for name, r in results.items():
    f = [r["per_class"][c]["f1-score"] for c in ["PER", "ORG", "LOC", "MISC"]]
    lines.append(f"| {name} | " + " | ".join(f"{x:.3f}" for x in f) + " |")
open("docs/results.md", "w", encoding="utf-8").write("\n".join(lines) + "\n")

# --- error dump: first 40 sentences where BERT differs from the gold labels ---
bert_name = "BERT (dslim/bert-base-NER)"


def fmt(tokens, tags):
    return " | ".join(f"{' '.join(tokens[s:e + 1])} [{t}]" for t, s, e in get_entities(tags)) or "(none)"


with open("docs/error_dump.txt", "w", encoding="utf-8") as f:
    shown = 0
    for r, g, p in zip(rows, gold, preds[bert_name]):
        if g != p and shown < 40:
            f.write("SENT: " + " ".join(r["tokens"]) + "\n")
            f.write("GOLD: " + fmt(r["tokens"], g) + "\n")
            f.write("BERT: " + fmt(r["tokens"], p) + "\n\n")
            shown += 1
print("\nSaved docs/results.md and docs/error_dump.txt")