# MCQ coverage check: every very important fact tested, nothing repeated

There is no quota. The goal: every **very important** fact on each page of the notes is tested by at least
one MCQ. Remove only what adds nothing; add an MCQ only where an important fact has none.

## Input (work/mcqcut/b<book>/in_NNN.md)

Each topic starts with `=== ROW r | title`. Each page is `## SUB k | title`, then its notes, then the MCQs
filed under it, labelled `[Qr.n]` with options, ANSWER and WHY. `SUB -1` holds MCQs filed under the whole topic.

## For each page

1. **List the very important facts** of the page's notes, as short phrases (3–12 per page, fewer on short
   pages). Very important = what the exam asks: Articles/Sections, Acts and their years, provisions, firsts,
   founders, committees and chairs, headline numbers and targets, definitions, anything the notes tag with
   an exam reference (APPSC 20xx key, PYQ, UPSC…), ⚠ Trap lines and `> Exam angle` lines. Not trivia
   (one-off district figures, decimals nobody quotes, minor dates).
2. **Map MCQs to facts.** For each fact, which MCQ(s) test it (the answer, or a statement in a statement MCQ).
3. **Decide every MCQ** of the page:
   - `keep` — it tests an important fact, or a useful fact not tested by another kept MCQ.
   - drop `dup` — it tests the same fact as a better MCQ you keep (same answer fact, reworded stem, reverse
     question, statements reshuffled). Keep the better one: clearer, tests understanding, good traps; between
     statement MCQs prefer one whose answer is not "all are correct". A very important fact may keep 2 MCQs
     if they test it from different angles.
   - drop `off` — its answer is not supported by this topic's notes (if it fits another page of the same
     topic, keep it with `"move": k` instead).
   - drop `trivia` — it only tests a trivial detail the exam would not ask.
   When unsure, keep.
4. **Fill gaps.** For each very important fact no kept MCQ tests, write one new MCQ in the style of the
   others (exam-like stem, 4 distinct plausible options, one correct answer that follows from the notes,
   WHY explaining every option, a short tip `tq`). Use only facts stated in the notes. Never invent.

## Output (work/mcqcut/b<book>/out_NNN.jsonl): one line per page that has notes or MCQs, in input order

```
{"row":3,"sub":0,
 "facts":[{"f":"Regulating Act 1773 created Governor-General of Bengal","by":["Q3.4"]},
          {"f":"Supreme Court at Calcutta 1774","by":["new1"]}],
 "keep":["Q3.4","Q3.0"], "move":{"Q3.7":2},
 "drop":{"Q3.9":"dup Q3.4","Q3.11":"trivia","Q3.12":"off"},
 "new":[{"id":"new1","s":"...","o":["...","...","...","..."],"a":2,"x":"...","tq":"..."}]}
```

Every label of the page appears exactly once: in `keep`, in `move` (kept, filed under page k of the same
topic), or in `drop`. `facts[].by` names kept/moved labels or new ids. Omit `new` and `move` when empty.
Check with `python3 tools/mcq_cut_check.py <book> NNN` until it passes. Write only the output file; no helper
scripts unless named with your batch number.
