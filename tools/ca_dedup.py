"""Current Affairs without the same item over and over: a scheme / project / event that runs through several periods
(announced -> launched -> carried out, e.g. AP's P4) keeps ONE full, current entry; the older repeats go. Judged by
helpers; applied to APPSC Complete's notes (the source of Group 2's notes) and to Group 2's one-liners.

    python3 tools/ca_dedup.py prep          data/cadedup/job-N.json: each job's sections (Group 2 6:g -> Complete row)
    python3 tools/ca_dedup.py check [N]     validate data/cadedup/job-N.out.json
    python3 tools/ca_dedup.py apply         apply all jobs' notes edits to app/src/complete/assets/book6.json (once:
                                            data/cadedup/applied.json records it) and move the notes links with them

job-N.out.json: {"notes": [{"row": R, "sec": s, "block": i, "drop": true},            Complete row R, as notes_fix show
                           {"row": R, "sec": s, "block": i, "md": "<merged markdown>"}],
                 "drop": ["<one-liner id>", ...],  "fix": [{"id", "s", "o", "a", "x"}, ...],
                 "items": [{"item": "P4", "kept": "6:95 sub 2", "removed": 4}, ...]}
Group 2's build (tools/group2_build.py) leaves out the dropped one-liners and applies the fixes.
"""
import glob, json, os, sys

sys.path.insert(0, os.path.dirname(__file__))
D, A = "data/cadedup", "app/src/complete/assets"
J = lambda p: json.load(open(p))
GROUPS = [range(1, 13), list(range(13, 25)), list(range(25, 36)) + [87, 88, 89], list(range(36, 55)) + [90],
          range(55, 68), [0] + list(range(68, 80)), list(range(80, 87)) + list(range(91, 97)), range(97, 116)]


def rows6():
    return [r for u in J(f"{A}/book6.json")["units"] for r in u["rows"]]


def prep():
    os.makedirs(D, exist_ok=True)
    rm = J("data/g2syl/rowmap.json")
    json.dump(rm, open(f"{D}/rowmap-at-cadedup.json", "w"))
    rows = rows6()
    for n, g in enumerate(GROUPS, 1):
        secs = [{"g2": f"6:{x}", "row": rm[f"6:{x}"][1], "title": rows[rm[f"6:{x}"][1]]["title"]} for x in g]
        json.dump({"sections": secs}, open(f"{D}/job-{n}.json", "w"), ensure_ascii=False, indent=1)
        print(f"job-{n}: {len(secs)} sections")


def check(only=None):
    from structured_md import to_blocks
    rows = rows6()
    m6 = J("app/src/group2/assets/mcq6.json")["rows"]
    bad = 0
    for f in sorted(glob.glob(f"{D}/job-*.out.json")):
        n = f.split("job-")[1].split(".")[0]
        if only and n != str(only):
            continue
        job = J(f"{D}/job-{n}.json")
        mine = {s["row"] for s in job["sections"]}
        ids = {q["id"] for s in job["sections"] for q in m6.get(s["g2"].split(":")[1], []) if not q["id"].startswith("y")}
        o = J(f)
        seen = set()
        for op in o.get("notes", []):
            k = (op.get("row"), op.get("sec"), op.get("block"))
            ok = k[0] in mine and k not in seen
            try:
                ok = ok and 0 <= k[2] < len(rows[k[0]]["secs"][k[1]]["b"])
            except Exception:
                ok = False
            if ok and "md" in op:
                try:
                    ok = bool(to_blocks(op["md"], []))
                except Exception:
                    ok = False
            elif ok:
                ok = op.get("drop") is True
            seen.add(k)
            if not ok:
                bad += 1; print(f"{f} bad notes op: {json.dumps(op)[:160]}")
        for i in o.get("drop", []):
            if i not in ids:
                bad += 1; print(f"{f} drop of unknown id {i}")
        for x in o.get("fix", []):
            if x.get("id") not in ids or len(x.get("o") or []) != 4 or x.get("a") not in range(4):
                bad += 1; print(f"{f} bad fix {json.dumps(x)[:160]}")
        print(f"{f}: {len(o.get('notes', []))} notes edits, {len(o.get('drop', []))} one-liners dropped, "
              f"{len(o.get('fix', []))} fixed, {len(o.get('items', []))} items")
    return bad


def apply():
    from structured_md import to_blocks
    if os.path.exists(f"{D}/applied.json"):
        print("already applied (data/cadedup/applied.json)"); return
    bk = J(f"{A}/book6.json")
    rows = [r for u in bk["units"] for r in u["rows"]]
    ops = {}
    for f in sorted(glob.glob(f"{D}/job-*.out.json")):
        for op in J(f).get("notes", []):
            ops[(op["row"], op["sec"], op["block"])] = op
    remap = {}  # (row, sec, old block) -> new block | None
    by = {}
    for (r, s, i), op in ops.items():
        by.setdefault((r, s), {})[i] = op
    for (r, s), od in by.items():
        old = rows[r]["secs"][s]["b"]
        new = []
        for i, blk in enumerate(old):
            op = od.get(i)
            if op is None:
                remap[(r, s, i)] = len(new); new.append(blk)
            elif op.get("drop"):
                remap[(r, s, i)] = None
            else:
                nb = to_blocks(op["md"], [])
                remap[(r, s, i)] = None
                new.extend(nb)
        # a subsection with nothing left: the app's hidden empty page
        rows[r]["secs"][s]["b"] = new or [{"k": "n", "x": [["No MCQ notes here: its facts are in the latest entry.", 0]]}]
    open(f"{A}/book6.json", "w").write(json.dumps(bk, ensure_ascii=False, separators=(",", ":")))
    nl = J(f"{A}/notelinks.json")
    moved = gone = 0
    for qid in list(nl):
        keep = []
        for ref in nl[qid]:
            p = ref.split(":")
            if p[0] == "6":
                bi, _, tr = p[3].partition(".")
                k = (int(p[1]), int(p[2]), int(bi))
                if (k[0], k[1]) in by:
                    nbi = remap.get(k)
                    if nbi is None:
                        gone += 1; continue
                    p[3] = str(nbi) + ("." + tr if tr else ""); moved += 1
            keep.append(":".join(p))
        if keep:
            nl[qid] = keep
        else:
            del nl[qid]
    open(f"{A}/notelinks.json", "w").write(json.dumps(nl, ensure_ascii=False, separators=(",", ":")))
    json.dump({"edits": len(ops), "subsections": len(by)}, open(f"{D}/applied.json", "w"))
    print(f"{len(ops)} notes edits in {len(by)} subsections; notes links: {moved} moved, {gone} dropped with their line")


if __name__ == "__main__":
    c = sys.argv[1]
    if c == "prep":
        prep()
    elif c == "check":
        sys.exit(1 if check(sys.argv[2] if len(sys.argv) > 2 else None) else 0)
    else:
        apply()
