#!/usr/bin/env bash
# Bluelium — paquet macOS : Helium.app compilé → Bluelium.app signée ad hoc
# dans un .dmg (+ .sha256), et publication facultative sur GitHub.
#
# Usage : scripts/package-macos.sh <out/Default> <dossier de sortie>
#   BLUELIUM_VERSION  version (ex. 0.22.4.1-glycine), obligatoire
#   BLUELIUM_ARCH     arm64 (défaut) ou x86_64
#   PUBLISH=1         ajoute le .dmg à la release GitHub v<version> si elle
#                     existe (build Linux de la même version), sinon crée la
#                     release v<version>-macos, non marquée « latest » pour que
#                     la mise à jour Linux (releases/latest) ne la voie pas.
#   BLUELIUM_REPO     dépôt GitHub (défaut : matthieuleconte1/bluelium)
#   BLUELIUM_SERIE    commit de la série (défaut : tools/couleur.py --serie)
#   BLUELIUM_REQUIRE_SIGN=1  échoue au lieu de signer ad hoc (CI : une
#                     signature ad hoc casserait les mises à jour Sparkle)
#
# Sortie : le .dmg, son .sha256, appcast-<arch>.xml et release-tag-<arch>.txt
# (tag GitHub visé), que scripts/publish-macos.sh publie.
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
# Numéro de build croissant pour Sparkle (il compare CFBundleVersion) :
# version Helium + date de l'emballage. Deux builds Bluelium sur la même
# version de Helium restent ainsi ordonnés.
HELIUM_VERSION=$(/usr/libexec/PlistBuddy -c "Print :CFBundleShortVersionString" "$PLIST")
BUILD_NUMBER="$HELIUM_VERSION.$(date -u +%Y%m%d%H%M)"
pb "Set :CFBundleVersion $BUILD_NUMBER"
bundle_id=$(/usr/libexec/PlistBuddy -c "Print :CFBundleIdentifier" "$PLIST")
if [ "$bundle_id" = net.imput.helium ]; then
  echo "ATTENTION : identifiant net.imput.helium (spec macos-identity absente ?)" >&2
fi

# Signature : Developer ID si MACOS_CERTIFICATE_NAME est défini ; sinon le
# certificat auto-signé « Bluelium Code Signing » du trousseau (identité
# stable d'une version à l'autre : Sparkle et les autorisations macOS la
# reconnaissent) ; à défaut, ad hoc.
SIGN_IDENTITY=${BLUELIUM_SIGN_IDENTITY:-Bluelium Code Signing}
if [ -n "${MACOS_CERTIFICATE_NAME:-}" ]; then
  codesign --force --deep --options runtime --timestamp \
    --sign "$MACOS_CERTIFICATE_NAME" "$APP"
elif security find-identity -p codesigning | grep -q "\"$SIGN_IDENTITY\""; then
  codesign --force --deep --sign "$SIGN_IDENTITY" "$APP"
else
  if [ "${BLUELIUM_REQUIRE_SIGN:-0}" = 1 ]; then
    echo "Certificat « $SIGN_IDENTITY » absent : signature refusée (BLUELIUM_REQUIRE_SIGN=1)" >&2
    exit 1
  fi
  echo "ATTENTION : certificat « $SIGN_IDENTITY » absent, signature ad hoc" >&2
  codesign --force --deep --sign - "$APP"
fi
codesign --verify --deep --strict "$APP"

# Image disque : fenêtre mise en page (fond dessiné, appli → Applications)
# par dmgbuild, installé une fois dans un venv en cache. En cas d'échec, .dmg
# simple sans mise en page.
DMG=$DEST/$NAME.dmg
rm -f "$DMG"
REPO_DIR=$(cd "$(dirname "$0")/.." && pwd)
VENV=${XDG_CACHE_HOME:-$HOME/.cache}/bluelium/dmgbuild-venv
if [ ! -x "$VENV/bin/dmgbuild" ]; then
  python3 -m venv "$VENV" && "$VENV/bin/pip" install -q 'dmgbuild==1.6.7' \
    || echo "ATTENTION : dmgbuild indisponible, .dmg sans mise en page" >&2
fi
if [ -x "$VENV/bin/dmgbuild" ] && "$VENV/bin/dmgbuild" \
    -s "$REPO_DIR/scripts/dmg-settings.py" \
    -D app="$APP" -D background="$REPO_DIR/assets/dmg/background.tiff" \
    -D icon="$APP/Contents/Resources/app.icns" \
    Bluelium "$DMG"; then
  :
else
  ln -s /Applications "$STAGE/Applications"
  hdiutil create -quiet -volname Bluelium -srcfolder "$STAGE" -ov -format ULMO "$DMG"
fi
rm -rf "$STAGE"
( cd "$DEST" && shasum -a 256 "$NAME.dmg" > "$NAME.dmg.sha256" )
echo "Paquet : $DMG"
echo "SHA-256 : $(cut -d' ' -f1 "$DMG.sha256")"

# Appcast Sparkle : signature EdDSA du .dmg avec la clé du trousseau
# (compte « bluelium »), outils Sparkle téléchargés une fois et vérifiés.
REPO=${BLUELIUM_REPO:-matthieuleconte1/bluelium}
B=$(cd "$(dirname "$0")/.." && pwd)
SERIE=${BLUELIUM_SERIE:-$(python3 "$B/tools/couleur.py" "$B" --serie)}
if NOTES=$(gh release view "v$VERSION" --repo "$REPO" --json body -q .body 2>/dev/null); then
  # Release Linux de la même version : même série attendue (même couleur
  # peut venir d'une autre série, voir tools/couleur.py).
  case "$NOTES" in
    *"série $SERIE"*) ;;
    *) echo "v$VERSION existe déjà avec une autre série que $SERIE : couleur déjà prise" >&2; exit 1 ;;
  esac
  TAG="v$VERSION"
else
  TAG="v$VERSION-macos"
fi
SPARKLE_VERSION=2.10.1
SPARKLE_SHA=1a856d2a9edb8e628de88121d7be04cf0e2167f8641650b78fca00b14244cf27
SPARKLE_DIR=${XDG_CACHE_HOME:-$HOME/.cache}/bluelium/sparkle-$SPARKLE_VERSION
if [ ! -x "$SPARKLE_DIR/bin/sign_update" ]; then
  mkdir -p "$SPARKLE_DIR"
  curl -sfL -o "$SPARKLE_DIR/s.tar.xz" \
    "https://github.com/sparkle-project/Sparkle/releases/download/$SPARKLE_VERSION/Sparkle-$SPARKLE_VERSION.tar.xz"
  echo "$SPARKLE_SHA  $SPARKLE_DIR/s.tar.xz" | shasum -a 256 -c - >/dev/null \
    || { echo "Outils Sparkle : empreinte invalide" >&2; exit 1; }
  tar -xf "$SPARKLE_DIR/s.tar.xz" -C "$SPARKLE_DIR"
fi
APPCAST=$DEST/appcast-$ARCH.xml
# Clé privée : fichier ~/.config/bluelium/sparkle-private-key (lisible sans
# fenêtre de confirmation), sinon le trousseau (compte « bluelium »).
SPARKLE_KEY=${BLUELIUM_SPARKLE_KEY:-$HOME/.config/bluelium/sparkle-private-key}
if [ -f "$SPARKLE_KEY" ]; then
  SIGN_ARGS=(--ed-key-file "$SPARKLE_KEY")
else
  SIGN_ARGS=(--account bluelium)
fi
if SIG=$("$SPARKLE_DIR/bin/sign_update" "${SIGN_ARGS[@]}" "$DMG"); then
  cat > "$APPCAST" <<XML
<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0" xmlns:sparkle="http://www.andymatuschak.org/xml-namespaces/sparkle">
  <channel>
    <title>Bluelium</title>
    <item>
      <title>Bluelium $VERSION</title>
      <pubDate>$(LC_ALL=C date -u '+%a, %d %b %Y %H:%M:%S +0000')</pubDate>
      <sparkle:version>$BUILD_NUMBER</sparkle:version>
      <sparkle:shortVersionString>$VERSION</sparkle:shortVersionString>
      <sparkle:minimumSystemVersion>13.0</sparkle:minimumSystemVersion>
      <enclosure url="https://github.com/$REPO/releases/download/$TAG/$NAME.dmg"
                 type="application/octet-stream" $SIG />
    </item>
  </channel>
</rss>
XML
  echo "Appcast : $APPCAST"
else
  APPCAST=
  echo "ATTENTION : signature Sparkle impossible (clé « bluelium » absente du trousseau ?)" >&2
fi

echo "$TAG" > "$DEST/release-tag-$ARCH.txt"

if [ "${PUBLISH:-0}" = 1 ]; then
  [ -n "$APPCAST" ] || { echo "Pas d'appcast : publication annulée" >&2; exit 1; }
  BLUELIUM_SERIE=$SERIE "$B/scripts/publish-macos.sh" "$DEST"
fi
