# Runbook for one job of the 2026 rebuild (all subjects, APPSC Complete)

You are a Claude Code helper doing ONE job. The owner's method was proven on the Satavahanas pilot
(`data/notes2026/pilot/`, read `PILOT.md`; the pilot's files are your worked example of every output). Never use the
Anthropic API. Do not edit `app/`, do not commit, do not touch other jobs' folders. Keep every scratch file (scripts, drafts) in `data/notes2026/runs/<job>/work/`, never in a shared scratchpad. Work only in your run folder
`data/notes2026/runs/<job>/` (it already holds `meta.json`, `pyqs.json`, `all-mcqs.json`, `old-notes.txt`).

Sources: `data/notes2026/src/INDEX.md` lists the local text library built from the owner's Drive (PDF + .txt per
source, with page ranges per topic). Priority: NextGen IAS notes → NextGen Rocket Sheets → Rocket CA → CARE → NextGen
general → (Carpediem CA = the app's own current affairs) → PMF CA → PMF Notes → Budget / Economic Survey → Praveen CA →
other Drive material → the app's current notes (`old-notes.txt`) → web search. If INDEX.md lacks your topic or is not
there yet, use `grep -il` over `data/notes2026/src/**/*.txt`, and if still nothing, the Google Drive tools (ToolSearch
"select:mcp__Google_Drive__search_files,mcp__Google_Drive__download_file_content"; folder ids in `SOURCES.md`; save
downloads under `data/notes2026/src/<subject>/`).

## 1. Keys: every PYQ in pyqs.json (the most important part)

The printed key is NOT evidence. Book answer grids, "official" keys and the app's old keys are often wrong. Lesson from
the pilot: the old notes said "Bellary theory = R.G. Bhandarkar (APPSC 2017 key)"; that was false — V.S. Sukthankar
placed the Satavahanas' home in Bellary from the Myakadoni inscription. A wrong key copied into the notes turns into a
wrong "fact" and a wrong "trap". So for EVERY PYQ:

1. Work out the answer yourself from the sources (NextGen first), without looking at the printed key.
2. Compare with the printed key (`a`, or `at` for a flashcard; `a` = -1 means no key).
   - Agree, and a source states it clearly → `method: "notes"`.
   - Disagree, the sources are silent or ambiguous, two sources conflict, the fact may have changed (data, schemes,
     appointments, records, districts, "largest/first/latest"), or the existing explanation contradicts the key →
     check at least two more sources in the Drive library (another NextGen file, Rocket, PMF, the standard books in
     "my upsc collection": Laxmikanth, Ramesh Singh, Spectrum, Shankar, NCERT …). Still unsettled → web search
     (official sites: gov.in, PIB, RBI, ISRO, Census, AP govt, NCERT, Britannica, UNESCO; Wikipedia only with its
     cited source). Decide by the verified fact → `method: "generated"`, `why_generated`: conflict / ambiguous /
     outdated / contradiction / not in notes.
   - Never keep a key "because the APPSC key says so" when the verified fact says otherwise. If an official key is
     itself disputed, key the verified fact and say "(official key: X)" in the explanation.
   - No printed option is correct but the correct answer is known (e.g. "the 77th Amendment" when only 85th/86th/… are
     offered; "26 Nov 1949" when only 1950 dates are offered) → do NOT leave it unkeyed and do NOT key the nearest
     wrong option: write `"add_option": "<the correct answer, in the options' style>"` (no `a`); the app adds it as a
     new last option, keys it and shows "⚠ Option added: …" above the explanation. Your x says why each printed
     option is wrong. Same when two printed options are both right only because the stem is loose? No — then key
     the better one and explain.
   - The strict fact differs from the answer most books / official keys give (e.g. "property ceased to be an FR in 1978"
     — most books — though Art. 31 went only from 20 June 1979): key the MOST COMMONLY GIVEN answer and write
     `"dispute": "Most books and keys: <X>. Strictly: <Y> (<source>)."` — the app shows it as a "⚠ Disputed:" line above
     the explanation, so the reader knows both. Use this also when official keys disagree with each other.
   - Only when even the correct answer cannot be established (authorities split, garbled question) → `a: -1` and the
     reason in x.
3. Explanation `x`: 1–3 short sentences — why the key is right, and why the tempting option is wrong. Reuse the notes'
   own wording where the notes state it. No sentence may contradict the key.
4. Outdated: `outdated: "⚠ Outdated: <what changed> — now <current fact> (<source>)"` and an inline "(now …)" in x.
5. `source`: the file + page (e.g. "NextGen Polity - APPSC Exams 07 p.12") or URL that settled it.

`keys.jsonl`, one line per PYQ (write in batches of ~20 as you go, so nothing is lost):
`{"id", "a" (or "at" for k:"f", or "add_option"), "method", "why_generated", "from_notes", "from_notes_src", "x", "outdated",
"source", "changed": true|false, "evidence": ["<each extra source checked when changed or generated>"]}`

The app's own MCQs (ids not starting with "y") in `all-mcqs.json`: you do not re-key them all, but if one's key
contradicts the sources / your notes, add a keys.jsonl line for it too (same fields, `changed: true`).

## 2. Blueprint (topic jobs): `blueprint.md`

As in `pilot/blueprint.md`, shorter: PYQ count by sub-topic, exams and years, angles (factual recall, chronology,
match, statements, NOT/wrong pair, assertion-reason, map/place, definition, current linkage), repeats, and what the
old notes cover heavily that is never asked.

## 3. Rebuilt notes (topic jobs): `notes/row-<N>.md` for each row in meta.json "rows"

Format exactly like `pilot/notes/row-46.md`: `=== <Sub-section title>` starts a sub-section (the app shows each as a
page); inside: `# Heading`, `- **Label:** text`, `  - sub-bullet`, markdown tables (`| a | b |` + `|---|---|`),
`> exam angle`, `~~ Sources: …` (last line of each sub-section), `**bold**` for the answer words. Rules:
- Light and exam-focused; sub-sections ordered and sized by the blueprint weight; every sub-section maps to tested
  content; no filler. Keep every fact a PYQ or an own MCQ needs (so every MCQ can be linked to a line).
- NextGen first, then Rocket, then the rest. Where sources conflict, settle it (web if needed) and write the settled
  fact with its source; never write a "trap" from an unverified key.
- Current-affairs linkage where PYQs show it; dated facts carry their date ("as of 2026").

## 4. Mapping: `mapping.json` — every MCQ in all-mcqs.json (PYQs and own MCQs)

Run `python3 tools/notes2026_jobs.py number <job>` to get `numbered/row-N.txt` (lines `[S:B]`, table rows `[S:B.R]`).
`{"<id>": {"row": N, "sub": S, "lines": ["S:B", "S:B.R"]}}` — exactly one sub-section (the dominant angle decides), 1–3
lines that state the answer. If no line states it, add `"add": "- **…:** …"` (one bullet that will be appended to that
sub-section) instead of / besides lines. A PYQ that belongs to a different topic of the same book:
`{"<id>": {"move_row": N}}` (row titles: `data/notes2026/rows-book<B>.txt`); a PYQ of another SUBJECT (another book): `{"<id>": {"move_book": B, "move_row": N}}` — still key it. Use sparingly.
For `keys` jobs the notes already exist in `notes/` (from the topic job): map onto them, use "add" for missing facts.

## 5. Finish

`python3 tools/notes2026_jobs.py check <job>` must print 0 problems. Then create the empty file `DONE` in the run folder
and reply in a few lines: PYQs checked, keys changed (list id: old → new, one-line reason), generated count, outdated
count, -1 count, notes sub-sections, and anything the owner should look at.

## Settled facts (apply everywhere)
- India's coastline is officially revised to **11,098.81 km** (PIB Release 2198800, 4 Dec 2025; Ports Ministry circular 29 Apr 2025): Gujarat 2,340.62 km, **Tamil Nadu 1,068.69 km (2nd)**, **Andhra Pradesh 1,053.07 km (3rd; old 973.7 / "974 km, 2nd")**. Key coastline PYQs to the current figures with an `outdated` line giving the old answer.
- RBI policy rates (job b3-r082, RBI MPC minutes prid=63839, 7 Oct 2026): repo **5.50%**, SDF 5.25%, MSF and Bank Rate 5.75%; SLR 18%; Governor **Sanjay Malhotra**. Use these as "now" in outdated lines.
- India's Ramsar sites: **103** (daily CA 20 Oct 2026: Sukhna Wetland, Sauj Jheel added); tiger reserves **58** (Sep 2026); tiger count 3,682 (2022). Use as "now".

## Owner rule on official keys (clarified)
Where an official key (APPSC/UPSC/other commission) or the answer most books give differs from the stricter fact, KEY THAT OFFICIAL / MOST-TOLD ANSWER and add `"dispute": "Official key / most books: X. Strictly: Y (source)."` — even when you think the official key is wrong, as long as that answer is among the printed options and is a defensible/commonly taught reading. Exception: an official key that is a flat factual error that books do NOT teach (e.g. Lutyens → Chandigarh) is keyed to the fact, with "(official key: X)" in x. Use `add_option` only when no printed option is defensible (e.g. a printed key that is a plain factual impossibility such as a wrong range name or a year with no source at all). Do not unscore (-1) a printed key just because you could not verify it — keep it and say "printed key, not verified" in `source`.
