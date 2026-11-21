#!/usr/bin/python3
import gettext
from pathlib import Path

from anduinos_offline_updater import gui


domain = "anduinos-offline-updater"
locale_dir = Path.home() / ".local/share/anduinos-offline-updater/locale"
catalog = locale_dir / "hr_HR/LC_MESSAGES" / f"{domain}.mo"
if not catalog.is_file():
    raise SystemExit(
        f"Translation not deployed: {catalog}\n"
        "Run: bash offline-updater/deploy.sh"
    )

gui._ = gettext.translation(domain, str(locale_dir), languages=["hr_HR"]).gettext
raise SystemExit(gui.main())
