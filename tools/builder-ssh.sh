#!/usr/bin/env bash
# Commande SSH vers la machine de build, lue dans ~/.config/bluelium/builder.env :
#   BLUELIUM_BUILDER=utilisateur@hôte   (obligatoire)
#   BLUELIUM_JUMP=utilisateur@rebond    (facultatif)
# Usage : tools/builder-ssh.sh 'commande'
set -euo pipefail
CONF=${BLUELIUM_CONF:-$HOME/.config/bluelium/builder.env}
[ -f "$CONF" ] && . "$CONF"
: "${BLUELIUM_BUILDER:?définir BLUELIUM_BUILDER dans $CONF}"
args=(-F /dev/null -o BatchMode=yes -o ConnectTimeout=15)
if [ -n "${BLUELIUM_JUMP:-}" ]; then
  args+=(-o "ProxyCommand=ssh -F /dev/null -o BatchMode=yes -o ConnectTimeout=15 -W %h:%p $BLUELIUM_JUMP")
fi
exec ssh "${args[@]}" "$BLUELIUM_BUILDER" "$@"
