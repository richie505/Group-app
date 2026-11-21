"""Telugu narration scripts for the lecture videos (tools/lecture_video.py, NARRATION=te): one per topic, written by
helper jobs from the topic's Rocket-style slides (data/lecrocket/<group>/<book>-<row>.json).

    python3 tools/lecvideo_jobs.py export group2        -> data/lecvideo/jobs/job-N.txt (about 10 topics each)
    python3 tools/lecvideo_jobs.py check N              -> checks the scripts of job N's topics
    python3 tools/lecvideo_jobs.py status               -> how many topics have a script
"""
import glob, json, os, re, sys

D = "data/lecvideo/jobs"
PER = 10


def topics(g):
    A = f"app/src/{g}/assets"
    idx = json.load(open(f"{A}/index.json"))["books"]
    for b in range(1, 7):
        rows = [r for u in json.load(open(f"{A}/book{b}.json"))["units"] for r in u["rows"]]
        for i, r in enumerate(rows):
            if idx[b - 1]["rows"][i].get("hide") or not os.path.exists(f"data/lecrocket/{g}/{b}-{i}.json"):
                continue
            yield b, i, r


def render(g, b, i, r):
    sl = json.load(open(f"data/lecrocket/{g}/{b}-{i}.json"))
    L = [f"## topic {g} {b}-{i} | {r['title']}"]
    for j in sorted(sl, key=int):
        L.append(f"### part {j}: {r['secs'][int(j)]['t']}")
        for bi, bl in enumerate(sl[j]):
            if bl["k"] == "t":
                L.append(f"[{bi}] table: " + " | ".join(bl["h"]))
                for ri, rw in enumerate(bl["r"]):
                    L.append(f"  [{bi}.{ri}] " + " | ".join(rw))
            else:
                L.append(f"[{bi}] {bl['k']}: {bl['x']}")
    return "\n".join(L)


def export(g):
    os.makedirs(D, exist_ok=True)
    T = list(topics(g))
    for f in glob.glob(f"{D}/job-*.txt"):
        os.unlink(f)
    for n in range(0, len(T), PER):
        open(f"{D}/job-{n // PER + 1}.txt", "w").write("\n\n".join(render(g, *t) for t in T[n:n + PER]) + "\n")
    print(f"{len(T)} topics in {-(-len(T) // PER)} jobs")


TE = re.compile(r"[ఀ-౿]")


def check_topic(g, b, i):
    p = f"data/lecvideo/{g}/{b}-{i}.json"
    if not os.path.exists(p):
        return ["no script"]
    try:
        s = json.load(open(p))
    except Exception as e:
        return [f"not JSON: {e}"]
    sl = json.load(open(f"data/lecrocket/{g}/{b}-{i}.json"))
    bad = []
    need = set()
    for j, bl in sl.items():
        for bi, x in enumerate(bl):
            if x["k"] == "t":
                need |= {(j, bi, ri) for ri in range(len(x["r"]))}
            elif x["k"] in ("b", "x"):
                need.add((j, bi, None))
    have = set()
    texts = [x.get("te", "") for x in s.get("intro", []) + s.get("outro", [])]
    for j, beats in (s.get("parts") or {}).items():
        if j not in sl:
            bad.append(f"part {j} is not a part of the slides")
            continue
        for bt in beats:
            bi, ri = bt.get("b"), bt.get("r")
            if not isinstance(bi, int) or not 0 <= bi < len(sl[j]):
                bad.append(f"part {j}: block {bi} does not exist")
                continue
            x = sl[j][bi]
            if x["k"] == "t" and ri is not None and not 0 <= ri < len(x["r"]):
                bad.append(f"part {j}: row {bi}.{ri} does not exist")
            have.add((j, bi, ri if x["k"] == "t" else None))
            texts.append(bt.get("te", ""))
    miss = sorted(need - have, key=lambda z: (int(z[0]), z[1], -1 if z[2] is None else z[2]))
    if miss:
        bad.append(f"rows / points not explained: {['%s:%s%s' % (j, bi, '' if ri is None else '.%s' % ri) for j, bi, ri in miss[:12]]}")
    if not s.get("intro") or not s.get("outro"):
        bad.append("intro / outro missing")
    if not s.get("recap") or not all(isinstance(x, str) for x in s["recap"]):
        bad.append("recap (English points for the last card) missing")
    for t in texts:
        if not t.strip():
            bad.append("an empty te line")
            break
        if len(TE.findall(t)) < 0.5 * len(re.findall(r"[A-Za-zఀ-౿]", t)):
            bad.append(f"not Telugu enough: {t[:60]!r}")
            break
        lat = re.findall(r"\b[A-Za-z]{2,}\b", t)
        if lat:
            bad.append(f"Latin letters (the voice cannot read them; write in Telugu script): {lat[:5]}")
            break
    return bad


def check(n):
    txt = open(f"{D}/job-{n}.txt").read()
    T = re.findall(r"^## topic (\S+) (\d+)-(\d+) ", txt, re.M)
    probs = 0
    for g, b, i in T:
        bad = check_topic(g, int(b), int(i))
        if bad:
            probs += 1
            print(f"{b}-{i}: " + "; ".join(bad))
    print(f"{len(T)} topics, {probs} with problems")


def status(g="group2"):
    T = list(topics(g))
    ok = sum(1 for b, i, _ in T if not check_topic(g, b, i))
    print(f"{g}: {ok} of {len(T)} topics have a good script")


if __name__ == "__main__":
    a = sys.argv[1:]
    {"export": lambda: export(a[1]), "check": lambda: check(a[1]), "status": lambda: status(*a[1:])}[a[0]]()
