"""A small resumable work queue; the work itself remains ordinary Markdown.

This module checks dependencies and saved inputs/results, never imagination quality.
The host supplies the model, research tools, and any authorized delegation.
"""
from __future__ import annotations

import re

import revisions

KINDS = ("evolution", "contrast")
ID_RE = re.compile(r"[a-z][a-z0-9_-]{0,63}")


def finished(job: dict) -> bool:
    return bool(job["results"]) and job["results"][-1]["status"] == "done"


def validate_jobs(state: dict, validate_artifact) -> None:
    jobs = state.get("work")
    if not isinstance(jobs, list):
        raise ValueError("State needs a development work list")
    seen = set()
    output_paths = set()
    phase_paths = {item["path"] for receipt in state["receipts"] for item in receipt["artifacts"]}
    for job in jobs:
        if not isinstance(job, dict) or not isinstance(job.get("id"), str) or not ID_RE.fullmatch(job["id"]):
            raise ValueError("Invalid work id")
        if job["id"] in seen or job.get("kind") not in KINDS:
            raise ValueError("Duplicate work id or unknown work kind")
        if not isinstance(job.get("question"), str) or not job["question"].strip():
            raise ValueError("Work needs a concrete question")
        if type(job.get("priority")) is not int or not 1 <= job["priority"] <= 3:
            raise ValueError("Work priority must be 1, 2 or 3")
        after = job.get("after")
        if not isinstance(after, list) or any(not isinstance(key, str) or key not in seen for key in after) or len(set(after)) != len(after):
            raise ValueError("Work dependencies must be distinct earlier work ids")
        inputs = job.get("inputs")
        if not isinstance(inputs, list) or not inputs:
            raise ValueError("Work needs saved inputs")
        for item in inputs:
            validate_artifact(item)
        results = job.get("results")
        if not isinstance(results, list):
            raise ValueError("Invalid work results")
        existing = job.get("files_at_registration")
        if not isinstance(existing, list) or any(not isinstance(name, str) for name in existing):
            raise ValueError("Work needs its file inventory at registration")
        if results and any(not finished(previous) for previous in jobs[:len(seen)] if previous["id"] in after):
            raise ValueError("Work results require completed dependencies")
        for index, result in enumerate(results):
            if not isinstance(result, dict) or result.get("status") not in {"done", "partial"}:
                raise ValueError("Invalid work result status")
            if not isinstance(result.get("reason"), str):
                raise ValueError("Work result reason must be a string")
            if result["status"] == "partial" and not result["reason"].strip():
                raise ValueError("Partial work needs a concrete reason")
            if result.get("origin") not in {"after_registration", "adopted"}:
                raise ValueError("Work result needs a declared origin")
            if result["origin"] == "adopted" and not result["reason"].strip():
                raise ValueError("Adopted work needs a reason")
            if result["status"] == "done" and index != len(results) - 1:
                raise ValueError("Completed work is immutable; open a dependent follow-up")
            files = result.get("artifacts")
            if not isinstance(files, list) or not files:
                raise ValueError("Work result needs an artifact")
            for item in files:
                validate_artifact(item)
                if result["origin"] == "after_registration" and (item["path"] in existing or item["path"] in output_paths or item["path"] in phase_paths or item["path"] in {i["path"] for i in inputs}):
                    raise ValueError("Work outputs must be distinct from phase artifacts, their inputs and previous outputs")
                output_paths.add(item["path"])
        seen.add(job["id"])
    # An output may be a later job's input, but the snapshots must agree.
    snapshots = {}
    for item in job_artifacts(jobs):
        previous = snapshots.setdefault(item["path"], item)
        if previous != item:
            raise ValueError("A work input/result has conflicting snapshots")


def job_artifacts(jobs: list[dict]):
    for job in jobs:
        yield from job["inputs"]
        for result in job["results"]:
            yield from result["artifacts"]


def summary(state: dict) -> dict:
    jobs = state["work"]
    complete = {job["kind"] for job in jobs if finished(job)}
    return {
        "required_kinds": state["work_required"],
        "missing_kinds": [kind for kind in state["work_required"] if kind not in complete],
        "pending_ids": [job["id"] for job in jobs if not finished(job)],
        "completed_ids": [job["id"] for job in jobs if finished(job)],
        "adopted_ids": [job["id"] for job in jobs if finished(job) and job["results"][-1]["origin"] == "adopted"],
        "quality": "not established by the queue",
    }


def require_finished(state: dict) -> None:
    current = summary(state)
    if current["missing_kinds"] or current["pending_ids"]:
        raise ValueError("Development work remains: " + str(current) + "; use next, complete the work, or record an honestly partial phase")


def next_action(state: dict) -> dict:
    jobs = {job["id"]: job for job in state["work"]}
    pending = [job for job in state["work"] if not finished(job)]
    ready = [job for job in pending if all(finished(jobs[key]) for key in job["after"])]
    if ready:
        job = min(ready, key=lambda item: item["priority"])
        return {
            "next": "work", "id": job["id"], "kind": job["kind"], "question": job["question"],
            "inputs": job["inputs"], "after": job["after"],
            "dependency_results": {key: jobs[key]["results"][-1]["artifacts"] for key in job["after"]},
            "previous_attempts": job["results"], "guide": "references/development.md",
        }
    index = len(state["receipts"])
    phase = state["phases"][index] if index < len(state["phases"]) else None
    current = summary(state)
    if phase in {"pathways", "reconcile"} and current["missing_kinds"]:
        return {"next": "plan_work", "phase": phase, "missing_kinds": current["missing_kinds"],
                "guide": "references/development.md"}
    if phase is not None:
        return {"next": "phase", "phase": phase}
    partial = revisions.partial_status(state, current)
    return {"next": "finished_with_limits" if pending or current["missing_kinds"] or partial["partial_phases"] else "recorded_complete",
        **partial,
        "semantic_status": "not established by this script"}


def add_job(state: dict, args, snapshot, timestamp: str, inventory: list[str]) -> dict:
    if not ID_RE.fullmatch(args.id) or any(job["id"] == args.id for job in state["work"]):
        raise ValueError("Use a new work id: lowercase letters, digits, hyphens or underscores")
    if not args.question.strip():
        raise ValueError("Work needs a concrete question")
    known = {job["id"]: job for job in state["work"]}
    if len(set(args.after)) != len(args.after) or any(key not in known for key in args.after):
        raise ValueError("Dependencies must be distinct existing work ids")
    inputs = [snapshot(name) for name in args.source]
    if len({item["path"] for item in inputs}) != len(inputs):
        raise ValueError("Duplicate work input")
    job = {"id": args.id, "kind": args.kind, "question": args.question.strip(),
           "priority": args.priority, "after": args.after, "created_at": timestamp,
           "inputs": inputs, "results": [], "files_at_registration": inventory}
    state["work"].append(job)
    return {"opened_work": args.id, "next": next_action(state)}


def record_result(state: dict, args, snapshot, timestamp: str) -> dict:
    jobs = {job["id"]: job for job in state["work"]}
    if args.id not in jobs:
        raise ValueError("Unknown work id")
    job = jobs[args.id]
    if finished(job):
        raise ValueError("Completed work is immutable; open a dependent follow-up")
    if any(not finished(jobs[key]) for key in job["after"]):
        raise ValueError("Finish dependencies before recording this result")
    if args.status == "partial" and not args.reason.strip():
        raise ValueError("Partial work needs a concrete --reason")
    files = [snapshot(name) for name in args.artifact]
    reserved = {item["path"] for item in job_artifacts(state["work"])}
    reserved.update(item["path"] for receipt in state["receipts"] for item in receipt["artifacts"])
    names = [item["path"] for item in files]
    if args.adopt_existing and not args.reason.strip():
        raise ValueError("Adopting existing work needs a concrete --reason")
    if len(set(names)) != len(names):
        raise ValueError("Duplicate work result artifact")
    if not args.adopt_existing and (reserved.intersection(names) or set(job["files_at_registration"]).intersection(names)):
        raise ValueError("Save a new work result, distinct from inputs and previous artifacts")
    job["results"].append({"recorded_at": timestamp, "status": args.status,
                           "origin": "adopted" if args.adopt_existing else "after_registration",
                           "reason": args.reason.strip(), "artifacts": files})
    return {"recorded_work": args.id, "status": args.status, "next": next_action(state)}
