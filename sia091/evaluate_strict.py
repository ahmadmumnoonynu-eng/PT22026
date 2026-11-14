# Strict evaluation with SQuAD-style exact match and token F1.
# Usage: python evaluate_strict.py <document> <eval set json>
# It runs the same pipeline and settings as app.py and never changes them.

import json
import re
import string
import sys
from collections import Counter

from src.answerer import Answerer
from src.chunker import chunk_pages
from src.embedder import Embedder
from src.loader import load_document
from src.retriever import Retriever

CHUNK_SIZE = 40
OVERLAP = 10
TOP_K = 5


def normalise_answer(text):
    # Same steps as the official SQuAD script: lower case, no punctuation, no articles
    text = text.lower()
    punctuation = set(string.punctuation)
    text = "".join(ch for ch in text if ch not in punctuation)
    text = re.sub(r"\b(a|an|the)\b", " ", text)
    return " ".join(text.split())


def exact_match(prediction, gold):
    # 1 only if both answers are identical after normalising
    return normalise_answer(prediction) == normalise_answer(gold)


def token_f1(prediction, gold):
    # Share of words that both answers have in common, between 0 and 1
    pred_tokens = normalise_answer(prediction).split()
    gold_tokens = normalise_answer(gold).split()
    same = sum((Counter(pred_tokens) & Counter(gold_tokens)).values())
    if same == 0:
        return 0.0
    precision = same / len(pred_tokens)
    recall = same / len(gold_tokens)
    return 2 * precision * recall / (precision + recall)


def loose_correct(prediction, gold):
    # The softer rule used in evaluate.py: gold inside the prediction,
    # or every word of the prediction inside the gold answer
    pred = " ".join(prediction.lower().split())
    ref = " ".join(gold.lower().split())
    if not pred:
        return False
    return ref in pred or set(pred.split()) <= set(ref.split())


def main():
    if len(sys.argv) < 3:
        sys.exit("Usage: python evaluate_strict.py <document> <eval set json>")
    document, eval_path = sys.argv[1], sys.argv[2]

    pages = load_document(document)
    # Used to skip questions whose answer is not in this copy of the document
    document_text = normalise_answer(" ".join(text for _, text in pages))

    retriever = Retriever(Embedder())
    retriever.build(chunk_pages(pages, CHUNK_SIZE, OVERLAP))
    answerer = Answerer()

    with open(eval_path, encoding="utf-8") as file:
        items = json.load(file)

    asked = skipped = loose = exact = 0
    f1_total = 0.0
    for item in items:
        if normalise_answer(item["answer"]) not in document_text:
            skipped += 1
            continue
        asked += 1
        hits = retriever.search(item["question"], TOP_K)
        prediction = answerer.answer(item["question"], hits)["answer"]

        loose += loose_correct(prediction, item["answer"])
        exact += exact_match(prediction, item["answer"])
        f1 = token_f1(prediction, item["answer"])
        f1_total += f1
        if not exact_match(prediction, item["answer"]):
            print(f"NOT EXACT (F1 {f1:.2f}): {item['question']}")
            print(f"    gold: {item['answer'][:50]} | model: {prediction[:50]}")

    name = eval_path.split("/")[-1]
    print(f"RESULT {name} | questions {asked} (skipped {skipped}) | loose {loose} | "
          f"exact match {exact} ({exact / asked:.2f}) | F1 {f1_total / asked:.2f}")


if __name__ == "__main__":
    main()
