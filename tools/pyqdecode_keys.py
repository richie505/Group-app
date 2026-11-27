"""Stage 2c: apply the key checks (data/pyqdecode/keycheck_g1.jsonl, keycheck_g2.jsonl) to pyq.db.
The key in APPSC's own document wins; the earlier stored key is kept in key_check for the record.
    python3 tools/pyqdecode_keys.py"""
import json, os, sqlite3, collections

con = sqlite3.connect("data/pyqdecode/pyq.db")
c = collections.Counter()
for f in ("data/pyqdecode/keycheck_g1.jsonl", "data/pyqdecode/keycheck_g2.jsonl"):
    if not os.path.exists(f):
        continue
    for l in open(f):
        if not l.strip():
            continue
        o = json.loads(l)
        qid = f"{o['paper']}#{o['n']}"
        r = o["result"]
        c[r] += 1
        note = f"{r} vs {o.get('doc')} ({o.get('doc_status') or ''}) {o.get('note') or ''}".strip()
        if r == "DIFFERENT" and o.get("doc_a") is not None:
            row = con.execute("SELECT options_json, key_index FROM question WHERE id=?", (qid,)).fetchone()
            opts = json.loads(row[0]) if row and row[0] else None
            con.execute("UPDATE question SET key_index=?, key_text=?, key_check=? WHERE id=?",
                        (o["doc_a"], opts[o["doc_a"]] if opts else None, note + f"; earlier stored key {row[1] if row else '?'}", qid))
        elif r == "DELETED_IN_DOC":
            con.execute("UPDATE question SET deleted=1, key_check=? WHERE id=?", (note, qid))
        else:
            con.execute("UPDATE question SET key_check=? WHERE id=?", (note, qid))
con.commit()
print(dict(c))
