# Fixing the review list (after the MCQ coverage pass)

`data/mcqcut/flags.txt` lists MCQs and notes the coverage agents found wrong or doubtful, one line per
batch: `b<book> <batch>: ...`. Labels `Qr.n` are positions in the pre-cut copy
`work/mcqcut/b<book>/orig.json` (`rows[r][n]`); find the MCQ by its `id` in the live asset
`app/src/main/assets/mcq<book>.json` (labels no longer match positions there). An MCQ the line says was
"dropped" is gone: nothing to do.

For your book, go through every line and decide:

- **Fix** when you are confident of the correct fact (standard reference knowledge, or the notes'
  own stronger statement): wrong answer key, wrong fact in a stem/option/explanation, two correct
  options, duplicate options, garbled text, typos. Change the fewest words; keep 4 distinct options and
  exactly one correct answer; make the WHY (`x`) agree with the key. Do not add, remove or reorder MCQs.
- **Fix the notes too** (`app/src/main/assets/book<book>.json`, the block text inside `units → rows →
  secs → b`) when the line says the notes carry the same error or contradict themselves, and you are
  confident which version is right. Edit only the wrong words in place; keep the block structure.
- **Leave** anything you are not confident about, and list it for human review.

Edit the JSON with a short Python script (load, change by `id` / exact substring, dump with
`ensure_ascii=False, separators=(",", ":")`). Never touch `index.json` or other books.

Write `data/mcqcut/fixes_b<book>.md`: two sections, **Fixed** (one line each: label, id, what changed,
and "notes too" if so) and **For review** (one line each: label, the doubt, why not fixed).
