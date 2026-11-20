"""APPSC Lectures for the desktop: one app holding the APPSC Lectures decks (Group 1 Prelims, Group 2) and the RocketOne
decks (Group 1 Prelims, Group 2), with a library, search, resume and full-screen presenting (desktop-lectures/web).

    python3 tools/desklec_build.py        -> out/desktop-lectures/APPSC Lectures/app/   (index.html opens in any browser)
    desktop-lectures/windows/build.sh     -> the Windows installer and portable zip around it

The decks are the phone apps' own (tools/lecture_app.py, tools/rocketone.py build), each given desktop-lectures/web/shim.js
so the deck talks to the app's window instead of the Android bridge.
"""
import json, os, shutil, sys

OUT = "out/desktop-lectures/APPSC Lectures/app"
WEB = "desktop-lectures/web"
GROUPS = [  # name, what it is, [(key, edition name, its lec/ folder's parent, notes assets for the part titles)]
    ("APPSC Lectures", "From the full notes of the APPSC apps",
     [("g1", "Group 1 Prelims", "app/src/lectures/assets", "app/src/group1/assets"),
      ("g2", "Group 2", "app/src/lectures/assets", "app/src/group2/assets")]),
    ("RocketOne", "Only from the Rocket Sheets and Rocket Current Affairs 2026",
     [("r1", "Group 1 Prelims", "app/src/rocketone/assets", "data/rocketone/assets"),
      ("r2", "Group 2", "app/src/rocketone/assets", "data/rocketone/assets-g2")]),
]
SHIM = '<script src="../../../shim.js"></script>'

shutil.rmtree("out/desktop-lectures", ignore_errors=True)
os.makedirs(OUT)
lib, n, size = {"groups": []}, 0, 0
for gname, note, eds in GROUPS:
    g = {"name": gname, "note": note, "eds": []}
    for key, ename, root, notes in eds:
        app = next(a for a in json.load(open(f"{root}/lec/index.json"))["apps"] if a["key"] == key)
        ed = {"key": key, "name": ename, "subjects": []}
        for sj in app["subjects"]:
            bk = json.load(open(f"{notes}/book{sj['id']}.json"))
            rows = [r for u in bk["units"] for r in u["rows"]]
            units = []
            for t in sj["topics"]:
                if not units or units[-1]["t"] != t["unit"]:
                    units.append({"t": t["unit"], "lectures": []})
                parts = [s["t"] for s in rows[t["row"]]["secs"] if s.get("b")]
                units[-1]["lectures"].append({"t": t["title"], "sl": t["slides"], "f": t["file"], "p": parts})
                src, dst = f"{root}/{t['file']}", f"{OUT}/{t['file']}"
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                doc = open(src, encoding="utf-8").read()
                assert "</head>" in doc, src
                doc = doc.replace("</head>", SHIM + "</head>", 1)
                open(dst, "w", encoding="utf-8").write(doc)
                n += 1
                size += len(doc)
            ed["subjects"].append({"title": sj["title"], "short": sj["short"], "units": units})
        g["eds"].append(ed)
        print(gname, ename, sum(len(u["lectures"]) for s in ed["subjects"] for u in s["units"]), "lectures")
    lib["groups"].append(g)
open(f"{OUT}/library.js", "w", encoding="utf-8").write("const LIB = " + json.dumps(lib, ensure_ascii=False, separators=(",", ":")) + ";\n")
for f in ("index.html", "shim.js"):
    shutil.copy(f"{WEB}/{f}", f"{OUT}/{f}")
shutil.copy("desktop/src/main/resources/icon.png", f"{OUT}/icon.png")
print(n, "lectures,", round(size / 1e6), "MB of decks,", round(os.path.getsize(f"{OUT}/library.js") / 1e6, 1), "MB library ->", OUT)
