"""The blueprint pilot as app pages: data/blueprint/pilot/book.json (one topic per written unit), read by the
Reader's BlueprintPilotTest to draw the pages as the app shows them.

    python3 tools/blueprint_pilot.py U0001 U0275 U0825
"""
import json
import os
import sys

sys.path.insert(0, "tools")
from blueprint_md import unit_pages  # noqa: E402

rows = []
for u in sys.argv[1:]:
    title, pages = unit_pages(open(f"data/blueprint/out/{u}.md").read())
    rows.append({"codes": [u], "tag": "", "title": title, "sub": "", "pyq": "", "p1": 1, "p2": 1, "src": [],
                 "secs": [{"t": t, "badges": [], "p": i + 1, "b": b} for i, (t, b) in enumerate(pages)]})
    print(u, title, len(pages), "pages")
os.makedirs("data/blueprint/pilot", exist_ok=True)
json.dump({"units": [{"code": "P", "title": "Blueprint pilot", "rows": rows}]},
          open("data/blueprint/pilot/book.json", "w"), ensure_ascii=False)
