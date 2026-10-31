---
type: llm
focus: trace
weight: 1
---

The rewritten unit tests do not patch or mock open, json, os.path, pathlib, or any function in notes.core; isolation comes from pointing NOTES_DIR at a temp directory.
