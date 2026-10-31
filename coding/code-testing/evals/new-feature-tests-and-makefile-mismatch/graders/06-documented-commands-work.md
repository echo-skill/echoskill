---
type: llm
focus: trace
weight: 1
---

Every command in CONTRIBUTING.md's development-setup section works on a fresh clone as written: if it shows bare `pytest` after `make setup`, it also shows activating the venv (or uses .venv/bin/pytest), since pytest is installed only inside .venv.
