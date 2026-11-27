# APPSC PYQ Decoding Manuals – Phase 0 audit and plan

Status: **audit done; waiting for approval** before any analysis or PDF. Full inventory: `source_inventory.csv`.

## 1. What the project already has

| Material | Group 1 | Group 2 |
|---|---|---|
| Question papers (clean JSON: stem, 4 options, key index, explanation, subject) | 11 Prelims papers, 2008–2024: **1,179 Qs** | 15 papers, 2008–2025: **2,129 Qs** |
| – stages | Prelims (Screening) only. Mains is descriptive – not MCQ | 2008 (3 papers) + 2012 Paper I: old single-stage pattern; Prelims 2017, 2019, 2024; Mains 2017, 2019 (3 papers each), 2025 (2 papers) |
| Answer keys in the data | 1,166 keyed, 13 deleted | 1,996 keyed (+ 425 Mains-2019 keys as answer text), ~43 deleted |
| Key status recorded | 6 papers "preliminary/initial", 5 "final" | 3 (2008) "preliminary", rest "final" |
| Official syllabus | `data/g1syl/official-2018.pdf` → **237** micro-topic leaves (`leaves.json`) | 27-04-2023 syllabus → **397** leaves (`data/g2syl/leaves.md`) |
| Question → syllabus mapping | partial (via app topics) | **exists**: `data/g2papers/*.leaves.json` (every Q → leaf code) |
| Blueprint keywords | shared notes blueprint (`data/blueprint/`) | `tools/data/blueprint-keywords.md` + notes blueprint |
| Existing statement analysis | `data/pyqanalysis/`: **16,314 APPSC PYQs → 66,815 units**, each with truth (T/F), true fact, change code (NUM, DATE, PERSON, PLACE, BODY, SCOPE, NEGATION, REVERSAL, PARTIAL, MISPAIR, CHRONO …), cue words, language rule, solving technique – but **all APPSC exams mixed**, keyed to app topics, not to the official syllabus leaves |

Question formats in the official papers (counted from stems):

| | Statement-based | Matching | Assertion–Reason |
|---|---|---|---|
| Group 1 Prelims | ~172 Qs (heavy from 2023: 2023 P2 = 47 of 60, 2024 P1 = 63 of 120) | ~54 | ~13 |
| Group 2 | ~111 Qs (2024 Prelims 22, 2025 Mains 55) | ~62 | ~26 (2019 Mains, 2025 Mains) |

## 2. Problems found (must be settled before analysis)

1. **Keys are third-party copies, not files from psc.ap.gov.in.** Papers and keys came from Sakshi, Examsnet, Adda247,
   BYJU'S, Bloom APPSC, StudyBizz etc. Their "preliminary/final" labels are what those copies say. APPSC's own
   site timed out from this machine before. → I will label each key "published key (copy from <site>), status <x>"
   and NOT call it "official APPSC key" unless fetched from APPSC itself.
2. **Group 2 Mains 2019 (3 papers, 432 Qs): options are missing** – only stem + answer text. Statement/option
   analysis needs the four options from the paper.
3. **6 Group 1 papers have only preliminary keys** (2008, 2010 ×2, 2017, 2023 ×2, 2024 P1). Final keys/revisions
   are not in the project.
4. **Old Group 2 pattern (2008, 2012)**: set on the pre-2023 syllabus; mapping to today's leaves is only partial.
5. **Group 1 Paper II (2019/2023/2024)**: only Part B (Science & Tech, Current Events) is stored; Part A (Mental
   Ability) left out by design.
6. Duplicates across papers (e.g. reused questions) are not yet de-duplicated; the anatomy has 27 items with two keys.
7. Earlier key checks (`data/keys/`) corrected ~1,150 app MCQs against the web; for the manuals the **published key is
   preserved as is** and any conflict is shown separately (Phase 13 rule).

## 3. Proposed database (SQLite `data/pyqdecode/pyq.db`, with CSV/JSON exports)

- `paper` (id, exam G1/G2, year, stage, paper, date, source_paper, source_key, key_status, key_source_kind)
- `question` (id, paper_id, qno, text_original, text_corrected, correction_reason, format, options_json,
  key_index, key_text, key_status, deleted, subject, leaf_code, source_ref, extraction_confidence)
- `statement` (id, question_id, label (S1/A/R/pair a-iii/step/option-as-sentence), text, truth (T/F/unknown),
  truth_basis (key/derived/fact-check), true_fact, mechanism (open list, new codes allowed), decisive_phrase,
  cue_words_json, leaf_code, topic, micro_topic, blueprint_keyword, verification (verified/pending/conflict),
  fact_source)
- `word_obs` (statement_id, word/phrase, leaf_code, truth, mechanism) – one row per **question-level** occurrence
- `syllabus` (exam, leaf_code, subject, unit, topic, micro_topic, official_wording, blueprint_keywords)
- `coverage` (exam, leaf_code, status: direct PYQ / no direct PYQ / related only / source missing / pending)

## 4. Method

- **Units of count** kept apart and always printed as numerator/denominator: question · statement · question-level word
  occurrence · mechanism. G1 and G2, Prelims and Mains, and years never pooled without saying so.
- **Truth of a statement**: from the key where the key fixes it (one-liner, NOT-question, a combination that only one
  reading fits); otherwise "pending fact check" and checked against the Constitution / Acts / Govt. publications /
  standard texts (Phase 13 order), each with its source. Key conflicts kept and explained, never overwritten.
- **Reuse**: the 66,815 existing units are matched to the official-paper questions (same question id/text) and used as
  a first draft; each unit is re-checked and re-mapped to the official syllabus leaf, and new mechanism codes are added
  where needed.
- **Confidence**: STRONG / MODERATE / WEAK / NO EVIDENCE per pattern; recurrence labels from counts, never
  "predictions".
- AI practice items clearly boxed and labelled.

## 5. Pipeline (resumable, each step saves its output and updates `project_progress.md`)

1. Audit (done) → 2. Load DB from the paper JSONs (+ fill gaps 2–3 above if you provide/allow) → 3. Map G1 questions
to the 237 G1 leaves (G2 mapping exists; re-check) → 4. Statement segmentation + deconstruction in batches of ~40
questions per helper, subject by subject (≈ 3,300 Qs, est. 10–12k statements) → 5. Fact verification pass on every F
statement and every non-key-derived truth → 6. Word/phrase behaviour and mechanism tables per micro-topic, frequency
tables → 7. Coverage matrix (237 + 397 leaves) → 8. Chapters (HTML) → 9. PDF render (Chromium print-to-PDF: A4, Unicode,
page numbers, clickable TOC, bookmarks) → 10. QA (counts, denominators, no clipped tables, every page opens) and final
report.

Rough size: each manual several hundred pages. Effort: a few days of helper batches (the weekly usage limit has been hit
before; the work is checkpointed so it can resume).

## 6. Decisions needed from you

1. **Keys**: accept the stored third-party copies of the keys (labelled honestly as above), or should I first try to
   fetch the official APPSC key PDFs?
2. **Group 2 Mains 2019**: drop its 432 questions from statement analysis, or fetch the papers to restore options?
3. **Old Group 2 papers (2008, 2012)**: include them (mapped where today's syllabus covers them) or keep only 2017+?
4. Group 1 = Prelims papers only (Mains is descriptive) – OK?
