"""APPSC Complete 2.0: notes written from the app's own MCQs. Writes data/c2/in/<n>.md, packets of about 350 MCQs
(a section never split): for each subsection with MCQs, its MCQs' questions, right answers and explanations.

    python3 tools/c2_plan.py
"""
import json, os, re

A = "app/src/complete/assets"
OUT = "data/c2/in"


def clip(t, n):
    t = re.sub(r"\s+", " ", t or "").strip()
    return t if len(t) <= n else t[:n].rsplit(" ", 1)[0] + "…"


def main():
    os.makedirs(OUT, exist_ok=True)
    packets, cur, size = [], [], 0
    for b in range(1, 7):
        bk = json.load(open(f"{A}/book{b}.json"))
        m = json.load(open(f"{A}/mcq{b}.json"))
        rows = [r for u in bk["units"] for r in u["rows"]]
        for ri, r in enumerate(rows):
            qs = m["rows"].get(str(ri), [])
            subs = m["subs"].get(str(ri)) or [-1] * len(qs)
            by = {}
            for q, s in zip(qs, subs):
                by.setdefault(s, []).append(q)
            if not by:
                continue
            L = [f"# ROW {b}:{ri} | {r['title']}"]
            n = 0
            for si in sorted(by, key=lambda s: (s < 0, s)):
                title = r["secs"][si]["t"] if si >= 0 else "(whole topic)"
                L.append(f"## SEC {b}:{ri}:{si} | {title}")
                for q in by[si]:
                    ans = q["o"][q["a"]] if 0 <= q.get("a", -1) < len(q["o"]) else "(no official key)"
                    pyq = f" | PYQ: {q.get('src', '')}" if q["id"].startswith("y") else ""
                    L.append(f"- Q: {clip(q['s'], 260)} => ANSWER: {clip(ans, 160)} | WHY: {clip(q.get('x', ''), 280)}{pyq}")
                    n += 1
            cur.append("\n".join(L))
            size += n
            if size >= 350:
                packets.append(cur)
                cur, size = [], 0
    if cur:
        packets.append(cur)
    for i, p in enumerate(packets):
        open(f"{OUT}/{i}.md", "w").write("\n\n".join(p) + "\n")
    print(len(packets), "packets")


if __name__ == "__main__":
    main()
