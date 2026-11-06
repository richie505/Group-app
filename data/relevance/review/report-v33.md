# Packet v33 review (book 6, rows 72-98)

v33: restore 44 (24 fixed), keep out 112 (dup 53, trivia 58, off-syllabus 1, unfixable 0)

- Input: 156 removed MCQs. Dry run: 44 MCQs would be restored, none invalid.
- Restored without changes: 20. Most ask a fact directly where the live MCQ is a NOT item keyed on the wrong version (Parakram Diwas 2021, DARPG e-Governance awards, India 4th at the Asian Para Games, ICTP prize age below 45, Surha Tal freshwater). Others ask the same fact from the other direction (Artemis II flyby, Safeena Husain and Educate Girls, IUCN coral reefs 2075, Telangana 5th in peak demand, CWG judo golds at Glasgow) or add new statements (Tarapur NOT item, Sangeet Natak Akademi honours, Critical and Emerging Technologies Index weights).
- Restored with a fix: 24
  - cae4e8da7dbb64: first NGOPV. Key changed from INS Sanghamitra to INS Shachi.
  - fdd91772e6d46: India's HDI in HDR 2025. Key changed from 0.63 to 0.685.
  - f4f47b74be0cf: growth-forecast pairs. Key updated to IMF October 2026 WEO 7.0%, with dated distractors.
  - ff2168dda47d9: India Justice Report statements. The doubtful claim about AP police was replaced with a false one (Telangana 1st), so the key is now "1 and 2 only".
  - nb67de092b0c: Ramsar COP15. The stem now gives the correct Fifth Strategic Plan period, 2025-2034.
  - caa1a9277d3866 / fe0f27ba87963: SEEI 2024. Both now ask for the group-wise top performer (AP 5-15 Mtoe; Maharashtra above 15 Mtoe).
  - n43bf7daa0e5: Booker 2025 shortlist. Flesh, a second correct answer, was replaced with Orbital.
  - nb747f95d25a: the second wrong pair was fixed (Qdenga is Takeda's tetravalent dengue vaccine).
  - ca448424d1b7dc: the WEF name was removed from the stem.
  - cafa0897b4ff77 / ca570e69a1bbb6: Assertion-Reason keys corrected.
  - 10 NOT or ambiguous items that hinged on a minor figure or on wording now key a clearly false statement: pharma exports, MAPS UAV, Kerala clam, UN AI dialogue, Liberhan Commission, BIOFACH, Gondhal, Asian Games hockey, World Archery Para Series, IBCA. Two ambiguous options were also replaced: Kulasekarapattinam (Space Vehicles Cluster) and Happy Seeder (Parali Protection Force).
- Kept out as duplicates (53): the same fact asked the same way as a PYQ or a live MCQ. Examples: GPT full form (PYQ y3605a432bdd), BHISHM sourcing agency (PYQ y2c9e97005ad), Operation Olivia (PYQ y7442756d9b8), index ranks already asked (EPI 176th, GPI 127th, Press Freedom 157th, QS), and Durand Cup winner. fabe19e90b045 (GII "2026") is counted here: once corrected to GII 2025, it repeats n738e8.
- Kept out as trivia (58): exact figures for minor items and names of minor officials. Examples: venues of award or book-release ceremonies, opponents' nationalities, dung-sample counts, MW figures for AP small hydro and biomass, death dates and ages of minor figures, mascots and prize money of minor awards.
- Kept out as off-syllabus (1): a FIFA World Cup final banner (cae4ec22114341).
