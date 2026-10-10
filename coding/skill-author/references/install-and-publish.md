# Installing, Testing, Publishing, and Reconciling Skills

Load this reference after authoring or revising a skill when you are ready to
install it locally, package a `.skill` bundle, test discoverability and
behavior, publish to a skills repo or marketplace, or reconcile duplicate and
drifted installs across agent platforms.

For Claude desktop app specifics (`.skill` bundle install commands on macOS,
updating in place, the two saved copies and sync lag, and comparing reformatted
frontmatter), also see `references/claude-desktop.md` in this skill.

---

## 1. Detect the Surface Before Choosing an Install Method

Don't blindly copy whatever `~/.claude/skills/` or `~/.gemini/skills/` already
shows. The right install channel depends on where the agent is actually running:

- **Standalone Claude Code (terminal CLI, `CLAUDE_CODE_ENTRYPOINT=cli`):**
  filesystem only — symlink into `~/.claude/skills/<name>/`, `npx skills add`,
  `echomodel skills install`, or a plugin. This is the only channel here.
- **Claude Code embedded in the Claude Desktop app (the "Code" tab,
  `CLAUDE_CODE_ENTRYPOINT=claude-desktop`):** the desktop app injects its own
  managed skills plugin (named `anthropic-skills`) into this tab, carrying
  Anthropic built-ins **and** skills saved to the user's Claude account. So a
  skill saved once in the Claude app already appears here once the app syncs
  its load copy (see `references/claude-desktop.md`). **Here, the Claude
  account is the default channel. Keep a `~/.claude/skills` link only for a
  skill that can run only on this machine (it drives the local browser or
  reads local files), and never install one skill both ways.** The Code tab sees the union of that injected
  plugin + native `~/.claude/skills`. The `.skill` build is a plain stdlib zip,
  and `open <file>.skill` triggers the desktop install popup directly.
- **A Claude app conversation (web, desktop, or mobile):** see "Installing from
  a Claude app conversation" below. Chat and Cowork were merged into one Claude
  conversation in September 2026, so anything older that says "Cowork" now
  means an ordinary Claude conversation.
- **Gemini CLI:** check `gemini skills list`. Prefer `gemini skills link` when
  working from a local clone of a skills repo.
- **Antigravity (`agy` / IDE):** discovers user-scope skills from
  `~/.gemini/config/skills/<name>/SKILL.md` (and workspace skills from
  `.agents/skills/<name>/SKILL.md` or `.claude/skills/<name>/SKILL.md`). Note
  that `~/.gemini/config/skills.json` does **not** expand `~` or `$HOME` in
  `path` entries — use relative symlinks in `~/.gemini/config/skills/<name>`
  pointing to the source repo directory so dotfiles stay portable across
  machines without hardcoded home paths.

Match an existing pattern only within the *same* channel — don't assume the
symlinks in `~/.claude/skills` are how a Desktop user's skills got there. Save
the resolved method to memory.

---

## 2. Install Locally

Install the skill so it's available in your agent platform before publishing
anywhere.

| Scope | Path / Command | When to use |
|-------|----------------|-------------|
| Claude Code (user) | `~/.claude/skills/<name>/SKILL.md` | Default for standalone CLI. Available in all projects on this machine. |
| Project (cross-agent) | `.claude/skills/<name>/SKILL.md` or `.agents/skills/<name>/SKILL.md` | Skill is specific to this repo and should be versioned with it. |
| Gemini CLI | `gemini skills link <local-path>` or `gemini skills install <path-or-url>` | Gemini CLI native install/link. |
| Antigravity (user) | `~/.gemini/config/skills/<name>` (relative symlink to skill dir) | Antigravity global skill discovery. |

**User-scope is the default.** Install at project scope only when the skill is
inherently tied to the repo (e.g., repo-specific workflow, project conventions).

### Platform install commands

**Gemini CLI:**

```bash
# Link a local clone (live updates, no reinstall needed — preferred for local repos)
gemini skills link <local-path>/<collection>/<skill-name>

# Install a single skill from a remote collection
gemini skills install <repo-url> --path <collection>/<skill-name>

# Install an entire collection
gemini skills install <repo-url> --path <collection>
```

`gemini skills link` creates a live link — edits to the source are reflected
immediately with no reinstall. Prefer this over `install` when working from a
local clone of the skills repo.

**Claude Code (standalone CLI):**

Standalone Claude Code has no skill management CLI. Install by symlinking from
a local clone of the marketplace repo (skip this if the user is on Claude
Desktop and the skill is already saved to their Claude account — it's injected
into the Code tab there):

```bash
# Clone the skills repo (once per machine)
git clone <repo-url> <local-path>

# Symlink the skill directory or SKILL.md
ln -s <local-path>/<collection>/<skill-name> ~/.claude/skills/<skill-name>
```

Symlinks keep the local install in sync with `git pull` — no re-copy needed
after updates.

**Antigravity (`agy`):**

```bash
# Relative symlink from ~/.gemini/config/skills/ so no hardcoded home path is needed
ln -s ../../../<relative-path-from-home>/<collection>/<skill-name> \
  ~/.gemini/config/skills/<skill-name>
```

**Plugin-bundled skills:**

If the skill ships inside a Claude Code plugin rather than a standalone
marketplace, the install command is different:

```bash
claude plugin install <plugin-name>@<marketplace> --scope user
```

Skills bundled in plugins are managed by the plugin lifecycle, not by manual
symlinks or copies.

### Project-scoped skills and git tracking

When installing at project scope, ensure the skill files will be
version-controlled:

1. Check that `.claude/skills/` (or `.agents/skills/`) is not gitignored. Many
   repos ignore `.claude/` entirely — add a `!.claude/skills/` exception in
   `.gitignore` if needed.
2. Run `git status` after creating the skill to confirm the new `SKILL.md`
   appears as untracked or staged.
3. If a `.gitignore` change was required, verify it didn't expose other files
   under `.claude/` (settings, cache, logs). Evaluate any newly surfaced files
   case by case before committing.

The `setup-agent-context` skill, if available, covers `.gitignore` management
for agent directories in detail — including per-file guidance on what to
version vs. exclude.

### Building a `.skill` bundle

A `.skill` bundle is a zip of the skill directory with `SKILL.md` at the root
of the zip (or inside a top-level `<name>/` folder).

- **Build from committed code** when the skill lives in a repo: commit first,
  then build, so what gets installed always matches version control. (In a
  Claude app conversation with no repo, see the next section.)
- **Include only what the skill needs:** `SKILL.md` plus any `references/`,
  `scripts/`, and `assets/` it uses.
- **Exclude:** `.git/`, virtualenvs (`venv/`, `.venv/`), `node_modules/`,
  caches (`__pycache__/`, `*.pyc`), editor and OS clutter (`*.swp`,
  `.DS_Store`), and above all **secrets and personal data** — `.env` files,
  credentials, tokens, local config, or user data files. `.git/` matters for
  the same reason: it carries the full history, including anything once
  committed and later removed.
- **Check before handing it over:**
  - Frontmatter uses **only the 6 standard `agentskills.io` keys** (`name`,
    `description`, `license`, `compatibility`, `metadata`, `allowed-tools`).
    The Claude app and `package_skill.py` reject any other frontmatter key
    (`Unexpected key(s) in SKILL.md frontmatter`).
  - `description` is at most 1024 characters with no tag-like `<...>` text (the
    Claude app rejects either).
  - Any bundled scripts use the Python standard library only.
- List the zip's contents before presenting it, and confirm nothing unexpected
  is inside.

### Installing from a Claude app conversation

When running in a Claude app conversation (it can present files but can't write
to the user's repos), write the skill here rather than handing another agent a
prompt to write it:

1. Write or edit it, starting from the installed copy when editing.
2. Package it: a single `SKILL.md`, or a `.skill` bundle per "Building a
   `.skill` bundle".
3. Present it as a file card to save or download, and say what changed.
4. Prompt the user to add it to a repo of their choice (see "Choose where the
   skill is versioned"), since an account-only copy has no history. Offer a
   short prompt for a local agent to copy the installed skill into that repo
   and then follow the user's normal workflow. Note that the app may reformat
   frontmatter on save (e.g. quoting `name:`), so compare content, not bytes,
   and keep the version as authored.

A conversation can't see skills saved during it, so verification happens in the
local agent or a new conversation.

### Verify the install landed — in the right place

Some platforms keep more than one copy of an installed skill: the store the
install writes to, and a separate copy that agents load from, which syncs
later. Check a save against the store the install wrote; check what agents will
actually get against the copy they load from, or ask a fresh agent to quote a
line unique to your edit. Expect a lag between the two.

Installers may also reformat frontmatter on save (quoting values, re-flowing
folded strings). Compare frontmatter as parsed data and the body exactly, not
file bytes, or every save will look like a difference. See
`references/claude-desktop.md` for Claude desktop app paths and comparison
rules.

---

## 3. Test the Skill

**Verify it's discoverable.** Before testing behavior, confirm the agent
platform sees the skill:

```bash
# Gemini CLI
gemini skills list

# Claude Code — check the slash menu or ask:
claude -p "list your available skills"
```

If the skill doesn't appear, check the install path and directory name.

**Test behavior.** Run a headless prompt that indirectly reveals whether the
skill loaded and influenced the agent's behavior. The prompt should exercise
the skill's guidance without requiring actual disk I/O or other privileged tool
usage — this keeps the test fast and safe.

```bash
# Claude Code
claude -p "prompt that reveals the skill's effectiveness"

# Gemini CLI
gemini -p "prompt that reveals the skill's effectiveness"
```

**Designing a good test prompt:**

- Ask the agent to describe how it would approach a task the skill covers. The
  response should reflect the skill's specific guidance, not generic behavior.
- If the skill has distinctive rules or preferences, ask about a scenario where
  those rules apply and check whether the response follows them.
- Add `--allowedTools ""` or similar flags to prevent actual tool execution if
  the prompt might trigger it. The goal is to verify the skill shaped the
  agent's reasoning, not to run a full workflow.
- For skills with `user-invocable: true`, test slash-command invocation too:
  does `/my-skill` trigger it?

---

## 4. Publish

Once the skill works locally, publish it. Skills that stay local get forgotten
— publish promptly so the skill is available where you (and others) will
actually use it. If the user hasn't specified a destination, ask where it
should go and push for a decision now.

### Choose where the skill is versioned — always ask

Every skill must end up version-controlled somewhere durable; an installed-only
copy is a single point of failure. **Ask the user which repo it belongs in** —
don't assume the public marketplace. Decide by reuse tier:

- **Generic** → a public marketplace (e.g. echoskill), only after the "Validate
  before publishing" checks pass.
- **Patterned / Bespoke** → a **private** git repo of the user's skills, or the
  user's **dotfiles** if that's how they version machine config (chezmoi, yadm,
  GNU Stow, or a bare-repo dotfiles setup — ask which they use). Private does
  not mean unversioned.
- Unsure whether content is safe to publish → treat it as private. Moving a
  skill from private to public later is easy; retracting a public leak is not.

Data-backed skills are usually Patterned or Bespoke: the generic process may be
publishable, but personal specifics belong in the data store, not the skill.
When a skill mixes both, split it: generic mechanism in the skill, identity in
the data store.

Save the chosen destination so later sessions don't re-ask.

### Where to publish

- **Cross-platform skills** go in the primary skills marketplace (e.g.,
  echoskill). These work across agents and belong in topical collections
  (`coding/`, `prompting/`, `consulting/`).
- **Platform-specific skills** go in a platform-specific collection or repo. If
  a skill genuinely only works on one agent (e.g., depends on Claude Code's
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

- **Frontmatter is complete**: `name` and `description` are required; only the
  6 standard `agentskills.io` keys are used if the skill may be packaged as a
  `.skill` bundle.
- **Name matches directory name.**
- **Size and progressive disclosure**: `SKILL.md` is under 500 lines and
  `< 5,000 tokens` (~20 KB); detailed procedures live in `references/*.md` one
  level deep with a routing table in `SKILL.md`.
- **No references to specific consuming repos or projects.** Usage examples
  must be generic. If repo-specific references are found, rewrite them to be
  generic before publishing.
- **No PII or user-specific identifiers** — account numbers, emails, names,
  repo/store names, folder ids, property names, real dollar figures. That's
  *identity*, not mechanism: externalize to config and recall at runtime. If a
  different user would need a different value, it's leaked config — pull it out
  before publishing.
- **Bundled scripts are fine, but note the portability cost** — a skill that
  bundles executable scripts targets Claude Code (or compatible); for a skill
  that must work across every agent, keep it instruction-only or move the code
  to a plugin/package.
- **No hard dependencies on non-ubiquitous tools** without offering 3+
  alternatives.

### Publish workflow

1. Copy the skill directory to the target repo at the confirmed path
2. Update the `README.md` table for the collection if one exists
3. `git diff --staged` to review
4. Confirm with the user
5. Commit and push
6. Show the user how to install the skill on other machines using actual values
   from the publish (repo URL, collection, skill name) — not angle-bracket
   placeholders.

---

## 5. Avoid Duplicate Installs & Reconcile Drift

### Avoiding duplicate installs

A skill can reach an agent through more than one channel:

- **Plugin/extension bundle** — managed by the packaging layer's install and
  update lifecycle (including Claude Desktop's `anthropic-skills` account sync).
- **Standalone symlink** — a link from the user-scope skills directory to a
  source repo. Live updates via `git pull`.
- **Standalone copy** — a plain file in the user-scope skills directory. Static
  snapshot, no link back.

Each is valid alone. But when two channels deliver the same skill
simultaneously, the agent's slash menu and skills listing show the skill twice,
and whichever copy loads first may not be the one the user expected.

**Rule: one channel per skill per machine.** If the user's installed
plugin/extension already bundles the skill, do not also install it standalone.
If they've chosen the symlink path, do not install the bundling
plugin/extension.

**Bundling scope (for authors of plugins/extensions):** a plugin/extension
should bundle a skill only if the plugin's own machinery (its agents, hooks,
MCP servers, native skills, or scripts) directly depends on that skill.
Bundling a skill purely for user convenience — because it's useful alongside
the plugin — is an "alt marketplace install" anti-pattern that creates the
duplication problem above. General-purpose skills belong in their own
marketplace; consumers install them separately.

**When duplicates are already present, reconcile:**

1. **Audit.** Search all install locations for the skill name — user-scope
   skill directories for standalone copies and symlinks, plugin/extension cache
   directories for bundled copies.
2. **Classify.** For each hit, determine whether it is a bundled copy (under a
   plugin/extension cache), a symlink to a source repo (run `readlink` or
   `ls -la`), or a static standalone copy.
3. **Pick one channel.** Prefer the channel already used for similar skills on
   this machine — don't introduce a new pattern for a single skill.
4. **Remove the others.** Standalone copies and symlinks: delete from the
   user-scope directory. Bundled copies: uninstall the bundling
   plugin/extension — but only if that plugin as a whole is the channel being
   dropped, not because it happens to bundle one duplicate skill.
5. **Restart the agent session** so menus and listings rebuild against the
   resolved set.

**The slash menu and skills listing are the warning signal.** If the same skill
name appears more than once, a duplicate-install situation exists. Investigate
before assuming one version is authoritative.

### Reconcile local installs with skills repo

Skills drift when they exist in multiple places — the local platform install
directory and the personal skills repo. Every publish action is an opportunity
to reconcile.

**Locate the skills repo.** Check memory for a previously saved skills repo
path. If not found, ask the user where their personal skills repo / marketplace
lives and save it to memory for future sessions (e.g., memory name:
`skills-repo-location`, type: `reference`).

**Known local install locations:**

- `~/.claude/skills/<name>/SKILL.md` — Claude Code user-scope
- `~/.gemini/skills/<name>/SKILL.md` — Gemini CLI user-scope (check
  `gemini skills list` for installed locations)
- `~/.gemini/config/skills/<name>/SKILL.md` — Antigravity user-scope
- `.claude/skills/<name>/SKILL.md` / `.agents/skills/<name>/SKILL.md` —
  project-scope (current repo)

**For each skill being published, compare across all locations:**

1. **Gather facts.** For each copy of the skill (local installs + repo), check:
   - Does the file exist?
   - File size and last-modified timestamp (`stat` or `ls -la`)
   - Content (`diff` between copies)
2. **Report to the user.** Present a clear status for each location:
   - **Missing in repo but installed locally** — the skill hasn't been
     published yet. Recommend copying local → repo.
   - **In repo but not installed locally** — the skill was published but never
     installed on this machine, or was removed. Recommend linking/copying
     repo → local.
   - **Identical in both** — in sync, nothing to do.
   - **Different** — show the diff. Recommend a direction based on timestamps
     (newer usually wins), but always ask the user which version to keep, or
     whether to merge changes manually.
3. **Act with user's blessing.** After the user confirms the direction:
   - Copy or symlink the chosen version to the target location(s)
   - Stage, commit, and push the skills repo if it was updated
   - Confirm the local install is current if that was updated
4. **Save the repo location to memory** if not already saved, so future publish
   actions skip the "where is your skills repo?" step.

**Do this reconciliation proactively** — don't wait for the user to ask. Every
time a skill is published or updated, check the other locations and flag drift.
The goal is a single source of truth in the repo with local installs as
consistent copies or symlinks.

---

## 6. Consider Agent Preloading

If the skill was developed for use by a specific custom agent or subagent (e.g.,
a coding agent, a review agent), consider whether that agent's `skills:`
frontmatter should be updated to preload it. Preloading injects the full skill
content into the subagent's context at startup — the subagent doesn't need to
discover or invoke the skill; it just has the knowledge.

```yaml
# In the agent's .md frontmatter:
skills:
  - safe-commit
  - show-code       # ← new skill preloaded here
```

**Platform support for skill preloading in agents:**

- **Claude Code** — supported via `skills:` list in agent/subagent frontmatter.
  Full skill content is injected at startup. Subagents don't inherit skills
  from the parent; list them explicitly.
  ([Claude Code docs: Preload skills into subagents](https://code.claude.com/docs/en/sub-agents#preload-skills-into-subagents))
- **Gemini CLI & Antigravity** — no equivalent frontmatter preloading mechanism
  as of 2026. Skills are discovered and loaded via progressive disclosure, not
  preloaded into agent definitions.
- **agentskills.io** — the spec covers skill format only, not agent definitions
  or skill-to-agent binding.

**When to preload vs. let the agent discover:**

- Preload when the custom subagent should *always* have this knowledge (e.g.,
  commit workflow, code style rules).
- Let discovery handle it when the skill is situational (e.g., PDF processing,
  dependency evaluation).
