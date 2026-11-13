#!/usr/bin/env bash
# Bluelium : AppImage à partir du paquet bluelium-<version>.tar.zst.
#   make-appimage.sh <paquet.tar.zst> <dossier de sortie>
# Produit Bluelium-<version>-x86_64.AppImage (+ .sha256) et
# Bluelium-x86_64.AppImage.zsync (mise à jour par AppImageUpdate / Gear Lever).
# Le profil reste ~/.config/net.imput.helium (même binaire que le paquet).
set -Eeuo pipefail

TAR=$1
OUTDIR=$2
HERE=$(cd "$(dirname "$0")" && pwd)
TOOL=${APPIMAGETOOL:-/root/glyphe/bin/appimagetool}
REPO=${BLUELIUM_REPO:-matthieuleconte1/bluelium}

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
install -m 644 "$HERE/bluelium.desktop" "$APPDIR/bluelium.desktop"
install -m 644 "$HERE/bluelium.desktop" "$APPDIR/usr/share/applications/bluelium.desktop"
for icon in "$APPDIR/bluelium.png" \
            "$APPDIR/usr/share/icons/hicolor/256x256/apps/bluelium.png"; do
  cp "$APPDIR/opt/bluelium/product_logo_256.png" "$icon"
done
ln -sf bluelium.png "$APPDIR/.DirIcon"

OUT=$OUTDIR/Bluelium-$VERSION-x86_64.AppImage
cd "$OUTDIR"
ARCH=x86_64 VERSION=$VERSION "$TOOL" --appimage-extract-and-run --no-appstream \
  -u "gh-releases-zsync|${REPO%%/*}|${REPO##*/}|latest|Bluelium-*-x86_64.AppImage.zsync" \
  "$APPDIR" "$OUT"
sha256sum "$(basename "$OUT")" > "$OUT.sha256"
echo "AppImage : $OUT"
