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
    "flatseal",
    "anduinos-offline-updater",
    "anduinos-oobe",
    "anduinos-whisper-gtk",
    "anduinos-yubikey-manager",
    "resources",
    "swapcontrol-gtk",
    "ufwall-gtk",
)

APP_PACKAGES = {
    "appearance": "anduinos-appearance",
    "control-panel": "anduinos-control-panel",
    "driver-center": "anduinos-driver-center",
    "exe-runner": "anduinos-exe-runner",
    "flatseal": "flatseal",
    "firewall": "anduinos-ufwall-gtk",
    "offline-updater": "anduinos-offline-updater",
    "resources": "resources",
    "swap-control": "anduinos-swapcontrol-gtk",
    "welcome": "anduinos-oobe",
    "voice-typing": "anduinos-whisper-gtk",
    "yubikey-security-center": "anduinos-yubikey-manager",
}


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
        self.stub_dir = self.root / "stubs"
        self.stub_dir.mkdir()
        self.installed_packages = self.root / "installed-packages"
        self.installed_packages.write_text(
            "\n".join(APP_PACKAGES.values()) + "\n",
            encoding="utf-8",
        )
        (self.stub_dir / "dpkg-query").write_text(
            "#!/usr/bin/env bash\n"
            "set -euo pipefail\n"
            "package=\"\"\n"
            "for argument in \"$@\"; do\n"
            "    if [[ $argument != -* ]]; then package=$argument; fi\n"
            "done\n"
            "if grep -Fqx -- \"$package\" \"$INSTALLED_PACKAGES_FILE\"; then\n"
            "    printf 'installed'\n"
            "else\n"
            "    exit 1\n"
            "fi\n",
            encoding="utf-8",
        )
        (self.stub_dir / "dpkg-query").chmod(0o755)
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
            env={
                **os.environ,
                "PATH": f"{self.stub_dir}:{os.environ['PATH']}",
                "INSTALLED_PACKAGES_FILE": str(self.installed_packages),
            },
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
        with (self.locale_dir / "flatseal.mo").open("rb") as stream:
            catalog = gettext.GNUTranslations(stream)
        self.assertEqual(catalog.gettext("Flatpak Version"), "Verzija Flatpaka")
        self.assertIn(
            "usr/share/locale/hr/LC_MESSAGES/ufwall-gtk.mo",
            self.manifest.read_text(encoding="utf-8"),
        )

    def test_skips_catalog_when_application_package_is_missing(self):
        packages = self.installed_packages.read_text(encoding="utf-8")
        packages = packages.replace("anduinos-ufwall-gtk\n", "")
        self.installed_packages.write_text(packages, encoding="utf-8")

        result = self.run_script("--package", "firewall")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Skipping firewall", result.stdout)
        self.assertFalse((self.locale_dir / "ufwall-gtk.mo").exists())
        self.assertFalse(self.manifest.exists())

    def test_installs_flatseal_catalog_when_debian_package_is_present(self):
        result = self.run_script("--package", "flatseal")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.locale_dir / "flatseal.mo").is_file())

    def test_installs_resources_catalog_when_debian_package_is_present(self):
        result = self.run_script("--package", "resources")
        self.assertEqual(result.returncode, 0, result.stderr)
        with (self.locale_dir / "resources.mo").open("rb") as stream:
            catalog = gettext.GNUTranslations(stream)
        self.assertEqual(catalog.gettext("Drive Read"), "Čitanje s diska")

    def test_installs_voice_typing_catalog_when_debian_package_is_present(self):
        result = self.run_script("--package", "voice-typing")

        self.assertEqual(result.returncode, 0, result.stderr)
        catalog_path = self.locale_dir / "anduinos-whisper-gtk.mo"
        self.assertTrue(catalog_path.is_file())
        with catalog_path.open("rb") as stream:
            catalog = gettext.GNUTranslations(stream)
        self.assertEqual(catalog.gettext("Settings"), "Postavke")
        self.assertEqual(
            catalog.gettext("Loading speech model…"),
            "Učitavanje modela govora…",
        )
        self.assertEqual(
            catalog.gettext(
                "Balanced — included and recommended for most computers"
            ),
            "Uravnotežen — uključen i preporučen za većinu računala",
        )

    def test_skips_flatseal_when_not_installed_as_debian_package(self):
        packages = self.installed_packages.read_text(encoding="utf-8")
        self.installed_packages.write_text(
            packages.replace("flatseal\n", ""),
            encoding="utf-8",
        )

        result = self.run_script("--package", "flatseal")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Skipping flatseal", result.stdout)
        self.assertFalse((self.locale_dir / "flatseal.mo").exists())

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
        self.assertIn("catalog missing", before.stdout)
        packages = self.installed_packages.read_text(encoding="utf-8")
        self.installed_packages.write_text(
            packages.replace("anduinos-ufwall-gtk\n", ""),
            encoding="utf-8",
        )
        missing_application = self.run_script("--list", "--package", "firewall")
        self.assertEqual(
            missing_application.returncode, 0, missing_application.stderr
        )
        self.assertIn("application missing", missing_application.stdout)

        self.installed_packages.write_text(packages, encoding="utf-8")
        self.assertEqual(self.run_script().returncode, 0)
        after = self.run_script("--list")
        self.assertNotIn("catalog missing", after.stdout)
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
