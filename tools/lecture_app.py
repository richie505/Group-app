"""APPSC Lectures app (flavor "lectures"): every topic's lecture slides (tools/lecture_pdf.py) as HTML, shown in a
WebView subject-wise and topic-wise. Same slides as the PDFs, a few KB each.

    python3 tools/lecture_app.py   -> app/src/lectures/assets/lec/<g1|g2>/<book>/<row>.html + lec/index.json
"""
import glob, json, os, re, shutil, subprocess, sys

sys.path.insert(0, os.path.dirname(__file__))
import lecture_pdf as LP

OUT = "app/src/lectures/assets/lec"
APPS = [("g1", "app/src/group1/assets", "APPSC Group 1 Prelims", "out/lectures/APPSC-Group1-Prelims-Lectures"),
        ("g2", "app/src/group2/assets", "APPSC Group 2", "out/lectures/APPSC-Group2-Lectures")]
SCREEN = """<meta name='viewport' content='width=1360'><style>
@media screen { html { background: #dfe3ec; scroll-snap-type: y proximity } body { padding: 28px 0 40px }
  section.s, div.s { margin: 0 auto 28px; box-shadow: 0 6px 22px rgba(20,30,70,.22); border-radius: 10px; scroll-snap-align: center } }
</style>"""
if os.path.exists(OUT):
    shutil.rmtree(OUT)
index = {"apps": []}
for key, A, name, pdfs in APPS:
    books = json.load(open(f"{A}/index.json"))["books"]
    app = {"key": key, "name": name, "subjects": []}
    for b in books:
        sj = {"id": b["id"], "title": b["title"], "short": b.get("short") or b["title"], "topics": []}
        units = [u["title"] for u in b["units"]]
        n = 0
        for r, info in enumerate(b["rows"]):
            if info.get("hide"):
                continue
            n += 1
            f = f"{OUT}/{key}/{b['id']}/{r}.html"
            os.makedirs(os.path.dirname(f), exist_ok=True)
            h = LP.build(A, b["id"], r, f[:-5] + ".pdf", name)
            doc = open(h).read().replace("<head>", "<head>" + SCREEN, 1)
            if h != f:
                os.unlink(h)
            open(f, "w").write(doc)
            # its slide count, from the PDF made by tools/lecture_all.py
            pdf = glob.glob(f"{pdfs}/{b['id']:02d} */{n:03d} *.pdf")
            pages = 0
            if pdf:
                m = re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", pdf[0]], capture_output=True, text=True).stdout)
                pages = int(m.group(1)) if m else 0
            sj["topics"].append({"n": n, "row": r, "title": info["title"], "unit": units[info.get("u", 0)] if units else "",
                                 "slides": pages, "q": info.get("q", 0), "file": f"lec/{key}/{b['id']}/{r}.html"})
        app["subjects"].append(sj)
    index["apps"].append(app)
    print(name, sum(len(s["topics"]) for s in app["subjects"]), "lectures")
json.dump(index, open(f"{OUT}/index.json", "w"), ensure_ascii=False, separators=(",", ":"))
tot = sum(os.path.getsize(os.path.join(d, x)) for d, _, fs in os.walk(OUT) for x in fs)
print(f"{tot / 1e6:.0f} MB of HTML")
