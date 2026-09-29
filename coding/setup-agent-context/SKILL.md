---
name: setup-agent-context
description: "Configure coding agent context for a repo by setting up CLAUDE.md, AGENTS.md (or GEMINI.md), .gemini/settings.json, and .gitignore rules. Use when starting a new project, onboarding a repo for AI-assisted development, or when asked to set up agent context, configure Claude/Gemini/Antigravity for a repo, or make a repo AI-ready."
---

Set up the standard agent context files so that Claude Code, Antigravity, and
Gemini CLI all automatically load the repo's README.md and CONTRIBUTING.md as
context — with zero agent-only prose duplication.

## What this skill creates/updates

1. **`CLAUDE.md`** (repo root) — a short pointer file for Claude Code
2. **`AGENTS.md`** (or existing **`GEMINI.md`** in repo root) — a short pointer file for Antigravity
3. **`.gemini/settings.json`** (repo root) — context file declarations for Gemini CLI
4. **`.gitignore`** — exclude `.gemini/` but include `!.gemini/settings.json`
5. **`README.md` / `CONTRIBUTING.md`** — links to every `docs/**/*.md`

## What belongs where

`CLAUDE.md` and `AGENTS.md` (or `GEMINI.md`) tell agents where to look. The
actual content lives in:

- **README.md** — what the project is, how to install and use it
- **CONTRIBUTING.md** — architecture, design principles, constraints, testing
  conventions, SDK structure, how to add features

This separation means Claude Code, Antigravity, and Gemini CLI all get
identical context from the same human-readable source files, with no
duplication. Every other placement rule in this skill — including which file
should link which docs — derives from this split.

## Step 1: Read existing files

Before making changes, read these files if they exist:
- `CLAUDE.md`
- `AGENTS.md`
- `GEMINI.md`
- `.gemini/settings.json`
- `.gitignore`
- `README.md` (to confirm it exists)
- `CONTRIBUTING.md` (to confirm it exists)

If README.md or CONTRIBUTING.md don't exist, tell the user and ask whether
to proceed anyway or create them first.

## Step 2: Ensure every `docs/**/*.md` is linked from README.md or CONTRIBUTING.md

Any markdown file living under `docs/` is only useful if readers (human or
agent) can discover it. The root `README.md` (and, for contributor-facing
docs, `CONTRIBUTING.md`) must link to every such file.

### Rules

- **Every `docs/**/*.md` file must be reachable** from `README.md` or
  `CONTRIBUTING.md`. Transitive discovery via an intermediate doc is fine
  (e.g., `README.md` → `docs/index.md` → `docs/third-party-product/categories.md`) as
  long as the chain starts at a top-level document.
- **Links must use markdown hypertext syntax** with both a descriptive
  title and a relative URL — e.g.,
  `[Third-Party Product Categories](docs/third-party-product/categories.md)`. Bare URLs,
  paths without titles, or plain text filenames are not sufficient.
- **Link titles must read as natural prose**, not filenames. No `.md`
  extension, no directory segments, no snake_case / kebab-case, no
  `UPPERCASE_IDS`. The title is what a human reader sees — it should be
  a short descriptive phrase (title case or sentence case), not the
  technical identifier of the target file.
  - Good: `[Third-Party Product Categories](docs/third-party-product/categories.md)`
  - Bad: `[docs/third-party-product/categories.md](docs/third-party-product/categories.md)`
  - Bad: `[categories.md](docs/third-party-product/categories.md)`
  - Bad: `[third-party-product-categories](docs/third-party-product/categories.md)`
  - This rule applies to every link between docs — README → docs, docs →
    docs, CONTRIBUTING → docs. Fix existing offenders when encountered.
- **Relative URLs only.** Never absolute paths or
  `https://github.com/.../blob/...` links for intra-repo docs — relative
  links stay correct across forks, mirrors, and local checkouts.
- **Audience determines which file links the doc.** Apply the README vs
  CONTRIBUTING split defined in "What belongs where" above:
  user-facing docs are linked from README.md; contributor-facing docs are
  linked from CONTRIBUTING.md. When a doc is genuinely dual-audience,
  prefer README.md and cross-link from CONTRIBUTING.md if helpful.
- **Every link carries a short summary of what it points to.** Never leave
  a bare link that a reader (or agent) has to open blindly. Pair each link
  with a 1-2 sentence description of the target doc's content — enough
  that someone who doesn't open the link still has a working mental model
  of what's there. This applies in both directions: from README or
  CONTRIBUTING down to docs, and from one doc to another.

  Two reasons:

  1. **Context residency.** Agents and humans often read the referring
     doc without following every link. A short summary ensures at least
     a skeletal understanding of the linked content is in memory even
     when the target isn't fetched. Bare links add zero context.
  2. **Informed incentive to open the target.** A title alone doesn't
     tell a reader whether the linked doc is worth loading right now.
     A summary lets them decide whether the target is relevant to their
     current task.

  Example shapes:

  - **Prose with inline link:** "See [Third-Party Product Categories](docs/third-party-product/categories.md),
    which lists every default category, its group, and the group's
    income/expense/transfer type, and explains why the product's defaults
    can double-count certain flows if left unchanged."
  - **Sectioned list with description:** a heading like "Documentation"
    followed by bullets where each bullet is `[Title](path)` — 1-2
    sentence summary. More compact than prose when linking many docs
    at once.

  Keep summaries short (one to two sentences). If a doc needs a longer
  description, that's a signal the title itself should be more
  descriptive, or the target should have a clearer lead paragraph that
  can be mirrored.

### Process

1. Enumerate all `docs/**/*.md` files.
2. For each one, search `README.md` and `CONTRIBUTING.md` for a markdown
   link to that relative path. A match anywhere in the chain of linked docs
   counts (transitive is fine).
3. For any unlinked doc, tell the user which file was found and propose a
   placement (README.md vs CONTRIBUTING.md, and which section or heading).
4. After user confirmation, add the links using descriptive titles and
   relative URLs. Group related docs under a section heading like
   "Documentation", "References", "Architecture", etc. — don't sprinkle
   orphan bullets at the bottom.

If the repo has no `docs/` directory, skip this step.

## Step 3: Ensure CONTRIBUTING.md declares a Version Management section

Repos that ship a versioned artifact need a Version Management section
in `CONTRIBUTING.md` — without it, contributors (and agents) reinvent
the bump rules per change, miss bumps entirely, and downstream
consumers stay on stale code because `pip install --upgrade` and
`pipx install --upgrade` only re-install when the version number
rises.

This step is conditional on repo shape. Detect:

| Shape | Signal | Version source of truth |
|-------|--------|-------------------------|
| Python package | `pyproject.toml` exists | `<pkg>/__init__.py` `__version__` (mirrored in `pyproject.toml`) |
| Claude plugin | `.claude-plugin/plugin.json` exists | `version` field in `plugin.json` |
| Both (a Python package distributed as a plugin) | both files present | bump both fields together in one commit |
| Neither | no signal | skip this step |

If the relevant shape applies and `CONTRIBUTING.md` has no Version
Management section, propose adding one. The section must cover:

- **Source(s) of truth** — name the file(s) and field(s) the version
  lives in. Where two locations mirror (e.g., `__init__.py` and
  `pyproject.toml`), state explicitly that both must move together
  in the same commit.
- **When to bump** — at minimum, a semver table mapping change type
  to bump kind (patch / minor / major). Include a note that
  documentation-only changes don't require a bump.
- **Bump-with-change as the default** — the version moves in the
  same commit as the change it ships with, not a separate commit.
  This keeps history honest (one commit = one logical change at
  one version) and avoids cluttering the log with bump-only commits.
- **Catch-up bump rule** — if a runtime-touching change shipped
  without a bump, fix it with a small follow-up commit titled
  `Bump version to X.Y.Z` whose body briefly notes what unreleased
  changes the bump covers. No `chore:` prefix — Conventional
  Commits ceremony is only appropriate when the repo runs
  `semantic-release`, `python-semantic-release`, `release-please`,
  or a similar Conventional-Commits-aware release tool. Detect via
  presence of `.releaserc*`, `release.config.*`, related
  `pyproject.toml` config, or a release workflow under
  `.github/workflows/`.
- **Release workflow** — concrete commands for editing the version
  file(s), committing, tagging (`vX.Y.Z` annotated), and pushing
  with tags.

**Field validation** for Python packages: the `__version__` value
must equal the `pyproject.toml` `version` value. If they drift,
flag it and propose a single commit that reconciles them.

Do not write the section blindly — fill in the actual file paths,
field names, and any project-specific bump-significance rules
(e.g., a framework whose major version is also a contract version
needs to call that out). When in doubt, model the section after a
sibling repo's existing Version Management section.

## Step 4: Create or update CLAUDE.md (for Claude Code)

The file should use Claude Code's `@path` import syntax to pull README.md
and CONTRIBUTING.md into context at session start. Do not put project-specific
instructions here — those belong in CONTRIBUTING.md. The CLAUDE.md content
should be:

```markdown
@README.md
@CONTRIBUTING.md
```

If additional lines already exist in CLAUDE.md (e.g., PII warnings for
public repos), preserve them. Only add the `@` imports if missing.

*Note on Claude Code and `AGENTS.md`:* By default (`claude-md-or-agents-md`),
Claude Code reads `CLAUDE.md` only and ignores `AGENTS.md` whenever `CLAUDE.md`
is present, so keeping both files causes zero duplicate loading.

## Step 5: Create or update AGENTS.md or GEMINI.md (for Antigravity)

Antigravity does not read `.gemini/settings.json`'s `context.fileName` or
`CLAUDE.md`; instead, it automatically discovers `AGENTS.md` and `GEMINI.md`
in the repository root and expands `@[label](path)` includes inline.

### Which filename to use
- If **`GEMINI.md` already exists** in the repo root and **`AGENTS.md` does not**,
  keep using **`GEMINI.md`** for backwards compatibility.
- Otherwise, create or update **`AGENTS.md`**.

### Pointer content
Do not put standalone project prose in `AGENTS.md` or `GEMINI.md` — move any
existing architectural or contributor rules into `CONTRIBUTING.md` first, then
set the file content to:

```markdown
@[README.md](README.md)
@[CONTRIBUTING.md](CONTRIBUTING.md)
```

### 24 KB inline expansion check
Antigravity enforces a **24,000-byte per-rule-file limit** after expanding
`@[label](path)` includes. Check the combined byte size of `README.md` +
`CONTRIBUTING.md`:
- If under 24,000 bytes, include both `@[README.md](README.md)` and
  `@[CONTRIBUTING.md](CONTRIBUTING.md)`.
- If over 24,000 bytes, warn the user and include only
  `@[CONTRIBUTING.md](CONTRIBUTING.md)` so contributor rules are never
  truncated.

## Step 6: Create or update .gemini/settings.json (for Gemini CLI)

```json
{
  "context": {
    "fileName": [
      "README.md",
      "CONTRIBUTING.md"
    ]
  }
}
```

If the file already exists, merge the context entries — don't overwrite
other settings that may be present.

## Step 7: Update .gitignore

Agent context directories (`.claude/`, `.gemini/`) contain a mix of
versioned configuration and local-only state. The `.gitignore` must
selectively include the files that should be shared while excluding
everything else.

Ensure these entries exist in `.gitignore`:

```
.claude/
!.claude/skills/
.gemini/
!.gemini/settings.json
```

**Why each line matters:**
- `.claude/` — excludes local Claude Code state (settings, cache, MCP config)
- `!.claude/skills/` — re-includes project-scoped skills so they're versioned
- `.gemini/` — excludes local Gemini state files
- `!.gemini/settings.json` — re-includes context configuration

Only add the `.claude/skills/` exception if the project actually has or
will have project-scoped skills. Don't pre-create it speculatively.

## Step 8: Verify git tracking

After modifying `.gitignore` or adding context/settings files for the
first time, run `git status` and verify:

1. **Expected files appear.** New or modified files under `.claude/` or
   `.gemini/` should show as untracked or staged — not invisible. If a
   file you just created doesn't appear in `git status`, the `.gitignore`
   is still excluding it. Debug the ignore rules.

2. **No unexpected files surfaced.** Changing `.gitignore` exclusion
   patterns can expose files that were previously hidden. If ANY file
   under `.claude/` or `.gemini/` newly appears in `git status` as a
   result of a `.gitignore` change, evaluate it **case by case** before
   proceeding. Do not batch-add or assume safety. Specific guidance:

   - **`.claude/settings.json` and `.gemini/settings.json`** — version
     these when they contain clean, portable, agent-helpful config:
     `context.fileName` arrays, `allowedTools` lists, tool permissions,
     or other settings that help collaborators and agents work
     consistently. These are valuable to share. But read the full file
     first — verify it contains no absolute paths with usernames,
     credentials, API keys, or references to local-only MCP servers
     by path. If clean: stage and commit. If not: clean it up or add
     a specific ignore rule.
   - **Cache, log, or state files** (e.g., `.cache/`, `*.log`,
     session history, MCP connection state) — never version these.
     They are ephemeral, machine-specific, and add noise. Add specific
     ignore rules if they surface.
   - **Any other file** under these directories that newly surfaces —
     do not commit without reading its content and understanding why it
     exists. When in doubt, add a specific ignore rule for it.

3. **Confirm with `git check-ignore`.** For any file you expect to be
   tracked, run `git check-ignore -v <path>` to confirm it is NOT
   ignored. For files that should stay excluded, confirm they ARE ignored.

## Step 9: Security scan before committing

Before staging any file under `.claude/` or `.gemini/` for commit, scan
its content for sensitive data:

- **Absolute paths with usernames** — `/Users/<name>/`, `/home/<name>/`.
  Replace with `~`, `$HOME`, or relative paths.
- **API keys, tokens, credentials** — never commit these, even to
  private repos.
- **User-specific identifiers** — GCP project IDs, Google Doc IDs, email
  addresses, account IDs.
- **Local MCP server registrations** — `.claude/settings.json` often
  contains `stdio` server entries with absolute paths to local
  executables. These are not portable and should not be committed.
- **Allowed-tool lists** — `.gemini/settings.json` may contain
  `allowedTools` arrays. These are generally safe to commit (they help
  collaborators), but verify they don't reference local-only MCP servers
  by path.

**The rule:** if a `.json` file under `.claude/` or `.gemini/` is being
git-added for the first time or has changed after a `.gitignore` edit,
read its full content and verify it contains nothing user-specific or
sensitive before committing. This is especially important because these
files are easy to commit reflexively with `git add .` without reviewing.

## Step 10: Report

Tell the user what was created or updated. Mention that Claude Code,
Antigravity, and Gemini CLI will now load README.md and CONTRIBUTING.md as
context, and that project-specific instructions belong in CONTRIBUTING.md.
If any `docs/**/*.md` files were newly linked, list them and note where the
link was added. If `.gitignore` was modified, note which files are now
versioned and confirm no sensitive content was exposed.
