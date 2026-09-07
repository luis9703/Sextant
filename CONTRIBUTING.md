# Contributing to Sextant

欢迎中文或英文贡献。最有帮助的材料是失败案例、遗漏的条件、来源更正、与已有观点的实质差异，以及能够复现的宿主问题。

For a behavior change, show the request, available evidence and cutoff, actual output, observed problem, and the smallest proposed correction. Separate what was tested from what is expected. Do not add a universal rule merely because it fixed one example.

For a new public case, include a reader-facing report and a concise process record: initial candidates, what research changed, second-pass candidates, actual review status, references, and limitations. Use only material you are entitled to share. Remove private data, credentials, local account paths, and confidential source excerpts; link to public sources rather than republishing their full contents.

Do not label a path original just because a search found no match, or successful because reviewers found it persuasive. Include the closest existing accounts, explicit conditions, and observations that could weaken it. Keep counterexamples and zero-increment cases.

Before submitting a pull request, run:

```sh
python3 -B scripts/check_project.py
python3 -B -m unittest discover -s tests -v
```

Changes to the Skill's behavior should include an appropriate bounded example or evaluation result. Keep evaluation answers out of the tested model's input. Compatibility claims should name the actual host, test type, and result; directory-copy checks are not automatic-discovery tests.

Follow [AGENTS.md](AGENTS.md) for repository and cloud-worktree conventions. The [evaluation guide](evals/README.md) explains the evidence needed for stronger claims. The project uses the [MIT license](LICENSE); external sources retain their own licenses and are not relicensed by a citation here.
