#!/usr/bin/env bash
# Bluelium (macOS) — reprend le profil Helium : onglets, favoris, historique,
# extensions, réglages, ET mots de passe/cookies (clé du trousseau recopiée).
#
# Helium et Bluelium doivent être fermés (le script attend). Le profil
# Bluelium existant est gardé dans « Bluelium.avant-migration ».
# macOS demande le mot de passe de session pour lire la clé « Helium Storage
# Key » : choisir « Autoriser ».
set -euo pipefail
AS="$HOME/Library/Application Support"
SRC="$AS/net.imput.helium"
DST="$AS/Bluelium"
[ -d "$SRC/Default" ] || { echo "Profil Helium introuvable : $SRC" >&2; exit 1; }

while pgrep -f '/(Helium|Bluelium)\.app/Contents/MacOS/' >/dev/null; do
  echo "$(date '+%T') en attente : fermer Helium et Bluelium (⌘Q)…"; sleep 10
done

if [ -d "$DST" ]; then
  rm -rf "$DST.avant-migration"
  mv "$DST" "$DST.avant-migration"
fi
# Caches et verrous exclus : Chromium les recrée.
rsync -a \
  --exclude 'Singleton*' --exclude 'RunningChromeVersion' \
  --exclude 'GrShaderCache' --exclude 'GraphiteDawnCache' --exclude 'ShaderCache' \
  --exclude 'GPUPersistentCache' --exclude 'Crashpad' --exclude 'BrowserMetrics*' \
  --exclude '/*/Cache' --exclude '/*/Code Cache' --exclude '/*/GPUCache' \
  "$SRC/" "$DST/"
echo "Profil copié ($(du -sh "$DST" | cut -f1))"

# Même clé de chiffrement que Helium, sous le nom que Bluelium cherche.
key=$(security find-generic-password -s 'Helium Storage Key' -a Helium -w)
security add-generic-password -U -s 'Bluelium Storage Key' -a Bluelium \
  -T /Applications/Bluelium.app -w "$key"
unset key
echo "Clé du trousseau recopiée : mots de passe et cookies lisibles dans Bluelium"
echo "Terminé. Ancien profil Bluelium : $DST.avant-migration"
