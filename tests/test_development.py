"""Execution invariants for work whose semantic content is intentionally unconstrained."""
from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from test_run_control import call, CONFIG


class DevelopmentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.run = Path(self.temp.name) / "case"
        self.ok("init", "--topic", "Synthetic future question")
        for phase in CONFIG["phases"][:5]:
            self.file(phase + ".md", "Synthetic phase " + phase)
            self.ok("record", "--phase", phase, "--artifact", phase + ".md")

    def ok(self, *args):
        if args[:1] == ("record",) and "review" in args:
            args += ("--review-format", "issue_summary", "--review-context", "isolated", "--review-coverage", "complete",
                     "--no-issues-reason", "Synthetic review with no issues")
        result = call(*args, "--run", str(self.run))
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def file(self, name, text="Synthetic work result, not a real case"):
        path = self.run / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def open(self, key="e1", kind="evolution", *extra):
        return self.ok("work-add", "--id", key, "--kind", kind, "--question", "A consequential question",
                       "--source", "recombine.md", *extra)

    def finish(self, key, name=None, *extra):
        name = name or "work/" + key + ".md"
        self.file(name)
        return self.ok("work-record", "--id", key, "--artifact", name, *extra)

    def state(self):
        return json.loads((self.run / "run-state.json").read_text())

    def test_missing_development_blocks_completed_pathways(self):
        self.assertEqual(self.ok("next")["next"], "plan_work")
        self.file("pathways.md")
        before = (self.run / "run-state.json").read_bytes()
        result = call("record", "--run", str(self.run), "--phase", "pathways", "--artifact", "pathways.md")
        self.assertEqual(result.returncode, 2)
        self.assertIn("Development work remains", result.stderr)
        self.assertEqual(before, (self.run / "run-state.json").read_bytes())
        self.open()
        self.finish("e1")
        self.assertEqual(self.ok("next")["missing_kinds"], ["contrast"])
        self.open("c1", "contrast")
        self.finish("c1")
        self.ok("record", "--phase", "pathways", "--artifact", "pathways.md")
        self.assertEqual(self.ok("next")["phase"], "review")

    def test_dependencies_priorities_and_read_only_next(self):
        self.open("parent", "evolution", "--priority", "3")
        self.open("child", "contrast", "--after", "parent", "--priority", "1")
        self.open("ready", "contrast", "--priority", "2")
        before = (self.run / "run-state.json").read_bytes()
        self.assertEqual(self.ok("next")["id"], "ready")
        self.assertEqual(before, (self.run / "run-state.json").read_bytes())
        self.file("child.md")
        blocked = call("work-record", "--run", str(self.run), "--id", "child", "--artifact", "child.md")
        self.assertEqual(blocked.returncode, 2)
        self.finish("parent")
        current = self.ok("next")
        self.assertEqual(current["id"], "child")
        self.assertEqual(current["dependency_results"]["parent"][0]["path"], "work/parent.md")
        self.finish("child")

    def test_partial_attempt_can_resume_without_rewriting_history(self):
        self.open()
        self.finish("e1", "work/attempt-1.md", "--status", "partial", "--reason", "Host interrupted")
        old = (self.run / "work/attempt-1.md").read_bytes()
        self.assertEqual(self.ok("next")["id"], "e1")
        self.assertEqual(self.ok("status")["development_work"]["pending_ids"], ["e1"])
        self.finish("e1", "work/attempt-2.md")
        self.assertEqual((self.run / "work/attempt-1.md").read_bytes(), old)
        self.assertEqual([r["status"] for r in self.state()["work"][0]["results"]], ["partial", "done"])
        result = call("work-record", "--run", str(self.run), "--id", "e1", "--artifact", "work/attempt-2.md")
        self.assertEqual(result.returncode, 2)
        self.assertIn("immutable", result.stderr)

    def test_input_and_result_tampering_are_detected(self):
        self.file("seed.md")
        self.ok("work-add", "--id", "e1", "--kind", "evolution", "--question", "What changes?", "--source", "seed.md")
        original = (self.run / "seed.md").read_bytes()
        self.file("seed.md", "Changed input")
        self.assertEqual(call("next", "--run", str(self.run)).returncode, 2)
        self.assertTrue(self.ok("status")["artifact_errors"])
        (self.run / "seed.md").write_bytes(original)
        self.finish("e1")
        self.file("work/e1.md", "Changed result")
        self.assertEqual(call("verify", "--run", str(self.run)).returncode, 1)
        self.assertIn("Development input/result changed", (self.run / "verification.json").read_text())

    def test_sources_outputs_and_metadata_cannot_be_recycled(self):
        self.open()
        outside = self.run.parent / "outside.md"
        outside.write_text("Synthetic external file")
        os.link(outside, self.run / "alias.md")
        before = (self.run / "run-state.json").read_bytes()
        for name in ["recombine.md", "run-state.json", "../outside.md", "alias.md"]:
            result = call("work-record", "--run", str(self.run), "--id", "e1", "--artifact", name)
            self.assertEqual(result.returncode, 2, name)
            self.assertEqual(before, (self.run / "run-state.json").read_bytes())
        self.finish("e1")
        self.ok("work-add", "--id", "c1", "--kind", "contrast", "--question", "A next question",
                "--source", "work/e1.md", "--after", "e1")
        self.finish("c1")
        result = call("record", "--run", str(self.run), "--phase", "pathways", "--artifact", "work/e1.md")
        self.assertEqual(result.returncode, 2)

    def test_open_followup_blocks_closure_even_after_minimum_kinds(self):
        self.open()
        self.finish("e1")
        self.open("c1", "contrast")
        self.finish("c1")
        self.open("e2", "evolution", "--after", "e1")
        self.file("pathways.md")
        result = call("record", "--run", str(self.run), "--phase", "pathways", "--artifact", "pathways.md")
        self.assertEqual(result.returncode, 2)
        self.ok("record", "--phase", "pathways", "--artifact", "pathways.md", "--status", "partial", "--reason", "Follow-up unfinished")
        self.assertEqual(self.ok("status")["partial_phases"], ["pathways"])

    def test_review_can_add_work_but_reconciliation_freezes_it(self):
        for key, kind in [("e1", "evolution"), ("c1", "contrast")]:
            self.open(key, kind)
            self.finish(key)
        for phase in ["pathways", "review"]:
            self.file(phase + ".md")
            self.ok("record", "--phase", phase, "--artifact", phase + ".md")
        self.open("e2", "evolution", "--after", "e1")
        self.file("report.md", "Synthetic final report\n")
        self.file("reconcile.md", "[Report excerpt](report.md#L1)\n> Synthetic final report\n")
        args = ("record", "--run", str(self.run), "--phase", "reconcile", "--artifact", "reconcile.md", "--report", "report.md")
        self.assertEqual(call(*args).returncode, 2)
        self.finish("e2")
        self.ok("revise", "--phase", "pathways", "--confirm", "--reason", "Synthetic follow-up made no content change")
        self.assertEqual(call(*args).returncode, 0)
        late = call("work-add", "--run", str(self.run), "--id", "late", "--kind", "contrast", "--source", "report.md", "--question", "New question")
        self.assertEqual(late.returncode, 2)
        self.ok("record", "--phase", "deliver", "--artifact", "report.md")
        self.assertEqual(self.ok("verify")["structural_status"], "pass")
        self.assertEqual(self.ok("next")["next"], "recorded_complete")

    def test_invalid_work_state_replaces_stale_verification(self):
        self.file("verification.json", '{"structural_status":"pass"}')
        state = self.state()
        state["work"] = [{"id": "bad", "inputs": None}]
        (self.run / "run-state.json").write_text(json.dumps(state))
        self.assertEqual(call("verify", "--run", str(self.run)).returncode, 2)
        data = json.loads((self.run / "verification.json").read_text())
        self.assertEqual(data["structural_status"], "invalid_state")

    def test_new_work_requires_recombination_and_valid_dependency(self):
        forward = call("work-add", "--run", str(self.run), "--id", "e1", "--kind", "evolution", "--source", "recombine.md", "--question", "Question", "--after", "e2")
        self.assertEqual(forward.returncode, 2)
        self.run = self.run.parent / "early"
        self.ok("init", "--topic", "Early synthetic case")
        self.file("seed.md")
        early = call("work-add", "--run", str(self.run), "--id", "e1", "--kind", "evolution", "--source", "seed.md", "--question", "Question")
        self.assertEqual(early.returncode, 2)

    def test_brief_profile_does_not_require_development_queue(self):
        self.run = self.run.parent / "brief"
        self.ok("init", "--topic", "Explicit short request", "--profile", "brief")
        for phase in CONFIG["phases"][:6]:
            self.file(phase + ".md")
            self.ok("record", "--phase", phase, "--artifact", phase + ".md")
        self.assertEqual(self.ok("status")["development_work"]["required_kinds"], [])

    def test_work_writer_respects_existing_lock(self):
        self.file(".run-control.lock", '{"pid":0,"note":"synthetic lock"}')
        before = (self.run / "run-state.json").read_bytes()
        result = call("work-add", "--run", str(self.run), "--id", "e1", "--kind", "evolution", "--source", "recombine.md", "--question", "Question")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(before, (self.run / "run-state.json").read_bytes())
        self.assertEqual(self.ok("next")["next"], "plan_work")
