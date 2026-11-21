#!/usr/bin/env python3
import gettext
import runpy
import shutil
import sys
from pathlib import Path


DOMAIN = "anduinos-exe-runner"
LOCALE_DIR = Path.home() / ".local/share" / DOMAIN / "locale"


def main():
    application = shutil.which("anduinos-exe-runner")
    if not application:
        raise SystemExit("anduinos-exe-runner is not installed or not in PATH.")

    original_translation = gettext.translation

    def translation(
        domain, localedir=None, languages=None, class_=None, fallback=False
    ):
        if domain == DOMAIN:
            localedir = str(LOCALE_DIR)
            languages = ["hr_HR"]
        return original_translation(domain, localedir, languages, class_, fallback)

    gettext.translation = translation
    runpy.run_path(application, run_name="__main__")


if __name__ == "__main__":
    main()
