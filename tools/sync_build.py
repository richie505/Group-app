"""APPSC Complete: the MCQ notes and the MCQs in step (data/sync/plan.json from tools/sync_plan.py).

1. Each MCQ filed under a page that does not hold its fact moves to the page of its topic that does (mcq*.json subs).
2. The MCQ notes are rebuilt (tools/simple_build.py: simple English), then each fact the writers added
   (data/sync/out/<n>.md: "F<k> | <heading> | <line>") goes on its page, under its heading (a new heading at the
   end of the page when the writer named one; at the end of the page when it has none). SKIP lines add nothing.

    python3 tools/sync_build.py
"""
import glob
import json
import re
import subprocess
import sys

A = "app/src/complete/assets"
N = "app/src/complete/mcqnotes"
sys.path.insert(0, "tools")
from simple_build import runs  # noqa: E402


def move():
    plan = json.load(open("data/sync/plan.json"))
    moves = plan["moves"]
    done = 0
    for b in range(1, 7):
        p = f"{A}/mcq{b}.json"
        m = json.load(open(p))
        # only to a page both notes have (the MCQ notes add "More from this topic's MCQs" to some topics)
        full = [len(r["secs"]) for u in json.load(open(f"{A}/book{b}.json"))["units"] for r in u["rows"]]
        for ri, qs in m["rows"].items():
            subs = m["subs"].setdefault(ri, [-1] * len(qs))
            for k, q in enumerate(qs):
                mv = moves.get(q["id"])
                if mv and mv[0] == b and mv[1] == int(ri) and subs[k] != mv[2] and mv[2] < full[int(ri)]:
                    subs[k] = mv[2]
                    done += 1
        open(p, "w").write(json.dumps(m, ensure_ascii=False, separators=(",", ":")))
    return done


def text(rs):
    return "".join(r[0] for r in rs)


def insert():
    plan = json.load(open("data/sync/plan.json"))
    adds = {}
    for f in sorted(glob.glob("data/sync/out/*.md")):
        for line in open(f):
            m = re.match(r"^F(\d+) \| (.+?)(?: \| (.+))?$", line.rstrip("\n"))
            if not m or m.group(2).strip() == "SKIP" or not m.group(3):
                continue
            k = int(m.group(1))
            x = plan["missing"][k]
            adds.setdefault((x["b"], x["r"], x["page"]), []).append((m.group(2).strip(), m.group(3).strip()))
    n = 0
    for b in range(1, 7):
        p = f"{N}/book{b}.json"
        bk = json.load(open(p))
        rows = [r for u in bk["units"] for r in u["rows"]]
        for (bb, ri, pg), items in adds.items():
            if bb != b:
                continue
            blocks = rows[ri]["secs"][pg]["b"]
            for head, line in items:
                blk = {"k": "b", "x": runs(line)}
                hi = next((i for i, x in enumerate(blocks) if x.get("k") == "h" and text(x["x"]).strip() == head), None)
                if hi is not None:
                    j = hi + 1
                    while j < len(blocks) and blocks[j].get("k") != "h":
                        j += 1
                    blocks.insert(j, blk)
                elif head.startswith("NEW:"):
                    title = head[4:].strip()
                    hj = next((i for i, x in enumerate(blocks) if x.get("k") == "h" and text(x["x"]).strip() == title), None)
                    if hj is None:
                        blocks.append({"k": "h", "x": [[title, 0]]})
                        blocks.append(blk)
                    else:
                        j = hj + 1
                        while j < len(blocks) and blocks[j].get("k") != "h":
                            j += 1
                        blocks.insert(j, blk)
                else:
                    blocks.append(blk)
                n += 1
            # a page that was a "no MCQs" placeholder is a real page now
            rows[ri]["secs"][pg]["b"] = [x for x in blocks if not (x.get("k") == "n" and text(x["x"]).startswith("No MCQ"))]
        open(p, "w").write(json.dumps(bk, ensure_ascii=False, separators=(",", ":")))
    return n


TAG = re.compile(r"\[[^\]·]*·\s*([^\]]+)\]\s*$")


def fill():
    """A page of the MCQ notes still saying "No MCQs on this subsection yet" while MCQs are filed under it or name it
    in their note ("[October 2026 · <page title>]", most current-affairs MCQs): its lines from the full notes (kept
    to what the MCQs test, tools/trim_notes.py) in place of the placeholder."""
    n = 0
    for b in range(1, 7):
        m = json.load(open(f"{A}/mcq{b}.json"))
        p = f"{N}/book{b}.json"
        bk = json.load(open(p))
        rows = [r for u in bk["units"] for r in u["rows"]]
        full = [r for u in json.load(open(f"{A}/book{b}.json"))["units"] for r in u["rows"]]
        titles = {}
        for ri, r in enumerate(rows):
            for si, sec in enumerate(r["secs"]):
                titles.setdefault(sec["t"].strip(), []).append((ri, si))
        want = set()
        for ri, qs in m["rows"].items():
            subs = m["subs"].get(ri, [])
            for k, q in enumerate(qs):
                if k < len(subs) and subs[k] >= 0:
                    want.add((int(ri), subs[k]))
                for note in q.get("n") or []:
                    t = TAG.search(note)
                    if t:
                        want |= set(titles.get(t.group(1).strip(), []))
        for ri, si in want:
            sec = rows[ri]["secs"][si]
            placeholder = len(sec["b"]) == 1 and sec["b"][0].get("k") == "n" and text(sec["b"][0]["x"]).startswith("No MCQ")
            if placeholder and si < len(full[ri]["secs"]):
                blocks = [x for x in full[ri]["secs"][si]["b"] if x.get("k") != "n"]
                if blocks:
                    sec["b"] = blocks
                    n += 1
        open(p, "w").write(json.dumps(bk, ensure_ascii=False, separators=(",", ":")))
    return n


if __name__ == "__main__":
    print("MCQs moved to the page with their fact:", move())
    subprocess.run([sys.executable, "tools/simple_build.py"], check=True)
    print("facts added to the MCQ notes:", insert())
    print("empty pages filled from the full notes:", fill())
