# a038 report

a038: keyword angles 45/56 covered (11 partly), APPSC PYQ angles 8/15 covered, 21 new MCQs, 137 reworded

Coverage was judged on existing own MCQs (before additions). APPSC PYQs plainly off-topic are left out of the count and listed as misfiled. Own-MCQ stems that were ':' / '____' fill-ins or wordy, and statement/sequence stems missing their question line, were reworded into APPSC question form (same fact, options, order and key).

| Unit | Topic | KW covered/partly/missing (of total) | APPSC covered/counted | New |
|---|---|---|---|---|
| U0229 | 1:228 | 8/0/0 (8) | 3/3 | 0 |
| U0230 | 1:229 | 7/0/0 (7) | 0/0 | 0 |
| U0231 | 1:230 | 7/1/0 (8) | 1/2 | 3 |
| U0232 | 1:231 | 7/2/0 (9) | 0/1 | 4 |
| U0233 | 1:232 | 11/5/0 (16) | 2/5 | 7 |
| U0234 | 1:233 | 5/3/0 (8) | 2/4 | 7 |

## What was missing
- **U0229**: nothing; misfiled: y43eebe735ad (Zulu tribes, geography), y1af2afd5dea (Employment News weekly)
- **U0230**: nothing (no APPSC PYQs)
- **U0231**: #3 partly: Samagra Gramseva and Article 40 (village panchayats) not asked directly; PYQ ybe73d70073a movement -> leader (Bhoodan, Vinoba) angle
- **U0232**: #1 partly: Harijan Sevak Sangh first president (Birla) and former name not asked; #6 partly: caste / Ambedkar link (Poona Pact context); PYQ y7daf5376dec temple-entry place in Andhra angle; misfiled: y82f60b6889d (child nutrition), y910cbe14c0c (Bird Man of India)
- **U0233**: #3 / #9 partly: why Kheda was called off; #4 partly: Ahmedabad dispute issue (plague bonus) and mediator (Anusuya Sarabhai); #6 partly: parties to the Champaran Agrarian Committee's appointment; #8 partly: no own sequence question; PYQ y4e163c330d3 plague bonus angle; PYQ yce73c75889f Kheda called off angle; PYQ y9c47251db29 Home Rule -> leader angle; misfiled: y8449445ed80 (B.N. Sharma linguistic states resolution), y596d8d188e1 (Tenali bomb case), y339ccd658fb (Tripuraneni song)
- **U0234**: #1 partly: officer who ordered the firing; #2 partly: who gave up what (Tagore, Sankaran Nair, Gandhi, Jinnah); #3 partly: no own chronology sequence; PYQ y6250f6f1e57 Andhra response (Guntur Bar Association) angle; PYQ ydcaf140288b chronology sequence angle; misfiled: ydaf24eed525 (Veeragandhamu song, NCM)

Check: `python3 tools/angle_add.py data/angle2/out-a038.json --dry` -> 21/21 new MCQs and 137/137 rewordings would be applied, none refused.
