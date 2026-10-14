"""Explanation pass (2.50): every MCQ's WHY checked against the restructured notes.

    python3 tools/mcq_why.py export [MCQs per batch=300]
        writes work/mcqwhy/in_NNN.md: per topic, each page's notes and its MCQs labelled by id
    python3 tools/mcq_why.py check [NNN]
    python3 tools/mcq_why.py apply
        writes every passing batch's corrected explanations (and the few corrected keys) into the assets

An agent answers in work/mcqwhy/out_NNN.jsonl (tools/mcq_why_guide.md): one line per MCQ it changes,
    {"id":"n0123456789a","x":"new explanation"}            explanation only
    {"id":"...","x":"...","a":2,"key":"notes say ..."}    the marked answer was wrong too
and a last line {"done":N} with N = the number of MCQs in the batch.
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from structured_md import from_blocks
from mcq_cut_export import question

A = "app/src/main/assets"
D = "work/mcqwhy"
WARN = "⚠ Sources differ"


def load(b):
    notes = json.load(open(f"{A}/book{b}.json"))
    return [r for u in notes["units"] for r in u["rows"]], json.load(open(f"{A}/mcq{b}.json"))


def export(per=300):
    os.makedirs(D, exist_ok=True)
    for f in os.listdir(D):
        if f.startswith("in_"):
            os.remove(f"{D}/{f}")
    batch, count, n = [], 0, 0

    def flush():
        nonlocal batch, count, n
        if batch:
            open(f"{D}/in_{n:03d}.md", "w").write("\n\n".join(batch) + "\n")
            n, batch, count = n + 1, [], 0

    for b in range(1, 7):
        rows, mcq = load(b)
        for ri, r in enumerate(rows):
            qs, subs = mcq["rows"].get(str(ri), []), mcq["subs"].get(str(ri), [])
            if not qs:
                continue
            under = {}
            for j, s in enumerate(subs):
                under.setdefault(s, []).append(j)
            parts = [f"=== BOOK {b} ROW {ri} | {r['title']}"]
            if -1 in under:
                parts.append("## PAGE -1 | whole topic")
                parts += [question(qs[j]["id"], qs[j]) for j in under[-1]]
            for si, s in enumerate(r["secs"]):
                if si not in under:
                    continue
                md, _ = from_blocks(s["b"], inline_tables=True)
                parts.append(f"## PAGE {si} | {s['t']}\n--- notes ---\n{md}\n--- MCQs ({len(under[si])}) ---")
                parts += [question(qs[j]["id"], qs[j]) for j in under[si]]
            if batch and count + len(qs) > per:
                flush()
            batch.append("\n\n".join(parts))
            count += len(qs)
    flush()
    print(f"{n} batches")


def ids_of(n):
    return re.findall(r"^\[(n[0-9a-f]{11}|[^\]\s]+)\] ", open(f"{D}/in_{n}.md").read(), re.M)


def check(n):
    path = f"{D}/out_{n}.jsonl"
    if not os.path.exists(path):
        return ["no output"], 0, 0
    ids, errs, seen, keys, done = set(ids_of(n)), [], set(), 0, None
    for ln, line in enumerate(open(path), 1):
        if not line.strip():
            continue
        try:
            o = json.loads(line)
        except Exception as e:
            errs.append(f"line {ln}: bad JSON ({e})")
            continue
        if "done" in o:
            done = o["done"]
            continue
        i = o.get("id")
        if i not in ids:
            errs.append(f"line {ln}: {i} is not an MCQ of this batch")
        elif i in seen:
            errs.append(f"line {ln}: {i} twice")
        seen.add(i)
        if not str(o.get("x", "")).strip():
            errs.append(f"line {ln}: {i} needs a non-empty x")
        if "a" in o:
            keys += 1
            if o["a"] not in (0, 1, 2, 3) or not str(o.get("key", "")).strip():
                errs.append(f"line {ln}: {i} key change needs a 0-3 and a 'key' reason")
    if done != len(ids):
        errs.append(f"last line must be {{\"done\":{len(ids)}}} (all MCQs read); got {done}")
    return errs, len(seen), keys


def apply():
    fixes = {}
    for f in sorted(os.listdir(D)):
        if f.startswith("out_"):
            n = f[4:7]
            if check(n)[0]:
                print(f"skip {n}: does not pass")
                continue
            for line in open(f"{D}/{f}"):
                o = json.loads(line) if line.strip() else {}
                if "id" in o:
                    fixes[o["id"]] = o
    changed = keyed = 0
    log = []
    for b in range(1, 7):
        path = f"{A}/mcq{b}.json"
        mcq = json.load(open(path))
        for qs in mcq["rows"].values():
            for q in qs:
                o = fixes.get(q["id"])
                if not o:
                    continue
                x = o["x"].strip()
                warn = [l for l in q.get("x", "").split("\n") if l.startswith(WARN)]
                if warn and WARN not in x:
                    x += "\n" + warn[0]
                if "a" in o and o["a"] != q["a"]:
                    log.append(f"{q['id']}\tbook {b}\t{'ABCD'[q['a']]} -> {'ABCD'[o['a']]}\t{o['key']}\t{q['s'][:100]}")
                    q["a"] = o["a"]
                    keyed += 1
                if x != q.get("x"):
                    q["x"] = x
                    changed += 1
        open(path, "w").write(json.dumps(mcq, ensure_ascii=False, separators=(",", ":")))
    open(f"{D}/keys_changed.tsv", "w").write("\n".join(log) + "\n")
    print(f"{changed} explanations rewritten, {keyed} answer keys corrected ({D}/keys_changed.tsv)")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "export":
        export(*map(int, sys.argv[2:]))
    elif cmd == "check":
        ns = sys.argv[2:] or sorted(f[3:6] for f in os.listdir(D) if f.startswith("in_"))
        good = 0
        for n in ns:
            errs, ch, k = check(n)
            if errs:
                print(f"{n}: FAIL", *errs[:12], sep="\n  ")
            else:
                good += 1
                print(f"{n}: pass, {ch} explanations changed, {k} keys")
        print(f"{good}/{len(ns)} batches pass")
    elif cmd == "apply":
        apply()
