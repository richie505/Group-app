"""Infographic brief (.md) -> JSON for render.js:
{"title": ..., "panels": [{"h": ..., "bullets": [...]} | {"h": ..., "table": {"head": [...], "rows": [[...]]}}]}"""
import json, re, sys


def parse(text):
    title, panels, cur = "", [], None
    for line in text.splitlines():
        l = line.strip()
        if not l:
            continue
        if l.lower().startswith("title:"):
            title = l.split(":", 1)[1].strip()
        elif re.match(r"^\d+\.\s", l) or l.startswith("## "):
            cur = {"h": re.sub(r"^(\d+\.\s*|##\s*)", "", l).replace("(table)", "").strip(), "bullets": []}
            panels.append(cur)
        elif l.startswith("|"):
            cells = [c.strip() for c in l.strip("|").split("|")]
            if all(re.fullmatch(r":?-+:?", c) for c in cells if c):
                continue
            if cur is None:
                cur = {"h": "", "bullets": []}; panels.append(cur)
            t = cur.setdefault("table", {"head": None, "rows": []})
            if t["head"] is None:
                t["head"] = cells
            else:
                t["rows"].append(cells)
        else:
            if cur is None:
                cur = {"h": "", "bullets": []}; panels.append(cur)
            cur["bullets"].append(re.sub(r"^[-•*]\s*", "", l))
    return {"title": title, "panels": panels}


if __name__ == "__main__":
    print(json.dumps(parse(open(sys.argv[1]).read()), ensure_ascii=False))
