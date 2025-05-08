import subprocess
import threading

# Jetzt korrekt zugeordnet:
# Wenn 'o' eingegeben wird → scrOpt.py
command_if_o = "lxterminal -e 'cgm_wecker/venv/bin/python scrOpt.py'"

# Wenn NICHT 'o' eingegeben wird → dexpy.py
command_else = "lxterminal -e 'cgm_wecker/venv/bin/python dexpy.py'"

user_input = None

def get_input():
    global user_input
    user_input = input("Enter 'o' to start the online Script which connects to the Dexcom-Server. If you don't press anything the offline script for the dexcom-receiver will start. (20 seconds): ").strip()

input_thread = threading.Thread(target=get_input)
input_thread.daemon = True
input_thread.start()

input_thread.join(timeout=20)

if user_input == "o":
    subprocess.run(command_if_o, shell=True)
else:
    subprocess.run(command_else, shell=True)
