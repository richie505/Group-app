"""APPSC Complete: the app's own one-fact MCQs not answered yet, three to a question ("Consider the following
statements: 1. 2. 3."). This writes the packets for the writers (data/m3/in/<n>.md, rules in data/m3/INSTRUCTIONS.md);
tools/m3_build.py puts the answers back. PYQs and statement MCQs stay as they are.

    python3 tools/m3_plan.py            (every one-fact MCQ, answered or not: the user's choice)
    python3 tools/m3_plan.py <backup.json>   (only those not answered in that backup)
Each fact is told whether its statement must be TRUE or FALSE (and, if false, the wrong option to use), so the key
is decided here, not by the writer.
"""
import hashlib, json, random, re, sys, os

A = "app/src/complete/assets"
MULTI = re.compile(r"statement|consider|following pairs|match|assertion|reason|list[- ]?i|chronolog|arrange|correctly matched", re.I)
PER = 100  # questions (triples) a packet
rnd = random.Random(2026)


def main(backup=None):
    done = {a.rsplit(":", 1)[0] for a in json.load(open(backup))["answers"]} if backup else set()
    groups, plan = [], {}
    for b in range(1, 7):
        m = json.load(open(f"{A}/mcq{b}.json"))
        titles = {}
        ri = 0
        for u in json.load(open(f"{A}/book{b}.json"))["units"]:
            for r in u["rows"]:
                titles[ri] = (r["title"], [s["t"] for s in r["secs"]])
                ri += 1
        for k, v in m["rows"].items():
            subs = m["subs"].get(k, [-1] * len(v))
            ok = [(q, subs[i]) for i, q in enumerate(v)
                  if not q["id"].startswith("y") and q["id"] not in done and 0 <= q["a"] < len(q["o"]) and len(q["o"]) >= 2
                  and not MULTI.search(q["s"]) and len(q["s"]) < 260]
            # by subsection first, then what is left over in the topic
            bysub, left = {}, []
            for q, s in ok:
                bysub.setdefault(s, []).append(q)
            trip = []
            for s, qs in bysub.items():
                for i in range(0, len(qs) - len(qs) % 3, 3):
                    trip.append((s, qs[i:i + 3]))
                left += qs[len(qs) - len(qs) % 3:]
            for i in range(0, len(left) - len(left) % 3, 3):
                trip.append((-1, left[i:i + 3]))
            for s, qs in trip:
                mid = "m" + hashlib.sha1("|".join(q["id"] for q in qs).encode()).hexdigest()[:12]
                # the key: all true 25%, two true 45%, one true 30%
                r = rnd.random()
                truth = [True] * 3 if r < .25 else (lambda f: [i != f for i in range(3)])(rnd.randrange(3)) if r < .70 else \
                    (lambda t: [i == t for i in range(3)])(rnd.randrange(3))
                wrong = [rnd.choice([o for j, o in enumerate(q["o"]) if j != q["a"]]) if not t else None for q, t in zip(qs, truth)]
                title = titles[int(k)][1][s] if 0 <= s < len(titles[int(k)][1]) else titles[int(k)][0]
                plan[mid] = {"b": b, "r": int(k), "s": s, "ids": [q["id"] for q in qs], "truth": truth}
                groups.append((b, int(k), title, mid, qs, truth, wrong))
    os.makedirs("data/m3/in", exist_ok=True)
    json.dump(plan, open("data/m3/plan.json", "w"), separators=(",", ":"))
    n = 0
    for p in range(0, len(groups), PER):
        out = []
        for b, r, title, mid, qs, truth, wrong in groups[p:p + PER]:
            out.append(f"## M {mid} | {title}")
            for i, (q, t, w) in enumerate(zip(qs, truth, wrong), 1):
                why = re.sub(r"\s+", " ", q.get("x", "")).strip()
                tell = "TRUE" if t else f"FALSE, use the wrong answer: {w}"
                out.append(f"{i}. [{tell}] Q: {re.sub(chr(10), ' ', q['s'])} => ANSWER: {q['o'][q['a']]} | WHY: {why}")
            out.append("")
        open(f"data/m3/in/{n}.md", "w").write("\n".join(out))
        n += 1
    facts = sum(len(g[4]) for g in groups)
    print(f"{len(groups)} questions from {facts} one-fact MCQs, {n} packets")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
