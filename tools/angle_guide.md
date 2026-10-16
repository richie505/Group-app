# Re-sorting a topic by blueprint angles (APPSC notes, ROCKET-sheet style)

Your batch (`work/angle/b<book>/in_NNN.md`) holds whole topics: `=== ROW r | title`, then its pages
`## S<k> | title`. Today the pages go by sub-topic, and the facts about one person, one Act or one term are
spread over several pages. APPSC asks by **angle** — "who said", "book → author", "first", "term → meaning",
"Act → year", "site → feature" — so rewrite each topic so that its pages follow the **blueprint angles**
that fit it, like the ROCKET sheets do.

## The angles
`tools/data/blueprint-keywords.md` lists the recurring APPSC question angles per subject (book 1 History →
"AP History" / "Indian History"; book 2 Polity, Society & IR → "Polity", "Society"; book 3 → "Indian Economy /
AP Economy"; book 4 → "Geography"; book 5 → "Science & Technology", "Environment"; book 6 → "Current Affairs").
Read the section(s) for your book first. Typical angle pages:

| Angle page | Holds | Usual form |
|---|---|---|
| Definitions, types and FIRSTs | meaning, classification, firsts / pioneers / earliest / largest | `Basis \| Types` table; `FIRST \| FACT` table |
| Persons → statements / contributions | every scholar, ruler, leader, founder with what they said, did, wrote | `Person \| Statement / contribution` table |
| Books → authors | every book, text, journal, report, study | `Book \| Author \| Theme / year` table |
| Terms → meaning | every technical term, local name, concept | `Term \| Meaning` table |
| Functions / features / provisions | lists the exam asks as a whole | numbered `#` headings, bullets, a table if scholars differ |
| Places / sites / regions | site → finding, community → region, river → state | `Place \| Region \| Feature` table |
| Acts, Articles, cases, committees | every law, Article, judgment, commission, scheme | `Act / case \| Year \| Provision` table |
| Data | census / survey / budget figures | table of figures, then the takeaways |
| Changes, issues and debates | causes → effects, problems, criticism | `Factor \| Effect` table, bullets |
| Universal angles (last page) | current relevance, AP angle, debates not placed above | bullets |

Choose the angles **this topic's facts need** (a topic on Acts may be mostly Act pages; a history dynasty:
ruler → contribution, capital, inscriptions, art, administration terms, FIRSTs). Do not create an angle page
for one fact — put a stray fact on the closest angle page. Usually as many pages as before (±30%), each
80–600 words, titled by angle: `Sociologists → statements on family`, `Acts, cases and commissions on family`,
`Satavahana rulers → contributions`.

## Style (ROCKET sheet)
- **Bold** every key word a question would hinge on: names, numbers, years, terms, places.
- A table whenever facts pair up (A → B); one row per fact; no `|` inside cells.
- `⚠` trap lines for the confusions an exam exploits ("**4 – 7 – 2** = **Murdock – Ogburn – Parsons**",
  "**Khasi** = youngest daughter; **Garo** = Machong"), built **only from facts on the topic**.
- Short lines; no prose paragraphs.

## Rules (the checker enforces 1–4)
1. **Keep every fact** — all dates, numbers, Articles/Sections, names, exam references ("APPSC 2019 key",
   "UPSC 2024"), source tags ((APP), (CDI), (IYB 2026), [GK], (LENS, Apr 2025) …), `> Exam angle` lines and
   `⚠` lines, exactly as written. A fact may appear on two angle pages only if both angles truly ask it
   (e.g. a person's book on the persons page and the books page) — otherwise once.
2. **Add no new facts.** You may write a term's meaning only from the topic's own text.
3. **Gap lines** `!! Not in your sources: …` — keep every one CHARACTER FOR CHARACTER, on the page whose facts
   they belong to (as a bullet: `- !! Not in your sources: …`).
4. Where the notes give two versions ("⚠ Sources differ …", "some texts say …"), keep both.
5. Keep the topic title exactly; the **Universal angles** page (input marked ` | universal`) stays the last
   page with ` | universal`.

## Output — `work/angle/b<book>/out_NNN.md` (same topics, same order)
```
=== ROW 106 | Family - types, functions and changing structure in India
## Family — definitions, types and FIRSTs | from: S0, S2
<page>
## Sociologists → statements on family | from: S0, S2, S5, S8
<page>
...
## Universal angles | from: S8 | universal
<page>
```
`from:` lists every input page whose facts went into this page (each input S<k> must appear in some `from:`).
Markdown as in the input: `# 1. Heading`, `- **Label:** text`, `  - ` sub-bullets (two spaces, no deeper),
`**bold**`, `> Exam angle: …`, `- !! Not in your sources: …`, `@@ ` / `~~ ` lines as given, tables (header,
`|---|` line, rows with the same number of cells, blank line before and after). No `###`, no italics, no
numbered lists.

## Check
`TOPIC_DIR=work/angle python3 tools/topic_check.py <book> NNN` must say OK for every topic (numbers, gap lines,
bold terms, from:, Universal page last). Fix what it reports and re-run; never pad text to satisfy it. Write
only `out_NNN.md` (scratch scripts in your own scratchpad folder). Reply with one line per topic: pages
before → after and the angle pages made.
