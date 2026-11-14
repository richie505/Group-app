import json,sys
ROOT='/home/user/Group-app/'
files=json.load(open(ROOT+'data/notes2026/review/book2-notes-files.json'))
def path(r): return ROOT+files[str(r)]['notes']
E=[]  # (row, old, new, src_to_add or None)
def ed(r,old,new,src=None): E.append((r,old,new,src))

ed(32,"- **Rule 377 – matters a day**: **20** in most books and keys (RAS 2018 key); NextGen Rocket says it was raised to **30** a day in 2015.",
 "- **Rule 377 – matters a day**: **20** in most books and keys (RAS 2018 key; PRS primer: \"presently **20 MPs** are allowed to raise matters under Rule 377 per day\", one matter per member per week); NextGen Rocket says it was raised to **30** a day in 2015 (not found in Lok Sabha / PRS sources) – answer **20** unless 30 alone is offered.",
 "PRS primer Engaging as a Parliamentarian p.10 (Rule 377: 20 MPs a day, one matter a week); Rocket Polity Part 2 p.29 (src/polity/rocket-polity-02.txt; 30 post-2015)")
ed(37,"- **131st Amendment Bill (app notes):** Lok Sabha **550 → 850**.",
 "- **Constitution (131st Amendment) Bill, 2026:** Lok Sabha ceiling **550 → 850** (815 from States + 35 from UTs; amends Arts 81, 82, 334A for early delimitation on the 2011 Census and women's reservation); **defeated in the Lok Sabha, April 2026** (298 for, 230 against – short of the special majority).",
 "PMF Lens Apr 2026 part 1 p.5 (src/current-affairs/pmf-lens-2026-04-01.txt); Praveen CA-360 Apr 2026 p.10 (src/current-affairs/praveen-ca360-2026-04-magazine.txt)")
ed(41,"Anglo-Indian nomination ended (104th Amendment, 2020)",
 "Anglo-Indian nomination ended (**104th Amendment Act, 2019**, in force **25 January 2020**)",
 "Laxmikanth 8th ed. (src/polity/laxmikanth-indian-polity-02.txt) 104th Amendment Act, 2019; Rocket Polity Part 1 (src/polity/rocket-polity-01.txt) p.33 (Anglo-Indian nomination ended after 25 Jan 2020)")
ed(33,"- Only **14** Private Members' Bills have become law, the last in **1970** – none \"recently for the first time\".",
 "- Only **14** Private Members' Bills have become law, the last in **1970** – none \"recently for the first time\"; also: in the Lok Sabha the **Committee on Private Members' Bills and Resolutions** (15 members, **Deputy Speaker** chairs) classifies such Bills and **allots time** (it also examines a private member's Constitution amendment Bill before introduction); the **Rajya Sabha has no such committee** – its **Business Advisory Committee** does this.",
 "Laxmikanth 8th ed. p.407 (Committee on Private Members' Bills and Resolutions; RS – Business Advisory Committee); Laxmikanth p.288 (pocket veto)")
ed(33,"| Assent | President: assent, withhold, or **return once** for reconsideration (suspensive veto) |",
 "| Assent | President: assent, withhold, or **return once** for reconsideration (suspensive veto); no time limit is fixed for his decision → **pocket veto** possible (Zail Singh, Indian Post Office (Amendment) Bill, 1986) |")
ed(35,"| Business Advisory | Allots time for Government and other business | LS 15, **Speaker chairs** |",
 "| Business Advisory | Allots time for Government and other business | LS 15, **Speaker chairs** (the Speaker also chairs the **Rules** and **General Purposes** Committees) |",
 "Laxmikanth 8th ed. p.337 (Speaker chairs Business Advisory, Rules and General Purposes Committees)")
ed(72,"current AG at the time of the exam (Sorabjee 2002; Venugopal 2018-2023 papers; not Rohatgi)",
 "current AG at the time of the exam (Sorabjee 2002; Venugopal for papers of 2018 – Sep 2022; not Rohatgi; from **1 Oct 2022** the AG is **R. Venkataramani** – a \"July 2023\" stem naming Venugopal as AG is factually wrong)",
 "Praveen CA-360 Jul 2026 (src/current-affairs/praveen-ca360-2026-07-magazine.txt) – AG R. Venkataramani")
ed(75,"- Re-introduced in **1971, 1977, 1985, 1989, 1996, 1998, 2001, Aug 2011, Dec 2011** (ten attempts in all); the tenth (Lokpal and Lokayuktas Bill, 2011) became the 2013 Act.",
 "- Re-introduced in **1971, 1977, 1985, 1989, 1996, 1998, 2001, Aug 2011, Dec 2011** (ten attempts in all – Laxmikanth); many books also list **2005 and 2008** (\"1968 … 2001, 2005, 2008\" – Indian Express via Wikipedia); the tenth (Lokpal and Lokayuktas Bill, 2011) became the 2013 Act.",
 "Laxmikanth 8th ed. ch.66 p.724-725 (ten Bills; no 2005/2008); en.wikipedia.org/wiki/Lokpal (2005, 2008, citing Indian Express 30 Jan 2019)")
ed(84,"- **3rd SFC** per-capita grant **ZP : MP : GP = Rs 8 : 16 : 8**.",
 "- **3rd SFC** per-capita grant **ZP : MP : GP = Rs 8 : 16 : 8**; the **4th SFC** (Gummadi Nancharaiah, report Oct 2019) recommended raising these grants to **Rs 25 : 50 : 25** (GP Rs 8 → 25, MP Rs 16 → 50, ZP Rs 8 → 25).",
 "AP 5th SFC Report ch.3 p.19-20 (src/ap-economy/vsfc.txt: per-capita grants GP Rs 8, MP Rs 16, ZP Rs 8 → 25/50/25)")
ed(100,"regulates **tariffs, interconnection, quality of service**.",
 "regulates **tariffs, interconnection, quality of service**; Chairperson **Anil Kumar Lahoti** (since Jan 2024; J.S. Sharma 2009-12 was the answer in 2011 papers).",
 "Praveen CA-360 Jul 2026 (src/current-affairs/praveen-ca360-2026-07-magazine.txt): TRAI chaired by Anil Kumar Lahoti")
ed(100,"regulates **public exhibition of films**.",
 "regulates **public exhibition of films**; also: **CDSCO** (Central Drugs Standard Control Organisation, headed by the **Drugs Controller General of India**, Health Ministry) **approves drugs and vaccines** and clinical trials – not ICMR, WHO or DRDO.",
 "PMF Lens Feb 2026 (src/current-affairs/pmf-lens-2026-02-13.txt, -02-14.txt): CDSCO approves clinical trials and market authorisation; DCGI")
ed(109,"- **J.C. Nesfield** is credited (APPSC key) with first using the word **\"untouchable\"** for these castes.",
 "- **J.C. Nesfield** is credited (APPSC key) with first using the word **\"untouchable\"** for these castes – an attribution found only in the key (not in Rocket, NextGen or NCERT); the colonial term was \"Depressed Classes\".")
ed(110,"Rocket: first caste association = **Justice Party (1916)**.",
 "Rocket: first caste association = **Justice Party (1916)** (keys follow Rocket; strictly the Justice Party was a political party – caste sabhas such as the **Nadar Mahajana Sangam (1910)** are older).",
 "Rocket Indian Society p.2 (first caste association = Justice Party); en.wikipedia.org/wiki/Nadar_Mahajana_Sangam (1910)")
ed(114,"- **Bogardus:** social mobility as **change on the same status level** (APPSC Hostel Welfare key).",
 "- **Bogardus:** social mobility as **change on the same status level** (APPSC Hostel Welfare key) – strictly, change on the same status level is **horizontal mobility** (Rocket: horizontal = same-status change; vertical = up or down).",
 "Rocket Indian Society p.23 (vertical = upward/downward; horizontal = same status change)")
ed(126,"- **First Chairperson:** Justice **Ranganath Misra** (12 Oct 1993 – 24 Nov 1996).",
 "- **First Chairperson:** Justice **Ranganath Misra** (12 Oct 1993 – 24 Nov 1996); Justice **M. Fathima Beevi** (first woman SC judge) was one of the first members (**1993-97**).",
 "en.wikipedia.org/wiki/Fathima_Beevi (NHRC member 1993-97)")
ed(126,"**May 2024:** re-accreditation of NHRC-India **deferred** for the second year running.",
 "**May 2024:** re-accreditation of NHRC-India **deferred** for the second year running – concerns: **independence** (political appointments, police officers in its investigations) and lack of **pluralism** (few women, no minority/Dalit/tribal members).",
 "The Hindu 14 May 2024 via janataweekly.org (1 Jun 2024) and sabrangindia.in (GANHRI SCA deferral, reasons)")
ed(128,"banned in AP by both the **Madras Act 1947** and the **AP Devadasis (Prohibition of Dedication) Act 1988** |",
 "banned in AP by both the **Madras Act 1947** and the **AP Devadasis (Prohibition of Dedication) Act 1988** (Act 10 of 1988, which repealed the 1947 Act – s.12) |",
 "legitquest.com – AP Devadasis (Prohibition of Dedication) Act, 1988 (Act 10 of 1988), s.12 repeals Act 31 of 1947")
ed(130,"or with the victim's (next of kin's) written authorisation to a recognised welfare organisation.",
 "or with the victim's (next of kin's) written authorisation to a recognised welfare organisation; in PYQ options this police officer appears as **\"Inspector of police\"**.")
ed(137,"general knowledge, not checked (RMSA, RUSA, SEMIS, NPEGEL details)",
 "general knowledge, not checked (RMSA, RUSA, SEMIS, NPEGEL details); checked: en.wikipedia.org RMSA (launched Mar 2009, merged into Samagra Shiksha 2018), RUSA (2013, CSS strategic funding of State higher education)")
ed(145,"| Baden | West Bengal (as keyed in the 2016 PYQ) |",
 "| Baden | West Bengal (as keyed in the 2016 PYQ; \"Baden\" is not in the 1976 Act's list of names – the match is solved by Gothi, Hali, Vetti) |",
 "Bonded Labour System (Abolition) Act 1976, Explanation to s.2(b) (Adiyamar … Hali … Vetti; no \"Baden\") – caseon.in")
ed(166,"| Skill India Digital Hub (2023) | **MSDE** (not Education) |",
 "| Skill India Digital Hub (2023) | **MSDE** (not Education); one platform for skills, jobs/apprenticeships and lifelong learning for the AI era – \"Badhna Hai Toh Yahan Judna Hai\" campaign, Feb 2026 |",
 "Praveen CA-360 Feb 2026 p.52 (src/current-affairs/praveen-ca360-2026-02-magazine.txt) – SIDH")

dry = len(sys.argv)>1 and sys.argv[1]=='dry'
texts={}
for r,old,new,src in E:
    p=path(r)
    t=texts.setdefault(p, open(p).read())
    n=t.count(old)
    if n!=1: print('COUNT',n,'row',r,old[:60]); continue
    i=t.index(old)
    t=t[:i]+new+t[i+len(old):]
    if src:
        j=t.find('\n~~ Sources:', i)
        if j<0: print('NO SRC',r); 
        else:
            k=t.find('\n', j+1)
            if k<0: k=len(t)
            t=t[:k]+'; '+src+t[k:]
    texts[p]=t
for p,t in texts.items():
    if not dry: open(p,'w').write(t)
print('files',len(texts),'edits',len(E))
