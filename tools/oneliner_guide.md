# Rewriting MCQs as one-liners (APPSC One-liners)

You get `work/oneliner/b<book>/in_NNN.md`: MCQs that are not one-liners (statement sets, pairs, match lists,
assertion-reason, "how many", order, "which is NOT"). Each has its key ("Answer:") and "Facts:" (its explanation).
Rewrite every MCQ as **one-liner MCQs, one per fact it tests**, into `work/oneliner/b<book>/out_NNN.jsonl`:
one JSON object per line, in input order:

    {"q": "<the MCQ's id>", "s": "<question>", "o": ["<opt>", "<opt>", "<opt>", "<opt>"], "a": <0-3>}

## What a one-liner is
- **One question, one line**, testing **one fact**: "Who wrote the Mahabhashya?", "The Saka era began in which year?",
  "Which Act created the post of Governor-General of Bengal?". Up to ~150 characters. No line breaks.
- **Four short options** (up to ~60 characters each), all of the same kind (four names, four years, four places),
  all different, exactly one right. Wrong options must be plausible (same field, same period), never silly.
- Never: "Which of the following statements…", "Consider…", statement numbers, "1 and 2 only", "Both", "Neither",
  "All/None of the above", "Only two", "a-iii", assertion/reason, "NOT/incorrect" questions. Ask positively.
- Plain text; no markdown, no "(1)" labels inside options.

## Which facts, and getting them right
- Take the facts **the MCQ itself tests**: each statement, each pair of a match list or pair set, A and R of an
  assertion-reason, each item of an order question (its date, or "which of these came first"). Usually 1-4
  one-liners per MCQ. Don't make one-liners from the extra background in "Facts:" that the MCQ doesn't test.
- **Follow the key.** A statement the key makes wrong is false: never use its wrong version as a right answer. Use
  the corrected fact from "Facts:" (e.g. "its river was the Krishna, not the Godavari" -> "According to P. C. Ray,
  the river of Andhranagari was?" with Krishna right, Godavari as a distractor). If the correct version isn't in the
  MCQ or "Facts:", leave that statement out.
- Don't add facts from outside the MCQ and its "Facts:". Distractors may be other names/years of the same kind.
- Two statements that give the same fact make one one-liner, not two.
- If nothing in an MCQ can be made a sound one-liner, write `{"q": "<id>", "skip": "<why, a few words>"}` (rare).

## Check
Run `python3 tools/oneliner_check.py <book> <NNN>` and fix what it reports until it passes.
