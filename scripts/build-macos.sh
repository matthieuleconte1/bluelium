#!/usr/bin/env bash
# Bluelium — build macOS (Apple Silicon) sur le Mac, à partir de helium-macos.
#
# Même déroulé que l'auto-build Linux : dernière version publiée de
# imputnet/helium-macos, étapes de Helium (patchs, substitutions, traductions,
# ressources), PUIS la série Bluelium (specs/SERIES, plateforme « mac »),
# compilation, et paquet Bluelium.app + .dmg (scripts/package-macos.sh).
#
# Usage : scripts/build-macos.sh [arm64|x86_64]
#
# Variables :
#   BLUELIUM_MAC_WORK  dossier de travail (défaut : ~/bluelium-build). Il faut
#                      un volume APFS (ou HFS+) avec ≥ MIN_FREE_GB Go libres :
#                      exFAT ne gère pas les liens symboliques de Chromium.
#                      Sur un disque externe exFAT, créer une image APFS :
#                        hdiutil create -size 200g -type SPARSEBUNDLE -fs APFS \
#                          -volname BlueliumBuild /Volumes/Medock/bluelium.sparsebundle
#                        hdiutil attach /Volumes/Medock/bluelium.sparsebundle
#                        BLUELIUM_MAC_WORK=/Volumes/BlueliumBuild scripts/build-macos.sh
#   HELIUM_TAG         version de helium-macos (défaut : la dernière publiée)
#   JOBS               tâches de compilation en parallèle (défaut : 8, 18 Go de RAM)
#   PGO                false pour couper le profil PGO (défaut : true, comme Helium)
#   PATCH_ONLY=1       s'arrête après la série Bluelium (vérifie qu'elle s'applique)
#   SKIP_FETCH=1       garde build/src tel quel et relance seulement gn + compilation
#   MIN_FREE_GB        espace minimal exigé (défaut : 100)
#   PUBLISH=1          publie le .dmg sur GitHub (voir package-macos.sh)
#   KEEP_GOING=1       continue malgré les erreurs (pour toutes les voir d'un coup)
set -Eeuo pipefail

ARCH=${1:-arm64}
case "$ARCH" in arm64|x86_64) ;; *) echo "Usage : $0 [arm64|x86_64]" >&2; exit 2 ;; esac
[ "$(uname -s)" = Darwin ] || { echo "Ce script tourne sur macOS." >&2; exit 1; }

B=$(cd "$(dirname "$0")/.." && pwd)
WORK=${BLUELIUM_MAC_WORK:-$HOME/bluelium-build}
W=$WORK/helium-macos
JOBS=${JOBS:-8}
MIN_FREE_GB=${MIN_FREE_GB:-100}
mkdir -p "$WORK"
LOG=$WORK/build-macos.log
exec > >(tee -a "$LOG") 2>&1
echo "=== $(date '+%F %T') build macOS ($ARCH) dans $WORK"

die() { echo "ÉCHEC : $*" >&2; exit 1; }
trap 'die "erreur inattendue (ligne $LINENO), voir $LOG"' ERR

# 1. Prérequis (voir helium-macos/docs/building.md).
for tool in greadlink zstd wget python3 git; do
  command -v "$tool" >/dev/null || die "$tool manquant : brew install python@3.13 wget zstd coreutils readline"
done
python3 -c 'import requests, PIL' 2>/dev/null \
  || die "modules Python manquants : python3 -m pip install --user --break-system-packages requests pillow"
# xcrun -f trouve un lanceur même sans la chaîne : il faut exécuter metal.
xcrun metal --version 2>&1 | grep -q '^Apple metal' \
  || die "chaîne Metal absente : xcodebuild -downloadComponent MetalToolchain"
mount_point=$(df -P "$WORK" | awk 'NR==2 {sub(/^([^ ]+ +){5}/, ""); print}')
fs=$(diskutil info "$mount_point" 2>/dev/null \
     | awk -F: '/File System Personality/ {gsub(/^ +/, "", $2); print $2}')
case "$fs" in
  *APFS*|*HFS*) ;;
  *) die "$WORK est sur « ${fs:-inconnu} » : il faut APFS ou HFS+ (voir l'en-tête du script)" ;;
esac
free_gb=$(df -g "$WORK" | awk 'NR==2 {print $4}')
if [ "${SKIP_FETCH:-0}" != 1 ] && [ "$free_gb" -lt "$MIN_FREE_GB" ]; then
  die "$free_gb Go libres sur le volume de $WORK, il en faut $MIN_FREE_GB (MIN_FREE_GB pour forcer)"
fi

# 2. helium-macos à la version voulue, avec helium-chromium (sous-module).
if [ ! -d "$W/.git" ]; then
  git clone https://github.com/imputnet/helium-macos.git "$W"
fi
git -C "$W" fetch --quiet --tags --force origin
TAG=${HELIUM_TAG:-$(git -C "$W" tag -l '[0-9]*' | sort -V | tail -1)}
[ -n "$TAG" ] || die "aucune version trouvée sur imputnet/helium-macos"
PATCH_ID=$(git -C "$B" log -1 --format=%h -- specs patches downloads.ini \
           tools/apply_spec.py tools/apply-series.py scripts/package-macos.sh)
VERSION="$TAG-g$PATCH_ID"
echo "Bluelium $VERSION (helium-macos $TAG)"

export _root_dir=$W
if [ "${SKIP_FETCH:-0}" != 1 ]; then
  git -C "$W" checkout --quiet --force "$TAG"
  git -C "$W" clean -fdq -- patches downloads.ini
  git -C "$W" submodule update --quiet --init --recursive --force

  # Sources en plus de Bluelium (Shimmer Tab…) : tout sauf l'archive Chromium
  # Linux, que helium-macos remplace par la sienne.
  python3 - "$B/downloads.ini" >> "$W/downloads.ini" <<'PY'
import configparser, sys
src = configparser.RawConfigParser(); src.read(sys.argv[1])
out = configparser.RawConfigParser()
for section in src.sections():
    if not section.startswith('chromium-'):
        out[section] = src[section]
print()
out.write(sys.stdout)
PY

  # 3. Étapes de Helium (prepare_sources : téléchargement, élagage, patchs,
  #    substitutions, traductions, version, ressources), sur un arbre neuf.
  rm -rf "$W/build/src" "$W/build/subs.tar.gz" "$W/build/namesubs.tar"
  # shellcheck source=/dev/null
  source "$W/devutils/shared.sh"
  prepare_sources true

  # 4. Série Bluelium sur l'arbre final, comme sous Linux.
  rm -rf "$WORK/patches-$VERSION"
  if ! python3 "$B/tools/apply-series.py" "$_src_dir" "$B" "$WORK/patches-$VERSION" mac \
       > "$WORK/series.log" 2>&1; then
    tail -20 "$WORK/series.log"
    die "un patch Bluelium ne s'applique pas sur Helium macOS $TAG : $(grep -m1 'ÉCHEC' "$WORK/series.log" | cut -c1-160)"
  fi
  cat "$WORK/series.log"
  echo "$VERSION" > "$WORK/series.version"
else
  # shellcheck source=/dev/null
  source "$W/devutils/shared.sh"
  [ -d "$_src_dir" ] || die "SKIP_FETCH=1 mais $_src_dir n'existe pas"
  VERSION=$(cat "$WORK/series.version" 2>/dev/null || echo "$VERSION")
fi

if [ "${PATCH_ONLY:-0}" = 1 ]; then
  trap - ERR
  echo "=== série appliquée (PATCH_ONLY), patchs régénérés dans $WORK/patches-$VERSION"
  exit 0
fi

# 5. Configuration et compilation (release : is_official_build, PGO).
write_gn_args "$ARCH" release
if [ "${PGO:-true}" = false ]; then
  sed -i '' '/^chrome_pgo_phase=/d' "$_out_dir/args.gn"
  echo 'chrome_pgo_phase=0' >> "$_out_dir/args.gn"
fi
gn_gen
helium_build -j "$JOBS" ${KEEP_GOING:+-k 0} || die "la compilation a échoué pour $VERSION"

# 6. Paquet Bluelium.app + .dmg (et publication si PUBLISH=1).
BLUELIUM_VERSION=$VERSION BLUELIUM_ARCH=$ARCH \
  "$B/scripts/package-macos.sh" "$_out_dir" "$WORK/releases"
trap - ERR
echo "=== $(date '+%F %T') terminé : $VERSION"
