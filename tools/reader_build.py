"""APPSC Reader: APPSC Complete's full notes only, for reading (no MCQs, no one-page summaries). Writes
app/src/reader/assets:
- book*.json: each topic's full-notes pages, in the order and groups the writers chose
  (data/structure/out, tools/structure_check.py), each page with its group heading ("g")
- index.json (page counts, no MCQ counts), keyterms.json (on the new page ids), empty MCQ files
- moved.json: APPSC Reader 3.19's page ids (APPSC Complete's) -> the new ones, so read marks, bookmarks and
  markers stay on their pages
The simple meanings (simple.json) are built by tools/words_check.py, the plan by tools/reader_plan.py.

    python3 tools/reader_build.py
"""
import json
import os
import sys

sys.path.insert(0, "tools")
from structure_check import problems, read_in, read_out  # noqa: E402

A = "app/src/complete/assets"
R = "app/src/reader/assets"
os.makedirs(R, exist_ok=True)

order = {}
n = 0
while os.path.exists(f"data/structure/in/{n}.md"):
    src, out = read_in(n), read_out(n)
    for t, pages in src.items():
        g = out.get(t)
        if g and not problems(pages, g):
            order[t] = g
    n += 1


def text(rs):
    return "".join(r[0] for r in rs)


def has_text(sec):
    return any(("x" in x and x.get("k") != "n" and text(x["x"]).strip()) or x.get("k") == "t" for x in sec["b"])


moved, gone, counts = {}, [], {}
keyterms = json.load(open(f"{A}/keyterms.json"))
new_terms = {}
grouped = 0
for b in range(1, 7):
    bk = json.load(open(f"{A}/book{b}.json"))
    ri = 0
    for u in bk["units"]:
        for row in u["rows"]:
            full = [(i, s) for i, s in enumerate(row["secs"]) if s.get("f")]
            plan = order.get(f"{b}:{ri}")
            if plan:
                grouped += 1
                seq = [(head, full[k - 1]) for head, ks in plan for k in ks]
            else:
                seq = [("", x) for x in full]
            secs = []
            kept = set()
            for head, (old, s) in seq:
                if not has_text(s):
                    continue
                s = {k: v for k, v in s.items() if k not in ("f", "o")}
                s["badges"] = [x for x in s.get("badges", []) if x != "Full notes"]
                if head:
                    s["g"] = head
                new = f"{b}:{ri}:{len(secs)}"
                moved[f"{b}:{ri}:{old}"] = new
                kept.add(old)
                if f"{b}:{ri}:{old}" in keyterms:
                    new_terms[new] = keyterms[f"{b}:{ri}:{old}"]
                secs.append(s)
            gone += [f"{b}:{ri}:{i}" for i in range(len(row["secs"])) if i not in kept]
            row["secs"] = secs
            counts[(b, ri)] = len(secs)
            ri += 1
    json.dump(bk, open(f"{R}/book{b}.json", "w"), ensure_ascii=False, separators=(",", ":"))

idx = json.load(open(f"{A}/index.json"))
for bi in idx["books"]:
    bi["uq"] = [0] * len(bi["uq"]) if isinstance(bi.get("uq"), list) else 0
    for ri, r in enumerate(bi["rows"]):
        r["q"] = 0
        r["n"] = counts[(bi["id"], ri)]
json.dump(idx, open(f"{R}/index.json", "w"), ensure_ascii=False, separators=(",", ":"))
json.dump({"edition": "reader", "name": "APPSC Reader"}, open(f"{R}/edition.json", "w"))
for b in range(1, 7):
    json.dump({"rows": {}, "units": {}, "subs": {}}, open(f"{R}/mcq{b}.json", "w"))
json.dump(new_terms, open(f"{R}/keyterms.json", "w"), ensure_ascii=False, separators=(",", ":"))
json.dump({"mcq": [], "full": []}, open(f"{R}/empty.json", "w"))
# 3.19 used APPSC Complete's ids: the pages that stay move, the one-page summaries are gone
json.dump({"v": "reader-2", "m": {k: v for k, v in moved.items() if k != v}, "g": sorted(set(gone))},
          open(f"{R}/moved.json", "w"), separators=(",", ":"))
json.dump([], open(f"{R}/notemoves.json", "w"))
topics = sum(len(b["rows"]) for b in idx["books"])
print(f"APPSC Reader: {topics} topics ({grouped} grouped), {sum(counts.values())} full-notes pages; "
      f"{len(gone)} one-page summary or blank pages left out")
