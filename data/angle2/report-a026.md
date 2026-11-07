# a026 report (U0157-U0162)

a026: keyword angles 41/45 covered (4 partly), APPSC PYQ angles 15/27 covered, 20 new MCQs, 82 reworded

| Unit | Topic | Keywords C/P/M of T | APPSC PYQ angles C/T | New |
|---|---|---|---|---|
| U0157 | 1:156 Danish and minor European settlements | 6/1/0 of 7 | 2/4 | 4 |
| U0158 | 1:157 Advent of Europeans in Andhra | 8/1/0 of 9 | 6/9 | 7 |
| U0159 | 1:158 Trade centres of coastal Andhra | 7/1/0 of 8 | 7/14 | 7 |
| U0160 | 1:159 First Carnatic War | 7/0/0 of 7 | 0/0 | 0 |
| U0161 | 1:160 Second Carnatic War | 6/1/0 of 7 | 0/0 | 2 |
| U0162 | 1:161 Third Carnatic War | 7/0/0 of 7 | 0/0 | 0 |

## Gaps found and filled
- **U0157:** #7 (Schulz and the Telugu Bible) was only partly covered: the only own MCQ naming Schulz was a NOT item. No own MCQ asked the translator angle of the Telugu Bible PYQs (ye988fa4b99d, y3b6d4f87c66). The two "first book printed in Telugu" PYQs are covered by f6cfe39e57402 and fe1890323ba56. Added 4 MCQs: Subbarayudu as Schulz's helper, Halle as the place where it was published, Ziegenbalg's Tamil New Testament (the translator angle the other way round), and Serampore as the press that printed the first Telugu Bible in India.
- **U0158 (CORE):** #1 (first factory in Andhra and its year) was only partly covered, by an order item. Three PYQ angles had no own MCQ: which power was at Machilipatnam in 1611 (y6f79360150c), the place of an Anglo-French battle (y2462ce48a8d), and the first Europeans to trade with India (ye226216d39a). Added 7 MCQs: Dutch 1605, English 1611, French 1669, Wandiwash as a place, Chandurthi as a battle, the order of arrival in India, and the Portuguese reaching India in 1498. Two misfiled PYQs were left out: ya85bbc0c788 (East Timor) and y86ff7bd2ab2 (Vijayanagara dams).
- **U0159 (HIGH):** #3 (shipbuilding) was only partly covered, by Corangi alone. APPSC asked about Narasapuram shipbuilding 3 times (y0476c042d02, yd16778cf934, y3a425a59c2c). Other PYQ angles with no own MCQ: Roman coins at Ghantasala (y8e408c18099), Motupalli as the Kakatiya port (ybacecdad5fa, yc9c9ecac0ac), and the first English factory in South India (ye7dc1e5c082). Added 7 MCQs: Methold and Narasapuram, Narasapuram's district, a statements item on Narasapuram and Corangi, Ghantasala and the Roman coins, Desiyakondapattanam as Motupalli, Marco Polo's visit under Rudrama Devi, and Masulipatnam 1611.
- **U0160:** All keywords covered. No APPSC PYQ is filed under this topic: the notes mention APPSC 2018, but that PYQ is not filed here.
- **U0161:** #1 was only partly covered: the Valapadu jagir was asked, but not Dupleix's title "governor south of the Krishna" (APPSC 2021, not filed here). Added 2 MCQs (the river, and who granted the title). One misfiled PYQ was left out: y63c7528923f (blood groups).
- **U0162:** All keywords covered. No APPSC PYQ is filed under this topic (the notes mention APPSC 2025 on the Treaty of Paris, which own MCQs n92d476cd407 and nindian-history-17-35 cover).

## APPSC wording
- New MCQs use the topics' APPSC framing: "Who among the following ...?", "Which European power ...?", "At which place ...?", "In which year ...?", "Which port was also called ...?" and one "Consider the following statements ... Which of the statements given above is/are correct?".

## Rewordings (82, stem only)
- Fill-ins ("... in:", "... by:", "... of the:", "____") and some "Which one of the following" stems in 1:156-1:161 became direct questions. The facts, the options, their order and the keys are unchanged.
- Left as they were: stems that already read like APPSC, statements, NOT and match items. Also left: stems where a reworded "Which of the following pairs is correctly matched?" would duplicate another stem in the same topic (n06eb13677b0, ndfe9e30602e), and n974c569ae74, whose options would not fit a question stem.

Check: `python3 tools/angle_add.py data/angle2/out-a026.json --dry` gives "20/20 new MCQs and 82/82 rewordings would be applied", none refused.
