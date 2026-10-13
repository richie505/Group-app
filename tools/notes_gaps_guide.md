# Filling gaps and settling hedges in the notes

Your batch (work/notegaps/in_NNN.md) lists open items, topic by topic. Run commands from /home/user/Group-app.
Read each topic's subsection first: `python3 tools/notes_fix.py show <book> <row> <sec>`.

## GAP — a line "!! Not in your sources: X"
The notes lack fact X. Find it:
- Use WebSearch (load it with ToolSearch "select:WebSearch,WebFetch") for anything current, numeric or AP-specific;
  prefer official sources (gov.in, PIB, RBI, Census, ministry/AP government sites, UN bodies, Britannica).
  Standard textbook facts you are certain of (NCERT level) need no search.
- **Filled:** replace the gap line with a normal line in the notes' style, the fact ending with `[GK]`
  (marks it as added from outside the notes): `  - **Label:** fact [GK]`. Keep the gap line's indentation.
  If the fact changes over time, give its date ("as of Aug 2026").
- **Not found / not certain:** leave the line exactly as it is. Never guess, never fill from vague memory.
- **Not worth it** (trivia an exam would never ask, e.g. a platform's software vendor, a minor seizure count):
  delete the gap line (`"md": ""`).
- Two gap lines asking the same thing: fill one, delete the other.

## HEDGE — "some notes / other notes / older notes say…", "verify", "misprint"
The notes give two versions of a fact. Decide it like the earlier contradiction pass:
- One version is the standard/correct one (official data, NCERT, an exam answer key quoted in the notes):
  state that one; keep the other only as a short trap if exams actually used it (`⚠ Trap: not 1963`),
  otherwise remove it. Remove the words "some notes/other notes/older notes" — the learner never saw "notes".
- Genuinely different authorities or dates (survey A vs survey B, provisional vs final): one line
  `⚠ Sources differ: A (source/year); B (source/year)`.
- "verify" / "misprint": check it and write the settled fact, without the word "verify".
- Can't settle it with a reliable source: leave it.

## Edits — work/notegaps/ops_NNN.json (a JSON list)
```
{"book": 2, "row": 126, "sec": 7, "block": "GANHRI (SCA) accreditation", "md": "  - **NHRC:** GANHRI \"A\" status ... [GK]"}
{"book": 2, "row": 126, "sec": 7, "block": "current GANHRI accreditation status", "md": ""}
{"book": 1, "row": 210, "sec": 0, "find": "short phrase", "replace": "new phrase"}
```
- "block": text found in exactly one block of that subsection; that block is replaced by "md" (markdown as
  `show` prints it, minus the `[n]` number; a table is replaced as a whole markdown table). "" deletes it.
- "find"/"replace": a small change inside one formatting run (exactly one occurrence).
- One op per block; don't touch blocks not in your list (except a table whose cell holds the item).
Check with `python3 tools/notes_fix.py apply work/notegaps/ops_NNN.json --dry` until all ok. Never run it without --dry.

## MCQs — work/notegaps/mcq_NNN.jsonl
If a settled hedge changes which answer is right, search app/src/main/assets/mcq<book>.json and fix or drop
MCQs keyed to the losing version: `{"book": 1, "id": "n…", "find": "…", "replace": "…"}` or
`{"book": 1, "id": "n…", "drop": true, "why": "…"}`. Filled gaps need no MCQ changes.

## Log — work/notegaps/log_NNN.jsonl, one line per item, in order
`{"b": 2, "r": 126, "s": 7, "i": 8, "kind": "GAP", "done": "filled|deleted|resolved|left", "src": "url or reason"}`

Write only those three files. Reply with counts (filled / deleted / resolved / left).

Helper scripts: other agents run at the same time — name any script you write with your batch number
(e.g. scratch/b031_ops.py), never a shared name.
