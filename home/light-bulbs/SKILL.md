---
name: light-bulbs
description: >-
  Keep a durable log of the light bulbs and fixtures installed at a home or
  across several properties, plus the spare bulbs on hand. Use when the user
  asks what bulb a fixture or socket takes, sends a photo of a bulb, socket,
  fixture, box, or receipt, replaces or installs a bulb, orders bulbs, shares
  old notes about bulbs, asks what spares they have, wants to log, record,
  track, update, look up, or correct lighting info, or is choosing wattage,
  brightness (lumens), color temperature (warm, soft white, bright white,
  daylight, Kelvin), base, or shape for a replacement.
metadata:
  data-store: google-drive
  data-selector: "skill-data=light-bulbs"
---

# Light Bulbs

## Objective

Nothing of value from any session may be lost. The data store holds every
record; this skill holds every process. Chat history and agent memory are not
storage; when an agent's memory disagrees with the data store, the data store
wins. If a session ends, an agent's memory is wiped, or the user switches
agent vendors, a new agent with this skill and access to the data store must be
able to continue without asking the user to repeat anything.

This skill is responsible for enforcing that: capture as facts arrive, and
promote any new rule the user sets into this skill (generic process) or the
data store (personal specifics) the moment it's set.

## Locating the data

The data is one spreadsheet tagged with the public file property
`skill-data = light-bulbs`. Find it by that property — never by title, path,
or a hardcoded ID:

```
properties has { key='skill-data' and value='light-bulbs' } and trashed = false
```

- **Exactly one match** → use it for the whole session.
- **Several matches** → ask which is authoritative.
- **No match in any connected account** → stop and ask: point me at an existing sheet (then tag it), or
  create a fresh one. Never create a new sheet just because the search came up
  empty. When creating: make the two tabs below with the headers exactly as
  listed, tag the file, and tell the user where it is.

Tabs are found **by title** (`Installed`, `Inventory`) until the spreadsheet
tooling supports in-file metadata. If a tab title isn't found, ask; don't
create a duplicate tab.

## Structure

### `Installed` tab — what is in each socket

One row per spot (a fixture or a group of identical fixtures).

| Column | Meaning |
|---|---|
| Property | Which home or property. Use the user's own name for it. |
| Spot | Room and fixture, specific enough to find it ("rear entry hall, inside door from garage"). |
| Base / Socket Type | E26 medium, E12 candelabra, G9, GU10, etc. |
| Socket Rating | Printed rating on the socket itself (e.g. 660W / 250V). This is the socket's limit, not the fixture's. |
| Fixture Max Wattage | The fixture's label limit. Usually lower than the socket rating. |
| Bulb Type | LED, halogen, incandescent, CFL; brand and relevant ratings (enclosed, damp). |
| Bulb Shape | A19, BR30, BR40, PAR38, G25, B11, etc. |
| Actual Watts | Power the installed bulb draws. |
| Equivalent Watts | The incandescent equivalent printed on LED packaging. |
| Color Temp (K) / Warmth | Kelvin and/or the label wording (Soft White, Bright White, Daylight). |
| Lumens | Brightness. |
| Replaced / As-Of Date | See "Dates" below. |
| Notes | Sources, verbatim user notes, orders, observations — see "Conventions". |

### `Inventory` tab — spares on hand and on order

One row per product (a box or pack), with Brand, Product / Type, Tech, Shape,
Base, Actual Watts, Equivalent Watts, Color / K, Lumens, Dimmable,
Ratings / Limits, Qty on Hand, Location, As-Of Date, Notes.

- Items on order go here too, with Qty marked "ON ORDER" and the order details
  in Notes. Update Qty and Location when they arrive.
- When a spare is installed, add or update the `Installed` row **and**
  decrement the `Inventory` quantity in the same step.

## Conventions

1. **Capture continuously.** Log facts as they arrive, not at the end.
2. **Lose no detail the user provides.** Keep their notes verbatim in Notes,
   with the source (note title, photo name, message) and every timestamp they
   give. Paraphrase is loss. Map what fits into columns *and* keep the verbatim
   text.
3. **Label the agent's contributions.** Suggestions, observations, and
   readings from photos go in Notes marked as the agent's, with the date
   ("Claude's suggestion (2026-01-05, not from the note): …"). Never let them
   read as the user's facts.
4. **Flag uncertainty.** If something is inferred ("these are probably the
   fridge bulbs"), start the note with UNCONFIRMED and say what the inference
   rests on. If text on a photo is partly illegible, say which part.
5. **No empty rows.** Every row must carry real information about a bulb or
   fixture. A to-do ("change the bulbs in the game room") with no specs is not
   a record — don't log it.
6. **Dates.** `Replaced / As-Of Date` must match the specs in that row. Use the
   install date when known ("2026-01-05 (installed)"); otherwise the date the
   specs were known to be true ("2024-09-27 (as-of)", e.g. the date of the
   user's note). When a bulb changes, update the date and the specs together.
7. **Properties the user says are gone** (sold, no longer theirs) are removed,
   and not re-added from old files or receipts.
8. **Don't duplicate.** A preference that's evident from the rows themselves
   (the color installed in a room) doesn't need restating elsewhere. Preferences
   that aren't evident (e.g. "never Daylight in this spot") go in that spot's
   Notes.

9. **Images** (photos, receipts, screenshots) are rare here, so there's no image
   column. Save the image to the skill's attachments folder (tagged
   `skill-data=light-bulbs`, `skill-data-role=attachments`; once it exists, tag
   the spreadsheet `skill-data-role=data`) and link it in that row's Notes, next
   to the text it relates to. If the tools can't make an inline link, put the
   URL(s) in Notes as plain text. If the agent can't upload, ask the user to
   save the image to Drive, then link it.

### Logging orders

For a bulb order, record in the relevant row's Notes (and in `Inventory`):
order number, order date, product name and specs, seller / store, price
breakdown (subtotal, shipping, discounts, tax, total), delivery estimate, and
how many spares it leaves. Mark "not yet installed" until it is.

- **Skip warranty terms** — noise.
- **Lifespan** only when it varies meaningfully among bulbs of the same type
  *and* can't be reliably looked up from the bulb type. Otherwise skip it.

## Helping choose a replacement

Work out, in order, and say which facts are confirmed vs. assumed:

1. **Base** — from the socket or old bulb (E26 is the standard US screw base).
2. **Shape and size** — measure the old bulb or the can:
   BR30 ≈ 3¾ in across (5–6 in cans), BR40 ≈ 5 in (6 in+ cans),
   PAR38 ≈ 4¾ in. A smaller can in the same room as BR40s is usually BR30.
3. **Wattage limit** — the fixture's label governs, not the socket rating.
   LEDs draw a fraction of their equivalent, so they rarely hit the limit.
4. **Brightness** — match the old bulb's lumens or equivalent wattage when
   known. Accent lights near main lights shouldn't outshine them.
5. **Color temperature** — match nearby fixtures in the same room; check the
   spot's Notes for recorded dislikes. 2700K soft white, 3000K bright white,
   4000K cool, 5000K daylight.
6. **Ratings** — damp or wet rated in bathrooms and outdoors; enclosed-rated
   under glass shades or domes; check "not for air-tight (ICAT) cans" warnings.
7. **Dimmer** — dimmable only matters if the switch is a dimmer.
8. **Check `Inventory` first** — the right bulb may already be on the shelf.
   Say why a spare does or doesn't fit (shape, color, rating).

Old incandescent reflector bulbs in cans often leave heat damage (flaking or
discolored housing paint); note it as an observation and prefer LED.

## Workflows

- **Photo of a bulb, socket, or box** → identify base, shape, and printed specs;
  log them with the photo's name and source; mark illegible parts.
- **User's old note** → log every detail verbatim with the note's title and
  timestamps; one row per spot even if the note grouped several.
- **Install** → update the `Installed` row (specs + date) and `Inventory`
  quantity together.
- **Order placed** → log per "Logging orders"; add an `Inventory` row marked
  ON ORDER.
- **Correction from the user** → fix the cell, and if the user's correction
  changes how records should be kept in general, update this skill.
- **End of session** → check the conversation against the sheet: anything
  provided, decided, or installed that isn't recorded gets recorded now.

## Known tooling gaps

- Some spreadsheet tools can't add, rename, or delete tabs, or insert/delete
  rows. If so: ask the user to add tabs by hand; to remove a row, rewrite the
  rows below it upward and clear the last one — confirm first.
- Tabs are located by title until in-file metadata lookup is available.
