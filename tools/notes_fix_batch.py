"""Apply data/notesfix_pyq/ops-<packet>.json files with tools/notes_fix.py, leaving out any edit whose anchor text an
earlier packet already changed (logged to data/notesfix_pyq/dropped.jsonl for review).

    NOTES_APP=complete python3 tools/notes_fix_batch.py n01 n02 ...
"""
import json, re, subprocess, sys

for pk in sys.argv[1:]:
    p = f"data/notesfix_pyq/ops-{pk}.json"
    ops = json.load(open(p))
    while True:
        r = subprocess.run([sys.executable, "tools/notes_fix.py", "apply", p, "--dry"], capture_output=True, text=True)
        bad = sorted({int(m) for m in re.findall(r"^op (\d+):", r.stdout + r.stderr, re.M)}, reverse=True)
        if not bad:
            break
        with open("data/notesfix_pyq/dropped.jsonl", "a") as f:
            for i in bad:
                f.write(json.dumps({"packet": pk, "op": ops[i]}, ensure_ascii=False) + "\n")
                del ops[i]
        json.dump(ops, open(p, "w"), ensure_ascii=False, indent=1)
    r = subprocess.run([sys.executable, "tools/notes_fix.py", "apply", p], capture_output=True, text=True)
    print(pk, (r.stdout + r.stderr).strip().splitlines()[-1])
