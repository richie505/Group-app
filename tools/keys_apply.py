"""Doubtful answer keys, checked against reliable sources (data/keys/out/<n>.md, rules in data/keys/INSTRUCTIONS.md):
"KEY n" sets the right option and its fact as the explanation, "EXPLAIN" replaces a wrong explanation; KEEP and
UNSURE change nothing. Applied wherever the MCQ is (APPSC Complete, APPSC Prep); APPSC Group 2 is rebuilt from
Complete after. Writes data/keys/report.md (every change with its source).

    python3 tools/keys_apply.py
"""
import glob
import json
import re

APPS = ["app/src/complete/assets", "app/src/main/assets"]


def read():
    out = {}
    for f in sorted(glob.glob("data/keys/out/*.md"), key=lambda p: int(re.findall(r"\d+", p)[-1])):
        for line in open(f):
            p = [x.strip() for x in line.rstrip("\n").split(" | ")]
            if len(p) >= 2:
                out[p[0]] = p[1:]
    return out


def main():
    dec = read()
    changed, report = {}, []
    for a in APPS:
        for b in range(1, 7):
            path = f"{a}/mcq{b}.json"
            try:
                m = json.load(open(path))
            except FileNotFoundError:
                continue
            hit = False
            for k, v in m.items():
                if not isinstance(v, dict):
                    continue
                for qs in v.values():
                    if not isinstance(qs, list):
                        continue
                    for q in qs:
                        d = dec.get(q.get("id"))
                        if not d:
                            continue
                        kind = d[0]
                        km = re.match(r"KEY (\d+)$", kind)
                        if km and len(d) >= 3:
                            n = int(km.group(1)) - 1
                            if 0 <= n < len(q["o"]) and q.get("a") != n:
                                old = q["o"][q["a"]] if 0 <= q.get("a", -1) < len(q["o"]) else "none"
                                q["a"] = n
                                q["x"] = d[2] if len(d) == 3 else d[-1]
                                q.pop("solution", None)
                                hit = True
                                changed[q["id"]] = (old, q["o"][n], d[1])
                        elif kind == "EXPLAIN" and len(d) >= 3:
                            if q.get("x") != d[-1]:
                                q["x"] = d[-1]
                                hit = True
                                changed.setdefault(q["id"], ("", "explanation corrected", d[1]))
            if hit:
                open(path, "w").write(json.dumps(m, ensure_ascii=False, separators=(",", ":")))
    counts = {}
    for d in dec.values():
        kind = "KEY" if d[0].startswith("KEY") else d[0]
        counts[kind] = counts.get(kind, 0) + 1
    report = ["# Answer keys checked against sources", "", f"Checked {len(dec)}: " +
              ", ".join(f"{k} {v}" for k, v in sorted(counts.items())), "", "| MCQ | Was | Now | Source |", "|---|---|---|---|"]
    report += [f"| {i} | {o} | {n} | {s} |" for i, (o, n, s) in sorted(changed.items())]
    open("data/keys/report.md", "w").write("\n".join(report) + "\n")
    print(report[2], "| changed", len(changed))


if __name__ == "__main__":
    main()
