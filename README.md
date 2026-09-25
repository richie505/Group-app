# APPSC Prep (Android)

Offline study app for APPSC Group-I + Group-II, built from the Combined Notes (G1+G2)
and the Restructured 90-Day Plan.

**Structure:** Day → Topic (UNIT) → Section (syllabus row) → Subsection (■ heading) → content.

Tabs: **Today** (today's targets) · **Plan** (all 90 days + buffer) · **Notes** (browse all 6 books)
· **Progress** · **Saved** (bookmarks).

## Updating the notes

The app data in `app/src/main/assets/` is generated from the PDFs:

```
pip install pymupdf
python3 tools/parse_notes.py <pdf_dir> app/src/main/assets        # book1.pdf .. book6.pdf
python3 tools/parse_plan.py <pdf_dir>/plan.pdf app/src/main/assets app/src/main/assets/plan.json
```

## Building

```
./gradlew assembleRelease          # app/build/outputs/apk/release/app-release.apk
./gradlew recordRoborazziDebug     # screenshots of the main screens into app/screenshots/
```

Both builds are signed with `keystore/appsc-prep.jks`, so a new APK installs over the old one
and keeps your progress.
