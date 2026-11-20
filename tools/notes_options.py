"""Statement-set options that leave a statement out: APPSC never asks about a statement no option mentions.
fix(q) rebuilds such a set's options (the key's truth unchanged) so every statement appears in at least one option,
decoys still near the key (one statement different), in APPSC's code style ("1 and 2 only", "2, 3 and 4 only")."""
import hashlib, itertools, random, re
import notes_realign as NR


def missing(q):
    lines, st = NR.parse(q)
    labs = [l for _, l, _ in st]
    if len(st) < 2 or NR.NOT_SET.search(q["s"]) or not labs[0].isdigit() or len(set(labs)) != len(labs):
        return None, labs
    O = " ".join(q.get("o") or [])
    if re.search(r"all of the above|all the above", O, re.I) or re.search(r"assertion|\(A\).*\(R\)", q["s"], re.I | re.S):
        return [], labs
    if sum(bool(re.match(r"\s*(only one|only two|only three|all (three|four|five)|none|all)\b", x, re.I)) for x in q.get("o") or []) >= 3:
        return [], labs  # "how many are correct": the options name no statement
    used = set(re.findall(r"\b([1-9])\b", O))
    return [l for l in labs if l not in used], labs


def fix(q):
    miss, labs = missing(q)
    if not miss or len(labs) < 3 or not (0 <= q.get("a", -1) < len(q.get("o") or [])):
        return q
    import appsc_tricks as T
    sel = T.picked(q["o"][q["a"]], labs)
    if sel is None:
        return q
    target = set(sel)
    rnd = random.Random(int(hashlib.md5(q["id"].encode()).hexdigest(), 16))
    subs = [set(c) for k in range(1, len(labs) + 1) for c in itertools.combinations(labs, k) if set(c) != target]
    best = None
    for _ in range(400):
        pick = rnd.sample(subs, 3)
        if set().union(target, *pick) != set(labs):
            continue
        score = sum(len(p ^ target) for p in pick)  # near misses first
        if best is None or score < best[0]:
            best = (score, pick)
    if best is None:
        return q
    opts = best[1] + [target]
    rnd.shuffle(opts)
    o = [NR.fmt(x, labs) for x in opts]
    return dict(q, o=o, a=opts.index(target))
