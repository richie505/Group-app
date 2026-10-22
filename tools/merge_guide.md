# Merging ROCKET sheets into the Prep topics (APPSC Complete)

Your batch `work/merge/b<book>/in_NNN.md` holds whole Prep topics. Each topic is `=== ROW r | title`, its Prep
pages (`## S<k> | title`, the reader opens one page at a time), then `=== ROCKET` and the ROCKET-sheet blocks
that belong to this topic (`## R<n> | sheet / page -> S<k>`: the Prep page it matched best — a hint, not a rule).

**The ROCKET sheets are the core notes.** Rewrite each topic so that every page leads with the ROCKET facts and
the Prep notes add what ROCKET does not have.

## For every page
1. **ROCKET first.** Put each ROCKET block's facts on the page where they belong (usually its `-> S<k>` page;
   a block may be split across pages). Keep ROCKET's wording, bold, tables and `> Exam angle` lines.
2. **Prep fills the gaps.** After the ROCKET facts, keep every Prep fact ROCKET does not already state — same
   wording, same bold. A Prep fact that only repeats a ROCKET fact goes (keep any extra detail it had, added
   to the ROCKET line).
3. **Disagreements: keep both.** When the two give a different number, year, name or count for the same thing,
   write the ROCKET version, then `⚠ Sources differ: other notes say …` with the Prep version. Never pick one
   silently and never drop either.
4. **Tables:** a ROCKET table and a Prep table on the same thing become one table (union of rows; ROCKET's
   values win, the Prep value goes in a `⚠ Sources differ` bullet under the table).
5. Keep every Prep heading structure that still makes sense; pages stay about 120–250 words. A page that grows
   past ~300 words is split at its headings into two pages; a ROCKET block with no fitting Prep page becomes a
   new page in the right place.

## Keep exactly
- Every number, date, Article, Section, name and bold term of both sources (the checker counts them).
- Gap lines `!! Not in your sources: …` character for character; exam references ("APPSC G2 2019", "UPSC 2024
  key"); source tags ((CDI), [GK], …); ⚠ Trap lines.
- ROCKET's source line (`~~ **Source:** …`) is not copied; nothing else of ROCKET is dropped.
- The Universal angles page stays last.

## Output — work/merge/b<book>/out_NNN.md (same topics, same order)
```
=== ROW 14 | <topic title exactly as in the input>
## Article 32 — clauses, scope, status and FIRSTs | from: S0, R0
<page>
## Writs → literal meaning, purpose and scope | from: S1, R1
...
## Universal angles | from: S6 | universal
```
- `from:` names every Prep page (`S<k>`) and ROCKET block (`R<n>`) whose facts went into the page. Every S and
  every R of the input must appear in at least one `from:` — except a ROCKET block that plainly belongs to a
  different topic (the matching is automatic and sometimes wrong): list those after the topic's last page as
  `=== NOT HERE: R8, R9` and they go to their right topic later. Do not use it for a block that merely overlaps.
- Page body format as in the input: `# 1. Heading`, `- **Label:** text`, `  - sub-point`, tables, `> Exam angle: …`.

## Check
`TOPIC_DIR=work/merge python3 tools/merge_check.py <book> NNN` must end `<n>/<n> topics pass`. Fix what it
reports and re-run. Write only `out_NNN.md`.
