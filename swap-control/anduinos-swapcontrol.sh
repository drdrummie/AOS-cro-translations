#!/usr/bin/env bash
set -euo pipefail

directory="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
domain="swapcontrol-gtk"
data_dir="$HOME/.local/share/anduinos-swapcontrol"
catalog="$data_dir/locale/hr_HR/LC_MESSAGES/$domain.mo"

if [[ ! -f $catalog ]]; then
    echo "Translation not deployed: $catalog" >&2
    echo "Run: bash $directory/deploy.sh" >&2
    exit 1
fi

application="$(command -v swapcontrol-gtk || true)"
if [[ -z $application ]]; then
    echo "swapcontrol-gtk is not installed or not in PATH." >&2
    exit 1
fi

# The application resolves its catalog through XDG_DATA_DIRS. Both locale
# variables are required: LC_ALL makes gettext search the deployed catalog and
# LANGUAGE selects the hr_HR subdirectory, which an inherited "hr:en_US:en"
# list would otherwise miss.
export XDG_DATA_DIRS="$data_dir:${XDG_DATA_DIRS:-/usr/local/share:/usr/share}"
export LC_ALL=hr_HR.UTF-8
export LANGUAGE=hr_HR

exec "$application" "$@"
