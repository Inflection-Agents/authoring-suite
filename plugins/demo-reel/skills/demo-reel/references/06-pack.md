# 06 Pack

**Goal.** Carry the author half to the machine with the code, in one file, under the transfer limit.
**Produces.** `demo-kit.zip`.
**Gate.** `pack.py` reports the kit under the limit. Skip this phase when everything runs on one machine.

## What goes in the kit

```
demo/
  _brief/engagement.md    the ledger, phases 01 to 05 approved
  narrative.md
  script.md
  shots.yaml
  figures/                the source document's figures, as SVG or PNG
  lexicon.json            pronunciations: {"word": {"respell": "..."}}
  voice-ref/              only for a cloned voice: ref.wav and ref.txt, if the owner sends it this way
  README.md               for the person carrying the kit
```

## Pack it

```bash
python3 <skill>/scripts/pack.py demo demo-kit.zip --limit-mb 20
```

The limit is checked against the uncompressed size, because mail gateways often decompress attachments to
scan them. The
packer skips symbolic links, `node_modules`, earlier zips and system junk, and writes nothing when the kit is over the
limit. It then lists the five largest files. Figures as SVG and the voice reference as a compressed file usually fix it.

## The hand-off README

Four steps, in this order:

1. Install the plugin: `/plugin marketplace add Inflection-Agents/authoring-suite`, then
   `/plugin install demo-reel@authoring-suite`.
2. Unzip the kit at the root of the code repository, so the folder is `<repo>/demo/`.
3. Start Claude Code in that repository and run `/demo-reel:status`.
4. Run `/demo-reel:reconcile`.

Add the open items from the ledger, so the code side settles them first.

## Leaving the phase

Update the ledger's `phase` to `reconcile` and `machine` to `code` before packing, so the code side starts in the
right place.
