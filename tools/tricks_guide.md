# Memory tricks for each notes page

Students read a page and do its MCQs, then forget the facts a week later. For every page in your batch
(`work/tricks/in_NNN.md`, each `=== PAGE b:r:s | topic > page` followed by its notes) write the **1–3 tricks
that best help an APPSC / UPSC prelims student remember that page's exam facts**, and **1–2 recall questions**.
Not a summary and not rote repetition: each trick must give the mind a hook (a pattern, a picture, a link,
a contrast) for facts that are actually on the page.

## Pick the technique that fits the facts (type)

| type | use it for | example |
|---|---|---|
| `mnemonic` | a list or order to remember (members, sources, features, stages, states) | Regions of AP: **C-N-R** "Coastal, North (Uttarandhra), Rayalaseema" |
| `chunk` | many items: group them into 2–4 meaningful groups with a label | 12 Fundamental Duties → "3 for the Constitution, 4 for society, 3 for nature & culture, 2 for self" |
| `number` | dates, counts, percentages, Articles: tie the number to something known or to another number on the page | Art. 21A (education) = "21 + A for Alphabet"; 73rd/74th: "3 for villages (rural, earlier), 4 for towns" |
| `story` | several linked facts: a short vivid scene or image that holds them together | a picture of Warren Hastings sitting in the new Calcutta Supreme Court (1774) as the Regulating Act's first Governor-General |
| `contrast` | look-alike facts the exam mixes up (two Acts, two committees, two years, two rivers) | "BRGF = Backward Regions **Grant** Fund (Centre, defunct) vs AP Industrial Policy (State incentives)" |
| `chain` | causes and effects, processes, before → after | 1991 BoP crisis → IMF loan → LPG reforms → FDI goal in foreign policy |
| `timeline` | several dates: anchor them to one date the student already knows | "1969: Jai Andhra & Mulki rules row; 1973: Six-Point Formula — 4 years apart" |
| `place` | locations: tie them to a map route, a direction or a familiar place | "Rayalaseema's new hub runs Kadapa (JSW steel) → Tirupati (Royal Enfield) → Sriharikota (Space City)" |
| `trap` | the wrong option exams love; say what is true and what the trap is | "112 Aspirational Districts are monitored by NITI Aayog, not the Planning Commission (abolished 2015)" |

**The most important rule: a trick is a hook, not a restatement.** Listing the facts again is rote learning
and is not allowed. Every `text` must say *how* to hold the facts: the letters, the picture, the pattern,
the link to something the student already knows, or the contrast. Test each trick: delete the hook words —
if what remains is just the notes, rewrite it.

| bad (just the notes again) | good (a hook) |
|---|---|
| "Harappa - Ravi; Mohenjodaro - Indus; Ropar - Sutlej; Kalibangan - Ghaggar." | "Two R's go together: **H**a**r**appa on the **R**avi. **Mo**henjodaro sits on the **mo**ther river, the Indus. **Ro**par is where the Sutlej **ro**lls out of the hills. **Kali**bangan on the dried-up Ghaggar — 'black bangles in a dry river'." |
| "Bhimbetka was found in 1957 by V.S. Wakankar and listed by UNESCO in 2003." | "**B**himbetka, near **B**hopal: 'Wakankar's W in '57, World Heritage in '03' — the same W twice, and 57 → 03 is 46 years of waiting." |
| "The 73rd Amendment is for Panchayats and the 74th for Municipalities." | "Villages come before towns, and 3 before 4: **73 = villages (Panchayats), 74 = towns (Municipalities)**." |

Rules:
- **Only facts on this page.** Numbers, names, years, Articles must match the page exactly. Never add a
  fact that is not there. A trick that teaches a wrong fact is worse than none.
- Choose by the page: a list page wants a mnemonic or chunk; a date-heavy page a timeline or number hook; a
  page with confusable pairs a contrast or trap. Do not force a mnemonic where it does not fit.
- `title`: what the trick is for, in a few words ("Three regions of AP", "BRGF vs AP Industrial Policy").
- `text`: the trick itself, 1–3 short sentences, plain English, easy to say aloud. Never mention "the notes", "older notes" or "sources"; where sources differ, give the right fact and the trap.
- Use a variety of techniques across the batch, chosen by the page; a `place` or `number` trick still needs a hook (direction, route, pattern, link), not a list.
- `mnemonic` also needs `cue` (the memory word or phrase) and `items` (the things its letters stand for,
  in order). Each letter of the cue (letters only, case ignored) must be the first letter of the matching
  item: cue "CNR", items ["Coastal Andhra", "North Andhra", "Rayalaseema"]. A pronounceable or funny cue
  is better ("RAVI": Ravi, ...). The checker rejects a cue whose letters do not match the items' initials.
- `recall`: 1–2 questions to ask yourself with the page closed, on its most exam-likely facts, each with a
  short answer: {"q": "Which three regions …?", "a": "Coastal Andhra, North Andhra, Rayalaseema"}.
- A very short page (one or two facts) gets 1 trick and 1 recall question; a rich page up to 3 and 2.
- Pages that only point elsewhere or have no real facts still need 1 trick + 1 recall about whatever they say.

## Output: `work/tricks/out_NNN.jsonl`
One line per page, in input order:
```
{"page":"2:118:0","tricks":[{"type":"mnemonic","title":"Regions of AP","text":"Think 'CNR' — Coastal, North, Rayalaseema: the three zones that every regional-imbalance question starts from.","cue":"CNR","items":["Coastal Andhra","North Andhra","Rayalaseema"]},{"type":"trap","title":"Uttarandhra","text":"Uttarandhra means North Andhra, a region of AP, not a part of Telangana."}],"recall":[{"q":"Name the three regions of Andhra Pradesh.","a":"Coastal Andhra, North Andhra (Uttarandhra), Rayalaseema"}]}
```
Last line: `{"done":N}` with N = the number of pages in the batch. Check with
`python3 tools/tricks.py check NNN` until it passes. Write only that output file (scratch scripts go in your
own folder under the scratchpad).
