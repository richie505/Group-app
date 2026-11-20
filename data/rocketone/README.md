# RocketOne

A Group 1 Prelims lecture app (the APPSC Lectures slide viewer, installed separately as "RocketOne") whose notes come
ONLY from the NextGen Rocket Sheets (15 subjects, about 1,740 pages) and Rocket Current Affairs 2026 (435 pages).

Owner's rules (20 Nov 2026):
1. Only what Rocket says. Where Rocket is silent, nothing is added from any other source.
2. The only thing settled from other sources is a disagreement: two Rocket lines that contradict each other, or a Rocket
   line that is wrong against the verified fact. The slide carries only the corrected line; what Rocket said and what
   settled it are in `CORRECTIONS.md`.
3. No MCQs. A separate app.

## How it is built (`tools/rocketone.py`)
| Step | What | Where |
|---|---|---|
| text | Rocket PDFs from the owner's Drive (ids in `data/notes2026/SOURCES-LOCAL.md`), `pdftotext -layout` | `work/rocket/*.txt` (not in git) |
| `chunks` | 53 subject-sheet chunks, 20 current-affairs chunks | `work/rocket/chunks/` |
| rows | every Rocket row filed under one of the 237 Group 1 Prelims syllabus lines (`GUIDE-ROWS.md`; 19,580 rows) | `rows/*.jsonl` |
| `topics` | rows grouped into 105 jobs by syllabus line | `work/rocket/topics/` |
| notes | lectures written from the rows; current affairs straight from the chunks, one lecture per Rocket sheet (`GUIDE-NOTES.md`, `JOB-SYLLABUS.md`) | `notes/*.json` |
| `check-rows`, `check-notes` | format, and that every Rocket line's words are in the output | |
| `build` | the app's books and index, `CORRECTIONS.md`, lecture PDFs, the app's slide decks | `assets/`, `out/rocketone/`, `app/src/rocketone/assets/lec/` |

Rows that no syllabus line names (other dynasties, pure sociology, economists) are kept under "More from the Rocket
Sheets" in their subject. Lectures of one or two lines are gathered into a "Short notes" lecture per subject. Rocket's
own asides ("according to the source", "in cited PYQ") are stripped from the slides by `tidy()` in the build.

**Group 2 edition:** the same lectures filed under the Group 2 syllabus (`GUIDE-G2MAP.md` -> `g2map/*.json`, one
Group 2 syllabus line per lecture; `collect_g2` in the build). Lectures no Group 2 line covers (general science, world
geography records, some all-India dynasties, a few economy topics) sit in a last subject, "More from the Rocket Sheets".
The app shows both editions on its home screen.

App: flavor `rocketone` (`./gradlew :app:assembleRocketoneRelease`, package `com.appsc.prep.rocketone`).

Known limits: lines were web-checked only where they looked wrong or contradicted another line, so an unflagged Rocket
error can remain; contradictions between lectures written by different jobs were caught only where noticed; Rocket
Current Affairs pages 421-435 are advertisement pages (no content).
