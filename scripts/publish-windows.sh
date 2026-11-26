#!/usr/bin/env bash
# Bluelium — publie sur GitHub l'installateur Windows fait par
# scripts/build-windows.py package (job « publication » de build-windows.yml).
#
# Usage : scripts/publish-windows.sh <dossier du paquet>
#   BLUELIUM_VERSION  version (ex. 0.22.5.1-vert-celadon), obligatoire
#   BLUELIUM_SERIE    commit de la série (défaut : tools/couleur.py --serie)
#   BLUELIUM_NOM      nom de la couleur (défaut : tools/couleur.py --nom)
#   BLUELIUM_REPO     dépôt GitHub (défaut : matthieuleconte1/bluelium)
#
# L'installateur rejoint la release v<version> si elle existe (même série),
# sinon la release v<version>-windows (jamais « latest », que lit la mise à
# jour Linux).
set -euo pipefail

DEST=${1:?Usage : $0 <dossier du paquet>}
VERSION=${BLUELIUM_VERSION:?définir BLUELIUM_VERSION}
REPO=${BLUELIUM_REPO:-matthieuleconte1/bluelium}
B=$(cd "$(dirname "$0")/.." && pwd)
SERIE=${BLUELIUM_SERIE:-$(python3 "$B/tools/couleur.py" "$B" --serie)}
NOM=${BLUELIUM_NOM:-$(python3 "$B/tools/couleur.py" "$B" --nom)}

EXE=$DEST/bluelium-$VERSION-windows-x64-installer.exe
for f in "$EXE" "$EXE.sha256"; do
  [ -f "$f" ] || { echo "Introuvable : $f" >&2; exit 1; }
done
(cd "$DEST" && sha256sum -c "$(basename "$EXE").sha256")

if NOTES=$(gh release view "v$VERSION" --repo "$REPO" --json body -q .body 2>/dev/null); then
  case "$NOTES" in
    *"série $SERIE"*) ;;
    *) echo "v$VERSION existe avec une autre série que $SERIE : couleur déjà prise" >&2; exit 1 ;;
  esac
  gh release upload "v$VERSION" "$EXE" "$EXE.sha256" --repo "$REPO" --clobber
  echo "Ajouté à la release v$VERSION"
elif gh release view "v$VERSION-windows" --repo "$REPO" >/dev/null 2>&1; then
  gh release upload "v$VERSION-windows" "$EXE" "$EXE.sha256" --repo "$REPO" --clobber
  echo "Release v$VERSION-windows mise à jour"
else
  gh release create "v$VERSION-windows" "$EXE" "$EXE.sha256" --repo "$REPO" \
    --latest=false --title "Bluelium $VERSION (Windows)" \
    --notes "Construit sur Helium Windows ${VERSION%%-*}, série $SERIE ($NOM). Windows x64, non signé : SmartScreen demande une confirmation au premier lancement.

Notes de version : docs/patch-notes/$VERSION.html

Installation : voir le README. Pas de mise à jour intégrée pour l'instant."
  echo "Release v$VERSION-windows publiée"
fi
