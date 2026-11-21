#!/usr/bin/env bash
set -euo pipefail

uuid="blur-my-shell@aunetx"
data_home="${XDG_DATA_HOME:-$HOME/.local/share}"
if [[ $data_home != /* ]]; then
    echo "XDG_DATA_HOME must be an absolute path: $data_home" >&2
    exit 1
fi
target="$data_home/gnome-shell/extensions/$uuid"
info="$(LC_ALL=C LANGUAGE=C gnome-extensions info "$uuid")"
if ! grep -Fxq "  Path: $target" <<< "$info"; then
    echo "GNOME Shell is not using the user-local extension: $target" >&2
    echo "Log out and back in after deployment, then check extension settings." >&2
    exit 1
fi
exec gnome-extensions prefs "$uuid"
