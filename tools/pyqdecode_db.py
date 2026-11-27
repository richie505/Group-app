"""Stage 2: build data/pyqdecode/pyq.db (SQLite) from the stored papers (data/g2papers, data/appscpapers/group1-*)
with key provenance (data/pyqdecode/key_provenance.json). Re-runnable; overwrites the paper/question tables only.
    python3 tools/pyqdecode_db.py"""
import glob, json, os, re, sqlite3

DB = "data/pyqdecode/pyq.db"
prov = json.load(open("data/pyqdecode/key_provenance.json"))
con = sqlite3.connect(DB)
con.executescript("""
DROP TABLE IF EXISTS paper; DROP TABLE IF EXISTS question;
CREATE TABLE paper(id TEXT PRIMARY KEY, exam TEXT, year INT, stage TEXT, title TEXT, date TEXT, source_paper TEXT,
  source_key TEXT, key_status TEXT, key_doc TEXT, key_doc_kind TEXT);
CREATE TABLE question(id TEXT PRIMARY KEY, paper_id TEXT, qno INT, text_original TEXT, text_corrected TEXT,
  correction_reason TEXT, format TEXT, options_json TEXT, key_index INT, key_text TEXT, key_status TEXT,
  key_check TEXT, deleted INT, subject TEXT, leaf_code TEXT, source_ref TEXT, extraction_confidence TEXT,
  explanation TEXT);
CREATE TABLE IF NOT EXISTS statement(id TEXT PRIMARY KEY, question_id TEXT, label TEXT, text TEXT, truth TEXT,
  truth_basis TEXT, true_fact TEXT, mechanism TEXT, decisive_phrase TEXT, cue_words_json TEXT, leaf_code TEXT,
  topic TEXT, micro_topic TEXT, blueprint_keyword TEXT, verification TEXT, fact_source TEXT);
CREATE TABLE IF NOT EXISTS syllabus(exam TEXT, leaf_code TEXT, subject TEXT, unit TEXT, topic TEXT, micro_topic TEXT,
  official_wording TEXT, blueprint_keywords TEXT, PRIMARY KEY(exam, leaf_code));
""")


def fmt(s, opts):
    t = s.lower()
    if "assertion" in t and "reason" in t: return "assertion-reason"
    if re.search(r"list[- ]?i\b|match the following|correctly matched|incorrectly matched|match list", t): return "matching"
    if re.search(r"chronological|correct order|sequence|arrange", t): return "chronology"
    if re.search(r"statements?\b", t) and re.search(r"\n\s*(i|1|a)[.)]\s", s, re.I): return "statement-based"
    if re.search(r"\bnot\b|\bincorrect\b|\bfalse\b|\bexcept\b", t): return "negative one-liner"
    return "one-liner"


n = 0
for f in sorted(glob.glob("data/g2papers/*[0-9].json")) + sorted(glob.glob("data/appscpapers/group1*.json")):
    pid = os.path.basename(f)[:-5]
    d = json.load(open(f))
    exam = "Group 1" if pid.startswith("group1") else "Group 2"
    stage = "Mains" if "mains" in pid else ("Prelims" if ("prelims" in pid or exam == "Group 1") else "Single-stage (pre-2016 pattern)")
    pv = prov.get(pid, {})
    con.execute("INSERT INTO paper VALUES(?,?,?,?,?,?,?,?,?,?,?)", (pid, exam, int(d["date"][:4]), stage, d["paper"], d["date"],
        d.get("source_paper"), d.get("source_key"), pv.get("status", d.get("key_status")), pv.get("doc"), pv.get("kind")))
    for q in d["questions"]:
        opts = q.get("o")
        a = q.get("a")
        key_text = (opts[a] if opts and isinstance(a, int) and 0 <= a < len(opts) else q.get("answer"))
        con.execute("INSERT INTO question VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (f"{pid}#{q['n']}", pid, q["n"], q["s"], None, None,
            fmt(q["s"], opts), json.dumps(opts, ensure_ascii=False) if opts else None, a if isinstance(a, int) else None, key_text,
            pv.get("status", d.get("key_status")), "pending", 1 if q.get("deleted") else 0, q.get("subject"), None,
            f"{pid} Q{q['n']}", "options missing" if not opts else "clean JSON", q.get("x")))
        n += 1
# Group 2: the existing question -> leaf mapping
for f in glob.glob("data/g2papers/*.leaves.json"):
    pid = os.path.basename(f)[:-len(".leaves.json")]
    for qn, leaf in json.load(open(f)).items():
        con.execute("UPDATE question SET leaf_code=? WHERE id=?", (leaf, f"{pid}#{qn}"))
con.commit()
for row in con.execute("SELECT p.exam, count(*), sum(q.deleted), sum(q.options_json IS NULL), sum(q.leaf_code IS NOT NULL) FROM question q JOIN paper p ON p.id=q.paper_id GROUP BY p.exam"):
    print(row)
for row in con.execute("SELECT p.exam, q.format, count(*) FROM question q JOIN paper p ON p.id=q.paper_id GROUP BY 1,2 ORDER BY 1,3 DESC"):
    print(row)
print(n, "questions ->", DB)
