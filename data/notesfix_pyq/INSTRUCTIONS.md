# Check APPSC Complete's notes against the user's "APPSC Group 2 - Topic-wise PYQ Notes"

The user's PYQ notes (Drive: latestpyqs/APPSC Group 2 - Topic-wise PYQ Notes.pdf) list facts APPSC has asked, each
with a short explanation, traps and the paper. Your extract is data/notesfix_pyq/<packet>.txt. Use it to correct and
complete the matching topics of APPSC Complete's notes (book <book>, rows given in your task).

Read a topic: `NOTES_APP=complete python3 tools/notes_fix.py show <book> <row>` (run in /home/user/Group-app).

For every PYQ point in your extract, find where the notes cover that fact and decide:
1. CONTRADICTION: the notes state a different fact (name, date, place, number, attribution). Decide what is right.
   The PYQ answer key (the point's headline) normally decides it. But if the point itself says "book key" / the key
   is plainly against the standard fact (NCERT, ASI, standard AP history texts), do not copy an error: make the
   notes give the standard fact and add "⚠ APPSC key (<year>) gave <x>" in the same bullet. Fix with the smallest
   edit, everywhere the wrong fact appears in your rows.
2. MISSING: the fact is not in the notes at all. Add it as ONE short bullet in the subsection where it belongs (the
   one whose subject it is), app style: `- **Label:** fact; key trap word **bold**` (one line, under 30 words, no
   exam names, no "PYQ" wording). Skip facts that are only trivia of another topic (put nothing) and skip points
   that are pure option-elimination with no fact.
3. COVERED: the notes already say it (in any words). Do nothing.

Write data/notesfix_pyq/ops-<packet>.json: a list of tools/notes_fix.py edits (see the docstring at the top of
tools/notes_fix.py: find/replace, after/md, append/md). Check with
`NOTES_APP=complete python3 tools/notes_fix.py apply data/notesfix_pyq/ops-<packet>.json --dry` until all ok. Never
run it without --dry. Also write data/notesfix_pyq/report-<packet>.md: a table of every CONTRADICTION (row, old,
new, why) and a count of MISSING added and COVERED. Edit no other file; do not commit.
Reply only: "<packet>: <c> contradictions fixed, <m> facts added, <k> already covered".
