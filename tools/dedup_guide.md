# Read each fact once: removing repeated facts across pages

The reader studies the notes day by day and keeps meeting the same fact again on another page or in another
topic (Bhakti saints in two topics, soils in India and in AP geography, the same scheme in Polity and in Current
Affairs). Your batch `work/dedup/in_NNN.md` holds clusters of note lines that look like repeats:

```
=== C12
U 1:142:3:7 | <topic> > <page>
- **Kabir:** ...
U 1:144:2:4 | <topic> > <page>
| **Saint** | **Teaching** |
| **Kabir** | ... |
```
Each `U` is one unit: a bullet with its sub-bullets, an exam line (`> `), or one table row (its header line is
shown for context). Decide each cluster in `work/dedup/out_NNN.md`:

```
C12 keep 1:142:3:7
N 1:142:3:7
- **Kabir:** <the richest version, now also holding any extra detail the dropped units had>
  - <sub-bullet>
C13 all
```
- `C<n> keep <uid>` — the fact stays only there; the cluster's other units are removed from their pages (the
  app shows "Also covered in" → the kept page there). Keep several (`keep a, b`) when the cluster holds two
  different facts.
- `N <uid>` + lines — optional new text for a kept unit, to fold in details only the dropped units had. A
  table row stays one `| ... |` line with the same number of cells; a bullet group starts `- ` (sub-bullets
  `  - `); an exam line starts `> `.
- `C<n> all` — not really the same fact (different years, different scheme, a list vs one item that the exam
  asks separately, a ⚠ trap that contrasts two things): keep everything.

## Where a fact should live (its home)
1. The topic that is **about** it (Kabir → the Bhakti saints topic, not the Bhakti origins overview; a soil type
   → the soils topic of that region; an Article → the Polity topic on it; a scheme → its sector topic).
2. Between India and AP versions of a topic: an AP fact lives in the AP topic, an all-India fact in the India one.
3. Between the overview/"Universal angles"/FIRSTs page and the detailed page: keep the detailed page, unless the
   unit is a FIRST/trap that only makes sense in the FIRSTs table.
4. Current Affairs (book 6) keeps only what is current (2025–26 events); background facts live in the subject book.

## Rules (the checker enforces 1–3)
1. Never lose a fact: every number and **bold** term of every unit in the cluster must be in the kept text. If a
   dropped unit has a detail the kept one lacks, add it in an `N` text — or keep both.
2. Add no new facts; use only the cluster's own words.
3. Every cluster decided once, in the input order.
4. When unsure whether two units are the same fact, choose `all`.

## Check
`DEDUP_DIR=work/dedup python3 tools/dedup_check.py NNN` must end `<n>/<n> clusters pass`. Write only
`out_NNN.md`.
