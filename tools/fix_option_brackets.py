"""Code options without brackets: "(1), (2), (3)" -> "1, 2 and 3", "(3) and (4) only" -> "3 and 4 only",
"1-(d),2-(a)" -> "1-d, 2-a". Where a question's options change, its "(1) ..." statements become "1. ...".
Every MCQ of both apps (only the way the codes are written changes).

    python3 tools/fix_option_brackets.py
"""
import json, re

M = r"\((?:[1-9]|[a-hA-H]|i{1,3}|iv|vi{0,3}|I{1,3}|IV|VI{0,3})\)"
LIST = re.compile(rf"^\s*{M}(?:\s*(?:,|and|&)\s*{M})*(\s+only)?\s*\.?$")
PAIRS = re.compile(r"^\s*\w{1,3}\s*[-–]\s*\(\w{1,3}\)(?:\s*[,.;]?\s*\w{1,3}\s*[-–]\s*\(\w{1,3}\))+\s*$")


def plain(o):
    if LIST.match(o):
        only = " only" if re.search(r"\bonly\s*\.?$", o) else ""
        marks = re.findall(r"\((\w{1,4})\)", o)
        return (marks[0] if len(marks) == 1 else ", ".join(marks[:-1]) + " and " + marks[-1]) + only
    if PAIRS.match(o):
        pairs = re.findall(r"(\w{1,3})\s*[-–]\s*\((\w{1,3})\)", o)
        return ", ".join(f"{a}-{b}" for a, b in pairs)
    return o


def main():
    for app in ("main", "complete"):
        n = 0
        for b in range(1, 7):
            p = f"app/src/{app}/assets/mcq{b}.json"
            m = json.load(open(p))
            for qs in m["rows"].values():
                for q in qs:
                    new = [plain(o) for o in q["o"]]
                    if new != q["o"] and len(set(new)) == len(new):
                        q["s"] = re.sub(r"(?m)^\((\w{1,4})\)\s*", r"\1. ", q["s"])
                        q["o"], n = new, n + 1
            json.dump(m, open(p, "w"), ensure_ascii=False, separators=(",", ":"))
        print(app, "questions with bracketed codes rewritten:", n)


if __name__ == "__main__":
    main()
