# Filling thin pages from the MCQ bank (no new MCQs)

Each page in `work/mcqgap/in_NNN.md` (`=== BOOK b ROW r SUB s | topic > page`) has notes but only 0–2
MCQs. Below its notes are the MCQs already on it (`[Qr.n]`) and candidates from the bank (`[P1]`, `[P2]` …):
MCQs the app once had, not in the app now.

For each page:

1. **List the very important facts** of the page's notes (3–10; fewer on short pages): what the exam asks —
   Articles, Acts and years, provisions, firsts, committees and chairs, headline numbers, definitions,
   anything tagged with an exam reference, ⚠ Trap and `> Exam angle` lines. Not trivia.
2. **For each fact**, if no MCQ already on the page tests it, pick the best candidate that does.
   A candidate qualifies only if its correct answer agrees with this page's notes (or is plainly true and
   the notes do not contradict it), it has one clear correct option, and it does not repeat an MCQ already
   on the page or another candidate you picked. A strong fact may take a second candidate from a different
   angle. Do not pick candidates for facts not on this page.
3. A fact no qualifying MCQ tests keeps `"by": []` — that is fine; do not invent MCQs.

Output `work/mcqgap/out_NNN.jsonl`, one line per page, in input order:

```
{"book":2,"row":70,"sub":4,"facts":[{"f":"16th FC constituted 31 Dec 2023","by":["P4"]},
 {"f":"14th FC used 1971 and 2011 population","by":["Q70.37"]},{"f":"local-body grants 7.91 lakh cr","by":[]}],
 "add":["P4"]}
```

`add` lists the candidates to file under this page. Check with `python3 tools/mcq_gap.py check NNN` until it
passes. Write only the output file.
