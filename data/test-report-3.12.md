# APPSC Complete 3.12: audit and test report (5 Nov 2026)

## Results

| Check | Result |
|---|---|
| APPSC Complete tests | **25 of 25 passed** |
| Shared code: APPSC Prep tests | 120 of 120 passed |
| Shared code: One-liners tests | 14 of 14 passed (1 failed before this audit: fixed) |
| Shared code: Revision tests | 12 of 12 passed |
| Android lint, Complete release | **0 errors** (17 warnings: library updates, icon, none affect the app) |
| Release APK | builds; version 3.12 (123); signed with the same key as every earlier version (installs over 3.10 and keeps your data) |
| Your 5 Nov backup | restores: 12,184 answers, 1,781 pages; 316 merged MCQs marked for revision; today's session 200 MCQs, 66 of them revision |

The tests run on the computer with a simulated Android (Robolectric), screens included; no emulator is needed. The
one thing they cannot do is open the installed APK on a phone: that is the check on your device.

## Problems found and fixed

1. **Weak spots lost in the merge.** 6,555 of your answers were on one-fact MCQs later merged into statement MCQs; the
   wrong and viewed ones no longer came back for revision. Now a merged MCQ is marked for revision when one of its
   old MCQs was (316 of them for you). Ones you got right stay new.
2. **Inflated counts.** The Today card's "to revise / mastered / only viewed" and the MCQs tab's "Answered wrong"
   counted MCQs not in this app (merged ones, Prep app answers in the same backup). Now only this app's MCQs.
3. **Page counts.** 20 topics have one more page in the MCQ notes ("More from this topic's MCQs") than in the full
   notes; it was left out of progress. Counted now, and counted as read in the notes that lack it.
4. **Topic screen.** "0 / 23 read" over 20 subsections shown, and "23 subsections" in the lists: now the pages shown.
5. **One-liners plan file** out of date after the priority plan: rebuilt.
6. **Lint** stopped on 8 false alarms (produceState): turned off with the reason written down.
7. Release copies of the tests could not start a screen (the test-only screen host is left out of release builds on
   purpose): they are switched off; the same tests run on the debug builds.

Found earlier today and fixed in 3.09-3.11: every statement marked in "Read from the notes", the quiz title fitting,
hidden pages left out of the notes view, the notes finder after switching notes, the 'Yavana Rajya Sthapanacharya' key.

## Checked and fine

- Data: 34,908 MCQs, every one on a plan day (88 days, 26 Oct - 21 Jan), no duplicate ids, every key in range, no
  empty or repeated options; the index counts match; 10,472 statement MCQs each with 3 statements, 3 explanation lines
  and a key that matches them.
- Both sets of notes load in full (17,663 pages each), all six books.
- Release APK contains every data file (both notes, MCQs, plan, merged map, hidden pages).

## Not changed (outside the Complete app)

- The Windows desktop build (old, 2.63) no longer compiles since the copy button and search sheet use Android-only
  parts. It is not part of the phone app.
- 574 PYQs have no key in their source papers (shown as "no key").

## APPSC Complete tests

| Class | Test | Result |
|---|---|---|
| CompleteTest | todayTabShowsDue | passed |
| CompleteTest | edition | passed |
| CompleteTest | pagesWithNothingForTheMcqsAreHiddenAndCountAsRead | passed |
| CompleteTest | readFromNotesOpensThePageWithTheAnswer | passed |
| CompleteTest | statementMcqSelectThenCheck | passed |
| CompleteTest | caBudgetPage | passed |
| CompleteTest | planMcqFileIsCurrent | passed |
| CompleteTest | group2Subject | passed |
| CompleteTest | aSubsectionPerBox | passed |
| CompleteTest | dueIsUnattemptedFromDay1 | passed |
| CompleteTest | notesTabGroup1AndGroup2 | passed |
| CompleteTest | currentAffairsTopics | passed |
| CompleteTest | aTopicIsOneListOfSubsections | passed |
| CompleteTest | currentAffairsSection | passed |
| CompleteTest | onelinerBackupRestoresHere | passed |
| CompleteTest | caUpiPage | passed |
| CompleteTest | everyStatementIsMarkedInTheNotes | passed |
| CompleteTest | theReadersBackupRestoresHere | passed |
| CompleteTest | mcqsTab | passed |
| CompleteTest | readFromNotesFindsTheAnswerForMostMcqs | passed |
| CompleteTest | everyMcqHasAGoodSearch | passed |
| CompleteTest | weakOneFactMcqsPassTheirRevisionOnToTheMergedMcq | passed |
| CompleteTest | everythingTheAppShipsLoads | passed |
| SyncShotsTest | todayTab | passed |
| SyncShotsTest | mcqsTab | passed |
