#!/usr/bin/env python3
"""Install the Sextant skill into an agent host's skill directory.

Copies the complete ``skills/sextant`` folder from this repository into
``<destination>/sextant``. Refuses to overwrite an existing installation and
never merges into one. Uses only the Python standard library (3.10+).

Examples:
    python3 scripts/install_skill.py --to "$HOME/.claude/skills"
    python3 scripts/install_skill.py --to "$HOME/.agents/skills" --dry-run

Exit codes: 0 installed or dry run, 1 invalid destination, 2 destination already
exists (also argparse usage errors), 3 invalid source, 4 filesystem error.
"""
from __future__ import annotations

import sys

sys.dont_write_bytecode = True  # keep cloud-synced checkouts free of __pycache__

import argparse
import json
import re
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = REPO_ROOT / "skills" / "sextant"

IGNORED_NAMES = {".DS_Store", "__pycache__", "Thumbs.db"}
IGNORED_PREFIXES = ("._",)
IGNORED_SUFFIXES = (".pyc", ".pyo")

EXIT_OK = 0
EXIT_USAGE = 1
EXIT_EXISTS = 2
EXIT_SOURCE = 3
EXIT_IO = 4
WORKBUDDY_KEYS = {
    "agent_created", "display_name", "display_name_en",
    "description_zh", "description_en", "visibility",
}


def is_ignored(name: str) -> bool:
    return (
        name in IGNORED_NAMES
        or name.startswith(IGNORED_PREFIXES)
        or name.endswith(IGNORED_SUFFIXES)
    )


def _copytree_ignore(_directory: str, names: list[str]) -> set[str]:
    return {name for name in names if is_ignored(name)}


def iter_files(source: Path) -> list[Path]:
    """Return the files that would be installed, relative to ``source``, sorted."""
    files = []
    for path in sorted(source.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(source)
        if any(is_ignored(part) for part in relative.parts):
            continue
        files.append(relative)
    return files


def validate_source(source: Path) -> str | None:
    if not source.is_dir():
        return f"source skill folder not found: {source}"
    if not (source / "SKILL.md").is_file():
        return f"source folder has no SKILL.md: {source}"
    for path in source.rglob("*"):
        if path.is_symlink():
            return f"source contains a symlink; package real files instead: {path.relative_to(source)}"
    return None


def workbuddy_skill_text(source: Path) -> str:
    """Render our installer overlay; this JSON is not a native host manifest."""
    overlay = json.loads((source / "agents" / "workbuddy.json").read_text(encoding="utf-8"))
    if not isinstance(overlay, dict) or set(overlay) != WORKBUDDY_KEYS:
        raise ValueError("WorkBuddy overlay has missing or unsupported fields")
    if type(overlay["agent_created"]) is not bool:
        raise ValueError("WorkBuddy agent_created must be a boolean")
    if any(not isinstance(v, str) or not v.strip() for k, v in overlay.items() if k != "agent_created"):
        raise ValueError("WorkBuddy display fields must be non-empty strings")
    text = (source / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---(?=\n|$)", text, re.DOTALL)
    if not match:
        raise ValueError("Source must have a closed YAML frontmatter block")
    keys = set(re.findall(r"^([A-Za-z0-9_-]+):", match.group(1), re.MULTILINE))
    if keys.intersection(WORKBUDDY_KEYS):
        raise ValueError("Source already contains WorkBuddy fields; use the portable source")
    additions = "\n".join(f"{key}: {json.dumps(value, ensure_ascii=False)}" for key, value in overlay.items())
    # JSON scalars are valid YAML scalars; body bytes and existing keys are retained.
    return "---\n" + additions + "\n" + match.group(1) + "\n---" + text[match.end():]


def install(source: Path, destination_dir: Path, dry_run: bool, host: str = "portable") -> int:
    problem = validate_source(source)
    if problem:
        print(f"error: {problem}", file=sys.stderr)
        return EXIT_SOURCE

    target = destination_dir / source.name
    if destination_dir.exists() and not destination_dir.is_dir():
        print("error: destination must be a directory", file=sys.stderr)
        return EXIT_USAGE
    if target.resolve().is_relative_to(source.resolve()):
        print("error: installation destination must not be inside the source skill", file=sys.stderr)
        return EXIT_USAGE
    if target.exists() or target.is_symlink():
        print(f"error: {target} already exists; nothing was changed.", file=sys.stderr)
        print(
            "Review and then remove or rename the existing installation first. "
            "This installer does not overwrite or merge.",
            file=sys.stderr,
        )
        return EXIT_EXISTS

    try:
        rendered = workbuddy_skill_text(source) if host == "workbuddy" else None
    except (OSError, ValueError, TypeError) as exc:
        print(f"error: invalid WorkBuddy source overlay: {exc}", file=sys.stderr)
        return EXIT_SOURCE

    files = iter_files(source)
    verb = "Would copy" if dry_run else "Copying"
    print(f"{verb} {len(files)} files")
    print(f"  from: {source}")
    print(f"  to:   {target}")
    print(f"  host: {host}")
    for relative in files:
        print(f"    {relative.as_posix()}")

    if dry_run:
        print("Dry run: no files were written.")
        return EXIT_OK

    try:
        destination_dir.mkdir(parents=True, exist_ok=True)
        # Exclusive creation prevents a concurrent install from being merged.
        target.mkdir()
    except FileExistsError:
        print(f"error: destination exists or is not a directory: {target}", file=sys.stderr)
        return EXIT_EXISTS
    try:
        shutil.copytree(source, target, ignore=_copytree_ignore, symlinks=False, dirs_exist_ok=True)
        if rendered is not None:
            (target / "SKILL.md").write_text(rendered, encoding="utf-8")
    except OSError as exc:
        print(f"error: copying failed: {exc}; partial installation retained at {target}; inspect it before retrying", file=sys.stderr)
        return EXIT_IO
    print(f"Installed {source.name} to {target}")
    print("Reload or restart the agent host if the skill does not appear.")
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="install_skill.py",
        description="Copy the Sextant skill folder into an agent host's skill directory.",
    )
    parser.add_argument(
        "--host", choices=("portable", "workbuddy"), default="portable",
        help="portable source for Codex/Claude Code, or apply WorkBuddy-only display fields to the copy",
    )
    parser.add_argument(
        "--to",
        required=True,
        type=Path,
        help="the host's skill directory, for example ~/.claude/skills or ~/.agents/skills",
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_SOURCE,
        help="skill folder to copy (default: this repository's skills/sextant)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="list what would be copied without writing anything",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    destination = args.to.expanduser().resolve()
    source = args.source.expanduser().resolve()
    try:
        return install(source, destination, args.dry_run, args.host)
    except OSError as exc:
        print(f"error: filesystem operation failed: {exc}", file=sys.stderr)
        return EXIT_IO


if __name__ == "__main__":
    sys.exit(main())
