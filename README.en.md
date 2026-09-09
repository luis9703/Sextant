# Sextant · Future pathway exploration

[中文](README.md) · [Skill](skills/sextant/SKILL.md) · [Worked example](examples/ai-delegation-2035/report.md) · [Release review](evals/results/2026-09-09-release-review.md)

**Explore what today's signals could become—with imagination, evidence, and room to revise.**

Sextant is an open Agent Skill for developing possible futures from emerging capabilities, papers, social changes, and observations. It explores assumptions, human desires, structural analogies, evolving institutions, and the conditions connecting them.

Version **0.2.0-alpha.1** is an experimental, usable method prototype. It has not demonstrated superiority over ordinary model prompting, experts, or other foresight methods. It has no validated long-term forecasting record.

Try a request such as:

> AI can now carry out some multistep online tasks. Explore how ordinary people's work, consumption, and relationships might change by 2035. Ground the possibilities in evidence and develop directions not adequately explored by the baseline discussion.

The workflow is: establish a small factual foothold, diverge, research both objections and enabling material, diverge again, connect pathways, and review. A research run uses a fresh reviewing context where the host supports it and authorization permits it. Otherwise, the limitation is explicit. The skill does not force scenario counts, exact years, probabilities, or claims of originality.

**Install for local use.** Use an agent host that can load Skills and supply research tools. No background service or additional API key is required by this repository. Installation and repository checks use Python 3.10+ with the standard library; the skill itself is Markdown.

```sh
git clone https://github.com/luis9703/Sextant.git
cd Sextant
```

For Codex's personal skill directory:

```sh
python3 scripts/install_skill.py --to "$HOME/.agents/skills"
```

For Claude Code's personal skill directory:

```sh
python3 scripts/install_skill.py --to "$HOME/.claude/skills"
```

For WorkBuddy with its existing display extensions:

```sh
python3 scripts/install_skill.py --to "$HOME/.workbuddy/skills" --host workbuddy
```

The canonical source uses portable frontmatter. `agents/workbuddy.json` is an overlay consumed by this project's installer, not a native WorkBuddy manifest. Only the installed WorkBuddy copy receives those extra fields; its method body remains identical. A symlink to canonical source does not apply the overlay. See the [host notes](skills/sextant/references/hosts/workbuddy.md); actual client loading and model behavior still require separate validation.

The installer copies the full `sextant` folder, including its license, and refuses existing targets, destinations inside the source, and symlinks inside the package. Add `--dry-run` to inspect the destination. You may manually copy the portable unit. Preserve local customizations before replacing an old installation; automatic overwrite and merging are unsupported. Filesystem failures are reported explicitly, with any partial destination retained for inspection rather than silently overwritten on retry.

These personal directories follow the current [Codex documentation](https://learn.chatgpt.com/docs/build-skills) and [Claude Code documentation](https://code.claude.com/docs/en/skills). Customized or older clients may use different locations. Invoke `$sextant` in Codex or `/sextant` in Claude Code, or explicitly ask the agent to use it. Follow the host's reload instructions if the skill does not appear. See the validation record for what has actually been tested; packaging compatibility is not a claim that every client has been verified.

**Full depth is the default.** `deep` covers both divergences, research, developed pathways, grounding and creative review, reconciliation, and delivery. `extensive` adds independent candidate exploration and further branch work where useful. Select `brief` only for an explicit request for a short sketch, never merely because the user says “imagine.” Resource limits create an honestly partial run, not an unannounced downgrade. Updating a case retains the necessary depth and earlier judgments.

Deep runs use a new `sextant-runs/<case-id>/`, phase artifacts, `run-state.json`, and `report.md`. The packaged receipt helper checks recorded order, missing or changed artifacts, and partial phases. It does not establish truth, actual reviewer isolation, creativity, or compliance by a host that bypasses it. See the [execution contract](skills/sextant/references/execution.md). Earlier examples retain their historical format.

The [resource profiles](skills/sextant/assets/depth-profiles.json) use provisional engineering targets of 50,000–100,000 run-wide tokens for deep and 100,000–200,000 for extensive. These ranges have not been validated as optimal. Edit them, set a profile target to null, or override them per run. A target is a planned envelope, not actual usage, a runtime cap or a minimum spend. Host telemetry is required for actual counters; unknown usage remains unknown. Spend extra capacity on different mechanisms, unfamiliar material, branch development and reconciliation rather than padding output.

From the repository root, initialize a new case and inspect progress:

```sh
python3 -B skills/sextant/scripts/run_control.py init --run sextant-runs/my-case --topic "My future question" --budget-min 50000 --budget-max 100000
python3 -B skills/sextant/scripts/run_control.py status --run sextant-runs/my-case
```

Personal runs are not automatically published. A monitoring proposal does not schedule a monitor. Scenario narratives need not be quantified forecasts. The protocol does not guarantee identical behavior across models; cross-host execution still needs validation.

Explore the [worked case](examples/ai-delegation-2035/report.md), its [process record](examples/ai-delegation-2035/exploration.md), the [evaluation approach](evals/README.md), and [behavioral cases](evals/cases.md). The detailed [design](docs/01-product-and-architecture.md) and [research notes](docs/02-research-and-evaluation.md) are currently in Chinese, as are the evaluation guide, the behavioral cases, the validation record, and the worked example.

Contributions are welcome through the [contribution guide](CONTRIBUTING.md), especially failed cases, counterexamples, source corrections, and host compatibility evidence. See the [changelog](CHANGELOG.md) and [MIT license](LICENSE).

Run local checks:

```sh
python3 -B scripts/check_project.py
python3 -B -m unittest discover -s tests -v
```

These checks cover packaging, local references, and installer behavior. They do not establish creativity, correct interpretation, or predictive accuracy. See the [release review](evals/results/2026-09-09-release-review.md) and the [partially completed behavioral validation](evals/results/2026-09-08-depth.md); the [initial record](evals/results/2026-09-07.md) is retained as history.
