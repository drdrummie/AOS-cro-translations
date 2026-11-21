#!/usr/bin/env bash
set -euo pipefail

application_id="com.github.tchx84.Flatseal"
data_dir="$HOME/.local/share/flatseal"
catalog="$data_dir/locale/hr/LC_MESSAGES/flatseal.mo"
test_launcher="$data_dir/flatseal-test.js"

if ! command -v flatpak >/dev/null 2>&1; then
    echo "Flatpak is required to launch Flatseal." >&2
    exit 1
fi
if [[ ! -f $catalog || ! -f $test_launcher ]]; then
    echo "Translation not deployed. Run: bash $(dirname "${BASH_SOURCE[0]}")/deploy.sh" >&2
    exit 1
fi
if ! flatpak info "$application_id" >/dev/null 2>&1; then
    echo "Flatseal Flatpak is not installed: $application_id" >&2
    exit 1
fi

exec flatpak run \
    --filesystem="$data_dir:ro" \
    --env="FLATSEAL_TRANSLATION_DIR=$data_dir/locale" \
    --env=LANGUAGE=hr:en_US:en \
    --command=gjs \
    "$application_id" "$test_launcher" "$@"
