#!/usr/bin/env bash
# Bluelium : la série s'applique-t-elle sur une version de Helium Linux ?
# Prépare les sources comme l'auto-build (téléchargement, élagage, patchs de
# Helium, substitutions, traductions, version, ressources), applique la série
# Bluelium (plateforme linux), et s'arrête là : pas de compilation.
#
# Usage : tools/test-serie-helium.sh <version helium-linux> <dossier de travail>
# Sorties dans le dossier de travail :
#   resultat.txt   ok | helium | bluelium (étape qui a échoué)
#   helium.log     étapes de Helium     series.log  série Bluelium
#   patches/       patchs Bluelium régénérés (si la série passe)
# Code de sortie : 0 la série passe, 1 échec côté Helium, 2 échec Bluelium.
# Utilisé par .github/workflows/veille-helium.yml ; marche aussi à la main
# sur Linux (~10 Go de disque).
set -Eeuo pipefail
TAG=${1:?version de helium-linux}
WORK=$(mkdir -p "${2:?dossier de travail}" && cd "$2" && pwd)
B=$(cd "$(dirname "$0")/.." && pwd)
W=$WORK/helium-linux
res() { echo "$1" > "$WORK/resultat.txt"; }
res helium

[ -d "$W/.git" ] || git clone --quiet https://github.com/imputnet/helium-linux.git "$W"
git -C "$W" fetch --quiet --tags --force origin
git -C "$W" checkout --quiet --force "$TAG"
git -C "$W" clean -fdq -- patches downloads.ini
git -C "$W" submodule update --quiet --init --recursive --force

# Sources en plus de Bluelium, comme l'auto-build.
python3 - "$B/downloads.ini" >> "$W/downloads.ini" <<'PY'
import configparser, sys
src = configparser.RawConfigParser(); src.read(sys.argv[1])
out = configparser.RawConfigParser()
for section in src.sections():
    if section != 'chromium-linux':
        out[section] = src[section]
print()
out.write(sys.stdout)
PY

cd "$W"
rm -rf build/src build/namesubs.tar build/subs.tar.gz
# shellcheck source=/dev/null
. "$W/scripts/shared.sh"
setup_environment
{
  echo "=== Helium $TAG (Chromium $(cat helium-chromium/chromium_version.txt))"
  fetch_sources false false
  apply_patches
  apply_domsub
  helium_substitution
  helium_apply_translations
  helium_version
  helium_resources
} > "$WORK/helium.log" 2>&1 || { tail -30 "$WORK/helium.log"; exit 1; }

res bluelium
rm -rf "$WORK/patches"
if ! KEEP_GOING=1 python3 "$B/tools/apply-series.py" "$W/build/src" "$B" "$WORK/patches" linux \
     > "$WORK/series.log" 2>&1; then
  grep -E "ÉCHEC|échec" "$WORK/series.log" | head -30
  exit 2
fi
res ok
tail -5 "$WORK/series.log"
