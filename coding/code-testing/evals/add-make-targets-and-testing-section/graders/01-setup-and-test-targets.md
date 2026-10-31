---
type: llm
focus: trace
weight: 1
---

The Makefile has a `setup` target that creates .venv and installs the project with its dev extras, and a `test` target that depends on `setup` and runs only the unit suite (not tests/integration).
