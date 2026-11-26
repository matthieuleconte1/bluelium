#!/usr/bin/env bash
# CI macOS : une étape de compilation, dans le temps qui reste au job.
# Usage : phase.sh <début du job (epoch)> <durée max du job, minutes>
# Écrit status=running (à reprendre au job suivant) ou status=finished dans
# $GITHUB_OUTPUT. Garde RESERVE_MIN minutes pour emballer et envoyer l'état.
set -uo pipefail
WORK=${BLUELIUM_MAC_WORK:?}
W=$WORK/helium-macos
START=${1:?}; MINUTES=${2:?}
RESERVE_MIN=${RESERVE_MIN:-75}
OUT=${GITHUB_OUTPUT:-/dev/null}

# shellcheck source=/dev/null
. "$WORK/meta.env"
if [ "$(uname -m)" != "${HOST_ARCH:-$(uname -m)}" ]; then
  echo "ÉCHEC : état préparé sur une machine ${HOST_ARCH}, ce job tourne sur $(uname -m)" >&2
  exit 1
fi

remaining=$(( MINUTES*60 - RESERVE_MIN*60 - $(date +%s) + START ))
if [ "$remaining" -le 600 ]; then
  echo "ÉCHEC : plus assez de temps dans ce job (${remaining} s)" >&2
  exit 1
fi
echo "Compilation de $VERSION pendant au plus $((remaining / 60)) min"
echo "status=running" >> "$OUT"

TIMEOUT=$(command -v gtimeout || command -v timeout)
export _root_dir=$W
code=0
"$TIMEOUT" -k 7m -s TERM "${remaining}s" \
  bash "$W/devutils/shared.sh" build ${JOBS:+-j "$JOBS"} || code=$?
case $code in
  0)   echo "status=finished" >> "$OUT"; echo "=== compilation terminée" ;;
  124) echo "=== temps écoulé : la suite au job suivant" ;;
  *)   echo "ÉCHEC : la compilation a échoué (code $code)" >&2; exit "$code" ;;
esac
