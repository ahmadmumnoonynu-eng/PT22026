# Draw the evaluation graphs from the CSV files written by evaluate.py.
# Usage: python plot_results.py

import csv
import os
import sys

import matplotlib

# Save images without opening a window, so it also works over a terminal
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROBERTA_FILE = "eval/results.csv"
DISTILBERT_FILE = "eval/results_distilbert.csv"
FIGURE_DIR = "eval/figures"

RULES = ["retrieval_first", "qa_prob", "qa_logit", "retrieval_x_prob", "logit_plus_retrieval"]
RULE_LABELS = {
    "retrieval_first": "first retrieved chunk",
    "qa_prob": "QA probability",
    "qa_logit": "QA raw score",
    "retrieval_x_prob": "retrieval x probability",
    "logit_plus_retrieval": "raw score + retrieval (app rule)",
}


def read_rows(path):
    # Read a results file and turn every number into a float
    if not os.path.exists(path):
        sys.exit(f"File not found: {path}. Run evaluate.py first.")
    with open(path, encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    for row in rows:
        for key, value in row.items():
            row[key] = float(value)
    return rows


def pick(rows, chunk_size):
    # Keep only the rows of one chunk size, ordered by top_k
    chosen = [row for row in rows if row["chunk_size"] == chunk_size]
    return sorted(chosen, key=lambda row: row["top_k"])


def plot_recall(rows, chunk_sizes):
    # Graph 1: how often the right sentence is inside the retrieved chunks
    plt.figure(figsize=(6, 4))
    for size in chunk_sizes:
        data = pick(rows, size)
        plt.plot([r["top_k"] for r in data], [r["recall"] for r in data],
                 marker="o", label=f"chunk size {int(size)}")
    plt.xlabel("Chunks retrieved (top-k)")
    plt.ylabel("Recall")
    plt.title("Retrieval recall")
    plt.xticks([1, 3, 5])
    plt.ylim(0, 1.05)
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{FIGURE_DIR}/recall_vs_topk.png", dpi=150)
    plt.close()


def plot_rules(rows, chunk_sizes):
    # Graph 2: accuracy of every ranking rule, one panel per chunk size
    figure, axes = plt.subplots(1, len(chunk_sizes), figsize=(5 * len(chunk_sizes), 4), sharey=True)
    for axis, size in zip(axes, chunk_sizes):
        data = pick(rows, size)
        for rule in RULES:
            if rule in data[0]:
                axis.plot([r["top_k"] for r in data], [r[rule] for r in data],
                          marker="o", label=RULE_LABELS[rule])
        axis.set_title(f"chunk size {int(size)}")
        axis.set_xlabel("Chunks retrieved (top-k)")
        axis.set_xticks([1, 3, 5])
        axis.set_ylim(0, 1.05)
        axis.grid(alpha=0.3)
    axes[0].set_ylabel("Answer accuracy")
    axes[-1].legend(fontsize=7, loc="lower right")
    figure.suptitle("Ranking rules (RoBERTa)")
    figure.tight_layout()
    figure.savefig(f"{FIGURE_DIR}/ranking_rules.png", dpi=150)
    plt.close(figure)


def plot_models(roberta, distilbert):
    # Graph 3: the two QA models side by side with the same ranking rule
    keys = [(r["chunk_size"], r["top_k"]) for r in roberta]
    labels = [f"{int(size)}/{int(k)}" for size, k in keys]
    by_key = {(r["chunk_size"], r["top_k"]): r for r in distilbert}
    positions = range(len(keys))
    width = 0.4

    plt.figure(figsize=(8, 4))
    plt.bar([p - width / 2 for p in positions], [by_key[k]["qa_logit"] for k in keys],
            width, label="DistilBERT")
    plt.bar([p + width / 2 for p in positions], [r["qa_logit"] for r in roberta],
            width, label="RoBERTa")
    plt.xticks(list(positions), labels)
    plt.xlabel("chunk size / top-k")
    plt.ylabel("Answer accuracy (raw score rule)")
    plt.title("DistilBERT vs RoBERTa")
    plt.ylim(0, 1.05)
    plt.grid(axis="y", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{FIGURE_DIR}/model_comparison.png", dpi=150)
    plt.close()


def main():
    os.makedirs(FIGURE_DIR, exist_ok=True)
    roberta = read_rows(ROBERTA_FILE)
    distilbert = read_rows(DISTILBERT_FILE)
    chunk_sizes = sorted({row["chunk_size"] for row in roberta})

    plot_recall(roberta, chunk_sizes)
    plot_rules(roberta, chunk_sizes)
    plot_models(roberta, distilbert)
    print(f"Saved 3 figures to {FIGURE_DIR}")


if __name__ == "__main__":
    main()
