# Current affairs in APPSC Complete: the CA app's pages first, Prep fills the gaps

Your input `work/camerge/in_<t>.md` is one current-affairs topic: `=== TOPIC t | title`, Prep's pages for it
(`## S<k> | title`, written across 2025-26), then `=== CA` and the CA app's news pages for the topic
(`## C<n> | period · title`, one page per news item, newest first). **The CA app's pages are the core.** Fold
every Prep fact into them, so the topic holds each fact once.

For each Prep page, fact by fact:
1. **Already on a CA page** (same fact, any wording) → nothing to do.
2. **Extra detail of a news item a CA page covers** (another figure, the year before, a trap, an exam
   reference) → add it to that CA page as a bullet in the right place, in Prep's wording. Rewrite the whole CA
   page as `## C<n> | <its title>` with every one of its own lines kept as they were.
3. **Disagreement** with a CA page (different number, date, name) → leave the CA line as it is and add
   `⚠ Sources differ: other notes say …` with Prep's version right after it.
4. **Not covered by any CA page** (background, a summary table across months, older events) → it stays on an
   overview page: `## <title> | from: S2, S7`. Overview pages keep Prep's headings, tables and wording but only
   the facts no CA page states; aim for 120–250 words each, split at headings if longer.
5. A Prep page whose every fact is on CA pages: list it in `=== COVERED: S1, S4` (one line, at the end).

Keep exactly: every number, date, name and bold term of both; gap lines `!! …` character for character; exam
references ("APPSC 2023", "UPSC 2024 key"); ⚠ Trap lines; source tags. Do not edit CA pages you do not add
anything to — do not write them at all.

## Output: `work/camerge/out_<t>.md`
```
## C17 | RBI raises repo rate 25 bps to 5.50%
<the whole CA page, its own lines unchanged, Prep's extra bullets added>
## RBI monetary policy — rates and MPC across 2025-26 | from: S4
<overview page: only the facts no CA page has>
=== COVERED: S1, S9
```
Every S must be named in a `from:` or in `=== COVERED:` — or its facts must all have gone into CA pages (then
list it in COVERED). Page format as in the input: `# 1. Heading`, `- **Label:** text`, sub-points, tables.

## Check
`python3 tools/ca_merge.py check <t>` must end `pass`. Fix what it reports and re-run. Write only out_<t>.md.
