# MCQ follow-up fixes (14 Nov 2026)

Input: review/mcq-followups.md and book{1..6}-fixes.md. `python3 tools/notes2026_jobs.py apply` was run, and every id below shows the new text or key in app/src/complete/assets/mcq*.json.

Where each edit went:
- own MCQs: edited in place in mcq<book>.json
- cp MCQs: edited in the new-mcqs.json of their run
- PYQs: one key line each in runs/b<book>-d02/keys_zfix.jsonl

**Tool note.** `apply` keeps the copy of a cp MCQ that is already in mcq<book>.json, so it does not re-read an edited new-mcqs.json. After the first apply the cp edits had not appeared. I copied s/o/a/x for the 7 cp ids from their new-mcqs.json into mcq<book>.json, then ran apply again. Both copies now match.

## Book 1
- **cp30c29bba1698** (b1-w098): options rebuilt as 1 only / 1 and 2 only / 1 and 3 only / 1, 2 and 3. Key changed from "1 and 3 only" to **"1 only"**. x now says statement 3 is wrong: Kashikhandam was dedicated to Veerabhadra Reddi (c. 1440), not Kataya Vema (d. 1414).
- **f0ed70bf56c4a**: x now says Kashikhandam was dedicated to Veerabhadra Reddi, not Kataya Vema. The key (Tippayya Setti) is unchanged.
- **nce17deda7ea**: stem changed from "founded Andhra Kesari" to "worked on the journal Andhra Kesari (Rajahmundry, 1904)". x changed to match.
- **n7527977b744**: x rewritten:
  - Mylapadu – Bezawada Gopala Reddy; Bellary – Kalluri Subbarao; Kakinada – Kasi Viswanadham (per the G2 2025 key).
  - Disputed chip added: NextGen gives Chollangi, while the G2 Mains 2025 key and CDI give Vadarevu.
  - The key (Chollangi – Bulusu) is unchanged.
- **n862d695454d**: Disputed chip added: Nur Jahan as Makhfi is from "some books"; the best-known Makhfi is Zeb-un-Nissa. x and xs reworded. The key is unchanged.
- **nap-history-17-17**: key changed from (b) to **(a)**. R reworded to "The communist leader Ravi Narayana Reddy was made president of that session", the means of the takeover (notes 255:6:6). x and xs rewritten.
- **y3823d23ed6b** (PYQ, b1-d02/keys_zfix): x now gives the range of estimates: 15 lakh (Famine Inquiry Commission) to 30 lakh (Sen), consensus about 21 lakh. The key (20 lakh) is unchanged.

## Book 2
- **ga8f5796c0f0a**: stem changed from "proposes" to "defeated in the Lok Sabha in April 2026, proposed … ceiling 550 → 850". x now gives 815 + 35, Arts 81/82/334A and the vote of 298–230. I dropped the unsourced ratio claim.
- **y6a6a538e801** (PYQ, b2-d02/keys_zfix): dispute line added: strictly, this is horizontal mobility (Rocket Indian Society p.23). x rewritten. The key is unchanged.

## Book 3
- **g647fa5028260**: option 3 changed from "Restructuring of the CBDT" to **"Review of service tax circulars"**, which is now the key. x now cites the CBEC review and the March 2007 report.
- **cpbe07dc9d4070** (b3-w059): x changed from "USSR agreement 1979" to "USSR-assisted".
- **y476e4314539 / y9adefa21c3e** (PYQ duplicates, b3-d02/keys_zfix): both are now keyed **1.6%**, the verified central-subsidy share (RBI Annual Report 2002-03, Economic Survey 2003-04). x for each carries "(official key: 7.0)", because no source supports 7.0.
  - y9adefa21c3e: key changed from 7.0 to the printed "16" option (1.6 with the decimal point lost). Its old dispute line is cleared.
- Not changed:
  - **f143f933dd952** and **f3f37367954a6** were removed by rewrite job b3-w048 and are not in the app.
  - **n64e26369dea** is only in unmerged.json (merged away) and is not in mcq3.json. The app's ₹500-note PYQ y9c41d0e6a43 already says about ₹3.

## Book 4
- **f1306036f422d**: stem changed from "median age of about 45" to "about 48". x now gives Japan 48.2, China/US 37–38 and India about 28, and says 45 is Western Europe.
- **g30e42aa06c40**: x changed from "Kolkata 10th" to "Kolkata 16th (WUP 2018)".
- **f7835e3598351**: stem now says "By total number of speakers (Ethnologue)", because the option "6th" is Bengali's native-speaker rank. x changed: Hindi is 3rd, and Bengali is 7th by total speakers (6th by native speakers).
- **yf3537c98634** (PYQ, b4-d02/keys_zfix): dispute line added: Apache is a Taiwanese group, called China- or Singapore-based in reports. x reworded. The key (Apache) is unchanged.
- Not changed:
  - **y6b2a4dee7c6**: the b4-d02 key line already has the outdated line (old answer 2nd, 974 km) and the app shows the chip.
  - **yba6d83ad8a1**: the Disputed chip is already present. The relink to the Zone III row is a mapping change, not a key line, so I did not make it.

## Book 5
- **cp7817231a040d** (b5-w034): statement 2 changed from "290 kg in a 500 km SSO" to "up to about 350 kg to low Earth orbit", which is still true. The key ("Only three") is unchanged and x is rewritten.
- **y415bd5dfd27** (PYQ, b5-d02/keys_zfix): key changed from "All three" to **"Only two"** (UPSC official key per GKToday and Vajiram). Dispute line added: PMF prints "All three". It now matches its twin y694adb32d4d, which is unchanged.
- **y2fc88e128db** (PYQ, b5-d02/keys_zfix): the key stays at 144 (printed key, not verified). Dispute line added: CAQM's 2021 year average is 209, which matches no option.

## Book 6
- **cac521e89e930c**: option 1 changed from "approximately 24%" to "approximately 22%" (21.76%, ISFR 2023). x, xs and n now give 21.76% and 25.17%. The key is unchanged.
- **cac63810760f64**: R changed to "Defence Secretary Rajesh Kumar Singh holds additional charge as Chairman of DRDO". x, xs and n reworded. The key (b) is unchanged.
- **nd7066b82109**: x and xa now name the SEEI 2024 group toppers, Maharashtra (Group 1) and AP (Group 2, 87.25).
- **cp5133ca881694** (b6-w068): match item changed from "BRICS – 10 members" to "11 members". x notes that the count is 10 if Saudi Arabia is left out.
- **cp348e5a202a33** (b6-w065): x changed from "UPI in 8 countries" to "8 till May 2026; 10–11 by Aug 2026, Uzbekistan from 1 Sep 2026".
- **gd5aa7937cc3f**: stem changed from "became the latest, in June 2026" to "began accepting UPI in June 2026". x now adds the Maldives (30 Jul) and Uzbekistan (1 Sep).
- **f0d6006be2fe8**: x date changed from 16–20 to **16–21 February 2026** (extended by a day).
- **cp311a25892c45** (b6-w107): x date changed from 19–20 to 16–21 February 2026.
- **cpe7e16fac598b** (b6-w096): x changed from "GSI (176 years)" to "175-year history (founded 1851)".
- **g144d0b918cc6**: x now dates the counts: 148/146/66 as of 1 April 2026, and 162/148 by July 2026.

## For the owner
- The notes lines these MCQs link to still carry the old figures, and I did not edit notes:
  - row 69 (6:69) "BRICS 10 members"
  - row 96 table "GSI (176 years)"
  - row 107 table "AI Impact Summit 19–20 Feb"
- Notes items in mcq-followups.md were not touched, because notes edits were out of scope: Agni-III row 5:48 and the Globe "January 1611" (row 1:157).
- The apply run also brought other done-job changes into the app that were made after the previous apply (for example y0ae69864b66, yc9f12b441db). As always, it copied PYQ keys to the other apps, including app/src/group2. I did not edit those files by hand.
