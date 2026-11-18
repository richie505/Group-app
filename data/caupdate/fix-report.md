# Current Affairs fact-fix report (18 Nov 2026)

Files written: `data/caangle/fixes.jsonl` (14 one-liner fixes), `data/caupdate/notefix.json` (9 notes edits for APPSC Complete book 6). The notes edits passed the dry run (`NOTES_APP=complete python3 tools/notes_fix.py apply data/caupdate/notefix.json --dry`: 9/9 ok). They have not been applied.

## 1. 6:68 Maritime trade share (by value vs by volume)
- **What was wrong:** One-liner `od456236f7d8` asked what share of trade by value goes by sea and gave 95% as the answer. The explanation of `o0238607d0fe` said "Maritime trade ~95% by value". The notes (Complete 6:32) were already right.
- **Right fact:** About 95% of India's trade by volume and about 70% by value moves by sea.
- **Source:** PIB, "Maritime India: From Vision 2030 to Amrit Kaal 2047" (26 Oct 2025): https://static.pib.gov.in/WriteReadData/specificdocs/documents/2025/oct/doc20251026676201.pdf
- **Changed:**
  - `od456236f7d8`: the answer is now 70%. The question was lightly reworded to "share of India's trade by value is carried by sea".
  - `o0238607d0fe`: corrected the explanation.
  - Notes: no change.

## 2. 6:3 NDB founding year (2014 vs 2015)
- **What was wrong:** `of6977cec7e1` asked "In which year was the NDB established?". Both 2014 and 2015 are among its options, the key was 2015, and other items say 2014, so the question was ambiguous. `o5b083ca17fb` paired "established 2014" with Shanghai, but the agreement was signed in Fortaleza.
- **Right fact:** The NDB agreement was signed at the 6th BRICS Summit in Fortaleza in July 2014. The first Board of Governors met on 7 July 2015, and the bank opened in Shanghai in 2015. NDB's own history page says it became fully operational in 2016.
- **Source:** https://www.ndb.int/about-ndb/history/
- **Changed:**
  - `of6977cec7e1`: the question is now "agreement ... signed", with answer 2014.
  - `o5b083ca17fb`: the question is now "agreement signed, and where headquartered" (2014, Shanghai).
  - Notes: no change. They already say "agreement 2014, operational 2015".

## 3. 6:4 AI Impact Summit dates
- **What was wrong:**
  - One-liner `o8f4ac191e92` gave 19–20 Feb, which is only the leaders' segment.
  - The notes (Complete 6:55 sub 3, and 6:107 sub 8) said 16–21 Feb.
- **Right fact:**
  - The India AI Impact Summit ran 16–20 February 2026 at Bharat Mandapam.
  - PM Modi inaugurated the leaders' segment on 19 Feb.
  - The Expo was extended by a day to 21 Feb, and the New Delhi Declaration was adopted on 21 Feb.
- **Source:** PIB feature, 20 Feb 2026: https://static.pib.gov.in/WriteReadData/specificdocs/documents/2026/feb/doc2026220797301.pdf (also https://www.newsonair.gov.in/india-ai-impact-summit-2026-adopts-new-delhi-declaration)
- **Changed:**
  - One-liner `o8f4ac191e92`: the answer option is now "16–20 February".
  - Notes 6:55 sub 3: the dates now read 16–20 February 2026, and I added a bullet on the leaders' segment, the Expo extension and the 21 Feb declaration.
  - Notes 6:107 sub 8: corrected the table cell.

## 4. 6:15 India–Italy ties
- **What was wrong:** `o9d017fccf95` gave the answer "Strategic Partnership Plus". The notes were already right.
- **Right fact:** Ties were elevated to a **Special Strategic Partnership** during PM Modi's visit to Italy on 19–20 May 2026.
- **Source:** India–Italy Joint Declaration, 20 May 2026: https://ambnewdelhi.esteri.it/wp-content/uploads/2026/05/Italy-India_JointDeclaration_20260520.pdf (also https://www.pmindia.gov.in/en/news_updates/india-italy-joint-declaration/)
- **Changed:**
  - `o9d017fccf95`: the answer option is now "Special Strategic Partnership".
  - Notes: no change.

## 5. 6:12 IMF FY27 projection for India
- **What was wrong:** `o55410c8421d` said the April 2026 IMF projection for FY27 was 6.2%, and the explanation of `o79839c792dc` repeated it. 6.2% was the October 2025 WEO figure.
- **Right fact:** The April 2026 WEO projected 6.5% for FY27, up from 6.4% in January 2026.
- **Source:** https://www.freepressjournal.in/business/imf-raises-indias-growth-forecast-to-65-in-fy27-after-eased-tariffs-despite-war (the IMF WEO April 2026 report)
- **Changed:**
  - `o55410c8421d`: the answer is now 6.5%. It replaces the 6.6% option.
  - `o79839c792dc`: corrected the explanation.
  - Notes: no change. 6:60 says 6.5%, and the 6.2% mentions are labelled October 2025.

## 6. 6:20 FGFA exit year
- **What was wrong:** `ob4d3d4ea176` gave 2021 as the answer. Its source was a magazine that got it wrong.
- **Right fact:** India joined the FGFA programme in 2007 and left in 2018 (reported 20 April 2018).
- **Sources:** https://thediplomat.com/2018/04/india-pulls-out-of and https://en.wikipedia.org/wiki/Sukhoi/HAL_FGFA
- **Changed:**
  - `ob4d3d4ea176`: the answer is now 2018.
  - Notes 6:71 sub 9: removed the in-text "Praveen says 2021 – go with 2018" remark, so the bullet just states 2018.

## 7. NITI Aayog CEO (6:30 vs 6:39), plus the Vice-Chairperson
- **Right fact:**
  - B.V.R. Subrahmanyam's term ended in Feb 2026.
  - Nidhi Chhibber then held additional (interim) charge.
  - **Anurag Jain** (1989 IAS, MP cadre) took charge as CEO on **17 Aug 2026**.
  - Separately, **Ashok Kumar Lahiri** became Vice-Chairperson in April 2026 (took charge May 2026), replacing Suman Bery.
- **Sources:** https://www.niti.gov.in/about-us/whos-who/leadership/ceo-niti-aayog and https://newsonair.gov.in/economist-ashok-lahiri-appointed-as-vice-chairperson-of-niti-aayog/
- **What was wrong:**
  - The 6:39 notes (Complete 6:93) listed Chhibber simply as "CEO". The 6:30 notes (Anurag Jain) were right.
  - 6:50 notes (Complete 6:105): "CEO Nidhi Chhibber" with no update.
  - 6:102 notes (Complete 6:11) and Complete 6:115: VC "Suman Bery", which is outdated.
  - One-liner `ob0c8d5f81b8` (6:50): CEO given as Chhibber.
  - One-liners `o49016af59b9` (6:82) and `o3e0352cbf6a` (6:102): VC given as Suman Bery.
  - One-liner `o5add26a1940`: the explanation names Bery as VC.
- **Changed:**
  - One-liners:
    - `ob0c8d5f81b8`: the answer is now Anurag Jain.
    - `o49016af59b9` and `o3e0352cbf6a`: the answer is now Ashok Kumar Lahiri.
    - `o5add26a1940`: corrected the explanation.
  - Notes:
    - 6:93 sub 7: the entry now reads "Additional charge as CEO ... regular CEO Anurag Jain from 17 Aug 2026".
    - 6:105 sub 4: added "(additional charge; Anurag Jain CEO from 17 Aug 2026)".
    - 6:11 sub 5: the VC is now Lahiri (earlier Bery).
    - 6:115 sub 0: the VC is now Lahiri, with "succeeded Suman Bery".

## 8. 6:1 18th BRICS Summit dates
- **What was wrong:** The explanation of `o9ddf15acbeb` said "September 17–19, 2026". The notes were already right.
- **Right fact:** The summit was held 12–13 September 2026 at Bharat Mandapam, New Delhi.
- **Source:** https://newsonair.gov.in/brics-summit-under-indias-presidency-begins-in-new-delhi/ (MEA announcement via IANS: https://ianslive.in/india-to-host-18th-brics-summit-in-delhi-on-september-12-13--20260827113836)
- **Changed:**
  - `o9ddf15acbeb`: corrected the explanation. The question and answer (BRICS) are unchanged.
  - Notes: no change. 6:52 and 6:53 already say 12–13 Sep.

## Seen but not changed (for the owner)
- **`ca25c68aa7e951` (mcq6 row 4):** This is not a one-liner. Its question is "Where is the NDB headquartered?" and its key is option 3, "Farakka". It should be option 1, "Shanghai".
- **`oe3399eebd98` (6:6):** It says 92 countries and organisations adopted the AI Impact declaration. Reports at the close (21 Feb 2026) gave 88; later counts vary.
- **NDB membership year:** Its history page lists Uzbekistan and Colombia as admitted in 2025. The app says Uzbekistan joined on 5 June 2026; that may be the date its membership took effect.
- **`o22283fcde02` (6:0):** "Suman Berry" is misspelt (should be Bery). I did not verify the quote it uses.
