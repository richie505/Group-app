"""The official APPSC Group 2 syllabus (27-04-2023, data/g2syl/official-27042023.txt) as a tree, in APPSC's own
words: exam -> paper/section (subject, marks) -> unit -> phrase. Phrases are the dash-separated items of each unit;
a phrase with "X: a, b" sub-parts keeps them in its text. Mental Ability is left out (the owner's choice).

    python3 tools/g2syl_tree.py   -> data/g2syl/tree.json, data/g2syl/tree.md
"""
import json, re

T = open("data/g2syl/official-27042023.txt").read()


def grab(a, b):
    s = T[T.index(a) + len(a): T.index(b)]
    s = re.sub(r"\n\s*\d+\s*\n", "\n", s)       # page numbers
    return re.sub(r"\s+", " ", s).strip()


def phrases(text):
    text = text.replace("Emergency of Buddhism", "Emergence of Buddhism")
    for a, b in (("Pre - Historic", "Pre-Historic"), ("Socio - Economic", "Socio-Economic"), ("Socio - Religious", "Socio-Religious"),
                 ("Socio - Cultural", "Socio-Cultural"), ("Non- Renewable", "Non-Renewable"), ("Climate:Structure", "Climate: Structure"),
                 ("Empire:Their", "Empire: Their"), ("Communication,Tourism", "Communication, Tourism"), ("AP Sate", "AP State"),
                 ("Radioisotopes –India", "Radioisotopes - India")):
        text = text.replace(a, b)
    parts = re.split(r"\s+[-–]\s+|\s+-(?=[A-Z])|(?<=[a-z])-\s+(?=[A-Z])", text)
    return [p.strip(" .;") for p in parts if p.strip(" .;")]


POINTS = json.load(open("data/g2syl/points.json"))  # hand-written: the parts a phrase lists (e.g. Family, Marriage, ...)


SUBJECTS = []


def subject(code, stage, paper, title, marks, units):
    SUBJECTS.append({"code": code, "stage": stage, "paper": paper, "title": title, "marks": marks,
                     "units": [{"code": f"{code}.{i + 1}", "title": t, "phrases": [{"code": f"{code}.{i + 1}.{j + 1}", "text": p, "points": POINTS.get(f"{code}.{i + 1}.{j + 1}", [])}
                                for j, p in enumerate(phrases(body))]} for i, (t, body) in enumerate(units)]})


def labelled(block, labels):
    """'Ancient History: ... Medieval History: ...' -> [(label, text)]"""
    out = []
    for k, l in enumerate(labels):
        a = block.index(l + ":") + len(l) + 1
        b = block.index(labels[k + 1] + ":") if k + 1 < len(labels) else len(block)
        out.append((l, block[a:b].strip()))
    return out


h = grab("INDIAN HISTORY (30M)", "GEOGRAPHY (30M)")
subject("P1", "Prelims", "Screening Test · General Studies", "Indian History", 30,
        labelled(h, ["Ancient History", "Medieval History", "Modern History"]))
g = grab("GEOGRAPHY (30M)", "INDIAN SOCIETY (30M)")
subject("P2", "Prelims", "Screening Test · General Studies", "Geography", 30,
        labelled(g, ["General and Physical Geography", "Economic Geography of India and AP", "Human Geography of India and AP"]))
s = grab("INDIAN SOCIETY (30M)", "CURRENT AFFAIRS (30M)")
subject("P3", "Prelims", "Screening Test · General Studies", "Indian Society", 30,
        labelled(s, ["Structure of Indian Society", "Social Issues", "Welfare Mechanism"]))
subject("P4", "Prelims", "Screening Test · General Studies", "Current Affairs", 30,
        [("Major Current Events and Issues", "International - National - State of Andhra Pradesh")])


def numbered(block, n0, n1):
    out = []
    for k in range(n0, n1 + 1):
        a = re.search(rf"(?<![\d.]){k}\.\s", block)
        b = re.search(rf"(?<![\d.]){k + 1}\.\s", block) if k < n1 else None
        body = block[a.end(): b.start() if b else len(block)].strip()
        out.append(body)
    return out


m1a = grab("SOCIAL AND CULTURAL HISTORY OF ANDHRA PRADESH.(75M)", "SECTION – B")
m1b = grab("INDIAN CONSTITUTION (75M)", "PAPER –II (150M)")
m2a = grab("INDIAN AND AP ECONOMY (75M)", "SECTION- B")
m2b = grab("SCIENCE AND TECHNOLOGY (75M)", "<<<<<>>>>>")
AP = ["Pre-historic cultures to the Andhra Cholas", "Andhradesa, 11th to 16th centuries A.D.", "Europeans, Company rule and the Nationalist Movement in Andhra (1885-1947)",
      "Andhra Movement and the formation of Andhra State, 1953", "Formation of Andhra Pradesh and events 1956-2014"]
subject("M1A", "Mains", "Paper I · Section A", "Social and Cultural History of Andhra Pradesh", 75, list(zip(AP, numbered(m1a, 1, 5))))
CON = ["Nature and salient features of the Constitution", "Structure and functions of the Indian Government", "Union-State powers and constitutional bodies",
       "Centre-State relations, parties and elections", "Centralisation vs decentralisation"]
subject("M1B", "Mains", "Paper I · Section B", "Indian Constitution", 75, list(zip(CON, numbered(m1b, 6, 10))))


def titled(block, n):
    out = []
    for body in numbered(block, 1, n):
        t, _, rest = body.partition(":")
        out.append((t.strip(), rest.strip()))
    return out


subject("M2A", "Mains", "Paper II · Section A", "Indian and AP Economy", 75, titled(m2a, 5))
subject("M2B", "Mains", "Paper II · Section B", "Science and Technology", 75, titled(m2b, 5))

json.dump({"source": "APPSC Group II syllabus, 27-04-2023", "subjects": SUBJECTS}, open("data/g2syl/tree.json", "w"), ensure_ascii=False, indent=1)
md = []
for s in SUBJECTS:
    md.append(f"## {s['code']} {s['stage']} · {s['paper']} · {s['title']} ({s['marks']}M)")
    for u in s["units"]:
        md.append(f"### {u['code']} {u['title']}")
        for p in u["phrases"]:
            md.append(f"- {p['code']}: {p['text']}")
            md += [f"    - {x}" for x in p["points"]]
open("data/g2syl/tree.md", "w").write("\n".join(md) + "\n")
print(sum(len(u["phrases"]) for s in SUBJECTS for u in s["units"]), "phrases,", sum(len(p["points"]) for s in SUBJECTS for u in s["units"] for p in u["phrases"]), "points")
