#!/usr/bin/env python3
"""Merge subsections that cover the same topic in two different sections (e.g. "POCSO Act 2012" under
Child rights and again under the JJ/POCSO section), so each topic is read once.

  * Run it until it merges nothing more (a merged page can take part in the next pass).
  * Score: how much of subsection A's distinctive content (rare words weighted by idf) is also in
    subsection B of another section. A topic pair is merged when the score is >= 0.6, or >= 0.5 with
    similar titles, or >= 0.4 / >= 0.3 with clearly / nearly the same title (top 3 matches each).
  * A is merged into B: the sentences / table rows of A that B does not already say (see
    dedup_notes.inside) are added at the end of B under A's title, then A is deleted. A pair is skipped
    when more than half of A would be new to B (85% when the titles say it is the same topic): then
    they are different topics after all.
    "Universal angles" pages are never merged; a section always keeps at least one subsection.
  * Ids shift: assets/moved.json maps every old "book:row:sec" (as shipped before this version) to its
    new id ("m"; a merged subsection to the one it went into) and lists the merged ones ("g"), so read
    marks and bookmarks move with them (ProgressStore.migrate). Each subsection keeps its shipped id in
    "o" across passes; delete those and moved.json before restructuring a later release again. MCQs and
    keyterms.json move the same way; index.json counts are updated.

Usage: python3 tools/merge_topics.py app/src/main/assets [--dry-run]
Then run tools/dedup_notes.py for repeated sentences.
"""
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dedup_notes import PRONOUN, content, cut, plain, run_list, sentences  # noqa: E402

GENERIC = set("universal angles key features provisions current relevance andhra pradesh india ap overview".split())
VERSION = "2.18"


def title_words(t):
    return {w for w in content(t)[0] if w not in GENERIC}


def covered(u, target_words):
    """The kept subsection already says this: 70% of its words and every number are there."""
    w, n = u[2], u[3]
    return len(w) < 3 or (len(w - target_words) <= 0.3 * len(w) and n <= target_words)


def units_of(sec):
    """(block index, row index or span, words, numbers, text) for each sentence / table row."""
    out = []
    for bi, blk in enumerate(sec["b"]):
        if blk["k"] == "t":
            for ri, row in enumerate(blk["r"]):
                text = " ".join(plain(c) for c in row)
                w, n = content(text)
                out.append((bi, ri, w, n, text))
        elif "x" in blk:
            text = plain(blk["x"])
            for span in sentences(text):
                w, n = content(text[span[0]:span[1]])
                out.append((bi, span, w, n, text[span[0]:span[1]]))
    return out


def main():
    assets = Path(sys.argv[1])
    dry = "--dry-run" in sys.argv
    books = {b: json.loads((assets / f"book{b}.json").read_text()) for b in range(1, 7)}
    rows = {b: [r for u in bk["units"] for r in u["rows"]] for b, bk in books.items()}
    for b in rows:
        for ri, r in enumerate(rows[b]):
            for si, s in enumerate(r["secs"]):
                s.setdefault("o", f"{b}:{ri}:{si}")

    subs = []
    for b in range(1, 7):
        for ri, r in enumerate(rows[b]):
            for si, s in enumerate(r["secs"]):
                us = units_of(s)
                w = set().union(*[u[2] for u in us]) if us else set()
                subs.append(dict(loc=(b, ri, si), sec=s, units=us, w=w,
                                 words=sum(len(u[4].split()) for u in us), title=s["t"]))
    at = {s["loc"]: i for i, s in enumerate(subs)}
    df = Counter(x for s in subs for x in s["w"])
    n_subs = len(subs)
    idf = {k: math.log(n_subs / v) for k, v in df.items()}
    inv = defaultdict(list)
    for i, s in enumerate(subs):
        for x in s["w"]:
            if df[x] <= 60:
                inv[x].append(i)

    cands = []
    for i, s in enumerate(subs):
        if s["title"].startswith("Universal") or not s["units"]:
            continue
        sc = Counter()
        for x in s["w"]:
            if df[x] <= 60:
                for j in inv[x]:
                    if subs[j]["loc"][:2] != s["loc"][:2]:
                        sc[j] += idf[x]
        total = sum(idf[x] for x in s["w"] if df[x] <= 60)
        if not sc or not total:
            continue
        for j, v in sc.most_common(3):
            if subs[j]["title"].startswith("Universal"):
                continue
            score = v / total
            a, c = title_words(s["title"]), title_words(subs[j]["title"])
            tsim = len(a & c) / max(1, min(len(a), len(c)))
            if score >= 0.6 or (score >= 0.5 and tsim >= 0.34) or (score >= 0.4 and tsim >= 0.5) or (score >= 0.3 and tsim >= 0.6):
                cands.append((score, tsim, i, j))
    cands.sort(reverse=True)

    merged_into = {}  # i -> j
    received = set()
    left = Counter((b, r) for b in rows for r in range(len(rows[b])) for _ in rows[b][r]["secs"])
    skipped_new = 0
    plans = []
    for score, tsim, i, j in cands:
        while j in merged_into:
            j = merged_into[j]
        if i in merged_into or i in received or i == j or subs[i]["loc"][:2] == subs[j]["loc"][:2]:
            continue
        if left[subs[i]["loc"][:2]] <= 1:
            continue
        a, t = subs[i], subs[j]
        new = [u for u in a["units"] if not covered(u, t["w"])]
        new_words = sum(len(u[4].split()) for u in new)
        # clearly the same topic: merge even when worded differently (up to 85% new wording)
        same_topic = (score >= 0.55 and tsim >= 0.34) or (score >= 0.45 and tsim >= 0.5)
        if new_words > (0.85 if same_topic else 0.5) * max(1, a["words"]):
            skipped_new += 1
            continue
        merged_into[i] = j
        received.add(j)
        left[a["loc"][:2]] -= 1
        plans.append((score, tsim, i, j, new, new_words))

    print(f"topic pairs: {len(cands)}; merged: {len(plans)}; kept apart (mostly different content): {skipped_new}")
    print("merged per book:", dict(sorted(Counter(subs[p[2]]["loc"][0] for p in plans).items())))
    saved = sum(subs[p[2]]["words"] - p[5] for p in plans)
    print(f"words no longer read twice: {saved}; facts carried over into the kept subsection: {sum(p[5] for p in plans)} words")
    if dry:
        for p in plans:
            if "POCSO" in subs[p[2]]["title"] or "Juvenile" in subs[p[2]]["title"] or "helpline" in subs[p[2]]["title"]:
                print("  example:", subs[p[2]]["loc"], subs[p[2]]["title"][:50], "->", subs[p[3]]["loc"], subs[p[3]]["title"][:50], f"+{p[5]}w")
        import random
        random.seed(7)
        for score, tsim, i, j, new, nw in random.sample(plans, min(40, len(plans))):
            a, t = subs[i], subs[j]
            print(f"{score:.2f}/{tsim:.2f} {a['loc']} {a['title'][:60]} [{a['words']}w, +{nw}] -> {t['loc']} {t['title'][:60]}")
        return

    # ---- carry the new facts into the kept subsection --------------------------------------------
    for score, tsim, i, j, new, nw in sorted(plans, key=lambda p: (p[3], p[2])):
        a, t = subs[i], subs[j]
        sec = t["sec"]
        sec["badges"] = list(dict.fromkeys(sec.get("badges", []) + a["sec"].get("badges", [])))
        if not new:
            continue
        keep_rows = defaultdict(set)
        keep_spans = defaultdict(list)
        for bi, key, *_ in new:
            if isinstance(key, int):
                keep_rows[bi].add(key)
            else:
                keep_spans[bi].append(key)
        added = []
        src = a["sec"]["b"]
        for bi, blk in enumerate(src):
            if blk["k"] == "t":
                if keep_rows[bi]:
                    added.append({**blk, "r": [r for k, r in enumerate(blk["r"]) if k in keep_rows[bi]]})
            elif "x" in blk:
                text = plain(blk["x"])
                spans = sentences(text)
                keep = set(keep_spans[bi])
                # keep a sentence the next kept one leans on ("It ...")
                for k in range(len(spans) - 1):
                    if spans[k + 1] in keep and PRONOUN.match(text[spans[k + 1][0]:spans[k + 1][1]]):
                        keep.add(spans[k])
                drop = [sp for sp in spans if sp not in keep]
                if keep:
                    added.append({**blk, "x": cut(run_list(blk["x"]), drop)})
                elif blk["k"] == "b" and bi + 1 < len(src) and src[bi + 1]["k"] == "s" and keep_spans[bi + 1]:
                    added.append(blk)
        if added:
            sec["b"] = sec["b"] + [{"k": "p", "x": [[a["title"], 1]]}] + added

    # ---- delete merged subsections and renumber ----------------------------------------------------
    gone = {subs[i]["loc"] for i in merged_into}
    new_id = {}
    for b in range(1, 7):
        for ri, r in enumerate(rows[b]):
            k = 0
            for si in range(len(r["secs"])):
                if (b, ri, si) not in gone:
                    new_id[(b, ri, si)] = (b, ri, k)
                    k += 1
            r["secs"] = [s for si, s in enumerate(r["secs"]) if (b, ri, si) not in gone]
    for i, j in merged_into.items():
        while j in merged_into:
            j = merged_into[j]
        new_id[subs[i]["loc"]] = new_id[subs[j]["loc"]]
    for b, bk in books.items():
        (assets / f"book{b}.json").write_text(json.dumps(bk, ensure_ascii=False, separators=(",", ":")))

    ids = lambda t: f"{t[0]}:{t[1]}:{t[2]}"  # noqa: E731
    moves = {ids(o): ids(n) for o, n in new_id.items() if o != n}
    # every subsection carries its id as shipped ("o"), so moved.json maps shipped ids to current ones
    moved_path = assets / "moved.json"
    prev = json.loads(moved_path.read_text()) if moved_path.exists() else {"m": {}, "g": []}
    cur = lambda t: ids(new_id[tuple(map(int, t.split(":")))])  # noqa: E731
    chained = {k: cur(v) for k, v in prev["m"].items() if k in prev["g"]}  # earlier merges follow their page
    gone_now = []
    for b in range(1, 7):
        for ri, r in enumerate(rows[b]):
            for si, s in enumerate(r["secs"]):
                if s["o"] != ids((b, ri, si)):
                    chained[s["o"]] = ids((b, ri, si))
    for i, j in merged_into.items():
        o = subs[i]["sec"]["o"]
        chained[o] = ids(new_id[subs[i]["loc"]])
        gone_now.append(o)
    moved_path.write_text(json.dumps({"v": VERSION, "m": chained, "g": sorted(set(prev["g"]) | set(gone_now))}, separators=(",", ":")))

    # key terms: follow the subsection, merged ones join the kept page's list
    kt_path = assets / "keyterms.json"
    kt = json.loads(kt_path.read_text())
    out = {}
    for k in sorted(kt, key=lambda k: k in moves and moves[k] != k):
        b, r, s = map(int, k.split(":"))
        nk = ids(new_id.get((b, r, s), (b, r, s)))
        out[nk] = list(dict.fromkeys(out.get(nk, []) + kt[k]))[:8]
    kt_path.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")))

    # MCQs follow their subsection (into another section when it was merged there)
    mcq = {b: json.loads((assets / f"mcq{b}.json").read_text()) for b in range(1, 7)}
    per = {b: defaultdict(list) for b in range(1, 7)}
    moved_q = 0
    for b, m in mcq.items():
        for r, qs in m["rows"].items():
            for q, s in zip(qs, m["subs"][r]):
                r = int(r)
                if s >= 0 and (b, r, s) in new_id:
                    nb, nr, ns = new_id[(b, r, s)]
                    moved_q += (nb, nr) != (b, r)
                else:
                    nb, nr, ns = b, r, s
                per[nb][nr].append((ns, q))
    counts = {}
    for b, m in mcq.items():
        m["rows"] = {str(r): [q for _, q in v] for r, v in sorted(per[b].items())}
        m["subs"] = {str(r): [s for s, _ in v] for r, v in sorted(per[b].items())}
        counts[b] = {r: len(v) for r, v in per[b].items()}
        (assets / f"mcq{b}.json").write_text(json.dumps(m, ensure_ascii=False, separators=(",", ":")))
    index_path = assets / "index.json"
    index = json.loads(index_path.read_text())
    for bk in index["books"]:
        for ri, r in enumerate(bk["rows"]):
            r["n"] = len(rows[bk["id"]][ri]["secs"])
            r["q"] = counts.get(bk["id"], {}).get(ri, 0)
    index_path.write_text(json.dumps(index, ensure_ascii=False, separators=(",", ":")))
    print(f"MCQs moved with their topic to another section: {moved_q}")


if __name__ == "__main__":
    main()
