# Fixing contradictions and gaps in the notes

You get a list of issues for one book (work/notefix/issues_b<book>.md). For each issue:

1. Read the topic: `python3 tools/notes_fix.py show <book> <row> [sec]` (run from /home/user/Group-app). Search other
   topics too when the issue says "rows X vs Y".
2. Decide the correct fact. Use the standard answer an APPSC/UPSC aspirant is expected to know (NCERT, official
   government data, the commission's own answer keys quoted in the notes). If an exam answer key quoted in the notes
   decides it, follow the key. If authorities genuinely differ, make the notes say so once ("⚠ Sources differ: …;
   exams have used …") instead of stating two facts as if both were true.
3. Fix it with the smallest edit: change the wrong number/name where it appears (all places), or add one bullet
   for a missing fact. Keep the notes' style: `- **Label:** text`, bold key terms. Do not rewrite other content.
4. MCQs: search app/src/main/assets/mcq<book>.json for MCQs about that fact (python, json). If a kept MCQ's keyed
   answer or text depends on the wrong version, fix its text (find/replace) or drop it.

## Output (write with a script or the Write tool; JSON only)

work/notefix/ops_b<book>.json — a list of edits for tools/notes_fix.py:
```
[{"book": 2, "row": 134, "sec": 8, "find": "Section 4A (2018)", "replace": "Section 18A (2018)"},
 {"book": 2, "row": 4, "sec": 1, "after": "anchor text in the block before", "md": "- **Objectives Resolution:** moved by **Nehru** on **13 Dec 1946**; adopted **22 Jan 1947**"}]
```
"find" must occur exactly once in that subsection and sit inside one formatting run (bold or plain): use a short
phrase. Check with `python3 tools/notes_fix.py apply work/notefix/ops_b<book>.json --dry` until it reports all ok.
Do NOT run it without --dry (the lead applies it).

work/notefix/mcq_b<book>.jsonl — one line per MCQ change:
```
{"book": 2, "id": "n1234abcd567", "find": "Section 4A", "replace": "Section 18A"}
{"book": 2, "id": "n89ab...", "drop": true, "why": "keyed to the wrong date"}
```
Edit no other file. Reply with one line per issue: what was wrong, what you set it to, and why.
