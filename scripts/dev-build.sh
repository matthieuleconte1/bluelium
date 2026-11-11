#!/usr/bin/env bash
# Build incrémental pour tester les patchs (sans PGO, sans effacer out/)
set -euo pipefail
export CCACHE_DIR=/root/.ccache
cd /root/helium-linux/build/src
./buildtools/linux64/gn gen out/Default --fail-on-unused-args
SISO_PATH=third_party/siso/cipd/siso python3 third_party/depot_tools/autoninja.py -C out/Default chrome -j ${JOBS:-32}
