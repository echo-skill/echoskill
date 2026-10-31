# The sociable testing method

Part of the `code-testing` skill. This file is the unit-testing method:
what to mock and what not to, how to isolate through the environment
instead of through fakes, the two boundary strategies, and how to shape
and name transaction-level tests. The testing hierarchy that decides
*which kind* of test a situation needs is in SKILL.md; the Python
project setup that makes this suite the default is in infrastructure.md.


## Background: Sociable vs Solitary

Jay Fields coined the terms "sociable" and "solitary" for
two schools of unit testing. Martin Fowler popularized them:

- **Solitary tests** isolate the unit under test using mocks
  or test doubles for all collaborators. The classically
  "mockist" approach.
- **Sociable tests** let the unit interact with real
  implementations of its collaborators. Isolation comes from
  controlling inputs and the environment, not from replacing
  internal code with fakes.

Fowler presents both as valid. This skill does not.

## This Skill's Position

**Write sociable tests. Avoid solitary tests.**

The unit of testing is a **meaningful transaction** — a
complete operation through the business logic layer (SDK,
core, lib, domain, service — whatever the project calls it),
not an individual function or module in isolation.

**No mocks unless you ask.** Isolate via temp dirs and env
vars, not by replacing collaborators with fakes.

Micro-isolating tests to a function or module that alone
cannot complete a meaningful transaction produces broad
swaths of technical-sounding tests where it becomes difficult
to assess what actual functionality is or isn't covered. When
a test mocks every collaborator, it verifies that your code
calls the mocks correctly, not that it works. The findings
are over-isolated to the point of risky irrelevance: all
tests pass, but the system is broken at the seams.

This approach leads to repo pollution and bloat — hundreds of
tests that are expensive to maintain, tightly coupled to
implementation details (not behavior), and fragile to
refactoring. Renaming an internal method breaks dozens of
tests that were never verifying user-facing behavior in the
first place.

Reserve mocking for system boundaries where real
collaboration is impractical — network calls, external
services, clocks. Everywhere else, let the code run.

## Testing Hierarchy

Bias strongly toward sociable unit tests. Cover everything
possible as fast, offline, deterministic unit tests before
reaching for any form of integration testing.

1. **Sociable unit tests** — the default. Every repo should
   have these. Cover all business logic through the core layer
   and interface layers using in-process testing (no network,
   no credentials, no external systems). This is where the
   vast majority of test value lives.

2. **Agent integration tests** (`tests/integration/agent/`) —
   add only when the repo's functionality involves LLM
   inference that needs behavioral verification. Keep them
   minimal, maximally reliable, and controlled. Do not look
   for opportunities to add agent tests to every project.

3. **Real-user integration tests** (`tests/integration/real-user/`)
   — last resort. Add only when the repo's core functionality
   depends largely or entirely on an external system that can
   only be tested with real, private user accounts that are
   not reusable across developers. Examples: proxying a
   third-party API with no sandbox environment, wrapping a
   platform where each developer must supply their own
   credentials and account data. Avoid entirely if unit tests
   with a local provider or contract testing can cover the
   same ground.

## What to Mock vs What NOT to Mock

The principle: **use the real thing when it's controllable and
fast. Mock when it's uncontrollable or slow.** These two
properties almost always go together, but not always — a local
database is controllable but slow to spin up, so it belongs in
integration tests, not unit tests.

**Mock (uncontrollable or slow):**
- Network calls (APIs, HTTP, external services)
- System clocks (if time precision matters)
- Heavy external processes (database servers, containers)

**Don't mock (controllable and fast):**
- File system operations — point at a temp dir instead
- Configuration parsers — write real config files to temp dirs
- Environment variables — set the real env var and revert it
  when the test ends. Use your test framework's built-in env
  management (e.g., `monkeypatch.setenv()` in pytest) rather
  than raw env manipulation with manual cleanup — the
  framework guarantees revert even if the test throws, and
  handles parallel execution safely. This is not mocking; the
  real environment is modified and restored.
- Core layer methods called by interface layers
- Ubiquitous CLI tools that are either too common to mention
  as prerequisites (e.g., `git`) or are documented project
  dependencies — run them for real against isolated temp dirs

## Choosing a Boundary Strategy

When setting up tests for a project, there are two valid
approaches to handling external dependencies. Choose one and
use it consistently.

**Option A: Mock at the network call.** Stub or patch the HTTP
client so the core layer's own code runs fully but never hits
the wire. Simpler when the core layer is a thin wrapper around
an API.

**Option B: Local provider with real data.** Build an
alternative backend (e.g., an in-memory store, a local
database, a file-backed provider) that implements the same
interface as the real provider. Tests run against real data
through real code paths — no patching at all. This eliminates
the network boundary entirely rather than mocking it.

**When to prefer Option B:**
- The core layer has a provider/repository abstraction already
- Multiple test files need the same realistic data set
- You want to test filtering, sorting, and aggregation logic
  without maintaining mock response fixtures per test
- The project already uses this pattern — continue it

**If existing tests already follow one pattern, continue that
pattern.** Consistency within a repo matters more than
theoretical preference. Do not introduce Option A into a repo
using Option B or vice versa without explicit approval.

The local provider pattern is a form of what Martin Fowler calls
**narrow integration testing** — exercising the code that would
talk to an external service, but with the boundary replaced
entirely. The seed data that the local provider serves is
effectively an informal **contract** — a captured representation
of the external API's response shape. For repos that proxy
third-party platforms, consider periodically verifying that the
seed data still matches the real API shape (this is the core
idea behind **contract testing**, formalized by tools like Pact).

## Environment Variable Isolation

Every project that reads from config or data directories must
support env var overrides for those paths. Tests use these to
redirect to temp directories.

**Pattern (Python example):**

```python
# In the core layer (config.py or similar):
def get_config_dir() -> Path:
    path_str = os.environ.get("MY_APP_CONFIG_DIR")
    if path_str:
        return Path(path_str)
    return Path.home() / ".config" / "my-app"
```

```python
# In conftest.py:
@pytest.fixture(autouse=True)
def isolate_config(tmp_path, monkeypatch):
    """Auto-isolate every test from real config directories."""
    test_config = tmp_path / "config"
    test_config.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("MY_APP_CONFIG_DIR", str(test_config))
```

Key points:
- `autouse=True` — applies to every test automatically
- `tmp_path` — unique per test, auto-cleaned
- `monkeypatch.setenv()` — auto-reverted when test ends, no
  cross-test leakage, no impact on parallel suites. Safer than
  raw `os.environ` manipulation.
- Place in `conftest.py` — central, no imports needed per test

**Isolate ALL writable paths:** config, data, cache, XDG
directories. If the core layer writes to it, tests must
redirect it.

## Local Provider Pattern (Option B)

When using a local provider for testing (Python example):

```python
# conftest.py
@pytest.fixture
def test_db_path(tmp_path):
    """Copy test data to temp directory."""
    src = Path(__file__).parent / "fixtures" / "test_data.json"
    dest = tmp_path / "test_data.json"
    shutil.copy(src, dest)
    return dest

@pytest.fixture
def local_provider(test_db_path):
    """Create a local provider with test data."""
    provider = LocalProvider(db_path=test_db_path)
    yield provider
    provider.close()
```

Seed data lives in `tests/unit/fixtures/` — either a static
file or generated from a seed file by a script. The seed file
is the only file that needs human review; generated data is
gitignored.

## Core-Layer-First Testing

All business logic lives in the core layer. CLI, MCP, REST,
and other interfaces are thin wrappers.

**Test the core layer directly** — don't test through interface
layers when verifying business logic.

```python
# Good: test core layer directly
def test_add_command_creates_config(tmp_path, monkeypatch):
    monkeypatch.setenv("MY_APP_CONFIG_DIR", str(tmp_path))
    result = core.add_command("fix", "Fix the bug")
    assert (tmp_path / "commands" / "fix.toml").exists()

# Bad: test through CLI subprocess
def test_add_command_cli(tmp_path):
    result = subprocess.run(["my-app", "cmds", "add", ...])
    # Slower, harder to isolate, tests CLI parsing not logic
```

## Interface Layer Tests

Thin, in-process tests for CLI, HTTP/REST, MCP, or other
interface layers. No out-of-process calls, no network traffic.
These verify wiring and request/response shape, not business
logic.

Examples:
- **HTTP/ASGI**: in-memory test client (e.g., httpx
  `ASGITransport` in Python, supertest in Node)
- **CLI**: built-in test runner (e.g., Click's `CliRunner` in
  Python, commander's programmatic API in Node)
- **MCP**: stdio protocol over pipes or in-process invocation

Interface tests belong in `tests/unit/` alongside core layer
tests — they're fast, deterministic, and need no credentials.

## Test Complete Transaction Flows

Test the full flow of a feature, not individual functions in
isolation.

Example: testing a "label email" feature:
1. Search for target email — confirm it exists without the label
2. Read email details (before) — assert label absent
3. Apply label — execute the operation
4. Read email details (after) — assert label present, other
   fields unchanged

This catches integration bugs between steps that isolated
function tests miss.

## Test Names

Test names describe **scenario + outcome**, not implementation
details.

Good:
- `test_not_installed_when_no_hooks_path`
- `test_refuses_to_overwrite_foreign_hook`
- `test_init_creates_manifest_and_dockerfile`
- `test_logs_food_to_current_date_directory`

Bad:
- `test_returns_false_when_file_missing`
- `test_respects_config`
- `test_returns_true`

