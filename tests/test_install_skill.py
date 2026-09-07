"""Tests for scripts/install_skill.py. Run with: python3 -B -m unittest discover -s tests -v"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "install_skill.py"
REAL_SKILL = REPO / "skills" / "sextant"


def run_installer(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-B", str(SCRIPT), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def make_source(root: Path) -> Path:
    """Build a small skill folder that includes files the installer must skip."""
    source = root / "sextant"
    (source / "references").mkdir(parents=True)
    (source / "__pycache__").mkdir()
    (source / "SKILL.md").write_text("---\nname: sextant\ndescription: t\n---\n# t\n", encoding="utf-8")
    (source / "references" / "notes.md").write_text("# notes\n", encoding="utf-8")
    (source / ".DS_Store").write_bytes(b"junk")
    (source / "._SKILL.md").write_bytes(b"junk")
    (source / "__pycache__" / "x.cpython-313.pyc").write_bytes(b"junk")
    return source


class InstallSkillTests(unittest.TestCase):
    def test_installs_real_skill_folder_completely(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp) / "host-skills"
            result = run_installer("--to", str(destination))
            self.assertEqual(result.returncode, 0, result.stderr)
            installed = destination / "sextant"
            expected = sorted(
                p.relative_to(REAL_SKILL)
                for p in REAL_SKILL.rglob("*")
                if p.is_file() and p.name != ".DS_Store" and not p.name.startswith("._") and "__pycache__" not in p.parts
            )
            actual = sorted(p.relative_to(installed) for p in installed.rglob("*") if p.is_file())
            self.assertEqual(actual, expected)
            self.assertIn("name: sextant", (installed / "SKILL.md").read_text(encoding="utf-8"))

    def test_dry_run_writes_nothing_and_lists_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp) / "host-skills"
            result = run_installer("--to", str(destination), "--dry-run")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(destination.exists())
            self.assertIn("SKILL.md", result.stdout)
            self.assertIn("Dry run", result.stdout)

    def test_refuses_to_overwrite_existing_installation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp) / "host-skills"
            existing = destination / "sextant"
            existing.mkdir(parents=True)
            marker = existing / "SKILL.md"
            marker.write_text("customized\n", encoding="utf-8")
            result = run_installer("--to", str(destination))
            self.assertEqual(result.returncode, 2)
            self.assertIn("already exists", result.stderr)
            self.assertEqual(marker.read_text(encoding="utf-8"), "customized\n")
            self.assertEqual([p.name for p in existing.iterdir()], ["SKILL.md"])

    def test_refuses_when_destination_is_a_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp) / "host-skills"
            destination.mkdir()
            elsewhere = Path(tmp) / "elsewhere"
            elsewhere.mkdir()
            (destination / "sextant").symlink_to(elsewhere)
            result = run_installer("--to", str(destination))
            self.assertEqual(result.returncode, 2)
            self.assertEqual(list(elsewhere.iterdir()), [])

    def test_skips_junk_and_bytecode(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = make_source(Path(tmp) / "src")
            destination = Path(tmp) / "host-skills"
            result = run_installer("--to", str(destination), "--source", str(source))
            self.assertEqual(result.returncode, 0, result.stderr)
            installed = destination / "sextant"
            names = sorted(p.relative_to(installed).as_posix() for p in installed.rglob("*") if p.is_file())
            self.assertEqual(names, ["SKILL.md", "references/notes.md"])
            self.assertFalse((installed / "__pycache__").exists())

    def test_rejects_missing_or_invalid_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp) / "host-skills"
            result = run_installer("--to", str(destination), "--source", str(Path(tmp) / "nope"))
            self.assertEqual(result.returncode, 3)
            self.assertFalse(destination.exists())
            no_skill = Path(tmp) / "sextant"
            no_skill.mkdir()
            result = run_installer("--to", str(destination), "--source", str(no_skill))
            self.assertEqual(result.returncode, 3)
            self.assertIn("SKILL.md", result.stderr)

    def test_requires_destination_argument(self) -> None:
        result = run_installer()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--to", result.stderr)


if __name__ == "__main__":
    unittest.main()
