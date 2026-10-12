# Cross-topic repeats

Each PAIR shows two MCQs from different topics that look alike. Decide per pair:
- Same fact tested (same answer fact, reworded or reversed) → drop one: keep the clearer, exam-style
  one, or the one whose topic is the natural home of the fact. `{"p":0,"drop":"<id of the one to drop>"}`
- Different facts, or a genuinely different angle (e.g. one asks the Article, the other the body it
  created) → keep both: `{"p":1,"drop":null}`

Write xdup_out_NNN.jsonl, one line per pair in order, every pair exactly once, ids copied exactly from the
[brackets]. Write only that file.
