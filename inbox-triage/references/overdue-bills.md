# Past-due and late-payment notices: check before surfacing

Read this when a triage candidate says a payment was missed, is late, or
is past due. It applies in both Sweep and Attention mode.

## Why this check exists

The universal safety net sends every past-due notice to `review`, and
that is the right default: the cost of archiving a live one is money or
service. But the same rule means a notice that was *already paid* comes
back run after run, because nothing ever clears it. The user stops
reading those lines, and that is how a real one gets missed later.

The evidence that a notice was resolved is usually already in reach: a
payment to that creditor in the finance tool, a "thank you for your
payment" from the same sender a few days later, the next statement with
nothing past due, and no further notices. Gathering it costs a handful
of bounded lookups. Not gathering it costs the user's attention on
every run. So: check first, then either propose the archive with the
evidence shown, or surface the notice with exactly what is still
unclear.

This never archives on its own. A resolved notice is *proposed* for
archive in its own bucket, evidence attached, and goes through the same
batch approval as everything else.

## Which notices get the check

Run it for any email whose subject or snippet says a payment was missed
or is late: "past due", "payment overdue", "late payment", "missed
payment", "you forgot a payment", "we haven't received your payment",
"minimum payment not received", "late fee assessed", "your account is
delinquent", "payment reminder: overdue", and the like, from any
creditor: card issuer, lender, utility, insurer, subscription, landlord,
medical biller, tax preparer, school.

**Always surface, with the check's findings attached as context, when
the notice has escalated past "a payment was missed":**

- Shutoff, disconnection, or suspension of service
- Referral to collections, a collection agency's own letters
- Legal action, lien, repossession, foreclosure, eviction
- Cancellation of insurance coverage for non-payment
- Account closure, credit-line reduction, or credit-bureau reporting
- Anything from a tax or government authority

These stay in front of the user because the downside of a wrong archive
is loss of coverage or legal exposure, and because escalation pipelines
lag: a collections letter can arrive after the payment posted, and the
user still needs to confirm the referral was withdrawn. Still run the
lookups; "payment found on the 8th, confirm with the utility" is a far
better line than "shutoff notice, 3 weeks old".

**Honor the user's own rules.** If `rules.md` says past-due notices must
always be surfaced even when resolved, do not propose the archive. Run
the check anyway and surface the notice with its evidence; the lookups
are what turn "past-due notice, 2 months old" into "past-due notice,
paid on the 8th".

## Step 1: Pin down the notice

From the subject, snippet, and sender, capture:

- creditor (the sender's organization, and the brand named in the
  subject if different, e.g. a servicer emailing about a store card)
- notice date, and its age today
- amount past due, if stated; the due date it missed
- an account hint, if any (last digits, a plan name) in case the user
  holds more than one account with this creditor

Read the body only if the subject and snippet lack the amount or the
account hint and the decision will turn on it.

## Step 2: Gather evidence

Four lookups, each bounded to one query. Do them all, even when the
first one looks decisive: the verdict needs the later-notices check,
and the sender-history check is a phishing guard.

**A. A payment to the creditor (finance tool).** Search transactions
whose payee matches the creditor, from about five days before the
notice date through today. Why before: notices are generated from a
balance snapshot, and a payment that posted a day or two earlier is
often the one that cleared it. Count a payment whose amount covers the
stated past-due amount (or the minimum due, when that is what was
missed). A smaller payment is partial; say so.

*Fallback:* no finance tool connected, or the creditor's name does not
appear in it (paid by paper check, or from an account the tool does not
see). Note "finance tool not connected" or "no matching payee" in the
evidence line and rely on B.

**B. A payment confirmation from the sender (Gmail).** Search mail from
the sender's domain after the notice date for "thank you for your
payment", "payment received", "payment posted", "payment confirmation",
"we received your payment". This is the direct evidence that works
without a finance tool and covers payments made outside it.

**C. Sender history before the notice (Gmail).** Search mail from the
sender's domain before the notice date. Expect statements, bills,
"payment due" reminders, autopay confirmations.

- History present: an established relationship, and a baseline cadence
  for reading D.
- No history at all: either a new account or a phishing attempt, and
  both are safety-net triggers in their own right. Surface the notice
  as suspicious, never as resolved, whatever A and B say. Also treat
  as suspicious a sender domain that does not match the brand in the
  subject, or links that point somewhere other than the creditor.

**D. What arrived after the notice (Gmail).** Search mail from the
sender's domain after the notice date and sort it into:

- a *later past-due notice*: the one in hand is superseded, and the
  account may be escalating
- a *later statement or bill*: read its body once, only for the past-due
  line, late fee, and interest charge, when A and B found nothing
- nothing: no signal either way (a creditor that only emails when
  something is wrong is common)

## Step 3: Decide

Direct evidence is a payment to the creditor after the notice (A), a
payment confirmation from the sender (B), or a later statement whose
body shows no past-due balance (D). Everything else is circumstantial:
statements before, silence after, the account looking normal elsewhere.

| Verdict | Condition | Outcome |
|---|---|---|
| **resolved** | at least one piece of direct evidence, no later past-due notice, sender history present | propose archive in an `overdue-resolved` bucket, evidence line attached |
| **superseded** | a later past-due notice from the same sender exists | propose archiving the older notice(s); surface only the latest, as escalating |
| **partial** | a payment was found but smaller than the stated amount | surface, with the gap stated |
| **unclear** | circumstantial evidence only | surface, listing what was checked and what was missing |
| **live** | recent notice (inside the creditor's grace window, about ten days), nothing found in A or B | `track-as-task`: pay or confirm |
| **suspicious** | no sender history, or domain or link mismatch | surface as possible phishing under the security safety net |

Why direct evidence is required: "the next statement arrived and there
were no more notices" is exactly what a creditor that emails sparsely
looks like whether or not the bill was paid. Silence is not payment.

When the evidence shows a late fee or interest charge was assessed, say
so in the evidence line even when the verdict is resolved. The user may
want to ask for a waiver, and that is their call to make before the
batch is approved.

## Step 4: Say what you found

One line per notice, the same shape for every verdict, so the user can
scan the bucket and veto any item. Lead with date and age like every
other surfaced item; name each source and the date of what it found;
name what was not found or not connected.

```
overdue-resolved — proposed archives (2)
Date (age)            | Notice                              | Evidence
Aug 14 (8 weeks ago)  | Payment past due $142 — a card      | paid $142 Aug 19 (finance); "Thank you for your payment" Aug 20; Sep 12 statement: no past-due line; no later notice
Sep 2 (6 weeks ago)   | Missed payment — an internet ISP    | "Payment received" Sep 5; Oct 1 bill: no past due, $10 late fee charged; no later notice; finance tool not connected

needs your eyes
Date (age)            | Notice                              | Status
Oct 9 (4 days ago)    | Payment overdue $88 — a utility      | live: no payment to this payee since Sep 30 (finance); no confirmation; history since 2024 → task: pay or confirm
Jul 30 (10 weeks ago) | Past due — a medical biller         | unclear: no finance match (payee not in tool); no confirmation; two earlier statements; nothing after → did you pay by check?
Sep 20 (3 weeks ago)  | Final notice before disconnection   | always surfaced: paid $210 Sep 22 (finance); no later notice → confirm the shutoff was cancelled
```

## Fallbacks and edge cases

- **No finance tool:** B and a later statement are the only direct
  sources. Say so in the line so the user knows what the verdict rests
  on.
- **Metadata-only mail access:** statement bodies cannot be read, so
  only A and B count as direct.
- **Several accounts with one creditor:** match on the account hint from
  Step 1. Without one, and with more than one candidate payment, call it
  unclear and name the ambiguity rather than picking.
- **Autopay creditors:** a past-due notice from a sender whose history
  shows autopay confirmations means the autopay skipped or failed. Even
  when resolved, say "autopay missed in August" so the user can check
  the next cycle.
- **A notice older than the next billing cycle with nothing after it:**
  still unclear, not resolved. The creditor may simply have stopped
  emailing. Ask the one question that settles it ("did you pay this by
  another route?") rather than assuming.

## Log it

In the run log entry, record each resolved or superseded notice with
its evidence line, so the archive is auditable later. If the user sets
a standing rule ("trust a payment confirmation from this sender",
"always surface this creditor"), capture it in `decisions.md` as usual.
