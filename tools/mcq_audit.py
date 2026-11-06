"""Audit of APPSC Complete's and Group 2's MCQs: (1) do they follow the latest APPSC pattern, (2) how much of the notes
do they cover. Writes data/audit/mcq_audit.json and prints a summary.

    python3 tools/mcq_audit.py
"""
import collections
import json
import os
import re
import sys

sys.path.insert(0, "tools")
from reshape_plan import shape  # noqa: E402

J = lambda p: json.load(open(p))
APPS = {"Complete": "app/src/complete/assets", "Group 2": "app/src/group2/assets"}
SHAPES = ["one-liner", "statements", "NOT", "match", "assertion", "sequence"]
os.makedirs("data/audit", exist_ok=True)

# --- the latest APPSC pattern: APPSC papers of 2023-2025 in the PYQ bank (GS papers; mental ability left out)
MA = re.compile(r"\b(series|next number|code[ds]?\b.*\bletters?|ratio|percent|average|probability|speed|train|"
                r"clock|calendar|dice|mirror|odd one|analogy|blood relation|seating|syllogism|simple interest|"
                r"compound interest|profit|ages?\b)", re.I)
latest = []
for line in open("data/pyq/all.jsonl"):
    r = json.loads(line)
    tag = " ".join(str(r.get(k, "")) for k in ("exam", "paper", "file"))
    if "APPSC" in tag and re.search(r"202[3-5]", tag) and r.get("s") and len(r.get("o", [])) == 4 and not MA.search(r["s"]):
        latest.append(r)
lat = collections.Counter(shape(r) for r in latest)
lat_share = {s: lat[s] / len(latest) for s in SHAPES}


def stats(qs):
    c = collections.Counter(shape(q) for q in qs)
    n = len(qs) or 1
    st = [q for q in qs if shape(q) == "statements"]
    return {
        "n": len(qs),
        "shares": {s: round(c[s] / n, 3) for s in SHAPES},
        "stem words (median)": sorted(len(q["s"].split()) for q in qs)[len(qs) // 2] if qs else 0,
        "4+ statements": sum(1 for q in st if len(re.findall(r"^\s*\d\.\s", q["s"], re.M)) >= 4),
        "code boilerplate": sum(1 for q in qs if re.search(r"select the correct answer using the code", q["s"], re.I)),
        "no explanation": sum(1 for q in qs if len(q.get("x", "")) < 10),
    }


report = {"latest APPSC (2023-25 GS papers)": {"n": len(latest), "shares": {s: round(v, 3) for s, v in lat_share.items()},
                                              "stem words (median)": sorted(len(r["s"].split()) for r in latest)[len(latest) // 2]}}


def bold_terms(sec):
    out = set()
    for x in sec["b"]:
        runs = x.get("x", []) if x.get("k") != "t" else [r for row in [x.get("h", [])] + x.get("r", []) for c in row for r in c]
        for r in runs:
            t = r[0].strip(" .,:;()-–").lower()
            if r[1] == 1 and len(t) >= 4 and not re.fullmatch(r"[\d\s,.%₹–\-/]+", t):
                out.add(t)
    return out


for app, A in APPS.items():
    idx = J(f"{A}/index.json")["books"]
    per_book, cover = {}, {}
    worst = []
    for b in range(1, 7):
        m = J(f"{A}/mcq{b}.json")
        rows = m["rows"]
        qs = [q for v in rows.values() for q in v]
        per_book[idx[b - 1]["short"]] = stats(qs)
        bk = J(f"{A}/book{b}.json")
        flat = [r for u in bk["units"] for r in u["rows"]]
        topics0 = sum(1 for ri in range(len(flat)) if not rows.get(str(ri)))
        pages = pages0 = 0
        terms = hit = 0
        for ri, r in enumerate(flat):
            subs = m.get("subs", {}).get(str(ri), [])
            body = len(r["secs"]) - 3 if len(r["secs"]) > 3 else len(r["secs"])  # the last three: revision, PYQs, traps
            on = collections.Counter(subs)
            pages += body
            pages0 += sum(1 for si in range(body) if not on.get(si))
            text = " ".join(json.dumps(q, ensure_ascii=False) for q in rows.get(str(ri), [])).lower()
            tt = th = 0
            for s in r["secs"][:body]:
                for t in bold_terms(s):
                    tt += 1
                    th += t in text
            terms += tt
            hit += th
            if tt >= 20:
                worst.append((round(th / tt, 2), b, ri, r["title"][:70], len(rows.get(str(ri), []))))
        cover[idx[b - 1]["short"]] = {"topics": len(flat), "topics without MCQs": topics0, "pages": pages,
                                      "pages without MCQs": pages0, "bold facts": terms,
                                      "bold facts asked": round(hit / terms, 3) if terms else 0}
    allq = [q for b in range(1, 7) for v in J(f"{A}/mcq{b}.json")["rows"].values() for q in v]
    report[app] = {"all": stats(allq), "by subject": per_book, "coverage": cover,
                   "least covered topics": sorted(worst)[:25]}

json.dump(report, open("data/audit/mcq_audit.json", "w"), ensure_ascii=False, indent=1)
L = report["latest APPSC (2023-25 GS papers)"]
print(f"latest APPSC: {L['n']} Qs, median stem {L['stem words (median)']} words, shares {L['shares']}")
for app in APPS:
    a = report[app]["all"]
    print(f"\n{app}: {a['n']} MCQs, median stem {a['stem words (median)']} words, 4+ statements {a['4+ statements']}, "
          f"code boilerplate {a['code boilerplate']}, no explanation {a['no explanation']}")
    print("  shares", a["shares"])
    for k, v in report[app]["by subject"].items():
        print(f"  {k:28} {v['n']:6}  " + "  ".join(f"{s[:4]} {v['shares'][s]:.2f}" for s in SHAPES))
    for k, v in report[app]["coverage"].items():
        print(f"  {k:28} topics {v['topics']:4} (no MCQs {v['topics without MCQs']:3})  pages {v['pages']:5} "
              f"(no MCQs {v['pages without MCQs']:5})  bold facts asked {v['bold facts asked']:.0%}")
