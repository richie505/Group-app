# Writing a unit's notes to the blueprint

The blueprint is `data/blueprint/APPSC_Notes_Blueprint.md`. Read its sections 2 (notes format and the model unit
U0291) and 4 (angles of the latest papers) first.

Input: `data/blueprint/src/<unit>.md`. It holds the unit's spec (rows, exams, tier with page budget, PYQ counts,
the numbered keyword angles, the latest-paper questions), then every line the app's notes hold for it.
Output: `data/blueprint/out/<unit>.md`, one unit in exactly the model unit's markdown.

## Rules

- **Facts from the source packet first** (and, for current-affairs units, the newer current-affairs files you
  are given). If two sources differ on a changeable fact (a rank, figure, office-holder, status), use the newest
  dated one and give its date.
- **Keep every fact the "MCQ NOTES" part of the packet holds**: the app's MCQs test exactly those facts, so each
  must still be in the unit (in a table, a bullet or a box). This matters more than the word budget.
- **Gaps: use web search.** When a keyword angle has no facts in the packet, or the packet gives two values for a
  fixed fact (a date, a count, a name), look it up with WebSearch and use what reliable sources agree on
  (government sites, PIB, NCERT, RBI, ISRO, UN bodies, established encyclopaedias and newspapers). Never write a
  fact from memory alone. If nothing reliable is found, leave that angle out rather than guess.
- **Cover every keyword angle.** Organise by topic in about 8-13 numbered sections (`### 1. TITLE`) with numbered
  sub-sections (`#### 1.1 Title`); the keywords decide what is covered, not the headings. Put the AP angle inside
  its natural section, and latest developments as dated bullets inside their section.
- Use comparison tables wherever things can be confused, full lists wherever a "which is NOT" question is
  possible, and boxes: `!TRAP`, `!KEY`, `!NUM`, `!PAIR a | b | c || d | e | f`, `!BOX` (one line each).
- **Always end with these three sections:** `NUMBER GAME AND QUICK REVISION` (a table, then `#### FIRST / LAST /
  SPECIAL FACTS`), `APPSC PREVIOUS YEAR QUESTIONS` (table: Examination | Question Area, from the PYQs the source
  names), `HIGH-PROBABILITY MCQ TRAPS` (`!BOX VERY IMPORTANT`, then 8-10 numbered traps).
- **Length:** the tier's budget (CORE ~2,000 words, HIGH ~1,350, MED ~850, LOW ~480); up to 1.5x when the
  MCQ facts need the room, never below 0.85x.
- Bold the exam words (`**...**`). Write plain, simple English.
- Never mention where a fact came from ("the app", "APP", "other notes", "sources say"). Where the sources
  give two values for a fixed fact (a date, a count), write the correct one only.
- Do NOT include a self-check list, source references, or provenance tags such as [GK], [Prep], "Not in your
  sources".
- The last line is `COVERAGE: 1>1.1,2; 2>3; ...`: every keyword number and the section(s) covering it.
- Begin with `## <unit> | <TITLE IN CAPITALS>`.

Also add, after the COVERAGE line, one line `WEB: <n>` with the number of facts you added from web search.

When you finish, run `python3 tools/blueprint_check.py <unit>` and fix every problem it lists.
