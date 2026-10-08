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

**Full forms of short forms** (2.19): the first NCPCR, SC, CWC … on each page shows its full form in grey, and
read-aloud says the same meaning (`data/Acronyms.kt`, `SpeechText.meaning`). The meanings come from a list checked
by hand against how the notes use them - 4,827 short forms (2.22: every short form in all six books now has one) (2.20: also the rare ones not spelled out next to them, and
mixed-case ones such as MoLE, MoSJE, MeitY, UoI, NaBFID)
(`tools/data/acronyms.tsv` → `tools/build_acronyms.py` → `assets/acronyms.json`). 133 have more than one meaning
in the notes, each with the words that pick it, and the whole page decides: CWC is the Child Welfare Committee on
a Juvenile Justice page, the Central Water Commission next to dams, the Central Warehousing Corporation in
agriculture and the Congress Working Committee in History; TMC is Trinamool Congress or thousand million cubic
feet of river water; ITC is input tax credit on GST pages and ITC Limited elsewhere; PR is Panchayati Raj, proportional representation, President's Rule or a Permanent
Representative. A full form is skipped only when the same bullet already spells it out. Hyphenated scheme names are read whole or part by part (NP-NSPE, PM-KISAN, NFHS-5, PMGSY-IV). A few (SC, MP, CAA, RE, ASI …) are
decided by the words right next to them ("challenged in the SC" vs "SC students").

**After a wrong answer** (2.33): the explanation's sentence on the picked option is highlighted, "why option (n) is
wrong" (`WrongPick`: for statement questions the sentence about a statement the pick got wrong - by number or by
its words; otherwise the sentence with the picked option's own words; else "The other ..." sentences) - 17% of
wrong picks, as most explanations only explain the right answer. Every answer also quotes **From your notes**: the
lines of the question's own notes page that best explain the right answer, source tags out, with a link to the
page (`NotesExcerpt`, 95% of questions).

**Explain simply** (2.31): ⋮ → *Explain simply* on any page opens Google's AI Mode (free, no sign-in, needs
internet) with the page's text and the request to explain it in very simple English for a class 6 student - short
sentences, an everyday example, every hard word explained, then 3 key points for the exam (`simplePrompt`: source
tags out, cut near 1,400 characters so the link stays short). *Add text from this page to my notes* keeps the
explanation at the end of the page as **Your note** (`UserNotes.PAGE`), read aloud and backed up with the rest.
Every Google page in the app (Explain simply, Search Google, a word's meaning) has two buttons at the top: **↗ Open
in Chrome** (`Platform.openInBrowser`, a Chrome tab where the reader is signed in to Google - Google does not allow
signing in inside an app's own web view, and its pages work best there) and **✦ Ask Gemini**
(`Platform.askGemini`: the question is shared to the Gemini app, or copied for gemini.google.com).

**Pick the MCQ set** (2.30): Today's MCQs and each section's practice card show three buttons with counts -
**Unattempted** (not tried yet), **Incorrect** (wrong on the latest attempt) and **All** (`practiceSets`, the
quiz modes "new", "wrong" and "all"). A set with nothing in it is greyed out.

**APPSC Revision** (2.28): a second, standalone app from the same code - revision sheets built from the app's
MCQs, on the same 90-day plan (same days, sections and pages, so "Day 12" is the same topics in both). It installs
next to APPSC Prep (`com.appsc.prep.revise`, green icon) with its own progress ("revised" marks), backup,
read-aloud, MCQ practice and full forms. Every MCQ's explanation states the fact behind its answer;
`tools/build_revision_mcq.py` (→ `app/src/revise/assets/rev{1..6}.json`) turns each page's questions into fact
bullets: filler out ("Statements 1 and 2 are correct", "Hence option (b)", option letters like "sequence B, D, A, C"),
"Statement 3 is false because X" → X,
one sentence per question, the answer in bold, a fact already given on the page (its rare words, all its numbers)
not repeated, the notes' exam-angle lines first. Each page keeps its most valuable facts - rare information, the
answer stated, key terms, past-paper questions - up to a budget by the plan's priority (HIGH 35%, MED 24%, LIGHT
14% of the page's notes). Pages with no questions get their key facts from the notes (`tools/build_revision.py`).
26,940 facts, 0.52 M words (half the notes). The edition is chosen by `edition.json` in the revision app's assets
(`Repository.revision`); tests for the notes app are in `src/testNotes`, for the revision app in `src/testRevise`.

**Plan dates** (2.26): Day 1 is 6 Oct 2026, Day 90 is 3 Jan 2027, the final buffer runs 4-23 Jan and the exam is
24 Jan 2027. `tools/reschedule_plan.py <plan.json> <day-1 date> <exam date>` moves every day (content and day
numbers stay; the review day is every 7th day, now called the weekly review) and spreads the buffer over the days
left; then rebuild the MCQ schedule PDFs (below). Re-running `parse_plan.py` restores the original dates.

**Backup** (2.25): Progress → *Back up now* saves read marks, bookmarks, MCQ answers, study days and own notes to one
JSON file (phone storage, Drive …; on Windows a Save box); *Restore* adds a backup to what is on the device - nothing
is deleted, the backup's MCQ answers and notes win, and a backup from before the notes were regrouped is moved to the
new page ids (`ProgressStore.backup`/`restore`, `BackupTest`). A phone backup restores on Windows and back.

**Read-aloud never closes the app** (2.25): each read-aloud step (`SpeechText.safely`) and the full forms on a page
are skipped if they fail on a phone, and the text is read as written. Unit tests run with `-Dprep.strict=true`, so
there a failing rule fails the build; `AndroidRegexTest` checks the look-behinds Android's regex engine rejects (the
2.22 crash).

**Read-aloud numbers and symbols** (2.22): Roman numerals become numbers (Classes I-VIII → "Classes 1 to 8",
Part IXB → "Part 9B", Chandragupta II → "Chandragupta the Second"); Indian amounts are read in lakhs and crores
(₹1,30,794.90 crore → "1 lakh 30 thousand 794.90 crore rupees"); "54 M" and "$2.5B" are millions and billions, but
Article 338B and Section 304B stay as they are; units (µg/m³, kWh, MT, ppm …), case names ("v." → versus), "Amdt",
"(₹ cr)" headings and symbols are read in words. `SpeechAuditTest` dumps the read-aloud text of every page
(`-Pspeech.audit=<file>`) so all six books can be checked at once.

**Fill the gaps** (2.21): under each grey "Not in your sources: ..." line (1,184 of them) are *Search Google*
(Google inside the app, searching for the missing fact) and *Add to notes*. On the Google page, tap *Add text from this page to
my notes* (2.24): the copy menu does not show inside the app, so the page's paragraphs are listed with tick boxes
(any selected or copied text comes first, already ticked); tick the useful ones, then edit it and Save. It is kept on the phone
(`ProgressStore.added`, `data/UserNotes.kt`) and shown - and read aloud - right under that line as **Your note**;
*Edit my note* changes or deletes it. Read-aloud also says "2 M" as "2 million" and "lakh MT" as "lakh metric tonnes".

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
# daily revision notes PDFs (APPSC Revision's sheets, same days and sections as the MCQ PDFs)
python3 tools/build_revision_mcq.py app/src/main/assets app/src/revise/assets
python3 tools/build_revision_pdfs.py app/src/main/assets app/src/revise/assets revision-schedule
python3 tools/build_revision_pdfs.py app/src/main/assets app/src/revise/assets revision-schedule-dark --dark
```

One PDF per plan day (Days 1–83; the mock week 84–90 has no sections), MCQs only with the answer after each,
under the app's headings: Day → Topic → Section → Subsection. Each MCQ is given once, on the first day its section
comes up (sections the plan never lists ride with their neighbour); days that only revisit sections get a
revision set (HIGH 15 / MED 8 / LOW 5 per section). `mcq-schedule/Answer Keys/` gets a key sheet per day:
question numbers and answers only, in a grid under the section headings.

## Building

```
./gradlew assembleNotesRelease     # APPSC Prep:     app/build/outputs/apk/notes/release/app-notes-release.apk
./gradlew assembleReviseRelease    # APPSC Revision: app/build/outputs/apk/revise/release/app-revise-release.apk
./gradlew testNotesDebugUnitTest testReviseDebugUnitTest
./gradlew recordRoborazziNotesDebug recordRoborazziReviseDebug   # screenshots into app/screenshots/
```

## Windows app

`desktop/` is the Windows version. Since 2.32 the screens use the whole window: lists keep a readable width,
centred, with the space as padding inside the list so the mouse wheel scrolls anywhere (`PageList`); subjects, the
90-day plan and progress lay their cards out in columns (`gridItems`, `columnsFor`); the reader keeps the section's
subsections listed on the left; a quiz (progress, question and buttons) stays in one centred column; tables fill
the page. Phones are unchanged (the extra width is zero there). `WindowShotsTest` draws every screen at 1366×768
and 1920×1080 into `desktop/build/shots` for checking. Read-aloud on Windows (2.33, `WindowsSpeech.kt`) uses Windows' own
offline voices (SAPI, as Narrator): each paragraph is spoken by a small script under `wscript.exe` (no console
window), an Indian English voice (Heera / Ravi) when installed; pause, skip, speed and on-to-the-next-page work as
on the phone (`DesktopSpeechTest`). Google pages (Search Google, Explain simply, a word's meaning) open in the web
browser at once (signed in to Google; an app window cannot hold a full browser); "Add text from this page to my
notes" then takes the text copied there with Ctrl + C. It compiles the same screens and data code as the Android app
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
