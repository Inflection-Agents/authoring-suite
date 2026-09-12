# Voice Sheet Schema

One entry per habit. Each entry has four fields: habit name, liked line,
rejected line, scope note.

## Fields

- `habit`: short name for one observable stylistic habit
  (for example, "grounds claims in a number").
- `liked`: a line the owner kept. Neutral placeholder text is fine;
  the habit must be audible in it.
- `rejected`: the same line with exactly that habit removed or broken
  and nothing else changed. One pair tests one habit, so the reader
  can see its edge.
- `scope`: the registers where the habit was observed (opinion,
  explainer, work story). Keep cross-register habits only.

## Admission rules

- A habit reaches the sheet only if it survives all three talk-through
  registers. A habit seen in one topic alone never reaches the sheet;
  note the exclusion in the scope field and drop the entry.
- Deletion check: strip the habit from the liked line. If the line
  stays strong without it, the habit is not load-bearing; drop it.
- On any conflict between this sheet and a stored draft-vs-rewrite
  pair, the rewrite wins without a sheet edit.
