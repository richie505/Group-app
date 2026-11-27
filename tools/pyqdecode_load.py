"""Stage 4 load: put the finished job outputs (data/pyqdecode/jobs/*.out.jsonl) into pyq.db – question fields (format,
leaf, micro_topic, blueprint keyword, core fact, reconstruction, key note) and one statement row per unit (replacing
the drafts of those questions). Mechanism names are normalised with data/pyqdecode/mechanisms.json.
    python3 tools/pyqdecode_load.py"""
import glob, json, sqlite3, collections

con = sqlite3.connect("data/pyqdecode/pyq.db")
M = json.load(open("data/pyqdecode/mechanisms.json"))["map"]
qcols = [r[1] for r in con.execute("PRAGMA table_info(question)")]
for c in ("micro_topic", "blueprint_keyword", "core_fact", "reconstruction", "key_note", "practice", "leaf_note", "analysed"):
    if c not in qcols:
        con.execute(f"ALTER TABLE question ADD COLUMN {c} TEXT")
scols = [r[1] for r in con.execute("PRAGMA table_info(statement)")]
for c in ("phrases_json", "mechanism_raw"):
    if c not in scols:
        con.execute(f"ALTER TABLE statement ADD COLUMN {c} TEXT")
norm = lambda m: M.get((m or "").strip().lower(), (m or "").strip().lower()) or None
c = collections.Counter()
for f in sorted(glob.glob("data/pyqdecode/jobs/*.out.jsonl")):
    for l in open(f):
        o = json.loads(l)
        qid = o["id"]
        con.execute("""UPDATE question SET format=?, leaf_code=?, leaf_note=?, micro_topic=?, blueprint_keyword=?, core_fact=?,
            reconstruction=?, key_note=?, practice=?, analysed=? WHERE id=?""",
            (o.get("format"), o.get("leaf"), o.get("leaf_note"), o.get("micro_topic"), o.get("blueprint_keyword"), o.get("core_fact"),
             json.dumps(o.get("reconstruction"), ensure_ascii=False), o.get("key_note"), o.get("practice"), f.split("/")[-1], qid))
        con.execute("DELETE FROM statement WHERE question_id=?", (qid,))
        for k, s in enumerate(o.get("statements") or []):
            con.execute("""INSERT INTO statement(id, question_id, label, text, truth, truth_basis, true_fact, mechanism, mechanism_raw,
                decisive_phrase, cue_words_json, phrases_json, leaf_code, micro_topic, blueprint_keyword, verification, fact_source, tier)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (f"{qid}:{k}", qid, s.get("label"), s.get("text"), s.get("truth"), s.get("basis"), s.get("true_fact"),
                 norm(s.get("mechanism")) if s.get("truth") == "F" else None, s.get("mechanism"), s.get("decisive_phrase"),
                 json.dumps([p.get("phrase") for p in s.get("phrases") or []], ensure_ascii=False),
                 json.dumps(s.get("phrases") or [], ensure_ascii=False), o.get("leaf"), o.get("micro_topic"), o.get("blueprint_keyword"),
                 "analysed (Stage 4)", s.get("fact_source"), "official"))
            c["statements"] += 1
        c["questions"] += 1
con.commit()
print(dict(c))
for r in con.execute("""SELECT p.exam, count(DISTINCT q.id), count(s.id), sum(s.truth='T'), sum(s.truth='F'), sum(s.truth='U')
    FROM question q JOIN paper p ON p.id=q.paper_id JOIN statement s ON s.question_id=q.id WHERE q.analysed IS NOT NULL GROUP BY 1"""):
    print(r)
