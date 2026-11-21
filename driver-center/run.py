#!/usr/bin/python3
import gettext
from pathlib import Path


DOMAIN = "anduinos-driver-center"
LOCALE_DIR = Path.home() / ".local/share/anduinos-driver-center/locale"
CATALOG = LOCALE_DIR / "hr_HR/LC_MESSAGES" / f"{DOMAIN}.mo"
_bindtextdomain = gettext.bindtextdomain


def _bind_user_catalog(domain, localedir=None):
    if domain == DOMAIN:
        localedir = str(LOCALE_DIR)
    return _bindtextdomain(domain, localedir)


def main():
    if not CATALOG.is_file():
        raise SystemExit(
            f"Translation not deployed: {CATALOG}\n"
            "Run: bash driver-center/deploy.sh"
        )

    gettext.bindtextdomain = _bind_user_catalog
    from anduinos_driver_center.app import main as app_main

    return app_main()


if __name__ == "__main__":
    raise SystemExit(main())
