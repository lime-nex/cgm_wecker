#!/bin/sh
sleep 10s
chmod +x install.sh
sudo ./install.sh
venv/bin/python start_dexcom.py
read -p "Drücke Enter zum Schließen..."
