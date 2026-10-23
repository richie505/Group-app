# Rerouting ROCKET blocks a topic sent back (round 2 of the merge)

Input `work/merge2/triage_<book>.md`: each block as `## B<id> | <ROCKET sheet / page>`, the topic that sent it
back, up to four `maybe <book>:<row> | <topic>` lines (likeliest homes), then the block. `work/merge2/topics.md`
lists every topic of books 1-5 as `<book>:<row> | title`.

**Only APPSC syllabus content goes in.** The app follows the APPSC Group 1 / Group 2 syllabus (Prep's topics).
For each block decide:
- `B<id> -> <book>:<row>` — a topic in topics.md whose syllabus subject the block is plainly about (any book,
  not only the "maybe" lines). A block of several items goes where most of it belongs.
- `B<id> -> drop` — no topic covers it: general physics / chemistry / biology (units, optics, acids, organs,
  vitamins, classification…), world superlatives and trivia lists, lists of PMs or persons with no syllabus
  topic, or anything the topic you would pick already states.

Write `work/merge2/triage_<book>.out`, one line per block, every B id of the input exactly once. Nothing else.
