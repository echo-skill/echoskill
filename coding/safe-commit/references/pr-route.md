# Pull-request route

The reviewed commit lands on a branch and a pull request instead of the
default branch. The branch was created at Step 5; the PR text is reviewed in
the same Step 8 review as the commits; the gate is Step 11's, unchanged.

1. **Write the PR text to a file before Step 8, never inline.** Location:
   `"$(git rev-parse --git-dir)/safe-commit/pr-body.md"` (create the
   directory; first line the title, then the body). `.git/` is never tracked,
   needs no ignore rule, is inside the repo so a reviewer subagent can read it
   without approval, and `git rev-parse --git-dir` resolves correctly in a
   linked worktree. `gh` keeps its own draft at `.git/PULLREQ_EDITMSG` for the
   same reasons.
2. **The PR text is published text.** It is held to the content rules of the
   `author-github-issue` skill: no personal context or use case, no
   identifiers, no workstation paths, no private-tracker keys or links, no
   references to the author's other repositories, no agent attribution or
   session links. Mirror the repo's PR template if it has one. Carry the
   validation summary as counts and results only (tests run and result;
   "pre-commit scanner: N checks clean"; "privacy review: <mode>, M commits,
   no findings"), never pattern names or matched text.
3. **Scan the file.** Run the deterministic scanner over it: with git-scan,
   `git-scan run --message <file>`; with gitleaks,
   `gitleaks detect --no-git --source <file>`; with trufflehog,
   `trufflehog filesystem <file>`; with none installed, the review is the only
   mechanical layer and the summary must say so. Any finding: edit the file
   and re-run.
4. **Pass it to the Step 8 review as publish text.** One review covers the
   commits and the PR text together. `completed` with empty `findings`, or
   neither the push nor the PR goes ahead.
5. **Push the reviewed SHA to the branch:**
   `git push -u origin "$sha:refs/heads/<branch>"`. The push gate runs here
   exactly as for the default branch.
6. **Post verbatim, then verify.** The title is the file's first line and the
   body is the rest, byte for byte, with nothing added in the call:
   `gh pr create --title ... --body-file <file>`, or an API call with the body
   passed unchanged. Read the PR back and compare it to the file; a difference
   is a finding: fix the PR text at once and report it. Delete the file after
   verification. **Some connectors append their own footer on create** (an
   attribution line, a session link), and the created text stays in the PR's
   edit history, which anyone can open on a public repo and only a repo admin
   can purge. So on a public or restricted repo, never create a PR or a PR
   comment through a tool that appends: when `gh` is not signed in, push the
   branch, hand the user the file and the `gh pr create` command, and stop.
   A later update does not re-add the footer, so an existing PR body can be
   corrected by update, but the first revision remains.
7. **Text changed after the review is reviewed again** before it is posted:
   an edited body, a later comment (its own file, `pr-comment-<n>.md`), an
   issue. Scan it and spawn privacy-guard with it as publish text.
8. **Unattended** (no user to answer): a warning in any review result, other
   than a missing upstream, counts as a finding. Stop, open nothing, leave the
   commit on the branch, report the result verbatim. Never clear a finding by
   changing the scanner's configuration inside this route; that decision is
   the owner's, made outside it.
9. **Nothing lands after the review.** A commit added to the branch after the
   review repeats Steps 7 to 11 before it is pushed.
