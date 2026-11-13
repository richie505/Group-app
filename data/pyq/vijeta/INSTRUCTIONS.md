# Reading the Vijeta Competitions "Previous Papers" scans into the PYQ bank

Source: Drive folder "new pyqs from 128 papers": four Adobe scans (A, B, C, D; 947 pages) of a Vijeta Competitions
previous-papers book: APPSC and other AP/Telangana recruitment papers, many of 2024-2026. A paper starts with a header
(post, "PAPER", "Held on: <date>"), its questions are numbered, each with four options "1. … 2. … 3. … 4. …", and an
"answers" grid follows ("14 23 33 43 53" = Q1 → option 4, Q2 → 3, …; OCR often drops the dot or reads 3 as 8 or 9).

You get one chunk: `data/pyq/vijeta/chunks/<chunk>.txt`: 12 pages of `pdftotext -layout` text, then a LOOKAHEAD of the
next 3 pages, used ONLY for answer grids of questions on your 12 pages. The pages are printed in TWO COLUMNS shown side
by side on the same lines: read the whole left column of a page first, then the right column. Each page header names
its scanned PDF and page (e.g. `PDF: data/pyq/vijeta/pdf/C-01.pdf, page 7`): whenever the text is unclear (columns
mixed, a number or word lost, an answer grid you cannot read), look at that page image with the Read tool
(`Read file_path=/home/user/Group-app/data/pyq/vijeta/pdf/C-01.pdf pages="7"`) and read it from the image.

Write `data/pyq/vijeta/out/<chunk>.jsonl`, one JSON object per line (json.dumps from a short Python script). Edit
nothing else; do not commit.

## One line per question

{"id": "vj-<chunk>-<page>-<n>", "exam": "<post and year as the header names it, tidied, e.g. APPSC Group-II Mains
Paper-I 2025, APPSC Forest Beat Officer 2025>", "year": "<year the paper was held>", "book": "vijeta-<scan>",
"page": <page>, "n": <question number in its paper>, "s": "<stem>", "o": ["<opt1>", "<opt2>", "<opt3>", "<opt4>"],
"a": <0-based key or -1>, "x": "", "src": "Vijeta previous papers"}

## Rules (owner's)

- KEEP EVERY QUESTION, whatever the subject (general studies, current affairs, AP topics, science, subject papers),
  EXCEPT MENTAL ABILITY AND REASONING (series, coding-decoding, blood relations, directions, seating, ranking in a row,
  syllogism, analogies, puzzles, clocks/calendars, arithmetic/aptitude sums, data interpretation). Leave those out.
- 5-option questions: keep all five options ("a" 0-4).
- One-liners (question + printed answer, no options): keep as flashcards in `out/<chunk>-oneliners.jsonl`:
  {"id": "vj-<chunk>-<page>-<n>-f", …, "s": "<question>", "k": "f", "at": "<printed answer>", "o": ["Knew it",
  "Did not know"], "a": 0, …}. Never invent options.
- Use the page image whenever the text is unclear. If a stem or option still cannot be read with certainty, write the
  question with your best reading, "[?]" where text is lost, "a": -1 unless the key is certain, and "unclear": 1.
- Keys: from the paper's answer grid (or a tick printed on the page). Map a key only when the question number and the
  option are certain; if a clearly read key contradicts a well-established fact, set -1. Never guess a key.
- Statements, List-I/List-II, assertion/reason: keep their lines in the stem ("A: …\nR: …", "I. …\nII. …").
- English only. Never invent a question, an option or a key. Questions that start in the LOOKAHEAD belong to the
  next chunk. Ids must be unique in your file (add b/c when two papers share a page and number).

Validate every file with Python (each line parses, unique ids, 4 or 5 non-empty options or a flashcard, a in range).
Reply with one line per chunk: "<chunk>: <n> written (<k> with key, <u> unclear), <f> one-liners, <m> mental
ability/reasoning left out".
