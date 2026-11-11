#!/usr/bin/env bash
# Remplace Helium (paquet système) par Bluelium sur le profil Helium existant.
#   autobuild/switch-to-bluelium.sh            bascule (Helium doit être fermé)
#   autobuild/switch-to-bluelium.sh --revert   revient à Helium
# Le profil (~/.config/net.imput.helium) est sauvegardé avant la bascule.
# Le paquet Helium reste installé : seule l'entrée du menu change, via une
# copie dans ~/.local/share/applications qui a priorité sur celle du système.
set -euo pipefail
APP="$HOME/Applications/helium-glyphe"
PROFILE="${XDG_CONFIG_HOME:-$HOME/.config}/net.imput.helium"
LAUNCHER="$HOME/.local/bin/bluelium"
DESKTOP="$HOME/.local/share/applications/helium.desktop"
SYSTEM_DESKTOP=/usr/share/applications/helium.desktop

if [ "${1:-}" = --revert ]; then
  rm -f "$DESKTOP"
  update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
  echo "Menu rendu à Helium. Lanceur $LAUNCHER et sauvegarde du profil conservés."
  exit 0
fi

[ -x "$APP/helium-wrapper" ] || { echo "Bluelium absent de $APP" >&2; exit 1; }
[ -f "$SYSTEM_DESKTOP" ] || { echo "Entrée Helium introuvable : $SYSTEM_DESKTOP" >&2; exit 1; }
# Profil en cours d'utilisation : Chromium tient un lien SingletonLock
# « hôte-pid » dans le dossier du profil.
lock=$(readlink "$PROFILE/SingletonLock" 2>/dev/null || true)
if [ -n "$lock" ] && kill -0 "${lock##*-}" 2>/dev/null; then
  echo "Helium est encore ouvert sur ce profil : fermer toutes ses fenêtres d'abord." >&2
  exit 1
fi

# 1. Sauvegarde du profil (une seule fois).
BACKUP="$PROFILE.backup-avant-bluelium"
if [ -d "$PROFILE" ] && [ ! -e "$BACKUP" ]; then
  cp -a "$PROFILE" "$BACKUP"
  echo "Profil sauvegardé : $BACKUP"
fi

# 2. Lanceur : mêmes options que helium-browser (fichiers de flags compris).
mkdir -p "$(dirname "$LAUNCHER")"
cat > "$LAUNCHER" <<EOF
#!/usr/bin/env bash
# Bluelium sur le profil Helium. Options : /etc/helium-browser-flags.conf,
# \${XDG_CONFIG_HOME:-\$HOME/.config}/helium-browser-flags.conf, \$HELIUM_USER_FLAGS.
FLAGS=()
for f in /etc/helium-browser-flags.conf "\${XDG_CONFIG_HOME:-\$HOME/.config}/helium-browser-flags.conf"; do
  [ -r "\$f" ] || continue
  while IFS= read -r line; do
    [[ "\$line" =~ ^[[:space:]]*(#|\$) ]] && continue
    read -r -a tokens <<< "\$line"
    FLAGS+=("\${tokens[@]}")
  done < "\$f"
done
[ -n "\${HELIUM_USER_FLAGS:-}" ] && read -r -a extra <<< "\$HELIUM_USER_FLAGS" && FLAGS+=("\${extra[@]}")
exec "$APP/helium-wrapper" "\${FLAGS[@]}" "\$@"
EOF
chmod +x "$LAUNCHER"

# 3. Entrée du menu (même nom de fichier : reste le navigateur par défaut).
mkdir -p "$(dirname "$DESKTOP")"
sed -e "s#^Exec=helium-browser#Exec=$LAUNCHER#" \
    -e 's#^Name=Helium Browser$#Name=Bluelium#' "$SYSTEM_DESKTOP" > "$DESKTOP"
update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true

# 4. Mise à jour automatique depuis les releases GitHub.
"$(dirname "$0")/install-updater.sh"
echo "Bascule faite : « Bluelium » dans le menu, profil Helium conservé."
echo "Retour à Helium : $0 --revert"
