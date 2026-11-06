# Packet v17 – second-look report

v17: restore 65 (2 fixed), keep out 94 (dup 89, trivia 3, off-syllabus 0, unfixable 2)

Input: 159 removed MCQs across 27 topics (book 2 rows 159–169; book 3 rows 0–17).
Dry run: `python3 tools/relevance.py restore data/relevance/review/restore-v17.json --dry` -> "65 MCQs would be restored", none invalid.

## Rule applied
- A question was kept out as a duplicate only when a PYQ or another live MCQ asks the same fact the same way (same stem idea, same answer), or when a live item's key already states it in full (for example, a combined-answer option).
- A question was restored when it asks the fact directly but the live item only has it as a wrong option in a "NOT correct" or "wrongly matched" question. It was also restored when it asks the fact from the other direction, or when the live item is a multi-pair match or a match-the-list item.

## Restored with fix (2)
- nff04e35acf6: premise corrected. 42.4% is the agriculture workforce share from PLFS Q2 FY26, not 2022-23.
- n2cfd680a698: stem changed from "2024-25" to NITI National MPI 2023 (NFHS-5, 2019-21), where 6.06% is correct.

## Examples restored
- f3e7c2cfdfa46: "Who chairs the DAC?" PYQ ydf546abbc5b asks what is not true of the CDS.
- n2332365b78c: names I2U2 from its member list. PYQ y485a3ac66c6 goes the other way.
- fa931fa62e615: same wage-goods fact from the other direction.
- fd868a3a75a76: number of AP Anganwadi centres. This is an AP fact, so it is not minor trivia.

## Examples kept out
- Duplicate: nd313e2d1540 repeats PYQ yaf3a4fe218f (first BRIC summit, Yekaterinburg). n74c91f7bb1c is identical to PYQ y2e125b6c3dd.
- Duplicate with a key conflict: fae2aae1f8953 has the same A/R as PYQ ybddfa5be0cd. fb92e15615124 asks the same question as PYQ yb0fd8c6ab43.
- Trivia: fc6f63e867f71 (number of NIC service types), f5a6ad320503f (rolling plan outlay), f3d0222164e59 (date Amitabh Kant took charge).
- Unfixable: nafb3ddd6061 and ffbb2725dc05e. The "chief objective of planning" question conflicts with the APPSC 2017 key (yf870674b552), and it cannot be keyed without ambiguity.
