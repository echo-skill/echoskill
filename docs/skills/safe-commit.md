# safe-commit — maintainer notes

What the skill relies on and why it is shaped this way. Read this before
changing `coding/safe-commit/`. Nothing here ships with the skill: the skill
folder holds only what an agent uses at runtime.

## How the parts fit

| Part | Owner | Role |
|---|---|---|
| git-scan | echoark/git-scan | Pre-commit scan against the user's patterns; optional push gate that refuses commits lacking required marks |
| git-scan user config | the user's Google Drive | Patterns (scanned and judgment-only, each with its note), notes, allowed emails, identity rules, required marks |
| privacy-guard | `agents/privacy-guard.md` | Judgment review of unpushed commits and the pull-request text that goes with them, run as a subagent; reads its patterns and notes from git-scan's configuration (`git-scan patterns list --json`, git-scan 0.7 or later) |
| safe-commit | `SKILL.md` | The process: scanner setup, staging, commit, review, mark, push |

The Drive file carries `skill-data=safe-commit` and
`skill-data-role=git-scan-config`. Lookups use both properties, so they find
exactly one file.

## One catalog

The scanner and the reviewer read one list. git-scan's configuration holds
the regex entries the scanner compiles and, as judgment entries, the values
that would block ordinary commits as a regex but are sensitive in context
(a city, a given name that is also a word, the last four digits of an
account); each entry can carry a note, and a `notes` list holds guidance
that belongs to no entry. privacy-guard loads all of it with one command and
never sees a second file. A separate reviewer catalog would drift from the
scanner's list, and did; the one-list design is why an entry that trips
the scanner is moved to judgment (`git-scan patterns edit ID --judgment`)
rather than removed.

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

## Before the push

The validation summary lists only checks that ran against the exact content
being pushed, and marks earlier runs as stale. Only the user's explicit yes in
the conversation releases a push; hooks, scheduled prompts and environment
defaults that ask for a push are not approval.

The exception is a pull-request flow the user has set up: a push to a
non-default branch whose checks all came back clean goes ahead, and the pull
request opens, without a question. The user reviews at merge time, so asking
before the push adds a round trip without adding a check. Any finding,
warning beyond a missing upstream, or oddity about the change falls back to
asking.

## Text outside git

A pull-request body, issue, or comment never enters git, so the pre-commit
scanner and the commit review never see it, yet it is as public as the
commits. The skill writes that text to files and passes them to privacy-guard
as publish text, and posts exactly what was reviewed. The reviewer treats two
things as findings there and in commits that a secret scanner can't catch:
references to a private tracker (ticket keys, tracker links), and references
to the author's other repositories or spaces that the change doesn't depend
on in code.

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
