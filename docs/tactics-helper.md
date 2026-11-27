# Helper brief: APPSC MCQ tactics – topic-by-topic technique sheets

Repo: /home/user/Group-app. Never use the Anthropic API. Do not commit, push or run git. Write only your own output
files. Scripts only in /tmp/claude-0/-home-user/4666e051-48dd-5910-831c-f2c172f98923/scratchpad/tcN/ and only to
read or convert – every line of advice is yours.

Goal: the student wants TECHNIQUES AND TRICKS to crack any MCQ APPSC can ask on a syllabus section – not a list of past
questions. For each section you are given (data/tactics/packs/<g>-<section>.json) write ONE sheet
data/tactics/out/<g>-<section>.json. The pack holds: the section's official syllabus leaves with how often each was asked
(years, recurrence label), EVERY official APPSC question of the section (stem, options, key, format, year, and the earlier
statement analysis: each statement's truth T/F, mechanism, decisive phrase, correct fact, and a micro-topic rule), plus
a sample of related questions from other APPSC exams (useful to see which angles APPSC likes).

Central rule (never break it): a word is not a trap by itself – the factual relationship inside the micro-topic decides.
So a technique is never "pick the longest option" or "'only' is always false"; it is "in THIS topic APPSC swaps X with Y –
check Z", "anchor on this date/number to eliminate", "this pair is always confused – remember the difference".

Output schema (JSON, English, short exact lines, no padding):

    {"section": "<code>",
     "overview": "<2–3 lines: what APPSC tests in this section, which formats, how heavily – use the pack's real counts>",
     "possibility": [  // topic-by-topic: which angles are asked and how often – from the counts, never a guarantee
        {"angle": "<micro-topic / angle, e.g. 'Satavahana coins and ports'>",
         "evidence": "<e.g. '5 Qs: 2008, 2017, 2019×2, 2024' or 'asked in other APPSC exams (3), not yet in Group 2'>",
         "level": "High historical recurrence" | "Moderate historical recurrence" | "Low historical recurrence" |
                  "Syllabus angle not yet asked",
         "what_they_ask": "<the exact kind of fact asked: who/when/where/which article/which number …>"} ],
        // cover EVERY syllabus leaf of the section (merge leaves into one angle where natural); 'not yet asked' leaves:
        // say which facts would be the natural targets, judged from how APPSC asks the neighbouring leaves
     "traps": [  // 4–10, the traps APPSC actually used here
        {"trap": "<e.g. 'Swaps the dynasty that issued ship-type coins'>",
         "spot": "<how to recognise it in the question>",
         "fix": "<the fact or check that defeats it>",
         "pyq": "<real example: short quote → correct fact> [<question id>]"} ],
     "techniques": [  // 3–8 solving methods for this section's questions
        {"name": "<e.g. 'Date-anchor elimination'>",
         "how": "<steps, 1–3 lines>",
         "example": "<worked on a REAL PYQ from the pack: what to look at → which options fall → answer> [<question id>]"} ],
     "confusions": [ {"a": "...", "b": "...", "remember": "<one-line difference / memory hook>"} ],  // 5–20 pairs
     "anchors": ["<a date / number / name / article that decides many questions here, with the fact>"],  // 5–20
     "checklist": ["<30-second checklist lines to run on any question of this section>"]  // 4–7
    }

Rules:
- Cite question ids in square brackets exactly as in the pack, e.g. [group2-2008-paper1#12]. Every trap and every
  technique needs at least one real citation. No invented PYQs, no invented counts.
- Facts must be correct; when in doubt check the app notes (`python3 tools/gapfill.py find <word> ...` from the repo
  root) or leave it out. Where the pack's key_note shows a key conflict, do not build a trick on that question.
- Recurrence words only as historical observation ("asked in 4 of 9 years") – never "will come", "sure shot".
- Sections with no official question: still fill possibility (from the leaves and related questions), confusions,
  anchors and checklist; traps/techniques may cite related questions in words (no id).
- Keep each sheet readable in about 1–2 printed pages.

When done with each section run `python3 tools/tactics_jobs.py check <g>-<section>` and fix until ok. Finish with one
line per section: angles, traps, techniques, confusions.
