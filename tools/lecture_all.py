"""Every topic of both apps as a lecture PDF (tools/lecture_pdf.py), subject-wise, zipped per app.

    python3 tools/lecture_all.py [group1|group2 ...]   -> out/lectures/<App>/<NN Subject>/<NNN Topic>.pdf + <App>.zip
"""
import json, os, re, sys, time, zipfile

sys.path.insert(0, os.path.dirname(__file__))
import lecture_pdf as LP

APPS = {"group1": ("app/src/group1/assets", "APPSC Group 1 Prelims", "APPSC-Group1-Prelims-Lectures"),
        "group2": ("app/src/group2/assets", "APPSC Group 2", "APPSC-Group2-Lectures")}
OUT = "out/lectures"
safe = lambda t, n=80: re.sub(r"\s+", " ", re.sub(r"[\\/:*?\"<>|]", "-", t)).strip()[:n].rstrip(" .-")
for key in (sys.argv[1:] or list(APPS)):
    A, name, folder = APPS[key]
    idx = json.load(open(f"{A}/index.json"))["books"]
    root = f"{OUT}/{folder}"
    total = 0
    for b in idx:
        sub = f"{root}/{b['id']:02d} {safe(b.get('short') or b['title'], 50)}"
        os.makedirs(sub, exist_ok=True)
        pairs, n = [], 0
        for r, info in enumerate(b["rows"]):
            if info.get("hide"):
                continue
            n += 1
            pdf = f"{sub}/{n:03d} {safe(info['title'])}.pdf"
            h = LP.build(A, b["id"], r, pdf, name)
            if h:
                pairs.append((h, pdf))
        t = time.time()
        LP.render(pairs)
        for h, _ in pairs:
            os.unlink(h)
        total += len(pairs)
        print(f"{name} · {b['title']}: {len(pairs)} lectures ({time.time() - t:.0f}s)", flush=True)
    z = f"{OUT}/{folder}.zip"
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for d, _, fs in os.walk(root):
            for f in sorted(fs):
                zf.write(os.path.join(d, f), os.path.relpath(os.path.join(d, f), OUT))
    print(f"{name}: {total} lectures -> {z} ({os.path.getsize(z) / 1e6:.0f} MB)", flush=True)
