# PYQ Decoding Manuals – progress

Approved 2026-11-27: fetch official keys; include ALL papers (G2 2008/2012 too; G1 = Prelims papers).

- [x] Stage 1 Audit – AUDIT_AND_PLAN.md, source_inventory.csv
- [x] Official keys: APPSC site unreachable (reset / 503). Copies of APPSC-issued key documents fetched for 17 papers
      (data/pyqdecode/keysrc/, gitignored; provenance in key_provenance.json). Final keys NOT found for G1 2017,
      2023 P1, 2024 P1 (initial keys used, labelled). 2008/2010/2012 keys: third-party only.
- [x] Stage 2a DB: tools/pyqdecode_db.py -> pyq.db (3,308 questions; G2 leaf mapping loaded)
- [x] Stage 2d: app PYQs added as a SECONDARY tier (tools/pyqdecode_appbank.py): 2,264 more (G1 998, G2 1,266) from 111
      sources (G1 1983-2004, G2 2000-2012, undated PYQ books); 3,491 duplicates skipped. App keys, not official;
      reported separately from official-paper evidence in every count.
- [ ] Stage 2b: restore options of G2 Mains 2019 (432 Qs) from the bilingual booklets
- [x] Stage 2c: keys checked (keycheck_g1/g2.jsonl, applied by tools/pyqdecode_keys.py). G1: 530 match, 9 deleted,
      1 changed by APPSC final key (2023 P2 Q63); G2: all APPSC-document keys match; 27 conflicts with the third-party
      2008 compilation kept as CONFLICT notes for fact verification.
- [ ] Stage 3: map G1 questions to the 237 G1 leaves; re-check G2 mapping
- [ ] Stage 4-8 as in AUDIT_AND_PLAN.md
