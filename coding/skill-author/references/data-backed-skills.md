# Data-Backed Skills

A **data-backed skill** exists to capture and maintain a body of user data
across sessions — a log, an inventory, a tracker, a body of research, a
piece of writing in progress — that the user
will revisit, revise, and extend over time. The skill is the *process*; one or
more cloud files are the *data*.

## Objective — and whose responsibility it is

**Nothing of value may be lost if any session ends, any agent's memory is
wiped, or the user switches agent vendors.** Only two stores count as durable:

| Store | Holds | Durable because |
|---|---|---|
| **Data files** in the user's cloud storage | every fact, record, note, decision about the data | revision history, reachable from every surface |
| **The skill**, versioned in git or dotfiles | every process, convention, rule, and refinement | version control, installable on any agent |

Chat history and agent memory are **not** storage. A fact that exists only in a
conversation, or a rule the user stated only in chat, is lost.

The skill — not the user — is responsible for enforcing this. Every data-backed
skill must carry these obligations in its own body so any agent that loads it
inherits them.

## When to create one

Propose a data-backed skill when a session starts producing records the user
will want to revisit: they're logging things, correcting earlier entries,
attaching sources, or saying "keep track of this." Propose; don't silently
generate. Check first whether an existing skill should own the data instead.

## Choosing a file format

Choose each file's format by the shape of its data, not by habit. A skill may
own files of different formats; give each its own `skill-data-role`.

| Data shape | Format | Examples |
|---|---|---|
| **Tabular** — many records with the same fields, growing over time | Spreadsheet (Google Sheets) | a daily log kept for years, an inventory, a register |
| **Structured but not tabular**, and small enough to read and rewrite whole on every change | JSON file | a config-only file, preferences, a small set of nested settings |
| **Mostly prose** — the value is in the writing itself | Document (Google Docs) | research collected and extended over time, an essay or book draft |

- **Spreadsheets** suit data that grows by adding records. Adding a row doesn't
  mean rewriting the whole file, and the user can filter, sort, and edit rows
  in a familiar interface.
- **JSON** suits nested or key/value data that stays small. Reading and
  rewriting the whole file on each change is fine at config size. It's the
  wrong choice for anything that grows without limit: a log kept for years
  belongs in a spreadsheet. Updating the same file keeps its revision history.
- **Documents** suit prose. Don't force records into paragraphs or narrative
  into cells. Edit documents section by section (insert or replace) rather
  than regenerating them, so the user's own edits survive.
- **Mixed data gets split by shape.** A research skill might keep its
  write-up in a document and its list of sources in a spreadsheet, each tagged
  with its own role.
- If the shape is unclear, ask the user. Switching formats later means
  migrating the data.

## Discovery convention

Locate data files by a **public custom file property**, never by hardcoded ID,
title, or path. The user may rename or move files freely.

| Key | Value | Required |
|---|---|---|
| `skill-data` | the skill's `name` | always, on every file the skill owns |
| `skill-data-role` | the file's role (`data`, `config`, `reference`, `log`, …) | only when the skill owns 2+ files |

- One query finds everything a skill owns:
  `properties has { key='skill-data' and value='<name>' } and trashed = false`
- Add a role condition to find one exact file. Roles live in a property, not
  the filename, because filenames are user-editable.
- Use **public** properties (visible to any client), not app-private ones. The
  skill runs through different agents and OAuth clients; private properties are
  invisible to all but the writer.
- A file may belong to only one skill (one key, one value). If two skills need
  the same data, one owns it; the other reaches it through the owner.
- Keep keys and values short — most providers cap property size (Google Drive:
  124 bytes per key+value).
- **Migrating from a legacy key:** properties merge, so tag files with both the
  old and new keys, update the skill, then remove the old key.

This is written against Google Drive custom file properties. For other
providers, use the equivalent queryable metadata (e.g. OneDrive/SharePoint
custom columns, Dropbox file properties/templates); if none exists, discover by
a pointer file at a well-known path and say so.

### Declare the binding in the skill

Use the spec's `metadata` field so any agent reading the skill knows where its
data lives without parsing prose:

```yaml
metadata:
  data-store: google-drive
  data-selector: "skill-data=<name>"
```

### Tabs and sections inside a file

Within one format, prefer **one file with several sections** over several
files when the data has the same audience and sharing settings. That means one
place to look and fewer moving parts. Sections are spreadsheet tabs,
document tabs or headings, or top-level keys in a JSON file. Use separate files
when sharing settings, formats, or sizes differ.

Find tabs and headings by title until the tooling supports metadata inside the
file (e.g. Sheets developer metadata tagged `skill-data-role=<tab-role>`).
Record in the skill which lookup method it currently uses. Users can rename
tabs and headings, so if a title lookup fails, ask rather than create a new
section.

## Provisioning — find, then ask, then create

1. Search by the property. Exactly one match → use it for the session.
2. Multiple matches → ask which is authoritative. Don't guess.
3. No match → **stop and ask**: point me at an existing file (then tag it), or
   create a fresh one. **Never scaffold over data you merely failed to find** —
   an empty store that looks like the real one is worse than stopping.
4. When creating: build the file in the format the skill specifies, write its
   initial structure exactly as the skill defines it (column headers, JSON
   skeleton, or document headings), tag it, and tell the user where it landed.

## Writing

- **Update in place.** Revision history on the same file ID is the version
  store. Never delete-and-recreate a file to "update" it.
- Confirm before destructive changes (removing rows, tabs, or files).
- If the tooling forces a history-destroying write, say so before writing.

## Capture obligations (embed in every data-backed skill)

1. **Capture continuously**, as facts arrive — not only at session end.
2. **Lose no detail** of anything the user provides: keep their text verbatim
   (in a notes column or field if it doesn't fit the structure), with its source and
   timestamps. Paraphrase is loss.
3. **Label agent-generated content** — suggestions, observations, inferences —
   as the agent's, with a date, so it's never mistaken for the user's facts.
4. **Flag unconfirmed inferences** explicitly; downgrade stated certainty when
   the evidence is circumstantial.
5. **Keep dates honest**: a record's as-of or effective date must correspond to
   the facts in that record. Update both together.
6. **No empty records**: don't create entries that carry no substantive data
   about the thing tracked. To-dos without specs are not records.
7. **Personal and sensitive data stays in the data store**, never in the skill.

## Promote refinements immediately

When the user sets a rule, preference, or correction, write it down *now*:

- **Generic process** (how records are structured, how notes are kept) → the
  skill's `SKILL.md`, then version it.
- **Personal specifics** (their preferences, names, places, identifiers) → the
  data store (a `skill-data-role=config` file, often a small JSON file, or a
  `Config` tab in an existing spreadsheet).

A rule the user had to state twice is evidence one of these writes was missed.

## Close-out audit

Before a session ends (or on request), compare the conversation against the
data store and the skill. List anything decided, provided, or refined that
isn't captured in one of them, and capture it. The `capture-context` skill, if
available, performs this audit in detail.

## Versioning the skill itself

A data-backed skill is usually **Patterned** or **Bespoke** (see "Reuse tiers"
in `SKILL.md`), so it often does not belong in a public marketplace. It must
still be versioned somewhere durable — see "Choose where the skill is
versioned" in `SKILL.md`. An installed-only copy is a single point of failure.

## Child skill skeleton

```markdown
---
name: <name>
description: >-
  <What the data is and when to use it — log, update, review, revise …>
metadata:
  data-store: google-drive
  data-selector: "skill-data=<name>"
---

# <Title>

## Objective
Nothing of value from any session may be lost. The data store holds all
records; this skill holds all process. Chat and agent memory are not storage.

## Locating the data
<property query; fallback: ask, then tag; never scaffold over unfound data>

## Structure
<each file: format and why, role, sections (tabs, headings, or keys),
columns or fields and what each means, how dates work>

## Conventions
<capture obligations above, plus domain-specific rules>

## Workflows
<adding, updating, correcting, reviewing records>

## Known tooling gaps
<current limitations and the fallback used>
```
