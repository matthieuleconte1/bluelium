#!/usr/bin/env bash
# Bluelium — auto-build (machine de build).
#
# Construit une version complète (PGO) quand Helium publie une nouvelle version
# OU quand les patchs Glyphe envoyés par tools/sync-builder.sh changent.
# Travaille dans /root/helium-auto : l'arbre de développement /root/helium-linux
# (builds incrémentaux) n'est jamais touché.
#
# Entrées (envoyées par sync-builder.sh) :
#   /root/glyphe/autobuild/patches/glyphe/*.patch
#   /root/glyphe/autobuild/patches/series.glyphe   (ordre des patchs Glyphe)
#   /root/glyphe/autobuild/downloads.glyphe.ini    (sources en plus, ex. Shimmer)
#   /root/glyphe/autobuild/helium-wrapper           (lanceur empaqueté)
# Sorties :
#   /root/glyphe/releases/bluelium-<version>.tar.zst (+ .sha256)
#   release GitHub v<version> sur $BLUELIUM_REPO si /root/glyphe/github.env
#   définit GH_TOKEN (jeton limité au dépôt, droit « Contents: write »)
#   /root/glyphe/releases/latest.json   (dernière version réussie)
#   /root/glyphe/releases/status.json   (idle | building | failed, détail)
#
# FORCE=1 reconstruit même si rien n'a changé. PGO=false pour aller plus vite.
set -euo pipefail

G=/root/glyphe
IN=$G/autobuild
W=/root/helium-auto
REL=$G/releases
LOG=$G/autobuild.log
STATE=$G/autobuild.state
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

[ -f "$IN/patches/series.glyphe" ] || fail "patchs Glyphe absents : lancer tools/sync-builder.sh"

# 1. Dernière version publiée de helium-linux.
if [ ! -d "$W/.git" ]; then
  git clone https://github.com/imputnet/helium-linux.git "$W"
fi
cd "$W"
git fetch --quiet --tags --force origin
TAG=$(git tag -l '[0-9]*' | sort -V | tail -1)
[ -n "$TAG" ] || fail "aucune version trouvée sur imputnet/helium-linux"

# 2. Empreinte des patchs Glyphe : un changement déclenche un build.
PATCH_ID=$(cd "$IN" && cat patches/series.glyphe downloads.glyphe.ini helium-wrapper \
           $(sed 's|^|patches/|' patches/series.glyphe) | sha256sum | cut -c1-10)
VERSION="$TAG-g$PATCH_ID"
if [ "${FORCE:-0}" != 1 ] && [ "$(cat "$STATE" 2>/dev/null)" = "$VERSION" ]; then
  echo "À jour : $VERSION"; exit 0
fi
status building "$VERSION"
echo "Build de $VERSION"

# 3. Arbre propre à la version publiée, patchs Glyphe en fin de série.
git checkout --quiet --force "$TAG"
git clean -fdq -- patches downloads.ini
git submodule update --quiet --init --recursive --force
rm -rf patches/glyphe
cp -r "$IN/patches/glyphe" patches/glyphe
cat "$IN/patches/series.glyphe" >> patches/series
printf '\n' >> downloads.ini
cat "$IN/downloads.glyphe.ini" >> downloads.ini

# 4. Sources neuves (le cache de téléchargement est gardé), patchs, build.
export CCACHE_DIR=/root/.ccache CCACHE_MAXSIZE=60G CCACHE_BASEDIR=$W/build/src
rm -rf build/src
. "$W/scripts/shared.sh"
setup_environment
fetch_sources false "${PGO:-true}"
if ! apply_patches > "$G/autobuild-patches.log" 2>&1; then
  tail -20 "$G/autobuild-patches.log"
  fail "un patch ne s'applique plus sur Helium $TAG (voir autobuild-patches.log)"
fi
apply_domsub
helium_substitution
helium_apply_translations
helium_version
helium_resources
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
install -m 755 "$IN/helium-wrapper" "$PKG/helium-wrapper"
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
# 6. Release GitHub (le PC se met à jour depuis là).
if [ -f "$G/github.env" ]; then . "$G/github.env"; fi
if [ -n "${GH_TOKEN:-}" ]; then
  export GH_TOKEN
  gh release create "v$VERSION" "$PKG.tar.zst" "$PKG.tar.zst.sha256" \
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
trap - ERR
status idle "$VERSION prêt"
echo "=== $(date -Is) terminé : $VERSION"
