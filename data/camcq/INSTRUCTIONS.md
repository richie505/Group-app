# MCQs for the new current affairs (APPSC Group 1 / Group 2 prelims)

Your packet (data/camcq/in/<topic>.md) lists the new current-affairs items of one topic, numbered [1], [2], ...
Write MCQs on them, the way APPSC asks, into data/camcq/out/<topic>.json. Edit nothing else; do not commit.

## How many
- About **2 MCQs per item** (1 for a thin item, 3 for a rich one with many testable facts). Every item gets at least one.
- One MCQ may combine 2-3 items of the same kind (e.g. a match of four schemes, or a statement set on three
  appointments): give all their numbers in "item".

## Facts
- Use **only the facts the packet states**. Never add a fact from memory; never "correct" the packet.
- Test what APPSC tests: who / what / where / when (dates, places, ministries, numbers, firsts, ranks, headquarters,
  the related Article, Act or scheme the item names, the static facts the item gives).
- Decoys must be plausible near-misses of the same kind (a neighbouring State, the next year, a related ministry, a
  similar scheme name), never jokes. A decoy must be certainly wrong from the packet's facts.

## Shapes (mix them; about 40% one-liner)
- **one-liner**: a short direct question (under 25 words), four options of the same kind.
- **NOT**: "Which of the following is NOT correct about <X>?" with four short one-line statements, three true, one false.
- **statements**: 2 or 3 numbered statements, each on its own line ("1. ...\n2. ..."), then "Which of the statements
  given above is/are correct?" with codes: 2 statements "1 only / 2 only / Both 1 and 2 / Neither 1 nor 2";
  3 statements "1 and 2 only / 2 and 3 only / 1 and 3 only / 1, 2 and 3". Make some statements false by changing one
  detail (number, place, date, ministry).
- **match**: "Which of the following pairs is correctly matched?" (or "INCORRECTLY matched") with four "X – Y" pairs
  as the options.
- **assertion**: "Assertion (A): ...\nReason (R): ..." with the four standard options in this order: "Both A and R
  are true and R is the correct explanation of A" / "Both A and R are true but R is not the correct explanation of A" /
  "A is true but R is false" / "A is false but R is true". Only when the packet gives a real cause-effect.
- **sequence**: "Arrange in chronological order:" with 3-4 dated items and four order codes. Only with clear dates.

Spread the key over positions 1-4. Stems must stand alone: name the State, body or event (no "this scheme", no
"the packet", no "the notes", no "item 3"). Do not mention any source. Write plain, simple English.

## Output
A JSON list:
`[{"item": 3, "shape": "one-liner", "s": "stem (\n between numbered lines)", "o": ["..", "..", "..", ".."], "a": <0-based key>,
"x": "1-2 sentences: why the key is right, and for NOT or false statements what is wrong"}, ...]`
("item" may be a list of numbers.) Then run `python3 tools/ca_mcq.py check <topic>` and fix until problems 0.
Reply with only the checker line.
