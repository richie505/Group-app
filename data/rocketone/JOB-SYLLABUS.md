# A RocketOne syllabus notes job

You were given a job name `<job>`. Read data/rocketone/GUIDE-NOTES.md fully and follow it exactly.

- Source: work/rocket/topics/<job>.jsonl (Rocket rows; read ALL of them). Output: data/rocketone/notes/<job>.json.
- The text of each syllabus line (leaf code) is in work/rocket/leaves.txt: use it to title and scope each lecture.
- One lecture per leaf in the file. Split a very large leaf into several lectures by sub-topic, all with the same leaf
  code. A job named `...-pN` is one part of a large syllabus line split over several jobs: write one or more lectures
  for what THIS file holds, titled by their sub-topic.
- Merge the repeats Rocket has across sheets. Settle only real disagreements (web-check with WebSearch; load it with
  ToolSearch "select:WebSearch" if needed) and write only the corrected line, recording it in `corrections`.
- A row with an empty cell or a cut-off cell stays as Rocket has it: do not fill it from memory.
- Other agents share the scratchpad: keep helper files in your own subfolder named after your job.
- When done run `python3 tools/rocketone.py check-notes data/rocketone/notes/<job>.json` and fix until it prints OK.
- Write only that one notes file in the repo; do not commit. Reply briefly: job, lectures, corrections, anything odd.
