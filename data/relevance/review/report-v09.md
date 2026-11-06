# Packet v09 review (book 1, rows 205-230, 159 removed MCQs)

v09: restore 69 (10 fixed), keep out 90 (dup 81, trivia 9, off-syllabus 0, unfixable 0)

## Counts
- Restored: 69, of which 10 restored with a fix
- Kept out: 90
  - Exact duplicate: 81 (79 straight repeats of a PYQ or another kept MCQ, plus 2 wrong-key items whose only repair, ffe0a11e268ee and nac7daf5cf72, would make them exact repeats of APPSC PYQs ydbe2a2d48fd / y8942e60466a)
  - Trivia: 9 (song line count, arrest counts, vote count, Sukhdev's birth district, 1934 amendment wording, 2026 news items with no exam angle)
  - Off-syllabus: 0
  - Unfixable: 0

`python3 tools/relevance.py restore data/relevance/review/restore-v09.json --dry` → "69 MCQs would be restored", none invalid.

## Examples
- Restored, off-topic but on-syllabus: nindian-history-92-3 (Charter Act 1833 created Governor-General of India), f308bd7421225 (Pitt's India Act dual control).
- Restored, other direction: na780d958942 (Unnava → Malapalli; PYQ asks Malapalli → author), n7a550a7de99 (2nd RTC → attendees; APPSC PYQ asks the reverse).
- Restored, direct vs multi-pair: f5bf5adc78f59 (Morley-Minto = Indian Councils Act 1909; existing item is a 4-pair question).
- Fixed: ncd50a4d0fe2 (Rampa span corrected to August 1922 – May 1924); n3a14b6d9ed4 / f5e554a2aaefa (first HSC president = Govind Rao Nanal per notes); n85bd3fb4d17 (Zenana Patrika = Rayasam Venkata Sivudu); nf397f663d38 (Andhra Socialist Party first president = N.G. Ranga); n10b42703ee0 (stem now cites APPSC G2 2025 key, Viswanatha, Rayaprolu option removed); nap-history-28-3 (second false statement about Pal's host replaced); n854b0438b3f / nbaf25bbe044 (disputed 1937/1938 Mahila Sabha year removed); n63ace4a7376 (stray markdown asterisks removed from options).
- Kept out, duplicate: n921a54c38a6 (Philosophy of the Bomb = APPSC PYQ yef62312cfd3), n45f1c01afc2 (same stem and options as PYQ yd7359bfdae0).
- Kept out, trivia: fbad622489eb1 (vote count 1,886 to 884), fb5247e6c2a19 (song line count).
