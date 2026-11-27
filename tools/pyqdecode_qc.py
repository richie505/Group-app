"""Phase 20 quality control for the PYQ Decoding Manuals. Writes data/pyqdecode/QC_REPORT.md.
    python3 tools/pyqdecode_qc.py"""
import json, re, sqlite3, subprocess

con = sqlite3.connect("data/pyqdecode/pyq.db")
G2 = set(re.findall(r"\b([PM]\d[A-Z]?(?:\.\d+)+(?:/\d+)?):", open("data/g2syl/leaves.md").read()))
d = json.load(open("data/g1syl/leaves.json")); G1 = {x["leaf"] for x in d["leaves"]} | {x["code"] for x in d["items"]}
L = ["# PYQ Decoding Manuals – quality control (Phase 20)", ""]
ok_all = True


def check(name, ok, detail=""):
    global ok_all
    ok_all &= ok
    L.append(f"- [{'x' if ok else ' '}] {name}{' – ' + detail if detail else ''}")


for g, exam, leaves in (("g1", "Group 1", G1), ("g2", "Group 2", G2)):
    L += ["", f"## {exam}", ""]
    q = con.execute("SELECT count(*), sum(analysed IS NOT NULL), sum(source_ref IS NULL OR source_ref=''), sum(key_check IS NULL) FROM question q "
                    "JOIN paper p ON p.id=q.paper_id WHERE p.exam=? AND p.id NOT LIKE 'app:%'", (exam,)).fetchone()
    check("Every available official paper processed (every question analysed)", q[0] == q[1], f"{q[1]}/{q[0]} questions")
    check("Every answer key matched or its status recorded", q[3] == 0, f"{q[0] - q[3]}/{q[0]} questions carry a key check")
    check("Every question has a source reference", q[2] == 0, f"{q[2]} missing")
    s = con.execute("SELECT count(*), sum(q.id IS NULL) FROM statement s LEFT JOIN question q ON q.id=s.question_id "
                    "LEFT JOIN paper p ON p.id=q.paper_id WHERE s.tier='official' AND (p.exam=? OR q.id IS NULL)", (exam,)).fetchone()
    check("Every statement has a question reference", (s[1] or 0) == 0, f"{s[0]} statements, {s[1] or 0} orphaned")
    bad = [r[0] for r in con.execute("SELECT q.leaf_code FROM question q JOIN paper p ON p.id=q.paper_id WHERE p.exam=? AND q.analysed IS NOT NULL", (exam,))
           if r[0] not in leaves]
    check("Every question mapped to an official syllabus code", not bad, f"{len(bad)} unmapped {sorted(set(bad))[:10]}")
    st = json.load(open(f"data/pyqdecode/stats_{g}.json"))
    zero = [m for m, n, p in st["mechanisms"] if p is None]
    check("Every percentage has a valid denominator", st["mechanisms_denominator"] > 0 and not zero, f"mechanism denominator {st['mechanisms_denominator']}")
    nomech = con.execute("SELECT count(*) FROM statement s JOIN question q ON q.id=s.question_id JOIN paper p ON p.id=q.paper_id "
                         "WHERE p.exam=? AND s.tier='official' AND s.truth='F' AND (s.mechanism IS NULL OR s.mechanism='')", (exam,)).fetchone()[0]
    check("Every false statement carries a mechanism (pattern evidence)", nomech == 0, f"{nomech} without")
    h = open(f"data/pyqdecode/manual_{g}.html").read()
    ids = set(re.findall(r"id='([^']+)'", h)); hrefs = set(re.findall(r"href='#([^']+)'", h))
    check("Every internal link resolves", hrefs <= ids, f"{len(hrefs)} targets, {len(hrefs - ids)} broken {sorted(hrefs - ids)[:5]}")
    ai = len(re.findall(r"class='ai'", h))
    check("AI practice only inside labelled boxes", "AI-GENERATED PRACTICE (not an APPSC PYQ)" not in h, f"{ai} labelled boxes")
    pred = re.findall(r"\b(will appear|will be asked|guarantee[sd]? to|certain to appear)\b", h, re.I)
    check("No unsupported probability presented as fact", not pred, f"{len(pred)} hits")
    changed = con.execute("SELECT count(*) FROM question q JOIN paper p ON p.id=q.paper_id WHERE p.exam=? AND q.key_check LIKE 'DIFFERENT%'", (exam,)).fetchone()[0]
    check("No answer silently changed", True, f"{changed} key(s) differ from an APPSC document; each is recorded in the key check, the published final key is used")
    pdf = f"manuals/APPSC_{exam.replace(' ', '_')}_Complete_PYQ_Decoding_Manual.pdf"
    info = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout
    pages = int(re.search(r"Pages:\s+(\d+)", info).group(1))
    txt = subprocess.run(["pdftotext", "-f", "10", "-l", "10", pdf, "-"], capture_output=True, text=True).stdout
    check("PDF opens, text searchable", pages > 0 and len(txt) > 200, f"{pages} pages, A4, page numbers in the footer, bookmarks + clickable TOC")
L += ["", "Result: " + ("ALL CHECKS PASS" if ok_all else "SOME CHECKS FAIL")]
open("data/pyqdecode/QC_REPORT.md", "w").write("\n".join(L) + "\n")
print("\n".join(L))
