# Merging repeated tables in notes pages

Read tools/restructure_guide.md first: the same page format, hard rules and check apply. These pages are
ALREADY in the structured format; the only problem is that the SAME TOPIC is tabled two or more times
(pages were built from several sources). Here tables are written out as markdown tables:

```
| **Work** | **Author** | **Period / subject** |
|---|---|---|
| **Rajatarangini** | **Kalhana**, 12th century | History of the kings of Kashmir |
```

## What to do on each page
1. Find tables on the same topic (same items in the first column, or the same kind of comparison).
   **Merge them into ONE table**:
   - Rows: the union of all rows. Same item in both tables → ONE row holding every detail from both
     (e.g. "History of the kings of Kashmir" + "Kings of Kashmir" → keep the fuller wording once;
     different facts → join with "; ").
   - Columns: the union of the columns (rename headers sensibly, e.g. "Period / subject / dynasty").
     A cell with nothing for that row gets "-".
   - Keep a sensible row order (chronological, or the order of the fuller table).
2. Tables on different topics stay separate. Do not merge a table into bullets or bullets into a table,
   except: a bullet whose every fact is now in the merged table may be dropped.
3. Keep the merged table where the first of its parts was. Everything else on the page stays as it is
   (headings, bullets, `> ` exam angles, `!! ` gap lines copied exactly).
4. Table syntax: a header line, a `|---|---|` line, then one line per row; every row has the same number
   of cells; no `|` inside a cell; `**bold**` allowed in cells; no blank lines inside a table; a blank
   line before and after the table.
5. Drop `[GK]` and source citations inside cells the same way as in text (see the main guide).

## Hard rules (checked automatically)
Every number, date, name and bold term of the input page must still be on the page (in a table or in
text), and every `!! ` gap line must stay character for character. Never add facts.

## When done
Run `RS_PREFIX=t python3 tools/restructure_check.py <book> <NNN>` and fix every listed page until it
prints `N/N pages pass`.
