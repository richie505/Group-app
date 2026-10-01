# APPSC Prep (Android + Windows)

Offline study app for APPSC Group-I + Group-II, built from the Combined Notes (G1+G2)
and the Restructured 90-Day Plan.

**Structure:** Day → Topic (UNIT) → Section (syllabus row) → Subsection (■ heading) → content.

After each section: **MCQ practice** — 64,789 MCQs written from these notes (from the MCQ app,
[groupsmcq](https://github.com/richie505/groupsmcq)), filed under each section and subsection, with every question in
one run (Previous / Skip / Next), a "Stuck? Show a hint" button, the explanation, what the question trains, and a
"why it went wrong" technique note from the APPSC MCQ Techniques guide (`data/Techniques.kt`), net score with
1/3 negative marking, and "retry wrong answers". Previous-year questions (PYQs) live in the MCQ app.

Tabs: **Today** (today's targets) · **Plan** (all 90 days + buffer) · **Notes** (browse all 6 books)
· **Progress** · **Saved** (bookmarks).

## Updating the notes

The app data in `app/src/main/assets/` is generated from the PDFs:

```
pip install pymupdf
python3 tools/parse_notes.py <pdf_dir> app/src/main/assets        # book1.pdf .. book6.pdf
python3 tools/parse_plan.py <pdf_dir>/plan.pdf app/src/main/assets app/src/main/assets/plan.json
python3 tools/build_notes_mcq.py <groupsmcq>/tools/generated app/src/main/assets   # the MCQs
```

The MCQ app writes its notes MCQs from the same notes files, so each question already names its
section and subsection; `build_notes_mcq.py` writes them to `mcq1.json` … `mcq6.json` and the per-section
counts to `index.json`. (`tools/build_mcq.py` and `tools/data/` are the old PYQ-bank pipeline, kept for
the MCQ app's source data.)
`tools/data/extra_secs.json` adds extra subsections (Science: general physics, chemistry,
biology, human body) to the notes files.

## MCQ schedule PDFs

```
pip install reportlab
python3 tools/build_mcq_pdfs.py app/src/main/assets mcq-schedule
```

One PDF per plan day (Days 1–83; the mock week 84–90 has no sections), MCQs only with the answer after each,
under the app's headings: Day → Topic → Section → Subsection. Each MCQ is given once, on the first day its section
comes up (sections the plan never lists ride with their neighbour); days that only revisit sections get a
revision set (HIGH 15 / MED 8 / LOW 5 per section). `mcq-schedule/Answer Keys/` gets a key sheet per day:
question numbers and answers only, in a grid under the section headings.

## Building

```
./gradlew assembleRelease          # app/build/outputs/apk/release/app-release.apk
./gradlew recordRoborazziDebug     # screenshots of the main screens into app/screenshots/
```

## Windows app

`desktop/` is the Windows version. It compiles the same screens and data code as the Android app
(`app/src/main/java`) with Compose for Desktop; only `MainActivity.kt` and `platform/` are Android-only,
and `desktop/src/main/kotlin` supplies the Windows side (window, left navigation pane, menu bar,
keyboard shortcuts, progress saved to `%APPDATA%\APPSC Prep\progress.json`).

```
./gradlew :desktop:run              # try it on this computer
./gradlew :desktop:test
tools/windows/build_windows.sh      # on Linux: APPSC-Prep-Setup.exe (~31 MB) + APPSC-Prep-Windows.zip
```

The build script needs `gcc-mingw-w64-x86-64`, `nsis`, `zip` and `curl`. It bundles a trimmed Windows
Java 17 runtime (Eclipse Temurin, cut down with jlink), so users do not need Java installed, and shrinks
the libraries with ProGuard (`desktop/rules.pro`). Windows 10 or 11, 64-bit. The installer is per-user (no admin
prompt) and adds Start menu and desktop shortcuts and an uninstaller. The zip is a portable copy:
unzip and run `APPSC Prep.exe`. The Windows version number is `appVersion` in `desktop/build.gradle.kts`.

Shortcuts: 1–4 or A–D pick an option, Left / Right arrow previous / next question, Esc or Alt+Left back,
Ctrl+1…5 switch tabs, Ctrl+= / Ctrl+− text size.

Both builds are signed with `keystore/appsc-prep.jks`, so a new APK installs over the old one
and keeps your progress.
