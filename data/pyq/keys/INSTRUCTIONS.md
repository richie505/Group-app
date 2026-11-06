# Answer keys for APPSC bank questions that have none

Your packet (data/pyq/keys/in/<pkt>.md) lists bank questions (id, number if known, stem, 4 options) that come from
one APPSC paper and have no answer key, and the Drive files that should hold that paper's key. Write
data/pyq/keys/out/<pkt>.json: {"<question id>": {"a": <0-based index into THE PACKET's option list>, "how": "<key file + its Q no.>"}}.
Edit nothing else; do not commit.

- Load Drive tools: ToolSearch "select:mcp__Google_Drive__download_file_content,mcp__Google_Drive__read_file_content".
  Try read_file_content first; if it has no usable text, download_file_content (the result is saved to a file: decode
  the base64 with python to /tmp/claude-0/-home-user-Group-app/9d62697f-c2bc-5d71-9828-630e63a36f4a/scratchpad/pdf/<pkt>-<k>.pdf) and read pages
  with the Read tool (pages "1-20" ...). Big files: use the "Part n of m" copies listed in data/pyq/drive_inventory.json.
- Match each packet question to the key's question by its TEXT (question numbers and option order can differ between
  sets/codes; official keys often print only the right option's text: match that text to the packet's options).
  Final key over initial key; a "DELETED" question: leave it out.
- Give a key ONLY when the key file shows it. Never answer from memory. If the listed files are not this paper, look
  for the right one in data/pyq/drive_inventory.json (identify the paper from its questions); if none, leave it out.
- Reply with one line: "<pkt>: <k> of <n> keyed from <file(s)>; <m> not found".
- Drive refuses downloads over about 8 MB. Use the "Part n of m" split copies (data/pyq/drive_inventory.json:
  entries whose "source_id" is the big file's id, or same title + " - Part n of m"), or a smaller copy of the same key.
