# APPSC Prep (Android)

Offline study app for APPSC Group-I + Group-II, built from the Combined Notes (G1+G2)
and the Restructured 90-Day Plan.

**Structure:** Day → Topic (UNIT) → Section (syllabus row) → Subsection (■ heading) → content.

After each section: **PYQ practice** in sets of 10, with instant answers, explanations (CDI),
net score with 1/3 negative marking, and "retry wrong answers".

Tabs: **Today** (today's targets) · **Plan** (all 90 days + buffer) · **Notes** (browse all 6 books)
· **Progress** · **Saved** (bookmarks).

## Updating the notes

The app data in `app/src/main/assets/` is generated from the PDFs:

```
pip install pymupdf
python3 tools/parse_notes.py <pdf_dir> app/src/main/assets        # book1.pdf .. book6.pdf
python3 tools/parse_plan.py <pdf_dir>/plan.pdf app/src/main/assets app/src/main/assets/plan.json
pip install python-docx
python3 tools/build_mcq.py <mcq_dir> app/src/main/assets   # PYQ Bank .docx files + CDI AP History PDF (+ tools/data/aph_prev.txt one-liners)
```

PYQs are attached to sections through the row codes in the PYQ Bank headings. CDI AP History
questions add their explanation to the matching bank question, or are filed under the closest
History & Culture section when the bank does not have them.
Hand-review decisions for each subject's "Other PYQs" live in `tools/data/subject_review.json`
(move to a row/subsection, drop from that subject, or send to another subject);
`tools/data/extra_secs.json` adds PYQ-only subsections (Science: general physics, chemistry,
biology, human body) to the notes files.

## Building

```
./gradlew assembleRelease          # app/build/outputs/apk/release/app-release.apk
./gradlew recordRoborazziDebug     # screenshots of the main screens into app/screenshots/
```

Both builds are signed with `keystore/appsc-prep.jks`, so a new APK installs over the old one
and keeps your progress.
