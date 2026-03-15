# Jurph Project Template

A boring-on-purpose Python starter repo for projects that deserve a clean runway.

The default workflow is intentionally opinionated:
- `uv` for environment and package management
- `pytest` for tests
- `ruff` for linting and formatting
- `mypy` for gradual typing

The README still shows a `pip` fallback because that is part of being a good citizen in the wider Python community.

## What this template standardizes

- `src/` layout for import discipline
- `uv` as the default environment/package workflow
- `pytest` as the default test runner
- `ruff` for linting and formatting
- `mypy` for gradual typing
- one obvious place for project-specific notes
- one optional personal growth checklist that stays local by default

## Quick start

1. Create a new project from the template:

```bash
python deploy.py finnegan
```

2. Change into the new repo.
3. Follow the install instructions below.
4. Run the standard checks:

```bash
uv run --extra dev pytest
uv run --extra dev ruff check --no-cache src tests
uv run --extra dev ruff format --check src tests
uv run --extra dev mypy src
uv run your-project
```

## Template deployment

`deploy.py` is part of the template factory. It creates a sibling folder next to the template, copies the scaffold, renames the package, initializes git, and rewrites the most obvious placeholders. It does not get copied into the generated repo.

Examples:

```bash
python deploy.py finnegan
python deploy.py orbital-radio --dry-run
python deploy.py old-project --force
```

## Install

Dependencies for this project are defined in `pyproject.toml`.

If you are using `uv`:

```bash
uv sync --extra dev
```

On Windows, this template includes a wrapper that keeps uv's cache and managed Python inside the
repository instead of relying on user-level AppData paths:

```bat
.\scripts\uvw.cmd sync --extra dev
.\scripts\uvw.cmd run --extra dev pytest
```

The first `sync` may still need normal network access to download Python or wheels. After that,
the wrapper keeps the repo self-contained.
For `run`, the wrapper also injects `--locked` so verification commands fail fast if `uv.lock`
falls behind `pyproject.toml` instead of rewriting the lockfile during a test or lint pass.

The wrapper intentionally does **not** override `TMP` or `TEMP`. On this machine, Python's
`tempfile.mkdtemp()` and `TemporaryDirectory()` can create Windows directories that immediately
reject child files and folders. If you need repo-local scratch space, use a normal directory such
as `.scratch/` created with `Path.mkdir()` and a unique name, not the `tempfile` directory APIs.

If you are using `pip`:

First create a virtual environment:

```bash
python -m venv .venv
```

Then activate it:

```bash
# Linux/macOS
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (cmd.exe)
.venv\Scripts\activate
```

Then install the project and development dependencies:

```bash
pip install -e .[dev]
```

<a href="https://hatch.pypa.io/1.13/config/metadata/">Hatch</a>,
<a href="https://pdm-project.org/en/latest/reference/pep621/">PDM</a>, and
<a href="https://python-poetry.org/docs/pyproject/">Poetry</a>
also support `pyproject.toml` natively.
If you prefer
<a href="https://docs.conda.io/projects/conda/en/25.5.x/user-guide/tasks/manage-environments.html">conda</a>,
you may need a few additional setup steps.

## Suggested first moves in a new repo

- Write down the project goal in `notes/project-brief.md`
- Define the first user-visible workflow before building helpers
- Decide what belongs in pure logic vs orchestration
- Add one smoke test before the first big feature
- Decide whether to commit `uv.lock` immediately or after the first real dependency lands

## Opinionated defaults

- Center `uv` in the README so the preferred workflow is obvious
- Keep packaging metadata in `pyproject.toml` so `uv` and `pip` both work cleanly
- Use `uv run ...` in examples so the happy path does not require manual activation
- Keep `pyproject.toml` as the single dependency source of truth
- Commit `uv.lock` once the project has real dependencies and you care about reproducibility
- Run normal CI checks on pushes and pull requests, and run dependency hygiene once per day on a schedule

## CI/CD hygiene

- `.github/workflows/ci.yml` runs tests, Ruff, and mypy on pushes and pull requests
- The same workflow runs `scripts/audit_dependencies.py` once per day to catch stale dependency declarations
- `scripts/audit_dependencies.py` is meant to be customized if a dependency's import name differs from its package name

## Codecov bootstrap

If you wire a new repo up to CircleCI and Codecov, there is a nasty half-initialized state where
Codecov can show `Deactivated` for the repo row or keep the badge stuck at `unknown` even though
the first upload already succeeded.

When that happens during setup, do the normal setup pieces first:

- create the GitHub repo and push `main`
- add `CODECOV_TOKEN` in CircleCI
- let the first CircleCI upload run once

Then run the one-shot bootstrap helper from the repo root:

```bash
uv run python scripts/bootstrap_codecov.py
```

The helper:

- infers the `owner/repo`, branch, and current commit from `origin` and `git`
- uses `CODECOV_TOKEN`
- runs `codecovcli create-commit` and `create-report` via `uvx`
- polls Codecov's public repo, commit, branch, and badge endpoints so you get a clear answer instead
  of waiting half a day and hoping

This is meant for initial setup only, not normal CI. If you need to override the inferred values,
run `uv run python scripts/bootstrap_codecov.py --help`.

## Standard commands

```bash
uv sync --extra dev
uv run --locked --extra dev pytest
uv run --locked --extra dev ruff check --no-cache src tests
uv run --locked --extra dev ruff format src tests
uv run --locked --extra dev mypy src
uv run --locked your-project
```
