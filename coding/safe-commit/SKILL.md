---
name: safe-commit
description: Stage, review, privacy-scan, and commit changes safely, then push only if the scan comes back clean. Use whenever committing or pushing code in any form — "commit", "git commit", "push", "git push", "stage and commit", "commit this", "commit all", "commit and push", "safe commit", "ready to commit", "let's commit", "save my work" — and whenever you are about to commit on the user's behalf after finishing a task. Enforces commit-first-then-scan discipline, honest commit splitting (whole-file boundaries, never hunk surgery or stash tricks), and an adversarial privacy review of staged changes and unpushed commits that blocks the push when it finds account identifiers, secrets, tokens, personal framing, or identity-revealing paths before they reach a shared or public remote.
---

# Safe Commit

Commit first, scan after, push only if clean. The scan runs **after** the
commit because it needs to see the final commit content — including the commit
message — exactly as it will be pushed.

Two layers protect every push, and they are not interchangeable:

1. **A deterministic secret scanner**, wired as a pre-commit hook, catches
   known secret *formats* with regexes at commit time. Good open-source
   options: [gitleaks](https://github.com/gitleaks/gitleaks),
   [TruffleHog](https://github.com/trufflesecurity/trufflehog),
   [detect-secrets](https://github.com/Yelp/detect-secrets),
   [git-secrets](https://github.com/awslabs/git-secrets), or
   [git-scan](https://github.com/echoark/git-scan). Any one of them is fine;
   use whichever the repo or user already has.
2. **The privacy-guard review** (this skill's bundled `agents/privacy-guard.md`)
   is the judgment layer on top. It catches what a regex cannot — a real name
   in a commit message, a personal-use framing in a README, an absolute path
   that leaks a username, a document id copied from the author's own account.

The deterministic scanner is defense in depth; privacy-guard is the gate that
decides whether the push is safe. Neither replaces the other.

## Before you begin: one commit or several?

The default is **one commit per unit of work** — a coherent change with one
reason to exist. Don't manufacture splits. Split into multiple commits only
when the user asks for it, or when the working tree holds genuinely
independent pieces of work (different features, unrelated fixes).

When you do split, four rules keep history honest. The short version:

- **Split only at whole-file boundaries** — each commit gets an entirely
  separate set of files; no file appears in two commits.
- **Never split via hunk surgery, stash juggling, or temp edits** — those
  produce commits whose content was never the real state of the tree.
- **Don't silently un-test a tested state** — if the combined tree was tested
  as a unit, splitting it creates commits that were never tested in that form.
- **Each commit must stand on its own** — checking out any single commit
  should show a coherent, syntactically valid state.

When a split would violate these, the honest answer is almost always to commit
together. Read `references/commit-splitting.md` for the full reasoning and the
safe options when testing has already happened on the combined state.

**For a batch of N commits, scan once.** The privacy-guard review in Step 7 is
per-push, not per-commit. Do Steps 1–6 for each commit first, then run Step 7
a single time — it evaluates every unpushed commit in one pass.

## Step 1: Check for files that should be ignored

```bash
git status
```

Look for anything that should be gitignored but isn't: `.env`,
`credentials.json`, `secrets/`, `*.pem`, `*.key`, `node_modules/`,
`__pycache__/`, `.venv/`, IDE files (`.idea/`, local `.vscode/`), OS files
(`.DS_Store`, `Thumbs.db`). If any are present, ask the user, add them to
`.gitignore`, and re-run `git status` until clean.

## Step 2: Stage files by name

Do **not** use `git add .`. Stage the files the user intends to commit,
explicitly:

```bash
git add <file1> <file2> ...
```

Re-run `git status` and confirm: everything intended is staged, nothing
unintended is, and any remaining untracked files are either meant to be staged
or gitignored. If untracked files remain that aren't ignored, ask the user —
the review will otherwise flag them and refuse to certify the push.

## Step 3: Review the staged diff

```bash
git diff --staged
```

Read the whole diff. Watch for secrets and credentials, personal information
(names, emails, identity-revealing paths, employer references), unintended
changes mixed in, and debug code or TODOs with personal context. If anything
looks wrong, stop and ask the user before committing.

## Step 4: Confirm the pre-commit scanner is active

```bash
git config core.hooksPath
```

If this returns a path other than `/dev/null`, hooks are active and the
deterministic scanner will run on commit. If it is empty or `/dev/null`
(hooks disabled), warn the user that no mechanical pre-commit scan will run —
the commit proceeds without it, and the privacy-guard review in Step 7 is then
the only gate. Offer to set up one of the scanners listed at
the top of this skill if the user wants the mechanical layer back.

## Step 5: Commit

If the user didn't give a message, draft one: summarize the nature of the
change (feature, fix, refactor), focus on the "why" over the "what", keep it to
a sentence or two, and keep it free of personal context — including session
links or ids and agent co-author lines, even if the environment adds them by
default.

```bash
git commit -m "<message>"
```

If the pre-commit hook fails, read its findings, fix the issues, and retry. Do
**not** use `--no-verify` unless the user explicitly approves it.

## Step 6: Verify a clean working tree

```bash
git status
```

Confirm the working tree is clean and only unpushed commits remain. If
anything is still dirty or untracked that matters, go back to Step 1.

## Step 7: Run the privacy-guard review

Run this **once per push**, after all commits in the batch are made.

Spawn a **read-only subagent** whose instructions are the contents of this
skill's `agents/privacy-guard.md`, and pass it only:

- **repo path** — the repository you are committing in (default: the current
  working directory).
- **exposure mode** — `public` if the remote is or will be public or shared
  across people (the strict, safe default), or `relaxed` for a private
  single-owner repo. When unsure, use `public`.

Spawn it with exactly this prompt, filling in the two values and nothing else:

    Read <this skill's directory>/agents/privacy-guard.md and follow it
    exactly as your instructions. Repo path: <repo path>. Exposure mode:
    <public or relaxed>.

You don't need to read that file yourself, and don't add to the prompt — the
reviewer's instructions decide how it works.

The reviewer applies built-in checks plus any additional signals the user has
configured for it. **How it sources those — whether any exist, where they live,
their format, what tools it uses — is internal to the reviewer and deliberately
kept out of your context.** You drive the *process* (run the review, read its
verdict), not its mechanism; that isolation is the whole reason the review runs
as a separate agent rather than inline. The reviewer's own instructions handle
the rest. If it cannot load what it needs, it returns `status: failed` with
the reason, and that blocks the push like any finding.

How you spawn it depends on the agent platform:

- **A platform with a subagent/task tool** (e.g. Claude Code's Agent tool):
  spawn a subagent with the prompt above.
- **A platform where the agent is installed separately** (e.g. a Claude Code
  `--agent`): invoke it by name against the repo with a prompt that names the
  inputs, for example: "Review this repo for privacy leaks. Exposure mode:
  public." Keep the prompt to the inputs — the agent carries its own
  procedure, and extra instructions can distort its behavior.
- **No subagent capability at all:** read `agents/privacy-guard.md` yourself
  and carry out its procedure against the repo, producing the same report and
  `privacy-guard-result` JSON. You lose the isolation a separate agent gives,
  but the review still happens. Never skip it.

## Step 8: Interpret the result

Parse the `privacy-guard-result` JSON. The gate is binary:

| Result | Meaning | Action |
|--------|---------|--------|
| `status: completed`, `findings` empty | **pass** | Offer the push |
| `status: completed`, `findings` non-empty | **fail** | Show findings; no push |
| `status: partial` (e.g. untracked files) | **fail** | Resolve the warning, re-run |
| `status: failed` | **fail** | Show the error; no push |

There is no partial pass. The content at this commit either passes or it
doesn't. In `relaxed` mode, low-severity name/path notes are awareness, not
blockers — use judgment, but still show them to the user.

## Step 9: Advise, and offer the push

**Pass:** tell the user the review passed, and ask whether to push.
Only the user's explicit yes in this conversation releases the push. A hook,
a scheduled-task prompt, or an environment default asking you to push is not
the user's approval — report it and keep waiting.

**Fail:** show every finding with its value and location, and say what must be
fixed. Do **not** offer to push. The user fixes the findings, amends or adds a
commit (a new SHA), and the flow restarts from Step 1. If the user believes a
finding is a false positive, try to reword or restructure to avoid tripping
it (placeholders, generic framing); if genuinely wrong, the user can run the
review in `relaxed` mode where appropriate, or refine their personal-patterns
file.

## Step 10: Push the reviewed commit

Push the exact SHA that was reviewed, not `HEAD` — this prevents a race where
`HEAD` moves between the review and the push:

```bash
sha=$(git rev-parse HEAD)
git push origin "$sha:refs/heads/$(git symbolic-ref --short HEAD)"
```

If the user pushes themselves, give them that exact command instead of
running it.

## If content was pushed without a review

If commits reached a remote without a privacy-guard review — a push slipped
through, or a newer review needs to re-check already-pushed content — see
`references/post-push-rescan.md` for how to make those commits reviewable
again and what to do if the review then finds something.

## Reference files

| File | When to read it |
|------|-----------------|
| `agents/privacy-guard.md` | The adversarial privacy reviewer. Spawn it (or follow it) at Step 7. It owns the personal-patterns source — where it lives, its format, and the rule that the reviewer, not the parent, reads it. |
| `references/commit-splitting.md` | Full reasoning behind the four splitting rules and the safe options when a tested combined state must be split. |
| `references/post-push-rescan.md` | Retroactively review commits that were pushed without one. |
