# a042 report (U0253-U0258, book 1 rows 252-257)

a042: keyword angles 99/120 covered (20 partly), APPSC PYQ angles 84/114 covered, 43 new MCQs, 216 reworded

| Unit | Topic | Keywords C/P/M of T | APPSC PYQs covered | New | Reworded |
|---|---|---|---|---|---|
| U0253 | 1:252 Ambedkar's social thought | 8/0/0 of 8 | 1/1 | 0 | 18 |
| U0254 | 1:253 Constituent Assembly | 7/1/1 of 9 | 2/2 | 4 | 22 |
| U0255 | 1:254 Nehru era | 6/1/0 of 7 | 1/2 | 3 | 27 |
| U0256 | 1:255 Andhra Movement, Andhra State 1953 | 65/17/0 of 82 | 73/102 | 32 | 109 |
| U0257 | 1:256 Wanchoo Committee | 7/0/0 of 7 | 6/6 | 0 | 19 |
| U0258 | 1:257 Press in the Andhra Movement | 6/1/0 of 7 | 1/1 | 4 | 21 |

## What was missing

- **U0253**: nothing. Only rewordings.
- **U0254**: #7 origin of the idea (M.N. Roy in 1934, INC in 1935) had no own MCQ. #4 criticisms were only partly covered: no MCQ on the Socialist Party's demand for dissolution or on the restricted 1935 franchise.
- **U0255**: #4 chronology was only partly covered (no own sequence MCQ). The angle of APPSC PYQ ye2873f4374c (author of a book) had no own MCQ, so I added author MCQs on Nehru's books. Misfiled: yb427e32ba69 ("Knowledge is Power"), y3d09fed7db5 (Gentlemen's Agreement year).
- **U0256** (CORE): 17 keywords were only partly covered:
  - #1/#77: formation date, budget presenter, Speaker
  - #3/#78: Partition Committee chairman; PSP backing Tirupati
  - #8/#10: Sri Bagh place and signatories
  - #9/#65: Swami Sitaram and Vinoba Bhave; place of the fast
  - #11: Gurunatham in The Hindu
  - #12: Panagal's Cooum boundary
  - #21: first APCC office-bearers
  - #26: Bapatla date and secretary
  - #42: Anandacharlu (1891) and Sanjiva Reddy as INC Presidents
  - #55: Andhra University's first HQ and year
  - #59: rival claims for the university seat
  - #68: Sriramulu's fast (start date, place, day of death)
  - #79: last CM
  
  29 APPSC PYQ angles had no own MCQ (listed in out-a042.json). Misfiled: yda3c6310f22, ye6fc76f21a6, y92fc5df2945, yfcdadfbc57a.
- **U0257**: nothing. Only rewordings.
- **U0258**: #2 first Telugu newspapers was only partly covered (no own MCQ on Satyadoota 1835 Bellary or on Andhra Prakasika as the first political journal).

Check: `python3 tools/angle_add.py data/angle2/out-a042.json --dry` -> 43/43 new MCQs and 216/216 rewordings would be applied, none refused.
