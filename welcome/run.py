#!/usr/bin/python3
import gettext
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from pathlib import Path


def main():
    domain = "anduinos-oobe"
    locale_dir = Path.home() / ".local/share/anduinos-oobe/locale"
    catalog = locale_dir / "hr_HR/LC_MESSAGES" / f"{domain}.mo"
    if not catalog.is_file():
        raise SystemExit(
            f"Translation not deployed: {catalog}\n"
            "Run: bash welcome/deploy.sh"
        )

    loader = SourceFileLoader("anduinos_oobe", "/usr/bin/anduinos-oobe")
    spec = spec_from_loader(loader.name, loader)
    if spec is None:
        raise RuntimeError("Could not load the installed AnduinOS Welcome application.")
    app = module_from_spec(spec)
    loader.exec_module(app)
    if gettext.find(domain, str(locale_dir)):
        app._ = gettext.translation(domain, str(locale_dir)).gettext
    return app.main()


if __name__ == "__main__":
    raise SystemExit(main())
