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
conversation, or a rule the user stated only in chat, is lost. Agent memory is
never where a fact is saved; when it disagrees with the data store, the data
store wins.

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
| **Structured but not tabular**, and small enough to read and rewrite whole on every change | JSON file, or the front matter of the entry file itself | a config-only file, preferences, a small set of nested settings |
| **Mostly prose** — the value is in the writing itself | Document (Google Docs) | research collected and extended over time, an essay or book draft |

- **Spreadsheets** suit data that grows by adding records. Adding a row doesn't
  mean rewriting the whole file, and the user can filter, sort, and edit rows
  in a familiar interface.
- **JSON** suits nested or key/value data that stays small. Reading and
  rewriting the whole file on each change is fine at config size. It's the
  wrong choice for anything that grows without limit: a log kept for years
  belongs in a spreadsheet. Updating the same file keeps its revision history.
  A handful of settings can live in the entry file's front matter instead of
  a separate file.
- **Read JSON and YAML as raw content.** Storage services often record them
  as a binary type, and some connectors' read-as-text tools refuse them or
  reformat them. Download the file's raw bytes instead.
- **Documents** suit prose. Don't force records into paragraphs or narrative
  into cells. Edit documents section by section (insert or replace) rather
  than regenerating them, so the user's own edits survive.
- **Mixed data gets split by shape.** A research skill might keep its
  write-up in a document and its list of sources in a spreadsheet, each tagged
  with its own role.
- If the shape is unclear, ask the user. Switching formats later means
  migrating the data.

## Discovery convention

Every data-backed skill owns one **entry file**: `<skill-name>.skill-data.md`,
named with the skill's exact `name`. It is the one file a skill has to find
without already knowing an ID; everything else is opened by the IDs it lists.
File IDs survive renames and moves, so the user can reorganize freely.

Why a file rather than a file property: stock cloud connectors (the ones an
agent platform ships, as opposed to a custom one) commonly search files by
title and full text but not by custom properties, while they can see the
whole drive. A name plus a marker line works through all of them.

### What it holds

Markdown with YAML front matter, the same shape as `SKILL.md`:

```markdown
---
kind: SkillData
version: 1
skill-data: <skill-name>
files:
  <role>:
    id: <file id>
    name: <title when created>      # for people; never used to find the file
settings:                           # optional: a few small per-user settings
  <key>: <value>
---

# <skill-name> skill data

This file tells the <skill-name> skill where its data is. The skill finds it
by its name or by the `skill-data: <skill-name>` line above, then opens the
files listed by ID. Please don't rename, trash or edit this file by hand.
```

- `kind` declares the format; `version` lets it change later.
- The `skill-data:` line is the **marker**: it finds the file even after a
  rename.
- Roles (`data`, `config`, `log`, `attachments`, …) are the keys under
  `files:`, so filenames stay free for people.
- Secrets never go here, or anywhere in skill data.

### Finding it

1. Search the user's storage for the exact title
   `<skill-name>.skill-data.md`, **or** for files whose full text contains
   `skill-data: <skill-name>`.
2. **Confirm every hit by reading it.** Full-text search matches loosely and
   returns unrelated files; keep only a file whose front matter says
   `kind: SkillData` and `skill-data: <skill-name>`.
3. One confirmed file: use it for the session. More than one: ask which is
   authoritative; don't guess. None: see "Provisioning".
4. **Read it as raw content** (download its bytes), not through a
   read-as-text tool: a text rendering may escape the Markdown, drop the
   indentation the front matter depends on, or return an older revision.

**Fallback for older stores:** if nothing is found and the tools can query
custom file properties, search by the public property
`skill-data=<skill-name>` (plus `skill-data-role=<role>`), as earlier
versions of this convention did. When that finds files, offer to create the
entry file listing them.

### Optional lock

Where the tools can set the storage service's own file lock (Google Drive:
the file's read-only content restriction), lock the entry file: it then
can't be renamed or edited by accident. To change it, unlock, edit, lock
again. A skill never fails, stops or asks because a lock can't be set.

### Files several skills share

The entry files of several skills may list the same data file. One skill
owns it and is the only one that writes it; the others only read it.

### Where files live

Prefer one parent folder for all skill data, with one subfolder per skill, so
a file is never loose where it could be deleted or edited by mistake. No
storage UI shows properties, so a loose file looks like any other.

| Folder | Key | Value |
|---|---|---|
| the parent of all skill data | `skill-data-role` | `root` |
| one skill's folder, inside the parent | `skill-data-folder` | the skill's `name` |

Placement is best effort. The entry file is what finds the data later, so a
skill never fails, stops, or asks just because it can't reach, create, or tag
a folder. Folders never carry `skill-data`, so a property query never returns
a folder. `root` is reserved as a role. The entry file goes in the skill's
folder.

The convention needs only title and full-text search plus raw download, which
most storage connectors offer (Google Drive, OneDrive/SharePoint, Dropbox).
Where a provider has queryable custom metadata, it is an extra fallback, not
the primary lookup.

### Declare the binding in the skill

Use the spec's `metadata` field so any agent reading the skill knows where its
data lives without parsing prose:

```yaml
metadata:
  data-store: google-drive
  data-entry: "<name>.skill-data.md"
```

### Tabs and sections inside a file

Within one format, prefer **one file with several sections** over several
files when the data has the same audience and sharing settings. That means one
place to look and fewer moving parts. Sections are spreadsheet tabs,
document tabs or headings, or top-level keys in a JSON file. Use separate files
when sharing settings, formats, or sizes differ.

Users can rename tabs and headings, so prefer metadata inside the file over
titles. Where the connected tools can read and write it (e.g. Sheets developer
metadata), tag each section `skill-data-role=<section-role>` and find it by that
tag. Where they can't, find it by title. The skill states both: the tag it
applies and the title it falls back to. When a title lookup finds an untagged
section and the tools can tag it, tag it then. If neither lookup finds the
section, ask rather than create a new one.

## Provisioning — find, then ask, then create

1. Find the entry file (see "Finding it"). Exactly one confirmed match → use
   it for the session.
2. Multiple confirmed matches → ask which is authoritative. Don't guess.
3. No match in **any** connected account or drive → **stop and ask**: point me
   at existing files (then create the entry file listing them), or create
   fresh ones. **Never scaffold over data you merely failed to find** — an
   empty store that looks like the real one is worse than stopping.
4. When creating: build each data file in the format the skill specifies,
   write its initial structure exactly as the skill defines it (column
   headers, JSON skeleton, or document headings), then create the entry file
   listing them by ID. Create Markdown and JSON as plain files, not converted
   to the provider's document format. Put them in the skill's data folder
   when the tools allow (see "Where files live"), lock the entry file where
   possible, and tell the user where it landed.

## Writing

- **Update in place.** Revision history on the same file ID is the version
  store. Never delete-and-recreate a file to "update" it.
- **Check that the tools can replace a file's content in place** before
  choosing where changing data goes. Some stock connectors can create files
  and change their name, folder or lock, but not their content. Keep the entry
  file mostly fixed (IDs rarely change), and put data that changes often in a
  spreadsheet or document, which such connectors usually can edit. If a write
  is impossible with the tools at hand, say so rather than recreate the file.
- Confirm before destructive changes (removing rows, tabs, or files).
- If the tooling forces a history-destroying write, say so before writing.

## Attachments (images, receipts, scans)

Keep attachments in the user's cloud storage and link to them from the record,
so they survive the conversation they were shared in.

- **Storage:** one attachments folder per skill, listed in the entry file
  under `files:` → `attachments` (by folder ID), next to the main data file
  (`data`). A record with 2+ attachments gets its own subfolder, and the record links the
  subfolder. When a second attachment arrives, move the first into it. Links use
  file IDs, so renames and moves don't break them.
- **Where the link goes:**
  - Attachments are **routine** for the table (e.g. a receipt per transaction) →
    a dedicated link column (one file, or the record's folder).
  - Attachments are **rare exceptions** → link inline in the record's free-text
    field (notes, comments, description), next to the text it relates to, if
    the tools support inline links.
  - The tools support only whole-cell links and the text needs more than one
    link or other text → store the URL(s) as **plain text** in that field.
    Convert to inline links when the record is next edited, once supported; no
    bulk backfill.
  - Documents: inline links. JSON: a URL field.
- **Can't upload** (tooling or sandbox limits) → ask the user to save the file
  to their cloud storage, then link it.

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

Promote only **lasting** rules. A lasting rule is about how things should always
be done ("whenever", "never", "that's noise"). A one-off is about the thing in
front of you ("give me that again", "use 3000K for this one"). Writing a one-off
into the skill clutters it; treating a lasting rule as a one-off makes the user
repeat it.

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
  data-entry: "<name>.skill-data.md"
---

# <Title>

## Objective
Nothing of value from any session may be lost. The data store holds all
records; this skill holds all process. Chat and agent memory are not storage.

## Locating the data
<find `<name>.skill-data.md` by name or marker, confirm by front matter, read
it raw, open files by the IDs it lists; fallback: the `skill-data` property;
then ask; never scaffold over unfound data; new files go in the skill's data
folder when the tools allow>

## Structure
<each file: format and why, role, sections (tabs, headings, or keys),
columns or fields and what each means, how dates work>

## Conventions
<capture obligations above, plus domain-specific rules>

## Workflows
<adding, updating, correcting, reviewing records>

## Known tooling gaps
<each capability the skill relies on that some tools lack, written as a check
with a fallback — "if the tools can't X, do Y" — never as a claim about what
today's tools can't do>
```

## Design decisions

- An entry file found by name or marker, not a file property: stock
  connectors search by title and full text but not custom properties, so a
  property-only convention locked skills to custom connectors. The name makes
  it self-describing; the marker survives a rename; the front-matter check
  rules out loose full-text matches.
- Markdown with YAML front matter, because `SKILL.md` already uses that
  standard, people can read it, and connectors read Markdown as text. `kind`
  and `version` declare the format; no new file extension, which providers
  would store as an unreadable binary type.
- The key is `skill-data`, a neutral name, not a vendor- or project-branded
  one: don't borrow a namespace you don't own.
- Roles live in the entry file, not the filename, because filenames are
  user-editable.
- Where properties are still used (the fallback), they are public, not
  app-private, so every agent and client can see them.
- No pattern-version stamps in child skills: children are identifiable by their
  `data-store` / `data-entry` metadata, which is enough to find and update
  them.
- How a child's own source gets updated and versioned stays here, not in each
  child.
- Deferred until a real case needs them: seeding a new store from scattered
  existing data, revision expiry on non-native files (e.g. JSON), resurfacing
  open items, concurrent-edit protection.
