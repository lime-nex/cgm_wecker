# save_state.py
import json

def save_state(first_time):
    with open("state.json", "w") as f:
        json.dump({"first_time": first_time}, f)

def load_state():
    try:
        with open("state.json", "r") as f:
            return json.load(f)["first_time"]
    except (FileNotFoundError, KeyError):
        return True  # Default value, falls Datei nicht existiert
