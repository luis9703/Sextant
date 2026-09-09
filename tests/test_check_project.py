"""Tests for scripts/check_project.py. Run with: python3 -B -m unittest discover -s tests -v"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "check_project.py"


def run_check(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-B", str(SCRIPT), "--root", str(root), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def make_repo(
    root: Path,
    *,
    version: str = "0.1.0",
    skill_name: str = "sextant",
    readme_link: str = "skills/sextant/SKILL.md",
    changelog_version: str | None = None,
) -> Path:
    skill = root / "skills" / "sextant"
    (skill / "references").mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\n"
        f"name: {skill_name}\n"
        'description: "A test skill."\n'
        "metadata:\n"
        f'  version: "{version}"\n'
        "---\n\n# Test\n\nRead [notes](references/notes.md).\n",
        encoding="utf-8",
    )
    (skill / "references" / "notes.md").write_text("# Notes\n", encoding="utf-8")
    (skill / "agents").mkdir()
    (skill / "agents" / "openai.yaml").write_text(
        'interface:\n  display_name: "Test"\n  short_description: "Test skill"\n',
        encoding="utf-8",
    )
    (root / "README.md").write_text(
        f"# Test\n\nVersion **{version}**. See the [skill]({readme_link}).\n",
        encoding="utf-8",
    )
    (root / "CHANGELOG.md").write_text(
        f"# Changelog\n\n## [{changelog_version or version}] - 2026-01-01\n\n- initial\n",
        encoding="utf-8",
    )
    return root


class CheckProjectTests(unittest.TestCase):
    def test_repository_passes_check(self) -> None:
        result = run_check(REPO)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("0 errors", result.stdout)

    def test_clean_synthetic_repository_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            result = run_check(root)
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertIn("0 errors, 0 warnings", result.stdout)

    def test_broken_document_link_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp), readme_link="examples/missing/report.md")
            result = run_check(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("broken link: examples/missing/report.md", result.stdout)

    def test_links_inside_code_are_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            readme = root / "README.md"
            readme.write_text(
                readme.read_text(encoding="utf-8")
                + "\n```text\n[not a link](missing.md)\n```\n\nAnd `[inline](also-missing.md)`.\n",
                encoding="utf-8",
            )
            result = run_check(root)
            self.assertEqual(result.returncode, 0, result.stdout)

    def test_skill_link_leaving_folder_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            skill_md = root / "skills" / "sextant" / "SKILL.md"
            skill_md.write_text(
                skill_md.read_text(encoding="utf-8") + "\nSee [readme](../../README.md).\n",
                encoding="utf-8",
            )
            result = run_check(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("leaves the skill folder", result.stdout)

    def test_name_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp), skill_name="Sextant Skill")
            result = run_check(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("does not match folder name", result.stdout)

    def test_version_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp), changelog_version="0.2.0")
            result = run_check(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("differs from SKILL.md version", result.stdout)

    def test_machine_path_and_env_file_fail(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            (root / "docs").mkdir()
            home = "/Users" + "/someone/"
            (root / "docs" / "notes.md").write_text(f"Runs live in {home}work/run1.\n", encoding="utf-8")
            (root / ".env").write_text("TOKEN=x\n", encoding="utf-8")
            result = run_check(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("macOS home path", result.stdout)
            self.assertIn("environment file", result.stdout)

    def test_cache_directory_warns_and_strict_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            (root / "scripts" / "__pycache__").mkdir(parents=True)
            self.assertEqual(run_check(root).returncode, 0)
            strict = run_check(root, "--strict")
            self.assertEqual(strict.returncode, 1)
            self.assertIn("cache directory", strict.stdout)

    def test_example_without_files_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            (root / "examples" / "case-a").mkdir(parents=True)
            (root / "examples" / "case-a" / "report.md").write_text("# r\n", encoding="utf-8")
            result = run_check(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("missing exploration.md", result.stdout)


    def test_remote_source_url_is_not_a_local_home_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            source = "https://example.org" + "/home" + "/index/news/123"
            with (root / "README.md").open("a", encoding="utf-8") as handle:
                handle.write(f"\n[Source]({source})\n")
            self.assertEqual(run_check(root).returncode, 0)

    def test_local_path_beside_remote_url_is_still_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            local = "/home" + "/someone/private/"
            with (root / "README.md").open("a", encoding="utf-8") as handle:
                handle.write("\nhttps://example.org/source\n" + local + "\n")
            result = run_check(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("Linux home path", result.stdout)

    def test_local_path_in_url_query_is_still_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            local = "/Users" + "/someone/private/"
            with (root / "README.md").open("a", encoding="utf-8") as handle:
                handle.write("\nhttps://example.org/debug?file=" + local + "\n")
            result = run_check(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("macOS home path", result.stdout)

    def test_secret_in_url_is_not_masked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            token = "ghp_" + "A" * 30
            with (root / "README.md").open("a", encoding="utf-8") as handle:
                handle.write("\nhttps://example.org/" + token + "\n")
            result = run_check(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("GitHub token", result.stdout)

    def test_local_workbuddy_state_is_not_package_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            state = root / ".workbuddy" / "memory"
            state.mkdir(parents=True)
            local = "/home" + "/someone/private/"
            (state / "notes.md").write_text(local)
            self.assertEqual(run_check(root).returncode, 0)

    def test_nonportable_frontmatter_and_duplicate_keys_fail(self) -> None:
        for extra in ('agent_created: true\n', 'description: "duplicate"\n'):
            with self.subTest(extra=extra), tempfile.TemporaryDirectory() as tmp:
                root = make_repo(Path(tmp))
                path = root / "skills/sextant/SKILL.md"
                path.write_text(path.read_text().replace("---\nname:", "---\n" + extra + "name:", 1))
                result = run_check(root)
                self.assertEqual(result.returncode, 1, result.stdout)

    def test_runtime_contract_version_drift_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            skill = root / "skills/sextant"
            (skill / "scripts").mkdir()
            (skill / "scripts/run_control.py").write_text("# synthetic fixture\n")
            (skill / "assets").mkdir()
            (skill / "assets/depth-profiles.json").write_text('{"contract_version":"different"}')
            result = run_check(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("contract_version differs", result.stdout)

    def test_installed_mit_license_must_match(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(Path(tmp))
            skill = root / "skills/sextant"
            path = skill / "SKILL.md"
            path.write_text(path.read_text().replace("---\nname:", "---\nlicense: MIT\nname:", 1))
            (root / "LICENSE").write_text("license fixture")
            self.assertEqual(run_check(root).returncode, 1)
            (skill / "LICENSE").write_text("license fixture")
            self.assertEqual(run_check(root).returncode, 0)


if __name__ == "__main__":
    unittest.main()
