# Placement check: is each PYQ filed under the right topic and subsection?

Read data/pyq/refile/in/<packet>.md. It lists PYQs grouped by the topic they are filed under now ("## TOPIC b:r Title",
with that topic's subsections "k:Name"). Each line: id, [sub k] = current subsection, (exam), question → correct answer.

For each PYQ ask: would a student studying THIS topic and THIS subsection expect this question here?
- Yes → leave it out of the output.
- Wrong subsection of the same topic → give the right one: "b:r:k".
- Wrong topic → find the right topic and subsection in data/pyq/arihant/topics.txt (lines "b:r Topic :: k:subsection |
  ..."; grep it by keyword) and give "b:r:k". Pick the most specific fit. Examples: a question on Arjuna Awards 2022 →
  the awards / sports topic in book 6 (grep "Award", "Sports"); a GST question → the GST topic in book 3; a cell-biology
  question → a biology/biotech topic in book 5 if one fits, else 5:1 (Relevance of S&T to Day-to-day Life: 5:1:3 Human
  Body, 5:1:2 Nutrition, 5:1:6 Household Chemicals, 5:1:1 Food Technology, 5:1:10 Quick Revision).
- Pure reasoning / mental ability / arithmetic (syllogisms, series, coding, directions, blood relations, clocks,
  calendars, number puzzles) → "drop". Do NOT drop a GS question just because it is hard or old.
Only move when clearly better; when in doubt leave it. Never move to a subsection index that does not exist.

Write only data/pyq/refile/out/<packet>.json: a JSON object of the PYQs to change, e.g.
{"y267e0134356": "6:96:3", "yabc123def45": "4:10:2", "y0123456789a": "drop"}
(an empty {} if every PYQ is well placed). Validate: python3 -c "import json;json.load(open('<file>'))".
Edit nothing else, run no git. Reply with one line: "<packet>: N checked, moved M, dropped D".
