# Test Infrastructure and Documentation

Part of the `code-testing` skill. SKILL.md carries the testing
hierarchy and sociable-method.md the unit-testing method; this file carries the Python project setup that
makes the method's default suite runnable from a fresh clone: directory
layout, pytest configuration, venv and dependencies, Makefile targets,
the README/CONTRIBUTING template, and rules for custom test runners.

The one rule everything below serves: **bare `pytest` runs only the
fast, offline, credential-free unit suite**, and the documented
bootstrap command actually exists. When a Makefile target, a doc, and
the real `pytest` behavior disagree, fix the disagreement before adding
anything.

## Directory Structure

```
tests/
  unit/                        # Fast, offline, no credentials (DEFAULT)
    conftest.py                # Shared fixtures (isolation, providers)
    fixtures/                  # Seed data, test configs
  integration/                 # Non-default suites (explicit invocation only)
    real-user/                 # Hits live third-party APIs with real
                               # credentials and real user data. Not stable
                               # across contributors — each needs their own
                               # account/credentials.
    agent/                     # LLM inference tests (see agent-tests.md)
```

Most repos need only `tests/unit/`. Do not add integration
subdirectories speculatively — add them when a specific,
unavoidable testing need arises that unit tests cannot cover.
See the Testing Hierarchy in SKILL.md for when each level is
appropriate.

## Test Segregation

Unit tests are the **only** default for bare `pytest`. Configure
this in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--ignore=tests/integration"
```

Running tests:
```bash
pytest                                      # unit only (default)
pytest tests/integration/real-user/         # explicit suite
pytest tests/integration/agent/             # explicit suite
pytest tests/integration/                   # all integration
pytest tests/unit tests/integration         # everything
```

Naming a suite directory as a positional argument runs it even though
`addopts` ignores `tests/integration` by default — the ignore applies to
collection under a *parent* path, not to a path named explicitly. That
is also why `pytest tests/` is **not** "everything": it still skips
`tests/integration/`. Name the suites you want.

## Unit Test Rules

- **Fast, local, no network, no credentials.**
- Subprocess calls only to ubiquitous tools (e.g., `git init`,
  `git commit` — never `git push`).
- Every test must be isolated from every other test and from
  the real filesystem.

## Virtual Environment and Dependencies

**Gitignore the venv directory.** Ensure `.venv/` is in
`.gitignore` before creating one.

**Test dependencies** go in the project's dev extras:

```toml
# pyproject.toml
[project.optional-dependencies]
dev = ["pytest", "pytest-asyncio"]
```

## Running Tests — README Template

The project's README (or CONTRIBUTING.md) must document how to
run each test suite. Template:

```markdown
## Testing

**Unit tests** run offline with no credentials:

    make setup                   # bootstrap .venv (once)
    source .venv/bin/activate    # or call .venv/bin/pytest directly
    pytest                       # run unit tests

Or from a fresh clone:

    make test        # creates venv + runs unit tests

**Integration tests** require additional setup:

| Suite | Path | Prerequisites |
|-------|------|--------------|
| real-user | `tests/integration/real-user/` | Platform credentials (see Authentication) |
| agent | `tests/integration/agent/` | `ANTHROPIC_API_KEY` |

Run explicitly:

    pytest tests/integration/real-user/
    pytest tests/integration/agent/

These are excluded from the default `pytest` invocation.
```

## Makefile

`make test` always runs unit tests only. `make setup` is
independently callable so contributors can bootstrap the venv
and then use `pytest` directly for non-default suites:

```makefile
setup:
	python -m venv .venv
	.venv/bin/pip install -e ".[dev]"

test: setup
	.venv/bin/pytest
```

```bash
make test                                            # unit tests (fresh clone safe)
make setup && .venv/bin/pytest tests/integration/...  # bootstrap then run any suite
```

## New Project Setup Checklist

1. Create `tests/unit/` with `conftest.py`
2. Decide on boundary strategy (Option A or B) — see SKILL.md
3. Configure `pyproject.toml` to ignore `tests/integration/`
   by default
4. Create isolation fixtures in `conftest.py`
5. Ensure all core layer config/data paths support env var
   overrides
6. Add `pytest` to dev dependencies
7. Gitignore `.venv/`
8. Add `setup` and `test` Makefile targets
9. Document test setup in README or CONTRIBUTING.md using the
   template above
10. Verify: bare `pytest` runs only unit tests

## Documentation placement

Where in the repo's docs the testing setup lives depends on the
project's type, technicality, and how central testing is to
someone cloning the repo. Acceptable placements:

- **README.md** — a short `## Testing` section showing minimal
  setup + invocation. Best when testing is central to what the
  repo IS (a library, a CLI tool, a repo whose value proposition
  includes its test suite).
- **CONTRIBUTING.md** — fuller setup instructions alongside other
  dev-workflow content. Best when the primary audience is
  evaluate → select → install → use, and testing is mostly for
  contributors.
- **docs/TESTING.md** — the bulk of detail lives there, with a
  short pointer from README or CONTRIBUTING. Best when the
  testing story is detailed enough that including it inline would
  dominate the surrounding doc.

Any of these is fine. **When extending an existing repo, follow
the precedent already established** — don't introduce a new
location if the repo already has one of these patterns.
Consistency within a codebase matters more than picking the
"best" placement in the abstract.

## Custom test runners (only if already present)

A repo may carry a custom test runner script as an **optional
alternative** to invoking `pytest` directly — e.g., `./runtests`,
`./my-app test <options>`, or similar.

**This skill never introduces such a script.** If a repo does not
already have one, do not create one as part of any testing-setup
task. The documented `make setup` + `pytest` path is the canonical
entry point; a runner is pure convenience on top of it.

When a runner **is** already present, enforce these compliance
rules:

1. **Pure stdlib.** The runner must run immediately after clone
   with no prerequisites — no `make setup`, no manual venv
   bootstrap, no `pip install`. Only the Python standard
   library. Anyone with Python 3 can clone the repo and invoke
   it.

2. **Auto-bootstrap the same venv.** The runner must internally
   perform the same venv setup that the README / CONTRIBUTING /
   docs/TESTING.md documents as the manual prerequisite for
   direct `pytest` invocation — same directory name (e.g.
   `.venv/`), same dependency source (the project's declared dev
   dependencies — `pyproject.toml`, `setup.py`,
   `requirements*.txt`, or whatever the docs point at), same
   activation approach. A contributor who runs `make setup` and
   then uses `pytest` directly must be able to switch to the
   runner (or vice versa) without the venv changing shape.

3. **README documentation shows both paths.** When a runner
   exists, the testing-setup doc must present it alongside bare
   `pytest` and `make test`, so contributors know all paths lead
   to the same outcome.

4. **Runner is additive, never authoritative.** Everything the
   runner does must be achievable by following the documented
   manual setup + bare `pytest`. The runner is a shortcut, not
   a parallel ecosystem. Test-behavior decisions (which tests
   run, what `pytest.ini` filters apply, which environment
   variables are set) stay in `pytest.ini` /
   `pyproject.toml` / `conftest.py` — the runner just invokes
   pytest after preparing the environment.

If an existing runner violates any of these, bring it into
compliance or remove it. A divergent runner is worse than no
runner — it silently installs a different dependency set,
documents an inconsistent setup, or claims to be a shortcut
while actually being a second way to test.

