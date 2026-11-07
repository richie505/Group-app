# a147 – angle check report

Packet units: U0821-5 (6:62), U0821-6 (6:63), U0821 (6:58–6:63), U0822-1 (6:64), U0822-2 (6:65), U0822-3 (6:66).
Keyword totals count the 27 numbered keywords plus N1/N2 (U0821) or 18 plus N1 (U0822).

| Unit | Keywords C/T (partly) | APPSC PYQ angles C/T | Notes gaps | New MCQs |
|---|---|---|---|---|
| U0821-5 | 20/29 (4) | 0/0 | 6 | 7 |
| U0821-6 | 27/29 (2) | 6/6 | 9 | 12 (2 web) |
| U0821 | 27/29 (2) | 8/9 | (counted under -5/-6) | – |
| U0822-1 | 18/19 (1) | 0/1 | 6 | 9 |
| U0822-2 | 19/19 (0) | 0/3 (+2 misfiled) | 9 | 12 |
| U0822-3 | 19/19 (0) | 0/0 | 7 | 7 |

## What was missing
- **U0821-5 (Apr–Nov 2025):** #16, #19 (MC13 Abu Dhabi), #24, #26 only partly covered. #5, #8, #23, #27 and N2 have no facts in this period's notes; 6:63 covers them. Notes gaps: Maratha Military Landscapes as the 44th site (12 forts), MC13 venue, WEO Oct 2026 India projection, South Africa's ICJ case, Indus Waters Treaty 1960, Atomic Energy Act 1962.
- **U0821-6 (Overview):** #21 IDA functions are not in the notes. A web fact was added (World Bank IDA page, Wikipedia): IDA was set up in 1960 and gives zero- or low-interest credits and grants to the poorest countries. N2 was only partly covered: the France MCQ asked the date, not the country. Notes gaps: INTERPOL in Lyon, UN Alliance of Civilizations, Makli necropolis, Bhutan rabies elimination, Silver Notice, Malta as the ISA's 119th member, APEC 2025 in Gyeongju, Washington Accords, OECD with 38 members.
- **U0821 (whole unit):** the APPSC oil-spill PYQ (y160fbcec8c6 / y53e6abf7fc8, Trinidad and Tobago, in 6:60) has no own MCQ, and the notes do not mention the oil spill. 6:60 belongs to packet a146 (U0821-1..4), so I wrote nothing for it here to avoid duplicates. I also did not reword stems in 6:58–6:61, which belong to a146.
- **U0822-1 (Sep–4 Nov 2026):** #9 defence platform -> country of origin was only partly covered. APPSC PYQ y130e2c1b0f4 (national fish) is now covered by MCQs on Hilsa as Bangladesh's national fish and West Bengal's state fish. Notes gaps: 2027 Year of Friendship with Vietnam, Kakinada green ammonia (Belgium), capital of Yemen, Ajeya Warrior, Samudra Shakti, Pitch Black.
- **U0822-2 (Jun–Aug 2026):** three APPSC PYQ angles had no own MCQ: Shia-majority Iran, pepper producer vs Singapore, first women to walk to both poles. y79a924fa7fe / y1fcbe7f6429 ("Every Indian is a VIP") are misfiled. **Conflict:** the notes say Ann Daniels and Caroline Hamilton are British, but PYQ y0ad855afd11's key is New Zealand. The new MCQ asks who they were and avoids their nationality. Notes gaps: Malabar members, Indonesia's independence (Soekarno), IFC-IOR in Gurugram, King Haakon VIII, Myanmar border states, Operation Sunrise, Treaty of Sugauli, Cambodia as the latest UPI country, Maitri Setu.
- **U0822-3 (Mar–May 2026):** two facts the notes mark "asked before" had no MCQ: Merz elected in the second round, and Indo-UK JETCO (2011). Other gaps: Midnight Hammer, ITLOS in Hamburg, Punatsangchhu-I (1,200 MW), PRAGATI full form, IFR 2026 at Visakhapatnam.

## Rewordings
229 own fill-in stems in 6:62–6:66 were turned into direct APPSC-style questions. Facts, options and keys are unchanged.

## Checks
`angle_add.py --dry`: 47/47 new and 229/229 rewordings would be applied, none refused. `notes_fix.py apply --dry` (NOTES_APP=complete): 1/1 ok.
