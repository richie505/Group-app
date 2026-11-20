# Helper brief: one Rocket rewrite job

You rewrite lecture-slide notes of an APPSC exam-prep Android app into the NextGen "Rocket Sheet" style.
Repo: /home/user/Group-app. Never use the Anthropic API. Do not commit, push or run git. Touch only your own output file; keep helper scripts in your own folder
/tmp/claude-0/-home-user/4666e051-48dd-5910-831c-f2c172f98923/scratchpad/jobN/ (other jobs share the scratchpad).

Read first:
1. docs/lectures/rocket-style.md – the rules and the output format; follow it exactly.
2. data/lecrocket/group2/1-37.json – a finished example (its keys are page indices; YOUR output is one JSON line per page keyed by the page id "h").
3. Your job file data/lecrocket/jobs/job-N.txt – pages, each "## page <id>", "topic:", "page title:", then lines "h:" heading,
   "b:" bullet, "x:" box, "n:" note, "t:" table header with "row:" lines (cells split by " | "). Text uses **bold**.

Rewrite EVERY page: mostly Fact | Key detail tables (or a fitting header pair), short headings, few bullets, bold key terms.
Keep every fact, number, name and year; add nothing; remove all quiz wording (answers, verdicts, wrong options, "NOT X",
TRUE/FALSE, exam labels) by stating the positive fact; drop source notes (book pages, URLs). Fix broken English.
Do not output the page title or topic as a block. Labelled facts ("**Author:** Kalidasa") belong in table rows
("Author | **Kalidasa**"); the checker does not need the colon.

Write data/lecrocket/jobs/job-N.out.jsonl: one line per page {"h": "<page id>", "b": [blocks]}, valid JSON, UTF-8, in the
job's order. Write in chunks (append ~15 pages at a time with a python heredoc using json.dumps(..., ensure_ascii=False)).

Then run `python3 tools/lecrocket.py check N` and fix what it reports; repeat until 0 pages with problems, except numbers
that were only exam years, question numbers, option codes, wrong options or citations (list those). Finish with one line: pages
written, problems left.
