# RocketOne step 1: one Rocket Sheets chunk -> rows filed under the Group 1 Prelims syllabus

You get one chunk of the NextGen "Rocket Sheets" (text made by pdftotext from the PDF): `work/rocket/chunks/<chunk>.txt`.
Write `data/rocketone/rows/<chunk>.jsonl`: every fact of the chunk as one JSON line, tagged with the Group 1 Prelims
syllabus line it belongs to. A later step writes the notes from these rows, so the rows must be complete and exact.

## The one rule
Only what Rocket says. Do not add a fact, a date, a full form, an explanation or a correction from your own knowledge,
and do not drop anything, even if it repeats, looks trivial or looks wrong. (Wrong lines are settled in a later step.)

## Reading the chunk
- `=== AP History · Sheet #10 · p.15` starts a page. The `src` of its rows is `"AP History #10"`.
- Most pages are tables. pdftotext wraps long cells over several lines and lifts some cells a line above or below their
  row: put each row back together by reading the columns. The first line(s) of a table are its column headings.
- Some pages are bullets or prose under headings.
- Mend PDF damage: a dropped "ti"/"ft"/"fi" ("administra on" -> "administration", "a er" -> "after"), a word split by
  a line break. Change nothing else: keep Rocket's spellings of names, its numbers and its wording.

## One JSON object per line
Table row:
`{"leaf":"A1/11","topic":"Satavahana administration","src":"AP History #10","h":["Period / Dynasty","Officer / Body","Key Fact"],"c":["Satavahana","Gramani","Jurisdiction over 5 or 10 villages"]}`
Bullet or sentence:
`{"leaf":"B1/7","topic":"Amendment procedure","src":"Indian Polity #23","under":"Crucial Rules","t":"No Joint Sitting: each House must pass the Bill independently with special majority; if one House rejects it, the Bill fails completely."}`

- `h` and `c` have the same number of entries; an empty cell is `""`. A table with no headings: leave `h` out.
- `t`: one fact per line. A bullet with sub-bullets that only make sense together stays one line (join with "; ").
- `under`: the Rocket heading the line sits under (table title, section heading), when there is one. It gives the row
  its context ("EOS-05", "Crucial Rules", "Imp Amendments").
- `topic`: a 2-5 word label of the sub-topic, the same wording for rows that belong together in this chunk.
- A row that holds two unrelated facts for two different syllabus lines: file it under the line of its main subject.

## `leaf`: the syllabus line
The 237 lines are in `work/rocket/leaves.txt` (code, section, text). Choose by what the row is about, not by which
Rocket subject it is printed in: a "Firsts" sheet has rows for many lines. Use the most specific line that fits.
- Dynasties, rulers, their inscriptions, coins, books, temples, officers, taxes: the dynasty's own line (A1-A3). A row
  that compares several dynasties goes to the first one named.
- History that the list does not name (Ikshvakus, Vishnukundins, Salankayanas, Pallavas, Musunuri, Velamas, Qutb Shahis
  before the Nizam, prehistory, Marathas outside A4/3, general art and culture with no dynasty): `"X"`.
- Asaf Jahis / Nizam, Europeans and the British in Andhra: A4/6 (or A4/1 for the trading companies). Andhra movement,
  Andhra State 1953, Andhra Pradesh 1956, bifurcation: A6/8. Andhra reformers, press, library movement: A5/5.
- Polity rows not covered by a narrower line: B1/8 (significant provisions). Elections, parties: B3/1 or B1/8.
- Indian society: rights and welfare of a group -> B5/1-B5/5; tribes, religions, languages, races -> D3/6; reform
  movements -> A5/4; pure sociology (family, kinship, caste theory, thinkers) -> `"X"`.
- Physics, chemistry, biology basics: E18/2. Scientists and inventions: E18/5. Diseases, nutrition, health: E22/13.
  Biotechnology / genetics: E22/10 or E22/12. Nuclear: E21/6. Space: E20. Computers, internet: E19.
- Environment: E22/1-E22/8; national parks, sanctuaries, tiger reserves, Ramsar sites: D2/9; vegetation: D2/8.
- Disaster management (law, NDMA, policy, general): E22/9; earthquakes, landslides: D2/4; cyclones: D1/10; floods,
  tsunami, drought: D1/13.
- Geography rows about Andhra Pradesh use the same D lines (they cover World, India and AP). AP economy: C5.
- Nothing fits: `"X"`. Do not force a row into a line that is not about it.

## Finish
Run `python3 tools/rocketone.py check-rows <chunk>`. It lists format errors and Rocket lines whose words are not in your
output. Fix them (a line may stay "not found" only if it is a column heading or a page title) and run it again until it
prints `OK`. Write only your own `.jsonl` file (in parts with several Write/append steps if it is long); do not edit
other files and do not commit. Reply with one line: the chunk, the number of rows, and anything odd you saw.
