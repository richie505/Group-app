# a023: keyword angles 76/88 covered (12 partly), APPSC PYQ angles 19/30 covered, 28 new MCQs, 217 reworded

Counts are taken before the new MCQs. After them, every partly-covered keyword and every missing APPSC PYQ angle has at least one own MCQ.

| Unit | Topic | Keywords C/T (partly) | APPSC C/T | New |
|---|---|---|---|---|
| U0139 | 1:138 | 13/17 (4) | 2/4 (+2 misfiled) | 9 |
| U0140 | 1:139 | 6/7 (1) | 8/11 | 4 |
| U0141 | 1:140 | 21/24 (3) | 4/4 | 3 |
| U0142 | 1:141 | 13/15 (2) | 1/2 (+1 misfiled) | 5 |
| U0143 | 1:142 | 15/17 (2) | 1/4 | 6 (incl. 1 for U0144) |
| U0144 | 1:143 | 8/8 | 3/5 (+1 misfiled) | 1 (+1 in 1:142) |

## U0139 (Mughal painting, music, literature)
- Partly: #2 Book -> author (Akbarnama 3rd volume, Futuhat-i-Alamgiri, Tuzuk-i-Jahangiri); #3 Tansen's original name and first patron; #7 rise of Urdu/Rekhta; #10 Later Mughal predecessor and sequence.
- APPSC missing: y336834bd15c (Akbarnama volumes), y08cf2890157 (indigenous vocal style). The new MCQ asks which style came from Vedic chanting (Dhrupad). It does not repeat the "non-Islamic" framing, so it does not clash with the APPSC 2010 key "Taraka".
- Misfiled: yf2d29238788 (Indian cinema), y5d828385ba2 (Circumvallation).

## U0140 (Decline, Later Mughals, successor states)
- Partly: #4 Asaf Jahi rulers in sequence (last Nizam, Subsidiary Alliance Nizam).
- APPSC missing: ybbdf16341e2 / y3957fe3d16f (founder of Hyderabad, now asked the other way round, founder -> dynasty) and yb0d7f5ae7fd (a year in Nizam-ul-Mulk's career).

## U0141 (Shivaji, Ashtapradhan, chauth)
- Partly: #2 and #10 (the Mughal side and terms of the Treaty of Purandar: Diler Khan, Sambhaji sent to court); #7 (the deshmukhs' opposition).
- All 4 APPSC PYQ angles were already covered. y391dcb8f988 (first fort, key Purandar against the notes' Torna) was left alone.

## U0142 (Peshwas, Panipat, Anglo-Maratha wars)
- Partly: #2 the Panipat eyewitness chronicler; #9 Peshwa sequence.
- APPSC missing: yb47fc29137f (Pindaris).
- Misfiled: y8006bb2100d (Haindava Dharmoddharak is Shivaji's title and belongs to 1:140).

## U0143 (Bhakti origins, Alvars and Nayanars)
- Partly: #2 Alvars and Nayanars (deity, number, Andal); #10 school -> founder (Dvaita).
- APPSC missing: ycbec2001ce6 / yab0f2e9346a (Alvars and Nayanars by deity) and ya9e6ebbece7 (movement -> leader, now asked as Virashaiva -> Basavanna).

## U0144 (Ramanuja, Madhva, Nimbarka, Vallabha, Ramananda)
- All keywords covered.
- APPSC missing: ye0099ca314c (Palnadu Brahmanaidu -> Ramanuja, now asked the other way round) and y2ac14ff343a (a Bhakti leader influenced by Islam). The 1:143 notes have no such fact, so the MCQ for it went into 1:142, from that topic's Namdev note.
- Misfiled: yaeb3f48c688 (Sahitya Sudha is not in the notes).

## Rewording
217 own stems across 1:138-1:143 were changed from "…:" fill-ins into direct APPSC-style questions ("Who wrote…?", "In which year…?", "Which post did … hold?"). Options and keys are unchanged.

Check: `python3 tools/angle_add.py data/angle2/out-a023.json --dry` gives 28/28 new and 217/217 rewordings, none refused.
