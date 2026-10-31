---
tags: [code-testing]
max_turns: 40
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

before we ship tinykv I want to know whether an agent can actually use these tools correctly from their descriptions alone. it's a small stdio MCP server (tinykv/server.py, run with `python -m tinykv`, data file set by TINYKV_PATH). I'm most worried about `remove` and `put` doing the wrong thing. check it and tell me what to fix.

Input files: pyproject.toml, README.md, tinykv/__init__.py, tinykv/__main__.py, tinykv/server.py, tinykv/store.py, tests/unit/test_store.py
