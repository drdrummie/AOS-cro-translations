#!/usr/bin/env bash
set -euo pipefail

directory="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
catalog="$HOME/.local/share/resources/locale/hr/LC_MESSAGES/resources.mo"
system_dir="/usr/share/locale/hr/LC_MESSAGES"

if [[ ! -f $catalog ]]; then
    echo "Translation not deployed: $catalog" >&2
    echo "Run: bash $directory/deploy.sh" >&2
    exit 1
fi
if ! command -v bwrap >/dev/null; then
    echo "bubblewrap is required to test the Resources translation." >&2
    exit 1
fi
if [[ ! -d $system_dir ]]; then
    echo "System Croatian locale directory not found: $system_dir" >&2
    exit 1
fi

application="$(command -v resources || true)"
if [[ -z $application ]]; then
    echo "resources is not installed or not in PATH." >&2
    exit 1
fi

mounts=(--bind / / --dev-bind /dev /dev --tmpfs "$system_dir")
shopt -s nullglob
for entry in "$system_dir"/*; do
    if [[ ${entry##*/} != resources.mo ]]; then
        mounts+=(--ro-bind "$entry" "$entry")
    fi
done
mounts+=(--ro-bind "$catalog" "$system_dir/resources.mo")

export LC_ALL=hr_HR.UTF-8
export LANGUAGE=hr
if [[ ${1:-} == --check-translation ]]; then
    if [[ $# -ne 1 ]]; then
        echo "--check-translation does not accept additional arguments." >&2
        exit 2
    fi
    result="$(bwrap "${mounts[@]}" -- gettext -d resources Resources)"
    if [[ $result != Resursi ]]; then
        echo "Resources translation lookup failed: $result" >&2
        exit 1
    fi
    echo "Resources translation lookup succeeded: $result"
    exit 0
fi

exec bwrap "${mounts[@]}" -- "$application" "$@"
