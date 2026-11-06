"""Checks a unit written to the blueprint (data/blueprint/out/<unit>.md): the format, the three closing sections,
the word budget of its tier, and that COVERAGE names every keyword and only real sections.

    python3 tools/blueprint_check.py <unit> [...]
"""
import re
import sys

BUDGET = {"CORE": 2000, "HIGH": 1350, "MED": 850, "LOW": 480}


def check(u):
    src = open(f"data/blueprint/src/{u}.md").read()
    spec = src.split("\n# NOTES OF APP TOPIC")[0]
    tier = re.search(r"\*\*Tier:\*\* (\w+)", spec).group(1)
    kw = len(re.findall(r"^\s+\d+\. ", spec.split("**Keywords:**")[1].split("- **Latest")[0], re.M))
    t = open(f"data/blueprint/out/{u}.md").read()
    p = []
    if not t.startswith(f"## {u} | "):
        p.append(f"must start with '## {u} | TITLE'")
    secs = re.findall(r"^### (\d+)\. (.+)$", t, re.M)
    nums = [int(n) for n, _ in secs]
    if nums != list(range(1, len(nums) + 1)):
        p.append(f"sections not numbered 1..n: {nums}")
    titles = [s.upper() for _, s in secs]
    if len(titles) < 3 or not titles[-3].startswith("NUMBER GAME") or "PREVIOUS YEAR" not in titles[-2] or "TRAPS" not in titles[-1]:
        p.append("the last three sections must be NUMBER GAME AND QUICK REVISION, APPSC PREVIOUS YEAR QUESTIONS, HIGH-PROBABILITY MCQ TRAPS")
    if "FIRST / LAST / SPECIAL FACTS" not in t:
        p.append("missing '#### FIRST / LAST / SPECIAL FACTS'")
    if "!BOX VERY IMPORTANT" not in t:
        p.append("missing '!BOX VERY IMPORTANT' in the traps section")
    if re.search(r"\b(APP notes|other notes|the app's notes|sources say)\b", t, re.I):
        p.append("never mention where a fact came from")
    if re.search(r"\[(GK|Prep|ROCKET|CA)\]|Not in your sources", t):
        p.append("provenance tags are not allowed")
    if not re.search(r"^WEB: \d+$", t, re.M):
        p.append("missing the 'WEB: <n>' line after COVERAGE")
    body = t.split("\nCOVERAGE:")[0]
    w = len(re.sub(r"[|#*!-]", " ", body).split())
    b = BUDGET.get(tier)
    if b and not (0.85 * b <= w <= 1.5 * b):
        p.append(f"{w} words; {tier} budget ~{b} (0.85x to 1.5x)")
    cov = re.search(r"^COVERAGE: (.+)$", t, re.M)
    if not cov:
        p.append("missing COVERAGE line")
    else:
        got = set()
        for part in cov.group(1).split(";"):
            if ">" in part:
                k, where = part.split(">", 1)
                k = k.strip()
                if k.isdigit():
                    got.add(int(k))
                for s in re.findall(r"\d+", where.split(".")[0] if "." not in where else where):
                    pass
        miss = sorted(set(range(1, kw + 1)) - got)
        if miss:
            p.append(f"COVERAGE misses keywords {miss}")
    print(f"{u}: {tier}, {kw} keywords, {len(secs)} sections, {w} words, problems {len(p)}")
    for x in p:
        print("  -", x)
    return len(p)


if __name__ == "__main__":
    sys.exit(1 if sum(check(u) for u in sys.argv[1:]) else 0)
