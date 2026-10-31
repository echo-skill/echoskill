---
type: llm
focus: trace
weight: 1
---

Tests for export record real entries through core against the temp TALLY_DIR, call export to a path under tmp_path, then read the CSV back and assert on its header and rows; they do not mock csv, open, pathlib, or any core function.
