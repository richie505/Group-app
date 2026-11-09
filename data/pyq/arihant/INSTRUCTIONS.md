# Checking Arihant PYQs before they go into APPSC Complete

You check one packet of previous-year questions (PYQs) read from the Arihant "14000+ Objective General Studies" book.
Each question shows its exam tag, the topic and subsection the app would file it under (FILED: book · topic › subsection),
the question, four options and the book's KEY (1-based). Read data/pyq/arihant/in/<packet>.md. Edit nothing else;
write only data/pyq/arihant/out/<packet>.json; do not commit.

For EVERY question decide one of:
- "ok": text readable, key correct, filed under a sensible topic and subsection.
- "key": the book's key is wrong and you are SURE of the right option (a well-established fact). Give the new key.
  If unsure, leave it "ok" (do not change keys on a hunch). Facts that changed later (a "current" office holder, the
  largest/latest X then): keep the key that was right when the exam was set, and say so in "note".
- "fix": the text has a PDF slip you can repair with certainty (words run together, a stray page header, a broken
  word, a missing "List I/List II" line break). Give the full corrected "s" and/or all 4 "o". Never change meaning.
- "drop": garbled beyond repair, options belong to another question, mental ability / arithmetic / reasoning /
  English, a question that needs a picture/map, or a question whose every option is now wrong or unanswerable.
- "move": the question is fine but belongs to another topic/subsection. Find the right one in
  data/pyq/arihant/topics.txt (lines "b:r Topic :: k:subsection | ..."; grep it) and give "to": "b:r:k".
  Also use "move" when FILED shows subsection "-" and a subsection of the same topic fits.
  A question may need both a key change and a move: give "key" plus "to".

Output, JSON object keyed by question id:
{"arihant-p1-7-142": {"v": "ok"},
 "arihant-p2-3-9": {"v": "key", "a": 3, "note": "Statue of Unity is in Gujarat"},
 "arihant-p1-2-81": {"v": "move", "to": "1:2:3"},
 "arihant-p3-5-1": {"v": "fix", "s": "...", "o": ["...","...","...","..."]},
 "arihant-p3-5-2": {"v": "drop", "note": "needs a map"}}
"a" is 1-based. Every id in the packet must appear exactly once. Validate: python3 -c "import json;json.load(open('<file>'))".
Reply with one line: "<packet>: N checked, ok X, key Y, fix Z, move M, drop D".

## Keep every GS question (user: "fill them all")
Never drop a question only because no topic fits exactly. File it under the NEAREST topic instead:
- general physics, chemistry, biology, human body, everyday science → a 5:1 subsection (5:1:3 Human Body,
  5:1:2 Nutrition and Vitamins, 5:1:6 Household Chemicals, 5:1:1 Food Technology), else 5:1:10 Number Game and Quick Revision;
- world history (revolutions, world wars, civilisations) → the nearest history/world topic in topics.txt
  (e.g. 1:150 Age of Discovery, a freedom-struggle topic for the world wars, or an international-relations topic in book 6);
- another state's GK, general misc GK → the nearest Indian geography/culture/static GK topic.
Drop only: garbled beyond repair, mental ability/arithmetic/reasoning/English, physics/maths numericals that need
calculation, a picture/map question, or no option correct.
