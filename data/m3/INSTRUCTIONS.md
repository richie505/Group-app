# APPSC Complete: three one-fact MCQs into one statement MCQ

You turn groups of three one-fact MCQs into one APPSC-style question:

> Consider the following statements about <topic>:
> 1. …
> 2. …
> 3. …
> Which of the statements given above is/are correct?

The question text and the options are built by a script. **You write only the three statements, the topic and one
explanation line per statement.**

## Input (your packet: data/m3/in/<n>.md)

```
## M m1234abcd | <subsection title>
1. [TRUE] Q: <question> => ANSWER: <right answer> | WHY: <explanation>
2. [FALSE, use the wrong answer: <wrong option>] Q: ... => ANSWER: ... | WHY: ...
3. [TRUE] Q: ...
```

## Output (data/m3/out/<n>.md)

For every `## M` block, in the same order, copy its header line exactly, then:

```
## M m1234abcd | <subsection title>
TOPIC: Satavahana religion
1. Sriparvata, associated with Acharya Nagarjuna, is identified with Nagarjunakonda.
2. Nagarjuna's Suhrullekha was addressed to Yajna Sri Satakarni.
3. The Jain work Samayasara was written by Dinnaga.
WHY1: Correct: Sriparvata is identified with Nagarjunakonda, where Yajna Sri Satakarni built a Mahachaitya for Nagarjuna.
WHY2: Correct: the Suhrullekha ('friendly letter') was Nagarjuna's letter to his patron Yajna Sri Satakarni.
WHY3: Incorrect: the Samayasara was written by Kundakundacharya, not Dinnaga.
```

Rules:
1. **Each statement is the question and an answer, as one plain declarative sentence.**
   - **TRUE:** the sentence states the right answer.
   - **FALSE:** the sentence states **exactly the wrong answer given**, written as if it were true. It must be clearly
     wrong: never a sentence that could also be read as true.
2. Keep every fact the question turns on: names, years, numbers, places, Articles. Write a full sentence, never
   "Q? – A". No "Which", no question marks, no "(a)", no option letters.
3. **TOPIC**: 2–6 words that fit all three statements (e.g. "the Indus Valley Civilisation", "Satavahana religion",
   "AP's 2025 schemes"). It goes after "Consider the following statements about".
4. **WHY1/WHY2/WHY3**: one or two short sentences per statement.
   - Start with "Correct:" or "Incorrect:", matching TRUE/FALSE.
   - For an incorrect statement, give the right fact ("…, not Dinnaga").
   - Use the WHY given. Never add a fact from memory, never "correct" the given answer.
5. Never change TRUE/FALSE, never swap the statements' order, never merge or drop a block.
6. If a question cannot become a sentence (e.g. its answer is "All of the above" or it needs its options), write the
   sentence from the WHY all the same; if even that is impossible, write `SKIP` as that block's TOPIC line and
   nothing else for it.

Work in parts (about 25 blocks at a time) in your scratch folder
/tmp/claude-0/-home-user-Group-app/9d62697f-c2bc-5d71-9828-630e63a36f4a/scratchpad/m3-<n>/ (never in the repository),
then join them into data/m3/out/<n>.md. Check before you finish:

```
python3 - <<'X'
import re
n = "<n>"
a = re.findall(r"^## M (\S+)", open(f"data/m3/in/{n}.md").read(), re.M)
b = re.findall(r"^## M (\S+)", open(f"data/m3/out/{n}.md").read(), re.M)
print("missing", sorted(set(a) - set(b)), "extra", sorted(set(b) - set(a)), "order ok", a == b)
X
```

Report in two lines: blocks written, anything odd.
