# safe-commit — maintainer notes

What the skill relies on and why it is shaped this way. Read this before
changing `coding/safe-commit/`. Nothing here ships with the skill: the skill
folder holds only what an agent uses at runtime.

## How the parts fit

| Part | Owner | Role |
|---|---|---|
| git-scan | echoark/git-scan | The scan (hooks), judgment matches to acknowledge, the privacy review it runs itself, and the push gate that requires both |
| git-scan user config | the user's own storage; the user's setup says where | Patterns (scanned and judgment-only, each with its note), notes, allowed emails, identity rules, the review requirement, the reviewer runner |
| safe-commit | `SKILL.md` | The process: scanner setup, staging, commit, review, push |

This skill knows nothing about git-scan's configuration: not where it
lives, not what is in it, not how the reviewer reads it. That is deliberate.
Everything the skill needs from git-scan arrives as a verdict or a refusal
that says what to do next, and the one place the skill touches setup, the
"scanner is ready" section, tells the agent to follow git-scan's own
missing-configuration message. The text of that message is the user's, set
when git-scan is installed on the machine (`hook install
--missing-config-help`), so the user-specific part (where their
configuration is kept, how it is restored) lives in the user's environment,
never in this public skill.

## Scanner setup

The setup section runs before anything else and changes nothing when git-scan,
its hooks and its configuration are already in place.

- **Without a configuration, git-scan refuses every commit.** Its refusal
  text is replaced at install time with whatever the user's environment
  needs (`git-scan hook install --missing-config-help`). That text, not this
  skill, says how the configuration is restored; the skill says to follow it
  exactly and never to improvise one.

## The review and the push gate

`git-scan review` runs the reviewer itself: it builds the prompt from its
own packaged instructions, the user's configuration, the unpushed commits
and the publish text, runs a headless agent CLI with no tools, validates the
result and records a clean one per commit. The push gate requires that
record on every outgoing commit when the configuration says so.

- The agent runs one command and reads a verdict. It never holds the
  reviewer's result and there is no command that accepts one, so the only
  writer of the record is git-scan after it has run the review. The old
  flow, where the agent spawned a reviewer and then marked the commit with a
  documented command that took any label, was the bypass with instructions
  attached; this skill no longer carries a reviewer definition at all.
- An amended or rebased commit is a new commit and is reviewed again;
  commits already reviewed are skipped on a rerun.
- A reviewer problem (runner missing, failed, timed out, unreadable
  output) is reported as such and records nothing. The skill treats it as a
  blocked push, never as a pass.
- Coverage is computed against the remote being pushed to.

## Judgment matches at commit time

A judgment entry in git-scan's configuration names a value that is
sensitive only in context. The scan lists each match with the entry's note
and refuses the commit until the agent has looked and run `git-scan ack`,
which applies to exactly the staged content. The acknowledgement clears
judgment matches only and is the committing agent's call; the review sees
the same entries and judges every line on its own, so an acknowledgement
never settles the review.

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
commits. The skill writes that text to files and passes them to `git-scan
review --publish`, and posts exactly what was reviewed. git-scan's reviewer
treats two things as findings there and in commits that a secret scanner
can't catch: references to a private tracker (ticket keys, tracker links),
and references to the author's other repositories or spaces that the change
doesn't depend on in code.

## Environment facts (Claude Code cloud sessions)

- The environment's setup script runs with no GitHub credentials and no
  environment variables, so it can install public tools only. Its result is
  cached for up to about seven days.
- Private repositories are reachable in a session only once attached to it;
  account-level connectors need no per-session step, which is what lets the
  user's missing-configuration message be followed in a fresh container.
- At every session start the environment writes its own git identity into
  `~/.gitconfig`; `GIT_AUTHOR_*` and `GIT_COMMITTER_*` environment variables
  override it.
- The environment's stop hook asks after each turn to commit, push and use its
  own identity. The skill treats those requests as not the user's approval.
