"""Outdated MCQs -> the latest answer (data/outdated/job-*.out.jsonl, each fact checked as of Nov 2026).

  rekey: the latest answer is an option -> keyed;  add: appended as an option and keyed (tag "added");
  stem:  the stem / options updated (old district, "present ..." wording);  ok: not outdated -> tag dropped.
Each changed MCQ gets the tag "updated" (shown as "Updated to latest") and an explanation line saying what the
answer was when the paper was set. Idempotent: run after every notes apply.

    python3 tools/outdated_apply.py [assets dir ...]
"""
import json, glob, sys

MARK = "Updated to the latest (Nov 2026): "


def load():
    d = {}
    # job outputs first, then the source-check pass (verify-*.jsonl) which overrides them
    for f in sorted(glob.glob("data/outdated/job-*.out.jsonl")) + sorted(glob.glob("data/outdated/verify-*.jsonl")):
        for l in open(f):
            if l.strip():
                o = json.loads(l); d[o["id"]] = o
    return d


def fix(q, u):
    act = u.get("action")
    tg = [t for t in q.get("tg", []) if t != "outdated"]
    if act == "ok":
        if tg: q["tg"] = tg
        else: q.pop("tg", None)
        return False
    if (q.get("x") or "").startswith(MARK):
        return False  # done already
    if act == "rekey" and isinstance(u.get("index"), int) and 0 <= u["index"] < len(q["o"]):
        q["a"] = u["index"]
    elif act == "add" and u.get("option"):
        if u["option"] in q["o"]: q["a"] = q["o"].index(u["option"])
        else: q["o"] = q["o"] + [u["option"]]; q["a"] = len(q["o"]) - 1
        if "added" not in tg: tg.append("added")
    elif act == "stem" and u.get("stem"):
        q["s"] = u["stem"]
        if isinstance(u.get("options"), list) and len(u["options"]) == len(q["o"]): q["o"] = u["options"]
    else:
        return False
    tg.append("updated")
    q["tg"] = tg
    then = (u.get("then") or "").strip()
    line = MARK + (u.get("latest") or "").strip()
    if then and act in ("rekey", "add"): line += f" (When this paper was set, the answer was: {then}.)"
    if u.get("source"): line += f" Source: {u['source']}"
    q["x"] = line + "\n" + (q.get("x") or "")
    return True


if __name__ == "__main__":
    upd = load()
    for A in sys.argv[1:] or ["app/src/complete/assets"]:
        n = 0
        for b in range(1, 7):
            p = f"{A}/mcq{b}.json"; m = json.load(open(p))
            for v in m["rows"].values():
                for q in v:
                    if q["id"] in upd and fix(q, upd[q["id"]]): n += 1
            open(p, "w").write(json.dumps(m, ensure_ascii=False, separators=(",", ":")))
        print(A, "updated", n, "of", len(upd))
