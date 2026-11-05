"""APPSC Complete's MCQ notes in simple English: the packets for the writers (data/simple/in/<n>.md; rules in
data/simple/INSTRUCTIONS.md). Bullets and sub-bullets only; headings, tables and placeholders stay as they are.
tools/simple_build.py puts the lines back, checked (same bold terms and numbers, never more words).

    python3 tools/simple_plan.py
"""
import json

SRC = "app/src/complete2/assets"  # the MCQ notes as written (kept unchanged: the originals)
PER = 300  # lines a packet, whole pages only


def md(runs):
    return "".join(f"**{t}**" if s == 1 else t for t, s, *_ in runs)


def main():
    packets, cur, n = [], [], 0
    for b in range(1, 7):
        bk = json.load(open(f"{SRC}/book{b}.json"))
        ri = 0
        for u in bk["units"]:
            for r in u["rows"]:
                for si, s in enumerate(r["secs"]):
                    lines = [(bi, x) for bi, x in enumerate(s["b"]) if x.get("k") in ("b", "s") and "x" in x]
                    if not lines:
                        continue
                    cur.append(f"## P {b}:{ri}:{si} | {r['title'][:80]} | {s['t']}")
                    cur += [f"L{b}:{ri}:{si}:{bi} {md(x['x'])}" for bi, x in lines]
                    n += len(lines)
                    if n >= PER:
                        packets.append(cur)
                        cur, n = [], 0
                ri += 1
    if cur:
        packets.append(cur)
    for i, p in enumerate(packets):
        open(f"data/simple/in/{i}.md", "w").write("\n".join(p) + "\n")
    print(len(packets), "packets,", sum(sum(l.startswith("L") for l in p) for p in packets), "lines")


if __name__ == "__main__":
    main()
