# Notes facts that APPSC would ask but no MCQ tests (second pass, APPSC Complete)

Your packet's units already had the angle pass (data/angle2/INSTRUCTIONS.md): blueprint keywords and APPSC PYQ
angles are covered and stems are in APPSC wording. This pass only looks for gaps in the NOTES.

For each unit in your packet (`data/angle2/queue.txt`), take its app topics (the `# NOTES OF APP TOPIC b:r` lines of
`data/blueprint/src/<unit>.md`) and run `python3 tools/relevance.py show <b> <r>`.

Read the notes sentence by sentence (every subsection, table row and bullet). A fact is a gap when:

- APPSC would ask it: it fits a blueprint keyword of the unit or the angle vocabulary — first / largest / oldest,
  who / which / where / when, founder, author, title, capital, ruler, inscription, Article, Act + year, committee
  + chairman, scheme + objective + ministry, location / district / river, ranking, report / index + publisher,
  data point — or it is the kind of fact the topic's APPSC PYQs ask; and
- no MCQ in the topic (own or PYQ) tests it.

Skip trivia (minor officials, attendee counts, venues of minor meetings, filler dates) and facts already tested
in any direction.

Write 1 MCQ per gap fact (2 for a CORE/HIGH unit's important fact), all rules of INSTRUCTIONS.md section "Write
MCQs for what is missing" and "APPSC wording": facts from the notes, 4 options, one right, APPSC framing like the
topic's APPSC PYQs, about the APPSC shape mix, `sub` = the notes subsection. No rewording in this pass.

Output `data/angle2/gap-<packet>.json`:

```json
{"units": [{"u": "U0001", "notes_gaps": 5}],
 "new": [{"book": 1, "row": 0, "sub": 3, "s": "…?", "o": ["…", "…", "…", "…"], "a": 2, "x": "…",
          "angle": "U0001 notes gap: Prinsep deciphered Brahmi"}]}
```

Check with `python3 tools/angle_add.py data/angle2/gap-<packet>.json --dry` (all added, none refused). Only `--dry`;
never apply, commit or edit other files. Reply first in one line: `<packet> gaps: G gap facts, N new MCQs`, then a
few examples.
