#!/usr/bin/env bash
set -euo pipefail

directory="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
catalog="$HOME/.local/share/anduinos-exe-runner/locale/hr_HR/LC_MESSAGES/anduinos-exe-runner.mo"

if [[ ! -f $catalog ]]; then
    echo "Translation not deployed: $catalog" >&2
    echo "Run: bash $directory/deploy.sh" >&2
    exit 1
fi

exec /usr/bin/python3 "$directory/run.py" "$@"
