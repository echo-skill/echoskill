---
type: llm
focus: trace
weight: 1
---

The eval plan or run uses a headless agent session that sees only the tinykv server started from the working tree (a server-only MCP config, e.g. a strict mcp config in a scratch directory), allows only tinykv's tools, and denies shell and file-write tools.
