# Authoring Suite

Three skills for one job: making a claim land, on a slide, in a paragraph, or in the picture
next to either.

| Skill | Answers |
|---|---|
| [`diagram-design`](plugins/diagram-design) | What does this system/flow/comparison look like? |
| [`narrative-spine`](plugins/narrative-spine) | Does the deck's title sequence carry the argument? |
| [`writing-voice`](plugins/writing-voice) | Does the prose sound like it, or like an LLM wrote it? |

All three live in this repo as independently installable plugins under one marketplace.
`diagram-design` was previously its own repo (`Inflection-Agents/diagram-design`, now
archived); this repo carries it forward as a fresh copy, not a history merge, so the pre-2026-08
commit-by-commit build trail lives in the archived repo, not here.

## Install

```
/plugin marketplace add Inflection-Agents/authoring-suite
/plugin install narrative-spine@authoring-suite
/plugin install writing-voice@authoring-suite
/plugin install diagram-design@authoring-suite
```

## Editable install

Managed installs are convenient, but local edits to a skill's references get replaced on the
next package update. Clone the repo and symlink the inner skill you want to customize:

```bash
git clone git@github.com:Inflection-Agents/authoring-suite.git ~/code/authoring-suite

ln -s ~/code/authoring-suite/plugins/diagram-design/skills/diagram-design ~/.claude/skills/diagram-design
ln -s ~/code/authoring-suite/plugins/narrative-spine/skills/narrative-spine ~/.claude/skills/narrative-spine
ln -s ~/code/authoring-suite/plugins/writing-voice/skills/writing-voice ~/.claude/skills/writing-voice
```

## How the three compose

`narrative-spine` structures a deck's argument and calls `diagram-design` for every picture.
`writing-voice` isn't deck-specific: it applies to the body text inside a deck, a whitepaper,
a commit message, or a chat response, anywhere prose gets written. Use it standalone, or let
`narrative-spine` invoke it when auditing a deck's body content.

## diagram-design's own CI

`plugins/diagram-design` carries its own gate suite (`.github/workflows/diagram-design-ci.yml`),
scoped to that path so it only runs when that plugin changes. Run its gates locally from inside
the plugin's own directory: see `plugins/diagram-design/CONTRIBUTING.md`.
