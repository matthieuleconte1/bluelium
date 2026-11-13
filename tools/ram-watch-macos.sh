#!/usr/bin/env bash
# Bluelium — surveille la mémoire pendant un build macOS et l'arrête avant
# que le Mac gèle (le build reprend avec SKIP_FETCH=1).
#
# Usage : tools/ram-watch-macos.sh [journal.csv]
# Seuils : MIN_FREE_PCT (défaut 10 % de mémoire libre selon memory_pressure),
#          MAX_SWAP_GB (défaut 10), MIN_DISK_GB (défaut 8, disque interne).
# Colonnes : heure, libre %, swap Go, compressé Go, disque interne libre Go,
#            nb de clang, RSS clang Go, RSS ld/lld Go, progression du build.
set -uo pipefail
CSV=${1:-$HOME/Library/Logs/Bluelium/ram.csv}
LOG=${BLUELIUM_MAC_WORK:-/Volumes/BlueliumBuild}/build-macos.log
MIN_FREE_PCT=${MIN_FREE_PCT:-10}
MAX_SWAP_GB=${MAX_SWAP_GB:-10}
MIN_DISK_GB=${MIN_DISK_GB:-8}
PAGE=$(sysctl -n hw.pagesize)
mkdir -p "$(dirname "$CSV")"
[ -s "$CSV" ] || echo "heure,libre_pct,swap_go,compresse_go,disque_go,clang_n,clang_go,link_go,etape" > "$CSV"

stop_build() {
  echo "$(date '+%T') ARRÊT : $1" | tee -a "$CSV"
  pkill -TERM -f 'cipd/siso ninja'; sleep 5
  pkill -9 -f 'cipd/siso'; pkill -9 -f 'build-macos.sh'; pkill -f 'caffeinate -is scripts'
  exit 1
}

while pgrep -f 'cipd/siso ninja' >/dev/null; do
  free=$(memory_pressure 2>/dev/null | awk -F': ' '/free percentage/ {gsub(/%/, "", $2); print $2}')
  swap=$(sysctl -n vm.swapusage | awk '{for (i=1;i<=NF;i++) if ($i=="used") {v=$(i+2); sub(/M/,"",v); printf "%.1f", v/1024}}')
  comp=$(vm_stat | awk -v p="$PAGE" '/occupied by compressor/ {gsub(/\./,"",$NF); printf "%.1f", $NF*p/1073741824}')
  disk=$(df -g / | awk 'NR==2 {print $4}')
  read -r cn cgo < <(ps -axo rss=,comm= | awk '$2 ~ /clang/ {n++; s+=$1} END {printf "%d %.1f\n", n, s/1048576}')
  lgo=$(ps -axo rss=,comm= | awk '$2 ~ /(^|\/)(ld|ld64.lld|lld)$/ {s+=$1} END {printf "%.1f", s/1048576}')
  step=$(tail -c 4000 "$LOG" 2>/dev/null | tr '\r' '\n' | grep -oE '^\[[0-9]+/[0-9]+\]' | tail -1)
  echo "$(date '+%T'),$free,$swap,$comp,$disk,$cn,$cgo,$lgo,$step" >> "$CSV"
  [ -n "$free" ] && [ "$free" -lt "$MIN_FREE_PCT" ] && stop_build "mémoire libre $free % < $MIN_FREE_PCT %"
  awk -v s="$swap" -v m="$MAX_SWAP_GB" 'BEGIN {exit !(s > m)}' && stop_build "swap $swap Go > $MAX_SWAP_GB Go"
  [ "$disk" -lt "$MIN_DISK_GB" ] && stop_build "disque interne $disk Go < $MIN_DISK_GB Go"
  sleep 10
done
echo "$(date '+%T') build terminé ou arrêté" >> "$CSV"
