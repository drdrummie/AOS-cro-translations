#!/usr/bin/env bash
set -euo pipefail

directory="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
root="$(cd "$directory/.." && pwd)"
domain="flatseal"
source="$directory/build/hr_HR/LC_MESSAGES/$domain.mo"
data_dir="$HOME/.local/share/flatseal"
target_dir="$data_dir/locale/hr/LC_MESSAGES"
target="$target_dir/$domain.mo"
launcher_source="$directory/flatseal-test.js"
launcher_target="$data_dir/flatseal-test.js"

bash "$root/scripts/translate.sh" build flatseal
if [[ -f $target ]] && cmp -s "$source" "$target" &&
    [[ -f $launcher_target ]] && cmp -s "$launcher_source" "$launcher_target"; then
    echo "Translation is already up to date: $target"
    exit 0
fi

mkdir -p "$target_dir"
temporary_catalog="$(mktemp "$target_dir/.${domain}.mo.XXXXXX")"
temporary_launcher="$(mktemp "$data_dir/.flatseal-test.js.XXXXXX")"
trap 'rm -f -- "$temporary_catalog" "$temporary_launcher"' EXIT

install -m 644 "$source" "$temporary_catalog"
install -m 644 "$launcher_source" "$temporary_launcher"
mv -f -- "$temporary_catalog" "$target"
mv -f -- "$temporary_launcher" "$launcher_target"
echo "Deployed user-local Flatseal translation: $target"
