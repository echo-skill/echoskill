---
name: inbox-triage
description: |
  Use when triaging, archiving, processing, cleaning up, or clearing
  out a Gmail inbox — and when unsubscribing from marketing senders
  found while doing so. Walks the live inbox via Google Workspace MCP
  tools, classifies each email against the user's triage rules
  (archive vs review vs track-as-task), and waits for explicit
  approval before changing anything. Never archives without
  confirmation. Also flags marketing senders worth unsubscribing from
  and presents them as a batch; executing the unsubscribe is delegated
  to a separate optional inbox-unsubscribe skill if installed.
  Self-locating: resolves where the user's rules and optional
  cross-cutting context live at runtime, asks once, remembers, and
  degrades gracefully when that data is absent. Verbs: triage,
  archive, process, clean, clear, sort, organize, sweep, review, scan,
  label, unsubscribe, opt out, opt-out, mute. Targets: inbox, email,
  emails, mailbox, gmail, mail, marketing, promo, newsletter, mailing
  list.
---

# inbox-triage

Walk the live Gmail inbox(es) and propose an archive / review /
track-as-task plan against the user's triage rules. The user approves
each batch before any change is applied. While triaging, also flag
marketing senders worth unsubscribing from and present them as a
batch; actually *executing* the unsubscribe is delegated to a separate
optional `inbox-unsubscribe` skill (see Step 3b). This skill works
fine without it — it just surfaces the candidates for you.

This skill is human-in-the-loop and never archives without explicit
approval on the batch.

## Prerequisites (MCP connectors)

This skill needs external connectors. They are environment, not part
of the bundle — confirm they are connected before relying on them.

| Connector | Required? | Used for |
|---|---|---|
| Google Workspace (Gmail) | **Required** | Reading the inbox, archiving (removing the `INBOX` label), reading individual emails. Without it the skill cannot run. |
| Google Drive (`drive_search`, `drive_list_folder`, `drive_update`, `drive_set_properties`) | **Required unless the data root is local** | Locating and read/writing the data root — see "Locating your data". This is what makes the skill work on mobile and web, where there is no filesystem. If Drive is unavailable, the skill can still run against a local data root on a shell surface. |
| A task manager MCP with `create_task` / `update_task` | Optional | The `track-as-task` outcome. If absent, surface the item to the user as "make a task" instead of creating one. |
| A banking/finance MCP with `list_accounts` / `list_transactions` | Optional | The Financial-sweep safety checks (verify a balance is positive / autopay ran before archiving an alert). If absent, treat those alerts conservatively as `review` rather than auto-archiving. |

Tool names vary by how the connector is registered in the session
(the same Gmail connector may surface as `search_emails`,
`remove_email_label`, `read_email`, etc. under different server
prefixes). Use whatever Gmail / task / finance tools the session
exposes; do not hardcode a specific server prefix, and do NOT use any
deprecated deployed triage tools.

## Locating your data (run this FIRST, before anything else)

This skill carries no personal data. Your triage rules and history
live OUTSIDE the skill, in a **data root**. A separate, optional
**project root** holds cross-cutting personal context the skill reads
only when an email calls for it.

### Data root — `$INBOX_DATA`

Holds the files the skill reads and writes every run:

| File | Role |
|---|---|
| `rules.md` | The triage ruleset, organized by category. **Authoritative for what to do.** |
| `lists.yaml` | Mailing-list senders to auto-archive when the user is not on To/Cc and not named in the body. |
| `contacts.yaml` | Known senders with explicit handling overrides. |
| `decisions.md` | Dated rulings: the call, the user's own words, the why, and a pointer to where it's codified. **Never restate full policy text here** (that lives in `rules.md`) and **never put session records here** (those go in the log). |
| `email-triage-log.md` | Chronological session log, **newest entries at the top**. PREPEND an entry after each run. Create if missing. |
| `gmail-filters.md` | Docs for the static Gmail filters + their backup/rollback procedure. Optional. |
| `gmail-filters-[account].xml` | Importable `mailFilters.xml` backup, one per Gmail account. Optional. |

Each file has exactly one job. If you find yourself writing the same
thing into two files, stop — pick the one that owns it.

**Do NOT refactor the user's `rules.md`.** It will mix reusable triage
doctrine with hyper-specific personal detail — their vendors, their
household, their accounts, named people — and that is fine. It is theirs.
Splitting it into a "generic" half and a "personal" half is a tempting,
plausible-sounding idea that the user has already considered and
rejected: the two are interleaved at the sentence level, the split buys
them nothing, and the churn risks losing rules. Add to it, refine it,
reorganize a section when asked — but do not propose carving it up.

#### THE DATA ROOT IS A GOOGLE DRIVE FOLDER — prefer it over any local path

The data root must be reachable from **every** surface the user might
run this skill from: desktop, web, and mobile. A filesystem path is not
— a phone has no shell, no clone, and no `$HOME`. Google Drive is keyed
to the user's Google identity, which is the same identity the Gmail
connector already authenticates as, so it follows the user everywhere.

Resolve `$INBOX_DATA` in this order, stopping at the first that works:

1. **Google Drive, discovered by property (PREFERRED — try this first,
   on every surface).** Search Drive for the folder tagged with the
   single custom property `echoskill-data = inbox-triage`:

   ```
   drive_search: properties has { key='echoskill-data' and value='inbox-triage' }
                 and mimeType = 'application/vnd.google-apps.folder'
                 and trashed = false
   ```

   Take the folder id, `drive_list_folder` it, and read the files above
   by their predictable names. Nothing is hardcoded — not the folder's
   name, not its path, not a file id — so the user may rename or move
   the folder anywhere in Drive and discovery still resolves.

   **WRITING BACK — read this before you save anything.** Update the
   EXISTING file in place, by its file id (`drive_update`). Revisions
   stack on that id, and that revision history IS the version store —
   it is what replaces git for these files.

   **NEVER delete-and-recreate a file to "update" it.** Creating a new
   file with the same name produces a NEW file id with ONE revision, and
   silently discards every prior version (the old file lands in Trash and
   is gone in ~30 days). Do this a few times and the version store the
   whole design rests on quietly does not exist. If the only create tool
   available is more convenient than the update tool, that is not a
   reason — use the update tool.

   Pin milestones with `keep_revision_forever`. Snapshot BEFORE a risky
   change as well as after, so there is a clean pre-change revision to
   roll back to (`drive_list_revisions` / `drive_get_revision`).

   **Known tooling gap — do not paper over it.** Some Drive MCPs expose
   an update tool that accepts ONLY base64, while the create tool accepts
   plain text. An agent cannot practically base64 a large text file (it
   would have to round-trip the whole thing through its own context), so
   the path of least resistance becomes create+delete — which is exactly
   what destroys the history. Some sandboxes also block Drive's
   resumable-upload URL, forcing bytes inline and making large writes
   expensive.

   If in-place update is genuinely unavailable for a large file: **say so
   to the user before writing**, and treat the lost history as a real
   cost, not a footnote. Do not silently trade the version store for
   convenience. The durable fix is an update tool that accepts plain text
   (worth filing against the Drive MCP).

2. The `INBOX_TRIAGE_HOME` environment variable, if set (local override,
   shell surfaces only).
3. A pointer file at `${XDG_CONFIG_HOME:-$HOME/.config}/inbox-triage/config.yaml`
   with a `data_dir:` key. Read it and use that path.
4. **In-repo auto-detect:** if the current working directory (or an
   ancestor) contains `inbox/rules.md`, use that `inbox/` directory.
5. **Ask the user:** "Where do your inbox-triage rules live?" Offer:
   (a) point me at an existing Drive folder — then **tag it** with
   `echoskill-data = inbox-triage` (`drive_set_properties`) so this is
   never asked again; (b) point me at a local folder; or (c) let me
   scaffold a fresh data root.
   - If scaffolding, **create the Drive folder and tag it**, seed it
     from this skill's `defaults/`, and tell the user plainly: "I
     created a fresh, generic ruleset. Your real tuned rules from
     another machine are NOT here — restore or sync them if you have
     them."

**If rungs 2–4 resolve but rung 1 did not, say so.** A local-only data
root means the user's rules do not exist on their phone. Offer to
promote it to Drive and tag it.

Never silently invent rules. If you cannot resolve `$INBOX_DATA` and
the user declines to scaffold, stop and explain — do not triage
against guessed rules. **Never scaffold generic defaults over the top
of a data root you merely failed to find** — an empty ruleset that
looks like a working one is worse than stopping.

#### Why one property on the folder, not tags on each file

Drive's query language has no "key exists" operator — `properties has`
requires both key and value — so one property whose value is constant
across everything the skill owns is what makes a single "find all my
stuff" query possible. Per-file tags for role/format/account are
redundant: role duplicates the filename, format is documentation not a
selector, and account is not an axis at all (the Drive owner *is* the
account). Tag the container once; name the files predictably.

The key is `echoskill-data`, not a vendor-specific name — this is plain
markdown any agent could execute, and `echoskill` is a namespace the
user controls. Other skills reuse the same key with a different value.

### Project root — `$PROJECT_ROOT` (optional, cross-cutting)

Some emails need richer personal context that does NOT belong to this
skill and is owned by the user's broader personal project:

| Context file (relative to `$PROJECT_ROOT`) | Read it when |
|---|---|
| A properties / listings config | An email looks like a short-term-rental OTA notification (e.g. Airbnb/Vrbo) or a property bill — to identify which property by listing title / property ID. |
| A subscriptions config | An App Store / Play Store / recurring subscription charge — to decide expected vs unexpected. |
| A people / household context file | An email concerns a specific person (e.g. a school email about a family member) — to confirm who it concerns. |

Resolve `$PROJECT_ROOT` like the data root: `INBOX_TRIAGE_PROJECT` env
var → `project_dir:` in the same pointer file → the repo root when
auto-detected in step 3 → otherwise ask ONCE when a candidate email
first needs it, and persist the answer.

**Graceful degradation is mandatory.** If `$PROJECT_ROOT` is unset or
a file is missing, do NOT block and do NOT guess. Surface the email
as `review` with a one-line note ("short-term-rental email — no
properties config available to identify the property") and move on. The cross-cutting
files are enrichment, never a hard dependency. Do not preload them;
read a file only when a candidate email's metadata points to it.

## Inputs

- **Profiles to process.** Default: every Gmail account the Workspace
  connector reports. Scope can be narrowed by the user ("just the
  rental account", "primary only").
- **Optional batch size or filter** — e.g., "just the marketing
  ones," "last 50 emails," "everything from this week."

## Workflow

### 1. Locate data, then load context

Resolve `$INBOX_DATA` (above). Read `$INBOX_DATA/rules.md`,
`$INBOX_DATA/lists.yaml`, `$INBOX_DATA/contacts.yaml`. Do not read
cross-cutting `$PROJECT_ROOT` files yet.

### 2. Fetch inbox(es)

Confirm which accounts are configured. For each profile in scope,
search with `query="in:inbox"`, `format="metadata"`,
`max_results=100`. If the result estimate exceeds 100, page via the
next-page token — but cap at 200 emails per profile per session
unless the user asked to clear everything.

### 2b. Label-driven mass-archive sweeps (run BEFORE classification)

Before classifying the raw inbox, run sweeps against pre-applied user
labels. The user has Gmail filters (or manual tagging) that already
classified some emails — let that work pay off instead of
re-classifying from scratch every session.

| Query | Action | Notes |
|---|---|---|
| `label:Archivable label:inbox` | **Bulk archive ALL, no per-email review.** Single batch confirmation, then archive. | User pre-tagged these; trust the tag. Surface only the count ("archiving 161 Archivable+inbox — proceed?"). |
| `label:Financial label:inbox` | **Scan for standouts, archive the rest.** | Standout = failed payment, declined transaction, negative balance, past-due / late fee, budget cap reached, anomalous large charge, anything matching the universal safety net in `rules.md`. Present standouts; archive the rest in one batch. |

For the **Financial sweep**, do NOT rely on subject keywords alone —
verify the underlying account state when a finance MCP is available
(if not, treat as `review`):

- "balance went negative" / "Overdrafts happen" → check the finance
  MCP for the named account's current balance. Positive everywhere →
  archive as historical noise. Still negative → surface as task.
- "Minimum Payment due" / "Payment due date approaching" → check for a
  recent autopay/EFT payment on the card. Autopay running → archive
  the alert. No recent payment → surface as task.
- "We declined your transaction" → if balance is now positive and the
  decline is historical, archive; if recent and still failing, surface.
- Budget alerts < 100% → archive. At 100% → surface (may be intended
  ramp or a runaway to investigate).

**Add additional label-driven sweeps here** as new buckets emerge
(candidates: `Bills`, `Rentals`, `Schools`, `Subscriptions`).

#### Future-proofing: Gmail filter API

The proper end state is to create/update the Gmail filter itself
(`users.settings.filters.create / list / delete`) so "always archive
X going forward" stops X from ever landing in the inbox — instead of
re-archiving each new instance. The current Gmail connector does not
yet expose those endpoints. Until it does, when asked to "always
archive X from now on":

1. Capture the rule in `$INBOX_DATA/decisions.md` with a dated entry
   describing the proposed filter (criteria + action).
2. Tell the user filter creation is not yet automated and they can
   create it manually (Gmail Settings → Filters and Blocked Addresses)
   or wait for the connector to expose filter management.
3. Keep executing one-off archives via the label-removal tool meanwhile.

### 3. Classify

For each email, decide one of:

- **archive** — matches an archive rule cleanly, no ambiguity, no
  safety-net trigger
- **review** — surface to user; can't auto-decide
- **track-as-task** — actionable; becomes a task (or a "make a task"
  suggestion if no task MCP is connected)
- **unknown** — no rule fires; default to review

Apply the universal safety net FIRST (urgent action, security alert,
past-due / penalty, payment failed, new account opened). Those ALWAYS
go to review (or task), never archive — even if another rule would
have archived them.

For ambiguous senders, do a quick `contacts.yaml` lookup. Don't read
full bodies unless metadata is genuinely insufficient.

### 3b. Flag unsubscribe candidates — FIRST-CLASS WORKFLOW STEP

While classifying, build a SECOND list in parallel: **senders the
user should unsubscribe from outright**, not just archive. Archive
clears the inbox today; unsubscribe stops the noise at the source.

A sender is an unsubscribe candidate if ANY of these apply:

- Pure marketing / promo, never actionable for this user (retail
  deals, "complete this survey", "unlock better pricing", event
  digests, vendor newsletters, etc.)
- Loyalty / rewards point notifications the user doesn't act on
- Vendor pitches the user hasn't bought from in 12+ months
- Social-media-style notifications the user never opens
- Newsletters / substacks the user hasn't read in months

NOT an unsubscribe candidate when:

- The email is itself transactional (receipt, statement, shipping
  notice, account alert) — there's no unsubscribe story for it
- The unsubscribe is **unscoped** ("Unsubscribe", "Stop all emails")
  AND the sender produces transactional email the user needs

**Hard rule — decide by the email's own description of its
unsubscribe (see `rules.md` "Unsubscribe policy"):**

- "Unsubscribe from promotional emails", "Stop receiving marketing
  emails", "Manage email preferences" → list-scoped, **safe** — even
  for a bank / card issuer / lender whose statements you want to keep
- Plain "Unsubscribe" / "Stop all emails" / generic `List-Unsubscribe`
  header → global scope, **defer** unless the sender produces no
  transactional email worth keeping

When the language is ambiguous, surface to the user with the actual
unsubscribe text quoted. Don't guess on scope.

**Present unsubscribe candidates as a separate batch after the
archive plan**, each with: sender, the offending subject, the
unsubscribe URL or header value, and a one-line reason. The user
approves the unsubscribe batch the same way they approve archives.

**Executing the approved unsubscribes is delegated to a separate,
optional `inbox-unsubscribe` skill** that encodes the per-sender
capability tiers (RFC 8058 one-click POST, HTTP one-click GET, CSRF
form, browser-driven Gmail UI fallback, mailto). If that skill is
installed, hand it the approved candidates. If it is NOT installed,
just present the candidates (sender + unsubscribe URL/header) for the
user to action by hand — this skill does not need it to function, and
identifying candidates is itself useful.

Every triage session should chip away at the noise floor. The archive
plan handles today's mess; flagging unsubscribe candidates stops next
week's.

### 4. Group and present

Present the archive plan grouped by rule, compact table per profile:

```
account — proposed archives (N)
─────────────────────────────────────────────────
Rule                       | Count | Examples
marketing-promo            | 5     | "Memorial Day deals are here", ...
shipping-delivered         | 3     | "Your package was delivered", ...
bill-statements-normal     | 4     | "Your statement is ready" (a bank), ...
```

Show review items separately (subject + sender + reason), and
track-as-task items separately (proposed task title).

#### MANDATORY: date + age on every surfaced item

Anything the user must judge — every `review`, `track-as-task`, and
"leave for you" item — **MUST show the email's date AND its age
relative to today.** Without the age the user can't tell yesterday
from three weeks ago, and that's the single most important fact for
deciding what to act on. Not optional.

- Plain relative terms paired with the date: `May 28 (3 days ago)`,
  `yesterday`, `2 weeks ago`, `last month`.
- Compute age against today's date (provided by the harness) — never
  show a bare date and make the user do the math.
- Put it in its own column (or lead the line with it). Don't bury it
  in a reason string.
- Sort each surfaced group **newest-first**.
- Applies even to "leave for you" lists — they're still actionable.
- Archive buckets (already-decided noise) don't need per-item ages,
  but if an archive decision depends on staleness, state the age that
  justified it.

```
account — needs your eyes (newest first)
Date (age)          | Subject                       | From             | Why
May 30 (yesterday)  | Invoice #### due — $###.##     | (a vendor)       | bill due → task?
May 28 (3 days ago) | Appointment follow-up         | (a clinic)       | medical vs marketing
May 6  (25 days ago)| Secure API access by June 19  | (a SaaS vendor)  | deadline action
```

### 5. Wait for approval

Never archive without explicit user confirmation on the batch. The
user may scope down, question a classification, or veto items.

**Exception — standing pre-authorized categories.** A few categories
in `rules.md` are marked as standing user rules that bypass this gate
(currently: "Review requests / feedback surveys"). Archive (or
unsubscribe-then-archive) those without asking, but still *report*
them in the run summary.

### 6. Execute

For each approved archive: remove the `INBOX` label, report
success/failure inline. For each approved track-as-task: create the
task first (or, with no task MCP, note it for the user), then archive
the source email.

### 7. Walk remaining

Do not move on to other work until every email in the original batch
has been addressed. Present remaining items in iterative groups until
the queue is empty.

### 8. Capture decisions

When the user says "going forward, always archive X" or "treat Y as a
task," append a dated entry to `$INBOX_DATA/decisions.md` before
continuing. These get distilled into `rules.md` later.

### 9. Log the run

PREPEND an entry to `$INBOX_DATA/email-triage-log.md` recording: what
was archived (by group + count), unsubscribe candidates flagged (and
handed to inbox-unsubscribe, if used), tasks created, standing
decisions made, and what was left open.

## What this skill does NOT do

- Does not auto-archive on confidence thresholds — every archive needs
  human approval on the batch.
- Does not write archive logs into the inbox; Gmail's own state is the
  system of record (the only file it writes is the data root's
  `decisions.md` / `email-triage-log.md`).
- Does not touch labels other than `INBOX`. Existing user labels stay
  intact.
- Does not execute unsubscribes itself — it only identifies and
  presents candidates (Step 3b, against `rules.md` "Unsubscribe
  policy"); the optional `inbox-unsubscribe` skill does the execution.

## Anti-patterns to avoid

- **Don't assume a property reference in a guest message points to a
  specific rental.** Verify via the listing title in the booking
  confirmation against the properties config under `$PROJECT_ROOT`
  before classifying a short-term-rental email.
- **Don't archive Venmo/Zelle/payment notifications without checking
  the body** for recipient + memo — a finance MCP only sees "VENMO
  PAYMENT"; the email holds the real context.
- **Don't batch-archive school emails without checking the To/Cc and
  child-name match** — the same school domain produces routine
  newsletters (archive) and specific-child concerns (task).
