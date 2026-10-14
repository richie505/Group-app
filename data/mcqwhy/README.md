# Explanation pass (2.50) — resume steps

1. `python3 tools/mcq_why.py export` (recreates work/mcqwhy/in_NNN.md, 166 batches; only valid while the
   MCQ assets are unchanged since the export — do not export again after `apply`).
2. `cp data/mcqwhy/out_*.jsonl work/mcqwhy/`
3. Run the batches without an out_ file (tools/mcq_why_guide.md), 20 agents at a time.
4. `python3 tools/mcq_why.py check` until all pass, then `python3 tools/mcq_why.py apply` once.
