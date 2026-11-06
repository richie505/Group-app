# Gap-fill pass

Each unit file data/blueprint/out/<unit>.md may end with `GAPS:` and `CHECK:` lines left when web search was
unavailable. For each unit you are given:

1. Read data/blueprint/INSTRUCTIONS.md (rules), the unit's out file, and its source packet data/blueprint/src/<unit>.md
   (the keyword list there gives the angle numbers that `GAPS:` refers to). Also read any line for the unit in
   data/blueprint/gaps_manual.txt.
2. For each `GAPS:` keyword: look it up with WebSearch (reliable sources only: government sites, PIB, NCERT, RBI,
   ISRO, UN bodies, established encyclopaedias and newspapers) and add its facts to the right section (a table row,
   bullet or box). Update the COVERAGE line so the keyword is listed. If nothing reliable is found, leave it out.
3. For each `CHECK:` fact (and each conflict in gaps_manual.txt): look it up. Write only the correct value
   everywhere it appears in the unit (body, tables, Number Game, traps). Where an APPSC answer key differs from
   the established fact, keep the established fact and add one `!TRAP` line saying the APPSC key gave the other
   value.
4. Remove the `GAPS:` and `CHECK:` lines you resolved (keep a line only for what stays unresolved), and raise the
   `WEB:` count by the facts you added. Never mention sources in the notes. Keep every existing fact.
5. Run `python3 tools/blueprint_check.py <unit>` and fix until problems 0.
