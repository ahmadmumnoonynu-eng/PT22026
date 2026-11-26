# Evaluation guide

The model card claims 98% accuracy, but gives no evaluation details. To report honest numbers, this project tests the model on a small set of images **you collect**.

## 1. Build the test set

Create one folder per class inside `evaluation/test_images/`, named exactly like the model's labels (case and `-`/`_` do not matter). Put **at least 10 images per class** in each folder (more is better).

```
evaluation/test_images/
    battery/
    biological/
    brown-glass/      (or brown-grass; use whatever your label check printed)
    cardboard/
    clothes/
    green-glass/
    metal/
    paper/
    plastic/
    shoes/
    trash/
    white-glass/
```

Good sources:
- **Your own phone photos** of real items. This is the best test because it shows real-world performance.
- Free images you download yourself. Record where they came from in your report.

Do not use images that were in the model's training set if you want a fair test. The Kaggle garbage-classification dataset was the training source, so avoid it for the main test. Photos you take yourself are safest.

## 2. Run

From the project root, with the virtual environment active:

```bash
python evaluation/evaluate.py
```

## 3. Results

Saved in `evaluation/results/`:
- `metrics.txt` (accuracy, per-class precision / recall / F1)
- `predictions.csv` (every image, its prediction and confidence)
- `confusion_matrix.png`

Copy the real numbers into your report. Do not edit them. Test images and results are git-ignored, so describe them in the report and README instead of committing them.
