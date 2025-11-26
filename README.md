# gamma-claude-skill

A Claude Skill that creates presentations using Gamma's API.

You ask Claude for something — a product update, an engineering changelog, or a news summary. When you trigger the Gamma skill, Claude prepares the content, sends it directly to the Gamma API, and returns a polished, ready-to-share deck in a few minutes.

## Prerequisites

You need a Gamma API key set in your environment as `GAMMA_API_KEY`. You can create one at https://gamma.app/settings/api-keys:

```bash
export GAMMA_API_KEY="sk-gamma-xxxxx"
```

## Installation

```bash
mkdir -p ~/.claude/skills/gamma
cp -r * ~/.claude/skills/gamma
```

## Examples

- "Review what we did this week, and use the Gamma skill to write a user-facing product update." in gemini-cli Github repo → [Gemini CLI Weekly Update](https://gamma.app/docs/Gemini-CLI-Weekly-Update-vdb95381b7ufr6v)
- "Search recent news about Gamma’s Series B round, and use the Gamma skill to create a presentation deck." → [Gamma Raises $68M Series B at $2.1B Valuation](https://gamma.app/docs/Gamma-Raises-68M-Series-B-at-21B-Valuation-uob785a81d64jva)

