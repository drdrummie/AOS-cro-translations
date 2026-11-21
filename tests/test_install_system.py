import gettext
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOMAINS = (
    "anduinos-appearance",
    "anduinos-control-panel",
    "anduinos-driver-center",
    "anduinos-exe-runner",
    "anduinos-offline-updater",
    "anduinos-oobe",
    "anduinos-yubikey-manager",
    "swapcontrol-gtk",
    "ufwall-gtk",
)


def translated_components():
    return sorted(
        path.name
        for path in ROOT.iterdir()
        if path.is_dir() and (path / "hr_HR.po").is_file()
    )


class SystemInstallTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.project = self.root / "project"
        (self.project / "scripts").mkdir(parents=True)
        for script in ("translate.sh", "install-system.sh"):
            shutil.copy(ROOT / "scripts" / script, self.project / "scripts")
        self.components = translated_components()
        for name in self.components:
            component = self.project / name
            component.mkdir()
            for template in (ROOT / name).glob("*.pot"):
                shutil.copy(template, component)
            shutil.copy(ROOT / name / "hr_HR.po", component)
        self.destdir = self.root / "stage"
        self.locale_dir = self.destdir / "usr/share/locale/hr/LC_MESSAGES"
        self.manifest = (
            self.destdir / "var/lib/anduinos-hr-translations/manifest.tsv"
        )

    def run_script(self, *arguments):
        return subprocess.run(
            [
                "bash",
                str(self.project / "scripts/install-system.sh"),
                "--destdir",
                str(self.destdir),
                *arguments,
            ],
            capture_output=True,
            text=True,
        )

    def test_installs_all_catalogs_into_language_directory(self):
        result = self.run_script()
        self.assertEqual(result.returncode, 0, result.stderr)
        for domain in DOMAINS:
            self.assertTrue((self.locale_dir / f"{domain}.mo").is_file(), domain)
        self.assertFalse((self.destdir / "usr/share/locale/hr_HR").exists())
        with (self.locale_dir / "anduinos-appearance.mo").open("rb") as stream:
            catalog = gettext.GNUTranslations(stream)
        self.assertEqual(
            catalog.gettext("AnduinOS Appearance"), "Izgled AnduinOS-a"
        )
        self.assertIn(
            "usr/share/locale/hr/LC_MESSAGES/ufwall-gtk.mo",
            self.manifest.read_text(encoding="utf-8"),
        )

    def test_second_run_leaves_catalogs_untouched(self):
        self.assertEqual(self.run_script().returncode, 0)
        target = self.locale_dir / "ufwall-gtk.mo"
        before = target.stat().st_mtime_ns
        again = self.run_script()
        self.assertEqual(again.returncode, 0, again.stderr)
        self.assertIn("Up to date", again.stdout)
        self.assertEqual(before, target.stat().st_mtime_ns)

    def test_refuses_to_overwrite_foreign_catalog_unless_forced(self):
        self.locale_dir.mkdir(parents=True)
        target = self.locale_dir / "ufwall-gtk.mo"
        target.write_text("foreign", encoding="utf-8")
        refused = self.run_script("--package", "firewall")
        self.assertNotEqual(refused.returncode, 0)
        self.assertIn("Refusing to overwrite", refused.stderr)
        self.assertEqual(target.read_text(encoding="utf-8"), "foreign")
        forced = self.run_script("--package", "firewall", "--force")
        self.assertEqual(forced.returncode, 0, forced.stderr)
        self.assertNotEqual(target.read_bytes(), b"foreign")

    def test_uninstall_keeps_modified_catalogs_until_forced(self):
        self.assertEqual(self.run_script("--package", "firewall").returncode, 0)
        self.assertEqual(self.run_script("--package", "welcome").returncode, 0)
        modified = self.locale_dir / "anduinos-oobe.mo"
        modified.write_bytes(modified.read_bytes() + b"\0")

        kept = self.run_script("--uninstall")
        self.assertNotEqual(kept.returncode, 0)
        self.assertIn("Keeping locally modified catalog", kept.stderr)
        self.assertFalse((self.locale_dir / "ufwall-gtk.mo").exists())
        self.assertTrue(modified.exists())

        removed = self.run_script("--uninstall", "--force")
        self.assertEqual(removed.returncode, 0, removed.stderr)
        self.assertFalse(self.locale_dir.exists())
        self.assertFalse(self.manifest.exists())

    def test_uninstall_package_only_touches_that_component(self):
        self.assertEqual(self.run_script().returncode, 0)
        result = self.run_script("--uninstall", "--package", "firewall")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.locale_dir / "ufwall-gtk.mo").exists())
        self.assertTrue((self.locale_dir / "anduinos-oobe.mo").exists())

    def test_list_reports_install_state(self):
        before = self.run_script("--list")
        self.assertEqual(before.returncode, 0, before.stderr)
        self.assertIn("not installed", before.stdout)
        self.assertEqual(self.run_script().returncode, 0)
        after = self.run_script("--list")
        self.assertNotIn("not installed", after.stdout)
        self.assertIn("firewall", after.stdout)

    def test_dry_run_changes_nothing(self):
        result = self.run_script("--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Would install", result.stdout)
        self.assertFalse(self.destdir.exists())

    def test_rejects_unknown_component(self):
        result = self.run_script("--package", "does-not-exist")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unknown component", result.stderr)

    @unittest.skipIf(os.geteuid() == 0, "root can write the system locale path")
    def test_requires_root_outside_destdir(self):
        result = subprocess.run(
            ["bash", str(self.project / "scripts/install-system.sh")],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("requires root privileges", result.stderr)


if __name__ == "__main__":
    unittest.main()
