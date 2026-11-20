# RocketOne pilot (20 Nov 2026)

Group 1 Prelims notes written only from the NextGen Rocket Sheets and Rocket Current Affairs 2026, shown as lecture
slides in the APPSC Lectures app's format. Build: `python3 tools/rocketone_pilot.py`.

## Rules applied
1. Only what Rocket says. Where Rocket is silent nothing is added, from any source.
2. Only where a Rocket line disagrees (with another Rocket line, or with the verified fact) is it settled from other
   sources. The slide shows a green SETTLED box that first quotes what Rocket says, then the settled fact.
3. Arranged by the Group 1 Prelims syllabus line (data/g1syl/leaves.json), not by Rocket's sheet order.
4. A Rocket row is placed in a topic only when Rocket itself ties it to that topic (e.g. the row's Period column says
   "Satavahana"). Rows with no period (Roman coins at Bhattiprolu, Arikamedu, Ajanta Cave 10 painting, Kanheri) were
   not put under Satavahanas.
5. Every line keeps its Rocket sheet number in the notes file (`src`), not on the slide.

## Pilot lectures
| Lecture | Syllabus line | Rocket source read | Slides | Settled |
|---|---|---|---|---|
| docs/rocketone/pilot-1-satavahanas.pdf | A1/11 The Satavahanas | AP History Rocket Sheets (73 p.) + Indian History Rocket Sheets (262 p.): rows on 50 pages | 17 | 6 |
| docs/rocketone/pilot-2-space-in-news.pdf | E20/2, G/2, G/3 | Rocket Current Affairs 2026 Sheet #17 (p.116-125) | 19 | 0 |

## Disagreements settled (Satavahanas)
| # | Rocket says | Settled | Checked against |
|---|---|---|---|
| 1 | Last ruler: "Pulomavi III (as per Puranas)" (AP #2) vs "Pulumavi IV (last Satavahana king)" (AP #3) | Both kept: Puranas = Pulomavi III; Myakadoni inscription king = Pulumavi IV | List of Satavahana kings (Wikipedia); GKToday |
| 2 | "V.V. Sukthankar" located the Satavahanas in Bellary | V.S. Sukthankar | Indian Antiquary vol. 48 |
| 3 | Ushavadatta's 2,000 karshapanas listed inside Gautami Balasri's Nasik inscription (AP #3) vs a separate Nasik inscription (AP #30) | Two different Nasik cave inscriptions; AP #30 is right | Epigraphia Indica vol. 8 (from memory, not re-read online) |
| 4 | Kharavela a contemporary of Hala (AP #23) | Hathigumpha inscription names Satakarni, identified with Satakarni I | Satakarni (Wikipedia); Epigraphia Indica vol. 20 |
| 5 | Motupalli = "Western seaport" of the Satavahanas (AP #8, #30) | Motupalli is on the east coast (Bapatla district) | geography |
| 6 | Potin = "Copper + Silver + Lead" (Indian History #12) | Copper + tin + lead, no silver | Numista and numismatic glossaries |

Space lecture: no disagreement found. EOS-05 (4 Sep 2026, GSLV-F17, first imaging from geosynchronous orbit) and the
Pixxel EO-PPP agreement (21 Jan 2026, 12 satellites, ₹1,200 crore) were checked on the web and match Rocket. The MMX
launch date and the SOLAR-1 renaming were not checked.

## Not done in the pilot
- No APK: this container has no Android SDK. The slides are the same ones the Lectures app shows.
- No MCQs / quick-check slides (the Lectures app takes them from the Group 1 app's question bank, which is not Rocket).
- Rocket Current Affairs parts 3 and 4 (pages 420-435) are scanned images with almost no text; they need OCR.
- On Sheet #17 the satellite-tagged turtle (Kaziranga), Vanjeevi Didi and the ambassadors list belong to other topics.
