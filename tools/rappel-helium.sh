#!/bin/sh
# Bluelium : rappel quand Helium sort une nouvelle version MAJEURE stable
# (la seule qui vaille une recompilation complète, voir tools/helium-tag.py).
# Notification macOS + ligne dans ~/Library/Logs/bluelium-rappel-helium.log.
# Lancé chaque jour par tools/installer-rappel-helium.sh ; à la main :
#   tools/rappel-helium.sh
DIR=$(cd "$(dirname "$0")" && pwd)
LOG="$HOME/Library/Logs/bluelium-rappel-helium.log"
MSG=$(/usr/bin/python3 "$DIR/helium-tag.py" check 2>&1) || {
  echo "$(date '+%F %T') vérification impossible : $MSG" >> "$LOG"; exit 0; }
[ -n "$MSG" ] || { echo "Helium : rien de nouveau (versions majeures)."; exit 0; }
echo "$MSG"
echo "$MSG" | sed "s/^/$(date '+%F %T') /" >> "$LOG"
# Une notification seulement s'il y a quelque chose à construire.
if echo "$MSG" | grep -q "À construire"; then
  TXT=$(echo "$MSG" | grep "À construire" | head -1 | sed 's/"/\\"/g')
  /usr/bin/osascript -e "display notification \"$TXT\" with title \"Bluelium\" subtitle \"Nouvelle version majeure de Helium\" sound name \"Glass\""
fi
