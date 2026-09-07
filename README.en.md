# Sextant · Future pathway exploration

[中文](README.md) · [Skill](skills/sextant/SKILL.md) · [Worked example](examples/ai-delegation-2035/report.md) · [Validation record](evals/results/2026-09-07.md)

**Explore what today's signals could become—with imagination, evidence, and room to revise.**

Sextant is an open Agent Skill for developing possible futures from emerging capabilities, papers, social changes, and observations. It explores assumptions, human desires, structural analogies, evolving institutions, and the conditions connecting them.

Version **0.1.0-alpha.1** is an experimental, usable method prototype. It has not demonstrated superiority over ordinary model prompting, experts, or other foresight methods. It has no validated long-term forecasting record.

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

The installer copies the full `sextant` folder and refuses to overwrite an existing installation. Add `--dry-run` to inspect the destination. You may also copy `skills/sextant/` manually into your host's configured skill directory. Review and preserve local customizations before replacing an old installation; automatic overwrite or merging is intentionally unsupported.

These personal directories follow the current [Codex documentation](https://learn.chatgpt.com/docs/build-skills) and [Claude Code documentation](https://code.claude.com/docs/en/skills). Customized or older clients may use different locations. Invoke `$sextant` in Codex or `/sextant` in Claude Code, or explicitly ask the agent to use it. Follow the host's reload instructions if the skill does not appear. See the validation record for what has actually been tested; packaging compatibility is not a claim that every client has been verified.

**Choose the depth.** Exploration produces a compact expansion with unverified premises labeled. Research produces a source-backed case with candidate revisions, conditions, review status, and signposts. Update revisits an existing case using new evidence while retaining earlier judgments. You can specify horizon, region, people, sources, and research budget.

Artifact-producing runs default to a new `sextant-runs/<case-id>/` with `exploration.md` and `report.md`. Personal runs are not automatically published. A monitoring proposal does not schedule a monitor. Scenario narratives need not be quantified forecasts.

Explore the [worked case](examples/ai-delegation-2035/report.md), its [process record](examples/ai-delegation-2035/exploration.md), the [evaluation approach](evals/README.md), and [behavioral cases](evals/cases.md). The detailed [design](docs/01-product-and-architecture.md) and [research notes](docs/02-research-and-evaluation.md) are currently in Chinese, as are the evaluation guide, the behavioral cases, the validation record, and the worked example.

Contributions are welcome through the [contribution guide](CONTRIBUTING.md), especially failed cases, counterexamples, source corrections, and host compatibility evidence. See the [changelog](CHANGELOG.md) and [MIT license](LICENSE).

Run local checks:

```sh
python3 -B scripts/check_project.py
python3 -B -m unittest discover -s tests -v
```

These checks cover packaging, local references, and installer behavior. They do not establish creativity, correct interpretation, or predictive accuracy. See the [validation record](evals/results/2026-09-07.md) for actual results and limitations.
