# Book icon → exact notes lines: final report (v3.33)

## What changed in the app

In APPSC Complete and APPSC Group 2, the book icon ("Read from the notes") on an MCQ used to guess a notes page by
matching words, and it often opened a neighbouring fact. It now opens a checked link, chosen for that MCQ. It shows:

1. **The correct answer is (n) option.**
2. The MCQ's explanation.
3. **From your notes:** the exact line(s) that state the answer, highlighted. For a table it shows just the one row,
   not the whole table. For statement, NOT and match questions it shows one line per statement, up to 4.

PYQs (ids starting "y") were left out, as asked. For them, the book icon still uses the old word-matching guess.

## Totals

| | |
|---|---|
| Packets | 249 rollout packets, plus the 6-topic pilot |
| Own MCQs linked, APPSC Complete | **74,851 of 74,851** (coverage check: 0 missing) |
| Own MCQs linked, APPSC Group 2 | 49,522 (all Group 2 own MCQs whose lines are in Group 2's notes; 400 sampled, all point at the same line as in Complete) |
| Facts added to the notes | 456 one-line bullets, each added at the end of a subsection (log: `notes_added.jsonl`) |
| Wrong or unclear explanations rewritten | 499 (log, old and new: `xfixed.jsonl`) |
| Options or keys changed | none, except the one corrupted MCQ below |

Most of the rewritten explanations were one of these:
- a wrong number, date or name compared with the notes;
- "the third statement is wrong" when it was really another one;
- stray generator text such as "(Sequence not possible…)";
- claims that the notes do not support.

## One MCQ repaired

**ca894e26c8cf6d** (FDI commitment under the India–New Zealand FTA). The dollar amounts had been stripped from its
options, so they read " billion over 5 years", "0 billion over 15 years" and so on. The options are now $10 bn over
5 years, **$20 bn over 15 years** (the key, unchanged), $15 bn over 10 years, and $10 bn by 2030. A scan of every
MCQ found no other options with missing amounts.

## MCQs whose key looks doubtful (not changed: please decide)

| MCQ | Issue |
|---|---|
| nindian-history-147-2 | Kalyani Chalukyas: key says c. 973–1195; notes say 973–1189 (the key is still the closest option) |
| n581249e3c0d | Key says "Bhaskara Mantri"; notes say the inscription was issued by Bhaskara Bhavadura, a prince |
| n5c8fd3adae6 | Northern Circars lease: 15 lakh (key, notes 168) vs 9 lakh fixed in 1766 (notes 167) |
| nap-history-15-2 | Satyasamvardhini option may also be wrong (two answers) |
| f2ab5ab784fb2 | Poona Pact reserved seats: 147 (key) vs 148 (another topic's notes) |
| nap-history-1-28 | First woman arrested in Salt Satyagraha in Andhra: Sitamahalakshmi (key) vs Rukmini Lakshmipathi (notes) |
| nfed258e8a7e, f073d1d60f392 | Jashuva's Padma Bhushan (1970): the APPSC 2025 key treated this statement as incorrect |
| fd753041845cc | Kuldip Nayar case was decided in 2006; the option and notes say 2009 |
| n6d5e279a886 | Lokpal: key says Section 11 sets up both wings; notes give Section 11 for Inquiry and Section 12 for Prosecution |
| nd9c0601092e | Ashok Mehta ideas: key says West Bengal only; notes also name Karnataka and AP |
| f161777c95110 | Thungon Committee option is also true (two correct options) |
| f07ab1728d8d5 | Tendulkar 2011-12 rural line: ₹26/day (key) vs ₹816/month ≈ ₹27/day (another line) |
| f7700da71a80b | NFSA NOT question: the keyed "Rice ₹3/kg" is actually true; the wrong statement is "revised upward with MSP" |
| n36d95beb0d7 | GSTAT: the "Finance Act 2024" distractor may also be wrong (GSTAT came via the Finance Act 2023) |
| gabeee7436035 | Tropical year: the key (365 d 6 h 9 min 9.5 s) is the sidereal year; the tropical year is ≈365 d 5 h 48 min 46 s (option A). The notes repeat the same mistake |
| nb73c6b84ca3 | Operation Clean Sweep: key says Tier-1/Tier-2 corporations; the drive covered all 123 ULBs |
| n5655d7a2007 | AP's latest IMR: 19 (key) vs 18 (SRS 2024, another line) |
| f4b2b6e4e6da2 | APSLSA Executive Chairperson: CJ Lisa Gill (key) vs Justice Ravinath Tilhari (another topic) |
| n84f4da01d35, nbf2cee33d7c | "Tallapalli" vs "Tallavajhala" Patanjali Sastry (spelling) |
| caa01ae8d95d83 | Notice against Speaker Om Birla: two options look correct |
| ca0238af6bf50b | PM SVANidhi: DFS and MoHUA options are also wrong (they are nodal bodies; SIDBI implements) |
| ca3b1e4d7bad62 | Stem says the Karandai plates were returned by the Netherlands; notes say the Anaimangalam plates came from Leiden |
| ca718c8d285049 | Padma option D ("Republic Day, by MHA") is also loose (announced on 25 Jan) |
| f863ddbd45f15 | Bharat Ratna suspension years: 1978-79/1993-97 (key) vs 1977-80/1992-95 (another topic and MCQ fb1b019790d49) |
| nb3e30dd744a | SGSY: notes and key say 1999; some keys say 1995 |
| n9edad36ecb1 | Hormuz 2026: "accelerated LNG/LPG imports" is only loosely supported (LNG volumes fell in Apr and May 2026) |

## Notes that disagree with themselves (no MCQ changed)

- **Book 3:**
  - 11th NITI Governing Council meeting: 19 Jun vs 11 Jun 2026.
  - One State-One RRB: "26 RRBs amalgamated" vs "15".
- **Book 4:** Fujiyama: active vs dormant.
- **Book 6:**
  - Cigarettes: 40% slab vs 28% + cess.
  - NDB founded: 2014 vs 2015.
  - WTO MC14: 26–29 vs 26–30 March 2026.
  - Mogali Venkatram's 800 m gold: 1 Jun vs 31 May, and his name is spelt two ways.
  - 17 Arjuna awards stated, but the table lists 14 names.
  - Vande Mataram: "Sanskrit" vs "Sanskritised Bengali".
  - SDR 2026: India 94/169 in the notes vs 94th of 167 on the web.
- **Earlier pass:** the 2:0 sub 8 table has wrong column headers.

## Added facts to double-check (agents wrote them from memory, or from a single or secondary source)

- **Book 3:** AP services GVA 2014-15 ≈ ₹2.15 lakh crore (44%) (3:109).
- **Book 4:** Perim Island captured by the Houthis, Sept 2026 (4:96).
- **Book 5:**
  - IBM to train 1 lakh people (notes), while reports say 50 lakh youth (5:8).
  - Vanashakti recall of Nov 2025: a 2:1 decision, about ₹20,000 crore of projects (5:77).
- **Book 6:**
  - NPS Swasthya 30% transfer (6:35).
  - PM-DHARA TBCB / cost-plus split (6:32).
  - US exits of January 2026, including UNFCCC, IPCC and IRENA (6:63).
  - NITI "Roadmap for Making Ayurveda Global", 2 Jul 2026 (6:46).
  - Nepal Gen Z protests and interim PM Sushila Karki (6:65).
  - Integrated Battle Groups from 17 Corps, each under a Major General (6:105).
- **Earlier packets:** ECI cap of 1,200 voters per booth; Law Ministry as the delimitation ministry; Gandhi in
  Hyderabad on 9 Mar 1934.

Every link file (`link-L*.json`) and every log is in `data/notelink/`.
