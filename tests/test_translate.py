import gettext
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HEADER = (
    'msgid ""\n'
    'msgstr ""\n'
    '"Content-Type: text/plain; charset=UTF-8\\n"\n'
    '"Language: hr_HR\\n"\n'
)


class TranslationTasksTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / "scripts").mkdir()
        shutil.copy(ROOT / "scripts/translate.sh", self.root / "scripts")
        self.directory = self.root / "example"
        self.directory.mkdir(parents=True)
        self.template = self.directory / "example-domain.pot"
        self.catalog = self.directory / "hr_HR.po"
        self.template.write_text(HEADER + '\nmsgid "Hello"\nmsgstr ""\n')
        self.catalog.write_text(HEADER + '\nmsgid "Hello"\nmsgstr "Bok"\n')

    def run_task(self, action, package="example"):
        return subprocess.run(
            ["bash", str(self.root / "scripts/translate.sh"), action, package],
            capture_output=True,
            text=True,
        )

    def test_build_produces_a_usable_catalog(self):
        result = self.run_task("build")
        self.assertEqual(result.returncode, 0, result.stderr)
        output = self.directory / "build/hr_HR/LC_MESSAGES/example-domain.mo"
        with output.open("rb") as stream:
            self.assertEqual(gettext.GNUTranslations(stream).gettext("Hello"), "Bok")

    def test_update_adds_new_messages_and_check_rejects_untranslated(self):
        with self.template.open("a") as stream:
            stream.write('\nmsgid "Goodbye"\nmsgstr ""\n')
        self.assertEqual(self.run_task("update").returncode, 0)
        self.assertIn('msgid "Goodbye"', self.catalog.read_text())
        self.assertNotEqual(self.run_task("check").returncode, 0)
        self.assertNotEqual(self.run_task("build").returncode, 0)

    def test_rejects_fuzzy_messages_and_ambiguous_templates(self):
        self.catalog.write_text(HEADER + '\n#, fuzzy\nmsgid "Hello"\nmsgstr "Bok"\n')
        self.assertNotEqual(self.run_task("check").returncode, 0)
        (self.directory / "other.pot").write_text(HEADER)
        self.assertNotEqual(self.run_task("update").returncode, 0)

    def test_rejects_paths_as_package_names(self):
        self.assertNotEqual(self.run_task("check", "../example").returncode, 0)
        self.assertNotEqual(self.run_task("check", "extensions/../example").returncode, 0)
        self.assertNotEqual(self.run_task("check", "other/example").returncode, 0)

    def test_supports_extension_directories(self):
        extensions = self.root / "extensions"
        extensions.mkdir()
        self.directory.rename(extensions / "example")
        result = self.run_task("build", "extensions/example")
        self.assertEqual(result.returncode, 0, result.stderr)
        output = extensions / "example/build/hr_HR/LC_MESSAGES/example-domain.mo"
        with output.open("rb") as stream:
            self.assertEqual(gettext.GNUTranslations(stream).gettext("Hello"), "Bok")


if __name__ == "__main__":
    unittest.main()
