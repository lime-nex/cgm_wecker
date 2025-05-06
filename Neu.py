import dexcom_receiver

def main():
    # Initialisiere den Dexcom-Empfänger
    receiver = dexcom_receiver.Receiver()

    # Verbinde mit dem Empfänger
    if receiver.connect():
        print("Erfolgreich mit dem Dexcom-Empfänger verbunden.")

        # Lese die neuesten Blutzuckerdaten
        glucose_data = receiver.get_glucose_readings()
        for reading in glucose_data:
            print(f"Zeit: {reading.timestamp}, Blutzucker: {reading.value} mg/dL")
    else:
        print("Verbindung zum Dexcom-Empfänger fehlgeschlagen.")

if __name__ == "__main__":
    main()
