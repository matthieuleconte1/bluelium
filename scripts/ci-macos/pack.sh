#!/usr/bin/env bash
# CI macOS : emballe l'arbre de build (sources, out/, outils) pour le job
# suivant. Usage : pack.sh <dossier de sortie>
set -euo pipefail
WORK=${BLUELIUM_MAC_WORK:?}
DEST=${1:?}
mkdir -p "$DEST"
rm -rf "$WORK/helium-macos/build/download_cache"
gsync --file-system "$WORK/helium-macos/build/src" 2>/dev/null || sync
df -h "$WORK"
tar -C "$WORK" --exclude='.git' -cf - helium-macos meta.env series.version \
  | zstd -9 -T0 -q -o "$DEST/etat.tar.zst"
( cd "$DEST" && shasum -a 256 etat.tar.zst > etat.sha256 )
du -h "$DEST/etat.tar.zst"
