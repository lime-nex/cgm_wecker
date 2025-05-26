import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.dates as mdates
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
filenametxt = BASE_DIR / 'text.txt'
# Schwellenwert für niedrigen Blutzucker
LOW_THRESHOLD = 80

werte = []
zeiten = []

# Datei einlesen
with open(filenametxt, "r") as file:
    for line in file:
        if '-' in line:
            teil = line.strip().split(' - ')
            if len(teil) == 2:
                try:
                    wert = int(teil[0])
                    zeit = datetime.strptime(teil[1], "%H:%M:%S")
                    werte.append(wert)
                    zeiten.append(zeit)
                    print(f"[{zeit.strftime('%H:%M:%S')}] Wert: {wert} mg/dL")
                except ValueError:
                    continue

# Plot vorbereiten
fig, ax = plt.subplots()

for i in range(1, len(werte)):
    x_vals = [zeiten[i - 1], zeiten[i]]
    y_vals = [werte[i - 1], werte[i]]
    farbe = 'red' if werte[i] < LOW_THRESHOLD else 'blue'
    ax.plot(x_vals, y_vals, color=farbe, linewidth=2)

# ALLE Zeitpunkte als x-Ticks setzen
ax.set_xticks(zeiten)
ax.set_xticklabels([t.strftime('%H:%M:%S') for t in zeiten], rotation=45)

# Beschriftung
ax.set_title("CGM Werte Verlauf")
ax.set_xlabel("Uhrzeit")
ax.set_ylabel("Glukose (mg/dL)")
ax.grid(True)
plt.tight_layout()
plt.show()
datum = datetime.now().strftime("%Y-%m-%d")
filename = f"/home/nexus/Desktop/Pi/Desktop/CGM Daten/cgm_diagramm_{datum}.png"
counter = 1
while os.path.exists(filename):
    filename = f"/home/nexus/Desktop/Pi/Desktop/CGM Daten/cgm_diagramm_{datum}_v{counter}.png"
    counter += 1
fig.savefig(filename)
print(f"Diagramm gespeichert als: {filename}")
