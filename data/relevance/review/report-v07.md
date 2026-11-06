# Packet v07 – second look (book 1, rows 164–187, 154 removed MCQs)

**v07: restore 54 (7 fixed), keep out 100 (dup 99, trivia 0, off-syllabus 0, unfixable 1)**

| Outcome | Count |
|---|---|
| Restored as is | 47 |
| Restored with fix | 7 |
| Kept out: exact duplicate | 99 |
| Kept out: trivia | 0 |
| Kept out: off-syllabus | 0 |
| Kept out: unfixable | 1 |

## How the calls were made
- Kept out only when a PYQ or MCQ in the same topic asks the same fact in the same direction with the same answer
  (e.g. n4d305c7dd0f vs PYQ yc46f34c79f9, both "Nawab at Buxar = Mir Jafar").
- Restored when the removed item asks the fact from the other direction (f4f92d5fef0dc: book → author, PYQ asks author → book;
  fd6dc8c4c28a3: Tantia Tope → real name), asks it directly where the topic only had it as one pair or statement inside a
  matching or statement item (n11dfcc18d8c, f1377f3a8c9da, f9c62926d39b6), or uses a different option set that
  teaches other facts (n5291c75a545, f120b87dc3dd9).
- Items the audit called off-topic or trivia were restored as syllabus-relevant: nindian-history-120-26 (Munda/Santhal
  revolts), n2a6b5537f74 (2026 SC plea, Articles 14/368), n4e5afc7ac53 (SCADA at Prakasam Barrage, 2026).

## Fixes (7)
- f08d11cb5038c: key → First Treaty of Allahabad (Diwani, 12 Aug 1765).
- f4debce0cd110: key → Canning (Widow Remarriage Act, July 1856).
- nbe71fd9e6be: second right answer removed (Dalhousie option now "Public Works Department").
- fcdb78b4b6c76: ambiguous Macaulay distractor replaced with Warren Hastings.
- fbd65af00b5a8: stem date for Osmania University 1917 → 1918.
- nindian-history-14-23: Calcutta Madarsa statement 1780 → 1781 (notes, nc7b161742e8).
- n19ba888fac1: stem now asks the district before the 2022 reorganisation (Kurnool).

Note: `fix` can only change s/o/a/x. The stored `xs`/`xa` bullets of nbe71fd9e6be (still say Dalhousie – Widow Remarriage
Act is correct) and nindian-history-14-23 (xa "sources differ: other notes say 1781") are now stale. Update them when the
fixes are applied.

## Kept out: unfixable (1)
- fa9337f91056f: "How many Viceroys 1858–1947?" Sources count this differently (acting Viceroys), so no key can be defended.
