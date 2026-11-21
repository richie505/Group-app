# Helper brief: Telugu narration for the lecture videos (one job, about 10 topics)

The APPSC Lectures videos show each topic's English Rocket-style slides, one row at a time, while a Telugu voice
(Piper, te_IN-padmavathi) explains it. You write the Telugu narration. Repo: /home/user/Group-app.
Never use the Anthropic API. Do not commit, push or run git. Keep scripts in
/tmp/claude-0/-home-user/4666e051-48dd-5910-831c-f2c172f98923/scratchpad/vidN/.

Your job file data/lecvideo/jobs/job-N.txt lists topics ("## topic group2 B-R | title"), each with its parts
("### part J: title") and their blocks, numbered: "[b] h: heading", "[b] b: bullet", "[b] x: box",
"[b] table: header" with rows "[b.r] cell | cell". Example of the style: data/lecvideo/group2/1-37.bilingual-part1.json
(its "te" lines; Part 1 of the Gupta Society topic).

For EACH topic write data/lecvideo/group2/B-R.json:

    {"intro":  [{"te": "స్వాగతం. ఈ పాఠంలో ... గురించి తెలుసుకుందాం."}, {"te": "<the parts, one line>"}],
     "parts":  {"0": [{"b": 1, "r": null, "te": "<optional one-line lead-in to the table>"},
                      {"b": 1, "r": 0, "te": "<explains row 1.0>"}, {"b": 1, "r": 1, "te": "..."}, {"b": 2, "r": null, "te": "<explains bullet 2>"}],
                "1": [...]},
     "outro":  [{"te": "<recap in 2-3 sentences>"}, {"te": "ఇప్పుడు ఏపీపీఎస్సీ గ్రూప్ టూ యాప్‌లో ఈ అంశంపై ఎంసీక్యూలను సాధన చేయండి. ధన్యవాదాలు."}],
     "recap":  ["<3-4 short ENGLISH points for the last card, with **bold** key terms>"]}

Rules:
1. **Every table row and every bullet / box gets its own beat**, in slide order ("b" = block number, "r" = row number
   for a table row, null otherwise). Headings need no beat; a lead-in beat on a table ("r": null) is optional.
2. **Explain like a teacher, in natural spoken Telugu**: one or two sentences per beat, ~15-40 words. Say the fact
   and make it clear (what it is, why it matters); never add facts that are not on the slide. No quiz talk.
3. **Telugu script only** – the voice cannot read Latin letters: write names and terms in Telugu script
   (తామ్రలిప్తి, విష్ణుకుండినులు, ఏపీపీఎస్సీ, జీడీపీ, రెపో రేటు). Digits are fine (476, 1956); write "క్రీ.శ." /
   "క్రీ.పూ." for CE / BCE. No English words in Latin letters, no ** marks in te lines.
4. The "recap" list is English (it is shown on screen), 3-4 points, each under ~15 words.

Then run `python3 tools/lecvideo_jobs.py check N` and fix everything it reports until "0 with problems".
Finish with one line: topics written, problems left.
