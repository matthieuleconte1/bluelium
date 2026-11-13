#!/usr/bin/env bash
# Bluelium — paquet macOS : Helium.app compilé → Bluelium.app signée ad hoc
# dans un .dmg (+ .sha256), et publication facultative sur GitHub.
#
# Usage : scripts/package-macos.sh <out/Default> <dossier de sortie>
#   BLUELIUM_VERSION  version (ex. 0.21.2.1-gabc1234), obligatoire
#   BLUELIUM_ARCH     arm64 (défaut) ou x86_64
#   PUBLISH=1         ajoute le .dmg à la release GitHub v<version> si elle
#                     existe (build Linux de la même version), sinon crée la
#                     release v<version>-macos, non marquée « latest » pour que
#                     la mise à jour Linux (releases/latest) ne la voie pas.
#   BLUELIUM_REPO     dépôt GitHub (défaut : matthieuleconte1/bluelium)
#
# Sans identité Developer ID, l'appli est signée ad hoc, comme les builds non
# signés de Helium : au premier lancement d'un .dmg téléchargé, ouvrir avec
# clic droit → Ouvrir (ou xattr -dr com.apple.quarantine Bluelium.app).
set -euo pipefail

OUT=${1:?Usage : $0 <out/Default> <dossier de sortie>}
DEST=${2:?Usage : $0 <out/Default> <dossier de sortie>}
VERSION=${BLUELIUM_VERSION:?définir BLUELIUM_VERSION}
ARCH=${BLUELIUM_ARCH:-arm64}
SRC_APP=$OUT/Helium.app
[ -d "$SRC_APP" ] || { echo "Introuvable : $SRC_APP" >&2; exit 1; }

NAME=bluelium-$VERSION-macos-$ARCH
STAGE=$DEST/$NAME
APP=$STAGE/Bluelium.app
rm -rf "$STAGE"; mkdir -p "$STAGE"
ditto "$SRC_APP" "$APP"

# Nom affiché et version Bluelium. L'identifiant de bundle et le dossier de
# profil viennent déjà de la spec macos_identity_spec.py.
PLIST=$APP/Contents/Info.plist
pb() { /usr/libexec/PlistBuddy -c "$1" "$PLIST"; }
pb "Set :CFBundleName Bluelium"
pb "Delete :CFBundleDisplayName" 2>/dev/null || true
pb "Add :CFBundleDisplayName string Bluelium"
pb "Delete :BlueliumVersion" 2>/dev/null || true
pb "Add :BlueliumVersion string $VERSION"
bundle_id=$(/usr/libexec/PlistBuddy -c "Print :CFBundleIdentifier" "$PLIST")
if [ "$bundle_id" = net.imput.helium ]; then
  echo "ATTENTION : identifiant net.imput.helium (spec macos-identity absente ?)" >&2
fi

# Signature : Developer ID si MACOS_CERTIFICATE_NAME est défini, sinon ad hoc.
if [ -n "${MACOS_CERTIFICATE_NAME:-}" ]; then
  codesign --force --deep --options runtime --timestamp \
    --sign "$MACOS_CERTIFICATE_NAME" "$APP"
else
  codesign --force --deep --sign - "$APP"
fi
codesign --verify --deep --strict "$APP"

# Image disque : l'appli et un raccourci vers Applications.
ln -s /Applications "$STAGE/Applications"
DMG=$DEST/$NAME.dmg
rm -f "$DMG"
hdiutil create -quiet -volname Bluelium -srcfolder "$STAGE" -ov -format ULMO "$DMG"
rm -rf "$STAGE"
( cd "$DEST" && shasum -a 256 "$NAME.dmg" > "$NAME.dmg.sha256" )
echo "Paquet : $DMG"
echo "SHA-256 : $(cut -d' ' -f1 "$DMG.sha256")"

if [ "${PUBLISH:-0}" = 1 ]; then
  REPO=${BLUELIUM_REPO:-matthieuleconte1/bluelium}
  if gh release view "v$VERSION" --repo "$REPO" >/dev/null 2>&1; then
    gh release upload "v$VERSION" "$DMG" "$DMG.sha256" --repo "$REPO" --clobber
    echo "Ajouté à la release v$VERSION"
  else
    gh release create "v$VERSION-macos" "$DMG" "$DMG.sha256" --repo "$REPO" \
      --latest=false --title "Bluelium $VERSION (macOS)" \
      --notes "Construit sur Helium macOS $(echo "$VERSION" | cut -d- -f1), patchs Bluelium $(echo "$VERSION" | sed 's/.*-g//'). macOS $ARCH, signé ad hoc.

Installation et mise à jour automatique : voir le README."
    echo "Release v$VERSION-macos publiée"
  fi
fi
