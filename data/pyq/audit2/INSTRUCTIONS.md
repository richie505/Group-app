# Audit of newly added APPSC previous-year questions

Each entry is a previous-year question shown in the app: some read from scans of the papers, some OCR'd from books
and given their answer from APPSC's official key. Check each one reads as a clean, complete MCQ. A user found one like
this in the app:

    Hathigumpha inscription of Kharavela gave the IV. Visakhadatta-Mudrarakshasa details of irrigation facilities provided in the
    0. I and II only   1. II and III only Kalinga Region by   2. I, II and III   3. All of the above

(statements I-III lost, a fragment of another line run into the stem and into an option). That must not be shown.

For each id decide:
- {"keep": true} : clean as it is (a stem that makes sense on its own; 4 real options belonging to it; any
  statements / pairs / lists the options refer to are present in the stem). Most should be this.
- {"keep": true, "s": "...", "o": [4 options], "a": <same index as given>, "x": ""} : repairable from what is there
  (debris, run-in words, statements on one line - put each statement on its own line with "\n"). Keep the original
  wording, the option order and the given ANSWER index. Never invent missing statements or options.
- {"keep": false, "why": "aptitude"} : any mental ability / aptitude / reasoning / maths question (series, coding,
  blood relations, directions, seating, ages, ratios, percentages, averages, time-work, clocks, calendars, dice,
  figures, syllogisms, data interpretation, analogies, odd one out, English grammar or vocabulary). The apps cover
  General Studies only.
- {"keep": false, "why": "..."} : statements / list / options missing, or parts of another question mixed in, or the
  stem does not make sense, or the given answer is plainly impossible for the options shown.

Do not change answers from your own knowledge. Write data/pyq/aph/out-au<N>.json (N = your packet number) as one JSON
object with every id of your packet. Validate with python3 -c "import json;json.load(open('<file>'))". Touch no other
file, do not commit. Reply with only: <N>: kept / repaired / dropped.
