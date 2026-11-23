"""Render the infographics of the given topics from their briefs (data/infographics/briefs/<b>-<j>-<k>.md)
to out/infographics/excalidraw/<b>/<b>-<j>-<k>.png and .excalidraw.
    python3 tools/excalinfo/make.py B J [B J ...]      or      python3 tools/excalinfo/make.py all"""
import glob, os, re, subprocess, sys, tempfile, json
sys.path.insert(0, os.path.dirname(__file__))
from brief2json import parse

a = sys.argv[1:]
if a == ["all"]:
    files = sorted(glob.glob("data/infographics/briefs/*-*-*.md"))
else:
    files = [f for i in range(0, len(a), 2) for f in sorted(glob.glob(f"data/infographics/briefs/{a[i]}-{a[i+1]}-*.md"))]
args, tmp = [], tempfile.mkdtemp()
for f in files:
    name = os.path.basename(f)[:-3]
    b = name.split("-")[0]
    os.makedirs(f"out/infographics/excalidraw/{b}", exist_ok=True)
    j = os.path.join(tmp, name + ".json")
    json.dump(parse(open(f).read()), open(j, "w"), ensure_ascii=False)
    args += [j, f"out/infographics/excalidraw/{b}/{name}.png", f"out/infographics/excalidraw/{b}/{name}.excalidraw"]
for k in range(0, len(args), 300):
    subprocess.run(["node", "tools/excalinfo/infographic.js"] + args[k:k + 300], check=True, stdout=subprocess.DEVNULL)
print(f"{len(files)} infographics rendered")
