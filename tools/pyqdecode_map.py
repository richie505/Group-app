"""Stage 3 (automatic part): give every question candidate syllabus leaves from the topic the apps file it under.
Group 1 leaves come from the Group 1 Prelims app's topic (index rows "leaves"), Group 2 codes from the Group 2 app's
topic (rows "codes"); topics are matched by title across the apps. A question gets
  leaf_code      - G2 official papers: the existing per-question mapping (kept); others: the topic's first leaf
  g1_leaves / g2_leaves (JSON lists) - every leaf of its topic, for the exact per-question choice in Stage 4
    python3 tools/pyqdecode_map.py"""
import json, re, sqlite3, collections

con = sqlite3.connect("data/pyqdecode/pyq.db")
cols = [r[1] for r in con.execute("PRAGMA table_info(question)")]
for c in ("g1_leaves", "g2_leaves", "topic"):
    if c not in cols:
        con.execute(f"ALTER TABLE question ADD COLUMN {c} TEXT")
norm = lambda t: re.sub(r"[^a-z0-9]+", " ", str(t).lower()).strip()


def rows(A):
    idx = json.load(open(f"{A}/index.json"))
    out = {}
    for b in range(1, 7):
        for j, r in enumerate(idx["books"][b - 1]["rows"]):
            out[(b, r["title"])] = r
    return out


g1, g2 = rows("app/src/group1/assets"), rows("app/src/group2/assets")
cidx = json.load(open("app/src/complete/assets/index.json"))
# every MCQ of the apps: id -> (book, topic title) and text -> (book, topic title)
by_id, by_text = {}, {}
for A, I in (("app/src/complete/assets", cidx), ("app/src/group2/assets", json.load(open("app/src/group2/assets/index.json"))),
             ("app/src/group1/assets", json.load(open("app/src/group1/assets/index.json")))):
    for b in range(1, 7):
        m = json.load(open(f"{A}/mcq{b}.json"))
        for j, qs in m["rows"].items():
            t = I["books"][b - 1]["rows"][int(j)]["title"]
            for q in qs:
                by_id.setdefault(q["id"], (b, t))
                by_text.setdefault(norm(q["s"])[:90], (b, t))
c = collections.Counter()
for qid, pid, text, leaf in con.execute("SELECT id, paper_id, text_original, leaf_code FROM question").fetchall():
    hit = by_id.get(qid.split("#", 1)[1]) if pid.startswith("app:") else None
    hit = hit or by_text.get(norm(text)[:90])
    if not hit:
        c["no topic found"] += 1
        continue
    b, t = hit
    l1 = (g1.get((b, t)) or {}).get("leaves") or []
    l2 = (g2.get((b, t)) or {}).get("codes") or []
    new_leaf = leaf or (l2[0] if (l2 and "group2" not in pid and pid.startswith(("prelims", "mains", "group2"))) else None)
    con.execute("UPDATE question SET g1_leaves=?, g2_leaves=?, topic=?, leaf_code=? WHERE id=?",
                (json.dumps(l1), json.dumps(l2), t, new_leaf, qid))
    c["topic found"] += 1
    c[f"with G1 leaves"] += bool(l1)
    c[f"with G2 codes"] += bool(l2)
con.commit()
print(dict(c))
for r in con.execute("""SELECT p.exam, p.id LIKE 'app:%', count(*), sum(q.topic IS NOT NULL), sum(q.g1_leaves NOT IN ('[]') AND q.g1_leaves IS NOT NULL),
                        sum(q.g2_leaves NOT IN ('[]') AND q.g2_leaves IS NOT NULL) FROM question q JOIN paper p ON p.id=q.paper_id GROUP BY 1,2"""):
    print(r)
