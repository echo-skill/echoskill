---
name: author-github-issue
description: >-
  Use when creating (gh issue create), editing (gh issue edit), or
  commenting on (gh issue comment) a GitHub issue, or when writing a pull
  request's title or body or commenting on a pull request — whether the user
  asks directly or the agent decides one should be filed for a bug,
  feature, design decision, or any other trackable item.
---

# Authoring GitHub Issues and Pull-Request Text

## Workflow: File-Based Creation and Editing

Always write the text to a file and post it with `--body-file` (or pass the
file's content unchanged to the GitHub API or tool). Never pass the body
inline via `--body` or heredocs. This ensures:

- The user sees the full content via the file-editing tool before it ships.
- Edits are visible as diffs, not opaque string replacements.
- No content is lost to shell escaping or truncation.

The same workflow covers issues, issue comments, pull-request titles and
bodies, and pull-request comments.

Keep the draft under the repository's git directory:
`"$(git rev-parse --git-dir)/safe-commit/"` (for example `issue-<slug>.md`,
`pr-title.txt`, `pr-body.md`, `pr-comment-<n>.md`). It is never tracked,
needs no ignore rule, and resolves correctly in a linked worktree. Outside a
repository, use a temp directory.

### Before Posting: Scan, Review, Post Verbatim, Read Back

1. **Scan the file** with a deterministic secret scanner: with git-scan,
   `git-scan run --message <file>`; with gitleaks,
   `gitleaks detect --no-git --source <file>`; with trufflehog,
   `trufflehog filesystem <file>`. Any finding: edit the file and scan again.
2. **Review it** where a review applies: when the text goes with a push
   reviewed by git-scan (the `safe-commit` skill), pass it to that review
   with `git-scan review --publish <file>`. `git-scan review` currently
   cannot review publish text on its own, without unpushed commits to review
   alongside it; until it can, text posted on its own gets the scan and the
   content rules below.
3. **Post verbatim:** the reviewed file, byte for byte, with nothing added
   in the call.
4. **Read it back** after posting and compare it to the file. A difference
   is a finding: fix the posted text at once and report it.

### Creating a New Issue

1. Write the issue body to the draft file:
   ```
   Write tool → "$(git rev-parse --git-dir)/safe-commit/issue-<slug>.md"
   ```
2. Let the user review/approve the file content, then scan it as above.
3. Create the issue:
   ```bash
   gh issue create --repo <owner>/<repo> --title "<title>" --body-file "$(git rev-parse --git-dir)/safe-commit/issue-<slug>.md"
   ```

### Updating an Existing Issue

1. Fetch the current body to a file:
   ```bash
   gh issue view <number> --repo <owner>/<repo> --json body --jq '.body' > "$(git rev-parse --git-dir)/safe-commit/issue-<number>.md"
   ```
2. Edit the file using the file-editing tool (Edit on Claude Code,
   `edit_file` on Gemini CLI). This shows the user a diff of what changed
   rather than replacing the entire issue body opaquely.
3. Scan it as above, then update the issue from the file:
   ```bash
   gh issue edit <number> --repo <owner>/<repo> --body-file "$(git rev-parse --git-dir)/safe-commit/issue-<number>.md"
   ```

### Pull Requests

Write the title and body to `pr-title.txt` and `pr-body.md` in the draft
directory before the push, so the push's review can cover them; post them
with `gh pr create --title "$(cat <title file>)" --body-file <body file>` (or
`gh pr edit`, `gh pr comment --body-file`), and read the pull request back.

### Why This Matters

- **Transparency**: The user sees exactly what will be published before it ships.
- **Diff visibility**: File edits show before/after in the agent's native tool
  approval UI, so the user can review deltas naturally.
- **No data loss**: Large issue bodies don't get truncated by shell quoting,
  heredoc limits, or argument length limits.
- **Auditability**: The draft file persists for the session if the user wants
  to review what was sent.

## Content Rules for GitHub Issues and Pull Requests

**Treat every issue, pull-request title, body and comment as a public-facing
artifact.** A pull-request body is as permanent as the commits it merges,
and its edit history stays visible. Even on private repos,
issues may become public (collaborators, open-sourcing, forks). Write from
the perspective of someone contributing to a reusable product, not from the
perspective of the current user's personal workflow.

### Never Include User-Specific Information

- PII: names, emails, usernames, employer names, phone numbers
- User workstation-specific paths (home directories, workspace roots,
  local directory layouts) or configurations
- Cloud/service identifiers: GCP project IDs, API keys, document IDs,
  account IDs
- Examples drawn from the user's local data, use cases, or environment
- Anything that reveals the author's identity as a user of the repo
- Keys or links from a private tracker (an issue key, a board URL). The
  tracker links to the public artifact, never the reverse.
- References to the user's other projects, repos, or GitHub repositories —
  unless the repo this issue belongs to directly imports or depends on that
  other project (e.g., it's declared as a dependency in package config).
  A personal project that *uses* this repo is not a valid reference;
  only direct code-level bindings between repos justify cross-references.

### Instead

- Use generic placeholders: `~/projects/my-app`, `your-project-id`,
  `user@example.com`
- Describe needs from the repo's perspective, not the user's workflow
- Write issue titles and bodies that would make sense to any contributor
- Focus on how the change benefits the product broadly

### Issue Body Structure

- **Lead with the problem.** What's broken, missing, or awkward?
- **Propose a solution.** Be specific about the desired behavior.
- **Include full session context** per the preservation rules below.
- **Add a work breakdown** with checkboxes for implementation steps,
  including explicit items that persist all context into repo files.
- **Update the body as scope evolves** — don't add comments for scope
  changes. The body should always reflect the current understanding.
  Comments are for discussion, not revisions to the spec.

### Session Context Preservation

**The issue should be a lossless bridge between the ephemeral session
and the permanent repo.**

An agent session is disposable — it will end, its context will vanish,
and a future session picking up the issue will start from zero. The
issue must therefore capture the full picture so nothing is lost and
no work must be repeated.

#### Layer 1: Capture everything into the issue

When creating or updating an issue, distill 100% of the session's
relevant context, detail, and nuance into the issue body. This is
not a summary — it is the authoritative record. Include:

- **Reasoning and decisions**: Why this approach? What alternatives
  were considered and why were they rejected?
- **Constraints and edge cases**: What limits the solution space?
  What non-obvious cases were identified?
- **Design principles and rationale**: Architectural decisions,
  conventions established, or guidelines that should govern the
  implementation and future work.
- **Discovery work**: Any testing, experimentation, commands run,
  what worked, what didn't, retries, and deviations from the
  originally assumed approach or the approach one might default to.
  This is the most at-risk knowledge — hard-won findings that, if
  lost, force someone to repeat the same trial-and-error or, worse,
  lead to a blocker or inferior solution because the discovery never
  happened again.
- **Working solutions**: Exact commands, configurations, code
  patterns, or workarounds that were proven to work during the
  session. Include enough detail that a future session can
  reproduce them without guesswork.

#### Layer 2: Prescribe persistence into the repo

The issue's work breakdown must include tasks that ensure every
piece of captured context ends up committed to the repo as code,
tests, documentation, or context files. The goal: **closing the
issue means the repo itself is self-sufficient.**

Not all knowledge belongs in the same place. Route captured context
to the right destination based on when and how it needs to be found:

- **Code, comments, and docstrings** — Implementation-specific
  discoveries: how we got a library to do X, workarounds for Y,
  the non-obvious approach that finally worked. This knowledge is
  best captured at the point of use — in the code itself — where
  it will be found naturally when someone revisits that module,
  function, or block. It does not need to live in context files
  or be kept in mind broadly; it just needs to be there when the
  relevant code is read.
- **Tests** — Not just regression guards. Tests are executable
  documentation. Use them to capture edge cases, failure modes,
  proven capabilities, and behavioral boundaries discovered during
  the session. This is especially valuable when documentation for
  a product or feature was unclear and the session involved
  exploration to prove how something actually works. A test that
  demonstrates a capability or boundary is more credible than a
  code snippet in docs alone — it's packaged for quick, repeatable
  self-verification through a standard runner like pytest. When a
  repo already has a test suite used for proof-of-concept capture,
  extend that suite. When no direct implementation exists yet in
  any repo that would exercise the discovered behavior, a test
  may be the right place to capture it until one does.
- **Context files** (`CONTRIBUTING.md`, `README.md`, or their
  equivalents) — Ongoing design principles, architectural
  decisions, implementation strategies, and conventions that any
  contributor or agent must continuously be mindful of and follow.
  These files are loaded as agent context at session start (via
  `CLAUDE.md` `@` imports and `.gemini/settings.json` context
  declarations — see the `setup-agent-context` skill), so
  principles documented there automatically inform every future
  session. Reserve context files for knowledge that must be
  actively kept in mind, not just findable when needed.

The work breakdown should include explicit items like:
- `[ ] Implement [feature/fix] with [approach determined above]`
- `[ ] Add tests covering [edge cases identified above]`
- `[ ] Capture [discovery/workaround] in code comments or docstrings
  at the point of use`
- `[ ] Document [principle/convention] in CONTRIBUTING.md`
- `[ ] Update README.md if [decision] affects user-facing behavior`

Content captured only in an issue body is invisible to agents and
contributors unless someone happens to go back and read a closed
issue. Every piece of knowledge must land in a versioned file —
the distinction is which file, based on whether it needs to be
continuously kept in mind or found when the relevant code is read.

#### Two-layer safety net

These layers create redundant protection against knowledge loss:

1. **Session dies** → nothing lost, because it's all in the issue.
2. **Issue is forgotten, deleted, or never revisited** → nothing
   lost, because the prescribed tasks, when carried out in full,
   ensure all the same detail winds up in code, tests, and
   documentation as commits to the repo itself.
