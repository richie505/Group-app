# PYQ Decoding Manuals – progress

Approved 2026-11-27: fetch official keys; include ALL papers (G2 2008/2012 too; G1 = Prelims papers).

- [x] Stage 1 Audit – AUDIT_AND_PLAN.md, source_inventory.csv
- [x] Official keys: APPSC site unreachable (reset / 503). Copies of APPSC-issued key documents fetched for 17 papers
      (data/pyqdecode/keysrc/, gitignored; provenance in key_provenance.json). Final keys NOT found for G1 2017,
      2023 P1, 2024 P1 (initial keys used, labelled). 2008/2010/2012 keys: third-party only.
- [x] Stage 2a DB: tools/pyqdecode_db.py -> pyq.db (3,308 questions; G2 leaf mapping loaded)
- [x] Stage 2d (user: use ALL app APPSC PYQs): tools/pyqdecode_appbank.py adds every APPSC PYQ held in the apps,
      deduplicated: SECONDARY tier G1 931 + G2 1,155 (app keys, years 1983-2012 + undated PYQ books); TERTIARY tier
      13,360 from other APPSC exams (Group III, Forest, Lecturers, Endowments ...) as supporting evidence of APPSC
      framing only. DB total 18,758 questions. Every count reports the tiers separately.
- [x] Stage 2b: G2 Mains 2019 – the APPSC documents are final-KEY booklets (keyed option only): all 432 keys confirmed;
      the other 3 options are in no available document (analysed as stem + key, no distractor analysis)
- [x] Stage 2c: keys checked (keycheck_g1/g2.jsonl, applied by tools/pyqdecode_keys.py). G1: 530 match, 9 deleted,
      1 changed by APPSC final key (2023 P2 Q63); G2: all APPSC-document keys match; 27 conflicts with the third-party
      2008 compilation kept as CONFLICT notes for fact verification.
- [x] Stage 3 (automatic): tools/pyqdecode_map.py – topic + candidate leaves for 18,742 of 18,758 questions; exact leaf
      chosen per question in Stage 4. Drafts: tools/pyqdecode_anatomy.py loaded 64,900 earlier statements as drafts.
- [~] Stage 4: G1 30/30 jobs DONE (1,179 Qs, 4,927 statements; 214/237 G1 leaves with direct PYQs). Loader:
      tools/pyqdecode_load.py (mechanism names normalised via mechanisms.json). G2: running.
- [ ] Stage 4 (orig. plan): official papers – 84 jobs (g1-1..30, g2-1..54; docs/pyqdecode-helper.md; check with
      tools/pyqdecode_jobs.py check <job>)
- [ ] Stage 4-8 as in AUDIT_AND_PLAN.md

Rebuild pyq.db: python3 tools/pyqdecode_db.py && python3 tools/pyqdecode_keys.py && python3 tools/pyqdecode_appbank.py && python3 tools/pyqdecode_map.py && python3 tools/pyqdecode_anatomy.py (then the 2019 key notes and Stage 4 loaders)

## Stage 4 complete, Stage 6 statistics (2026-11-27)
- All official questions deconstructed: Group 1 1,179 Q → 4,927 statements (1,651 T / 3,269 F / 7 U); Group 2 2,129 Q →
  7,524 statements (2,602 T / 4,865 F / 57 U). Every job passes `pyqdecode_jobs.py check`.
- `tools/pyqdecode_stats.py` → `stats_g1.json`, `stats_g2.json`, `coverage_g1.csv`, `coverage_g2.csv`.
- Coverage: Group 1 214/237 leaves with direct official PYQs (90.3%), 20 related-only, 3 none;
  Group 2 296/397 (74.6%), 39 related-only, 62 none.
- Stage 5: `tools/pyqdecode_verify.py` → VERIFICATION_REPORT.md (G1: 14 deleted, 23 conflicts, 7 unsettled, 21 time-sensitive; G2: 33, 62, 57, 54).
- Next: chapters (Stage 7) and PDFs (Stage 8).
