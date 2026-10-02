# Claude desktop app: installing and verifying skills

Load this when the harness is the Claude desktop app (its Code tab, or a
desktop conversation) and you are installing, updating, or verifying a skill.
The file locations below are observed app internals, not a documented
interface: they can change between app versions. Re-check them if a path is
missing.

## Installing a `.skill` bundle (macOS)

On macOS, once you have the `.skill` file, hand it to the installer one of two
ways, and **offer the user the choice**, because they serve different moments:

| Command | What happens | When |
|---|---|---|
| `open -R <file>.skill` | Reveals the file **selected** in Finder; the user drags it into the install UI | The user wants to *see what they're installing and choose deliberately* |
| `open <file>.skill` | `.skill` is registered to the Claude desktop app, so this (= double-click) launches the **install popup directly**: one click to install or replace | Fast, one-step install |

More generally: whenever you direct a user to a local file they must act on
(install, upload, attach, drag), run `open -R <path>` (reveal it selected) or
`open <path>` (hand it to its handler) rather than just printing the path.

A bundle whose zip contains a top-level folder named after the skill
(`<name>/SKILL.md`) has also been observed to install correctly.

## Updating an already-installed skill

Re-installing an edited `.skill` replaces the saved skill in place, leaving a
single copy rather than a stale duplicate. Prefer this over dropping a
`~/.claude/skills/<name>` symlink beside a saved skill of the same name, which
creates two same-named skills and ambiguity about which one loads.

The update does **not** reach agents immediately. See the two copies below.

## Two copies of every saved skill

The app keeps a saved skill in two places, and only one of them changes when
the user clicks Save:

| Copy | Observed location (macOS) | Updated |
|---|---|---|
| **App store**: what the save writes | `~/Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin/<id>/<id>/skills/<name>/` | Immediately on Save |
| **Load copy**: what Code-tab agents (and `claude -p` in the same account) load, injected as the `anthropic-skills` plugin | `~/.claude/skills/synced/<id>_<id>/<name>/` | When the app next syncs. Not on Save, and not necessarily when a new session starts |

So:

- **"Did the save land?"** → compare against the **app store**.
- **"Will an agent on this machine get the new version?"** → compare against
  the **load copy**, or ask a fresh agent (e.g. `claude -p`) to quote a line
  unique to the edit and say where it loaded the skill from.
- Until the load copy syncs, agents keep loading the previous version even
  though the save succeeded. Checking only the load copy gives a false "not
  saved"; checking only the app store gives a false "agents have it".

## Comparing an installed copy to the source

The app reformats frontmatter on save: it quotes `name:` and re-flows folded
(`>-`) strings into a single line. So compare:

- **`SKILL.md` frontmatter**: parsed as YAML, compared as data.
- **`SKILL.md` body**: exactly.
- **Every other file** (`references/`, `scripts/`, `assets/`): byte for byte.

A byte-level diff of `SKILL.md` will report a difference after every save even
when the content is identical.
