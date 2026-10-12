# MCQ rescue: re-file good MCQs that sat under the wrong topic

These MCQs were dropped because their own topic's notes do not hold their fact. Each is shown with
three candidate subsections from other topics (only their most relevant notes lines).

For each MCQ decide:
- **Move** it to a candidate (`"to": "r.s"`, the candidate's number exactly as shown) only if that
  subsection's notes clearly state the fact the MCQ tests AND the MCQ's keyed answer is right by those
  notes (in a statement question, every statement's truth must follow from them).
- **Leave it dropped** (`"to": null`) if no candidate states the fact, the key is wrong or doubtful,
  the options are broken, or it is trivia (one-off figures, single-event counts, exact crore amounts).

Be strict: a candidate that only shares a few words is not a match.

Write rescue_out_NNN.jsonl (one line per MCQ, in input order):
```
{"q":"Q19.60","to":"20.3"}
{"q":"Q19.62","to":null}
```
Every label in the input must appear exactly once. Write only that file.
