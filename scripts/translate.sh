#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
    echo "Usage: bash scripts/translate.sh {update|check|build} PACKAGE" >&2
    exit 2
fi

action=$1
package=$2
if [[ ! $package =~ ^[[:alnum:]_-][[:alnum:]_.-]*$ ]]; then
    echo "Invalid package directory name: $package" >&2
    exit 2
fi

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
directory="$root/$package"
catalog="$directory/hr_HR.po"

shopt -s nullglob
templates=("$directory"/*.pot)
if (( ${#templates[@]} != 1 )); then
    echo "Expected exactly one POT file in $directory." >&2
    exit 1
fi
if [[ ! -f $catalog ]]; then
    echo "Catalog not found: $catalog" >&2
    exit 1
fi
template=${templates[0]}

check() {
    LC_ALL=C msgfmt --check --check-format --statistics -o /dev/null "$catalog"
    LC_ALL=C msgcmp --no-fuzzy-matching "$catalog" "$template"
}

case "$action" in
    update)
        LC_ALL=C msgmerge --update --backup=none "$catalog" "$template"
        echo "PO updated. Review new and fuzzy translations, then run the check."
        ;;
    check)
        check
        echo "Translation is valid and complete."
        ;;
    build)
        check
        domain="$(basename "$template" .pot)"
        output="$directory/build/hr_HR/LC_MESSAGES"
        mkdir -p "$output"
        LC_ALL=C msgfmt --check --check-format -o "$output/$domain.mo" "$catalog"
        echo "Built: $output/$domain.mo"
        ;;
    *)
        echo "Unknown action: $action" >&2
        exit 2
        ;;
esac
