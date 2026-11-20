# RocketOne step 2: write the lecture notes (only from Rocket)

RocketOne is a Group 1 Prelims lecture app whose notes come ONLY from the NextGen Rocket Sheets and Rocket Current
Affairs 2026. You get one job and write one notes file, `data/rocketone/notes/<job>.json`.

- A **current affairs job** (`ca-NN`): the source is `work/rocket/chunks/ca-NN.txt`, text made by pdftotext from the
  PDF (`=== Rocket CA 2026 · Sheet #17 · p.116` starts a page). Write ONE lecture per Rocket sheet (#n).
- A **syllabus job** (any other name): the source is `work/rocket/topics/<job>.jsonl`, Rocket rows already filed under
  one Group 1 Prelims syllabus line (`leaf`), each with its Rocket sheet (`src`), sub-topic label (`topic`), and either
  table cells (`h` headings, `c` cells) or a sentence (`t`, sometimes with the Rocket heading it sat `under`).
  Write one lecture per `leaf` in the file; if a leaf has far too much for one lecture (more than about 14 parts),
  split it into several lectures by sub-topic, each with a clear title.

## Rule 1: only what Rocket says
Every fact on a slide must be in the source. Do not add dates, full forms, examples, background, "exam tips" or links
between facts from your own knowledge. Where Rocket is silent the notes are silent. Keep every fact, name, number and
date Rocket gives: nothing is dropped. Keep Rocket's spellings of names.

## Rule 2: the only thing you settle is a disagreement
- Two Rocket lines that contradict each other (two different dates, names, numbers or claims for the same thing).
- A Rocket line that is plainly wrong against the established fact (wrong person, place, year, article number,
  direction, a "first" that was not the first, a garbled name).
For these, check with WebSearch (official and standard sources) and write ONLY the corrected line in the notes, as an
ordinary line: no "Rocket says", no warning sign, no box. Record it in `corrections` (below). If the two Rocket lines
are both right in different senses, write one line that keeps both, each with its sense.
Do not "correct" what you merely doubt: if you cannot verify it, keep Rocket's line and record it with
`"kind": "unverified"`. Current affairs of 2025-26 are after your training: never correct them from memory, only from
a web check. Be economical: check what looks wrong or contradictory, not every line (about 10 searches a job at most,
more only if the job really has more disputes).

## Writing the lecture
- Group the facts into **parts** by theme (3 to 14 parts a lecture), in a teaching order: who/what first, then
  chronology or structure, then details. The Rocket sheets are arranged by kind of fact (firsts, lasts, titles, books,
  inscriptions...), not by theme: regroup them.
- **The same fact given several times is written once.** Rocket repeats facts across sheets and in end-of-sheet recap
  tables; merge the repeats and keep every extra detail any copy has.
- Mend PDF damage ("administra on" -> "administration"), repair rows that pdftotext broke across lines, and write
  clean plain English. Do not otherwise reword Rocket's facts.
- Items of a part:
  - `["b", "**Founder:** **Simuka** (Simukha); also written Sindhuk / Shiprak.", "AP History #16; Indian History #4"]`
    a bullet: a bold label or key term (`**...**`), then the fact. One fact a bullet, at most about 250 characters.
  - `["t", ["Term", "Meaning"], [["**Aharas**", "Administrative divisions"], ["**Amatyas**", "Officers of the Aharas"]], "AP History #10, #38"]`
    a table, for facts that share a shape (lists of officers, books and authors, missions, parameter / value).
    2 to 4 columns; every row has as many cells as there are headings; cells short (under about 150 characters).
    Bold the key term of each row.
  - `["h", "Amaravati Stupa"]` a sub-heading inside a part.
  - `["x", "**EOS-05** is India's first satellite to image from a geosynchronous orbit.", "CA #17"]` a "remember" box
    for the one or two facts of a part that Rocket itself stresses. Use sparingly.
- The last entry of `b`, `t` and `x` is `src`: the Rocket sheet(s) the line comes from (`"AP History #10"`,
  `"CA #17"`). It is not shown on the slide; it keeps every line traceable.
- Titles: plain, no "Rocket", no sheet numbers. Lecture title at most 80 characters, part title at most 70.

## The file
```json
{"lectures": [
  {"leaf": "A1/11", "title": "The Satavahanas",
   "parts": [{"t": "Founder, capital and identity", "items": [["b", "...", "AP History #1"], ["t", ["..."], [["..."]], "..."]]}]}
 ],
 "corrections": [
  {"title": "The Satavahanas", "kind": "rocket-vs-fact", "src": "AP History #8, #30",
   "rocket": "Motupalli - Western seaport of the Satavahanas",
   "corrected": "Motupalli: a seaport of the Satavahanas on the east coast.",
   "checked": "Motupalli is in Bapatla district on the Bay of Bengal (https://...)"}
 ]}
```
- Syllabus job: each lecture has `"leaf"` (the code in the rows; for rows with leaf `X/...` keep that code).
- Current affairs job: each lecture has `"sheet": 17` and `"unit": N` instead of `leaf`, where N is the number of the
  best-fitting group:
  0 AP government decisions, schemes, appointments · 1 AP budget and Socio-Economic Survey · 2 AP projects,
  investments, industry, infrastructure · 3 AP awards, GI tags, culture, sports, persons · 4 National polity and
  governance (bills, acts, judgments, elections) · 5 National economy (Budget, Economic Survey, RBI, banking, data) ·
  6 National schemes, missions, portals, apps, launches · 7 Committees and commissions · 8 International summits and
  conferences · 9 Treaties, agreements, international organisations · 10 Bilateral visits, defence exercises,
  geopolitics · 11 Science and technology (space, defence technology, health, biotech) · 12 Environment (species,
  protected areas, energy, climate) · 13 Reports and indices · 14 Awards and honours · 15 Sports · 16 Books and
  authors, important days, festivals, culture · 17 Persons in news (firsts, appointments, obituaries).
  A sheet that mixes groups still stays one lecture, under the group most of it belongs to.
- `corrections[].kind`: `rocket-vs-rocket`, `rocket-vs-fact` or `unverified`. `rocket` quotes Rocket's line(s),
  `corrected` is the line as you wrote it, `checked` says what settled it (source name and URL).

## Finish
Run `python3 tools/rocketone.py check-notes data/rocketone/notes/<job>.json`. It checks the format and lists Rocket
lines whose words are missing from your notes. Add what is missing (a line may stay "not found" only if it is a repeat,
a heading, or the wrong value of a correction) and run it again until it prints `OK`.
Write only your own notes file (build it with several Write/Edit steps if it is long; a small Python script that
assembles the JSON is fine, kept in your scratch space, not in the repo). Do not edit other files; do not commit.
Reply with one short line: the job, lectures, corrections made, anything odd.
