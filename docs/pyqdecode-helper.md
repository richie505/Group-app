# Helper brief: APPSC PYQ decoding – statement-level deconstruction (Stage 4)

Repo: /home/user/Group-app. Never use the Anthropic API. Do not commit, push or run git. Write only your own output
file. Scripts only in /tmp/claude-0/-home-user/4666e051-48dd-5910-831c-f2c172f98923/scratchpad/dcN/ and only to read
or convert – every judgement is yours, question by question.

Goal: reverse-engineer how APPSC turns a syllabus fact into an exam statement. Central rule: **a word is not a trap by
itself – the factual relationship inside the exact micro-topic decides whether a statement is true or false.** Never
label "only / all / not / first / highest / however / elected / appointed ..." true or false by habit.

Input: data/pyqdecode/jobs/<g>-<n>.json – ~40 official APPSC Group 1 or Group 2 questions, each with options, the
key (key_index 0-3, key_text), key_status and key_check (how the key was verified; "CONFLICT ..." = a third-party key
differs), deleted, candidate_leaves (official syllabus micro-topics: code -> official wording), the app's explanation
and draft_statements (an earlier, unverified analysis – use it as a draft only; re-check every truth value).
Group 2 Mains 2019 questions have no options: analyse the stem + key_text as the true proposition, no distractors.

For EVERY question write one JSON line to data/pyqdecode/jobs/<g>-<n>.out.jsonl:

    {"id": "...",
     "format": "one-liner" | "negative one-liner" | "statement-based" | "matching" | "chronology" | "assertion-reason" |
               "multiple-correct" | "odd-one-out" | "data/passage" | <another real format>,
     "leaf": "<ONE syllabus code – the micro-topic actually tested. candidate_leaves are only suggestions (often wrong):
              choose the right code from the exam's syllabus (data/g1syl/leaves.json or data/g2syl/leaves.md) and give the
              reason in leaf_note when it is not a candidate>",
     "leaf_note": "",
     "micro_topic": "<finer than the leaf: e.g. 'Parliament > PAC > Chairperson > appointment'>",
     "blueprint_keyword": "<the syllabus/blueprint keyword the fact hangs on, e.g. 'Public Accounts Committee'>",
     "core_fact": "<the underlying constitutional/historical/geographical/economic/scientific fact, stated independently of APPSC's wording>",
     "statements": [ one per testable unit:
        statement-based: each numbered statement; matching: each pair as keyed AND each wrong pair a distractor offers;
        assertion-reason: "A", "R", and "R explains A"; chronology: each adjacent step of the keyed order;
        one-liner / negative: each option read as a full sentence (stem + option)
       {"label": "S1" | "A" | "R" | "R->A" | "a-iii" | "opt2" | "step1-2",
        "text": "<the unit as a full sentence>",
        "truth": "T" | "F" | "U" (U only if neither the key nor reliable facts settle it),
        "basis": "key" (the key fixes it) | "key+fact" | "fact" (key does not fix this unit; you verified the fact) | "pending",
        "true_fact": "<for F: the correct version>",
        "mechanism": "<for F – one of: authority swap, institution substitution, person substitution, location substitution,
                      chronological displacement, numerical alteration, fraction/majority alteration, article/act/amendment
                      substitution, true fact not the one asked, definition distortion, function/power substitution, exception removal, exception
                      insertion, scope expansion, scope restriction, quantifier distortion, comparison reversal, direction
                      reversal, cause-effect reversal, true core + false extra, multi-fact merge, similar-term confusion,
                      wrong period, wrong institution, wrong pair, fabricated – or a NEW name if none fits>",
        "decisive_phrase": "<the exact words that decide truth>",
        "phrases": [ {"phrase": "<fact-bearing word/phrase>", "meaning_here": "<its meaning in THIS micro-topic>",
                      "correct": true|false, "would_be_correct_if": "<for false>", "role": "fact" | "qualifier" | "trap",
                      "note": "<how APPSC used/changed it; whether it behaves differently in other micro-topics>"} ],
        "fact_source": "<for basis fact/key+fact: Article / Act / report / standard text / official site – be specific>"}],
     "reconstruction": {"correct_statement": "...", "transformation": "<exact difference between the fact and the exam wording>",
                        "decisive": "...", "why": "<the factual logic, not a trick>",
                        "micro_topic_rule": "<a rule for THIS micro-topic, e.g. 'PAC chairman is appointed by the Speaker – watch authority swaps to the President'>"},
     "key_note": "" | "<conflict: the key vs an authoritative fact – keep the key, explain>",
     "practice": "" | "AI-GENERATED PRACTICE (not an APPSC PYQ): <one similar statement and its truth>" }

Rules:
- The key stands. If you believe it is wrong, keep it and explain in key_note with a source. Deleted questions: still
  analyse the statements, note "deleted by APPSC" in key_note.
- For a combined-option key (e.g. "1 and 3 only"), statement truths follow only if the option set fixes them; if not,
  verify the fact (basis "fact") or mark "pending".
- One-liner options: the unit is "stem + option" as an answer to THIS question. An option that is a true fact but not
  the answer asked for is F with mechanism "true fact not the one asked".
- Facts: check with the app notes (`python3 tools/gapfill.py find <word> ...`; data/notes2026/src/INDEX.md lists the
  source texts) and well-established knowledge; cite them in fact_source. If nothing settles a unit, basis "key".
- "phrases": list only fact-bearing words and the qualifiers that matter (2–6 per statement; 1–3 per one-liner option); mark role "trap" only
  where the change of THAT word makes the statement false here.
- Time-sensitive facts: state the date/period the fact refers to.
- Short, exact, no padding. English.

Then run `python3 tools/pyqdecode_jobs.py check <g>-<n>` and fix until "problems: 0". Finish with one line per job:
questions, statements, F statements by mechanism (top 5), key conflicts.
