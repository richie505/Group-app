# Rewrite app MCQs into APPSC question shapes

You rewrite MCQs of an APPSC (Andhra Pradesh Public Service Commission) Group 1 / Group 2 prelims prep app so that the
app asks questions the way APPSC does. The app's MCQs lean on UPSC-style "consider the following statements" sets;
real APPSC papers are mostly direct single-fact questions. Only write the output JSON file you are told to; edit nothing else.

Each line of your packet: `[id] TARGET: <shape> | NOW: <shape> | stem || (1) .. / (2) .. / (3) .. / (4) .. || ANS n || WHY: ...`
(ANS is 1-based). Keep the SAME facts and the same topic - you only change the form. Never invent facts; use only what
the question, its options, its answer and its WHY establish (plus completely standard facts).

STRICT FACT RULE (most important): build every new question only from facts the original CONFIRMS - a statement the key
marks as true, the keyed option itself, or a fact stated in WHY. A statement the key marks as false tells you only that
it is false; do NOT "correct" it from memory into a new fact (e.g. if "Kushana trade ran through the Black Sea" is false,
you may NOT make "Red Sea" the answer unless WHY says so). False statements may be reused only as the false option of a
NOT question or as decoys. If nothing confirmed is left to ask, rewrite the question as a NOT question or a 2-statement set
from the original's own statements.

TARGET shapes (APPSC style):
- one-liner: one direct question about the most exam-worthy fact in the original ("Who ...?", "Which ...?", "In which year
  ...?", "Where ...?", "... is known as:", or a fill-in-the-blank with ____). Short stem (ideally under 25 words).
  Four options of the same kind (four names, four years, four places...). Decoys must be plausible and wrong: change one
  detail of the key (a neighbouring ruler, the next year, a nearby place), never jokes or obviously absurd options.
- NOT: "Which of the following is NOT correct about <X>?" (or "... is INCORRECT", "... is wrongly matched") with four
  short one-line statements as options - three true, one false (the false one is the key). Build them from the original's
  true and false statements.
- statements: 2 or 3 short numbered statements, then "Which of the above statement(s) is/are correct?" with codes like
  "1 only / 2 only / Both 1 and 2 / Neither 1 nor 2" (2 statements) or "1 and 2 only / 2 and 3 only / 1 and 3 only /
  1, 2 and 3" (3 statements). Never 4 or more statements.
- assertion: "Assertion (A): ... Reason (R): ..." with the four standard options in this order:
  "Both A and R are true and R is the correct explanation of A" / "Both A and R are true but R is not the correct
  explanation of A" / "A is true but R is false" / "A is false but R is true".
- match: "Which of the following pairs is correctly matched?" (or "INCORRECTLY matched") with four "X – Y" pairs as the
  options. Do not use A-1/B-2 code grids.
- sequence: "Arrange in chronological order:" with 3-4 items and four order codes, only when the facts carry clear dates;
  if they do not, write a one-liner instead.

If the TARGET shape cannot be built honestly from the facts given, use the nearest shape that can (usually one-liner) and
say so in "shape". Keep stems free of "Select the correct answer using the code given below" boilerplate except where a
code is genuinely needed.

Write the final `data/reshape/out/<n>.json` (put any partial files in your scratch folder, never in data/reshape/out) (same number as your packet): a JSON object
{"<id>": {"shape": "<shape you wrote>", "s": "stem (use \n between numbered statements)", "o": ["..","..","..",".."],
"a": <0-based index of the key>, "x": "1-2 sentences: why the key is right (and for NOT: why that statement is false)"}, ...}
Every id in the packet must appear. Spread the key across positions 1-4 rather than always the same slot.
Validate with: python3 -c "import json;json.load(open('<file>'))". Large packets: read in chunks and write the output in
parts, merging into one valid JSON object at the end. Reply at the end with only the count written per shape.

## TARGET: restyle (keep the shape)
Some packets ask you to restyle MCQs without changing their shape. For each:
- If it already reads like an APPSC question (short, one clear fact, four plausible same-kind options, no UPSC
  boilerplate), write only {"<id>": {"same": true}} - do not rewrite it for the sake of it.
- Otherwise rewrite it in the same shape the APPSC way: shorten the stem, cut "Select the correct answer using the code
  given below" style boilerplate, make the decoys plausible near-misses of the same kind, keep the same fact and key, and
  give the usual {"shape", "s", "o", "a", "x"}. A statement set must keep at most 3 statements.

## Working files
If you need scratch files, put them ONLY in /tmp/claude-0/-home-user-Group-app/9d62697f-c2bc-5d71-9828-630e63a36f4a/scratchpad/reshape-<packet number>/
(other rewriters run at the same time; never use or touch a shared folder or another packet's files).
