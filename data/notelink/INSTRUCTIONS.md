# Link every own MCQ to the exact notes lines that state its answer (APPSC Complete)

The book icon on an MCQ must open the notes lines that answer THAT question, like a good reference answer:
the right answer and the line(s) of the notes that state it. Today the app guesses the page by matching words and
often shows a neighbouring fact. You replace the guess with a checked link for every own MCQ (ids not starting
"y"; PYQs are left alone).

## For each topic in your packet

Run `python3 tools/notelink.py show <book> <row>`. It prints the topic's notes with every line numbered
(`row:sec:block`; a table row `row:sec:block.row`) and then the topic's own MCQs (answer marked `*`, and `x`).

For EVERY own MCQ listed, pick the line(s) that state the fact the right answer depends on:

- **One-liner:** the 1 line (at most 2) that says the answer for what the stem asks (Phase I of Veligonda
  inaugurated at Markapuram on 31 Aug 2026 -> the line with "Phase I inaugurated ... 31 August 2026 ...
  Markapuram"). A table: link the one ROW, never the whole table.
- **Statements / NOT / match / chronology:** one line per statement or pair, the line that settles whether it is
  right (up to 4 lines).
- The line must actually state the fact. Do not link a line that only shares words with the question, a heading,
  or a "traps" / "number game" line when a body line states it.
- If the fact is on another topic's page, you may link that line (`row:sec:block` of that topic in the same book).
- **If no line in the notes states it**, add the fact to the notes: a `notes` op in the notes_fix.py format,
  appended to the right subsection, simple English, one bullet:
  `{"book": 6, "row": 14, "sec": 0, "append": true, "md": "- **Title:** fact."}`
  Use the MCQ's own explanation only if it is correct; when unsure, check the web (official or two agreeing
  sources) and never contradict the notes or a recorded APPSC key. Then link it as `"+k"` (k = index of that op in
  your `notes` list). If the MCQ's key itself looks wrong against the notes, link the line that shows it and add it
  to `doubtful` (do not change the MCQ).

## Output

`data/notelink/link-<packet>.json`:

```json
{"links": [{"book": 6, "id": "ca4cf9d4152886", "lines": ["14:0:1"]},
           {"book": 6, "id": "…", "lines": ["14:0:2.3"]},
           {"book": 6, "id": "…", "lines": ["+0"]}],
 "notes": [{"book": 6, "row": 14, "sec": 3, "append": true, "md": "- **…:** …"}],
 "doubtful": [{"id": "…", "why": "key says X, notes line 14:2:5 says Y"}]}
```

Every own MCQ of every topic in the packet must appear exactly once in `links`.

Check: `python3 tools/notelink.py check data/notelink/link-<packet>.json` must say "all ok". Then read
`python3 tools/notelink.py preview data/notelink/link-<packet>.json` and fix any MCQ whose linked text does not
plainly answer it. Only check/preview: never apply, never commit, never edit other files.

Reply first in one line: `<packet>: N MCQs linked (T table rows, M multi-line), A notes additions, D doubtful`.
