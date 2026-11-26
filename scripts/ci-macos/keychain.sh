#!/usr/bin/env bash
# CI macOS : installe le certificat « Bluelium Code Signing » (secret
# MACOS_SIGN_P12, .p12 en base64, mot de passe MACOS_SIGN_P12_PASSWORD) dans
# un trousseau temporaire, et la clé Sparkle (secret SPARKLE_PRIVATE_KEY) dans
# un fichier. Écrit BLUELIUM_SPARKLE_KEY dans $GITHUB_ENV.
set -euo pipefail
: "${MACOS_SIGN_P12:?secret MACOS_SIGN_P12 absent (voir README, build macOS sur GitHub)}"
: "${SPARKLE_PRIVATE_KEY:?secret SPARKLE_PRIVATE_KEY absent (voir README, build macOS sur GitHub)}"
TMP=${RUNNER_TEMP:-$(mktemp -d)}
KC=$TMP/bluelium.keychain-db
KCPW=$(openssl rand -hex 16)
echo "$MACOS_SIGN_P12" | base64 --decode > "$TMP/sign.p12"
security create-keychain -p "$KCPW" "$KC"
security set-keychain-settings -lut 21600 "$KC"
security unlock-keychain -p "$KCPW" "$KC"
security import "$TMP/sign.p12" -k "$KC" -P "${MACOS_SIGN_P12_PASSWORD:-}" -T /usr/bin/codesign
security set-key-partition-list -S apple-tool:,apple:,codesign: -s -k "$KCPW" "$KC" >/dev/null
security list-keychains -d user -s "$KC" $(security list-keychains -d user | tr -d '"')
security default-keychain -s "$KC"
rm -f "$TMP/sign.p12"
security find-identity -p codesigning "$KC"
umask 077
printf '%s\n' "$SPARKLE_PRIVATE_KEY" > "$TMP/sparkle-private-key"
echo "BLUELIUM_SPARKLE_KEY=$TMP/sparkle-private-key" >> "${GITHUB_ENV:-/dev/null}"
