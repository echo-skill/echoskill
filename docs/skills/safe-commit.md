# safe-commit — maintainer notes

What the skill relies on and why it is shaped this way. Read this before
changing `coding/safe-commit/`. Nothing here ships with the skill: the skill
folder holds only what an agent uses at runtime.

## How the parts fit

| Part | Owner | Role |
|---|---|---|
| git-scan | echoark/git-scan | Pre-commit scan against the user's patterns; optional push gate that refuses commits lacking required marks |
| git-scan user config | the user's Google Drive | Patterns, allowed emails, identity rules, required marks |
| privacy-guard | `agents/privacy-guard.md` | Judgment review of unpushed commits, run as a subagent |
| privacy-guard catalog | the user's Google Drive | The reviewer's personal patterns |
| safe-commit | `SKILL.md` | The process: scanner setup, staging, commit, review, mark, push |

Both Drive files carry `skill-data=safe-commit`, and each carries a
`skill-data-role` (`git-scan-config`, `privacy-guard-catalog`). Lookups use
both properties, so each finds exactly one file.

## Scanner setup

The setup section runs before anything else and changes nothing when git-scan,
its hook and its config are already in place.

- **The config comes from Drive.** It is the user's own data, reachable from
  every surface the skill runs on (a workstation, a cloud session) through the
  account's Drive connector, with no repository to attach and no credential to
  manage.
- **On a machine with a local Drive sync folder,** the config path is a symlink
  to the synced copy, confirmed by the sync client's file id. git-scan writes
  its config in place, so edits made with its CLI go through the link to Drive,
  and Drive keeps the file's revision history.
- **Elsewhere, a subagent downloads it.** The config is a catalog of the user's
  personal identifiers, so it stays out of the parent agent's context: the
  subagent reports back only the path, the size and the pattern count.
- **Without a config, git-scan refuses every commit.** Its refusal text can be
  replaced at install time (`git-scan hook install --missing-config-help`).
  Setting it to point at this skill is what brings an agent here when it tries
  a plain `git commit` first.

## The push gate and the review mark

git-scan's push gate refuses any outgoing commit that lacks its own `scanned`
mark or a mark the user requires. This skill adds `privacy-review` after a
clean review (`git-scan mark privacy-review`), so the gate refuses pushes that
skipped the review.

- One mark on the newest commit covers every unpushed commit in the review,
  matching how privacy-guard reviews the whole unpushed range.
- An amended or rebased commit is a new commit and needs a new review.
- The mark records that the review step ran, not how well; the gate catches a
  forgotten review.
- Coverage is computed against the remote being pushed to. A repository with
  several remotes can push commits that were reviewed relative to a different
  one.

## Exposure mode

`relaxed` needs two confirmations: the hosting service reports the repository
as private, and the repository is one the owner reserves for personal material
(by a naming convention the owner has stated, or by asking). Anything else is
`public`. Privacy alone is not enough because private repositories are often
shared or published later.

## Landing routes and PR text

The skill asks where the commit lands (direct to the default branch, or a
branch and a pull request) before the commit, not after.

- **The branch name is scanned at commit time.** git-scan's pre-commit pass
  checks branch names along with the content; a branch created after the
  commit would skip that check.
- **No pointer moves.** Committing on the right branch from the start means
  no later `git branch -f` or reset to relocate a reviewed SHA, and the mark
  on that SHA is the one the push gate sees.
- **Follow-ups have a home.** A fix after review goes on the same branch and
  into the same PR, instead of landing on the default branch by accident.

PR text is scanned and reviewed because, until this route existed, it was the
one thing that reached the remote through no check at all: commit messages go
through the commit-msg hook and privacy-guard, branch names through the
pre-commit pass, but a PR title, body or comment posted straight from the
agent's context was unscanned. A PR body is as permanent as the commits it
merges, its edit history stays visible on a public repository, and the
original text has already gone out by notification email before any edit. So
the text is written to a file, scanned by the deterministic scanner
(`git-scan run --message <file>`), reviewed by privacy-guard as an artifact
file, posted verbatim, and read back.

The file lives under `.git/` (`"$(git rev-parse --git-dir)/safe-commit/`)
because that directory is never tracked and needs no ignore rule, is inside
the repository so a reviewer subagent can read it without a path approval, and
resolves correctly in a linked worktree. `gh` keeps its own draft at
`.git/PULLREQ_EDITMSG` for the same reasons. The file is deleted once the
posted text has been read back and compared.

- **Connector footers.** Some agent connectors append an attribution line
  with a session link when they create a PR, an issue, or a comment, and
  GitHub keeps the created text in the item's edit history. The route
  therefore allows only tools that post the file as-is (`gh ... --body-file`)
  on a public or restricted repo, and otherwise hands the user the file and
  the command. Observed before the rule existed; a body corrected by update
  still carries the first revision until a repo admin deletes it.
- **Delegated agents.** A subagent usually cannot spawn agents, so it must not
  take the in-process fallback and read the catalog itself; it stops after
  the commit and the caller runs the review. That is what makes a delegated
  run a two-phase handoff.

## Before the push

The validation summary lists only checks that ran against the exact content
being pushed, and marks earlier runs as stale. Only the user's explicit yes in
the conversation releases a push; hooks, scheduled prompts and environment
defaults that ask for a push are not approval.

## Environment facts (Claude Code cloud sessions)

- The environment's setup script runs with no GitHub credentials and no
  environment variables, so it can install public tools only. Its result is
  cached for up to about seven days.
- Private repositories are reachable in a session only once attached to it;
  Drive connectors are account-level and need no per-session step.
- At every session start the environment writes its own git identity into
  `~/.gitconfig`; `GIT_AUTHOR_*` and `GIT_COMMITTER_*` environment variables
  override it.
- The environment's stop hook asks after each turn to commit, push and use its
  own identity. The skill treats those requests as not the user's approval.
