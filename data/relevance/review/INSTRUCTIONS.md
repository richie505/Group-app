# Second look at the MCQs the relevance audit removed

The relevance audit took 5,392 of APPSC Complete's own MCQs out of the app; they are kept in
`data/relevance/archive.jsonl`. The user wants MCQs kept: remove one only after critical analysis. Your job is to
re-judge every removed MCQ in your packet and put back every one that is useful for APPSC Group 1 / Group 2.

Your packet's removed MCQs are in `data/relevance/review/in-<packet>.jsonl` (one per line: book, row, subsection,
the reason it was removed, and the full question `q`). Read the file completely.

For each topic (book:row) in your packet, look at what the app still has:
`python3 tools/relevance.py show <book> <row>` prints the topic's notes and its current MCQs (PYQs have ids starting "y").

## Decide for each removed MCQ

**Restore** it unless one of these is clearly true:

1. **Exact duplicate.** A PYQ or another MCQ still in the same topic asks the same fact in essentially the same
   way (same stem idea, same answer), so this one adds nothing. If it tests a different angle, a different
   statement, a different option set that teaches something new, or the same fact from the other direction,
   restore it. A near-duplicate is not enough to stay removed; it must be a real repeat.
2. **Pure trivia with no exam value**: attendee counts, minor officials' names, venues of minor meetings, serial
   numbers, exact rupee amounts of minor items, dates of trivial events. Anything APPSC could plausibly ask
   (schemes, reports, indices, firsts, rankings, places, persons of note, constitutional/legal facts, AP facts)
   is NOT trivia: restore it.
3. **Clearly off-syllabus** for APPSC Group 1/2 (e.g. cooking tips, celebrity gossip, foreign-only local trivia).

**Wrong or ambiguous key / wrong stem / outdated figure**: do not leave it out for that alone. If you are sure of the
right answer from the notes or solid knowledge, restore it with a `fix` (correct `a`, and/or reword `s`, `o`, `x`
so exactly one option is right and the explanation matches). Only leave it out if it cannot be repaired.

When unsure, restore.

## Output

Write `data/relevance/review/restore-<packet>.json`:

```json
{"restore": [{"id": "n…", "why": "different angle: asks the year, PYQ asks the place"},
             {"id": "f…", "why": "key fixed", "fix": {"a": 2, "x": "…"}}],
 "keep_out": [{"id": "n…", "why": "exact repeat of PYQ y… (same stem and answer)"}]}
```

Every id in your input file must appear exactly once, in `restore` or in `keep_out`. `fix` may set any of `s`
(stem), `o` (full options list), `a` (0-based index of the right option), `x` (explanation).

Check it: `python3 tools/relevance.py restore data/relevance/review/restore-<packet>.json --dry` must report all
your restore ids with none invalid. Run ONLY with `--dry`; never apply, never commit, never edit other files.

Also write `data/relevance/review/report-<packet>.md` with counts (restored, restored with fix, kept out by reason)
and a few examples. If the harness will not let you write the report, put it in your final message instead.

Reply in one line first: `<packet>: restore N (F fixed), keep out K (dup D, trivia T, off-syllabus O, unfixable U)`.
