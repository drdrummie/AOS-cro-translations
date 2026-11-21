import importlib.util
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("welcome_runner", ROOT / "welcome/run.py")
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


class WelcomeDeploymentTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.project = self.root / "project"
        self.component = self.project / "welcome"
        self.component.mkdir(parents=True)
        (self.project / "scripts").mkdir()
        for name in ("anduinos-oobe.pot", "hr_HR.po", "deploy.sh"):
            shutil.copy(ROOT / "welcome" / name, self.component)
        shutil.copy(ROOT / "scripts/translate.sh", self.project / "scripts")
        self.home = self.root / "home"
        self.home.mkdir()
        self.target = (
            self.home / ".local/share/anduinos-oobe/locale"
            / "hr_HR/LC_MESSAGES/anduinos-oobe.mo"
        )
        self.env = {**os.environ, "HOME": str(self.home), "LANGUAGE": "hr_HR"}

    def deploy(self):
        return subprocess.run(
            ["bash", str(self.component / "deploy.sh")],
            capture_output=True,
            text=True,
            env=self.env,
        )

    def test_deploy_and_launch_use_user_catalog(self):
        with mock.patch.dict(os.environ, self.env, clear=True):
            with self.assertRaisesRegex(SystemExit, "Translation not deployed"):
                RUNNER.main()

        result = self.deploy()
        self.assertEqual(result.returncode, 0, result.stderr)
        before = self.target.stat().st_mtime_ns
        app = SimpleNamespace(_=lambda text: text)
        app.main = lambda: app._("Welcome Home.")
        with (
            mock.patch.dict(os.environ, self.env, clear=True),
            mock.patch.object(RUNNER, "SourceFileLoader") as loader,
            mock.patch.object(RUNNER, "spec_from_loader"),
            mock.patch.object(RUNNER, "module_from_spec", return_value=app),
        ):
            self.assertEqual(RUNNER.main(), "Dobro došli kući.")
            loader.return_value.exec_module.assert_called_once_with(app)

        again = self.deploy()
        self.assertEqual(again.returncode, 0, again.stderr)
        self.assertEqual(before, self.target.stat().st_mtime_ns)

    def test_invalid_catalog_does_not_replace_deployed_translation(self):
        self.assertEqual(self.deploy().returncode, 0)
        original = self.target.read_bytes()
        catalog = self.component / "hr_HR.po"
        catalog.write_text(
            catalog.read_text(encoding="utf-8").replace(
                'msgstr "Dobro došli kući."', 'msgstr ""', 1
            ),
            encoding="utf-8",
        )
        self.assertNotEqual(self.deploy().returncode, 0)
        self.assertEqual(self.target.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
