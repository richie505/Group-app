# Settling the review list

`data/mcqcut/fixes_b<book>.md` has a **For review** section: MCQs and notes the fix pass was unsure about.
For each item of your book:

1. Check the fact against reliable sources (WebSearch / WebFetch): official sites (gov.in, nic.in, RBI,
   ISRO, UNESCO, Census, Finance Commission reports, PIB), standard references, Wikipedia with citations.
   For an APPSC answer key versus the standard fact, follow the standard fact and keep a one-line
   "⚠ APPSC key said X" note in the MCQ's WHY (`x`) and in the notes when the key is cited there.
2. **Fix** when the sources agree: the MCQ in `app/src/main/assets/mcq<book>.json` (find it by `id`; change
   the fewest words; 4 distinct options, one correct answer, WHY agrees with the key) and the notes in
   `book<book>.json` when they carry the same claim (edit the wrong words in place). Do not add, remove or
   reorder MCQs; never touch `index.json` or other books.
3. **Leave** it when the sources disagree or you can't confirm it.

Edit JSON with a short Python script (`ensure_ascii=False, separators=(",", ":")`).
Append to `data/mcqcut/fixes_b<book>.md` a section **Review settled**: one line per item — fixed (what, and
the source) or left (why).
