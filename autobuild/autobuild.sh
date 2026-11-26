#!/usr/bin/env bash
# Bluelium — auto-build (machine de build).
#
# Construit une version complète (PGO) quand Helium publie une nouvelle version
# stable (petites versions comprises, tools/helium-tag.py latest) OU quand les patchs Bluelium changent sur GitHub (specs/, patches/,
# downloads.ini, lanceur). Travaille dans /root/helium-auto : l'arbre de
# développement /root/helium-linux (builds incrémentaux) n'est jamais touché.
#
# Entrées :
#   imputnet/helium-linux        dernière version stable
#   $BLUELIUM_GIT (branche main) specs/SERIES, specs/, patches/glyphe/,
#                                downloads.ini, autobuild/helium-wrapper
# Sorties :
#   /root/glyphe/releases/bluelium-<version>.tar.zst (+ .sha256)
#   release GitHub v<version> sur $BLUELIUM_REPO si /root/glyphe/github.env
#   définit GH_TOKEN (jeton limité au dépôt, droit « Contents: write »)
#   /root/glyphe/releases/patches-<version>/  patchs régénérés sur cette version
#   /root/glyphe/releases/latest.json   (dernière version réussie)
#   /root/glyphe/releases/status.json   (idle | building | failed, détail)
#
# FORCE=1 reconstruit même si rien n'a changé. PGO=false pour aller plus vite.
# PATCH_ONLY=1 s'arrête après la série Bluelium (vérifie qu'elle s'applique).
# Build de test d'une branche, sans rien publier :
#   BLUELIUM_BRANCH=<branche> PUBLISH=0 HELIUM_TAG=<tag> FORCE=1 PGO=false \
#   BLUELIUM_WORK=/root/helium-test BLUELIUM_CLONE=/root/bluelium-test
# PUBLISH=0 : pas de release GitHub, état (autobuild.state, latest.json) intact.
set -Eeuo pipefail  # -E : le piège ERR vaut aussi dans les fonctions de Helium

# Lancé par systemd, le service n'a pas de HOME : les outils Go de Chromium
# (générateur de Dawn/Tint) en ont besoin pour leur cache.
export HOME=${HOME:-/root}
export XDG_CACHE_HOME=${XDG_CACHE_HOME:-$HOME/.cache}

G=/root/glyphe
# BLUELIUM_WORK / BLUELIUM_CLONE : autres dossiers, pour un build de test qui
# ne touche pas l'arbre de l'auto-build de nuit.
W=${BLUELIUM_WORK:-/root/helium-auto}
B=${BLUELIUM_CLONE:-/root/bluelium}
REL=$G/releases
LOG=$G/autobuild.log
STATE=$G/autobuild.state
BLUELIUM_GIT=${BLUELIUM_GIT:-https://github.com/matthieuleconte1/bluelium.git}
mkdir -p "$REL"
exec 9>/run/glyphe-autobuild.lock
flock -n 9 || { echo "Un auto-build tourne déjà."; exit 0; }
exec > >(tee -a "$LOG") 2>&1
echo "=== $(date -Is) auto-build"

status() {  # état, détail
  python3 - "$REL/status.json" "$1" "$2" <<'PY'
import json, sys, datetime
path, state, detail = sys.argv[1:]
json.dump({'state': state, 'detail': detail,
           'time': datetime.datetime.now().astimezone().isoformat(timespec='seconds')},
          open(path, 'w'), ensure_ascii=False, indent=1)
PY
}
# Jeton GitHub (releases, issues) : droits « Contents: write » et « Issues: write ».
if [ -f "$G/github.env" ]; then . "$G/github.env"; fi
[ -z "${GH_TOKEN:-}" ] || export GH_TOKEN
REPO=${BLUELIUM_REPO:-matthieuleconte1/bluelium}
LOG_START=$(wc -l < "$LOG"); START_TS=$(date +%s)

# Échec : issue GitHub « auto-build » (une seule ouverte à la fois : un nouvel
# échec y ajoute un commentaire). Fermée au build réussi suivant. Rien pour
# les builds de test (PUBLISH=0).
issue_echec() {
  [ "${PUBLISH:-1}" = 1 ] && [ -n "${GH_TOKEN:-}" ] || return 0
  local body num
  body=$(mktemp)
  {
    echo "**Auto-build Linux : échec** ($(date -u '+%F %H:%M') UTC)"
    echo
    echo "$1"
    echo
    echo "Version : \`${VERSION:-?}\` (Helium ${TAG:-?}), branche \`${BRANCH:-main}\`."
    if [ -s "$G/autobuild-series.log" ] && grep -q 'ÉCHEC' "$G/autobuild-series.log" \
       && [ "$(stat -c %Y "$G/autobuild-series.log")" -ge "$START_TS" ]; then
      echo; echo "Série Bluelium :"; echo; echo '```'
      grep -A6 'ÉCHEC' "$G/autobuild-series.log" | head -40 || true; echo '```'
    fi
    echo; echo "Fin du journal (\`/root/glyphe/autobuild.log\`) :"; echo; echo '```'
    tail -n +"$((LOG_START + 1))" "$LOG" | tr '\r' '\n' | grep -v '^\[[0-9]*/[0-9]*\]' | tail -30 || true
    echo '```'
  } > "$body"
  gh label create auto-build --repo "$REPO" --color d73a4a \
     --description "Échec de l'auto-build Linux" >/dev/null 2>&1 || true
  num=$(gh issue list --repo "$REPO" --label auto-build --state open --limit 1 \
          --json number --jq '.[0].number' 2>/dev/null || true)
  if [ -n "$num" ]; then
    gh issue comment "$num" --repo "$REPO" --body-file "$body" >/dev/null \
      && echo "Échec ajouté à l'issue #$num" || echo "Issue GitHub : commentaire impossible (droit « Issues: write » ?)"
  else
    gh issue create --repo "$REPO" --label auto-build \
       --title "Auto-build : échec ${VERSION:-} — ${1:0:80}" --body-file "$body" \
      || echo "Issue GitHub : création impossible (droit « Issues: write » ?)"
  fi
  rm -f "$body"
}
issue_succes() {
  [ "${PUBLISH:-1}" = 1 ] && [ -n "${GH_TOKEN:-}" ] || return 0
  local num
  for num in $(gh issue list --repo "$REPO" --label auto-build --state open \
                 --json number --jq '.[].number' 2>/dev/null); do
    gh issue close "$num" --repo "$REPO" \
       --comment "Réparé : $VERSION construit et publié ($(date -u '+%F %H:%M') UTC)." >/dev/null || true
  done
}
fail() { trap - ERR; status failed "$1"; echo "ÉCHEC : $1"; issue_echec "$1" || true; exit 1; }
trap 'fail "erreur inattendue (ligne $LINENO), voir autobuild.log"' ERR

# 1. Dépôt helium-linux (tags).
if [ ! -d "$W/.git" ]; then
  git clone https://github.com/imputnet/helium-linux.git "$W"
fi
cd "$W"
git fetch --quiet --tags --force --no-recurse-submodules origin

# 2. Patchs Bluelium : dernier commit de main qui les touche.
if [ ! -d "$B/.git" ]; then
  git clone --quiet "$BLUELIUM_GIT" "$B"
fi
BRANCH=${BLUELIUM_BRANCH:-main}
git -C "$B" fetch --quiet origin "$BRANCH"
git -C "$B" checkout --quiet --force "origin/$BRANCH"

# Version de Helium : la dernière stable, petites versions comprises ; les
# pré-versions sont ignorées (tools/helium-tag.py latest). HELIUM_TAG force
# une version.
CUR=$(cat "$STATE" 2>/dev/null || true); CUR=${CUR%%-*}
TAG=${HELIUM_TAG:-$(python3 "$B/tools/helium-tag.py" latest imputnet/helium-linux "$CUR")}
[ -n "$TAG" ] || fail "aucune version trouvée sur imputnet/helium-linux"
git rev-parse --quiet --verify "refs/tags/$TAG" >/dev/null \
  || fail "la version $TAG de helium-linux n'existe pas"
PATCH_ID=$(git -C "$B" log -1 --format=%h -- specs patches downloads.ini \
           autobuild/helium-wrapper autobuild/glyphe-update \
           tools/apply_spec.py tools/apply-series.py \
           tools/rename-product.py \
           ':!specs/macos_*' ':!patches/glyphe/macos-*')
# Version publiée : Helium + couleur de la série (tools/couleur.py), la même
# que sur macOS pour les mêmes patchs. KEY (avec PATCH_ID, qui suit aussi
# l'emballage Linux) décide seule s'il faut reconstruire.
COULEUR=$(python3 "$B/tools/couleur.py" "$B")
SERIE=$(python3 "$B/tools/couleur.py" "$B" --serie)
VERSION="$TAG-$COULEUR"
KEY="$TAG-g$PATCH_ID"
if [ "${FORCE:-0}" != 1 ] && [ "$(cat "$STATE" 2>/dev/null)" = "$KEY" ]; then
  echo "À jour : $VERSION ($KEY)"; exit 0
fi
status building "$VERSION"
echo "Build de $VERSION"

# 3. Arbre propre à la version publiée de Helium (sa série seule) et sources
#    en plus de Bluelium (tout ce qui suit [chromium-linux] dans downloads.ini).
git checkout --quiet --force "$TAG"
git clean -fdq -- patches downloads.ini
git submodule update --quiet --init --recursive --force
python3 - "$B/downloads.ini" >> downloads.ini <<'PY'
import configparser, sys
src = configparser.RawConfigParser(); src.read(sys.argv[1])
out = configparser.RawConfigParser()
for section in src.sections():
    if section != 'chromium-linux':
        out[section] = src[section]
print()
out.write(sys.stdout)
PY

# 4. Sources neuves (le cache de téléchargement est gardé), étapes de Helium,
#    puis la série Bluelium sur l'arbre final, comme dans l'arbre de dev.
export CCACHE_DIR=/root/.ccache CCACHE_MAXSIZE=60G CCACHE_BASEDIR=$W/build/src
# Caches de substitution de Helium : leur présence fait échouer la relance.
rm -rf build/src build/namesubs.tar build/subs.tar.gz
. "$W/scripts/shared.sh"
setup_environment
fetch_sources false "${PGO:-true}"
apply_patches > "$G/autobuild-patches.log" 2>&1 \
  || fail "les patchs de Helium $TAG ne s'appliquent pas (voir autobuild-patches.log)"
apply_domsub
helium_substitution
helium_apply_translations
helium_version
helium_resources
rm -rf "$REL/patches-$VERSION"
if ! python3 "$B/tools/apply-series.py" "$W/build/src" "$B" "$REL/patches-$VERSION" linux \
     > "$G/autobuild-series.log" 2>&1; then
  tail -20 "$G/autobuild-series.log"
  fail "un patch Bluelium ne s'applique plus sur Helium $TAG : $(grep -m1 'ÉCHEC' "$G/autobuild-series.log" | cut -c1-120)"
fi
cat "$G/autobuild-series.log"
if [ "${PATCH_ONLY:-0}" = 1 ]; then
  trap - ERR
  status idle "$VERSION : série appliquée (PATCH_ONLY), pas de build"
  echo "=== $(date -Is) série appliquée, arrêt (PATCH_ONLY)"
  exit 0
fi
write_gn_args
gn_gen
build -j "${JOBS:-32}" || fail "la compilation a échoué pour $VERSION"

# 5. Paquet : mêmes fichiers que le paquet officiel, binaire allégé.
#    package <out> <fichier .tar.zst> <strip> : le dossier dans l'archive
#    s'appelle toujours bluelium-<version> (lu par make-appimage.sh).
package() {
  local out=$1 tarball=$2 strip_bin=$3 pkg=$REL/bluelium-$VERSION
  rm -rf "$pkg"; mkdir -p "$pkg/locales"
  for f in helium chrome_100_percent.pak chrome_200_percent.pak helium_crashpad_handler \
           icudtl.dat libEGL.so libGLESv2.so libqt5_shim.so libqt6_shim.so \
           libvk_swiftshader.so libvulkan.so.1 product_logo_256.png resources.pak \
           v8_context_snapshot.bin vk_swiftshader_icd.json xdg-mime xdg-settings; do
    [ -e "$out/$f" ] && cp -r "$out/$f" "$pkg/"
  done
  cp "$out"/locales/*.pak "$pkg/locales/"
  "$strip_bin" "$pkg/helium"
  install -m 755 "$B/autobuild/helium-wrapper" "$pkg/helium-wrapper"
  # Le lanceur remet à jour ~/.local/bin/glyphe-update avec celui-ci.
  install -m 755 "$B/autobuild/glyphe-update" "$pkg/glyphe-update"
  echo "$VERSION" > "$pkg/VERSION"
  tar -C "$REL" -cf - "bluelium-$VERSION" | zstd -q -T0 -10 -o "$tarball" -f
  rm -rf "$pkg"
  ( cd "$(dirname "$tarball")" && sha256sum "$(basename "$tarball")" > "$tarball.sha256" )
}
OUT=$W/build/src/out/Default
PKG=$REL/bluelium-$VERSION
package "$OUT" "$PKG.tar.zst" strip
SHA=$(cut -d' ' -f1 "$PKG.tar.zst.sha256")
if [ "${PUBLISH:-1}" = 1 ]; then
python3 - "$REL/latest.json" "$VERSION" "bluelium-$VERSION.tar.zst" "$SHA" <<'PY'
import json, sys, datetime
path, version, name, sha = sys.argv[1:]
json.dump({'version': version, 'file': name, 'sha256': sha,
           'time': datetime.datetime.now().astimezone().isoformat(timespec='seconds')},
          open(path, 'w'), indent=1)
PY
fi
# 5 bis. AppImage (même contenu, un seul fichier exécutable).
ASSETS=("$PKG.tar.zst" "$PKG.tar.zst.sha256")
if bash "$B/autobuild/make-appimage.sh" "$PKG.tar.zst" "$REL"; then
  ASSETS+=("$REL/Bluelium-$VERSION-x86_64.AppImage"
           "$REL/Bluelium-$VERSION-x86_64.AppImage.sha256"
           "$REL/Bluelium-$VERSION-x86_64.AppImage.zsync")
else
  echo "AppImage non produite (le paquet tar.zst reste publié)."
fi
# 6. Release GitHub (le PC se met à jour depuis là).
if [ "${PUBLISH:-1}" != 1 ]; then
  echo "PUBLISH=0 : build de test, rien n'est publié ($VERSION, branche $BRANCH)."
elif [ -n "${GH_TOKEN:-}" ]; then
  if NOTES=$(gh release view "v$VERSION" --repo "$REPO" --json body -q .body 2>/dev/null); then
    # Release déjà là : même série (seul l'emballage Linux a changé), on
    # remplace ses fichiers ; autre série tombée sur la même couleur, on
    # s'arrête (les mises à jour, qui comparent les versions, la rateraient).
    case "$NOTES" in
      *"série $SERIE"*) ;;
      *) fail "la couleur $COULEUR est déjà prise sur Helium $TAG par une autre série (v$VERSION) : un nouveau commit de la série change de couleur" ;;
    esac
    gh release upload "v$VERSION" "${ASSETS[@]}" --repo "$REPO" --clobber \
      || fail "mise à jour de la release GitHub échouée pour $VERSION"
  else
    gh release create "v$VERSION" "${ASSETS[@]}" \
       --repo "$REPO" \
       --title "Bluelium $VERSION" \
       --notes "Construit automatiquement sur Helium $TAG (Chromium $(cat "$W/chromium_version.txt" 2>/dev/null || echo '?')), série $SERIE ($(python3 "$B/tools/couleur.py" "$B" --nom)), paquet $PATCH_ID. Linux x86_64 ; arm64 (aarch64) ajouté quelques heures après.

Installation et mise à jour automatique : voir le README." \
      || fail "publication de la release GitHub échouée pour $VERSION"
  fi
else
  echo "Pas de GH_TOKEN : release GitHub non publiée."
fi
[ "${PUBLISH:-1}" != 1 ] || echo "$KEY" > "$STATE"

# 7. Deuxième temps : arm64 (aarch64, Asahi Linux…), compilé en croisé sur le
#    même arbre (sysroot Debian arm64 de Chromium), sans PGO (Helium n'a de
#    profil que pour x64). Ajouté à la release x86_64 déjà publiée. Un échec
#    ici n'annule pas la release x86_64 : l'état le signale, FORCE=1 relance
#    tout. ARM64=0 saute cette étape.
if [ "${ARM64:-1}" = 1 ]; then
  arm_fail() { fail "arm64 : $1 (x86_64 publié : $VERSION)"; }
  trap 'arm_fail "erreur inattendue (ligne $LINENO), voir autobuild.log"' ERR
  status building "$VERSION arm64"
  echo "=== $(date -Is) arm64 : $VERSION"
  ARM_OUT=$W/build/src/out/arm64
  rm -rf "$ARM_OUT"
  _out_dir=$ARM_OUT _build_arch=arm64 _has_pgo=false write_gn_args
  ( cd "$W/build/src" && ./buildtools/linux64/gn gen out/arm64 --fail-on-unused-args ) \
    || arm_fail "gn gen"
  _out_dir=$ARM_OUT build -j "${JOBS:-32}" || arm_fail "la compilation a échoué"
  # .tzst et non .tar.zst : les anciens glyphe-update prennent la première
  # archive .tar.zst de la release, sans regarder l'architecture.
  ARM_TAR=$REL/bluelium-$VERSION-aarch64.tzst
  package "$ARM_OUT" "$ARM_TAR" "$W/build/src/third_party/llvm-build/Release+Asserts/bin/llvm-strip"
  ARM_ASSETS=("$ARM_TAR" "$ARM_TAR.sha256")
  if APPIMAGE_ARCH=aarch64 bash "$B/autobuild/make-appimage.sh" "$ARM_TAR" "$REL"; then
    ARM_ASSETS+=("$REL/Bluelium-$VERSION-aarch64.AppImage"
                 "$REL/Bluelium-$VERSION-aarch64.AppImage.sha256"
                 "$REL/Bluelium-$VERSION-aarch64.AppImage.zsync")
  else
    echo "AppImage arm64 non produite (le paquet .tzst reste publié)."
  fi
  rm -rf "$ARM_OUT"
  if [ "${PUBLISH:-1}" = 1 ] && [ -n "${GH_TOKEN:-}" ]; then
    gh release upload "v$VERSION" "${ARM_ASSETS[@]}" --repo "$REPO" --clobber \
      || arm_fail "ajout à la release v$VERSION échoué"
    echo "arm64 ajouté à la release v$VERSION"
  fi
fi

# On garde les trois derniers paquets de chaque architecture.
ls -1t "$REL"/bluelium-*.tar.zst | grep -v -- '-aarch64\.tar\.zst$' | tail -n +4 \
  | while read -r old; do rm -f "$old" "$old.sha256"; done
ls -1t "$REL"/bluelium-*-aarch64.tzst "$REL"/bluelium-*-aarch64.tar.zst 2>/dev/null | tail -n +4 \
  | while read -r old; do rm -f "$old" "$old.sha256"; done
for arch in x86_64 aarch64; do
  ls -1t "$REL"/Bluelium-*-$arch.AppImage 2>/dev/null | tail -n +4 \
    | while read -r old; do rm -f "$old" "$old.sha256" "$old.zsync"; done
done
trap - ERR
if [ "${PUBLISH:-1}" != 1 ]; then
  status idle "test $VERSION ($BRANCH) prêt, non publié"
  echo "=== $(date -Is) terminé (test) : $VERSION"
else
  status idle "$VERSION prêt"
  issue_succes
  echo "=== $(date -Is) terminé : $VERSION"
fi
