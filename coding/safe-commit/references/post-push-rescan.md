# Reviewing content that was already pushed

Sometimes commits reach a remote without a privacy-guard review — a push
slipped through in an environment with no review wired up, a push happened
outside this workflow, or a newer version of the review needs to re-check
content that was pushed earlier. This is how to make already-pushed commits
reviewable again, because the review only looks at **unpushed** commits
(`git log @{upstream}..HEAD`).

The idea: create a temporary branch at the pre-push baseline, push it to
establish a remote tracking point, then merge the real branch in. Relative to
the temporary branch's upstream, the already-pushed commits now appear as
"unpushed" and fall within the review's scope.

## Setup

```bash
# 1. Identify the last commit that was on the remote BEFORE the unreviewed push.
git log --oneline -20

# 2. Create a baseline branch at that commit and push it to set an upstream.
git checkout -b rescan-basis <baseline-sha>
git push -u origin rescan-basis

# 3. Merge your real branch in. The pushed commits are now "ahead" of
#    rescan-basis's upstream, so the review will see them.
git merge <your-branch>
```

## Run the review

Run the privacy-guard review (skill Step 8) against this repo while
`rescan-basis` is checked out. Keep the exposure mode matched to the remote
the content was pushed to — `public` for a public or shared remote. The review
reads the commits that are now ahead of `rescan-basis`'s upstream.

## Interpret and clean up

**If the review passes**, the scaffolding has done its job — remove it:

```bash
git checkout <your-branch>
git branch -D rescan-basis
git push origin --delete rescan-basis
```

**If the review finds something**, the content is already on the remote, so
fixing it locally is not enough on its own:

1. Fix the findings in a new commit on your real branch and push it, so the
   current tip is clean.
2. Recognize that the sensitive content still exists in the remote's
   **history**. Depending on severity, that may call for rotating any exposed
   credential immediately (treat a pushed secret as compromised), and for
   history rewriting or repository remediation that is beyond this skill's
   scope — surface it to the user rather than attempting it silently.

The `rescan-basis` branch can be deleted either way — it was only scaffolding
to bring the already-pushed commits back into the review's view.
