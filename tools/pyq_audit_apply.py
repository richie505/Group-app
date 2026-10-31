"""Applies the PYQ audit (data/pyq/audit/out/*.json, written by reviewers from tools/pyq_audit_packets.py).

    python3 tools/pyq_audit_apply.py notes   # notes corrections into APPSC Complete's sources (data/onepager, data/complete-full)
    python3 tools/pyq_audit_apply.py mcqs    # MCQ fixes and drops, bad PYQs out: APPSC Complete and Prep assets

Order of a full rebuild: notes -> tools/onepager_app.py complete -> tools/pyq_apply.py -> mcqs.
A subsection k of topic b:r is box k of data/onepager/b<b>/r<r>.json when k < its box count, else page k - K of the
topic in data/complete-full/book<b>.json. A correction whose text is no longer there is reported and skipped.
Writes data/pyq/audit/applied.json (what was done) and data/pyq/bad.json (PYQ ids tools/pyq_apply.py leaves out).
"""
import glob, json, re, subprocess, sys

OUT = "data/pyq/audit/out"
APPS = {"complete": "app/src/complete/assets", "main": "app/src/main/assets"}


def results():
    for f in sorted(glob.glob(f"{OUT}/*.json")):
        try:
            yield json.load(open(f))
        except ValueError:
            print("unreadable:", f)


def plain(t):
    return re.sub(r"\*\*|==", "", t)


def fix_strings(x, find, repl):
    """Replaces find in the first string of a nested plan box that holds it (formatting dropped if it was split)."""
    if isinstance(x, str):
        if find in x:
            return x.replace(find, repl, 1), True
        if find in plain(x):
            return plain(x).replace(find, repl, 1), True
        return x, False
    if isinstance(x, list):
        for i, v in enumerate(x):
            nv, ok = fix_strings(v, find, repl)
            if ok:
                x[i] = nv
                return x, True
        return x, False
    if isinstance(x, dict):
        for k, v in x.items():
            if k == "type":
                continue
            nv, ok = fix_strings(v, find, repl)
            if ok:
                x[k] = nv
                return x, True
    return x, False


def fix_runs(block, find, repl):
    """A full-notes block's runs: in one run if it is there, else the block's text as one plain run."""
    if block.get("k") == "t":
        for row in [block["h"]] + block["r"]:
            for cell in row:
                for r in cell:
                    if find in r[0]:
                        r[0] = r[0].replace(find, repl, 1)
                        return True
        return False
    runs = block.get("x", [])
    for r in runs:
        if find in r[0]:
            r[0] = r[0].replace(find, repl, 1)
            return True
    text = "".join(r[0] for r in runs)
    if find in text:
        block["x"] = [[text.replace(find, repl, 1), 0]]
        return True
    return False


def notes():
    done, missed = 0, []
    full = {b: json.load(open(f"data/complete-full/book{b}.json")) for b in range(1, 7)}
    rows = {b: [r for u in full[b]["units"] for r in u["rows"]] for b in full}
    for res in results():
        b, ri = map(int, res["topic"].split(":"))
        pf = f"data/onepager/b{b}/r{ri}.json"
        plan = json.load(open(pf))
        K = len(plan["boxes"])
        for fx in res.get("notes_fix", []):
            try:
                k, i = map(int, fx["ref"].split("#"))
            except (ValueError, KeyError):
                missed.append((res["topic"], fx.get("ref"), "bad ref"))
                continue
            find, repl = fx.get("find", ""), fx.get("replace", "")
            if not find or find == repl:
                continue
            if k < K:
                box, ok = fix_strings(plan["boxes"][k], find, repl)
                if not ok and k == 0 and find in plan.get("quote", ""):
                    plan["quote"], ok = plan["quote"].replace(find, repl, 1), True
            else:
                secs = rows[b][ri]["secs"]
                ok = 0 <= k - K < len(secs) and 0 <= i < len(secs[k - K]["b"]) and fix_runs(secs[k - K]["b"][i], find, repl)
                if not ok and 0 <= k - K < len(secs):  # the reviewer's block number can be off by the gap notes: any block
                    ok = any(fix_runs(bl, find, repl) for bl in secs[k - K]["b"])
            if ok:
                done += 1
            else:
                missed.append((res["topic"], fx["ref"], find[:60]))
        json.dump(plan, open(pf, "w"), ensure_ascii=False, indent=1)
    for b in full:
        json.dump(full[b], open(f"data/complete-full/book{b}.json", "w"), ensure_ascii=False, separators=(",", ":"))
    print(f"notes: {done} corrections applied, {len(missed)} not found")
    return done, missed


def mcqs():
    fixes, drops, bad = {}, {}, {}
    for res in results():
        for f in res.get("mcq_fix", []):
            if f.get("id"):
                fixes[f["id"]] = f
        for d in res.get("mcq_drop", []):
            if d.get("id"):
                drops[d["id"]] = d.get("why", "")
        for p in res.get("pyq_bad", []):
            if p.get("id", "").startswith("y") and not p.get("why", "").lower().startswith("suspect key"):
                bad[p["id"]] = p.get("why", "")
    json.dump(bad, open("data/pyq/bad.json", "w"), indent=0)
    gone = set(drops) | set(bad)
    stats = {}
    for app, A in APPS.items():
        index = json.load(open(f"{A}/index.json"))
        nf = nd = 0
        for b in range(1, 7):
            m = json.load(open(f"{A}/mcq{b}.json"))
            for k in list(m["rows"]):
                qs, subs = m["rows"][k], m["subs"].get(k)
                keep = [i for i, q in enumerate(qs) if q["id"] not in gone]
                nd += len(qs) - len(keep)
                qs = [qs[i] for i in keep]
                if subs is not None:
                    m["subs"][k] = [subs[i] for i in keep]
                for q in qs:
                    f = fixes.get(q["id"])
                    if not f:
                        continue
                    changed = False
                    if isinstance(f.get("o"), list) and len(f["o"]) == len(q["o"]) and all(isinstance(o, str) and o for o in f["o"]):
                        q["o"], changed = f["o"], True
                    if isinstance(f.get("s"), str) and f["s"].strip():
                        q["s"], changed = f["s"].strip(), True
                    if isinstance(f.get("a"), int) and 0 <= f["a"] < len(q["o"]) and q.get("k") != "f":
                        q["a"], changed = f["a"], True
                        if q.get("k") == "u":
                            q.pop("k")
                    if changed:
                        q["fixed"] = f.get("why", "")[:200]  # shown nowhere; kept so a later audit knows
                        nf += 1
                m["rows"][k] = qs
                if int(k) < len(index["books"][b - 1]["rows"]):
                    index["books"][b - 1]["rows"][int(k)]["q"] = len(qs)
            json.dump(m, open(f"{A}/mcq{b}.json", "w"), ensure_ascii=False, separators=(",", ":"))
        open(f"{A}/index.json", "w").write(json.dumps(index, ensure_ascii=False, separators=(",", ":")))
        stats[app] = {"fixed": nf, "dropped": nd}
        print(f"{app}: {nf} MCQs corrected, {nd} taken out")
    subprocess.run([sys.executable, "tools/build_plan_mcq.py", APPS["complete"]], check=True)
    return stats


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "mcqs"
    log = {}
    if what == "notes":
        d, missed = notes()
        log = {"notes_applied": d, "notes_missed": missed}
        json.dump(log, open("data/pyq/audit/applied-notes.json", "w"), ensure_ascii=False, indent=0)
    else:
        json.dump(mcqs(), open("data/pyq/audit/applied-mcqs.json", "w"), indent=0)
