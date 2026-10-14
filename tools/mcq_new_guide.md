# Writing MCQs for the untested important facts

Each page in `work/mcqnew/in_NNN.md` (`=== BOOK b ROW r SUB s | topic > page`) shows the page's notes, the
MCQs already on it, and under **FACTS TO TEST** the important facts no MCQ tests yet, labelled `[B1R5S8F1]`.

For each fact write **one** MCQ in the style of the existing ones (APPSC Group-I/II prelims):

- Exam-like stem; 4 distinct, plausible options of similar form (same kind of thing: four years, four
  places, four people…); exactly one correct answer, and it must follow from this page's notes.
  Statement-type ("Consider the following statements…") or match-type is fine where it suits the fact.
- Use only facts stated in the notes (plainly standard facts the notes do not contradict are fine for
  distractors). Never invent a fact. Do not repeat an MCQ already on the page.
- `x` (WHY): 1–3 sentences: the correct answer and the fact that makes it right; for statement/NOT
  questions say which item is false and why. Do not mention "the notes".
- `tq`: one short tip for remembering it.
- Vary the position of the correct answer (a = 0–3).
- If a fact is unclear, trivial or contradicted by the notes and no fair MCQ is possible, write
  `{"fact":"…","skip":"reason"}` instead (rare).

Write `work/mcqnew/out_NNN.jsonl`: one line per fact,
`{"fact":"B1R5S8F1","s":"…","o":["…","…","…","…"],"a":2,"x":"…","tq":"…"}`, and finally `{"done":N}`
(N = facts in the batch). Check with `python3 tools/mcq_new.py check NNN` until it passes. Write only that
output file (a scratch script in the scratchpad is fine).
