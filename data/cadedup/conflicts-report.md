# Conflict check against the web (18 Nov 2026)

Note edits: `data/cadedup/conflictfix.json` (31 edits; the dry run passes 31/31; **not applied**).
One-liner fixes: 37 lines appended to `data/caangle/fixes.jsonl` (none of the ids were already in the file).
"Notes" refers to the APPSC Complete books (`app/src/complete/assets/bookN.json`), given as book:row.sec[block].

## 1. EAGLE HQ (AP): Mangalagiri vs Vijayawada. Settled: **Mangalagiri**
- The anti-drug website launch in June 2026 and the Red Cross MoU in August 2026 both took place "at EAGLE headquarters in Mangalagiri". The ANI report of April 2026 ("new HQ in Vijayawada") is datelined Vijayawada.
  - https://www.deccanchronicle.com/southern-states/andhra-pradesh/eagle-launches-anti-drug-website-honours-56-personnel-1966507
  - https://www.deccanchronicle.com/southern-states/andhra-pradesh/andhra-pradesh-eagle-red-cross-join-hands-to-fight-drug-abuse-1983041
- Notes: 6:1.2[1] drops "(some sources: Vijayawada)".
- One-liners: od8fef78d6a6 now answers Mangalagiri.
- Not fixable through fixes.jsonl: the `xa` text of n8f600245422 still says "EAGLE … HQ Vijayawada".

## 2. India FDI 2025: USD 38.89 bn vs USD 47 bn. Settled: **USD 38.89 bn (+44%), 11th**
- USD 38.89 bn is the final figure in UNCTAD's World Investment Report 2026 (7 July 2026). USD 47 bn (+73%) was the preliminary estimate in the January 2026 Global Investment Trends Monitor.
  - https://unctad.org/system/files/press-material/pr26007_wir26_asia_en.pdf
  - https://www.dailyexcelsior.com/fdi-inflows-to-india-increased-by-44-per-cent-to-usd-39-billion-in-2025-un/
- Notes: 6:35.9[0] and 6:63.10[1] now give 38.89 bn, with the January estimate noted as preliminary.
  - Left as is: the "global FDI +14%, China −8%" figures in 6:35.9[0], which come from the January Monitor.
- One-liners: oN316a351121, n703ca5108a3, n8fe7e5fe030, oNab00c8ce88.

## 3. 11th UPI country: Uzbekistan vs Maldives. Settled: **Uzbekistan**
- The 10 countries before it were Singapore, UAE, France, Mauritius, Nepal, Bhutan, Qatar, Sri Lanka, Cambodia and Greece. Uzbekistan's UPI–UZQR link (NIPL with NIPC) went live on 31 Aug / 1 Sep 2026.
- The Maldives Favara–UPI link (30 July 2026) is a person-to-person remittance corridor into India. It is not UPI acceptance, and the Ministry of Finance does not count it.
  - https://curlytales.com/india/trending/after-visa-free-entry-for-indians-uzbekistan-to-accept-upi-becomes-country-to-embrace-platform/
  - https://ianslive.in/indians-can-now-make-upi-payments-in-uzbekistan--20260831170903
  - https://newsonair.gov.in/favara-upi-cross-border-payment-corridor-goes-live-between-maldives-and-india/
- Notes: the 6:65.10[0] table cell is rewritten.
- One-liners: oNbd72921ba4, oa647872bde2, oNf6b0102e3f (the Favara date was wrongly "August"; it is 30 July 2026).

## 4. GST April 2026: Rs 2.42 vs 2.43 lakh crore. Settled: **Rs 2,42,702 crore ≈ Rs 2.43 lakh crore** (+8.7%)
- Both figures are roundings of Rs 2,42,702 crore. Rs 2.43 lakh crore is used as the standard figure.
  - https://www.businesstoday.in/latest/story/gst-collections-hit-record-high-in-april-rise-87-to-rs243-lakh-crore-528403-2026-05-01
  - https://newsonair.gov.in/gst-collections-hit-all-time-high-of-over-%E2%82%B92-42-lakh-crore-in-april/
- Notes: 6:34.7[0].
- One-liners: oa01b61f3cfb.

## 5. DAY-NRLM launch and rename dates. Settled: **launched June 2011** (restructured SGSY; approved 2010), **renamed DAY-NRLM in November 2015**
- Sources:
  - New India Samachar, a PIB publication: "launched … in June 2011 … In 2015, it was renamed". https://newindiasamachar.pib.gov.in/WriteReadData/flipbook/2022/Nov/2nd/English/files/basic-html/page20.html
  - Government district page: "In November 2015, the program was renamed". https://dhalai.nic.in/scheme/nrlm/
- The 2016 and 29-Mar-2016 dates appear only in secondary sources.
- Notes:
  - 6:42.2[5]: "2010" becomes "June 2011" and "2016" becomes "November 2015".
  - 6:33.6[5]: "NRLM 2010" becomes "NRLM June 2011".
  - Also fixed in books 2–3: 2:123.2[0], 2:166.2[1], 3:37.0[8].
  - 6:40.5[15] and 6:19.8[18] were already right.
- One-liners: o3021e4f9821, o44e6cfb25d4, o92218428373, o3db73435280, o9540967597c, ned8f737cc5d, nc0bb05f41d6, ca471f730e55b4 (a junk distractor in this last one is also replaced).

## 6. UPI merchant fee (MDR) start date. Settled: **was due 15 Oct 2026; deferred**
- On 13 Oct 2026 NPCI deferred the MDR until after Diwali. The new date is "to be notified separately", and none had been notified by 18 Nov 2026.
  - https://www.deccanherald.com/india/mdr-on-upi-deferred-until-after-diwali-npci-4181482
  - https://www.theweek.in/news/biz-tech/2026/10/13/npci-defers-upi-mdr-until-after-diwali.html
- Notes: 6:32.3[0] heading and 6:32.3[1].
- One-liners: o09520c4da7e, o8003ec18226, oa2b92b1f9a5, of55ec44aa8a (only the x changes).

## 7. FIDE President: Anand (interim) vs Dvorkovich. Settled: **Timur Turlov**
- Turlov was elected President at the FIDE General Assembly in Samarkand (26–27 Sep 2026), with Anand as Deputy President.
- Anand had been Interim President since July 2026, after Dvorkovich stepped aside.
  - https://www.fide.com/?p=50456
  - https://en.chessbase.com/post/decisions-fide-general-assembly-2026
- Notes: 6:97.3[10], 6:99.2[8], 6:99.8[11].
- One-liners:
  - o4661a9f2a76: only x changes.
  - ca8f5fd11897f2: the question is unchanged and x adds the September election.

## 8. National e-Governance Gold Award 2026: ICMR-mINDS vs Panchayat Advancement Index. Settled: **both won Gold**
- Panchayat Advancement Index won in Category VII (data analytics). ICMR-mINDS won in the AI / new-age technology category.
  - https://www.iasgyan.in/daily-current-affairs/panchayat-advancement-index-pai-wins-gold-award-at-national-e-governance-awards-2026
  - https://www.dailypioneer.com/news/icmr-minds-wins-gold-at-national-awards-for-egovernance
- Notes: 6:96.3[16] now names both.
- One-liners: none needed (ca3b6807bea28c is correct).

## 9. No Khel Ratna for 2025: "third such case since 1991" vs "first since 2014". Settled: **both are true**
- No award was given for 2008 or 2014, so 2025 is the third such year and the first since 2014.
  - https://en.wikipedia.org/wiki/Major_Dhyan_Chand_Khel_Ratna (2008 and 2014 listed as "No award")
  - https://theprint.in/sport/no-khel-ratna-for-2025-tejaswin-divya-and-gayatri-gopichand-among-arjuna-awardees/3018100/ ("last time … 2014")
- Notes: 6:96.5[4] and 6:98.9[2] now say "after 2008 and 2014".
- One-liners: n85c176d5f5c (only x changes).

## 10. NTCA founding year: 2005 vs 2006. Settled: **2006**
- NTCA was constituted under Section 38L of the Wildlife (Protection) Act, 1972 "as amended in 2006". 2005 is the year of the Tiger Task Force.
  - https://ntca.gov.in/about-us/
- Notes: 6:79.2[9].
- One-liners: o04da710c8fb (the 2005 option is now 2006), o4916307c710 (answer now 2006).

## 11. India's SDR rank 112th: 2015 vs 2023. Settled: **both are true, in different senses**
- India ranked 112th of 166 in the SDR 2023 edition.
- SDR 2026 back-casts India's 2015 baseline to 112th ("up 18 places from 112th in 2015 to 94th").
  - https://www.drishtiias.com/daily-updates/daily-news-analysis/un-sustainable-development-report-2026/print_manually
- Notes: 5:81.6[4] now states both senses.
- One-liners: o85eb41ed133 is reworded. It asked about a "Sustainable Development Report 2015", which does not exist, and its x was garbled.

## 12. Lowest TFR state: Sikkim (1.0) vs Delhi (1.2). Settled: **Delhi, 1.2** (SRS 2024)
- I found no source for Sikkim at 1.0. The SRS report gives TFR only for the bigger States/UTs.
  - https://www.theweek.in/news/india/2026/06/07/tfr-drops-below-replacement-level-which-states-have-the-highest-and-lowest-fertility-rates-and-why-are-they-falling.html
- Notes: the 6:83.3[18] table row drops Sikkim.
- One-liners: od6f1ca96cbd (answer now Delhi).

## 13. Ramayapatnam port district: Prakasam vs SPSR Nellore. Settled: **Prakasam**
- The port is in Gudluru mandal of the Kandukur division. That division moved to SPSR Nellore in 2022 and returned to Prakasam on 31 Dec 2025.
  - https://en.wikipedia.org/wiki/Kandukur_revenue_division
  - https://www.deccanchronicle.com/southern-states/andhra-pradesh/prakasam-district-expanded-to-28-mandals-after-reorganisation-1927251
  - https://www.constructionworld.in/transport-infrastructure/ports-and-shipping/ramayapatnam-port-nears-phase-i-launch-in-2026/83131 (Gudluru mandal, Prakasam)
- Notes: 6:13.2[5], 4:95.6[0], 3:69.5[1], 3:117.2[0].
  - Left as is: 3:125.0[16] ("BPCL … Ramayapatnam, Nellore") and 3:141.3[2].
- One-liners: occ82c50f042, od2d9966e158, n1ac5f73cd40, o638f88df439, o0341055bfb7, oc7302462bcd.

## 14. Kakinada green ammonia capacity: 1.1 vs 1.5 MTPA. **NOT SETTLED, left as is**
- ADB's 15 Oct 2026 release says "about 1.1 million tons per year": https://www.adb.org/news/adb-japan-back-one-world-largest-green-ammonia-plants-first-accel-investment
- Reports of the January 2026 foundation stone (state and company) give a final capacity of 1.5 MTPA, ramping from 0.5 MTPA: https://www.deccanchronicle.com/southern-states/andhra-pradesh/naidu-pawan-lay-foundation-stone-for-mega-green-ammonia-project-in-kakinada-1930918
- Neither source reconciles the two figures. Some one-liners (obda0b9b0e17, o45da028325b) also say "1 MTPA".
- No changes made.

## 15. AP highway lane-km record: 28.89 lane-km vs 28.95 km. Settled: **28.89 lane-km and 10,655 t in 24 hours** (NH-544G, near Puttaparthi, 6 Jan 2026)
- This is the NHAI / PIB figure. The 28.95 km and 7,500 t figures come from the contractor's later press note.
  - https://newindiasamachar.pib.gov.in/WriteReadData/flipbook/2026/Feb/1st/English/files/basic-html/page7.html
  - https://www.thestatesman.com/india/nhai-creates-4-guinness-world-records-in-andhra-pradesh-1503538974.html
- Notes: 6:13.12[0].
- One-liners: oe54bdd49d79, oNcb52b66a21.

## 16. Ugadi 2026 awards count: 122 vs 123. **NOT SETTLED, left as is**
- Two outlets report 38 Kala Ratna and 122 Ugadi awards.
- Deccan Chronicle reports 123 Ugadi awards, 161 in total: https://www.deccanchronicle.com/southern-states/andhra-pradesh/cm-naidu-presents-161-ugadi-awards-for-contributions-in-diverse-fields-1945026
- I found no official G.O. or I&PR list.
- The notes already say "123 in some reports". No changes made.

## 17. Visakhapatnam per capita income / GDDP. Settled: **PCI Rs 6,58,964; GDDP Rs 1,61,009 crore** (2025-26 advance estimates)
- Sources:
  - https://www.deccanchronicle.com/southern-states/andhra-pradesh/per-capita-income-rayalaseema-districts-lag-behind-visakhapatnam-records-highest-earnings-1948928 (PCI Rs 6,58,964)
  - https://assets.thehansindia.com/andhra-pradesh/states-economy-triples-in-a-decade-1055755 (GDDP ₹1.61 lakh crore)
- I found no source for Rs 6,58,091 / Rs 1,60,771 crore.
- Notes: 6:8.1[4] drops the "Feb 2026 release" sentence and states the settled figures.
  - Still inconsistent: Parvathipuram Manyam's PCI is ₹1,56,977 in this block but ₹1,56,875 in 6:8.1[3]. I did not check it.
- One-liners: none needed.
