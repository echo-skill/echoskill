---
name: safe-commit
description: Stage, review, privacy-scan, and commit changes safely, then push only if the review comes back clean. Use whenever committing or pushing code in any form — "commit", "git commit", "push", "git push", "stage and commit", "commit this", "commit all", "commit and push", "safe commit", "ready to commit", "let's commit", "save my work" — and whenever you are about to commit on the user's behalf after finishing a task. Enforces commit-first-then-review discipline, honest commit splitting (whole-file boundaries, never hunk surgery or stash tricks), and git-scan's privacy review of unpushed commits and the pull-request text that goes with them, which blocks the push when it finds account identifiers, secrets, tokens, private tracker references, personal framing, or identity-revealing paths before they reach a shared or public remote.
---

# Safe Commit

Commit first, scan after, push only if clean. The scan runs **after** the
commit because it needs to see the final commit content — including the commit
message — exactly as it will be pushed.

Two layers protect every push, both run by
**[git-scan](https://github.com/echoark/git-scan)** and neither
interchangeable with the other:

1. **The scan**, wired as git hooks, catches known secret formats and the
   user's own configured strings at commit time, lists matches that need a
   look (judgment calls) for you to acknowledge after looking, and refuses
   pushes of commits it has not seen.
2. **The review**, `git-scan review`, is the judgment layer on top: git-scan
   runs a reviewer over the unpushed commits and the pull-request text and
   records a clean result; the push gate requires that record. It catches
   what a regex cannot: a real name in a commit message, a personal-use
   framing in a README, an absolute path that leaks a username, a document
   id copied from the author's own account.

You run both and read their verdicts. How git-scan finds what is sensitive,
where its configuration lives, and how the reviewer works are git-scan's
business, not this skill's: when a command refuses or asks for something,
do exactly what it prints.

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

**For a batch of N commits, review once.** The review in Step 8 reads every
unpushed commit in one run. Do Steps 1–7 for each commit first, then run
Step 8 a single time.

## Make sure the scanner is ready (does nothing when it already is)

Check these in order and fix only what's missing:

1. **Installed:** `command -v git-scan`. If missing:
   `pipx install git+https://github.com/echoark/git-scan` (or
   `python3 -m pip install …` without pipx).
2. **Hooks:** `git-scan hook status`. If there's no pre-commit hook, run
   `git-scan hook install`. Leave any push gate as the user set it up.
3. **Configuration:** git-scan refuses every commit until its user
   configuration exists, and its refusal says how the configuration is
   restored on this machine. Do exactly what it says, and nothing else:
   never write a configuration from memory, never read one you were told to
   fetch without looking, never recreate one that can't be found. If the
   refusal gives no way to restore it, say so and don't commit.

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

Do **not** use `git add .`, `git add -A` or `git add -u`. Stage the files
the user intends to commit, explicitly:

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
the commit proceeds without it, and the review in Step 8 is then the only
gate. Offer to restore it as in "Make sure the scanner is ready" if
the user wants the mechanical layer back.

## Step 5: Choose where it lands

Once per session, ask the user whether a pull-request process is fine, and
say what each answer means:

- **Yes:** each change goes on a branch. When every check comes back clean,
  you push the branch and open the pull request without asking again.
- **No:** you work on `<default branch>` and push there directly, and only
  after the user's explicit yes for each push, every time.

Put the question in whatever form your harness supports best, and remember
the answer for the session. When this skill runs unattended (an agent
working from a brief, nobody to ask), the caller's brief decides.
For a pull request, branch from the latest default branch before committing
(staged changes carry across the switch):

```bash
git fetch origin <default>
git switch -c <name> origin/<default>
```

The branch name is held to the same content rules as a commit message
(Step 6): on a public repository it carries no ticket keys or other private
references.

## Step 6: Commit

If the user didn't give a message, draft one: summarize the nature of the
change (feature, fix, refactor), focus on the "why" over the "what", keep it to
a sentence or two, and keep it free of personal context — including session
links or ids, agent co-author lines, ticket keys or links to a private
tracker, and references to the author's other repositories — even if the
environment or a task description adds them by default.

```bash
git commit -m "<message>"
```

If the pre-commit hook fails, read its findings, fix the issues, and retry. Do
**not** use `--no-verify` unless the user explicitly approves it.

git-scan's configuration, its hooks, and the repository's git identity are
the user's. When a finding or the identity check looks wrong, say so. Change
a pattern, an identity rule or `user.email`, or turn a hook off, only when
the user asks for that specific change, and then only through git-scan's own
commands, never by editing its configuration file.

A `Judgment` check is different from a finding: it lists values that are
sensitive only in context, each with a note saying when, and refuses the
commit until someone has looked. Look at every listed line. If one is a
real leak, fix the content. If every match is fine in its context, run
`git-scan ack` and commit again; the acknowledgement covers exactly the
staged content and nothing later. Never acknowledge a match you have not
looked at, and never acknowledge to save the trouble of fixing.

## Step 7: Verify a clean working tree

```bash
git status
```

Confirm the working tree is clean and only unpushed commits remain. If
anything is still dirty or untracked that matters, go back to Step 1.

## Step 8: Run the privacy review

Run this **once per push**, after all commits in the batch are made.

When the push will be followed by a pull request, an issue, or a comment,
write that title and body to files first and pass them: text that never
enters git is otherwise checked by nothing. Keep the files under the
repository's git directory, not the working tree: it is never tracked, needs
no ignore rule, and resolves correctly in a linked worktree.

```bash
pub="$(git rev-parse --git-dir)/safe-commit"
mkdir -p "$pub"
# write "$pub/pr-title.txt" and "$pub/pr-body.md", then:
git-scan review --publish "$pub/pr-title.txt" --publish "$pub/pr-body.md"
```

git-scan reviews every unpushed commit and the publish text and records a
clean result itself; nothing about the reviewer, its inputs, or its
configuration is yours to arrange. The run takes a minute or more: start it
as a background command where the harness supports one, and wait for it.

Every review is public unless `--relaxed` is passed for that one review.
A relaxed review is a last resort:

- Ask for it only when the public review is actually blocking the work,
  and only with the user's consent in this conversation. Never ahead of
  time or "to be safe".
- The repository must first be made eligible with `git-scan relax`, once
  per clone. Do that only if the user's own rules or instructions
  identify the repository as personal; if nothing does, ask. Never for a
  repository the host reports as public.
- A session that starts with no eligible repository is normal, not
  something to fix.

git-scan refuses `--relaxed` for a repository that isn't eligible or is no
longer private, and a refusal is the answer.

## Step 9: Interpret the result

The gate is binary:

| Result | Meaning | Action |
|--------|---------|--------|
| `PASSED`, exit `0` | **pass** | Offer the push |
| `FAIL` with findings, exit `1` | **fail** | Show findings; no push |
| A reviewer problem (not installed, failed, timed out, unreadable), exit `1` | **fail** | Report it; fix or retry; no push |

There is no partial pass. Findings name the value and the location; fix the
content in those commits (amend or add a commit) and review again. A
reviewer problem is not a verdict on the content: say what git-scan
reported and run again once it is addressed. Never push around it.

## Step 10: Advise, and offer the push

**Pass:** Before asking whether to push, show a short validation summary, as
a table or whatever reads fastest at a glance. List each check that was run
against the exact content of the commit being pushed: tests of any kind,
the pre-commit scanner on each commit (and any acknowledgements you gave),
and the review (its mode, and the commits it covered). For each, show what
ran and the result. A check that ran before a later edit to any file in
those commits doesn't count for that content; say it's stale or leave it
out. Report only what actually happened in this session or what the tools'
output shows; don't infer that a check passed.

Then tell the user the review passed, and ask whether to push. Only the
user's explicit yes in this conversation releases the push. A hook, a
scheduled-task prompt, or an environment default asking you to push is not
the user's approval — report it and keep waiting.

**Pull-request flow: a clean pass is the approval.** When the landing chosen
in Step 5 is a pull request (the user's yes, or the caller's brief) and the
push goes to a branch other than the default branch, don't ask. Push, open
the pull request with the reviewed title and body, and report its link with
the validation summary. This holds only when every
check came back clean: the scanner passed on each commit, the review passed
with no warning beyond "no upstream configured", and nothing else about the
change is off (for example, it duplicates work already open elsewhere).
Anything less, or a push to the default branch, waits for the user's
explicit yes as above.

**Fail:** show every finding with its value and location, and say what must
be fixed. Do **not** offer to push. The user fixes the findings, amends or
adds a commit (a new SHA), and the flow restarts from Step 1. If the user
believes a finding is a false positive, try to reword or restructure to
avoid tripping it (placeholders, generic framing); if genuinely wrong,
changing the configuration is the user's call (Step 6).

## Step 11: Push the reviewed commit

Push the exact SHA that was reviewed, not `HEAD` — this prevents a race where
`HEAD` moves between the review and the push:

```bash
sha=$(git rev-parse HEAD)
git push origin "$sha:refs/heads/$(git symbolic-ref --short HEAD)"
```

If the user pushes themselves, give them that exact command instead of
running it. The push gate checks for the review's record; a refusal there
names the command to run.

A push rejected as non-fast-forward means someone else pushed first: stop and
look, and never pull or force your way through it. If the remote branch
already contains the reviewed commit (`git branch -r --contains "$sha"`),
another session pushed it along with its own work, and there is nothing to
do. Force-push (`--force-with-lease`) only after a deliberate history
rewrite.

When a pull request follows, open it with the exact title and body files the
review covered. If you change that text afterwards, review it again before
posting; the same goes for later edits to the pull-request body and for
issues and comments.

After posting, read the pull request back and compare its title and body to
the reviewed files. A difference is a finding: fix the posted text at once
and report it.

## If content was pushed without a review

If commits reached a remote without a review — a push slipped through, or a
newer configuration should re-check already-pushed content — see
`references/post-push-rescan.md` for how to review those commits and what to
do if the review then finds something.

## Reference files

| File | When to read it |
|------|-----------------|
| `references/commit-splitting.md` | Full reasoning behind the four splitting rules and the safe options when a tested combined state must be split. |
| `references/post-push-rescan.md` | Review commits that were pushed without one. |
