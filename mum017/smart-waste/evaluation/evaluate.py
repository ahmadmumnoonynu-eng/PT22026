"""Evaluate the classifier on YOUR OWN labelled test images.

Expected folder layout (one sub-folder per class, named like the class):

    evaluation/test_images/
        battery/      img1.jpg img2.jpg ...
        cardboard/    ...
        green-glass/  ...

Run from the project root:
    python evaluation/evaluate.py
    python evaluation/evaluate.py --images path/to/other_folder

Outputs (in evaluation/results/): metrics.txt, predictions.csv, confusion_matrix.png
All numbers come from running the model, nothing is hard-coded.
"""

import argparse
import csv
import sys
from pathlib import Path

# Allow "from src..." when running this file directly.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib

matplotlib.use("Agg")  # draw to files, no window needed
import matplotlib.pyplot as plt
from PIL import Image
from sklearn.metrics import classification_report, confusion_matrix

from src.classifier import WasteClassifier
from src.recommender import normalize_label
from src.validation import InvalidImageError, validate_image

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def collect_images(root: Path):
    """Return a list of (image_path, true_label_folder_name)."""
    items = []
    for class_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        for f in sorted(class_dir.iterdir()):
            if f.suffix.lower() in IMAGE_EXTENSIONS:
                items.append((f, class_dir.name))
    return items


def main():
    default_root = Path(__file__).resolve().parent / "test_images"
    parser = argparse.ArgumentParser(description="Evaluate the waste classifier")
    parser.add_argument("--images", type=Path, default=default_root)
    args = parser.parse_args()

    if not args.images.is_dir():
        sys.exit(f"Test image folder not found: {args.images}\nSee evaluation/README.md")

    items = collect_images(args.images)
    if not items:
        sys.exit("No images found. Add images in class sub-folders (see evaluation/README.md).")

    clf = WasteClassifier()
    model_labels = clf.labels
    norm_to_model = {normalize_label(l): l for l in model_labels}

    # Check that every folder name matches a model label.
    unknown = {c for _, c in items if normalize_label(c) not in norm_to_model}
    if unknown:
        sys.exit(
            f"These folders do not match any model label: {sorted(unknown)}\n"
            f"Model labels are: {model_labels}"
        )

    y_true, y_pred, rows = [], [], []
    for path, class_name in items:
        true_label = norm_to_model[normalize_label(class_name)]
        try:
            img = validate_image(Image.open(path))
        except (InvalidImageError, OSError) as err:
            print(f"Skipping {path}: {err}")
            continue
        top = clf.predict(img, top_k=1)[0]
        y_true.append(true_label)
        y_pred.append(top[0])
        rows.append([str(path), true_label, top[0], f"{top[1]:.4f}", top[0] == true_label])

    results = Path(__file__).resolve().parent / "results"
    results.mkdir(exist_ok=True)

    accuracy = sum(t == p for t, p in zip(y_true, y_pred)) / len(y_true)
    report = classification_report(y_true, y_pred, labels=model_labels, zero_division=0)
    summary = f"Images evaluated: {len(y_true)}\nOverall accuracy: {accuracy:.4f}\n\n{report}"
    print(summary)
    (results / "metrics.txt").write_text(summary, encoding="utf-8")

    with open(results / "predictions.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["path", "true_label", "predicted_label", "confidence", "correct"])
        writer.writerows(rows)

    cm = confusion_matrix(y_true, y_pred, labels=model_labels)
    fig, ax = plt.subplots(figsize=(9, 8))
    ax.imshow(cm, cmap="Greens")
    ax.set_xticks(range(len(model_labels)), model_labels, rotation=60, ha="right")
    ax.set_yticks(range(len(model_labels)), model_labels)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    ax.set_title("Confusion matrix")
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            if cm[i, j]:
                ax.text(j, i, cm[i, j], ha="center", va="center", fontsize=8)
    fig.tight_layout()
    fig.savefig(results / "confusion_matrix.png", dpi=150)
    print(f"\nSaved results to {results}")


if __name__ == "__main__":
    main()
