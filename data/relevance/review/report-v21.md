# Packet v21 – second look

v21: restore 61 (11 fixed), keep out 89 (dup 74, trivia 13, off-syllabus 1, unfixable 1)

150 removed MCQs across 31 topics (3:120–3:144 AP economy/reorganisation, 4:0–4:7 general geography).

## Counts
- Restored: 61, 11 of them with a fix
- Kept out: 89
  - Exact duplicate: 74 (mostly the same fact asked the same way as a PYQ, or a current MCQ whose key/distractors already turn on that exact fact)
  - Trivia: 13 (e.g. venue of ISHA award event, awardee's district, market fee to Dec 2025, out-of-school head-count, a politician's 2026 statement, 1881 geological congress)
  - Off-syllabus: 1 (Karnataka's "Beyond Bengaluru" strategy)
  - Unfixable: 1 (n06d91060834 "APIIC coordinates Single Desk": not supported by notes, and Single Desk is already well covered)

## Restore rules used
- Same fact asked from the other direction (e.g. place → institution, VBRI n444c6aeddd6; 73% → which tax, n1a2ba90475e)
- A positive direct question where the current item is a NOT-correct / NOT-matched one (e.g. f14d98f82c70d Part IXB, f4a65ffe65248 San Andreas)
- A different sub-fact or a new practice instance (f698456e3fe46 Sec 94(4); fc4221b80ed83 antipode)
- n686566b75e0: the matching PYQ ye9aa6061b62 has no key marked

## Fixes (11)
- n5dbe2194717 RSKs: removed the 10,606 option, so only 8,489 fits
- f6323f5f91a5e mobile vet clinics: removed the 350 option (2×175), so 340 is the only fit
- fab07291cae3b aqua-power tariff: stem changed to "outside notified zones" because the 10-acre cap was lifted in Aug 2026
- n41cad2668f2 PACS: updated to 2,024 (2025-26)
- nd6271608faf ARDBs: stem changed from "In AP" to the national cooperative structure
- fc72f60bec652: the "three-layer" wording from the notes replaced by a neutral stem
- f446bbac57fb8 MMR: updated to SRS 2021-23 = 30
- n6ca66972cd6: 26 → 28 districts
- nf03debfaa7d: fixed the second wrong pair (IMR now AP 19 / India 25)
- f4e3634614b35 deferred taxes: Section 51(1) → 53(1)
- na70b68e9abc IAU moons: June → March 2026

## Kept-out examples
- na7429a60564 CTRI Rajahmundry = PYQ y5dbf094c1f2
- nbd2e74dc989 Assembly 175→225 = PYQ ya6093f481bf
- f9234d45b3c13 "Atchannaidu third time" is already the point of n0de18447ffc's distractors

Dry run: `python3 tools/relevance.py restore data/relevance/review/restore-v21.json --dry` reported "61 MCQs would be restored" and no invalid ids.
