# RocketOne for Group 2: file each lecture under the Group 2 syllabus

RocketOne's lectures (written only from the Rocket Sheets and Rocket Current Affairs) are arranged by the Group 1
Prelims syllabus. The same lectures are now also shown arranged by the APPSC Group 2 syllabus. You file one batch.

- The Group 2 syllabus: `work/rocket/g2/leaves.txt` (`## paper`, `# unit`, then `code<TAB>syllabus line`).
- Your batch: `work/rocket/g2/lectures-N.txt`, one lecture a line:
  `key<TAB>where it sits in Group 1 (syllabus line, or current-affairs group)<TAB>title<TAB>[its part titles]`.
- If the title and parts do not settle it, read the lecture: file `data/rocketone/notes/<job>.json` (key = `job#n`,
  n = its position in `lectures`).

Write `data/rocketone/g2map/N.json`: `{"<key>": "<Group 2 leaf code>", ...}` with every key of your batch.
- Choose the ONE Group 2 syllabus line the lecture mostly teaches (e.g. `"P1.1.1/1"`). Prefer the most specific line.
- Andhra history, culture, movements -> the M1A lines; all-India history -> P1. Constitution and polity -> M1B.
  Economy -> M2A (AP economy -> M2A.4 / M2A.5). Geography -> P2. Society, social issues, welfare, rights of groups
  -> P3. Science, technology, energy, environment, health, disasters -> M2B. Every current-affairs lecture -> a P4 line
  (regional / national / international, by what most of it is).
- A lecture that no Group 2 line covers at all (e.g. world history of physics, pure world geography records) ->
  `"X"`. Do not force it.
Check: every key present once, every value a code that is in leaves.txt or "X". Write only that file; do not commit.
Reply with one line: batch, how many filed, how many "X".
