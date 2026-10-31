---
type: llm
focus: trace
weight: 1
---

CLI tests call the CLI entry point in-process (e.g. notes.cli.main([...])) against the same temp directory, not via subprocess, and do not mock notes.core.
