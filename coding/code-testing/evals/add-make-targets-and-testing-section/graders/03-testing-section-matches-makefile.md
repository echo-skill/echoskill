---
type: llm
focus: trace
weight: 1
---

README.md has a Testing section whose commands all work from a fresh clone exactly as written: every make target it names exists in the Makefile under that name, and any bare `pytest` it shows is preceded by activating the venv or is written as .venv/bin/pytest. It shows how to run unit tests from a fresh clone and lists the integration suite with its path, its prerequisite (the API token), and the explicit command to run it.
