"""APPSC Complete's Current Affairs book: Prep's 18 current-affairs topics, the CA app's news pages in them.

    python3 tools/ca_build.py <CA app assets dir> [assets=app/src/complete/assets]
Reads work/merge/ca_map.json (tools/ca_map.py) and Prep's book6 / mcq6 (app/src/main/assets). Writes the new
app's book6.json, mcq6.json and its index.json entry:
  * a topic (unit) per Prep current-affairs topic, in Prep's order;
  * in each topic a section (row) per CA-app period, newest first ("Sep–Oct 2026", ... "Special topics"), its
    pages the CA app's news pages that went to this topic, in the CA app's order (newest month first);
  * then a section "Prep notes" with Prep's own pages of the topic, until tools/ca_merge folds them in;
  * every MCQ follows its page: the CA app's (src "ca") and Prep's.
Each section keeps Prep's syllabus codes, Group-I/II tag and Group-II syllabus lines, so the Notes tab's Group 1
and Group 2 blocks (tools/build_exams.py) list it.
"""
import json, os, sys
from collections import defaultdict
from pathlib import Path

ca_dir = Path(sys.argv[1])
A = Path(sys.argv[2] if len(sys.argv) > 2 else "app/src/complete/assets")
PREP = Path("app/src/main/assets")
PERIODS = {11: "Sep–Oct 2026", 12: "Jun–Aug 2026", 13: "Mar–May 2026", 14: "Dec 2025–Feb 2026", 15: "Apr–Nov 2025",
           16: "Special topics"}


def rows_of(d):
    return [r for u in d["units"] for r in u["rows"]]


def main():
    cmap = json.load(open("work/merge/ca_map.json"))["ca"]
    prep = json.load(open(PREP / "book6.json"))
    prows = rows_of(prep)
    pmcq = json.load(open(PREP / "mcq6.json"))
    ca_books = {b: json.load(open(ca_dir / f"book{b}.json")) for b in PERIODS}
    ca_rows = {b: rows_of(d) for b, d in ca_books.items()}
    ca_mcq = {b: json.load(open(ca_dir / f"mcq{b}.json")) for b in PERIODS}
    # (CA book, row, page) -> Prep topic
    to = {(x["b"], x["r"], x["s"]): x["to"] for x in cmap}

    units, rows, origin = [], [], {}  # origin: ("ca", b, r, s) or ("prep", r, s) -> (new row, new sec)
    for ti, pr in enumerate(prows):
        units.append({"code": "", "title": pr["title"]})
        for b, period in PERIODS.items():
            secs = []
            for r, row in enumerate(ca_rows[b]):
                for s, sec in enumerate(row["secs"]):
                    if to.get((b, r, s)) == ti:
                        origin[("ca", b, r, s)] = (len(rows), len(secs))
                        secs.append(dict(sec, o=f"ca{b}:{r}:{s}"))
            if secs:
                rows.append({"codes": pr.get("codes", []), "tag": pr.get("tag", ""), "title": f"{period}: {pr['title']}",
                             "sub": pr.get("sub", []), "pyq": pr.get("pyq", ""), "p1": pr.get("p1", 0), "p2": pr.get("p2", 0),
                             "secs": secs, "src": ["CA app"], "unit": ti})
        for s, sec in enumerate(pr["secs"]):
            origin[("prep", ti, s)] = (len(rows), s)
        rows.append(dict(pr, title=f"Prep notes: {pr['title']}", unit=ti))
    # units hold their rows
    book = {k: v for k, v in prep.items() if k != "units"}
    book["units"] = [dict(u, rows=[{k: v for k, v in r.items() if k != "unit"} for r in rows if r["unit"] == i])
                     for i, u in enumerate(units)]
    # MCQs follow their pages
    mrows, msubs = defaultdict(list), defaultdict(list)
    for b in PERIODS:
        for r, qs in ca_mcq[b]["rows"].items():
            for q, s in zip(qs, ca_mcq[b]["subs"].get(r, [-1] * len(qs))):
                at = origin.get(("ca", b, int(r), s))
                if at:
                    mrows[str(at[0])].append(dict(q, src="ca"))
                    msubs[str(at[0])].append(at[1])
    for r, qs in pmcq["rows"].items():
        for q, s in zip(qs, pmcq["subs"].get(r, [-1] * len(qs))):
            at = origin.get(("prep", int(r), max(s, 0)))
            if at:
                mrows[str(at[0])].append(q)
                msubs[str(at[0])].append(s if s >= 0 else -1)
    mcq = {"rows": dict(mrows), "units": {}, "subs": dict(msubs)}
    dump = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":"))
    (A / "book6.json").write_text(dump(book))
    (A / "mcq6.json").write_text(dump(mcq))
    os.system(f"{sys.executable} tools/ca_index.py {A}")
    flat = rows_of(book)
    print(f"book 6: {len(book['units'])} topics, {len(flat)} sections, {sum(len(r['secs']) for r in flat)} pages, "
          f"{sum(len(v) for v in mcq['rows'].values())} MCQs "
          f"({sum(q.get('src') == 'ca' for v in mcq['rows'].values() for q in v)} from the CA app)")


if __name__ == "__main__":
    main()
