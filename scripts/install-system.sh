#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
root="$(cd "$script_dir/.." && pwd)"

locale_root="/usr/share/locale"
state_dir="/var/lib/anduinos-hr-translations"
manifest_name="manifest.tsv"

# Only these components have a complete hr_HR.po and a gettext domain that the
# installed application actually reads from /usr/share/locale. Add a component
# here only after its catalog is complete, so this installer can never place a
# partially translated catalog system-wide.
components=(
    appearance
    control-panel
    driver-center
    exe-runner
    firewall
    offline-updater
    swap-control
    welcome
    yubikey-security-center
)

# The language-only directory is deliberate. glibc only falls back from
# "hr_HR" to "hr", never the other way round, and AnduinOS sets
# LANGUAGE=hr:en_US:en in a stock session. A hr_HR-only catalog would therefore
# be invisible there. Python's gettext and gettext-rs (the GTK applications)
# both resolve the "hr" directory for a "hr" or "hr_HR" selection.
install_locale="hr"

usage() {
    cat <<'EOF'
Install the Croatian gettext catalogs of the AnduinOS components system-wide so
that the applications use them when started outside this checkout, for example
from the GNOME application grid. The user-local deploy.sh scripts remain
available for isolated testing.

Usage: sudo bash scripts/install-system.sh [OPTIONS]

Options:
  --package NAME  Restrict the action to one component (repeatable).
  --uninstall     Remove the catalogs this script installed.
  --list          Show each component and whether its catalog is installed.
  --dry-run       Print the planned actions without changing the filesystem.
  --force         Replace or remove a catalog this script did not install.
  --destdir DIR   Prepend DIR to every path. Intended for staging and tests;
                  the command then runs without root privileges.
  -h, --help      Show this help.

Without --package every component listed in this script is processed.
EOF
}

fail() {
    echo "$*" >&2
    exit 1
}

# Resolve the gettext domain of a component from its single POT file.
package_domain() {
    local package=$1
    local -a templates
    shopt -s nullglob
    templates=("$root/$package"/*.pot)
    shopt -u nullglob
    if (( ${#templates[@]} != 1 )); then
        fail "Expected exactly one POT file in $root/$package."
    fi
    basename "${templates[0]}" .pot
}

known_component() {
    local candidate
    for candidate in "${components[@]}"; do
        if [[ $candidate == "$1" ]]; then
            return 0
        fi
    done
    return 1
}

original_args=("$@")
dry_run=0
force=0
uninstall=0
list_only=0
destdir=""
selected=()

while (( $# )); do
    case "$1" in
        --package)
            (( $# >= 2 )) || fail "--package requires a component directory name."
            selected+=("$2")
            shift 2
            ;;
        --package=*)
            selected+=("${1#--package=}")
            shift
            ;;
        --uninstall)
            uninstall=1
            shift
            ;;
        --list)
            list_only=1
            shift
            ;;
        --dry-run)
            dry_run=1
            shift
            ;;
        --force)
            force=1
            shift
            ;;
        --destdir)
            (( $# >= 2 )) || fail "--destdir requires a directory."
            destdir="${2%/}"
            shift 2
            ;;
        --destdir=*)
            destdir="${1#--destdir=}"
            destdir="${destdir%/}"
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            usage >&2
            fail "Unknown option: $1"
            ;;
    esac
done

if (( ${#selected[@]} == 0 )); then
    packages=("${components[@]}")
else
    packages=()
    for package in "${selected[@]}"; do
        known_component "$package" ||
            fail "Unknown component: $package. Known components: ${components[*]}"
        packages+=("$package")
    done
fi

manifest="$destdir$state_dir/$manifest_name"
declare -A recorded=()

if [[ -f $manifest ]]; then
    while IFS=$'\t' read -r checksum path; do
        if [[ -z ${checksum:-} || -z ${path:-} ]]; then
            continue
        fi
        recorded["$path"]=$checksum
    done < "$manifest"
fi

checksum_of() {
    sha256sum "$1" | cut -d' ' -f1
}

write_manifest() {
    if (( dry_run )); then
        return 0
    fi
    if (( ${#recorded[@]} == 0 )); then
        rm -rf -- "$destdir$state_dir"
        return 0
    fi
    install -d -m 755 "$destdir$state_dir"
    local temporary path
    temporary="$(mktemp "$destdir$state_dir/.manifest.XXXXXX")"
    for path in "${!recorded[@]}"; do
        printf '%s\t%s\n' "${recorded[$path]}" "$path"
    done | LC_ALL=C sort -k2 > "$temporary"
    chmod 644 "$temporary"
    mv -f -- "$temporary" "$manifest"
}

relative_for() {
    printf '%s/%s/LC_MESSAGES/%s.mo' "$locale_root" "$install_locale" "$1"
}

if (( list_only )); then
    for package in "${packages[@]}"; do
        relative="$(relative_for "$(package_domain "$package")")"
        if [[ -f $destdir$relative ]]; then
            state="installed"
        else
            state="not installed"
        fi
        printf '%-24s %-14s %s%s\n' "$package" "$state" "$destdir" "$relative"
    done
    exit 0
fi

if (( ! dry_run )) && [[ -z $destdir ]] && (( EUID != 0 )); then
    echo "Writing to $locale_root requires root privileges." >&2
    echo "Run: sudo bash scripts/install-system.sh ${original_args[*]:-}" >&2
    echo "Use --destdir DIR to stage the catalogs without root." >&2
    exit 1
fi

if (( uninstall )); then
    if (( ${#recorded[@]} == 0 )); then
        echo "No catalogs recorded in $destdir$state_dir/$manifest_name."
        exit 0
    fi

    # With --package, only the domains that belong to the selected components
    # are removed; a plain --uninstall removes everything this script installed.
    declare -A wanted=()
    if (( ${#selected[@]} > 0 )); then
        for package in "${packages[@]}"; do
            wanted["$(relative_for "$(package_domain "$package")")"]=1
        done
    fi

    removed=0
    kept=0
    while IFS= read -r relative; do
        case $relative in
            "$locale_root/$install_locale/LC_MESSAGES/"*.mo) ;;
            *)
                echo "Ignoring unexpected manifest entry: $relative" >&2
                continue
                ;;
        esac
        if (( ${#wanted[@]} > 0 )) && [[ -z ${wanted[$relative]:-} ]]; then
            continue
        fi

        target="$destdir$relative"
        if [[ ! -f $target ]]; then
            unset 'recorded[$relative]'
            echo "Already absent: $relative"
            continue
        fi
        if [[ $(checksum_of "$target") != "${recorded[$relative]}" ]] && (( ! force )); then
            echo "Keeping locally modified catalog: $relative" >&2
            kept=$((kept + 1))
            continue
        fi
        if (( dry_run )); then
            echo "Would remove: $relative"
            continue
        fi
        rm -f -- "$target"
        rmdir --ignore-fail-on-non-empty "$(dirname "$target")" 2>/dev/null || true
        unset 'recorded[$relative]'
        echo "Removed: $relative"
        removed=$((removed + 1))
    done < <(printf '%s\n' "${!recorded[@]}" | LC_ALL=C sort)

    if (( ! dry_run )); then
        rmdir --ignore-fail-on-non-empty \
            "$destdir$locale_root/$install_locale/LC_MESSAGES" \
            "$destdir$locale_root/$install_locale" 2>/dev/null || true
        write_manifest
    fi

    if (( kept )); then
        echo "Kept $kept locally modified catalog(s); use --force to remove them." >&2
        exit 1
    fi
    if (( dry_run )); then
        echo "Dry run: no catalog was removed."
    else
        echo "Removed $removed catalog(s)."
    fi
    exit 0
fi

command -v msgfmt >/dev/null || fail "msgfmt is required (install the gettext package)."

# The build step validates the catalog and writes the same .mo file that
# deploy.sh uses, so a system install always matches a local test deploy.
declare -A domains=()
for package in "${packages[@]}"; do
    echo "Validating: $package"
    bash "$root/scripts/translate.sh" build "$package"
    domain="$(package_domain "$package")"
    if [[ -n ${domains[$domain]:-} ]]; then
        fail "Duplicate gettext domain $domain in ${domains[$domain]} and $package."
    fi
    source_catalog="$root/$package/build/hr_HR/LC_MESSAGES/$domain.mo"
    [[ -f $source_catalog ]] || fail "Missing build output: $source_catalog"
    domains["$domain"]=$package
done

failed=0
count=0
pending=0
for domain in $(printf '%s\n' "${!domains[@]}" | LC_ALL=C sort); do
    relative="$(relative_for "$domain")"
    target="$destdir$relative"
    source_catalog="$root/${domains[$domain]}/build/hr_HR/LC_MESSAGES/$domain.mo"

    if [[ -f $target ]] && cmp -s "$source_catalog" "$target"; then
        if [[ -n ${recorded[$relative]:-} ]]; then
            recorded["$relative"]="$(checksum_of "$target")"
            echo "Up to date: $relative"
        elif (( force )); then
            recorded["$relative"]="$(checksum_of "$target")"
            echo "Up to date (now managed): $relative"
        else
            # Identical content, but the file may belong to a distribution
            # package. Leave it out of the manifest so that --uninstall never
            # deletes something this script did not place.
            echo "Up to date, not managed: $relative"
        fi
        count=$((count + 1))
        continue
    fi
    if [[ -f $target && -z ${recorded[$relative]:-} ]] && (( ! force )); then
        echo "Refusing to overwrite a catalog this script did not install: $relative" >&2
        echo "It may belong to a distribution package. Use --force to replace it." >&2
        failed=1
        continue
    fi
    if (( dry_run )); then
        echo "Would install: $relative"
        pending=$((pending + 1))
        continue
    fi
    install -D -m 644 "$source_catalog" "$target"
    recorded["$relative"]="$(checksum_of "$target")"
    echo "Installed: $relative"
    count=$((count + 1))
done

write_manifest

if (( failed )); then
    echo "Some catalogs were not installed." >&2
    exit 1
fi

if (( dry_run )); then
    total=$((count + pending))
    echo "Dry run: $pending of $total catalog(s) would be installed in $destdir$locale_root/$install_locale."
elif (( count == 0 )); then
    echo "No catalog was changed."
else
    echo "Processed $count catalog(s) in $destdir$locale_root/$install_locale."
    echo "The applications pick them up on their next start."
fi
