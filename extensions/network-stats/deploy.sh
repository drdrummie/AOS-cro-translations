#!/usr/bin/env bash
set -euo pipefail

directory="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
root="$(cd "$directory/../.." && pwd)"
uuid="network-stats@gnome.noroadsleft.xyz"
source="/usr/share/gnome-shell/extensions/$uuid"
data_home="${XDG_DATA_HOME:-$HOME/.local/share}"
if [[ $data_home != /* ]]; then
    echo "XDG_DATA_HOME must be an absolute path: $data_home" >&2
    exit 1
fi
parent="$data_home/gnome-shell/extensions"
target="$parent/$uuid"
catalog="$directory/build/hr_HR/LC_MESSAGES/network-stats.mo"

if [[ ! -f $source/metadata.json ]]; then
    echo "System extension not found: $source" >&2
    exit 1
fi
if [[ -e $target || -L $target ]]; then
    echo "User extension already exists; refusing to overwrite: $target" >&2
    exit 1
fi

bash "$root/scripts/translate.sh" build extensions/network-stats
mkdir -p "$parent"
temporary="$(mktemp -d "$parent/.network-stats.XXXXXXXX")"
trap 'if [[ -n $temporary ]]; then rm -rf -- "$temporary"; fi' EXIT
cp -a "$source/." "$temporary/"
for language in hr hr_HR; do
    install -d "$temporary/locale/$language/LC_MESSAGES"
    install -m 644 "$catalog" "$temporary/locale/$language/LC_MESSAGES/network-stats.mo"
done
mv -T -n -- "$temporary" "$target"
if [[ -e $temporary ]]; then
    echo "User extension appeared during deployment; refusing to overwrite: $target" >&2
    exit 1
fi
temporary=""
echo "Deployed a user-local extension copy: $target"
echo "Log out and back in before testing; this copy may shadow system updates."
