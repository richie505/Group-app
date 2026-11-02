# APPSC Complete 2.0: notes from the MCQs

You write the notes pages of a study app for the APPSC (Andhra Pradesh) Group 1 / Group 2 exams. Each page is one
**subsection** of the syllabus, and it must cover **exactly what that subsection's MCQs test**: a student reads the
page, then practises its MCQs and can answer every one of them.

## Input (your packet: data/c2/in/<n>.md)

```
# ROW 1:0 | <section title>
## SEC 1:0:0 | <subsection title>
- Q: <question> => ANSWER: <the right option> | WHY: <explanation> | PYQ: <exam>     (PYQ part only for previous-year questions)
- Q: ...
## SEC 1:0:3 | <subsection title>
...
```

`SEC b:r:-1 | (whole topic)` holds MCQs filed under the whole section: write a page for it like any other.
An ANSWER "(no official key)" has no confirmed answer: use only what its WHY confirms, else leave that MCQ out.

## Output (data/c2/out/<n>.md)

The same `# ROW` and `## SEC` header lines, copied exactly (same ids, same titles), each SEC followed by its notes:

```
## SEC 1:0:0 | Literary sources: work & author
### Kashmir chronicles
- ★ **Rajatarangini** (12th c., Sanskrit) — **Kalhana**; chronicle of the kings of **Kashmir**
- ★ Continued by **Jonaraja** and **Srivara**
### Satavahana-age texts
| Work | Author | Note |
|---|---|---|
| Brihatkatha | Gunadhya | in **Paisachi** |
| Gathasaptasati | King **Hala** | Prakrit verses |
- **Harshacharita** (Banabhatta) calls **Yajna Sri Satakarni** "Trisamudradheesvara"
  - sub-point under the bullet above (two spaces, then "- ")
```

Rules:
1. **Only facts the MCQs confirm**: the right answers and what the WHY says. Never add a fact from memory, never
   "correct" an MCQ, never turn a wrong option into a fact. If an answer and its WHY disagree, use only what both
   support.
2. **Every MCQ is covered**: each MCQ's tested fact appears on its page (the fact, not the question). Several MCQs on
   the same fact: one bullet. Keep the specifics the questions turn on (names, years, numbers, places, Articles).
3. **Fact bullets**: one fact per line, short, no full sentences needed ("**Kalhana** — Rajatarangini (12th c.)").
   **Bold** the key word of each fact (the name, year, number the MCQ asks for). No paragraphs.
4. **★** at the start of a bullet whose fact a **PYQ** asked (an MCQ with "| PYQ:"). Only those.
5. **Headings** (`### ...`, short) to group bullets when a page has more than about 6 facts. Order the facts so they
   read well: chronological, or by theme.
6. **Tables** (markdown, header row + `|---|` row) when 3 or more facts share the same fields (work / author;
   dam / river / state; article / subject). Bold inside cells is fine.
7. The subsection's title is the frame: the facts on its page belong together. Do not move facts between SECs.
8. Plain text only otherwise: no links, no numbering of the MCQs, no "Q:", no answer letters, no "Option 3".

Work through the packet in parts (e.g. 4–6 ROWs at a time) and write each part to your own scratch folder
/tmp/claude-0/-home-user-Group-app/9d62697f-c2bc-5d71-9828-630e63a36f4a/scratchpad/c2-<n>/ (never anywhere in the
repository), then join them into data/c2/out/<n>.md. Check before you finish:

```
python3 - <<'X'
import re
n = "<n>"
src = re.findall(r"^## SEC (\S+)", open(f"data/c2/in/{n}.md").read(), re.M)
out = re.findall(r"^## SEC (\S+)", open(f"data/c2/out/{n}.md").read(), re.M)
print("missing", sorted(set(src) - set(out)), "extra", sorted(set(out) - set(src)))
X
```

Both lists must be empty, and no SEC may be left without notes. Report in two lines: SECs written, anything odd.
