# The agent kernel

Every agent prompt this skill writes, capturing or not, carries these eleven points. Check a prompt against the list
before sending it.

1. **A mode line first:** build, read-only, or adversarial.
2. **The absolute working directory**, and the repository and branch when it is code.
3. **A numbered read-first list**, each item annotated with why it matters: the ledger, the shot list, this skill's
   reference for the phase.
4. **One named source of truth**, with the override order stated. For a demo: the ledger's rulings, then
   `shots.yaml`, then `narrative.md`.
5. **Ownership:** the files the agent owns, the files it must not touch, and the names of the agents working at the
   same time. Two agents never record against one running system at once.
6. **A loop with the actual commands in it**, for example "record the take, run `build_props.py` for both cuts, fix,
   repeat".
7. **A definition of done**, named by the phase's gate rather than restated.
8. **An invention guard:** never invent a value, an endpoint, a name or a number on screen that the events or the
   ledger do not support.
9. **A voice line**, even for agents that write no prose, because their reports are read by the owner.
10. **A reporting format**, capped in length, that asks for what went wrong, including every tool gap worked around.
11. **Provenance for numbers:** every agent that puts a number on screen names the take and the event it came from.

When the prompt touches engagement material, add a confidentiality grep against the engagement's term list and
require a zero-matches line in the report.
