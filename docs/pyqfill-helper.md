# Helper brief: one PYQ-fill job (Group 2 previous-year questions the app lacks)

Repo: /home/user/Group-app. Never use the Anthropic API. Do not commit, push or run git. Write only your own output
file. Keep any scripts in /tmp/claude-0/-home-user/4666e051-48dd-5910-831c-f2c172f98923/scratchpad/pqN/.

Your job file data/pyqfill/job-N.txt lists about 30 questions ("## <id> | <exam> | key: (k)") taken from OCR'd PYQ
books. The OCR is messy: two questions are often merged, options carry pieces of the next question, and the printed key
is sometimes wrong. For EVERY question decide:

- **add** – a real Group 2 question you can rebuild cleanly: the question, four options, and an answer you are sure of.
  - Rebuild the stem and options from the OCR (drop fragments of other questions, "Q75.", page furniture). Keep the
    exam's wording where it is clear; fix spelling.
  - The answer: use the printed key only when it is right. Check it against the app notes with
    `python3 tools/gapfill.py find <word> [<word> ...]` (it prints matching notes pages as "b:r:j | topic | page | text").
    When the notes or well-established facts show another option is right, use that one. If you cannot be sure, skip.
  - `x`: one or two lines that explain the answer (why it is right; a word on the others when useful). No citations.
  - `src`: the exam – "APPSC Group 2 (2011)", "APPSC Group II-B (1991)", "APPSC Group 2 (2016) – AP History",
    or "APPSC Group 2 PYQ" when the year is not known.
  - `page`: the notes page the question belongs on, from the finder ("b:r:j", e.g. "1:60:0").
- **exists** – the app already has this question (same fact, same options) – search with the finder and, if needed,
  `grep -l "<distinctive words>" app/src/group2/assets/mcq*.json`.
- **skip** (with `why`) – Mental Ability / reasoning / arithmetic (not wanted), a deleted question, OCR too broken to
  rebuild, or an answer you cannot be sure of.

Write data/pyqfill/job-N.out.jsonl, one line per question, in the job's order:

    {"id": "aph-9eaf2b971a", "d": "add", "page": "1:60:0",
     "mcq": {"s": "Which was the Roman trading station on the east coast of India?", "o": ["Arikamedu", "Motupalli",
             "Arikapally", "None of these"], "a": 0, "x": "Arikamedu (near Puducherry) was the Indo-Roman trading station ...",
             "src": "APPSC Group II-B (1991)"}}
    {"id": "...", "d": "exists"}
    {"id": "...", "d": "skip", "why": "Mental Ability"}

Then run `python3 tools/pyqfill.py check N` and fix what it reports until "problems: 0". Finish with one line:
questions, added, exists, skipped.
