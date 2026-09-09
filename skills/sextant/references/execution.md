# Full-depth execution and honest completion

The default is `deep`, including when the user says “imagine” or “想象一下”. Only an explicit request for a short sketch selects `brief`. A limit, tool failure or exhausted context creates a partial deep run, not an unannounced switch to brief. An update follows the same obligations for affected parts, with references to preserved earlier work.

Read the [profiles](../assets/depth-profiles.json) when planning resources. Provisional defaults are 50,000–100,000 run-wide tokens for deep and 100,000–200,000 for extensive. They are editable engineering starting points, not empirically optimal allocations; set a profile target to null to disable it. No minimum token expenditure is required for completion. A user-specified target overrides the default at initialization. If usage is unavailable, report unknown rather than estimating from answer length. Do not count repeated context or cached input as independent new reasoning. Different providers expose different counters; never add nested reasoning or cached counters twice.

Use extra capacity on useful work: additional independent candidates, underrepresented people and source fields, alternative explanations, branch development, and both grounding and creative review. Protect these activities when the source list grows. Source discovery should stop or narrow before it consumes all opportunity for imagination. Do not exhaust a budget on filler, redundant citations, or repeatedly paraphrasing the same candidates.

**Nine obligations, open-ended content.** Phases describe work and evidence of work, not prescribed headings or a fixed number of future worlds. A meaningful artifact may be concise; its length alone does not satisfy a phase.

| Phase | Work to retain | Completion question |
| --- | --- | --- |
| frame | User's seed, intended imagination, scope, profile, resource plan and assumptions | Is this still the user's future-world question, rather than a replacement research or investment task? |
| foothold | Minimal current premises with source or unverified status, units and ambiguities | Can the initial imagination distinguish a known capability from an assumption? |
| diverge | Candidates saved before the broad survey, spanning different mechanisms and human experiences | Did exploration reach beyond variations of the obvious answer? |
| research | Key sources, counterevidence, unfamiliar enabling material, closest prior accounts | Did research both challenge and expand the material available for imagination? |
| recombine | New, replaced and refined candidates with the material that motivated the change | Is there actual second-pass creation rather than only selection and annotation? |
| pathways | Developed changes to life, relationships and institutions, branch-specific conditions and feedback | Are there transitions and consequential effects beyond today's product form? |
| review | Neutral packet plus actual grounding and creative review; or an explicit inability record | Were numbers, dependencies, pruned possibilities and discriminating observations checked? |
| reconcile | Issue-by-issue dispositions pointing to concrete draft changes or unresolved limits | Do accepted corrections actually appear in the final reasoning? |
| deliver | Reader-facing report plus observed verification and resource status | Can the user see the futures, their conditions, what changed, and what remains uncertain? |

For deep/extensive work, retain phase artifacts such as `01-frame.md` through `08-reconcile.md` and `report.md`. Names are flexible. Early artifacts are historical records: append corrections in later files or new versions rather than rewriting them after the fact. Keep source notes and candidate summaries, not private chain-of-thought. The review phase uses a separate packet and actual review where available.

**Receipts when a shell is available.** Resolve the packaged script relative to the installed skill root. The commands below are examples run from that root; `--run` selects the user's run directory. Use a new directory for each case.

```sh
python3 -B scripts/run_control.py init --run /path/to/new-case --topic "The user's actual future question"
python3 -B scripts/run_control.py record --run /path/to/new-case --phase frame --artifact 01-frame.md
python3 -B scripts/run_control.py status --run /path/to/new-case
python3 -B scripts/run_control.py verify --run /path/to/new-case
```

Run `record` immediately after the corresponding phase. Supply `--artifact` more than once for a packet and review. Use `--status partial --reason "the concrete limitation"` if the phase cannot be completed. Subsequent useful phases may proceed, but the final receipt check remains partial. `init` refuses an existing directory; it does not create a schema for source claims, pathways or forecasts.

`verify` checks phase order, completeness and whether recorded files still match their hashes. It refuses to report structural completion when artifacts are absent, changed, reused across phases or a phase is partial. This is not proof that a source was really read, a reviewer was actually isolated, or a pathway is true. Those claims still require inspection of the recorded evidence and actual host operations. Direct manual editing of the state is not an audited execution method.

`verify` writes `verification.json` separately from the recorded report. Cite that result in the final response; do not edit the report after recording it merely to insert “passed,” which would invalidate its hash. `status` is read-only. Budget endpoints can be supplied as `--budget-min` and `--budget-max` to `init`; they never become measured usage or a hard host limit.

State and verification writes use atomic replacement. Writers serialize through `.run-control.lock`; if a prior process crashed, inspect the lock's PID and actual process state before manually removing a stale lock. Never remove an active writer's lock. `status` can read progress without mutating it. Phase artifacts must be separate ordinary files, not hardlink aliases. Verification records a fingerprint of the checked state; it is a snapshot, so run verification again after changes. Invalid state replaces a previous cached pass with an explicit failure. These measures prevent common accidental corruption, not deliberate tampering or a proof of power-loss durability.

If a previously recorded premise is corrected, preserve that artifact and explain the correction and affected paths during reconciliation. If a run must be substantially restarted, create a new case and link back; do not rewrite receipts to make the first attempt look successful.

Without Python or files, complete what the host supports and explicitly state that receipt verification was unavailable. Never represent manual labels as script-verified completion. A host that ignores the Skill or bypasses the script cannot be made reliable solely by these instructions; cross-model behavior still needs testing.

**Depth review before stopping.** Check whether important perspectives remain unexplored, a current product limitation incorrectly killed a broader future, the second pass introduced real alternatives, each path has its own conditions, and the observations could distinguish competing explanations. Repair the most consequential gap while resources permit. Record remaining gaps when they do not.

Use a completion statement that distinguishes requested profile, structural receipt status, actual review isolation, semantic findings, research limits and measured usage. Token usage is `unknown` unless the host supplied a report; the receipt script never invents it. A structural pass and a fluent report are insufficient to claim expert approval, novelty or calibrated prediction performance.
