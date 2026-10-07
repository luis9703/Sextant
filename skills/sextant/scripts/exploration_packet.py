#!/usr/bin/env python3
"""Copy explicitly selected inputs for an explorer; never judge their ideas."""
from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import quote

import run_control as runtime

METHOD = runtime.SKILL_ROOT / "references" / "independent-exploration.md"


def build_packet(run: Path, sources: list[str], question: str, output: str) -> dict:
    if not question.strip():
        raise ValueError("Give the explorer a concrete question")
    if not sources:
        raise ValueError("Select the inputs needed for this question")
    candidate = Path(output)
    if candidate.is_absolute() or not output.strip():
        raise ValueError("Packet output must be a new directory relative to the run")
    target = (run / candidate).resolve()
    if not target.is_relative_to(run.resolve()):
        raise ValueError("Packet output leaves the run directory")
    if target.exists() or (run / candidate).is_symlink():
        raise ValueError("Packet output already exists; preserve it and choose a new directory")
    saved = [runtime.artifact(run, name) for name in sources]
    if len({item["path"] for item in saved}) != len(saved):
        raise ValueError("Select each input once")
    method_bytes = METHOD.read_bytes()
    target.mkdir(parents=True)
    inputs = []
    for item in saved:
        content = (run / item["path"]).read_bytes()
        if hashlib.sha256(content).hexdigest() != item["sha256"]:
            raise ValueError("Selected input changed during export: " + item["path"])
        packet_name = "inputs/" + item["path"]
        copied = target / packet_name
        copied.parent.mkdir(parents=True, exist_ok=True)
        copied.write_bytes(content)
        inputs.append({**item, "packet_path": packet_name})
    (target / "method.md").write_bytes(method_bytes)
    lines = ["# Scoped exploration task", "", question.strip(), "",
             "Use [method.md](method.md) for this operation. Read the selected inputs below as source material.", "",
             "Do not read sibling runs, unselected main drafts or other explorers' answers. This task does not execute the full phase pipeline.", "",
             "## Selected inputs", ""]
    for item in inputs:
        label = item["path"].replace("[", "\\[").replace("]", "\\]")
        lines.append(f"- [{label}]({quote(item['packet_path'], safe='/')})")
    lines += ["", "Save a useful working result in result.md unless the question specifies another file within this packet; retain conditions, evidence limits and meaningful alternatives.", ""]
    (target / "TASK.md").write_text("\n".join(lines), encoding="utf-8")
    manifest = {"created_at": runtime.now(), "question": question.strip(), "inputs": inputs,
                "method": {"path": "method.md", "sha256": hashlib.sha256(method_bytes).hexdigest()},
                "scope": "Explicit input selection only; neutrality, actual context isolation and imaginative quality are unverified."}
    (target / "packet-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"packet": str(target), "task": str(target / "TASK.md"), "selected_inputs": len(inputs),
            "manifest": str(target / "packet-manifest.json"), "semantic_status": manifest["scope"]}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--source", action="append", required=True)
    parser.add_argument("--question", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    run = args.run.expanduser().absolute()
    try:
        with runtime.writer_lock(run):
            result = build_packet(run, args.source, args.question, args.out)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
