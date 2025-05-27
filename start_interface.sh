#!/bin/bash

# Verzeichnis ermitteln, in dem dieses Skript liegt
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Starte dein Python-Programm relativ zu diesem Verzeichnis
sudo python3 "$SCRIPT_DIR/main.py"

