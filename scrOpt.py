import matplotlib.pyplot as plt
import matplotlib.animation as animation
from pydexcom import Dexcom
from datetime import datetime
from pathlib import Path
from config_handler import load_config, load_config_constants
import pygame
import threading
import random
import time
import os

early_pass = True
BASE_DIR = Path(__file__).resolve().parent
last_alarm_time = 0
username, password, region = load_config()
LOW_THRESHOLD, COOLDOWN_MINUTES = load_config_constants()
COOLDOWN_SECONDS = COOLDOWN_MINUTES * 60

while early_pass:
    try:
        pygame.init()
        stop_alarm = threading.Event()
        dexcom = Dexcom(username=username, password=password, region=region)
        reading = dexcom.get_current_glucose_reading()
        werte = []
        zeiten = []
        Sound = [BASE_DIR / 'Sound' / 'Alarm1.mp3', BASE_DIR / 'Sound' / 'Alarm2.mp3', BASE_DIR / 'Sound' / 'Alarm3.mp3', BASE_DIR / 'Sound' / 'Alarm4.mp3', BASE_DIR / 'Sound' / 'Alarm5.mp3']
        last_alarm_time = 0
        first_b = True
        last_wert_i = 1
        differenz_i = 1
        print("Earlypass completed")
        early_pass = False
    except:
        print("Cannot initiate script. This may be a problem with your login information or your internet connection. To be sure please check both.")
        time.sleep(5)

def get_glucose_reading_with_timeout(timeout_seconds=20):
    result = {}
    def target():
        try:
            result["reading"] = dexcom.get_current_glucose_reading()
        except Exception as e:
            result["error"] = e

    thread = threading.Thread(target=target)
    thread.start()
    thread.join(timeout_seconds)
    if thread.is_alive():
        raise TimeoutError("Dexcom request timed out.")
    if "error" in result:
        raise result["error"]
    return result["reading"]

def prediction(wert, current_time):
    global last_alarm_time
    global first_b
    global last_wert_i
    global differenz_i
    global LOW_THRESHOLD
    global COOLDOWN_SECONDS
    try:
        prediction_wert_i = 1
        zeit = datetime.now().strftime("%H:%M:%S")
        if first_b:
            first_b = False
            last_wert_i = wert
        else:
            differenz_i = last_wert_i - wert
            if differenz_i > 0:
                for i in range(1,3):
                    prediction_wert_i = wert - differenz_i
                    if prediction_wert_i < LOW_THRESHOLD and i == 1 and (current_time - last_alarm_time > COOLDOWN_SECONDS):
                        last_alarm_time = current_time
                        set_alarm()
                    elif prediction_wert_i < LOW_THRESHOLD and i > 1:
                        print(f"[{zeit}] Warning: In the next {i} values your bloodsugar might fall under {LOW_THRESHOLD}")
            last_wert_i = wert
    except:
        print("Fehler in prediction")
    
def play_alarm():
    try:
        my_sound = pygame.mixer.Sound(random.choice(Sound))
        while not stop_alarm.is_set():
            my_sound.play()
    except ImportError:
        while not stop_alarm.is_set():
            os.system("echo -e '\a'")
            time.sleep(1)

def math_problem():
    a = random.randint(5, 20)
    b = random.randint(2, 10)
    correct_answer = a * b
    while True:
        try:
            user_answer = int(input(f"What is {a} × {b}? "))
            if user_answer == correct_answer:
                print("Correct. The alarm will now be stopped for",COOLDOWN_SECONDS/60,"minutes.")
                stop_alarm.set()
                break
            else:
                print("Wrong! Try again.")
        except ValueError:
            print("Please enter a valid number!")
    print("Paused Alarm")
def set_alarm():
    stop_alarm.clear()
    threading.Thread(target=play_alarm, daemon=True).start()
    math_problem()

def update(frame):
    global last_alarm_time
    global LOW_THRESHOLD
    global COOLDOWN_SECONDS
    try:
        reading = get_glucose_reading_with_timeout()
        wert = reading.value
        zeit = datetime.now().strftime("%H:%M:%S")
        werte.append(wert)
        zeiten.append(zeit)
        print(f"[{zeit}] Wert: {wert} mg/dL")
        ax.clear()
        for i in range(1, len(werte)):
            x_vals = [zeiten[i - 1], zeiten[i]]
            y_vals = [werte[i - 1], werte[i]]
            farbe = 'red' if werte[i] < LOW_THRESHOLD else 'blue'
            ax.plot(x_vals, y_vals, color=farbe, linewidth=2)
        ax.set_title("Live CGM Werte")
        ax.set_xlabel("Time")
        ax.set_ylabel("Glukose (mg/dL)")
        ax.grid(True)
        plt.xticks(rotation=75)
        plt.tight_layout()
        current_time = time.time()
        if wert < LOW_THRESHOLD and (current_time - last_alarm_time > COOLDOWN_SECONDS):
            last_alarm_time = current_time
            set_alarm()
        prediction(wert, current_time)
    except:
        try:
            zeit = datetime.now().strftime("%H:%M:%S")
            print(f"[{zeit}] Error while reading data. Your internet may have disconnected.")
        except:
            zeit = "unbekannt"
            print(f"[{zeit}] Error while reading data. Your internet may have disconnected.")

if __name__ == "__main__":
    fig, ax = plt.subplots()
    ani = animation.FuncAnimation(fig, update, interval=300000)  # 5 Minuten = 300000 ms
    plt.show()
    datum = datetime.now().strftime("%Y-%m-%d")
    filename = BASE_DIR / f"CGM Daten/cgm_diagramm_{datum}.png"
    counter = 1
    while os.path.exists(filename):
        filename = BASE_DIR / f"CGM Daten/cgm_diagramm_{datum}_v{counter}.png"
        counter += 1
    fig.savefig(filename)
    print(f"Diagramm saved as: {filename}")
    time.sleep(5)
