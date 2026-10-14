# Checking every full form the notes show

The app adds a grey full form after the first use of a short form on each page ("NITI (National Institution
for Transforming India)") and read-aloud says it. One was wrong: "VC (venture capital)" on a NITI Aayog page,
where VC is the Vice-Chairperson. Your batch `work/acr/in_NNN.md` lists, per short form, the current list of
meanings and **every place** the app shows a full form, one per line: `page <TAB> full form shown <TAB> the line`.

## Current list format
`=== VC   current list: venture capital [] | Vice-Chancellor [universit, Chancellor]` — each meaning with the
words that pick it (`[]` = the default, used when no other meaning's words are on the page).

How the app picks: it looks at the whole page (all its text, plus the topic and page titles) and the line.
Each meaning scores 1 per word found (2 for `@b`, "the page is in book b"); the highest score wins; with no
hits, the default (`[]`) is used. Word rules: lowercase `universit` matches any word **starting** with it, any
case; a word with capitals (`NITI`, `UP `) matches exactly as written; `@1`..`@6` = the book (1 History,
2 Polity/Society/IR, 3 Economy, 4 Geography, 5 Science/Tech/Environment, 6 Current Affairs).
A meaning of `-` means "show nothing, read it as written" (names, labels, Roman numerals, words in capitals).

## What to do
For each short form, read every line and decide whether the full form shown is right **in that line**.
If all are right, write nothing. If any is wrong, write the corrected **complete** list of meanings so that
every line gets the right one: add the missing meaning with words that pick it (words that appear on those
pages but not on the pages of the other meanings), fix a wrong default, fix a misspelt or wrong full form,
or use `-` where nothing should be shown. Prefer standard Indian-exam usage (VC on a university page:
Vice-Chancellor; on NITI Aayog / Planning Commission: Vice-Chairperson; with funds/startups: venture capital).
Choose words carefully: a word common to many pages will pick the meaning everywhere.

## Output: `work/acr/out_NNN.jsonl`
One line per short form you change:
`{"acr":"VC","senses":[["Vice-Chairperson",["NITI","Aayog","Planning Commission"]],["Vice-Chancellor",["universit","Chancellor"]],["venture capital",[]]],"why":"NITI page said venture capital"}`
— exactly one meaning with `[]` (the default). If a wrong full form comes from something the list cannot fix
(the line shows "(not in acronyms.tsv…)"), you can still add a list for it here: the list is used for most short forms (a few are decided by built-in rules; list them anyway).
Last line: `{"done":N}` with N = the number of short forms (`===` lines) in the batch.
Check with `python3 tools/acr_audit.py check NNN` until it passes. Write only that file.
