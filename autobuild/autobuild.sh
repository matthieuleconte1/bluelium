#!/usr/bin/env bash
# Bluelium — auto-build (machine de build).
#
# Construit une version complète (PGO) quand Helium publie une nouvelle version
# OU quand les patchs Bluelium changent sur GitHub (specs/, patches/,
# downloads.ini, lanceur). Travaille dans /root/helium-auto : l'arbre de
# développement /root/helium-linux (builds incrémentaux) n'est jamais touché.
#
# Entrées :
#   imputnet/helium-linux        dernière version publiée (tag)
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
set -Eeuo pipefail  # -E : le piège ERR vaut aussi dans les fonctions de Helium

# Lancé par systemd, le service n'a pas de HOME : les outils Go de Chromium
# (générateur de Dawn/Tint) en ont besoin pour leur cache.
export HOME=${HOME:-/root}
export XDG_CACHE_HOME=${XDG_CACHE_HOME:-$HOME/.cache}

G=/root/glyphe
W=/root/helium-auto
B=/root/bluelium
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
fail() { status failed "$1"; echo "ÉCHEC : $1"; exit 1; }
trap 'status failed "erreur inattendue (ligne $LINENO), voir autobuild.log"' ERR

# 1. Dernière version publiée de helium-linux.
if [ ! -d "$W/.git" ]; then
  git clone https://github.com/imputnet/helium-linux.git "$W"
fi
cd "$W"
git fetch --quiet --tags --force --no-recurse-submodules origin
TAG=$(git tag -l '[0-9]*' | sort -V | tail -1)
[ -n "$TAG" ] || fail "aucune version trouvée sur imputnet/helium-linux"

# 2. Patchs Bluelium : dernier commit de main qui les touche.
if [ ! -d "$B/.git" ]; then
  git clone --quiet "$BLUELIUM_GIT" "$B"
fi
git -C "$B" fetch --quiet origin main
git -C "$B" checkout --quiet --force origin/main
PATCH_ID=$(git -C "$B" log -1 --format=%h -- specs patches downloads.ini \
           autobuild/helium-wrapper tools/apply_spec.py tools/apply-series.py \
           ':!specs/macos_*' ':!patches/glyphe/macos-*')
VERSION="$TAG-g$PATCH_ID"
if [ "${FORCE:-0}" != 1 ] && [ "$(cat "$STATE" 2>/dev/null)" = "$VERSION" ]; then
  echo "À jour : $VERSION"; exit 0
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
OUT=$W/build/src/out/Default
PKG=$REL/bluelium-$VERSION
rm -rf "$PKG"; mkdir -p "$PKG/locales"
for f in helium chrome_100_percent.pak chrome_200_percent.pak helium_crashpad_handler \
         icudtl.dat libEGL.so libGLESv2.so libqt5_shim.so libqt6_shim.so \
         libvk_swiftshader.so libvulkan.so.1 product_logo_256.png resources.pak \
         v8_context_snapshot.bin vk_swiftshader_icd.json xdg-mime xdg-settings; do
  [ -e "$OUT/$f" ] && cp -r "$OUT/$f" "$PKG/"
done
cp "$OUT"/locales/*.pak "$PKG/locales/"
strip "$PKG/helium"
install -m 755 "$B/autobuild/helium-wrapper" "$PKG/helium-wrapper"
echo "$VERSION" > "$PKG/VERSION"
tar -C "$REL" -cf - "bluelium-$VERSION" | zstd -q -T0 -10 -o "$PKG.tar.zst" -f
rm -rf "$PKG"
SHA=$(sha256sum "$PKG.tar.zst" | cut -d' ' -f1)
echo "$SHA  bluelium-$VERSION.tar.zst" > "$PKG.tar.zst.sha256"
python3 - "$REL/latest.json" "$VERSION" "bluelium-$VERSION.tar.zst" "$SHA" <<'PY'
import json, sys, datetime
path, version, name, sha = sys.argv[1:]
json.dump({'version': version, 'file': name, 'sha256': sha,
           'time': datetime.datetime.now().astimezone().isoformat(timespec='seconds')},
          open(path, 'w'), indent=1)
PY
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
if [ -f "$G/github.env" ]; then . "$G/github.env"; fi
if [ -n "${GH_TOKEN:-}" ]; then
  export GH_TOKEN
  gh release create "v$VERSION" "${ASSETS[@]}" \
     --repo "${BLUELIUM_REPO:-matthieuleconte1/bluelium}" \
     --title "Bluelium $VERSION" \
     --notes "Construit automatiquement sur Helium $TAG (Chromium $(cat "$W/chromium_version.txt" 2>/dev/null || echo '?')), patchs Bluelium $PATCH_ID. Linux x86_64.

Installation et mise à jour automatique : voir le README." \
    || fail "publication de la release GitHub échouée pour $VERSION"
else
  echo "Pas de GH_TOKEN : release GitHub non publiée."
fi
echo "$VERSION" > "$STATE"
# On garde les trois derniers paquets.
ls -1t "$REL"/bluelium-*.tar.zst | tail -n +4 | while read -r old; do rm -f "$old" "$old.sha256"; done
ls -1t "$REL"/Bluelium-*.AppImage 2>/dev/null | tail -n +4 | while read -r old; do rm -f "$old" "$old.sha256" "$old.zsync"; done
trap - ERR
status idle "$VERSION prêt"
echo "=== $(date -Is) terminé : $VERSION"
