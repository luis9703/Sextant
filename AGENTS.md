# Working on Sextant

Sextant is an experimental foresight Skill. Preserve its focus on evidence-informed imagination: initial divergence, research that discovers and challenges, a second divergence, and concrete pathway review. Do not replace it with a generic industry report or a guaranteed prediction product.

`skills/sextant/` is the installable unit. Keep it self-contained and use relative links for its resources. The detailed design notes and archived drafts explain decisions; the current Skill and public validation record describe what is actually implemented. Do not preload worked examples into an independent evaluation.

Use Markdown for new cases. Add schemas, dependencies, orchestration, and scoring services only for demonstrated needs. Keep facts, inferences, assumptions, fictional scenes, observed test results, and untested proposals distinct. Preserve old predictions and failed candidates. Source citations support stated premises, not a promise about the future.

Run `python3 -B scripts/check_project.py` and `python3 -B -m unittest discover -s tests -v` before handing off package or installer changes. For substantial Skill behavior changes, use a bounded fresh-context forward test when available and authorized, with a realistic request and minimum raw materials. Record the actual result; do not supply the intended answer or call model review an expert evaluation.

Keep private runs, credentials, machine-specific paths, and account data out of public commits. Publishing a case is separate from producing it. Do not change user-wide agent settings or install globally as a side effect of working on this repository.

For cloud-synced checkouts under OneDrive, iCloud Drive, or macOS CloudStorage:

- Detect the location before installing dependencies. The current package needs no third-party runtime dependencies.
- Put environments under `${AI_PROJECT_ENVS_HOME:-$HOME/.local/share/project-envs}/<stable-project-id>/`; isolate each project's Python environment and keep Node dependencies outside the checkout.
- Do not create real environments, dependency folders, bytecode, tool caches, coverage data, or build staging inside the cloud worktree when they can be kept locally. Use `python3 -B` and OS temporary directories for checks.
- Preserve existing environments and dirty changes. Do not move or delete unknown environments without checking reproducibility and applicable authorization.
- Source, documentation, lockfiles, approved data, and final deliverables may remain in the approved cloud location. Add a project setup script only if dependencies are introduced, and document its external paths.
- Use ignored dependency symlinks only when supported by the package manager. If externalization is uncertain, inspect and adapt rather than guessing.

This file is the project instruction source of truth. `CLAUDE.md` imports it.
