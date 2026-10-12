# MCQ trim: fewer, stronger MCQs that match the notes

The learner has 90 days for all notes and all MCQs. Loose, repetitive MCQs eat that time. Your job: for
each topic, keep the MCQs that test what the notes teach, once each, in the strongest form.

## Input (in_NNN.md)

Each topic starts with `=== ROW r | title`. Each subsection `## SUB k | title` shows its notes, then the
MCQs filed under it, labelled `[Q<row>.<n>]` with options A–D, ANSWER and WHY. `SUB -1` holds MCQs
filed under the whole topic.

## Decide every MCQ (exactly one decision per label)

1. **Off the notes → drop (`off`).** The fact the MCQ tests (its correct answer, and in statement
   questions each statement's truth) must be found in this topic's notes. If it is in another
   subsection of the same topic, keep it and move it (`"sub": k`). If it is nowhere in this topic's
   notes, drop it.
2. **Repeat → drop (`dup`).** Two MCQs testing the same fact (same answer fact, reworded stem, the same
   statement set reshuffled, the reverse question "X is associated with?" / "Y is associated with?").
   Keep the better one (clearer, tests understanding, has traps like the exam) and drop the other,
   naming it: `"why": "dup Q0.28"`.
3. **Trivia → drop (`trivia`).** Facts the exam does not ask and a learner should not memorise:
   one-off district/bench figures, crop-wise or scheme-wise percentages for a single season, exact
   crore amounts of a single event, decimal statistics nobody quotes, frequencies/measurements to 4+
   digits, meeting dates of minor bodies, counts like "how many ULBs set up PMUs". Keep headline numbers
   the exam does ask (Articles, years of Acts, firsts, founders, GDP growth, budget size, major
   targets like 500 GW).
4. **Merge (`merge`).** When 2–3 kept MCQs test closely linked single facts of one subsection, you may
   replace them with ONE better MCQ (usually "Consider the following statements" or a match list) that
   covers all their facts. Make some statements false (change one detail the notes contradict), so the
   answer is not always "all of the above"; the right answer must follow from the notes.
5. **Keep (`keep`).** Everything else that is on the notes and worth testing.

Be firm: most topics should end with roughly **55–70%** of their MCQs (count a merge as one). Keep at
least 3 per subsection that has notes, if that many on-note MCQs exist. Never invent facts; merged
MCQs use only facts stated in the notes. Do not edit kept MCQs.

Statement MCQs whose answer is "all are correct": these are over-used (two in three). When choosing
between repeats, prefer the one whose answer is not "all correct".

## Output (out_NNN.jsonl): one JSON object per line, in the order of the input

```
{"q":"Q0.28","d":"keep"}
{"q":"Q0.29","d":"keep","sub":2}
{"q":"Q0.30","d":"drop","why":"dup Q0.28"}
{"q":"Q0.31","d":"drop","why":"trivia"}
{"q":"Q0.32","d":"drop","why":"off"}
{"d":"merge","from":["Q0.33","Q0.35"],"sub":0,"s":"Consider the following statements about ...:\n1. ...\n2. ...\nWhich of the statements given above is/are correct?","o":["1 only","2 only","Both 1 and 2","Neither 1 nor 2"],"a":0,"x":"Statement 1 is correct: ... Statement 2 is wrong: ...","tq":"short tip on how to crack it"}
```

- `q` labels exactly as given; `sub` is the subsection number (k) in the same topic, or -1.
- A merge's `from` labels get no other line. Exactly 4 options, `a` is 0–3, `x` explains every option.
- Write only the JSONL file (use the Write tool), nothing else; then check it:
  `python3 tools/mcq_trim_check.py <book> <NNN>` and fix anything it reports.
