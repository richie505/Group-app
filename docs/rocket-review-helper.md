# Helper brief: final answer-key and fact check of the Rocket One-liners MCQs

Repo: /home/user/Group-app. Never use the Anthropic API. Do not commit, push or run git. Write only your own output
files. Scripts only in /tmp/claude-0/-home-user/4666e051-48dd-5910-831c-f2c172f98923/scratchpad/rvN/ (and only to
read/view the batch – the judging is yours, MCQ by MCQ).

The app (APPSC Group 1 + Group 2) is about to be published. Each file data/rocketoneliner/review/rev-N.txt holds 1,000
one-line MCQs, one per line:

    <id> [book:row topic] question || 0) opt | *1) opt | 2) opt | 3) opt      (* = the keyed answer)

Most were generated automatically from the notes' tables (a blank "_____" or "X – heading?" asks for one cell), so
typical faults are: the key is wrong, ANOTHER option is also right, the fact itself is wrong or out of date, or the
question cannot be understood. Read EVERY MCQ and ask: does the question, read as a student would, have exactly one
right option, and is it the starred one, and is that fact true today (late 2026)?

Write data/rocketoneliner/review/rev-N.out.jsonl with a line ONLY for each MCQ that needs a change:

    {"id": "k6816c2ef632", "a": 2, "why": "the scheme gave 25%? no – 2 is right because ..."}      key is wrong
    {"id": "...", "o": {"3": "Nellore"}, "why": "option 3 (Guntur) is also correct"}            replace a 2nd right option (or a wrong fact in the answer) with text of the same kind
    {"id": "...", "s": "Which body implemented the AP Debt Redemption Scheme 2014?", "why": "question unclear"}
    {"id": "...", "drop": "out of date / wrong fact / cannot be made clear", "why": "..."}

You may combine a, o and s in one line. Options are numbered as printed (0-3). Rules:
- Fix only what you are SURE of (well-established facts, the Constitution, Census 2011, standard history,
  geography). For recent current affairs (2025–26 budgets, schemes, indices, appointments) the notes are newer than
  your memory: change those only if clearly impossible or self-contradictory. Use
  `python3 tools/gapfill.py find <word> ...` to read the notes when in doubt.
- Out of date: an older "present" fact (old Census figures when 2011 is meant as the latest, abolished bodies,
  former holders asked as current) – fix it to the current fact or drop.
- Unclear: when the question gives no way to tell what is asked (e.g. "Biggest – Key detail?" with sentence options,
  or a blank whose clue is only a vague phrase) rewrite `s` into a clear one-liner for the starred answer; drop only if
  even that is impossible.
- Easy-but-correct MCQs need no line. Do not restyle; correctness and clarity only.

Then run `python3 tools/rocket_oneliner.py checkrev N` until "problems: 0" (an empty output file is fine if nothing
needs a change). Finish with one line per batch: MCQs, fixes, drops.
