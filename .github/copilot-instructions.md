# Project instructions

- Communicate with the user in Croatian.
- Write code, task names, filenames, messages, and project documentation in English.
  Croatian application translations
  and original upstream message strings are not project documentation.
- Keep each component's gettext resources in its own `<package>/`
  directory. Preserve message identifiers, format placeholders, and existing
  translation context when editing catalogs.
- For each component, provide a component-specific `deploy.sh` and
  `<application>.sh` for user-local deployment and testing. Adapt them to the
  application's localization mechanism; do not assume every app uses Python
  or the same gettext domain. Validate before deploying and report failures.
- Validate changes with `bash scripts/translate.sh check <package>` and run
  `python3 -m unittest discover -s tests -v` when changing the workflow.
- Do not install or overwrite system or user-local translations unless the
  user explicitly requests it.
