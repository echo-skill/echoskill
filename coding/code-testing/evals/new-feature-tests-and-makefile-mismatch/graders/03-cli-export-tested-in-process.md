---
type: llm
focus: trace
weight: 1
---

A test invokes the CLI export command in-process (tally.cli.main([...])) and asserts on the resulting file, without subprocess and without mocking core.
