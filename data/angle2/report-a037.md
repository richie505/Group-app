# a037 report

a037: keyword angles 49/59 covered (10 partly), APPSC PYQ angles 18/25 covered, 18 new MCQs, 111 reworded

Coverage was judged on existing own MCQs (before additions). APPSC PYQs plainly off-topic are excluded from the count and listed as misfiled. Existing own-MCQ stems that were ':' / '____' fill-ins or wordy were reworded into APPSC question form (same fact, options, order and key).

| Unit | Topic | KW covered/partly/missing (of total) | APPSC covered/counted | New |
|---|---|---|---|---|
| U0223 | 1:222 | 8/1/0 (9) | 7/8 | 3 |
| U0224 | 1:223 | 5/2/0 (7) | 0/0 | 3 |
| U0225 | 1:224 | 15/2/0 (17) | 4/6 | 4 |
| U0226 | 1:225 | 8/1/0 (9) | 6/8 | 3 |
| U0227 | 1:226 | 7/1/0 (8) | 1/3 | 2 |
| U0228 | 1:227 | 6/3/0 (9) | 0/0 | 3 |

## What was missing
- **U0223**: #4 partly: ban years - Hyderabad State ban (1946) and 1934 imposition not asked by own MCQs (only lifting); PYQ y8840dbfc6ef Doddi Komaraiah killing as trigger of the Telangana struggle angle (own MCQ asks only the place); misfiled: y5192031ec24 (Prathivadi Bhayankarachari, Revolutionary Society in Godavari - not in notes)
- **U0224**: #1 partly: British PM who announced the Communal Award; group given separate electorate for the first time; #4 partly: first president of the All India Anti-Untouchability League (G.D. Birla); misfiled: y5e2ba4063e4 (first best actress Oscar)
- **U0225**: #5 partly: Central Legislative Assembly elections held under the 1919 Act (years); #17 partly: elections under the 1919 Act vs the 1935 Act; PYQ y607855b08f7 Section 96(C) -> Public Service Commission angle (own MCQs ask only the year it was set up); PYQ y8a6973dbce1 Act/reform that introduced communal electorates angle (only a pair in a NOT-matched MCQ)
- **U0226**: #5 partly: Round Table Conferences - years/venue and agenda not asked by own MCQs; PYQ yda13ff6b5f5 year of a Round Table Conference angle; PYQ ya9e402b46e9 purpose/agenda of the Round Table Conference angle; misfiled: yf7c7ce902e0 (Commonwealth of India Bill - not in notes), y51e37e4964d (bank nationalisation 1969)
- **U0227**: #1 partly: reason for the Congress ministries' resignation (own MCQs give only date/sequence); PYQ y092d3b8c4f4 Sri Bagh Pact year angle (own MCQ asks only the house); PYQ y45829f22a53 reason for the resignation of Congress ministries in 1939 angle
- **U0228**: #1 partly: drafter of the Lahore Resolution (Sikandar Hayat Khan) only in a non-APPSC PYQ; #4 partly: 'Divide and Quit' slogan -> Jinnah; #7 partly: author of 'The Man Who Divided India' (Rafiq Zakaria) only as a distractor

Check: `python3 tools/angle_add.py data/angle2/out-a037.json --dry` -> 18/18 new MCQs and 111/111 rewordings would be applied, none refused.
