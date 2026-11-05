# APPSC Complete: put each MCQ's missing fact into its notes page

Each `## PAGE` block shows a page of the MCQ notes (its current lines, `#` = heading) and, below, `F<k>` lines: MCQs
whose fact is not on that page yet (question, answer, explanation).

For every `F<k>` write ONE output line, in the same order:

```
F12 | <heading> | **Parliamentary laws** set up the regional councils
F13 | SKIP
```

- `<heading>`: one of the page's headings (`#` lines) copied exactly, the one the fact belongs under; or `NEW: <2-4 word
  heading>` if none fits; or `-` if the page has no headings.
- The line: the fact the MCQ tests, as ONE short note line in simple English (at most 25 words), like the page's own
  lines ("**term** — fact"). Bold (`**...**`) the answer or key term. Use ONLY the question, answer and explanation
  given: no fact from memory. For a 3-statement MCQ, write the TRUE fact (for a false statement, the correct fact from
  its explanation). For Assertion-Reason, write what is true.
- `SKIP` when the page's current lines already state this fact (even spelt differently), or when the MCQ has no single
  fact to note (a list of names, an answer code with no explanation, "All of the above" with nothing to say).

Write data/sync/out/<n>.md. Check: every F id of the packet appears exactly once, in order:

```
python3 - <<'Y'
import re; n="<n>"
a=re.findall(r"^(F\d+) ", open(f"data/sync/in/{n}.md").read(), re.M)
b=re.findall(r"^(F\d+) \|", open(f"data/sync/out/{n}.md").read(), re.M)
print("missing", sorted(set(a)-set(b))[:5], "extra", sorted(set(b)-set(a))[:5], "order ok", a==b)
Y
```
