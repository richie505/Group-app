# a071 report

a071: keyword angles 44/52 covered (8 partly), APPSC PYQ angles 19/21 covered, 20 notes gaps, 35 new MCQs, 147 reworded

Dry run: `python3 tools/angle_add.py data/angle2/out-a071.json --dry` -> 35/35 new MCQs and 147/147 rewordings would be applied, none refused.

| Unit | Topic | Keywords C/P/M of T | APPSC PYQs covered | Notes gaps | New |
|---|---|---|---|---|---|
| U0427 | 2:153 India-USA | 9/0/0 of 9 | 0/0 | 2 | 3 |
| U0428 | 2:154 India-Russia/EU/Japan/Israel/Gulf/Africa | 6/2/0 of 8 | 0/0 (1 misfiled) | 3 | 7 |
| U0429 | 2:155 United Nations organs | 7/2/0 of 9 | 4/5 (1 misfiled) | 5 | 9 |
| U0430 | 2:156 UN agencies | 7/2/0 of 9 | 9/9 (1 misfiled) | 4 | 6 |
| U0431 | 2:157 Bretton Woods, ADB, AIIB, NDB | 7/2/0 of 9 | 6/6 (2 misfiled) | 4 | 7 |
| U0432 | 2:158 WTO | 8/0/0 of 8 | 0/1 | 2 | 3 |

## What was missing
- **U0427**: no keyword gaps. Notes gaps were the Oct 2025 10-year defence framework (signatory) and Malabar's partners. Also added a direct question on the 123 Agreement, which was only asked inside a chronology.
- **U0428**: #1 first Indian PM to visit Israel (the APPSC-G2 2017 angle in the notes had no own MCQ). #2 Africa: MGCC Niamey, e-VidyaBharati, Sierra Leone mission. Notes gaps: BrahMos name, Abraham Accords, JIMEX. Misfiled: y6c4b4fc43cd (garbled Indo-UK JETCO question).
- **U0429**: APPSC PYQ yeb12ec0f3b3 (P5+1, Germany): P5 membership angle. #5 UNSC term and veto Article. #8 first Hindi UNGA speech (Vajpayee 1977). Notes gaps: 193 members, Art. 18, Guterres's country, Vijaya Lakshmi Pandit as UNGA President. Misfiled: ydb9a68a6119 (UGC).
- **U0430**: #3 India chaired the CND (only a statement distractor before). #4 WHO GCTM Jamnagar (only a non-APPSC PYQ before). Notes gaps: UNICEF founding year (APPSC 2019), IMO HQ, WIPO HQ, IAEA as a related organisation. Misfiled: ycf83c232283 (Nadia Murad).
- **U0431**: #3 heads: Ajay Banga (the APPSC PYQ asked from the other side) and the IMF MD (DSK PYQ angle). #7 ADB's Japanese-president convention. Notes gaps: SDR renminbi and 'paper gold', IFC year, Green Hydrogen Mission lender. Misfiled: y85789debc25 (Wall Street Journal), y4d36fa5aa62 (Tata PTT).
- **U0432**: APPSC PYQ y7ceb4c39a01 (phytosanitary = non-tariff barrier) had no own MCQ on the barrier type. Notes gaps: WTO Director-General, and SPS asked directly.

## Rewording
147 own fill-in stems ("...:", "... in:") across the six topics were turned into direct APPSC-style questions ("In which year...?", "Where is the headquarters of...?", "Who among the following...?"). Options and keys are unchanged. Two ordinal "____" stems (nebd5f670b9b, f9d3a9d7772e1) were left as they are because a direct question would read awkwardly.

## Note for review
The notes put the INSTC "via Chabahar", but the existing MCQ n1ea2b652abf has Bandar Abbas as its key. Only its stem was reworded; it was not changed otherwise.
