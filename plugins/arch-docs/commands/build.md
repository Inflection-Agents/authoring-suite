---
description: Build the diagrams, in waves of agents with disjoint file ownership
argument-hint: [diagram numbers or range]
---

Use the `arch-docs` skill and load `references/07-build-agents.md`.

Split the work so each agent owns its own spec files, name the files other agents hold, and ban the whole-set build
command from agent prompts. Every agent plans coordinates before writing a spec, looks at the rendered image before
reporting a page done, and reports every library gap it worked around. Run the set build yourself after the wave.
