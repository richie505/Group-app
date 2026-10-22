"""The Notes tab's two blocks for APPSC Complete: Group 1 and Group 2, each with its own subjects.

    python3 tools/build_exams.py [assets dir=app/src/complete/assets]
writes <assets>/exams.json:
  [{"title": "Group 1", "sub": ..., "subjects": [{"title", "sub", "groups": [{"title", "rows": [[book, row], ...]}]}]},
   {"title": "Group 2", ...}]
Group 1: the Prelims sections (A History & Culture ... Current Affairs), one subject per book, its topics (units)
as groups, only the sections tagged GROUP-I. Group 2: the Screening and Mains sections, from each section's
"Group-II <code>: <item>" syllabus lines, the syllabus items as groups, in syllabus order. A section that is in
both exams is listed in both, the same pages.
"""
import json, re, sys
from pathlib import Path

A = Path(sys.argv[1] if len(sys.argv) > 1 else "app/src/complete/assets")

G1_TITLES = {1: "A. History & Culture", 2: "B. Polity, Governance, Society & IR", 3: "C. Indian & AP Economy",
             4: "D. Geography", 5: "E. Science, Technology & Environment", 6: "Current Affairs"}
G2 = [  # code prefix, title, exam part
    ("S1", "Indian History", "Screening"),
    ("S2", "Geography", "Screening"),
    ("S3", "Indian Society", "Screening"),
    ("S4", "Current Affairs", "Screening"),
    ("M1-A", "Social & Cultural History of Andhra Pradesh", "Mains · Paper I · Section A"),
    ("M1-B", "Indian Constitution", "Mains · Paper I · Section B"),
    ("M2-A", "Indian & AP Economy", "Mains · Paper II · Section A"),
    ("M2-B", "Science & Technology", "Mains · Paper II · Section B"),
]


def main():
    books = {b: json.loads((A / f"book{b}.json").read_text()) for b in range(1, 7)}
    g1 = []
    for b, d in books.items():
        groups, gi = [], 0
        for u in d["units"]:
            rows = []
            for r in u["rows"]:
                if "GROUP-I" in r.get("tag", "").replace("GROUP-II", "") or b == 6:
                    rows.append([b, gi])
                gi += 1
            if rows:
                groups.append({"title": u["title"], "code": u.get("code", ""), "rows": rows})
        n = sum(len(g["rows"]) for g in groups)
        g1.append({"title": G1_TITLES[b], "sub": f"{len(groups)} topics · {n} sections", "groups": groups})
    # Group 2: syllabus item -> sections
    items = {}  # (prefix, number) -> (item title, [[book, row]])
    for b, d in books.items():
        gi = 0
        for u in d["units"]:
            for r in u["rows"]:
                for line in r.get("sub", []):
                    m = re.match(r"Group-II\s+(S\d|M\d-[AB])-(\d+):\s*(.*)", line)
                    if m:
                        k = (m.group(1), int(m.group(2)))
                        items.setdefault(k, [m.group(3).strip(), []])[1].append([b, gi])
                gi += 1
    g2 = []
    for code, title, part in G2:
        groups = [{"title": f"{code}-{n}: {t}", "code": f"{code}-{n}", "rows": rows}
                  for (c, n), (t, rows) in sorted(items.items()) if c == code]
        if groups:
            n = len({tuple(x) for g in groups for x in g["rows"]})
            g2.append({"title": title, "sub": f"{part} · {len(groups)} syllabus items · {n} sections", "groups": groups})
    out = [
        {"title": "Group 1", "sub": "Prelims · Paper I (General Studies)", "subjects": g1},
        {"title": "Group 2", "sub": "Screening and Mains", "subjects": g2},
    ]
    (A / "exams.json").write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")))
    for e in out:
        print(e["title"], [(s["title"], s["sub"]) for s in e["subjects"]])


if __name__ == "__main__":
    main()
