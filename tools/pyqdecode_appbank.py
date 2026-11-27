"""Stage 2d: add the APPSC Group 1 / Group 2 PYQs held in the apps (app/src/complete/assets/mcq*.json, src naming a
APPSC exam) to data/pyqdecode/pyq.db as a SECONDARY tier (Group 1 / 2) or TERTIARY tier (other APPSC exams) (paper ids "app:<src>"), minus questions
already in the official papers. Their keys are the app's (web-checked, not official APPSC documents); questions the
app updated to current facts or repaired keep that tag, because their wording may differ from the original paper.
    python3 tools/pyqdecode_appbank.py"""
import json, re, sqlite3

con = sqlite3.connect("data/pyqdecode/pyq.db")
norm = lambda t: re.sub(r"[^a-z0-9]+", " ", str(t).lower()).strip()
con.execute("DELETE FROM question WHERE paper_id LIKE 'app:%'")
con.execute("DELETE FROM paper WHERE id LIKE 'app:%'")
have = {norm(s)[:90] for (s,) in con.execute("SELECT text_original FROM question")}
seen, papers, n, dup = set(), {}, 0, 0
for b in range(1, 7):
    m = json.load(open(f"app/src/complete/assets/mcq{b}.json"))
    for qs in m["rows"].values():
        for q in qs:
            src = q.get("src") or ""
            if "appsc" not in src.lower():
                continue
            g = re.search(r"group[- ]?(iii|ii|2|i|1)\b", src, re.I)
            if g and g.group(1).lower() in ("ii", "2"):
                exam = "Group 2"
            elif g and g.group(1).lower() in ("i", "1"):
                exam = "Group 1"
            else:
                exam = "Other APPSC exam"
            k = norm(q["s"])[:90]
            if k in have or k in seen:
                dup += 1
                continue
            seen.add(k)
            pid = "app:" + src
            if pid not in papers:
                y = re.search(r"(19|20)\d\d", src)
                stage = "Mains" if re.search(r"mains", src, re.I) else ("Prelims" if re.search(r"prelim|screening", src, re.I) else "unknown")
                papers[pid] = (pid, exam, int(y.group(0)) if y else None, stage, src, None, "app question bank (PYQ books / earlier collections)" if exam != "Other APPSC exam" else "app question bank: other APPSC exam (supporting evidence only)",
                               None, "app key (web-checked, not an APPSC document)", None, "secondary" if exam != "Other APPSC exam" else "tertiary")
            tags = ",".join(q.get("tags") or [])
            con.execute("INSERT INTO question VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (f"{pid}#{q['id']}", pid, None, q["s"], None, None,
                None, json.dumps(q.get("o"), ensure_ascii=False), q.get("a"), (q["o"][q["a"]] if q.get("o") and 0 <= q.get("a", -1) < len(q["o"]) else None),
                "app key", "secondary – not an official key", 0, None, None, f"app MCQ {q['id']} ({src})",
                "app copy" + (f"; tags: {tags}" if tags else ""), q.get("x")))
            n += 1
con.executemany("INSERT INTO paper VALUES(?,?,?,?,?,?,?,?,?,?,?)", papers.values())
con.commit()
print(f"added {n} secondary PYQs from {len(papers)} sources; {dup} skipped as duplicates of the official papers or each other")
for r in con.execute("SELECT exam, count(*) FROM question q JOIN paper p ON p.id=q.paper_id WHERE p.id LIKE 'app:%' GROUP BY exam"): print(r)
