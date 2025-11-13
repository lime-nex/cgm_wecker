#!/bin/bash
set -e

echo "CGM Wecker – Installation startet..."
sleep 1

# Sicherstellen, dass git vorhanden ist
echo "Installiere benötigte Systempakete..."
sudo apt update
sudo apt install -y git python3 python3-pip

# Projekt klonen, falls es noch nicht vorhanden ist
if [ ! -d "cgm_wecker" ]; then
    echo "Klone Repository..."
    git clone https://github.com/lime-nex/cgm_wecker.git
    cd cgm_wecker
else
    echo "Repository bereits vorhanden, aktualisiere..."
    cd cgm_wecker
    git pull
fi

# start.sh ausführbar machen
echo "Mache Startskript ausführbar..."
chmod +x start.sh

# Startskript ausführen
echo "Starte CGM Wecker..."
./start.sh

echo ""
echo "Installation abgeschlossen!"
echo "CGM Wecker sollte jetzt gestartet sein."
echo "Beim nächsten Start kannst du einfach die Desktop-Verknüpfung 'CGM Wecker starten' benutzen."
