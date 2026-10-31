---
tags: [code-testing]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Our test suite is green but we keep shipping bugs where the CLI and the core disagree (last week `notes add` wrote the tag to the wrong file and no test caught it). Please review tests/unit/ and rewrite the tests so they actually verify behavior. Don't change notes/ production code unless a test proves it's broken, and keep the suite fast and offline.

Input files: pyproject.toml, notes/__init__.py, notes/core.py, notes/cli.py, tests/unit/test_core.py, tests/unit/test_cli.py
