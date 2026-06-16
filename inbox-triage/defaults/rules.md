# Inbox triage rules (generic starter)

This is a generic, non-personal starter ruleset shipped with the
inbox-triage skill. When the skill scaffolds a fresh data root, it
copies this file in. Replace and tune it for your own inbox — your
real rules supersede everything here.

## Universal safety net (evaluate FIRST — these never auto-archive)

Always route to `review` (or `track-as-task`), even if another rule
would archive them:

- Urgent action explicitly required by a real deadline
- Security alerts (new sign-in, password reset, MFA changes)
- Past-due notices, penalties, late fees
- Failed / declined payments, insufficient-funds notices
- A new account opened or credit line changed
- Anything threatening loss of service, money, or access

## Archive (clean matches, no ambiguity)

- **marketing-promo** — retail deals, sales, "X% off", seasonal
  promos, vendor newsletters you don't read
- **shipping-delivered** — "your package was delivered" after the
  fact (in-transit notices for something you're waiting on → review)
- **bill-statements-normal** — "your statement is ready" when autopay
  is configured and working; routine balance/posting notices
- **autopay-working** — upcoming-recurring-payment reminders and
  payment-sent confirmations when autopay is functioning. Surface
  ONLY on failure / skip / amount change / insufficient funds.
- **social-notifications** — "X posted", trending digests, "people
  you may know", forum activity you never open
- **receipts-noise** — low-value automated receipts already captured
  elsewhere (only if you don't need them for accounting)

## Review (surface to the user)

- Anything matching the safety net
- Personal mail from a real person
- Bills with a due date and no confirmed autopay → likely a task
- Medical / health follow-ups
- Mail you can't confidently classify (default for `unknown`)

## Track-as-task (actionable)

- A bill due that needs a payment action
- A form / response with a deadline
- A scheduling request that needs a calendar action
- An explicit "please do X by Y" from a real person

## Unsubscribe policy (summary)

Decide by the SCOPE of the opt-out, read from the email's own words:

- "Unsubscribe from promotional emails" / "Stop marketing emails" /
  "Manage email preferences" → list-scoped, **safe to unsubscribe**,
  even for a bank/card/lender whose statements you want to keep.
- Plain "Unsubscribe" / "Stop all emails" / generic List-Unsubscribe
  header → global scope, **defer** unless the sender produces no
  transactional mail worth keeping.
- Ambiguous → surface to the user with the unsubscribe text quoted.

Never unsubscribe from transactional senders (receipts, statements,
shipping, account alerts) — there's no marketing list to leave.

## Stale-review heuristic

An item left unaddressed long enough is often safe to archive (an
expired reservation request, a deal that ended). When an archive
decision depends on staleness, state the age that justified it.
