# Packet v01 review (book 1, rows 24-45)

156 removed MCQs re-judged.

| Outcome | Count |
|---|---|
| Restored | 85 |
| of which restored with fix | 6 |
| Kept out: exact duplicate | 68 |
| Kept out: trivia | 2 |
| Kept out: off-syllabus | 0 |
| Kept out: unfixable | 1 |

`python3 tools/relevance.py restore data/relevance/review/restore-v01.json --dry` -> "85 MCQs would be restored", none invalid.

## Restored examples
- f0d5328a3fc3e (1:28): asks which symbol stands for the first sermon. PYQ y44f3ae1d7cb asks the reverse (the wheel stands for which event).
- n3ebeabd77cd, n8fffaf63609, n0f387a8271d, ndf8d723cb30 (1:31): each asks a Charvaka/Ajivika fact in the reverse direction from its PYQ.
- nindian-history-17-3, nindian-history-29-12, nindian-history-29-14, nindian-history-4-26 etc.: flagged as "off-topic" for their row, but they are core APPSC facts (Kalinga War date, Tuluva dynasty, Sayyid-Lodi order, Jejakabhukti). Restored.

## Fixed
- nbee0c5aec4d (1:29): Bhavaviveka's seat is disputed (notes say Dhanyakataka, the APPSC key says Sriparvata). Reworded to ask who wrote the Tarkajvala.
- nac70359156a (1:30): the Guntupalli = Siddharthaka key was disputed. Now asks which sect centre Guntupalli was (Rajagirika).
- nf2d32ed5d6e (1:30): had two wrong pairs. "Rajagirika - Sriparvata" changed to "Rajagirika - Guntupalli".
- n36edd347662 (1:36): the Erragudi distractor could also count as right, so it was replaced with Kalsi.
- n95dc6271d61 (1:38): "Yakshi - Didarganj" was also correct. Changed it to "Yaksha - Didarganj".
- nc8e49fb58b0 (1:40): the Siddharthaka-Guntupalli key was disputed. Rebuilt the pairs so that only Sriparvata - Nagarjunakonda is right.

## Kept out examples
- nf0d9fded73b, n744b9288378, nda90cacbdf1 etc.: the same stem and answer as an existing PYQ.
- nindian-history-142-2 (1:44): repeats nee33dfb0419, which was restored in this packet.
- n16b95b6044c (Korean Cheugugi rain-gauge year) and f8e8a181031b0 (70,000 troops against Pan Chao): trivia.
- f7e1fb209f1a5 (Yogasara author): unfixable. The notes say Nagarjuna, the topic PYQ is keyed Kundakundacharya, and the PYQ already asks it.

## Note for the caller
- PYQ y3d119c97154 (1:40, "APPSC Group-II 2008", Siddharthaka chaitya) is keyed Guntupalli. The notes for 1:40 and 1:30 say the 2008 key was Gudivada. Not changed (out of scope).
- PYQ yf30cd4b82ef (1:38, Tamralipti) shows no keyed answer in `show`.
