# One-page micro-theme notes

You get `work/onepager/b<book>/r<row>.md`: all the notes of one syllabus topic (from APPSC Complete). Turn it into
**one landscape A4 page** of coloured boxes, like a topper's one-pager: the whole topic at a glance, for revision
the night before the exam. Write the page plan as JSON to `work/onepager/b<book>/r<row>.json`, then run
`python3 tools/onepager.py check <book> <row>` until it prints PASS.

## The page plan

    {"title": "Information about Harappan sites",       // short; the topic, not the syllabus line
     "tag": "Ancient History",                           // the subject area, 1-3 words
     "quote": "…",                                       // optional: one striking line from the notes
     "boxes": [ {"type": "...", "title": "...", ...}, ... ]}   // 5-11 boxes

Box types (pick what suits the content; vary them):

| type | fields | use for |
|---|---|---|
| `bullets` | `items`: ["…"] | key facts |
| `table` | `head`: [..], `rows`: [[..], ..] | comparisons (A vs B), lists with 2-4 attributes (site, river, excavator, finds) |
| `timeline` | `items`: [{"when": "1921", "what": "…"}] | dated events in order |
| `cards` | `cards`: [{"title": "Lothal", "lines": ["…"]}] | many similar items each with 2-4 facts (sites, schemes, texts) |
| `cycle` | `steps`: ["…"], `centre`: "…" (optional) | a cycle (savings → investment → growth → income → savings) |
| `flow` | `steps`: ["…"] | a process or cause → effect chain |
| `hierarchy` | `levels`: [{"name": "Jana", "note": "head: Rajan"}] (top first) | ranks, levels, tiers |
| `note` | `items`: ["…"] | the exam corner: PYQ keys, traps, "follow the key" points (one per page, last) |

## Rules
- **Only facts from the notes file.** No outside facts, no figures that aren't in it (the checker compares every
  figure and name with the notes). Where the notes say sources differ, give the exam (key) version and mark the other
  "⚠ other notes: …".
- **Cover the topic, not every line.** Choose what an aspirant must remember: definitions, names, dates, numbers,
  firsts, comparisons, PYQ-tested points. Drop repetition and background.
- **Telegraphic, not sentences.** "Excavated by **R.S. Bisht** (1990)", "Capital: **Pataliputra**". Bold names, years
  and numbers with `**…**`; highlight the single most-tested fact of a box with `==…==` (sparingly: 1-2 per box).
- **Fit one page.** About 350-550 words in all; table cells short; 4-8 bullets a box. If the check says it does not
  fit, cut the longest boxes.
- Box titles in a few words ("Primary vs secondary sources", "Excavators & finds", "Exam corner").
- Use at least one non-bullet box (table, cards, timeline, cycle, flow or hierarchy) where the content allows.
