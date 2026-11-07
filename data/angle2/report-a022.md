# a022 report

a022: keyword angles 58/71 covered (13 partly), APPSC PYQ angles 10/13 covered, 20 new MCQs, 160 reworded

All APPSC PYQs in each topic are counted, except one plainly misfiled (U0135 yb4a3720c44e, Gulmika in Ashoka's Maski inscription). All new MCQs use APPSC question framing. 160 own-MCQ stems (fill-ins ending ':' or '____', and wordy stems) are reworded into APPSC question form. Each keeps the same fact, the same options in the same order and the same key.

| Unit | Topic | KW covered/partly/missing (of total) | APPSC covered/relevant | New |
|---|---|---|---|---|
| U0133 | 1:132 | 8/0/0 (8) | 0/1 | 2 |
| U0134 | 1:133 | 10/4/0 (14) | 0/0 | 6 |
| U0135 | 1:134 | 8/0/0 (8) | 1/1 (+1 misfiled) | 0 |
| U0136 | 1:135 | 12/5/0 (17) | 4/6 | 5 |
| U0137 | 1:136 | 6/1/0 (7) | 1/1 | 2 |
| U0138 | 1:137 | 14/3/0 (17) | 4/4 | 5 |

## What was missing
- **U0133**: PYQ y44615cc88a3 (identify a Jat leader from an epithet or deed): no own MCQ asked "which Jat leader". Added Gokula (1669 Mathura revolt) and Rajaram (Sikandra plunder).
- **U0134**: #1 and #10: who introduced mansabdari and where the model came from (APPSC GS 2018 area); #3 and #10: who introduced du-aspa sih-aspa (Jahangir), and the rule of 20 horses per 10 sawars; #11: full ascending order of units and the faujdar's function. All partly covered.
- **U0135**: nothing missing. yb4a3720c44e is misfiled (it belongs to Ashoka's inscriptions).
- **U0136**: #2 and #11: share of produce marketed (~25%, APPSC G2 2017 area); #6 and #13: Surat as Bab-ul-Makka; #12: Manucci and Pelsaert, which country each came from. All partly covered. PYQ y9ca7d30c433: Vijayanagara agriculture through tanks, dams and wells. PYQ yc4ecbe03869: traveller -> country.
- **U0137**: #2: origin of Nauroz (Persian) and tuladan (Hindu), partly covered.
- **U0138**: #3: builder of Bibi ka Maqbara (Azam Shah) and place of Sher Shah's tomb (Sasaram); #5 and #11: why the Buland Darwaza was built (Gujarat victory) and its name "Gate of Magnificence". All partly covered. Also added a NOT question, "not built in Akbar's reign", for the APPSC G1 2024 angle that keeps coming back.

Check: `python3 tools/angle_add.py data/angle2/out-a022.json --dry` -> 20/20 new MCQs and 160/160 rewordings would be applied, none refused.
