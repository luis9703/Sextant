#!/usr/bin/env python3
"""Check that the Sextant repository is packaged consistently.

Verifies the skill's frontmatter, that the skill folder is self-contained,
that relative links in repository documents resolve, that version strings
agree, that no environment files, secrets, machine-specific paths, or cache
directories sit in the checkout, and that each example has its files.

It checks packaging only. It says nothing about the quality, creativity,
or predictive value of anything the skill produces.

Usage:
    python3 -B scripts/check_project.py [--root PATH] [--strict]

Exit code 1 when errors are found (or warnings, with --strict), else 0.
"""
from __future__ import annotations

import sys

sys.dont_write_bytecode = True  # keep cloud-synced checkouts free of __pycache__

import argparse
import re
from pathlib import Path
from urllib.parse import unquote

SKILL_DIR = Path("skills") / "sextant"
SKILL_MAX_LINES = 500
NAME_MAX = 64
DESCRIPTION_MAX = 1024

DOC_ROOTS = (
    "README.md",
    "README.en.md",
    "CONTRIBUTING.md",
    "AGENTS.md",
    "CLAUDE.md",
    "CHANGELOG.md",
    "docs",
    "evals",
    "examples",
    "skills",
)
SKIP_DIRS = {".git", "sextant-runs", "runs", "tmp", ".venv", "venv", "node_modules", ".idea", ".vscode"}
CACHE_DIRS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".tox", ".nox"}
TEXT_SUFFIXES = {".md", ".py", ".yaml", ".yml", ".txt", ".json", ".toml", ".cfg", ".ini", ".sh"}
TEXT_NAMES = {"LICENSE", ".gitignore", ".gitattributes"}
JUNK_FILES = {".DS_Store", "Thumbs.db"}
SECRET_SUFFIXES = {".pem", ".key", ".p12"}

LINK_RE = re.compile(r"\[[^\]]*\]\((?:<([^>]+)>|([^)\s]+))(?:\s+\"[^\"]*\")?\)")
FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
VERSION_BOLD_RE = re.compile(r"\*\*(\d+\.\d+\.\d+(?:-[0-9A-Za-z.]+)?)\*\*")
CHANGELOG_HEADING_RE = re.compile(r"^## \[?([^\]\s]+)\]?", re.MULTILINE)
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

# Patterns are assembled from pieces so that this file does not match itself.
SECRET_PATTERNS = [
    ("GitHub token", re.compile("gh[pousr]_" + "[A-Za-z0-9]{20,}")),
    ("API key", re.compile(r"\bsk-" + "[A-Za-z0-9_-]{20,}")),
    ("AWS access key", re.compile("AKIA" + "[0-9A-Z]{16}")),
    ("private key block", re.compile("-----BEGIN " + "[A-Z ]*PRIVATE KEY-----")),
]
PATH_PATTERNS = [
    ("macOS home path", re.compile("/Users" + "/[A-Za-z0-9._-]+/")),
    ("Linux home path", re.compile("/home" + "/[a-z0-9._-]+/")),
    ("Windows home path", re.compile(r"[A-Za-z]:\\" + r"Users\\")),
    ("cloud-sync vault path", re.compile("iCloud~md" + "~obsidian")),
]


class Report:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.counts: dict[str, int] = {}

    def _rel(self, path: Path | None) -> str:
        if path is None:
            return "(repository)"
        try:
            return path.resolve().relative_to(self.root.resolve()).as_posix()
        except ValueError:
            return str(path)

    def error(self, path: Path | None, message: str) -> None:
        self.errors.append(f"{self._rel(path)}: {message}")

    def warn(self, path: Path | None, message: str) -> None:
        self.warnings.append(f"{self._rel(path)}: {message}")

    def count(self, key: str, n: int = 1) -> None:
        self.counts[key] = self.counts.get(key, 0) + n


def _unquote_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        inner = value[1:-1]
        if value[0] == '"':
            inner = inner.replace('\\"', '"').replace("\\\\", "\\")
        return inner
    return value


def parse_frontmatter(text: str) -> tuple[dict, str | None]:
    """Parse the YAML subset used by SKILL.md: scalars and one nested mapping level."""
    if not text.startswith("---\n"):
        return {}, "does not start with a '---' frontmatter block"
    end = text.find("\n---", 4)
    if end == -1:
        return {}, "frontmatter block is not closed with '---'"
    data: dict = {}
    parent: dict | None = None
    for raw in text[4:end].splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        key, sep, value = raw.strip().partition(":")
        if not sep or not key.strip():
            return data, f"cannot parse frontmatter line {raw!r}"
        key = key.strip()
        if indent == 0:
            if value.strip() == "":
                parent = {}
                data[key] = parent
            else:
                data[key] = _unquote_scalar(value)
                parent = None
        else:
            if parent is None:
                return data, f"indented frontmatter line without a parent mapping: {raw!r}"
            parent[key] = _unquote_scalar(value)
    return data, None


def iter_links(text: str) -> list[str]:
    """Return link targets outside fenced and inline code."""
    stripped = INLINE_CODE_RE.sub("", FENCE_RE.sub("", text))
    targets = []
    for match in LINK_RE.finditer(stripped):
        targets.append(match.group(1) or match.group(2))
    return targets


def is_external(target: str) -> bool:
    lowered = target.lower()
    return lowered.startswith(("http://", "https://", "mailto:", "tel:", "#"))


def resolve_link(document: Path, target: str) -> Path:
    cleaned = unquote(target.split("#", 1)[0])
    return (document.parent / cleaned).resolve()


def check_skill(root: Path, report: Report) -> str | None:
    """Check SKILL.md frontmatter and that the skill folder links only to itself. Returns the version."""
    skill_dir = root / SKILL_DIR
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        report.error(skill_md, "missing SKILL.md")
        return None

    text = skill_md.read_text(encoding="utf-8")
    data, problem = parse_frontmatter(text)
    if problem:
        report.error(skill_md, problem)

    name = data.get("name")
    if not isinstance(name, str) or not name:
        report.error(skill_md, "frontmatter has no 'name'")
    else:
        if not NAME_RE.match(name):
            report.error(skill_md, f"name {name!r} must be lowercase letters, digits, and single hyphens")
        if len(name) > NAME_MAX:
            report.error(skill_md, f"name is longer than {NAME_MAX} characters")
        if name != skill_dir.name:
            report.error(skill_md, f"name {name!r} does not match folder name {skill_dir.name!r}")

    description = data.get("description")
    if not isinstance(description, str) or not description.strip():
        report.error(skill_md, "frontmatter has no non-empty 'description'")
    elif len(description) > DESCRIPTION_MAX:
        report.error(skill_md, f"description is longer than {DESCRIPTION_MAX} characters")

    metadata = data.get("metadata")
    version = metadata.get("version") if isinstance(metadata, dict) else None
    if not version:
        report.warn(skill_md, "frontmatter has no metadata.version; version consistency cannot be checked")

    line_count = text.count("\n") + (0 if text.endswith("\n") else 1)
    if line_count > SKILL_MAX_LINES:
        report.warn(skill_md, f"SKILL.md has {line_count} lines; keep the entry point compact and move detail to references")

    skill_root = skill_dir.resolve()
    for document in sorted(skill_dir.rglob("*.md")):
        for target in iter_links(document.read_text(encoding="utf-8")):
            if is_external(target):
                continue
            report.count("skill links")
            resolved = resolve_link(document, target)
            if not resolved.exists():
                report.error(document, f"broken link: {target}")
                continue
            try:
                resolved.relative_to(skill_root)
            except ValueError:
                report.error(document, f"link leaves the skill folder, so the installed copy would break: {target}")

    openai_yaml = skill_dir / "agents" / "openai.yaml"
    if not openai_yaml.is_file():
        report.warn(openai_yaml, "missing; Codex UI metadata is optional but expected for this package")
    else:
        yaml_text = openai_yaml.read_text(encoding="utf-8")
        for key in ("display_name", "short_description"):
            if key not in yaml_text:
                report.warn(openai_yaml, f"does not set {key}")

    return version if isinstance(version, str) else None


def check_links(root: Path, report: Report) -> None:
    documents: list[Path] = []
    for entry in DOC_ROOTS:
        path = root / entry
        if path.is_file():
            documents.append(path)
        elif path.is_dir():
            documents.extend(sorted(p for p in path.rglob("*.md") if not any(part in SKIP_DIRS for part in p.parts)))
    skill_root = (root / SKILL_DIR).resolve()
    for document in documents:
        try:
            document.resolve().relative_to(skill_root)
            continue  # already checked in check_skill
        except ValueError:
            pass
        for target in iter_links(document.read_text(encoding="utf-8")):
            if is_external(target):
                continue
            report.count("document links")
            if not resolve_link(document, target).exists():
                report.error(document, f"broken link: {target}")


def check_versions(root: Path, report: Report, skill_version: str | None) -> None:
    if not skill_version:
        return
    for name in ("README.md", "README.en.md"):
        path = root / name
        if not path.is_file():
            continue
        match = VERSION_BOLD_RE.search(path.read_text(encoding="utf-8"))
        if not match:
            report.warn(path, "no bold version string found; cannot compare with SKILL.md")
        elif match.group(1) != skill_version:
            report.error(path, f"version {match.group(1)} differs from SKILL.md version {skill_version}")
    changelog = root / "CHANGELOG.md"
    if changelog.is_file():
        headings = [h for h in CHANGELOG_HEADING_RE.findall(changelog.read_text(encoding="utf-8")) if h.lower() != "unreleased"]
        if not headings:
            report.warn(changelog, "no versioned '## [x.y.z]' heading found")
        elif headings[0] != skill_version:
            report.error(changelog, f"latest entry {headings[0]} differs from SKILL.md version {skill_version}")


def is_text_file(path: Path) -> bool:
    return path.suffix.lower() in TEXT_SUFFIXES or path.name in TEXT_NAMES


def check_tree(root: Path, report: Report) -> None:
    for path in sorted(root.rglob("*")):
        relative_parts = path.relative_to(root).parts
        if any(part in SKIP_DIRS for part in relative_parts):
            continue
        if path.is_dir():
            if path.name in CACHE_DIRS:
                report.warn(path, "cache directory inside the checkout; keep caches outside cloud-synced worktrees")
            continue
        if not path.is_file():
            continue
        name = path.name
        if name in JUNK_FILES or name.startswith("._"):
            report.warn(path, "operating-system junk file present (ignored by git, but still clutter)")
            continue
        if name == ".env" or (name.startswith(".env.") and not name.endswith(".example")):
            report.error(path, "environment file must not be in the repository")
            continue
        if path.suffix.lower() in SECRET_SUFFIXES or path.suffix.lower() in {".pyc", ".pyo"}:
            report.error(path, "credential or bytecode file must not be in the repository")
            continue
        if relative_parts[-2:] == (".claude", "settings.local.json"):
            report.error(path, "local agent settings must not be in the repository")
            continue
        if not is_text_file(path):
            continue
        report.count("files scanned")
        raw = path.read_bytes()
        if b"\r\n" in raw:
            report.warn(path, "contains CRLF line endings; the repository uses LF")
        text = raw.decode("utf-8", errors="replace")
        for label, pattern in SECRET_PATTERNS:
            if pattern.search(text):
                report.error(path, f"looks like it contains a {label}")
        for label, pattern in PATH_PATTERNS:
            match = pattern.search(text)
            if match:
                report.error(path, f"contains a {label}: {match.group(0)!r}")
        for match in EMAIL_RE.finditer(text):
            report.warn(path, f"contains an email address: {match.group(0)}")


def check_examples(root: Path, report: Report) -> None:
    examples = root / "examples"
    if not examples.is_dir():
        return
    cases = [p for p in sorted(examples.iterdir()) if p.is_dir() and not p.name.startswith(".")]
    if not cases:
        report.warn(examples, "examples folder is empty")
    for case in cases:
        report.count("examples")
        for required in ("report.md", "exploration.md"):
            if not (case / required).is_file():
                report.error(case, f"example is missing {required}")


def run(root: Path) -> Report:
    report = Report(root)
    version = check_skill(root, report)
    check_links(root, report)
    check_versions(root, report, version)
    check_tree(root, report)
    check_examples(root, report)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="check_project.py", description="Check Sextant repository packaging.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent, help="repository root (default: this checkout)")
    parser.add_argument("--strict", action="store_true", help="treat warnings as errors")
    args = parser.parse_args(argv)

    root = args.root.expanduser().resolve()
    if not root.is_dir():
        print(f"error: root is not a directory: {root}", file=sys.stderr)
        return 1

    report = run(root)
    for line in report.errors:
        print(f"ERROR  {line}")
    for line in report.warnings:
        print(f"WARN   {line}")
    checked = ", ".join(f"{n} {key}" for key, n in sorted(report.counts.items()))
    print(f"check_project: {len(report.errors)} errors, {len(report.warnings)} warnings; checked skill frontmatter, versions, {checked}")
    if report.errors or (args.strict and report.warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
