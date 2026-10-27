# Additional one-page notes

Every topic already has its one-pager (`work/onepager/b<book>/r<row>.json`): the most-tested facts of its notes.
The notes hold more. Write the topic's **additional one-pager**: one more landscape A4 page with what the notes
have and the one-pager does **not**, so the two pages together cover the topic without saying anything twice.

Inputs for a topic (book B, row R):
- `work/onepager/bB/rR.md`: the topic's full notes (use only them; ignore anything after `=== RELATED NOTES`).
- `work/onepager/bB/rR.json`: its one-pager. Read it first: nothing on it goes on the additional page.

Write `work/onepager-extra/bB/rR.json` yourself with the Write tool, then run
`python3 tools/onepager.py check-extra B R` and fix what it reports until it prints PASS.

**Long topics get more pages.** `python3 tools/onepager.py extra-pages B R` says how many (1, 2 or 3: notes over
5,000 and 10,000 words). For 2 or 3, write `rR.json`, `rR-2.json` (and `rR-3.json`), check each with
`check-extra B R`, `check-extra B R-2` ... ; split the topic's notes between them in the notes' order (each page
its own part, titled for it: "... (2 of 3): banking and prices"), nothing twice across the pages.

## The page plan

The same format as the one-pagers (see `tools/onepager_guide.md` for every box type):

    {"title": "...", "tag": "...", "quote": "...", "boxes": [...]}    // 3-11 boxes

- **title**: the one-pager's topic and what this page adds, short: "Harappan sites: more sites and finds".
- **tag**: the subject area, as on the one-pager.
- **quote**: optional.

## Rules

- **Only what the one-pager lacks.** Go through the notes section by section; for each fact ask "is it on the
  one-pager?" If yes, leave it out. The check fails any line whose words are mostly on one of the one-pager's lines.
  A fact the one-pager only touches may come back with its added detail only ("Lothal: also bead factory, warehouse"
  is fine when the one-pager says only "Lothal: dockyard").
- **Only facts from the notes** (the check compares every figure and name with them). Where the notes say sources
  differ, give the exam (key) version and mark the other "⚠ other notes: …".
- **What matters most first**: names, dates, numbers, firsts, lists, comparisons and PYQ points the one-pager left out;
  then the remaining detail. Drop repetition and background.
- **Telegraphic**, bold names, years and numbers with `**…**`, `==…==` for the most-tested fact of a box (1-2 a box).
- **Fit one page**: about 350-550 words. A topic whose notes the one-pager already covers well gets a shorter page
  (3-4 boxes) — never pad it with what the one-pager says.
- Vary the box types to suit the content (tables, cards, timelines, flows ...). An exam corner is optional here; if
  you add one, only with points not in the one-pager's exam corner.
