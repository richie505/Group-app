## Facts the notes lack: search the web (the user's rule)

Some angles have no fact in the notes, so no MCQ could be written: a blueprint keyword whose facts are not in the
notes, or an APPSC PYQ angle (even one with no key) the notes do not cover. Do not skip these any more. For each one:

1. Search the web (WebSearch; WebFetch to read a page). Prefer official and standard sources: government sites
   (gov.in, nic.in, pib.gov.in, AP government portals), RBI, ISRO, UN bodies, NCERT, Britannica, reputed newspapers.
   Use a fact only if two sources agree or one official source states it. For current data, take the latest figure
   and say which year it is for.
2. Add the fact to the notes: a `notes` entry in your output (the format of tools/notes_fix.py, run with
   NOTES_APP=complete), normally appended to the subsection it belongs to:
   `{"book": 2, "row": 134, "sec": 3, "append": true, "md": "- **Title:** fact in one or two short sentences."}`
   Simple English, the notes' own style, only facts APPSC could ask. Never change or delete existing note text.
3. Write 1-2 MCQs on it (all the usual rules; `sub` = that `sec`), and add `"web": "<source URL>"` to each such MCQ.
4. Never use the web to overrule the notes or a recorded APPSC key. If the web contradicts the notes, write no
   note and no MCQ; list the conflict in your report.
5. If no reliable source settles the fact, leave it out and say so.

Check the notes edits with `NOTES_APP=complete python3 tools/notes_fix.py apply <a file with just your notes list> --dry`
(all ok) as well as the usual `angle_add.py --dry`. In your reply, add: `W web facts added (notes + MCQs)`.
