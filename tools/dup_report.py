"""APPSC Complete's question bank, checked for duplicates (flags them; deletes nothing): data/merge-report.md.

- exact duplicate: same question text and the same options (normalised: case, spaces, punctuation, option order);
- conflicting answers: such a pair whose keys differ;
- near-duplicate (for review): same topic, same right answer, question words 80%+ the same, or the same text with
  different options. Two MCQs on one subject (two on Article 21) are not duplicates unless they ask the same thing.

    python3 tools/dup_report.py
"""
import collections, json, re

A = "app/src/complete/assets"
STOP = set("the a an of in on to and or for with by is are was were which following what who whom when where how not as at be it its from that this these".split())


def norm(t):
    return re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()


def toks(t):
    return {w for w in norm(t).split() if w not in STOP and len(w) > 1}


def main():
    qs = []
    for b in range(1, 7):
        for r, v in json.load(open(f"{A}/mcq{b}.json"))["rows"].items():
            for q in v:
                qs.append((b, int(r), q))
    total = len(qs)
    pyq = sum(q["id"].startswith("y") for _, _, q in qs)
    by_subject = collections.Counter(b for b, _, _ in qs)
    no_x = sum(1 for _, _, q in qs if not (q.get("x") or "").strip())
    no_key = sum(1 for _, _, q in qs if not 0 <= q["a"] < len(q["o"]))

    exact = collections.defaultdict(list)
    for b, r, q in qs:
        exact[(norm(q["s"]), tuple(sorted(norm(o) for o in q["o"])))].append((b, r, q))
    ex_groups = [g for g in exact.values() if len(g) > 1]
    conflicts = [g for g in ex_groups if len({norm(q["o"][q["a"]]) if 0 <= q["a"] < len(q["o"]) else "" for _, _, q in g}) > 1]

    near = []
    by_row = collections.defaultdict(list)
    for b, r, q in qs:
        by_row[(b, r)].append(q)
    seen_pairs = set()
    for (b, r), v in by_row.items():
        for i, x in enumerate(v):
            tx, ax = toks(x["s"]), norm(x["o"][x["a"]]) if 0 <= x["a"] < len(x["o"]) else ""
            for y in v[i + 1:]:
                ay = norm(y["o"][y["a"]]) if 0 <= y["a"] < len(y["o"]) else ""
                same_text = norm(x["s"]) == norm(y["s"])
                if not (same_text or (ax and ax == ay)):
                    continue
                ty = toks(y["s"])
                j = len(tx & ty) / max(1, len(tx | ty))
                key = (x["id"], y["id"])
                if (j >= 0.8 or same_text) and key not in seen_pairs and (norm(x["s"]), tuple(sorted(map(norm, x["o"])))) != (norm(y["s"]), tuple(sorted(map(norm, y["o"])))):
                    seen_pairs.add(key)
                    near.append((b, r, x, y, j))

    extra = sum(len(g) - 1 for g in ex_groups)
    out = [
        "# APPSC Complete: question bank check",
        "",
        "Made by `tools/dup_report.py` from the app's own files; nothing is deleted. Exact duplicates are listed so they",
        "can be hidden from targets; near-duplicates are only for review.",
        "",
        "| | Count |",
        "|---|---|",
        f"| MCQs in the app | {total:,} |",
        f"| of which PYQs | {pyq:,} |",
        f"| of which the app's own | {total - pyq:,} |",
        f"| Exact duplicate groups (same text, same options) | {len(ex_groups):,} |",
        f"| Extra copies in those groups | {extra:,} |",
        f"| Of the groups, keys that conflict | {len(conflicts):,} |",
        f"| Near-duplicates for review (same topic, same answer, ~same question) | {len(near):,} |",
        f"| MCQs without an explanation | {no_x:,} |",
        f"| MCQs without an answer key | {no_key:,} |",
        f"| Unique MCQs (all, minus extra copies) | {total - extra:,} |",
        "",
        "By subject: " + ", ".join(f"book {b}: {n:,}" for b, n in sorted(by_subject.items())),
        "",
        "## Exact duplicates",
        "",
    ]
    for g in ex_groups:
        out.append("- " + " = ".join(f"`{q['id']}` ({b}:{r})" for b, r, q in g) + f": {g[0][2]['s'][:120]}")
    out += ["", "## Conflicting keys", ""]
    for g in conflicts:
        out.append("- " + "; ".join(f"`{q['id']}` → {q['o'][q['a']] if 0 <= q['a'] < len(q['o']) else 'no key'}" for _, _, q in g) + f": {g[0][2]['s'][:100]}")
    out += ["", "## Near-duplicates (review)", ""]
    for b, r, x, y, j in near:
        out.append(f"- `{x['id']}` / `{y['id']}` ({b}:{r}, {j:.0%}): {x['s'][:90]} | {y['s'][:90]}")
    open("data/merge-report.md", "w").write("\n".join(out) + "\n")
    # the extra copies (not where the keys conflict): the app leaves them out of daily sessions, keeps them in sections
    skip = {q["id"]: g[0][2]["id"] for g in ex_groups if g not in conflicts for _, _, q in g[1:]}
    json.dump(skip, open(f"{A}/dups.json", "w"), separators=(",", ":"))
    print("\n".join(out[5:19]))


if __name__ == "__main__":
    main()
