# MCQ coverage run (in progress)

Answers from tools/mcq_cut_guide.md, one file per batch. They refer to the MCQ assets as of commit
3839602 (not yet changed). To resume in a fresh container:

1. `for b in 1 2 3 4 5 6; do python3 tools/mcq_cut_export.py $b; done` (recreates work/mcqcut/b*/in_NNN.md)
2. `cp data/mcqcut/b*/out_*.jsonl` back into `work/mcqcut/b*/`
3. Run the batches without an out_ file (queue.txt lists all 159; next.txt = how many were started).
4. When all pass `tools/mcq_cut_check.py`, run `tools/mcq_cut_import.py <book>` for each book.

flags.txt lists MCQs and notes the agents found doubtful or wrong, for review.

Book 1 (History) has been imported (commit 8418dab); do not re-run its import or export from the new asset.
Book 2 (Polity) imported too.
