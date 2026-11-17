import json
from datetime import datetime
from pathlib import Path


PROJECT_FOLDER = Path(__file__).resolve().parents[2]
DATA_FOLDER = PROJECT_FOLDER / "data"
HISTORY_FILE = DATA_FOLDER / "history.json"


def load_history():
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
    DATA_FOLDER.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(records, file, indent=4, ensure_ascii=False)


def add_history_record(source, text, result, metadata=None):
    records = load_history()
    record = {
        "source": source,
        "text": text,
        "sentiment": result["sentiment"],
        "confidence": result["confidence"],
        "scores": result["scores"],
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    if metadata:
        record.update(metadata)
    records.insert(0, record)
    save_history(records)
    return record


def clear_history():
    save_history([])
    return []


def get_history():
    return load_history()
