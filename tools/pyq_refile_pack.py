"""Packs every PYQ in APPSC Complete, grouped by the topic it is filed under, into data/pyq/refile/in/R<nn>.md for a
placement check (data/pyq/refile/INSTRUCTIONS.md). tools/pyq_refile.py applies the results."""
import json, re

A = "app/src/complete/assets"
T = {}
for l in open("data/pyq/arihant/topics.txt"):
    br, rest = l.split(" ", 1)
    title, subs = rest.split("  ::  ") if "  ::  " in rest else (rest, "")
    T[br] = (title.strip(), subs.strip())
items = []
for b in range(1, 7):
    m = json.load(open(f"{A}/mcq{b}.json"))
    for r, qs in m["rows"].items():
        for q, s in zip(qs, m["subs"].get(r) or [-1] * len(qs)):
            if q["id"].startswith("y"):
                items.append((b, int(r), s, q))
items.sort(key=lambda x: (x[0], x[1], x[2]))
N, packs, cur = 200, [], []
for it in items:
    cur.append(it)
    if len(cur) >= N:
        packs.append(cur); cur = []
if cur:
    packs.append(cur)
for i, p in enumerate(packs):
    out, last = [f"# Packet R{i:03d}: {len(p)} PYQs\n"], None
    for b, r, s, q in p:
        if (b, r) != last:
            t, subs = T.get(f"{b}:{r}", ("?", ""))
            out.append(f"\n## TOPIC {b}:{r} {t}\nSubsections: {subs}\n")
            last = (b, r)
        stem = re.sub(r"\s+", " ", q["s"])[:260]
        ans = q["o"][q["a"]] if q.get("a", -1) >= 0 else "?"
        out.append(f"- {q['id']} [sub {s}] ({q.get('src','')[:30]}) {stem} → {ans[:60]}")
    open(f"data/pyq/refile/in/R{i:03d}.md", "w").write("\n".join(out) + "\n")
print(len(items), "PYQs in", len(packs), "packets")
