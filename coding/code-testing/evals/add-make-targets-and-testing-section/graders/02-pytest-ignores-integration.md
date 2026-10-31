---
type: llm
focus: trace
weight: 1
---

pyproject.toml has a [tool.pytest.ini_options] section (or equivalent config) so that bare `pytest` runs only tests/unit and excludes tests/integration by default.
