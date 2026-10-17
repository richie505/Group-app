# Structured MCQ explanations (Testbook-style "Solution" + "Additional Information")

Your batch `work/expl/b<book>/in_NNN.md` holds whole topics: `=== ROW r | title`, its notes pages
(`## S<k> | title`), then `=== MCQS` — each MCQ as `Q <id> | page S<k>`, the stem, options, `Answer:` and
`Old:` (today's one-line explanation). For every MCQ write an explanation laid out like a coaching-app solution:

```
Q n1a2b3c4d5e6
- The most significant feature of the IVC was **buildings made of burnt bricks** — so option **(3)** is correct.
- **Barter** was how the Harappans traded, and **local transport** used bullock carts: neither is the IVC's hallmark.
- **John Marshall**, DG of the **ASI**, announced the discovery in **1924**.
+ The IVC is also called the **Harappan Civilization**; it flourished around **2500 BC**.
+ Port cities: **Lothal**, **Sutkagendor**, **Balakot**, **Allahdino**.
+ **Kalibangan** (Rajasthan) lay on the **Ghaggar**; **Lothal** at the head of the **Gulf of Cambay**.
```

## The two parts
`- ` **Solution** (2–5 bullets): the first bullet states the correct answer as a fact, naming it (its key words,
and `option **(n)**`). Then the facts that prove it, and — where the notes allow — why the other options are
wrong (what each wrong option really is: "**Dipavamsa** is a Sri Lankan chronicle"). For statement questions
("Which of the statements is/are correct"), one bullet per statement: correct or not, and the fact behind it.
For matching / chronology questions, the correct pairs or order with the years.

`+ ` **Additional Information** (2–6 bullets): facts from the **same topic's notes** that sit next to the asked
fact and that an APPSC paper could ask next — the other members of the list, the same person's other works,
the year before / after, the confusable pair (as a `⚠` trap). Prefer the page the MCQ is filed on (`page S<k>`),
then the rest of the topic. Do not repeat a solution bullet.

## Rules (the checker enforces most)
1. **Only facts from the topic's notes or the question itself.** No outside knowledge, no new numbers: every
   number you write must appear in the notes or the question. If the notes say nothing about a wrong option,
   say nothing about it — never guess. Keep source tags off (no `(CDI)`, `[GK]`), and no "Not in your sources".
2. **Bold** the words an exam hinges on: names, years, numbers, places, terms, the answer. Short bullets
   (one fact, under ~35 words), no paragraphs, no italics, no headings.
3. If the `Answer:` looks wrong against the notes, still explain the keyed answer from the notes, and add one
   `+ ⚠ ` bullet quoting what the notes say. Never change the key.
4. Every `Q <id>` of the input once, in the same order. Nothing else in the file.

## Check
`EXPL_DIR=work/expl python3 tools/expl_check.py <book> NNN` must end `<n>/<n> MCQs pass`. Fix what it reports
and re-run. Write only `out_NNN.md` (scratch files in your own scratchpad folder).
