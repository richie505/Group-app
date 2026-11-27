# PYQ Decoding Manuals – progress

Approved 2026-11-27: fetch official keys; include ALL papers (G2 2008/2012 too; G1 = Prelims papers).

- [x] Stage 1 Audit – AUDIT_AND_PLAN.md, source_inventory.csv
- [x] Official keys: APPSC site unreachable (reset / 503). Copies of APPSC-issued key documents fetched for 17 papers
      (data/pyqdecode/keysrc/, gitignored; provenance in key_provenance.json). Final keys NOT found for G1 2017,
      2023 P1, 2024 P1 (initial keys used, labelled). 2008/2010/2012 keys: third-party only.
- [x] Stage 2a DB: tools/pyqdecode_db.py -> pyq.db (3,308 questions; G2 leaf mapping loaded)
- [ ] Stage 2b: restore options of G2 Mains 2019 (432 Qs) from the bilingual booklets
- [ ] Stage 2c: check every stored key against the APPSC documents (key_check column)
- [ ] Stage 3: map G1 questions to the 237 G1 leaves; re-check G2 mapping
- [ ] Stage 4-8 as in AUDIT_AND_PLAN.md
