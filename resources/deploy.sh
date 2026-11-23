#!/usr/bin/env bash
set -euo pipefail

directory="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
root="$(cd "$directory/.." && pwd)"
domain="resources"
source="$directory/build/hr_HR/LC_MESSAGES/$domain.mo"
target_dir="$HOME/.local/share/resources/locale/hr/LC_MESSAGES"
target="$target_dir/$domain.mo"

bash "$root/scripts/translate.sh" build resources
if [[ -f $target ]] && cmp -s "$source" "$target"; then
    echo "Translation is already up to date: $target"
    exit 0
fi

mkdir -p "$target_dir"
temporary="$(mktemp "$target_dir/.${domain}.mo.XXXXXX")"
trap 'rm -f -- "$temporary"' EXIT
install -m 644 "$source" "$temporary"
mv -f -- "$temporary" "$target"
echo "Deployed: $target"
