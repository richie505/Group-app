# Do the app's own MCQs ask what APPSC asks? (APPSC Complete)

Goal: every exam angle in the APPSC blueprint, and every angle APPSC has actually asked (its PYQs), must have at
least one of the app's OWN MCQs on it (ids not starting with "y"). Where one is missing, write it. Never remove or
edit an existing MCQ or PYQ, and never edit the notes.

## Your packet

`data/angle2/queue.txt` gives your packet's blueprint units. For each unit:

1. Read `data/blueprint/src/<unit>.md` from the top down to the first `# NOTES OF APP TOPIC` line: tier, PYQ counts
   and the numbered **Keywords** (each keyword is an exam angle, e.g. "Inscription -> ruler + language + script").
   The `# NOTES OF APP TOPIC b:r` lines name the app topics the unit covers.
2. For each of those topics run `python3 tools/relevance.py show <b> <r>`: the topic's notes (subsections) and all
   its MCQs. PYQs have ids starting "y"; those marked APPSC in their source are APPSC PYQs.

## Judge

- **Keyword angles.** For each keyword: is there an own MCQ that asks that angle (the relation the keyword names,
  e.g. ruler of an inscription, location of a park, Article number of a provision)? Covered / partly / missing.
- **APPSC PYQ angles.** For each APPSC PYQ in the topic: is there an own MCQ that tests the same angle (same kind of
  relation, not necessarily the same fact; a PYQ asking "author of Mudrarakshasa" is covered by own MCQs asking
  authors of other works of the same period, or the same book the other way round)? Covered / missing.
  The PYQ itself does not count: the point is practice beyond the PYQ. A PYQ with no key or a doubtful key still
  counts fully: what matters is the angle it asks and how it asks it. Only an APPSC PYQ plainly filed under the
  wrong topic (its subject is not in this topic's notes at all) is left out of the count; list it in `missing`
  as "misfiled".

- **Notes facts with no MCQ (the user's rule).** Read each topic's notes sentence by sentence. A fact that APPSC
  would ask — it fits a blueprint keyword or the angle vocabulary (first/largest, who/which/where/when, founder,
  author, title, capital, Article, Act + year, committee + chairman, scheme + objective, location, inscription,
  ranking, data point) or it is the kind of fact the topic's APPSC PYQs ask — but that no MCQ (own or PYQ) tests,
  is a gap. Fill these too. Skip trivia (minor officials, attendee counts, venue of a minor meeting, page-filler
  dates) and facts already tested.

## Write MCQs for what is missing

For each missing (or only partly covered) angle write 1-2 new MCQs, more (up to 4) for a CORE or HIGH unit when
APPSC asked the angle repeatedly:

- Facts only from the topic's notes (or solid standard knowledge that agrees with them). Never contradict the notes
  or an APPSC key recorded in them ("⚠ APPSC key").
- Do not copy a PYQ: test the same angle with another fact from the notes, or the PYQ's fact from the other
  direction.
- APPSC shapes: mostly one-liners; some "consider the following statements" (2-3 statements, options like
  "1 only / 2 only / Both 1 and 2 / Neither"), NOT-correct, match-the-pairs (3-4 pairs), assertion-reason,
  chronology, in about the APPSC mix (79% one-liner, 10% statements, 5% NOT, 4% match, 1% assertion, 1% sequence).
- Exactly 4 options, exactly one correct; plausible distractors from the same category; `a` is the 0-based index
  of the right option; `x` is a short explanation (1-2 sentences) that says why, in simple English.
- `sub` is the notes subsection number (SUB n in `show`) the fact comes from, or -1.
- Do not write an MCQ that repeats an own MCQ already in the topic.

## APPSC wording (the user's rule: our MCQs must read like APPSC's)

Frame every new MCQ the way the topic's APPSC PYQs are framed: the same kind of words, phrases and sentence
structure. Copy their framing, not their facts. Across all APPSC PYQs:

- 60% are direct questions ending in "?"; only 10% are fill-ins ending in ":". Our own MCQs are 45% fill-ins
  ("X is:", "X was founded by:", "The capital was:") — APPSC asks "Who founded X?", "Which was the capital of X?".
- Typical APPSC openers: "Which of the following …?", "Who among the following …?", "Who was the first …?",
  "In which year was/did …?", "In which of the following …?", "What is the name of …?", "Who is the author of …?",
  "Which among the following …?", "Who was the founder of …?", "Which Article of the Constitution …?",
  "Where was the first …?", "What is the full form of …?", "Consider the following statements: … Which of the
  statements given above is/are correct?", "Match the following: List-I … List-II", "Select the correct answer
  using the code given below".
- We overuse "Which one of the following …" and "Consider the following statements"; prefer the opener the
  topic's APPSC PYQs use for that angle.
- Plain, short, exam English; no "best described as", no meta-words ("APPSC asked", "according to the notes").

## Reword existing own MCQs

In each topic, also reword the stems of own MCQs (ids not starting "y") that are framed unlike APPSC — chiefly the
"…:" fill-ins and awkward or wordy stems — into APPSC wording, keeping the SAME fact, the SAME options in the same
order and the SAME answer. Only the stem changes, and the reworded stem must still fit the options exactly (e.g.
options are people -> "Who …?"; years -> "In which year …?"). Leave stems that already read like APPSC alone;
never reword a PYQ. List rewordings in `reword`.

## Output

`data/angle2/out-<packet>.json`:

```json
{"units": [{"u": "U0001", "kw_total": 13, "kw_covered": 9, "kw_partly": 2, "kw_missing": 2,
            "appsc_pyqs": 14, "appsc_covered": 11,
            "missing": ["#5 Earliest inscriptions -> script decipherer", "PYQ y… Kalhana -> Rajatarangini angle"],
            "notes_gaps": 4}],
 "reword": [{"book": 1, "id": "n…", "s": "Who among the following founded …?"}],
 "new": [{"book": 1, "row": 0, "sub": 3, "s": "…", "o": ["…", "…", "…", "…"], "a": 2, "x": "…",
          "angle": "U0001 #5 Earliest inscriptions -> decipherer"}]}
```

Check: `python3 tools/angle_add.py data/angle2/out-<packet>.json --dry` must apply all your new MCQs and rewordings
with none refused. Run ONLY with `--dry`; never apply, never commit, never edit other files. Write
`data/angle2/report-<packet>.md` (per unit: counts and what was missing); if the harness will not let you write
the report, put it in your final message.

Reply first in one line: `<packet>: keyword angles C/T covered (P partly), APPSC PYQ angles C/T covered, G notes gaps, N new MCQs, R reworded`.
