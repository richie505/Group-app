# a000 report (U0001-U0006)

a000: keyword angles 54/61 covered (7 partly), APPSC PYQ angles 35/49 covered, 25 new MCQs, 168 reworded

| Unit | Topic | Keywords C/P/M of T | APPSC PYQ angles C/T | New |
|---|---|---|---|---|
| U0001 | 1:0 Sources of ancient Indian history | 12/1/0 of 13 | 9/13 | 5 |
| U0002 | 1:1 Sources for Andhra history | 7/0/0 of 7 | 12/18 | 6 |
| U0003 | 1:2 Stone Age cultures of India | 9/0/0 of 9 | 2/3 | 2 |
| U0004 | 1:3 Pre-historic cultures of Andhra | 7/1/0 of 8 (incl. N1) | 7/8 | 4 |
| U0005 | 1:4 Pre-/Early Harappan | 8/0/0 of 8 | 0/0 | 0 |
| U0006 | 1:5 IVC discovery, extent, boundary sites | 11/5/0 of 16 | 5/7 | 8 |

## Gaps found and filled
- **U0001:** #2 inscription language/script/vocabulary was only partly covered. PYQs on the language and script of Satavahana inscriptions (y5d70b5b95b5, yfabccf8d5c7) and on Bhattiprolu's ruler Kubhiraka (y79e445dd76f, ye69538fabc3) had no own MCQ. Added: Naneghat in Prakrit-Brahmi, a statements item (Prakrit / Junagadh Sanskrit), Kubhiraka to Bhattiprolu, a match of inscription to issuer, and Maski "Gulmika".
- **U0002:** All keywords covered. PYQ angles missing: where the early Satavahana inscriptions are (Maharashtra), the nigama-sabha term, Malkapuram's contents, the language of copper-plate grants, Rudrapurushadatta's inscription, and Alluru's gifts. Added 6 MCQs. I avoided asking "which inscription mentions nigama-sabha" because the PYQ key (Nanaghat) disagrees with the notes (Bhattiprolu). For the same reason I avoided the Kondamudi language question (PYQ key Pali, notes say Prakrit) and tested the language angle with Mayidavolu instead.
- **U0003:** Levallois technique to site (Sembur, APPSC 2023). Added a one-liner and a statements item.
- **U0004:** N1 (district concentration of burial types) was partly covered, and Betamcherla had no own MCQ. Added Billa Surgam near Betamcherla, cist in Visakhapatnam, sarcophagus in the Krishna valley / Nagarjunakonda, and a NOT-matched item. These follow the 1:3 notes and the G2 2025 key. The 1:2 notes list sarcophagi in Chittoor/Anantapur, so no sarcophagus or cist district item was written for 1:2.
- **U0005:** Fully covered; no APPSC PYQs.
- **U0006:** Partly covered: the northernmost site, site to district, the Dholavira occupation span, and India vs Pakistan sites. PYQ angles missing: Chanhudaro bead industry and Harappa's river. Added Manda, a boundary-sites match, Kalibangan-Hanumangarh, Harappa-Ravi from the other direction, Mohenjodaro-Larkana, Dholavira 3000-1800 BCE, the Chanhudaro bead/bangle factory, and a site in Pakistan.

## APPSC wording
- All 25 new MCQs follow the APPSC framing: direct questions ending in "?" ("Who issued ...?", "In which district ...?", "What is X known for?"), "Consider the following statements ... Which of the statements given above is/are correct?", and "Match the following: List-I ... List-II ... Select the correct answer using the code given below."
- The 2 keyless APPSC PYQs (Mohenjodaro "Mound of the Dead", y0fb812efdd9 and ya6bb83fed73) count fully. Their angle is covered by nef5a9079ddd.

## Rewordings (168, stem only)
- Rows 1:0 to 1:5: every own fill-in stem ("X was written by:", "X is in:", "The ... is the:", "____") became a direct APPSC-style question. The fact, the options, their order and the key are unchanged.
- Left as they were: statements, assertion-reason, chronology and match items, stems that already end in "?", and 4 fill-ins whose options would not fit a question (n0dcca7eecef, nf586a6b7529, nc24f91c15dc, f2bc74f524abe).
- No reworded stem duplicates another stem in its topic.

## Off-topic APPSC PYQs filed under these topics (not counted)
- 1:2: y54e9057d7c8 (chocolate and dogs), y70068357208 (human bones)
- 1:3: yb0444cdab7f, ye26f80fb09b (leaf lamina), ya0d0538edab (district area)
- 1:5: y62bd619ebdc (TTD Asthana Vidvamsulu), yead6b76739c (206 bones)

Check: `python3 tools/angle_add.py data/angle2/out-a000.json --dry` gives "25/25 new MCQs and 168/168 rewordings would be applied", none refused.
