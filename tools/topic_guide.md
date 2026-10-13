# Reorganising a whole topic (APPSC notes)

Your batch (work/topic/b<book>/in_NNN.md) holds whole topics. A topic is `=== ROW r | title` followed by its
subsections `## S<k> | title` (the reader opens one subsection at a time). The topics were built from several
sources, so a topic's subsections are in no particular order, related ones are scattered, and the same fact is
often repeated in two or three subsections.

Rewrite each topic so that it:
1. **Follows a logical sequence** — chronological for history and evolution (e.g. 1773 → 1784 → … → 1935),
   otherwise general → specific: meaning/background → composition/provisions → working/powers → issues →
   AP-specific → comparisons and quick-revision tables last, the Universal angles page at the very end.
2. **Brings related subsections together** — merge subsections that cover the same theme (e.g. "Dyarchy" and
   "Montagu-Chelmsford subjects"; two pages on the same Act); split a subsection that mixes two unrelated
   themes. Each new subsection = one clear theme, with a descriptive title in the style
   `Government of India Act, 1919 — Montagu–Chelmsford` or `Communal electorates — development from 1909 to 1935`.
   Aim for subsections of roughly 80–600 words; don't merge everything into one page.
3. **Removes identical or near-identical bullets** — when two bullets (anywhere in the topic) state the same
   fact, keep ONE, in the subsection where it belongs, combining any extra detail either one had. Same for
   table rows that repeat a bullet in the same subsection. Two tables on the same topic → merge into one
   (union of rows/columns), unless one is a deliberately different revision view (e.g. an "Act → what it
   introduced FIRST" table kept for revision at the end — keep such cross-topic comparison tables).
4. **Keeps every fact** — all dates, numbers, Articles/Sections, provisions, names, exam references
   ("APPSC 2019 key", "UPSC 2024", "BPSC 2024 key"), ⚠ Trap lines, `> Exam angle` lines, and source tags
   ((APP), (CDI), (IYB 2026), [GK], (LENS, Apr 2025) …) exactly as written. Do not add new facts.
5. **Does not settle disagreements** — where the notes give two versions ("some texts say about 10%",
   "⚠ Sources differ …"), keep both versions as written.
6. **Gap lines** `!! Not in your sources: …` — keep every one, text CHARACTER FOR CHARACTER (they hold the
   reader's own notes). They move with the facts they belong to.

## Output — work/topic/b<book>/out_NNN.md (same topics, same order)
```
=== ROW 0 | <topic title exactly as in the input>
## Company rule — Regulating Act 1773 to Charter Act 1853 | from: S3, S5
<page content>
## Government of India Act, 1858 — transfer to the Crown | from: S1
...
## Universal angles | from: S8 | universal
<page content>
```
- `from:` lists the input subsections whose facts went into this page (every input S<k> must appear in at
  least one `from:`). The Universal angles page keeps ` | universal` and stays last (its content may be
  trimmed of bullets now stated elsewhere only if the same exam angle is kept there).
- Page content uses the same markdown form as the input: `# 1. Heading` group headings, `- **Label:** text`
  bullets, `  - ` sub-bullets (two spaces, no deeper), `**bold**`, `> Exam angle: …`, `!! Not in your sources: …`
  (as a bullet or sub-bullet, e.g. `  - !! Not in your sources: …`), `@@ ` and `~~ ` lines as given,
  tables as markdown tables (header line, `|---|` line, one line per row, same number of cells per row,
  no `|` inside cells, blank line before and after). No `###`, no italics, no numbered lists.
- A bold plain line before a table (`**GoI Act 1935 - provisions, implemented or not**`) may stay as a caption.

## Check
`python3 tools/topic_check.py <book> NNN` must report OK for every topic: it compares each topic's numbers,
gap lines and bold terms with the input. Fix what it reports (usually a number you dropped while merging) and
re-run. Never pad the text to satisfy it (no term written twice, no "(**same term**)" echoes). Write only out_NNN.md. Helper scripts, if any: name them with your batch number (e.g. scratch/b2_000.py).
Reply with one line per topic: subsections before → after, and what you merged/moved.
