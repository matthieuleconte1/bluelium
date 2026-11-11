#!/usr/bin/env bash
# Installe la mise à jour automatique sur le PC (utilisateur courant).
set -euo pipefail
cd "$(dirname "$0")"
install -Dm755 glyphe-update "$HOME/.local/bin/glyphe-update"
install -Dm644 glyphe-update.service "$HOME/.config/systemd/user/glyphe-update.service"
install -Dm644 glyphe-update.timer "$HOME/.config/systemd/user/glyphe-update.timer"
# Le lanceur sait installer une mise à jour prête avant d'ouvrir Helium.
install -m755 helium-wrapper "$HOME/Applications/helium-glyphe/helium-wrapper"
systemctl --user daemon-reload
systemctl --user enable --now glyphe-update.timer
systemctl --user list-timers glyphe-update.timer --no-pager
