# Reading the 2026 OCR "previous bits" books into the PYQ bank

Source: Drive folder "OCR Output" (six books scanned and OCR'd on 10 Nov 2026): `ap-history`, `polity`,
`economy`, `science-tech`, `history-geography-dm` (Indian history, world geography, disaster management) and
`adobe-scan` (Indian geography and more). Each book is a set of previous papers: a header names the exam and year
(e.g. "APPSC GROUP-II - 2012", "APSLPRB SUB-INSPECTOR FINAL WRITTEN EXAM - 2023", "TSPSC JUNIOR LECTURERS - 2023"),
its questions follow, numbered, each with four options "1. … 2. … 3. … 4. …", and an "ANSWERS" grid closes the
paper: "1.1 2.4 3.1 4.4 …" = question 1 → option 1, question 2 → option 4, …

You get one chunk: `data/pyq/ocr2026/chunks/<chunk>.txt` (12 pages; after the line "LOOKAHEAD" come the next 3 pages,
which you use ONLY to find the answer grid of questions in your 12 pages). Write
`data/pyq/ocr2026/out/<chunk>.jsonl`, one JSON object per line. Edit nothing else; do not commit.

## One line per question

{"id": "ocr26-<chunk>-<page>-<n>", "exam": "<exam and year as the header names it, tidied, e.g. APPSC Group-II 2012,
APSLPRB SI 2023, TSPSC Junior Lecturers 2023>", "year": "<year>", "book": "<book>", "page": <page>, "n": <question number
in its paper, or your best reading>, "s": "<stem>", "o": ["<opt1>", "<opt2>", "<opt3>", "<opt4>"], "a": <0-based key or -1>,
"x": "", "src": "OCR 2026 <book>"}

## Reading rules

- OCR noise to undo: "G)" / "@" / "(1)" for option 1; "1.1, 0, Wl, IV" for "I, II, III, IV"; options of two columns
  read across ("1. Mumbai\n3. Chennai\n\n2. Visakhapatnam\n4. Kolkata" = options 1-4 in number order); hyphenated
  line breaks ("talu-\nka" = "taluka"); a lost question number before ". The father of …". Fix only such noise; never
  change a fact, a name or a number you cannot read with certainty.
- Answer grids are OCR'd badly: "92 103 113 124 13.1" = 9.2 10.3 11.3 12.4 13.1; "184 191" = 18.4 19.1; a mark like
  "2,)" or "(3)" or a tick printed by an option in the question itself may also show the key. Map a key only when the
  question number and the option are certain; otherwise a = -1. A grid belongs to the paper above it: match numbers
  within that paper only.
- Keep: general studies questions (history, AP history, polity, economy, geography, science and technology,
  environment, disaster management, current affairs). Skip: mental ability, reasoning, maths, English, Telugu,
  questions of a technical subject paper, and any question whose stem or any option you cannot read.
- Statements, List-I/List-II and assertion/reason: keep their lines ("1. …\n2. …", "A. … B. …", "List-I … List-II …")
  in the stem, and the codes as the four options.
- English only. Never invent a question, an option or a key.
- Questions that start on your 12 pages are yours; a question that starts in the LOOKAHEAD belongs to the next chunk.

Reply with one line: "<chunk>: <n> questions written (<k> with key), <m> skipped (<why>)".
