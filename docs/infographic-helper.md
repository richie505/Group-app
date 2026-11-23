# Helper brief: Canva infographic notes for Group 2 topics

Repo: /home/user/Group-app. Never use the Anthropic API. Do not commit, push or run git. Scripts only in
/tmp/claude-0/-home-user/4666e051-48dd-5910-831c-f2c172f98923/scratchpad/igN/ (your own folder).

The user wants, for EVERY topic of the APPSC Group 2 app (the latest notes in app/src/group2/assets), Canva
infographics of that topic's notes, restructured for revision, that cover EACH AND EVERY FACT of the notes – no fact
may be lost. One infographic cannot hold a whole topic, so make ONE INFOGRAPHIC PER SECTION (each "## " heading of
`tools/infonotes.py`): <book>-<row>-<k>.png for section k = 1, 2, ... Your job file data/infographics/jobs/job-N.txt lists
about 20 topics as "book row title". For each topic, in order:

1. Read the notes: `python3 tools/infonotes.py <book> <row>`.
2. Restructure each section into an infographic brief (write them to data/infographics/briefs/<book>-<row>-<k>.md):
   - Title = topic (short) + section heading. Group the section's facts under 3–6 numbered panels with clear
     headings (e.g. AT A GLANCE / KEY PERSONS / TIMELINE / FEATURES / COMPARISON / EXAM TRAPS – what fits).
   - EVERY fact of the section must appear: every bullet, every table row, every name, year, number, place,
     Article, definition, cause and result, every ⚠ trap and "statement angle" (as an EXAM TRAPS box). Restate each
     as a short point (≤ 22 words); tables stay tables (or comparison panels with every row). A timeline strip
     when there is a sequence.
   - Leave out only exam citations ("G2 2008", "asked 13 times", "APPSC PYQ", "UPPSC 2008") and book/source
     names – those are not facts. Spell every name exactly as the notes do.
   - Before generating, tick off the section line by line: every fact in the notes is in the brief.
3. Generate: load the Canva tools with ToolSearch ("select:mcp__Canva__create-design,mcp__Canva__get-create-design-async-job,mcp__Canva__export-design")
   and call create-design with format "Infographic" and a brief that starts "Vertical infographic study notes for
   the APPSC Group 2 exam (<subject>). Title: ... Clean exam-revision style: dark blue headings, numbered sections,
   icons, highlighted key terms, a red EXAM TRAPS box at the bottom. Use exactly this content (spell every word
   exactly as given):" followed by your sections. Poll get-create-design-async-job, waiting with `sleep 15`
   (one sleep of at most 15 s per Bash call) between polls.
4. Export as PNG (export-design, type png) and download the URL with curl to
   out/infographics/<book>/<book>-<row>-<k>.png. Read the PNG and PROOFREAD it against your brief: every name, year,
   number and word, and that NO point of the brief was dropped. If anything is misspelt, wrong, missing or unreadable, fix it – load the Canva editing tools
   (ToolSearch "canva edit design" and follow their instructions to replace the text), or regenerate with the
   brief (at most 2 more tries). Export and download again, and read it again.
5. Append one line to data/infographics/designs-N.jsonl (N = your job):
   {"b": 1, "j": 178, "k": 1, "title": "...", "section": "...", "design_id": "D...", "url": "https://canva.link/...", "png": "out/infographics/1/1-178-1.png", "proofread": "ok" | "fixed: <what>" | "issues left: <what>"}

Finish with one line per infographic: book row section, design url, proofread result.
