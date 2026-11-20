"""Current affairs 5-18 Nov 2026 (data/caupdate): its notes pages ("Latest: 5-18 Nov 2026") and 243 MCQs, keyed by
APPSC Complete rows, for both apps (Group 2 had the pages but its MCQs only in the old one-liner mode)."""
import glob, hashlib, json, os, sys

sys.path.insert(0, os.path.dirname(__file__))
D = "data/caupdate"


def _ru():
    return json.load(open(f"{D}/rowmap-at-caupdate.json")) if os.path.exists(f"{D}/rowmap-at-caupdate.json") else {}


def pages():
    """{(book, Complete row): [(leaf, title, blocks)]}"""
    from structured_md import to_blocks
    ru, out = _ru(), {}
    for f in sorted(glob.glob(f"{D}/notes-*.jsonl")):
        for l in open(f):
            if l.strip():
                o = json.loads(l)
                out.setdefault(tuple(ru[o["row"]]), []).append((o.get("leaf", "P4.1.2"), o["title"], to_blocks(o["md"], [])))
    return out


def mcqs():
    """{(book, Complete row): [(page title, mcq)]}"""
    ru, out = _ru(), {}
    for f in sorted(glob.glob(f"{D}/mcq-*.jsonl")):
        for l in open(f):
            if l.strip():
                n = json.loads(l)["new"]
                q = {"id": "oU" + hashlib.md5(f"{n['row']}|{n['s']}".encode()).hexdigest()[:10], "s": n["s"], "o": n["o"],
                     "a": n["a"], "x": n.get("x", "")}
                out.setdefault(tuple(ru[n["row"]]), []).append((n.get("sub", ""), q))
    return out
