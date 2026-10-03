# APPSC Prep (Android + Windows)

Offline study app for APPSC Group-I + Group-II, built from the Combined Notes (G1+G2)
and the Restructured 90-Day Plan.

**Structure:** Day → Topic (UNIT) → Section (syllabus row) → Subsection (■ heading) → content.

After each section: **MCQ practice** — 64,789 MCQs written from these notes (from the MCQ app,
[groupsmcq](https://github.com/richie505/groupsmcq)), filed under each section and subsection, with every question in
one run (Previous / Skip / Next), a "Stuck? Show a hint" button, the explanation, what the question trains, and a
"why it went wrong" technique note from the APPSC MCQ Techniques guide (`data/Techniques.kt`), net score with
1/3 negative marking, and "retry wrong answers". Previous-year questions (PYQs) live in the MCQ app.

**Listen** (headphones in the reader): reads the notes aloud with the phone's text-to-speech (Indian English
voice first), highlighting and scrolling to the paragraph being read; tables are read headings once, then row by row
("Table: Factor, How it changes the family." then "Industrialisation: …"). Play/pause, previous/next paragraph, speed 0.75×–2×, tap a
paragraph to read from there; it carries on through the following subsections, also with the screen locked or
the app in the background (foreground service with a Pause/Stop notification, `platform/ReadAloud*.kt`), until
Stop, leaving the reader or closing the app.
What is spoken (`data/SpeechText.kt`): no citations ([GK], (CDI; APP), (LENS Apr 2026), (APPSC-G2 2025 key),
"Sources: …", source names in sentences become "one source"), and short forms said in full - Sec 6 → Section 6,
WTO → World Trade Organization, ₹5,000 cr → 5,000 crore rupees, Group-II → Group 2 - from a built-in list, the
727 short forms the notes define (`assets/abbr.json`, `tools/build_abbreviations.py`), and context rules for
the ones with two meanings (SC: Supreme Court or Scheduled Caste from the words around it).

**Meaning** (select any word in the notes or in MCQ practice): offline dictionary card with the word's top
meanings and an example (WordNet 3.1, 147,478 words: `assets/dict/`, `tools/build_dictionary.py` from the npm
package wordnet-db), finds the dictionary form ("governments" → government), gives the full form of short forms
(WTO, the notes' own VCIC ...), and lists notes subsections whose heading mentions the word (tap to open)
(`ui/components/DictionaryArea.kt`, `data/Dictionary.kt`).

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
python3 tools/build_mcq_pdfs.py app/src/main/assets mcq-schedule-dark --dark   # reverse print: white on black
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
