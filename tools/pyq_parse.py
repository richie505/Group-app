"""Parse the PYQ markdown (Drive folder MCQ-MARKDOWN) into data/pyq/all.jsonl, one question per line.

    python3 tools/pyq_parse.py <MCQ-MARKDOWN dir>
"""
import json, os, re, sys

def parse_file(path):
    txt = open(path, encoding="utf-8").read()
    out = []
    for blk in re.split(r"\n---\n", txt):
        m = re.search(r"^## \d+\s*$", blk, re.M)
        if not m:
            continue
        blk = blk[m.end():]
        meta = dict(re.findall(r"^- (\w+): ?(.*)$", blk.split("**Q.**")[0], re.M))
        if "id" not in meta:
            continue
        q = {"id": meta["id"], **{k: v for k, v in meta.items() if k != "id"}, "file": os.path.basename(path)}
        qm = re.search(r"\*\*Q\.\*\*\s*(.*?)(?=\n\d+\. |\n\*\*Answer|\Z)", blk, re.S)
        q["s"] = qm.group(1).strip() if qm else ""
        body = blk[qm.end():] if qm else blk
        opts = re.findall(r"^(\d+)\. (.*)$", body.split("**Answer")[0], re.M)
        q["o"] = [o for _, o in opts]
        am = re.search(r"\*\*Answer:\*\*\s*(.*)", blk)
        a = am.group(1).strip() if am else ""
        n = re.match(r"\(?(\d)\)?", a)
        q["a"] = int(n.group(1)) - 1 if n else (int(meta["answer"]) - 1 if meta.get("answer", "").isdigit() else -1)
        em = re.search(r"\*\*Explanation:\*\*\s*(.*?)(?=\n> \*\*|\Z)", blk, re.S)
        q["x"] = em.group(1).strip() if em else ""
        ck = re.search(r"> \*\*CHECK:\*\*\s*(.*)", blk)
        if ck:
            q["check"] = ck.group(1).strip()
        out.append(q)
    return out

if __name__ == "__main__":
    root = sys.argv[1]
    seen, allq = {}, []
    for d, _, fs in sorted(os.walk(root)):
        for f in sorted(fs):
            if f.endswith(".md") and f != "Answer-key corrections.md":
                for q in parse_file(os.path.join(d, f)):
                    q["dir"] = os.path.relpath(d, root)
                    if q["id"] in seen:
                        seen[q["id"]].setdefault("also", []).append(f)
                        continue
                    seen[q["id"]] = q
                    allq.append(q)
    os.makedirs("data/pyq", exist_ok=True)
    with open("data/pyq/all.jsonl", "w") as fh:
        for q in allq:
            fh.write(json.dumps(q, ensure_ascii=False) + "\n")
    print(len(allq), "unique questions")
