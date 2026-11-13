#!/usr/bin/env bash
# Installe la mise à jour automatique de Bluelium sur le Mac (utilisateur
# courant) : agent launchd toutes les 2 h et à l'ouverture de session.
set -euo pipefail
cd "$(dirname "$0")"
LABEL=io.github.matthieuleconte1.bluelium-update
BIN=$HOME/.local/bin/bluelium-update-macos
AGENT=$HOME/Library/LaunchAgents/$LABEL.plist
LOGS=$HOME/Library/Logs/Bluelium
mkdir -p "$(dirname "$BIN")" "$(dirname "$AGENT")" "$LOGS"
install -m 755 bluelium-update-macos "$BIN"
cat > "$AGENT" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key>
  <array><string>/usr/bin/python3</string><string>$BIN</string></array>
  <key>StartInterval</key><integer>7200</integer>
  <key>RunAtLoad</key><true/>
  <key>ProcessType</key><string>Background</string>
  <key>StandardOutPath</key><string>$LOGS/update.log</string>
  <key>StandardErrorPath</key><string>$LOGS/update.log</string>
</dict>
</plist>
EOF
launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$AGENT"
echo "Agent $LABEL installé (journal : $LOGS/update.log)"
