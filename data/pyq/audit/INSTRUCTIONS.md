# Audit of APPSC Complete against the previous-year questions

You audit an APPSC (Andhra Pradesh Public Service Commission, Group 1/2 prelims) exam-prep app against real
previous-year questions (PYQs). Only read the packet files and write JSON result files; edit nothing else, no git.

Each packet `data/pyq/audit/in/<b>-<r>.md` has one topic: its NOTES (subsections "sub k"; each bullet tagged
[k#i] = subsection k, block i), the PYQS filed under it (official answers; "APPSC" ones are from the actual exam,
the others are UPSC / other state PSCs - their keys are authoritative facts too), and the APP MCQS. ANS n is 1-based.

For each topic:
1. WRONG FACTS. Using the PYQs as the source of truth (plus well-established knowledge where no PYQ covers it),
   find app MCQs whose marked answer is wrong, or whose stem/options state a false fact, or that contradict a PYQ;
   and NOTES bullets that state something a PYQ (or an established fact) contradicts. Flag only what you are
   confident is wrong, not wording preferences. If a PYQ key itself looks wrong (OCR / key slip), do not "fix" the
   app to match it - list it under pyq_bad with "suspect key: ...".
2. ODD / OFF-DEPTH MCQs -> drop. The exam is APPSC (not UPSC): mostly direct single-fact questions, some short
   statement / match / assertion questions, a strong Andhra Pradesh tilt. Drop app MCQs that are factually dubious,
   ambiguous or oddly worded (no exam words it that way), obscure trivia far beyond the depth the PYQs show for this
   topic, opinion items ("most appropriate criticism"), or near-duplicates of another app MCQ here (keep the better
   one). Do NOT drop sound MCQs just because no PYQ covers them. Expect to drop roughly 0-10% per topic.
3. BAD PYQs. PYQ ids start with "y". Flag ones that are garbled / unreadable, whose options belong to another
   question, that are mental-ability (reasoning, arithmetic, data interpretation) items, or that are filed under the
   wrong topic ("wrong topic: <better topic in a few words>").
4. PATTERNS. 3-6 short bullets: how APPSC actually asks this topic (shapes, recurring facts, traps, keywords),
   and how the app's MCQs differ.

Current-affairs figures dated 2025-26 that you cannot verify: leave them alone.

Write `data/pyq/audit/out/<b>-<r>.json` (same name as the packet) with exactly:
{
 "topic": "<b>:<r>",
 "mcq_fix": [{"id": "...", "a": <new 0-based answer index, optional>, "s": "<corrected stem, optional>", "o": ["<all 4 corrected options, optional>"], "why": "short, cite PYQ id if any"}],
 "mcq_drop": [{"id": "...", "why": "short"}],
 "notes_fix": [{"ref": "k#i", "find": "<exact substring of that bullet>", "replace": "<corrected text>", "why": "short, cite PYQ id"}],
 "pyq_bad": [{"id": "y...", "why": "garbled | wrong options | mental ability | suspect key: ... | wrong topic: ..."}],
 "patterns": ["..."],
 "stats": {"app_mcqs": n, "pyqs": n, "fixed": n, "dropped": n}
}
Keep "why" short. Validate each file: python3 -c "import json;json.load(open('<file>'))".
If an output file already exists, skip that topic. Work through your list one packet at a time.
At the end reply with only: topics done, totals of fixed / dropped / notes fixes / bad PYQs, and any topic you could not finish.
