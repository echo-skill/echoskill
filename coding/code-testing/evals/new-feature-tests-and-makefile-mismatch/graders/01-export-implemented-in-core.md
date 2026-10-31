---
type: llm
focus: trace
weight: 1
---

The export behavior (writing all entries as CSV rows to a caller-supplied path) is implemented in tally/core.py, and tally/cli.py only parses the argument and calls core.
