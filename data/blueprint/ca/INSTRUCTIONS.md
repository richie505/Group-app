# Sorting the new current affairs (15 Oct - 4 Nov 2026) into the blueprint's current-affairs units

The daily files are text versions of current-affairs PDFs (ignore page footers, "Follow Us", youtube/mailto lines,
stray digits from the watermark, and scrambled passages). Every news item goes to exactly ONE of these units (the
best fit):

| Unit | What goes there |
|---|---|
| U0812 | Andhra Pradesh - government decisions, new schemes, appointments, administrative changes |
| U0813 | Andhra Pradesh - budget and Socio-Economic Survey highlights |
| U0814 | Andhra Pradesh - projects, investments, MoUs, industrial and infrastructure developments |
| U0815 | Andhra Pradesh - awards, GI tags, cultural events, sports and persons in news |
| U0816 | National - polity and governance: bills, acts, ordinances, rules, landmark judgments |
| U0817 | National - economy: budget, RBI policy, key data releases (GST, GDP, inflation), banking |
| U0818 | National - new central schemes, missions and their features |
| U0819 | National - committees, commissions and their reports |
| U0820 | International - summits, conferences and their outcomes |
| U0821 | International - treaties, agreements, international organisations |
| U0822 | International - bilateral visits, defence deals and exercises, geopolitical developments |
| U0823 | Science and technology in news - space, defence tests, health and biotech |
| U0824 | Environment in news - reports, species, protected areas, climate negotiations |
| U0825 | Reports and indices - releasing agency, India's rank, key findings |
| U0826 | Awards and honours |
| U0827 | Sports - tournaments, winners, records, hosting |
| U0828 | Books and authors; important days and their themes |
| U0829 | Persons in news - appointments, resignations, obituaries |

For each item write ONE line in your output file for its unit, in your own words, keeping every exam fact (names,
places, numbers, dates, ranks, firsts, themes, headquarters and founders given as "Additional Information"):

    - [16 Oct 2026] <headline>: <fact>; <fact>; <fact>

No markdown other than the leading "- ", no `|`. Facts only from the files.
Output: `data/blueprint/ca/<part>/<unit>.md` (only units that got items), where <part> is the folder name you are given.
