"""APPSC Group-I Prelims 2023 Paper I and 2024 Paper I: the official FINAL keys (psc.ap.gov.in) applied over the
preliminary keys the app had.

    2023 Paper I: https://psc.ap.gov.in/Documents/KEYS/28_2022/FinalKeys/GS-1G-100%20GROUP-I%20PAPER-I%20FINAL%20KEY.pdf
    2024 Paper I: https://psc.ap.gov.in/Documents/KEYS/122023/FinalKeys/Group-I%20Paper-I%20Final%20KEY_122023_13042024.pdf

Changes data/appscpapers/<paper>.json (answer, deleted, explanation, key_status, source_key) and the same questions,
by id, in every app's assets (mcq*.json found under app/src/*/assets). Idempotent.

    python3 tools/g1_final_keys_apply.py [--check]
"""
import glob, hashlib, json, sys

CHECK = "--check" in sys.argv
DEL = "Deleted by APPSC in the final key. "
KEYS = {
    "group1-prelims-2023-paper1": {
        "source_key": "https://psc.ap.gov.in/Documents/KEYS/28_2022/FinalKeys/GS-1G-100%20GROUP-I%20PAPER-I%20FINAL%20KEY.pdf",
        # n: (0-based final answer, new explanation or None to keep)
        "key": {
            12: (2, "Variyam was a committee of the village assembly, kudumbu a ward, kudavolai the pot-ticket lottery by "
                    "which committee members were chosen, and perumakkal the members of the assembly. The final key is "
                    "IV, I, II, III (the preliminary key had II and III the other way round)."),
            31: (2, "Under Articles 243-I and 243-Y a State Finance Commission is set up every five years and recommends "
                    "the taxes, duties, tolls and fees to be assigned to the Panchayats and Municipalities. Statement III "
                    "is wrong: the Finance Commission is constituted under Article 243-I, not Article 243. The final key "
                    "is I and II."),
            96: (1, "Kudgi is in Karnataka, Kahalgaon in Bihar, Sipat in Chhattisgarh and Dadri in Uttar Pradesh, so the "
                    "final key is II, IV, I, III."),
        },
        "deleted": [32, 93, 102, 105, 108],
        "also": {35: "The final key accepts both option 1 and option 4.",
                 70: "The final key accepts both option 2 (Tax Revenue) and option 3 (Interest Receipts from Public Debt)."},
    },
    "group1-prelims-2024-paper1": {
        "source_key": "https://psc.ap.gov.in/Documents/KEYS/122023/FinalKeys/Group-I%20Paper-I%20Final%20KEY_122023_13042024.pdf",
        "key": {
            29: (1, "The Hindustan Republican Association was founded in 1924 at Kanpur by Sachindra Nath Sanyal, Jogesh "
                    "Chandra Chatterjee and Ram Prasad Bismil. Chandra Shekhar Azad joined it afterwards, and Bhagat Singh "
                    "helped turn it into the HSRA in 1928. The final key is II, III and IV."),
            37: (0, "The Administrative Reforms Commission had recommended an Inter-State Council before the Sarkaria "
                    "Commission did, so III is valid. A law made during President's rule can be altered by the State "
                    "Legislature later, and a national-interest resolution under Article 249 is passed by the Rajya Sabha, "
                    "so II and IV are wrong. The final key accepts only III; the preliminary key had also accepted I "
                    "(the Punchhi Commission on impeaching Governors)."),
            51: (2, None),
            63: (3, "NIDHI (National Integrated Database of Hospitality Industry) is a technology platform for the "
                    "hospitality sector, and the services PMI has stayed in the expansion zone, above 50. The final key "
                    "does not accept II (the USD 1 trillion tourism economy by 2047 goes with 100 million international "
                    "tourists, not investors) or III. The final key is I and IV."),
            73: (2, "Subsidised Bharat Atta sales helped contain wheat prices and the Bharat Dal scheme was extended to "
                    "moong dal. The final key also accepts III (retail inflation rising at the beginning of 2024 on "
                    "commodity prices), which the preliminary key had not; I is not accepted. The final key is II, III "
                    "and IV."),
        },
        "deleted": [58, 101],
        "also": {103: "The final key accepts both option 3 and option 4.",
                 115: "The final key accepts both option 1 (Moscow to Vladivostok) and option 3 (St. Petersburg to Vladivostok)."},
    },
}

qid = lambda slug, n: "yQ" + hashlib.md5(f"{slug}|{n}".encode()).hexdigest()[:10]
fix = {}      # id -> (a, x, deleted)
report = []
for slug, K in KEYS.items():
    f = f"data/appscpapers/{slug}.json"
    p = json.load(open(f, encoding="utf8"))
    Q = {q["n"]: q for q in p["questions"]}
    for n, (a, x) in K["key"].items():
        q = Q[n]
        if q["a"] != a: report.append(f"{slug} Q{n}: answer {q['a'] + 1} -> {a + 1} ({q['o'][a]})")
        q["a"] = a; q["deleted"] = False
        if x: q["x"] = x
        fix[qid(slug, n)] = (a, q["x"], False)
    for n in K["deleted"]:
        q = Q[n]
        if not q.get("deleted"):
            report.append(f"{slug} Q{n}: deleted in the final key (was option {q['a'] + 1})")
            old = q["x"].replace("As per the official key", "As per the preliminary key").replace("The official key", "The preliminary key")
            q["x"] = f"The preliminary key gave option {q['a'] + 1} ({q['o'][q['a']]}). " + old
        q["a"] = -1; q["deleted"] = True
        fix[qid(slug, n)] = (-1, DEL + q["x"], True)
    for n, note in K["also"].items():
        q = Q[n]
        if note not in q["x"]:
            q["x"] = q["x"].rstrip() + " " + note
            report.append(f"{slug} Q{n}: note added - {note}")
        fix[qid(slug, n)] = (q["a"], q["x"], False)
    p["key_status"] = "final"; p["source_key"] = K["source_key"]
    if not CHECK:
        open(f, "w", encoding="utf8", newline="\n").write(json.dumps(p, ensure_ascii=False, indent=1) + "\n")

touched = {}
for f in sorted(glob.glob("app/src/*/assets/mcq*.json")):
    raw = open(f, encoding="utf8").read()
    if not any(i in raw for i in fix): continue
    m = json.loads(raw); n = 0
    for qs in m.get("rows", {}).values():
        for q in qs:
            if q.get("id") in fix:
                a, x, dele = fix[q["id"]]
                new = dict(q); new["a"] = a; new["x"] = x
                if dele: new["k"] = "u"; new["cx"] = 1
                else:
                    if new.get("k") == "u": new.pop("k"); new.pop("cx", None)
                if new != q:
                    q.clear(); q.update(new); n += 1
    if n:
        touched[f] = n
        if not CHECK:
            open(f, "w", encoding="utf8", newline="\n").write(json.dumps(m, ensure_ascii=False, separators=(",", ":")))
print("\n".join(report) or "sources already final")
print(f"{len(fix)} questions; assets changed:" if touched else f"{len(fix)} questions; assets already up to date")
for f, n in touched.items(): print(f"  {f}: {n}")
