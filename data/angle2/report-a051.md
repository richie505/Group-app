# a051 report (U0307-U0312)

a051: keyword angles 61/72 covered (11 partly), APPSC PYQ angles 24/27 covered, 13 notes gaps, 32 new MCQs, 166 reworded

| Unit | Topic | Keywords C/P/M of T | APPSC PYQs covered | Notes gaps | New |
|---|---|---|---|---|---|
| U0307 Legislative procedure (CORE) | 2:33 | 13/3/0 of 16 | 5/6 | 3 | 10 |
| U0308 Budget in Parliament (HIGH) | 2:34 | 6/2/0 of 8 | 10/10 | 2 | 5 |
| U0309 Parliamentary committees (HIGH) | 2:35 | 5/3/0 of 8 | 5/5 | 2 | 7 |
| U0310 Privileges, anti-defection (MED) | 2:36 | 21/2/0 of 23 | 1/2 | 2 | 4 |
| U0311 Productivity of Parliament (LOW) | 2:37 | 8/0/0 of 8 | 0/1 | 2 | 3 |
| U0312 Parliamentary vs presidential (MED) | 2:38 | 8/1/0 of 9 | 3/3 | 2 | 3 |

## What was missing / partly covered
- **U0307**: #3 the "notifies his intention" wording for a joint sitting, and the 1978 joint-sitting Bill (partly) -> 2 MCQs; #9 the department that prepares the Budget, the Vote on Account Article, and a cut-motion match (partly) -> 3; #11 adjournment sine die (APPSC 2025, partly) -> 1; PYQ y0d38a7f6035 (Public vs Private Bill follow the same procedure) -> 1, plus a statements MCQ on Private Member's Bills (#7). Notes gaps: pocket veto, Appropriation Bill deemed passed after 14 days, 1978 joint sitting. Misfiled APPSC PYQs (left out of the count): ya939e35fa31 and y0e1ad8641f1 (overriding a Supreme Court decision), ybd95b0dc74f (Inter-State Council).
- **U0308**: #3 Appropriation Bill's automatic repeal clause (partly) -> 1; #7 who set up the Contingency Fund of India, and who controls the Public Account (partly) -> 2. Notes gaps: Finance Bill amendments (reduce or abolish only), Budget 2023-24 presenter (APPSC 2023) -> 2. Misfiled: y1b6ed8b32b5 (Vision 2030 in the 2019 interim budget is not in the notes).
- **U0309**: #1 PAC Opposition-chair convention, identifying financial committees, and a strength statements MCQ (partly) -> 3; #2 a past PAC chairman, Murli Manohar Joshi (partly) -> 1; #6 SC/ST Welfare Committee make-up 20 + 10 (partly) -> 1. Notes gaps: DRSC strength 31 (21 + 10), and a JPC year match -> 2. Misfiled: y4cdf02bbd98 (Lok Sabha quorum).
- **U0310**: PYQ y6bbb7234fd1 (punishments for breach of privilege) -> 1; #7 outsiders can be punished (partly) -> 1; #2 freedom from arrest: civil cases only, 40 days (partly) -> 2.
- **U0311**: PYQ y5013719f7a9 (first Leader of Opposition) -> 1 MCQ asking about the first LoP under the 1977 Act (Y.B. Chavan). This matches both the notes and the APPSC key. I wrote no MCQ asking "who was recognised in 1969", so the ⚠ APPSC key in the notes is not contradicted. Notes gaps: Rajya Sabha productivity in Monsoon 2026, and the State Assembly with the most sittings (Odisha) -> 2. Misfiled: ye5a3ac1f5f2 (AP budget irrigation), y51311816bc8 (NCMP 100 days).
- **U0312**: #1 dual membership six-month rule (partly) -> 1. Notes gaps: in India the PM can come from either House; NCRWC advised keeping the parliamentary system -> 2. Misfiled: y101d1f0e890 (Planning Commission).

## Rewording
- 166 own MCQ stems across rows 33-38 were changed from "...:" fill-ins (and a few stems with no ending) into direct APPSC-style questions ("Which Article ...?", "Who ...?", "In which year ...?", "What happens ...?"). Fact, options, option order and answer are unchanged. Statement, assertion-reason, chronology, match, NOT-type and stems that already end in "?" were left alone.

Check: `python3 tools/angle_add.py data/angle2/out-a051.json --dry` -> 32/32 new MCQs and 166/166 rewordings would be applied, none refused.
