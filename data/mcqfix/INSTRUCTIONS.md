# MCQs to the latest APPSC pattern, every exam angle asked

Your packet (data/mcqfix/in/<packet>.md) has up to 3 topics of the APPSC Complete app. For each topic it gives the
notes file, the exam angles (the numbered **Keywords** of data/blueprint/src/<unit>.md; the notes' last
`COVERAGE:` line says which sections cover each angle), and the topic's MCQs listed under the section (page) they sit
on. Write data/mcqfix/out/<packet>.json. Edit nothing else; do not commit.

The latest APPSC papers (2023-25) are about 79% direct one-liners, 10% statement sets (2-3 statements), 5% NOT,
4% match, 1% assertion-reason, 1% sequence.

## Three jobs

1. **RESHAPE** (listed under `### RESHAPE`): rewrite each MCQ into the TARGET shape, following the rules of
   data/reshape/INSTRUCTIONS.md (read its first part: shapes and the STRICT FACT RULE). Same facts, same topic.
2. **CUT** (listed under `### CUT`): statement sets with 4+ statements: rewrite with at most 3 statements (a
   "statements" MCQ of 2-3, or a one-liner), keeping the same facts.
3. **NEW**: read the topic's notes and its exam angles. Write new MCQs so that
   - every exam angle (keyword) is asked by **at least 2 MCQs** in total (existing + new; judge from the stems listed),
     covering the sub-points the keyword names (e.g. "Article 72, forms, nature" -> forms and nature both asked);
   - every numbered section (page) has **at least 2 MCQs**, except the last three (Number Game, PYQs, Traps), whose
     facts are asked through the sections they belong to;
   - the facts the notes mark as exam traps (`TRAP`, `Don't confuse`, `KEY`, numbers in the Number Game) are asked.
   Do not repeat a fact an existing MCQ already asks the same way. Mostly **one-liners** (about 4 in 5), the rest NOT,
   2-3-statement sets or match, as APPSC does.

## Rules for new MCQs
- Facts **only from the notes** of the topic. Never from memory. A decoy must be certainly wrong by the notes.
- APPSC style: short direct stems (under 25 words), four options of the same kind (four Articles, four years, four
  names), plausible near-miss decoys (the neighbouring Article, the next amendment, a similar body). No "Select the
  correct answer using the code given below", no "all of the above", no "the notes", no sources.
- Statement sets open with what they are about: "Consider the following statements about <X>:\n1. ...\n2. ...\n3. ..." then "Which of the statements given above is/are correct?" with the
  standard codes ("1 and 2 only / 2 and 3 only / 1 and 3 only / 1, 2 and 3", or for 2: "1 only / 2 only / Both 1 and 2
  / Neither 1 nor 2").
- Spread keys over positions 1-4. Explanations: 1-2 plain sentences (why the key is right; what is wrong in a false one).

## Output: one JSON object
```
{"reshape": {"<id>": {"shape": "...", "s": "...", "o": ["..","..","..",".."], "a": 0, "x": "..."}, ...},
 "new": [{"topic": <topic number>, "sec": <section number, 1-based>, "angle": "<keyword number(s), e.g. 2 or 2,5>",
          "shape": "one-liner", "s": "...", "o": [...], "a": 0, "x": "..."}, ...]}
```
Every RESHAPE and CUT id must be in "reshape" (write {"same": true} only if it already fits). Large packets: build the
file in parts in /tmp/claude-0/-home-user-Group-app/9d62697f-c2bc-5d71-9828-630e63a36f4a/scratchpad/mcqfix-<packet>/ and merge into one valid
JSON object. Then run `python3 tools/mcq_fix.py check <packet>` and fix until problems 0.
Reply with only the checker line.
