"""Audit of the full forms the notes show (tools/acr_audit_guide.md).

    ./gradlew testNotesDebugUnitTest --tests '*AcronymAuditTest' -Pacronym.audit=$PWD/work/acr/dump.tsv
    python3 tools/acr_audit.py check [NNN]
    python3 tools/acr_audit.py apply      -> rewrites tools/data/acronyms.tsv, then run build_acronyms.py
"""
import json, os, re, sys

D = "work/acr"
TSV = "tools/data/acronyms.tsv"


def acrs(n):
    return re.findall(r"^=== (\S+)", open(f"{D}/in_{n}.md").read(), re.M)


def check(n):
    path = f"{D}/out_{n}.jsonl"
    if not os.path.exists(path):
        return ["no output"], []
    want, errs, got, done = set(acrs(n)), [], [], None
    for ln, line in enumerate(open(path), 1):
        if not line.strip():
            continue
        try:
            o = json.loads(line)
        except Exception as e:
            errs.append(f"line {ln}: bad JSON ({e})"); continue
        if "done" in o:
            done = o["done"]; continue
        a, s = o.get("acr"), o.get("senses")
        if a not in want:
            errs.append(f"line {ln}: {a} is not in this batch")
        if not isinstance(s, list) or not s or not all(isinstance(x, list) and len(x) == 2 and str(x[0]).strip() and isinstance(x[1], list) for x in s):
            errs.append(f"line {ln}: senses must be [[meaning, [words]], ...]"); continue
        if sum(1 for x in s if not x[1]) != 1:
            errs.append(f"line {ln}: {a} needs exactly one default meaning (empty words)")
        if any("\t" in str(x[0]) or any("," in w or "\t" in w for w in x[1]) for x in s):
            errs.append(f"line {ln}: no tabs or commas inside a meaning or word")
        got.append(o)
    if done != len(want):
        errs.append(f"last line must be {{\"done\":{len(want)}}}; got {done}")
    return errs, got


def apply():
    fix = {}
    for f in sorted(os.listdir(D)):
        if f.startswith("out_"):
            n = f[4:7]
            errs, got = check(n)
            if errs:
                print(f"skip {n}: does not pass"); continue
            for o in got:
                fix[o["acr"]] = o
    lines, done = [], set()
    for l in open(TSV).read().splitlines():
        a = l.split("\t")[0]
        if a in fix and not l.startswith("#"):
            if a in done:
                continue
            done.add(a)
            # default first, as before: the app takes the first meaning with no words when none match
            for m, w in fix[a]["senses"]:
                lines.append("\t".join([a, m.strip()] + ([", ".join(x.strip() for x in w)] if w else [])))
        else:
            lines.append(l)
    for a, o in fix.items():
        if a not in done:
            for m, w in o["senses"]:
                lines.append("\t".join([a, m.strip()] + ([", ".join(x.strip() for x in w)] if w else [])))
    open(TSV, "w").write("\n".join(lines) + "\n")
    with open(f"{D}/changes.tsv", "w") as f:
        for a, o in sorted(fix.items()):
            f.write(f"{a}\t{' | '.join(m for m, _ in o['senses'])}\t{o.get('why', '')}\n")
    print(f"{len(fix)} short forms changed ({D}/changes.tsv)")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "check":
        ns = sys.argv[2:] or sorted(f[3:6] for f in os.listdir(D) if f.startswith("in_"))
        good = 0
        for n in ns:
            errs, got = check(n)
            if errs:
                print(f"{n}: FAIL", *errs[:12], sep="\n  ")
            else:
                good += 1; print(f"{n}: pass, {len(got)} changed")
        print(f"{good}/{len(ns)} batches pass")
    elif cmd == "apply":
        apply()
