# Lecture slides in the Rocket-sheet style

The lecture slides of the APPSC apps read like the NextGen **Rocket Sheets** (data/notes2026/sources/rocket-ap-history-satavahanas.txt):
crisp, flawless fact sheets, mostly **Fact | Key detail** tables. Pilot: data/lecrocket/group2/1-37.json
(Gupta Society and Economy), rendered in docs/lectures/pilot-rocket-gupta-society.pdf.

## The rules for one notes page

1. **Every fact stays.** Every name, number, year, place, term, ruler, article, scheme, figure of the page is on the
   rewritten page. Nothing new is added: no fact that is not on the page (no outside knowledge), no opinion.
2. **Each fact once.** A fact said twice on the page is said once.
3. **No quiz wording.** The notes were written from MCQs; nothing of that is left:
   - no answers or verdicts: "(b) is false", "→ a, c, d", "= IV, I, II, III", "A and R true", "all true", "TRUE / FALSE", "correct / wrong statement";
   - no wrong options: "– not X, Y or Z", "NOT Bhavabhuti", "Tamralipti was only his port of departure" – write the fact itself;
   - no exam labels: "Exam fact", "Exam angle", "Statement angle", "Trap", "A-R", "Match", "AP angle", "asked", "PYQ", "key", "option";
   - a fact stated only as a negation of a wrong option becomes the positive fact ("NOT a feature: non-autonomous" → "Nature: autonomous").
   Real contrasts that teach something stay ("decomposition is anaerobic (not fungal)"; "Art. 256, not 257" may become "Art. 256 – compliance with Union laws").
4. **No citations:** no exam names with years, no book names (NextGen, PMF, Laxmikanth, Spectrum ...), no "sources differ".
5. **Rocket layout:**
   - mostly tables: `Fact | Key detail` (2 columns), or a better header pair when it fits (`Port | Region | Key detail`, `Cause | Effect`,
     `Ruler | Contribution`, `Article | Provision`, `Scheme | Key detail`, `Year | Event`);
   - short headings (`h`) to group the tables, as the notes had;
   - a few bullets (`b`) only where a fact is a chain or an explanation that does not fit a table row;
   - at most one `x` box ("REMEMBER") for the single most important line, if any;
   - key terms in **bold** (names, numbers, terms): "**Eran, 510 CE**";
   - cells short: a phrase, not a paragraph; "–" for an empty cell.
6. **Flawless English:** full words, no fragments, no doubled punctuation, consistent names.
7. Tables of the page that are already good stay as they are (with the column names fixed: "Exam fact" → "Key detail").

## Output format: one JSON line per page

    {"h": "<page id, as given>", "b": [
      {"k": "h", "x": "Ports"},
      {"k": "t", "h": ["Port", "Region", "Key detail"], "r": [["**Tamralipti** (Tamluk)", "Bengal, east coast", "Outlet of **North India's** trade"]]},
      {"k": "b", "x": "**R.S. Sharma:** shrinking towns ... → **urban decay** thesis."},
      {"k": "x", "x": "**Sudarshana lake:** built by **Pushyagupta** → repaired by **Rudradaman** ..."}
    ]}

`k`: "h" heading, "t" table (`h` header cells, `r` rows of cells; every row as many cells as the header), "b" bullet,
"x" REMEMBER box. Text uses `**bold**`. Nothing else.
