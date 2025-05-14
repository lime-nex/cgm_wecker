import subprocess
import threading
from pathlib import Path

# Basisverzeichnis dynamisch ermitteln
BASE_DIR = Path(__file__).resolve().parent
PYTHON_BIN = BASE_DIR / 'venv' / 'bin' / 'python'
SCR_OPT = BASE_DIR / 'scrOpt.py'
DEXPY = BASE_DIR / 'dexpy.py'

# Dynamisch zusammenbauen
command_if_o = f"lxterminal -e '{str(PYTHON_BIN)} {str(SCR_OPT)}'"
command_else = f"lxterminal -e '{str(PYTHON_BIN)} {str(DEXPY)}'"

user_input = None

def get_input():
    global user_input
    user_input = input("Enter 'o' to start the online script which connects to the Dexcom server. If you don't press anything, the offline script for the Dexcom receiver will start. (20 seconds): ").strip()

input_thread = threading.Thread(target=get_input)
input_thread.daemon = True
input_thread.start()

input_thread.join(timeout=20)

if user_input == "o":
    subprocess.run(command_if_o, shell=True)
else:
    subprocess.run(command_else, shell=True)
