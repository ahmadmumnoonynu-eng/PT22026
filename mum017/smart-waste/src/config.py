

from pathlib import Path

# --- Model -----------------------------------------------------------------
MODEL_ID = "watersplash/waste-classification"  # pretrained ViT on Hugging Face
TOP_K = 3                                      # how many predictions to show

# --- Confidence tiers ------------------------------------------------------
# Softmax probability of the top prediction decides how much we trust it.
HIGH_CONFIDENCE = 0.80    # >= 80%  -> show advice normally
MEDIUM_CONFIDENCE = 0.50  # 50-80%  -> show advice + "please double-check"
                          # < 50%   -> "uncertain", ask for a clearer photo

# If the 2nd prediction is at least this likely AND forms a commonly confused
# pair with the 1st, we show an extra warning.
CONFUSION_MIN_SECOND = 0.15

# --- Image validation ------------------------------------------------------
MIN_IMAGE_SIDE = 32       # pixels; smaller images are rejected
MAX_IMAGE_SIDE = 6000     # pixels; larger images are shrunk before inference

# --- Paths -----------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent
KNOWLEDGE_BASE_PATH = ROOT_DIR / "data" / "knowledge_base.json"
