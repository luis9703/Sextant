"""Behavioral checks for phase order, artifact integrity and honest partial status."""
from __future__ import annotations

import json
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "skills/sextant/scripts/run_control.py"
CONFIG = json.loads((REPO / "skills/sextant/assets/depth-profiles.json").read_text())


def call(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(SCRIPT), *args], capture_output=True, text=True)


class RunControlTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.run = Path(self.temp.name) / "case"
        result = call("init", "--run", str(self.run), "--topic", "Synthetic future question")
        self.assertEqual(result.returncode, 0, result.stderr)

    def record(self, phase: str, *extra: str) -> subprocess.CompletedProcess:
        name = phase + ".md"
        if not (self.run / name).exists():
            (self.run / name).write_text(f"Synthetic fixture for {phase}; not a real evaluation.\n")
        if phase == "pathways":
            state = json.loads((self.run / "run-state.json").read_text())
            for kind in state["work_required"]:
                work_id = "fixture-" + kind
                if any(job["id"] == work_id for job in state["work"]):
                    continue
                opened = call("work-add", "--run", str(self.run), "--id", work_id, "--kind", kind,
                              "--source", "recombine.md", "--question", "Synthetic development question")
                self.assertEqual(opened.returncode, 0, opened.stderr)
                result_name = work_id + ".md"
                (self.run / result_name).write_text("Synthetic work result; not imagination quality evidence.\n")
                saved = call("work-record", "--run", str(self.run), "--id", work_id, "--artifact", result_name)
                self.assertEqual(saved.returncode, 0, saved.stderr)
        if phase == "reconcile":
            state = json.loads((self.run / "run-state.json").read_text())
            if not any(r['phase']=='pathways' for r in state['revisions']):
                confirmed = call("revise", "--run", str(self.run), "--phase", "pathways", "--confirm", "--reason", "Synthetic unchanged synthesis")
                self.assertEqual(confirmed.returncode, 0, confirmed.stderr)
            (self.run / "deliver.md").write_text("Synthetic report; not a real evaluation.\n")
            (self.run / name).write_text("Disposition fixture.\n[Report excerpt](deliver.md#L1)\n> Synthetic report; not a real evaluation.\n")
            extra = ("--report", "deliver.md", *extra)
        if phase == "review":
            context = "unavailable" if "partial" in extra else "isolated"
            coverage = "limited" if context == "unavailable" else "complete"
            extra = ("--review-format", "issue_summary", "--review-context", context, "--review-coverage", coverage,
                     "--no-issues-reason", "Synthetic review raised no material issues", *extra)
        return call("record", "--run", str(self.run), "--phase", phase, "--artifact", name, *extra)

    def reach_reconciliation(self) -> None:
        for phase in CONFIG["phases"][:CONFIG["phases"].index("reconcile")]:
            self.assertEqual(self.record(phase).returncode, 0)
        confirmed = call("revise", "--run", str(self.run), "--phase", "pathways", "--confirm", "--reason", "Synthetic unchanged synthesis")
        self.assertEqual(confirmed.returncode, 0, confirmed.stderr)

    def test_done_reconciliation_requires_saved_report(self) -> None:
        self.reach_reconciliation()
        (self.run / "reconcile.md").write_text("Disposition notes")
        before = (self.run / "run-state.json").read_bytes()
        result = call("record", "--run", str(self.run), "--phase", "reconcile", "--artifact", "reconcile.md")
        self.assertEqual(result.returncode, 2)
        self.assertIn("--report", result.stderr)
        self.assertEqual(before, (self.run / "run-state.json").read_bytes())

    def test_report_changed_after_reconciliation_blocks_delivery(self) -> None:
        self.reach_reconciliation()
        self.assertEqual(self.record("reconcile").returncode, 0)
        before = (self.run / "run-state.json").read_bytes()
        (self.run / "deliver.md").write_text("Changed conclusion after reconciliation")
        result = self.record("deliver")
        self.assertEqual(result.returncode, 2)
        self.assertIn("Report changed after reconciliation", result.stderr)
        self.assertEqual(before, (self.run / "run-state.json").read_bytes())
        self.assertEqual(call("verify", "--run", str(self.run)).returncode, 1)

    def test_delivery_must_include_the_bound_report(self) -> None:
        self.reach_reconciliation()
        self.assertEqual(self.record("reconcile").returncode, 0)
        shutil.copyfile(self.run / "deliver.md", self.run / "other.md")
        result = call("record", "--run", str(self.run), "--phase", "deliver", "--artifact", "other.md")
        self.assertEqual(result.returncode, 2)
        self.assertIn("must include", result.stderr)
        self.assertEqual(self.record("deliver").returncode, 0)
        self.assertEqual(call("verify", "--run", str(self.run)).returncode, 0)

    def test_report_snapshot_uses_artifact_boundaries_and_distinct_role(self) -> None:
        self.reach_reconciliation()
        (self.run / "reconcile.md").write_text("Disposition notes")
        outside = self.run.parent / "outside.md"
        outside.write_text("Outside file")
        os.link(outside, self.run / "linked.md")
        for name in ["../outside.md", "missing.md", "run-state.json", "frame.md", "reconcile.md", "linked.md"]:
            with self.subTest(name=name):
                result = call("record", "--run", str(self.run), "--phase", "reconcile", "--artifact", "reconcile.md", "--report", name)
                self.assertEqual(result.returncode, 2, result.stdout)
        self.assertEqual(outside.read_text(), "Outside file")
        result = call("record", "--run", str(self.run), "--phase", "reconcile", "--artifact", "reconcile.md", "--status", "partial", "--reason", "No completed report")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.record("deliver").returncode, 0)
        data = json.loads(call("verify", "--run", str(self.run)).stdout)
        self.assertEqual(data["partial_phases"], ["reconcile"])

    def test_report_binding_cannot_be_attached_to_another_phase(self) -> None:
        (self.run / "draft.md").write_text("Draft")
        result = self.record("frame", "--report", "draft.md")
        self.assertEqual(result.returncode, 2)
        self.assertIn("only used", result.stderr)

    def test_invalid_report_snapshot_clears_stale_pass(self) -> None:
        for phase in CONFIG["phases"]:
            self.assertEqual(self.record(phase).returncode, 0)
        self.assertEqual(call("verify", "--run", str(self.run)).returncode, 0)
        state_file = self.run / "run-state.json"
        state = json.loads(state_file.read_text())
        receipt = next(r for r in state["receipts"] if r["phase"] == "reconcile")
        receipt["report_snapshot"]["sha256"] = "invalid"
        state_file.write_text(json.dumps(state))
        self.assertEqual(call("verify", "--run", str(self.run)).returncode, 2)
        self.assertEqual(json.loads((self.run / "verification.json").read_text())["structural_status"], "invalid_state")

    def test_reconciliation_rejects_wrong_excerpt_locations(self) -> None:
        self.reach_reconciliation()
        (self.run / "report.md").write_text("# Saved report\nA conditional conclusion.\n")
        (self.run / "other.md").write_text("A conditional conclusion.\n")
        invalid = [
            "Disposition without evidence\n",
            "[Report excerpt](report.md#L1)\n> A conditional conclusion.\n",
            "[Report excerpt](report.md#L2)\n> Invented repair.\n",
            "[Report excerpt](report.md#L99)\n> A conditional conclusion.\n",
            "[Report excerpt](other.md#L1)\n> A conditional conclusion.\n",
            "[Report excerpt](report.md#L0)\n> A conditional conclusion.\n",
            "[Report excerpt](report.md#L2)\nMissing blockquote\n",
        ]
        before = (self.run / "run-state.json").read_bytes()
        for text in invalid:
            with self.subTest(text=text):
                (self.run / "notes.md").write_text(text)
                result = call("record", "--run", str(self.run), "--phase", "reconcile", "--artifact", "notes.md", "--report", "report.md")
                self.assertEqual(result.returncode, 2, result.stdout)
                self.assertEqual(before, (self.run / "run-state.json").read_bytes())
        (self.run / "notes.md").write_text("Accepted repair.\n[Report excerpt](report.md#L2)\n> conditional conclusion\n")
        result = call("record", "--run", str(self.run), "--phase", "reconcile", "--artifact", "notes.md", "--report", "report.md")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_verify_rechecks_excerpt_even_with_matching_note_hash(self) -> None:
        for phase in CONFIG["phases"]:
            self.assertEqual(self.record(phase).returncode, 0)
        self.assertEqual(call("verify", "--run", str(self.run)).returncode, 0)
        note = self.run / "reconcile.md"
        note.write_text("[Report excerpt](deliver.md#L99)\n> Synthetic report\n")
        state_file = self.run / "run-state.json"
        state = json.loads(state_file.read_text())
        receipt = next(r for r in state["receipts"] if r["phase"] == "reconcile")
        receipt["artifacts"][0].update(sha256=hashlib.sha256(note.read_bytes()).hexdigest(), bytes=note.stat().st_size)
        state_file.write_text(json.dumps(state))
        result = call("verify", "--run", str(self.run))
        self.assertEqual(result.returncode, 1)
        self.assertIn("Report excerpt does not match", result.stdout)

    def test_defaults_to_deep_and_does_not_invent_usage(self) -> None:
        result = call("status", "--run", str(self.run))
        data = json.loads(result.stdout)
        self.assertEqual(data["profile"], "deep")
        self.assertIsNone(data["measured_token_usage"])
        self.assertEqual(data["missing_phases"], CONFIG["phases"])

    def test_refuses_to_overwrite_run(self) -> None:
        before = (self.run / "run-state.json").read_bytes()
        result = call("init", "--run", str(self.run), "--topic", "Other")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(before, (self.run / "run-state.json").read_bytes())

    def test_cannot_skip_to_delivery(self) -> None:
        result = self.record("deliver")
        self.assertEqual(result.returncode, 2)
        self.assertIn("Next phase", result.stderr)
        self.assertEqual(call("verify", "--run", str(self.run)).returncode, 1)

    def test_complete_receipts_only_prove_structure(self) -> None:
        for phase in CONFIG["phases"]:
            result = self.record(phase)
            self.assertEqual(result.returncode, 0, result.stderr)
        result = call("verify", "--run", str(self.run))
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["semantic_status"], "not established by this script")
        self.assertTrue((self.run / "verification.json").is_file())

    def test_changed_earlier_artifact_is_detected(self) -> None:
        self.assertEqual(self.record("frame").returncode, 0)
        (self.run / "frame.md").write_text("Rewritten after the event")
        self.assertEqual(call("verify", "--run", str(self.run)).returncode, 1)
        self.assertEqual(self.record("foothold").returncode, 2)

    def test_missing_and_reused_artifacts_are_rejected(self) -> None:
        result = call("record", "--run", str(self.run), "--phase", "frame", "--artifact", "missing.md")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(self.record("frame").returncode, 0)
        result = call("record", "--run", str(self.run), "--phase", "foothold", "--artifact", "frame.md")
        self.assertEqual(result.returncode, 2)

    def test_partial_review_cannot_be_certified_as_complete(self) -> None:
        for phase in CONFIG["phases"]:
            extra = ("--status", "partial", "--reason", "Review tool unavailable") if phase == "review" else ()
            self.assertEqual(self.record(phase, *extra).returncode, 0)
        result = call("verify", "--run", str(self.run))
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["partial_phases"], ["review"])

    def test_rejects_artifact_outside_run(self) -> None:
        (self.run.parent / "outside.md").write_text("outside")
        result = call("record", "--run", str(self.run), "--phase", "frame", "--artifact", "../outside.md")
        self.assertEqual(result.returncode, 2)

    def test_budget_is_plan_not_measurement(self) -> None:
        second = self.run.parent / "second"
        result = call("init", "--run", str(second), "--topic", "Question", "--budget-min", "50000", "--budget-max", "100000")
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(call("status", "--run", str(second)).stdout)
        self.assertEqual(data["token_target"], [50000, 100000])
        self.assertIsNone(data["measured_token_usage"])
        invalid = call("init", "--run", str(self.run.parent / "invalid"), "--topic", "Question", "--budget-min", "100")
        self.assertEqual(invalid.returncode, 2)
        self.assertFalse((self.run.parent / "invalid").exists())

    def test_metadata_hardlink_does_not_overwrite_outside_file(self) -> None:
        outside = self.run.parent / "outside.txt"
        outside.write_text("Synthetic external content")
        os.link(outside, self.run / "verification.json")
        result = call("verify", "--run", str(self.run))
        self.assertEqual(result.returncode, 1)
        self.assertEqual(outside.read_text(), "Synthetic external content")
        self.assertIsInstance(json.loads((self.run / "verification.json").read_text()), dict)

    def test_verification_alias_cannot_destroy_recorded_report(self) -> None:
        for phase in CONFIG["phases"]:
            self.assertEqual(self.record(phase).returncode, 0)
        report = self.run / "deliver.md"
        before = report.read_bytes()
        os.link(report, self.run / "verification.json")
        result = call("verify", "--run", str(self.run))
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(report.read_bytes(), before)
        self.assertIn("hardlink", result.stdout)

    def test_physical_artifact_alias_is_rejected(self) -> None:
        self.assertEqual(self.record("frame").returncode, 0)
        os.link(self.run / "frame.md", self.run / "alias.md")
        result = call("record", "--run", str(self.run), "--phase", "foothold", "--artifact", "alias.md")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(len(json.loads((self.run / "run-state.json").read_text())["receipts"]), 1)

    def test_invalid_state_replaces_stale_pass_with_failure(self) -> None:
        for phase in CONFIG["phases"]:
            self.assertEqual(self.record(phase).returncode, 0)
        self.assertEqual(call("verify", "--run", str(self.run)).returncode, 0)
        state_file = self.run / "run-state.json"
        state = json.loads(state_file.read_text())
        state["receipts"][0].update(status="partial", reason=42)
        state_file.write_text(json.dumps(state))
        result = call("verify", "--run", str(self.run))
        self.assertEqual(result.returncode, 2)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(json.loads((self.run / "verification.json").read_text())["structural_status"], "invalid_state")

    def test_writer_lock_preserves_state_and_status_is_read_only(self) -> None:
        lock = self.run / ".run-control.lock"
        lock.write_text('{"pid":0,"note":"test lock"}')
        before = (self.run / "run-state.json").read_bytes()
        result = self.record("frame")
        self.assertEqual(result.returncode, 2)
        self.assertIn("Writer lock", result.stderr)
        self.assertEqual(before, (self.run / "run-state.json").read_bytes())
        names = sorted(p.name for p in self.run.iterdir())
        self.assertEqual(call("status", "--run", str(self.run)).returncode, 0)
        self.assertEqual(names, sorted(p.name for p in self.run.iterdir()))
        self.assertEqual(before, (self.run / "run-state.json").read_bytes())

    def test_concurrent_writers_cannot_both_record_same_phase(self) -> None:
        (self.run / "frame.md").write_text("Shared fixture")
        argv = [sys.executable, "-B", str(SCRIPT), "record", "--run", str(self.run), "--phase", "frame", "--artifact", "frame.md"]
        processes = [subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for _ in range(2)]
        for process in processes:
            process.communicate(timeout=10)
        self.assertEqual(sorted(p.returncode for p in processes), [0, 2])
        self.assertEqual(len(json.loads((self.run / "run-state.json").read_text())["receipts"]), 1)

    def test_invalid_profile_config_fails_without_creating_run(self) -> None:
        installed = self.run.parent / "installed"
        shutil.copytree(SCRIPT.parent.parent, installed)
        config_path = installed / "assets/depth-profiles.json"
        config = json.loads(config_path.read_text())
        for bad in ("not json", json.dumps({**config, "phases": []}), json.dumps({**config, "profiles": {"deep": {"token_target": [True, 100]}}})):
            config_path.write_text(bad)
            target = self.run.parent / "bad-config-run"
            result = subprocess.run([sys.executable, "-B", str(installed / "scripts/run_control.py"), "init", "--run", str(target), "--topic", "test"], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertNotIn("Traceback", result.stderr)
            self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
