# Helper brief: rewrite Rocket One-liners MCQs as real one-line questions

Repo: /home/user/Group-app. Never use the Anthropic API. Do not commit, push or run git. Do NOT run
tools/rocket_oneliner.py without arguments (that rebuilds the app). Write only your own output files. Scripts only in
/tmp/claude-0/-home-user/4666e051-48dd-5910-831c-f2c172f98923/scratchpad/stN/, and only to view the batch or turn
your hand-written lines into JSON – every question and option is written by you, one by one, never by a template.

The user wants every MCQ to look like this (a real exam one-liner):

    Which Nikaya is the collection of kindred sayings?
    Samyutta Nikaya | Digha Nikaya | Khuddaka Nikaya | Majjhima Nikaya

and NOT like the machine-made ones in your batch:

    Brahmi; records his _____, his conflict with the Satavahanas ...      literary | stone | achievements | trigonometry
    Mehrgarh: Date – Key detail?                                          949 CE | 1925 | c. 7000 BCE | 1761

Your file data/rocketoneliner/style/sty-N.txt has 500 MCQs, each as:

    <id> [book:row topic]
      Q: the current stem
      O: 0) opt | *1) opt | 2) opt | 3) opt        (* = right answer)
      F: the fact from the notes it was made from

For EVERY MCQ write one line in data/rocketoneliner/style/sty-N.out.jsonl, in the file's order:

    {"id": "ka1a94ce523a", "s": "Which site gives the earliest evidence of agriculture (wheat, barley) in the subcontinent?", "o": ["Mehrgarh", "Kot Diji", "Amri", "Kalibangan"], "a": 0}
    {"id": "k27f0b2d9ae3", "s": "To about when is the Neolithic settlement at Mehrgarh dated?", "o": ["c. 7000 BCE", "c. 2600 BCE", "c. 1500 BCE", "c. 600 BCE"], "a": 0}
    {"id": "...", "drop": "the fact is only a heading / a study tip – nothing to ask"}

Rules:
- `s`: ONE clear question a student understands without the notes: it names the subject (the person, dynasty,
  site, scheme, Article, year, report ...) and starts with Which / Who / What / When / Where / How / In which /
  Under which / By whom / Whose / Name the / For what / During which / Near which / To whom ... (the full list is QWORD in tools/rocket_oneliner.py) and ends with "?". At most 150 characters. No blanks, no
  "X – Heading?", no "Key detail?", no "Identify". Keep the topic's key point – the same fact the MCQ tested.
- `o`: always give all 4 options: the right answer short (a name, place, year, number, term – not a whole sentence)
  and 3 wrong ones of the SAME kind (sites with sites, years with years, rulers with rulers), plausible, certainly
  wrong, taken from the same topic where you can. Keep the current options if they already fit; otherwise replace
  them. No "All/None of these"; no two options alike; the answer's words must not appear in the question.
- `a`: index 0-3 of the right option; spread it over the positions.
- The answer is the STARRED option (it was checked and corrected in a final fact review; where F, the notes, disagrees, keep the starred answer). If both are wrong and you are SURE, ask the correct fact.
  correct fact. If there is truly nothing to ask (a bare heading, a tip, a fragment), `drop` with why.
- Several MCQs from one table row may ask the same thing: make each ask a DIFFERENT point of the row, or drop the
  repeat ("drop": "repeat of <id>").

Then run `python3 tools/rocket_oneliner.py checkstyle N` and fix what it reports until "problems: 0". Finish with one
line per batch: MCQs, rewritten, dropped.
