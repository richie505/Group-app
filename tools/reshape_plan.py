"""Reshape the apps' own MCQs to the APPSC mix of question shapes (data/pyq/shape_targets: Group 1 / Group 2 papers).

    python3 tools/reshape_plan.py      -> data/reshape/plan.json and data/reshape/in/<n>.md (packets for the rewriters)

The apps lean on UPSC-style "consider the following statements" sets (35-47% of their MCQs); APPSC papers are
75-80% direct one-liners. Per topic (APPSC Complete's topics, then Prep's own MCQs by Prep topic) it works out how many
of each shape the topic should hold, keeps the best-fitting MCQs as they are, and marks the rest for rewriting into the
missing shapes - the longest statement sets and the code-style matches first. An MCQ shared by both apps is planned once.
"""
import json, os, re, sys
from collections import Counter

sys.path.insert(0, "tools")
from pyq_secrets import kind, neg  # noqa: E402

# Group 1 / Group 2 shares by subject (tools/pyq_secrets on the G1, G2 books and APPSC 2021-25 papers), rounded
TARGET = {
    1: {"one-liner": .78, "statements": .10, "match": .04, "NOT": .04, "sequence": .03, "assertion": .01},
    2: {"one-liner": .62, "statements": .20, "NOT": .12, "assertion": .03, "match": .02, "sequence": .01},
    3: {"one-liner": .75, "statements": .11, "NOT": .07, "assertion": .03, "match": .02, "sequence": .02},
    4: {"one-liner": .75, "statements": .09, "NOT": .09, "match": .03, "assertion": .02, "sequence": .02},
    5: {"one-liner": .72, "statements": .09, "NOT": .11, "assertion": .05, "match": .02, "sequence": .01},
    6: {"one-liner": .65, "statements": .20, "NOT": .06, "match": .06, "assertion": .02, "sequence": .01},
}
OUT = "data/reshape"


def shape(q):
    k = kind(q)
    if k in ("statements", "statement options", "how many"):
        return "statements"
    if k in ("match", "pairs"):
        return "match"
    if k in ("assertion", "sequence"):
        return k
    return "NOT" if neg(q) else "one-liner"


def heaviness(q):
    """How UPSC-like a question is: long stems and many statements first in line for rewriting."""
    return len(q["s"]) + 80 * len(re.findall(r"(?:^|\n|\s)\(?(?:[1-6]|i{1,3}|iv|v|vi)[.)]\s", q["s"]))


def plan_topic(qs, book):
    """qs: own MCQs of one topic. Returns {id: target shape} for those to rewrite."""
    n = len(qs)
    want = {s: round(n * f) for s, f in TARGET[book].items()}
    have = Counter(shape(q) for q in qs)
    by = {s: sorted([q for q in qs if shape(q) == s], key=heaviness, reverse=True) for s in have}
    # surplus: the heaviest of each over-full shape
    surplus = []
    for s, c in have.items():
        extra = c - want.get(s, 0)
        if extra > 0:
            surplus += [(q, s) for q in by[s][:extra]]
    surplus.sort(key=lambda x: heaviness(x[0]), reverse=True)
    # deficits filled in order of the exam's weight; one-liners take the rest
    need = []
    for s in ("NOT", "statements", "assertion", "match", "sequence"):
        need += [s] * max(0, want.get(s, 0) - have.get(s, 0))
    out = {}
    for i, (q, s) in enumerate(surplus):
        target = need[i] if i < len(need) else "one-liner"
        if target != s:
            out[q["id"]] = target
    return out


def text(q):
    opts = " / ".join(f"({i + 1}) {o}" for i, o in enumerate(q.get("o", [])))
    x = (q.get("x") or " ".join(q.get("xs", [])))[:300]
    return f"{q['s'].replace(chr(10), ' ')} || {opts} || ANS {q['a'] + 1}" + (f" || WHY: {x}" if x else "")


def main():
    os.makedirs(f"{OUT}/in", exist_ok=True)
    plan, rows = {}, []
    for app in ("complete", "main"):
        for b in range(1, 7):
            book = json.load(open(f"app/src/{app}/assets/book{b}.json"))
            titles = [r["title"] for u in book["units"] for r in u["rows"]]
            m = json.load(open(f"app/src/{app}/assets/mcq{b}.json"))
            for ri, qs in m["rows"].items():
                own = [q for q in qs if not q["id"].startswith("y") and len(q.get("o", [])) == 4 and q.get("a", -1) >= 0
                       and q["id"] not in plan]
                for i, t in plan_topic(own, b).items():
                    plan[i] = t
                    q = next(q for q in own if q["id"] == i)
                    rows.append((b, titles[int(ri)], q, t, shape(q)))
    json.dump(plan, open(f"{OUT}/plan.json", "w"), indent=0)
    print(len(plan), "MCQs to rewrite:", Counter(plan.values()), "from", Counter(r[4] for r in rows))
    # packets of about 250 MCQs, a topic never split
    packets, cur, size, last = [], [], 0, None
    for r in rows:
        key = (r[0], r[1])
        if size >= 250 and key != last:
            packets.append(cur)
            cur, size = [], 0
        cur.append(r)
        size += 1
        last = key
    if cur:
        packets.append(cur)
    for n, p in enumerate(packets):
        L, last = [], None
        for b, title, q, t, s in p:
            if (b, title) != last:
                L += ["", f"## SUBJECT {b} - TOPIC: {title}"]
                last = (b, title)
            L.append(f"- [{q['id']}] TARGET: {t} | NOW: {s} | {text(q)}")
        open(f"{OUT}/in/{n}.md", "w").write("\n".join(L) + "\n")
    print(len(packets), "packets")


if __name__ == "__main__":
    main()
