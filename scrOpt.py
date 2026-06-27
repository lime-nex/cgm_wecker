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
import queue

early_pass = True
BASE_DIR = Path(__file__).resolve().parent
last_alarm_time = 0
reading_queue = queue.Queue(maxsize=1)
worker_running = True
alarm_active = False
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

def glucose_worker():
    global dexcom
    global worker_running
    error_counter = 0
    while worker_running:
        try:
            reading = dexcom.get_current_glucose_reading()
            # immer nur den neuesten Wert behalten
            while not reading_queue.empty():
                try:
                    reading_queue.get_nowait()
                except queue.Empty:
                    break
            reading_queue.put(reading)
            error_counter = 0
        except Exception as e:
            print(f"Worker Error: {e}")
            error_counter += 1
            # nach drei Fehlern neu verbinden
            if error_counter >= 3:
                print("Reconnecting Dexcom...")
                try:
                    dexcom = Dexcom(username=username, password=password, region=region)
                    print("Reconnect successful")
                except Exception as e2:
                    print("Reconnect failed:", e2)
                error_counter = 0
        # exakt fünf Minuten warten
        for _ in range(150):
            if not worker_running:
                return
            time.sleep(1)

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

def alarm_worker():
    global alarm_active
    stop_alarm.clear()
    sound_thread = threading.Thread(target=play_alarm, daemon=True)
    sound_thread.start()
    math_problem()
    alarm_active = False

def set_alarm():
    global alarm_active
    if alarm_active:
        return
    alarm_active = True
    threading.Thread(target=alarm_worker, daemon=True).start()

def update(frame):
    global last_alarm_time
    global LOW_THRESHOLD
    global COOLDOWN_SECONDS
    try:
        try:
    	    reading = reading_queue.get_nowait()
        except queue.Empty:
            zeit = datetime.now().strftime("%H:%M:%S")
            print(f"[{zeit}] No new reading available.")
            return
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
    threading.Thread(target=glucose_worker, daemon=True).start()
    print("Worker started")
    for i in range(10):
        time.sleep(1)
        p=10-i
        print(f"Wait {p} seconds for booting")
        i=i-1
    fig, ax = plt.subplots()
    ani = animation.FuncAnimation(fig, update, interval=300000, cache_frame_data=False)  # 5 Minuten = 300000 ms
    plt.show()
    worker_running = False	
    datum = datetime.now().strftime("%Y-%m-%d")
    filename = BASE_DIR / f"CGM Daten/cgm_diagramm_{datum}.png"
    counter = 1
    while os.path.exists(filename):
        filename = BASE_DIR / f"CGM Daten/cgm_diagramm_{datum}_v{counter}.png"
        counter += 1
    fig.savefig(filename)
    print(f"Diagramm saved as: {filename}")
    time.sleep(5)
