---
type: llm
focus: trace
weight: 1
---

Tasks are phrased the way a user would (no parameter names, no tool names, no recipes), and each task gets its own fresh copy of a seeded data file via TINYKV_PATH so runs cannot interfere.
