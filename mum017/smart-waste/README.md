# ♻️ AI-Powered Smart Waste Classification & Recycling Recommendation System

An interactive Machine Learning application that identifies household waste from a photo and gives tailored recycling and disposal guidance.

Built for the *Professional Training* mid-term assignment (individual project).

## Features

- **Waste classification** with a pretrained Vision Transformer (12 classes)
- **Top-3 predictions** with confidence bars
- **Confidence tiers** (high, medium, low): low-confidence results ask for a better photo instead of giving false certainty
- **Recycling assistant**: bin type, preparation steps, disposal method, things to avoid, tips, and environmental notes
- **Confusable-pair warnings** (e.g. paper vs cardboard, different glass colours)
- **Input validation** (missing image, wrong file, too-small image, transparent PNGs)
- **Gradio dashboard** with a Classify tab and an About-the-model tab
- **Evaluation script** that produces accuracy, per-class metrics and a confusion matrix on your own test images

## Model

| | |
|---|---|
| Model | [`watersplash/waste-classification`](https://huggingface.co/watersplash/waste-classification) |
| Architecture | Vision Transformer (ViT), about 85.8M parameters |
| Training data (per model card) | Kaggle *garbage-classification* dataset (mostafaabla) |
| Classes | Battery, Biological, Brown glass, Cardboard, Clothes, Green glass, Metal, Paper, Plastic, Shoes, Trash, White glass |

The model is downloaded automatically from Hugging Face on first run and is **not** stored in this repository. The model card reports 98% accuracy but does not describe its evaluation. This project measures accuracy independently (see `evaluation/`).

## Project structure

```
app.py                  Gradio interface (entry point)
src/
  config.py             model name, thresholds, paths
  validation.py         checks and cleans the uploaded image
  classifier.py         loads the ViT and returns top-k predictions
  recommender.py        confidence tiers + recycling advice logic
data/knowledge_base.json  recycling guidance for each class
evaluation/             evaluation script and instructions
tests/test_core.py      unit tests (no model download needed)
requirements.txt
```

## Installation

Requires Python 3.9 or newer.

```bash
# 1. Go into this project's folder
cd <your-folder>

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
python app.py
```

Open the printed URL (normally http://127.0.0.1:7860), upload an image and press **Classify**. The first run downloads the model and may take a minute.

## Testing

```bash
pytest -v                          # unit tests (fast, offline)
python evaluation/evaluate.py      # model evaluation on your own images
```

See `evaluation/README.md` for how to prepare the test images.

## Limitations

- The model was trained on mostly clean, single-object images; cluttered photos may be misclassified.
- Only 12 categories (no electronics, composite packaging, or medical waste).
- The `trash` class is a catch-all.
- Recycling rules differ by city and country, so the guidance is general.

## References

- Dosovitskiy et al., *An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale*, ICLR 2021.
- Model: https://huggingface.co/watersplash/waste-classification
- Hugging Face Transformers: https://huggingface.co/docs/transformers
- Gradio: https://www.gradio.app
- Dataset named on the model card: Kaggle *garbage-classification* by mostafaabla.
