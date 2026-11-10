# PYQ web check: deep

Model claude-sonnet-5-5, effort medium, web search (max 3), Message Batches API. 1079 PYQs decided, 0 paused mid-search (run resume), 22 failures.

| Decision | PYQs |
|---|---|
| KEEP | 493 |
| KEY | 224 |
| UNSURE | 362 |

Tokens: input 52,409,316, output 1,593,408; web searches 2,472.
Cost: $85.10 ($7.89 per 100 PYQs).
keys_apply.py file: data/keys/out/10.md

## Failures

- yd04ea4bce3d: no verdict line in g146 (stop_reason=tool_use)
- y6fd099b5a50: no verdict line in g146 (stop_reason=tool_use)
- yb3b3672650a: no verdict line in g146 (stop_reason=tool_use)
- yf7f553cdcd8: no verdict line in g146 (stop_reason=tool_use)
- ye9e5c7a9cef: no verdict line in g260 (stop_reason=tool_use)
- yab9287bdeba: no verdict line in g260 (stop_reason=tool_use)
- y9ea29c991e3: no verdict line in g260 (stop_reason=tool_use)
- y42e4efccaa9: no verdict line in g260 (stop_reason=tool_use)
- yb0adc6e9c71: no verdict line in g237 (stop_reason=end_turn)
- y5eeac1ea1db: no verdict line in g118 (stop_reason=tool_use)
- yb3085abc950: no verdict line in g118 (stop_reason=tool_use)
- yc0c058a14d0: no verdict line in g118 (stop_reason=tool_use)
- yb375ee3365c: no verdict line in g118 (stop_reason=tool_use)
- y78c67ef841a: no verdict line in g2 (stop_reason=tool_use)
- yf711206c1ac: no verdict line in g2 (stop_reason=tool_use)
- y1dc61c701db: no verdict line in g2 (stop_reason=tool_use)
- y8ec177b7334: no verdict line in g2 (stop_reason=tool_use)
- yd2c27589650: no verdict line in g75 (stop_reason=end_turn)
- y6ceb35ca4cd: no verdict line in g131 (stop_reason=tool_use)
- y2b1b9be6370: no verdict line in g131 (stop_reason=tool_use)
- y76e48714cfc: no verdict line in g131 (stop_reason=tool_use)
- y0e28b793ac9: no verdict line in g131 (stop_reason=tool_use)

## Key changes

- `y0ca4d24be2f` [BPSC (Pre) 2018] Which one of the following most appropriately describes the nature of the ‘Green Revolution’ of the late sixties of 20th century?
  (3) High-Yielding Varieties Programme → (4) Seed-Fertiliser-Water Technology. The Green Revolution was a package technology of seed, fertiliser and water, in which HYV seeds are only the core component, so 'Seed-Fertiliser-Water Technology' best describes its nature. (https://www.egyankosh.ac.in/bitstream/123456789/62780/1/Block-4.pdf)
- `yf121b994e8b` [Astt. Comm. 2017] Which one of the following statements about Allahabad Prashasti is correct?
  (3) Line 23 refers to Samudragupta violently exterminating a number of kings of Aryavarta. → (1) It clearly present the Gupta empire as the epicentre of a complex web of varied political relationship.. For UPSC CAPF (AC) 2017 Q59 the answer given by gkscientist and Testbook is (a)/option 1, that the Allahabad Prashasti presents the Gupta empire as the epicentre of a complex web of varied political relationships. (https://gkscientist.com/capf-exam-2017-solved/)
- `y9c756784abb` [APPSC AP History PYQ] Where was the first meeting of the Krishna District Congress Association held?
  none → (2) Guntur. The 1st meeting of the Krishna District Congress Association was held at Guntur (per the APPSC Group 2 2012 Paper 2 bit-bank; the official key itself was not opened). (https://aphistorybitbank.blogspot.com/2013/09/appsc-group-2-2012-paper-2-group-2.html)
- `y57c4dab1a89` [APPSC AP History PYQ] Who was the woman who gave great service to Buddhism during the time of the Ikshvakus?
  (1) Bapisiri → (3) Bodhisiri. Upasika Bodhisiri is the woman credited with great service to Buddhism during the Ikshvaku (Virapurushadatta) period (per the APPSC Group 2 2012 Paper 2 bit-bank; the official key itself was not opened). (https://aphistorybitbank.blogspot.com/2013/09/appsc-group-2-2012-paper-2-group-2.html)
- `y5400bef73cb` [APPSC Gazetted Posts GS 2010 (Notification 30/2008)] Which temple town is known as Dakshina Dwaraka?
  none → (3) Guruvayur. Guruvayur in Kerala, home of the Guruvayurappan Krishna temple, is known as Dakshina Dwaraka (Dwaraka of the South). (https://en.wikipedia.org/wiki/Guruvayur)
- `yb0620b67c10` [APPSC Gazetted Posts GS 2010 (Notification 30/2008)] Who was the Governor General of India when the Revolt of 1857 took place?
  none → (1) Canning. Lord Canning was Governor-General of India (1856-58) during the Revolt of 1857, and became the first Viceroy in 1858. (https://en.wikipedia.org/wiki/Charles_Canning,_1st_Earl_Canning)
- `y1ce91343cd5` [APPSC Group-I 2017] What was the practice adopted by the Vijayanagar Kings to protect the inhabitants within a fortified area from starvation due to sieges by enemy armies?
  (1) Large granaries were built within the fortified area to store grains → (3) Large agricultural tracts were incorporated within the fortified area. Per NCERT (Themes in Indian History II, ch. 7), granaries were the ordinary measure against sieges, while the Vijayanagara rulers adopted the more elaborate strategy of enclosing agricultural tracts within the fortified area. (https://sathee.iitk.ac.in/sathee-ssc/student-corner/ncert-books/class-12/themes-in-indian-history/chapter-07-an-imperial-capital-vijayanagara/)
- `ya2b47f41b11` [APPSC Group-I 2017] What is the amount of special assistance provided by the Central Government to Andhra Pradesh in 2016-17?
  (3) Rs 1,176.50 Cr → (2) Rs 1,976.50 Cr. PIB states the Centre provided Special Assistance of Rs 1,976.50 crore to Andhra Pradesh in 2016-17 (Rs 1,176.50 cr resource gap + Rs 350 cr backward districts + Rs 450 cr capital); Rs 4,058.04 cr was total central assistance released that year. (https://www.pib.gov.in/newsite/PrintRelease.aspx?relid=159289&reg=48&lang=2)
- `ya63ec01a2c4` [APPSC Group-I 2019 (26-05-2019)] Who is the winner of United Nations Human Rights Prize 2018 in the field of activities for the rights of Women and Girls?
  (4) All three Ms. Joenia Wapichana, Ms. Asma Jahangir and Ms. Rebeca Gyumi → (3) Ms. Rebeca Gyumi only. OHCHR lists Rebeca Gyumi (Tanzania) as the 2018 UN Human Rights Prize winner as activist for the rights of women and girls, while Asma Jahangir was honoured as a human rights lawyer and Joênia Wapichana for indigenous communities' rights. (https://www.ohchr.org/EN/NewsEvents/Pages/hrprize2018.aspx)
- `yf6bfb94e7a8` [SSC 2017] Who among the following supports customary rights?
  (2) Locke → (1) Ritchie. Ritchie supported customary rights, linking them to natural rights, so the correct option is Ritchie, not Locke. (https://www.gktoday.in/question/who-among-the-following-supports-customary-rights)
- `ydc30c8e58aa` [APPSC Group-1 PYQ] Who defeated Harsha and assumed the title 'Parameshwar'?
  (1) Pulakesin I → (2) Pulakesin II. Pulakesin II defeated Harsha on the Narmada and assumed the title Parameshvara (Aihole inscription); Pulakesin I lived before Harsha's reign, so he cannot be the answer. I could not open the official key. (https://en.wikipedia.org/wiki/Pulakeshin_II)
- `y1eefd1f200c` [U.P. R.O./A.R.O. (Pre) 2023] Which statements is/are true regarding Lord Curzon?
1. Establishing the English Empire on granite rock.
2. Announcement of Calcutta Municipal Act.
Select the correct answer the code given below : Code -
  (1) Both 1 and 2 → (3) Only 2. Only statement 2 is true: the Calcutta Municipal (Corporation) Act was passed in 1899 under Curzon, while the 'empire on granite rock' claim is marked incorrect in the UPPSC RO/ARO solutions (Testbook, StudyIQ); the official key was not seen. (https://testbook.com/question-answer/which-statements-isare-true-regarding-lord-curzo--65cb158d010a8de8332474e1)
- `yafd99ca3eca` [U.P.R.O./A.R.O. (Pre) (Re-Exam) 2016 +1 more] Which of the following statements is NOT true about the "Quit India Movement of 1942"?
  (4) It was a spontaneous movement → (3) It was a non-violent movement. Quit India is treated as a spontaneous mass movement (UPSC 2011 counts 'spontaneous' as true), the Congress committees were declared unlawful and Gandhi led it, but violence became widespread after the leaders' arrest, so 'it was a non-violent movement' is the NOT-true statement. (https://testbook.com/question-answer/which-of-the-following-statement-is-not-true-about--5f8420c31c24f7f42f62ef7a)
- `ye95d7045a20` [APPSC Gazetted Posts GS 2010 (Notification 30/2008)] What is the language of the Sangam literature?
  none → (3) Tamil. Sangam literature is the classical literature composed in the Tamil language. (https://en.wikipedia.org/wiki/Sangam_literature)
- `y0d98e419362` [APPSC Gazetted Posts GS 2010 (Notification 30/2008)] Who is the founder of the All India Harizan Sangh?
  none → (1) Mahatma Gandhi. Mahatma Gandhi founded the All India Harijan Sangh (Harijan Sevak Sangh, originally the All India Anti-Untouchability League) in 1932. (https://en.wikipedia.org/wiki/Harijan_Sevak_Sangh)
- `y3ca5c136b34` [APPSC Gazetted Posts GS 2010 (Notification 30/2008)] Who is the first Prime Minister of the Federal Democratic Republic of Nepal?
  none → (2) Pushpa Kamal Dahal (Prachanda). Pushpa Kamal Dahal 'Prachanda' became the first Prime Minister of the Federal Democratic Republic of Nepal in August 2008; Ram Baran Yadav was its first President. (https://en.wikipedia.org/wiki/Pushpa_Kamal_Dahal)
- `y0055d912b5f` [APPSC Gazetted Posts GS 2010 (Notification 30/2008)] The first Indian scholar who treated Mathematics as a distinct subject was
  none → (3) Aryabhatta. Aryabhata (Aryabhatiya, 499 CE) is regarded as the first Indian scholar to treat mathematics as a subject distinct from astronomy. (https://en.wikipedia.org/wiki/Aryabhata)
- `yb6b108df546` [APPSC 2025 Forest Section Officer] What is the benefit of biological control of forest pests ?
  none → (2) Low cost. A standard advantage of biological control of forest pests is that it is low cost (and eco-friendly) compared with chemical control; the official key PDF could not be opened, so this follows textbook knowledge. (https://portal-psc.ap.gov.in/HomePages/KeysToPapers)
- `y422f0c5832e` [APPSC 2025 Forest Section Officer] Which deficiency causes rickets in young animals , leading to weak bones ?
  none → (2) Calcium and Vitamin D. Rickets in young animals, with weak and soft bones, results from deficiency of calcium and vitamin D (vitamin D is needed to absorb calcium and phosphorus). (https://portal-psc.ap.gov.in/HomePages/KeysToPapers)
- `yb43f445adee` [APPSC 2025 Forest Section Officer] In Andhra Pradesh , which organization is primarily responsible for collecting and selling the majority of Minor Forest Produce ( MFP ) items ?
  none → (2) Girijan Cooperative Corporation. The Girijan Cooperative Corporation (GCC) is the tribal cooperative that collects and markets most Minor Forest Produce in Andhra Pradesh; the official key PDF could not be opened, so this follows general knowledge and the app's notes. (https://portal-psc.ap.gov.in/HomePages/KeysToPapers)
- `yef76bb94664` [APPSC Group-II 2008] Where was the first meeting of the Rayalaseema Mahasabha, formed in 1934, held?
  (2) Anantapur → (3) Madras. The first session of the Rayalaseema Mahasabha (formed 1934) was held at Madras on 28 January 1934; the second session was at Cuddapah in 1935 (followed Wikipedia/GKToday as the official key could not be opened). (https://en.wikipedia.org/wiki/Sribagh_Pact)
- `y4b6fb166900` [APPSC Group-II 2008] Who of the following authored The History of Telangana Armed Struggle?
  none → (3) Ravi Narayana Reddy. Ravi Narayana Reddy, the Telangana armed struggle leader, is the author among the options (Heroic Telangana: Reminiscences & Experiences, 1973); the other options were not authors on this subject. (https://thetricontinental.org/dossier-80-culture-and-the-telugu-peoples-class-struggle/?output=pdf)
- `y5d13fe15596` [APPSC Group-II 2008] Assume that an ad valorem tax is imposed on a commodity. The price of that commodity will rise if its elasticity of demand is
  none → (1) zero. When demand is perfectly inelastic (elasticity zero) consumers bear the entire tax so the price rises by the full tax, whereas with infinite elasticity the price does not rise. (https://en.wikipedia.org/wiki/Tax_incidence)
- `y18d886430d8` [APPSC Group-1 PYQ] The venue for the ASEAN Mekong Basin Commonwealth Bank ODI tri series in cricket Development Cooperation Meeting in August 2007 against Australia by: was:
A) 6 runs
B) 7 runs
C) 8 runs
D) 9 runs
  (3) Jakarta → (4) Manila Arabian Sea recently was:. The 9th ASEAN-Mekong Basin Development Cooperation (AMBDC) Ministerial Meeting was held in Manila, Philippines, on 27 August 2007. (https://asean.org/the-9th-ministerial-meeting-of-the-asean-mekong-basin-development-cooperation-ambdc-philippines-manila/)
- `y1aae847374a` [APPSC Group-1 PYQ] The Liberalisation, Privatisation and Globalisation 69. Ral Model of Economic Development assigns a key role to:
  none → (3) Private Sector. The LPG (1991 reforms) model of development removes restrictions on the private sector and reduces the government's role, giving the private sector the key role. (https://ncert.nic.in/textbook/pdf/keec103.pdf)
- `y9559a8f9726` [APPSC Group-1 PYQ] Which Vedic text first refers to money lending?
  (1) Atharvaveda → (3) Satapatha Brahmana. Standard references say the earliest mention of money-lending is in the Shatapatha Brahmana, which calls the usurer 'kusidin' (I could not confirm the official APPSC key). (https://selfstudyhistory.com/2020/05/05/money-lending-in-ancient-india/)
- `y53ff06257c3` [IAS (Pre) 2018] Which one of the following processes is not a part of long-wave radiation?
  (1) Conduction → (2) Scattering. Conduction, convection and radiation are the heat-transfer processes tied to long-wave (terrestrial) radiation, whereas scattering is a shortwave process, so Scattering is the odd one out. (https://testbook.com/question-answer/which-one-of-the-following-processes-is-nota--5efd8dde2cd8470d0cde14c9)
- `y50c12d06c63` [APPSC Group-II 2000 (Backlog)] Which of the following is an institution under Madras Presidency?
  (1) Bellary → (3) Banaganapalli. Banganapalle (Banaganapalli) was a princely state (samsthanam) ruled by a Nawab and linked to the Madras Presidency, whereas Bellary, Chittoor and Madanapalle were districts or towns; 'institution' is probably a mistranslation of 'samsthanam'. This is from my own knowledge and was not checked against a source. (https://en.wikipedia.org/wiki/Banganapalle_State)
- `y54eced4b7ca` [RAS/RTS (Pre) 1996] The main source of knowledge about the inhabitants of Indus Valley Civilisations is the discovery os
  (2) utensils, jewellery, weapons and tools → (1) seals. Because the Indus script is undeciphered, seals are the main source of knowledge about the Indus people, their trade, art and beliefs. (https://ras.pscnotes.com/rpsc-ras-prelims/the-main-source-of-knowledge-about-the-in-habitants-of-indus-valley-ci/)
- `y9f54670166b` [APPSC Gazetted Posts GS 2010 (Notification 30/2008)] Recently Ministry of Human Resource Development announced that there is no examination to the 10th Standard from the year?
  none → (2) 2011. HRD Minister Kapil Sibal announced in 2009 that the CBSE Class X board examination would be scrapped from 2011, while the March 2010 batch still had to sit the board exam. (https://www.deccanherald.com/india/no-board-exam-cbse-class-2561405)
- `yffc95b84227` [R.A.S./R.T.S. (Pre) 1999] Which of the following changes is catalyzed by the enzyme trypsin?
  (3) Proteins to amino acids → (2) Proteins to peptides. Trypsin hydrolyses peptide bonds and breaks proteins into smaller peptides; other proteases then convert these peptides to amino acids, so option 3 is wrong. (https://en.wikipedia.org/wiki/Trypsin)
- `y995dad9fca0` [M.P.P.C.S. (Pre) 2022 +2 more] Buddhist caves are not situated in which of the following places?
  (2) Bagh → (4) Bulsar. Ajanta and Bagh have Buddhist rock-cut caves and Sanchi is a major Buddhist site, whereas Bulsar has no Buddhist caves, so Bulsar is the answer (MPPSC 2022 Pre). (https://testbook.com/question-answer/buddhist-caves-are-not-situated-in-which-of-the-fo--6469cc8d3e210675fa0f2860)
- `yf4882d1f42f` [NDA 2012] Consider the following statements.

I. Typhoons occur mainly in the region of 6° to 20° North and South of the equator.

II. Typhoons are most frequent from May to June.

III. The velocity of Typhoons is 100 mph.

IV. Torrential downpour is accompanied by thunder and lightening in a typhoon.
Which of the statements given above is/are correct?
  (1) I and II → (4) None of these. Typhoons occur 6–20° N and S and bring torrential rain with thunder and lightning, but they are most frequent July–October (not May–June), so only I and IV are correct and none of the offered combinations fits, leaving 'None of these'. (https://testbook.com/question-answer/which-of-the-following-months-are-when-typhoon-occ--5d40c3b0fdb8bb0d267f8595)
- `y7b303f4ba05` [NDA 2014] Which of the following statements is/are correct?

I. Early buddhist literature is generally composed of the canonical text.

II. The Buddhist school classify their canonical literatures as only the Pitakas.
Codes
  (4) Neither I nor II → (1) Only I. Early Buddhist literature is largely canonical (Tripitaka), but Buddhist schools do not classify their canonical literature as 'only' Pitakas (Nikayas/Agamas and non-canonical texts also exist), so only statement I is correct. (https://examrobot.com/cds-ii/2014/history-culture/isare-early-buddhist-literature-generally-composed-canonical-text-buddhist-schools-classify-their)
- `ya5474ce1e4f` [APPSC Group-I Prelims 2002 (28-03-2002)] The bamboo flowers after attaining the age of
  (2) 12 years → (4) 48 years. Bamboo flowering cycles are reported as 48, 60 or 120 years, so 48 years is the only recognised cycle among the options; the 12-year cycle belongs to Neelakurinji, not bamboo, and I could not check the official key. (https://sj.jst.go.jp/news/202308/n0824-03k.html)
- `y11931f541af` [APPSC Group-II 2008] The United Nations World Refugee Day is
  none → (2) 20th June. The United Nations World Refugee Day is observed every year on 20 June. (https://www.un.org/en/observances/refugee-day)
- `y2fe7fb920f4` [APPSC Group-II 2008] Which is the cause of growing urbanisation in India ?
  none → (4) All of the above. Urbanisation in India is driven by industrial and trade growth in cities (pull) together with rural population pressure and low agricultural productivity (push), so all of the above apply. (https://en.wikipedia.org/wiki/Urbanisation_in_India)
- `yfe7d1a865b6` [APPSC Group-II 2008] Which one of the following is considered a transfer payment ?
  none → (4) Old age pensions. Old age pensions are the standard example of a transfer payment, a one-way payment made without any good or service given in exchange. (https://testbook.com/question-answer/an-example-of-transfer-payments-is--5f7c6270642b37e7561c2283)
- `yc7d84ae32ba` [U.P. Lower Sub. (Pre) 2002] By which of the following is the maximum percentage of Earth covered ?
  (1) Arid Region → (4) Humid Region. Drylands (hyper-arid, arid, semi-arid and dry sub-humid) cover only about 41% of the land, so humid regions cover the largest share of the Earth's land area. (https://en.wikipedia.org/wiki/Drylands)
- `y44044e3ad1e` [I.A.S. (Pre) 2001] Consider the following statements about the minorities in India:
1. The Government of India has notified five communities, namely, Muslims, Sikhs, Christians, Buddhists and Zoroastrians as minorities.
2. The National Commission for Minorities was given statutory status in 1993.
3. The smallest religious minority in India are the Zoroastrians.
4. The Constitution of India recognizes and protects religious and linguistic minorities. Which of these statements are correct ?
  (4) 1, 2 and 4 → (3) 2, 3 and 4. Statements 2, 3 and 4 are taken as correct (NCM statutory from the 1992 Act/1993, Zoroastrians are the smallest religious minority, the Constitution protects religious and linguistic minorities), while Statement 1 is treated as the incorrect one because the Jains were added later (2014); I could not see the official key. (https://examrobot.com/ias/2001/polity-governance/minorities-india-government-india-notified-five-communities-namely-muslims-sikhs-christians)
- `yb8358891e9b` [I.A.S. (Pre) 2001] Consider the following States:
1. Gujarat
2. Karnataka
3. Maharashtra
4. Tamil Nadu The descending order of these States with reference to their Per Capita Net State Domestic Product is:
  (1) 1, 3, 4, 2 → (4) 3, 1, 4, 2. The descending order of per capita NSDP is Maharashtra > Gujarat > Tamil Nadu > Karnataka (3, 1, 4, 2); other sources give 3, 1, 2, 4, and I did not find the official key. (https://educationprovince.com/5a-macroeconomy-prelims-pyqs/)
- `y750a7e05cd2` [APPSC Group-II 2012] The book "Hyderabad in Retrospect" was authored by?
  (2) Laik Ali → (3) Ali Yavar Jung. 'Hyderabad in Retrospect' (Bombay, 1949), published under the name 'An ex-official of Hyderabad', is attributed in scholarly citations to Nawab Ali Yavar Jung, while Laik Ali wrote 'Tragedy of Hyderabad'; I did not see the official APPSC key. (https://www.anveshi.org.in/wp-content/uploads/2021/09/Berkshire-Telugu-nationalism-and-Police-Action-against-Hyderabad.pdf)
- `y814f8be4a94` [APPSC Group-II 2011] The sacred books of Jains are called
  (2) Angas → (1) Agamas. The sacred books of the Jains are called Agamas (Siddhanta), the works of Mahavira's immediate disciples; the Angas are only the twelve main divisions within the Agama canon. (https://www.gktoday.in/question/sacred-book-of-jainism-is-called-_______)
- `y7767e3e47d9` [APPSC AP History PYQ] Who wrote the 'Kurnool Circular'?
  none → (4) Kala Venkata Rao. The Kurnool Circular (July 1942, Quit India) was drafted by Kala Venkata Rao and forwarded to the CWC through Pattabhi Sitaramaiah. (https://www.pib.gov.in/newsite/printrelease.aspx?relid=169423&reg=48&lang=2)
- `y9962c489171` [APPSC AP History PYQ] Who were the first political victims to be jailed in the Vande Mataram movement in Andhra?
  none → (2) Bodi Narayana Rao and Gadicherla Harisarvottama Rao. Gadicherla Harisarvottama Rao and Bodi Narayana Rao were the first political sufferers in Andhra jailed during the Vande Mataram movement. (http://appscgroupsmaterial-srujana.blogspot.com/2012/02/appsc-material-ap-history-freedom_06.html)
- `y42b0458bb4d` [APPSC AP History PYQ] What was the first criminal case reported in Andhra during the Vande Mataram movement?
  none → (2) Kakinada case. The Kakinada (Riot) Case of 1907, in which Dr Kemp assaulted Kompalli Krishna Rao, is regarded as the first criminal case in Andhra during the Vande Mataram movement. (http://appscgroupsmaterial-srujana.blogspot.com/2012/02/appsc-material-ap-history-freedom_06.html)
- `y9b871f87389` [I.A.S. (Pre) 2002] With reference to the Indian Public Finance, consider the following statements :
1. External liabilities reported in the Union Budget are based on historical exchange rates.
2. The continued high borrowing has kept the real interest rates high in the economy.
3. The upward trend in the ratio of Fiscal Deficit to GDP in recent years has an adverse effect to private investments.
4. Interest payments is the Single largest component of non-plan revenue expenditure of the Union Government. Which of these statements are correct?
  (3) 2, 3 and 4 → (4) 1, 2, 3 and 4. All four statements are correct: external debt is shown in the Budget at historical exchange rates, high borrowing keeps real interest rates high and crowds out private investment, and interest payments are the largest single item of non-plan revenue expenditure. (https://www.scribd.com/document/872910249/UPSC-IAS-Prelims-General-Studies-Question-Paper-2002-With-Answers)
- `yb865e78afb0` [I.A.S. (Pre) 2002] Assertion (A) : Artificial satellites are always launched from the earth in the eastward direction.
Reason (R) : The earth rotates from west to east and so the Satellite attains the escape velocity.
  (4) (A) is false, but (R) is true → (3) (A) is true, but (R) is false. Satellites are launched eastward to use Earth's rotational speed boost, so A is accepted as true, but a satellite in orbit does not attain escape velocity, so R is false. (https://www.sarthaks.com/78311/assertion-artificial-satellites-are-always-launched-from-the-earth-eastward-direction)
- `y1cb129a71bb` [U.P. P.C.S. (Pre) 2018 +1 more] In which of the following hills the world famous temple of Lord Venkateshwar (Tirupati) is located?
  (1) Shevaroy → (4) Mallmalla. The Venkateshwara temple at Tirumala is on the Seshachalam hills of the Eastern Ghats in Andhra Pradesh; Shevaroy (Salem, Tamil Nadu), Javadhi (Tamil Nadu) and Biligiriranga (Karnataka) are elsewhere, so Nallamalla is the only plausible option. (https://www.adda247.com/upsc-exam/uppcs-question-paper-2018/)
- `yfd9471b6e85` [APPSC Group-I Prelims 2018] Which of the following statements rightly explain about Tropopause?
(i) Seasonal variation occurs in the height of tropopause.
(ii) It is the transition zone between troposphere and stratosphere.
(iii) It lies below the stratosphere.
  (3) Statements ii & iii are correct → (1) Statements i, ii & iii are correct. The tropopause is the transition zone between the troposphere and stratosphere, lies below the stratosphere, and its height varies with season and latitude, so all three statements are correct. (https://ncert.nic.in/textbook/pdf/kegy101.pdf)
- `y6b47bb4a32c` [APPSC Group-I Prelims 2024 (17-03-2024)] Which of the following statements regarding Himalayas are correct?

I. Himalayas are geologically young and structurally fold mountains.

II. They are wide in Kashmir and narrow in the North-eastern states.

III. The folds of Great Himalayas are asymmetrical in nature and their core is composed of granite.

IV. The longitudinal valleys lying between Greater and Lesser Himalayas are known as Duns.
Select the correct answer using the codes given below:
  (4) I, II, III and IV → (2) I, II and III. Statements I, II and III are true, but Duns are the longitudinal valleys between the Lesser Himalaya and the Shiwaliks, not between the Greater and Lesser Himalayas, so statement IV is false (NCERT). (https://ncert.nic.in/textbook/pdf/kegy101.pdf)
- `ya427474f6fe` [Chhattisgarh P.C.S. (Pre) 2017 +1 more] Which philosophy accepts ‘Triratna’?
  (3) Yoga philosophy → (4) Jainism. Triratna (Ratnatraya: right faith, right knowledge, right conduct) is the Jain path to moksha; Yoga philosophy has no Triratna, so the given key is wrong (Testbook's CGPSC 2017 solution gives Jainism). (https://testbook.com/question-answer/which-philosophy-accepts-triratna--6080026b51c086166ad4b9d8)
- `yc5d376b116f` [APPSC AP History PYQ] Who was the President of the Andhra Mahasabha between 1941-1946?
  none → (4) Sir Vijaya. The APPSC Group-II Paper-II (A.P. Social History) initial key gives 'Sir Vijaya' as President of the Andhra Mahasabha during 1941–1946; I could not check the final key. (https://img.freejobalert.com/uploads/2019/09/Initial-Key-APPSC-Group-II-A.P-Social-History-Constitution.pdf)
- `yf49191826e7` [UKPSC (Pre) 2005] Which one of the following is used in making Bullet proof Jacket’?
  (4) Laminated glass → (1) Fibrous glass. Wearable body armour has used glass-fibre (fibrous glass) composites, whereas laminated glass is rigid bullet-resistant window glass and cannot form a jacket; the given key (4) is not supported, but I did not verify this against an official key. (https://en.wikipedia.org/wiki/Body_armor)
- `ye502d5759c7` [APPSC AP History PYQ] Gangadevi was a disciple of whom?
  none → (1) Agastya. Gangadevi, the Vijayanagara queen and author of Madhura Vijayam, is listed in APPSC PYQ material as the student of Agastya (Pandita), whom she praises in her poem; the other options are chronologically or otherwise unrelated. (https://www.scribd.com/document/353134723/AP-HISTORY-PYQ-pdf)
- `y1c1700f851e` [APPSC Group-II 2011] What was the main point of difference between Nizam Ali of Hyderabad and the English?
  (1) The Northern sarkar → (2) The Sarkar of Guntur. The Sarkar (Circar) of Guntur, held by Nizam Ali's brother Basalat Jang and excepted from British rule during his lifetime, was the bone of contention between Nizam Ali and the English. (https://en.wikipedia.org/wiki/Northern_Circars)
- `y8b98025f084` [APPSC Group-II 2008] Which case recognized that the Preamble is a part of the Indian Constitution?
  none → (1) Kesavananda Bharati. In Kesavananda Bharati v. State of Kerala (1973) the Supreme Court held that the Preamble is a part of the Constitution, overruling the Berubari Union (1960) view. (https://fortuneiascircle.com/backgrounder/basic_structure_doctrine)
- `y58d1431d578` [APPSC Group-II 2008] Which state in India produces the largest amount of coal ?
  none → (3) Orissa. Of the listed states, Orissa was the largest coal producer around 2008, ahead of Madhya Pradesh, while West Bengal produces only about 4% of India's coal and Bihar's coalfields passed to Jharkhand in 2000. (https://www.mlsu.ac.in/econtents/1895_Distribution%20of%20Coal%20&%20Petroleum%20in%20India.pdf)
- `ybdf59c539b3` [APPSC Group-II 2008] Which of the following is false with regards to socio-religious and economic conditions during the Satavahana rule?
  none → (3) The women were looked down upon. The statement that women were looked down upon is false, because Satavahana women enjoyed a respected status (kings used metronymics and queens made donations), while the four-fold caste system, Buddhist patronage by queens and flourishing maritime trade are accurate. (https://kpiasacademy.com/satavahana-social-conditions/)
- `ybd406b07a80` [UKPSC (Mains) 2002] The Home Rule Leagues of Tilak and Annie Besant were merged into one in
  (2) 1918 → (3) 1920. The Home Rule Leagues of Tilak and Besant came together in 1920, when the All India Home Rule League elected Gandhi president and became the Swarajya Sabha; no source supports a 1918 merger. (https://www.gktoday.in/all-india-home-rule-league-1915-1920/)
- `y38f7d12f5e2` [APPSC Group-II Mains 2025 (23-02-2025)] Which of the following statement(s) is/are incorrect?

a. Vijayaditya II is credited with the construction of 108 temples.

b. Raja Raja Narendra constructed Rajarajeswara temple at Biccavole.

c. Chalukya Bhima constructed Bhimeswara Swamy temple at Draksharama.
  (2) b and c → (3) b only. Vijayaditya II's 108 temples (a) and Chalukya Bhima I's Bhimeswara temple at Draksharama (c) are correct, so only statement b is the incorrect one, giving option 3 (b only); this rests on standard references, not a fetched official key. (https://en.wikipedia.org/wiki/Draksharama)
- `y8bdb1940f85` [APPSC Group-II Prelims 2017 (26-02-2017)] The proposed gravitational-wave observation project in India would be run by the consortium of research institutions known under the English acronym
  (3) IndLIGO → (1) IndIGO. IndIGO (Indian Initiative in Gravitational-wave Observations) is the consortium behind the LIGO-India project; 'IndLIGO' is not the consortium's name. (https://gw-indigo.org)
- `ya3d7dd7eae3` [APPSC Junior Assistants (Dr. NTR University of Health Scienc] What is the architectural style of the 'Alampur' temples built by the Chalukyas?
  (4) Vesara → (2) Nagara. The Alampur Navabrahma temples built by the Badami Chalukyas are in the Nagara (rekha-prasada) style, not Vesara. (https://en.wikipedia.org/wiki/Alampur_Navabrahma_temples)
- `y3bd005867ed` [APPSC 2025 Draughtsman Grade-II (Technical Assistant) In A.P] As per State Energy Efficiency Index , 2024 released by BEE ( Bureau of Energy Efficiency ) , which State stood as top performer ?
  none → (3) Maharashtra. In BEE's State Energy Efficiency Index 2024 (released 29 Aug 2025), Maharashtra is listed first and ranked top, as the Group 1 (>15 MToE) topper; Andhra Pradesh topped only Group 2. (https://www.pib.gov.in/PressReleasePage.aspx?PRID=2161803&reg=48&lang=2)
- `y27137bd0b86` [APPSC 2025 Forest Section Officer] Which of the following is a characteristic feature of the grassland ecosystem ?
  none → (3) Low water availability. Grasslands occur where rainfall is too low to support forest, so low water availability is their characteristic feature, unlike high rainfall and dense vegetation, which describe forests. (https://www.britannica.com/science/grassland)
- `yc0ca3cc0dd0` [U.P.P.C.S. (Pre) 2009 +3 more] In India for estimation of GDP at constant prices, at present the base year is :
  (3) 2002-2003 → (1) 1999-2000. India's GDP at constant prices used 1999-2000 as the base year until the 2004-05 series was introduced in January 2010, so 1999-2000 was current at the 2009 exam; no source gives 2002-03. (https://www.mospi.gov.in)
- `y43bcd14d8ae` [U.P.P.C.S. (Pre) 2012 +1 more] The leading producer of Manganese in India is –
  (3) Madhya Pradesh → (4) Odisha. The UPPSC Prelims 2012 paper's key for the largest manganese producer is Odisha (Orissa), which also has the largest manganese resources (44%); production rankings among MP, Maharashtra and Odisha varied year to year, so I followed the paper's key. (https://selfstudyhistory.com/2016/01/29/uppsc-prelims-general-studies-paper-2011-part-2-2/)
- `y8880f2d5083` [R.A.S./R.T.S.(Pre) 2013 +1 more] Which one of the following international waterways is operated through lock-system?
  (3) Danube River → (4) Panama Canal. The Panama Canal operates through a system of locks (Gatun, Pedro Miguel, Miraflores), whereas the Suez Canal is a sea-level canal without locks. (https://testbook.com/question-answer/which-one-of-the-following-international-waterways--600a85f2f78ca15195c9e9ed)
- `y464b22dcc41` [R.A.S./R.T.S. (Pre) 2016 +1 more] Inflation rate based on Consumer Price Index increases if :
  (4) Repo Rate is increased → (1) Bank Rate is decreased. Per the RPSC RAS 2016 answer as reproduced by Testbook, a decrease in Bank Rate makes credit cheaper and raises liquidity, so CPI-based inflation increases, whereas raising the repo rate or SLR curbs inflation. (https://testbook.com/question-answer/inflation-rate-based-on-consumer-price-index-incre--5ffd921adf15ec3a4ff9ae4a)
- `y7e94ad75bf4` [CGPSC 2020] During the first phase of Civil Disobedience Movement the following events took place in Chhattisgarh? (i) An attempt to hoist tricolour on the high school building of Bilaspur by the students. (ii) Imprisonment of Wamanrao Lakhe, Shivdas Daga, Abdul Rauf and Pyarelal Singh in Raipur. (iii) Celebration ‘Poorna Swaraj’ week at different places in Chhattisgarh. (iv) Election of Pt. Ravi Shankar Shukla as Chairman of Raipur District Council while he was in the Jail.
Select the answer determining chronology of these events.
  (4) (iv), (iii), (ii), (i) → (3) (iii), (i), (ii), (iv). In 1930 Poorna Swaraj week came first, then the Bilaspur flag attempt and the Raipur imprisonments, and Shukla's re-election as Raipur District Council president while in jail came last (24 Oct 1930), giving (iii),(i),(ii),(iv); the question is reported to have been deleted by CGPSC. (https://testbook.com/question-answer/during-the-first-phase-of-the-civil-diso--601e958cf4a0f5e415390d56)
- `y802eb3264f7` [APPSC Gazetted Posts GS 2010 (Notification 30/2008)] Which of the following is a member of SAARC?
  none → (1) Bhutan. Bhutan is a SAARC member; Tibet is not a country, Myanmar is only an observer, and Malaysia is not a South Asian state. (https://www.worldatlas.com/articles/which-countries-are-members-of-saarc.html)
- `y90573c023b2` [APPSC Gazetted Posts GS 2010 (Notification 30/2008)] Which of the following fighter-Aircrafts is supplied to India by European Union?
  none → (3) Tyhoon. The Eurofighter Typhoon, made by a European consortium, was the European fighter offered to India in the MMRCA competition, whereas the F-16 is American, the Gripen is Swedish and the MiG-35 is Russian. (https://www.rusi.org/publication/indias-procurement-european-fighter)
- `yc279f00b90d` [APPSC Group-II 2011] Who argued that the Ikshvakus were Telugu people?
  (3) Gopalachari → (1) Caldwell. Caldwell held that the Ikshvakus were natives of the Krishna-coast (Andhra/Telugu) region, whereas Gopalachari held they were Tamil, Vogel Kannada, and Bühler and Rapson north Indian. (https://pratibha.eenadu.net/tspsc/lesson/group-iii/paper-1/telugumedium/ikshvakus/2-1016-241-539-913-1099-11396-18212-23040000750)
- `y3b793e23dba` [APPSC Group-I Prelims 2003] Golden jubilee celebrations were held in Delhi in January 2003 on the occasion of the Sangeet Natak Akademi completing 50 years since its founding. Who is the present chairman of the Akademi?
  (1) Abhijit Chatterjee → (4) Bhupen Hazarika. Bhupen Hazarika was chairman of the Sangeet Natak Akademi from 2003 to 2008 (moderate confidence, from recall, not confirmed on an opened page); nothing links Abhijit Chatterjee to the post. (https://en.wikipedia.org/wiki/Bhupen_Hazarika)
- `ydd607e776ef` [SSC (10+2) 2018] How CNG is a cleaner fuel?

I. It produces oxides of Sulphur and Nitrogen in very smal amounts.

II. It makes environment less polluted.

III. It emits less greenhouse gases.
  (3) Only I and III → (4) All I, II and III. CNG (mostly methane) produces very small amounts of sulphur and nitrogen oxides, pollutes less and emits fewer greenhouse gases, so all three statements I, II and III are correct. (https://testbook.com/question-answer/how-cng-is-a-cleaner-fueli-it-produces-oxides--5b45ea92fc1e290c44f6e62d)
- `y6cca4bf6148` [SSC (10 + 2) 2018] More density of the particles in the medium through which sound travels, creates more ……… and vice versa.
  (2) energy → (1) pressure. In a sound wave, greater density of particles in the medium corresponds to greater pressure (compressions are high-density, high-pressure regions), and vice versa. (https://testbook.com/question-answer/more-density-of-the-particles-in-the-medium-throug--5bd80174433e6e1864bc1225)
- `yd3fb68aa20b` [CDS 2017] Which of the following statement is/are correct?

I. Himalayan rivers have their origin in the snow-covered areas, hence are dry in winter season.

II. Rivers of the Peninsular plateau have reached maturity.

III. Himalayan rivers depict all the three stages of normal cycle of erosion.
Select the correct answer using the codes given below.
  (1) Only II → (3) II and III only. Himalayan rivers are perennial (so I is false), Peninsular rivers have reached maturity (II true), and Himalayan rivers show youthful, mature and old stages along their course (III true), so II and III only; this follows CDS II 2017 paper solutions from Testbook and EduRev, as no official key was found. (https://testbook.com/question-answer/which-of-the-following-statements-isare-correct--5be023289235ce73588842a6)
- `y14f423318a4` [APPSC Group-2 PYQ] Which Article of the Constitution of India provides for Co-operation between the States: in A
  (3) Article-14 → (4) Article 263 C. Article 263 provides for an Inter-State Council to coordinate and co-operate between the States; Articles 14 and 32 deal with equality and constitutional remedies. (https://vajiramandravi.com/current-affairs/article-263-of-the-indian-constitution/)
- `y280f5fdd1c2` [BPSC (Pre) 1999] In which of the following states of India, silver is not found?
  (4) Bihar → (3) Gujarat. The compiled BPSC 1999 key gives Gujarat, because the Indian Minerals Yearbook lists silver in Rajasthan, Jharkhand (undivided Bihar in 1999), Andhra Pradesh, Karnataka, Odisha and others but not Gujarat. (https://www.iasbook.com/mineral-resources-india-questions/)
- `y3f5fdc9c1b0` [U.P.P.C.S. (Mains) 2009 +1 more] Pulse crop which does not fix atmospheric nitrogen is
  (1) Gram → (3) Rajma. Rajma (Phaseolus vulgaris) is the pulse crop that does not fix atmospheric nitrogen (a poor nodulator), unlike gram, pea and moong; the solved UPPCS 2009 paper gives (C) Rajma. (https://iasexamportal.com/Paper/UPPCS-Mains-Exam-General-Studies-Question-Paper-Solved-2009)
- `ycedd861b150` [U.P.P.C.S. (Mains) 2009 +1 more] Consider the following important sources of tax revenue for the Central Government :
1. Corporation tax
2. Tax on income other than corporation tax
3. Customs
4. Union Excise Duties Which of the following is the correct descending order in terms of gross tax revenue?
  (3) 3, 1, 2, 4 → (1) 1, 2, 4, 3. The correct descending order of gross tax revenue is Corporation tax, then Income tax (other than corporation tax), then Union excise duties, then Customs (1, 2, 4, 3). (https://testbook.com/question-answer/consider-the-following-important-sources-of-tax-re--607d96172ba5e0b6527738a0)
- `y2b1406d35b3` [Jharkhand P.C.S. (Pre) 2013] Which one of the following is not taken as a factor among the non-economic factors, which contribute in economic growth?
  (2) Corruption → (4) Market surplus in agriculture. Human resource, social organization and corruption are all treated as non-economic factors in the textbook, so market surplus in agriculture is the one that is not; corruption cannot be the answer (followed the textbook, official key not accessible). (https://www.shaalaa.com/question-bank-solutions/what-are-the-non-economic-factors-determining-development_223804)
- `y85a4a420db5` [APPSC Group-I 2023 (08-01-2023)] Consider the following statements regarding ExoMars:

I. Its rover will be the first mission to combine the capability to move across the surface and to study Mars at depth.

II. ExoMars is a joint programme of the European Space Agency (ESA) and the Russian Space Agency - Roscosmos.
Which of the statements given above is/are correct?
  (4) Neither I nor II → (3) Both I and II. ESA states the ExoMars rover will be the first mission to combine surface mobility with studying Mars at depth, and ExoMars was set up as a joint ESA–Roscosmos programme, so both statements are true. (https://www.esa.int/Science_Exploration/Human_and_Robotic_Exploration/Exploration/ExoMars/ExoMars_rover)
- `y011c7c045ad` [IAS (Pre) 2010] With reference to the Indian economy, consider the follwing statements.

I. The Gross Domestic Product (GDP) has increased by four times in the last 10 years.

II. The percentage share of Public Sector in GDP has declined in the last 10 years.
Which of the statements given above is/are correct?
  (4) Neither I nor II → (2) Only II. GDP did not rise four-fold in the 10 years to 2010 (statement I is false), but the public sector's share of GDP declined after liberalisation (statement II is true), so only statement II is correct. (https://www.gktoday.in/question/with-reference-to-indian-economy-consider-the-following-statements-the-735642)
- `y6e128702dee` [APPSC Group-II 2008] Who of the following rulers built Rajahmundry?
  none → (2) Ammaraja. Rajahmundry (Rajamahendravaram) is traditionally said to have been founded by the Eastern Chalukya king Ammaraja; Rajaraja Narendra later made it a prominent capital (source not fully verified). (https://www.kupi.com/en/explore/india/rajahmundry/history)
- `ye1cf97b92d8` [SSC 2010] The first Indian Hindi scholar of the Mughal period was
  (2) Abdur Rahim → (1) Malik Muhammad Jayasi. Malik Muhammad Jayasi, who wrote Akhiri Kalam (1529-30) under Babur and Padmavat in Awadhi Hindi, is the answer given as the first Indian Hindi scholar of the Mughal period; Abdur Rahim is not. (https://www.examveda.com/the-first-indian-hindi-scholar-of-the-mughal-period-was-77911/)
- `y3d8f5bd9b1d` [U.P.P.C.S. (Pre) 2015] Green Revolution was the result of adaptation of the new Agricultural Strategy, which was introduced in the 20th century during decades of –
  (2) Seventies → (3) Sixties. India's New Agricultural Strategy and HYV seeds programme began in 1965-66, so the Green Revolution belongs to the 1960s (sixties). (https://en.wikipedia.org/wiki/Green_Revolution_in_India)
- `y47d869c1458` [U.P.P.C.S. (Mains) 2006 +1 more] Steel Authority of India was established in the year :
  (1) 1965 → (3) 1974. SAIL was incorporated on 24 January 1973 as the holding company for the public-sector steel plants, so 1965, 1971 and 1956 are wrong and 1974 is the nearest option. (https://sail.co.in/en/company/background-history)
- `y767de17d50f` [APPSC Group-2 PYQ] The present Chairman of the Rajya Sabha is
  none → (3) Hamid Ansari. In 2016-17, the year of the exam, Mohammad Hamid Ansari was Chairman of the Rajya Sabha and P.J. Kurien was Deputy Chairman. (https://cms.rajyasabha.nic.in/UploadedFiles/Debates/OfficialDebatesDatewise/Floor/240/F18.07.2016.pdf)
- `yfcdf044dac3` [APPSC AP History PYQ] Which tank was built by Surambika, the wife of Peda Komati Vema?
  none → (4) Santana Sagar. Surambika, queen of Peda Komati Vema Reddy, built the Santhana Sagaram tank at Phirangipuram (Guntur district). (https://appscgrouptimes.blogspot.com/2012/07/ap-history-bits.html)
- `y1da51b7cc3b` [APPSC AP History PYQ] Who presided over the 'Visalandhra Mahasabha' in 1949?
  none → (4) A. Kaleswara Rao. The Visalandhra Mahasabha of 26 November 1949 was organised at Vijayawada under the chairmanship of Ayyadevara Kaleswara Rao. (https://www.rcreddyiasstudycircle.com/public/images/APPSC_Grand_Test_English_Telugu_Key_(1-150)_GT-3.pdf)
- `yd98085063d8` [APPSC AP History PYQ] Who was the first / founder of the Andhra Pradesh State Legislative Assembly?
  (4) Devulapalli Ramanuja Rao → (2) Ayyadevara Kaleswara Rao. Ayyadevara Kaleswara Rao was elected the first Speaker of the Andhra Pradesh Legislative Assembly at its first meeting on 3 December 1956, per the AP Legislature's official site. (https://apuat21.cgg.gov.in/web/legislative-assembly/overview)
- `yfe94afbb670` [U.P.P.C.S. (Pre) 2001] The Pradhan Mantri Gram Sadak Yojana is :
  (4) To develop community life in villages which are not → (1) To augment road connectivity and provide food grains. PMGSY, launched on 25 December 2000, aims to provide all-weather road connectivity to unconnected rural habitations, so the road-connectivity option fits and 'community life' does not. (https://vajiramandravi.com/current-affairs/pradhan-mantri-gram-sadak-yojana/)
- `y3c439658331` [APPSC Group-II 2012] Ramappa Temple belongs to which type?
  (3) Trikuta → (1) Monolithic. The Ramappa (Rudreshwara) temple at Palampet is a single-shrine (ekakuta/ekasila) temple, not a trikuta; the trikuta temple at Palampet is a separate, older structure. (https://www.scribd.com/document/353134723/AP-HISTORY-PYQ-pdf)
- `y99cfe93a5d0` [APPSC Group-II 2012] In the Satavahana period the Guild "Padhika" belonged to?
  (1) Katikavaru (Butchers) → (2) Carpenters. Padhika is a garbled form of Vadhika, the Satavahana-era occupational term for carpenters, so the guild belonged to carpenters. (https://kpiasacademy.com/satavahana-social-conditions/)
- `y66a721819fe` [APPSC Group-2 PYQ] Who is the Scientific Adviser to the Defence Minister?
  none → (4) G. Satheesh Reddy. G. Satheesh Reddy became the 12th Scientific Adviser to the Defence Minister in 2015, succeeding S. Christopher. (https://en.wikipedia.org/wiki/G._Satheesh_Reddy)
- `y0d3e3c19ae7` [APPSC Group-2 PYQ] Statement A: Natality refers to the birth of individuals in a population. Statement B: Natality rate is expressed as the number of individuals produced per female per unit time.
  (3) Statement A is true, but statement B is false → (1) Both statements A and B are true. Natality is the birth of individuals in a population, and natality rate is expressed as the number of individuals produced per female per unit time, so both statements are true. (https://www.slideshare.net/slideshow/population-ecology-234709404/234709404)
- `yb391538d958` [APPSC Group-1 PYQ] Who from the following were associated with Subhash Chandra Bose's Indian National Army and faced the trial in Delhi in 1945?
  (2) GS. Dhillon → (4) Bhulabhai Desai. The INA officers tried at the Red Fort in 1945 were Shah Nawaz Khan, P.K. Sahgal and G.S. Dhillon, while Bhulabhai Desai was only their defence counsel, so he is the one who was not tried (the 2004 original reads 'Who of the following was not...'). (https://www.livelaw.in/articles/two-monumental-red-fort-trials-bahadur-shah-zafar-ina-301090)
- `y43288e2ed32` [SSC 2008] The staple food of the Vedic Aryan was
  (1) barley and rice → (2) milk and its products. The staple food of the Vedic Aryans was milk and its products (curd, ghee and similar), with barley (yava) the main grain and rice only a later addition. (https://testbook.com/question-answer/what-was-the-staple-food-of-the-vedic-aryans--6455fff82bdd6272f87c2a58)
- `y120f15f91d1` [APPSC Group-2 PYQ] The main objective of the National Development Council is
  none → (2) To strengthen and mobilise the efforts and resources of the Nation in support of the Plan. The NDC's first stated objective (1952 resolution) is to strengthen and mobilise the efforts and resources of the nation in support of the Plan. (https://en.wikipedia.org/wiki/National_Development_Council_(India))
- `y2a6035054c8` [APPSC Group-2 PYQ] Regarding the Panchayat Raj System, in 1978 the Ashok Mehta Committee recommended for
  (3) two tier system with five years of term → (1) two tier system with four years of term. The Ashok Mehta Committee (1978) recommended a two-tier Panchayati Raj system (Zilla Parishad and Mandal Panchayat) with a fixed four-year term (standard textbook position; official 2025 key could not be verified). (https://en.wikipedia.org/wiki/Ashok_Mehta_Committee)
- `y8cfa1051042` [APPSC Group-2 PYQ] Arrange the following Committees of Panchayat Raj in chronological order.
a. Gadgil Committee
b. Dantwala Committee
c. L. M. Singhvi Committee
d. Balwant Rai Mehta Committee
  (1) d, b, a, c → (4) d, b, c, a. Balwant Rai Mehta (1957), Dantwala (1978), L. M. Singhvi (1986), Gadgil (1988) gives the order d, b, c, a. (https://en.wikipedia.org/wiki/Panchayati_raj_in_India)
- `y8991c5da0d2` [APPSC Group-2 PYQ] President's Rule is declared under which Article of the Constitution?
  none → (1) Article 356. President's Rule is imposed under Article 356 (failure of constitutional machinery in a State); Art. 352 is national emergency, 358 suspension of Art. 19 during emergency, 360 financial emergency. (https://www.constitutionofindia.net/articles/article-356-provisions-in-case-of-failure-of-constitutional-machinery-in-states/)
- `yd4e28386620` [APPSC Group-2 PYQ] The prize considered equivalent to Nobel Prize for Mathematics is
  none → (1) Fields Medal. The Fields Medal is regarded as the highest honour in mathematics, often called the Nobel Prize of mathematics. (https://en.wikipedia.org/wiki/Fields_Medal)
- `y6de9671897b` [NDA 2009] When oil floats on water, the surface tension of water
  (4) remains unaffected. → (2) decreases considerably.. When oil spreads over water it forms a film that considerably lowers the surface tension of the water surface, so the surface tension decreases considerably. (https://testbook.com/question-answer/when-oil-floats-on-water-the-surface-tension-of-w--5ec54c6ff60d5d4a3678a3b8)
- `y2c790d60819` [CDS 2016] Which one of the following is the cause of long-term sea-level change?
  (2) Change in marine water density. → (4) Melting of ice sheets.. Long-term (eustatic) sea-level change is driven mainly by the melting and freezing of ice sheets, so 'Melting of ice sheets' is the best option (I could not open the official key to confirm). (https://testbook.com/question-answer/which-one-of-the-following-is-the-cause-of-long-te--5cdaf057fdb8bb21951aaf92)
- `y95090f6fb81` [U.P.P.C.S. (Pre) 2011] Which of the following authority sanctions foreign exchange for import of goods?
  (2) Exchange Bank → (3) Reserve Bank of India. The Reserve Bank of India is the exchange-control authority under FEMA that sanctions foreign exchange for imports, acting through Authorised Dealer banks; 'Exchange Bank' is not an authority. (https://mcqmate.com/discussion/156340/which-of-the-following-authority-sanctions-foreign-exchange-for-the-import-of-goods-up-pcs-2011)
- `y5a511e9e8ea` [U.P.P.C.S. (Pre) 2011] Assertion (A) : If somebody stops taking green vegetables hewill suffer from night blindness.
Reason (R) : He will suffer from vitamin A deficiency.
Select the correct answer from the codes given below:
Code :
  (4) (A) is false, but (R) is true → (1) Both (A) and (R) are true, and (R) is the correct. Green vegetables are a source of vitamin A, whose deficiency causes night blindness, so both A and R are true and R explains A. (https://www.embibe.com/questions/Assertion-(A)-If-somebody-stops-taking-green-vegetables-he-will-suffer-from-night-blindness.Reason-(R)-He-will-suffer-from-vitamin-A-deficiency.Select-the-correct-answer-from-the-code-given-below./EM9232803)
- `yc174f3398eb` [U.P.P.C.S. (Pre) 2011 +2 more] LPG used as domestic fuel chiefly contains :
  (3) Ethylene → (4) Butane. Domestic LPG consists mainly of butane and propane (not ethylene), and of the listed options butane is the chief constituent. (https://en.wikipedia.org/wiki/Liquefied_petroleum_gas)
- `y406c1f7239c` [APPSC Group-2 PYQ] Locate the Constitutional power which enabled the Central government to Legislate on cow slaughter
  (4) Article 48 in the Directive Principles → (3) Entry 17, list 3 in schedule for prevention of cruelty to animals. Legislative power flows from Art. 246 and the Seventh Schedule, and 'prevention of cruelty to animals' is Entry 17 of the Concurrent List; Article 48 is only a Directive Principle addressed to States and confers no legislative power. (https://en.wikipedia.org/wiki/Prevention_of_Cruelty_to_Animals_Act,_1960)
- `y92cdd0e1699` [APPSC Group-2 PYQ] The annual growth rate of real GDP of India in 2014-15 is
  none → (1) 7.3. The CSO's provisional estimate (May 2015, 2011-12 series) put India's real GDP growth for 2014-15 at 7.3%. (https://pib.gov.in)
- `y95515d6c5fd` [APPSC Group-2 PYQ] According to a World Bank Report, India has recently surpassed France to become the largest economy in the world. (1) (3) °C
  (3) Fifth → (4) Sixth of. World Bank data for 2017 showed India ($2.597 trillion) overtaking France ($2.582 trillion) to become the world's sixth-largest economy; Fifth came only in 2019 after overtaking the UK. (https://scroll.in/latest/886134/india-overtakes-france-to-become-worlds-sixth-biggest-economy-report)
- `y98e279c5649` [APPSC Group-I Prelims 2024 (17-03-2024)] Which of the following statement/statements is/are valid regarding the office of the 'Whip'?

I. Although not mentioned in the Constitution of India, the office of the 'Whip' has however been incorporated in the Rules of the House by the 'Leaders and Chief Whips of Recognised Parties and Groups in Parliament (Facilities) Act, 1998'.

II. The role of the Chief Whip of the government party in the Lok Sabha is served by the Minister of State for Parliamentary Affairs.

III. All political parties – whether ruling or opposition, will have their own Whips in the Parliament.

IV. The Chief Whip is not responsible to the leader of the House but is responsible only to the leader of the party that has appointed him/her to the office of Chief Whip.
Select the correct answer using the codes given below:
  (3) II and III → (2) Only III. Only statement III is valid: the 1998 Act merely gives Chief Whips facilities rather than incorporating the office into House rules, and the Lok Sabha Government Chief Whip is the Minister of Parliamentary Affairs (the Minister of State holds the post in the Rajya Sabha), so only III is correct. (https://testbook.com/question-answer/which-of-the-following-statementstatements-isar--67b325a08486bcdc3db5b31c)
- `y5aa82bd0bbf` [APPSC Group-I Prelims 2024 (17-03-2024)] Which of the following State Bill/Bills will have to be mandatorily reserved for the President's consideration?

I. A Bill that proposes to give effect to certain Directive Principles of State Policy.

II. A Bill requiring prior Presidential sanction but which was however not obtained under Article 304.

III. A Bill that attracts the provisions of Article 288.

IV. A Bill seeking to operate a provision that belongs to one of the Concurrent List entries, but which is however repugnant to any Union law.
Select the correct answer using the codes given below:
  (2) I, II and IV → (3) Only III. Only a state Bill attracting Article 288(2) must mandatorily be reserved for the President's consideration; Article 304(b) requires prior sanction for introduction, and DPSP (Art. 31C) and repugnancy (Art. 254(2)) cases are not mandatory reservations. (https://testbook.com/question-answer/which-of-the-following-state-billbills-will-have--67b32858288f3f5272115170)
- `y54c941741eb` [UPPSC (Pre) 1993, 1991] Who launched the first Home Rule League Movement?
  (1) Annie Besant → (4) Tilak. Tilak launched the first Home Rule League in April 1916 at Belgaum, and Annie Besant's league followed in September 1916 at Madras. (https://vajiramandravi.com/upsc-exam/home-rule-movement/)
- `y64163a820a6` [I.A.S. (Pre) 1996 +1 more] Which one of the following regions of India is regarded as an ‘ecological hot spot’?
  (1) Western Himalayas → (3) Western Ghats. The Western Ghats is the Indian region regarded as an ecological hot spot in this question, and UPSC 1996 Q39 is keyed to Western Ghats; the Western Himalayas is not a hotspot. (https://www.unlockias.in/uppsc-2019-prelims-question-paper/q104-most-biodiversity-rich-area-india)
- `y9cf6bf6e0e8` [I.A.S. (Pre) 1997 +2 more] Which one of the following was not proposed by the 73rd Constitutional Amendment in context to Panchayati Raj?
  (2) The States will constitute their Finance Commissions → (3) The Panchayati Raj elected functionaries will be. The 73rd Amendment did not add a disqualification of Panchayati Raj functionaries having more than two children (option 3); State Finance Commissions (Art. 243-I) and elections within six months of dissolution were provided for. (https://edurev.in/question/1503804/Which-one-of-the-following-was-NOT-proposed-by-the)
- `yd140b876d50` [U.P.P.C.S. (Pre) 2024 +1 more] Given below are two statements, one is labelled as
Assertion (A) and the other as
Reason (R).
Assertion (A) : CO2, SO2 and NO2 gases get dissolved in rain water and produce acid rain.
Reason (R) : Atmosphere air is polluted due to high concentration of gases like carbon dioxide, sulphur dioxide and oxides of nitrogen.
Select the correct answer from the codes given below:
  (3) Both (A) and (R) are true, but (R) is not the correct → (1) Both (A) and (R) are true and (R) is the correct. The PW key for Q108 marks (A) 'Both (A) and (R) are true and (R) is the correct explanation of (A)'. Selfstudywala (official-key based) and Testbook agree, so this is app option 1. (https://static.pw.live/5eb393ee95fab7468a79d189/GLOBAL_CMS_BLOGS/31f8f7f3-2cc4-4933-a94a-5b50054d9e5d.pdf)
- `yed2b73975b9` [APPSC] As of May 2025, what is the monthly expenditure by the Andhra Pradesh government on social security pensions? Note: For this question, discrepancy is found in question/answer. So,this question is ignored for all candidates.
  none → (3) ₹2,758 crore. AP spends roughly ₹2,700+ crore every month on NTR Bharosa social security pensions (about ₹33,000 crore a year), and ₹2,758 crore is the only option near that figure; the commission dropped the question and I could not confirm the exact May 2025 number. (https://ommcomnews.com/india-news/andhra-pradesh-spending-rs-33000-cr-annually-on-social-security-pensions/)
- `yc0fe8e70788` [APPSC] Identify the correct sequence in the classification of government receipts:
A. Revenue Receipts
B. Capital Receipts
C. Tax Revenue
D. Non-tax Revenue Note: For this question, discrepancy is found in question/answer. So,this question is ignored for all candidates.
  none → (4) A → C → D → B. Government receipts are classified as revenue receipts (tax revenue, then non-tax revenue) followed by capital receipts, i.e. A → C → D → B. (https://www.indiabudget.gov.in/doc/Budget_at_Glance/bag1.pdf)
- `y07b5a4f7196` [APPSC 2018 Lecturers in Government Polytechnic Colleges (Eng] Which of the following pairs is NOT matched correctly? Note: For this question, discrepancy is found in question/answer. So,this question is ignored for all candidates.
  none → (4) Anemometer – wind direction. An anemometer measures wind speed (a wind vane gives direction), so 'Anemometer – wind direction' is the incorrectly matched pair. (https://www.britannica.com/science/anemometer)
- `y730138166f1` [U.P.P.C.S. (Spl) (Mains) 2004] Who was the candidate of the United Progressive Alliance (UPA) in 15th Presidential Election in India?
  (3) Droupadi Murmu → (1) Yashwant Sinha. Yashwant Sinha was the common candidate of the UPA and other opposition parties in the 2022 presidential election, while Droupadi Murmu was the NDA candidate. (https://en.wikipedia.org/wiki/2022_Indian_presidential_election)
- `ye7f7904855f` [APPSC Group-2 PYQ] Which enactment deals with withdrawal of 104. W currency notes from being legal tender?
  none → (2) Reserve Bank of India Act. The legal-tender status of the old ₹500 and ₹1000 notes was withdrawn on 8 November 2016 by a Central Government notification under Section 26(2) of the Reserve Bank of India Act, 1934. (https://www.rbi.org.in/commonman/english/scripts/FAQs.aspx?Id=1923)
- `ye67bb6889d5` [APPSC Group-II Mains 2019 Paper-3] Share of labour force in agriculture sector in AP
  (2) 65 → (1) 55. The APPSC final key for Group-II Mains Paper-III (Q149) marks 55% as the share of labour force in agriculture in AP, not 65%; the initial key also says 55%. (https://img.freejobalert.com/uploads/2020/01/Final-Key-APPSC-Group-II-Exam-Paper-III-Planning-in-India-and-Indian-Economy.pdf)
- `y5c63786d03e` [JPSC (Pre) 2016] National Mission for Green India has been initiated in the following states by Governments of India with the aim to improve the density of existing forests.
  (1) Jharkhand → (3) Both States. The National Mission for a Green India is being implemented in both Jharkhand (plan approved by its National Executive Council) and Madhya Pradesh, so 'Both States' is correct. (https://testbook.com/question-answer/national-mission-for-green-india-has-been-initiate--60350a78bf143f2445ecabd0)
- `y6b7617bcd56` [APPSC Group-II 2008] Who filed a Public Interest Petition in the Delhi High Court, seeking the striking down of the restriction that the general public could not fly the national flag?
  none → (2) Naveen Jindal. Industrialist Naveen Jindal filed the public interest petition in the Delhi High Court seeking the striking down of the restriction on the general public flying the national flag. (https://theflagcorp.com/pages/flag-code-of-india)
- `yb465430a425` [APPSC Group-II 2008] Tourism in Andhra Pradesh is
  none → (4) All are correct. Tourism in Andhra Pradesh generates direct employment, a larger amount of indirect employment (about 1.36 indirect jobs per direct job) and foreign exchange earnings, so all the statements hold (no official key found). (https://www.researchgate.net/publication/285562182_Economic_Contribution_of_Tourism_to_Andhra_Pradesh_India)
- `y433128550aa` [APPSC 2021 Horticulture Officer] In July 2022, the Andhra Pradesh Industrial Infrastructure Corporation (APIIC) exchanged a Memorandum of Understanding (MoU) with which of the following banks for providing loans to the Micro, Small, and Medium Enterprises (MSMEs) in 39 industrial parks in the first phase and other MSMEs in the next phase?
  (1) Union Bank → (4) Punjab National Bank. Punjab National Bank signed an MoU with APIIC for credit facilitation to MSMEs in 39 shortlisted industrial parks (SIDBI's separate APIIC MoU was in Nov 2023). (https://www.thehansindia.com/andhra-pradesh/guntur-pnb-exchanges-mou-with-apiic-812517)
- `y64e0e4dde44` [APPSC 2021 Medical Officer (Ayurveda) In Ayush Department] Which place was established by the treasurers of Warangal, Harihara and Bukka during modern history of Andhra? Note: For this question, discrepancy is found in question/answer. So,this question is ignored for all candidates.
  none → (2) Vijayanagara. Harihara and Bukka, former treasury officials of the Kakatiya (Warangal) kingdom, founded the Vijayanagara Empire, although APPSC dropped the question for all candidates. (https://en.wikipedia.org/wiki/Origin_of_Vijayanagara_Empire)
- `y1facb0c163c` [APPSC Group-2 PYQ] Which of the following statement / statements is / are correct?
A. The President can nominate 02 members from the Anglo-Indian Community if not adequately represented in the Lok Sabha.
B. The Governor can nominate 02 members from the Anglo-Indian Community if not adequately represented in the Legislative Assembly.
  (3) Both A and B → (1) Only A. The official APPSC Group-2 Screening (5 May 2019) final key gives 'Only A': the President nominates 2 Anglo-Indians to the Lok Sabha (Art. 331) but the Governor nominates only 1 to the Assembly (Art. 333), so B is false. (https://education.sakshi.com/sites/default/files/pdf/2019/05/05/previouspapers-groupii-appscgroup2-2018key.pdf)
- `y068c91d610f` [APPSC Group-2 PYQ] According to 2011 Census, the child sex ratio (0-6 years) in Andhra Pradesh is
  (3) 929 → (2) 940. The official APPSC final key for the Group-2 Screening Test (5 May 2019) gives 940 as the 2011 Census child sex ratio (0-6) of Andhra Pradesh; the given 929 is not supported. (https://education.sakshi.com/sites/default/files/pdf/2019/05/05/previouspapers-groupii-appscgroup2-2018key.pdf)
- `y4384f756aa1` [APPSC Group-2 PYQ] The present Chairman of the Rajya Sabha is
  none → (3) Hamid Ansari. In the APPSC Group-II Screening Test of 26.02.2017 the final key gives Hamid Ansari, who was Vice-President and ex-officio Rajya Sabha Chairman until August 2017. (https://education.sakshi.com/en/group-2/previous-papers-2016/appsc-group-ii-screening-test-question-paper-em-final-key-held-26022017-38299)
- `yb796007906a` [UPPSC (Mains) 2011] The Principles for election to the State Legislatures include

I. It will be on the basis of adult suffrage.

II. There will be only one electroal roll for every territorial constituency.

III. Religion, race, sex, etc. will have no place in the formation of the electoral roll.

IV. The political parties will be free to have their norms.
Select the correct answer using the codes given below.
  (4) All of these → (3) I, II and III. Articles 325 and 326 give one general electoral roll per territorial constituency, no exclusion on grounds of religion, race, caste or sex, and adult suffrage; nothing in the Constitution makes 'political parties free to have their own norms' a principle of election, so I, II and III are correct. (https://www.constitutionofindia.net/articles/article-325-no-person-to-be-ineligible-for-inclusion-in-or-to-claim-to-be-included-in-a-special-electoral-roll-on-grounds-of-religion-race-caste-or-sex/)
- `y08cf2890157` [APPSC Group-1 PYQ] The style of vocal Hindustani music which was non-Islamic in character was:
  (1) Taraka → (4) Dhrupad. Dhrupad is the oldest major Hindustani vocal form and is indigenous (Hindu-court) in character, unlike Khayal and Qawwali (Persian/Sufi-influenced); 'Taraka' is not a recognised vocal style. (https://en.wikipedia.org/wiki/Dhrupad)
- `yc513d2a71af` [APPSC Group-1 PYQ] Which of the following had Chandragupta Maurya's revolt against the Nanda king as its plot?
  (3) Patanjali's Mahabhashya → (2) Visakhadatta's Mudrarakshasa. Visakhadatta's Sanskrit play Mudrarakshasa dramatises Chandragupta Maurya's overthrow of the Nanda dynasty with Chanakya's help; Patanjali's Mahabhashya is a grammar commentary. (https://en.wikipedia.org/wiki/Mudrarakshasa)
- `y7224ff88539` [Chhattisgarh P.C.S. (Pre) 2016] Which of the following pairs (pact and year) is correctly matched?
  (2) Gandhi-Irwin pact- 1932 → (1) Lucknow pact - 1916. The Lucknow Pact between the Congress and the Muslim League was signed in December 1916, while the Gandhi–Irwin Pact was signed on 5 March 1931, not 1932. (https://testbook.com/question-answer/which-of-the-following-pair-pact-and-year-is-cor--63502000a716151f684e29e1)
- `y7dbe048a172` [APPSC Group-II 2011] Under the Pegged rate of exchange the demand for and supply of foreign currency
  (4) Need to come into balance → (2) Need not come into balance. Under a pegged (fixed) exchange rate the central bank buys or sells foreign currency to absorb any gap, so private demand for and supply of foreign currency need not come into balance (textbook theory; official key not seen). (https://scholar.harvard.edu/files/frankel/files/wtpfrankel.cp16.p291-306.pdf)
- `y68193c554fb` [APPSC Group-II 2011] Capital output ratio determines the rate of growth of an economy along with
  (3) Investment → (2) Savings. In the Harrod-Domar model the growth rate g = s/k, so it is determined by the savings rate together with the capital-output ratio (textbook theory and app notes followed; official key not seen). (https://en.wikipedia.org/wiki/Harrod%E2%80%93Domar_model)
- `y48c76505681` [APPSC Group-II 2011] During the Reddy Rajas' period, which text gives extensive information about sea trade?
  (2) Kashikhandam → (3) Haravilasam. Srinatha's Haravilasam records the foreign (sea) trade of the Reddy kings' period through Motupalli port; Kashikhandam is a pilgrimage-themed work (secondary sources only; official key not seen). (https://www.rcreddyiasstudycircle.com/public/images/APPSC_Grand_Test_English_Telugu_Key_(1-150)_GT-3.pdf)
- `y66213c3d0c5` [APPSC Group-II 2011] Real National Income refers to National Income at
  (4) Factor Prices → (3) Constant Prices. Real national income is national income measured at constant (base-year) prices, which removes the effect of price changes. (https://www.mospi.gov.in/sites/default/files/Statistical_year_book_india_chapters/National%20Product-writeup.pdf)
- `y52d14e4b5c5` [APPSC Group-II (old paper)] Who is the present Governor of RBI ?
  none → (2) Y.B. Reddy. Y.V. Reddy (misprinted Y.B. Reddy) was RBI Governor from 2003 to 2008; Rangarajan (1992-97) and Manmohan Singh (1982-85) were earlier Governors, and Ahluwalia never held the post. (https://en.wikipedia.org/wiki/Y._V._Reddy)
- `ycbfd6777d5a` [APPSC Group-II (old paper)] Where can one expect dry winter in India ?
  none → (1) Bengal plains. The lower Ganga/Bengal plains fall in the Köppen Cwg type (monsoon with dry winters), whereas J&K and Punjab-Haryana get western-disturbance winter rain and Tamil Nadu gets north-east monsoon rain. (https://byjus.com/free-ias-prep/climate-of-india-upsc-geography-notes/)
- `ycebf15c1b7a` [APPSC Group-II (old paper)] Tourism in Andhra Pradesh is
  none → (4) All are correct. Tourism in Andhra Pradesh creates direct employment, a larger amount of indirect employment, and earns foreign exchange, so all the statements are correct. (https://en.wikipedia.org/wiki/Economy_of_Andhra_Pradesh)
- `y56d481c66dd` [WBCS 2018] Who was the first leader arrested in the Non-Cooperation Movement?
  (3) Gandhiji → (2) CR Das. The WBCS 2018 solved paper (jigasha.com) and Testbook mark C. R. Das as the first leader arrested in the Non-Cooperation Movement; Gandhi was arrested only in March 1922. (https://www.jigasha.com/2021/06/wbcs-preliminary-exam-paper-2018-in-english.html)
- `y77f20817f41` [WBCS 2018] Expenditure for public administration falls under
  (4) None of the above → (2) non-plan expenditure. Expenditure on public administration is non-plan (non-developmental) expenditure, as marked in the WBCS 2018 solved paper and the app's notes. (https://www.jigasha.com/2021/06/wbcs-preliminary-exam-paper-2018-in-english.html)
- `y339ccd658fb` [APPSC AP History PYQ] Tripuraneni Ramaswami Chowdary wrote the lines 'Veera Gandhamu Techinaramu Veerulevaro Telpudi...'. On which occasion did he write this work?
  none → (3) Salt Satyagraha Movement. Tripuraneni Ramaswamy Chowdary wrote the song 'Veera Gandhamu Techinaramu' during the Salt Satyagraha. (https://www.thehansindia.com/featured/sunday-hans/a-chronicle-of-lives-times-561976)
- `yf3026a4b1cb` [SSC 2019] Decision given by SC are binding on
  (4) All of the above → (1) area under any state. Under Article 141 the law declared by the Supreme Court binds all courts within the territory of India (including J&K), not only district courts, so only 'area under any state' is correct and 'All of the above' is wrong. (https://www.gktoday.in/article-141/)
- `yf9f39518089` [CDS 2009] Assertion (A) Physiological density is preferable to arithmetic density as an index of population density.
Reason (R) Physiological density is based on arable land while arithmetic density is based on total area.
Codes
  (4) A is false, but R is true → (1) Both A and R are true and R is the correct explanation of A. NCERT Class XII treats arithmetic density as a crude measure and physiological density (population divided by net cultivated area) as the better measure of pressure on land, so A and R are both true and R explains A. (https://www.drishtiias.com/images/pdf/NCERT-Class-12-Geography-Part-2.pdf)
- `yaf09ea96524` [APPSC Group-1 PYQ] The relationship in India between redistributive resource transfers from the Centre to States and various economic outcomes like per capita consumption, growth in GDP, tax revenue effort is
  none → (4) negative. Economic Survey 2016-17 found no evidence of a positive relationship between redistributive resource transfers and per capita consumption, GSDP growth or own tax revenue effort, and instead found suggestive evidence of a negative relationship. (https://www.pib.gov.in/newsite/PrintRelease.aspx?relid=157798&reg=3&lang=2)
- `y991ea3c1394` [NDA 2018] Consider the following statements about Roaring Forties.

I. They are strong Westerly winds found in the oceans of Southern Hemisphere.

II. The strong East to West air currents are caused by the combination of air being displaced from the Equator towards the South Pole and the Earth’s rotation and abundance of landmasses to serve as wind breaks.
Which of the statements given above is/are correct?
  (3) Both I and II → (1) Only I. The Roaring Forties are strong westerly winds of the Southern Hemisphere, but they blow West to East, so statement II (East to West) is wrong and only statement I is correct. (https://testbook.com/question-answer/consider-the-following-statements-about-roaring-fo--5e9410e8f60d5d0d0ba571a0)
- `y0702cbc28ec` [NDA 2015] Harappan craft display an amazing degree of standardisation according to Kenoyer, what was the possible reason for such an achievement?
  (1) Availability of raw materials at local level → (4) State control. Kenoyer attributes the remarkable standardisation of Harappan crafts to centralised state control, not merely local availability of raw materials; I could not open the source to confirm this. (https://ncert.nic.in/textbook.php?lehs1=2-4)
- `ye9ce32c0e57` [U.P.P.C.S. (Pre) 1996] Right to Property is a –
  (3) Statutory Right → (4) Legal Right. After the 44th Amendment (1978) the right to property is a legal (constitutional) right under Article 300A, not a Fundamental Right; the UPPCS 1996 official key could not be checked, so this follows the standard textbook position. (https://testbook.com/question-answer/right-to-property-is-a--589c7150995a2d7730624d31)
- `y2333d3ec524` [NDA 2007] Which one of the following is correct? Due to continuous use of calcium superphosphate as fertiliser in soil, the pH of soil increases or decreases.
  (1) More than 7 → (2) Less than 7. Superphosphate is mainly acidic monocalcium phosphate, Ca(H2PO4)2, so its continued use lowers soil pH to below 7. (https://en.wikipedia.org/wiki/Superphosphate)
- `y4d9361533b6` [APPSC Group-2 PYQ] Which of the following statements is incorrect with reference to the Ikshvakus of Vijayapuri?
  (1) Puranas mentioned Ikshvakus as ' Sri Parva thiyas → (2) In their inscriptions, Ikshvakus of Vijayapuri had described themselves as the descendants of Ikshvakus of Ayodhya. The Puranas call the Ikshvakus of Vijayapuri 'Sri Parvatiyas', and Veerapurushadatta's Saka (Ujjain) marriage and Buddhist patronage are true, so the incorrect statement is option 2, since their inscriptions do not claim descent from the Ikshvakus of Ayodhya (this also matches the app's notes on the G2 2025 key). (https://en.wikipedia.org/wiki/Andhra_Ikshvaku)
- `yc531c3671a5` [BPSC (Pre) 1996] Poet Bana was inhabitant of
  (4) None of the above → (2) Thaneshwar. A BPSC solved-paper compilation gives (b) Thaneshwar for 'Poet Banabhatta was inhabitant of', as he was Harsha's court poet at Thaneswar, so 'None of the above' is not supported. (https://www.slideshare.net/slideshow/bpsc-prelims-solved-papers-english-mediumremovedpdf/265910363)
- `y059c79cd69c` [U. P. Lower Sub. (Pre) 2004] Who devastated Chola dynasty eventually?
  (2) Bakhtiyar Khalji → (4) Malik Kafur. The Chola empire was devastated by Malik Kafur, the commander of Alauddin Khalji; Bakhtiyar Khalji's conquests were in Bihar and Bengal. (https://lotusarise.com/chola-dynasty-upsc/)
- `ye73db047377` [U.P. Lower Sub. (Pre) 2013] Which one of the following statements is not correct ?
  (1) The fibre length of cotton is 1-5 cm → (4) Edible part of apple is mesocarp. The edible part of an apple is the fleshy thalamus (receptacle), not the mesocarp, so option 4 is the incorrect statement; cotton fibre length of about 1-5 cm and boron as a micronutrient are correct. (https://en.wikipedia.org/wiki/Apple)
- `y14cd75005d7` [APPSC Group-II Mains 2017 Paper-I (15-07-2017)] Which of the following are generally formed in combustion of saturated hydrocarbons?
  (1) Carbon, Water and Heat → (3) Carbon Dioxide, Water and Heat. Combustion of saturated hydrocarbons (alkanes) generally gives carbon dioxide, water and heat (and light); carbon/soot forms only in incomplete combustion, so the standard NCERT answer is option 3 (I could not open the official APPSC key to confirm what it says). (https://ncert.nic.in/textbook.php?kech2=4-4)
- `y0e590189530` [APPSC Group-I Prelims 2004 (28-03-2004)] Maumoon Abdul Gayoom, the longest-serving Head of State in Asia, started his fifth-year term as President of Maldives on November 11, 2003. How many terms had he served as the President of Maldives earlier?
  (2) 4 times → (3) 5 times. Gayoom was elected in 1978, 1983, 1988, 1993 and 1998, so he had served five terms before the term that began on 11 November 2003 (his sixth). (https://en.wikipedia.org/wiki/Maumoon_Abdul_Gayoom)
- `y156e7cf7b45` [APPSC Group-II 2008] Which committee recommended the inclusion of a separate chapter on Fundamental Duties in the Constitution?
  none → (4) Swaran Singh. The Sardar Swaran Singh Committee (1976) recommended adding a chapter on Fundamental Duties, which the 42nd Amendment inserted as Part IVA (Article 51A). (https://testbook.com/question-answer/a-committee-was-constituted-to-formulate-fundament--692fb71fd04f253bffe585b7)
- `y0c2660fb106` [APPSC Group-II 2008] The largest producer of long staple cotton is
  none → (1) Sudan. Among the listed countries, Sudan is the leading producer of long and extra-long staple cotton (with Egypt and Peru), well ahead of the USA; China and India grow mostly medium-staple cotton. (https://documents1.worldbank.org/curated/en/993231468295857200/pdf/multi-page.pdf)
- `y707f110fb22` [APPSC Group-II 2008] To estimate GDP and GSDP of Andhra Pradesh in constant prices, today the base year is
  none → (3) 1999 – 2000. At the time of the 2008 exam, Andhra Pradesh's GSDP was estimated at constant 1999–2000 prices, the base year of the series then in use. (https://www.indiastat.com/andhra-pradesh-state/data/economy/gross-state-domestic-product-gsdp)
- `y78b24b03b78` [APPSC Group-II Mains 2017 (16-07-2017)] Which of the following sectors in Andhra Pradesh registered the highest gross value added through various activities in 2015-16?
  (4) Fishing and aqua culture → (3) Crops (agriculture and horticulture). In AP's 2015-16 gross state value added, crops (agriculture and horticulture) contributed far more in absolute value than fishing and aquaculture; fishing is the fastest-growing, not the largest, sub-sector (unverified, from memory of the survey). (https://s3.ap-south-1.amazonaws.com/apfinance.gov.in/uploads/index-docs/SocioEconomicalSurvey2017-18.pdf)
- `y7b802fe0a9e` [APPSC Group-II 2008] How can we achieve favourable BoP ?
  none → (3) Both (1) and (2). A favourable BoP is achieved by encouraging more exports and reducing imports, so both (1) and (2) apply. (https://egyankosh.ac.in/bitstream/123456789/79474/1/Unit-11.pdf)
- `y82f60b6889d` [APPSC Group-II 2008] Which of the following is most important for the growth of children upto the age of 14 ?
  none → (4) Proteins. Proteins are the body-building nutrient essential for the growth and repair of tissues in growing children. (https://ncert.nic.in/textbook.php?hesc1=2-6)
- `y7398e0c65dd` [APPSC Group-II 2008] What was the official language of the Eastern Chalukyas of Vengi?
  none → (2) Telugu. APPSC-prep sources, including a Group-II 2008 AP History bit, give Telugu as the official language of the Eastern Chalukyas of Vengi; the official key was not accessible. (https://www.gktoday.in/question/which-language-served-as-the-official-language-of-the-eastern-chalukya-187015)
- `y50e509cd9c4` [U.P. P.C.S (Pre) 2025] Given below are two statements, one is labelled as
Assertion (A) and the other as
Reason (R).
Assertion (A): Public Interest Litigation in India is essential for the rule of law.
Reason (R): Public Interest Litigation provides effective access of Justice to socially and economically weaker sections.
Select the correct answer from the code given below:
  (2) (A) is false, but (R) is true → (4) Both (A) and (R) are true and (R) is the correct. Both A and R are true and R explains A: PIL relaxes locus standi to give the poor and weak access to justice, which is integral to the rule of law (coaching-site keys; official PDF could not be opened). (https://upscsociology.in/q-given-below-are-two-statements-one-is-labelled-as-assertion-a-and-the-other-as-reason-r-assertion-a-public-interest-litigation-in-india-is-essential-for-the-rule-of-law/)
- `y2efa1d722b4` [U.P. P.C.S (Pre) 2025] Given below are two statements, one is labelled as
Assertion (A) and the other as
Reason (R).
Assertion (A): The concept of National Integration involves political, economic, social, cultural and psychological dimensions and inter-relation between them.
Reason (R) : The National Integration Council was constituted in 1961 on the principle of ‘Unity in Diversity’.
Select the correct answer from the code given below :
  (3) (A) is true, but (R) is false → (4) Both (A) and (R) are true and (R) is the correct. National integration is multi-dimensional (A true) and the National Integration Council was constituted in 1961 to promote unity in diversity (R true), so the 'R is false' key is wrong; option 4 follows the majority of sources. (https://prepp.in/question/given-below-are-two-statements-one-is-labelled-as-68eb539e19a2a0e5808a1c30)
- `yfa795927995` [APPSC AP History PYQ] Which was the first criminal case registered during the Vande Mataram movement in Andhra?
  none → (2) Kakinada riot case. The official APPSC Group-II Paper-II key (Q59) gives the Kakinada (Cocanada) Riot Case of 1907 as the first criminal case in Andhra during the Vandemataram movement. (https://img.freejobalert.com/uploads/2019/09/Initial-Key-APPSC-Group-II-A.P-Social-History-Constitution.pdf)
- `y67aea937e1d` [APPSC AP History PYQ] Ravindra Bharati, a cultural institution built in Hyderabad to mark the birth centenary of Tagore, was started by whom in 1961?
  none → (1) S. Radhakrishnan. Ravindra Bharathi, built for Tagore's birth centenary, was inaugurated on 11 May 1961 by S. Radhakrishnan. (https://en.wikipedia.org/wiki/Ravindra_Bharathi)
- `y87f5a3b56c6` [APPSC AP History PYQ] Who among the following Ikshvaku kings depicted a trampled Shivalinga in their sculptures?
  (2) Shantamula II → (3) Mathariputra Vira Purusha Datta. The Nagarjunakonda sculpture showing a Shivalinga trampled underfoot is attributed to the Ikshvaku king Mathariputra Virapurushadatta (son of Santamula I), not to Shantamula II. (http://kingpublications.blogspot.com/2019/12/telangana-history-ikshvaks.html)
- `y04cd43f70f7` [APPSC Group-1 PYQ] Which of the following politicians completed 50 years as Legislator in March, 2017?
  none → (1) K.M. Mani. K.M. Mani (Pala, Kerala Congress-M) completed 50 years as a legislator in the Kerala Assembly in March 2017; Ganpatrao Deshmukh's 50 years were marked in 2012 and H.A. Halim died in 2015. (https://zeenews.india.com/tags/km-mani.html)
- `y89c39e9d3dd` [U.P.P.C.S. (Mains) 2012] Which of the following are the members of the electoral college for electing the President of India?
Select the correct answer from the code given below:
1. All the members of the two Houses of Parliament.
2. All the elected members of the State Legislative Assemblies.
3. All the elected members of the U.T. Assemblies
4. All the Governors and Lt. Governors
  (4) 1, 2, 3 and 4 → (3) 1, 2 and 3 only. Under Article 54 the electoral college is the elected members of both Houses of Parliament and of the State Legislative Assemblies, plus the elected members of the Delhi and Puducherry assemblies; Governors and Lt. Governors do not vote, so statements 1, 2 and 3 are right and 4 is wrong. (https://en.wikipedia.org/wiki/Electoral_College_(India))
- `y8612be52895` [APPSC Group-II 2011] Implementation of uniform sales tax in India commenced from 1st January
  (4) 2003 → (1) 2000. Uniform floor rates of sales tax were implemented by the States and UTs from 1 January 2000 (Economic Survey 1999-2000 and GST Council discussion paper), not 2003. (https://www.indiabudget.gov.in/budget_archive/es99-2000/chap23.pdf)
- `yef2bbde0be4` [APPSC AP History PYQ] When Gandhiji asked for donations in the independence movement, which woman was the first in Andhra to donate all her gold and jewellery?
  none → (2) Maganti Annapurnamma. Maganti Annapurnamma (Annapurna Devi) of Eluru gave all her gold ornaments to Gandhiji during his 1921 Andhra tour, and is regarded as the first Andhra woman to do so. (https://www.thehansindia.com/posts/index/womenia/2018-08-15/women-in-freedom-struggle/405624)
- `y7372a22dede` [APPSC AP History PYQ] Which was the most popular form of marriage in the Vijayanagara Empire?
  none → (4) Brahma vivaham. Brahma vivaha is the most honoured and widely approved of the eight forms of Hindu marriage, and I followed the app's notes in taking it as the most popular form in the Vijayanagara Empire. (https://en.wikipedia.org/wiki/Brahma_marriage)
- `y39a19ad3aeb` [APPSC AP History PYQ] What did the word 'Udranga' refer to during the ancient Chalukya period?
  none → (3) Tax on water. Udranga is generally explained as a water (irrigation) tax, so 'tax on water' is the best-supported option. (https://www.gktoday.in/question/which-of-the-following-was-a-tax-imposed-on-tempor)
- `y34be75585ef` [APPSC AP History PYQ] Who received the title of 'Gandharva Vidya Visarada' in the Chalukya court?
  none → (2) Challavva. The APPSC Group II Paper II initial key gives Chellavva (Challavva), the Chalukya court dancer, as the holder of the title 'Gandharva Vidya Visarada'. (https://img.freejobalert.com/uploads/2019/09/Initial-Key-APPSC-Group-II-A.P-Social-History-Constitution.pdf)
- `y30821591358` [APPSC Group-II Mains 2019 Paper-3] According to 2011 census the main workers in service sector is
  none → (1) 26.70 percent. The APPSC Group-II Mains Paper-III official initial key (Q38) gives 26.70 percent as the share of main workers in the service sector per the 2011 census. (https://cdn-images.prepp.in/public/image/APPSC_Group_2_Mains_Paper_III_2018_Question_Paper_with_Key_0be7336fd0cf42cfe9f8876f74fed961.pdf)
- `y75da7cc62c8` [APPSC Group-II 2019] Who told us that the Vijayanagara Empire had more than 300 port towns?
  (3) Barbosa → (4) Abdul Razak. The figure of about 300 sea-ports in the Vijayanagara empire is attributed to the Persian envoy Abdur Razzaq, not to Barbosa. (https://zenodo.org/records/19500273)
- `y415bd5dfd27` [UPSC CSE Prelims 2023] Consider the following statements regarding mercury pollution:
1. Gold mining activity is a source of mercury pollution in the world.
2. Coal-based thermal power plants cause mercury pollution.
3. There is no known safe level of exposure to mercury.
How many of the above statements are correct?
  (2) Only two → (3) All three. The UPSC key for Prelims 2023 (Set A, Q59) is (c): all three statements are correct. Gold mining and coal-fired power plants emit mercury, and there is no known safe level of mercury exposure. (https://www.drishtiias.com/images/pdf/1685947263_UPSC%202023%20Ans.%20English-1.pdf)
- `y66744ee4e39` [UPSC CSE Prelims 2025] Consider the following space missions:
1. Axiom-4
2. SpaDEx
3. Gaganyaan
How many of the space missions given above encourage and support microgravity research?
  (2) Only two → (3) All the three. Axiom-4, SpaDeX and Gaganyaan all support microgravity research, so the answer is all three (C). (https://maxias.in/blog/upsc-prelims-2025-key-with-solutions-analysis/)
- `y20027168808` [APPSC Group-II 2008] The essential condition of equilibrium in a two sector model is
  none → (2) Savings = Investment. In a two-sector (households and firms) economy, equilibrium income is reached when planned saving equals planned investment (S = I); the app had no key, and no official key could be opened. (https://testbook.com/question-answer/the-essential-conditionofequilibrium-i--67827e3f712f48078519e987)
- `yf7940e1a0da` [APPSC Group-II 2008] During whose regnal period did Buddhism receive great patronage in the Ikshvaku kingdom?
  none → (1) Virapurushadatta. Buddhism received great patronage under Ikshvaku king Virapurushadatta, whose reign is regarded as the golden age of Buddhism at Nagarjunakonda. (https://www.scribd.com/document/353134723/AP-HISTORY-PYQ-pdf)
- `y9e4ff40b700` [APPSC Group-II 2008] Which one of the following was not a form of industrial capital and colonial exploitation during British rule in India ?
  none → (3) Construction of railways was financed by the British government. Indian railways were built with private British capital on a guaranteed 5% return paid from Indian revenue, not financed by the British government, so statement 3 is the one that was not a form of exploitation. (https://digital.nios.ac.in/content/315en/315_History_Eng_Lesson17.pdf)
- `ybe9d2dd8af8` [U.P.P.C.S. (Pre) 2022] Given below are two statements, one is labelled as
Assertion (A) and the other as
Reason (R).
Assertion (A) : Rainfall occurs in the winter season in Mediterranean climate.
Reason (R) : In summer these regions remain under the influence of dry terrestrial winds.
Select the correct answer from the code given below :
  (4) Both (A) and (R) are true but (R) is not the correct → (2) Both (A) and (R) are true and (R) is the correct. Mediterranean regions get winter rain from the westerlies and stay dry in summer under dry offshore (land) trade winds as the pressure belts shift, so both A and R are true and R explains A. (https://testbook.com/question-answer/given-below-are-two-statements-one-is-labelled-as--62a93cbe8e8a60975147e95e)
- `y19c5b3a7bc1` [MPPSC 2015] Which river in Maharashtra flows all around the year (Perennially)?
  (3) Godavari → (4) None of these. No river in Maharashtra is truly perennial: Godavari is largely seasonal there, so the answer is 'None' (Testbook and Sarthaks solutions to the MPSC 2015 question; official key not opened). (https://testbook.com/question-answer/which-river-in-maharashtra-flows-all-round-the-yea--6002f7ef79ca3f43b14f8aff)
- `yab4d7ac81e2` [MPPSC 2015] Consider the following statements regarding the Parliament.

I. The provision for the calling Attention Notices was first made in the year 1954.

II. Notices of calling Attention have to be given by members in writing by 10:00 AM.

III. A member can give not more than one calling Attention Notice for any one sitting.
Which of the above statements is not correct?
  (1) I and II → (3) Only III. Calling Attention began in 1954 and notices are due by 10.00 hours, so I and II are correct; a member may give up to two notices per sitting, so only statement III is incorrect. (https://testbook.com/question-answer/consider-the-following-statements-regarding-the-pa--6002f93a637270a27e79b0a2)
- `ybc43160aae2` [U.P.P.C.S. (Mains) 2007] Which sector got high rate of growth in its cooperative units ?
  (2) Cotton textile → (1) Sugar. Sugar is the industry where cooperative units have grown most strongly and are most successful in India; cotton textile cooperatives are comparatively small (based on the standard NCERT view, with no official key retrieved). (https://www.legacyias.com/chapter-6-manufacturing-industries/)
- `ye7e903f4dad` [U.P. Lower Sub. (Mains) 2013] Which of the following is not correct with respect to the composition of Panchayat?
  (3) Each State will constitute Panchayat at the village, → (4) Panchayat at the intermediate level shall not be. Art. 243B(1) requires Panchayats at village, intermediate and district levels (so option 3 is correct), while Art. 243B(2) says intermediate-level Panchayats 'may not' be constituted in a State with population up to 20 lakh, so option 4's 'shall not be' is the incorrect statement (official key not retrieved; judged from the constitutional text). (https://www.tnrd.tn.gov.in/constitutionalprovision.html)
- `yfdbf0d34542` [APPSC 2025 Thanedar] Hindalco Industries plans to invest R 586 crore in Andhra Pradesh to manufacture aluminium parts for which company's products ?
  none → (4) Apple. Hindalco will invest about ₹586 crore in an aluminium extrusion plant at Kuppam, Andhra Pradesh, to make raw material for the iPhone (Apple) chassis. (https://www.icicidirect.com/research/equity/trending-news/hindalco-invests-586cr-to-produce-aluminum-for-iphones)
- `yf30cd4b82ef` [APPSC Gazetted Posts GS 2010 (Notification 30/2008)] By Mauryan times the main port of the Ganges basin was
  none → (3) Tamralipti. Following Basham, by Mauryan times Tamralipti became the main sea port of the Ganges basin. (https://www.wisdomlib.org/history/essay/history-culture-and-antiquities-of-tamralipta/d/doc1455682.html)
- `y2677a92e184` [APPSC AP History PYQ] Who was the Reddy king who had the title 'Rachuru Durga Vibhala'?
  (1) Prolaya Vemareddy → (3) Anavema. The title 'Rachuru Durga Vibhala' (destroyer of the Rachuru fort) is attributed to Anavema Reddy of Kondaveedu, as in the APPSC Group 2 2017 question and the app's notes; the official key PDF itself was not opened. (https://www.careerpower.in/blog/wp-content/uploads/2025/09/24183001/English-Paper-2.pdf)
- `ybb1398b058a` [APPSC Gazetted Posts GS 2010 (Notification 30/2008)] Which place was occupied by India in telephone connection?
  none → (2) Second. Around 2008–2010 India had the world's second-largest telephone network, after China (not verified against the APPSC key). (https://www.trai.gov.in)
- `y63a46480de4` [APPSC Gazetted Posts GS 2010 (Notification 30/2008)] Which of the following diseases is shivering the world?
  none → (2) Swine influenza. Swine influenza (H1N1) was the disease that caused the 2009–10 global pandemic declared by WHO (the official APPSC key was not checked). (https://www.who.int/news-room/questions-and-answers/item/influenza-a-(h1n1)-pandemic)
- `y500b69c0cd0` [APPSC Gazetted Posts GS 2010 (Notification 30/2008)] What is main goal in Buddhism is?
  none → (4) Nirvana. Nirvana, the end of suffering and of the cycle of rebirth, is the ultimate goal in Buddhism; the Madhyama Marga is only the path to it. (https://ncert.nic.in)
- `yb1265c8443c` [U.P. R.O./A.R.O. (Mains) 2021] Which of the following is incorrect regarding the Pradhan Mantri Krishi Sinchai Yojana?
  (3) Enhancement of recharging of aquifers → (2) Construction of wells. PMKSY objectives include creating and renovating water sources, rain-water harvesting structures and enhancing aquifer recharge, so 'enhancement of recharging of aquifers' is correct; construction of wells is the item not listed (the same question in the 67th BPSC Prelims Re-exam has it as the incorrect statement). (https://www.manage.gov.in/fpoacademy/CGSchemes/PMKSY.pdf)
- `ya8b6fd4d21c` [APPSC AP History PYQ] In the second Visalandhra Mahasabha held at Hyderabad in 1954, who among the following strongly supported Visalandhra?
  none → (1) Swami Ramananda Theertha. Swami Ramananda Tirtha publicly backed linguistic states and the Greater Andhra stand of Kaleswara Rao, and is the best-supported of the four options; J.V. Narasinga Rao only joined the Mahasabha's meetings, and Burgula Ramakrishna Rao's support was never stated in writing. (http://telugujativedika.blogspot.com/2010/12/greater-andhra-movement-2-by.html)
- `y123bfdc01dc` [APPSC AP History PYQ] Who is not a member of the 'Brahmatraya'?
  none → (2) Chilakamarthi Lakshminarasimham. The Andhra Brahmo 'Brahmatraya' is recalled as Veeresalingam, Raghupathi Venkataratnam Naidu and Desiraju Peda Bapayya, so Chilakamarthi Lakshminarasimham is not a member (not confirmed against a source I could open). (https://en.wikipedia.org/wiki/Raghupathi_Venkataratnam_Naidu)
- `y7eef651141a` [NDA 2019] Planning in India drew on
  (1) the new economic programme of Lenin → (2) the Fabian Socialism of Sidney and Beatrice Web. Indian planning drew on the Fabian socialism of Sidney and Beatrice Webb (alongside Soviet planning); Lenin's NEP is not named as its source. Based on a coaching note only, as the official UPSC key could not be opened. (https://jovikdefenceprep.com/indian-economic-planning-five-year-plans/)
- `y7b68c74e49c` [APPSC AP History PYQ] Who was the cause of the Palnadu war?
  (2) Balachandra → (3) Nagamma. The Palnadu war arose from Nayakuralu Nagamma's intrigue, which exiled Malideva and Brahmanaidu and had Alaraju poisoned; Balachandra was only a hero who died in the war. (https://en.wikipedia.org/wiki/Battle_of_Palnadu)
- `y05ab7d90fa2` [APPSC AP History PYQ] The first copperplate found in Andhra Pradesh belongs to?
  none → (2) Brihatphalayanas. The Kondamudi copper-plate grant of Jayavarman of the Brihatphalayanas is regarded in standard Andhra history texts as the earliest copperplate found in Andhra. (https://en.wikipedia.org/wiki/Bruhatpalayana)
- `ycaf849c48aa` [APPSC AP History PYQ] Which name was first suggested by the Joint Select Committee for the new state during the formation of Andhra Pradesh?
  (3) Visalandhra → (4) None of these. The Joint Select Committee indicated the name 'Andhra Pradesh' (the draft bill had 'Andhra Telangana'; Visalandhra was a movement slogan), so none of the listed names is correct. (https://kpiasacademy.com/gentlemens-agreement-1956-telangana-andhra-merger/)
- `y0f253c852da` [M.P.P.C.S. (Pre) 2010] Size of virtual memory depends on –
  (3) Disc space → (1) Address lines. The size of virtual memory (the virtual address space) is determined by the number of CPU address lines, e.g. 32 address lines give 2^32 bytes; disc space only limits the backing store. (https://testbook.com/question-answer/size-of-virtual-memory-depends-on--6110cc12659a4dfc5ca86055)
- `ycb80910d76a` [M.P.P.C.S. (Pre) 2013 +2 more] When did Swami Vivekananda deliver his speech in ‘World Religion Conference’ in Chicago?
  (3) 1881 → (2) 1892. Swami Vivekananda delivered his speech at the Parliament of the World's Religions in Chicago in September 1893; in the MPPSC 2013 paper option 2 is 1893 (the app's '1892' looks like a misprint), and 1881 is wrong. (https://testbook.com/question-answer/when-did-swami-vivekanand-deliver-his-speech-at-th--60b89d64145b9f3f41dfbaf0)
- `y7350f11e085` [I.A.S. (Pre) 2022] Consider the following States:
1. Andhra Pradesh
2. Kerala
3. Himachal Pradesh
4. Tripura
How many of the above are generally known as tea-producing States?
  (3) Only three States → (4) All four States. Andhra Pradesh, Kerala, Himachal Pradesh and Tripura are all recognised tea-producing States, so all four is the answer given for UPSC Prelims 2022. (https://testbook.com/question-answer/consider-the-following-states1-andhra-pradesh--629dc891033652792fde19be)
- `y696323b18cc` [IAS (Pre) 1996] Which one of the following elements is alloyed with iron to produce steel which can resist high temperatures and also have high hardness and abrasion resistance?
  (2) Chromium → (4) Tungsten. Tungsten is the element alloyed with iron to make steel that keeps its hardness at high temperature and resists abrasion, as in high-speed and tool steels. (https://examrobot.com/ias/1996/science-technology/one-elements-alloyed-iron-produce-steel-which-resist-high-temperatures-also-high-hardness-abrasion)
- `y535a8ab0e1d` [APPSC Group-1 PYQ] Which of the following could be the most important factor in decline of slate industry in Markapur?
  none → (4) Change in user preferences. Markapur's slate industry declined mainly because demand fell as plastic and other material slates replaced stone slates, which is a change in user preferences. (https://www.thehansindia.com/posts/index/andhra-pradesh/2015-01-10/markapur-stone-slates-losing-sheen/125451)
- `ya1c54b40dec` [APPSC AP History PYQ] During the period of the Chalukyas, who received the title "Gandharva Vidya Visarada"?
  none → (4) Chellavva. Under Eastern Chalukya Bhima the musician-dancer Chellavva (daughter of the musician Mallappa) was honoured with the village of Attili; she is the Chalukya-period recipient of the 'Visarada' title (exact wording not confirmed in a source, so moderate confidence). (http://andhraportal.org/history-eastern-chalukya-dynasty/)
- `ybc868606254` [APPSC AP History PYQ] A direct battle between the British and the followers of Alluri Sitarama Raju took place here?
  none → (4) Panjerighat. Chintapalli, Rajavommangi and Addateegala were police-station raids by Alluri's followers, so by elimination Panjerighat is the site of the direct battle with the British forces (not verified from a source). (https://en.wikipedia.org/wiki/Rampa_Rebellion_of_1922)
- `ya6c23b8297b` [APPSC AP History PYQ] When was the Hyderabad State Congress formed?
  none → (2) 28 February 1938. The Hyderabad State Congress was formed after the February 1938 Haripura resolution, so 28 February 1938 is the best-supported date, and 29 January 1938 would predate Haripura (not verified from a source that states the exact date). (https://en.wikipedia.org/wiki/Hyderabad_State_Congress)
- `y15fc4f332d6` [M.P.P.C.S. (Pre) 1995] Gold is dissolved in –
  (2) Nitric acid → (3) Mixture of Sulfuric and Nitric Acid. Gold does not dissolve in nitric, hydrochloric or sulfuric acid alone; it dissolves only in oxidising acid mixtures such as aqua regia (3 HCl : 1 HNO3), and of the options only the mixture of acids (nitric with sulfuric) can dissolve it. I could not find the official key. (https://www.911metallurgist.com/blog/solubility-of-gold/)
- `y6f79360150c` [APPSC AP History PYQ] Who built the fort at Machilipatnam in 1611?
  none → (3) The Dutch. The Masulipatnam (Machilipatnam) fort was built by the Dutch, who settled there from 1605, while the British only opened a factory there around 1611. (https://vajiramandravi.com/current-affairs/machilipatnam/)
- `yebf980e3473` [APPSC AP History PYQ] Famous dancer Amrapali renounced her profession and followed Buddha; likewise, who among the following dancers followed Gandhi?
  (3) Unnava Lakshmibayamma → (4) Yamini Poorna Tilakam. Yamini Poorna Tilakam is the only dancer among the options and the one known as the dancer who gave up her profession and followed Gandhi, whereas Unnava Lakshmibayamma was a freedom fighter and writer; this rests on background knowledge, not a source that states it directly. (https://ierj.in/journal/index.php/ierj/article/download/3113/3444/6406)
- `y9fff10615d1` [APPSC AP History PYQ] Who was the first woman to announce during Gandhi's visit to Andhra that she would boycott foreign clothes and wear Khaddar?
  none → (2) Maganti Annapurnamma. During Gandhi's 1921 Andhra tour, Maganti Annapurnamma was the first woman to announce she would discard foreign clothes and wear khaddar. (https://ierj.in/journal/index.php/ierj/article/download/3113/3444/6406)
- `y04c354545cf` [APPSC Group-I Prelims 2024 (17-03-2024)] Consider the following statements:

I. Silicon and oxygen are common elements in all types of feldspar and sodium, potassium, calcium, aluminium etc. are found in specific feldspar variety.

II. Almost one-fourth of the Earth's crust is composed of feldspar and quartz.
Which of the above statements is/are correct?
  (3) Both of them → (1) Statement I only. Followed NCERT Class 11 (Minerals and Rocks): Statement I on feldspar is verbatim NCERT, but the textbook says half (not one-fourth) of the Earth's crust is feldspar, so Statement II is wrong and only Statement I is correct. (https://ncert.nic.in/textbook/pdf/kegy105.pdf)
- `y400fc5b4926` [APPSC Group-I Prelims 2024 (17-03-2024)] In the context of Centre – State Relations, which of the following statement/statements are valid?

I. Punchhi Commission had recommended that the procedure that is followed for the removal of President should also be applicable for the impeachment of Governors as well.

II. The law that is made by the Parliament with respect to any matter in the State List in relation to the State in which President's rule is imposed, cannot be 're-enacted' by the State Legislature after the President's rule is ended.

III. The Sarkaria Commission was not the first to recommend the establishment of an Inter-State Council.

IV. Only the Lok Sabha can pass a resolution declaring that it is necessary in the national interest that the Parliament should make laws with respect to Goods and Services Tax.
Select the correct answer using the codes given below:
  (1) Only III → (2) I and III. Followed Laxmikanth and the Constitution: Punchhi recommended impeachment of Governors by the State Legislature like the President (I true), Article 357(2) allows re-enactment by the State Legislature (II false), the ARC preceded Sarkaria on the Inter-State Council (III true), and the Article 249 GST resolution is passed by the Rajya Sabha only (IV false), so I and III are correct. (https://prsindia.org/policy/report-summaries/commission-on-centre-state-relations-punchhi-commission)
- `yf5eb6009a5b` [APPSC Group-I Prelims 2024 (17-03-2024)] In connection with the lapsing of Bills, which of the following statement/statements is/are valid?

I. If the Lok Sabha has passed the Bill, but if the Bill has still not been discussed in the Rajya Sabha, then such a Bill does not lapse.

II. A Bill returned by the President for reconsideration of the Houses will not lapse. However, the Lok Sabha should not have been dissolved by the time the Bill is returned.

III. A Bill that is passed by both the Houses but pending for President's assent will not lapse.

IV. A Bill that is pending in the Rajya Sabha but which has not been passed by the Lok Sabha will also lapse.
Select the correct answer using the codes given below:
  none → (1) Only III. Followed Laxmikanth: a Bill passed by the Lok Sabha but pending in the Rajya Sabha lapses (I false), a Bill returned by the President does not lapse, so II's added Lok Sabha condition is spurious (II false), a Bill pending assent does not lapse (III true), and a Bill pending in the Rajya Sabha but not passed by the Lok Sabha does not lapse (IV false), so only III is correct. (https://prsindia.org/billtrack/how-a-bill-becomes-law)
- `yd1e94386035` [APPSC Group-II 2008] Which of the following is a direct method of reducing economic inequalities ?
  none → (4) Ceiling on holding. A ceiling on holdings directly limits ownership of property and so directly reduces inequality, whereas estate duty, wealth tax and capital gains tax are fiscal (tax) measures. (https://en.wikipedia.org/wiki/Land_reform_in_India)
- `y5a9e72d2650` [APPSC Group-II 2008] Who was the first Deputy Speaker of the Lok Sabha constituted after Independence in India?
  none → (1) Anantasayanam Ayyangar. M. Ananthasayanam Ayyangar was the first Deputy Speaker of the Lok Sabha (30 May 1952 – 7 March 1956) under Speaker G.V. Mavalankar. (https://en.wikipedia.org/wiki/M._A._Ayyangar)
- `y6c79bdd7510` [APPSC Group-II 2008] Which of the following provides long term finance to industries ?
  none → (1) IDBI. IDBI was established as the apex development financial institution to provide long-term finance to industry. (https://en.wikipedia.org/wiki/Industrial_Development_Bank_of_India)
- `y31980592fe7` [APPSC Group-II 2008] Which of the following classes participated the least in the Indian National Movement ?
  none → (1) Princes of states. The princes of the princely states largely stayed loyal to the British and participated least in the Indian National Movement, unlike peasants and capitalists. (https://en.wikipedia.org/wiki/Princely_state)
- `yd3f4489664d` [APPSC Group-I Prelims 2024 (17-03-2024)] Which of the following statement/statements is/are valid in connection with Sustainable Development Goals (SDGs)?

I. Achieving Goal 10 will require an entire reform of the financial system that promotes equitable pay and decent work for young people.

II. NITI Aayog has developed the National Indicator Framework (NIF) for facilitating monitoring of SDGs in India.

III. 'Mission LiFE' aims to influence government and industrial policy to support both sustainable consumption and production.

IV. The concept of global citizenship embedded in Sustainable Development Goal 4 (SDG 4) is a reference term that indicates flexible citizenship rights across countries for the purpose of facilitating better labour markets.
Select the correct answer using the codes given below:
  (4) II and IV → (3) Only III. The National Indicator Framework for SDGs was developed by MoSPI, not NITI Aayog, and SDG 4's global citizenship does not mean flexible citizenship rights, so II and IV are false and only III (Mission LiFE) is valid. (https://www.mospi.gov.in/sustainable-development-goals)
- `y46bd8bc8532` [WBCS 2017] The unorganised sector of India is characterised by
  (1) more currency transactions → (3) more barter transactions. The WBCS 2017 key gives 'more barter transactions' as the answer for the unorganised sector of India, so option 3 is correct and the given key of option 1 is wrong. (https://www.wbcsmadeeasy.in/wp-content/uploads/2017/01/WBCS-Prelims-Answer-key-2017.pdf)
