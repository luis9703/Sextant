"""Associate registered objections with dispositions and literal saved locations.

Coverage checks do not decide whether an objection or its repair is correct.
"""
from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote

ID_PATTERN = r"[A-Za-z][A-Za-z0-9_-]{0,63}"
ID_RE = re.compile(ID_PATTERN)
ACTIONS = {"revise": "revise", "修改": "revise", "keep": "keep", "保留": "keep",
           "drop": "drop", "移除": "drop", "unresolved": "unresolved", "未决": "unresolved",
           "not_used": "not_used", "不采用": "not_used"}
DISPOSITION_RE = re.compile(r"^\[(?:Disposition|处置) (" + ID_PATTERN + r"): ([^\]]+)\]$")
EXCERPT_RE = re.compile(r"^\[(Report excerpt|报告摘录|Pathway excerpt|路径摘录)(?: (" + ID_PATTERN + r"))?\]\(([^#\r\n)]+)#L([1-9][0-9]*)\)$")
EXCERPT_PREFIXES = ("[Report excerpt", "[报告摘录", "[Pathway excerpt", "[路径摘录")


def validate_issues(state: dict, validate_artifact) -> None:
    issues = state.get("review_issues")
    if not isinstance(issues, list):
        raise ValueError("State needs a review issue list")
    seen = set()
    for issue in issues:
        if not isinstance(issue, dict) or not isinstance(issue.get("id"), str) or not ID_RE.fullmatch(issue["id"]) or issue["id"] in seen:
            raise ValueError("Invalid or duplicate review issue id")
        if issue.get("kind") not in {"material", "lead"} or not isinstance(issue.get("question"), str) or not issue["question"].strip():
            raise ValueError("Review issue needs a kind and concrete question")
        targets = issue.get("targets")
        if not isinstance(targets, list) or any(t not in {"report", "pathways"} for t in targets) or len(set(targets)) != len(targets):
            raise ValueError("Invalid review issue targets")
        if issue["kind"] == "material" and not targets:
            raise ValueError("A material issue needs affected targets")
        validate_artifact(issue["source"])
        seen.add(issue["id"])


def add_issue(state, args, source, timestamp):
    if not ID_RE.fullmatch(args.id) or any(i["id"] == args.id for i in state["review_issues"]):
        raise ValueError("Use a new review issue id")
    if not args.question.strip():
        raise ValueError("Review issue needs a concrete --question")
    targets = args.target if args.target is not None else (["pathways", "report"] if args.kind == "material" else [])
    if len(set(targets)) != len(targets):
        raise ValueError("Duplicate affected target")
    issue = {"id": args.id, "kind": args.kind, "question": args.question.strip(), "targets": targets,
             "source": source, "recorded_at": timestamp}
    state["review_issues"].append(issue)
    return issue


def examine(run, files, report, pathways, issues, snapshot, required):
    targets = {"report": report}
    if pathways is not None:
        targets["pathways"] = pathways
    texts = {key: (run / value["path"]).read_text(encoding="utf-8").splitlines() for key, value in targets.items()}
    known = {issue["id"]: issue for issue in issues}
    dispositions = {}
    excerpts = []
    for note in files:
        lines = (run / note["path"]).read_text(encoding="utf-8").splitlines()
        for index, line in enumerate(lines):
            if line.startswith(("[Disposition ", "[处置 ")):
                match = DISPOSITION_RE.fullmatch(line)
                if match is None or match[2] not in ACTIONS:
                    raise ValueError("Malformed issue disposition")
                key = match[1]
                if key not in known or key in dispositions:
                    raise ValueError("Disposition has unknown or duplicate issue id: " + key)
                tail = next((item.strip() for item in lines[index + 1:] if item.strip()), "")
                if not tail or tail.startswith(("[", ">", "#", "```")):
                    raise ValueError("Disposition needs a concrete rationale after its marker")
                dispositions[key] = {"id": key, "action": ACTIONS[match[2]], "reason": tail}
            if not line.startswith(EXCERPT_PREFIXES):
                continue
            match = EXCERPT_RE.fullmatch(line)
            if match is None or index + 1 >= len(lines) or not lines[index + 1].startswith("> "):
                raise ValueError(f"Malformed report excerpt in {note['path']} at line {index + 1}")
            key = match[2]
            if key is None and known:
                raise ValueError("Excerpt needs an explicit issue id; it cannot inherit a disposition id")
            if key is not None and key not in known:
                raise ValueError("Excerpt has an unregistered issue id: " + key)
            target = "report" if match[1] in {"Report excerpt", "报告摘录"} else "pathways"
            if target not in targets:
                raise ValueError("No bound pathway synthesis for this excerpt")
            reference_name = Path(note["path"]).parent / unquote(match[3])
            reference = snapshot(str(reference_name))
            if reference["path"] != targets[target]["path"]:
                raise ValueError("Excerpt must refer to the bound current " + target)
            number = int(match[4])
            quote = lines[index + 1][2:]
            if not quote.strip() or number > len(texts[target]) or quote not in texts[target][number - 1]:
                raise ValueError(f"Report excerpt does not match {targets[target]['path']} at line {number}")
            excerpts.append({"issue": key, "target": target, "line": number, "quote": quote})
    if required and not any(item["target"] == "report" for item in excerpts):
        raise ValueError("Completed reconciliation needs a Report excerpt or 报告摘录 with a literal passage")
    if required:
        missing = set(known) - set(dispositions)
        if missing:
            raise ValueError("Missing dispositions for review issues: " + ", ".join(sorted(missing)))
        for key, decision in dispositions.items():
            if decision["action"] == "not_used":
                continue
            covered = {item["target"] for item in excerpts if item["issue"] == key}
            missing_targets = set(known[key]["targets"]) - covered
            if missing_targets:
                raise ValueError(f"Issue {key} needs an excerpt for each affected target: {sorted(missing_targets)}")
    return {"dispositions": list(dispositions.values()), "excerpts": excerpts,
            "unresolved_ids": [key for key, item in dispositions.items() if item["action"] == "unresolved"],
            "not_used_ids": [key for key, item in dispositions.items() if item["action"] == "not_used"],
            "semantic_status": "coverage and literal positions only; adequacy unverified"}
