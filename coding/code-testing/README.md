# code-testing

Most unit test guides teach you to mock everything. This one teaches your agent to mock nothing, and then tells it which kind of test a situation actually needs.

`code-testing` is one skill for how a codebase is tested. `SKILL.md` is the map: a four-rung hierarchy (sociable unit tests, then agent tests of a product's own LLM features, then agent evals of an MCP tool surface, then real-user integration tests as a last resort) and when each applies. Each rung's method lives one level down in `references/`.

Sociable unit tests verify complete transactions through your business logic — the same code paths your users hit in production. Isolation comes from temp directories and environment variables, not from replacing half your system with fakes. The result: tests that actually catch integration bugs, the exact class of defects that mocked tests miss.

**What this skill covers:**

The map, in `SKILL.md`:
- Which kind of test a situation needs, and where each kind lives
- The one-paragraph sociable position, and the infrastructure the hierarchy requires

The method, in `references/sociable-method.md`:
- When to mock (uncontrollable or slow) vs when not to (controllable and fast)
- Boundary strategies: mock at the network call vs a local provider with real data
- Transaction-level test design for core/business logic and interface layers
- Test naming that describes behavior, not implementation

Python test infrastructure, in `references/infrastructure.md`:
- `tests/` layout and keeping integration suites out of bare `pytest`
- `.venv` bootstrap, dev extras, `make setup` / `make test` targets
- README / CONTRIBUTING Testing-section template and where testing docs belong
- Compliance rules for a repo's existing custom test-runner script

Agent tests, in `references/agent-tests.md`:
- Tests of a product's own LLM features: pinned model, controlled context, signal-based assertions

Agent evals, in `references/agent-evals.md`:
- Can an outside agent use an MCP server's tools correctly from their descriptions alone: isolate the agent, allow only the server's tools, fresh data per task, judge by end state; verified harness recipes for Claude Code and Antigravity CLI

Cross-platform — works with any AI agent that supports the SKILL.md format.

## Install

```bash
pipx install echomodel
em skills install code-testing
```

Or install directly with Gemini CLI:

```bash
gemini skills install https://github.com/echo-skill/echoskill.git --path coding/code-testing
```

## Evals

`evals/` holds test cases in the `claude plugin eval` layout. From the repo root:

```bash
claude plugin eval coding/code-testing --allow-tools Write,Edit,Bash --scaffold
```
