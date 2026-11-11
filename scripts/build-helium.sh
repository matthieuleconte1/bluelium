#!/usr/bin/env bash
# Build Helium (équivalent de scripts/build.sh, avec -j limité pour la RAM)
set -euo pipefail
export CCACHE_DIR=/root/.ccache CCACHE_MAXSIZE=60G
JOBS=${JOBS:-32}
. /root/helium-linux/scripts/shared.sh
setup_environment
rm -rf "${_src_dir}/out" || true
fetch_sources false "${PGO:-true}"
apply_patches
apply_domsub
helium_substitution
helium_apply_translations
helium_version
helium_resources
write_gn_args
gn_gen
build -j "$JOBS"
