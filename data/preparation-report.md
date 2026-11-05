# APPSC Complete: preparation analysis and what changed (3.05)

Source: the reader's backup of 5 Nov 2026 (the original file is untouched; a working copy was used). Every number
below was read from that file or from the app's own data with `tools/dup_report.py` and the app's tests.

## What the backup fields mean (from the app's code)

| Field | What it is |
|---|---|
| `answers` (12,184) | One per MCQ: its **latest** result, `id:1` right / `id:0` wrong. Re-attempts overwrite it. |
| `seen` (1,307) | MCQs whose answer was **viewed before picking** ("Show the answer"), plus MCQs without a key that were practised (38 of them). |
| `missed` (2,156) | MCQs **ever** answered wrong (kept after a later right answer). |
| `done` (1,781) | Notes pages marked read (`book:row:sec`), not MCQs. |
| `log` (27) | Per device and day: practised MCQs (every pick, incl. re-attempts and viewed answers), right answers, seconds on notes, seconds on MCQs. |
| `spent` (1,804) | Per day and per notes page / quiz: seconds and MCQs. |
| `dates` | Days with any study. `edits` (248): your MCQ corrections. `added` (9): your own notes. `saved` (1): bookmarked page. `noteRounds`: which note-id moves were applied. |
| `rate` 1.5 / `scale` 1.0 | Read-aloud speed and text size. |
| `device` | This phone's id; other devices' logs are kept apart and added up per day. |

## Your actual practice (APPSC Complete MCQs only)

- 10,168 MCQs answered at least once; 9,870 right on the latest attempt, 298 wrong now.
- 1,890 were wrong at some point; 1,592 of those are right now.
- Answers viewed first: 1,065 (excluding the 38 key-less ones); 818 of them were later answered, 278 never were.
- **Viewing is rising:** 1,006 viewed in the 3 Nov backup → 1,307 on 5 Nov. On 4 Nov you practised 922 MCQs but got
  519 right: about a third of that day was answers viewed.

Daily practice (all devices, days with 100+ MCQs, last 20): median 825, average 752, lower quarter 620, lowest 191;
last 7 days 551–1,111 (median 964). About 19 s per MCQ, so 600 MCQs ≈ 3 h 10 min plus reading explanations.

## Daily targets (worked out in the app every day; nothing carries over)

From the last 14 days' practice days:
- **Standard** = the lower quarter (a normal day, not your best): **600** today.
- **Minimum** = half: **300**, about your lightest full days (327 and 330).
- **Stretch** (optional) = about your typical good day: **950**.
- Three practice days in a row well under the standard bring it down by 15%. A light day adds nothing to tomorrow.
- Sessions of 200 (3 make the standard). Each starts with the revision that is due (at most a third), then new MCQs
  in the plan's order. Extra copies of the same MCQ are left out.

## Answer tracking (from 3.05)

Every MCQ now keeps its attempts: right on its own, wrong on its own, or answer viewed first, and the day.
Mastery: **New** (never tried), **Learning** (answer viewed, not yet answered on its own), **Needs revision** (latest
own answer wrong), **Improving** (right after a slip or a view), **Mastered** (right first time on its own, or twice in a
row). A viewed answer never counts as solved. Revision: wrong and viewed come back the next day, improving after three
days, mastered not by itself. Older answers were turned into histories on first start (and on restore of an older
backup). Your 5 Nov backup restores with every answer, page mark and history (tested).

Answering: tap an option to select it, then **Check answer** (or tap it again). The answer shows only after a choice.

## Question bank check (`data/merge-report.md`)

55,852 MCQs (15,659 PYQs, 40,193 the app's own). 427 groups of exact duplicates (same text, same options) with 435
extra copies; 24 of the groups have conflicting keys (listed, kept apart). 1,194 near-duplicates flagged for review,
none removed. 3,520 MCQs have no explanation, 574 no key. Unique: 55,417. The 406 extra copies whose keys agree are
left out of daily sessions (still in their sections).

## Notes

APPSC Complete now carries the notes written from its MCQs (Complete 2.0's) as **MCQ notes**, the default, with the
**full notes** kept whole: a switch at the top of the Notes tab. Same pages and ids, so marks and links stay. The book
icon on an MCQ opens the notes in use.

## Still to do

The 3-statement merge (31,428 one-fact MCQs → 10,476 "Which of the statements given above is/are correct?"
questions, pre-2022 pattern): packets are ready in `data/m3/`; the writing resumes after the usage limit resets
(6 Nov, 2 pm UTC).
