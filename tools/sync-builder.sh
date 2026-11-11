#!/usr/bin/env bash
# Installe l'auto-build Bluelium sur la machine de build. Les patchs, eux,
# viennent du dépôt GitHub (branche main) : pousser suffit pour un nouveau build.
#   tools/sync-builder.sh                 installe (build à la prochaine nuit)
#   tools/sync-builder.sh --now           installe et lance l'auto-build
#   tools/sync-builder.sh --patch-only    installe et vérifie seulement que la
#                                         série s'applique sur Helium (sans build)
# Hôte : ~/.config/bluelium/builder.env (voir tools/builder-ssh.sh).
set -euo pipefail
cd "$(dirname "$0")/.."
SSH=(tools/builder-ssh.sh)
tar -cf - autobuild/autobuild.sh autobuild/glyphe-autobuild.service \
          autobuild/glyphe-autobuild.timer | "${SSH[@]}" '
  set -e
  mkdir -p /root/glyphe/autobuild
  tar -xf - -C /root/glyphe/autobuild --strip-components=1
  install -m644 /root/glyphe/autobuild/glyphe-autobuild.{service,timer} /etc/systemd/system/
  systemctl daemon-reload && systemctl enable --now glyphe-autobuild.timer >/dev/null
  echo "Auto-build installé ; prochain passage : $(systemctl show -p NextElapseUSecRealtime --value glyphe-autobuild.timer)"'
case "${1:-}" in
  --now)
    "${SSH[@]}" 'systemctl start --no-block glyphe-autobuild.service && echo "Auto-build lancé (journal : /root/glyphe/autobuild.log)"' ;;
  --patch-only)
    "${SSH[@]}" 'systemd-run --unit=bluelium-patch-check --collect -E FORCE=1 -E PATCH_ONLY=1 /root/glyphe/autobuild/autobuild.sh >/dev/null && echo "Vérification de la série lancée (journal : /root/glyphe/autobuild.log)"' ;;
esac
