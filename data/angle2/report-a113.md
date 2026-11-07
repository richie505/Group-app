# a113 report (U0679-U0684)

a113: keyword angles 62/73 covered (11 partly), APPSC PYQ angles 42/52 covered, 36 notes gaps, 51 new MCQs, 175 reworded

| Unit | Topic | Keywords C/P/M of T | APPSC PYQ angles C/T | Notes gaps | New |
|---|---|---|---|---|---|
| U0679 | 4:90 Classification of basic industries | 7/0/0 of 7 | 5/5 | 2 | 4 |
| U0680 | 4:91 AP industries, nodes, corridors | 11/4/0 of 15 | 4/4 (+1 misfiled) | 10 | 11 |
| U0681 | 4:92 Transport in India - roads, railways, pipelines | 13/4/0 of 17 | 13/17 (+4 misfiled) | 6 | 12 |
| U0682 | 4:93 Waterways, shipping, ports, aviation | 8/0/0 of 8 | 2/3 | 7 | 8 |
| U0683 | 4:94 Communication networks | 8/1/0 of 9 | 1/3 | 5 | 7 |
| U0684 | 4:95 Transport in AP | 15/2/0 of 17 (incl. N1, N2) | 17/20 (+1 misfiled) | 6 | 9 |

## Gaps found and filled
- **U0679:** All keywords covered. Notes gaps: main coal user (power), top wood-pulp producer (USA, FAO 2025). Also added a "NOT a core industry" item (PYQ yba60d878300 angle) and a "NOT mineral-based" item (PYQ yc75d33ea112 angle).
- **U0680:** Partly covered: #4 craft towns (added Etikoppaka, Markapur and a town-product match), #7 ODOP (not in notes, so nothing written), #9 township districts (added Sri City and Mallavalli), #13 Udyam district share (added Anantapur). Notes gaps also filled: Orvakal district, Kopparthy Phase-I area (PYQ area angle), Rare Earth corridor, ADB total US$ 625 mn, G.O. 68. Misfiled: y194502586e4 (Mission Purvodaya).
- **U0681:** Partly covered: the N-S/E-W junction at Jhansi (only PYQs had it), the first train (added Dalhousie and GIPR), production units (added a CLW/RCF/MCF/ICF match). PYQ angles missing: old NH number (added NH-16 = old NH-5 and the 2010 renumbering; I left out old NH-1 because the notes carry a doubtful APPSC 2002 key), Jhansi junction (other direction plus a statements item), Mission 41K (other direction), NH-44 cities. Also added West Central and East Central HQs and the Konkan Railway HQ. Misfiled: yca2d72fe54c, yb87eff67cf1, yf0e029f181f, y02f92f05a07.
- **U0682:** All keywords covered. PYQ y9d23f404b4c (year of aviation nationalisation): added the AAI year (1995) and the Air Corporations Act (other direction). Notes gaps: Leh airport, a major port to State match, State Maritime Boards, Sagarmala 2015, Mumbai-Pune expressway, Harmuti-Naharlagun.
- **U0683:** #6 PM-WANI only partly covered: added 2 items plus Digital Bharat Nidhi. PYQ angles missing: IP/MPLS router (other direction) and AIR's earlier name (added the 1936 renaming year). Notes gaps: post office count 2025, Bharat 6G Vision.
- **U0684:** Partly covered: #5 special coaches (added Vistadome and Shunya Plus stations) and N2 (added Setu Bandhan ROBs, which agrees with the APPSC G1 2024 key). PYQ angles missing: Visakhapatnam port traffic rank (other direction) and AP airport losses (statements item with other facts). Also added Dolphin's Nose, INS Dega, Buckingham Canal length and a port to district match (Ramayapatnam left out because its district changed). Misfiled: ybacd83bfd59 (Istanbul airport).

## APPSC wording
- New MCQs use direct questions ending in "?" ("Where is the headquarters of ...?", "In which year ...?", "Which of the following is NOT ...?"), plus 4 match items, 3 statements items and 3 NOT items.

## Rewordings (175, stem only)
- In rows 4:90 to 4:95, every own fill-in stem ("... is:", "... in:", "... was established in:", "____") became a direct question. Options, their order and the key are unchanged. Old "Which of the above statement(s)" endings now read "Which of the statements given above is/are correct?".
- Stems already ending in "?", plus assertion, match and NOT items, were left as they were. ne2bbb7b6ffd (Vizhinjam "India's first:") was also left, because no direct question fits its options well.

Check: `python3 tools/angle_add.py data/angle2/out-a113.json --dry` gives 51/51 new and 175/175 rewordings, none refused.
