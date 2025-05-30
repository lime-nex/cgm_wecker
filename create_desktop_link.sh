#!/bin/bash

DESKTOP_PATH="$HOME/Desktop"
SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXEC_PATH="$SCRIPT_PATH/start_interface.sh"
ICON_PATH="$SCRIPT_PATH/icons/icon1.png"

cat > /tmp/cgm_wecker.desktop <<EOF
[Desktop Entry]
Type=Application
Name=CGM Wecker starten
Exec=bash -c "$EXEC_PATH"
Icon=$ICON_PATH
Terminal=true
EOF

sleep 5s

chmod +x /tmp/cgm_wecker.desktop
mv /tmp/cgm_wecker.desktop "$DESKTOP_PATH/cgm_wecker.desktop"

chmod +x start_interface.sh
