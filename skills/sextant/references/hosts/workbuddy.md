# WorkBuddy host notes

## 0. When to read this

Read this file only when the current host is WorkBuddy. Signals: the session has `Agent` and `present_files` tools, or the skill was loaded from `~/.workbuddy/skills`.

This file covers host-specific execution only. Where it conflicts with `SKILL.md` or the execution and methodological references, those sources win. Default to full `deep` work even for “想象一下”; do not infer brief mode from that phrase or from switching models. Use the packaged phase helper through Bash when Python is available, and record unknown usage when WorkBuddy exposes no run-wide counters.

The repository's canonical frontmatter is portable. To preserve WorkBuddy-only display and management fields, the repository installer supports `--host workbuddy`, reading [agents/workbuddy.json](../../agents/workbuddy.json) and adding its fields to the copied SKILL.md. That JSON is this project's installer configuration, not a native WorkBuddy manifest. The method body remains unchanged. A symlink to canonical source does not apply an install-time overlay; existing customized or symlinked installations must be reviewed and preserved before choosing copy installation. Do not mutate global installation or settings as a side effect of a foresight run. Overlay rendering is tested; actual WorkBuddy field interpretation and client behavior remain separate tests.

## 0.1. Independent candidate exploration

When a broad seed has meaningful alternative directions and authorized Agent contexts are available, use [independent-exploration.md](../independent-exploration.md). The orchestrating session launches explorers directly with the same neutral seed and needed facts, but different useful questions; do not send the main candidate list or another explorer's answer. Use the installed exploration_packet.py to export selected inputs, or packet_argv from next for a recorded work question. Give the explorer TASK.md and the packet contents rather than the full run or control response. Integrate actual returned mechanisms before naming a main account. No explorer count or independent-generation claim is required when the host cannot provide it.

## 1. Review phase: fresh-context review

**Which tool.** Use the `Agent` tool with `subagent_type: general-purpose`.

- Do not use `Explore`: it is read-only, and a reviewer needs to fetch sources to verify numbers and dates.
- Do not use `Plan`: it returns a plan, not verification findings.
- Do not use `run_in_background`: the review must return to the current session to be recorded.

**What goes into the prompt.**

| Include | Exclude |
| --- | --- |
| The user's original question | Authorship, which model or subagent produced the candidates |
| Scope, region, and source cutoff | Self-scores, preferred candidates, rankings |
| Neutral candidate descriptions, in shuffled order with no quality marks | The first-pass candidate list and any generation history |
| The explicit assumptions each candidate depends on | Leading phrasing such as "please confirm these paths are sound" |
| Supporting and conflicting evidence, with links | The expected conclusion |
| The review request below | Chat context beyond the source list for this run |

Review request, reusable verbatim:

> Identify and list, one by one: (1) factual contradictions or premises the sources do not support; (2) missing transitions, resources, actor responses, cultural conditions, or delays; (3) alternative explanations that account for the same phenomenon, or similar cases that failed differently; (4) conditions that can be kept as explicit speculation but not called established; (5) repairs that would strengthen a candidate, or failures that would open another path.
> Give a basis for each item. Mark anything recalled from memory as unverified. Do not adjust probabilities to make the set pass, and do not remove a candidate for lack of precedent. End with the objections that remain.

Also perform a creative challenge: identify paths prematurely pruned by today's product form, overlooked desires or institutions, and alternative mechanisms that could open a different future. This does not authorize invented factual support.

Ask the reviewer to distinguish supported premise corrections from proposed causal repairs. The generating session judges both: it may use a sourced fact while rejecting the mechanism proposed around it. When a bridge fails, consider a justified alternative that preserves or transforms the future; do not invent an exclusion to make the scene concrete. Keep and unresolved remain valid dispositions.

**Recovering the result.** Save the actual review as a full reply or faithfully labelled issue summary, declaring context and coverage. Register material objections and park unused peripheral leads. Update the pathway synthesis with a new version, or confirm it unchanged when warranted, then complete and re-open the current synthesis and report. Record issue dispositions and bilingual literal excerpts as described in [review-and-updates.md](../review-and-updates.md). The helper binds both current files; deliver the frozen report and point readers to 00-current.md. Use the actual installed script/reference paths returned by next, not paths relative to an assumed working directory. Earlier cases retain their original records and matching contracts.

**Known hazard.** On Claude Code, a subagent that spawns another subagent can have the result routed to the top-level session instead of its parent, which stalls the wait. Mitigation: always launch the reviewing subagent directly from the orchestrating session. Never spawn a subagent from inside a generating subagent.

**When isolation is unavailable.** Isolation may be unavailable because there is no `Agent` tool, the call fails, the user forbids it, or the budget is spent. Record the actual limit in the review phase artifact and receipt, and summarize it in the review-status line of `report.md`. If a same-context check was performed, state:

> 本次为同上下文检查，未做隔离审查。同一模型与同一批来源不构成独立的事实佐证。

Never write "independently reviewed" or "expert verified".

An unperformed review remains partial with context unavailable. A performed same-context or source-limited review declares that actual context and coverage with a reason. A reviewer's network failure is a source-access limit; it does not by itself mean that no isolated review occurred. Use the existing phase records and 00-current.md; do not create an extra exploration.md for a nine-phase run.

## 2. Foothold and research phases: choosing network tools

| Situation | First choice | Why |
| --- | --- | --- |
| Keyword discovery, finding the closest existing ideas, scanning counterexamples | `WebSearch` | Fast, suited to open-ended discovery |
| Known URL, verifying numbers, dates, or qualifications in the source itself | `WebFetch` | Fetches the body so source qualifications can be preserved |
| `WebSearch` and `WebFetch` both failing repeatedly (observed in a real run) | Bash + `curl` | A completed run fell back to this and still gathered 24 sources; channels narrow to site search and known URLs |
| Pages behind login, dynamic rendering, or a captcha | the `web-access` skill | Drives a local browser with session state and rendering |
| Facing a captcha | Do not bypass it | Record the source as unread or unreachable, per `references/research.md` |

If every route fails: work from the supplied materials, list the unread sources and gaps in the actual foothold or research phase artifact and receipt, and label `report.md` as **bounded research**. Reflect any review limitation in its review status. Do not describe it as completed comprehensive research or create an extra process manuscript.

## 3. Artifacts and delivery

- Write to `sextant-runs/<case-id>/` under the current work area. Never overwrite an existing case.
- Deep/extensive files follow [execution.md](../execution.md): preserve phase artifacts and receipts plus the reader-facing report. Store the actual review and packet, and point each accepted correction to its concrete reconciliation. Existing 0.1 cases retain their historical files.
- Default to Markdown: the report carries source links, conditions, and qualifications, and Markdown stays quotable, diffable, and archivable. Produce an additional `report.html` only when the user explicitly asks for visualization or a presentation; keep the Markdown original.
- Call `present_files` as the final step before replying, passing absolute paths.

## 4. WorkBuddy specifics

- Respond in the user's language. Keep source titles in their original language.
- Do not assume the working directory is a particular project root. Confirm where `sextant-runs/` should go before writing.
- Never write case output into the skill's own install directory under `~/.workbuddy/skills/`; a reinstall or relink replaces it.
- Do not modify user-level agent configuration and do not install anything globally. Anything that writes outside the current work area needs the user's applicable authorization.
- Keep machine-specific paths and account data out of the artifacts.
