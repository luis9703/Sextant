#!/usr/bin/env python3
"""Install the Sextant skill into an agent host's skill directory.

Copies the complete ``skills/sextant`` folder from this repository into
``<destination>/sextant``. Refuses to overwrite an existing installation and
never merges into one. Uses only the Python standard library (3.10+).

Examples:
    python3 scripts/install_skill.py --to "$HOME/.claude/skills"
    python3 scripts/install_skill.py --to "$HOME/.agents/skills" --dry-run

Exit codes: 0 installed or dry run, 1 usage error, 2 destination already
exists, 3 source skill folder is missing or invalid.
"""
from __future__ import annotations

import sys

sys.dont_write_bytecode = True  # keep cloud-synced checkouts free of __pycache__

import argparse
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
    return None


def install(source: Path, destination_dir: Path, dry_run: bool) -> int:
    problem = validate_source(source)
    if problem:
        print(f"error: {problem}", file=sys.stderr)
        return EXIT_SOURCE

    target = destination_dir / source.name
    if target.exists() or target.is_symlink():
        print(f"error: {target} already exists; nothing was changed.", file=sys.stderr)
        print(
            "Review and then remove or rename the existing installation first. "
            "This installer does not overwrite or merge.",
            file=sys.stderr,
        )
        return EXIT_EXISTS

    files = iter_files(source)
    verb = "Would copy" if dry_run else "Copying"
    print(f"{verb} {len(files)} files")
    print(f"  from: {source}")
    print(f"  to:   {target}")
    for relative in files:
        print(f"    {relative.as_posix()}")

    if dry_run:
        print("Dry run: no files were written.")
        return EXIT_OK

    destination_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target, ignore=_copytree_ignore, symlinks=False)
    print(f"Installed {source.name} to {target}")
    print("Reload or restart the agent host if the skill does not appear.")
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="install_skill.py",
        description="Copy the Sextant skill folder into an agent host's skill directory.",
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
    return install(source, destination, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
