# Helper brief: repair MCQ layout by hand

Repo /home/user/Group-app. Never use the Anthropic API. Do not commit, push or run git. Write only your own output
file. Scratch scripts only in /tmp/claude-0/-home-user/4666e051-48dd-5910-831c-f2c172f98923/scratchpad/lfN/ and only to read
or convert – every repair is yours, question by question.

Input: lines of data/layoutfix_todo.jsonl (your line range is given). Each has id, issues (automatic flags – may be false
alarms), stem s, options o, key index a (0-based), src. These are mostly scraped previous-year papers whose LAYOUT broke.

For every line write one JSON line to your output file:
  {"id": "...", "s": "<repaired stem>", "o": [<repaired options, same order>], "note": "<what you changed>"}
  or {"id": "...", "ok": true, "note": "false alarm: ..."} when nothing is wrong
  or {"id": "...", "skip": true, "note": "<why it cannot be repaired safely>"}
Omit "s" or "o" when that part is unchanged.

Target layout (what the app draws well):
- lead-in sentence on its own line; each statement / item on its own line as "1. ...", "a. ...", "I. ..." (keep the
  original labels – the options refer to them); the question line ("Which of the statements given above ...?",
  "Select the correct answer ...") on its own line after the last item.
- Assertion–Reason: "Assertion (A): ..." and "Reason (R): ..." each on its own line.
- Matching: "List I (title)" / items / "List II (title)" / items / closing line.

Allowed repairs (layout and scraping damage only):
- line breaks; split items run together on one line; move a glued question line to its own line;
- a list whose lead-in and first label were lost ("Carbon monoxide\n2. Methane ..."): restore "1. " and, if needed, a
  neutral lead-in such as "Consider the following:" / "Consider the following statements:" – nothing else;
- remove scraped junk: doubled words/punctuation from bad OCR ("field field??" -> "field?"), answer-sheet text stuck to an
  option ("Bokaro Answers with Explanations Q1 Answer:" -> "Bokaro"), page/paper furniture;
- OCR'd labels/codes ("a-l" -> "a-I", "b-1" -> "b-I") when the other options make the intended label certain;
- an option that is pure garbage ("2. 3. 4.") or two identical options: only fix when the original wording is certain from
  the question/explanation/other options; otherwise "skip" with a note.
Never change the meaning of the question, any fact, the order of options, or the key. "option-label-prefix" flags are
mostly false alarms ("(A) and (B) only", "B. R. Ambedkar") – answer ok:true for those.

Finish: check every id of your range appears exactly once in your output; report counts repaired / ok / skipped.
