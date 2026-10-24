"""Turns an APPSC Prep backup into one for APPSC Complete, so read marks, bookmarks, MCQ answers, own notes and
study time carry over to the merged app.

    python3 tools/backup_to_complete.py <prep backup.json> <out.json>

Pages: Complete's moved.json (Prep page id -> Complete page id), and a new page counts as read when every Prep
page it was made from was read. Current Affairs (book 6) was rebuilt from the CA app, so its ids don't carry
over: a Complete page there counts as read when 80% of its words are on Prep pages that were read, and a Prep
page's bookmark, notes and time go to the Complete page that holds most of its words. Own notes: moved with Complete's notemoves.json, then put under the same
"Not in your sources" line on the page; where the merge filled that gap, the note closes the page instead.
MCQs: kept where Complete has the same question; a question the trims merged (work/mcqfull*/b<book>) passes
its answer to the merged one (wrong if any source was wrong), and a dropped repeat to the copy that was kept
(unless that one was answered itself). The file names Complete's ids version and note rounds, so the app
restores it as is.
"""
import glob, hashlib, json, os, re, sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(__file__))
P, C = "app/src/main/assets", "app/src/complete/assets"


def pages(A):
    out = {}
    for b in range(1, 7):
        rows = [r for u in json.load(open(f"{A}/book{b}.json"))["units"] for r in u["rows"]]
        for ri, r in enumerate(rows):
            for si, s in enumerate(r["secs"]):
                out[f"{b}:{ri}:{si}"] = (r["title"], s["t"], s["b"])
    return out


def block_text(b):
    x = b.get("x")
    return "".join(r[0] for r in x if isinstance(r, list) and r and isinstance(r[0], str)).strip() if isinstance(x, list) else ""


def is_gap(b):
    return b.get("k") != "h" and block_text(b).startswith("Not in your sources")


def norm(t):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", t.lower())).strip()


def qid(stem, options):  # as tools/mcq_trim_import.py
    key = norm(stem)[:300] + "|" + "|".join(norm(o)[:60] for o in options)
    return "n" + hashlib.sha1(key.encode()).hexdigest()[:11]


def bank(A):
    return {q["id"] for b in range(1, 7) for qs in json.load(open(f"{A}/mcq{b}.json"))["rows"].values() for q in qs}


def mcq_moves():
    """id -> ("merge", new id) or ("dup", kept id), over every trim stage of Complete."""
    moves = {}
    for d in sorted(glob.glob("work/mcqfull*/b*")):
        if not os.path.exists(f"{d}/orig.json"):
            continue
        orig = json.load(open(f"{d}/orig.json"))["rows"]

        def at(ref):
            r, j = ref[1:].split(".")
            qs = orig.get(r, [])
            return qs[int(j)]["id"] if int(j) < len(qs) else None
        for f in sorted(glob.glob(f"{d}/out_*.jsonl")):
            for line in open(f):
                if not line.strip():
                    continue
                o = json.loads(line)
                if o["d"] == "merge":
                    new = qid(o["s"], o["o"])
                    for ref in o["from"]:
                        i = at(ref)
                        if i and i != new:
                            moves[i] = ("merge", new)
                elif o["d"] == "drop":
                    g = re.match(r"dup (Q\d+\.\d+)", str(o.get("why", "")))
                    i, k = at(o["q"]), g and at(g.group(1))
                    if i and k and i != k:
                        moves[i] = ("dup", k)
        for f in sorted(glob.glob(f"{d}/xdup_out_*.jsonl")):
            src = open(f"{d}/xdup_in_{os.path.basename(f)[9:12]}.md").read()
            pairs = {int(p): re.findall(r"\[(n[0-9a-f]+)\]", body)
                     for p, body in re.findall(r"=== PAIR (\d+).*?\n(.*?)(?=\n=== PAIR |\Z)", src, re.S)}
            for line in open(f):
                if line.strip():
                    o = json.loads(line)
                    other = [i for i in pairs.get(o.get("p"), []) if i != o.get("drop")]
                    if o.get("drop") and other:
                        moves.setdefault(o["drop"], ("dup", other[0]))
    return moves


def main():
    src, dst = sys.argv[1], sys.argv[2]
    B = json.load(open(src))
    assert B.get("app") == "APPSC Prep backup", "not an APPSC Prep backup"
    mv = json.load(open(f"{C}/moved.json"))
    pm, cm = pages(P), pages(C)
    if B.get("ids") != json.load(open(f"{P}/moved.json"))["v"]:
        print(f"warning: the backup's page ids are version {B.get('ids')}; this tool expects the current Prep app's")
    words = lambda bl: {w for b in bl for w in re.findall(r"[a-z0-9]{4,}", block_text(b).lower())}
    cw6 = {k: words(v[2]) for k, v in cm.items() if k.startswith("6:")}
    best6 = {}

    def page(x):
        if not x.startswith("6:"):
            return mv["m"].get(x, x)
        if x not in best6 and x in pm:
            pw = words(pm[x][2])
            best6[x] = max(cw6, key=lambda k: len(pw & cw6[k]))
        return best6.get(x, x)

    report = {}

    # read marks, bookmarks, last page
    done = {page(x) for x in B["done"] if page(x) in cm and not x.startswith("6:")}
    read6 = set().union(*[words(pm[x][2]) for x in B["done"] if x.startswith("6:") and x in pm])
    done |= {k for k, w in cw6.items() if w and len(w & read6) / len(w) >= 0.8}
    done |= {new for new, olds in mv.get("r", {}).items()
             if new in cm and not new.startswith("6:") and olds and all(o in B["done"] for o in olds)}
    report["pages read"] = f"{len(B['done'])} -> {len(done)}"
    saved = []
    for line in B["saved"]:
        p = line.split("\t")
        if len(p) >= 4 and page(p[1]) in cm and all(s[1] != page(p[1]) for s in saved):
            row, title, _ = cm[page(p[1])]
            saved.append((p[0], page(p[1]), title, row))
    report["bookmarks"] = f"{len(B['saved'])} -> {len(saved)}"
    last = page(B["last"]) if B.get("last") and page(B["last"]) in cm else None

    # own notes: Complete's note rounds, then the same gap line on the page (or the page's end)
    rounds = json.load(open(f"{C}/notemoves.json"))
    added = {}
    for line in B["added"]:
        key, text = line.split("\t", 1)
        pid, bi = key.split("#")
        gap = block_text(pm[pid][2][int(bi)]) if pid in pm and 0 <= int(bi) < len(pm[pid][2]) else ""
        k = key
        for r in rounds:
            if r["id"] not in B.get("noteRounds", []):
                k = r["m"].get(k, k)
        npid, nbi = k.split("#")
        npid = npid if npid in cm else page(pid)
        blocks = cm.get(npid, (None, None, []))[2]
        if not (0 <= int(nbi) < len(blocks) and is_gap(blocks[int(nbi)])):
            same = [i for i, b in enumerate(blocks) if is_gap(b) and norm(block_text(b)) == norm(gap)]
            nbi = str(same[0]) if same else "-1"
        if npid not in cm:
            continue
        nk = f"{npid}#{nbi}"
        added[nk] = added[nk] + "\\n" + text if nk in added else text
    report["own notes"] = f"{len(B['added'])} -> {len(added)} ({sum(k.endswith('#-1') for k in added)} at a page's end)"

    # MCQ answers
    cb, moves = bank(C), mcq_moves()

    def final(i, depth=0):
        if i in cb or depth > 8:
            return i if i in cb else None
        m = moves.get(i)
        return final(m[1], depth + 1) if m else None

    ans = {a.rsplit(":", 1)[0]: a.endswith(":1") for a in B["answers"]}
    out_ans, via = {}, defaultdict(list)
    for i, ok in ans.items():
        if i in cb:
            out_ans[i] = ok
        elif (f := final(i)):
            via[f].append(ok)
        else:
            out_ans[i] = ok  # no longer in the bank: kept, as the Prep app keeps it
    carried = 0
    for f, oks in via.items():
        if f not in ans:
            out_ans[f] = all(oks)
            carried += 1
    to = lambda xs: sorted({final(i) or i for i in xs})
    seen, missed = to(B["seen"]), to(B["missed"] + [i for i, ok in out_ans.items() if not ok])
    in_bank = sum(i in cb for i in out_ans)
    report["MCQ answers"] = (f"{sum(i in cb for i in ans)} of {len(ans)} on the same question in Complete; "
                             f"{sum(map(len, via.values()))} on questions merged or repeated, carried to {carried} new ones "
                             f"(the rest were already answered there); {in_bank} answers on Complete's questions")

    # study time per page / practice (two Prep pages that became one add up)
    spent = defaultdict(lambda: [0, 0])
    for line in B.get("spent", []):
        p = line.split("\t")
        if len(p) < 5:
            continue
        k = p[2]
        if k.startswith("n:") and page(k[2:]) in cm:
            k = "n:" + page(k[2:])
        elif k.startswith("q:sub:") and page(k[6:]) in cm:
            k = "q:sub:" + page(k[6:])
        t = spent[(p[0], p[1], k)]
        t[0] += int(p[3])
        t[1] += int(p[4])

    out = dict(B)
    out.update({
        "ids": mv["v"],
        "done": sorted(done),
        "saved": sorted(f"{i}\t{a}\t{t}\t{r}" for i, (_, a, t, r) in enumerate(saved)),
        "answers": sorted(f"{k}:{1 if v else 0}" for k, v in out_ans.items()),
        "seen": seen,
        "missed": missed,
        "noteRounds": sorted(set(B.get("noteRounds", [])) | {r["id"] for r in rounds}),
        "added": sorted(f"{k}\t{v}" for k, v in added.items()),
        "spent": sorted(f"{d}\t{day}\t{k}\t{a}\t{b}" for (d, day, k), (a, b) in spent.items()),
    })
    if last:
        out["last"] = last
    else:
        out.pop("last", None)
    json.dump(out, open(dst, "w"), ensure_ascii=False, indent=1)
    for k, v in report.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
