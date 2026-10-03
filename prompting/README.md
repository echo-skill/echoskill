# Prompting

General-purpose session workflow skills: capturing context before a
session ends, extending documents safely, deferring topics, and reviewing
how a session went.

## Skills in this collection

| Skill | Purpose |
|-------|---------|
| [`capture-context`](capture-context/) | End-of-session audit and handoff: catalog completed work, surface unresolved items, propose durable capture destinations, and ensure nothing from the session is lost before exit. |
| [`extend-document`](extend-document/) | Safely append or integrate new content into an existing document without losing original content. Use when adding research findings, session notes, or new sections to an existing `.md` file. |
| [`for-later`](for-later/) | Cheap, non-disruptive capture of a topic the user wants to defer until later in the session. Records without analysis, continues in-flight work uninterrupted, and resurfaces the item at natural review points for disposition. |
| [`retrospective`](retrospective/) | End-of-session workflow analysis: timeline of errors and retries, skill and tool effectiveness audit, project documentation gaps, external knowledge dependencies, permission anomalies, and concrete improvement recommendations. |

## A note on organization

The name `prompting/` originally described "skills invoked via slash
commands" — which is true of the skills here but also true of almost any
skill. The skills currently in this collection share a more
specific theme: they're **generic cross-cutting workflow tools** that
don't belong to any specific domain (coding, consulting, etc.). If this
repo ever reorganizes its collections around subject matter rather than
invocation style, the contents of `prompting/` would likely move into a
collection named something like `workflow/` together. Until then, this
is the general-purpose home for non-domain-specific workflow skills.
