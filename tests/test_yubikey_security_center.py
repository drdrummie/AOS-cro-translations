import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class YubiKeySecurityCenterDeploymentTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.project = self.root / "project"
        self.component = self.project / "yubikey-security-center"
        self.component.mkdir(parents=True)
        (self.project / "scripts").mkdir()
        for name in (
            "anduinos-yubikey-manager.pot",
            "hr_HR.po",
            "anduinos-yubikey-manager.sh",
            "deploy.sh",
        ):
            shutil.copy(ROOT / "yubikey-security-center" / name, self.component)
        shutil.copy(ROOT / "scripts/translate.sh", self.project / "scripts")
        self.home = self.root / "home"
        self.home.mkdir()
        self.target = (
            self.home
            / ".local/share/anduinos-yubikey-manager/locale/hr_HR/LC_MESSAGES"
            / "anduinos-yubikey-manager.mo"
        )
        self.stubs = self.root / "stubs"
        self.stubs.mkdir()
        self.application = self.stubs / "anduinos-yubikey-manager"
        self.application.write_text(
            "#!/usr/bin/env python3\n"
            "import gettext, os\n"
            "from pathlib import Path\n"
            'entries = os.environ["XDG_DATA_DIRS"].split(":")\n'
            "for entry in entries:\n"
            '    locale = Path(entry) / "locale"\n'
            "    if locale.is_dir():\n"
            "        break\n"
            "else:\n"
            '    raise SystemExit("no locale directory in XDG_DATA_DIRS")\n'
            'language = os.environ["LANGUAGE"].split(":")[0]\n'
            "catalog = gettext.translation(\n"
            '    "anduinos-yubikey-manager", str(locale), languages=[language]\n'
            ")\n"
            'print(entries[0])\n'
            'print(os.environ["LC_ALL"])\n'
            'print(os.environ["LANGUAGE"])\n'
            'print(catalog.gettext("Security Center"))\n',
            encoding="utf-8",
        )
        self.application.chmod(0o755)
        self.env = {
            **os.environ,
            "HOME": str(self.home),
            "PATH": f"{self.stubs}{os.pathsep}{os.environ['PATH']}",
            "LANGUAGE": "hr:en_US:en",
        }
        self.env.pop("LC_ALL", None)

    def run_script(self, name):
        return subprocess.run(
            ["bash", str(self.component / name)],
            capture_output=True,
            text=True,
            env=self.env,
        )

    def test_deploy_and_launch_use_user_catalog(self):
        missing = self.run_script("anduinos-yubikey-manager.sh")
        self.assertNotEqual(missing.returncode, 0)
        self.assertIn("Translation not deployed", missing.stderr)

        deployed = self.run_script("deploy.sh")
        self.assertEqual(deployed.returncode, 0, deployed.stderr)
        before = self.target.stat().st_mtime_ns
        result = self.run_script("anduinos-yubikey-manager.sh")
        self.assertEqual(result.returncode, 0, result.stderr)
        data_dir, locale, language, title = result.stdout.splitlines()
        self.assertEqual(
            data_dir, str(self.home / ".local/share/anduinos-yubikey-manager")
        )
        self.assertEqual(locale, "hr_HR.UTF-8")
        self.assertEqual(language, "hr_HR")
        self.assertEqual(title, "Centar sigurnosti")

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
                'msgstr "Centar sigurnosti"', 'msgstr ""', 1
            ),
            encoding="utf-8",
        )
        self.assertNotEqual(self.run_script("deploy.sh").returncode, 0)
        self.assertEqual(self.target.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
