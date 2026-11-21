"""Style rewrite: flag rewritten MCQs whose keyed option is not the original right answer while another option is
(a script that reordered options may have left "a" on the wrong slot).
    python3 tools/style_keycheck.py [N ...]"""
import glob, json, re, sys
norm = lambda t: re.sub(r"[^a-z0-9]+", " ", str(t).lower()).strip()
D = "data/rocketoneliner/style"
ns = sys.argv[1:] or sorted(int(re.search(r"sty-(\d+)\.out", f).group(1)) for f in glob.glob(f"{D}/sty-*.out.jsonl"))
bad = 0
for n in ns:
    Q, cur = {}, None
    for l in open(f"{D}/sty-{n}.txt"):
        if l.startswith("  O: "):
            ops = l[5:].rstrip("\n").split(" | ")
            Q[cur] = norm(re.sub(r"^\*?\d\) ", "", next(o for o in ops if o.startswith("*"))))
        elif not l.startswith("  "):
            cur = l.split(" ", 1)[0]
    for l in open(f"{D}/sty-{n}.out.jsonl"):
        if not l.strip():
            continue
        o = json.loads(l)
        if o.get("drop") or not isinstance(o.get("o"), list):
            continue
        ans = Q.get(o["id"])
        opts = [norm(x) for x in o["o"]]
        hit = [i for i, x in enumerate(opts) if x == ans]
        if hit and o["a"] not in hit:
            bad += 1
            print(f"sty {n} {o['id']}: keyed {o['o'][o['a']]!r}, original answer is option {hit[0]} {o['o'][hit[0]]!r}")
print(f"suspect keys: {bad}")
