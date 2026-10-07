# Full-depth execution and honest completion

The default is `deep`, including when the user says “imagine” or “想象一下”. Only an explicit request for a short sketch selects `brief`. A limit, tool failure or exhausted context creates a partial deep run, not an unannounced switch to brief. An update follows the same obligations for affected parts, with references to preserved earlier work.

Read the [profiles](../assets/depth-profiles.json) when planning resources. Provisional defaults are 50,000–100,000 run-wide tokens for deep and 100,000–200,000 for extensive. They are editable engineering starting points, not empirically optimal allocations; set a profile target to null to disable it. No minimum token expenditure is required for completion. A user-specified target overrides the default at initialization. If usage is unavailable, report unknown rather than estimating from answer length. Do not count repeated context or cached input as independent new reasoning. Different providers expose different counters; never add nested reasoning or cached counters twice.

Make generation, recombination and pathway development the primary use of discretionary effort: capability migration, unfamiliar complements, changing wants and consequential branches. Research and review serve those explorations. Stop or narrow source work when it no longer changes meaningful possibilities; keep process records concise rather than repeatedly paraphrasing candidates. A missing future precedent does not make an imagination phase incomplete. If necessary present-day verification cannot be completed, mark that specific limit while preserving useful conditional exploration.

**Nine obligations, open-ended content.** Phases describe work and evidence of work, not prescribed headings or a fixed number of future worlds. A meaningful artifact may be concise; its length alone does not satisfy a phase.

| Phase | Work to retain | Completion question |
| --- | --- | --- |
| frame | User's seed, intended imagination, scope, profile, resource plan and assumptions | Is this still the user's future-world question, rather than a replacement research or investment task? |
| foothold | Minimal current premises with source or unverified status, units and ambiguities | Can the initial imagination distinguish a known capability from an assumption? |
| diverge | Candidates saved before the broad survey, spanning different mechanisms and human experiences | Did exploration reach beyond variations of the obvious answer? |
| research | Key sources, counterevidence, unfamiliar enabling material, closest prior accounts | Did research both challenge and expand the material available for imagination? |
| recombine | New, replaced and refined candidates with the material that motivated the change | What dependency or actor response changed, and what consequence makes this more than a renamed or better-qualified candidate? |
| pathways | Development work results and their synthesis: changes to life, conditional actor choices, relationships, institutions and feedback | What happens after enabling conditions hold, who responds differently, and what changes the resulting path? |
| review | Neutral packet plus actual grounding and creative review; or an explicit inability record | Were numbers, dependencies, pruned possibilities and discriminating observations checked? |
| reconcile | Completed report draft, re-read before dispositions cite actual lines and repair excerpts; a report snapshot when using the helper | Do the saved report's lead, conditions and observations substantiate the dispositions? |
| deliver | Reader-facing report plus observed verification and resource status | Can the user see the futures, their conditions, what changed, and what remains uncertain? |

For deep/extensive work, retain phase artifacts such as `01-frame.md` through `08-reconcile.md` and `report.md`. Names are flexible. Early artifacts are historical records: append corrections in later files or new versions rather than rewriting them after the fact. Keep source notes and candidate summaries, not private chain-of-thought. The review phase uses a separate packet and actual review where available.

After recombination and before recording pathways, use the [development workbench](development.md). The helper stores questions, saved inputs, dependencies and result attempts inside the existing run state; substantive work stays in Markdown. `work-add`, `next` and `work-record` support additional passes and review-driven follow-ups. Deep/extensive require completed evolution and contrast work, with no pending jobs, for pathways and reconciliation to be recorded as done. These requirements are not a number of scenarios, a semantic score or proof that the work was sufficiently deep. A completed pass may preserve conditional uncertainty or reject its candidate; unfinished execution remains partial.

**Receipts when a shell is available.** Resolve the packaged script relative to the installed skill root. The commands below are examples run from that root; `--run` selects the user's run directory. Use a new directory for each case.

```sh
python3 -B scripts/run_control.py init --run /path/to/new-case --topic "The user's actual future question"
python3 -B scripts/run_control.py record --run /path/to/new-case --phase frame --artifact 01-frame.md
python3 -B scripts/run_control.py status --run /path/to/new-case
python3 -B scripts/run_control.py verify --run /path/to/new-case
```

Run `record` immediately after the corresponding phase. Supply `--artifact` more than once for a packet and review. Use `--status partial --reason "the concrete limitation"` if the phase cannot be completed. Subsequent useful phases may proceed, but the final receipt check remains partial. `init` refuses an existing directory; it does not create a schema for source claims, pathways or forecasts.

**Reconcile against the saved report.** Revise the complete report before finishing the disposition record. Re-open it with line numbers and use the [report-excerpt locators](review-and-updates.md) for accepted repairs; recheck those locations if the report changes. The UTF-8 report must be a separate file from earlier phase artifacts and the UTF-8 disposition record. Once both are stable, record reconciliation with its report snapshot, then record delivery without rewriting that report:

```sh
python3 -B scripts/run_control.py record --run /path/to/new-case --phase reconcile --artifact 08-reconcile.md --report report.md
python3 -B scripts/run_control.py record --run /path/to/new-case --phase deliver --artifact report.md
```

Completed reconciliation requires `--report` and at least one valid report-excerpt locator. The tool checks every locator marked `[Report excerpt]`, the saved report at reconciliation and delivery, and rejects wrong quote positions, changed or substituted reports. It does not verify whether all important repairs were cited, or the truth or semantic adequacy of dispositions. A partial reconciliation may omit `--report` with a concrete reason and still deliver useful material, but remains partial. Finish edits before recording; if a recorded run needs further revision, preserve it and create a linked new case/version rather than editing receipts. Older runs require their matching Skill version.

`verify` checks phase order, completeness, report binding and whether recorded files still match their hashes. It refuses to report structural completion when artifacts are absent, changed, reused across phases, the delivered report differs from the reconciliation snapshot or a phase is partial. This is not proof that a source was really read, a reviewer was actually isolated, or a pathway is true. Those claims still require inspection of the recorded evidence and actual host operations. Direct manual editing of the state is not an audited execution method.

The same check covers development input/result snapshots and pending work. Work results are separate from phase synthesis; a later job may read an earlier result without rewriting it. Partial attempts remain available when resumed, and a completed job can be revised through a dependent follow-up. Once reconciliation binds the report, new work belongs in a linked new run. The queue does not make model calls or impose a Token cap; the host performs the selected work with its available tools.

`verify` writes `verification.json` separately from the recorded report. Cite that result in the final response; do not edit the report after recording it merely to insert “passed,” which would invalidate its hash. `status` is read-only. Budget endpoints can be supplied as `--budget-min` and `--budget-max` to `init`; they never become measured usage or a hard host limit.

State and verification writes use atomic replacement. Writers serialize through `.run-control.lock`; if a prior process crashed, inspect the lock's PID and actual process state before manually removing a stale lock. Never remove an active writer's lock. `status` can read progress without mutating it. Phase artifacts must be separate ordinary files, not hardlink aliases. Verification records a fingerprint of the checked state; it is a snapshot, so run verification again after changes. Invalid state replaces a previous cached pass with an explicit failure. These measures prevent common accidental corruption, not deliberate tampering or a proof of power-loss durability.

If a previously recorded premise is corrected, preserve that artifact and explain the correction and affected paths during reconciliation. If a run must be substantially restarted, create a new case and link back; do not rewrite receipts to make the first attempt look successful.

Without Python or files, complete what the host supports and explicitly state that receipt verification was unavailable. Never represent manual labels as script-verified completion. A host that ignores the Skill or bypasses the script cannot be made reliable solely by these instructions; cross-model behavior still needs testing.

**Depth review before stopping.** Use the causal comparison in [imagination.md](imagination.md) and the final-text checks in [review-and-updates.md](review-and-updates.md). Check whether important experiences remain unexplored and each path has its own conditions and discriminating observations. Repair the most consequential gap while resources permit; record remaining gaps when they do not.

Use a completion statement that distinguishes requested profile, structural receipt status, actual review isolation, semantic findings, research limits and measured usage. Token usage is `unknown` unless the host supplied a report; the receipt script never invents it. A structural pass and a fluent report are insufficient to claim expert approval, novelty or calibrated prediction performance.
