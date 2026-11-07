# a015 report

a015: keyword angles 69/79 covered (9 partly), APPSC PYQ angles 84/98 covered, 23 new MCQs, 149 reworded

| Unit | Topic | KW covered/partly/missing (of total) | APPSC covered/counted | New |
|---|---|---|---|---|
| U0091 | 1:90 | 7/0/0 (7) | 0/0 | 0 |
| U0092 | 1:91 | 7/0/0 (7) | 4/6 | 2 |
| U0093 | 1:92 | 16/2/1 (19, incl. N1-N2) | 41/44 | 6 |
| U0094 | 1:93 | 11/2/0 (13) | 12/17 | 4 |
| U0095 | 1:94 | 20/4/0 (24) | 18/21 | 7 |
| U0096 | 1:95 | 8/1/0 (9) | 9/10 | 4 |

## What was missing
- **U0091**: nothing; all 7 keyword angles have own MCQs (no APPSC PYQs in topic).
- **U0092**: PYQs yfcd1f9b41ed / yd23e4d6efb9 (Yadava language) had no own MCQ -> 2 new (language of scholarship; Marathi statements). y7b1f7c057e7 (Kridabhiramam, Orugallu) misfiled.
- **U0093**: #3/#12 Ganapatideva's 1263 defeat by the Pandyas (PYQs y4e673c37b9a, yf066de05a4b) -> 2 new (Muttukur; Nellore lost); #13 first overlords Rashtrakutas (missing) -> 2 new; PYQ ye66d2a2a9dc unifier of Andhradesa -> 2 new (Ganapatideva/Telugudesam; second after Satavahanas). Misfiled: ye502d5759c7 (Gangadevi's guru), yb97e39bc1ad (Malkapuram/Pasupata).
- **U0094**: #2/#8 captor of Prataparudra (PYQs y8420a397ecd, y98e6cb01146, yfa4f2df1833) -> 2 new (Ulugh Khan later Muhammad bin Tughlaq; under Ghiyasuddin); PYQ y45c92ad0d36 Vidyanatha = Agastya -> 1 new; PYQ y79555460663 Gangadevi disciple of Agastya -> 1 new.
- **U0095**: #1/#16 Chitrameli and Ubhaya Nanadesi meaning -> 3 new; #2/#17 Motupalli = Desiyakonda Pattanam (PYQs y0ddee7b7ae9, y5cddb6b388e) -> 2 new; PYQ y9609aa75f13 Tirthas = ministers -> 2 new. Misfiled: y41deeee26ed (Machilipatnam, Golconda 1600s).
- **U0096**: #7 Kapalikas from Pasupata and Kalamukha centres (partly) -> 2 new; PYQ yc6e6f7c8c4a Siddhatraya -> 2 new. Misfiled: yd903c610858 (Vipra Vinodinis, Vijayanagara). Note: PYQ y42f818c876c's key (Purushartha Saramu) disagrees with the notes (Ketana's Vignaneswaram); new MCQs avoid that fact.

Rewording: 149 own fill-in stems (ending ':') and wordy stems were turned into APPSC-style direct questions across 1:90-1:95, with the same options, order and key.

Check: `python3 tools/angle_add.py data/angle2/out-a015.json --dry` -> 23/23 new MCQs and 149/149 rewordings would be applied, none refused.
