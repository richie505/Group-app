# APPSC Complete: the MCQ notes in simple English

You make each line of the notes easier for an APPSC aspirant to read, in **simple English**, using **only what the
line already says**. You never add a fact, never remove a fact, and never make a line longer.

## Input (your packet: data/simple/in/<n>.md)

```
## P 2:14:3 | <topic> | <page title>
L2:14:3:1 **★ **Elected by **both Houses of Parliament**, **PR-STV** (**Article 66**); **not appointed** by the President
L2:14:3:2 **★ ****State Legislatures do not take part** in electing the VP
```

`## P` lines give the topic and page (context only). Each `L<id> <text>` is one line of the notes; `**...**` is bold.

## Output (data/simple/out/<n>.md)

Every `L` line of the packet, in the same order, with the same id, then a space, then the line in simple English
- or `=` alone if the line is already simple and plain (most short lines are):

```
L2:14:3:1 **★ **Chosen by **both Houses of Parliament**, by **PR-STV** (**Article 66**); **not appointed** by the President
L2:14:3:2 **★ ****State Legislatures have no role** in choosing the VP
L2:14:3:5 =
```

Do not copy the `## P` lines.

## Rules

1. **Same facts, nothing new.** Every name, number, date, year, %, Article, Act, place and term stays. Use only what
   the line says: no fact, example or explanation from memory.
2. **Never more words** than the line has. Same or fewer.
3. **Bold stays bold, word for word.** Every `**...**` part must appear again exactly (same spelling, same
   characters), in any order. You may change the plain words around them. Do not add new bold. Keep `★ `, `⚠ `,
   `→`, `=` signs where they carry meaning (`→` and `—` may stay as they are).
4. **Simple English:** short common words for hard ones ("brought in" for "introduced", "has no role" for "does not
   take part", "kept" for "undistributed", "set by" for "triggered by", "part of" for "integral part of",
   "ripens slowly" for "delayed ripening"); clear order (who/what — then the fact); split a long tangle with a
   semicolon. Keep exam terms that must be learnt as they are (collective responsibility, no-confidence motion,
   ex-officio, PR-STV, repo rate, CRISPR ...).
5. If a line is already simple, write `=`. Do not change a line just to change it.
6. Never merge, split, drop or reorder lines.

Work in parts (about 100 lines at a time) in your scratch folder
/tmp/claude-0/-home-user-Group-app/9d62697f-c2bc-5d71-9828-630e63a36f4a/scratchpad/simple-<n>/ (never in the
repository), then join them into data/simple/out/<n>.md. Check before you finish:

```
python3 tools/simple_build.py --check <n>
```

It lists any line that breaks a rule (bold changed, a number lost, longer than before); fix those or write `=`.
Report in one line: lines changed, lines kept (`=`).
