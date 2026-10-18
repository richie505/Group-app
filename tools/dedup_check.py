"""Checks dedup decisions (guide: tools/dedup_guide.md).

    python3 tools/dedup_check.py NNN
out_NNN.md, one block per cluster of in_NNN.md:
    C<n> all                          (not real repeats: keep every unit)
    C<n> keep <uid>[, <uid> ...]      (keep these, drop the other units of the cluster)
    N <uid>                           (optional, after a keep line: the kept unit's new text, merged)
    <markdown lines, as in the input>
Rules checked: every cluster decided once; kept/new uids belong to the cluster; a new text keeps the unit's form
(a table row stays one "| ... |" row with the same number of cells; a bullet group starts "- "); every number
and **bold** term of a dropped unit, and of the kept unit itself, is in the cluster's kept text.
"""
import os, re, sys

D = os.environ.get("DEDUP_DIR", "work/dedup")


def parse_in(t):
    out = {}
    for block in re.split(r"(?m)^=== ", t)[1:]:
        name, _, rest = block.partition("\n")
        units = {}
        for u in re.split(r"(?m)^(?=U \S+ \| )", rest):
            m = re.match(r"U (\S+) \| [^\n]*\n(.*)", u, re.S)
            if m:
                units[m.group(1)] = m.group(2).strip()
        out[name.strip()] = units
    return out


def parse_out(t):
    dec, cur, new, errs = {}, None, None, []
    for line in t.splitlines():
        m = re.match(r"(C\d+) (all|keep (.+))$", line.strip())
        if m:
            cur = m.group(1)
            if cur in dec:
                errs.append(f"{cur}: decided twice")
            dec[cur] = {"all": m.group(2) == "all",
                        "keep": [u.strip() for u in (m.group(3) or "").split(",") if u.strip()], "new": {}}
            new = None
            continue
        m = re.match(r"N (\S+)$", line.strip())
        if m and cur:
            new = m.group(1)
            dec[cur]["new"][new] = []
            continue
        if new and line.strip():
            dec[cur]["new"][new].append(line.rstrip())
        elif line.strip():
            errs.append(f"stray line: {line[:60]}")
    return dec, errs


def table_cells(md):
    rows = [l for l in md.splitlines() if l.startswith("|")]
    return rows[-1].strip("|").split(" | ") if rows else []


def facts(md):
    body = md.splitlines()[-1] if md.startswith("|") else md   # table rows: the header is context, not a fact
    nums = set(re.findall(r"\d+(?:\.\d+)?", body.replace(",", "")))
    bold = {b.strip().lower() for b in re.findall(r"\*\*(.+?)\*\*", body)}
    return nums, bold


def check(units, d):
    errs = []
    if d["all"]:
        return errs
    keep = d["keep"]
    if not keep:
        return ["no unit kept"]
    for u in keep + list(d["new"]):
        if u not in units:
            errs.append(f"{u} is not in this cluster")
    if errs:
        return errs
    final = {}
    for u in keep:
        if u in d["new"]:
            lines = d["new"][u]
            if "." in u.split(":")[-1]:
                if len(lines) != 1 or not lines[0].startswith("|"):
                    errs.append(f"{u}: a table row must stay one '| ... |' line")
                elif len(lines[0].strip().strip("|").split(" | ")) != len(table_cells(units[u])):
                    errs.append(f"{u}: table row needs {len(table_cells(units[u]))} cells")
                final[u] = units[u].splitlines()[0] + "\n" + lines[0] if lines else ""
            else:
                if not lines or not (lines[0].startswith("- ") or lines[0].startswith("> ")):
                    errs.append(f"{u}: new text must start with '- ' (or '> ' for an exam line)")
                final[u] = "\n".join(lines)
        else:
            final[u] = units[u]
    for u in d["new"]:
        if u not in keep:
            errs.append(f"{u}: new text for a unit that is not kept")
    kn, kb = set(), set()
    for md in final.values():
        n, b = facts(md)
        kn |= n
        kb |= b
    ktext = " ".join(final.values()).lower().replace("**", "")
    for u, md in units.items():
        n, b = facts(md)
        miss_n = n - kn
        miss_b = {x for x in b - kb if x not in ktext}
        if miss_n or miss_b:
            what = ("kept " if u in keep else "dropped ") + u
            errs.append(f"{what} loses {sorted(miss_n)[:5]} {sorted(miss_b)[:4]}")
    return errs


if __name__ == "__main__":
    n = sys.argv[1]
    src = parse_in(open(f"{D}/in_{n}.md").read())
    p = f"{D}/out_{n}.md"
    dec, errs = parse_out(open(p).read()) if os.path.exists(p) else ({}, [])
    for e in errs:
        print(f"{n}: {e}")
    ok = 0
    for c, units in src.items():
        if c not in dec:
            print(f"{n} {c}: missing")
            continue
        e = check(units, dec[c])
        for x in e:
            print(f"{n} {c}: {x}")
        ok += not e
    for c in dec:
        if c not in src:
            print(f"{n} {c}: not in the input")
    print(f"{ok}/{len(src)} clusters pass")
