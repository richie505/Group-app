"""Turns an APPSC Complete backup into one for APPSC One-liners, so the progress carries over.

    python3 tools/backup_to_oneliner.py <complete backup.json> <out.json> [one-liners backup.json]

Read marks, bookmarks, own notes, last page, study days and time: as they are; on restore the One-liners app moves
them from Complete's pages to each topic's one page (its moved.json and notemoves.json, tools/onepager_app.py: a
topic is read when all its pages were). MCQ answers: a question that is a one-liner in both apps keeps its answer; an MCQ that was rewritten as
one-liners (work/oneliner/b<book>/out_*.jsonl) passes its result to each of them (right stays right; wrong puts
them under "answered wrong" to revise); a seen-only one makes them seen. One-liners already answered in the
One-liners app (its backup, if given) are left out, so a restore never overwrites what was practised there.
"""
import glob, hashlib, json, re, sys
from collections import defaultdict


def norm(t):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", t.lower())).strip()


def qid(s, o):  # as tools/oneliner_import.py
    return "o" + hashlib.sha1((norm(s) + "|" + "|".join(sorted(norm(x) for x in o))).encode()).hexdigest()[:11]


def main():
    B = json.load(open(sys.argv[1]))
    assert B.get("app") == "APPSC Prep backup", "not an APPSC backup"
    own = json.load(open(sys.argv[3])) if len(sys.argv) > 3 else {}
    done_there = {a.rsplit(":", 1)[0] for a in own.get("answers", [])} | set(own.get("seen", []))

    bank = {q["id"] for b in range(1, 7)
            for qs in json.load(open(f"app/src/oneliner/assets/mcq{b}.json"))["rows"].values() for q in qs}
    made = defaultdict(list)  # Complete MCQ id -> its one-liners' ids
    for f in glob.glob("work/oneliner/b*/out_*.jsonl"):
        for line in open(f):
            if line.strip():
                x = json.loads(line)
                if "s" in x and (i := qid(x["s"], x["o"])) in bank:
                    made[x["q"]].append(i)

    def to(i):
        return [i] if i in bank else made.get(i, [])

    answers, carried, same = {}, 0, 0
    for a in B["answers"]:
        i, ok = a.rsplit(":", 1)[0], a.endswith(":1")
        for j in to(i):
            if j in done_there:
                continue
            # one MCQ's result on several one-liners; a wrong anywhere wins
            answers[j] = answers.get(j, True) and ok
            same += j == i
            carried += j != i
    seen = sorted({j for i in B.get("seen", []) for j in to(i)} - set(answers) - done_there)
    missed = sorted({j for i in B.get("missed", []) for j in to(i)} - done_there)

    out = dict(B)
    out.update({
        "answers": sorted(f"{k}:{1 if v else 0}" for k, v in answers.items()),
        "seen": seen,
        "missed": missed,
    })
    json.dump(out, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
    print(f"pages read {len(B['done'])}, bookmarks {len(B['saved'])}, own notes {len(B['added'])}; "
          f"MCQ answers {len(B['answers'])} -> {len(answers)} one-liners ({same} the same question, {carried} made from "
          f"the MCQs answered; {sum(not v for v in answers.values())} to revise), {len(seen)} seen; "
          f"{len(done_there)} already practised in One-liners left as they are")


if __name__ == "__main__":
    main()
