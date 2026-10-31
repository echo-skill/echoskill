# Agent Tests

Part of the `code-testing` skill. Agent tests check a **product's own LLM
features**: the prompts, model calls, and tool wiring the product ships,
exercised by the product's test suite under `tests/integration/agent/`.
They are not agent evals. An agent eval asks the opposite question: can an
*outside* agent, knowing nothing but the tool names and descriptions,
drive this product's MCP tool surface correctly? That method, with its
harness recipes, is in [agent-evals.md](agent-evals.md). Use this file
when the code under test calls a model; use agent-evals.md when a model
is the user of the code under test. Most repos need neither; read this
only when the repo's functionality involves inference whose behavior
needs automated verification.

Agent tests follow the sociable unit testing philosophy from
SKILL.md — no mocks of internal collaborators, test complete
transactions, meaningful assertions — with one exception:
inference calls to an LLM are inherently non-deterministic, so
assertions check for reasonable signals rather than exact
outputs.

This section is optional. Most repos do not need agent tests.
Use this when a repo tests AI inference behavior and prompts
are expected to produce reliable, testable outputs.

## Requirements for Predictability

- **Known model version** — pin the model in the test, not in
  ambient config
- **Identical prompt and context each run** — no user-scoped,
  machine-scoped, or project context files that aren't fully
  controlled by the test
- **No tool calls to external services or user-specific data**
  — stub or mock all data backends with test fixtures
- **Assert on reasonable signals, not exact strings** — check
  that expected data appeared, a tool was called, or output
  contains key indicators

## Agent CLI Ambient Context

When testing via an agent CLI program (e.g., `claude -p`,
`gemini -p`) rather than a direct API call, these programs
load user-scoped and machine-scoped context by default —
global context files, plugin hooks, MCP registrations, shell
environment. Tests **must** disable all ambient context so the
only context the model sees is what the test explicitly
provides. For example, `claude --bare` strips all user and
project context.

## What Does NOT Belong in tests/integration/agent/

Tests where the model makes tool calls to services backed by
shifting data, user-specific accounts, or configurations that
vary across contributors. Those belong in
`tests/integration/real-user/` or are not suitable for
automated testing.

## Excluded from Default Test Runner

Agent tests require connectivity and API key env vars. They
are excluded from default `pytest` and documented in the
README alongside other integration suites.

```bash
pytest tests/integration/agent/
```

## Example Pattern

```python
# tests/integration/agent/conftest.py
import shutil, os, pytest

_HAS_KEY = bool(os.environ.get("ANTHROPIC_API_KEY"))
requires_api_key = pytest.mark.skipif(
    not _HAS_KEY, reason="ANTHROPIC_API_KEY not set"
)

@pytest.fixture
def mcp_config(tmp_path):
    """MCP config with stub backends only."""
    config = {"mcpServers": {
        "my-app": {"command": "my-app-mcp", "args": ["stdio"]},
        "stub-backend": {"command": "python", "args": ["tests/stubs/backend.py"]},
    }}
    path = tmp_path / "mcp.json"
    path.write_text(json.dumps(config))
    return str(path)
```

```python
# tests/integration/agent/test_prompts.py
@requires_api_key
def test_tool_invocation(mcp_config):
    result = subprocess.run(
        ["claude", "--bare", "--mcp-config", mcp_config,
         "-p", "List items with a balance over 500"],
        capture_output=True, text=True, timeout=120,
    )
    assert result.returncode == 0
    # Assert on signals, not exact output
    assert "500" in result.stdout or "balance" in result.stdout.lower()
```
