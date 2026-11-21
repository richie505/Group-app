# Helper brief: one gap-fill job

Facts in the source library (NextGen, Rocket Sheets, CARE, PMF, standard books) that the app notes may lack.
Repo: /home/user/Group-app. Never use the Anthropic API. Do not commit, push or run git. Write only your own output file.
Keep any scripts in /tmp/claude-0/-home-user/4666e051-48dd-5910-831c-f2c172f98923/scratchpad/gfN/.

Your job file data/gapfill/job-N.txt lists terms ("## term:"), each with its subject and one or two source passages.
For EVERY term decide:
- **exists** – the notes already have this fact. Check with `python3 tools/gapfill.py find <word> [<word> ...]`
  (try other spellings: Qutub/Qutb, Raya/Rayalu, Krishnadeva/Krishnadevaraya, Pulumavi/Pulamavi ...).
- **skip** – nothing to add: OCR noise or a word fragment ("Septem", "Inthis"), page furniture (book titles, publisher,
  "Download", "Moreover"), a common word, or a fact no APPSC Group 1 Prelims / Group 2 paper would ask (pure trivia far
  from the syllabus).
- **add** – a real, exam-worthy fact the notes lack. Write ONE crisp line in the Rocket-sheet style, using ONLY what
  the source passage says (no outside knowledge; if the passage is unclear, skip): "**Term:** fact, with **key words**
  bold". No citations, no "asked", no exam names. Choose the notes page it belongs on with the finder (its id "b:r:j"
  – book:row:page of APPSC Complete). Add an MCQ only when the fact is clearly exam-worthy: APPSC style, one question,
  four options, the answer index 0-3, and a one-line explanation x.

Write data/gapfill/job-N.out.jsonl, one line per term, in the job's order:
  {"term": "...", "d": "exists"}   {"term": "...", "d": "skip", "why": "OCR fragment"}
  {"term": "...", "d": "add", "page": "1:62:3", "line": "**Raavi Narayana Reddy:** ...",
   "mcq": {"s": "...", "o": ["...", "...", "...", "..."], "a": 2, "x": "..."}}   (mcq optional)

Then run `python3 tools/gapfill.py check N` and fix what it reports until "problems: 0". Finish with one line:
terms, added, exists, skipped, MCQs.
