# Helper brief: complete MCQs whose options / statements were cut off

Repo /home/user/Group-app. Never use the Anthropic API. Do not commit, push or run git. Write only your own output
file. Scratch scripts only in /tmp/claude-0/-home-user/4666e051-48dd-5910-831c-f2c172f98923/scratchpad/tfN/ (read /
convert only – every completion is yours, question by question).

Input: your line range of data/truncfix_todo.jsonl. Each line: id, stem s, options o, key index a (0-based), explanation
x, src (the exam the PYQ is from), cut_options (indexes of options that look cut off), cut_stem (a statement line looks
cut off). These are mostly previous-year papers scraped from two-column PDFs: the end of a long option or statement was
lost at the line break, e.g. "He wrote a book 'Poverty and Un-British Rule in" (should end "... Rule in India'"),
"He laid the foundation of woman's education in Bom-" ("... in Bombay"), "It was imposed by the British Government
and the" ("... and the Congress was helpless").

For every line write one JSON line to your output file:
  {"id": "...", "o": [<all options, same order, cut ones completed>], "s": "<stem, only if a statement was completed>",
   "note": "<what was completed; 'original wording' or 'completed from the facts'>"}
  or {"id": "...", "ok": true, "note": "false alarm"}   (the text is complete, e.g. an option that really ends "by")
  or {"id": "...", "skip": true, "note": "<why>"}

Rules:
- Restore the ORIGINAL wording of the paper wherever you know it (these are well-known UPSC / State PSC / APPSC questions).
  Otherwise complete the cut phrase as briefly as possible so it reads as a full, natural option, using the explanation
  x, the other options and the facts (check the app notes with `python3 tools/gapfill.py find <word> ...` from the repo
  root).
- The completion must NOT change which option is correct: the keyed option stays correct, a wrong option stays wrong
  (in a NOT/incorrect question: the keyed option stays the incorrect one). Re-read the stem after completing.
- Keep the options' order and count; never touch the key. Change nothing else in the question.
- If you cannot complete an option without guessing in a way that could change the answer, "skip".

Finish: check every id of your range appears exactly once; report repaired / ok / skipped counts.
