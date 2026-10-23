"""ROCKET's General Science (Physics, Chemistry, Biology) as topics of APPSC Complete's Science book.

    python3 tools/add_general_science.py <ROCKET assets dir> [assets=app/src/complete/assets]
Prep's Science & Technology book has no general-science topics, so most ROCKET Physics / Chemistry / Biology
blocks came back from the merge as "NOT HERE". This appends ROCKET's three units to book5.json whole, as the
last topics, with their MCQs (src "rocket"); an MCQ that tools/merge_mcqs.py already put in book 4 or 5 is not
added twice. Run after tools/topic_import.py and tools/merge_mcqs.py for books 4 and 5; then
tools/build_exams.py. Running it again does nothing (the units are found by title).
"""
import json, os, sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from merge_mcqs import same

UNITS = ["Physics", "Chemistry", "Biology"]
TITLE = "General Science: "


def rows_of(d):
    return [r for u in d["units"] for r in u["rows"]]


def index_entry(entry, book, mcq):
    entry["units"] = [{"code": u.get("code", ""), "title": u["title"]} for u in book["units"]]
    entry["rows"], gi = [], 0
    for ui, u in enumerate(book["units"]):
        for r in u["rows"]:
            entry["rows"].append({"u": ui, "codes": r.get("codes", []), "title": r["title"], "tag": r.get("tag", ""),
                                  "pyq": r.get("pyq", ""), "p1": r.get("p1", 0), "p2": r.get("p2", 0),
                                  "n": len(r["secs"]), "q": len(mcq["rows"].get(str(gi), []))})
            gi += 1
    entry["pages"] = sum(r["n"] for r in entry["rows"])


def main():
    rk = Path(sys.argv[1])
    A = Path(sys.argv[2] if len(sys.argv) > 2 else "app/src/complete/assets")
    book = json.load(open(A / "book5.json"))
    mcq = json.load(open(A / "mcq5.json"))
    if any(u["title"].startswith(TITLE) for u in book["units"]):
        print("book 5: General Science already added")
        return
    rbook = json.load(open(rk / "book5.json"))
    rmcq = json.load(open(rk / "mcq5.json"))
    have = [q for b in (4, 5) for qs in json.load(open(A / f"mcq{b}.json"))["rows"].values() for q in qs]
    gi = len(rows_of(book))
    rgi, added, skipped, pages = 0, 0, 0, 0
    for u in rbook["units"]:
        take = u["title"] in UNITS
        if take:
            new_u = {"code": "GS", "title": TITLE + u["title"], "rows": []}
        for r in u["rows"]:
            if take:
                new_u["rows"].append({k: v for k, v in r.items() if k != "codes"} | {"codes": []})
                pages += len(r["secs"])
                qs, subs = rmcq["rows"].get(str(rgi), []), rmcq["subs"].get(str(rgi), [])
                keep = [(dict(q, src="rocket"), s) for q, s in zip(qs, subs or [-1] * len(qs))
                        if not any(same(q, h) for h in have)]
                skipped += len(qs) - len(keep)
                if keep:
                    mcq["rows"][str(gi)] = [q for q, _ in keep]
                    mcq["subs"][str(gi)] = [s for _, s in keep]
                    added += len(keep)
                gi += 1
            rgi += 1
        if take:
            book["units"].append(new_u)
    dump = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":"))
    (A / "book5.json").write_text(dump(book))
    (A / "mcq5.json").write_text(dump(mcq))
    index = json.load(open(A / "index.json"))
    index_entry(index["books"][4], book, mcq)
    (A / "index.json").write_text(dump(index))
    print(f"book 5: General Science added, {pages} pages, {added} MCQs ({skipped} already in books 4-5)")


if __name__ == "__main__":
    main()
