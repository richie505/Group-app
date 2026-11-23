# Helper brief: clean infographic notes (Excalidraw style) for Group 2 topics

Repo: /home/user/Group-app. Never use the Anthropic API. Do not commit, push or run git. No Canva. Scripts only in
/tmp/claude-0/-home-user/4666e051-48dd-5910-831c-f2c172f98923/scratchpad/igN/ (your own folder).

The user wants, for EVERY topic of the APPSC Group 2 app (the latest notes, app/src/group2/assets), clean
infographics that cover EACH AND EVERY valid fact of the notes – no fact lost, and nothing extra. A renderer draws
them in Excalidraw style from a brief you write. Your job file data/infographics/jobs/job-N.txt lists 5 topics as
"book row title". For each topic:

1. Read the notes: `python3 tools/infonotes.py <book> <row>`.
2. For each section of the notes (each "## " heading; k = 1, 2, ... in order) write the brief
   data/infographics/briefs/<book>-<row>-<k>.md in EXACTLY this format (see data/infographics/briefs/1-178-*.md):

       Title: <topic, short> – <section heading>

       1. <panel heading>
       - <fact>
       - <fact>

       2. <panel heading> (table)
       | <col 1> | <col 2> |
       | <cell> | <cell> |
       - <optional facts under the table>

   - 3–6 panels with plain subject headings (Origin / Rulers / Administration / Features / Timeline / Comparison
     ... whatever fits). A table when the notes have a table or when 3+ items share the same attributes
     (first row = column headings).
   - EVERY valid fact of the section: every name, year, number, place, Article, definition, feature, cause,
     result, every table row. One crisp point each (≤ 18 words); a fact the notes repeat goes in once.
   - Leave OUT everything that is not a subject fact: ⚠ traps, "distractors", "statement angle", "exams answer",
     memory tips, exam citations ("G2 2008", "asked 13 times", "APPSC PYQ"), source/book/URL names. Where the notes
     say "sources differ", keep the settled fact. Spell every name exactly as the notes do.
   - Before moving on, tick the section off line by line: every fact in the notes is in the brief.
   - A very short section (fewer than ~6 facts) may be merged into the next section's brief (then k skips it).
3. Render the topic: `python3 tools/excalinfo/make.py <book> <row>` -> out/infographics/excalidraw/<book>/....png.
   Look at one or two of the PNGs (Read tool) to check nothing overlaps or is cut; fix the brief if needed
   (e.g. split a very long panel) and render again.

Finish with one line per topic: book row, number of infographics, any fact you could not place.
