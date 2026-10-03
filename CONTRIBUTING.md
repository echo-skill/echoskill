# Contributing

## Repo Structure

This repo is organized into **collections** — top-level folders that
each function as a self-contained skill marketplace. Skills within a
collection are portable and dependency-free by default, unless the
collection name signals otherwise.

```
echoskill/
  coding/              ← general-purpose collection (portable, no dependencies)
    skill-a/SKILL.md
    skill-b/SKILL.md
  prompting/           ← general-purpose collection (portable)
    capture-context/SKILL.md
  claude/              ← platform-specific (Claude Code only)
    sessions/SKILL.md
```

Each skill is a directory containing a `SKILL.md` file. Each collection
is a directory containing one or more skill directories.

### Collections as mini-marketplaces

Each collection is independently installable. Skill management tools
consume them at the collection level:

```bash
# Gemini CLI — install one collection or one skill
gemini skills install <url> --path coding
gemini skills install <url> --path coding/skill-a

# ecm — register the whole repo, auto-discovers collections
ecm skills marketplace register echoskill <url>
# produces: echoskill/coding, echoskill/prompting, echoskill/claude, …
```

`gemini skills install` scans one level deep within a `--path` target
for `*/SKILL.md`. Without `--path`, it scans from repo root — which
finds nothing here because skills are two levels deep (collection →
skill → SKILL.md). Gemini users must specify `--path` per collection.

`ecm skills marketplace register` auto-discovers collections by
classifying the immediate children of the target path as skills,
collections, or both — and registers each collection as a derived
marketplace with a compound name (e.g., `echoskill/coding`).

See the [compatibility guide](docs/COMPATIBILITY.md) for detailed
behavior across platforms.

### Portability expectations by collection

**General-purpose collections** (`coding/`, `prompting/`, `consulting/`):
skills must be portable and dependency-free. They should work for any
user on any platform without requiring specific tools or frameworks.
If a skill references a tool, it must offer 3+ alternatives (see
Tool Dependencies below).

**Platform-specific collections** (`claude/`, `gemini/`): skills may
depend on platform-specific features. The collection name signals this
— users installing `claude/` skills expect Claude Code.

**Ecosystem-specific collections** (named for the ecosystem they
promote): skills may assume the user has or is adopting the
ecosystem's tooling. They should still support standard
alternatives where practical but are allowed to recommend the
ecosystem's tools as the primary path. The collection name
signals this intent. (None currently present in this repo —
ecosystem-native skills may be co-located in their ecosystem's
primary framework repo instead, e.g., `skills/` in the framework
repo itself.)

## Adding a Skill

1. Create `<collection>/<skill-name>/SKILL.md`
2. Include `name` and `description` in YAML frontmatter (required)
3. Keep the `name` field matching the directory name
4. Write platform-neutral instructions when possible
5. If the skill is platform-specific, place it under `claude/` or `gemini/`
6. If the skill promotes a specific ecosystem, consider whether
   it belongs in an ecosystem-named collection here or co-located
   with the ecosystem's primary framework repo

## Frontmatter

Use standard [agentskills.io](https://agentskills.io/specification) fields.
Claude-specific fields (e.g., `disable-model-invocation`) are allowed — Gemini
ignores them.

## No Scripts

Skills in this repo are pure instructions. If a skill requires deterministic
script execution, it belongs in a plugin (Claude) or extension (Gemini).

## Tool Dependencies

Skills in a general-purpose marketplace must not hard-depend on tools that
the average consumer of an open marketplace of skills is unlikely to have
installed. If a skill needs a non-ubiquitous tool, it must offer 3+
alternatives so it works for everyone. See the
[skill-author](coding/skill-author/SKILL.md) skill for the pattern.

## Skill Memories

Skills can instruct the agent to save memories (persistent notes for future
sessions). The agentskills.io specification explicitly permits this:

> "The Markdown body after the frontmatter contains the skill instructions.
> There are no format restrictions. Write whatever helps agents perform the
> task effectively."
>
> — [agentskills.io/specification](https://agentskills.io/specification),
> "Body content" section

Since skills are loaded as instructions into the agent's context, and both
Claude Code and Gemini CLI agents have memory tools available during normal
operation, a skill instruction like "save a memory recording which method
was used" triggers normal tool use — no special mechanism needed.

### Guidelines for skill authors

- Be explicit: "After completing this workflow, save a memory noting: the
  publishing method used was [method], the target repo was [repo]."
- Specific instructions produce more reliable results than vague ones.
- Memory instructions are best-effort — agents follow them with high
  reliability but they are instructions, not enforced configuration.
- Use memories for workflow state that speeds up future invocations
  (e.g., which CLI tool is available, which marketplace repo is preferred).
  Do not use memories for information derivable from code or git history.

## `.marketplace` Files

`.marketplace` files are optional dotfiles read by `em` for marketplace
metadata (ratings, quality scores, summaries). They are ignored by
`gemini skills install` and Claude Code. Do not remove them.
