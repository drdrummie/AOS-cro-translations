import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class FlatsealDeploymentTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.project = self.root / "project"
        self.component = self.project / "flatseal"
        self.component.mkdir(parents=True)
        (self.project / "scripts").mkdir()
        for name in (
            "flatseal.pot",
            "hr_HR.po",
            "flatseal-test.js",
            "deploy.sh",
            "flatseal.sh",
        ):
            shutil.copy(ROOT / "flatseal" / name, self.component)
        shutil.copy(ROOT / "scripts/translate.sh", self.project / "scripts")

        self.home = self.root / "home"
        self.home.mkdir()
        self.data_dir = self.home / ".local/share/flatseal"
        self.catalog = self.data_dir / "locale/hr/LC_MESSAGES/flatseal.mo"
        self.launcher = self.data_dir / "flatseal-test.js"

        self.stub_dir = self.root / "stubs"
        self.stub_dir.mkdir()
        self.flatpak_args = self.root / "flatpak-args"
        (self.stub_dir / "flatpak").write_text(
            "#!/usr/bin/env bash\n"
            "set -euo pipefail\n"
            "if [[ $1 == info ]]; then exit 0; fi\n"
            "if [[ $1 == run ]]; then\n"
            f"    printf '%s\\n' \"$@\" > {self.flatpak_args}\n"
            "    exit 0\n"
            "fi\n"
            "exit 2\n",
            encoding="utf-8",
        )
        (self.stub_dir / "flatpak").chmod(0o755)
        self.env = {
            **os.environ,
            "HOME": str(self.home),
            "PATH": f"{self.stub_dir}:{os.environ['PATH']}",
        }

    def run_script(self, name, *args):
        return subprocess.run(
            ["bash", str(self.component / name), *args],
            capture_output=True,
            text=True,
            env=self.env,
        )

    def test_deploys_user_local_catalog_and_launcher_for_flatpak(self):
        missing = self.run_script("flatseal.sh")
        self.assertNotEqual(missing.returncode, 0)
        self.assertIn("Translation not deployed", missing.stderr)

        result = self.run_script("deploy.sh")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(self.catalog.is_file())
        self.assertTrue(self.launcher.is_file())

        deployed_catalog = self.catalog.read_bytes()
        deployed_launcher = self.launcher.read_bytes()
        repeated = self.run_script("deploy.sh")
        self.assertEqual(repeated.returncode, 0, repeated.stderr)
        self.assertIn("already up to date", repeated.stdout)
        self.assertEqual(self.catalog.read_bytes(), deployed_catalog)
        self.assertEqual(self.launcher.read_bytes(), deployed_launcher)

        launched = self.run_script("flatseal.sh", "--check-translation")
        self.assertEqual(launched.returncode, 0, launched.stderr)
        args = self.flatpak_args.read_text(encoding="utf-8").splitlines()
        self.assertIn(f"--filesystem={self.data_dir}:ro", args)
        self.assertIn(f"--env=FLATSEAL_TRANSLATION_DIR={self.data_dir}/locale", args)
        self.assertIn("--env=LANGUAGE=hr:en_US:en", args)
        self.assertIn("--command=gjs", args)
        self.assertIn("com.github.tchx84.Flatseal", args)
        self.assertIn(str(self.launcher), args)
        self.assertIn("--check-translation", args)

    def test_invalid_catalog_does_not_replace_deployed_files(self):
        deployed = self.run_script("deploy.sh")
        self.assertEqual(deployed.returncode, 0, deployed.stderr)
        original_catalog = self.catalog.read_bytes()
        original_launcher = self.launcher.read_bytes()

        catalog = self.component / "hr_HR.po"
        catalog.write_text(
            catalog.read_text(encoding="utf-8").replace(
                'msgstr "Verzija Flatpaka"', 'msgstr ""', 1
            ),
            encoding="utf-8",
        )
        result = self.run_script("deploy.sh")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.catalog.read_bytes(), original_catalog)
        self.assertEqual(self.launcher.read_bytes(), original_launcher)


if __name__ == "__main__":
    unittest.main()
