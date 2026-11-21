# APPSC Group 2 History: where the examiners' questions come from

Scope: Indian History (Prelims/Screening, leaf P1.*) and AP history / social and cultural history of AP (Mains Paper I, leaf M1A.*). Evidence comes from (a) web book lists and analyses and (b) a mechanical match of the official PYQs in `/home/user/Group-app/data/g2papers/*.json` against the local source library `/home/user/Group-app/data/notes2026/src/{indian-history,ap-history}/*.txt`, plus raw Wikipedia text.

Method for the local match: 461 history questions (all P1.* and M1A.* leaves across the 2008 P1-P3, 2012 P1, 2017 prelims and mains, 2019 prelims and mains, 2024 prelims and 2025 mains papers). For each, I took the stem plus the correct option, built every 5-word sequence with at least 3 content words, and counted exact hits in each library file. The scripts and outputs are in `/tmp/claude-0/-home-user/4666e051-48dd-5910-831c-f2c172f98923/scratchpad/dr-hist/` (match.py, matches.json, matches2.json; Wikipedia raw text is in `wiki/`). Strength labels: **verbatim** means a clause matches word for word, **clear fact match** means the same distinctive fact or name is present in different words, **likely** means the topic is covered but the evidence is weak.

## Which books do toppers, coaching institutes and APPSC analyses name for Group 2 history, and which are cited most consistently?

### Takeaway
The public book lists are thin and come from coaching or aggregator sites. None of them is a topper's account or an APPSC statement. The books named most often are B.S.L. Hanumantha Rao's *AP History*, the Vijeta *Social and Cultural History of Andhra Pradesh*, P. Raghunadha Rao's *History and Culture of Andhra Pradesh*, Telugu Academy books or Telugu-medium NCERTs, and Bipan Chandra's or Saeed's modern history. I found no source that ties APPSC's examiners to any particular book, and Telugu Academy shows up mainly for polity, economy and geography rather than history.

### Cited Findings
- Telugu-medium book lists name: *AP History* by B.S.L. Hanumantha Rao; *Andhra Pradesh History* by Jogi Naidu; *History and Culture of Andhra Pradesh (Earliest Times to 2019)* by P. R. Rao (P. Raghunadha Rao); Telugu Academy books or Telugu NCERTs (plus "Seenaiah Sir notes") for Indian history; Saeed's *Modern Indian History* or Bipan Chandra's *Modern History* (Telugu) for modern India; and for social and cultural history of AP, the Vijeta book and Saeed's *Andhra Pradesh History and Culture*. These come from aggregator search results. — [Testbook](https://testbook.com/appsc-group-2/books-for-preparation); [Embibe](https://www.embibe.com/exams/appsc-group-2-books/); [Freshersnow](https://www.freshersnow.com/appsc-group-2-books/); [BYJU'S Exam Prep](https://byjusexamprep.com/state-exams/appsc-group-2-exam-books) (BYJU'S returned 503 and Freshersnow returned 404 when fetched; their content is known only from search snippets).
- Testbook's Group 2 list recommends one history title, for both Prelims Section B and Mains Paper I: "APPSC Group-2 Social And Cultural History Of Andhra Pradesh" by Vijeta (Vijeta Publications). — [Testbook](https://testbook.com/appsc-group-2/books-for-preparation)
- An APPSC reference list on a KL University PDF names I. Seenayya, *Social and Cultural History of Andhra Pradesh*; P.V.K. Prasada Rao, *Andhra Pradesh Samagra Charitra*; and P. R. Rao, *History and Culture of Andhra Pradesh (Earliest Times to 2019)*. Its Telugu Akademi entries are geography and economy books. This is from the search summary only, because the PDF returned 404 when fetched. — [KL University reference list](https://WWW.KLUNIVERSITY.IN/ba/pdf/Reference-Books-appsc.pdf)
- Coaching analyses of the 2025 Mains say Paper I Section A (75 questions) covered AP social and cultural history, was easy to moderate, and was heavy on assertion-reason questions. None of them names a source book. — [Sakshi Education](https://education.sakshi.com/en/appsc/education-news/appsc-group-2-mains-2025-exam-analysis-expected-cutoff-scores-subject-wise-topics-172337); [Adda247](https://adda247.com/exams/andhra-pradesh/appsc-group-2-mains-question-paper-2025)
- The owner's own library ranks NextGen IAS notes first, then NextGen Rocket Sheets. Among standard books it holds only Spectrum (Rajiv Ahir, *A Brief History of Modern India*, rev. ed. 2019), Nitin Singhania (*Indian Art and Culture*, 2nd ed., McGraw Hill), PMF notes and a PW OnlyIAS NCERT compilation. It has **no Telugu Academy, B.S.L. Hanumantha Rao, P. Raghunadha Rao or Sarojini Regani text.** — local file `/home/user/Group-app/data/notes2026/SOURCES-LOCAL.md`

### Inferences
- Across lists, the most consistent AP-history names are B.S.L. Hanumantha Rao, P. Raghunadha Rao and the Vijeta social and cultural history book; for modern India it is Bipan Chandra. Spectrum appears in Group 1 lists rather than Group 2 lists.
- The lists recycle one another and include no topper testimony, so "most cited" means "most copied between coaching sites". It does not show what examiners use.

### Gaps
- I found no topper interview naming Group 2 history books. The Unacademy and Adda247 Telugu strategy sessions are behind logins or are videos.
- I found no APPSC statement on reference books. Edition years are unknown for every AP-history book.
- I could not confirm the coordinator's suggested names (Sarojini Regani, Vakulabharanam, B.N. Sharma, Tamil Nadu or old NCERT, AP SCERT) as Group 2 recommendations in any source I fetched.

## Matching actual PYQs to sources

### Takeaway
1. **AP history questions match only PYQ compilations.** In 2008, 2017 and 2019, the AP-history questions match the NextGen and Powerplay files almost word for word. On inspection, those files are one-liner compilations of earlier APPSC questions (lines such as "⇒ P. Anandacharyulu ... In which year did he become President of the Congress -1891"). The match is circular and proves nothing about the examiners' source.
2. **Coaching texts are not the source.** Once those compilations are excluded, almost no history question matches the coaching notes, Spectrum, Singhania or PMF verbatim. Of 461 questions, only about 30 have 3 or more matching 5-word sequences, and several of those are boilerplate.
3. **The 2025 Mains Paper I has clear Wikipedia fingerprints.** Several statements are lifted verbatim from English Wikipedia (Nannaya, Gurram Jashuva, Eastern Chalukya architecture, Thousand Pillar Temple). This is the only source I could tie to examiner wording with verbatim evidence.

### Cited Findings

**Verbatim matches to Wikipedia (2025 Mains Paper I)**
- **Q10 (M1A.1.3/5), Nannaya.** Statement I: "Nannaya Bhattu was a Telugu poet and the author of 'Andhra Mahabharatam', a Telugu retelling of the Sanskrit-language Mahabharata." Wikipedia's lead reads: "...was a Telugu poet and the author of *Andhra Mahabharatam*, a Telugu retelling of the Sanskrit-language *Mahabharata*." **Verbatim.** Statement II (credited with writing *Andhra Shabda Chintamani*, a Sanskrit work on Telugu grammar) mirrors Wikipedia's "also credit him with writing the Sanskrit-language *Andhra-shabda-chintamani*, said to be the first work on Telugu grammar". **Close paraphrase.** — [Wikipedia: Nannayya](https://en.wikipedia.org/wiki/Nannaya)
- **Q34 (M1A.5.5), Gurram Jashuva.** The options "He was appointed to the Andhra Pradesh Legislative Council as a member in 1964", "He was presented the Sahitya Akademi award for his work titled 'Gabbilam' in 1964" (the false option; Wikipedia says *Kreesthu Charitra*), "awarded the Padma Bhushan by the Government of India" and the September 28 birth date all reproduce Wikipedia's bullet sentences. Wikipedia has "Jashuva was presented the Sahitya Akademi Award for his work titled *Kreesthu Charitra* in 1964" and "Jashuva was appointed to the Andhra Pradesh Legislative Council as a member in 1964". The examiner built the false option by swapping in the title *Gabbilam*. **Verbatim.** — [Wikipedia: Gurram Jashuva](https://en.wikipedia.org/wiki/Gurram_Jashuva)
- **Q13 (M1A.1.3/6), Draksharama.** "exemplifies the independent style of the Chalukya-Cholas, incorporating Pallava and early Chalukya influences" matches Wikipedia's "The Eastern Chalukyas, following the Pallava and Chalukya traditions, developed their own independent style of architecture, which is visible in the Pancharama shrines (especially the Draksharama temple)". **Clear fact and phrase match.** — [Wikipedia: Eastern Chalukyas](https://en.wikipedia.org/wiki/Eastern_Chalukyas)
- **Q17 (M1A.2.2/4), Thousand Pillar Temple.** "built in 'Trikuta style' ... three shrines" and "influence of Chalukya temple architecture" match Wikipedia's "later Chalukyan and early Kakatiyan Architecture, star-shaped and triple shrined (Trikutalaya)". Wikipedia names Shiva, Vishnu and Surya; the question says Rudreshwara, Vasudeva and Suryadeva. **Clear fact match.** — [Wikipedia: Thousand Pillar Temple](https://en.wikipedia.org/wiki/Thousand_Pillar_Temple)
- **Q32 (M1A.3.11/1), "Abhinava Nannaya" = Rayaprolu Subbarao.** Wikipedia: "He is known as Abhinava Nannaya". The phrase does not appear anywhere in the local coaching library. **Clear fact match.** — [Wikipedia: Rayaprolu Subba Rao](https://en.wikipedia.org/wiki/Rayaprolu_Subba_Rao)
- **Q27 (M1A.4.5), Krishna Patrika.** The option "Krishna Patrika was started in 1902 by Konda Venkatappaya" matches Wikipedia's "founded in 1902 by Konda Venkatappayya and Dasu Narayana Rao". **Clear fact match.** — [Wikipedia: Krishna Patrika](https://en.wikipedia.org/wiki/Krishna_Patrika)

**2025 Mains facts that the local coaching library does not contain** (grep across all NextGen, Rocket, Powerplay, PMF, Spectrum and Singhania text, with PYQ compilations excluded):
- Absent: "Nedumba Vasati" (Q5), "Potnuru" victory pillar (Q24), "Jananathapura" (Q15), "Marichi Parinayam" (Q18), "Madanavilasabanam" (Q23), "Desamante" (Q52), "Abhinava Nannaya" (Q32), "Grandhalaya Sarvasvam" (Q40). — local grep over `/home/user/Group-app/data/notes2026/src/`
- Present in NextGen AP-history notes or Rocket Sheets: Denduluru (Q6), Pedaganjam (Q35), Moturpha (Q25), Arikesari and Sanigaram (Q21, Q22), Kumaraswamy Raja (Q42), Krishikar Lok Party (Q47), Mutyala Saralu, Pedanandipadu, Vignana Chandrika (Q39), Gatha Saptasati (Q2). These are **fact matches only**, with no wording matches. — local grep, as above

**2024 Prelims (Indian history, 30 P1 questions)**
- 20 of 30 questions have no hit of 2 or more 5-word sequences in any library file. The best matches are for famous standard facts. **Likely, not verbatim**:
  - Q23 Macaulay "single shelf of a good European Library..." quote: 13 matching sequences in PMF Modern History part 3. The quote itself is a stock text.
  - Q11 AITUC, first session presided by Lala Lajpat Rai: matches PMF Modern part 5 and Spectrum ("Congress (AITUC) founded in 1920. Lala Lajpat Rai was its...").
  - Q79 Dhar Commission (1948): topic matches Spectrum ("The Dhar Commission...").
  - Q21 Charter Act 1833 and Q27 Indian Society of Oriental Art: topic matches PMF and Spectrum.
  — local files `/home/user/Group-app/data/notes2026/src/indian-history/pmf-modern-history-03.txt`, `pmf-modern-history-05.txt`, `spectrum-modern-india.txt`
- Some 2024 facts are missing from every local text: "Lottery Committee" (1817, town planning, Q26), "Lex Loci" (Q30), "Tayuni/Taiyuni movement" (Q29). "Romaka Siddhanta" (Q5) appears only in PMF Ancient and Medieval; "Sohgaura" (Q17) is in PMF, Rocket and Singhania. The examiners therefore go beyond the coaching notes on modern-India minutiae. — local grep, as above
- Q30's correct option ("provided the right to inherit ancestral property to Hindu converts") matches the Wikipedia article on the Caste Disabilities Removal Act, 1850 ("allowed Hindus who converted ... equal rights ..., especially in the case of inheritance"). **Clear fact match.** — [Wikipedia: Caste Disabilities Removal Act, 1850](https://en.wikipedia.org/wiki/Caste_Disabilities_Removal_Act,_1850)

**2008, 2017 and 2019 Mains (AP history): circular matches to PYQ compilations**
- Paper 2 of 2008 (74 M1A questions), Paper 2 of 2017 Mains (75) and Paper 2 of 2019 Mains (75) match strongly, often 10 to 26 five-word sequences per question. The matches are in `ap-history-appsc-06/07.txt` (NextGen AP HISTORY Parts 6-7) and `powerplay1-ancient-11/12.txt` (AP History Powerplay). Inspection shows these are lists of past APPSC questions with answers. Examples:
  - 2008 P2 Q19: "P. Anandacharyulu was the first Andhra who became the President of the INC... -1891" (18 of 18 sequences).
  - 2008 P2 Q15: Aravamudu Iyengar committee.
  - 2017 Mains P2 Q1: "Identify the lake which is mentioned in the Pithapuram inscription of Prithvisvara of Velanadu - Kolleru lake".
  - 2019 Mains P2 Q27: "Women's property is inherited wholly by the daughters..." (16 of 16 sequences).
  — local files `/home/user/Group-app/data/notes2026/src/ap-history/ap-history-appsc-07.txt` (page 5) and `powerplay1-ancient-11.txt`
- With those compilations excluded, the only non-circular hits are fact matches in the NextGen notes, for example 2008 P2 Q39 (Nasik inscription of Gautami Balasri under Vasishtiputra Pulomavi, `ap-history-appsc-08.txt`), 2019 Mains P2 Q35 (Reddi-period sea-trade literary work) and 2019 Mains P2 Q13/Q48 (Mangalapura inscription; 17th-century diamond trader, `rocket-ap-history.txt`). — local, as above
- Paper 2 of 2019 Mains asks very fine-grained AP social-history details, such as the foundation cream used by Satavahana dancers (Q7), the Kolika guild (Q6), Kakatiya caste associations (Q24) and the most popular festival under the Reddis (Q37). Details at this level usually come from Telugu-medium AP social-history texts (Telugu Academy, B.S.L. Hanumantha Rao or P. Raghunadha Rao type). I could not verify any of them against those books because none is in the library or online in searchable form.

**2012, 2017 and 2019 Prelims (Indian history)**
- 2019 Prelims: 0 of 30 history questions have a match of 2 or more sequences in any library file. 2012 Paper 1: 1 of 32. 2008 Paper 1: 4 of 22, all generic (for example, Third Battle of Panipat lost to the Afghans). The best 2012 hit is Q14, Fa-Hien under Chandragupta II, a fact match in PMF Ancient. — local `matches2.json`

### Inferences
- **Examiners write their own text from a mix of sources.** The questions are not copied from coaching notes or from Spectrum or Singhania. Coaching material such as NextGen is useful mainly because it has absorbed the earlier PYQs.
- **The 2025 Mains setter drew on English Wikipedia.** At least four Paper I questions (Q10, Q13, Q17, Q34) use Wikipedia sentences, and the false options were made by swapping one fact (for example, *Gabbilam* for *Kreesthu Charitra*). This is the strongest source-to-question link I found. These are fact-level and phrase-level matches; I did not compare against a Telugu Academy edition.
- **The 2024 Prelims modern-India questions match the topics of Spectrum, PMF and Bipan Chandra, but not their wording.** Items such as the Lottery Committee, Lex Loci and the Taiyuni movement point to wider reading (Wikipedia, or Grover and Mehta style books).
- **Recurring themes repeat across years**, often with the same fact:
  - Battle of Padmanabham (2008 P2 Q68; 2025 Q37, Q63)
  - Vijayaditya II and the 108 temples (2008 P2 Q48; 2019 P2 Q16; 2025 Q12)
  - Veeresalingam, the first widow remarriage, and Vivekavardhini (2008, 2019, 2025)
  - Chirala-Perala and Duggirala (2019, 2025)
  - Machilipatnam English and Dutch factories (2008 Q32; 2017 Q36; 2025 Q31, Q62)
  - Andhra State formation dates, Gentlemen's Agreement and Sribagh Pact (every Mains year)
  
  So PYQ-derived material covers a large share of each new AP-history paper.

### Gaps
- I could not test the main suspected source for AP history, the Telugu Academy AP history and culture books (Telugu medium), or B.S.L. Hanumantha Rao, P. Raghunadha Rao, Sarojini Regani and Vakulabharanam. None is in the local library and none could be fetched as searchable text. Lifting from Telugu Academy is plausible, but this research did not confirm it.
- No Bipan Chandra, old NCERT, Tamil Nadu board or AP SCERT text is in the library (only the PW OnlyIAS NCERT compilation), so I could not test NCERT wording against the Indian-history questions.
- My matching used English stems only. Telugu-version wording, which may be the original drafting language, was not compared.
- The 5-gram method misses paraphrased lifts. Fact-level matching was done by hand only for a sample: all of the 2025 Mains and the 2024 Prelims questions, plus a few from other years.

## Are there patterns (e.g. AP history lifted from Telugu Academy, modern history from Spectrum/Bipan Chandra, recurring themes)?

### Takeaway
1. The AP-history papers recycle earlier PYQ facts heavily. That is why PYQ compilations "match" so well.
2. The 2025 Mains moved to statement, match-list and assertion-reason formats, built partly from English Wikipedia sentences.
3. Modern Indian history in the 2024 Prelims covers Spectrum and Bipan Chandra topics but not their wording.
4. The idea that AP history is lifted from Telugu Academy is widely assumed but untested here.

### Cited Findings
- Format shift: 2008, 2017 and 2019 AP-history questions were one-line factual recall ("The Communist Party was banned in Hyderabad State in -1946"). In 2025, 40 or more of the 75 Paper I questions are match-list, assertion-reason, statement or chronology items, with an explicit note on "Common codes for English and Telugu Versions". — local `/home/user/Group-app/data/g2papers/mains-2025-paper1.json`; [Sakshi analysis](https://education.sakshi.com/en/appsc/education-news/appsc-group-2-mains-2025-exam-analysis-expected-cutoff-scores-subject-wise-topics-172337)
- Wikipedia lifting in 2025 Q10, Q13, Q17, Q32 and Q34 (details above). — [Nannayya](https://en.wikipedia.org/wiki/Nannaya); [Gurram Jashuva](https://en.wikipedia.org/wiki/Gurram_Jashuva); [Eastern Chalukyas](https://en.wikipedia.org/wiki/Eastern_Chalukyas); [Thousand Pillar Temple](https://en.wikipedia.org/wiki/Thousand_Pillar_Temple); [Rayaprolu Subba Rao](https://en.wikipedia.org/wiki/Rayaprolu_Subba_Rao)
- Of the 461 history questions, about 30 non-circular items have 3 or more matching 5-word sequences in any coaching or standard-book text, and about 7 of those are match-list boilerplate. Spectrum is the best match for only a few items (2008 P2 Q19 jointly; 2024 Q79 Dhar Commission). — local `matches2.json`

### Inferences
- Priority by evidence:
  1. Past APPSC (and APPSC Group 1) PYQs, as captured in NextGen and Powerplay compilations: highest coverage.
  2. Telugu-medium AP social-history standard texts (Telugu Academy, B.S.L. Hanumantha Rao, P. Raghunadha Rao): assumed by every coaching list but unverified.
  3. English Wikipedia articles on AP dynasties, poets and monuments: verified for 2025.
  4. Spectrum, Bipan Chandra or PMF-level modern India for Prelims: topic-level matches.
  5. Nitin Singhania or PMF for art and culture (stupa parts, Mughal painting): topic-level matches.
- For Prelims Indian history, the 2024 paper looks UPSC-style (Rummindei one-eighth bali, Boghazkoi, Pautavadhyaksha, Sar-i-Naubat). That suggests the setters draw on standard UPSC-level texts (R.S. Sharma, Satish Chandra, Spectrum) and UPSC PYQs rather than Telugu Academy, but I found no wording evidence for this.

### Gaps
- I found no published coaching analysis that traces APPSC Group 2 history questions to specific books. Every claim that "questions came from book X" would need fresh matching against the Telugu Academy texts.
- I could not determine whether earlier papers (2017, 2019) also used Wikipedia, because their answer options are missing in the JSON ("ans" is empty for 2019 Mains Paper 2) and their stems are terse one-liners.
