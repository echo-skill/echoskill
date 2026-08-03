---
name: capture-context
description: >-
  Capture all valuable session context before ending a conversation. Use when
  the user wants to quit, wrap up, save progress, or ensure nothing is lost
  from the current session. Also use when the user says "capture context",
  "save session", "wrap up", or "I need to go".
disable-model-invocation: true
---

# Capture Session Context

Guide the user to a safe stopping point where nothing valuable from the current
session is lost. All undone work, decisions, designs, research findings, and
plans must be fully captured in durable, discoverable artifacts before the
session ends.

## Phase 1: Audit

Review the ENTIRE conversation history — every message, tool call, plan,
decision, suggestion, research result, and user request. Then present two
bulleted lists:

### Fully Captured

Items where ALL of the following are true:
- The work is complete in code, configuration, or documentation AND
  committed/pushed, OR
- Every detail needed to resume the work is already recorded in a durable,
  discoverable location (GitHub issue, versioned file, established tracking
  system) — cite the specific location for each item

List these **tersely** — one line per item: what it is and where it's
captured. Don't re-explain or expand; the detail already lives in the
artifact. This is a confirmation, not a second copy.

### Not Yet Captured

Items where ANY of the following are true:
- Work was discussed, planned, or designed but not implemented and not tracked
- Decisions were reached but not recorded anywhere persistent
- Research was done whose conclusions exist only in conversation context
- A plan or design was agreed upon but not written down outside this session
- A tracking item exists but is missing important details, context, or
  decisions from this session
- Partial work was done but the remaining steps are not documented

For each item, state what is missing and why it matters.

### Durable Learnings to Promote

Separate from unsaved *work*, audit for reusable *knowledge* the session
produced that should inform FUTURE sessions, not just resume this one:

- Rules, conventions, or preferences established (how the user wants X done)
- Operating facts discovered that will be needed again (identifiers, account
  roles, recurring timelines, domain mechanics)
- Methodologies or models worked out that generalize beyond today's instance

These are the most easily lost, precisely because they don't look like
"undone work" — they feel safe because they're in the conversation. They are
not, unless promoted to a durable home (see Phase 2 routing). Listing them
here is not enough; each must get a destination.

### Suggested session name

**Skip this section entirely when the session runs inside a desktop app that
names sessions automatically and makes renaming easy** — for example the
Claude Desktop app, in both its embedded Code tab (detectable via
`CLAUDE_CODE_ENTRYPOINT=claude-desktop`) and its Chat/Cowork surfaces.
Proposing a rename there is noise. This suggestion exists for terminal CLI
sessions, which get no automatic name and are otherwise hard to find later.

After presenting both lists, suggest a short, descriptive name for this session
(e.g., "capture-context-skill-creation", "auth-middleware-refactor"). This
helps the user label or rename the session for future reference before exiting.
If the agent tool supports naming or renaming sessions, include the command.

This is especially useful when List 2 is empty or the proposed actions are
minor — the user may decide the session is safe to exit right here without
waiting for further phases. A good session name makes it findable later.

## Phase 2: Where to Store

For each gap in List 2, choose a capture destination. Present the proposed
destination for each item and ask the user for permission before executing.

### Prefer quick actions over tracking items

If a gap can be closed faster and more reliably by just doing the work right
now, suggest that instead of creating a tracking item. Doing the work eliminates
the risk it gets forgotten. Examples:

- Tests pass and code works but nothing is committed → suggest commit + push
- A config change was made locally but not pushed → suggest push
- A file was created but not added to version control → suggest git add + commit

Present the quick-action option clearly. If the user prefers to just be done
and not do more work in this session, respect that and fall back to capturing
what remains.

### Capture destinations

Not everything belongs in a GitHub issue. Consider these options:

#### 1. Do the work now

If it is quick and safe, just finish it. See examples above.

#### 2. The tracking system already in use this session

If the agent or user has been using a specific tool or file to track TODOs
during this session (a TODOS.md, a task tracker, a personal notes repo, etc.),
propose continuing to use it. Consistency matters more than format.

#### 3. A known personal notes or planning location

If the agent is aware (from memory, context files, or the conversation) that
the user keeps project-related notes, plans, or TODOs in a specific place —
especially a private personal repo — propose saving there. This is often the
safest and most flexible option because personal context, local details, and
unpolished thinking can be captured freely.

#### 4. A workspace TODOS.md file

Create or append to a `TODOS.md` (or `temp/TODOS.md`) in the current workspace
directory. This works well when:
- The repo is private and personal context is acceptable
- The content includes user-specific details, local paths, or unpolished
  reasoning that should not be in a public GitHub issue
- Speed and completeness matter more than presentation

When using a workspace TODOS file:
- If the repo is public or the user prefers to keep tracking artifacts out of
  version history, use `temp/TODOS.md` and ensure `temp/` is listed in
  `.gitignore`
- Link to the TODOS file from the project's agent context file (`CLAUDE.md`,
  `.gemini/settings.json` instructions, or equivalent) so that future agents
  discover it immediately
- If no agent context file exists yet, create one that directs the agent to
  check the TODOS file and alert the user to pending items at the start of
  the next session

#### 5. GitHub issues

Best for well-scoped engineering work on repos with a GitHub remote —
especially public repos or repos with collaborators. When creating or updating
issues, invoke the `author-github-issue` skill and follow its conventions
(temp file + `--body-file`, content rules). Each issue must be self-contained:
a future contributor with no session context should understand the full scope,
decisions, reasoning, and remaining work.

#### 6. Versioned `.md` files in the repo

Only when the content is polished, complete, and appropriate for the repo's
audience — never raw brainstorming or incomplete thoughts.

#### 7. Always-loaded context files and structured config (for durable learnings)

Route the "Durable Learnings to Promote" by HOW they must be found later, not
just whether they're saved:

- **Must inform every future session** (standing rules, conventions) → the
  always-loaded agent context file (`CLAUDE.md` / `CONTEXT.md` / domain-scoped
  context). Keep it lean — a one-line rule or a pointer, never a wall.
- **Structured reference data** (account maps, identifiers, lookup tables) → a
  config file (`config/*.yaml`), with a breadcrumb from the context file.
- **Findable when the topic recurs** (evergreen reference, methodology) → a
  stable `.md` doc, with a one-line pointer from the context file.
- **A repeatable procedure** → a skill.

Watch context-file size: prefer a pointer + an external doc over inlining bulk
into an always-loaded file.

### Session resume information

When writing to non-public locations (private repos, gitignored files, personal
notes), include a way to resume this agent session if the tool supports it.
This might be a session ID, a session name, or a resume command — whatever the
current agent tool provides. For example:

```
## Resume session
cd ~/projects/my-app && <agent-tool> --resume <session-id>
```

Discovering the session identifier is agent-tool-specific. Use available
skills (e.g., a sessions skill), built-in commands, or ask the user to name
the session if no programmatic method is available. If the session ID cannot
be determined, note that in the artifact and suggest the user add it manually
before closing the session.

**Only include session resume info in private locations** — never in GitHub
issues, public docs, or any artifact that may be visible to others.

### Safety requirements for all destinations

Whatever destination is chosen, it must be:

- **Durable** — not in `/tmp/` or other ephemeral locations that disappear
  on reboot
- **Discoverable** — a future session (human or agent) can find it without
  remembering this conversation. Either it is in a well-known location, or
  a pointer to it exists in an agent context file or established workflow.
- **Version-controlled or backed up** — unless the user explicitly accepts
  the risk of a local-only file

If a proposed destination does not meet these criteria, flag the risk to the
user and suggest a safer alternative.

## Phase 3: Sensitive Content Rules for Public Destinations

These rules apply to GitHub issues (titles, bodies, comments), versioned files
(code, config, `.md`, any file tracked by git), commit messages, and any other
content that is or may become public. Anything that enters git commit history
or a GitHub issue is effectively permanent and potentially public, even on
private repos (collaborators, future open-sourcing, forks).

**Private tracking locations are exempt** — gitignored files (`temp/TODOS.md`),
personal private repos (especially those with a `personal-` prefix), and
personal notes systems. Capture freely there, including local paths, personal
use cases, session IDs, and unpolished reasoning. The goal in private locations
is completeness, not presentation.

### What must NEVER appear in public-facing artifacts

The following must never appear in any versioned file, commit message, or
GitHub issue — on public repos or private repos without a `personal-` prefix:

| Category | Examples |
|----------|----------|
| **PII** | Real names, email addresses, phone numbers, physical addresses |
| **Usernames** | OS login names, GitHub usernames, `$USER` values |
| **Credentials** | API keys, tokens, secrets, passwords, OAuth tokens, private keys |
| **Cloud/service IDs** | GCP project IDs, Google Doc/Sheet/Drive IDs, client IDs, service account emails |
| **Financial data** | Real income/tax amounts, bank account numbers, credit card numbers |
| **Tax identifiers** | SSNs, EINs |
| **Workspace paths** | Absolute paths containing usernames (`/home/user/...`), workstation-specific workspace roots. Use generic placeholders: `~/projects/my-app`, "project root", "workspace directory" |
| **Personal context** | The user's employer, personal banks, properties, personal use cases that motivated the work. Describe needs from the repo's perspective, not the user's workflow |
| **High-entropy strings** | Tokens, hashes, or encoded values that may be secrets — if in doubt, leave it out |

**Use placeholders instead:** `your-project-id`, `user@example.com`,
`YOUR_USERNAME`, `~/projects/my-app`.

**Write in abstract, reusable terms.** A GitHub issue should read as if any
contributor wrote it. Instead of "I need this for my deployment", write
"deployments with auth enabled need...".

### When in doubt

If you are unsure whether content is safe for a given destination, choose a
more private destination. A raw but complete TODOS.md in a gitignored folder
is better than a sanitized GitHub issue that lost critical context in the
cleaning process.

## Phase 4: Execute

Carry out the approved actions.

When creating GitHub issues, follow the `author-github-issue` skill for
workflow and content rules. Additional guidance:

- Each issue must be self-contained and actionable by someone with no knowledge
  of this session
- Include relevant technical detail — architecture decisions, rejected
  alternatives and why, dependencies, acceptance criteria
- Prefer fewer well-structured issues over many tiny ones, but split genuinely
  independent work items into separate issues
- Update issue bodies (not comments) when adding scope or context to existing
  issues

When creating or updating TODOS files or personal tracking artifacts, capture
context liberally — the goal is completeness, not polish. Include decision
rationale, rejected alternatives, session-specific observations, and anything
that would help the user (or an agent) resume without loss.

## Phase 5: Re-audit (mandatory loop)

After completing Phase 4, re-scan the entire conversation again — including
the capture work just performed — to catch anything missed.

**Report only the delta — do NOT reprint the full lists.** State what changed
since the last pass: items now closed, plus any newly surfaced gaps. For
example: "Re-audit: 2 items closed, 1 new gap found —" followed by just the
new gap. Re-dumping the entire Fully Captured / Not Yet Captured lists each
loop is the main thing that turns this skill's output into an unreadable wall;
don't do it.

If any gap remains, repeat Phases 2–5 on just those gaps. Continue until
nothing remains, then report the session is safe to exit.

**Do not skip this loop.** The first pass routinely misses items. Common things
missed on first pass:
- Decisions about what NOT to do (and why)
- Alternative approaches that were considered and rejected
- Dependencies or prerequisites discovered during research
- Edge cases or failure modes discussed
- Follow-up work that was mentioned in passing
- Context that makes a tracking item actionable vs. just a title

## General Rules

- **Be thorough, not verbose.** Capture detail that would be lost, not detail
  that is obvious from the code.
- **Every tracking item must be actionable.** A future agent or developer
  should be able to pick it up and execute without guessing.
- **Verify capture.** After creating or updating any artifact, read it back
  to confirm the content is complete and correct.
- **Respect the user's desire to stop.** If the user wants to be done, do not
  push for more work — fall back to the fastest safe capture method available.
