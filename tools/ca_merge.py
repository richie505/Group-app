"""Folding Prep's current-affairs pages into the CA app's pages, topic by topic (guide: tools/ca_merge_guide.md).

    python3 tools/ca_merge.py export <topic> [...]   -> work/camerge/in_<topic>.md
    python3 tools/ca_merge.py check <topic>          -> problems, then "pass" / "FAIL"
    python3 tools/ca_merge.py import <topic> [...]   -> app/src/complete/assets book6 / mcq6 / index (after check)
in_<t>.md:  === TOPIC t | title,  ## S<k> | Prep page,  === CA,  ## C<n> | period · CA page title
out_<t>.md: ## C<n> | title           a CA page with Prep facts added (whole new page)
            ## <title> | from: S2, S5   an overview page made of Prep facts the CA pages lack
            === COVERED: S1, S4         Prep pages whose every fact the CA pages already state
"""
import json, os, re, sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from merge_map import page_md
from restructure_check import problems, BOLD
from structured_md import to_blocks
from notes_fix import plain_cells

A = Path(os.environ.get("MERGE_ASSETS", "app/src/complete/assets"))
W = Path("work/camerge")


def load():
    book = json.load(open(A / "book6.json"))
    rows = [r for u in book["units"] for r in u["rows"]]
    unit_of = [ui for ui, u in enumerate(book["units"]) for _ in u["rows"]]
    return book, rows, unit_of


def topic_rows(rows, unit_of, t):
    """(CA rows of the topic, its Prep-notes row) as global row numbers."""
    mine = [i for i, u in enumerate(unit_of) if u == t]
    prep = [i for i in mine if rows[i]["title"].startswith("Prep notes: ")]
    return [i for i in mine if i not in prep], (prep[0] if prep else None)


def export(t):
    book, rows, unit_of = load()
    ca, pr = topic_rows(rows, unit_of, t)
    if pr is None:
        print(f"topic {t}: already merged")
        return
    parts = [f"=== TOPIC {t} | {book['units'][t]['title']}"]
    parts += [f"## S{k} | {s['t']}\n{page_md(s)}" for k, s in enumerate(rows[pr]["secs"])]
    parts.append("=== CA")
    n = 0
    for i in ca:
        period = rows[i]["title"].split(":")[0]
        for s in rows[i]["secs"]:
            parts.append(f"## C{n} | {period} · {s['t']}\n{page_md(s)}")
            n += 1
    W.mkdir(parents=True, exist_ok=True)
    (W / f"in_{t}.md").write_text("\n\n".join(parts) + "\n")
    print(f"topic {t}: {len(rows[pr]['secs'])} Prep pages, {n} CA pages -> {W}/in_{t}.md")


def sections(text):
    return [(c.partition("\n")[0].strip(), c.partition("\n")[2].strip()) for c in re.split(r"(?m)^## ", text)[1:]]


def parse(t):
    src = (W / f"in_{t}.md").read_text()
    prep_part, _, ca_part = src.partition("\n=== CA")
    S, C = sections(prep_part), sections(ca_part)
    out = (W / f"out_{t}.md").read_text()
    m = re.search(r"(?m)^=== COVERED:(.*)$", out)
    covered = {int(x) for x in re.findall(r"S(\d+)", m.group(1))} if m else set()
    new = sections(re.sub(r"(?m)^=== COVERED:.*$", "", out))
    return S, C, new, covered


def check(t):
    S, C, new, covered = parse(t)
    p = []
    changed, overview = {}, []
    for head, body in new:
        m = re.match(r"C(\d+)\s*\|", head)
        if m:
            k = int(m.group(1))
            if k >= len(C):
                p.append(f"unknown page C{k}")
                continue
            changed[k] = body
            # a CA page keeps all its own facts
            p += [f"C{k}: {x}" for x in problems(C[k][1], body) if not x.startswith("bold terms lost") or len(x) > 0]
        else:
            frm = [int(x) for x in re.findall(r"S(\d+)", head.partition("from:")[2])]
            if not frm:
                p.append(f"overview page without from: {head[:50]}")
            overview.append((head, body, frm))
    used = {k for _, _, f in overview for k in f} | covered
    # a Prep page used only through CA pages is named by nothing: it must be covered or added
    missing = [k for k in range(len(S)) if k not in used and not any(f"S{k}" in h for h, _ in new)]
    # every Prep fact is somewhere in the topic (the changed / untouched CA pages or an overview page)
    final = "\n".join(changed.get(k, C[k][1]) for k in range(len(C))) + "\n" + "\n".join(b for _, b, _ in overview)
    prep_all = "\n".join(b for _, b in S)
    for x in problems(prep_all, final):
        if x.startswith("bold terms lost"):
            toks = set(re.findall(r"[a-z0-9]+", final.lower()))
            lost = [b for b in BOLD.findall(prep_all) if not set(re.findall(r"[a-z0-9]+", b.lower())) <= toks]
            if len(lost) > max(1, len(set(BOLD.findall(prep_all))) // 15):
                p.append(f"Prep bold terms lost ({len(lost)}): " + "; ".join(sorted(set(lost))[:6]))
        else:
            p.append("Prep " + x)
    for h, b in new:
        try:
            if not to_blocks(b, []):
                p.append(f"empty page: {h[:40]}")
        except Exception as e:
            p.append(f"page does not parse ({h[:40]}): {e}")
    if missing:
        p.append("Prep pages neither covered nor used: " + ", ".join(f"S{k}" for k in missing))
    return p, changed, overview


def do_import(t):
    p, changed, overview = check(t)
    if p:
        print(f"topic {t}: check fails, not imported")
        return
    book, rows, unit_of = load()
    ca, pr = topic_rows(rows, unit_of, t)
    flat = [(i, j) for i in ca for j in range(len(rows[i]["secs"]))]
    for k, body in changed.items():
        i, j = flat[k]
        rows[i]["secs"][j]["b"] = [plain_cells(b) for b in to_blocks(body, [])]
    mcq = json.load(open(A / "mcq6.json"))
    prep_secs = rows[pr]["secs"]
    if overview:
        new_secs = []
        for head, body, frm in overview:
            new_secs.append({"t": head.partition(" | ")[0].strip(), "badges": [], "p": prep_secs[frm[0]].get("p", 0),
                             "b": [plain_cells(b) for b in to_blocks(body, [])], "o": prep_secs[frm[0]].get("o", "")})
        # Prep's MCQs: to the overview page that took most of their page, else the first overview page
        where = {}
        for j, (_, _, frm) in enumerate(overview):
            for k in frm:
                where.setdefault(k, j)
        qs, subs = mcq["rows"].get(str(pr), []), mcq["subs"].get(str(pr), [])
        mcq["subs"][str(pr)] = [where.get(s, 0) for s in subs]
        rows[pr]["secs"] = new_secs
        rows[pr]["title"] = rows[pr]["title"].replace("Prep notes: ", "Overview and data: ")
    else:
        # nothing left of Prep's pages: their MCQs go to the topic's newest section (re-filed by the MCQ trim)
        qs, subs = mcq["rows"].pop(str(pr), []), mcq["subs"].pop(str(pr), [])
        mcq["rows"].setdefault(str(ca[0]), []).extend(qs)
        mcq["subs"].setdefault(str(ca[0]), []).extend([0] * len(qs))
        # drop the empty section, renumbering the later ones
        u = book["units"][t]
        u["rows"] = [r for r in u["rows"] if r is not rows[pr]]
        for key in ("rows", "subs"):
            mcq[key] = {str(int(r) - (int(r) > pr)): v for r, v in mcq[key].items()}
    dump = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":"))
    (A / "book6.json").write_text(dump(book))
    (A / "mcq6.json").write_text(dump(mcq))
    os.system(f"{sys.executable} tools/ca_index.py")
    print(f"topic {t}: {len(changed)} CA pages enriched, {len(overview)} overview pages")


if __name__ == "__main__":
    cmd, topics = sys.argv[1], [int(x) for x in sys.argv[2:]]
    for t in topics:
        if cmd == "export":
            export(t)
        elif cmd == "check":
            p, changed, overview = check(t)
            for x in p:
                print(f"topic {t}: {x}")
            print(f"topic {t}: {'FAIL' if p else 'pass'} ({len(changed)} CA pages enriched, {len(overview)} overview pages)")
        elif cmd == "import":
            do_import(t)
