import matplotlib.pyplot as plt
import matplotlib.animation as animation
from pydexcom import Dexcom
from datetime import datetime
import pygame
import threading
import random
import time
import os

early_pass = True

while early_pass:
    try:
        pygame.init()
        stop_alarm = threading.Event()
        username = "enter-username-here(or whatever you use to login to dexcom)" #example: username = "exampleusername"
        password = "enter-password-here" # example: password = "safepassword1234"
        region = "either enter (us) for Amerika, (ous) for out of us and (jp) for japan" #example: region = "ous" 
        dexcom = Dexcom(username=username, password=password, region=region)
        reading = dexcom.get_current_glucose_reading()
        LOW_THRESHOLD = 200
        werte = []
        zeiten = []
        Sound = ['Sound/Alarm1.mp3','Sound/Alarm2.mp3','Sound/Alarm3.mp3','Sound/Alarm4.mp3','Sound/Alarm5.mp3']
        COOLDOWN_SECONDS = 1500  # z.B. 5 Minuten Cooldown
        last_alarm_time = 0
        first_b = True
        last_wert_i = None
        differenz_i = None
        early_pass = False
    except:
        print("Cannot initiate script. This may be a problem with your login information or your internet connection. To be sure please check both.")
        time.sleep(5)

def prediction(wert):
    global last_alarm_time
    global first_b
    global last_wert_i
    global differenz_i
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
    try:
        reading = dexcom.get_current_glucose_reading()
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
        prediction(wert)
        if wert < LOW_THRESHOLD and (current_time - last_alarm_time > COOLDOWN_SECONDS):
            last_alarm_time = current_time
            set_alarm()
    except:
        print("[{zeit}] Error reading Data. Your internet may have disconnected.")

if __name__ == "__main__":
    fig, ax = plt.subplots()
    ani = animation.FuncAnimation(fig, update, interval=300000)  # 5 Minuten = 300000 ms
    plt.show()
    datum = datetime.now().strftime("%Y-%m-%d")
    filename = f"CGM Daten/cgm_diagramm_{datum}.png"
    counter = 1
    while os.path.exists(filename):
        filename = f"CGM Daten/cgm_diagramm_{datum}_v{counter}.png"
        counter += 1
    fig.savefig(filename)
    print(f"Diagramm saved as: {filename}")
