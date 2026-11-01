# Clean and check AP History previous-paper questions

These are APPSC-style previous-year questions on Andhra Pradesh history and culture, read by OCR from a scanned book
(RRR Publications, "AP History Previous Papers"). The OCR left debris: exam tags glued to options ("GROUP-1-1994",
"DL-2011 OPTIONAL"), stray letters at the end of an option ("Dinabandhu A"), question numbers and fragments of the
neighbouring question run into the stem ("With Whom did the Rashtrakutas fight 21. Th to capture Kanauj?"), and
sometimes options that belong to another question. Edit only the JSON file you are told to write.

For every question in your input file, decide:
- keep: true if it can be shown as a clean 4-option MCQ (after you repair the text); false if it is unrecoverable
  (stem is mostly fragments, options belong to another question, fewer than 4 real options).
- s: the repaired stem - remove debris, fix obvious OCR spelling, keep the original wording and meaning. If the
  question lists statements / pairs, put each on its own line ("\n").
- o: exactly 4 repaired options, in the original order (do not reorder).
- a: the 0-based index of the correct option. Start from BOOK ANSWER (1-based in the input; "none" = no key). Keep the
  book's answer when it is right. If you are confident from well-established AP history it is wrong, give the right
  index and set "key": "corrected: <short reason>". If the book has no answer and you know it confidently, give it with
  "key": "supplied"; if not confident, a = -1.
- x: one or two crisp sentences explaining the answer (use the BOOK EXPLANATION where it fits); may be empty.

Write a JSON object to the output file: {"<id>": {"keep": true, "s": "...", "o": ["...","...","...","..."], "a": 0, "x": "...", "key": "..."}, "<id>": {"keep": false, "why": "..."}, ...}
Every id in your input must appear. Validate with: python3 -c "import json;json.load(open('<file>'))".
Reply at the end with only: kept / dropped / answers corrected / answers supplied.
