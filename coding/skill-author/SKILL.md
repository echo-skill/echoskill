---
name: skill-author
description: >-
  Guide for developing, validating, and publishing AI agent skills.
  Provides reliable steps to make, build, create, or develop a skill,
  to review or revise a skill, or to publish or register a new or
  updated skill either locally — installing it at project, user, or
  global scope for one or more agents — or to a central registry,
  marketplace, or repo. Use when writing a SKILL.md, setting up
  frontmatter, choosing where a skill belongs, or preparing a skill
  for distribution.
---

# Developing Portable Agent Skills

## Default Posture: Portability

Always aim for cross-platform skills unless there is a genuine reason a skill
can only work on one platform. Challenge assumptions about platform specificity:

- "Does this skill REALLY require Claude-only features, or can the instructions
  be written neutrally?"
- "Am I using platform-specific frontmatter out of habit or necessity?"

If the user says they're building for just one platform, evaluate whether the
skill's purpose is truly platform-specific by nature. Guide them toward portable
design when feasible.

**Scope of this skill.** This skill is about *portability and placement* — making
a skill work across agents and putting it in the right home and tier. For the
craft of building and evaluating a single skill (drafting, test prompts, evals,
description-trigger tuning, packaging), defer to the agentskills.io spec and,
where available, Anthropic's `skill-creator` — don't re-derive those basics here;
assume the model and those resources carry them.

## First — does this already have a home?

Before drafting anything new, check the skills already registered in the session
(from their names/descriptions, *without* activating them): is one of them the
right home for this content — or would it be with a subtle rename/restructure to
absorb the new functionality? Prefer augmenting (and re-versioning) an existing
skill over creating a near-duplicate, with the user's blessing. This is the
reuse-value check applied at capture time: don't spawn a new skill where an
existing one should grow.

## Skill Format: agentskills.io Standard

Skills use the [agentskills.io](https://agentskills.io/specification) open
standard, supported by 30+ tools (Claude Code, Gemini CLI, VS Code/Copilot,
Cursor, and many others).

A skill is a directory containing `SKILL.md` with YAML frontmatter:

```yaml
---
name: my-skill
description: When to invoke this skill and what it does
---

Instructions for the agent...
```

### Required Fields

- `name` — lowercase, hyphens, 1-64 chars, must match directory name
- `description` — up to **1024 characters** (agentskills.io spec). This
  field is for **discovery and selection only** — it tells agents and
  users *when* this skill applies and *what problem it solves*, not
  *how* it works.

  **Front-load the first 250 characters.** Claude Code truncates
  descriptions beyond 250 chars in the skill listing. Put the primary
  trigger and use case up front. Additional keywords and scenarios can
  follow after 250 chars — they're still available when the full
  description loads into context, just not visible in the listing.

  **Use imperative framing.** Include "Use when..." to tell the agent
  when to act. Agents are making a selection decision — tell them when
  to select this skill, not just what it is.

  **Cover synonyms and verb variants.** Users say the same thing many
  ways. A skill for building skills should say "make, build, create,
  develop" not just "create". A PDF skill should say "reading,
  extracting, combining, merging, splitting..." — enumerate the verbs.
  This is established best practice per agentskills.io: "err on the
  side of being pushy" and "include cases where the user doesn't name
  the domain directly."

  **Avoid disqualifying language.** The description gates selection.
  If it mentions a specific platform, an agent building for a different
  platform may skip it. If it says "portable" or "cross-platform", an
  agent building a platform-specific skill may skip it. Keep the
  description maximally inclusive — opinionated guidance (like "prefer
  portability") belongs in the body where it can be articulated with
  nuance, not in the gate where it's a binary filter.

  Example: a skill for building agent skills should NOT say "for Claude
  Code and Gemini CLI" in the description — an agent building a Cursor
  skill or a platform-specific skill would self-exclude. The body can
  then guide toward portability where appropriate.

  **Add negative triggers only when non-obvious.** "Don't use for Vue
  or Svelte projects" helps a CSS skill avoid false triggers. "Not for
  using existing skills" is obvious and only hurts invocation chances.
  If the boundary is clear from context, don't state it.

  **Do:**
  - Name the activity or situation that triggers it
  - Say what outcome the skill produces
  - Use "Use when..." imperative framing
  - Cover synonyms — enumerate the verbs and nouns users might say
  - Use the full 1024 chars if needed for thorough keyword coverage

  **Do NOT:**
  - Include implementation details (tool names, commands, file formats)
  - Include agent instructions ("read the file", "render in chat")
  - Describe the skill's internal workflow or steps
  - Mention specific platforms unless the skill is genuinely
    platform-specific by nature
  - Add negative triggers for boundaries that are already obvious
  - Repeat what belongs in the body of the SKILL.md

  The body of SKILL.md is where implementation details, agent
  instructions, rules, anti-patterns, and workflow steps go.

### Optional Fields (agentskills.io)

- `compatibility` — max 500 chars, environment requirements. Covers
  both system dependencies ("Requires git, docker, jq") and intended
  product ("Designed for Claude Code (or similar products)") per the
  spec's own examples. Use it when a skill genuinely requires specific
  tools, runtimes, or agent features. Don't add it reflexively when
  the skill works everywhere — most skills don't need this field.
- `metadata` — arbitrary key-value map for additional properties
- `allowed-tools` — space-delimited pre-approved tools (experimental)
- `license` — license name or reference to a bundled license file.
  Only include if the user suggests it.

### Platform Extension Fields

These are Claude Code extensions. Other agents silently ignore them.

- `disable-model-invocation: true` — user-only / slash-only, agent won't auto-invoke. Also blocks programmatic agent invocation via the Skill tool — only the user typing the slash command works.
- `user-invocable: false` — ambient-only, hidden from slash menu
- `allowed-tools: Bash, Read` — pre-approved tools
- `argument-hint: "[pattern]"` — autocomplete hint
- `context: fork` — run in isolated subagent
- `agent: Explore` — subagent type when `context: fork` is set
- `model` — model override when skill is active
- `effort` — effort level override (low/medium/high/max)
- `paths: "**/*.py"` — glob patterns limiting when skill activates
- `shell` — `bash` (default) or `powershell`
- `hooks` — skill-scoped lifecycle hooks

Using platform extension fields does not make a skill non-portable —
other agents silently ignore unknown fields. But if the skill *depends*
on a platform extension to function (e.g., `context: fork` is essential
to its operation), note that in `compatibility`.


## Scripts in Skills — supported; instruction-only is a portability choice

**Skills can bundle and execute scripts.** The Agent Skills standard defines a
skill as a directory that can carry `scripts/` alongside `SKILL.md`, and agents
that support it run them. Reference bundled files by their path within the skill's
own directory — how that directory is resolved at runtime is agent-specific (Claude
Code exposes a `${CLAUDE_SKILL_DIR}` variable for it; don't assume that exact
variable exists on every agent — check the target's docs). Bundling a script is
fully legitimate — it keeps deterministic logic *with* the skill, so it installs
everywhere the skill does. The decision is **portability**, not permission.

- **Instruction-only is the most portable.** Gemini's `run_shell_command` requires
  approval by default, and the allowlist that grants it is global session /
  Policy-Engine config, not scoped to an individual skill — you *can* restrict it
  to specific command prefixes (e.g. `run_shell_command(git)`), but that's a
  user-level setting the skill can't control. The Cowork `.skill` packaging is
  **stdlib-only** (no venv/pip). So a skill that bundles runnable scripts —
  especially ones needing dependencies — narrows to Claude Code (or compatible)
  and can't ship as a stdlib-only Cowork bundle or assume shell access under
  Gemini's defaults.
- **Targeting Claude Code (or compatible)? Bundle scripts freely.** If the skill's
  value is a deterministic, repeatable operation, put it in `scripts/` and call it
  from `SKILL.md`. Progressive disclosure applies to code as well as reference
  docs.

Default to instruction-only when one skill must work across *every* agent; bundle
scripts when determinism matters and the target supports execution.

### Instruction-only patterns (the portable baseline)

- Reference MCP tools by name: "call the `gapp_deploy` tool"
- Describe commands the agent should run: "run `git status` on each repo"
- Include hints, examples, or templates for the agent to adapt
- Trust the agent to formulate execution plans with user approval

### When a plugin (beyond a script-bearing skill) is warranted

Bundling a script does NOT require a plugin. Reach for a **plugin** (Claude) or
**extension** (Gemini) when you need MORE than a script: an MCP server, hooks,
dependency / venv management, lifecycle, or distribution as a cross-agent unit.
"This skill needs to run code" is satisfied by a bundled script; the packaging
layer is for the rest.

## Marketplace Structure

Skills live in git repos organized as directories:

```
skills-repo/
├── prompting/              ← collection
│   ├── nm/SKILL.md
│   └── proceed/SKILL.md
├── coding/                 ← collection
│   ├── develop-skill/SKILL.md
│   └── develop-unit-tests/SKILL.md
└── claude/                 ← platform-specific collection
    └── sessions/SKILL.md
```

**Collection** = a folder of skill subfolders. Installable as a group:
```bash
gemini skills install <url> --path coding
```

Or individually:
```bash
gemini skills install <url> --path coding/skill-author
echomodel skills install skill-author
```

## Installation

Skills are installed via `echomodel skills install` (cross-platform) or
`gemini skills install` (Gemini native). Standalone Claude Code has no skill
CLI — `echomodel` writes directly to `~/.claude/skills/`. The **Claude Desktop**
app is a separate channel: skills install through its Cowork `.skill` flow into
a managed `anthropic-skills` plugin that the app injects into both its Cowork and
embedded-Code tabs (see "Detect the surface" under *After Writing* for picking
the right channel).

Agents discover skills by scanning directories for `SKILL.md` files.
No registration or manifest needed beyond the file itself.

## Writing Good Skill Instructions

- **Write for any agent by default.** Describe the desired outcome, not a
  tool-specific mechanism. Only target a specific agent platform when the
  user has explicitly said the skill is platform-specific.
- **Reference tools by name** when the skill depends on them (e.g., MCP tools).
  Note that the tool must be installed separately.
- **Include examples** of commands, workflows, or outputs the agent should
  produce. Agents perform better with concrete examples.
- **Keep it focused.** One skill, one purpose. If it does two unrelated things,
  split it into two skills.

## Per-User Config & State: Where It Lives

When a skill needs per-user configuration or must remember resolved state
(account ids, which thing is which, user preferences), decide *where* that
lives deliberately. Present the applicable options to the user when it matters;
don't reach for a heavy store by default.

**Default, don't bind.** State an opinionated skill's approach (a specific
tool/backend/dependency — "I use Google Drive"; "the Downloads folder, i.e.
`~/Downloads` on macOS") as a *default*, not a hard binding. Write the
load-settings seam wide enough that an adopter can substitute the backend with
low churn — resolved at runtime by discovery or a short dialogue, or supplied in
their own context file at whatever scope. Structure it for **accreting
examples**: work one provider concretely and *name* the alternatives even before
they're fully worked, so an OneDrive / Dropbox / Ubuntu / Windows user isn't shut
out on day one (the seam says "for others, discover or ask"); add same-depth
hints for the rest over time without rewriting. This is what makes a Patterned
skill genuinely promotable. Bound it with the reuse-value check: build
substitutability only where adopter-substitution is plausible (Patterned/Generic,
not Bespoke), and keep it *cheap to discover*, not pre-built for every backend —
over-generalizing every skill into infinite pluggability is its own failure mode.

**Discover or seed (provision, don't just read).** Resolve settings by discovery
first. When a durable store is genuinely needed and absent, create it at the
scope matching the skill's install scope — an agent context file
(`CLAUDE.md`/`GEMINI.md`/`CONTEXT.md`) or an XDG config file — and seed it in
dialogue with the user, then update it as conventions evolve. Bounded: prefer
discovery, confirm before writing, match scope to applicability, never
speculatively over-write.

**Principles**

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
  read live, never stored stale. Strip those out and a structured config file is
  frequently left with nothing — or with content that already lives, as prose,
  in a document the user maintains.
- **A prose doc the skill locates is a first-class config source.** When the
  user already keeps the relevant policy as a written document (a project
  `*.md`, a runbook, a standing-rules file), the right "load settings" seam is
  to **find that doc and read it**, not to re-encode it as JSON. Locate it by
  convention (look in the current project), and **if it isn't found, ask the
  user where it is** (remember for the session; re-discovery is cheap). This
  keeps the skill generic, avoids a second copy that drifts, and respects that
  the user's document is the system-of-record.

**Tiers — cheapest / most portable first:**

1. **Runtime discovery → session memory.** Re-derive each session from the
   system-of-record. Zero storage, fully portable, self-healing. The default
   when discovery is cheap and confident.
2. **Local file.** For machine-local state with no obvious home, `~/.config/<name>.json`
   (a flat file is spec-compliant; graduate to `~/.config/<name>/` once more than
   one file is needed). Prefer **JSON over YAML** when a stdlib-only reader
   matters — Python reads `json` with no install; `yaml` needs a package (venv).
   But match the *shape* to the data (see principles): if the user already keeps
   this as a prose document, the file is **that doc, located in-project or
   asked-for** — not a new structured schema. Resolve by an absolute, well-known
   path (XDG base dir, or the discovered doc's path); **never a cwd-relative path
   or a hardcoded workspace root** — both break across sessions and machines.
3. **Agent permanent memory.** Spans sessions, but is typically **per-surface and
   local** — it does **not** sync across agent surfaces (e.g. a CLI agent vs a
   web/mobile app of the same vendor are separate memory stores). It's for
   learned prose context, not structured config. Use sparingly.
4. **Centralized cloud** (a per-user file or sheet in the user's own cloud
   account, located via a stable tag/property). The **only cross-surface**
   option; heaviest; adds a connector dependency and a tamper surface. Use when
   cross-device or multi-user truly requires it. A locked/hidden file (e.g. an
   app-private folder) resists casual tampering better than a user-editable
   spreadsheet.

**Binding-dependency caveat:** cross-surface config portability is moot unless
the skill's required tools/connectors actually exist on that surface — the
connector is the real dependency, not the config store.

## Reuse tiers — where a skill belongs

Every skill sits in one of three tiers along two axes — exposure (private ↔
published) and generality (one-instance ↔ broadly useful):

- **Generic** — published / shareable. **Zero PII, ever.** Lives in a
  cross-cutting marketplace, or the specific tool's own public repo when it's
  coupled to that tool. Use when the value is genuinely reusable and has an
  audience beyond one.
- **Patterned** — private, opinionated ("here's how I do X; you could too").
  Identifiers externalized to config (per "Per-User Config & State"). Built as a
  **promotion candidate**: keep mechanism and identity cleanly separated so it can
  graduate to Generic — or serve another user — with a light refactor, never a
  rewrite.
- **Bespoke** — private, single-instance, welded to one vendor/account. Don't
  genericize the method (no audience). Still externalize *sensitive* identifiers
  (account numbers, card last-4s, billing ids) to config; non-sensitive specifics
  may stay inline.

The test for any fact: *would another person's copy need a different value here?*
→ it's identity → config, not skill.

**Reuse-value check — defer, don't duplicate.** Before investing to make something
Generic, or promoting Patterned → Generic, ask whether the reusable value is real
and *not already owned* by an existing artifact (especially a well-maintained or
official one). If it's covered, don't duplicate it or water your skill down
competing — defer to the existing artifact and keep only your genuine delta. (For
the craft of building and evaluating a single skill, that's the agentskills.io
spec and Anthropic's `skill-creator`; see "Scope of this skill" — this skill's
delta is portability and placement.)

## After Writing: Install, Test, Publish

Skills are fast-to-market by design. The goal is to impact the user's
workflow quickly — a skill sitting uninstalled helps no one. In most
cases, install immediately after writing with limited or no interim
testing. The skill format is low-risk and easy to revise in place.

Publishing is equally urgent. If a skill isn't version-controlled in
a known location and available across the user's working environments,
it erodes trust in the entire skills workflow. Skills that feel
chaotically scattered — local copies here, stale versions there, no
change history — discourage the user from investing time in writing
or adopting them. Publish promptly to a tracked, central location so
the user can rely on skills being available, up to date, and backed
up wherever they work.

The exception is publishing to broadly adopted skills marketplaces
where multiple users are affected. There, test thoroughly before
publishing — a broken skill at scale is worse than a delayed one.

### 1. Install locally

Install the skill so it's available in your agent platform before
publishing anywhere.

| Scope | Path | When to use |
|-------|------|-------------|
| User / machine | `~/.claude/skills/<name>/SKILL.md` | Default. Available in all projects on this machine. |
| Project | `.claude/skills/<name>/SKILL.md` | Skill is specific to this repo and should be versioned with it. |
| Gemini | `gemini skills install <path-or-url>` | Gemini CLI native install. |

**User-scope is the default.** Install at project scope only when the
skill is inherently tied to the repo (e.g., repo-specific workflow,
project conventions).

**Project-scoped skills and git tracking.** When installing at project
scope, ensure the skill files will be version-controlled:

1. Check that `.claude/skills/` is not gitignored. Many repos ignore
   `.claude/` entirely — add a `!.claude/skills/` exception in
   `.gitignore` if needed.
2. Run `git status` after creating the skill to confirm the new
   `SKILL.md` appears as untracked or staged.
3. If a `.gitignore` change was required, verify it didn't expose
   other files under `.claude/` (settings, cache, logs). Evaluate any
   newly surfaced files case by case before committing.

The `setup-agent-context` skill, if available, covers `.gitignore`
management for agent directories in detail — including per-file
guidance on what to version vs. exclude.

#### Installing a `.skill` bundle (Claude desktop / Cowork, macOS)

Some platforms install a skill from a packaged `.skill` bundle rather
than a filesystem path. On macOS, once you have the `.skill` file,
hand it to the installer one of two ways — and **offer the user the
choice**, because they serve different moments:

| Command | What happens | When |
|---|---|---|
| `open -R <file>.skill` | Reveals the file **selected** in Finder; user drags it into the install UI | User wants to *see what they're installing and choose deliberately* |
| `open <file>.skill` | `.skill` is registered to the Claude desktop app, so this (= double-click) launches the **install popup directly** — one click to install/replace | Fast, one-step install |

Both are verified. More generally: whenever you direct a user to a
local file they must act on (install, upload, attach, drag), run
`open -R <path>` (reveal it selected) or `open <path>` (hand it to its
handler) rather than just printing the path — it takes them straight
there instead of making them hunt. Building the `.skill` bundle itself
is a separate, platform-specific packaging step (not covered here).

**Updating a skill that's already injected via `anthropic-skills`.**
Re-installing an edited `.skill` this way **overwrites the managed copy
in place** — including the copy a currently-running Code-tab session
loads from — so the update takes effect without waiting for a new
session, and leaves a **single** copy on disk (no stale duplicate).
Prefer this over dropping a `~/.claude/skills/<name>` symlink *beside*
an injected skill of the same name, which creates two same-named skills
and ambiguity about which one loads. To confirm an install landed:
locate the installed `SKILL.md` under the app's managed skills directory
and `grep` it for a string unique to your edit (and check its mtime).

### 2. Test the skill

**Verify it's discoverable.** Before testing behavior, confirm the
agent platform sees the skill:

```bash
# Gemini CLI
gemini skills list

# Claude Code — check the slash menu or ask:
claude -p "list your available skills"
```

If the skill doesn't appear, check the install path and directory name.

**Test behavior.** Run a headless prompt that indirectly reveals
whether the skill loaded and influenced the agent's behavior. The
prompt should exercise the skill's guidance without requiring actual
disk I/O or other privileged tool usage — this keeps the test fast
and safe.

```bash
# Claude Code
claude -p "prompt that reveals the skill's effectiveness"

# Gemini CLI
gemini -p "prompt that reveals the skill's effectiveness"
```

**Designing a good test prompt:**

- Ask the agent to describe how it would approach a task the skill
  covers. The response should reflect the skill's specific guidance,
  not generic behavior.
- If the skill has distinctive rules or preferences, ask about a
  scenario where those rules apply and check whether the response
  follows them.
- Add `--allowedTools ""` or similar flags to prevent actual tool
  execution if the prompt might trigger it. The goal is to verify the
  skill shaped the agent's reasoning, not to run a full workflow.
- For skills with `user-invocable: true`, test slash-command invocation
  too: does `/my-skill` trigger it?

### 3. Publish

Once the skill works locally, publish it. Skills that stay local get
forgotten — publish promptly so the skill is available where you (and
others) will actually use it. If the user hasn't specified a
destination, ask where it should go and push for a decision now.

#### Where to publish

**Cross-platform skills** go in the primary skills marketplace (e.g.,
echoskill). These work across agents and belong in topical collections
(`coding/`, `prompting/`, `consulting/`).

**Platform-specific skills** go in a platform-specific collection or repo.
If a skill genuinely only works on one agent (e.g., depends on Claude Code's
`context: fork` or Gemini-specific features), publish it under a
platform-specific collection (e.g., `claude/`) in the marketplace, or in a
platform-specific repo. Don't pollute the primary cross-platform marketplace
with skills that only work on one agent.

### Determine placement

Glob the target repo for `*/SKILL.md` and `*/*/SKILL.md` to understand how
skills are organized. Show the user the existing structure and confirm which
collection the skill belongs in. If the skill already exists (same name),
confirm the user wants to update it.

### Validate before publishing

Before copying to the target:

- **Frontmatter is complete**: `name` and `description` are required.
- **Name matches directory name.**
- **No references to specific consuming repos or projects.** Usage
  examples must be generic. If repo-specific references are found,
  rewrite them to be generic before publishing.
- **No PII or user-specific identifiers** — account numbers, emails, names,
  repo/store names, folder ids, property names, real dollar figures. That's
  *identity*, not mechanism: externalize per "Per-User Config & State" and recall
  at runtime. If a different user would need a different value, it's leaked config
  — pull it out before publishing.
- **Bundled scripts are fine, but note the portability cost** — a skill that
  bundles executable scripts targets Claude Code (or compatible); for a skill that
  must work across every agent, keep it instruction-only or move the code to a
  plugin/package (see "Scripts in Skills").
- **No hard dependencies on non-ubiquitous tools** without offering
  alternatives.

### Publish workflow

1. Copy the skill directory to the target repo at the confirmed path
2. Update the README.md table for the collection if one exists
3. `git diff --staged` to review
4. Confirm with the user
5. Commit and push

### Installing from a marketplace on other machines

After publishing, show the user how to install the skill elsewhere.
Use actual values from the publish (repo URL, collection, skill name)
— not angle-bracket placeholders.

**Detect the surface before choosing a method — don't just copy whatever
`~/.claude/skills/` already shows.** The right install path depends on where
the agent is actually running:

- **Standalone Claude Code (terminal CLI, `CLAUDE_CODE_ENTRYPOINT=cli`):**
  filesystem only — symlink into `~/.claude/skills/<name>/`, `npx skills add`,
  or a plugin. This is the only channel here.
- **Claude Code embedded in the Claude Desktop app (the "Code" tab,
  `CLAUDE_CODE_ENTRYPOINT=claude-desktop`):** the desktop app injects its own
  managed skills plugin (named `anthropic-skills`) into this tab, carrying
  Anthropic built-ins **and** skills the user installed via the desktop app's
  Cowork `.skill` flow. So a skill installed once through Cowork already appears
  here — **a `~/.claude/skills` symlink is usually redundant.** The Code tab sees
  the union of that injected plugin + native `~/.claude/skills`. **You do NOT need
  a Cowork session to install or update from the Code tab** (verified): the
  `.skill` build is a plain stdlib zip, and `open <file>.skill` triggers the
  desktop install popup directly (see "Installing a `.skill` bundle" above). Only
  the Cowork *Save-card* (`present_files`) itself needs a Cowork session — the
  build and the `open`-based install do not.
- **Cowork / Claude Desktop app surface:** package a `.skill` bundle and install
  it via the desktop Save-card flow (a meta-skill like `install-cowork-skill`).

Check `gemini skills list` for the Gemini side. Match an existing pattern only
within the *same* channel — don't assume the symlinks in `~/.claude/skills`
are how a Desktop user's skills got there. Save the resolved method to memory.

**Gemini CLI:**

```bash
# Install a single skill from a collection
gemini skills install <repo-url> --path <collection>/<skill-name>

# Install an entire collection
gemini skills install <repo-url> --path <collection>

# Link a local clone (live updates, no reinstall needed)
gemini skills link <local-path>/<collection>/<skill-name>
```

`gemini skills link` creates a live link — edits to the source are
reflected immediately with no reinstall. Prefer this over `install`
when working from a local clone of the skills repo.

**Claude Code (standalone CLI — see surface detection above):**

Standalone Claude Code has no skill management CLI. Install by symlinking from
a local clone of the marketplace repo (skip this if the user is on Claude
Desktop and the skill is already installed via the Cowork `.skill` flow — it's
injected into the Code tab there):

```bash
# Clone the skills repo (once per machine)
git clone <repo-url> <local-path>

# Symlink the skill
ln -s <local-path>/<collection>/<skill-name>/SKILL.md \
  ~/.claude/skills/<skill-name>/SKILL.md
```

Symlinks keep the local install in sync with `git pull` — no re-copy
needed after updates.

**Plugin-bundled skills:**

If the skill ships inside a Claude Code plugin rather than a
standalone marketplace, the install command is different:

```bash
claude plugin install <plugin-name>@<marketplace> --scope user
```

Skills bundled in plugins are managed by the plugin lifecycle, not
by manual symlinks or copies.

### Avoiding duplicate installs

A skill can reach an agent through more than one channel:

- **Plugin/extension bundle** — managed by the packaging layer's
  install and update lifecycle.
- **Standalone symlink** — a link from the user-scope skills
  directory to a source repo. Live updates via `git pull`.
- **Standalone copy** — a plain file in the user-scope skills
  directory. Static snapshot, no link back.

Each is valid alone. But when two channels deliver the same skill
simultaneously, the agent's slash menu and skills listing show the
skill twice, and whichever copy loads first may not be the one the
user expected.

**Rule: one channel per skill per machine.** If the user's installed
plugin/extension already bundles the skill, do not also install it
standalone. If they've chosen the symlink path, do not install the
bundling plugin/extension.

**Bundling scope (for authors of plugins/extensions):** a
plugin/extension should bundle a skill only if the plugin's own
machinery (its agents, hooks, MCP servers, native skills, or scripts)
directly depends on that skill. Bundling a skill purely for user
convenience — because it's useful alongside the plugin — is an
"alt marketplace install" anti-pattern that creates the duplication
problem above. General-purpose skills belong in their own marketplace;
consumers install them separately.

**When duplicates are already present, reconcile:**

1. **Audit.** Search all install locations for the skill name —
   user-scope skill directories for standalone copies and symlinks,
   plugin/extension cache directories for bundled copies.
2. **Classify.** For each hit, determine whether it is a bundled copy
   (under a plugin/extension cache), a symlink to a source repo (run
   `readlink` or `ls -la`), or a static standalone copy.
3. **Pick one channel.** Prefer the channel already used for similar
   skills on this machine — don't introduce a new pattern for a
   single skill.
4. **Remove the others.** Standalone copies and symlinks: delete from
   the user-scope directory. Bundled copies: uninstall the bundling
   plugin/extension — but only if that plugin as a whole is the
   channel being dropped, not because it happens to bundle one
   duplicate skill.
5. **Restart the agent session** so menus and listings rebuild
   against the resolved set.

**The slash menu and skills listing are the warning signal.** If the
same skill name appears more than once, a duplicate-install situation
exists. Investigate before assuming one version is authoritative.

### Reconcile local installs with skills repo

Skills drift when they exist in multiple places — the local platform
install directory and the personal skills repo. Every publish action
is an opportunity to reconcile.

**Locate the skills repo.** Check memory for a previously saved
skills repo path. If not found, ask the user where their personal
skills repo / marketplace lives and save it to memory for future
sessions (e.g., memory name: `skills-repo-location`, type:
`reference`).

**Known local install locations:**
- `~/.claude/skills/<name>/SKILL.md` — Claude Code user-scope
- `~/.gemini/skills/<name>/SKILL.md` — Gemini CLI user-scope (if
  applicable; check `gemini skills list` for installed locations)
- `.claude/skills/<name>/SKILL.md` — project-scope (current repo)

**For each skill being published, compare across all locations:**

1. **Gather facts.** For each copy of the skill (local installs +
   repo), check:
   - Does the file exist?
   - File size and last-modified timestamp (`stat` or `ls -la`)
   - Content (`diff` between copies)

2. **Report to the user.** Present a clear status for each location:
   - **Missing in repo but installed locally** — the skill hasn't
     been published yet. Recommend copying local → repo.
   - **In repo but not installed locally** — the skill was published
     but never installed on this machine, or was removed. Recommend
     copying repo → local.
   - **Identical in both** — in sync, nothing to do.
   - **Different** — show the diff. Recommend a direction based on
     timestamps (newer usually wins), but always ask the user which
     version to keep, or whether to merge changes manually.

3. **Act with user's blessing.** After the user confirms the
   direction:
   - Copy the chosen version to the target location(s)
   - Stage, commit, and push the skills repo if it was updated
   - Confirm the local install is current if that was updated

4. **Save the repo location to memory** if not already saved, so
   future publish actions skip the "where is your skills repo?" step.

**Do this reconciliation proactively** — don't wait for the user to
ask. Every time a skill is published or updated, check the other
locations and flag drift. The goal is a single source of truth in the
repo with local installs as consistent copies.

### Consider agent preloading

If the skill was developed for use by a specific agent (e.g., a coding
agent, a review agent), consider whether that agent's `skills:` frontmatter
should be updated to preload it. Preloading injects the full skill content
into the agent's context at startup — the agent doesn't need to discover
or invoke the skill; it just has the knowledge.

```yaml
# In the agent's .md frontmatter:
skills:
  - safe-commit
  - show-code       # ← new skill preloaded here
```

**Platform support for skill preloading in agents:**

- **Claude Code** — supported via `skills:` list in agent/subagent
  frontmatter. Full skill content is injected at startup. Subagents
  don't inherit skills from the parent; list them explicitly.
  ([Claude Code docs: Preload skills into subagents](https://code.claude.com/docs/en/sub-agents#preload-skills-into-subagents))
- **Gemini CLI** — no equivalent mechanism as of 2026. Skills are
  discovered and loaded via progressive disclosure, not preloaded
  into agent definitions.
- **agentskills.io** — the spec covers skill format only, not agent
  definitions or skill-to-agent binding.

**When to preload vs. let the agent discover:**

- Preload when the agent should *always* have this knowledge (e.g.,
  commit workflow, code style rules)
- Let discovery handle it when the skill is situational (e.g.,
  PDF processing, dependency evaluation)

## Close the flywheel

Once this skill has run in a session, make sure the standing capture behavior is
in place: if the agent's global context doesn't already instruct it to watch for
and *propose* capturing reuse opportunities, propose adding that line
(discover-or-seed, with the user's blessing). That converts one-off capture into
an ongoing loop — the agent notices opportunities, this skill captures them, and
capture keeps the watch-behavior alive. Propose, never auto-write; the
watch-behavior proposes skills, it doesn't silently generate them.

## Cross-Skill References

Skills must be self-contained. A skill that fails or misleads when a
referenced skill is absent is a broken skill. Follow these rules when
one skill relates to another:

### Only reference co-packaged skills

Only reference skills distributed in the same unit — same marketplace
collection, same plugin, same repo. Never reference skills from
external sources; they may not be installed.

### Hint-level only

References must be non-essential hints to supplementary content. The
referencing skill must function fully on its own. Use language like:

> "The `setup-agent-context` skill, if available, covers this in
> more detail."

> "See the `safe-commit` skill if installed for commit workflow
> guidance."

Never write references that create a dependency:

> "Follow the steps in `setup-agent-context` to complete this task."

> "This skill requires `safe-commit` to be installed."

### Prefer duplication over cross-skill dependencies

If a skill needs specific content from another skill to work correctly,
duplicate that content inline. Three repeated paragraphs are better
than a dependency chain that breaks when a skill is missing.

### Exception: platform-native bundled skills

Skills that are privately co-bundled into an **agent platform** (Claude
Code, Gemini CLI, Cursor, or similar native agent environments) — and
are NOT also published from the same source into a skills marketplace —
may use firm cross-references. The platform ships them as a unit, so
co-presence is guaranteed.

This exception does NOT apply to marketplace-published skills, even if
they also happen to be bundled into a platform. If a skill is available
outside the platform (via a marketplace, a shared repo, or standalone
installation), it must follow the hint-level rules above, because
marketplace consumers may pick and choose which skills to install.

### Terminology note

**Agent platform** is the umbrella term for native agent environments
— Claude Code, Gemini CLI, Cursor, and similar tools where agents
execute with access to tools, files, and skills. Use "agent platform"
(not "IDE", "CLI", or "runtime" alone) when referring to this category
generically.
