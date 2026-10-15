"""Tests for scripts/lint.py and scripts/scaffold.py. Standard library only.

Run: python3 -m unittest discover -s tests
"""
import importlib.util
import io
import os
import shutil
import sys
import tempfile
import time
import unittest
from contextlib import redirect_stdout
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "skills" / "ai-workspace" / "scripts"


def load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


lint = load("lint")
scaffold = load("scaffold")

HAS_SYMLINKS = True
try:
    _d = tempfile.mkdtemp()
    os.symlink("x", os.path.join(_d, "y"))
except (OSError, NotImplementedError):
    HAS_SYMLINKS = False
finally:
    shutil.rmtree(_d, ignore_errors=True)


def quiet(fn, *args):
    with redirect_stdout(io.StringIO()):
        return fn(*args)


class WorkspaceCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.root = self.tmp / "ws"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def init(self, lang="en", extra=()):
        argv = ["init", str(self.root), "--lang", lang, *extra]
        if not HAS_SYMLINKS:
            argv.append("--no-symlink")
        self.assertEqual(quiet(scaffold.main, argv), 0)

    def project(self, rel, lang="en"):
        argv = ["project", str(self.root / rel), "--lang", lang]
        if not HAS_SYMLINKS:
            argv.append("--no-symlink")
        self.assertEqual(quiet(scaffold.main, argv), 0)

    def run_lint(self, **kw):
        linter = lint.Linter(self.root, **kw)
        linter.run()
        return linter

    def codes(self, linter, level=None):
        return [f.code for f in linter.findings if level is None or f.level == level]

    def write(self, rel, text):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        return p

    def append(self, rel, text):
        p = self.root / rel
        with open(p, "a", encoding="utf-8") as fh:
            fh.write(text)


class TestScaffoldPassesItsOwnLint(WorkspaceCase):
    def check_clean(self, lang):
        self.init(lang)
        self.project("projects/alpha", lang)
        self.project("projects/beta", lang)
        self.append("AGENTS.md", "| Alpha | projects/alpha | A small test project | 🚧 |\n")
        linter = self.run_lint()
        self.assertEqual([(f.code, f.path, f.message) for f in linter.findings], [])

    def test_english(self):
        self.check_clean("en")

    def test_chinese(self):
        self.check_clean("zh")

    def test_minimal_layout_drops_forks_and_vendor(self):
        self.init("zh", ["--layout", "minimal"])
        text = (self.root / "AGENTS.md").read_text(encoding="utf-8")
        self.assertNotIn("`forks/`", text)
        self.assertFalse((self.root / "vendor").exists())
        self.assertEqual(self.codes(self.run_lint()), [])

    def test_init_refuses_existing_workspace(self):
        self.write("CLAUDE.md", "# rules\n")
        argv = ["init", str(self.root)]
        self.assertEqual(quiet(scaffold.main, argv), 3)
        self.assertFalse((self.root / "AGENTS.md").exists())

    def test_never_overwrites(self):
        self.init()
        self.write("projects/x/STATUS.md", "# mine\n\n## Current state\n- keep me\n\n## Next entry\n- me too\n")
        self.project("projects/x")
        self.assertIn("keep me", (self.root / "projects/x/STATUS.md").read_text(encoding="utf-8"))

    def test_no_symlink_writes_import_stub(self):
        self.init(extra=["--no-symlink"])
        claude = self.root / "CLAUDE.md"
        self.assertFalse(claude.is_symlink())
        self.assertEqual(claude.read_text(encoding="utf-8").strip(), "@AGENTS.md")
        self.assertNotIn("L201", self.codes(self.run_lint()))

    def test_project_keeps_existing_claude_md_as_real_file(self):
        self.init()
        self.write("projects/old/CLAUDE.md", "# old\n")
        self.project("projects/old")
        agents = self.root / "projects/old/AGENTS.md"
        if HAS_SYMLINKS:
            self.assertTrue(agents.is_symlink())
            self.assertEqual(os.readlink(agents), "CLAUDE.md")
        self.assertEqual((self.root / "projects/old/CLAUDE.md").read_text(encoding="utf-8"), "# old\n")


class TestFindings(WorkspaceCase):
    def setUp(self):
        super().setUp()
        self.init()
        self.project("projects/alpha")

    def test_missing_root(self):
        os.remove(self.root / "AGENTS.md")
        os.remove(self.root / "CLAUDE.md")
        self.assertIn("R001", self.codes(self.run_lint(), "error"))

    def test_root_over_budget(self):
        self.append("AGENTS.md", "\nfiller line\n" * 120)
        self.assertIn("B101", self.codes(self.run_lint()))

    def test_two_real_instruction_files(self):
        os.remove(self.root / "projects/alpha/CLAUDE.md")
        self.write("projects/alpha/CLAUDE.md", "# a different copy\n")
        self.assertIn("L201", self.codes(self.run_lint(), "error"))

    @unittest.skipUnless(HAS_SYMLINKS, "needs symlinks")
    def test_broken_symlink(self):
        os.remove(self.root / "projects/alpha/CLAUDE.md")
        os.symlink("GONE.md", self.root / "projects/alpha/CLAUDE.md")
        self.assertIn("L202", self.codes(self.run_lint(), "error"))

    def test_claude_only_folder(self):
        self.write("projects/beta/CLAUDE.md", "# beta\n")
        self.assertIn("L203", self.codes(self.run_lint(), "warn"))

    def test_status_without_hand_off(self):
        self.write("projects/alpha/STATUS.md", "# alpha\n\n## Log\n- did things\n")
        codes = self.codes(self.run_lint())
        self.assertIn("S301", codes)
        self.assertIn("S302", codes)

    def test_status_body_budget_ignores_archive(self):
        body = "# a\n\n## Current state\n- ok\n\n## Next entry\n- go\n\n## Archive\n" + "- old\n" * 150
        self.write("projects/alpha/STATUS.md", body)
        codes = self.codes(self.run_lint())
        self.assertNotIn("B131", codes)
        self.write("projects/alpha/STATUS.md", body.replace("## Archive\n", "## Notes\n"))
        self.assertIn("B131", self.codes(self.run_lint()))

    def test_claude_md_with_import_and_extra_lines_is_a_pointer(self):
        os.remove(self.root / "projects/alpha/CLAUDE.md")
        self.write("projects/alpha/CLAUDE.md", "Follow AGENTS.md in full:\n\n@AGENTS.md\n\n- Claude-only tip\n")
        self.assertNotIn("L201", self.codes(self.run_lint()))

    def test_plan_without_status(self):
        os.remove(self.root / "projects/alpha/STATUS.md")
        self.assertIn("S303", self.codes(self.run_lint()))

    def test_long_index_line_date_and_missing_path(self):
        self.append("AGENTS.md",
                    "| Big | projects/alpha | " + "An index line that keeps going " * 4 + " | 🚧 |\n"
                    "| Gone | projects/nowhere | Short | ✅ |\n"
                    "| Dated | projects/alpha | Shipped 2026-01-02 | 📦 |\n")
        codes = self.codes(self.run_lint())
        self.assertIn("I401", codes)
        self.assertIn("P501", codes)
        self.assertIn("I402", codes)

    def test_chinese_width(self):
        self.append("AGENTS.md", "| 甲 | projects/alpha | " + "一" * 31 + " | 🚧 |\n")
        self.assertIn("I401", self.codes(self.run_lint()))
        self.assertEqual(lint.width("一" * 30), 60)

    def test_stale_active_project(self):
        self.append("AGENTS.md", "| Alpha | projects/alpha | Test | 🚧 |\n")
        later = time.time() + 40 * 86400
        self.assertIn("S305", self.codes(self.run_lint(now=later)))

    def test_memory_orphan_long_hook_and_truncation(self):
        self.write("memory/orphan.md", "---\nname: x\n---\nbody\n")
        self.write("memory/linked.md", "body\n")
        self.append("memory/MEMORY.md", "- [Linked](linked.md) — " + "very long hook " * 10 + "\n")
        codes = self.codes(self.run_lint())
        self.assertIn("M601", codes)
        self.assertIn("I403", codes)
        self.append("memory/MEMORY.md", "- [Linked](linked.md) — short\n" * 210)
        self.assertIn("B112", self.codes(self.run_lint(), "error"))

    def test_broken_link_in_memory(self):
        self.append("memory/MEMORY.md", "- [Missing](missing.md) — short\n")
        self.assertIn("P502", self.codes(self.run_lint()))

    def test_link_in_inline_code_is_ignored(self):
        self.append("AGENTS.md", "\nFormat: `- [Title](file-name.md) — hook`\n")
        self.assertNotIn("P502", self.codes(self.run_lint()))

    def test_same_fact_in_two_places(self):
        fact = "The staging database lives on the second server and resets every night at two."
        self.append("projects/alpha/STATUS.md", "")
        self.write("projects/alpha/STATUS.md",
                   "# a\n\n## Current state\n- " + fact + "\n\n## Next entry\n- go\n")
        self.append("AGENTS.md", "\n" + fact + "\n")
        self.assertIn("D701", self.codes(self.run_lint()))

    def test_template_lines_are_not_duplicates(self):
        self.project("projects/beta")
        self.project("projects/gamma")
        self.assertNotIn("D701", self.codes(self.run_lint()))

    def test_unfilled_placeholder(self):
        self.append("projects/alpha/AGENTS.md", "\nOwner: {{OWNER}}\n")
        self.assertIn("T801", self.codes(self.run_lint()))

    def test_vendor_is_skipped(self):
        self.write("vendor/lib/CLAUDE.md", "# upstream\n" + "x\n" * 500)
        self.assertNotIn("B121", self.codes(self.run_lint()))

    def test_cli_exit_codes(self):
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(lint.main([str(self.root)]), 0)
            os.remove(self.root / "projects/alpha/CLAUDE.md")
            self.write("projects/alpha/CLAUDE.md", "# copy\n")
            self.assertEqual(lint.main([str(self.root), "--json"]), 1)
        self.assertIn('"L201"', out.getvalue())


if __name__ == "__main__":
    unittest.main()
