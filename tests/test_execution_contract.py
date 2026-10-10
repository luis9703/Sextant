"""Regressions from the AI-glasses run; fixtures do not evaluate imagination."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_run_control import call, CONFIG, SCRIPT


class ExecutionContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.run = Path(self.temp.name) / "run"
        self.init_output = self.ok("init", "--topic", "Synthetic future question")

    def ok(self, *args):
        result = call(*args, "--run", str(self.run))
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def file(self, name, content="Synthetic retained record\n"):
        path = self.run / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    def recombine(self, partial_research=False):
        for phase in CONFIG["phases"][:5]:
            self.file(phase + ".md")
            extra = ("--status", "partial", "--reason", "Synthetic interrupted research") if partial_research and phase == "research" else ()
            self.ok("record", "--phase", phase, "--artifact", phase + ".md", *extra)

    def review(self, no_issues=True, limited=False, partial_research=False):
        self.recombine(partial_research)
        for kind in ["evolution", "contrast"]:
            self.ok("work-add", "--id", kind, "--kind", kind, "--source", "recombine.md", "--question", "Synthetic work question")
            self.file(kind + ".md")
            self.ok("work-record", "--id", kind, "--artifact", kind + ".md")
        self.file("pathways.md", "Original synthetic availability premise\nOriginal synthetic capture premise\n")
        self.ok("record", "--phase", "pathways", "--artifact", "pathways.md")
        self.file("review.md", "Synthetic issue summary: F1 availability, F2 capture\n")
        extra = ("--no-issues-reason", "No material issues in this synthetic fixture") if no_issues else ()
        if limited:
            extra += ("--reason", "Only the declared subset was reviewed")
        self.ok("record", "--phase", "review", "--artifact", "review.md", "--review-format", "issue_summary",
                "--review-context", "isolated", "--review-coverage", "limited" if limited else "complete", *extra)

    def issue(self, key, kind="material", *extra):
        self.ok("review-add", "--id", key, "--kind", kind, "--question", "Synthetic objection " + key,
                "--source", "review.md", *extra)

    def revised(self):
        self.file("pathways-v2.md", "Conditional availability corrected\nCapture condition corrected\n")
        self.ok("revise", "--phase", "pathways", "--artifact", "pathways-v2.md", "--reason", "Synthetic review corrections")

    def reconciliation(self, content):
        self.file("report.md", "Availability retained as a condition\nCapture retained as a condition\n")
        self.file("notes.md", content)
        return call("record", "--run", str(self.run), "--phase", "reconcile", "--artifact", "notes.md", "--report", "report.md")

    def two_dispositions(self):
        return (
            "[处置 F1: 修改]\nUpdated the availability premise in both targets.\n"
            "[路径摘录 F1](pathways-v2.md#L1)\n> Conditional availability corrected\n"
            "[报告摘录 F1](report.md#L1)\n> Availability retained as a condition\n"
            "[处置 F2: 修改]\nUpdated the capture premise in both targets.\n"
            "[路径摘录 F2](pathways-v2.md#L2)\n> Capture condition corrected\n"
            "[报告摘录 F2](report.md#L2)\n> Capture retained as a condition\n"
        )

    def test_init_and_next_have_contracts_and_resolvable_resources_from_any_cwd(self):
        self.assertEqual(self.init_output["budget"]["meaning"], CONFIG["accounting"])
        self.assertIsNone(self.init_output["budget"]["measured_token_usage"])
        self.assertTrue(self.init_output["contract"]["completion"])
        self.recombine()
        self.ok("work-add", "--id", "e1", "--kind", "evolution", "--source", "recombine.md", "--question", "Question")
        before = (self.run / "run-state.json").read_bytes()
        result = subprocess.run([sys.executable, "-B", str(SCRIPT), "next", "--run", str(self.run)],
                                cwd=self.run.parent, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        value = json.loads(result.stdout)
        self.assertTrue(Path(value["guide"]).is_file())
        self.assertTrue(all(Path(ref).is_file() for ref in value["contract"]["references"]))
        self.assertTrue(Path(value["resources"]["run_control"]).is_file())
        self.assertEqual(value["record_argv"][2], str(SCRIPT))
        self.assertEqual(before, (self.run / "run-state.json").read_bytes())

    def test_plan_work_does_not_return_a_pathway_completion_contract(self):
        self.recombine()
        value = self.ok("next")
        self.assertEqual(value["next"], "plan_work")
        self.assertEqual(value["missing_kinds"], ["evolution", "contrast"])
        self.assertEqual(Path(value["guide"]).name, "development.md")
        self.assertTrue(Path(value["guide"]).is_file())
        self.assertNotIn("contract", value)
        self.assertNotIn("record_argv", value)

    def test_partial_pathways_can_recover_with_an_updated_or_confirmed_synthesis(self):
        for kind in ("update", "confirm"):
            with self.subTest(kind=kind):
                self.run = Path(self.temp.name) / kind
                self.ok("init", "--topic", "Synthetic resumable future question")
                self.recombine()
                self.file("pathways.md", "Original synthetic availability premise\n")
                self.ok("record", "--phase", "pathways", "--artifact", "pathways.md",
                        "--status", "partial", "--reason", "Development work remains")
                historical = json.loads((self.run / "run-state.json").read_text())["receipts"][-1]
                original = (self.run / "pathways.md").read_bytes()
                self.file("review.md")
                self.ok("record", "--phase", "review", "--artifact", "review.md", "--review-format", "issue_summary",
                        "--review-context", "isolated", "--review-coverage", "complete",
                        "--no-issues-reason", "Synthetic review with no material issues")
                self.ok("revise", "--phase", "pathways", "--confirm", "--reason", "Current limited draft retained")
                self.assertEqual(self.ok("status")["partial_phases"], ["pathways"])
                value = self.ok("next")
                self.assertEqual(value["next"], "plan_work")
                self.assertNotIn("contract", value)
                for work_kind in ("evolution", "contrast"):
                    self.ok("work-add", "--id", work_kind, "--kind", work_kind, "--source", "recombine.md",
                            "--question", "Synthetic recovery question")
                    self.file(work_kind + ".md")
                    self.ok("work-record", "--id", work_kind, "--artifact", work_kind + ".md")
                self.ok("work-add", "--id", "followup", "--kind", "evolution", "--source", "pathways.md",
                        "--question", "Synthetic follow-up remains")
                self.ok("revise", "--phase", "pathways", "--confirm", "--reason", "Follow-up is still pending")
                self.assertEqual(self.ok("status")["partial_phases"], ["pathways"])
                self.file("followup.md")
                self.ok("work-record", "--id", "followup", "--artifact", "followup.md")
                self.assertEqual(self.ok("status")["partial_phases"], ["pathways"])
                self.assertEqual(self.ok("next")["next"], "refresh_pathways")
                if kind == "update":
                    self.revised()
                else:
                    self.ok("revise", "--phase", "pathways", "--confirm", "--reason", "Completed work supports the retained synthesis")
                value = self.ok("status")
                self.assertEqual(value["partial_phases"], [])
                self.assertEqual(value["superseded_partial_phases"], ["pathways"])
                result = self.reconciliation("[报告摘录](report.md#L1)\n> Availability retained as a condition\n")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.ok("record", "--phase", "deliver", "--artifact", "report.md")
                self.assertEqual(self.ok("verify")["structural_status"], "pass")
                self.assertEqual(self.ok("next")["next"], "recorded_complete")
                state = json.loads((self.run / "run-state.json").read_text())
                self.assertEqual(state["receipts"][5], historical)
                self.assertEqual((self.run / "pathways.md").read_bytes(), original)

    def test_partial_research_requires_explicit_completion_and_preserves_history(self):
        for kind in ("update", "confirm"):
            with self.subTest(kind=kind):
                self.run = Path(self.temp.name) / ("research-" + kind)
                self.ok("init", "--topic", "Synthetic resumable research")
                self.review(partial_research=True)
                state = json.loads((self.run / "run-state.json").read_text())
                historical = state["receipts"][3]
                original = (self.run / "research.md").read_bytes()
                self.file("research-v2.md", "Synthetic completed research with remaining future conditions\n")
                self.ok("revise", "--phase", "research", "--artifact", "research-v2.md", "--reason", "More material, no completion declaration yet")
                self.assertEqual(self.ok("status")["partial_phases"], ["research"])
                before = (self.run / "run-state.json").read_bytes()
                option = self.ok("next")["resume_options"][0]
                self.assertEqual(option["phase"], "research")
                self.assertIn("--complete", option["complete_argv"])
                self.assertTrue(all(Path(ref).is_file() for ref in option["contract"]["references"]))
                self.assertEqual(before, (self.run / "run-state.json").read_bytes())
                self.ok("revise", "--phase", "pathways", "--confirm", "--reason", "Synthetic current conditional synthesis")
                if kind == "update":
                    self.file("research-v3.md", "Synthetic actually finished research\n")
                    args = ("--artifact", "research-v3.md")
                else:
                    args = ("--confirm",)
                self.ok("revise", "--phase", "research", *args, "--complete", "--reason", "Actual fixture phase work completed; futures remain conditional")
                status = self.ok("status")
                self.assertEqual(status["partial_phases"], [])
                self.assertEqual(status["superseded_partial_phases"], ["research"])
                self.assertEqual(self.ok("next")["next"], "refresh_pathways")
                self.ok("revise", "--phase", "pathways", "--confirm", "--reason", "Rechecked after upstream completion")
                result = self.reconciliation("[报告摘录](report.md#L1)\n> Availability retained as a condition\n")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.ok("record", "--phase", "deliver", "--artifact", "report.md")
                self.assertEqual(self.ok("verify")["structural_status"], "pass")
                saved = json.loads((self.run / "run-state.json").read_text())
                self.assertEqual(saved["receipts"][3], historical)
                self.assertEqual((self.run / "research.md").read_bytes(), original)
                index = (self.run / "00-current.md").read_text()
                self.assertIn("research：partial", index)
                self.assertIn("已更新的阶段材料", index)
                self.assertIn("research：版本3，done", index)

    def test_completion_does_not_clear_other_partial_phases_or_pending_work(self):
        self.recombine(partial_research=True)
        self.ok("work-add", "--id", "pending", "--kind", "evolution", "--source", "recombine.md", "--question", "Synthetic unfinished evolution")
        self.file("pathways.md")
        self.ok("record", "--phase", "pathways", "--artifact", "pathways.md", "--status", "partial", "--reason", "Work pending")
        self.ok("revise", "--phase", "research", "--confirm", "--complete", "--reason", "Research completed, development not completed")
        value = self.ok("status")
        self.assertEqual(value["partial_phases"], ["pathways"])
        self.assertEqual(value["development_work"]["pending_ids"], ["pending"])
        self.assertEqual(value["execution_status"], "incomplete")

    def test_old_revision_without_status_does_not_claim_research_completion(self):
        self.recombine(partial_research=True)
        self.file("research-v2.md")
        self.ok("revise", "--phase", "research", "--artifact", "research-v2.md", "--reason", "Synthetic legacy document update")
        path = self.run / "run-state.json"
        state = json.loads(path.read_text())
        del state["revisions"][0]["status"]
        path.write_text(json.dumps(state))
        value = self.ok("status")
        self.assertEqual(value["partial_phases"], ["research"])
        self.assertEqual(value["current_versions"]["research"]["status"], "partial")

    def test_invalid_completion_status_and_post_reconciliation_changes_are_rejected(self):
        self.recombine(partial_research=True)
        self.ok("revise", "--phase", "research", "--confirm", "--complete", "--reason", "Synthetic actual completion")
        path = self.run / "run-state.json"
        state = json.loads(path.read_text())
        state["revisions"][0]["status"] = ["done"]
        path.write_text(json.dumps(state))
        invalid = call("status", "--run", str(self.run))
        self.assertEqual(invalid.returncode, 2)
        self.assertIn("Invalid revision completion status", invalid.stderr)
        self.run = Path(self.temp.name) / "frozen"
        self.ok("init", "--topic", "Synthetic frozen reconciliation")
        self.review()
        self.ok("revise", "--phase", "pathways", "--confirm", "--reason", "Synthetic retained synthesis")
        result = self.reconciliation("[报告摘录](report.md#L1)\n> Availability retained as a condition\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        before = (self.run / "run-state.json").read_bytes()
        rejected = call("revise", "--run", str(self.run), "--phase", "research", "--confirm", "--complete", "--reason", "Too late")
        self.assertEqual(rejected.returncode, 2)
        self.assertIn("Reconciliation is frozen", rejected.stderr)
        self.assertEqual(before, (self.run / "run-state.json").read_bytes())

    def test_preexisting_result_requires_explicit_adoption(self):
        self.recombine()
        self.file("existing.md", "Already performed exploration\n")
        self.ok("work-add", "--id", "e1", "--kind", "evolution", "--source", "recombine.md", "--question", "Question")
        before = (self.run / "run-state.json").read_bytes()
        rejected = call("work-record", "--run", str(self.run), "--id", "e1", "--artifact", "existing.md")
        self.assertEqual(rejected.returncode, 2)
        self.assertEqual(before, (self.run / "run-state.json").read_bytes())
        self.ok("work-record", "--id", "e1", "--artifact", "existing.md", "--adopt-existing", "--reason", "Adopted actual earlier exploration, not a new pass")
        state = json.loads((self.run / "run-state.json").read_text())
        self.assertEqual(state["work"][0]["results"][0]["origin"], "adopted")
        self.assertEqual(self.ok("status")["development_work"]["adopted_ids"], ["e1"])

    def test_prior_phase_work_can_be_adopted_without_repeating_it(self):
        self.recombine()
        self.ok("work-add", "--id", "e1", "--kind", "evolution", "--source", "recombine.md", "--question", "Reuse earlier work")
        self.ok("work-record", "--id", "e1", "--artifact", "recombine.md", "--adopt-existing", "--reason", "Earlier fixture already contains the required operation")
        self.assertEqual(self.ok("status")["artifact_errors"], [])

    def test_one_generic_quote_cannot_close_two_registered_issues(self):
        self.review(no_issues=False)
        self.issue("F1")
        self.issue("F2")
        self.revised()
        result = self.reconciliation("[Report excerpt](report.md#L1)\n> Availability retained as a condition\n")
        self.assertEqual(result.returncode, 2)
        self.assertIn("explicit issue id", result.stderr)
        content = self.two_dispositions().split("[处置 F2:")[0]
        result = self.reconciliation(content)
        self.assertEqual(result.returncode, 2)
        self.assertIn("F2", result.stderr)
        result = self.reconciliation(self.two_dispositions())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.ok("record", "--phase", "deliver", "--artifact", "report.md")
        checked = self.ok("verify")
        self.assertEqual(checked["structural_status"], "pass")
        self.assertEqual(len(checked["issue_coverage"]["dispositions"]), 2)
        self.assertNotIn("excerpts", checked["issue_coverage"])
        self.assertEqual(len(checked["issue_coverage"]["excerpt_locations"]), 4)
        self.assertEqual(checked["issue_coverage"]["details_in"], ["notes.md"])

    def test_unnumbered_excerpts_do_not_inherit_the_previous_disposition(self):
        self.review(no_issues=False)
        self.issue("F1")
        self.issue("F2")
        self.revised()
        before = (self.run / "run-state.json").read_bytes()
        content = self.two_dispositions().split("[处置 F2:")[0] + (
            "[处置 F2: 保留]\nThe capture condition remains unresolved in this fixture.\n"
            "[报告摘录](report.md#L1)\n> a\n"
            "[路径摘录](pathways-v2.md#L1)\n> c\n"
        )
        result = self.reconciliation(content)
        self.assertEqual(result.returncode, 2)
        self.assertIn("explicit issue id", result.stderr)
        self.assertEqual(before, (self.run / "run-state.json").read_bytes())

    def test_excerpts_must_use_registered_ids_and_cannot_cover_another_issue(self):
        self.review(no_issues=False)
        self.issue("F1")
        self.issue("F2")
        self.revised()
        content = self.two_dispositions()
        result = self.reconciliation(content.replace("摘录 F2]", "摘录 F3]"))
        self.assertEqual(result.returncode, 2)
        self.assertIn("unregistered issue id", result.stderr)
        result = self.reconciliation(content.replace("摘录 F2]", "摘录 F1]"))
        self.assertEqual(result.returncode, 2)
        self.assertIn("Issue F2 needs an excerpt", result.stderr)
        # Correct ids and literal positions do not certify repair adequacy or
        # impose a minimum excerpt length, even for a one-character substring.
        result = self.reconciliation(content.replace("> Capture retained as a condition", "> a").replace("> Capture condition corrected", "> c"))
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_updated_synthesis_is_current_and_old_bytes_are_preserved(self):
        self.review()
        original = (self.run / "pathways.md").read_bytes()
        self.revised()
        self.assertEqual((self.run / "pathways.md").read_bytes(), original)
        value = self.ok("status")
        self.assertEqual(value["current_versions"]["pathways"]["artifacts"][0]["path"], "pathways-v2.md")
        index = (self.run / "00-current.md").read_text()
        self.assertIn("pathways-v2.md", index)
        self.assertIn("版本1，审查前草稿", index)
        self.assertEqual(self.ok("next")["phase"], "reconcile")

    def test_report_only_repair_does_not_satisfy_pathway_target(self):
        self.review(no_issues=False)
        self.issue("F1")
        self.revised()
        result = self.reconciliation("[处置 F1: 修改]\nUpdated only the report.\n[报告摘录 F1](report.md#L1)\n> Availability retained as a condition\n")
        self.assertEqual(result.returncode, 2)
        self.assertIn("pathways", result.stderr)

    def test_accepted_change_cannot_keep_an_unchanged_synthesis(self):
        self.review(no_issues=False)
        self.issue("F1")
        self.ok("revise", "--phase", "pathways", "--confirm", "--reason", "Kept the old premise")
        result = self.reconciliation("[处置 F1: 修改]\nCorrected only the reader report.\n[报告摘录 F1](report.md#L1)\n> Availability retained as a condition\n[路径摘录 F1](pathways.md#L1)\n> Original synthetic availability premise\n")
        self.assertEqual(result.returncode, 2)
        self.assertIn("updated synthesis", result.stderr)

    def test_new_work_after_checkpoint_requests_a_new_synthesis_check(self):
        self.review()
        self.ok("revise", "--phase", "pathways", "--confirm", "--reason", "Original remains valid")
        self.ok("work-add", "--id", "e2", "--kind", "evolution", "--source", "pathways.md", "--question", "A new important question")
        self.file("e2.md")
        self.ok("work-record", "--id", "e2", "--artifact", "e2.md")
        self.assertEqual(self.ok("next")["next"], "refresh_pathways")

    def test_unused_lead_and_unresolved_issue_are_not_unperformed_review(self):
        self.review(no_issues=False, limited=True)
        self.issue("F1")
        self.issue("L1", "lead")
        self.revised()
        content = (
            "[处置 F1: 未决]\nThe premise remains a visible condition in both targets.\n"
            "[报告摘录 F1](report.md#L1)\n> Availability retained as a condition\n"
            "[路径摘录 F1](pathways-v2.md#L1)\n> Conditional availability corrected\n"
            "[处置 L1: 不采用]\nPeripheral lead was not used by any dependent claim.\n"
        )
        result = self.reconciliation(content)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.ok("record", "--phase", "deliver", "--artifact", "report.md")
        checked = self.ok("verify")
        self.assertEqual(checked["structural_status"], "pass")
        self.assertEqual(checked["review_record"]["format"], "issue_summary")
        self.assertEqual(checked["review_record"]["coverage"], "limited")
        self.assertEqual(checked["issue_coverage"]["unresolved_ids"], ["F1"])
        self.assertEqual(checked["issue_coverage"]["not_used_ids"], ["L1"])

    def test_no_issues_requires_an_explicit_declaration(self):
        self.review(no_issues=False)
        self.ok("revise", "--phase", "pathways", "--confirm", "--reason", "No changes found")
        result = self.reconciliation("[Report excerpt](report.md#L1)\n> Availability retained as a condition\n")
        self.assertEqual(result.returncode, 2)
        self.assertIn("no-issues-reason", result.stderr)

    def test_actual_missing_work_and_corruption_have_different_statuses(self):
        before = self.ok("status")
        self.assertEqual(before["structural_status"], "incomplete")
        self.assertEqual(before["integrity_status"], "pass")
        self.recombine()
        self.file("frame.md", "Changed historical input")
        after = self.ok("status")
        self.assertEqual(after["structural_status"], "invalid")
        self.assertEqual(after["integrity_status"], "invalid")

    def test_confirming_a_synthesis_does_not_certify_its_content(self):
        self.review()
        self.ok("revise", "--phase", "pathways", "--confirm", "--reason", "Synthetic unchanged premise")
        result = self.reconciliation("[报告摘录](report.md#L1)\n> Availability retained as a condition\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.ok("record", "--phase", "deliver", "--artifact", "report.md")
        value = self.ok("verify")
        self.assertEqual(value["structural_status"], "pass")
        self.assertIn("adequacy unverified", value["issue_coverage"]["semantic_status"])

    def test_registered_keep_can_complete_with_an_unchanged_synthesis(self):
        self.review(no_issues=False)
        self.issue("F1")
        original = (self.run / "pathways.md").read_bytes()
        self.ok("revise", "--phase", "pathways", "--confirm", "--reason", "Review objection was considered; current premise retained")
        content = (
            "[处置 F1: 保留]\nThe objection was considered; this conditional account is retained.\n"
            "[路径摘录 F1](pathways.md#L1)\n> Original synthetic availability premise\n"
            "[报告摘录 F1](report.md#L1)\n> Availability retained as a condition\n"
        )
        result = self.reconciliation(content)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.ok("record", "--phase", "deliver", "--artifact", "report.md")
        value = self.ok("verify")
        self.assertEqual(value["structural_status"], "pass")
        self.assertEqual(value["issue_coverage"]["dispositions"], [{"id": "F1", "action": "keep"}])
        self.assertEqual((self.run / "pathways.md").read_bytes(), original)

    def test_new_reviewed_document_can_serve_as_both_synthesis_and_report(self):
        self.review(no_issues=False)
        self.issue("F1")
        self.file("combined.md", "Corrected synthesis and reader report\n")
        self.ok("revise", "--phase", "pathways", "--artifact", "combined.md", "--reason", "Integrated corrected pathways into the reader document")
        self.file("notes.md", "[处置 F1: 修改]\nBoth roles use this corrected current document.\n[报告摘录 F1](combined.md#L1)\n> Corrected synthesis and reader report\n[路径摘录 F1](combined.md#L1)\n> Corrected synthesis and reader report\n")
        self.ok("record", "--phase", "reconcile", "--artifact", "notes.md", "--report", "combined.md")
        self.ok("record", "--phase", "deliver", "--artifact", "combined.md")
        self.assertEqual(self.ok("verify")["structural_status"], "pass")

    def test_claim_sweep_and_ledger_tables_travel_with_reconciliation(self):
        # The sweep and ledger check are plain tables. Disposition markers stay
        # reserved for registered review issues, so a ledger row cannot use one.
        self.review(no_issues=False)
        self.issue("F1")
        self.revised()
        self.file("report.md", "Availability retained as a condition\nCapture retained as a condition\n")
        self.file("notes.md", self.two_dispositions().split("[处置 F2:")[0])
        self.file("ledger-markers.md", "[处置 C8: 保留]\nSynthetic set-aside core.\n")
        before = (self.run / "run-state.json").read_bytes()
        rejected = call("record", "--run", str(self.run), "--phase", "reconcile", "--artifact", "notes.md",
                        "--artifact", "ledger-markers.md", "--report", "report.md")
        self.assertEqual(rejected.returncode, 2)
        self.assertIn("unknown or duplicate issue id: C8", rejected.stderr)
        self.assertEqual(before, (self.run / "run-state.json").read_bytes())
        self.file("claim-sweep.md", (
            "| Line | Statement | Source | Period and edition | What it measures | Read status | Action |\n"
            "| --- | --- | --- | --- | --- | --- | --- |\n"
            "| report.md#L1 | Synthetic availability | synthetic source | synthetic period | synthetic measure | full text | kept |\n"
            "\n| Candidate | Quoted core | State | Location |\n| --- | --- | --- | --- |\n"
            "| C8 | Synthetic set-aside core | set aside: synthetic reason | none |\n"))
        self.ok("record", "--phase", "reconcile", "--artifact", "notes.md", "--artifact", "claim-sweep.md", "--report", "report.md")
        self.ok("record", "--phase", "deliver", "--artifact", "report.md")
        checked = self.ok("verify")
        self.assertEqual(checked["structural_status"], "pass")
        self.assertEqual(checked["issue_coverage"]["details_in"], ["notes.md", "claim-sweep.md"])
        self.assertEqual(checked["issue_coverage"]["dispositions"], [{"id": "F1", "action": "revise"}])
