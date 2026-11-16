#!/bin/sh
# Installe (ou retire avec --retirer) le rappel quotidien Helium sur ce Mac :
# agent launchd ~/Library/LaunchAgents/com.bluelium.rappel-helium.plist,
# chaque jour à 10 h et à l'ouverture de session.
DIR=$(cd "$(dirname "$0")" && pwd)
ID=com.bluelium.rappel-helium
PLIST="$HOME/Library/LaunchAgents/$ID.plist"
launchctl bootout "gui/$(id -u)/$ID" 2>/dev/null
if [ "$1" = --retirer ]; then rm -f "$PLIST"; echo "Rappel retiré."; exit 0; fi
mkdir -p "$HOME/Library/LaunchAgents"
cat > "$PLIST" <<PL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>$ID</string>
  <key>ProgramArguments</key><array>
    <string>/bin/sh</string><string>$DIR/rappel-helium.sh</string>
  </array>
  <key>StartCalendarInterval</key><dict>
    <key>Hour</key><integer>10</integer><key>Minute</key><integer>0</integer>
  </dict>
  <key>RunAtLoad</key><true/>
</dict></plist>
PL
launchctl bootstrap "gui/$(id -u)" "$PLIST" && echo "Rappel installé : chaque jour à 10 h ($PLIST)."
