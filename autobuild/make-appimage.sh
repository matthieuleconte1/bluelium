#!/usr/bin/env bash
# Bluelium : AppImage à partir du paquet bluelium-<version>.tar.zst.
#   make-appimage.sh <paquet.tar.zst> <dossier de sortie>
# Produit Bluelium-<version>-<arch>.AppImage (+ .sha256) et son .zsync
# (mise à jour par AppImageUpdate / Gear Lever). <arch> : APPIMAGE_ARCH,
# x86_64 par défaut, ou aarch64 (nom donné par « uname -m », que lit
# appimage-update).
# Profil ~/.config/bluelium, copié une fois depuis celui de Helium (AppRun).
set -Eeuo pipefail

TAR=$1
OUTDIR=$2
HERE=$(cd "$(dirname "$0")" && pwd)
TOOL=${APPIMAGETOOL:-/root/glyphe/bin/appimagetool}
REPO=${BLUELIUM_REPO:-matthieuleconte1/bluelium}
AARCH=${APPIMAGE_ARCH:-x86_64}
RUNTIME=()
[ "$AARCH" = x86_64 ] || RUNTIME=(--runtime-file "${APPIMAGE_RUNTIME:-/root/glyphe/bin/runtime-$AARCH}")

NAME=$(basename "$TAR" .tar.zst)      # bluelium-<version>
VERSION=${NAME#bluelium-}
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT

APPDIR=$WORK/Bluelium.AppDir
mkdir -p "$APPDIR/opt" "$APPDIR/usr/share/icons/hicolor/256x256/apps" \
         "$APPDIR/usr/share/applications"
zstd -dc "$TAR" | tar -C "$APPDIR/opt" -xf -
mv "$APPDIR/opt/$NAME" "$APPDIR/opt/bluelium"
# Dans l'AppImage, pas de mise à jour « staged » : c'est l'AppImage qu'on remplace.
rm -f "$APPDIR/opt/bluelium/helium-wrapper"

install -m 755 "$HERE/AppRun" "$APPDIR/AppRun"
install -m 755 "$HERE/appimage-update" "$APPDIR/opt/bluelium/appimage-update"
install -m 644 "$HERE/bluelium.desktop" "$APPDIR/bluelium.desktop"
install -m 644 "$HERE/bluelium.desktop" "$APPDIR/usr/share/applications/bluelium.desktop"
for icon in "$APPDIR/bluelium.png" \
            "$APPDIR/usr/share/icons/hicolor/256x256/apps/bluelium.png"; do
  cp "$APPDIR/opt/bluelium/product_logo_256.png" "$icon"
done
ln -sf bluelium.png "$APPDIR/.DirIcon"

OUT=$OUTDIR/Bluelium-$VERSION-$AARCH.AppImage
cd "$OUTDIR"
ARCH=$AARCH VERSION=$VERSION "$TOOL" --appimage-extract-and-run --no-appstream "${RUNTIME[@]}" \
  -u "gh-releases-zsync|${REPO%%/*}|${REPO##*/}|latest|Bluelium-*-$AARCH.AppImage.zsync" \
  "$APPDIR" "$OUT"
sha256sum "$(basename "$OUT")" > "$OUT.sha256"
echo "AppImage : $OUT"
