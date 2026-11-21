# Helper brief: one-liner MCQs for the Rocket facts the generator could not make options for

Repo: /home/user/Group-app. Never use the Anthropic API. Do not commit, push or run git. Write only your own output
file. Scripts only in /tmp/claude-0/-home-user/4666e051-48dd-5910-831c-f2c172f98923/scratchpad/rxN/.

The APPSC Rocket One-liners app asks one short question per fact of the Rocket notes (APPSC Group 1 and Group 2).
Your file data/rocketoneliner/extra/job-N.txt has about 200 facts the automatic generator skipped, one JSON per line:
a table row {"h": headers, "r": cells, "head": table heading, "topic", "k"} or a bullet {"b": text, "topic", "k"}.
`**bold**` marks the key term.

For EVERY fact write one MCQ (two when a bullet holds two clearly separate exam facts), each a line of
data/rocketoneliner/extra/job-N.out.jsonl, in the job's order:

    {"k": "af968f5abc3b", "q": "Which site's finds show that Harappan urbanisation was gradual and local?", "o": ["Kalibangan", "Lothal", "Dholavira", "Rakhigarhi"], "a": 0}
    {"k": "...", "skip": "no testable fact"}

Rules:
- `q`: ONE line (at most ~25 words), exam style, asking the fact's key point (usually the bold term, a name, year,
  place, number or the defining feature). It must not give the answer away (the answer's words must not appear in q).
- `o`: exactly 4 short options, the right one plus 3 wrong ones of the SAME kind (other sites, other years, other
  rulers, other Articles ...), plausible to a student, and certainly wrong. Take them from the same topic where you
  can. No "All of these" / "None of these". No two options alike. `a` = index 0-3 of the right one; vary its place.
- The answer must be what the fact says. If the fact is only a heading, a vague remark, a tip or too broken to ask,
  write `skip` with a short why. Do not drop facts just because distractors are hard – think of real ones.
- Use `python3 tools/gapfill.py find <word> ...` if you need related notes for sound distractors.

Then run `python3 tools/rocket_oneliner.py check N` and fix what it reports until "problems: 0". Finish with one line:
facts, MCQs written, skipped.
