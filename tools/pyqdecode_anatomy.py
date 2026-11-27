"""Stage 4 seed: load the earlier statement-level "PYQ anatomy" (data/pyqanalysis/full/job-*.out.jsonl, 2026-11) into
pyq.db as DRAFT statements (verification = "draft: earlier anatomy"), matched to questions by app id or by text.
Official-paper questions are re-done in full in Stage 4 and replace these drafts.
    python3 tools/pyqdecode_anatomy.py"""
import glob, json, re, sqlite3, collections

con = sqlite3.connect("data/pyqdecode/pyq.db")
cols = [r[1] for r in con.execute("PRAGMA table_info(statement)")]
for c in ("english_rule", "subject_rule", "tier", "draft"):
    if c not in cols:
        con.execute(f"ALTER TABLE statement ADD COLUMN {c} TEXT")
con.execute("DELETE FROM statement WHERE verification LIKE 'draft:%'")
norm = lambda t: re.sub(r"[^a-z0-9]+", " ", str(t).lower()).strip()
q_in = {}
for f in glob.glob("data/pyqanalysis/full/job-*.json"):
    for q in json.load(open(f)):
        q_in[q["id"]] = q
out = {}
for f in glob.glob("data/pyqanalysis/full/job-*.out.jsonl"):
    for l in open(f):
        if l.strip():
            o = json.loads(l)
            out[o["id"]] = o
by_text = {norm(q["q"])[:90]: i for i, q in q_in.items()}
c = collections.Counter()
for qid, pid, text, exam in con.execute("SELECT q.id, q.paper_id, q.text_original, p.exam FROM question q JOIN paper p ON p.id=q.paper_id").fetchall():
    aid = qid.split("#", 1)[1] if pid.startswith("app:") and qid.split("#", 1)[1] in out else by_text.get(norm(text)[:90])
    o = out.get(aid)
    if not o:
        continue
    tier = "official" if not pid.startswith("app:") and exam != "Other APPSC exam" else ("secondary" if exam != "Other APPSC exam" else "tertiary")
    for k, u in enumerate(o.get("units") or []):
        con.execute("""INSERT OR REPLACE INTO statement(id, question_id, label, text, truth, truth_basis, true_fact, mechanism,
            decisive_phrase, cue_words_json, verification, english_rule, subject_rule, tier, draft) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (f"{qid}:{k}", qid, u.get("label"), u.get("text"), u.get("truth"), u.get("how"), u.get("true_fact"), u.get("change"),
             ", ".join(u.get("cue_words") or []), json.dumps(u.get("cue_words") or [], ensure_ascii=False), "draft: earlier anatomy",
             ",".join(u.get("english_rule") or []), u.get("subject_rule"), tier, json.dumps({"pattern": o.get("pattern"), "solve": o.get("solve"), "difficulty": o.get("difficulty"), "doubt": o.get("doubt")}, ensure_ascii=False)))
        c[(exam, tier)] += 1
con.commit()
for k, v in sorted(c.items()): print(k, v)
print("statements:", con.execute("SELECT count(*) FROM statement").fetchone()[0])
