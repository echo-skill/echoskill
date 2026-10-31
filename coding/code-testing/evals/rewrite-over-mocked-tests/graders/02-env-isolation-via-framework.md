---
type: llm
focus: trace
weight: 1
---

Tests set the NOTES_DIR environment variable through the test framework's environment management (for example a pytest monkeypatch.setenv fixture, ideally autouse in conftest.py) rather than assigning to os.environ directly.
