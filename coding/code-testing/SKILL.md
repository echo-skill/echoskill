---
name: code-testing
description: "How to test code: which kind of test a situation needs and how to write and set up each. Use when writing, reviewing, or fixing tests, deciding what to mock, or whenever a repo's test setup is created, documented, or audited: tests/ layout, pytest config in pyproject.toml, keeping integration suites out of the default pytest run, .venv bootstrap and dev extras, Makefile setup and test targets, a README or CONTRIBUTING Testing section, rules for an existing custom test runner. Also for tests of a product's own LLM features (pinned model, no ambient context, assert on signals), for agent evals that check whether an outside agent can drive an MCP server's tools correctly from their descriptions alone, and for real-user integration suites. Use it when asked to add make targets, a conftest.py, or a Testing section to a Python project, when a Makefile and its docs disagree about how tests run, or to check whether an agent can use these tools, even if nobody says test."
---

# Code testing

One skill for how a codebase is tested: which kind of test a situation
calls for, and how to write and set up each kind. This file is the map.
Each kind has its own reference; read the one the task reaches, when it
reaches it.

## The position, in one paragraph

Write **sociable** unit tests: the unit under test is a meaningful
transaction through the business-logic layer, run against real
collaborators, real files in a temp directory, and real environment
variables set and reverted by the test framework. Mock only at system
boundaries that are uncontrollable or slow (network, clocks, heavy
external processes). A suite that mocks its own collaborators verifies
that the code calls the mocks, not that it works, and breaks on every
refactor. Cover everything you can this way, fast and offline, before
reaching for any form of integration test.

## The hierarchy: which kind of test, and when

Work down this list and stop at the first rung that covers the need.
Every repo has rung 1. Most repos stop there.

| # | Kind | Use it when | Lives in | Default `pytest` run? | Reference |
|---|------|-------------|----------|------------------------|-----------|
| 1 | **Sociable unit tests** | Always. All business logic through the core layer, plus thin in-process tests of each interface layer (CLI, HTTP, MCP) for wiring and shape. No network, no credentials, deterministic. | `tests/unit/` | Yes, the only default | [sociable-method.md](references/sociable-method.md) |
| 2 | **Agent tests** of the product's own LLM features | The code under test calls a model (prompts, inference, tool wiring the product ships) and its behavior needs automated verification. Pinned model, no ambient context, assertions on signals. Rare. | `tests/integration/agent/` | No, needs an API key | [agent-tests.md](references/agent-tests.md) |
| 3 | **Agent evals** of the product's MCP tool surface | The product exposes MCP tools and you need to know whether an *outside* agent, given only tool names and descriptions, uses them correctly. Run when adding or reworking tools that write, delete, or edit by position, after changing a tool description, and before a breaking tool-surface change. | Harness runs from a scratch directory, not the test suite | No, headless agent runs | [agent-evals.md](references/agent-evals.md) |
| 4 | **Real-user integration tests** | Last resort. The core functionality depends on an external system that can only be exercised with real, private credentials that are not reusable across contributors. Avoid if a local provider or contract test covers the same ground. | `tests/integration/real-user/` | No, explicit only | [sociable-method.md](references/sociable-method.md) (hierarchy section) |

Rungs 2 and 3 share vocabulary and are easy to confuse. The test is who
calls the model: in an agent *test* the product's code calls a model and
the suite checks the product; in an agent *eval* a model is the user of
the product's tools and the eval checks whether the tool surface led it
to the right result.

## Infrastructure that the hierarchy requires

The method dictates the setup, so the setup is part of the skill:

- bare `pytest` runs rung 1 only, configured in `pyproject.toml` so
  `tests/integration/` is ignored unless named;
- `make setup` bootstraps `.venv` with the editable install and dev
  extras; `make test` depends on it and runs the default suite, so a
  fresh clone runs tests with one command;
- the README or CONTRIBUTING Testing section documents each suite, its
  path, and its prerequisites, using commands that exist under exactly
  those names;
- a custom test-runner script is never introduced, and one that already
  exists must be stdlib-only, bootstrap the same venv, and stay additive.

Setup, template, checklist, and the runner rules:
[infrastructure.md](references/infrastructure.md). When a Makefile
target, a doc, and the real `pytest` behavior disagree, fix the
disagreement before adding anything.

## Routing table

| Task reaches... | Read |
|-----------------|------|
| Writing or reviewing unit tests; deciding what to mock; choosing between mocking at the network call and a local provider with real data; isolating config, data, and cache paths through env vars; conftest fixtures; test names; interface-layer tests; what a real-user suite is for | [references/sociable-method.md](references/sociable-method.md) |
| Setting up tests in a new repo; adding or auditing `make setup` / `make test`; pytest configuration; `tests/` layout; `.venv` and dev extras; writing or reviewing a Testing section; a repo whose Makefile, docs, and `pytest` invocation disagree; an existing `./runtests`-style script | [references/infrastructure.md](references/infrastructure.md) |
| Tests whose subject is the product's own model calls: predictability requirements, stripping ambient agent-CLI context, what does not belong in `tests/integration/agent/`, conftest and test examples | [references/agent-tests.md](references/agent-tests.md) |
| Checking whether an agent can use an MCP server's tools from their descriptions: isolating the agent, allowlisting only the server's tools, realistic under-specified prompts, fresh data per task, judging by end state, what to look for, and verified harness recipes for Claude Code and Antigravity CLI | [references/agent-evals.md](references/agent-evals.md) |

References are one level deep and self-contained; none depends on
another to be read first. Frameworks that ship their own test suite
(for example an MCP framework's auth and wiring conformance tests) add
to rung 1 and run in the default suite; their own documentation covers
them.
