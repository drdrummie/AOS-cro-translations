#!/usr/bin/env bash
set -euo pipefail

directory="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
domain="anduinos-whisper-gtk"
data_dir="$HOME/.local/share/$domain"
catalog="$data_dir/locale/hr_HR/LC_MESSAGES/$domain.mo"

if [[ ! -f $catalog ]]; then
    echo "Translation not deployed: $catalog" >&2
    echo "Run: bash $directory/deploy.sh" >&2
    exit 1
fi

application="$(command -v anduinos-whisper-gtk || true)"
if [[ -z $application ]]; then
    echo "AnduinOS Voice Typing is not installed or not in PATH." >&2
    exit 1
fi

export LC_ALL=hr_HR.UTF-8
export LANGUAGE=hr_HR

exec /usr/bin/python3 - "$application" "$@" <<'PY'
import gettext
import runpy
import sys
from pathlib import Path

domain = "anduinos-whisper-gtk"
locale_dir = Path.home() / ".local/share" / domain / "locale"
bindtextdomain = gettext.bindtextdomain


def bind_user_catalog(name, localedir=None):
    if name == domain:
        localedir = str(locale_dir)
    return bindtextdomain(name, localedir)


gettext.bindtextdomain = bind_user_catalog
application, *arguments = sys.argv[1:]
sys.argv = [application, *arguments]
runpy.run_path(application, run_name="__main__")
PY
