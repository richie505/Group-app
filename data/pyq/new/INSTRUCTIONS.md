# Reading an APPSC question paper from Drive into the PYQ bank

You get one Drive file (an APPSC question paper, usually with its key) by file id. Turn its General Studies MCQs into
data/pyq/new/<name>.jsonl, one JSON object per line. Edit nothing else; do not commit.

## Getting the pages
1. Load the Drive tools: ToolSearch "select:mcp__Google_Drive__download_file_content,mcp__Google_Drive__read_file_content".
2. Try read_file_content first: if it returns the questions' text (stem + options), use that text.
3. Otherwise (scans, or the official "Final Keys" PDFs whose text layer holds only "Question Number : n ... Options :"):
   call download_file_content. Its result is saved to a file (the tool says where): decode the base64 with python
   (json.load the saved file if it is JSON; the base64 is in the content/data field) into
   /tmp/claude-0/-home-user-Group-app/9d62697f-c2bc-5d71-9828-630e63a36f4a/scratchpad/pdf/<name>.pdf.
   Then read the PDF pages with the Read tool (pages "1-10", "11-20", ...: up to 20 pages a call) and transcribe.
   If the PDF is too large for one Read, split it with `pdfseparate`/`qpdf` or `python3 -c "import pypdf"` if present,
   else read page ranges.

## What to write (one line per question)
{"id": "<name>-<n>", "exam": "<exam name as the inventory gives it, e.g. APPSC - 2019-12 Food Safety Officer>",
 "paper": "<paper, e.g. Paper-I General Studies & Mental Ability>", "year": "<year>", "source": "APPSC <official key | question paper with key> (Drive: <file title>)",
 "file": "APPSC - <name>.md", "n": <question number>, "s": "<stem>", "o": ["<opt1>","<opt2>","<opt3>","<opt4>"],
 "a": <0-based key, or -1 if the paper gives no key>, "x": ""}

## Rules
- Only General Studies questions (history, polity, economy, geography, science & tech, environment, current affairs,
  AP-specific GS). SKIP mental ability / reasoning / maths / data interpretation / English grammar questions, and
  subject-paper questions (engineering, medicine, forestry technical, etc.).
- Transcribe EXACTLY what the paper says: the stem, the four options in their printed order, statements on their own
  lines ("1. ...\n2. ..."), List-I/List-II as printed, codes as printed. Fix only obvious OCR/scan noise. English only
  (bilingual papers: take the English text). Never invent a question, an option or a key.
- The key: from the paper's own key (official "Final Key" marks the right option, often with a tick or a green/bold
  option, or a key table at the end; Sakshi "with Key" papers print the answer). Use the FINAL key over the initial key.
  "DELETED" / dropped questions: skip. If you cannot read the key for a question with certainty, a = -1.
- If a page is unreadable, skip those questions; do not guess text.
- At the end print a one-line summary: "<name>: <n> GS questions written (<k> with key), <m> skipped (mental ability etc.)".
Reply with only that line.
