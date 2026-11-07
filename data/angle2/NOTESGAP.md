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

Also go back over the unit's blueprint keywords and APPSC PYQ angles: any that still has no MCQ because the notes lack the fact is handled by the web rule below (the previous pass skipped these; its `missing` lists in `data/angle2/out-<packet>.json` and `report-<packet>.md` name many of them).

Check with `python3 tools/angle_add.py data/angle2/gap-<packet>.json --dry` (all added, none refused). Only `--dry`;
never apply, commit or edit other files. Reply first in one line: `<packet> gaps: G gap facts, N new MCQs`, then a
few examples.

## Facts the notes lack: search the web (the user's rule)

Some angles have no fact in the notes, so no MCQ could be written: a blueprint keyword whose facts are not in the
notes, or an APPSC PYQ angle (even one with no key) the notes do not cover. Do not skip these any more. For each one:

1. Search the web (WebSearch; WebFetch to read a page). Prefer official and standard sources: government sites
   (gov.in, nic.in, pib.gov.in, AP government portals), RBI, ISRO, UN bodies, NCERT, Britannica, reputed newspapers.
   Use a fact only if two sources agree or one official source states it. For current data, take the latest figure
   and say which year it is for.
2. Add the fact to the notes: a `notes` entry in your output (the format of tools/notes_fix.py, run with
   NOTES_APP=complete), normally appended to the subsection it belongs to:
   `{"book": 2, "row": 134, "sec": 3, "append": true, "md": "- **Title:** fact in one or two short sentences."}`
   Simple English, the notes' own style, only facts APPSC could ask. Never change or delete existing note text.
3. Write 1-2 MCQs on it (all the usual rules; `sub` = that `sec`), and add `"web": "<source URL>"` to each such MCQ.
4. Never use the web to overrule the notes or a recorded APPSC key. If the web contradicts the notes, write no
   note and no MCQ; list the conflict in your report.
5. If no reliable source settles the fact, leave it out and say so.

Check the notes edits with `NOTES_APP=complete python3 tools/notes_fix.py apply <a file with just your notes list> --dry`
(all ok) as well as the usual `angle_add.py --dry`. In your reply, add: `W web facts added (notes + MCQs)`.
