"""Append-only document revisions and the current-version view."""
from __future__ import annotations

import hashlib
import json

REVISION_PHASES = {"frame", "foothold", "diverge", "research", "recombine", "pathways"}


def digest(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def current(state: dict) -> dict:
    result = {receipt["phase"]: {"artifacts": receipt["artifacts"], "version": 1, "status": receipt["status"],
              "after_receipts": state["phases"].index(receipt["phase"]) + 1}
              for receipt in state["receipts"]}
    for revision in state["revisions"]:
        phase = revision["phase"]
        result[phase] = {**revision, "status": revision.get("status", result[phase]["status"])}
    return result


def dependency_fingerprint(state: dict) -> str:
    upstream = {phase: {"artifacts": item["artifacts"], "status": item["status"]}
                for phase, item in current(state).items()
                if phase in REVISION_PHASES - {"pathways"}}
    material = [issue for issue in state["review_issues"] if issue["kind"] == "material"]
    return digest({"work": state["work"], "upstream": upstream, "material_issues": material})


def pathway_ready(state: dict) -> bool:
    item = current(state).get("pathways")
    review_index = state["phases"].index("review") + 1
    return bool(item and item["after_receipts"] >= review_index and
                item.get("dependency_fingerprint") == dependency_fingerprint(state))


def partial_status(state: dict, work_summary: dict) -> dict:
    """Preserve historical partials and explicit completion declarations.

    A document update alone does not finish an incomplete upstream phase.
    Pathway recovery still requires the existing work and review checkpoint.
    """
    historical = [receipt["phase"] for receipt in state["receipts"] if receipt["status"] == "partial"]
    active = current(state)
    superseded = [phase for phase in historical if phase in REVISION_PHASES - {"pathways"}
                  and active[phase]["status"] == "done"]
    if ("pathways" in historical and pathway_ready(state)
            and not work_summary["pending_ids"] and not work_summary["missing_kinds"]):
        superseded.append("pathways")
    return {"partial_phases": [phase for phase in historical if phase not in superseded],
            "superseded_partial_phases": superseded}


def validate(state: dict, validate_artifact) -> None:
    revisions = state.get("revisions")
    if not isinstance(revisions, list):
        raise ValueError("State needs a revisions list")
    active = {r["phase"]: {"artifacts": r["artifacts"], "version": 1, "status": r["status"]}
              for r in state["receipts"]}
    for item in revisions:
        if not isinstance(item, dict) or item.get("phase") not in REVISION_PHASES or item["phase"] not in active:
            raise ValueError("Revision must refer to a recorded revisable phase")
        previous = active[item["phase"]]
        status = item.get("status", previous["status"])
        if not isinstance(status, str) or status not in {"done", "partial"} or (previous["status"] == "done" and status == "partial"):
            raise ValueError("Invalid revision completion status")
        if item.get("previous") != previous["artifacts"] or type(item.get("version")) is not int or item["version"] != previous["version"] + 1:
            raise ValueError("Revision chain does not match its predecessor")
        if not isinstance(item.get("reason"), str) or not item["reason"].strip():
            raise ValueError("Revision needs a concrete reason")
        if type(item.get("after_receipts")) is not int or not state["phases"].index(item["phase"]) + 1 <= item["after_receipts"] <= len(state["receipts"]):
            raise ValueError("Invalid revision checkpoint")
        if item.get("kind") not in {"update", "confirm"} or not isinstance(item.get("artifacts"), list) or not item["artifacts"]:
            raise ValueError("Invalid revision artifacts")
        for saved in item["artifacts"]:
            validate_artifact(saved)
        if item["kind"] == "confirm" and item["artifacts"] != previous["artifacts"]:
            raise ValueError("Confirmation must retain the current version")
        if item["kind"] == "update" and {f["path"] for f in item["artifacts"]}.intersection(f["path"] for f in previous["artifacts"]):
            raise ValueError("An update needs a new file, preserving the preceding version")
        if not isinstance(item.get("dependency_fingerprint"), str) or len(item["dependency_fingerprint"]) != 64:
            raise ValueError("Invalid revision dependency fingerprint")
        active[item["phase"]] = {**item, "status": status}


def artifacts(state: dict):
    for item in state["revisions"]:
        yield from item["artifacts"]


def append(state: dict, phase: str, files, reason: str, confirm: bool, timestamp: str, complete: bool = False) -> dict:
    active = current(state)
    if phase not in REVISION_PHASES or phase not in active:
        raise ValueError("Revise a previously recorded phase")
    if any(r["phase"] == "reconcile" for r in state["receipts"]):
        raise ValueError("Reconciliation is frozen; create a linked new run for later changes")
    if not reason.strip():
        raise ValueError("Revision or confirmation needs --reason")
    old = active[phase]
    item = {"phase": phase, "version": old["version"] + 1, "kind": "confirm" if confirm else "update",
            "status": "done" if complete else old["status"],
            "previous": old["artifacts"], "artifacts": old["artifacts"] if confirm else files,
            "reason": reason.strip(), "recorded_at": timestamp, "after_receipts": len(state["receipts"]),
            "dependency_fingerprint": dependency_fingerprint(state)}
    state["revisions"].append(item)
    return item
