
import json
from pathlib import Path
from datetime import datetime


# Store history in the project's data folder
PROJECT_FOLDER = Path(__file__).resolve().parent.parent
DATA_FOLDER = PROJECT_FOLDER / "data"
HISTORY_FILE = DATA_FOLDER / "history.json"


def load_history():
    """Load saved analysis records."""

    DATA_FOLDER.mkdir(parents=True, exist_ok=True)

    if not HISTORY_FILE.exists():
        return []

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            records = json.load(file)

        if isinstance(records, list):
            return records

        return []

    except (json.JSONDecodeError, OSError):
        return []


def save_history(records):
    """Save analysis records to the JSON file."""

    DATA_FOLDER.mkdir(parents=True, exist_ok=True)

    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(records, file, indent=4, ensure_ascii=False)


def add_history_record(source, text, result):
    """Add a new analysis to history."""

    records = load_history()

    record = {
        "source": source,
        "text": text,
        "sentiment": result["sentiment"],
        "confidence": result["confidence"],
        "scores": result["scores"],
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    records.insert(0, record)

    save_history(records)

    return record


def clear_history():
    """Delete all saved analysis records."""

    save_history([])

    return []


def get_history():
    """Return all saved analysis records."""

    return load_history()
