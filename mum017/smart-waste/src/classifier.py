"""Wraps the pretrained Vision Transformer so the rest of the app stays simple.

Pipeline for one image:
    PIL image -> image processor (resize 224x224, normalise, to tensor)
              -> ViT model -> logits (12 raw scores)
              -> softmax -> probabilities (sum to 1)
              -> sort -> top-k (label, probability)
"""

from typing import List, Tuple

from PIL import Image

from src.config import MODEL_ID, TOP_K


class WasteClassifier:
    """Loads the model once (lazily) and returns ranked predictions."""

    def __init__(self, model_id: str = MODEL_ID):
        self.model_id = model_id
        self._processor = None
        self._model = None
        self._torch = None

    # -- loading ------------------------------------------------------------
    def load(self) -> None:
        """Download (first run only) and load the model. Safe to call twice."""
        if self._model is not None:
            return
        # Imported here so the rest of the project (tests, knowledge base)
        # works even before the heavy libraries are installed.
        import torch
        from transformers import AutoImageProcessor, AutoModelForImageClassification

        self._torch = torch
        self._processor = AutoImageProcessor.from_pretrained(self.model_id)
        self._model = AutoModelForImageClassification.from_pretrained(self.model_id)
        self._model.eval()  # inference mode: switches off dropout

    @property
    def labels(self) -> List[str]:
        """Class names read directly from the model's own config."""
        self.load()
        id2label = self._model.config.id2label
        return [id2label[i] for i in sorted(id2label)]

    # -- prediction ---------------------------------------------------------
    def predict(self, image: Image.Image, top_k: int = TOP_K) -> List[Tuple[str, float]]:
        """Return the top_k (label, probability) pairs, most likely first."""
        self.load()
        torch = self._torch

        inputs = self._processor(images=image, return_tensors="pt")
        with torch.no_grad():  # no gradients needed -> faster, less memory
            logits = self._model(**inputs).logits[0]
        probabilities = torch.softmax(logits, dim=-1)

        k = min(top_k, probabilities.shape[0])
        top_probs, top_ids = torch.topk(probabilities, k)
        id2label = self._model.config.id2label
        return [(id2label[int(i)], float(p)) for p, i in zip(top_probs, top_ids)]
