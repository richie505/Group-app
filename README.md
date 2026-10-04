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

**Meaning** (select any word in the notes or in MCQ practice), Indian context first:
1. *In Indian context* - an exam glossary of 271 core terms written for India, all subjects including Science,
   Environment and Current Affairs (`tools/data/india_glossary.tsv`);
2. *From your notes* - the notes' own definitions ("Absolute humidity: …", 6,800+ terms), then what the notes
   say about anything selected: up to 5 sentences that mention it, citations hidden, lines opening with the term
   first. Terms are recognised however they are written (`data/NotesTerms.kt`): s.144 / sec144 / Sec. 144 /
   Section 144, Art 21 / Article 21, 84th Amendment / Eighty-fourth Amendment, 7th / Seventh Schedule;
3. the full form of short forms (WTO, the notes' own VCIC …);
4. *Dictionary* - WordNet 3.1 (139,343 words, `assets/dict/`, from the npm package wordnet-db) with every
   US-only sense removed (US government, states, Civil War, agencies);
5. notes subsections whose heading mentions the word (tap to open);
6. *Search on Google* - Google (India settings) inside the app (an in-app WebView; the only part that needs
   internet; back goes back a page, ✕ returns to the card).

**Each topic once** (2.18): the notes repeated whole topics in different sections (e.g. POCSO Act and JJ Act
under both "Child rights" and the JJ/POCSO section) and single facts on several pages. 986 repeated
subsections were merged into the one in the section the topic belongs to (any facts only the other copy had
are carried over under its heading), and 4,511 repeated sentences / table rows were cut where another page
already says them; the page that lost them ends with **Also covered in** links. The notes are 8% shorter
(1.09M → 1.01M words; 9,563 → 8,577 subsections). MCQs moved with their topic (60 near-identical ones dropped);
read marks and bookmarks move to the new pages on first start (`assets/moved.json`, `ProgressStore.migrate`).

**Full forms of short forms** on the page: the first NCPCR, SC, CAA … on each page gets its full form in grey
(`data/Acronyms.kt`; read-aloud skips it as it already says the short form in full). The words around decide
SC (Supreme Court / Scheduled Caste), CAA (after "101st": Constitutional Amendment Act), RTGS, ASI …; a meaning
the notes define on another page shows only if this page uses its words (no "CWC (Central Water Commission)" on
a child-welfare page).

**Key terms** at the end of every notes page (89% of pages; `tools/build_key_terms.py` → `assets/keyterms.json`):
the terms on that page that have a meaning in the app; tap one for its Meaning card.

The app is light-only and opts out of phones' automatic "dark mode for apps" (`android:forceDarkAllowed`), which
had turned the notes black behind pop-ups.
Built by `tools/build_dictionary.py` then `tools/build_india_glossary.py` (`assets/india.json`); app side
`data/Dictionary.kt`, `ui/components/DictionaryArea.kt`. The dictionary form is found for other forms
("governments" → government).

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
Then, to read each topic once (run `merge_topics.py` until it merges nothing more):

```
python3 tools/merge_topics.py app/src/main/assets     # repeated topics -> one subsection, writes moved.json
python3 tools/dedup_notes.py app/src/main/assets      # repeated sentences / rows, "Also covered in" links
python3 tools/build_key_terms.py app/src/main/assets
```

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
