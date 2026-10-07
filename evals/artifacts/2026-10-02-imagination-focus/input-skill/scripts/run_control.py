#!/usr/bin/env python3
"""Record Sextant phase artifacts. Structural checks do not prove content quality."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote

sys.dont_write_bytecode = True
PROFILE_FILE = Path(__file__).resolve().parents[1] / "assets" / "depth-profiles.json"
STATE_NAME = "run-state.json"
VERIFICATION_NAME = "verification.json"
LOCK_NAME = ".run-control.lock"
REPORT_EXCERPT_RE = re.compile(r"^\[Report excerpt\]\(([^#\r\n)]+)#L([1-9][0-9]*)\)$")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path.name}")
    return value


def write_json(path: Path, value: dict) -> None:
    if path.is_symlink():
        raise ValueError(f"Refusing to write through a symlink: {path.name}")
    temporary = None
    try:
        # A sibling enables atomic replacement on the same filesystem. It also
        # breaks hardlink aliases instead of modifying their shared contents.
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=f".{path.name}.", suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        if path.is_symlink():
            raise ValueError(f"Refusing to replace a symlink: {path.name}")
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


@contextmanager
def writer_lock(run: Path):
    if run.is_symlink() or not run.is_dir():
        raise ValueError("Run must be an existing real directory")
    lock = run / LOCK_NAME
    try:
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise ValueError("Writer lock exists; another writer may be active. Inspect the lock and owning process before removing a stale lock.") from exc
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump({"pid": os.getpid(), "created_at": now()}, handle)
        yield
    finally:
        lock.unlink(missing_ok=True)


def valid_target(value) -> bool:
    return value is None or (
        isinstance(value, list) and len(value) == 2
        and all(type(item) is int for item in value)
        and 0 < value[0] <= value[1]
    )


def load_config() -> dict:
    config = read_json(PROFILE_FILE)
    if not isinstance(config.get("contract_version"), str) or not config["contract_version"].strip():
        raise ValueError("Config needs a contract version")
    phases = config.get("phases")
    if not isinstance(phases, list) or not phases or any(not isinstance(p, str) or not re.fullmatch(r"[a-z][a-z0-9_]*", p) for p in phases):
        raise ValueError("Config needs a non-empty list of phase names")
    if len(set(phases)) != len(phases):
        raise ValueError("Config contains duplicate phases")
    profiles = config.get("profiles")
    if not isinstance(profiles, dict) or not profiles or not all(isinstance(p, str) and p for p in profiles):
        raise ValueError("Config needs named profiles")
    if not isinstance(config.get("default_profile"), str) or config["default_profile"] not in profiles:
        raise ValueError("Config default profile is not defined")
    for profile in profiles.values():
        if not isinstance(profile, dict) or "token_target" not in profile or not valid_target(profile["token_target"]):
            raise ValueError("Profile token target must be null or two positive, ordered integer endpoints")
    return config


def validate_artifact_record(item: dict) -> None:
    if not isinstance(item, dict) or not isinstance(item.get("path"), str) or not item["path"]:
        raise ValueError("Invalid artifact path in receipt")
    if not isinstance(item.get("sha256"), str) or not re.fullmatch(r"[0-9a-f]{64}", item["sha256"]):
        raise ValueError("Invalid artifact hash in receipt")
    if type(item.get("bytes")) is not int or item["bytes"] <= 0:
        raise ValueError("Invalid artifact size in receipt")


def load_state(run: Path, config: dict) -> dict:
    if run.is_symlink() or (run / STATE_NAME).is_symlink():
        raise ValueError("Run directory and state must not be symlinks")
    state = read_json(run / STATE_NAME)
    if state.get("contract_version") != config["contract_version"]:
        raise ValueError("Contract version differs; use the matching skill version for this run")
    if state.get("phases") != config["phases"]:
        raise ValueError("Phase list differs from the installed contract")
    if not isinstance(state.get("profile"), str) or state["profile"] not in config["profiles"]:
        raise ValueError("Unknown profile in state")
    if "token_target" not in state or not valid_target(state["token_target"]):
        raise ValueError("Invalid token target in state")
    receipts = state.get("receipts")
    if not isinstance(receipts, list) or len(receipts) > len(state["phases"]):
        raise ValueError("Invalid receipt list")
    for index, receipt in enumerate(receipts):
        if not isinstance(receipt, dict) or receipt.get("phase") != state["phases"][index]:
            raise ValueError("Receipts are not in contract order")
        if not isinstance(receipt.get("status"), str) or receipt["status"] not in {"done", "partial"}:
            raise ValueError("Invalid phase status")
        if not isinstance(receipt.get("reason"), str):
            raise ValueError("Phase reason must be a string")
        if receipt["status"] == "partial" and not receipt["reason"].strip():
            raise ValueError("A partial phase needs a reason")
        if not isinstance(receipt.get("artifacts"), list) or not receipt["artifacts"]:
            raise ValueError("Each phase needs an artifact, including a limitation record")
        for item in receipt["artifacts"]:
            validate_artifact_record(item)
        if "report_snapshot" in receipt:
            if receipt["phase"] != "reconcile":
                raise ValueError("Only reconciliation can bind a report snapshot")
            validate_artifact_record(receipt["report_snapshot"])
        elif receipt["phase"] == "reconcile" and receipt["status"] == "done":
            raise ValueError("Completed reconciliation needs a report snapshot")
    return state


def artifact(run: Path, name: str) -> dict:
    candidate = Path(name)
    if candidate.is_absolute():
        raise ValueError("Artifact paths must be relative to the run directory")
    path = (run / candidate).resolve()
    try:
        relative = path.relative_to(run.resolve()).as_posix()
    except ValueError as exc:
        raise ValueError("Artifact leaves the run directory") from exc
    if relative in {STATE_NAME, VERIFICATION_NAME, LOCK_NAME}:
        raise ValueError("Process metadata cannot serve as a phase artifact")
    if not path.is_file():
        raise ValueError(f"Missing artifact: {relative}")
    if path.stat().st_nlink > 1:
        raise ValueError(f"Artifact has hardlink aliases; provide an independent copy: {relative}")
    content = path.read_bytes()
    if not content.strip():
        raise ValueError(f"Empty artifact: {relative}")
    return {"path": relative, "sha256": hashlib.sha256(content).hexdigest(), "bytes": len(content)}


def check_report_excerpts(run: Path, files: list[dict], snapshot: dict, required: bool) -> None:
    """Check literal locations only; an excerpt does not prove a repair is adequate."""
    report_lines = (run / snapshot["path"]).read_text(encoding="utf-8").splitlines()
    found = 0
    for note in files:
        lines = (run / note["path"]).read_text(encoding="utf-8").splitlines()
        for index, line in enumerate(lines):
            if not line.startswith("[Report excerpt]"):
                continue
            match = REPORT_EXCERPT_RE.fullmatch(line)
            if match is None or index + 1 >= len(lines) or not lines[index + 1].startswith("> "):
                raise ValueError(f"Malformed report excerpt in {note['path']} at line {index + 1}")
            reference_name = Path(note["path"]).parent / unquote(match.group(1))
            reference = artifact(run, str(reference_name))
            if reference["path"] != snapshot["path"]:
                raise ValueError("Report excerpt must refer to the bound report")
            line_number = int(match.group(2))
            quote = lines[index + 1][2:]
            if not quote.strip() or line_number > len(report_lines) or quote not in report_lines[line_number - 1]:
                raise ValueError(f"Report excerpt does not match {snapshot['path']} at line {line_number}")
            found += 1
    if required and not found:
        raise ValueError("Completed reconciliation needs a [Report excerpt](report.md#L<number>) followed by a > literal passage")


def verify(run: Path, state: dict) -> dict:
    errors = []
    seen = set()
    report_snapshot = None
    for receipt in state["receipts"]:
        for saved in receipt["artifacts"]:
            if not isinstance(saved, dict) or not isinstance(saved.get("path"), str):
                errors.append(f"Invalid artifact record in {receipt['phase']}")
                continue
            name = saved["path"]
            if name in seen:
                errors.append(f"Artifact reused across receipts: {name}")
            seen.add(name)
            try:
                current = artifact(run, name)
                if current != saved:
                    errors.append(f"Artifact changed after receipt: {name}")
            except (OSError, ValueError) as exc:
                errors.append(str(exc))
        if receipt["phase"] == "reconcile" and "report_snapshot" in receipt:
            report_snapshot = receipt["report_snapshot"]
            if report_snapshot["path"] in seen:
                errors.append("Reconciled report must be separate from earlier phase artifacts")
            try:
                if artifact(run, report_snapshot["path"]) != report_snapshot:
                    errors.append(f"Report changed after reconciliation: {report_snapshot['path']}")
                check_report_excerpts(run, receipt["artifacts"], report_snapshot, receipt["status"] == "done")
            except (OSError, ValueError) as exc:
                errors.append(str(exc))
        if receipt["phase"] == "deliver" and report_snapshot is not None:
            if report_snapshot["path"] not in {item["path"] for item in receipt["artifacts"]}:
                errors.append("Delivery does not include the report bound during reconciliation")
    missing = state["phases"][len(state["receipts"]):]
    partial = [r["phase"] for r in state["receipts"] if r["status"] == "partial"]
    passed = not errors and not missing and not partial
    return {
        "checked_at": now(),
        "profile": state["profile"],
        "state_fingerprint": hashlib.sha256(json.dumps(state, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest(),
        "structural_status": "pass" if passed else "incomplete_or_invalid",
        "recorded_phases": len(state["receipts"]),
        "missing_phases": missing,
        "partial_phases": partial,
        "artifact_errors": errors,
        "token_target": state["token_target"],
        "measured_token_usage": None,
        "usage_status": "unknown; consult host telemetry separately",
        "semantic_status": "not established by this script",
        "scope": "Checks recorded order and artifact integrity; not source truth, actual isolation, creativity, or model compliance outside this helper.",
    }


def main(argv: list[str] | None = None) -> int:
    try:
        config = load_config()
    except (OSError, ValueError) as exc:
        print(f"error: invalid profile configuration: {exc}", file=sys.stderr)
        return 2
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init", help="Create a new run; never overwrite an existing directory")
    init.add_argument("--run", type=Path, required=True)
    init.add_argument("--topic", required=True)
    init.add_argument("--profile", choices=config["profiles"], default=config["default_profile"])
    init.add_argument("--budget-min", type=int)
    init.add_argument("--budget-max", type=int)
    record = sub.add_parser("record", help="Record the next phase immediately after doing it")
    record.add_argument("--run", type=Path, required=True)
    record.add_argument("--phase", choices=config["phases"], required=True)
    record.add_argument("--artifact", action="append", required=True)
    record.add_argument("--report", help="Saved UTF-8 report to bind during reconcile; required when reconcile is done")
    record.add_argument("--status", choices=["done", "partial"], default="done")
    record.add_argument("--reason", default="")
    for name in ("status", "verify"):
        command = sub.add_parser(name)
        command.add_argument("--run", type=Path, required=True)
    args = parser.parse_args(argv)
    run = args.run.expanduser().absolute()
    try:
        if args.command == "init":
            if not args.topic.strip():
                raise ValueError("Topic must not be empty")
            target = config["profiles"][args.profile]["token_target"]
            if args.budget_min is not None or args.budget_max is not None:
                if args.budget_min is None or args.budget_max is None or not 0 < args.budget_min <= args.budget_max:
                    raise ValueError("Provide both positive budget endpoints in increasing order")
                target = [args.budget_min, args.budget_max]
            if run.exists() or run.is_symlink():
                raise ValueError("Run path already exists; choose a new directory")
            run.mkdir(parents=True)
            state = {
                "contract_version": config["contract_version"],
                "created_at": now(),
                "topic": args.topic.strip(),
                "profile": args.profile,
                "token_target": target,
                "phases": config["phases"],
                "receipts": [],
            }
            write_json(run / STATE_NAME, state)
            print(json.dumps({"created": str(run), "profile": args.profile, "token_target": target}, ensure_ascii=False))
            return 0
        if args.command == "status":
            result = verify(run, load_state(run, config))
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        with writer_lock(run):
            return mutate_run(args, run, config)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


def mutate_run(args: argparse.Namespace, run: Path, config: dict) -> int:
    try:
        state = load_state(run, config)
    except (OSError, ValueError) as exc:
        if args.command == "verify":
            # Do not leave a stale pass report when a new verification fails.
            write_json(run / VERIFICATION_NAME, {
                "checked_at": now(), "structural_status": "invalid_state",
                "artifact_errors": [str(exc)], "semantic_status": "not established by this script",
                "measured_token_usage": None,
            })
        raise
    if args.command == "record":
        index = len(state["receipts"])
        expected = state["phases"][index] if index < len(state["phases"]) else None
        if args.phase != expected:
            raise ValueError(f"Next phase is {expected!r}, not {args.phase!r}")
        if args.status == "partial" and not args.reason.strip():
            raise ValueError("A partial phase needs a concrete --reason")
        if args.report is not None and args.phase != "reconcile":
            raise ValueError("--report is only used when recording reconcile")
        if args.phase == "reconcile" and args.status == "done" and not args.report:
            raise ValueError("Finish and re-read the report, then record reconcile with --report <relative path>")
        existing = verify(run, state)["artifact_errors"]
        if existing:
            raise ValueError("Earlier artifacts changed or disappeared: " + "; ".join(existing))
        files = [artifact(run, name) for name in args.artifact]
        prior = {f["path"] for r in state["receipts"] for f in r["artifacts"]}
        names = [f["path"] for f in files]
        if len(set(names)) != len(names) or prior.intersection(names):
            raise ValueError("Use distinct phase artifacts; preserve earlier phase records")
        receipt = {
            "phase": args.phase, "recorded_at": now(), "status": args.status,
            "reason": args.reason.strip(), "artifacts": files,
        }
        if args.report is not None:
            snapshot = artifact(run, args.report)
            if snapshot["path"] in prior or snapshot["path"] in names:
                raise ValueError("Reconciled report must be separate from earlier phase artifacts and the disposition record")
            check_report_excerpts(run, files, snapshot, args.status == "done")
            receipt["report_snapshot"] = snapshot
        if args.phase == "deliver":
            snapshot = next((r["report_snapshot"] for r in state["receipts"] if "report_snapshot" in r), None)
            if snapshot is not None and snapshot["path"] not in names:
                raise ValueError("Delivery must include the report bound during reconciliation")
        state["receipts"].append(receipt)
        write_json(run / STATE_NAME, state)
        print(json.dumps({"recorded": args.phase, "status": args.status}, ensure_ascii=False))
        return 0
    result = verify(run, state)
    write_json(run / VERIFICATION_NAME, result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["structural_status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
