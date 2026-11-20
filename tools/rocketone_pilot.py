"""RocketOne pilot: Group 1 Prelims notes written ONLY from the NextGen Rocket Sheets and Rocket Current Affairs 2026,
as lecture slides (tools/lecture_pdf.py, the APPSC Lectures app's slides).

    python3 tools/rocketone_pilot.py   -> data/rocketone/pilot/assets/ (the notes, in the app's format)
                                          docs/rocketone/pilot-*.pdf   (the lectures)

Rules (owner, 20 Nov 2026):
  1. Only what Rocket says. Where Rocket is silent, nothing is added from any other source.
  2. Only where a Rocket line disagrees (with another Rocket line, or with the verified fact) is it settled from
     other sources; that is shown in a SETTLED box which first quotes what Rocket says.
Every line ends with its Rocket sheet in the notes file ("src"), not on the slide.
"""
import json, os, re, sys

sys.path.insert(0, os.path.dirname(__file__))
import lecture_pdf as LP

A = "data/rocketone/pilot/assets"
OUT = "docs/rocketone"
APP = "RocketOne · Group 1 Prelims"


def runs(t):
    """'**bold** plain' -> the app's runs"""
    out = []
    for i, p in enumerate(re.split(r"\*\*(.+?)\*\*", t)):
        if p:
            out.append([p, i % 2])
    return out


def blocks(items):
    out = []
    for it in items:
        k = it[0]
        if k == "t":
            out.append({"k": "t", "h": [runs(c) for c in it[1]], "r": [[runs(c) for c in r] for r in it[2]], "src": it[3]})
        else:
            out.append({"k": k, "x": runs(it[1]), **({"src": it[2]} if len(it) > 2 else {})})
    return out


AP, IH, CA = "AP History Rocket Sheet ", "Indian History Rocket Sheet ", "Rocket Current Affairs 2026 "

SATAVAHANA = [
    ("Founder, capital and identity", [
        ("b", "**First historical ruling dynasty of the Deccan:** the **Satavahanas**.", AP + "#1, #35"),
        ("b", "**Founder:** **Simuka** (Simukha); also written **Sindhuk / Shiprak**.", AP + "#16; " + IH + "#4"),
        ("b", "**Earlier link:** Simuka came after **Susharma** of the **Kanva** dynasty.", IH + "#29"),
        ("b", "**Capital:** **Paithan**.", AP + "#31, #43"),
        ("b", "**Caste of the Satavahanas:** **Brahmins**.", AP + "#45"),
        ("b", "**Home of the Satavahanas:** Sukthankar located them in **Bellary**, from the **Myakadoni** inscription.", AP + "#3"),
        ("s", "Rocket prints the name as \"V.V. Sukthankar\". The scholar is **V.S. Sukthankar** (Vishnu Sitaram Sukthankar), "
              "who put the Satavahana home in Bellary.", "name checked: Indian Antiquary vol. 48 (1919)"),
    ]),
    ("Rulers, queens and titles", [
        ("t", ["Ruler / queen", "What to remember"], [
            ["**Simuka**", "Founder of the dynasty"],
            ["**Satakarni I**", "The **Nanaghat** inscription is important for his governance"],
            ["**Devi Naganika**", "Queen who acted as **regent** during the minority of her son"],
            ["**Hala**", "Title **Kavivatsala**; author of **Gatha Saptasati**"],
            ["**Gautamiputra Satakarni**", "Defeated **Nahapana**; titles **Thrisamudrapati**, **Ekabrahmana** (unrivalled Brahmana) and **Rajaraja**"],
            ["**Gautami Balasri**", "Issued the **Nasik** inscription during the reign of Vasishtiputra Pulomavi"],
            ["**Vasishtiputra Pulomavi**", "The Nasik inscription of Gautami Balasri belongs to his reign"],
            ["**Pulomavi and Yagnasri**", "Their coins indicate Satavahana **maritime trade**"],
            ["**Chanda Satakarni**", "The **Kodavali** inscription is his"],
        ], AP + "#3, #5, #16, #27, #36, #42, #44; " + IH + "#11, p.8"),
        ("b", "**Anupa** under Gautamiputra Satakarni: capital **Mahishmathi**.", AP + "#31, #43"),
        ("b", "**Nagalapuram (Palnadu):** ancient name **Hala**.", AP + "#20"),
        ("h", "The last ruler"),
        ("b", "**Last ruler of the Satavahanas as per the Puranas:** **Pulomavi III**.", AP + "#2"),
        ("b", "**Myakadoni inscription:** of **Pulumavi IV**, called the last Satavahana king.", AP + "#3"),
        ("s", "Rocket gives two numbers for the last king: Pulomavi III (Sheet #2) and Pulumavi IV (Sheet #3). Both stand, for "
              "different questions: **\"as per the Puranas\" = Pulomavi III**; the king of the **Myakadoni inscription = "
              "Pulumavi IV**, the last king of the main line in the historians' count.",
         "en.wikipedia.org/wiki/List_of_Satavahana_kings; gktoday.in (Puranas: Pulomavi III)"),
        ("h", "Contemporary"),
        ("b", "**Kharavela:** Rocket lists him as a contemporary of **Hala**.", AP + "#23"),
        ("s", "Rocket says Kharavela was a contemporary of Hala. Kharavela's own **Hathigumpha inscription** names "
              "**Satakarni** as the Satavahana king of his time, identified with **Satakarni I** (husband of Naganika), not Hala.",
         "en.wikipedia.org/wiki/Satakarni; Epigraphia Indica vol. 20"),
    ]),
    ("Inscriptions", [
        ("t", ["Inscription", "Issued by / related to", "Key fact"], [
            ["**Nasik** (Gautami Balasri)", "Gautami Balasri, during Vasishtiputra Pulomavi", "Military achievements of **Gautamiputra Satakarni**; title **Ekabrahmana**"],
            ["**Nasik** (Ushavadatta)", "Western Kshatrapa / Satavahana era", "**Ushavadatta (Rishabhadatta)** invested **2,000 Karshapanas** in a weavers' guild at **Govardhana**; interest **12%**"],
            ["**Nanaghat**", "Satavahana", "Satakarni I's governance; Satavahana administration"],
            ["**Myakadoni**", "Pulumavi IV", "Sukthankar located the Satavahanas in Bellary; **\"Gulmika\"** = feudatory chief"],
            ["**Kodavali**", "Chanda Satakarni", "Inscription of Chanda Satakarni"],
            ["**Bhattiprolu**", "Raja Kubhiraka", "Mentions the **'Nigama-sabha'** of the Satavahanas; ruler Kubhiraka (3rd century BC)"],
        ], AP + "#3, #4, #27, #30; " + IH + "p.8"),
        ("s", "Rocket Sheet #3 puts the Ushavadatta investment inside Gautami Balasri's Nasik inscription; Sheet #30 gives it as a "
              "separate Nasik inscription of the Western Kshatrapa era. Sheet #30 is right: they are **two different Nasik cave "
              "inscriptions** - Balasri's praises Gautamiputra Satakarni; Ushavadatta's (son-in-law of Nahapana) records the guild deposit.",
         "Epigraphia Indica vol. 8 (Senart), Nasik inscriptions no. 2 and no. 12"),
        ("b", "**Language and script:** all Satavahana inscriptions are in **Prakrit**, in the **Brahmi** script.", AP + "#11"),
        ("b", "**Earliest epigraphic record of religious land grants:** **Satavahana inscriptions**.", IH + "#30, #90"),
    ]),
    ("Administration", [
        ("t", ["Term", "Meaning"], [
            ["**Aharas**", "Administrative divisions of the Satavahana empire"],
            ["**Amatyas**", "Officers who administered the Aharas"],
            ["**Mahasenadhipathulu**", "Military officers who administered Aharas far from the capital"],
            ["**Visvamaatyulu**", "Royal employees consulted for important decisions"],
            ["**Rajaamatyas**", "Advisors"],
            ["**Mahaamatyas**", "Special officers helping the king"],
            ["**Mantri Parishad**", "Helped the king in administration"],
            ["**Nigama Sabha**", "Looked after the administration of cities / towns"],
            ["**Gramani**", "Jurisdiction over **5 or 10 villages**"],
            ["**Gaaha Pati**", "**Karshaka Pratinidhi** - representative of farmers"],
            ["**Gulmika**", "Feudatory chief (Myakadoni inscription)"],
        ], AP + "#3, #10, #38"),
    ]),
    ("Economy - revenue, guilds and trade", [
        ("h", "Revenue"),
        ("b", "**Land revenue:** the chief source of income.", AP + "#37"),
        ("b", "**Bhodga / Deeva Meeya:** the king's share in the produce raised by a peasant.", AP + "#37"),
        ("b", "**Kaarukara:** duty (sistu) paid by professionals.", AP + "#37"),
        ("h", "Guilds"),
        ("b", "**Guilds / Srenulu:** associations that helped the development of trade.", AP + "#9, #30, #37"),
        ("b", "**Kolika:** the weavers' guild.", AP + "#30, #37"),
        ("b", "**Rate of interest on deposits in guilds:** **12%**.", AP + "#30, #37"),
        ("b", "**Vadhika:** carpenters.", AP + "#24"),
        ("h", "Trade"),
        ("b", "**Flourishing maritime trade** was a feature of the Satavahana period; the coins of **Pulomavi** and **Yagnasri** indicate it.", AP + "#9, #14"),
        ("b", "**Motupalli:** a seaport of the Satavahanas.", AP + "#8, #30"),
        ("s", "Rocket calls Motupalli the \"Western seaport\" of the Satavahanas. Motupalli is on the **east coast** (Bay of Bengal, "
              "Bapatla district, Andhra Pradesh), so it is an eastern, not a western, seaport.", "location: Motupalli, Bapatla district (AP)"),
    ]),
    ("Coinage", [
        ("b", "**Metals of Satavahana coins:** **Lead + Copper + Bronze + Silver + Potin**; lead and copper were the major metals.", IH + "#12, #35"),
        ("b", "**Metal absent:** **Gold** - no gold coins.", IH + "#12, #35"),
        ("b", "**Nickel** was NOT used by the Satavahanas.", AP + "#14"),
        ("b", "**Potin:** an alloy / mixture used in Satavahana coinage.", IH + "#12"),
        ("s", "Rocket gives potin as \"Copper + Silver + Lead\". Potin is a base-metal alloy of **copper, tin and lead** - "
              "it has no silver.", "numista.com (potin karshapana); numismatic glossaries"),
        ("b", "**Karpanamulu:** copper coins.", AP + "#14"),
        ("b", "**Coins of Pulomavi and Yagnasri:** indicate maritime trade.", AP + "#9, #14"),
    ]),
    ("Society, language and literature", [
        ("b", "**Fourfold caste system** existed during Satavahana rule.", AP + "#45"),
        ("b", "**Prakrit:** the official language; the Satavahana rulers patronised Prakrit.", AP + "#11; " + IH + "#32"),
        ("b", "**Desi Bhaasha:** the language of the common people; belongs to the **Dravidian** family.", AP + "#11"),
        ("b", "**Gatha Saptasati (Gathasaptasati):** by **Hala**; it contained writing by women.", AP + "#5, #41, #46"),
        ("b", "**Aradalam:** the foundation cream used by Satavahana dancers.", AP + "#20"),
        ("b", "**Itsing** (post-Satavahana era): Chinese traveller; saw students learning **\"Sushrullekha\"** by heart.", AP + "#23"),
    ]),
    ("Religion", [
        ("t", ["Who", "Religion patronised"], [
            ["**Satavahana rulers**", "**Vedic** religion"],
            ["**Satavahana queens**", "**Buddhism**"],
        ], AP + "#28, #34, #41"),
        ("b", "**Chaityams:** built by the **queens of the Satavahanas** for Buddhist monks.", AP + "#18"),
    ]),
    ("Art and architecture", [
        ("b", "The Satavahanas patronised **public arts** and **Buddhist architecture and sculpture**.", IH + "#32"),
        ("h", "Amaravati Stupa"),
        ("b", "Built during **Satavahana** rule.", AP + "#18, #24"),
        ("b", "**Ayaka pillars** represent the **five key events** in the Buddha's life.", AP + "#18"),
        ("b", "On the **right bank of the Krishna** river, Andhra Pradesh; **Colin Mackenzie** traced it in **1797**.", IH + "#66"),
        ("h", "Caves"),
        ("t", ["Caves", "Place", "Key fact"], [
            ["**Ajanta** - earlier phase", "Maharashtra", "The earlier caves are of the **Satavahana** phase (the later phase is Vakataka)"],
            ["**Nasik / Pandavleni**", "Maharashtra", "Buddhist; Satavahana period; Buddhist devotional practices"],
            ["**Karla**", "Maharashtra", "Buddhist; Satavahana period; **largest and most evolved Hinayana Chaitya**"],
        ], IH + "#76; Indian History Rocket Sheets part 2, p.17"),
    ]),
]

SPACE = [
    ("Satellites and missions at a glance", [
        ("t", ["Satellite / mission", "Organisation / country", "Notes"], [
            ["**EOS-05**", "ISRO", "Earth-observation satellite; launched **4 September 2026** on **GSLV-F17**"],
            ["**MOI-1A**", "TakeMe2Space, India", "**India's first orbital computing satellite**; AI-based data processing in space"],
            ["**Pathfinder**", "Pixxel and Sarvam, India", "**India's first orbital data-centre satellite**; announced 4 May 2026"],
            ["**BlueBird Block-2**", "AST SpaceMobile, USA", "Communication satellite launched by ISRO's **LVM3-M6** on **24 December 2025**"],
            ["**BlueBird 1-5**", "AST SpaceMobile", "Five satellites launched in September 2024; direct-to-smartphone constellation"],
            ["**SOLAR-1**", "NOAA, USA", "First US satellite designed exclusively for continuous operational space-weather observations"],
            ["**SWFO-L1**", "NOAA, USA", "Earlier name of SOLAR-1: Space Weather Follow-On-Lagrange 1"],
            ["**MMX**", "JAXA, Japan", "Martian Moons eXploration mission; launched **20 October 2026**"],
            ["**Aditya-L1**", "ISRO", "Solar-observation mission; more than **37 terabytes** of data made public by October 2026"],
            ["**Sputnik-1**", "Soviet Union", "First artificial satellite; launched 4 October 1957"],
            ["**Artemis II / Orion**", "NASA, USA", "Crewed lunar-flyby mission; the crew named the spacecraft **Integrity**"],
            ["**Chandrayaan-3**", "ISRO", "The Vikram lander did a controlled **hop experiment** on the lunar surface"],
        ], CA + "#17, p.116"),
        ("b", "**Autonomous satellite docking:** **SpaDeX**.", CA + "#17, p.125"),
    ]),
    ("EOS-05 - imaging from geosynchronous orbit", [
        ("x", "**EOS-05** is identified as **India's first satellite to carry out imaging from a geosynchronous orbit**."),
        ("t", ["Parameter", "Notes"], [
            ["Type", "Earth-observation satellite"],
            ["Launch date", "**4 September 2026**"],
            ["Launch vehicle", "**GSLV-F17**"],
            ["Launch centre", "Satish Dhawan Space Centre, **Sriharikota**"],
            ["Orbit", "**Geosynchronous** orbit"],
            ["Engine for orbit-raising", "Liquid Apogee Motor"],
            ["Launch organisation", "ISRO"],
        ], CA + "#17, p.117"),
    ]),
    ("Computing in orbit - MOI-1A and Pathfinder", [
        ("h", "MOI-1A - India's first orbital computing satellite"),
        ("b", "**Developer:** **TakeMe2Space** (India).", CA + "#17, p.117"),
        ("b", "**Use:** AI-based data processing in space; reference date 2 October 2026.", CA + "#17, p.117"),
        ("h", "Pathfinder - India's first orbital data-centre satellite"),
        ("b", "**Announced:** 4 May 2026; Indian company **Pixxel**, AI partner **Sarvam**.", CA + "#17, p.118"),
        ("b", "**Purpose:** run AI models and process data in orbit; a single-satellite demonstrator.", CA + "#17, p.118"),
        ("b", "**Payload:** hyperspectral imaging payload; production facility **Gigapixxel** (Pixxel's upcoming facility).", CA + "#17, p.118"),
        ("h", "What is an orbital data centre?"),
        ("b", "A space-based computing system: satellites carry high-performance processors such as data-centre-class **GPUs**.", CA + "#17, p.118"),
        ("b", "AI models run directly in orbit; data is processed closer to where it is generated.", CA + "#17, p.118"),
        ("b", "Less dependence on sending large volumes of raw satellite data to ground data centres; similar to **edge computing**.", CA + "#17, p.118"),
    ]),
    ("BlueBird Block-2 and the LVM3-M6 mission", [
        ("t", ["Parameter", "Notes"], [
            ["Satellite", "**BlueBird Block-2** - commercial communication satellite"],
            ["Company", "**AST SpaceMobile**, USA"],
            ["Launch", "**24 December 2025** on **LVM3-M6** (ISRO)"],
            ["Orbit", "Low Earth Orbit"],
            ["Payload mass", "**6,100 kg**"],
            ["Phased-array area", "223 m²"],
            ["Main application", "**Direct-to-smartphone** connectivity"],
        ], CA + "#17, p.118-119"),
        ("h", "LVM3-M6 mission milestones"),
        ("b", "**104th** launch from Sriharikota.", CA + "#17, p.119"),
        ("b", "**Ninth** successful LVM3 mission; **third** dedicated commercial mission.", CA + "#17, p.119"),
        ("h", "AST SpaceMobile's BlueBird constellation"),
        ("b", "BlueBird 1-5 were launched in September 2024.", CA + "#17, p.119"),
        ("b", "Aim: cellular broadband directly to smartphones - 4G and 5G voice and video calls, text messaging, streaming and data.", CA + "#17, p.119"),
    ]),
    ("SOLAR-1 - space-weather satellite", [
        ("t", ["Parameter", "Notes"], [
            ["Current name", "**SOLAR-1** - Space Weather Observations at L1 to Advance Readiness-1"],
            ["Previous name", "**SWFO-L1**"],
            ["Operator", "**NOAA**, United States"],
            ["Launch", "24 September 2025; SpaceX Falcon 9; Kennedy Space Center, Florida"],
            ["Orbit", "**Sun-Earth Lagrange Point 1 (L1)**"],
            ["Operational date", "10 June 2026"],
        ], CA + "#17, p.119"),
        ("h", "Purpose"),
        ("b", "Continuous monitoring of space weather; observing solar activity and its effects on the space environment.", CA + "#17, p.120"),
        ("b", "Early warning of solar events that may affect technological infrastructure and space missions.", CA + "#17, p.120"),
        ("b", "Data goes to NOAA's **Space Weather Prediction Center (SWPC)**, which issues forecasts, watches, warnings and alerts.", CA + "#17, p.120"),
    ]),
    ("MMX - Martian Moons eXploration", [
        ("t", ["Parameter", "Notes"], [
            ["Agency", "**JAXA** (Japan)"],
            ["Launch", "**20 October 2026**; H3 Flight No. 10; Tanegashima Space Center, Japan"],
            ["Target", "**Phobos and Deimos**"],
            ["Planned duration", "About five years"],
            ["Expected arrival at Mars", "2027"],
            ["Expected sample return", "2031"],
            ["Sample objective", "At least **10 grams from Phobos**"],
            ["Mission objective", "**First sample return from the Martian system**"],
        ], CA + "#17, p.120"),
        ("h", "Technical features"),
        ("b", "Three spacecraft modules: propulsion, exploration and return; solar panels for electricity; chemical propulsion for manoeuvres.", CA + "#17, p.120"),
        ("b", "Uses a quasi-satellite orbit around Mars near Phobos; carries **13** mission instruments.", CA + "#17, p.120"),
        ("b", "**TENGOO:** about 40 cm imaging resolution. **OROCHI:** images at multiple wavelengths. **LIDAR:** surface distance by laser pulses.", CA + "#17, p.120"),
        ("b", "**Collaboration:** Japan, France, Germany and USA.", CA + "#17, p.123"),
    ]),
    ("GAGAN and NavIC", [
        ("t", ["Feature", "GAGAN", "NavIC"], [
            ["Full form", "**GPS Aided GEO Augmented Navigation**", "**Navigation with Indian Constellation**"],
            ["Nature", "Satellite-Based Augmentation System (**SBAS**)", "Regional Navigation Satellite System"],
            ["Main purpose", "Augments GPS signals - better accuracy and integrity", "Provides positioning, navigation and timing"],
            ["Main application", "Precise aircraft navigation and landing", "Regional navigation services"],
            ["Developed by", "**ISRO and AAI**", "ISRO"],
        ], CA + "#17, p.121"),
        ("b", "**GAGAN in numbers:** **3** geostationary satellites, **15** reference stations, **2** master control centres, **3** land uplink stations.", CA + "#17, p.125"),
        ("h", "First satellite-based landing demonstration"),
        ("b", "Late June 2026: **DGCA** supervised India's first Satellite-Based Landing System approach by a commercial jet using GAGAN.", CA + "#17, p.121"),
        ("b", "**Aircraft:** IndiGo **Airbus A321**; satellite-derived guidance was used instead of a conventional Instrument Landing System (ILS).", CA + "#17, p.121"),
    ]),
    ("India's first indigenous commercial EO constellation", [
        ("t", ["Parameter", "Notes"], [
            ["Programme", "Earth Observation Public-Private Partnership (**EO-PPP**)"],
            ["Agency", "**IN-SPACe**"],
            ["Consortium", "**Pixxel-led Allied Orbits**; lead company Pixxel Space India"],
            ["Agreement date", "21 January 2026"],
            ["Planned investment", "More than **₹1,200 crore**, over five years from January 2026"],
            ["Number of satellites", "**12**"],
            ["Planned operationalisation", "By **2029**"],
            ["Announcement / official statement", "12 August 2026"],
        ], CA + "#17, p.122"),
        ("h", "Satellite sensor technologies"),
        ("t", ["Sensor / data type", "Application"], [
            ["**Panchromatic**", "High-resolution black-and-white imaging"],
            ["**Multispectral**", "Data across selected spectral bands"],
            ["**Hyperspectral**", "Detailed information across many narrow spectral bands"],
            ["**Microwave SAR**", "Radar-based imaging, including in cloud-covered conditions"],
        ], CA + "#17, p.122"),
        ("b", "**Major applications:** climate-change monitoring, disaster management, agriculture and crop monitoring, infrastructure "
              "planning, geospatial services, governance and public-service delivery.", CA + "#17, p.122"),
    ]),
    ("Satellite imagery for agriculture; space cooperation", [
        ("t", ["Model", "Full form", "Function"], [
            ["**ALU**", "Agricultural Landscape Understanding", "Maps field boundaries, trees, woodlands, wells and small irrigation structures"],
            ["**AMED**", "Agricultural Monitoring and Event Detection", "Tracks crop activity, likely crops, sowing and harvesting periods"],
        ], CA + "#17, p.123"),
        ("b", "**Applications:** agricultural landscape mapping, crop monitoring, agricultural credit, water management, policy planning, sustainable rice cultivation.", CA + "#17, p.123"),
        ("h", "Satellite-related international cooperation and defence"),
        ("t", ["Initiative / agreement", "Countries / organisations", "Notes"], [
            ["India-Japan defence cooperation", "India and Japan", "Satellite-based maritime awareness; **JAIMEX 25** and naval cooperation"],
            ["US-Denmark-Greenland Arctic Defence Agreement", "USA, Denmark and Greenland", "**Pituffik Space Base** supports satellite tracking and space surveillance"],
            ["**G20 Open Satellite Data Partnership**", "Proposed by India", "Proposed initiative for global data cooperation"],
            ["India-EU cooperation", "India and EU", "Space and technology cooperation in the broader strategic engagement"],
            ["**LUPEX / Chandrayaan-5**", "India and Japan", "Lunar polar exploration mission"],
            ["**SMILE**", "Chinese Academy of Sciences and ESA", "Joint space mission"],
        ], CA + "#17, p.123"),
    ]),
]

BOOKS = [
    {"id": 1, "title": "History & Culture (Indian and Andhra Pradesh)", "short": "History & Culture",
     "unit": "Indus Valley Civilization, Vedic Age, Mahajanapadas, Jainism & Buddhism, Magadha, Mauryas, Foreign Invasions, "
             "Kushanas, Satavahanas, Sangam Age, Sungas, Gupta Empire",
     "row": "The Satavahanas", "leaves": ["A1/11"], "secs": SATAVAHANA, "pdf": "pilot-1-satavahanas.pdf",
     "from": "AP History Rocket Sheets (73 pages) and Indian History Rocket Sheets (262 pages)"},
    {"id": 2, "title": "Current Affairs and Current Events", "short": "Current Affairs",
     "unit": "Science and technology in news - space missions, defence tests, health and biotech developments",
     "row": "Space and satellites in news", "leaves": ["E20/2", "G/2", "G/3"], "secs": SPACE, "pdf": "pilot-2-space-in-news.pdf",
     "from": "Rocket Current Affairs 2026, Sheet #17 (pages 116-125)"},
]

os.makedirs(A, exist_ok=True)
os.makedirs(OUT, exist_ok=True)
index, pairs = {"books": []}, []
for b in BOOKS:
    secs = [{"t": t, "badges": [], "b": blocks(items)} for t, items in b["secs"]]
    row = {"codes": [], "tag": "GROUP-I", "title": b["row"], "secs": secs, "src": [b["from"]]}
    json.dump({"id": b["id"], "title": b["title"], "short": b["short"], "units": [{"code": "", "title": b["unit"], "rows": [row]}]},
              open(f"{A}/book{b['id']}.json", "w"), ensure_ascii=False, indent=1)
    json.dump({"rows": {}, "units": {}, "subs": {}}, open(f"{A}/mcq{b['id']}.json", "w"))
    index["books"].append({"id": b["id"], "title": b["title"], "short": b["short"], "units": [{"title": b["unit"]}],
                           "rows": [{"u": 0, "title": b["row"], "leaves": b["leaves"], "q": 0}]})
json.dump(index, open(f"{A}/index.json", "w"), ensure_ascii=False, indent=1)
for b in BOOKS:
    h = LP.build(A, b["id"], 0, f"{OUT}/{b['pdf']}", APP)
    pairs.append((h, f"{OUT}/{b['pdf']}"))
    n = sum(len(i) for _, i in b["secs"])
    fixes = sum(1 for _, i in b["secs"] for x in i if x[0] == "s")
    print(f"{b['row']}: {len(b['secs'])} parts, {n} blocks, {fixes} settled")
LP.render(pairs)
for h, _ in pairs:
    os.unlink(h)
