---
type: llm
focus: trace
weight: 1
---

The rewritten suite fails when run against the original, unmodified notes/cli.py (it catches the seeded argument-order bug in the tag command), and at least one test reads the note's JSON file off disk independently of notes.core to verify what was persisted.
