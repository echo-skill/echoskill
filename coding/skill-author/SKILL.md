---
name: skill-author
description: >-
  Use when making, building, creating, developing, reviewing, revising,
  validating, installing, or publishing an AI agent skill (SKILL.md).
  Covers agentskills.io frontmatter, description auto-activation,
  progressive disclosure and size limits, references/ layout, per-user
  config and data-backed skills, choosing which reuse tier or repo a
  skill belongs in, and installing or reconciling skills across project,
  user, or global scope and marketplaces.
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

**Scope of this skill.** This skill is about *portability, progressive
disclosure, and placement* — making a skill work across agents, structuring it
so instructions never truncate, and putting it in the right home and tier. For
the craft of building and evaluating a single skill (drafting, test prompts,
evals, description-trigger tuning), defer to the agentskills.io spec and, where
available, Anthropic's `skill-creator` — don't re-derive those basics here.

| Topic | Reference |
|-------|-----------|
| Per-user config & state (default-don't-bind seams, discover-or-seed, prose docs as config, 4 storage tiers) | [references/config-and-state.md](references/config-and-state.md) |
| Data-backed skills (cloud file formats, `skill-data` property discovery, provisioning, in-place writes, capture obligations, close-out audit, child skeleton) | [references/data-backed-skills.md](references/data-backed-skills.md) |
| Installing locally across agent platforms, building `.skill` bundles, headless testing, publishing workflow, duplicate-install & repo-drift reconciliation, and subagent preloading | [references/install-and-publish.md](references/install-and-publish.md) |
| Claude desktop app specifics (`.skill` install on macOS, updating in place, the two saved copies and sync lag, comparing reformatted frontmatter) | [references/claude-desktop.md](references/claude-desktop.md) |

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
standard, supported by 30+ tools (Claude Code, Gemini CLI, Antigravity, VS Code,
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

- `name` — lowercase alphanumeric and single hyphens (`a-z0-9-`), 1–64 chars,
  must match directory name.
- `description` — up to **1024 characters** (agentskills.io spec). This field is
  for **discovery and selection only** — it tells agents and users *when* this
  skill applies and *what problem it solves*, not *how* it works.

  **Front-load the first 250 characters.** Claude Code truncates descriptions
  beyond 250 chars in the compact skill listing, caps combined `description` +
  `when_to_use` at **1,536 characters**, and budgets the total skill listing at
  **1% of the context window** (dropping least-used descriptions when
  overflowing). Put the primary trigger and use case up front. Additional
  keywords and scenarios can follow after 250 chars — they remain available when
  the full description loads into context.

  **Use imperative framing.** Include "Use when..." to tell the agent when to
  act. Agents are making a selection decision — tell them when to select this
  skill, not just what it is.

  **Cover synonyms and verb variants.** Users say the same thing many ways. A
  skill for building skills should say "make, build, create, develop" not just
  "create". A PDF skill should say "reading, extracting, combining, merging,
  splitting..." — enumerate the verbs. Per agentskills.io best practices: "err
  on the side of being pushy" and "include cases where the user doesn't name the
  domain directly."

  **Avoid disqualifying language.** The description gates selection. If it
  mentions a specific platform, an agent building for a different platform may
  skip it. If it says "portable" or "cross-platform", an agent building a
  platform-specific skill may skip it. Keep the description maximally inclusive
  — opinionated guidance (like "prefer portability") belongs in the body where
  it can be articulated with nuance, not in the gate where it's a binary filter.

  **Add negative triggers only when non-obvious.** "Don't use for Vue or Svelte
  projects" helps a CSS skill avoid false triggers. "Not for using existing
  skills" is obvious and only hurts invocation chances.

  **Do:**
  - Name the activity or situation that triggers it
  - Say what outcome the skill produces
  - Use "Use when..." imperative framing
  - Cover synonyms — enumerate the verbs and nouns users might say
  - Use up to 1024 chars if needed for thorough keyword coverage (with no
    `<...>` angle brackets, which the Claude app `.skill` uploader rejects)

  **Do NOT:**
  - Include implementation details (tool names, commands, file formats)
  - Include agent instructions ("read the file", "render in chat")
  - Describe the skill's internal workflow or steps
  - Mention specific platforms unless the skill is genuinely platform-specific
  - Add negative triggers for boundaries that are already obvious
  - Repeat what belongs in the body of `SKILL.md`

### Optional Fields (agentskills.io)

The open standard defines 6 total frontmatter keys (`name`, `description`, plus
these 4 optional keys):

- `compatibility` — max 500 chars, environment requirements. Covers both system
  dependencies ("Requires git, docker, jq") and intended product ("Designed for
  Claude Code (or similar products)"). Omit when the skill works everywhere.
- `metadata` — arbitrary key-value map for additional properties.
- `allowed-tools` — space-delimited pre-approved tools (experimental).
- `license` — license name or reference to a bundled license file. Only include
  if the user suggests it.

### Platform Extension Fields & `.skill` Bundle Portability

Claude Code supports additional frontmatter keys (`disable-model-invocation`,
`user-invocable`, `argument-hint`, `context: fork`, `agent`, `model`, `effort`,
`paths`, `shell`, `hooks`, `when_to_use`).

- **Filesystem installs (`~/.claude/skills/`, `~/.gemini/skills/`,
  `~/.gemini/config/skills/`):** Other agents silently ignore unknown
  frontmatter keys, so extension keys do not break filesystem loading. If the
  skill *depends* on a platform extension to function (e.g., `context: fork`),
  note that in `compatibility`.
- **`.skill` bundles (Claude app / `claude.ai` upload and `package_skill.py`):**
  The `.skill` packager and Claude app uploader **strictly validate against the
  6 `agentskills.io` keys** (`name`, `description`, `license`, `compatibility`,
  `metadata`, `allowed-tools`) and **reject any other frontmatter key** with
  `Unexpected key(s) in SKILL.md frontmatter`. Never add platform extension
  keys to a skill that will be packaged as a `.skill` bundle or shared across
  Claude Desktop / `claude.ai`.

## Progressive Disclosure, Size Limits & Context Architecture

Skills use a **three-tier progressive disclosure model** so agents can carry
dozens of skills with near-zero baseline context cost:

1. **Tier 1 — Catalog (`name` + `description` at session start):** ~50–100
   tokens per skill. Keep `description` $\le$ 1024 chars and front-load the
   first 250 chars.
2. **Tier 2 — `SKILL.md` Body (on activation):** Keep `SKILL.md` **under 500
   lines and `< 5,000 tokens` (~20 KB)**.
   - *Why these limits matter across harnesses:*
     - **agentskills.io spec:** Recommends `< 500 lines` and `< 5,000 tokens`
       for the `SKILL.md` body.
     - **Claude Code:** Recommends `< 500 lines`, and **on auto-compaction
       re-attaches only the first `5,000 tokens` (~20 KB) of each invoked
       skill** (within a 25,000-token combined budget across all active skills).
       Anything past 5,000 tokens is dropped after compaction.
     - **Antigravity / Gemini IDEs:** Load `SKILL.md` on demand via file-view
       tools that truncate a single read at **800 lines** or **46,080 bytes
       (~45 KB)**.
   - **Front-load invariants and routing:** Place non-negotiable rules, core
     principles, and the `references/` routing table near the top of `SKILL.md`
     so they always survive single-call reads and context compaction.
3. **Tier 3 — Bundled Resources (`references/`, `scripts/`, `assets/` on
   demand):**
   - Move detailed procedures, platform-specific mechanics, schemas, templates,
     and long examples into `references/*.md`.
   - **Keep reference files one level deep** from `SKILL.md` (`SKILL.md` →
     `references/topic.md`, never `SKILL.md` → `references/a.md` →
     `references/b.md`). Both `agentskills.io` and Claude Code warn that agents
     may read nested reference chains only partially.
   - **Route explicitly from `SKILL.md`:** Include a 1-line summary of each
     topic in `SKILL.md` and a routing table (`| Topic | Reference |`) stating
     *when* to read each file so the agent knows what exists before opening any
     reference.

### Global Context (`CONTEXT.md` / `CLAUDE.md` / `GEMINI.md` / `AGENTS.md`) vs. Hub / Router Skills

Always-on global context files face strict size and truncation limits (for
example, Antigravity caps individual rule files at **24 KB** / 20,000 aggregate
tokens and can truncate large global files around ~12 KB; Claude Code
recommends keeping `CLAUDE.md` under **200 lines**). Never dump long procedural
workflows into global context files.

Use this division of labor between always-on global context and skills:

- **Skill descriptions catch user-request triggers** — when the user's prompt
  asks to do something the skill covers, the agent matches the skill's
  `description` and loads `SKILL.md`.
- **Global context catches autonomous agent decisions** — when the agent
  decides *on its own* mid-task where to place a new file/config/repo, which
  library to choose, how to scaffold a project, or what pre-commit checks to
  run, skill descriptions won't fire because the user didn't ask about those
  choices.
- **Pattern:** Keep Global Context compact (~5–10 KB) containing only:
  1. **Universal safety, privacy, and identity invariants** that must hold in
     every turn even when no skill is loaded.
  2. **1-line autonomous-decision trigger pointers** to compact **Hub / Router
     Skills** (e.g., *"Load `<coding-hub-skill>` before deciding where
     code/configs/skills/repos go, scaffolding, choosing a framework, deploying,
     or releasing"*).
  Each Hub Skill stays compact (`< 200 lines`) with a 1-line-per-topic summary
  and a routing table pointing one level deep to `references/*.md`.

## Scripts in Skills — supported; instruction-only is a portability choice

**Skills can bundle and execute scripts.** The Agent Skills standard defines a
skill as a directory that can carry `scripts/` alongside `SKILL.md`, and agents
that support it run them. Reference bundled files by their path within the
skill's own directory — how that directory is resolved at runtime is
agent-specific (Claude Code exposes `${CLAUDE_SKILL_DIR}`; don't assume that
exact variable exists on every agent — check the target's docs). Bundling a
script keeps deterministic logic *with* the skill, so it installs everywhere the
skill does. The decision is **portability**, not permission.

- **Instruction-only is the most portable.** Gemini's `run_shell_command`
  requires approval by default, and the allowlist that grants it is global
  session / Policy-Engine config, not scoped to an individual skill. The Claude
  app's `.skill` packaging is **stdlib-only** (no venv/pip). So a skill that
  bundles runnable scripts — especially ones needing dependencies — narrows to
  Claude Code (or compatible) and can't ship as a stdlib-only `.skill` bundle or
  assume shell access under Gemini's defaults.
- **Targeting Claude Code (or compatible)? Bundle scripts freely.** If the
  skill's value is a deterministic, repeatable operation, put it in `scripts/`
  and call it from `SKILL.md`. Progressive disclosure applies to code as well as
  reference docs.

Default to instruction-only when one skill must work across *every* agent;
bundle scripts when determinism matters and the target supports execution.

### Instruction-only patterns (the portable baseline)

- Describe the capability a step needs: "use a Drive tool that replaces a
  file's content in place by its ID"
- Describe commands the agent should run: "run `git status` on each repo"
- Include hints, examples, or templates for the agent to adapt
- Trust the agent to formulate execution plans with user approval

### When a plugin (beyond a script-bearing skill) is warranted

Bundling a script does NOT require a plugin. Reach for a **plugin** (Claude) or
**extension** (Gemini) when you need MORE than a script: an MCP server, hooks,
dependency / venv management, lifecycle, or distribution as a cross-agent unit.

## Marketplace Structure

Skills live in git repos organized as directories:

```
skills-repo/
├── prompting/              ← collection
│   ├── capture-context/SKILL.md
│   └── extend-document/SKILL.md
├── coding/                 ← collection
│   ├── skill-author/SKILL.md
│   └── sociable-unit-tests/SKILL.md
└── claude/                 ← platform-specific collection
    └── sessions/SKILL.md
```

**Collection** = a folder of skill subfolders, installable as a group or
individually (`gemini skills install <url> --path coding/skill-author`,
`gemini skills link <local-path>/coding/skill-author`, or
`echomodel skills install skill-author`). Agents discover skills by scanning
directories for `SKILL.md` files — no registration or manifest needed beyond the
file itself.

## Writing Good Skill Instructions

- **Write for any agent by default.** Describe the desired outcome, not a
  tool-specific mechanism. Only target a specific agent platform when the
  user has explicitly said the skill is platform-specific.
- **Name the capability, not a tool.** When a step needs an external tool,
  describe what it must do — "a Drive tool that replaces a file's content in
  place by its ID", "a tool that lists a folder's files" — not one MCP
  server's tool name. Users connect different servers for the same service,
  and a named tool makes the skill look inapplicable to everyone else. Name a
  specific tool as required only when the skill truly depends on that one
  tool (its own MCP server, or a capability no other tool offers), and say it
  must be installed separately.
- **Include examples** of commands, workflows, or outputs the agent should
  produce. Agents perform better with concrete examples.
- **Keep it focused.** One skill, one purpose. If it does two unrelated things,
  split it into two skills.
- **Coherent specification, not a history exposé.** Write `SKILL.md` and
  `references/*.md` to describe what the design *is*, not the history of how it
  got there or deprecated prior approaches.

## Per-User Config & State: Where It Lives

When a skill needs per-user configuration or must remember resolved state
(account ids, which thing is which, user preferences), decide *where* that
lives deliberately. Read
[references/config-and-state.md](references/config-and-state.md) for the full
design patterns ("Default, don't bind", "Discover or seed", cloud-vs-local
resolution order, and prose documents as config sources).

**Core principles:**

- **Default, don't bind.** State an opinionated backend/tool as a default behind
  a single "load settings" seam so adopters can substitute alternatives (worked
  or named) without rewriting skill logic.
- **Prefer discovery over storage.** Re-derive facts from the system-of-record
  at runtime using **structural signals** (types, subtypes, status), **not
  user-chosen names/labels**. Confirm once and persist only when genuinely
  ambiguous.
- **A prose doc is a first-class config source.** Public reference data and
  domain mechanics belong in the skill; mutable state should be read live. When
  the user already keeps policy in a written project doc (`*.md`, runbook,
  standing rules), find and read that doc rather than re-encoding it as JSON.

**Tiers — cheapest / most portable first:**

1. **Runtime discovery → session memory** — zero storage, self-healing default.
2. **Local file** — `~/.config/<name>.json` (prefer JSON over YAML for
   stdlib-only reading) or the user's located prose doc; resolve by absolute XDG
   or discovered path, **never** a cwd-relative path or hardcoded workspace
   root.
3. **Agent permanent memory** — local per-surface prose context only (does not
   sync across CLI vs. web/mobile app).
4. **Centralized cloud** — per-user cloud file/sheet located via public property
   `skill-data=<skill-name>` (plus `skill-data-role=<role>` when owning 2+
   files). The only cross-surface option; use when cross-device or multi-user
   truly requires it.

## Data-Backed Skills

When a skill's purpose is to capture and maintain user data across sessions (a
log, inventory, tracker, body of research, or piece of writing), its data lives
in centralized cloud files (tier 4 above) and the skill itself takes on an
explicit durability responsibility: nothing of value may be lost if a session
ends, an agent's memory is wiped, or the user changes agent vendors. Read
[references/data-backed-skills.md](references/data-backed-skills.md) before
authoring or revising one.

**Binding-dependency caveat:** cross-surface config portability is moot unless
the skill's required tools/connectors actually exist on that surface — the
connector is the real dependency, not the config store.

## Reuse tiers — where a skill belongs

Every skill sits in one of three tiers along two axes — exposure (private ↔
published) and generality (one-instance ↔ broadly useful):

- **Generic** — published / shareable. **Zero PII, ever.** Lives in a
  cross-cutting marketplace, or the specific tool's own public repo when coupled
  to that tool. Use when the value is genuinely reusable and has an audience
  beyond one.
- **Patterned** — private, opinionated ("here's how I do X; you could too").
  Identifiers externalized to config. Built as a **promotion candidate**: keep
  mechanism and identity cleanly separated so it can graduate to Generic — or
  serve another user — with a light refactor, never a rewrite.
- **Bespoke** — private, single-instance, welded to one vendor/account. Don't
  genericize the method (no audience). Still externalize *sensitive* identifiers
  (account numbers, card last-4s, billing ids) to config; non-sensitive
  specifics may stay inline.

The test for any fact: *would another person's copy need a different value
here?* → it's identity → config, not skill.

**Reuse-value check — defer, don't duplicate.** Before investing to make
something Generic, or promoting Patterned → Generic, ask whether the reusable
value is real and *not already owned* by an existing artifact (especially a
well-maintained or official one). If it's covered, defer to the existing
artifact and keep only your genuine delta.

## After Writing: Install, Test, Publish

Skills are fast-to-market by design: install immediately after writing, verify
discoverability and behavior, and publish promptly to a version-controlled
repository so skills never drift as untracked local copies.

Read [references/install-and-publish.md](references/install-and-publish.md) for
the full step-by-step commands and workflows, and
[references/claude-desktop.md](references/claude-desktop.md) when targeting the
Claude desktop app. Key rules at a glance:

1. **Detect the surface first (one channel per skill per machine):**
   - **Standalone Claude Code CLI (`CLAUDE_CODE_ENTRYPOINT=cli`):** symlink into
     `~/.claude/skills/<name>`.
   - **Claude Desktop Code tab (`CLAUDE_CODE_ENTRYPOINT=claude-desktop`):**
     loads the managed `anthropic-skills` plugin (synced from the user's Claude
     account) *plus* `~/.claude/skills/`. If the skill is saved to the Claude
     account, a `~/.claude/skills` symlink creates a duplicate — install/update
     via `.skill` bundle instead (see
     [references/claude-desktop.md](references/claude-desktop.md)).
   - **Gemini CLI:** prefer `gemini skills link <local-path>` for local clones,
     or `gemini skills install <repo-url> --path <collection>/<skill-name>`.
   - **Antigravity (`agy`):** relative symlink in
     `~/.gemini/config/skills/<name>` (or workspace `.agents/skills/<name>`).
2. **Choose where the skill is versioned — always ask:**
   - **Generic** → public marketplace (e.g., `echoskill`) after validation.
   - **Patterned / Bespoke** → private git repo of the user's skills or their
     dotfiles. Unsure whether content is safe to publish → treat as private.
3. **Validate before publishing:**
   - Frontmatter has `name` (matching directory) and `description` ($\le 1024$
     chars, no `<...>` tags); uses only the 6 standard `agentskills.io` keys if
     packaged as `.skill`.
   - `SKILL.md` is under 500 lines and `< 5,000 tokens` (~20 KB); detailed
     procedures live one level deep in `references/*.md`.
   - Zero PII, zero user/project-specific identifiers, and 3+ alternatives if
     referencing non-ubiquitous tools.
4. **Reconcile proactively:** Whenever publishing or updating a skill, compare
   all local install locations (`~/.claude/skills/`, `~/.gemini/skills/`,
   `~/.gemini/config/skills/`, `.claude/skills/`) against the source repo and
   resolve any drift or duplicate channels with the user's blessing.

## Close the flywheel

Once this skill has run in a session, make sure the standing capture behavior is
in place: if the agent's global context doesn't already instruct it to watch for
and *propose* capturing reuse opportunities, propose adding that line
(discover-or-seed, with the user's blessing). That converts one-off capture into
an ongoing loop — the agent notices opportunities, this skill captures them, and
capture keeps the watch-behavior alive. Propose, never auto-write; the
watch-behavior proposes skills, it doesn't silently generate them.

## Cross-Skill References

Skills must be self-contained. A skill that fails or misleads when a referenced
skill is absent is a broken skill.

- **Only reference co-packaged skills** — distributed in the same marketplace
  collection, plugin, or repo. Never reference skills from external sources.
- **Hint-level only** — references must be non-essential hints to supplementary
  content (e.g., *"The `setup-agent-context` skill, if available, covers this in
  more detail."*). Never write references that create a hard dependency.
- **Prefer duplication over cross-skill dependencies** — if a skill needs
  specific content from another skill to work correctly, duplicate those
  paragraphs inline rather than creating a dependency chain that breaks when a
  skill is missing.
- **Exception: platform-native bundled skills** — skills privately co-bundled
  into an **agent platform** (Claude Code, Gemini CLI, Antigravity, Cursor — use
  "agent platform" as the umbrella term, not "IDE" or "CLI" alone) and *not*
  published to a standalone marketplace may use firm cross-references because
  co-presence is guaranteed.
