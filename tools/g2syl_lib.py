"""Group 2 built on the official APPSC syllabus (27-04-2023) - the data tools/group2_build.py uses:

- data/g2syl/tree.json, leaves.json: the official tree and its 328 leaves (tools/g2syl_tree.py)
- data/g2syl/secmap.json: each section (by APPSC Complete row) -> its official leaves (tools/g2syl_secmap.py)
- data/g2syl/sub-out-*.jsonl: each subsection of a many-leaf section -> one leaf or "beyond" (MCQs take it)
- data/g2syl/depth-out-*.jsonl: notes written where a leaf was thin or missing (added as subsections)
- data/g2papers/*.json: full official Group 2 papers
Keys "b:r" are APPSC Complete rows unless named g2.
"""
import glob, json, os, sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(__file__))
from g2syl_source import tier, year

J = lambda p: json.load(open(p))
TREE = J("data/g2syl/tree.json")
LEAVES = J("data/g2syl/leaves.json")
LEAF = {x["leaf"]: x for x in LEAVES}
ORDER = {x["leaf"]: i for i, x in enumerate(LEAVES)}
SECMAP = J("data/g2syl/secmap.json")
SUBJ = {s["code"]: s for s in TREE["subjects"]}
SUBJ_ORDER = [s["code"] for s in TREE["subjects"]]
subject_of = lambda leaf: leaf.split(".")[0]
stage_of = lambda leaf: "P" if leaf.startswith("P") else "M"

# rows of the section map were taken from the Group 2 rows of the time; sub-out uses the same Complete keys
SUBLEAF = {}  # "b:r" (Complete) -> {sub index: leaf | "beyond"}
for f in sorted(glob.glob("data/g2syl/sub-out-*.jsonl")):
    for l in open(f):
        if l.strip():
            o = json.loads(l)
            SUBLEAF[o["key"]] = {int(i): v for i, v in o["subs"].items()}


def leaves_of(key):
    """All official leaves a section serves: its own and its subsections' (main one first)."""
    own = list(SECMAP.get(key, {}).get("leaves", []))
    for v in SUBLEAF.get(key, {}).values():
        if v != "beyond" and v not in own:
            own.append(v)
    return own


def question_leaf(key, sub):
    """The leaf a section's MCQ in subsection [sub] is asked under ("x" = beyond the syllabus)."""
    s = SUBLEAF.get(key)
    if s is not None and sub in s:
        return "x" if s[sub] == "beyond" else s[sub]
    own = SECMAP.get(key, {}).get("leaves", [])
    return own[0] if own else "x"


ADDS = defaultdict(list)  # "b:r" (Complete) -> [(leaf, title, md)]: notes written for thin / missing leaves
_RM = J("data/g2syl/rowmap-at-mapping.json")
for f in sorted(glob.glob("data/g2syl/depth-out-*.jsonl")):
    for l in open(f):
        if l.strip():
            o = json.loads(l)
            a = o.get("add")
            if a:
                ADDS["%d:%d" % tuple(_RM[a["g2"]])].append((o["leaf"], a["title"], a["md"]))


def added_secs(key):
    """The added notes of a section as subsections (the app's blocks)."""
    from structured_md import to_blocks
    out = []
    for leaf, title, md in ADDS.get(key, []):
        out.append({"t": title, "badges": [], "b": to_blocks(md, []), "leaf": leaf})
    return out


HOME = {1: ("P1", "M1A"), 2: ("M1B", "P3"), 3: ("M2A",), 4: ("P2",), 5: ("M2B",), 6: ("P4",)}


def home(b, leaves):
    """The official subject a section is filed under in its book (its book's own subject first), "X" beyond."""
    subs = [subject_of(c) for c in leaves]
    for h in HOME[b]:
        if h in subs:
            return h
    return subs[0] if subs else "X"


def priorities(qs_by_leaf):
    """Leaf -> HIGH / MED / LIGHT within its subject, from the PYQs asked under it: a Group 2 PYQ since 2017 counts 4,
    an older Group 2 PYQ 3, another APPSC paper 1, UPSC 0.5, other exams 0.2; top 30% HIGH, next 40% MED."""
    score = {}
    for leaf in LEAF:
        s = 0.0
        for q in qs_by_leaf.get(leaf, []):
            if not q["id"].startswith("y"):
                continue
            t = tier(q)
            s += {"g2": 4 if year(q) >= 2017 else 3, "ap": 1, "up": 0.5}.get(t, 0.2)
        score[leaf] = s
    out = {}
    for sc in SUBJ_ORDER:
        ls = sorted([l for l in LEAF if subject_of(l) == sc], key=lambda l: -score[l])
        for i, l in enumerate(ls):
            out[l] = "HIGH" if i < 0.3 * len(ls) and score[l] > 0 else "MED" if i < 0.7 * len(ls) and score[l] > 0 else "LIGHT"
    return out, score


def syllabus_json(rows_by_leaf, qs_by_leaf, pri, papers):
    subjects = []
    for s in TREE["subjects"]:
        units = []
        for u in s["units"]:
            phrases = []
            for p in u["phrases"]:
                codes = [f"{p['code']}/{i}" for i in range(1, len(p["points"]) + 1)] or [p["code"]]
                lv = []
                for c in codes:
                    qs = qs_by_leaf.get(c, [])
                    py = [q for q in qs if q["id"].startswith("y")]
                    g2 = [q for q in py if tier(q) == "g2"]
                    lv.append({"code": c, "text": LEAF[c]["text"], "rows": rows_by_leaf.get(c, []), "q": len(qs), "pyq": len(py),
                               "g2": len(g2), "years": sorted(year(q) for q in g2 if year(q)), "pri": pri[c]})
                phrases.append({"code": p["code"], "text": p["text"], "leaves": lv})
            units.append({"code": u["code"], "title": u["title"], "phrases": phrases})
        subjects.append({k: s[k] for k in ("code", "stage", "paper", "title", "marks")} | {"units": units})
    return {"source": TREE["source"], "subjects": subjects, "papers": papers}
