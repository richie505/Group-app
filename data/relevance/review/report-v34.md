# Packet v34: second-look report

Input: 79 removed MCQs (book 6, rows 99–115).

| Outcome | Count |
|---|---|
| Restored | 26 |
| of which restored with fix | 8 |
| Kept out | 53 |
| exact duplicate | 9 |
| trivia | 41 |
| off-syllabus | 3 |
| unfixable | 0 |

`python3 tools/relevance.py restore data/relevance/review/restore-v34.json --dry`: 26 MCQs would be restored, none invalid.

## Examples

- **Restored, other direction:** `ne33ea5043e1` asks who ran 10.09 s; `ca48aac5021043` asks Gurindervir's time.
- **Restored, other direction:** `fb86216cf4f6c` asks where the Santal Hul was proclaimed (Bhognadih); the kept MCQ only says it was not Ranchi.
- **Restored with fix:** `cad608876d0212` key changed from 42 to 44 World Heritage Sites (Jan 2026), which matches the notes.
- **Restored with fix:** `cad2fb387d6551` had an arguable "not Bengali" key. That option now reads "adopted as the National Anthem", which is clearly false because it is the National Song.
- **Restored with fix:** `ff73cd5061ae6` had "Beat Plastic Pollution", the 2025 campaign slogan, as a second defensible answer. It is replaced with the 2024 theme, so only "Ending Plastic Pollution" is right.
- **Restored with fix:** `fb5d43013201a` and `ca41a09c8d8533`: the stems gave the answer away and are reworded.
- **Kept out, duplicate:** `n1122c0754d9` repeats PYQ `yfe7bfe6d338` (IBA Women's Worlds 2025 at Niš).
- **Kept out, trivia:** stamp denominations, AGM venues, counts of matches, plays or votes, IPS cadre, the Insurance Act section number of a minor committee.
