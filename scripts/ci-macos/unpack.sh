#!/usr/bin/env bash
# CI macOS : déballe l'état laissé par le job précédent.
# Usage : unpack.sh <dossier téléchargé>
set -euo pipefail
WORK=${BLUELIUM_MAC_WORK:?}
SRC=${1:?}
( cd "$SRC" && shasum -a 256 -c etat.sha256 )
mkdir -p "$WORK"
zstd -d -q -c "$SRC/etat.tar.zst" | tar -C "$WORK" -xf -
rm -rf "$SRC"
cat "$WORK/meta.env"
df -h "$WORK"
