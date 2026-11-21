# Croatian translations for AnduinOS

Each component has its own translation directory:

```text
appearance/
  anduinos-appearance.pot
  anduinos-appearance.sh
  deploy.sh
  hr_HR.po
exe-runner/
  anduinos-exe-runner.pot
  anduinos-exe-runner.sh
  deploy.sh
  hr_HR.po
  run.py
offline-updater/
  anduinos-offline-updater.pot
  anduinos-offline-updater.sh
  deploy.sh
  hr_HR.po
  run.py
control-panel/
  anduinos-control-panel.pot
  anduinos-control-panel.sh
  deploy.sh
  hr_HR.po
  run.py
driver-center/
  anduinos-driver-center.pot
  anduinos-driver-center.sh
  deploy.sh
  hr_HR.po
  run.py
firewall/
  ufwall-gtk.pot
  anduinos-firewall.sh
  deploy.sh
  hr_HR.po
yubikey-security-center/
  anduinos-yubikey-manager.pot
  anduinos-yubikey-manager.sh
  deploy.sh
  hr_HR.po
```

The POT file is the message template; the PO file contains the Croatian
translation. The Control Panel and Welcome templates were extracted from the
locally installed versions; the Driver Center template was extracted from its
installed Python sources and the Secure Boot toolkit UI, with desktop-entry
and PolicyKit messages included for upstream contribution. The Swap Control
template was taken from the maintainers' `po/swapcontrol-gtk.pot`. Before
contributing upstream, compare each template with the current source code and
the maintainers' templates.
The Firewall template was extracted from the installed AnduinOS Firewall
2.0.5 English catalog. It also includes the desktop-entry and PolicyKit
strings already present in the application's catalog for upstream contribution.
The Appearance template was extracted from the installed AnduinOS Appearance
2.1.0 Python UI and desktop entry.
The Offline Updater template was extracted from its installed Python UI,
desktop entry, and PolicyKit action. The desktop-entry and PolicyKit messages
are included for upstream contribution.
The YubiKey Security Center template was extracted from its installed English
gettext catalog, desktop entry, and PolicyKit action. The desktop-entry and
PolicyKit messages are included for upstream contribution.
The Exe Runner template was extracted from its installed English gettext
catalog and desktop entry.

`swap-control/` follows the same layout but has no `run.py`: Swap Control is a
compiled GTK application, so its launcher only selects the language and points
the application at the user-local catalog.

## Tasks

In VS Code, open **Terminal → Run Task** and select a task:

- **Translation: update PO from POT** updates the existing PO using `msgmerge`.
  Review new messages and suggestions marked `fuzzy`.
- **Translation: check** checks syntax, format placeholders, and completeness
  against the POT. Untranslated and `fuzzy` messages cause the check to fail.
- **Translation: build MO** checks the translation, then builds an MO file in
  `<package>/build/hr_HR/LC_MESSAGES/`. The MO name comes from the POT name.
  Git ignores the generated files.

Tasks prompt for the package directory name, defaulting to `control-panel`.
For a new component, add one POT file and `hr_HR.po` under
`package-name/`. Create a new PO with `msginit`, for example:

```bash
msginit --locale=hr_HR.UTF-8 --input=package-name/domain.pot \
  --output-file=package-name/hr_HR.po
```

GNU gettext tools are required. The same operations are available in a terminal:

```bash
bash scripts/translate.sh update control-panel
bash scripts/translate.sh check control-panel
bash scripts/translate.sh build control-panel
```

Extension components can use `extensions/<package>/` as their package
directory. Once a catalog has been added, it can be checked with, for example,
`bash scripts/translate.sh check extensions/arcmenu`. The generated `build/`
directory is ignored there as well. This does not add extension catalogs to
the system installer.

## GNOME Shell extensions

On the inspected AnduinOS 2.0.6 installation, ArcMenu, Dash to Panel,
Blur my Shell, SimpleWeather and Network Stats are system-installed GNOME Shell
extensions. ArcMenu, Dash to Panel and Blur my Shell are enabled in the
distribution defaults; SimpleWeather and Network Stats are not listed there.
Individual users can enable or install additional extensions.

| Extension | UUID | Gettext domain |
| --- | --- | --- |
| ArcMenu | `arcmenu@arcmenu.com` | `arcmenu` |
| Dash to Panel | `dash-to-panel@jderose9.github.com` | `dash-to-panel` |
| Blur my Shell | `blur-my-shell@aunetx` | `blur-my-shell@aunetx` |
| SimpleWeather | `simple-weather@romanlefler.com` | `simple-weather@romanlefler.com` |
| Network Stats | `network-stats@gnome.noroadsleft.xyz` | `network-stats` |

These installed extensions have their own `locale/` directories, which GNOME
Shell binds as their gettext locations. The inspected Blur my Shell, Dash to
Panel, and SimpleWeather versions have Croatian catalogs in this repository;
Network Stats does not. Catalogs in this repository are not automatically used
by GNOME Shell. In particular, the application deployment instructions below
do not apply to extensions.

System extension directories belong to distribution packages and require
administrator privileges to modify. The absence of a Croatian catalog in one
installed version does not guarantee that a later package update will not
provide or replace it. A system installation must check each destination and
avoid overwriting an existing catalog without explicit approval. The inspected
session uses `LANGUAGE=hr:en_US:en`, so the `hr` locale directory is relevant.
Shell and extension preference processes may need restarting to pick up a new
catalog.

### Blur my Shell catalog

`extensions/blur-my-shell/` contains a template extracted from the installed
version 78 JavaScript and embedded UI resources, and a Croatian PO merged from
the upstream Croatian catalog. Existing translations were reviewed and the
remaining messages translated. Compare the template with the installed
extension again after upgrades.

```bash
bash scripts/translate.sh check extensions/blur-my-shell
bash scripts/translate.sh build extensions/blur-my-shell
```

The component's `deploy.sh` is for user-local testing:

```bash
bash extensions/blur-my-shell/deploy.sh
# Log out and back in.
bash extensions/blur-my-shell/blur-my-shell.sh
```

Deployment validates and builds the catalog. It
copies the system extension into the user's GNOME Shell extension directory,
adds the compiled `hr` and `hr_HR` catalogs to that copy, and refuses to
overwrite an existing user extension. It does not modify the system extension.
The copy may shadow later system updates and must be maintained separately.
Log out and back in before using `blur-my-shell.sh` to open its preferences;
the launcher checks that GNOME Shell is actually using the user-local copy.
The preferences use the desktop session's language settings. Neither script is
run by building the catalog.

### SimpleWeather catalog

`extensions/simple-weather/` contains a template extracted from the installed
SimpleWeather version 12 JavaScript sources and a Croatian translation. Compare
the template with the installed extension again after upgrades.

```bash
bash scripts/translate.sh check extensions/simple-weather
bash scripts/translate.sh build extensions/simple-weather
```

For user-local testing:

```bash
bash extensions/simple-weather/deploy.sh
# Log out and back in.
bash extensions/simple-weather/simple-weather.sh
```

Deployment validates and builds the catalog, copies the system extension to
the user's GNOME Shell extension directory, adds the compiled `hr` and `hr_HR`
catalogs, and refuses to overwrite an existing user extension. It does not
modify the system extension. The copy may shadow later system updates and must
be maintained separately. The launcher checks that GNOME Shell is using the
user-local copy. The preferences use the desktop session's language settings.
Neither script is run by building the catalog.

### Dash to Panel catalog

`extensions/dash-to-panel/` contains a template extracted from the installed
version 74 JavaScript and UI resources, and a Croatian translation for its
gettext domain. Compare the template with the installed extension again after
upgrades.

```bash
bash scripts/translate.sh check extensions/dash-to-panel
bash scripts/translate.sh build extensions/dash-to-panel
```

For user-local testing:

```bash
bash extensions/dash-to-panel/deploy.sh
# Log out and back in.
bash extensions/dash-to-panel/dash-to-panel.sh
```

Deployment validates and builds the catalog, copies the system extension to
the user's GNOME Shell extension directory, adds the compiled `hr` and
`hr_HR` catalogs, and refuses to overwrite an existing user extension. It does
not modify the system extension. The copy may shadow later system updates and
must be maintained separately. The launcher checks that GNOME Shell is using
the user-local copy. Neither script is run by building the catalog.

## Testing Control Panel

Deploy the current catalog to your user account, then launch the installed
application with that translation:

```bash
bash control-panel/deploy.sh
bash control-panel/anduinos-control-panel.sh
```

Deployment validates and builds the PO before updating
`~/.local/share/anduinos-control-panel/locale/`. It leaves an identical
catalog unchanged, and does not modify system files. Building alone does not
deploy changes. The test launcher uses the current language settings; to
select Croatian for a test:

```bash
LANGUAGE=hr_HR bash control-panel/anduinos-control-panel.sh
```

Close any running Control Panel instance first: the application may otherwise
reuse it. The existing user desktop launcher also uses this deployed catalog,
but GNOME search results may start the system application instead.

## Testing AnduinOS Appearance

```bash
bash appearance/deploy.sh
bash appearance/anduinos-appearance.sh
```

Deployment validates and builds the catalog before placing it in
`~/.local/share/anduinos-appearance/locale/`. The test launcher points the
installed application at that user-local catalog and selects Croatian.
Deployment does not modify system files; the system desktop entry remains
unchanged. Close any running Appearance instance before testing, because the
application may otherwise reuse its existing window.

## Testing AnduinOS Offline Updater

```bash
bash offline-updater/deploy.sh
bash offline-updater/anduinos-offline-updater.sh
```

Deployment validates and builds the catalog before placing it in
`~/.local/share/anduinos-offline-updater/locale/`. The test launcher opens the
installed updater with the user-local Croatian catalog. Deployment does not
modify system files; the system desktop entry and PolicyKit prompt remain
unchanged. Close any running Offline Updater instance before testing, because
the application may otherwise reuse its existing window.

## Testing AnduinOS Exe Runner

```bash
bash exe-runner/deploy.sh
LANGUAGE=hr_HR bash exe-runner/anduinos-exe-runner.sh /path/to/program.exe
```

The installed runner binds its gettext domain to `/usr/share/locale`. The test
launcher redirects that domain to the user-local catalog in
`~/.local/share/anduinos-exe-runner/locale/` and selects Croatian. Deployment
validates and builds the catalog before placing it there; it does not modify
system files. The desktop entry remains system-provided and is not changed by
this user-local test setup. Close any running Exe Runner instance before
testing, because the application may otherwise reuse its existing window.

## Testing AnduinOS Welcome

```bash
bash welcome/deploy.sh
bash welcome/anduinos-oobe.sh
```

Deployment validates and compiles the catalog before placing it in
`~/.local/share/anduinos-oobe/locale/`. The project launcher loads the
installed application and applies that catalog for the selected language.
The ordinary desktop and automatic first-run launchers remain unchanged and do
not use the user-local catalog. Close any running Welcome instance before
testing; the application may otherwise reuse it. As with Control Panel, set
`LANGUAGE=hr_HR` when launching to select Croatian for a test.

## Testing AnduinOS Driver Center

```bash
bash driver-center/deploy.sh
LANGUAGE=hr_HR bash driver-center/anduinos-driver-center.sh
```

The launcher redirects the Driver Center gettext domain to the user-local
catalog because the installed application normally binds that domain to
`/usr/share/locale`. Deployment and testing do not modify system files. Close
any running Driver Center instance before testing; the application may
otherwise reuse it. Desktop-entry and PolicyKit strings are included in the
catalog for upstream use; this user-local launcher does not change the
system-installed desktop entry or authentication prompts.

For each new component, provide its own `deploy.sh` and
`<application>.sh` test launcher. Adapt deployment and launch to the
component's localization mechanism and document their effects. Do not assume
that other applications use the Control Panel's Python gettext setup.

## Testing Swap Control

```bash
bash swap-control/deploy.sh
bash swap-control/anduinos-swapcontrol.sh
```

Deployment validates and compiles the catalog before placing it in
`~/.local/share/anduinos-swapcontrol/locale/`. It leaves an identical catalog
unchanged and does not modify system files. The launcher resolves the catalog
through `XDG_DATA_DIRS` and forces `LC_ALL=hr_HR.UTF-8` with
`LANGUAGE=hr_HR`, so it is Croatian regardless of the session language. Both
variables are required: `LC_ALL` makes gettext search the user-local
directory, and `LANGUAGE` selects its `hr_HR` subdirectory when the desktop
session already exports a language list such as `hr:en_US:en`.

The desktop entry `com.anduinos.swapcontrol.desktop` and the polkit policy
still come from the system package, so an ordinary launch from GNOME search
shows the English name and the untranslated authentication prompt. Close a
running instance before testing, because the application may otherwise reuse
its existing window.

The Swap Control catalog also carries the desktop entry and polkit strings, so
the translation can be contributed upstream unchanged.

## Testing AnduinOS Firewall

```bash
bash firewall/deploy.sh
LANGUAGE=hr_HR bash firewall/anduinos-firewall.sh
```

The Firewall application is a compiled GTK application. Its launcher searches
for its gettext catalog through `XDG_DATA_DIRS`, so the test launcher points it
at the user-local catalog and selects Croatian. Deployment validates and builds
the catalog before placing it in
`~/.local/share/anduinos-ufwall-gtk/locale/`; it does not modify system files.
The desktop entry and PolicyKit prompts remain system-provided and are not
changed by this user-local test setup. Close any running Firewall instance
before testing, because the application may otherwise reuse its existing
window.

## Testing AnduinOS YubiKey Security Center

```bash
bash yubikey-security-center/deploy.sh
LANGUAGE=hr_HR bash yubikey-security-center/anduinos-yubikey-manager.sh
```

The Security Center uses the `anduinos-yubikey-manager` gettext domain. Its
launcher adds the user-local catalog directory to `XDG_DATA_DIRS` and selects
Croatian. Deployment validates and builds the catalog before placing it in
`~/.local/share/anduinos-yubikey-manager/locale/`; it does not modify system
files. The desktop entry and PolicyKit prompt remain system-provided and are
not changed by this user-local test setup. Close any running Security Center
instance before testing, because the application may otherwise reuse its
existing window.

## System-wide Installation

The user-local `deploy.sh` scripts are meant for testing: each one redirects a
single application to `~/.local/share/...`, so the desktop entries and every
other launch path keep using the untranslated system catalog. To translate the
applications when they are started normally, for example from the GNOME
application grid, install the compiled catalogs system-wide:

```bash
sudo bash scripts/install-system.sh
```

The script builds and checks every listed component with
`scripts/translate.sh`, then installs the resulting `.mo` files into
`/usr/share/locale/hr/LC_MESSAGES/`, which is the directory those applications
read. The language-only `hr` directory is intentional: glibc only falls back
from `hr_HR` to `hr` and never the other way round, and AnduinOS ships
`LANGUAGE=hr:en_US:en` by default. A `hr_HR`-only catalog would therefore be
invisible in a stock desktop session. Python's gettext and the gettext-rs
crate used by the GTK applications both resolve the `hr` directory for a `hr`
or `hr_HR` selection.

Every installed path is recorded with its checksum in
`/var/lib/anduinos-hr-translations/manifest.tsv`, so the installer never
overwrites a catalog it does not own (another distribution package, for
example) without `--force`, and `--uninstall` removes only its own files:

```bash
bash scripts/install-system.sh --list
sudo bash scripts/install-system.sh --package firewall
sudo bash scripts/install-system.sh --dry-run
sudo bash scripts/install-system.sh --uninstall
```

`--package NAME` restricts any action to one component and is repeatable.
`--destdir DIR` prepends a directory to every path, which is how the tests
exercise the script without root. Adding a component to the project is not
enough; list it in `scripts/install-system.sh` once its `hr_HR.po` is complete
so that a partially translated catalog is never installed system-wide.

Only gettext catalogs are installed. The desktop entries and PolicyKit
actions are shipped by the distribution packages, and the project does not
modify them; their Croatian strings are kept in the catalogs for upstream
contribution. Uninstalling does not require removing the user-local
deployments, though both can coexist.
