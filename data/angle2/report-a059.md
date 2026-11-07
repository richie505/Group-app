# a059 report

a059: keyword angles 117/130 covered (13 partly), APPSC PYQ angles 30/43 covered, 14 notes gaps, 40 new MCQs, 200 reworded

| Unit | Topic | KW covered/partly/missing (of total) | APPSC covered/counted | Notes gaps | New |
|---|---|---|---|---|---|
| U0355 | 2:81 | 26/7/0 (33) | 8/10 | 3 | 12 |
| U0356 | 2:82 | 22/2/0 (24) | 8/11 | 2 | 8 |
| U0357 | 2:83 | 24/1/0 (25) | 6/8 | 2 | 5 |
| U0358 | 2:84 | 22/2/0 (24) | 4/8 | 3 | 7 |
| U0359 | 2:85 | 15/1/0 (16) | 1/3 | 2 | 6 |
| U0360 | 2:86 | 8/0/0 (8) | 3/3 | 2 | 2 |

## What was missing
- **U0355**: partly #4/#10 (Eleventh Schedule count asked only by PYQ; subject identification), #9 (count of Part IX Articles), #12 (243A powers left to State Legislature), #17 (fresh polls within six months), #22 (States short of 50% women), #26 (first State to implement the 73rd). PYQ yf66f36fa20c (Panchayat own tax domain), PYQ y90036ad3dc9 (Eleventh Schedule count). Notes gaps: J&K outside Part IX till 2019; 5th AP SFC chair (S. Rathna Kumari); UIDF via National Housing Bank.
- **U0356**: partly #12 (243Q, 243ZA), #20 (MPC two-thirds elected). PYQ y39aa98846b3 (ULB type -> area), PYQ y95db8d973f6 (number of AP municipalities), PYQ y1ed691df841 (Ward Committee 3 lakh). Misfiled: y7218fb74dea (ration cards 2005). Notes gaps: "Nagarpalika Act" name; Cantonments Act 2006.
- **U0357**: partly #22 (ST Articles number game: 332, 46, 244A, 338A, 342). PYQs yc0f0d6f8613 / y4d08c850e30 (ST Order amended by AP Reorganisation Act). Misfiled: y77dcb7d114d (Ease of Living Index). TAC-size PYQs counted covered by the own TAC-composition MCQ. Notes gaps: Income Tax s.10(26) exemption; Seethampeta ITDA district.
- **U0358**: partly #1 (Nagar Panchayat count), #6 (first AP PR law, 1959). PYQs y3ddf42bdc04 / y0eea9028d48 / yf24cc569f6a (Gram Sabha membership, written as the 243(b) definition), PYQ y4e8e1be11bc (Article 243G). Misfiled: y43ce9b6f7c6 (OncerTM), y1f724c03007 (drinking-water pH). Notes gaps: Kasu Brahmananda Reddy; AIIB water project; Uniform Mutation Fee Bill 2026.
- **U0359**: partly #4 (Simon, Lindblom). PYQ yead99673583 (social justice), PYQ y1b58d364fa7 (AP Social Welfare Fund). Notes gaps: general health services not a targeted welfare service (APPSC-GS 2019 area); RSBY as social protection.
- **U0360**: nothing missing. Notes gaps: PM's Communication Wing; Baxi's fears (NOT electoral).

Rewordings: 200 own-MCQ fill-in stems ("…:" / "… the:" / "… in") turned into APPSC-style direct questions, with the same fact, options, order and key. Assertion-reason, chronology and statement stems left alone.

Check: `python3 tools/angle_add.py data/angle2/out-a059.json --dry` -> 40/40 new MCQs and 200/200 rewordings would be applied, none refused.
