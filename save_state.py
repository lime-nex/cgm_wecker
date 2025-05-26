# save_state.py
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
filename = BASE_DIR / "configs" / "state.json"

def save_state(first_time):
    with open(filename, "w") as f:
        json.dump({"first_time": first_time}, f)

def load_state():
    try:
        with open(filename, "r") as f:
            return json.load(f)["first_time"]
    except (FileNotFoundError, KeyError):
        return True  # Default value, falls Datei nicht existiert

