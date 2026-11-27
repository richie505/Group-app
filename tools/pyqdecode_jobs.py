"""Stage 4: export the official-paper questions (Group 1 / Group 2, tier "official") as analysis jobs
data/pyqdecode/jobs/<g1|g2>-<n>.json (~40 questions, grouped by subject), each with its options, key and key status,
candidate syllabus leaves (code + official wording) and the earlier draft statements. Questions without options (G2 Mains 2019) carry only the keyed answer. Check a job's output with:  python3 tools/pyqdecode_jobs.py check <g1|g2>-<n>
    python3 tools/pyqdecode_jobs.py export"""
import glob, json, os, re, sqlite3, sys

D = "data/pyqdecode/jobs"
con = sqlite3.connect("data/pyqdecode/pyq.db")
G2L = dict(re.findall(r"\b([PM]\d[A-Z]?(?:\.\d+)+(?:/\d+)?):\s*(.+)", open("data/g2syl/leaves.md").read()))
G1L = {x["leaf"]: x["text"] for x in json.load(open("data/g1syl/leaves.json"))["leaves"]}
MECH = None


def export(per=40):
    os.makedirs(D, exist_ok=True)
    for f in glob.glob(f"{D}/*.json"):
        os.unlink(f)
    for g, exam, L in (("g1", "Group 1", G1L), ("g2", "Group 2", G2L)):
        qs = con.execute("""SELECT q.id, q.paper_id, p.title, p.year, p.stage, q.qno, q.text_original, q.options_json, q.key_index,
            q.key_text, q.key_status, q.key_check, q.deleted, q.subject, q.leaf_code, q.g1_leaves, q.g2_leaves, q.topic, q.explanation
            FROM question q JOIN paper p ON p.id=q.paper_id WHERE p.exam=? AND q.paper_id NOT LIKE 'app:%' 
            ORDER BY q.subject, p.year, q.paper_id, q.qno""", (exam,)).fetchall()
        items = []
        for r in qs:
            cand = json.loads((r[15] if g == "g1" else r[16]) or "[]")
            if g == "g2" and r[14] and r[14] not in cand:
                cand = [r[14]] + cand
            drafts = [dict(label=s[0], text=s[1], truth=s[2], true_fact=s[3], change=s[4], cues=s[5]) for s in
                      con.execute("SELECT label, text, truth, true_fact, mechanism, decisive_phrase FROM statement WHERE question_id=? ORDER BY id", (r[0],))]
            items.append({"id": r[0], "paper": r[2], "year": r[3], "stage": r[4], "qno": r[5], "question": r[6],
                          "options": json.loads(r[7]) if r[7] else "NOT AVAILABLE – only the keyed answer is known: analyse the stem + key_text as the true proposition; no distractor analysis", "key_index": r[8], "key_text": r[9], "key_status": r[10],
                          "key_check": r[11], "deleted": bool(r[12]), "subject": r[13], "app_topic": r[17],
                          "candidate_leaves": {c: L.get(c, "") for c in cand}, "explanation_in_app": r[18], "draft_statements": drafts})
        for n, k in enumerate(range(0, len(items), per), 1):
            json.dump(items[k:k + per], open(f"{D}/{g}-{n}.json", "w"), ensure_ascii=False, indent=1)
        print(g, len(items), "questions ->", (len(items) - 1) // per + 1, "jobs")


def check(job):
    g = job.split("-")[0]
    L = G1L if g == "g1" else G2L
    want = {q["id"] for q in json.load(open(f"{D}/{job}.json"))}
    got, bad = set(), []
    for k, l in enumerate(open(f"{D}/{job}.out.jsonl")):
        if not l.strip():
            continue
        try:
            o = json.loads(l)
        except Exception as e:
            bad.append(f"line {k+1}: not JSON ({e})"); continue
        qid = o.get("id")
        if qid not in want:
            bad.append(f"line {k+1}: unknown id {qid}"); continue
        got.add(qid)
        if o.get("leaf") not in L:
            bad.append(f"{qid}: leaf {o.get('leaf')!r} is not a {g.upper()} syllabus leaf")
        for f in ("format", "micro_topic", "reconstruction", "statements"):
            if not o.get(f):
                bad.append(f"{qid}: missing {f}")
        for s in o.get("statements") or []:
            if s.get("truth") not in ("T", "F", "U"):
                bad.append(f"{qid}: statement truth must be T/F/U")
            if s.get("truth") == "F" and not (s.get("true_fact") and s.get("mechanism") and s.get("decisive_phrase")):
                bad.append(f"{qid}: F statement needs true_fact, mechanism, decisive_phrase")
            if not s.get("basis"):
                bad.append(f"{qid}: statement needs basis (key / fact-check)")
    for m in sorted(want - got):
        bad.append(f"{m}: missing")
    print(f"{job}: {len(want)} questions, problems: {len(bad)}")
    for b in bad[:40]:
        print("  " + b)


if __name__ == "__main__":
    a = sys.argv[1:]
    export() if a[:1] == ["export"] else check(a[1])
