"""APPSC Reader: APPSC Complete's full notes only, for reading (no MCQs). Writes app/src/reader/assets
(edition, topic index without MCQ counts, empty MCQ files in place of APPSC Prep's); the notes themselves come from
app/src/complete/assets at build time (Gradle task readerAssets). The simple meanings (simple.json) are built by
tools/words_check.py.

    python3 tools/reader_build.py
"""
import json
import os

A = "app/src/complete/assets"
R = "app/src/reader/assets"
os.makedirs(R, exist_ok=True)
json.dump({"edition": "reader", "name": "APPSC Reader"}, open(f"{R}/edition.json", "w"))
idx = json.load(open(f"{A}/index.json"))
for b in idx["books"]:
    b["uq"] = [0] * len(b["uq"]) if isinstance(b.get("uq"), list) else 0
    for r in b["rows"]:
        if "q" in r:
            r["q"] = 0
json.dump(idx, open(f"{R}/index.json", "w"), ensure_ascii=False, separators=(",", ":"))
for b in range(1, 7):
    json.dump({"rows": {}, "units": {}, "subs": {}}, open(f"{R}/mcq{b}.json", "w"))
topics = sum(len(b["rows"]) for b in idx["books"])
print("APPSC Reader:", topics, "topics")
