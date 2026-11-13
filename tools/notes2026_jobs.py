"""The 2026 notes rebuild + PYQ key validation for ALL subjects of APPSC Complete, in jobs done by Claude Code helpers
(never the Anthropic API). Method: data/notes2026/RUNBOOK.md (the Satavahanas pilot, data/notes2026/pilot, is job b1-r046).

    python3 tools/notes2026_jobs.py plan                 # data/notes2026/jobs.json (keeps the status of known jobs)
    python3 tools/notes2026_jobs.py prep <job>           # data/notes2026/runs/<job>/: meta, pyqs.json, all-mcqs.json, old-notes.txt
    python3 tools/notes2026_jobs.py number <job>         # notes/row-N.md -> numbered/row-N.txt (helpers run it while mapping)
    python3 tools/notes2026_jobs.py check <job>          # validates a helper's output; prints problems
    python3 tools/notes2026_jobs.py apply                # rebuilds every book from ALL done jobs (idempotent), then
                                                         # copies keys + explanations to the other apps by id
    python3 tools/notes2026_jobs.py status

Jobs:
  topic  rows R (one unit, together <= ~150 PYQs): validated keys for the PYQs it lists, blueprint, rebuilt notes for R,
         mapping of every MCQ of R (or of the first 150 PYQs + all own MCQs for a huge row)
  keys   the remaining PYQs of a huge row, 150 at a time; runs after that row's topic job; maps onto its notes
  place  PYQs that other jobs moved to a row of another job ("move_row"); maps them onto that row's notes
Outputs in the run folder: keys.jsonl, mapping.json, notes/row-N.md + blueprint.md (topic jobs), DONE (empty file).
mapping.json: {"<id>": {"row": N, "sub": S, "lines": ["S:B[.R]"...], "add": "<md bullet>"}} or {"<id>": {"move_row": N}}
  "add": a notes line the sub-section lacked (appended to that sub-section; the MCQ is linked to it).
"""
import glob
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, "tools")
from structured_md import to_blocks, from_blocks  # noqa: E402
import notelink as nl  # noqa: E402

A = "app/src/complete/assets"
D = "data/notes2026"
JOBS = f"{D}/jobs.json"
CAP = 150          # PYQs per job
MCQ_CAP = 450      # MCQs per topic job (own + PYQs)


def is_pyq(q):
    return isinstance(q, dict) and q["id"].startswith("y")


def load_jobs():
    return json.load(open(JOBS)) if os.path.exists(JOBS) else []


def save_jobs(jobs):
    json.dump(jobs, open(JOBS, "w"), ensure_ascii=False, indent=1)


def run_dir(job):
    return job.get("dir") or f"{D}/runs/{job['id']}"


def plan():
    old = {j["id"]: j for j in load_jobs()}
    idx = json.load(open(f"{A}/index.json"))
    jobs = [{"id": "b1-r046", "type": "topic", "book": 1, "rows": [46, 47, 48, 49], "dir": f"{D}/pilot",
             "status": "done", "pyqs": "all"}]
    for b in range(1, 7):
        m = json.load(open(f"{A}/mcq{b}.json"))
        irows = idx["books"][b - 1]["rows"]
        cur, cur_p, cur_n, cur_u = [], 0, 0, None

        def flush():
            nonlocal cur, cur_p, cur_n
            if cur:
                jobs.append({"id": f"b{b}-r{cur[0]:03d}", "type": "topic", "book": b, "rows": cur, "pyqs": "all"})
            cur, cur_p, cur_n = [], 0, 0

        for r in range(len(irows)):
            if b == 1 and r in (46, 47, 48, 49):
                flush()
                continue
            lst = m["rows"].get(str(r), [])
            p = sum(1 for q in lst if is_pyq(q))
            if p == 0:
                continue
            u = irows[r].get("u")
            if p > CAP:                       # a huge row: its own topic job + keys jobs
                flush()
                pids = [q["id"] for q in lst if is_pyq(q)]
                jobs.append({"id": f"b{b}-r{r:03d}", "type": "topic", "book": b, "rows": [r], "pyqs": pids[:CAP]})
                for k, i in enumerate(range(CAP, len(pids), CAP), 1):
                    jobs.append({"id": f"b{b}-r{r:03d}-k{k}", "type": "keys", "book": b, "rows": [r],
                                 "pyqs": pids[i:i + CAP], "after": f"b{b}-r{r:03d}"})
                cur_u = u
                continue
            if cur and (u != cur_u or cur_p + p > CAP or cur_n + len(lst) > MCQ_CAP):
                flush()
            cur.append(r)
            cur_p += p
            cur_n += len(lst)
            cur_u = u
        flush()
    for j in jobs:
        if j["id"] in old:
            j["status"] = old[j["id"]].get("status", "todo")
            for k in ("dir",):
                if k in old[j["id"]]:
                    j[k] = old[j["id"]][k]
        j.setdefault("status", "todo")
    save_jobs(jobs)
    from collections import Counter
    print(len(jobs), "jobs", Counter(j["type"] for j in jobs), Counter(j["status"] for j in jobs))


def get(jid):
    for j in load_jobs():
        if j["id"] == jid:
            return j
    sys.exit(f"no job {jid}")


def slim(q, r):
    return {"id": q["id"], "row": r, "src": q.get("src"), "s": q["s"], "o": q.get("o", []), "a": q.get("a"),
            "k": q.get("k"), "at": q.get("at"), "x": q.get("x") or " ".join(q.get("xa") or [])}


def prep(jid):
    j = get(jid)
    d = run_dir(j)
    os.makedirs(f"{d}/notes", exist_ok=True)
    m = json.load(open(f"{A}/mcq{j['book']}.json"))
    pyqs, allm = [], []
    want = None if j["pyqs"] == "all" else set(j["pyqs"])
    for r in j["rows"]:
        for q in m["rows"].get(str(r), []):
            if not isinstance(q, dict):
                continue
            if is_pyq(q):
                if want is None or q["id"] in want:
                    pyqs.append(slim(q, r))
                    allm.append(slim(q, r))
            elif j["type"] == "topic":
                allm.append(slim(q, r))
    if j["type"] == "place":
        pyqs = j["items"]
        allm = list(pyqs)
    json.dump(j, open(f"{d}/meta.json", "w"), ensure_ascii=False, indent=1)
    json.dump(pyqs, open(f"{d}/pyqs.json", "w"), ensure_ascii=False, indent=0)
    json.dump(allm, open(f"{d}/all-mcqs.json", "w"), ensure_ascii=False, indent=0)
    with open(f"{d}/old-notes.txt", "w") as fh:
        for r in j["rows"]:
            fh.write(subprocess.run([sys.executable, "tools/notelink.py", "show", str(j["book"]), str(r)],
                                    capture_output=True, text=True).stdout.split("\n=== OWN MCQS")[0] + "\n")
    if j["type"] in ("keys", "place"):          # the rebuilt notes they map onto
        for r in j["rows"]:
            src = rebuilt_row(j["book"], r)
            if src:
                open(f"{d}/notes/row-{r}.md", "w").write(open(src).read())
        number(jid)
    print(f"{d}: {len(pyqs)} PYQs to key, {len(allm)} MCQs to map, rows {j['rows']}")


def rebuilt_row(book, r):
    for j in load_jobs():
        if j["book"] == book and j["type"] == "topic" and r in j["rows"] and j["status"] == "done":
            f = f"{run_dir(j)}/notes/row-{r}.md"
            if os.path.exists(f):
                return f
    return None


def parse(md):
    secs, cur = [], None
    for line in md.splitlines():
        if line.startswith("=== "):
            cur = {"t": line[4:].strip(), "lines": []}
            secs.append(cur)
        elif cur is not None:
            cur["lines"].append(line)
    return [{"t": s["t"], "badges": [], "b": to_blocks("\n".join(s["lines"]), [])} for s in secs]


def numbered(secs):
    out = []
    for si, s in enumerate(secs):
        out.append(f"## SUB {si} | {s['t']}")
        for bi, blk in enumerate(s["b"]):
            if blk["k"] == "t":
                out.append(f"[{si}:{bi}] TABLE head: " + " | ".join(nl.cell(h) for h in blk["h"]))
                out += [f"  [{si}:{bi}.{ti}] " + " | ".join(nl.cell(c) for c in tr) for ti, tr in enumerate(blk["r"])]
            else:
                out.append(f"[{si}:{bi}] {from_blocks([blk], inline_tables=True)[0]}")
    return out


def number(jid):
    d = run_dir(get(jid))
    os.makedirs(f"{d}/numbered", exist_ok=True)
    for f in sorted(glob.glob(f"{d}/notes/row-*.md")):
        r = int(re.findall(r"\d+", os.path.basename(f))[-1])
        secs = parse(open(f).read())
        open(f"{d}/numbered/row-{r}.txt", "w").write("\n".join([f"=== NEW NOTES row {r}"] + numbered(secs)) + "\n")
        print(f"row {r}: {len(secs)} sub-sections, {sum(len(s['b']) for s in secs)} blocks")


def line_ok(secs, ref):
    try:
        s, b = ref.split(":")
        bi, _, tr = b.partition(".")
        blk = secs[int(s)]["b"][int(bi)]
        if tr:
            return blk["k"] == "t" and int(tr) < len(blk["r"])
        return blk["k"] != "t"
    except (ValueError, IndexError, KeyError):
        return False


def read_keys(d):
    keys = {}
    for f in sorted(glob.glob(f"{d}/keys*.jsonl")):
        for line in open(f):
            if line.strip():
                k = json.loads(line)
                keys[k["id"]] = k
    return keys


def read_mapping(d):
    mp = {}
    for f in glob.glob(f"{d}/mapping*.json"):
        mp.update(json.load(open(f)))
    return mp


def check(jid, quiet=False):
    j = get(jid)
    d = run_dir(j)
    probs = []
    pyqs = json.load(open(f"{d}/pyqs.json"))
    allm = json.load(open(f"{d}/all-mcqs.json"))
    keys, mp = read_keys(d), read_mapping(d)
    byid = {q["id"]: q for q in allm}
    for q in pyqs:
        k = keys.get(q["id"])
        if not k:
            probs.append(f"{q['id']}: no key")
            continue
        if q.get("k") == "f":
            if not (k.get("at") or q.get("at")):
                probs.append(f"{q['id']}: flashcard without answer")
        elif not k.get("add_option") and not (isinstance(k.get("a"), int) and -1 <= k["a"] < len(q["o"])):
            probs.append(f"{q['id']}: bad a {k.get('a')}")
        if not k.get("x", "").strip():
            probs.append(f"{q['id']}: no explanation")
        if not k.get("source"):
            probs.append(f"{q['id']}: no source")
    secs = {}
    for r in j["rows"]:
        f = f"{d}/notes/row-{r}.md"
        if os.path.exists(f):
            secs[r] = parse(open(f).read())
        elif j["type"] == "topic":
            probs.append(f"row {r}: no notes/row-{r}.md")
    for q in allm:
        e = mp.get(q["id"])
        if e is None:
            probs.append(f"{q['id']}: not mapped")
            continue
        if "move_row" in e:
            continue
        r = int(e.get("row", q["row"]))
        if r not in secs:
            probs.append(f"{q['id']}: row {r} is not one of this job's rebuilt rows")
            continue
        if not 0 <= int(e.get("sub", -1)) < len(secs[r]):
            probs.append(f"{q['id']}: sub {e.get('sub')} out of range")
            continue
        bad = [x for x in e.get("lines", []) if not line_ok(secs[r], x)]
        if bad:
            probs.append(f"{q['id']}: bad lines {bad}")
        if not e.get("lines") and not e.get("add"):
            probs.append(f"{q['id']}: no notes line and no 'add'")
    extra = set(mp) - set(byid)
    if extra:
        probs.append(f"{len(extra)} mapping ids not in this job, e.g. {sorted(extra)[:3]}")
    if j["type"] == "topic" and not os.path.exists(f"{d}/blueprint.md"):
        probs.append("no blueprint.md")
    if not quiet:
        print(f"{jid}: {len(pyqs)} PYQs, {len(keys)} keys, {len(allm)} MCQs, {len(mp)} mapped; {len(probs)} problems")
        for p in probs[:40]:
            print("  ", p)
    return probs


def apply():
    jobs = [j for j in load_jobs() if j["status"] == "done"]
    others = [f for f in glob.glob("app/src/*/assets/mcq*.json") if not f.startswith(A)]
    allkeys = {}
    links = json.load(open(f"{A}/notelinks.json"))
    idx = json.load(open(f"{A}/index.json"))
    # cross-book moves ({"move_book": B, "move_row": N}): taken out of their book, filed under book B row N
    xmoves, xkeys = {}, {}
    for j in jobs:
        xkeys.update(read_keys(run_dir(j)))
        for i, e in read_mapping(run_dir(j)).items():
            if "move_book" in e and int(e["move_book"]) != j["book"]:
                xmoves[i] = (int(e["move_book"]), int(e["move_row"]))
    incoming = {}                                    # book -> [(row, q)]
    for b in range(1, 7):
        m = json.load(open(f"{A}/mcq{b}.json"))
        for r, lst in m["rows"].items():
            for q in lst:
                if isinstance(q, dict) and q["id"] in xmoves and xmoves[q["id"]][0] != b:
                    if q["id"] in xkeys:
                        set_key(q, xkeys[q["id"]])
                        allkeys[q["id"]] = xkeys[q["id"]]
                    incoming.setdefault(xmoves[q["id"]][0], []).append((xmoves[q["id"]][1], q))
                    links.pop(q["id"], None)
    for b in range(1, 7):
        bj = [j for j in jobs if j["book"] == b]
        if not bj and b not in incoming:
            continue
        bk = json.load(open(f"{A}/book{b}.json"))
        rows = [r for u in bk["units"] for r in u["rows"]]
        m = json.load(open(f"{A}/mcq{b}.json"))
        where = {}                                   # id -> (row, q)
        for r, lst in m["rows"].items():
            for q in lst:
                if isinstance(q, dict) and not (q["id"] in xmoves and xmoves[q["id"]][0] != b):
                    where[q["id"]] = (int(r), q)
        moved_in = {q["id"] for _, q in incoming.get(b, [])}
        for r, q in incoming.get(b, []):
            where[q["id"]] = (r, q)
        new = {}                                     # rebuilt row -> secs
        for j in bj:
            if j["type"] != "topic":
                continue
            for r in j["rows"]:
                f = f"{run_dir(j)}/notes/row-{r}.md"
                if os.path.exists(f):
                    new[r] = parse(open(f).read())
        mapping, keys = {}, {}
        order = {"topic": 0, "keys": 1, "place": 2}
        for j in sorted(bj, key=lambda j: order[j["type"]]):
            mapping.update(read_mapping(run_dir(j)))
            keys.update(read_keys(run_dir(j)))
        # notes additions: appended to their sub-section, in id order, then linked
        adds = {}
        for i, e in sorted(mapping.items()):
            if e.get("add") and "move_row" not in e and int(e.get("row", -1)) in new:
                r, s = int(e["row"]), int(e["sub"])
                if 0 <= s < len(new[r]):
                    blks = to_blocks(e["add"].strip(), [])
                    if blks:
                        new[r][s]["b"].append(blks[0])
                        e = dict(e, lines=list(e.get("lines", [])) + [f"{s}:{len(new[r][s]['b']) - 1}"])
                        adds[i] = e
        mapping.update(adds)
        for r, secs in new.items():
            old = rows[r]
            p = old["secs"][0].get("p", old.get("p1", 0)) if old["secs"] else old.get("p1", 0)
            for s in secs:
                s["p"] = p
            old["secs"] = secs
        # placement: MCQs mapped by a done job go to (row, sub); everything else stays where it is
        placed = {}
        for i, (r, q) in where.items():
            e = mapping.get(i)
            tr, sub = r, None
            if e is not None:
                if "move_row" in e:
                    tr = int(e["move_row"])
                    if links.get(i, [""])[0].split(":")[1:2] != [str(tr)]:
                        links.pop(i, None)
                else:
                    tr = int(e.get("row", r))
                    if tr in new:
                        sub = int(e.get("sub", len(new[tr]) - 1))
                        sub = sub if 0 <= sub < len(new[tr]) else len(new[tr]) - 1
                        refs = [x for x in e.get("lines", []) if line_ok(new[tr], x)]
                        if refs:
                            links[i] = [f"{b}:{tr}:{x}" for x in refs[:3]]
                        else:
                            links.pop(i, None)
                    else:
                        tr = r
            elif r in new:                            # in a rebuilt row but no job mapped it: last sub, no link
                sub = len(new[r]) - 1
                if links.get(i) and links[i][0].split(":")[1] == str(r):
                    links.pop(i, None)
            if tr in new and sub is None:
                sub = len(new[tr]) - 1
            placed.setdefault(tr, []).append((sub, q))
            k = keys.get(i)
            if k:
                allkeys[i] = k
                set_key(q, k)
        old_subs = {r: dict(zip([q["id"] for q in m["rows"][r] if isinstance(q, dict)], m["subs"].get(r, [])))
                    for r in m["rows"]}
        for r in list(m["rows"]):
            lst = placed.get(int(r), [])
            if int(r) in new:
                lst.sort(key=lambda t: (t[0], 0 if t[1]["id"].startswith("y") else 1))
                m["rows"][r] = [q for _, q in lst]
                m["subs"][r] = [s for s, _ in lst]
            else:
                os_ = old_subs.get(r, {})
                kept = [(os_.get(q["id"], s if s is not None else 0), q) for s, q in lst]
                m["rows"][r] = [q for _, q in kept]
                if r in m["subs"]:
                    m["subs"][r] = [s for s, _ in kept]
            idx["books"][b - 1]["rows"][int(r)]["q"] = len(m["rows"][r])
        json.dump(bk, open(f"{A}/book{b}.json", "w"), ensure_ascii=False, separators=(",", ":"))
        json.dump(m, open(f"{A}/mcq{b}.json", "w"), ensure_ascii=False, separators=(",", ":"))
        print(f"book {b}: {len(new)} rows rebuilt, {len(mapping)} mapped, {len(keys)} keys")
    open(f"{A}/index.json", "w").write(json.dumps(idx, ensure_ascii=False, separators=(",", ":")))
    json.dump(links, open(f"{A}/notelinks.json", "w"), ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    subprocess.run([sys.executable, "tools/build_plan_mcq.py", A], check=True)
    n = 0
    for f in others:                                 # the same PYQ (same id) in the other apps gets the same key
        mm = json.load(open(f))
        ch = False
        for part in ("rows", "units"):
            for lst in (mm.get(part) or {}).values():
                for q in lst:
                    if isinstance(q, dict) and q["id"] in allkeys:
                        set_key(q, allkeys[q["id"]])
                        ch = True
                        n += 1
        if ch:
            json.dump(mm, open(f, "w"), ensure_ascii=False, separators=(",", ":"))
    print(f"keys copied into the other apps: {n}")


def set_key(q, k):
    if q.get("k") == "f":
        q["at"] = k.get("at") or q.get("at", "")
    elif k.get("add_option"):                    # no printed option was right: the correct one is added and keyed
        opt = k["add_option"].strip()
        low = [o.strip().lower() for o in q.get("o", [])]
        if opt.lower() not in low:
            q["o"] = list(q.get("o", [])) + [opt]
            low.append(opt.lower())
        q["a"] = low.index(opt.lower())
        if q.get("k") == "u":
            q.pop("k", None)
    elif isinstance(k.get("a"), int) and -1 <= k["a"] < len(q.get("o", [])):
        q["a"] = k["a"]
        if k["a"] >= 0 and q.get("k") == "u":
            q.pop("k", None)
        if k["a"] == -1:
            q["k"] = "u"
    tag = ""
    if k.get("add_option") and q.get("k") != "f":
        tag = (f"⚠ Option added: the printed options did not include the correct answer"
               f" ({k['add_option'].strip()}); it is added as option {q['a'] + 1}.\n")
    xx = tag + (k.get("outdated", "").strip() + "\n" if k.get("outdated") else "") + k.get("x", "").strip()
    if xx.strip():
        q["x"] = xx.strip()
        q.pop("xs", None)
        q.pop("xa", None)


def status():
    from collections import Counter
    jobs = load_jobs()
    c = Counter((j["type"], j["status"]) for j in jobs)
    print(dict(c))
    for b in range(1, 7):
        bj = [j for j in jobs if j["book"] == b]
        print(f"book {b}: {sum(1 for j in bj if j['status'] == 'done')}/{len(bj)} done")



def done_next(jid, book=None):
    """Marks <jid> done (check must pass), picks the next runnable job (same book first), preps it, prints its prompt."""
    probs = check(jid, quiet=True)
    if probs:
        print("check failed:", probs[:5])
        return
    jobs = load_jobs()
    st = {j["id"]: j["status"] for j in jobs}
    b = int(book) if book else get(jid)["book"]
    nxt = None
    for j in jobs:
        if j["id"] == jid:
            j["status"] = "done"
            st[jid] = "done"
    for pref in (b, None):
        for j in jobs:
            if j["status"] == "todo" and st.get(j.get("after"), "done") == "done" and (pref is None or j["book"] == pref):
                nxt = j
                break
        if nxt:
            break
    if nxt:
        nxt["status"] = "running"
    save_jobs(jobs)
    if nxt:
        prep(nxt["id"])
        print_prompt(nxt["id"])


def start(book):
    jobs = load_jobs()
    st = {j["id"]: j["status"] for j in jobs}
    for j in jobs:
        if j["book"] == book and j["status"] == "todo" and st.get(j.get("after"), "done") == "done":
            j["status"] = "running"
            save_jobs(jobs)
            prep(j["id"])
            print_prompt(j["id"])
            return


def print_prompt(jid):
    j = get(jid)
    titles = dict(l.rstrip("\n").split("\t", 1) for l in open(f"{D}/rows-book{j['book']}.txt"))
    topic = f"book {j['book']} rows {j['rows']}: " + "; ".join(titles[str(r)] for r in j["rows"])
    txt = (open(f"{D}/HELPER-PROMPT{'-KEYS' if j['type'] == 'keys' else ''}.txt").read()
           .replace("{JOB}", jid).replace("{TOPIC}", topic))
    open(f"{run_dir(j)}/PROMPT.txt", "w").write(txt)
    print(f"next: {jid} ({j['type']}, book {j['book']}, rows {j['rows']}) -> {run_dir(j)}/PROMPT.txt")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "start":
        start(int(sys.argv[2]))
    elif cmd == "prompt":
        print_prompt(sys.argv[2])
    elif cmd == "done_next":
        done_next(*sys.argv[2:])
    elif cmd in ("plan", "apply", "status"):
        globals()[cmd]()
    else:
        globals()[cmd](sys.argv[2])
