#!/bin/bash

DESKTOP_PATH="$HOME/Desktop"
SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXEC_PATH="$SCRIPT_PATH/start_sound.sh"
ICON_PATH="$SCRIPT_PATH/icons/icon1.png"

cat > /tmp/cgm_wecker.desktop <<EOF
[Desktop Entry]
Type=Application
Name=CGM Wecker starten
Exec=lxterminal --command="bash --login -c '$EXEC_PATH; exec bash'"
Icon=$ICON_PATH
Terminal=true
EOF

cat << 'EOF' > "$EXEC_PATH"
#!/bin/bash

SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXEC_PATH="$SCRIPT_PATH/start_sound.sh"

export XDG_RUNTIME_DIR=/run/user/$(id -u)
exec "$SCRIPT_PATH/venv/bin/python3" "$SCRIPT_PATH/Intertface.py"
EOF

chmod +x "$EXEC_PATH"




chmod +x /tmp/cgm_wecker.desktop
mv /tmp/cgm_wecker.desktop "$DESKTOP_PATH/cgm_wecker.desktop"

chmod +x start_interface.sh
