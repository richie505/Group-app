# Helper brief: last review of the PYQs about to be added to the Group 2 app

Repo: /home/user/Group-app. Never use the Anthropic API. Do not commit, push or run git. Write only your own output
file. Scripts only in /tmp/claude-0/-home-user/4666e051-48dd-5910-831c-f2c172f98923/scratchpad/rvN/.

About 750 previous-year questions from other exams were judged one batch at a time by different helpers; the batches
did not always judge alike. Your file data/pyqfill/review/rev-N.txt lists about 100 of them, grouped by syllabus leaf:
"## <id> | leaf | page | source", the question, the options (the answer marked *), the explanation, and
"looks like: <ids>" when another add has a similar question. The syllabus is data/g2syl/leaves.md.

For EVERY question give one verdict:
- **keep** – fine as it is.
- **fix** – keep, with a correction: the answer index, an option, the wording or the explanation. Give only the
  changed fields: {"fix": {"a": 2}} or {"fix": {"s": "...", "x": "..."}}; a better notes page as "page": "b:r:j".
- **drop** (with `why`):
  1. a repeat: another add asks the same fact (keep the clearest one, drop the others – check the "looks like" ids,
     which may sit in another rev file: `grep -h '"<id>"' data/pyqfill/all/job-*.out.jsonl`), or the Group 2 app
     already asks it (`grep -l "<words>" app/src/group2/assets/mcq*.json`);
  2. out of date: the answer no longer holds (old statistics or rankings, "present"/"latest" holders, schemes,
     taxes or bodies abolished or replaced – Planning Commission, VAT, service tax, old cesses, JNNURM, IAY, SSA ...;
     old Census figures when newer ones exist);
  3. outside the syllabus under these common rules:
     - general science (plain physics, chemistry, biology) – only health and disease, biodiversity, energy,
       pollution, environment, space, defence, nuclear, biotechnology and computers/internet/cyber (M2B lines) stay;
     - old current affairs (before 2024): only lasting facts stay (an institution founded, a treaty, a mission or
       launch, a first, a scheme still running); awards, award lists, appointments, rankings, sports results and
       sports trivia, book-and-author trivia, obituaries, day themes and summit venues of that time go;
     - world geography: physical geography, climates, oceans and landforms stay; capitals, city nicknames and
       country trivia go;
     - ancient history: Indus, Vedic, Buddhism, Jainism, Mauryas, Guptas, Harsha (and AP's Satavahanas, Ikshvakus ...)
       stay; other dynasties' detail (Kushans, Shungas, Pallavas, Cholas beyond administration, Rajputs ...) goes,
       unless the question is really about Buddhism or a listed line;
     - other states' local facts go;
  4. a wrong or doubtful answer you cannot fix with certainty.

Write data/pyqfill/review/rev-N.out.jsonl, one line per question, in the file's order:

    {"id": "...", "v": "keep"}
    {"id": "...", "v": "fix", "fix": {"a": 1, "x": "..."}}
    {"id": "...", "v": "drop", "why": "repeat of gc-indi-1234abcd"}

Check: every id of the rev file has exactly one line; options stay 4 and "a" 0-3. Finish with one line:
questions, keep, fix, drop.
