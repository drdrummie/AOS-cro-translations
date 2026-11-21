#!/usr/bin/env bash
set -euo pipefail

directory="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
data_dir="$HOME/.local/share/anduinos-appearance"
catalog="$data_dir/locale/hr_HR/LC_MESSAGES/anduinos-appearance.mo"

if [[ ! -f $catalog ]]; then
    echo "Translation not deployed: $catalog" >&2
    echo "Run: bash $directory/deploy.sh" >&2
    exit 1
fi

application="$(command -v anduinos-appearance || true)"
if [[ -z $application ]]; then
    echo "anduinos-appearance is not installed or not in PATH." >&2
    exit 1
fi

export ANDUINOS_APPEARANCE_LOCALE="$data_dir/locale"
export LANGUAGE=hr_HR

exec "$application" "$@"
