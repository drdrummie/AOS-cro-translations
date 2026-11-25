# Vision

Make AnduinOS easier to use in Croatian by maintaining reliable, locally
testable UI translations and providing a practical path toward Croatian
language support in the distribution.

## Goals
- Translate and maintain Croatian UI catalogs for AnduinOS components and
  relevant applications and GNOME Shell extensions used with AnduinOS.
- Give Croatian users clear, safe ways to test translations locally and
  install supported catalogs for everyday use.
- Prepare accurate, maintainable translations and component-specific context
  that help AnduinOS developers and other upstream maintainers adopt them.
- Track the source versions behind catalogs and review changes when upstream
  applications or their messages change.

## Target users
- Croatian AnduinOS users who want a consistent, understandable localized UI.
- Translators and contributors who need to review, validate, and test catalogs.
- AnduinOS developers and upstream maintainers who may integrate Croatian
  translations into their projects and the distribution.

## Principles
- Prefer natural, consistent Croatian that fits the UI and preserves the
  meaning of the source.
- Keep each component's gettext resources in its own directory; preserve
  message identifiers, contexts, plural forms, and format placeholders.
- Adapt deployment and testing to each application's localization mechanism
  and gettext domain rather than assuming a common runtime.
- Make small, reviewable changes and document relevant version and
  compatibility limitations. Respect upstream ownership and licenses.
- Validate before deployment. Never install or overwrite system or user-local
  translations without an explicit user request.

## Out of scope
- Changing application behavior or redesigning AnduinOS instead of translating
  its UI.
- Claiming Croatian is officially supported or that translations have been
  accepted upstream before that happens.
- Submitting contributions upstream or modifying installed translations
  without human authorization.

## Quality bar
- Run `bash scripts/translate.sh check <package>` for each changed catalog.
- Run `python3 -m unittest discover -s tests -v` for workflow changes, and add
  focused tests for new or corrected behavior.
- Review translations in context, including placeholders and plurals; test
  affected UI locally when feasible without modifying installed translations.
- Report validation failures and document deployment and compatibility
  limitations; do not treat incomplete or unverified work as complete.

## Protected areas
Paths (globs in backticks) and topics that always need a human. The factory
never merges changes that touch them; they go to your inbox.
- `.github/workflows/**`
- `LICENSE`
- `scripts/install-system.sh`
- System-wide or user-local installation and overwrite behavior
- Licensing and third-party material
- Upstream submissions
