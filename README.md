# Croatian translations for AnduinOS

Each component has its own translation directory:

```text
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
```

The POT file is the message template; the PO file contains the Croatian
translation. The Control Panel and Welcome templates were extracted from the
locally installed versions; the Driver Center template was extracted from its
installed Python sources and the Secure Boot toolkit UI, with desktop-entry
and PolicyKit messages included for upstream contribution. The Swap Control
template was taken from the maintainers' `po/swapcontrol-gtk.pot`. Before
contributing upstream, compare each template with the current source code and
the maintainers' templates.

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
