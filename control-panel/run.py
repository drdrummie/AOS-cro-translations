#!/usr/bin/python3
import gettext
from pathlib import Path

from anduinos_control_panel.app import main


domain = "anduinos-control-panel"
locale_dir = Path.home() / ".local/share/anduinos-control-panel/locale"
catalog = locale_dir / "hr_HR/LC_MESSAGES" / f"{domain}.mo"
if not catalog.is_file():
    raise SystemExit(
        f"Translation not deployed: {catalog}\n"
        "Run: bash control-panel/deploy.sh"
    )
if gettext.find(domain, str(locale_dir)):
    gettext.bindtextdomain(domain, str(locale_dir))

raise SystemExit(main())
