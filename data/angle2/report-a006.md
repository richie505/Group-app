# a006 report (U0037-U0042)

a006: keyword angles 66/87 covered (19 partly), APPSC PYQ angles 25/35 covered, 29 new MCQs, 122 reworded

| Unit | Topic | Keywords C/P/M of T | APPSC PYQ angles C/T | New |
|---|---|---|---|---|
| U0037 | 1:36 Ashokan inscriptions | 11/5/0 of 16 | 8/13 | 9 |
| U0038 | 1:37 Mauryan administration | 11/6/0 of 17 | 4/6 | 5 |
| U0039 | 1:38 Mauryan economy, society, art | 19/3/2 of 24 | 3/3 | 5 |
| U0040 | 1:39 Decline of the Mauryas | 15/0/0 of 15 | 3/5 | 3 |
| U0041 | 1:40 Early historic Andhra | 5/3/0 of 8 | 4/5 | 4 |
| U0042 | 1:41 Sungas and Kanvas | 5/2/0 of 7 | 3/3 | 3 |

## Gaps found and filled
- **U0037:** Partly covered keywords: #2 (first ruler to inscribe messages on stone), #3 (Erragudi content), #6/#10 (RE XII tolerance, RE II southern kingdoms, RE XIII Andhras) and #8 (only Kosam-Akbar was asked for moved pillars). APPSC PYQ angles with no own MCQ: Erragudi teachers and students (y6b880eff8f5, y23453b32a5a), prisoners freed on the coronation anniversary (y00c38caeaa3), RE XIII naming the Andhras (yeb08b7f23d6), and the earliest inscriptions in Andhra (y646c822a60c). Added 9 MCQs: Ashoka as the first ruler to inscribe messages, Erragudi edict and content, why Erragudi and Rajula Mandagiri matter (earliest inscriptions in Andhra), a statements item on prisoners and the PE IV respite, peoples named in RE XIII, the subject of RE XII, the kingdoms named in RE II, and the Topra and Meerut pillars moved by Firoz Shah. Rajula Mandagiri is not used as an Erragudi distractor because its own content (guru and disciple) overlaps.
- **U0038:** Samaharta and Dandapala had only APPSC PYQs (y838e75da064, y4c3d5a7e61b), with no own MCQ. Also partly covered: the settlement-unit order and the civic penalty. Added 5 MCQs: Samaharta's duty, the tirtha that headed the army, a tirtha-to-department match, the Sthaniya-to-Sangrahana order, and Pankodakasannirodhe.
- **U0039:** Missing: #11 Megasthenes' seven classes and #19 the Barabar caves' sect (Ajivikas). Partly covered: the Barabar donors, guilds, and capitals to site. All 3 counted APPSC PYQs were covered (Pana, Tamralipti, Mauryan art forms). Added 5 MCQs: seven classes, the Ajivikas, Ashoka and Dasaratha as donors, a capital-to-site match, and shrenis funding Buddhist centres.
- **U0040:** All keywords covered. APPSC PYQ angles missing: Kannabenna (Krishna) in the Hathigumpha inscription (yedd1c1eea3b) and Kharavela's Jainism (yd435da01d89). Added 3 MCQs: Kannabenna = Krishna, Kharavela ignoring Satakarni, and the Jaina king among post-Mauryan rulers. The Kannabenna fact is standard knowledge and does not conflict with the notes.
- **U0041:** Partly covered: Andhapatha/Andhakarattha to text, Siddharthaka chaitya, and the Assaka capital. The angle of the APPSC PYQ yd39b6e827ef (Andhra Padha to text) had no own MCQ. Added 4 MCQs: Andhapatha in the Vinayavatthu, Andhakarattha, Siddharthaka chaitya = Gudivada (this follows the notes and the G2 2008 key, so Guntupalli is kept out of the options), and Assaka's capital Bodhan. Bhimasena is left out of the Andhapatha options so that the G2 2019 key is not contradicted.
- **U0042:** Partly covered: source to author (only Garga was asked) and the Sunga home region. All APPSC PYQ angles were covered. yc513d2a71af, whose key is doubtful, is covered by n6b8869608ee. Added 3 MCQs: the Sunga heartland, a statements item (Ujjain origin, Agnimitra at Vidisha), and Banabhatta as the author of the Harshacharita.

## Misfiled APPSC PYQs (not counted)
- 1:38: y5594f6cd647 (Salankayana = Holy Bull), y5b09e61fd61 (insurance coverage)

## APPSC wording
- The new MCQs are mostly direct questions ending in "?" ("Who was the first ...?", "Which was the capital of ...?", "Who is the author of ...?", "Into how many ...?"). There are also 3 "Consider the following statements" items and 3 "Match the following ... Select the correct answer using the code given below" items.

## Rewordings (122, stem only)
- In 1:36 to 1:41, every own fill-in stem (ending in ":" or an open "the/by/in") became a direct question. Two "best described as" stems were also reworded. The facts, the options, their order and the keys are unchanged.
- Left as they were: statements, assertion-reason, match and NOT items, stems that already end in "?", and all PYQs.

Check: `python3 tools/angle_add.py data/angle2/out-a006.json --dry` gives "29/29 new MCQs and 122/122 rewordings would be applied", none refused.
