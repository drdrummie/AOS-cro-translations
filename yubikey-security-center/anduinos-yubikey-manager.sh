#!/usr/bin/env bash
set -euo pipefail

directory="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
data_dir="$HOME/.local/share/anduinos-yubikey-manager"
catalog="$data_dir/locale/hr_HR/LC_MESSAGES/anduinos-yubikey-manager.mo"

if [[ ! -f $catalog ]]; then
    echo "Translation not deployed: $catalog" >&2
    echo "Run: bash $directory/deploy.sh" >&2
    exit 1
fi

application="$(command -v anduinos-yubikey-manager || true)"
if [[ -z $application ]]; then
    echo "anduinos-yubikey-manager is not installed or not in PATH." >&2
    exit 1
fi

export XDG_DATA_DIRS="$data_dir:${XDG_DATA_DIRS:-/usr/local/share:/usr/share}"
export LC_ALL=hr_HR.UTF-8
export LANGUAGE=hr_HR

exec "$application" "$@"
