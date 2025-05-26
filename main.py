import subprocess
import threading
from pathlib import Path

# Basisverzeichnis dynamisch ermitteln
BASE_DIR = Path(__file__).resolve().parent
PYTHON_BIN = BASE_DIR / 'venv' / 'bin' / 'python'
INTERFACE = BASE_DIR / 'Intertface.py'

command_if_o = f"lxterminal -e '{str(PYTHON_BIN)} {str(INTERFACE)}'"

subprocess.run(command_if_o, shell=True)