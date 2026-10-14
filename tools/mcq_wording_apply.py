"""Apply reworded explanations: python3 tools/mcq_wording_apply.py work/mcqwhy/wording_out_*.jsonl
Each line {"id":..., "x":...}; only the explanation changes."""
import json, sys
fix = {}
for p in sys.argv[1:]:
    for l in open(p):
        if l.strip():
            o = json.loads(l); fix[o["id"]] = o["x"].strip()
n = 0
for b in range(1, 7):
    path = f"app/src/main/assets/mcq{b}.json"; m = json.load(open(path))
    for qs in m["rows"].values():
        for q in qs:
            if q["id"] in fix and fix[q["id"]]:
                q["x"] = fix[q["id"]]; n += 1
    open(path, "w").write(json.dumps(m, ensure_ascii=False, separators=(",", ":")))
print(f"{n} explanations reworded")
