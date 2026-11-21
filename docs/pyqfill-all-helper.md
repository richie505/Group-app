# Helper brief: one job of other exams' PYQs for the Group 2 app

Goal: the Group 2 app should hold every previous-year question (from UPSC, APPSC's other exams, APPSC Group 1, state
PSCs) that a line of the official Group 2 syllabus covers. Repo: /home/user/Group-app. Never use the Anthropic API.
Do not commit, push or run git. Write only your own output file. Scripts only in
/tmp/claude-0/-home-user/4666e051-48dd-5910-831c-f2c172f98923/scratchpad/pqaN/.

Read data/g2syl/leaves.md first: the official APPSC Group 2 syllabus (27-04-2023) as leaves, P* = Prelims/Screening,
M* = Mains. Mental Ability is not wanted.

Your job file data/pyqfill/all/job-N.txt lists about 50 questions ("## <id> | <exam> | key: (k)", the question, four
options, an explanation). For EVERY question decide one of:

- **beyond** – no Group 2 line covers it. Judge fairly, not narrowly: it FITS when a Group 2 Screening or Mains
  question could fairly be set from it under a leaf (the line's topic, background, causes, features, people, places,
  related facts). Beyond is e.g. world history not in the syllabus, another state's local history/geography (UP, Bihar,
  MP, Rajasthan ...), pure Group 1-only topics, deep technical trivia no line asks.
- **exists** – the Group 2 app already has the same question (the same fact asked; distractors may differ). Related
  facts spread over other questions do not count – then it is an add. Search:
  `grep -l "<distinctive words>" app/src/group2/assets/mcq*.json`, or `python3 tools/gapfill.py find <word> ...`.
- **skip** (with `why`) – Mental Ability, a question whose answer is out of date (a "present"/"current"/"latest" fact
  that has changed since the exam – the app keeps only the latest facts), an answer you cannot be sure of, or text too
  broken to rebuild.
- **add** – it fits a leaf, the app lacks it, and you are sure of the answer:
  - `leaf`: the leaf code it is asked under, exactly as in leaves.md (e.g. "P1.1.3/4", "M2A.1.2").
  - `page`: the notes page it belongs on, from `python3 tools/gapfill.py find <word> [<word> ...]` (prints
    "b:r:j | topic | page | text"; choose the page on that leaf's topic).
  - `mcq`: s (the question, cleaned up), o (4 options), a (0-3), x (one or two lines explaining the answer, no
    citations), src (the exam as given in the job, made readable, e.g. "UPSC CSE (Pre) 2016", "APPSC Group 1 Prelims
    2019", "APPSC Forest Range Officer 2019", "UPPSC (Pre) 2012").
  - The printed key is usually right but not always: check it against the notes (finder) and well-established facts;
    if another option is right, use it; if unsure, skip.

Write data/pyqfill/all/job-N.out.jsonl, one line per question, in the job's order:

    {"id": "...", "d": "add", "leaf": "P1.1.3/4", "page": "1:37:2",
     "mcq": {"s": "...", "o": ["...", "...", "...", "..."], "a": 1, "x": "...", "src": "UPSC CSE (Pre) 2016"}}
    {"id": "...", "d": "exists"}
    {"id": "...", "d": "beyond", "why": "Rajasthan local history"}
    {"id": "...", "d": "skip", "why": "out of date"}

Then run `python3 tools/pyqfill.py check all N` and fix what it reports until "problems: 0". Finish with one line:
questions, added, exists, beyond, skipped.
