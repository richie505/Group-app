# APPSC Group 2 Geography: Where the Questions Come From (Prelims/Screening; 2008, 2012, 2017, 2019, 2024 papers)

Method: I pulled every question mapped to a P2.* (geography) leaf from the official-paper JSONs in `data/g2papers/` (`*.leaves.json` gives the mapping, `leaves.md` the syllabus). I grepped distinctive phrases against the local library in `data/notes2026/src/`. That library holds NCERT compilations (PW OnlyIAS, which summarise NCERT VI-XII), G.C. Leong, PMF, NextGen and Rocket AP and India geography, Shankar Environment and the AP Socio-Economic Survey 2024-25. I also ran a few web searches for book lists and paper analyses.

Match strength used below:
- **verbatim**: wording or numbers that appear word-for-word in the source.
- **clear fact match**: the same fact, list or example set, paraphrased.
- **likely**: consistent with the source, but the fact also appears elsewhere.

A note on the NCERT evidence: the local NCERT files are compilations, not the original textbooks. A match there implies the NCERT original contains the same text. Some matches come from my knowledge of the NCERT textbooks and could not be checked against a local copy. Those are labelled "(not verified locally)".

Geography questions per paper (P2.* leaf counts):

| Paper | Geography Qs | Main leaves |
|---|---|---|
| Prelims 2024 | 30 | 10 on P2.1.6, 5 on P2.2.3, 4 on P2.1.3 |
| Prelims 2019 | 20 | 6 on P2.1.6, 4 on P2.3.2 |
| Prelims 2017 | 3 | Old syllabus: no geography section; the 3 sit in economy or HDI |
| 2008 Paper I | 19 | — |
| 2008 Paper III | 24 | Mostly AP human and economic geography |
| 2012 Paper I | 35 | 19 disaster management, 9 world places |

Sources: [prelims-2024.leaves.json](/home/user/Group-app/data/g2papers/prelims-2024.leaves.json), [prelims-2019.leaves.json](/home/user/Group-app/data/g2papers/prelims-2019.leaves.json), [prelims-2017.leaves.json](/home/user/Group-app/data/g2papers/prelims-2017.leaves.json), [group2-2012-paper1.leaves.json](/home/user/Group-app/data/g2papers/group2-2012-paper1.leaves.json), [group2-2008-paper1.leaves.json](/home/user/Group-app/data/g2papers/group2-2008-paper1.leaves.json), [group2-2008-paper3.leaves.json](/home/user/Group-app/data/g2papers/group2-2008-paper3.leaves.json).

## Q1. Which books do toppers, coaching institutes and analyses name for Group 2 geography? Which are most consistent?

### Takeaway
Public, citable book lists for APPSC Group 2 geography are thin and come only from commercial sites. The titles named most consistently are:
- **Telugu Akademi**: AP Geography, and Indian and World Geography.
- **NCERT Class 11**: Indian Physical Geography, and Fundamentals of Physical Geography.
- **Telugu-medium guides**, for example Raman Raju (Geography: World, India and AP), and coaching e-books (Adda247 AP Geography and Indian Geography).

I found no named topper interview or institute analysis that ties 2024 geography questions to specific books. The paper evidence in Q2 is much stronger than the published lists.

### Cited Findings
- A coaching-site summary of an APPSC syllabus and book list names "Indian and World Geography – Telugu Academy Books", "AP Geography – Telugu Academy" and a "Map Book" for geography. — [Web search summary of Scribd APPSC Syllabus Book List](https://www.scribd.com/document/670489635/APPSC-Syllabus-Book-List)
  - The Scribd page itself would not load when fetched, so this rests on the search snippet only.
- Freshersnow's APPSC Group 2 books list (per search snippet) names "Geography (world, India & AP) Telugu – Raman Raju". — [freshersnow](https://www.freshersnow.com/appsc-group-2-books/)
  - The page returned 404 when fetched, so this is not verified.
- Testbook's APPSC pages list "Indian Physical Geography (NCERT Class 11)" under geography. — [Testbook APPSC best books](https://testbook.com/appsc/best-books-for-preparation)
  - Testbook's Group 2-specific page lists no geography book at all. It names only Vijeta GS, Ramesh Singh and Vijeta AP Economy. — [Testbook APPSC Group 2 books](https://testbook.com/appsc-group-2/books-for-preparation)
- Adda247 sells an "AP Geography eBook" (Telugu medium, first edition) and an "Indian Geography eBook" for APPSC Group 1, 2 and 4. — [Adda247 AP Geography](https://www.adda247.com/product-ebooks/48618/ap-geography-ebook-for-appsc-group-sachivalayam-and-other-exams-by-adda247); [Adda247 Indian Geography](https://www.adda247.com/product-ebooks/49170/indian-geography-ebook-for-appsc-group-1-group-2-ap-grama-sachivalayam-j-dl-deo-and-other-appsc-exams-by-adda247)
  - Adda247 also sells "Fundamentals of Geography" and "Principles of Indian Geography" for APPSC and TSPSC. — [Adda247](https://www.adda247.com/product-books/17571/fundamentals-of-geography-for-appsc-tspsc-other-state-pcs-exams-english-printed-edition)
- The CollegeDekho (Telugu) analysis of the 25 Feb 2024 screening test rated Geography "Easy to Moderate" ("ఈజీ నుంచి మోడరేట్"). Some candidates called history and geography "very easy". It names no sources. — [CollegeDekho 2024 analysis](https://www.collegedekho.com/te/news/appsc-group-2-prelims-exam-2024-analysis-review-50244/)
- The local source register ranks standard books (Leong, NCERT compilations) as priority 11, below NextGen and Rocket coaching notes. The library holds:
  - G.C. Leong
  - PW OnlyIAS NCERT compilations (physical, Indian, human geography)
  - PMF
  - NextGen AP and Indian geography
  - Rocket AP, Indian, World and General geography

  — [SOURCES-LOCAL.md](/home/user/Group-app/data/notes2026/SOURCES-LOCAL.md); [src/geography listing](/home/user/Group-app/data/notes2026/src/geography/)

### Inferences
- The lists agree on two layers: NCERT (Class 6-12) for physical and India geography, and Telugu Akademi for AP geography. The paper evidence in Q2 supports both.
- Majid Husain, Khullar and Leong appear in generic State PSC lists, not in APPSC Group 2-specific lists I could verify. The question level is closer to NCERT than to these books (see Q2).

### Gaps
- I found no named APPSC Group 2 topper strategy for geography. The Unacademy book-list sessions are login-gated and show no titles.
- I found no coaching institute analysis that attributes 2024 geography questions to specific books. The Sakshi and Eenadu analyses did not surface in search.
- Edition details for the Telugu Akademi AP Geography could not be verified online.

## Q2. Which sources do actual PYQs match?

### Takeaway
Prelims 2024 geography (30 questions) reads almost like an NCERT question bank:
- **About 20 of 30 match NCERT** (Class 6/7/9/10/11/12), several verbatim.
- **The remaining 5 AP questions** come from AP-specific material: Telugu Akademi or AP SCERT-type AP geography, APIIC and AP Socio-Economic Survey facts, and AP Tourism.

Prelims 2019 is different:
- It leans on recent reports for about 5 questions: ISFR 2017, Global MPI 2018, UNDP HDR 2018 update and Census 2011.
- The rest are basic NCERT or general facts, plus about 4 AP questions.

The older papers:
- **2012** drew heavily on disaster-management reports and world-atlas place facts.
- **2008 Paper III** drew on AP Census 2001 and NHDR 2001 data.

### Cited Findings

**Prelims 2024: physical and world geography (NCERT Class 7 and Class 11 Fundamentals of Physical Geography)**

- **Q39, salinity order "Lake Van > Dead Sea > Great Salt Lake": NCERT XI, *Fundamentals of Physical Geography*, ch. "Water (Oceans)". Verbatim figures.** The NCERT compilation reads "Lake Van in Turkey (330 o/oo)", Dead Sea 238, Great Salt Lake 220. The answer is simply the NCERT order. — [onlyias-ncert-physical-geography-08.txt](/home/user/Group-app/data/notes2026/src/geography/onlyias-ncert-physical-geography-08.txt)
- **Q38, ocean bottom relief match: same NCERT XI chapter. Verbatim.**
  - Option text "Associated with active volcanoes and strong earthquakes" (oceanic deeps) appears word-for-word.
  - So does "Massive sedimentary deposits received over a long time by the continental shelves".

  — [onlyias-ncert-physical-geography-08.txt](/home/user/Group-app/data/notes2026/src/geography/onlyias-ncert-physical-geography-08.txt)
- **Q36, heating of the atmosphere (advection = horizontal, convection = vertical, conduction = lower layers): NCERT XI ch. "Solar Radiation, Heat Balance and Temperature". Clear fact match.** The compilation reads "The transfer of heat through horizontal movement of air is called advection". — [onlyias-ncert-physical-geography-06.txt](/home/user/Group-app/data/notes2026/src/geography/onlyias-ncert-physical-geography-06.txt)
- **Q31, deleted from the final key**: "Pangaea split... 150 million years ago... Gondwanaland broke up 65 million years ago". NCERT XI dates the Pangaea break-up to about 200 million years ago. The examiner seems to have mis-transcribed a textbook figure, which would explain the deletion (not verified locally). — [prelims-2024.json](/home/user/Group-app/data/g2papers/prelims-2024.json)
- **Q32, Q33, Q34, Q35, Q40, Q41 (likely or verbatim NCERT; not verified locally):**
  - **Q32**: option (c) "Epicentre is the first one to experience the waves" mirrors the NCERT XI ch. 3 sentence "The point on the surface, nearest to the focus, is called epicentre. It is the first one to experience the waves." Verbatim.
  - **Q35**: "meteorites burn up when they enter from the space" mirrors NCERT VII *Our Environment* ch. 4 "Air": "Mesosphere... Meteorites burn up in this layer on entering from the space". Verbatim.
  - **Q33**: granite as an intrusive rock is NCERT VII ch. 2. Clear fact match.
  - **Q34**: landforms and their agents is NCERT VII ch. 3 or XI ch. 7. Clear fact match.
  - **Q40**: Alps as young fold mountains versus Aravalli, Urals and Appalachians as old is NCERT VI ch. 6. Clear fact match.
  - **Q41**: Prairies in the USA and Canada is NCERT VII ch. "Life in the Temperate Grasslands". Clear fact match.

  — question texts in [prelims-2024.json](/home/user/Group-app/data/g2papers/prelims-2024.json)

**Prelims 2024: India geography (NCERT IX *Contemporary India I*, XI *India: Physical Environment*, XII *India: People and Economy*, X *Contemporary India II*)**

- **Q45, Mango Showers on the coast of Karnataka: NCERT XI *India: Physical Environment*, ch. "Climate". Clear fact match.** The NCERT compilation says "Mango Shower – Kerala and coastal Karnataka – pre-monsoon showers at the end of summer". Karnataka is the only option that fits. — [onlyias-ncert-indian-geography-05.txt](/home/user/Group-app/data/notes2026/src/geography/onlyias-ncert-indian-geography-05.txt)
- **Q42, Satluj to Kali = Kumaon Himalayas: NCERT XI *India: Physical Environment* ch. 2 (river-valley division of the Himalayas). Clear fact match.** The compilation lists "Kumaon Himalayas, Nepal Himalayas, and Assam Himalayas". — [onlyias-ncert-indian-geography-03.txt](/home/user/Group-app/data/notes2026/src/geography/onlyias-ncert-indian-geography-03.txt)
- **Q52, functional classification of towns: NCERT XII *India: People and Economy*, ch. "Human Settlements". Clear fact match on the example list.** The question pairs Ankleshwar = mining (oil), Jamshedpur = industrial, Gandhinagar = administrative and Udhampur = garrison. The compilation shows the same scheme ("Garrison Cantonment ... Ambala, Jalandhar"; Gandhinagar under administrative towns). The original NCERT example lists include Ankaleshwar (mining) and Udhampur (garrison); that part is not verified locally.
  - The pairing of Ankleshwar with mining, rather than with industry, is a giveaway that the NCERT example list is the source.

  — [onlyias-ncert-human-geography-04.txt](/home/user/Group-app/data/notes2026/src/geography/onlyias-ncert-human-geography-04.txt)
- **Q57, HVJ pipeline (Gujarat, MP, UP; not Maharashtra): NCERT XII ch. "Transport and Communication". Clear fact match.** The compilation reads "The 1700 km long Hazira-Vijaipur Jagdishpur cross country gas pipeline links Mumbai High...". — [onlyias-ncert-human-geography-0x](/home/user/Group-app/data/notes2026/src/geography/) (grep hit in an onlyias compilation file)
- **Q56, first cement plant at Madras in 1904: NCERT X *Contemporary India II*, ch. "Manufacturing Industries" ("The first cement plant was set up in Chennai in 1904"). Clear fact match.** The local hit is a coaching file: "The first attempt to manufacture cement in India was made in 1904...". — [src/geography grep hit](/home/user/Group-app/data/notes2026/src/geography/)
- **Q37, Q43, Q44, Q46, Q47, Q53, Q54 (likely or verbatim NCERT; not verified locally):**
  - **Q43**: "Eastern Ghats... from the Mahanadi valley to the Nilgiris" is NCERT IX ch. 2. Near-verbatim. The compilation also says "The Eastern and Western Ghats converge at the Nilgiri Hills".
  - **Q47**: tropical deciduous forests as "the most widespread forests of India" is NCERT IX and XI. Verbatim phrase.
  - **Q46**: "very deep" black soil in the north-western Deccan is NCERT XI ch. "Soils". Clear fact match.
  - **Q44**: Narmada forming the Dhuandhar falls is NCERT XI drainage. Clear fact match.
  - **Q54**: tea plantation started in the 1840s in the Brahmaputra valley of Assam is NCERT XII. The final key accepted both Brahmaputra valley and Darjeeling.
  - **Q53**: rapeseed and mustard as rabi crops is NCERT XII ch. "Land Resources and Agriculture". Clear fact match.
  - **Q37**: Kavaratti and the Eight Degree Channel are NCERT IX ch. 1-2. Clear fact match. Note the trick: the question writes "Nine Degree" where the fact is the Eight Degree Channel.

  — [prelims-2024.json](/home/user/Group-app/data/g2papers/prelims-2024.json)
- **Q58, Bilaspur = South East Central Railway zone**: from Indian Railways and India Year Book-type data, not NCERT. Clear fact match. — [prelims-2024.json](/home/user/Group-app/data/g2papers/prelims-2024.json)

**Prelims 2024: AP-specific (Telugu Akademi or AP SCERT AP geography, APIIC, SES, AP Tourism)**

- **Q48, origins of AP rivers.** Correct pairings: Vamsadhara = Jayapur hills, Machkund = Mudugal hills, Gundlakamma = Nallamala, Pennar = Nandidurga.
  - Rocket AP Geography has "Jayapur Hills, Odisha – Origin of Vamsadhara", and NextGen AP Geography has "Originates in Jayapur hills @ Odisha". That is a clear fact match.
  - The non-standard spelling "Jayapur" (standard: Jeypore) is shared by the question and the Telugu-medium coaching notes. That points to a Telugu-medium source, likely Telugu Akademi.
  - "Mudugal hills" does not occur anywhere in the local library, so that pairing traces to an AP-specific source outside it.

  — [rocket-ap-geography.txt](/home/user/Group-app/data/notes2026/src/geography/rocket-ap-geography.txt); [nextgen-ap-geography-appsc-02.txt](/home/user/Group-app/data/notes2026/src/geography/nextgen-ap-geography-appsc-02.txt)
- **Q59, minerals of AP by erstwhile district** (bauxite in the Visakhapatnam and East Godavari agency forests, mica in Nellore, limestone at Jammalamadugu and Mydukuru, manganese at Garividi):
  - Rocket AP Geography has "Bauxite → Eastern Ghats → erstwhile Visakhapatnam + East Godavari" and "Mica: Erstwhile Nellore → 1st in production & reserves". Clear fact match.
  - Rocket lists manganese under Srikakulam. "Garividi" appears only in the AP Reorganisation file. The examiner therefore used a different AP geography text, probably Telugu Akademi or an older AP SES minerals chapter. Likely.

  — [rocket-ap-geography.txt](/home/user/Group-app/data/notes2026/src/geography/rocket-ap-geography.txt)
- **Q55, APIIC clusters** (Gandrajupalle silk and garments, Kopparthi engineering, Makavarapalem aluminium, Machilipatnam jewellery): official APIIC and AP government material. Likely.
  - "Kopparthy" appears in AP Socio-Economic Survey 2024-25 as an APIIC industrial node.
  - "Gandrajupalle" does not occur in the local library.

  — [ap-socio-economic-survey-2024-25.txt](/home/user/Group-app/data/notes2026/src/economy/ap-socio-economic-survey-2024-25.txt)
- **Q60, AP beaches and nearest towns** (Suryalanka–Bapatla, Manginapudi–Machilipatnam, Kothapatnam–Ongole, Perupalem–Narasapuram): AP Tourism and SES-type facts. Likely.
  - Suryalanka and Kothapatnam appear in AP SES 2024-25.
  - Perupalem appears only in a 2026 current-affairs file.

  — [ap-socio-economic-survey-2024-25.txt](/home/user/Group-app/data/notes2026/src/economy/ap-socio-economic-survey-2024-25.txt)
- **Q49, laterite soils (with the extent of laterite in AP)**: the NCERT XI soils definition (high temperature and heavy rainfall; suited to cashew) plus an AP-extent statement from AP geography. Clear fact match on the incorrect statement. — [prelims-2024.json](/home/user/Group-app/data/g2papers/prelims-2024.json)

**Prelims 2019: report-driven and Census questions**

- **Q119, "proportion of area covered by forest in India as of 2017 = 24.39%": India State of Forest Report 2017 (Forest Survey of India). Verbatim figure.**
  - 24.39% is ISFR 2017's total forest plus tree cover; forest cover alone was 21.54%, which is also an option.
  - Shankar Environment reproduces it: "The total forest and tree cover is 24.39 percent".

  — [shankar-environment-11.txt](/home/user/Group-app/data/notes2026/src/environment/shankar-environment-11.txt)
- **Q101 and Q102, Global MPI 2018** (Bihar poorest; 271 million moved out of poverty, 2005-06 to 2015-16): the UNDP-OPHI Global Multidimensional Poverty Index 2018 report. Verbatim figure from the report headline. No local copy was found. — [prelims-2019.json](/home/user/Group-app/data/g2papers/prelims-2019.json)
- **Q130, "India's HDI value increased by nearly 50 percent between 1990 and 2017"**: the UNDP HDR 2018 Statistical Update and UNDP India press release wording. Verbatim phrase; not verified locally. — [prelims-2019.json](/home/user/Group-app/data/g2papers/prelims-2019.json)
- **Census 2011 questions:**
  - **Q116**: highest Hindu share, Himachal Pradesh. Census 2011 religion tables. Clear fact match.
  - **Q136**: AP child sex ratio (0-6) keyed as 940. Census 2011. Likely. The undivided-AP Census figure is usually quoted as 939; the key used a rounded or residual-AP figure.

  — [prelims-2019.json](/home/user/Group-app/data/g2papers/prelims-2019.json)
- **Q30**: rainfall deficiency over 50% = "severe drought", the IMD classification. Clear fact match. **Q28**: ITIC in Honolulu, from UNESCO-IOC. — [prelims-2019.json](/home/user/Group-app/data/g2papers/prelims-2019.json)
- **Q33, Kanchenjunga 8,586 m**: Survey of India / standard figure. This one deliberately does **not** follow NCERT IX, which gives 8,598 m (not verified locally).
  - Local PMF and Rocket give "Kangchenjunga (8,586 m)".

  — [src/geography grep](/home/user/Group-app/data/notes2026/src/geography/)
- **Q34, Arwah caves (Meghalaya)**: appears in PMF Indian Physical Geography and in NextGen Indian Geography. Likely. — [pmf-indian-physical-geography-01.txt](/home/user/Group-app/data/notes2026/src/geography/pmf-indian-physical-geography-01.txt)
- **Q69, Cuddapah Basin as "the oldest landmass in AP"**: PMF says the region "is formed from the Gondwana land breakup, thus making it a part of the oldest landmass". This is AP geography (Telugu Akademi-type). Likely. — [pmf-indian-physical-geography-01.txt](/home/user/Group-app/data/notes2026/src/geography/pmf-indian-physical-geography-01.txt)
- **Q72, Polavaram first envisaged as "Ramapada Sagar" by Sonti Venkata Ramamurthy**: an AP irrigation-history fact that is a repeat PYQ. The CDI compilation of AP history Group 2 PYQs from 2000-2025 carries "Who said that the project named Ramapada Sagaram near Polavaram will be built?" with the answer Sir Sonti Venkataramamurthy. — [cdi-ap-history-g2-pyqs-2000-2025.txt](/home/user/Group-app/data/notes2026/src/ap-history/cdi-ap-history-g2-pyqs-2000-2025.txt)

**Prelims 2017: Agricultural Census 2010-11**

- **Q125 and Q126 use the Agricultural Census 2010-11** (Phase I). Average operational holding: 1.15 ha for all classes, 0.80 for SC and 1.52 for ST. Plus the claim that 85% of holdings hold only "x%" of the area. These are figures straight from the census report.
  - The stem says "small and medium". The census figure is for small plus marginal, about 85% of holdings with about 44% of area, yet the key marks 24.58%.
  - That suggests a garbled transcription from the report. Treat the key with caution.

  — [prelims-2017.json](/home/user/Group-app/data/g2papers/prelims-2017.json)

**Older papers: 2008 and 2012**

- **2012 Paper I: world places (9 questions).** Atlas Mountains, Tigris, Lop Nor, Dasht-e-Kavir, Mindanao, Cardamom Mountains (Cambodia), Lake Michigan, Takla Makan, Sagarmatha. These are atlas and Leong-type world regional place facts. Likely (Oxford/Orient Blackswan school atlas, or G.C. Leong). — [group2-2012-paper1.json](/home/user/Group-app/data/g2papers/group2-2012-paper1.json)
- **2012 Paper I: disaster management (19 questions).** The facts track Government of India disaster-management documents, the kind summarised in the local Rocket DM notes:
  - the Vulnerability Atlas by BMTPC
  - the High Powered Committee of 1999 (J.C. Pant)
  - Landslide Zonation Mapping since the 1980s
  - Ministry of Agriculture as nodal ministry for drought
  - the State Crisis Management Committee chaired by the Chief Secretary
  - the World Bank report "Managing Disaster Risk in Emerging Economies"

  Local hits include "High Powered Committee (1999) classified disasters into 5 broad categories" and "First Chairman of the High Powered Committee (HPC)". Clear fact match to the MHA/NIDM material. — [rocket-disaster-mgmt.txt](/home/user/Group-app/data/notes2026/src/disaster-mgmt/rocket-disaster-mgmt.txt)
- **2012 Q110, "Main worker... 183 days"**: the Census of India definition. Verbatim definition. Local notes read "Main Worker is a person who works for atleast 183 days (or six months) in a year". — [src grep hit](/home/user/Group-app/data/notes2026/src/)
- **2008 Paper III: AP data questions.** All are AP human and economic data from Census 2001 and the National Human Development Report 2001 (Planning Commission). Clear fact match by construction.
  - Q116: AP population 2001 about 7.5 crore.
  - Q112: AP female literacy 2001 about 50%.
  - Q84: rural to urban ratio 73:27.
  - Q83: AP growth below India's in 1991-2001.
  - Q101: NHDR 2001 HDI of AP below India's.
  - Q88: 2004-05 poverty in AP, urban higher than rural.
  - Q131: number of NHs in AP.

  — [group2-2008-paper3.json](/home/user/Group-app/data/g2papers/group2-2008-paper3.json)
- **2008 Paper I: textbook physical geography** (hygrometer, blizzards, jet stream, orographic rain, black soil = chernozem, haematite, bauxite) at school and NCERT or old school-textbook level.
  - One question names the scholar for the origin of the Earth from gases and dust as "O. Schmid". That is the standard Indian-textbook spelling of Otto Schmidt, which points to Indian textbook or guide sources (Khullar-type), not Leong.

  — [group2-2008-paper1.json](/home/user/Group-app/data/g2papers/group2-2008-paper1.json)

### Inferences
Ranking of sources by evidence for current-pattern prelims (2019 and 2024):

1. **NCERT XI *Fundamentals of Physical Geography* and *India: Physical Environment*.** Strongest: at least 3 verbatim (Q38, Q39 and, from memory, Q32) and about 8 clear fact matches in 2024.
2. **NCERT VI-VII *Our Environment* / *The Earth Our Habitat*.** Q35 verbatim from memory; Q33, Q34, Q40 and Q41.
3. **NCERT XII *India: People and Economy*, and X *Contemporary India II*.** Q52, Q53, Q54, Q56, Q57.
4. **Telugu Akademi / AP SCERT AP geography** (rivers, minerals, physiography), as inferred from the "Jayapur" spelling and the AP-specific item lists in Q48, Q59 and Q69.
5. **Government reports**: ISFR (FSI), UNDP HDR and Global MPI, IMD definitions, Census 2011, Agricultural Census. These dominate 2019 and 2017.
6. **AP Socio-Economic Survey, APIIC and AP Tourism**: Q55 and Q60. Likely, not verbatim.
7. **India Year Book / Indian Railways**: Q58.
8. **G.C. Leong, atlas**: only the 2012 world-place set. No 2019 or 2024 question needs Leong beyond NCERT.

- Majid Husain and Khullar are not needed for any 2019 or 2024 question I checked. The difficulty ceiling is NCERT level.
- Deleted or disputed items (Q31 and Q51 deleted; Q41 and Q54 accepting two keys) cluster where the examiner paraphrased a textbook loosely. That is further evidence of textbook-sentence framing.

### Gaps
- I could not check original NCERT PDFs or Telugu Akademi books. The "not verified locally" matches rely on my knowledge of the NCERT text.
- The sources of the Q55 APIIC cluster list and of the "Mudugal hills" and "Garividi" pairings were not found. Older AP SES editions or the Telugu Akademi AP Geography are the best candidates.
- The AP child sex ratio of 940 (Q136) does not exactly match the commonly cited Census figure of 939.
- The Agricultural Census figure keyed in 2017 Q126 (24.58%) looks inconsistent with the report.

## Q3. Patterns: share of AP-specific vs India vs world/physical geography; Census-based questions

### Takeaway
Current prelims (2024) splits roughly 1/3 world or physical geography, 1/2 India and 1/6 AP. 2019 had a similar split but swapped some physical theory for human-development and report data. Census or data-table questions appear in every paper. They are most frequent in the 2008 Mains-type Paper III (AP Census 2001) and recur in 2017 (Agricultural Census) and 2019 (Census 2011).

### Cited Findings
- **Prelims 2024 (30 Qs, my classification of the paper's questions):**

  | Group | Questions | Count | Share |
  |---|---|---|---|
  | World or general physical | 31-36, 38-41 | 10 | ~33% |
  | India | 37, 42-47, 50-54, 56-58 | 15 | 50% |
  | AP-specific | 48, 49, 55, 59, 60 | 5 | ~17% |
  | Census / data-table | — | 0 | — |

  Physical geography of India and AP (P2.1.6) is the single largest leaf with 10 questions. — [prelims-2024.json](/home/user/Group-app/data/g2papers/prelims-2024.json); [prelims-2024.leaves.json](/home/user/Group-app/data/g2papers/prelims-2024.leaves.json)
- **Prelims 2019 (20 Qs):**

  | Group | Questions | Count | Share |
  |---|---|---|---|
  | General or concept | 14, 28-30, 117, 118 | 6 | ~30% |
  | India | 33-36, 101, 102, 115, 116, 119, 130 | 10 | 50% |
  | AP | 69, 72, 73, 136 | 4 | 20% |
  | Census 2011 | 116, 136 | 2 | — |
  | Other reports (ISFR, MPI, HDR) | 101, 102, 119, 130 | 4 | — |

  Human geography (P2.3) took 8 of 20. — [prelims-2019.json](/home/user/Group-app/data/g2papers/prelims-2019.json)
- **2012 Paper I (35 geography-mapped Qs):**

  | Group | Count |
  |---|---|
  | Disaster management | 19 |
  | World places | 9 |
  | AP | 3 (Q59 floods in the Krishna-Godavari deltas, Q79 AP has the second-longest coastline, part of Q118 storm surge Ongole-Machilipatnam) |
  | Census definition | 1 (Q110) |

  — [group2-2012-paper1.json](/home/user/Group-app/data/g2papers/group2-2012-paper1.json)
- **2008:**
  - Paper I's 19 geography questions are almost all world or general physical, plus 7 basic India questions, with no AP questions.
  - Paper III's 24 geography-mapped questions include about 10 AP questions, at least 7 of them Census 2001 or NHDR data.

  — [group2-2008-paper1.json](/home/user/Group-app/data/g2papers/group2-2008-paper1.json); [group2-2008-paper3.json](/home/user/Group-app/data/g2papers/group2-2008-paper3.json)
- Census-type stems seen: "As per 2011 Census... highest proportion of Hindus", "child sex ratio (0-6) in AP", "Main worker... days", "Which State has the largest number of towns" (UP, Census 2001), "State with the lowest sex ratio" (Haryana), and AP population, literacy and rural-urban ratio from 2001. — [prelims-2019.json](/home/user/Group-app/data/g2papers/prelims-2019.json); [group2-2012-paper1.json](/home/user/Group-app/data/g2papers/group2-2012-paper1.json); [group2-2008-paper3.json](/home/user/Group-app/data/g2papers/group2-2008-paper3.json)
- Recurrence across years:
  - The Tropic of Cancer states appear in both 2008 (Q116) and 2019 (Q36).
  - Narmada falls appear as Marble Falls in 2012 (Q78) and as Dhuandhar in 2024 (Q44).
  - Minicoy and Lakshadweep appear in 2008 (Q117) and 2024 (Q37).
  - Black soil appears in 2008 (Q111, Q119) and 2024 (Q46).
  - Ramapada Sagar / Polavaram is a known repeat (2019 Q72; also in the CDI PYQ compilation).

  — [g2papers](/home/user/Group-app/data/g2papers/); [cdi-ap-history-g2-pyqs-2000-2025.txt](/home/user/Group-app/data/notes2026/src/ap-history/cdi-ap-history-g2-pyqs-2000-2025.txt)

### Inferences
- Under the 2023 syllabus (2024 paper), AP-specific geography is about 5 of 30 questions. In 2024 every AP question was a "Match the following" on lists (rivers and origins, minerals and districts, APIIC clusters, beaches and towns). That rewards list-heavy AP sources: Telugu Akademi AP Geography, AP SES and the AP Tourism / APIIC websites.
- Census 2011 and other report data (ISFR, HDR, MPI) entered through the human-geography leaves in 2019. Expect current-edition reports (ISFR 2021/2023, Census 2011 tables, Global MPI or HDR of the year) to be the source for P2.3 questions.
- Old (2008 and 2012) papers lean on world atlas facts and disaster management. Under the current syllabus, disaster management is one leaf (P2.1.7), and the 2024 paper asked none on it.

### Gaps
- My share figures are my own classification of 50 current-pattern questions, not a published analysis.
- The 2017 prelims used an older syllabus with no geography section, so it does not show the current pattern.
