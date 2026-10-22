# MCQs of APPSC Complete: one strong set per page, ROCKET first

Follow tools/mcq_trim_guide.md (decisions keep / drop off, dup, trivia / merge; output out_NNN.jsonl; check with
`TRIM_ASSETS=app/src/complete/assets TRIM_DIR=work/mergemcq python3 tools/mcq_trim_check.py <book> <NNN>`), with
these changes for the merged notes:

1. **ROCKET MCQs are the core.** Questions marked `(ROCKET)` come from the ROCKET sheets. When a ROCKET MCQ and
   a Prep MCQ test the same fact, keep the ROCKET one and drop the Prep one as `dup` — unless the Prep one is
   clearly the stronger exam question (a statement / match / assertion question testing several facts the
   ROCKET one does not), then keep the Prep one and drop the ROCKET one.
2. **Same fact, different words is a repeat.** "Which writ runs against private persons?" and "Habeas corpus
   lies against …" test one fact: keep one. Reverse questions, reshuffled statement sets and the same fact in a
   different question type are repeats too.
3. **Aim for about 4–6 MCQs per page** (a page with many facts may keep up to 8; a short page 2–3), so a topic
   ends with roughly **55–65%** of its MCQs. Never drop the only MCQ testing a fact of the page.
4. Prefer, among repeats: statement / match / assertion questions over one-liners; answers that are not "all of
   the above"; ROCKET wording.

## Current affairs (book 6)
Questions marked `(CA app)` come from the CA app, the core of current affairs: they take ROCKET's place in
rule 1 (keep the CA app's question when it and a Prep question test the same fact). The notes of a section are
one period's news pages; an MCQ whose fact is on another period's page of the same topic is `off` here only if
it is on no page of this section. Aim for about **4–5 MCQs per news page**; trivia rule 3 applies firmly
(single-event crore amounts, minor dates, decimal statistics).
