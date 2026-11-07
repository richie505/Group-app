# a021 report

a021: keyword angles 66/87 covered (20 partly), APPSC PYQ angles 15/19 covered, 36 new MCQs, 214 reworded

Misfiled APPSC PYQs (subject not in the topic's notes) are left out of the count and listed as missing. All new MCQs use APPSC wording. 214 own-MCQ stems (fill-ins ending in ':' or '____', and wordy stems) are reworded as APPSC-style questions. Each keeps the same fact, the same options in the same order and the same key.

| Unit | Topic | KW covered/partly/missing (of total) | APPSC covered/counted | New |
|---|---|---|---|---|
| U0127 | 1:126 | 11/3/0 (14) | 6/7 | 5 |
| U0128 | 1:127 | 4/4/0 (8) | 0/0 | 5 |
| U0129 | 1:128 | 12/4/0 (16) | 3/4 | 7 |
| U0130 | 1:129 | 19/4/1 (24) | 2/3 | 9 |
| U0131 | 1:130 | 6/3/0 (9) | 2/2 | 5 |
| U0132 | 1:131 | 14/2/0 (16) | 2/3 | 5 |

## What was missing
- **U0127**: #1/#8 year of Talikota (partly); #10 order of the Aravidu rulers (partly). PYQ yf03eb99786c, Kshetrayya's patron: the angle is a poet's or scholar's Nayaka court, so new MCQs on Govinda Dikshita and the Tanjore Nayaks. Also added Chandragiri -> Venkatapati II (#12).
- **U0128**: #1 chronological order of the battles, and Kannauj -> Humayun (partly); #2 cities gained after Panipat I (partly); #3 statements on the establishment of the empire (partly); #6 language of the Tuzuk-i-Baburi (partly, written as an assertion-reason). The only APPSC PYQ, ye184120cb16 (Peter O'Toole), is misfiled.
- **U0129**: #2/#11 Grand Trunk Road route, other Sur roads, builder/restorer (partly; APPSC asked this in 2018 and 2022); #5 order of Humayun's events (partly); #10 order of the battles (partly). PYQ ybd7bcc1ad08, Akbar's coronation at Kalanaur: new MCQ on the year. Also added Purana Qila -> Humayun (#14). PYQ y468c39c1251 (gold carats) is misfiled.
- **U0130**: #1/#12 Akbar's literacy and educational reforms, emperors' memoirs (partly); #3 Rajput holdouts: Rao Chandrasena of Marwar, and Mewar's submission under Jahangir (partly); #19 emperor-wise share of Hindu nobles (missing); #23 Naqshbandi founder and Sirhindi's order (partly). PYQ y936f5f43ea1, illiterate emperor: new MCQs. PYQ y67acbd14ff4 (US global terrorist designation) is misfiled.
- **U0131**: #3 duties of the bitikchi and amalguzar (partly); #5 maal as the main state income, and suyurghal (partly); #6 first proper Diwan, Muzaffar Khan Turbati (partly). PYQ y9eda4e5234c (Deshmukh's duty) is counted as covered by the own official -> duty MCQs.
- **U0132**: #4 Thomas Roe's sending monarch and the place he was received (partly); #15 Aurangzeb's reimposition of jizya (partly). PYQ y2a8ddf2ca3e, Dara Shikoh's Persian translations: new MCQs on the Yogvashishta and Sirr-i-Akbar.

Check: `python3 tools/angle_add.py data/angle2/out-a021.json --dry` -> 36/36 new MCQs and 214/214 rewordings would be applied, none refused.
