---
tags: [code-testing]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

add make targets and a Testing section for this Python repo. new contributors keep running `pytest` right after cloning and either hit the live-API tests in tests/integration by accident (they fail without a token) or don't have the dev deps installed. I want a fresh clone to be able to run the unit tests with one command, and the integration suite to be something you run on purpose.

Input files: pyproject.toml, README.md, .gitignore, ledger/__init__.py, ledger/core.py, tests/unit/conftest.py, tests/unit/test_core.py, tests/integration/real-user/test_live_rates.py
