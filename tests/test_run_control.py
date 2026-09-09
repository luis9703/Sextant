"""Behavioral checks for phase order, artifact integrity and honest partial status."""
from __future__ import annotations

import json
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
        (self.run / name).write_text(f"Synthetic fixture for {phase}; not a real evaluation.\n")
        return call("record", "--run", str(self.run), "--phase", phase, "--artifact", name, *extra)

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
