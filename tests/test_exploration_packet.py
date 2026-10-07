"""Input-scope regressions for optional host dispatch, not creativity tests."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_run_control import call, CONFIG, SCRIPT

PACKET = SCRIPT.with_name("exploration_packet.py")


class ExplorationPacketTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.run = Path(self.temp.name) / "case"
        self.ok("init", "--topic", "Synthetic future question")

    def ok(self, *args):
        result = call(*args, "--run", str(self.run))
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def file(self, name, content):
        path = self.run / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    def packet(self, *args):
        return subprocess.run([sys.executable, "-B", str(PACKET), "--run", str(self.run), *args],
                              cwd=self.run.parent, capture_output=True, text=True)

    def test_only_selected_inputs_are_copied_and_phase_state_is_unchanged(self):
        self.file("notes/seed facts.md", "Neutral ability and unverified condition\n")
        self.file("main-draft.md", "A preferred future the explorer must not receive\n")
        before = (self.run / "run-state.json").read_bytes()
        result = self.packet("--source", "notes/seed facts.md", "--question", "What new activity?\nA literal $(expression)",
                             "--out", "exploration/activity")
        self.assertEqual(result.returncode, 0, result.stderr)
        value = json.loads(result.stdout)
        packet = Path(value["packet"])
        manifest = json.loads(Path(value["manifest"]).read_text())
        self.assertEqual(manifest["inputs"][0]["path"], "notes/seed facts.md")
        copied = packet / manifest["inputs"][0]["packet_path"]
        self.assertEqual(copied.read_bytes(), (self.run / "notes/seed facts.md").read_bytes())
        self.assertEqual(hashlib.sha256(copied.read_bytes()).hexdigest(), manifest["inputs"][0]["sha256"])
        self.assertEqual([p.relative_to(packet / "inputs").as_posix() for p in (packet / "inputs").rglob("*") if p.is_file()], ["notes/seed facts.md"])
        self.assertIn("inputs/notes/seed%20facts.md", Path(value["task"]).read_text())
        self.assertIn("$(expression)", manifest["question"])
        self.assertTrue((packet / "method.md").is_file())
        self.assertFalse((packet / "run-state.json").exists())
        self.assertEqual(before, (self.run / "run-state.json").read_bytes())

    def test_work_argument_template_uses_inputs_and_completed_dependencies_only(self):
        for phase in CONFIG["phases"][:5]:
            self.file(phase + ".md", "Unselected main history")
            self.ok("record", "--phase", phase, "--artifact", phase + ".md")
        self.file("neutral.md", "Selected neutral input")
        self.ok("work-add", "--id", "e1", "--kind", "evolution", "--source", "neutral.md", "--question", "Parent question")
        self.file("parent-result.md", "Completed dependency result")
        self.ok("work-record", "--id", "e1", "--artifact", "parent-result.md")
        self.ok("work-add", "--id", "c1", "--kind", "contrast", "--source", "neutral.md", "--after", "e1",
                "--question", "A specific comparison question")
        action = self.ok("next")
        argv = [value if value != "<new-packet-directory>" else "exploration/comparison" for value in action["packet_argv"]]
        result = subprocess.run(argv, cwd=self.run.parent, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        manifest = json.loads(Path(json.loads(result.stdout)["manifest"]).read_text())
        self.assertEqual([item["path"] for item in manifest["inputs"]], ["neutral.md", "parent-result.md"])
        self.assertEqual(manifest["question"], "A specific comparison question")
        self.assertEqual(self.ok("next")["id"], "c1")

    def test_cannot_overwrite_a_packet_or_create_one_without_a_question(self):
        self.file("seed.md", "Seed")
        args = ("--source", "seed.md", "--question", "Question", "--out", "packet")
        first = self.packet(*args)
        self.assertEqual(first.returncode, 0, first.stderr)
        original = (self.run / "packet/TASK.md").read_bytes()
        second = self.packet(*args)
        self.assertEqual(second.returncode, 2)
        self.assertEqual((self.run / "packet/TASK.md").read_bytes(), original)
        empty = self.packet("--source", "seed.md", "--question", " ", "--out", "empty")
        self.assertEqual(empty.returncode, 2)
        self.assertFalse((self.run / "empty").exists())

    def test_selected_inputs_and_output_stay_in_the_run(self):
        self.file("seed.md", "Seed")
        outside = self.run.parent / "outside.md"
        outside.write_text("Outside source")
        os.symlink(outside, self.run / "escape.md")
        os.symlink(self.run.parent, self.run / "escape-dir")
        for source, output in (("../outside.md", "bad1"), ("escape.md", "bad2"),
                               ("seed.md", "../bad3"), ("seed.md", "escape-dir/bad4")):
            with self.subTest(source=source, output=output):
                result = self.packet("--source", source, "--question", "Question", "--out", output)
                self.assertEqual(result.returncode, 2)
        self.assertFalse((self.run.parent / "bad3").exists())
        self.assertFalse((self.run.parent / "bad4").exists())

    def test_process_metadata_and_hardlink_aliases_are_not_dispatch_inputs(self):
        outside = self.run.parent / "alias-source.md"
        outside.write_text("Aliased source")
        os.link(outside, self.run / "alias.md")
        before = (self.run / "run-state.json").read_bytes()
        for source in ("run-state.json", "alias.md"):
            with self.subTest(source=source):
                result = self.packet("--source", source, "--question", "Question", "--out", "bad-packet")
                self.assertEqual(result.returncode, 2)
                self.assertFalse((self.run / "bad-packet").exists())
        self.assertEqual(before, (self.run / "run-state.json").read_bytes())

    def test_packet_export_respects_an_active_run_writer(self):
        self.file("seed.md", "Seed")
        self.file(".run-control.lock", "Another active writer")
        result = self.packet("--source", "seed.md", "--question", "Question", "--out", "packet")
        self.assertEqual(result.returncode, 2)
        self.assertIn("Writer lock", result.stderr)
        self.assertTrue((self.run / ".run-control.lock").exists())
        self.assertFalse((self.run / "packet").exists())
