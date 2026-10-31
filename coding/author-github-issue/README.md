# author-github-issue

Your agent files GitHub issues and opens pull requests — but does it follow your team's conventions, avoid leaking PII, and write text that someone else can actually pick up? This skill enforces structured authoring: a file-based workflow, privacy rules, a scan and review of the text before it is posted, and self-contained bodies that don't assume conversation context. The same rules cover a pull request's title, body, and comments.

Activates automatically whenever the agent creates, edits, or comments on a GitHub issue or pull request.

Cross-platform — works with any AI agent that supports the SKILL.md format.

## Install

```bash
pipx install echomodel
em skills install author-github-issue
```

Or install directly with Gemini CLI:

```bash
gemini skills install https://github.com/echo-skill/echoskill.git --path coding/author-github-issue
```

