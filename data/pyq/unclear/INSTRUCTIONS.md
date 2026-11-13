# Checking the "unclear" PYQs against the scanned pages

Each packet `data/pyq/unclear/in-<NN>.json` lists questions whose OCR text lost something ("[?]") when the books were
read. Each item names the scanned PDF and page (`pdf`, `pdf_page`). For every item:

1. Look at the page image: Read tool, `file_path=/home/user/Group-app/<pdf>`, `pages="<pdf_page>"` (if the question is
   not there, try the page before/after; a question can run onto the next page). Zoom by reading the page again if
   needed; you may also render a crop with `pdftoppm -f <p> -l <p> -r 200 -png` into your scratch folder.
2. Read the question exactly as printed: stem, all options in order, and the key from the paper's answer grid (the
   grid is usually at the end of that paper, a page or two later) or a tick printed on the page.
3. Write one result per item to `data/pyq/unclear/out-<NN>.json` (a JSON list):
   {"id": "<id>", "status": "fixed", "s": "<stem>", "o": ["<opt1>", …], "a": <0-based key or -1>}
   for a flashcard (item has "k": "f"): {"id", "status": "fixed", "s": "<question>", "at": "<printed answer>"}
   or {"id": "<id>", "status": "unreadable", "why": "<short reason>"} when even the image cannot be read with certainty.
   - Keep the item's own wording where it was right; fix only what the image shows. No "[?]" may remain in a fixed item.
   - The key: only if the grid (or tick) is certain; if a clearly read key contradicts a well-established fact, -1.
   - Mental ability / reasoning questions: {"id", "status": "drop", "why": "mental ability"}.
4. Validate with Python: every input id appears exactly once; fixed items have a non-empty stem, 4 or 5 non-empty
   options without "[?]" and a in -1..len-1 (or s and at for flashcards).

Edit nothing else; do not commit. Reply with one line per packet: "<NN>: <fixed> fixed, <u> unreadable, <d> dropped".
