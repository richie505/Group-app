# APPSC Rocket One-liners

Flavor `rocketoneliner` (app id `com.appsc.prep.rocketoneliner`, name "APPSC Rocket One-liners", version as the other apps).
It has the Group 1 and Group 2 topics, and each topic's MCQs are one-line, 4-option questions made by
`tools/rocket_oneliner.py`, with no LLM, from every fact of the Rocket-style lecture notes (`data/lecrocket/`).

    python3 tools/rocket_oneliner.py            # writes app/src/rocketoneliner/assets (about 2 minutes)
    python3 tools/rocket_oneliner.py sample 40  # also prints 40 random MCQs to check
    ./gradlew :app:testRocketonelinerDebugUnitTest :app:assembleRocketonelinerRelease

When the Rocket notes change, run the tool again and update `MCQS` in
`app/src/testRocketoneliner/java/com/appsc/prep/RocketOnelinerTest.kt` to the total it prints.

## Topics and notes

- The app starts from **APPSC Group 2's assets**, which hold all 927 topics (Group 1 has the same 927, in another
  order). The `rocketonelinerAssets` Sync task in `app/build.gradle.kts` copies `src/group2/assets`, and the files
  in `src/rocketoneliner/assets` replace Group 2's. It leaves out the Group 2 files that are keyed by Group 2's own MCQ ids
  or list its PYQ papers: mcqlinks, notelinks, solved, dups, merged, unmerged, syllabus.
- Each Group 1 topic is matched to its Group 2 topic by title, and each page by its title within the topic.
  Group 2 blanks 215 pages that Group 1 needs ("No MCQ notes here: the same page is above"), so those get Group 1's notes
  back. The 10 pages only Group 1 has are added at the end of their topic. The topic Group 2 hides (1:263) is shown and
  added to the plan.
- `exams.json` = Group 1 Prelims (Group 1's syllabus, with its rows remapped) + Group 2. The plan is Group 2's.
- Each page's Rocket one-liners are filed under that page (`subs`). A page that both groups share gives its MCQs once
  (the id is a hash of the question and answer), and they show under the one topic both exams point to.

## How a one-liner is made

- **Table row**: the identifying cell is the first one, or the next one when the first column only numbers the rows.
  The question names that cell and the column asked, using a template where one fits ("Who wrote X?",
  "Capital of X?", "X – which year?", "In which year: <event>?"), or else "X – <column>?". A row label that means
  nothing alone ("Origin", "Status", a label 4+ tables use) gets the table's heading in front. Long cells are not used as
  answers. Instead the cell's most specific **bold** term is blanked, or a figure when the cell has no bold term. A
  year-first table asks for the year. A 3+ column table asks each column that holds its own short fact, plus at most one
  blank from a long column.
- **Bullet / box**: the most specific bold term (figures, dates, acronyms and names first, the bullet's opening label
  last) is blanked. A long bullet gives one question per sentence, up to 3. The question is cut to about 140 characters
  around the blank, at a clause where it can be.
- **Distractors** come from the same table column first, then the same page, topic and book (cells under the same column
  heading first). They must be the same kind as the answer (year, date, figure with the same unit, article, acronym,
  person or place name, thing name, plain text) and about its size, with years close to it and figures of a similar
  size. No distractor may be equal or near-equal to the answer or to another option (same text, one inside the other,
  the same figures or date, more than 80% similar), and none may share a content word or number with the question. A
  question whose answer's words already appear in it is not used.
- Options are shuffled deterministically by the MCQ id (`k` + 11 hex digits). The explanation `x` is the full source
  line (the row's cells joined by "–", or the bullet).
- A fact is skipped only when no sound question or distractors can be found. The tool prints how many.

## Numbers (21 Nov 2026 build)

96,421 facts (unique table rows and bullets/boxes), giving 100,939 MCQs. 7,339 facts were skipped (6,424 table rows,
915 bullets/boxes), and 3,970 repeats were left out (the same question and answer on another page).

## Final answer-key and fact check (2026-11-21)

Every MCQ (106,906) was read once more, in 107 batches (data/rocketoneliner/review/rev-N.txt, brief
docs/rocket-review-helper.md). 2,816 MCQs changed: 2,566 fixed (wrong key, a second right option replaced, a wrong or
out-of-date fact corrected, an unclear question reworded) and 250 dropped (no single right answer could be made).
The generator applies rev-N.out.jsonl by MCQ id; `python3 tools/rocket_oneliner.py checkrev N` checks a batch.
Result: 100,939 MCQs.

## Style rewrite (2026-11-21)

Every MCQ that was a blank ("Brahmi; records his _____ ...") or a label ("Mehrgarh: Date – Key detail?") – 98,624 of
them – was rewritten by hand as a real one-line question naming its subject, with four options of the same kind
(198 batches, data/rocketoneliner/style/sty-N.txt -> sty-N.out.jsonl, brief docs/rocket-style-helper.md, checked by
`python3 tools/rocket_oneliner.py checkstyle N` and `python3 tools/style_keycheck.py`). Repeats of the same fact were
dropped. The fact-checked answers were kept. Result: 100,939 MCQs, none a blank or a label.
