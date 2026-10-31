---
type: llm
focus: trace
weight: 1
---

The integration suite is still reachable on purpose: the documented explicit command (a make target or an explicit pytest path) collects tests/integration/real-user/test_live_rates.py, and running it without the token fails loudly rather than being skipped or silently excluded.
