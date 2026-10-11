# Rewriting notes pages into the structured, keyword-driven format

You get a batch file of exam notes pages (APPSC Group 1/2, India). Each page starts with a header line
`=== <id> | <title>` followed by its content in a small markdown form. Rewrite EVERY page into the structured
format below and write the result to the output file, with the SAME header lines in the SAME order.

## The markdown form (the app reads exactly this; nothing else)
- `# 1. Heading` — a group heading inside the page
- `- text` — bullet;  `  - text` (two spaces) — sub-bullet. No deeper levels.
- `**x**` — bold. Do not use italics, links, numbered lists, tables or `###`.
- `> text` — exam-angle callout (keep these as `> ` lines).
- `@@ text` see-also line, `~~ text` grey note: keep as they are.
- `!! Not in your sources: ...` — a gap line. Copy it CHARACTER FOR CHARACTER (it is a key for the
  reader's own notes). It may move (to sit under the group it belongs to) and may be a bullet or sub-bullet
  (`- !! ...` or `  - !! ...`), but its text after `!! ` must not change.
- `<<table N>>` — a table; keep each placeholder exactly once, on its own line, near the facts it belongs to.
- `[GK]` and other muted tags: drop them.

## How to restructure
1. **Group** the page's facts by topic. When a page has more than ~5 bullets covering 2+ topics, use
   `# 1. ...`, `# 2. ...` headings (usually 2–5). Short pages (≤5 bullets, one topic) need no heading.
   A bold plain line in the input (e.g. `**GoI Act 1935 - provisions, implemented or not**`) is a sub-topic
   title: turn it into a heading or fold its facts into the right group.
2. **Every bullet starts with a bold keyword label** and a colon: `- **Funding pattern:** ...`,
   `- **Core objective:** ...`, `- **Federal Court:** ...`. Keep the text after it short and keyword-driven:
   drop filler ("It is important to note that", "This Act is the answer to"), keep the fact.
3. **Split chains**: a sentence listing several facts joined by `;` or "and" becomes a label bullet with
   sub-bullets (`- **Timeline:**` then `  - Phase 1: Launched **2018-19**`). Use `=`, `+`, `→`, `vs` where they
   read naturally (`General states = **60:40** (Centre:State)`).
4. **Merge repeats**: the same fact stated twice on a page (pages were built from several sources) is
   written ONCE, keeping every detail either version had (the fuller date, the extra number).
5. **Bold** the key terms, names, numbers, dates and articles, as the input does.
6. **Exam traps / PYQs**: keep exam tags like `(UPSC 2024)`, `(APPSC-GS 2018)`, `(APPSC G2 2025 key)`, `PYQ`.
   A "trap" or "key" remark becomes a sub-bullet such as
   `  - ⚠ **Trap:** "1 April 2021 to 31 March 2026" is WRONG (UPSC 2026)`.
7. **Source citations go**: `(IYB)`, `(IYB 2026)`, `(TH, 26 Jan 2026)`, `(LENS May 2026)`, `(LENSD, 22 May 2026)`,
   `(CDI)`, `(CDX)`, `(APP)`, `(APPCA ...)`, `(VIS ...)`, `(ES 2025-26)`, `(APSES 2024-25)`, `(UPSC notes)`, `[GK]`.
   BUT if the citation is the only place a figure's year/period is given, keep that year in the text
   (e.g. `- **GSDP (2024-25):** ...`). When sources disagree ("some texts say about 10%"), keep both values.

## Hard rules
- **Never drop a fact.** Every number, date, name, article/section, place and bold term of the input page
  must still be on the rewritten page (an automatic check compares them). Never add facts that are not in the
  input; do not "correct" facts; do not expand abbreviations (the app adds full forms itself).
- Keep each page's header line exactly. Keep every page, in order. Do not merge pages together.
- Output only the pages — no commentary.

## Example
Input:
```
=== 2:61:0 | Capacity building - RGSA, NIRDPR and SIRDs, eGramSwaraj, AuditOnline
- **Rashtriya Gram Swaraj Abhiyan (RGSA)**, run from **2018-19**: strengthen PRIs to achieve SDGs; convergence with **Mission Antyodaya**; focus on **117 aspirational districts**; covers non-Part IX areas too (IYB).
- Funding **60:40** (Centre:State); **90:10** for NE and hilly states; **100%** Central for UTs (IYB).
- **Revamped RGSA: 1 April 2022 - 31 March 2026**, matching the 15th FC period (IYB) (UPSC 2026 trap: not 2021).
- **Backward Regions Grant Fund (BRGF)** is the programme merged into RGSA (APPSC-GS 2018 key).
- 2025-26: **₹394.84 crore** released and **8,67,915** participants trained (IYB).
- Training bodies: **NIRDPR, Hyderabad** at the national level; **SIRDs** in states [GK].
- **eGramSwaraj** combines panchayat planning, accounting and reporting (LENSD, 22 May 2026); launched with SVAMITVA on **24 April 2020** [GK]. **AuditOnline** audits panchayat accounts online [GK].
- **SVAMITVA** (24 Apr 2020; Survey of India): "Record of Rights" for rural homes and a property-tax baseline (IYB; LENS, May 2026).
- !! Not in your sources: whether RGSA has been extended after 31 March 2026.
- **Revamped RGSA: 1 April 2022 - 31 March 2026**, co-terminus with the **XV Finance Commission** (IYB 2026) - so "1 April 2021 to 31 March 2026" is wrong (UPSC 2026 key).
- Capacity building: **35 lakh+** trained in FY25 (ES 2025-26); 2025-26: **₹394.84 crore** released, **8,67,915** trained (IYB 2026); Training of Trainers on **own-source revenue** (LENS Jul 2025).
```
Output:
```
=== 2:61:0 | Capacity building - RGSA, NIRDPR and SIRDs, eGramSwaraj, AuditOnline
# 1. Rashtriya Gram Swaraj Abhiyan (RGSA)
- **Core objective:** Strengthen **PRIs** to achieve **SDGs**
- **Key targets:** Focus on **117 aspirational districts** + convergence with **Mission Antyodaya**
- **Jurisdiction:** Covers non-Part IX areas too
- **Timeline:**
  - Phase 1: Launched **2018-19**
  - **Revamped RGSA: 1 April 2022 – 31 March 2026** (co-terminus with **XV Finance Commission**)
  - ⚠ **Trap:** "1 April 2021 to 31 March 2026" is WRONG (UPSC 2026)
  - !! Not in your sources: whether RGSA has been extended after 31 March 2026.
- **Funding pattern:**
  - General states = **60:40** (Centre:State)
  - NE & hilly states = **90:10**
  - UTs = **100%** Central
- **Merger:** **Backward Regions Grant Fund (BRGF)** merged into RGSA (APPSC-GS 2018)
- **Performance data:**
  - 2025-26: **₹394.84 crore** released; **8,67,915** participants trained
  - FY25: **35 lakh+** trained; Training of Trainers on **own-source revenue**
# 2. Institutional training bodies
- **National level:** **NIRDPR**, **Hyderabad**
- **State level:** **SIRDs**
# 3. Digital interventions & property rights
- **eGramSwaraj:** Integrates panchayat **planning, accounting and reporting** (launched with SVAMITVA on **24 April 2020**)
- **AuditOnline:** Online audit of panchayat accounts
- **SVAMITVA (24 Apr 2020):**
  - Implemented by **Survey of India**
  - Gives **"Record of Rights"** for rural homes + a **property-tax baseline**
```

## When done
Run `python3 tools/restructure_check.py <book> <NNN>` from the repository root. It lists pages that lost a
number, changed a gap line, lost a table or many bold terms. Fix every listed page in your output file and run
it again until it prints `N/N pages pass`.
