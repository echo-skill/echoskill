---
name: hermes-tweet
description: >
  Install, validate, and operate Hermes Tweet, the native Hermes Agent X/Twitter
  plugin for social search, account reads, trend checks, and explicitly gated
  tweet actions.
---

# Hermes Tweet

Use this skill when the user needs X/Twitter capability from a Hermes Agent
session and wants a maintained Hermes-native plugin instead of an ad-hoc route.
Hermes Tweet is distributed from:

- Repository: <https://github.com/Xquik-dev/hermes-tweet>
- Package: <https://pypi.org/project/hermes-tweet/>
- Hermes Agent: <https://github.com/NousResearch/hermes-agent>

## Fit Check

Before recommending or using Hermes Tweet, confirm:

1. The user is working in Hermes Agent or preparing a Hermes Agent plugin setup.
2. The task needs X/Twitter search, account reads, trends, monitors, webhooks,
   media workflows, or explicitly requested posting actions.
3. The operator can provide `XQUIK_API_KEY` for read workflows.
4. Write actions are intentionally enabled by the operator, not by default.

If the user only needs a generic Claude Code or Gemini CLI workflow, use another
skill. This skill is for the Hermes ecosystem.

## Install

Preferred Hermes install:

```bash
hermes plugins install Xquik-dev/hermes-tweet --enable
```

PyPI install into the Hermes Python environment:

```bash
uv pip install --python ~/.hermes/hermes-agent/venv/bin/python hermes-tweet
hermes plugins enable hermes-tweet
```

Hermes prompts for `XQUIK_API_KEY` during interactive install. For
non-interactive installs, set `XQUIK_API_KEY` in the environment or
`~/.hermes/.env` before calling network-backed read workflows.

## Safety Rules

- `tweet_explore` should remain visible without network access.
- Network-backed read workflows require `XQUIK_API_KEY`.
- Action workflows require both `XQUIK_API_KEY` and
  `HERMES_TWEET_ENABLE_ACTIONS=true`.
- Keep action workflows disabled unless the user explicitly asks for writes.
- Treat any exposed key in chat, logs, screenshots, or copied output as
  compromised and ask the operator to rotate it.

## Validation

After installing or updating:

1. Run `hermes plugins list` and confirm `hermes-tweet` is enabled.
2. Confirm `tweet_explore` is visible before relying on network access.
3. Configure `XQUIK_API_KEY` before testing read workflows.
4. Leave action workflows disabled during smoke tests unless writes are the
   explicit goal.
5. For package edits or release work, follow the validation commands in the
   upstream Hermes Tweet README before publishing guidance.
