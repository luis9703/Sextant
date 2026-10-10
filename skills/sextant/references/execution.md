# Executing, revising and reading a run

Default to deep for a future-imagination request. An explicit short request selects brief. Resource exhaustion leaves performed work and specific remaining work visible; it does not silently change the profile. A missing historical precedent is not unperformed imagination.

## Resolve the actual installed unit

The host already knows the SKILL.md it loaded. Its sibling scripts/run_control.py is the entry point. The following examples are explicitly from this repository's root:

```sh
python3 -B skills/sextant/scripts/run_control.py init --run /path/to/new-case --topic "The user's future question"
python3 -B skills/sextant/scripts/run_control.py next --run /path/to/new-case
```

In an installed copy, use that copy's absolute script path. Do not assume the caller's current directory is the Skill root. init and next return the resolved script, Skill root, reference paths, completion criteria, input snapshots and record argument template. Substantive content stays in Markdown. The machine-readable [execution contract](../assets/execution-contract.json) is the source of phase goals and completion criteria; methodological details remain in the linked references. Paths in saved state remain relative; absolute runtime paths appear only in tool output.

When next returns plan_work, it lists the missing work kinds and resolves development.md. It does not attach the later phase's completion contract or ask for a synthesis before the work is done.

The obligations remain frame → foothold → diverge → research → recombine → pathways → review → reconcile → deliver. pathways means a **pre-review synthesis**, not an approved final world. Read [research.md](research.md) for the narrower foothold intake and incidental-exposure policy; broad topical research follows the initial divergence. Read [development.md](development.md) after recombination.

Authorized independent explorations can use [selected input packets](independent-exploration.md) before merging candidates. The packet helper copies only requested inputs, preserves their snapshots, and leaves phase state unchanged. For a ready work item, next provides packet_argv using its inputs and completed dependencies; the host decides whether to dispatch it. This is optional context support, not an extra phase or closure condition.

## Work and its provenance

The existing queue keeps questions, inputs, dependencies and result attempts. Default work-record requires a result file not present when the question was registered. A file already written can be adopted with --adopt-existing and a reason; its origin is recorded as adopted. This permits genuine earlier work to be used once, without relabelling it as a new post-question or post-review pass. A copied file newly appearing after registration still does not prove new reasoning. The checker observes file lineage and declared execution, not cognition or semantic adequacy.

Partial attempts can resume with new files, and finished jobs can have dependent follow-ups. The two required work kinds for deep/extensive are minimum process coverage. They are not counts of worlds or a quality score. Do not repeat an ordinary-event exercise once in imagination and again merely for the queue: register before doing it, or adopt the existing work transparently, then deepen a consequential gap.

## Keep history and update the current synthesis

Recorded artifacts remain immutable history. A revision appends a new file and changes the current pointer, without replacing the old receipt. After review and any new work, update the pathway synthesis; if it truly remains valid, explicitly confirm it with a reason. From the repository root:

```sh
python3 -B skills/sextant/scripts/run_control.py revise --run /path/to/case --phase pathways --artifact 06-pathways-v2.md --reason "The review changed a material premise and its dependent paths"
```

For checked unchanged content, use revise --phase pathways --confirm --reason instead. Confirmation does not perform a correction. Accepted changes that affect pathways need a changed version. The tool's next action requests a refresh if upstream versions, material issues or development results changed since the checkpoint. Other recorded early phases can also be revised with new files.

00-current.md is the reader's entry point. It identifies the latest pathway version, bound report and historical versions. Phase completion refers to the work performed at that point in history. Reconciliation binds the current synthesis and report; once bound, later changes need a linked new run. Older cases use their matching frozen Skill and retain their original status.

An early partial pathways receipt remains in history. Once required and pending work is finished and the current synthesis is updated or confirmed after review against those results, that historical partial no longer blocks completion. The helper reports it in superseded_partial_phases; partial_phases lists remaining incomplete phases. A stale synthesis checkpoint, unfinished work or a partial in another phase still leaves the run incomplete. This records recovery, not semantic approval of the synthesis.

For an interrupted revisable upstream phase (frame, foothold, diverge, research or recombine), preserve the partial receipt and finish the actual remaining work. Append its completed material using revise --complete; if the saved current material already covers the completed work, use --confirm --complete with a concrete reason. A document revision without --complete inherits the current completion status and does not clear a partial. next includes resume_options with the original phase contract and resolved arguments; they are recovery options, not a rule to halt useful conditional work when a source remains unavailable. A coordination checkpoint can simply save working files without closing an unfinished phase.

```sh
python3 -B skills/sextant/scripts/run_control.py revise --run /path/to/case --phase research --artifact 04-research-v2.md --complete --reason "Finished the interrupted research; remaining future assumptions are explicit"
```

The old receipt and files stay unchanged, and 00-current.md points to the current phase material and completion declaration. Changes to upstream status invalidate an earlier pathway checkpoint, so recheck its current synthesis before reconciliation. This declaration concerns performed work, not source certainty or imagined-future validity. Pathways keep their existing work and review conditions; review, reconciliation and delivery cannot be completed through this document revision option. Reconciliation remains frozen, and older contracts require their matching Skill rather than an implicit state upgrade.

## Record a performed review in its actual form

Read [review-and-updates.md](review-and-updates.md). A full reply or a faithful issue summary can record a performed review. Declare representation, actual context and coverage; summary length alone is not grounds for partial. Limited or same-context review needs a concrete reason. Unavailable review is unperformed and remains partial.

```sh
python3 -B skills/sextant/scripts/run_control.py record --run /path/to/case --phase review --artifact 07-review-summary.md --review-format issue_summary --review-context isolated --review-coverage complete
python3 -B skills/sextant/scripts/run_control.py review-add --run /path/to/case --id F1 --source 07-review-summary.md --question "A material premise and its dependent claim require correction"
```

Material issues affect both pathways and report by default; narrow targets explicitly with --target when only one is affected. Peripheral proposed material can be registered as --kind lead with no default targets. Do not create an issue for every citation: record consequential objections, and group unused peripheral leads when appropriate. If the review raised no material issue, give --no-issues-reason on the review or reconciliation receipt. This is a declaration to audit, not proof that nothing was missed.

## Reconcile issue by issue

Complete the current synthesis and reader-facing report first. Sweep the report's present-day claims and read the candidate ledger against the finished files as described in [review-and-updates.md](review-and-updates.md); make any resulting edits before collecting locators. Re-open saved files with line numbers. In the disposition note, associate every registered id with an action, rationale and literal excerpts for its affected targets. See the bilingual marker syntax in [review-and-updates.md](review-and-updates.md). revise, keep, drop and unresolved need target excerpts; not_used needs a reason but no invented report passage. Unresolved future conditions can be addressed honestly without becoming unperformed work.

```sh
python3 -B skills/sextant/scripts/run_control.py record --run /path/to/case --phase reconcile --artifact 08-reconcile.md --artifact 08-claim-sweep.md --report report.md
python3 -B skills/sextant/scripts/run_control.py record --run /path/to/case --phase deliver --artifact report.md
python3 -B skills/sextant/scripts/run_control.py verify --run /path/to/case
```

The first current pathway artifact is the default synthesis; --pathways can select another artifact in that current version. The helper binds both synthesis and report, checks all labelled literal positions and requires dispositions for every registered issue. It can reject a missing F2 despite a valid F1 excerpt. It cannot detect an unregistered objection or decide whether the cited passage truly resolves it. Check semantic coverage of the actual review, lead, dependent paths and observations before declaring completion.

The claim sweep and ledger check are plain tables; here they travel in 08-claim-sweep.md with the same receipt. Only disposition and excerpt markers are parsed.

Partial reconciliation may retain useful work with a reason. Finished report bytes are delivered unchanged. verify writes verification.json separately; do not edit the bound report to insert a pass message.

## Interpret statuses and resources

integrity_status concerns saved bytes and contract consistency. execution_status concerns recorded obligations and unfinished work. review_record states format, context and declared coverage. issue_coverage states recorded dispositions, including unresolved and unused items. structural_status is pass, incomplete or invalid; valid unfinished work is not corrupt work. None of these is expert approval, creativity evaluation or forecast performance.

Resource targets in [depth-profiles.json](../assets/depth-profiles.json) are provisional planning envelopes, not measured usage, caps or minimum spend. init, next and status include their accounting meaning. Host telemetry is required for actual input, output, cache and reasoning counters; absent counters remain unknown. Additional capacity follows questions that can change the futures, not repetition or citation volume.

State and current-index writes use atomic replacement; writers serialize through .run-control.lock. Inspect a crashed owner's process before removing its lock. status and next are read-only. Symlink escapes and hardlink artifact aliases are rejected. Verification fingerprints identify a snapshot, not deliberate-tampering protection or power-loss durability. Invalid state clears cached verification success.

Without Python, keep the same version pointers, issue dispositions and work origins in Markdown and label runtime checking unavailable. The host provides actual model and source tools; the Skill cannot force a host that bypasses them. Preserve concise evidence, results and decisions rather than private chain-of-thought.
