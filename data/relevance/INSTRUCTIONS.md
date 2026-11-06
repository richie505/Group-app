# Exam-relevance audit: APPSC Complete (Group 2 is built from it)

Goal: everything a student reads or practises in a topic is worth marks in APPSC Group 1 / Group 2 (Prelims and
Mains objective papers). Remove what is not; fix what is wrong. Be conservative: only clear cases. Your packet lists
book:row topics. For each: `python3 tools/relevance.py show <book> <row>` (in /home/user/Group-app).

NOTES - remove (or trim) a block only if it is clearly one of:
  a. outside the topic and the APPSC syllabus (stray content from another subject, generic filler, study advice);
  b. trivia with no exam angle (e.g. page/serial numbers, minor names inside long lists that no paper would ask,
     repeated restatement of the same fact in the same subsection);
  c. a duplicate of another block in the same topic (keep the clearer one);
  d. plainly outdated "current" data superseded inside the same notes (keep the newer).
  Never remove: anything with "⚠ APPSC key", PYQ-tested facts, tables of core data, traps, definitions.
  Edits: data/relevance/ops-<packet>.json in tools/notes_fix.py format ({"book","row","sec","block": "<anchor text
  unique in that subsection>","md": ""} deletes a block; "find"/"replace" trims text). Check with
  `NOTES_APP=complete python3 tools/notes_fix.py apply data/relevance/ops-<packet>.json --dry` until all ok.

MCQs (own MCQs only; ids starting "y" are real PYQs - never list them) - drop only if clearly:
  1. not about the topic's syllabus content, or testing trivia no APPSC paper would ask;
  2. a near-duplicate of another MCQ in the same topic (same fact, same angle) - keep the better one;
  3. wrong or ambiguous key / two correct options / no correct option and not fixable by you with certainty;
  4. outdated: a "current" fact that the notes themselves show is superseded.
  Write data/relevance/drops-<packet>.json: {"drop": [{"book": 1, "id": "n...", "why": "short reason"}]} and check
  with `python3 tools/relevance.py drop data/relevance/drops-<packet>.json --dry`.

Write data/relevance/report-<packet>.md: per topic, counts (notes blocks removed/trimmed, MCQs dropped by reason)
and 3-5 examples. Do not run anything without --dry; touch no other file; do not commit. Reply only:
"<packet>: notes -<n> blocks, MCQs -<m> of <total> (<reasons>)".

PYQs (ids "y..."): never in drops. But list clear problems in data/relevance/pyq-<packet>.json:
{"exclude": [{"id": "y...", "why": "wrong key: <key> but standard fact is <x>" | "off-syllabus: <what>"}]}
Only (a) a key that is plainly wrong against the standard fact (not a disputed one; not one the notes record with
"⚠ APPSC key"), or (b) a question outside the APPSC GS syllabus altogether (pure trivia of an unrelated field). A PYQ
that is relevant but filed under the wrong topic: leave it. These are taken out of the apps by the lead.
