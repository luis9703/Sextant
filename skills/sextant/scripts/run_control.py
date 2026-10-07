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

sys.dont_write_bytecode = True
import development
import revisions
import review_contract

SKILL_ROOT = Path(__file__).resolve().parents[1]
PROFILE_FILE = SKILL_ROOT / "assets" / "depth-profiles.json"
CONTRACT_FILE = SKILL_ROOT / "assets" / "execution-contract.json"
STATE_NAME = "run-state.json"
VERIFICATION_NAME = "verification.json"
LOCK_NAME = ".run-control.lock"
CURRENT_NAME = "00-current.md"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path.name}")
    return value


def write_json(path: Path, value: dict) -> None:
    write_text_atomic(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def write_text_atomic(path: Path, content: str) -> None:
    if path.is_symlink():
        raise ValueError(f"Refusing to write through a symlink: {path.name}")
    temporary = None
    try:
        # A sibling enables atomic replacement on the same filesystem. It also
        # breaks hardlink aliases instead of modifying their shared contents.
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=f".{path.name}.", suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(content)
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
        kinds = profile.get("work_required")
        if not isinstance(kinds, list) or any(kind not in development.KINDS for kind in kinds) or len(set(kinds)) != len(kinds):
            raise ValueError("Profile needs distinct supported development work kinds")
    if not isinstance(config.get("accounting"), str) or not config["accounting"].strip():
        raise ValueError("Config needs the budget accounting explanation")
    contracts = read_json(CONTRACT_FILE)
    if set(contracts.get("phases", {})) != set(phases) or set(contracts.get("work", {})) != set(development.KINDS):
        raise ValueError("Execution contracts must cover the configured phases and work kinds")
    for item in [*contracts["phases"].values(), *contracts["work"].values()]:
        if not isinstance(item, dict) or not isinstance(item.get("goal"), str) or not item["goal"].strip():
            raise ValueError("Invalid execution goal")
        if not isinstance(item.get("completion"), list) or not item["completion"] or any(not isinstance(x, str) or not x.strip() for x in item["completion"]):
            raise ValueError("Execution contract needs completion criteria")
        if not isinstance(item.get("references"), list) or any(not (SKILL_ROOT / name).is_file() or not (SKILL_ROOT / name).resolve().is_relative_to(SKILL_ROOT) for name in item["references"]):
            raise ValueError("Execution reference must resolve inside the Skill")
    config["contracts"] = contracts
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
    if state.get("budget_accounting") != config["accounting"]:
        raise ValueError("Budget meaning differs from the installed contract")
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
        if "pathways_snapshot" in receipt:
            validate_artifact_record(receipt["pathways_snapshot"])
        if receipt["phase"] == "review":
            info = receipt.get("review_record")
            if not isinstance(info, dict) or info.get("format") not in {"full", "issue_summary"} or info.get("context") not in {"isolated", "same", "unavailable"} or info.get("coverage") not in {"complete", "limited"}:
                raise ValueError("Review receipt needs representation, context and coverage")
            if receipt["status"] == "done" and info["context"] == "unavailable":
                raise ValueError("Unavailable review cannot be recorded as performed")
    if state.get("work_required") != config["profiles"][state["profile"]]["work_required"]:
        raise ValueError("Development work requirements differ from the installed profile")
    development.validate_jobs(state, validate_artifact_record)
    review_contract.validate_issues(state, validate_artifact_record)
    revisions.validate(state, validate_artifact_record)
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
    if relative in {STATE_NAME, VERIFICATION_NAME, LOCK_NAME, CURRENT_NAME}:
        raise ValueError("Process metadata cannot serve as a phase artifact")
    if not path.is_file():
        raise ValueError(f"Missing artifact: {relative}")
    if path.stat().st_nlink > 1:
        raise ValueError(f"Artifact has hardlink aliases; provide an independent copy: {relative}")
    content = path.read_bytes()
    if not content.strip():
        raise ValueError(f"Empty artifact: {relative}")
    return {"path": relative, "sha256": hashlib.sha256(content).hexdigest(), "bytes": len(content)}


def check_report_excerpts(run, files, snapshot, required, pathway=None, issues=None):
    return review_contract.examine(run, files, snapshot, pathway, issues or [],
                                   lambda name: artifact(run, name), required)


def check_pathway_changes(state, coverage, pathway):
    original = next(r["artifacts"] for r in state["receipts"] if r["phase"] == "pathways")
    for item in coverage["dispositions"]:
        issue = next(i for i in state["review_issues"] if i["id"] == item["id"])
        if item["action"] in {"revise", "drop"} and "pathways" in issue["targets"] and pathway["sha256"] in {f["sha256"] for f in original}:
            raise ValueError("Accepted pathway changes need an updated synthesis, not an unchanged confirmation")


def coverage_summary(receipt):
    coverage = receipt.get("issue_coverage")
    if coverage is None:
        return None
    return {"dispositions": [{"id": item["id"], "action": item["action"]} for item in coverage["dispositions"]],
            "excerpt_locations": [{"issue": item["issue"], "target": item["target"], "line": item["line"]} for item in coverage["excerpts"]],
            "unresolved_ids": coverage["unresolved_ids"], "not_used_ids": coverage["not_used_ids"],
            "semantic_status": coverage["semantic_status"],
            "details_in": [item["path"] for item in receipt["artifacts"]]}


def resource_contract(result: dict, state: dict, config: dict, run: Path) -> dict:
    """Return actionable instructions; absolute resource paths live only in tool output."""
    result = dict(result)
    active = revisions.current(state)
    resumable = [phase for phase in revisions.partial_status(state, development.summary(state))["partial_phases"]
                 if phase in revisions.REVISION_PHASES - {"pathways"}]
    if resumable:
        result["resume_options"] = []
        for name in resumable:
            base = [sys.executable, "-B", str(Path(__file__).resolve()), "revise", "--run", str(run), "--phase", name]
            goal = config["contracts"]["phases"][name]
            result["resume_options"].append({"phase": name, "current": active[name],
                "contract": {**goal, "references": [str((SKILL_ROOT / ref).resolve()) for ref in goal["references"]]},
                "complete_argv": [*base, "--artifact", "<completed-phase-version>", "--complete", "--reason", "<what-was-actually-completed>"],
                "confirm_complete_argv": [*base, "--confirm", "--complete", "--reason", "<why-the-saved-material-now-completes-this-phase>"],
                "meaning": "Finish the actual phase work before declaring completion; editing a document alone does not complete it."})
    phase = result.get("phase")
    if result.get("next") == "phase" and phase == "reconcile" and not revisions.pathway_ready(state):
        result.update(next="refresh_pathways", phase="pathways", current=revisions.current(state).get("pathways"))
    contract = None
    if result.get("next") == "work":
        contract = config["contracts"]["work"].get(result.get("kind"))
    elif result.get("next") == "phase":
        contract = config["contracts"]["phases"].get(result.get("phase"))
    if contract is not None:
        result["contract"] = {**contract, "references": [str((SKILL_ROOT / name).resolve()) for name in contract["references"]]}
        if result.get("next") == "phase":
            result["record_argv"] = [sys.executable, "-B", str(Path(__file__).resolve()), "record", "--run", str(run),
                                     "--phase", result["phase"], "--artifact", "<saved-phase-artifact>"]
            if result["phase"] == "review":
                result["record_argv"] += ["--review-format", "<full|issue_summary>", "--review-context", "<isolated|same|unavailable>",
                                          "--review-coverage", "<complete|limited>"]
            if result["phase"] == "reconcile":
                result["record_argv"] += ["--report", "<saved-report>"]
                result["contract"]["no_issues"] = "If the review raised no material issues, give --no-issues-reason; otherwise register and disposition each issue."
        elif result.get("next") == "work":
            result["record_argv"] = [sys.executable, "-B", str(Path(__file__).resolve()), "work-record", "--run", str(run),
                                     "--id", result["id"], "--artifact", "<result-artifact>"]
            selected = list(dict.fromkeys(item["path"] for item in [*result["inputs"],
                            *(saved for files in result["dependency_results"].values() for saved in files)]))
            result["packet_argv"] = [sys.executable, "-B", str(SKILL_ROOT / "scripts/exploration_packet.py"),
                                     "--run", str(run), "--question", result["question"], "--out", "<new-packet-directory>"]
            for name in selected:
                result["packet_argv"] += ["--source", name]
    if result.get("next") == "refresh_pathways":
        result["contract"] = {"goal": "Update the pathway synthesis after review, or confirm it unchanged with a reason.",
                              "completion": ["Preserve previous files", "Use revise with new artifacts for changes or --confirm for a checked unchanged synthesis", "Do this after follow-up work and material issue registration"],
                              "references": [str(SKILL_ROOT / "references/execution.md")]}
        base = [sys.executable, "-B", str(Path(__file__).resolve()), "revise", "--run", str(run), "--phase", "pathways"]
        result["update_argv"] = [*base, "--artifact", "<new-pathway-version>", "--reason", "<actual-change>"]
        result["confirm_argv"] = [*base, "--confirm", "--reason", "<why-the-current-version-remains-valid>"]
    if "guide" in result:
        result["guide"] = str((SKILL_ROOT / result["guide"]).resolve())
    result["resources"] = {"skill_root": str(SKILL_ROOT), "run_control": str(Path(__file__).resolve()), "run": str(run)}
    result["budget"] = {"planned_token_target": state["token_target"], "measured_token_usage": None,
                         "meaning": config["accounting"]}
    if "input_artifacts" not in result:
        result["input_artifacts"] = {phase: item["artifacts"] for phase, item in revisions.current(state).items()}
    result["review_issues"] = state["review_issues"]
    return result


def persist_state(run: Path, state: dict) -> None:
    if (run / CURRENT_NAME).is_symlink():
        raise ValueError("Current-version index must not be a symlink")
    write_json(run / STATE_NAME, state)
    from urllib.parse import quote
    def link(item):
        label = item["path"].replace("[", "\\[").replace("]", "\\]")
        return f"[{label}]({quote(item['path'], safe='/')})"
    lines = ["# 当前版本入口", "", "此文件由执行器生成；历史回执保持原样。", "",
             "状态指纹：`" + revisions.digest(state) + "`", ""]
    active = revisions.current(state)
    path = active.get("pathways")
    if path:
        role = "审查后已更新/确认" if revisions.pathway_ready(state) else "审查前草稿或需再次更新"
        lines += ["## 当前路径", "", f"版本 {path['version']}，{role}。", ""]
        lines.extend("- " + link(item) for item in path["artifacts"])
    report = next((r.get("report_snapshot") for r in state["receipts"] if r["phase"] == "reconcile"), None)
    if report:
        lines += ["", "## 当前报告", "", link(report)]
    lines += ["", "## 阶段执行", ""]
    superseded = revisions.partial_status(state, development.summary(state))["superseded_partial_phases"]
    for receipt in state["receipts"]:
        suffix = ("；" + receipt["reason"]) if receipt["reason"] else ""
        if receipt["phase"] in superseded:
            suffix += ("；早期未完成已由当前综合承接" if receipt["phase"] == "pathways"
                       else "；早期未完成已由当前阶段版本的完成声明承接")
        lines.append(f"- {receipt['phase']}：{receipt['status']}{suffix}")
    updated = [(phase, item) for phase, item in active.items()
               if phase in revisions.REVISION_PHASES - {"pathways"} and item["version"] > 1]
    if updated:
        lines += ["", "## 已更新的阶段材料", ""]
        for phase, item in updated:
            lines.append(f"- {phase}：版本{item['version']}，{item['status']}；" + ", ".join(link(f) for f in item["artifacts"]))
    lines += ["", "## 路径历史", ""]
    for receipt in state["receipts"]:
        if receipt["phase"] == "pathways":
            lines.extend("- 版本1，审查前草稿：" + link(item) for item in receipt["artifacts"])
    for item in state["revisions"]:
        if item["phase"] == "pathways":
            lines.append(f"- 版本{item['version']}（{item['kind']}）：" + ", ".join(link(f) for f in item["artifacts"]))
    lines += ["", "完整性、审查覆盖与内容判断分别说明；当前指针不证明推演正确。", ""]
    write_text_atomic(run / CURRENT_NAME, "\n".join(lines))


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
                pathway_snapshot = receipt.get("pathways_snapshot")
                coverage = check_report_excerpts(run, receipt["artifacts"], report_snapshot, receipt["status"] == "done",
                                                 pathway_snapshot, state["review_issues"])
                if receipt.get("issue_coverage") != coverage:
                    errors.append("Reconciliation issue coverage differs from its saved notes")
                if receipt["status"] == "done" and (not revisions.pathway_ready(state) or pathway_snapshot is None or
                        pathway_snapshot not in revisions.current(state)["pathways"]["artifacts"]):
                    errors.append("Reconciliation must bind the current post-review pathway synthesis")
                if receipt["status"] == "done" and pathway_snapshot is not None:
                    check_pathway_changes(state, coverage, pathway_snapshot)
                if receipt["status"] == "done" and not state["review_issues"] and not receipt.get("no_issues_reason", "").strip():
                    errors.append("Reconciliation needs a no-issues declaration when no issues were registered")
                if pathway_snapshot is not None and artifact(run, pathway_snapshot["path"]) != pathway_snapshot:
                    errors.append("Pathway synthesis changed after reconciliation")
            except (OSError, ValueError) as exc:
                errors.append(str(exc))
        if receipt["phase"] == "deliver" and report_snapshot is not None:
            if report_snapshot["path"] not in {item["path"] for item in receipt["artifacts"]}:
                errors.append("Delivery does not include the report bound during reconciliation")
    extra_artifacts = [*development.job_artifacts(state["work"]), *revisions.artifacts(state),
                       *(issue["source"] for issue in state["review_issues"])]
    for saved in extra_artifacts:
        try:
            if artifact(run, saved["path"]) != saved:
                errors.append(f"Development input/result changed: {saved['path']}")
        except (OSError, ValueError) as exc:
            errors.append(str(exc))
    work_summary = development.summary(state)
    review_info = next((r["review_record"] for r in state["receipts"] if r["phase"] == "review"), None)
    reconciliation = next((r for r in state["receipts"] if r["phase"] == "reconcile"), None)
    missing = state["phases"][len(state["receipts"]):]
    partial_status = revisions.partial_status(state, work_summary)
    partial = partial_status["partial_phases"]
    passed = not errors and not missing and not partial and not work_summary["pending_ids"] and not work_summary["missing_kinds"]
    return {
        "checked_at": now(),
        "profile": state["profile"],
        "state_fingerprint": hashlib.sha256(json.dumps(state, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest(),
        "structural_status": "pass" if passed else ("invalid" if errors else "incomplete"),
        "integrity_status": "pass" if not errors else "invalid",
        "execution_status": "complete" if not missing and not partial and not work_summary["pending_ids"] and not work_summary["missing_kinds"] else "incomplete",
        "recorded_phases": len(state["receipts"]),
        "missing_phases": missing,
        **partial_status,
        "artifact_errors": errors,
        "development_work": work_summary,
        "review_record": review_info,
        "issue_coverage": coverage_summary(reconciliation) if reconciliation else {"registered_ids": [i["id"] for i in state["review_issues"]], "status": "awaiting_reconciliation"},
        "current_versions": revisions.current(state),
        "token_target": state["token_target"],
        "budget_accounting": state["budget_accounting"],
        "measured_token_usage": None,
        "usage_status": "unknown; consult host telemetry separately",
        "semantic_status": "not established by this script",
        "scope": "Checks recorded order and artifact integrity; not source truth, actual isolation, creativity, or model compliance outside this helper.",
    }


def main(argv: list[str] | None = None) -> int:
    try:
        config = load_config()
    except (OSError, ValueError, KeyError, TypeError) as exc:
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
    record.add_argument("--review-format", choices=("full", "issue_summary"))
    record.add_argument("--review-context", choices=("isolated", "same", "unavailable"))
    record.add_argument("--review-coverage", choices=("complete", "limited"))
    record.add_argument("--no-issues-reason", default="")
    record.add_argument("--pathways", help="Current pathway synthesis to bind during reconciliation; defaults to its first current artifact")
    revise = sub.add_parser("revise", help="Append a new document version or confirm the current version after review")
    revise.add_argument("--run", type=Path, required=True)
    revise.add_argument("--phase", choices=sorted(revisions.REVISION_PHASES), required=True)
    revise.add_argument("--artifact", action="append", default=[])
    revise.add_argument("--confirm", action="store_true")
    revise.add_argument("--complete", action="store_true", help="Declare actually completed phase work, preserving the earlier partial receipt")
    revise.add_argument("--reason", required=True)
    issue = sub.add_parser("review-add", help="Register a material objection or unused research lead for explicit disposition")
    issue.add_argument("--run", type=Path, required=True)
    issue.add_argument("--id", required=True)
    issue.add_argument("--kind", choices=("material", "lead"), default="material")
    issue.add_argument("--question", required=True)
    issue.add_argument("--source", required=True)
    issue.add_argument("--target", choices=("report", "pathways"), action="append")
    add_work = sub.add_parser("work-add", help="Open a development question after recombination; save inputs without overwriting them")
    add_work.add_argument("--run", type=Path, required=True)
    add_work.add_argument("--id", required=True)
    add_work.add_argument("--kind", choices=development.KINDS, required=True)
    add_work.add_argument("--question", required=True)
    add_work.add_argument("--source", action="append", required=True)
    add_work.add_argument("--after", action="append", default=[])
    add_work.add_argument("--priority", type=int, choices=(1, 2, 3), default=2)
    record_work = sub.add_parser("work-record", help="Save a result; a partial attempt stays pending and can resume with a new artifact")
    record_work.add_argument("--run", type=Path, required=True)
    record_work.add_argument("--id", required=True)
    record_work.add_argument("--artifact", action="append", required=True)
    record_work.add_argument("--status", choices=("done", "partial"), default="done")
    record_work.add_argument("--reason", default="")
    record_work.add_argument("--adopt-existing", action="store_true", help="Explicitly adopt existing analysis; cannot be presented as newly created work")
    for name in ("status", "verify", "next"):
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
                "budget_accounting": config["accounting"],
                "phases": config["phases"],
                "receipts": [],
                "work_required": config["profiles"][args.profile]["work_required"],
                "work": [],
                "revisions": [],
                "review_issues": [],
            }
            persist_state(run, state)
            result = {"created": str(run), "profile": args.profile, "token_target": target,
                      **development.next_action(state)}
            print(json.dumps(resource_contract(result, state, config, run), ensure_ascii=False, indent=2))
            return 0
        if args.command in {"status", "next"}:
            state = load_state(run, config)
            result = verify(run, state)
            if args.command == "next":
                if result["artifact_errors"]:
                    raise ValueError("Recorded inputs/results changed: " + "; ".join(result["artifact_errors"]))
                result = resource_contract(development.next_action(state), state, config, run)
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
    except (OSError, ValueError, KeyError, TypeError) as exc:
        if args.command == "verify":
            # Do not leave a stale pass report when a new verification fails.
            write_json(run / VERIFICATION_NAME, {
                "checked_at": now(), "structural_status": "invalid_state",
                "artifact_errors": [str(exc)], "semantic_status": "not established by this script",
                "measured_token_usage": None,
            })
        raise
    if args.command in {"work-add", "work-record", "revise", "review-add"}:
        phases = [receipt["phase"] for receipt in state["receipts"]]
        if "reconcile" in phases:
            raise ValueError("Reconciliation is frozen; preserve it and start a linked new run")
        if args.command in {"work-add", "work-record"} and "recombine" not in phases:
            raise ValueError("Development work runs after recombine and before reconcile; preserve a reconciled run and start a new version")
        errors = verify(run, state)["artifact_errors"]
        if errors:
            raise ValueError("Recorded inputs/results changed: " + "; ".join(errors))
        snapshot = lambda name: artifact(run, name)
        if args.command == "work-add":
            inventory = sorted(p.resolve().relative_to(run.resolve()).as_posix() for p in run.rglob("*")
                               if p.is_file() and p.resolve().is_relative_to(run.resolve()))
            result = development.add_job(state, args, snapshot, now(), inventory)
        elif args.command == "work-record":
            result = development.record_result(state, args, snapshot, now())
        elif args.command == "review-add":
            if "review" not in phases:
                raise ValueError("Save the actual review receipt before registering its issues")
            result = {"registered_issue": review_contract.add_issue(state, args, snapshot(args.source), now())}
        else:
            if args.confirm == bool(args.artifact):
                raise ValueError("Choose new --artifact files, or --confirm without artifacts")
            files = [snapshot(name) for name in args.artifact]
            reserved = {item["path"] for receipt in state["receipts"] for item in receipt["artifacts"]}
            reserved.update(item["path"] for item in revisions.artifacts(state))
            reserved.update(item["path"] for item in development.job_artifacts(state["work"]))
            if len({item["path"] for item in files}) != len(files) or reserved.intersection(item["path"] for item in files):
                raise ValueError("Revision updates need new files distinct from earlier artifacts")
            result = {"revision": revisions.append(state, args.phase, files, args.reason, args.confirm, now(), args.complete)}
        development.validate_jobs(state, validate_artifact_record)
        review_contract.validate_issues(state, validate_artifact_record)
        revisions.validate(state, validate_artifact_record)
        persist_state(run, state)
        if "next" in result and isinstance(result["next"], dict):
            result["next"] = resource_contract(result["next"], state, config, run)
        else:
            result["next"] = resource_contract(development.next_action(state), state, config, run)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    if args.command == "record":
        index = len(state["receipts"])
        expected = state["phases"][index] if index < len(state["phases"]) else None
        if args.phase != expected:
            raise ValueError(f"Next phase is {expected!r}, not {args.phase!r}")
        if args.status == "partial" and not args.reason.strip():
            raise ValueError("A partial phase needs a concrete --reason")
        if args.report is not None and args.phase != "reconcile":
            raise ValueError("--report is only used when recording reconcile")
        if args.pathways is not None and args.phase != "reconcile":
            raise ValueError("--pathways is only used when recording reconcile")
        if any([args.review_format, args.review_context, args.review_coverage]) and args.phase != "review":
            raise ValueError("Review representation/context/coverage are only used for review")
        if args.no_issues_reason and args.phase not in {"review", "reconcile"}:
            raise ValueError("No-issues declaration is only used for review or reconciliation")
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
        work_outputs = {f["path"] for job in state["work"] for result in job["results"] for f in result["artifacts"]}
        if work_outputs.intersection(names):
            raise ValueError("Integrate work into a separate phase artifact; retain its original result")
        if args.phase in {"pathways", "reconcile"} and args.status == "done":
            development.require_finished(state)
        receipt = {
            "phase": args.phase, "recorded_at": now(), "status": args.status,
            "reason": args.reason.strip(), "artifacts": files,
        }
        if args.phase == "review":
            if not all([args.review_format, args.review_context, args.review_coverage]):
                raise ValueError("Review needs --review-format, --review-context and --review-coverage")
            if args.status == "done" and args.review_context == "unavailable":
                raise ValueError("Unavailable review is unperformed; record it as partial")
            if (args.review_context != "isolated" or args.review_coverage == "limited") and not args.reason.strip():
                raise ValueError("Limited or non-isolated review needs a concrete --reason")
            receipt["review_record"] = {"format": args.review_format, "context": args.review_context,
                                        "coverage": args.review_coverage, "no_issues_reason": args.no_issues_reason.strip()}
        if args.report is not None:
            snapshot = artifact(run, args.report)
            if snapshot["path"] in prior or snapshot["path"] in names or snapshot["path"] in work_outputs:
                raise ValueError("Reconciled report must be separate from earlier phase artifacts and the disposition record")
            active = revisions.current(state).get("pathways")
            pathway_snapshot = artifact(run, args.pathways) if args.pathways else (active["artifacts"][0] if active else None)
            if active is None or pathway_snapshot not in active["artifacts"]:
                raise ValueError("Bind the current pathway synthesis, not a historical or unrelated file")
            if args.status == "done" and not revisions.pathway_ready(state):
                raise ValueError("Update or confirm the pathway synthesis after review and follow-up work using revise")
            no_issues_reason = args.no_issues_reason.strip() or next((r["review_record"].get("no_issues_reason", "") for r in state["receipts"] if r["phase"] == "review"), "")
            if args.status == "done" and not state["review_issues"] and not no_issues_reason:
                raise ValueError("Register review issues, or give --no-issues-reason for a review with no material issues")
            if args.no_issues_reason and state["review_issues"]:
                raise ValueError("A no-issues declaration conflicts with registered issues")
            if state["review_issues"]:
                no_issues_reason = ""
            coverage = check_report_excerpts(run, files, snapshot, args.status == "done", pathway_snapshot, state["review_issues"])
            if args.status == "done":
                check_pathway_changes(state, coverage, pathway_snapshot)
            receipt["report_snapshot"] = snapshot
            receipt["pathways_snapshot"] = pathway_snapshot
            receipt["issue_coverage"] = coverage
            receipt["no_issues_reason"] = no_issues_reason
        if args.phase == "deliver":
            snapshot = next((r["report_snapshot"] for r in state["receipts"] if "report_snapshot" in r), None)
            if snapshot is not None and snapshot["path"] not in names:
                raise ValueError("Delivery must include the report bound during reconciliation")
        state["receipts"].append(receipt)
        persist_state(run, state)
        print(json.dumps({"recorded": args.phase, "status": args.status,
                          "next": resource_contract(development.next_action(state), state, config, run)}, ensure_ascii=False, indent=2))
        return 0
    result = verify(run, state)
    write_json(run / VERIFICATION_NAME, result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["structural_status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
