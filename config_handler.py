import json
from pathlib import Path
import keyring

# Funktion zum Speichern in eine JSON-Datei
BASE_DIR = Path(__file__).resolve().parent
filename1 = BASE_DIR / "configs" / "config_login.json"
filename2 = BASE_DIR / "configs" / "config_constants.json"

def save_config(var1, var2, var3):
    data = {
        "var1": var1,
        "var3": var3
    }
    with open(filename1, 'w') as f:
        json.dump(data, f, indent=4)
    keyring.set_password("meine_app", "mein_user", var2)

# Funktion zum Laden aus der JSON-Datei
def load_config():
    with open(filename1, 'r') as f:
        data = json.load(f)
    password = keyring.get_password("meine_app", "mein_user")
    return data["var1"], password, data["var3"]

def save_config_constants(var1, var2):
    data = {
        "var1": var1,
        "var2": var2
    }
    with open(filename2, 'w') as f:
        json.dump(data, f, indent=4)

# Funktion zum Laden aus der JSON-Datei
def load_config_constants():
    with open(filename2, 'r') as f:
        data = json.load(f)
    return data["var1"], data["var2"]



