"""APPSC Group 2's PYQs as two-column A4 PDFs, Prelims and Mains apart: one PDF per Screening subject and per Mains
paper section (exams.json "Group 2"), its syllabus items in order, each item's sections (topics) with their PYQs,
then that topic's answers and explanations. A topic on two items of the same stage shows on the first only; a topic
in both Prelims and Mains shows in both.

    python3 tools/pyqpdf/make_pyq_g2.py out_dir   -> out_dir/<stage>-<n>.html  (then node tools/pyqpdf/pdf.js)
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from make_pyq import CSS, TAGS, answer, E

A = "app/src/group2/assets"
CSS2 = CSS + """
h1.i { column-span: all; font-size: 10.5pt; color: #fff; background: #1e293b; padding: 4px 7px; border-radius: 4px; margin: 4mm 0 2mm; }
"""


def pdf(subj, label, rows_of, idx, mcq, used):
    items = []
    for g in subj["groups"]:
        secs = []
        for b, r in g["rows"]:
            if (b, r) in used:
                continue
            qs = [q for q in mcq[b]["rows"].get(str(r), []) if q["id"].startswith("y")]
            used.add((b, r))
            if qs:
                secs.append((b, r, qs))
        if secs:
            items.append((g, secs))
    n_all = sum(len(qs) for _, s in items for *_, qs in s)
    out = [f"<html><head><meta charset='utf-8'><title>APPSC Group 2 PYQs - {E(subj['title'])}</title><style>{CSS2}</style></head><body>",
           f"<div class='cover'><h1>APPSC Group 2 · Previous Year Questions</h1><h2>{E(label)}</h2><h2>{E(subj['title'])}</h2>"
           f"<p>{n_all} PYQs in {sum(len(s) for _, s in items)} topics, by syllabus item as in the APPSC Group 2 app · "
           f"each topic's answers and explanations follow its questions</p></div><div class='cols'>"]
    for g, secs in items:
        out.append(f"<h1 class='i'>{E(g['title'])}</h1>")
        for b, r, qs in secs:
            row = idx["books"][b - 1]["rows"][r]
            meta = " · ".join(x for x in [", ".join(row.get("codes") or []), f"{len(qs)} PYQs"] if x)
            out.append(f"<h2 class='r'>{E(row['title'])}</h2><div class='meta'>{E(meta)}</div>")
            for i, q in enumerate(qs, 1):
                opts = "" if q.get("k") == "f" else "".join(f"<div class='o'>({j + 1}) {E(o)}</div>" for j, o in enumerate(q["o"]))
                out.append(f"<div class='q'><b>{i}.</b> <span class='s'>{E(q['s'])}</span> <span class='src'>[{E(q.get('src', ''))}]</span>{opts}</div>")
            out.append("<h3 class='k'>Answers &amp; explanations</h3>")
            for i, q in enumerate(qs, 1):
                tg = " ".join(f"<span class='t'>[{TAGS[t]}]</span>" for t in q.get("tg", []) if t in TAGS)
                out.append(f"<div class='a'><b>{i}. {E(answer(q))}</b> {tg} <span class='x'>{E((q.get('x') or '').replace(chr(10), ' '))}</span></div>")
    out.append("</div></body></html>")
    return "".join(out), n_all, {(b, r) for _, s in items for b, r, _ in s}


if __name__ == "__main__":
    od = sys.argv[1]
    os.makedirs(od, exist_ok=True)
    idx = json.load(open(f"{A}/index.json"))
    mcq = {b: json.load(open(f"{A}/mcq{b}.json")) for b in range(1, 7)}
    subs = json.load(open(f"{A}/exams.json"))[0]["subjects"]
    used = {"Prelims": set(), "Mains": set()}
    k = {"Prelims": 0, "Mains": 0}
    stage_q = {"Prelims": set(), "Mains": set()}
    for s in subs:
        st = "Prelims" if s["sub"].startswith("Screening") else "Mains"
        k[st] += 1
        label = "Prelims (Screening Test)" if st == "Prelims" else "Mains · " + " · ".join(s["sub"].split(" · ")[1:3])
        h, n, rows = pdf(s, label, None, idx, mcq, used[st])
        open(f"{od}/{st}-{k[st]}.html", "w").write(h)
        for b, r in rows:
            stage_q[st] |= {q["id"] for q in mcq[b]["rows"].get(str(r), []) if q["id"].startswith("y")}
        print(st, k[st], s["title"], n)
    allp = {q["id"] for b in mcq for qs in mcq[b]["rows"].values() for q in qs if q["id"].startswith("y")}
    print("PYQs: Prelims", len(stage_q["Prelims"]), "Mains", len(stage_q["Mains"]), "in either", len(stage_q["Prelims"] | stage_q["Mains"]), "of", len(allp))
