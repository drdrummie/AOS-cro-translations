import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DriverCenterDeploymentTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.project = self.root / "project"
        self.component = self.project / "driver-center"
        self.component.mkdir(parents=True)
        (self.project / "scripts").mkdir()
        for name in (
            "anduinos-driver-center.pot",
            "hr_HR.po",
            "anduinos-driver-center.sh",
            "deploy.sh",
            "run.py",
        ):
            shutil.copy(ROOT / "driver-center" / name, self.component)
        shutil.copy(ROOT / "scripts/translate.sh", self.project / "scripts")
        self.home = self.root / "home"
        self.home.mkdir()
        self.target = (
            self.home / ".local/share/anduinos-driver-center/locale"
            / "hr_HR/LC_MESSAGES/anduinos-driver-center.mo"
        )
        self.stub = self.root / "stubs/anduinos_driver_center"
        self.stub.mkdir(parents=True)
        (self.stub / "__init__.py").write_text("", encoding="utf-8")
        (self.stub / "app.py").write_text(
            'import gettext\n'
            'gettext.bindtextdomain("anduinos-driver-center", "/usr/share/locale")\n'
            'gettext.textdomain("anduinos-driver-center")\n'
            'def main():\n'
            '    print(gettext.gettext("AnduinOS Driver Center"))\n'
            '    return 0\n',
            encoding="utf-8",
        )
        self.env = {
            **os.environ,
            "HOME": str(self.home),
            "LANGUAGE": "hr_HR",
            "PYTHONPATH": str(self.stub.parent),
        }

    def run_script(self, name):
        return subprocess.run(
            ["bash", str(self.component / name)],
            capture_output=True,
            text=True,
            env=self.env,
        )

    def test_deploy_and_launch_use_user_catalog(self):
        missing = self.run_script("anduinos-driver-center.sh")
        self.assertNotEqual(missing.returncode, 0)
        self.assertIn("Translation not deployed", missing.stderr)

        deployed = self.run_script("deploy.sh")
        self.assertEqual(deployed.returncode, 0, deployed.stderr)
        before = self.target.stat().st_mtime_ns
        result = self.run_script("anduinos-driver-center.sh")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout.strip(),
            "AnduinOS centar za upravljačke programe",
        )

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
                'msgstr "AnduinOS centar za upravljačke programe"',
                'msgstr ""',
                1,
            ),
            encoding="utf-8",
        )
        result = self.run_script("deploy.sh")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.target.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
