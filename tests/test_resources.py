import gettext
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ResourcesDeploymentTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.project = self.root / "project"
        self.component = self.project / "resources"
        self.component.mkdir(parents=True)
        (self.project / "scripts").mkdir()
        for name in ("resources.pot", "hr_HR.po", "deploy.sh", "resources.sh"):
            shutil.copy(ROOT / "resources" / name, self.component)
        shutil.copy(ROOT / "scripts/translate.sh", self.project / "scripts")
        self.home = self.root / "home"
        self.home.mkdir()
        self.catalog = self.home / ".local/share/resources/locale/hr/LC_MESSAGES/resources.mo"
        self.stubs = self.root / "stubs"
        self.stubs.mkdir()
        self.arguments = self.root / "arguments"
        (self.stubs / "bwrap").write_text(
            "#!/usr/bin/env bash\n"
            'printf "%s\\n" "$@" > "$ARGUMENTS_FILE"\n'
            'printf "Resursi\\n"\n',
            encoding="utf-8",
        )
        (self.stubs / "resources").write_text("#!/usr/bin/env bash\n", encoding="utf-8")
        for name in ("bwrap", "resources"):
            (self.stubs / name).chmod(0o755)
        self.env = {
            **os.environ,
            "HOME": str(self.home),
            "PATH": f"{self.stubs}:{os.environ['PATH']}",
            "ARGUMENTS_FILE": str(self.arguments),
        }

    def run_script(self, name, *args):
        return subprocess.run(
            ["bash", str(self.component / name), *args],
            capture_output=True,
            text=True,
            env=self.env,
        )

    def test_deploys_and_selects_catalog_without_changing_system_files(self):
        missing = self.run_script("resources.sh")
        self.assertNotEqual(missing.returncode, 0)
        self.assertIn("Translation not deployed", missing.stderr)

        deployed = self.run_script("deploy.sh")
        self.assertEqual(deployed.returncode, 0, deployed.stderr)
        self.assertTrue(self.catalog.is_file())
        before = self.catalog.stat().st_mtime_ns
        repeated = self.run_script("deploy.sh")
        self.assertEqual(repeated.returncode, 0, repeated.stderr)
        self.assertEqual(self.catalog.stat().st_mtime_ns, before)

        if not Path("/usr/share/locale/hr/LC_MESSAGES").is_dir():
            self.skipTest("System Croatian locale directory is unavailable")
        launched = self.run_script("resources.sh", "--check-translation")
        self.assertEqual(launched.returncode, 0, launched.stderr)
        arguments = self.arguments.read_text(encoding="utf-8").splitlines()
        self.assertIn(str(self.catalog), arguments)
        self.assertIn("/usr/share/locale/hr/LC_MESSAGES/resources.mo", arguments)
        self.assertIn("--tmpfs", arguments)
        device_mount = arguments.index("--dev-bind")
        self.assertEqual(arguments[device_mount + 1 : device_mount + 3], ["/dev", "/dev"])

    def test_invalid_catalog_does_not_replace_deployed_catalog(self):
        self.assertEqual(self.run_script("deploy.sh").returncode, 0)
        original = self.catalog.read_bytes()
        po = self.component / "hr_HR.po"
        po.write_text(
            po.read_text(encoding="utf-8").replace(
                'msgstr "Čitanje s diska"', 'msgstr ""', 1
            ),
            encoding="utf-8",
        )
        result = self.run_script("deploy.sh")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.catalog.read_bytes(), original)

    def test_runtime_placeholders_and_croatian_plural_forms(self):
        self.assertEqual(self.run_script("deploy.sh").returncode, 0)
        with self.catalog.open("rb") as stream:
            catalog = gettext.GNUTranslations(stream)
        for key, translation in catalog._catalog.items():
            if not key:
                continue
            if isinstance(key, tuple):
                self.assertEqual(translation.count("{}"), 1, key)
            else:
                self.assertEqual(translation.count("{}"), key.count("{}"), key)
        singular = "Successfully ended the process"
        plural = "Successfully ended {} processes"
        for count, expected in (
            (1, "Uspješno je završen 1 proces"),
            (2, "Uspješno su završena 2 procesa"),
            (5, "Uspješno je završeno 5 procesa"),
            (21, "Uspješno je završen 21 proces"),
        ):
            self.assertEqual(catalog.ngettext(singular, plural, count).format(count), expected)


if __name__ == "__main__":
    unittest.main()
