#!/bin/sh
chmod +x create_desktop_link.sh
./create_desktop_link.sh
chmod +x install.sh
sudo ./install.sh
venv/bin/python start_sound.sh

