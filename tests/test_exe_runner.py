import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ExeRunnerDeploymentTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.project = self.root / "project"
        self.component = self.project / "exe-runner"
        self.component.mkdir(parents=True)
        (self.project / "scripts").mkdir()
        for name in (
            "anduinos-exe-runner.pot",
            "hr_HR.po",
            "anduinos-exe-runner.sh",
            "deploy.sh",
            "run.py",
        ):
            shutil.copy(ROOT / "exe-runner" / name, self.component)
        shutil.copy(ROOT / "scripts/translate.sh", self.project / "scripts")

        self.home = self.root / "home"
        self.home.mkdir()
        self.target = (
            self.home / ".local/share/anduinos-exe-runner/locale"
            / "hr_HR/LC_MESSAGES/anduinos-exe-runner.mo"
        )
        self.stubs = self.root / "stubs"
        self.stubs.mkdir()
        self.application = self.stubs / "anduinos-exe-runner"
        self.application.write_text(
            "import gettext, sys\n"
            "translate = gettext.translation(\n"
            "    'anduinos-exe-runner', '/usr/share/locale', fallback=True\n"
            ").gettext\n"
            "print(translate('Windows Application Runner'))\n"
            "print(sys.argv[1])\n",
            encoding="utf-8",
        )
        self.application.chmod(0o755)
        self.env = {
            **os.environ,
            "HOME": str(self.home),
            "LANGUAGE": "en_US",
            "PATH": f"{self.stubs}{os.pathsep}{os.environ['PATH']}",
        }

    def run_script(self, name, *args):
        return subprocess.run(
            ["bash", str(self.component / name), *args],
            capture_output=True,
            text=True,
            env=self.env,
        )

    def test_deploy_and_launcher_use_user_catalog(self):
        missing = self.run_script("anduinos-exe-runner.sh", "/tmp/example.exe")
        self.assertNotEqual(missing.returncode, 0)
        self.assertIn("Translation not deployed", missing.stderr)

        deployed = self.run_script("deploy.sh")
        self.assertEqual(deployed.returncode, 0, deployed.stderr)
        before = self.target.stat().st_mtime_ns
        result = self.run_script("anduinos-exe-runner.sh", "/tmp/example.exe")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout.splitlines(),
            ["Pokretač Windows aplikacija", "/tmp/example.exe"],
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
                'msgstr "Pokretač Windows aplikacija"',
                'msgstr ""',
                1,
            ),
            encoding="utf-8",
        )
        self.assertNotEqual(self.run_script("deploy.sh").returncode, 0)
        self.assertEqual(self.target.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
