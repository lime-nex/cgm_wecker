#!/bin/bash

DESKTOP_PATH="$HOME/Desktop"
SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXEC_PATH="$SCRIPT_PATH/start_interface.sh"

cat > "$DESKTOP_PATH/cgm_wecker.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=CGM Wecker starten
Exec=bash -c "$EXEC_PATH"
Icon=utilities-terminal
Terminal=true
EOF

chmod +x "$DESKTOP_PATH/cgm_wecker.desktop"

chmod +x start_interface.sh
