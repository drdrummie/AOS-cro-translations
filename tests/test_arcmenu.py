import gettext
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
UUID = "arcmenu@arcmenu.com"
SYSTEM_EXTENSION = Path("/usr/share/gnome-shell/extensions") / UUID
HEADER = (
    'msgid ""\n'
    'msgstr ""\n'
    '"Content-Type: text/plain; charset=UTF-8\\n"\n'
    '"Language: hr_HR\\n"\n'
)


@unittest.skipUnless(SYSTEM_EXTENSION.is_dir(), "System ArcMenu not installed")
class ArcMenuDeploymentTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.component = self.root / "extensions/arcmenu"
        self.component.mkdir(parents=True)
        (self.root / "scripts").mkdir()
        shutil.copy(ROOT / "scripts/translate.sh", self.root / "scripts")
        for name in ("deploy.sh", "arcmenu.sh"):
            shutil.copy(ROOT / "extensions/arcmenu" / name, self.component)
        (self.component / "arcmenu.pot").write_text(
            HEADER + '\nmsgid "Hello"\nmsgstr ""\n'
        )
        self.catalog = self.component / "hr_HR.po"
        self.catalog.write_text(HEADER + '\nmsgid "Hello"\nmsgstr "Bok"\n')
        self.home = self.root / "home"
        self.home.mkdir()
        self.target = self.home / ".local/share/gnome-shell/extensions" / UUID
        self.env = os.environ.copy()
        self.env.update(HOME=str(self.home))
        self.env.pop("XDG_DATA_HOME", None)

    def run_script(self, name):
        return subprocess.run(
            ["bash", str(self.component / name)],
            env=self.env,
            capture_output=True,
            text=True,
        )

    def test_deploy_copies_extension_and_refuses_existing_target(self):
        result = self.run_script("deploy.sh")
        self.assertEqual(result.returncode, 0, result.stderr)
        for language in ("hr", "hr_HR"):
            catalog = self.target / "locale" / language / "LC_MESSAGES" / "arcmenu.mo"
            self.assertTrue(catalog.is_file())
            self.assertEqual(catalog.read_bytes(), (
                self.component / "build/hr_HR/LC_MESSAGES/arcmenu.mo"
            ).read_bytes())
            with catalog.open("rb") as stream:
                self.assertEqual(gettext.GNUTranslations(stream).gettext("Hello"), "Bok")
        marker = self.target / "test-marker"
        marker.write_text("unchanged")
        result = self.run_script("deploy.sh")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(marker.read_text(), "unchanged")

    def test_invalid_catalog_does_not_create_user_extension(self):
        self.catalog.write_text(HEADER + '\nmsgid "Hello"\nmsgstr ""\n')
        result = self.run_script("deploy.sh")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.target.exists())

    def test_launcher_requires_the_user_extension_to_be_active(self):
        bindir = self.root / "bin"
        bindir.mkdir()
        executable = bindir / "gnome-extensions"
        executable.write_text(
            '#!/bin/sh\n'
            'if [ "$1" = info ]; then printf "  Path: %s\\n" "$EXTENSION_PATH"; '
            'else printf "%s\\n" "$*" > "$LAUNCH_LOG"; fi\n'
        )
        executable.chmod(0o755)
        log = self.root / "launch.log"
        self.env.update(
            PATH=f"{bindir}:{self.env['PATH']}",
            EXTENSION_PATH=str(SYSTEM_EXTENSION),
            LAUNCH_LOG=str(log),
        )
        self.assertNotEqual(self.run_script("arcmenu.sh").returncode, 0)
        self.assertFalse(log.exists())
        self.env["EXTENSION_PATH"] = str(self.target)
        result = self.run_script("arcmenu.sh")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(log.read_text().strip(), f"prefs {UUID}")


if __name__ == "__main__":
    unittest.main()
