# Transcribe PYQs from the "latestpyqs" books (Drive folder latestpyqs)

Three scanned books, split into parts, are downloaded as PDFs in
/tmp/claude-0/-home-user-Group-app/9d62697f-c2bc-5d71-9828-630e63a36f4a/scratchpad/latest/:
- b1p1..b1p4: Shreshta "APPSC PYQs (2008-2025) with explanation": whole papers (Group-2 Prelims 2024, Group-2 Mains
  2025, Prelims 2019, Mains 2019/2017 Papers ...), answers + explanations in an EXPLANATIONS block after each paper.
- b2p1..b2p4: RRR "AP History Previous Papers": AP history questions, each tagged with its exam (GROUP-I 2023, GROUP-II
  2008, SI Prelims 2023 ...), answer blocks "N. Answer:4:- explanation" after each block of questions.
- b3p1..b3p4: Shreshta "APPSC Group-1 & 2 Prelims & Mains PYQs": whole papers with an ANSWER KEY ("Q1 - Answer: (2)
  Explanation: ...") after each paper.
Each part also has a text layer: <name>.layout.txt in the same folder (pdftotext -layout; pages split by form feed
\f). Two-column pages: the text layer mixes columns, so READ THE PAGE IMAGES with the Read tool (file_path = the pdf,
pages = "3-5"; at most 20 pages per call) and use the text only to help.

You own the questions PRINTED on your pages (your part, pages A-B). For each:
- Find its answer: in the answer block on your pages, or, if that block comes later, on the following pages (also the
  next part, e.g. b1p2 after b1p1). Ignore answer blocks at the start of your pages that belong to questions before
  your pages.
- Find its exam: the paper heading (look back to earlier pages if the paper started before your pages) or the tag on
  the question. Write it as e.g. "APPSC Group-II Prelims 2024 (25-02-2024)", "APPSC Group-I 2023 (08-01-2023)",
  "AP Police SI Prelims 2023". Non-APPSC exams (Police, VDO, DSC, ...) are written as such.
- Skip mental ability / aptitude / reasoning / maths / English questions, and questions in Telugu only.
- Transcribe stem and the 4 options exactly (fix only obvious OCR typos). Statements / lists / pairs each on its own
  line ("\n"). Match-the-list: put both lists in the stem and the codes as options.
- a = 0-based index of the book's answer (book prints 1-4 or (1)-(4) or A-D). If the book marks the question deleted
  or gives no answer, a = -1.
- x = the book's explanation, shortened to at most 2 sentences (may be "").

Write data/pyq/new/latest-<part>-<A>.jsonl (e.g. latest-b1p2-9.jsonl), one JSON object per line:
{"id":"latest-<part>-<A>-<k>","exam":"...","paper":"...","year":"2024","source":"latestpyqs <book title> p<page>",
 "file":"APPSC - latest.md","n":<printed number>,"s":"...","o":["","","",""],"a":0,"x":"..."}
For a non-APPSC exam use "file":"Other - latest.md". Validate every line with python json. Touch no other repo file;
do not commit. Reply only: "<part> <A>-<B>: <n> questions (<k> with answer), skipped <m> (aptitude etc.)".
