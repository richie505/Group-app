"""PYQs whose question text carried the previous question's explanation, or stray page/question numbers from the
scan ("... scheme 70. W started by"). Each is rebuilt by hand: the real question, clean options; an explanation
that was stuck in the stem moves to the explanation when it is about this question. Keys are left as they were.

    python3 tools/pyq_fix_leaks.py      (both apps)
"""
import json

SDG = ("As per the SDG India Index 2020-21 (NITI Aayog), the top-ranking States were: 1. Kerala (score 75); "
       "2. Himachal Pradesh and Tamil Nadu (74 each); 3. Andhra Pradesh, Goa, Karnataka and Uttarakhand (72 each); "
       "4. Sikkim (71); 5. Maharashtra (70). Gujarat was not among them.\n"
       "SDG India Index 2023-24 (released July 2024): 1. Kerala and Uttarakhand (79 each); 2. Tamil Nadu (78); "
       "3. Goa and Himachal Pradesh (77 each); 4. Punjab and Sikkim (76 each); 5. Karnataka (75). Bihar was last (57); "
       "Uttar Pradesh moved to the 'Front Runner' category (67).")

# id -> stem, options (None: keep), explanation: "keep" | "lead" (the text cut from the stem goes first) | a string
FIX = {
    "ycb77387227c": ("As per the SDG India Index and Dashboard 2020-21 published by the NITI Aayog, which one of the "
                     "following States was NOT among the top five States in their performance regarding SDGs in the country?",
                     None, SDG),
    "y36ee458903c": ("Consider the following types of pottery:\nI. Black and Red Ware\nII. Black Slipped Ware\n"
                     "III. Painted Grey Ware\nIV. Red Ware\nV. Northern Black Polished Ware\n"
                     "Which of the above types of pottery were associated with the Later Vedic people?",
                     ["II, III and IV only", "II, III and V only", "I, II, III and IV", "I, II, III, IV and V"], "keep"),
    "yacb0c1c6926": ("What was the exact constitutional status of India on 26th January, 1950?", None,
                     "The exact constitutional status on 26-1-1950 was 'A SOVEREIGN DEMOCRATIC REPUBLIC'. The words "
                     "socialist, secular and integrity were added by the 42nd Amendment Act, 1976."),
    "yb1244be52dc": ('What is the objective of the "Badikosta" scheme started by the Government of Andhra Pradesh?',
                     ["To minimize dropout rate of girl students from high school",
                      "To promote bicycle as a mode of environmentally-friendly transport for students",
                      "To provide bicycles at low cost to girl students",
                      "To provide incentive to teachers for getting girl students enrolled in school"], "keep"),
    "y6a9a8cb950d": ("Second Five Year Plan of India was based on an economic model developed by:", None,
                     "In the Second Plan, the allocation of resources to broad sectors such as agriculture and industry "
                     "was based on the two- and four-sector model prepared by Prof. P.C. Mahalanobis (the 2nd Plan is also "
                     "called the Mahalanobis Plan). It focussed on rapid industrialisation and capital-intensive heavy and "
                     "basic industries. The Industrial Policy, 1956 set a socialistic pattern of society as the goal of economic policy."),
    "yd8da8c14d2b": ("How many PSUs were there at the commencement of the First Five Year Plan?", None,
                     "At the end of the VII Plan in 1990, the total number of Public Sector Undertakings (PSUs) in India stood at 244."),
    "y00e3d2a0f96": ("According to the Census of 2001, the annual exponential growth rate of the population in India "
                     "during the last decade was:", None, "keep"),
    "y05bcb4ce5d3": ("Long-term objective of the National Population Policy 2000 is to achieve a stable population by:", None,
                     "Under the long-term target, stabilisation of the population was set for the year 2045; it was later "
                     "modified to 2070."),
    "yd6b991ece3f": ("Swachh Bharat Mission (Grameen) has been launched in India in:", None,
                     "Swachh Bharat Mission was launched in October 2014 to achieve an 'Open Defecation Free' (ODF) and "
                     "'Clean India' by 2 October 2019, the 150th birth anniversary of Mahatma Gandhi. It has two components: "
                     "Rural (Grameen) and Urban (Shahari). Phase 1 lasted till October 2019."),
    "y1aae847374a": ("The Liberalisation, Privatisation and Globalisation (LPG) Model of Economic Development assigns a key role to:",
                     None, "keep"),
    "ye30b131d467": ("Global capital flows to developing countries increased significantly during the nineties. In view of "
                     "the East Asian financial crisis and Latin American experience, which type of inflow is good for the host country?",
                     None, "keep"),
    "y7ef5ccafa96": ("As per the present policy, what is the percentage of Foreign Direct Investment permitted in total "
                     "equity for Multi-Brand Retail Trading Sector?", ["51%", "49%", "26%", "100%"], "keep"),
    "ye7f7904855f": ("Which enactment deals with withdrawal of currency notes from being legal tender?", None, "keep"),
    "y1f52d888bf9": ("From the following, which cyclone struck the western coast of India in the year 2021?", None, "keep"),
    "yf17b964de7d": ("Which of the following is the first pipeline constructed in India for the transportation of crude oil?",
                     None, "keep"),
    "y94325099aad": ("Which of the following was the first digital wallet company in India?", None, "keep"),
    "y55c4b938a86": ("How many national missions have been started as part of the National Action Plan on Climate Change?",
                     None, "keep"),
    "y6e472170e06": ("Which among the following rare natural phenomenon is going to happen in 2024, after 221 years, in "
                     "the United States of America?",
                     ["Fire Tornadoes", "Glow Worm Caves", "New York's Ice Volcano", "Double Cicada Explosion"], "keep"),
    "y1fcbe7f6429": ('"Every Indian is special. Every Indian is a VIP." On which occasion did Prime Minister Narendra Modi '
                     "tweet these words?",
                     ["On International Yoga day", "On launching the BHIM App", "During the UP election campaign",
                      "On abolition of red beacons on vehicles"], "keep"),
    "yf13c2513a94": ("Mahmoud Abu Zeid has won the 2018 UNESCO/Guillermo Cano World Press Freedom Prize. He hails from "
                     "which country?", None, "keep"),
    "yf88720d1216": ("In the context of Central Government programmes, which one of the following statement/statements "
                     "is/are incorrect?\n"
                     "I. The objective of Pradhan Mantri Anusuchit Jaati Abhyuday Yojana (PM-AJAY) is aimed at reducing "
                     "poverty of the ST communities by generating additional employment opportunities.\n"
                     "II. Under the Pradhan Mantri Shram Yogi Maandhan Yojana (PM-SYM), monthly contribution is payable by "
                     "the beneficiary, the State Government and the Central Government.\n"
                     "III. Under the 'FutureSkills Prime' Programme, Centre for Development of Advanced Computing (C-DAC) "
                     "is the key implementing agency.\n"
                     "IV. Mission Karmayogi comprises of eight key pillars that are intended to create functional and "
                     "behavioural competencies among the civil servants.\n"
                     "Select the answer using the codes given below:", None, "keep"),
    "y93d416b9788": ("Consider the following statements:\n"
                     "Statement I: The researchers from various organizations have identified a new species of burrowing "
                     "frog in the urban landscape of Karnataka and named it as 'Sphaerotheca Varshaabhu'.\n"
                     "Statement II: Sphaerotheca Varshaabhu got its name from its behaviour of changing colours from brown "
                     "to pale brown in the beginning of monsoon season.\n"
                     "Select the correct answer using the codes given below:",
                     ["Statement I and Statement II are correct and Statement II is the correct explanation for Statement I",
                      "Statement I and Statement II are correct, but Statement II is not the correct explanation for Statement I",
                      "Statement I is correct, but Statement II is incorrect",
                      "Statement I is incorrect, but Statement II is correct"], "keep"),
}
# small cuts: stray question/page numbers inside the text
CUT = {
    "y707380a85c1": [("Consolidated 47. Fund", "Consolidated Fund")],
    "ye24cad4ce8a": [(" 82. Select", "\nSelect")],
    "y79b97c376a7": [(" Indian Polity: Other Concepts PMF IAS IP – 118", "")],
    "yda9ec98d4c3": [("around 300.", "around 30°."), ("82030' E", "82°30' E")],
    "yb5d5e573e53": [(" 66.\n", "\n")],
    "y906a48e29db": [("11th 85. March", "11th March"), ("the 86. age", "the age")],
    "yb0629ad29a5": [(" Which among", "\nWhich among")],
}
OPT = {"y906a48e29db": {3: "None of the above"}}


def fix(q):
    i = q["id"]
    if i in FIX:
        s, o, x = FIX[i]
        cut = q["s"][: max(0, q["s"].find(s.split("\n")[0][:25]))].strip() if s.split("\n")[0][:25] in q["s"] else ""
        q["s"] = s
        if o:
            q["o"] = o
        if x == "lead" and cut:
            q["x"] = (cut + "\n" + q.get("x", "")).strip()
        elif x not in ("keep", "lead"):
            old = q.get("x", "").strip()
            q["x"] = x + ("\n" + old if old else "")
    for a, b in CUT.get(i, []):
        assert a in q["s"], (i, a)
        q["s"] = q["s"].replace(a, b)
    for k, v in OPT.get(i, {}).items():
        q["o"][k] = v


def main():
    for app in ("main", "complete"):
        n = 0
        for b in range(1, 7):
            p = f"app/src/{app}/assets/mcq{b}.json"
            m = json.load(open(p))
            for v in m["rows"].values():
                for q in v:
                    if q["id"] in FIX or q["id"] in CUT or q["id"] in OPT:
                        fix(q)
                        n += 1
            open(p, "w").write(json.dumps(m, ensure_ascii=False, separators=(",", ":")))
        print(app, n, "PYQs repaired")


if __name__ == "__main__":
    main()
