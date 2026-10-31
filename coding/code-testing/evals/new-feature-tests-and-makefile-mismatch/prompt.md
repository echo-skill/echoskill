---
tags: [code-testing]
max_turns: 40
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Add an `export` command to tally that writes every entry to a CSV file at a path the user gives (`tally export out.csv`), with tests. While you're in there: a new contributor followed CONTRIBUTING.md yesterday and the test setup step failed for them, so please make sure a fresh clone can actually run the tests the way the docs describe.

Input files: pyproject.toml, Makefile, CONTRIBUTING.md, .gitignore, tally/__init__.py, tally/core.py, tally/cli.py, tests/unit/conftest.py, tests/unit/test_core.py, tests/unit/test_cli.py
