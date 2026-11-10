# PYQ answer-key check and notes links: where it stands (10 Nov 2026)

Scope: the 25,076 real exam PYQs of APPSC Complete (MCQs whose `src` is an exam, not `app`, `ca` or `rocket`).
Everything below runs on the Message Batches API with the key in the environment variable `KEY`.

## Done

| Step | Tool | PYQs | Result | Cost |
|---|---|---|---|---|
| Notes check (keys vs the six apps' notes) | `tools/pyq_notes_check.py` | 25,076 | AGREE 18,896 · CONFLICT 1,006 · NOT_COVERED 4,453 · NO_KEY 575 | $45.27 |
| Web check (official keys first, 8 per paper) | `tools/pyq_web_check.py` | 6,180 | KEEP 4,159 · KEY 917 · UNSURE 1,069 | $70.46 |
| Keys applied (`tools/keys_apply.py`) | | | 929 MCQs corrected in Complete + Prep; 425 copied into Group 2 in place | — |
| Owner rulings (`data/keys/out/9.md`) | | 3 | Guntupalli = Rajagirika; Siddharthaka chaitya = Gudivada | — |
| Notes fixed | | | Rajagirika = Guntupalli in Prep and Complete2 | — |
| Deep web pass on UNSURE + unanswered | `pyq_web_check.py --retry-from web --group 4` | 1,101 | KEEP 493 · KEY 224 · UNSURE 362 · 22 no answer; 224 applied (99 also in Group 2) | $85.10 |
| Notes links + missing explanations | `tools/pyq_notelink.py` | 23,975 | 20,180 linked (84%); 9,780 explanations written | $23.70 |
| Pilots and comparisons | | | | ~$8 |

Released as APPSC Complete 3.43 and APPSC Group 2 3.43 (`apks/`). API spend so far: about $231.

## Left to do (needs API credits)

1. Done in 3.43: all KEY decisions applied, 1,153 MCQs corrected in total (`data/keys/report.md`). Still open:
   362 PYQs UNSURE after the deep pass and 22 with no answer (`web_check/deep/summary.md`), for manual review.
2. Link the 1,101 deep-pass PYQs to their notes lines (~$2):
   `python3 tools/pyq_notelink.py build --run links2` (it skips PYQs already linked), then submit/status/collect/
   revalidate/apply.
3. 72 PYQs the links run skipped, and 3,723 PYQs whose fact is not in the notes (no link; their sheet still shows
   "Key points"). The facts can be added as notes lines with `tools/notelink.py` (~$10-15).
4. Group 2: its notelinks use its own row numbers; the new PYQ links must be mapped across (or Group 2 rebuilt,
   which resets its plan).
5. 27 questions that appear twice in Complete with different keys (exam PYQs), and garbled old explanations
   (OCR noise such as "off- 3323 season").

## Adding new APPSC PYQs later

Once the new PYQs are in `app/src/complete/assets/mcq*.json` (each with `src`, filed under its topic row):

```
python3 tools/pyq_notes_check.py extract                      # only if the UPSC/Rocket repos changed
python3 tools/pyq_notes_check.py build --run new              # builds requests for ALL exam PYQs; to save cost,
                                                              # filter requests.jsonl to the new ids first
python3 tools/pyq_notes_check.py submit|status|collect --run new
python3 tools/pyq_web_check.py build --run newweb --from new  # CONFLICT + NO_KEY + NOT_COVERED, grouped by paper
python3 tools/pyq_web_check.py submit|status|collect --run newweb
python3 tools/keys_apply.py
python3 tools/pyq_notelink.py build --run newlinks            # links only PYQs without one
python3 tools/pyq_notelink.py submit|status|collect|revalidate|apply --run newlinks
```

Measured rates: notes check ~$1.8 per 1,000 PYQs; web check ~$1.15 per 100 flagged PYQs; links ~$1 per 1,000.
