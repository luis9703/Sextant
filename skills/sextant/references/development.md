# Developing a future beyond its prerequisites

Read after the second divergence. Use this workbench to turn promising candidates and unresolved choices into developed worlds. The two operations below apply to technical, social and cultural questions. They produce short working documents, not extra sections to fill in the final report.

## Choose the work that could change the answer

Select a consequential candidate that currently ends at its enabling conditions, and a consequential choice where different people, settings or alternatives are still lumped together. Open concrete `evolution` and `contrast` questions against saved inputs. These are two kinds of work, not two required future worlds. A single candidate may need several dependent passes; unimportant candidates need not receive equal effort.

Let additional capacity follow unresolved questions: which exploration could reveal a different use, actor response, relationship or outcome? After each result, decide what changed, what to integrate or reject, and which newly exposed question is worth continuing. Open a follow-up when the gap could materially change the future. Stop a branch when further work repeats it, it rests on a fatal contradiction, or a remaining question requires unavailable observation; give the actual reason. A lack of historical adoption data is not a reason to stop conditional imagination. Do not stop merely because every heading has prose or the minimum kinds have results.

## Evolution: run the world after the conditions hold

Separate current footholds from a small set of temporary, explicitly hypothetical enabling conditions. Assume those conditions hold for this pass. This temporarily moves present uncertainty out of the way; it does not turn an assumption into evidence.

Follow an ordinary event in that world. Show what someone does or newly wants, how another person or organization responds, and how repeated use changes the situation facing them next time. Feed that changed situation into another consequential episode. Look for learning, refusal, status, belonging and meaning as well as prices and efficiency. Describe visible actions and outcomes, not private chain-of-thought.

The useful result is a change in the world: a relationship is reorganized, a practice becomes normal, a new need or conflict appears, or an earlier bottleneck loses its role. Follow important consequences until there is a feedback, reversal or branch worth explaining. Re-listing enabling conditions, inventing a job title or adding a governance body does not perform this operation. Preserve failures that open a different lived future; do not only return to today's workflow.

Then return to the present. Explain a plausible entry point, the few transitions connecting it to the imagined episode, and what could send it another way. Distinguish prerequisites from effects produced by adoption. Use relative timing and dependencies when dates are unknown. Research a current premise if it can change the bridge; do not require an established precedent for a future episode.

Keep a concise result with the assumptions held open, the episode and subsequent responses, the changed world, a reverse bridge, and the next consequential question. Prose or a small state-transition table is sufficient; there is no fixed number of actors or simulated years. This is conceptual conditional exploration, not an empirically calibrated agent-based simulation.

## Contrast: explain who chooses what and what changes that choice

Hold a concrete desired outcome or situation steady. Compare people or organizations whose relevant constraints or desires differ, and compare plausible responses available to them. Include remaining with the current practice, refusing the activity, or doing it without a supplier when those are meaningful alternatives. Do not invent demographic differences just to fill groups.

Explain what each option lets the actor accomplish and what it asks them to give up: money, time, effort, control, identity, coordination, or switching costs. Keep the person benefiting, the decision-maker, the person doing the work, and whoever bears its costs distinct when that difference matters. For commercial questions, additionally separate need, direct use, willingness to pay and who can capture the payment. For social questions, do not force payment or business models into the comparison.

Make a conditional choice rather than a list of possibilities: under this specific setting, why would one response be preferable or feasible, and what change would reverse it? Change one influential condition while holding the rest stable. If that does not distinguish the choices, name the still-missing discriminator and develop it where possible. Qualitative tradeoffs are enough; no invented price, utility score, probability or universal ranking is needed.

Distinguish replacement of an existing activity from a new activity that previously made no sense, including nonconsumption. When the user's question names specific products or institutions, retain any relevant differences; verify current properties or state them as conditions. Do not end with an undifferentiated “any provider could win” when the comparison can explain a branch. Sometimes alternatives remain indistinguishable: record that result instead of forcing a winner.

Keep the comparable situation, the meaningful actor differences, conditional choices, a switch condition and implications. A table can help but is optional. Feed the resulting choices into the evolution pass: who adopts, who refuses and who captures value will change the world being explored. Conversely, use a new world from evolution as the input to another contrast.

## A resumable queue, using the existing helper

The host agent runs these commands; the user need not operate a CLI. The examples are from the repository root. In an installed copy use the absolute script path returned by init/next; reference paths in next are also resolved. Artifact paths are relative to the run. Use new result files rather than overwriting saved inputs. The identifiers and questions illustrate syntax, not answers.

```sh
python3 -B skills/sextant/scripts/run_control.py work-add --run /path/to/case --id branch-e1 --kind evolution --source 05-recombine.md --question "What changes after the selected branch's enabling conditions hold?" --priority 1
python3 -B skills/sextant/scripts/run_control.py next --run /path/to/case
python3 -B skills/sextant/scripts/run_control.py work-record --run /path/to/case --id branch-e1 --artifact work/branch-e1.md
python3 -B skills/sextant/scripts/run_control.py work-add --run /path/to/case --id choice-c1 --kind contrast --source work/branch-e1.md --after branch-e1 --question "Which affected actors choose different responses in the same situation, and what reverses those choices?"
python3 -B skills/sextant/scripts/run_control.py work-record --run /path/to/case --id choice-c1 --artifact work/choice-c1.md
```

`next` is read-only. It returns the highest-priority ready question with input snapshots, dependency results and earlier attempts, or the next phase to perform. Priority 1 is highest; ties retain insertion order. Dependencies must reference existing work and be complete before a dependent result can be recorded. The tool schedules recorded questions; it does not discover all missing questions or invoke models.

`work-record --status partial --reason "concrete remaining work"` preserves an incomplete attempt. The job remains pending; resume with a new result file. A finished result may conclude that a candidate should be rejected or that a choice remains conditional—the prose explains why. That is different from not having performed the operation. Finished jobs cannot be overwritten; open a dependent follow-up to revise them. Questions found during review can be added before reconciliation.

Register a question before producing a new result. The helper records which files already existed then and rejects them as new post-registration results. Use --adopt-existing with a reason to transparently reuse genuine earlier work, including a performed operation in a phase artifact. Adopted work is not counted as a new follow-up. No file inventory proves when an idea was thought of, who wrote it or whether a newly copied file contains new reasoning. Do not repeat a developed ordinary event simply to satisfy the queue; perform it once, adopt it if necessary, then spend capacity on the remaining gap. There is no content-score or placeholder detector.

Deep and extensive profiles require results for both kinds before completed pathways and reconciliation. An open or partial job prevents those phases from being recorded as done and prevents a final structural pass. If resources or tools prevent completion, use partial phase receipts and describe the actual limit. Unknown future outcomes do not themselves make a performed work item partial. Brief requests have no mandatory queue; without Python, keep the same inputs, results and open questions in Markdown and label runtime checking unavailable.

Integrate useful results into a separate pre-review synthesis. After review-driven work, update that synthesis with a new version before the final report, or explicitly confirm it unchanged when warranted. 00-current.md identifies the current files. During review, the neutral packet carries the developed world and conditional choices. Reconciliation accounts for registered objections in both synthesis and report. Semantic review must still check that valuable development survived compression; save significant limits without claiming they were resolved.

When authorized host delegation is available, the orchestrator may dispatch ready questions into separate contexts with their recorded inputs and this reference, and later collect the actual results. Independent jobs may run in parallel; dependencies remain sequential. The same-context route is valid when delegation is unavailable. Do not create nested reviewing agents, invent tool execution or treat separate contexts as independent facts.

For a scoped dispatch, use the packet_argv returned by next, substituting a new packet directory. It includes only the job's selected inputs and completed dependency results. The [packet helper](../scripts/exploration_packet.py) also accepts a neutral seed directly before initial divergence, as described in [independent-exploration.md](independent-exploration.md). The host sends TASK.md and the copied inputs, not the entire control response or phase history. Input selection is reproducible; the host still judges neutrality and honors the scope.

When exploring an alternative mechanism, use a neutral capability/relationship note instead of a main draft where possible. When intentionally continuing a candidate, make the dependency explicit. A current design's property can be changed conditionally during evolution or contrast; examine the resulting choices and new activity rather than treating the original form as a permanent limit.

Queue integrity is deterministic: input and result snapshots, dependency order, immutable attempts, and phase closure. Whether an episode is insightful, a comparison fair, or an integration substantive remains a semantic judgment. Do not implement word-count, novelty-score or keyword gates as substitutes.
