"""MCQ tactics guide: export one data pack per syllabus section, group them into helper jobs, and check outputs.
    python3 tools/tactics_jobs.py export          -> data/tactics/packs/<g>-<section>.json, data/tactics/jobs.json
    python3 tools/tactics_jobs.py check [<g>-<section> ...]   (default: every pack with an output)"""
import collections, json, os, re, sqlite3, sys

con = sqlite3.connect("data/pyqdecode/pyq.db")
con.row_factory = sqlite3.Row
os.makedirs("data/tactics/packs", exist_ok=True); os.makedirs("data/tactics/out", exist_ok=True)


def sec_of(g, leaf):
    return leaf.split("/")[0] if g == "g1" else ".".join(leaf.split("/")[0].split(".")[:2])


def titles(g):
    if g == "g1":
        d = json.load(open("data/g1syl/leaves.json"))
        return {i["code"]: f"{i['part']} › {i['code']}: {i['text']}" for i in d["items"]}, {l["leaf"]: l["text"] for l in d["leaves"]}
    T, L, part = {}, {}, ""
    for line in open("data/g2syl/leaves.md"):
        if line.startswith("## "):
            part = line[3:].strip()
        elif line.startswith("### "):
            c, t = line[4:].strip().split(" ", 1); T[c] = f"{part} › {c} {t}"
        else:
            m = re.match(r"\s*-?\s*([PM]\d[A-Z]?(?:\.\d+)+(?:/\d+)?):\s*(.+)", line)
            if m:
                L[m.group(1)] = m.group(2).strip()
    return T, L


def export():
    jobs = []
    for g, exam, col in (("g1", "Group 1", "g1_leaves"), ("g2", "Group 2", "g2_leaves")):
        T, LV = titles(g)
        stats = json.load(open(f"data/pyqdecode/stats_{g}.json"))
        packs = collections.defaultdict(lambda: {"questions": [], "related": []})
        for q in con.execute("""SELECT q.*, p.year, p.stage FROM question q JOIN paper p ON p.id=q.paper_id WHERE p.exam=? AND q.analysed IS NOT NULL
                ORDER BY p.year, q.id""", (exam,)):
            sts = [{"l": s["label"], "t": s["text"], "v": s["truth"], "m": s["mechanism"], "d": s["decisive_phrase"], "fact": s["true_fact"]}
                   for s in con.execute("SELECT * FROM statement WHERE question_id=? ORDER BY rowid", (q["id"],))]
            rec = json.loads(q["reconstruction"] or "{}")
            packs[sec_of(g, q["leaf_code"])]["questions"].append({
                "id": q["id"], "year": q["year"], "stage": q["stage"], "leaf": q["leaf_code"], "format": q["format"], "stem": q["text_original"],
                "options": json.loads(q["options_json"]) if q["options_json"] else None, "key": q["key_text"], "deleted": q["deleted"],
                "core_fact": q["core_fact"], "statements": sts, "rule": rec.get("micro_topic_rule"), "key_note": q["key_note"] or ""})
        for r in con.execute(f"""SELECT q.text_original, q.key_text, q.{col} lv, p.exam, p.title FROM question q JOIN paper p ON p.id=q.paper_id
                WHERE q.paper_id LIKE 'app:%'"""):
            lv = json.loads(r["lv"] or "[]")
            if lv and r["exam"] in (exam, "Other APPSC exam"):
                packs[sec_of(g, lv[0])]["related"].append(f"{r['text_original'][:200]} → {r['key_text']} [{'same exam' if r['exam'] == exam else r['title'][:40]}]")
        cov = collections.defaultdict(list)
        for r in stats["coverage"]:
            cov[sec_of(g, r["leaf"])].append({"leaf": r["leaf"], "wording": r["official_wording"], "official_Q": r["official_Q"],
                                              "years": r["years_list"], "recurrence": r["recurrence"]})
        for sec in sorted(set(packs) | set(cov)):
            if sec not in cov:  # app-bank questions outside the syllabus (code X)
                continue
            p = packs[sec]
            rel = p["related"]
            out = {"exam": exam, "section": sec, "title": T.get(sec, sec), "syllabus_leaves": cov.get(sec, []),
                   "official_questions": p["questions"], "related_count": len(rel), "related_sample": rel[:80]}
            json.dump(out, open(f"data/tactics/packs/{g}-{sec}.json", "w"), ensure_ascii=False, indent=0)
            jobs.append((f"{g}-{sec}", len(p["questions"])))
    json.dump(jobs, open("data/tactics/jobs.json", "w"), indent=0)
    print(len(jobs), "packs;", sum(n for _, n in jobs), "questions")


REQ = ["section", "overview", "possibility", "traps", "techniques", "confusions", "anchors", "checklist"]


def check(names):
    names = names or [f[:-5] for f in sorted(os.listdir("data/tactics/out")) if f.endswith(".json")]
    bad = 0
    for n in names:
        pk = json.load(open(f"data/tactics/packs/{n}.json"))
        ids = {q["id"] for q in pk["official_questions"]}
        try:
            o = json.load(open(f"data/tactics/out/{n}.json"))
        except Exception as e:
            print(n, "MISSING/INVALID", e); bad += 1; continue
        pr = [k for k in REQ if k not in o]
        cites = re.findall(r"\[([^\[\]\s]+#[^\[\]\s]+)\]", json.dumps(o, ensure_ascii=False))
        wrong = [c for c in cites if c not in ids]
        if pk["official_questions"]:
            if len(o.get("traps", [])) < 1 or len(o.get("techniques", [])) < 1:
                pr.append("needs ≥1 trap and ≥1 technique")
            for t in o.get("traps", []) + o.get("techniques", []):
                if not re.search(r"\[[^\[\]\s]+#[^\[\]\s]+\]", json.dumps(t, ensure_ascii=False)):
                    pr.append(f"no PYQ citation: {str(t)[:60]}")
        if re.search(r"\b(will (definitely|surely) (come|appear|be asked)|guaranteed to (come|appear|be asked)|sure[- ]shot)\b", json.dumps(o), re.I):
            pr.append("prediction wording")
        if wrong:
            pr.append(f"unknown PYQ ids {wrong[:3]}")
        bad += bool(pr)
        print(n, "ok" if not pr else pr[:6])
    print("problems:", bad)


if __name__ == "__main__":
    export() if sys.argv[1] == "export" else check(sys.argv[2:])
