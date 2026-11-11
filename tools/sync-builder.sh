#!/usr/bin/env bash
# Envoie les patchs Glyphe et l'auto-build au conteneur CT 118.
#   tools/sync-builder.sh          envoie seulement (build à la prochaine nuit)
#   tools/sync-builder.sh --now    envoie et lance l'auto-build tout de suite
set -euo pipefail
cd "$(dirname "$0")/.."
SSH=(tools/builder-ssh.sh)  # hôte dans ~/.config/bluelium/builder.env
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/autobuild/patches"
grep '^glyphe/' patches/series > "$tmp/autobuild/patches/series.glyphe"
while read -r p; do
  [ -f "patches/$p" ] || { echo "patch manquant : patches/$p" >&2; exit 1; }
done < "$tmp/autobuild/patches/series.glyphe"
cp -r patches/glyphe "$tmp/autobuild/patches/glyphe"
# Sources ajoutées par Glyphe : tout ce qui suit [chromium-linux] dans downloads.ini.
python3 - downloads.ini > "$tmp/autobuild/downloads.glyphe.ini" <<'PY'
import configparser, sys
src = configparser.RawConfigParser(); src.read(sys.argv[1])
out = configparser.RawConfigParser()
for section in src.sections():
    if section != 'chromium-linux':
        out[section] = src[section]
out.write(sys.stdout)
PY
cp autobuild/autobuild.sh autobuild/helium-wrapper autobuild/glyphe-autobuild.service \
   autobuild/glyphe-autobuild.timer "$tmp/autobuild/"
tar -C "$tmp" -cf - autobuild | "${SSH[@]}" '
  set -e
  rm -rf /root/glyphe/autobuild.new && mkdir -p /root/glyphe/autobuild.new
  tar -xf - -C /root/glyphe/autobuild.new --strip-components=1
  rm -rf /root/glyphe/autobuild && mv /root/glyphe/autobuild.new /root/glyphe/autobuild
  install -m644 /root/glyphe/autobuild/glyphe-autobuild.{service,timer} /etc/systemd/system/
  systemctl daemon-reload && systemctl enable --now glyphe-autobuild.timer >/dev/null
  echo "Patchs Glyphe envoyés : $(wc -l < /root/glyphe/autobuild/patches/series.glyphe)"'
if [ "${1:-}" = --now ]; then
  "${SSH[@]}" 'systemctl start --no-block glyphe-autobuild.service && echo "Auto-build lancé (journal : /root/glyphe/autobuild.log)"'
fi
