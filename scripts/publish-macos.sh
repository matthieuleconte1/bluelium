#!/usr/bin/env bash
# Bluelium — publie sur GitHub un paquet macOS fait par scripts/package-macos.sh.
# Tourne sur macOS comme sous Linux (job de publication de la CI).
#
# Usage : scripts/publish-macos.sh <dossier du paquet>
#   BLUELIUM_VERSION  version (ex. 0.22.4.1-glycine), obligatoire
#   BLUELIUM_ARCH     arm64 (défaut) ou x86_64
#   BLUELIUM_SERIE    commit de la série (défaut : tools/couleur.py --serie)
#   BLUELIUM_NOM      nom de la couleur (défaut : tools/couleur.py --nom)
#   BLUELIUM_REPO     dépôt GitHub (défaut : matthieuleconte1/bluelium)
#
# Le dossier contient bluelium-<version>-macos-<arch>.dmg (+ .sha256),
# appcast-<arch>.xml et release-tag-<arch>.txt. Le .dmg rejoint la release
# Linux v<version> si elle existe (même série), sinon la release
# v<version>-macos (jamais « latest », que lit la mise à jour Linux).
# L'appcast va dans la release fixe « appcast ».
set -euo pipefail

DEST=${1:?Usage : $0 <dossier du paquet>}
VERSION=${BLUELIUM_VERSION:?définir BLUELIUM_VERSION}
ARCH=${BLUELIUM_ARCH:-arm64}
REPO=${BLUELIUM_REPO:-matthieuleconte1/bluelium}
B=$(cd "$(dirname "$0")/.." && pwd)
SERIE=${BLUELIUM_SERIE:-$(python3 "$B/tools/couleur.py" "$B" --serie)}
NOM=${BLUELIUM_NOM:-$(python3 "$B/tools/couleur.py" "$B" --nom)}

NAME=bluelium-$VERSION-macos-$ARCH
DMG=$DEST/$NAME.dmg
APPCAST=$DEST/appcast-$ARCH.xml
for f in "$DMG" "$DMG.sha256" "$APPCAST" "$DEST/release-tag-$ARCH.txt"; do
  [ -f "$f" ] || { echo "Introuvable : $f" >&2; exit 1; }
done
TAG=$(cat "$DEST/release-tag-$ARCH.txt")
# L'appcast pointe vers ce tag : il doit être celui qui reçoit le .dmg.
grep -q "/releases/download/$TAG/$NAME.dmg" "$APPCAST" \
  || { echo "L'appcast ne pointe pas vers $TAG/$NAME.dmg" >&2; exit 1; }

if [ "$TAG" = "v$VERSION" ]; then
  NOTES=$(gh release view "v$VERSION" --repo "$REPO" --json body -q .body) \
    || { echo "Release v$VERSION introuvable" >&2; exit 1; }
  case "$NOTES" in
    *"série $SERIE"*) ;;
    *) echo "v$VERSION existe avec une autre série que $SERIE : couleur déjà prise" >&2; exit 1 ;;
  esac
  gh release upload "v$VERSION" "$DMG" "$DMG.sha256" --repo "$REPO" --clobber
  echo "Ajouté à la release v$VERSION"
elif gh release view "$TAG" --repo "$REPO" >/dev/null 2>&1; then
  gh release upload "$TAG" "$DMG" "$DMG.sha256" --repo "$REPO" --clobber
  echo "Release $TAG mise à jour"
else
  gh release create "$TAG" "$DMG" "$DMG.sha256" --repo "$REPO" \
    --latest=false --title "Bluelium $VERSION (macOS)" \
    --notes "Construit sur Helium macOS ${VERSION%%-*}, série $SERIE ($NOM). macOS $ARCH, signé avec le certificat auto-signé Bluelium.

Notes de version : docs/patch-notes/$VERSION.html

Installation : voir le README. Les versions suivantes s'installent ensuite toutes seules (Sparkle)."
  echo "Release $TAG publiée"
fi

if ! gh release view appcast --repo "$REPO" >/dev/null 2>&1; then
  gh release create appcast --repo "$REPO" --latest=false --prerelease \
    --title "Appcast (mises à jour macOS)" \
    --notes "Fichiers lus par la mise à jour intégrée de Bluelium. Ne pas supprimer."
fi
gh release upload appcast "$APPCAST" --repo "$REPO" --clobber
echo "Appcast publié : $TAG"
