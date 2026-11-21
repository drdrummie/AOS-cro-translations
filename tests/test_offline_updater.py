import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class OfflineUpdaterDeploymentTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.project = self.root / "project"
        self.component = self.project / "offline-updater"
        self.component.mkdir(parents=True)
        (self.project / "scripts").mkdir()
        for name in (
            "anduinos-offline-updater.pot",
            "hr_HR.po",
            "anduinos-offline-updater.sh",
            "deploy.sh",
            "run.py",
        ):
            shutil.copy(ROOT / "offline-updater" / name, self.component)
        shutil.copy(ROOT / "scripts/translate.sh", self.project / "scripts")
        self.home = self.root / "home"
        self.home.mkdir()
        self.target = (
            self.home / ".local/share/anduinos-offline-updater/locale"
            / "hr_HR/LC_MESSAGES/anduinos-offline-updater.mo"
        )
        self.stub = self.root / "stubs/anduinos_offline_updater"
        self.stub.mkdir(parents=True)
        (self.stub / "__init__.py").write_text("", encoding="utf-8")
        (self.stub / "gui.py").write_text(
            'import gettext\n'
            '_ = gettext.gettext\n'
            'def main():\n'
            '    print(_("Offline Updater"))\n'
            '    return 0\n',
            encoding="utf-8",
        )
        self.env = {
            **os.environ,
            "HOME": str(self.home),
            "PYTHONPATH": str(self.stub.parent),
        }

    def run_script(self, name):
        return subprocess.run(
            ["bash", str(self.component / name)],
            capture_output=True,
            text=True,
            env=self.env,
        )

    def test_deploy_and_launch_are_user_local_and_idempotent(self):
        missing = self.run_script("anduinos-offline-updater.sh")
        self.assertNotEqual(missing.returncode, 0)
        self.assertIn("Translation not deployed", missing.stderr)

        deployed = self.run_script("deploy.sh")
        self.assertEqual(deployed.returncode, 0, deployed.stderr)
        before = self.target.stat().st_mtime_ns
        result = self.run_script("anduinos-offline-updater.sh")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "Izvanmrežno ažuriranje")

        again = self.run_script("deploy.sh")
        self.assertEqual(again.returncode, 0, again.stderr)
        self.assertIn("already up to date", again.stdout)
        self.assertEqual(before, self.target.stat().st_mtime_ns)

    def test_invalid_catalog_does_not_replace_deployed_translation(self):
        self.assertEqual(self.run_script("deploy.sh").returncode, 0)
        original = self.target.read_bytes()
        catalog = self.component / "hr_HR.po"
        catalog.write_text(
            catalog.read_text(encoding="utf-8").replace(
                'msgstr "Izvanmrežno ažuriranje"', 'msgstr ""', 1
            ),
            encoding="utf-8",
        )
        self.assertNotEqual(self.run_script("deploy.sh").returncode, 0)
        self.assertEqual(self.target.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
