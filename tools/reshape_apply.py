"""Puts the rewritten MCQs (data/reshape/out/*.json, from tools/reshape_plan.py packets) into APPSC Complete (only).

    python3 tools/reshape_apply.py

An MCQ keeps its id (so its place, progress and links stay); its stem, options, key and explanation are replaced, the
old structured explanation (which talked about the old statements and options) is dropped, and "rs" records the new
shape. A rewrite is used only when it is a sound four-option MCQ with a key. Re-running it is harmless.
"""
import glob, json, re

APPS = ("app/src/complete/assets",)  # APPSC Complete only: the Prep app keeps its MCQs as they are


def num(x):
    """An option that is just a number / year / percentage (with a unit word at most)."""
    m = re.fullmatch(r"[^\d]{0,4}?([\d,]+(?:\.\d+)?)\s*(?:%|per ?cent|crore|lakh|million|billion|km|kms|sq ?km|AD|BC|CE|BCE|years?|times|days?)?\.?", x.strip(), re.I)
    if not m:
        return None
    try:
        return float(m.group(1).replace(",", ""))
    except ValueError:
        return None


# where APPSC keys its answer (data/pyq/secrets.json): ordinary questions, and NOT / INCORRECT questions
POS = [0.27, 0.27, 0.25, 0.21]
POS_NOT = [0.22, 0.22, 0.21, 0.35]


def movable(r, o):
    """Options in no natural order: not codes, not assertion-reason, no 'All / None / Both' option."""
    # decided by what the options are (agents' shape labels are not always right)
    if re.search(r"(?i)\bassertion\b|\breason\b \(R\)|chronological|arrange|correct order|sequence", r.get("s", "")):
        return False
    code = (r"(?i)^(?:all|none|both|neither|only)\b|of the above|\bonly$|^\(?[1-6a-divx]+\)?\s*(?:only|,|and|-|–)"
            r"|^\(?[A-D]\)?\s*[-–]\s*\(?[1-4ivx]+\)?|\bA\b.*\bR\b")
    return not any(re.search(code, x.strip()) for x in o)


def place_key(qid, o, a, shape, stem):
    """Move the key to a slot drawn (deterministically, from the id) from APPSC's own key positions."""
    import hashlib
    neg = shape.startswith("NOT") or re.search(r"\b(?:NOT|INCORRECT|INCORRECTLY|EXCEPT)\b", stem)
    w = POS_NOT if neg else POS
    u = int(hashlib.md5(qid.encode()).hexdigest()[:8], 16) / 0xFFFFFFFF
    slot, acc = 3, 0.0
    for i, p in enumerate(w):
        acc += p
        if u < acc:
            slot = i
            break
    o = list(o)
    o[a], o[slot] = o[slot], o[a]
    return o, slot


def swap_two(qid, s, o, a, x):
    """Two-statement sets lean to '1 only' (writers put the true fact first). For about 40% of those, swap statements
    1 and 2 (and every 'statement 1/2' in the explanation) so the key becomes '2 only'. Returns (s, x, a) or None."""
    import hashlib
    if [t.lower() for t in o[:2]] != ["1 only", "2 only"] or a != 0:
        return None
    if int(hashlib.md5((qid + "#2").encode()).hexdigest()[:8], 16) % 10 >= 4:
        return None
    m = re.fullmatch(r"(?s)(.*?\n)1\.\s*(.+?)\n2\.\s*(.+?)(\n.*)", s)
    if not m or re.search(r"\n3\.", s):
        return None
    s2 = f"{m.group(1)}1. {m.group(3).strip()}\n2. {m.group(2).strip()}{m.group(4)}"
    if re.search(r"(?i)\b(?:first|second)\b(?!\s+(?:largest|highest|most|time))", x):
        return None  # explanation says "the first/second statement": leave the set as it is
    flip = lambda k: k.group(1) + ("2" if k.group(2) == "1" else "1")
    x2 = re.sub(r"(?i)\b(statement\s*\(?)([12])\b(?!\s*(?:and|&|,)\s*[12])", flip, x)
    x2 = re.sub(r"(?i)(\b|\()([12])(\)?\s+only\b)", lambda k: k.group(1) + ("2" if k.group(2) == "1" else "1") + k.group(3), x2)
    return s2, x2, 1


# writers' notes about the rewrite itself, sometimes left in brackets in the explanation
NOTE = re.compile(r"\s*\((?:TARGET|Nearest honest|Original|The original|A sequence question|No dated|No dates|Match grid|"
                  r"Rewritten|Restyled|Written as)[^()]*\)", re.I)


def clean(x):
    x0, x = x, re.sub(r"(?:^|(?<=[.;] ))The original key [^.]*\.\s*", "", NOTE.sub("", x))
    x = re.sub(r"[ \t]{2,}", " ", x).strip()
    return x or re.sub(r"^The original key marks", "The incorrect statement is", x0.strip())


def valid(r):
    o = r.get("o")
    return (isinstance(r.get("s"), str) and len(r["s"].strip()) >= 10 and isinstance(o, list) and len(o) == 4
            and all(isinstance(x, str) and x.strip() for x in o) and len({x.strip().lower() for x in o}) == 4
            and isinstance(r.get("a"), int) and 0 <= r["a"] <= 3)


def main():
    new, bad = {}, 0
    for f in sorted(f for f in glob.glob("data/reshape/out/*.json") if re.fullmatch(r"\d+\.json", f.rsplit("/", 1)[-1])):
        try:
            d = json.load(open(f))
        except ValueError:
            print("unreadable", f)
            continue
        for i, r in d.items():
            if r.get("same"):
                continue
            if valid(r):
                new[i] = r
            else:
                bad += 1
    done = {}
    for A in APPS:
        n = 0
        for b in range(1, 7):
            p = f"{A}/mcq{b}.json"
            m = json.load(open(p))
            for qs in m["rows"].values():
                for q in qs:
                    r = new.get(q["id"])
                    if not r:
                        continue
                    o, a = [x.strip() for x in r["o"]], r["a"]
                    nums = [num(x) for x in o]
                    if all(v is not None for v in nums) and len(set(nums)) == 4:  # APPSC prints numbers and years in order
                        order = sorted(range(4), key=lambda k: nums[k])
                        o, a = [o[k] for k in order], order.index(a)
                    elif movable(r, o):
                        o, a = place_key(q["id"], o, a, r.get("shape", ""), r["s"])
                    s, x = clean(r["s"].strip()), clean(r.get("x") or "")
                    sw = swap_two(q["id"], s, o, a, x)
                    if sw:
                        s, x, a = sw
                    q["s"], q["o"], q["a"] = s, o, a
                    q["x"] = x
                    for k in ("xs", "tq", "t"):
                        q.pop(k, None)
                    # extra notes stay only if they do not point at the old options / statements
                    q["xa"] = [x for x in q.get("xa", []) if not re.search(r"(?i)option\s*\(?\d|\bstatements?\s*\d|\(\d\)", x)]
                    if not q["xa"]:
                        q.pop("xa")
                    q["rs"] = r.get("shape", "")[:20]
                    n += 1
            json.dump(m, open(p, "w"), ensure_ascii=False, separators=(",", ":"))
        done[A] = n
    print(f"rewrites: {len(new)} usable, {bad} rejected; applied {done}")


if __name__ == "__main__":
    main()
