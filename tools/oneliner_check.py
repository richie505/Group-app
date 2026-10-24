"""Checks one-liner answers: python3 tools/oneliner_check.py <book> <NNN> (tools/oneliner_guide.md).
Prints PASS, or FAIL with what to fix."""
import json, re, sys

book, n = sys.argv[1], sys.argv[2]
d = f"work/oneliner/b{book}"
ids = re.findall(r"^## Q (\S+) \|", open(f"{d}/in_{n}.md").read(), re.M)
BAN = re.compile(r"(?i)\b(statements?|consider the following|which of the following pairs|assertion|reason \(r\)|list[- ]?i\b|"
                 r"correctly matched|all of the above|none of the above)\b")
OPT = re.compile(r"(?i)^\s*(only\s+(one|two|three|four)|all\s+(four|three)|both\b|neither\b|[1-6](\s*(,|and|&)\s*[1-6])+(\s*only)?$|"
                 r"[1-6]\s+only$|[a-f]\s*[-–—]\s*[ivx]+\b|\(\d\))")
errs, seen, got, skips = [], set(), {}, 0
try:
    lines = [l for l in open(f"{d}/out_{n}.jsonl") if l.strip()]
except FileNotFoundError:
    print("FAIL: no out file"); sys.exit()
for k, line in enumerate(lines, 1):
    try:
        o = json.loads(line)
    except Exception:
        errs.append(f"line {k}: not JSON"); continue
    q = o.get("q")
    if q not in ids:
        errs.append(f"line {k}: q {q!r} is not an MCQ of this batch"); continue
    got[q] = got.get(q, 0) + 1
    if "skip" in o:
        skips += 1; continue
    s, opts, a = o.get("s", ""), o.get("o"), o.get("a")
    if not isinstance(s, str) or not s.strip() or "\n" in s or len(s) > 200:
        errs.append(f"line {k} ({q}): the question must be one line, up to ~150 characters")
    elif BAN.search(s):
        errs.append(f"line {k} ({q}): not a one-liner question ({BAN.search(s).group(0)!r})")
    if not isinstance(opts, list) or len(opts) != 4 or not all(isinstance(x, str) and x.strip() for x in opts):
        errs.append(f"line {k} ({q}): needs 4 options"); continue
    if len({x.strip().lower() for x in opts}) < 4:
        errs.append(f"line {k} ({q}): options repeat")
    for x in opts:
        if len(x) > 90 or "\n" in x:
            errs.append(f"line {k} ({q}): option too long: {x[:40]!r}…")
        elif OPT.search(x) or BAN.search(x):
            errs.append(f"line {k} ({q}): option is not a plain answer: {x!r}")
    if a not in (0, 1, 2, 3):
        errs.append(f"line {k} ({q}): a must be 0-3")
    key = re.sub(r"\W+", " ", s.lower()).strip()
    if key in seen:
        errs.append(f"line {k} ({q}): same question twice")
    seen.add(key)
missing = [i for i in ids if i not in got]
if missing:
    errs.append(f"no one-liners for {len(missing)} MCQs: " + ", ".join(missing[:10]))
if skips > max(2, len(ids) // 10):
    errs.append(f"{skips} MCQs skipped; skip only when no sound one-liner can be made")
total = sum(got.values()) - skips
if errs:
    print(f"FAIL ({len(errs)}):\n" + "\n".join(errs[:40]))
else:
    print(f"PASS: {len(ids)} MCQs -> {total} one-liners ({skips} skipped)")
