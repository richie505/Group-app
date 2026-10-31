"""Audit packets: one text file per APPSC Complete topic with its notes, its PYQs (the answer key that wins) and the
app MCQs filed there (APPSC Complete's), for a reviewer
to mark wrong answers, wrong statements and MCQs that are off the exam's depth.

    python3 tools/pyq_audit_packets.py [book:row ...]   (default: every topic)

Writes data/pyq/audit/in/<book>-<row>.md.
"""
import json, os, sys

sys.path.insert(0, "tools")
from onepager_app import block_text  # noqa: E402

C = "app/src/complete/assets"
OUT = "data/pyq/audit/in"


def opts(q):
    return " / ".join(f"({i + 1}) {o}" for i, o in enumerate(q.get("o", [])))


def line(q):
    a = q.get("a", -1)
    ans = f"ANS {a + 1}" if a >= 0 else "NO KEY"
    return f"[{q['id']}] {q['s'].replace(chr(10), ' ')} || {opts(q)} || {ans}"


def main(only):
    os.makedirs(OUT, exist_ok=True)
    n = 0
    for b in range(1, 7):
        book = json.load(open(f"{C}/book{b}.json"))
        cm = json.load(open(f"{C}/mcq{b}.json"))
        ri = 0
        for u in book["units"]:
            for r in u["rows"]:
                key = f"{b}:{ri}"
                if only and key not in only:
                    ri += 1
                    continue
                L = [f"# TOPIC {key}: {r['title']}", "", "## NOTES"]
                for k, s in enumerate(r["secs"]):
                    L.append(f"### sub {k}: {s['t']}{' (full notes)' if s.get('f') else ''}")
                    L += [f"- [{k}#{i}] {block_text(x)}" for i, x in enumerate(s["b"]) if block_text(x).strip()]
                qs, subs = cm["rows"].get(str(ri), []), cm["subs"].get(str(ri), [])
                py = [(s, q) for q, s in zip(qs, subs) if q["id"].startswith("y")]
                own = [(s, q) for q, s in zip(qs, subs) if not q["id"].startswith("y")]
                L += ["", "## PYQS (official answers: these are right)"]
                L += [f"- sub {s} {('APPSC ' if q.get('ap') else '')}{q.get('src', '')}: {line(q)}" for s, q in py]
                L += ["", "## APP MCQS (APPSC Complete)"]
                L += [f"- sub {s}: {line(q)}" for s, q in own]
                open(f"{OUT}/{b}-{ri}.md", "w").write("\n".join(L) + "\n")
                n += 1
                ri += 1
    print(n, "packets")


if __name__ == "__main__":
    main(set(sys.argv[1:]))
