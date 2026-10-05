# Per-User Config & State: Where It Lives

Load this reference when a skill needs per-user configuration, must remember
resolved state (account ids, which thing is which, user preferences), or needs
a "load settings" seam so adopters can substitute backends without editing
skill logic.

For skills whose primary purpose is to capture and maintain durable user data
across sessions (inventories, logs, trackers, bodies of research, or writing),
also see `references/data-backed-skills.md` in this skill.

---

## Core Design Seams

When a skill needs per-user configuration or must remember resolved state,
decide *where* that lives deliberately. Present the applicable options to the
user when it matters; don't reach for a heavy store by default.

### Default, don't bind

State an opinionated skill's approach (a specific tool/backend/dependency — "I
use Google Drive"; "the Downloads folder, i.e. `~/Downloads` on macOS") as a
*default*, not a hard binding. Write the load-settings seam wide enough that an
adopter can substitute the backend with low churn — resolved at runtime by
discovery or a short dialogue, or supplied in their own context file at
whatever scope.

Structure it for **accreting examples**: work one provider concretely and
*name* the alternatives even before they're fully worked, so an OneDrive /
Dropbox / Ubuntu / Windows user isn't shut out on day one (the seam says "for
others, discover or ask"); add same-depth hints for the rest over time without
rewriting. This is what makes a Patterned skill genuinely promotable. Bound it
with the reuse-value check: build substitutability only where
adopter-substitution is plausible (Patterned/Generic, not Bespoke), and keep it
*cheap to discover*, not pre-built for every backend — over-generalizing every
skill into infinite pluggability is its own failure mode.

### Discover or seed (provision, don't just read)

Resolve settings by discovery first. When a durable store is genuinely needed
and absent, create it at the scope matching the skill's install scope — an
agent context file (`CLAUDE.md`/`GEMINI.md`/`CONTEXT.md`) or an XDG config file
— and seed it in dialogue with the user, then update it as conventions evolve.
Bounded: prefer discovery, confirm before writing, match scope to
applicability, never speculatively over-write.

For a skill whose store may be cloud (tier 4) or local (tier 2), resolve the
location once per session, in this order:

1. A location already known this session wins;
2. Else, if the cloud connector can search by property and update in place,
   search by the `skill-data` property and — if nothing is found — propose
   creating the file there;
3. Else, if the filesystem is reachable, use the XDG path and propose creating
   it there;
4. Else stop and say which to set up.

Never silently fall back to a weaker lookup (e.g. by filename) or invent a
third store. Treat cloud and local as alternatives, not mirrors.

---

## Principles

- **Prefer discovery over storage.** If a fact is re-derivable from the
  system-of-record at runtime, derive it instead of storing it. Discover by
  **structural signals** (types, subtypes, status, recent activity), **not by
  user-chosen names/labels** — names are themselves user-specific config, so
  matching on them just relocates the problem. Discovery also **self-heals**
  when an underlying id changes (e.g. an account recreated on a reconnection
  keeps its type/name but gets a new id).
- **Keep the skill generic; put user-specifics behind one "load settings"
  seam** so the *source* can change without touching skill logic.
- **Confirm-once-then-persist** for discoveries that are genuinely ambiguous.
- **Config need not be structured — and often shouldn't be.** Before defining a
  schema, ask whether the per-user facts are really *settings* at all. Public
  reference data (published rates, limits, tax tables) is not user config — it's
  domain knowledge the skill carries. Domain mechanics (how often a thing
  happens, how a value is derived) belong in the skill, not a preferences file.
  Mutable, re-derivable state (a "last done" date, a current balance) should be
  read live, never stored stale. Strip those out and a structured config file
  is frequently left with nothing — or with content that already lives, as
  prose, in a document the user maintains.
- **A prose doc the skill locates is a first-class config source.** When the
  user already keeps the relevant policy as a written document (a project
  `*.md`, a runbook, a standing-rules file), the right "load settings" seam is
  to **find that doc and read it**, not to re-encode it as JSON. Locate it by
  convention (look in the current project), and **if it isn't found, ask the
  user where it is** (remember for the session; re-discovery is cheap). This
  keeps the skill generic, avoids a second copy that drifts, and respects that
  the user's document is the system-of-record.

---

## Storage Tiers (Cheapest / Most Portable First)

1. **Runtime discovery → session memory.** Re-derive each session from the
   system-of-record. Zero storage, fully portable, self-healing. The default
   when discovery is cheap and confident.
2. **Local file.** For machine-local state with no obvious home,
   `~/.config/<name>.json` (a flat file is spec-compliant; graduate to
   `~/.config/<name>/` once more than one file is needed). Prefer **JSON over
   YAML** when a stdlib-only reader matters — Python reads `json` with no
   install; `yaml` needs a package (venv). But match the *shape* to the data
   (see principles): if the user already keeps this as a prose document, the
   file is **that doc, located in-project or asked-for** — not a new structured
   schema. Resolve by an absolute, well-known path (XDG base dir, or the
   discovered doc's path); **never a cwd-relative path or a hardcoded workspace
   root** — both break across sessions and machines.
3. **Agent permanent memory.** Spans sessions, but is typically **per-surface
   and local** — it does **not** sync across agent surfaces (e.g. a CLI agent
   vs a web/mobile app of the same vendor are separate memory stores). It's for
   learned prose context, not structured config. Use sparingly.
4. **Centralized cloud** (a per-user file or sheet in the user's own cloud
   account, located via a public file property — `skill-data=<skill-name>`,
   plus `skill-data-role=<role>` only when the skill owns 2+ files; a set of
   skills that share one data file tags it with their common name prefix, e.g.
   `skill-data=bills` for `bills-status` / `bills-pay`). The **only
   cross-surface** option; heaviest; adds a connector dependency and a tamper
   surface. Use when cross-device or multi-user truly requires it. A
   locked/hidden file (e.g. an app-private folder) resists casual tampering
   better than a user-editable spreadsheet — but app-private properties are
   invisible to other agents and clients, so don't use them for discovery.

**Binding-dependency caveat:** cross-surface config portability is moot unless
the skill's required tools/connectors actually exist on that surface — the
connector is the real dependency, not the config store.
