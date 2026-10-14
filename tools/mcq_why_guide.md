# Explanation pass: every MCQ's WHY agrees with the notes

The notes were restructured topic by topic and corrected; many explanations (WHY) were written against
older notes. `work/mcqwhy/in_NNN.md` has, per topic (`=== BOOK b ROW r`), each page's notes
(`## PAGE k | title`) followed by the MCQs filed under it, each labelled `[id]` with options, ANSWER and WHY.

For **every** MCQ, read its stem, options, ANSWER and WHY against that page's notes (and the topic's other
pages) and decide:

- **Keep** (write nothing) when the WHY is correct, agrees with the notes, and says why the answer is right.
- **Rewrite the WHY** when it: states a fact the notes contradict (date, number, name, place, Article,
  ranking…); explains the wrong option; is missing or only repeats the answer; says "all correct" when a
  statement is false; or is garbled. A good WHY is 1–3 sentences: the correct answer and the fact from the
  notes that makes it right; for statement / match / assertion–reason / "NOT" questions, name which item is
  false or the trap and why. Use only facts in the notes (or plainly standard facts the notes do not
  contradict). Keep any line starting `⚠ Sources differ` and any "APPSC key said…" remark.
- **Correct the key too** (rare) only when the notes clearly show the marked answer is wrong and another
  option is right: add `"a"` (0–3 = A–D) and `"key"` (one line: what the notes say).

Do not change stems or options. Write `work/mcqwhy/out_NNN.jsonl`: one line per changed MCQ,
`{"id":"n…","x":"…"}` (plus `"a"`, `"key"` for a key change), and finally `{"done":N}` where N is the number
of MCQs in the batch. Check with `python3 tools/mcq_why.py check NNN` until it passes. A short Python script
in the scratchpad may help write the file; write nothing else in the repo.
