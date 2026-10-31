# code-testing — maintainer notes

Formerly `sociable-unit-tests`. Renamed when it became the single home for
how a codebase is tested, not only the unit-testing method.

Shape:

- `SKILL.md` is a router, kept well under 200 lines: the four-rung
  hierarchy (sociable unit tests → agent tests → agent evals → real-user),
  when each applies, the sociable position in one paragraph, the
  infrastructure the hierarchy requires, and a routing table. Nothing in it
  is a procedure; procedures live one level down.
- `references/sociable-method.md` — the unit-testing method (what was
  Part 1 of the old single file).
- `references/infrastructure.md` — Python test setup: `tests/` layout,
  pytest config that ignores `tests/integration/` by default, `.venv` and
  dev extras, `make setup` / `make test`, README/CONTRIBUTING Testing
  template, custom-runner rules (old Part 2). General project hygiene,
  kept here because the method dictates the setup.
- `references/agent-tests.md` — tests of a product's *own* LLM features
  (old Part 3). Its first paragraph distinguishes it from agent evals.
- `references/agent-evals.md` — can an outside agent drive an MCP tool
  surface from descriptions alone. The method and harness recipes came
  from the mcp-app skill's `references/agent-evals.md`; mcp-app should
  point here rather than carry its own copy, keeping only what is
  framework-specific.

Why: the single-file version was 614 lines (over the 500-line body
guideline, no progressive disclosure), its name and description covered
only the method, and "agent tests" and "agent evals" lived in two skills
without cross-reference. The description now names all four parts and the
concrete things an agent searches for (make targets, pytest config, tests/
layout, Testing section, LLM feature tests, MCP tool evals); keep it that
way when editing, and keep it under 1024 characters with no angle brackets.

`evals/` holds four cases in the `claude plugin eval` layout: method-only
(rewrite over-mocked tests), infrastructure-only (add make targets and a
Testing section), mixed (new feature plus a Makefile whose target name
disagrees with the docs), and an MCP server (can an agent use these tools
from their descriptions). The last needs a harness that can run `claude -p`
or `agy -p` with authentication; without one it can only be planned, not run.
