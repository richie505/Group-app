"""Explanation video for one lecture (HyperFrames): the topic's Rocket-style slides, revealed row by row as a narrator
explains them, with captions. Narration script: data/lecvideo/<group>/<book>-<row>.json ({"intro": [...],
"parts": {"<page>": [{"b": block, "r": row|null, "say": "..."}]}, "outro": [...]}); slides:
data/lecrocket/<group>/<book>-<row>.json. Voice: Piper (offline TTS).

    python3 tools/lecture_video.py group2 1 37 <work dir> [voice.onnx]   -> <work dir>/index.html + narration.wav
    then in <work dir>: npx hyperframes render -o video.mp4
"""
import html, json, os, re, subprocess, sys, wave

G, B, R, OUT = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
VOICE = sys.argv[5] if len(sys.argv) > 5 else os.environ.get("PIPER_VOICE", "")
TE_VOICE = os.environ.get("PIPER_TE_VOICE", "")  # Telugu voice: each beat is explained in English, then in Telugu
SCRIPT = os.environ.get("LECTURE_SCRIPT", "")  # a narration file other than data/lecvideo/<group>/<book>-<row>.json
TE_FONT = os.environ.get("TE_FONT", "")  # Telugu font file (woff2 / ttf), embedded in the project
GAP = 0.45  # silence after each beat (s)
A = f"app/src/{G}/assets"
APP = {"group1": "APPSC Group 1 Prelims", "group2": "APPSC Group 2"}[G]

script = json.load(open(SCRIPT or f"data/lecvideo/{G}/{B}-{R}.json"))
slides = json.load(open(f"data/lecrocket/{G}/{B}-{R}.json"))
bk = json.load(open(f"{A}/book{B}.json"))
row = [r for u in bk["units"] for r in u["rows"]][R]
subject = json.load(open(f"{A}/index.json"))["books"][B - 1].get("short", "")
os.makedirs(f"{OUT}/audio", exist_ok=True)


def md(t):
    t = html.escape(str(t))
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)


# ---- voice: one clip per line, then one narration track ----------------------------------------------------------
lines = []  # (key, text, lang); a beat's Telugu explanation follows its English line, keyed "<key>t"


ONLY_TE = os.environ.get("NARRATION") == "te"  # Telugu narration only, over the English slides


def add(key, item):
    en, te = (item.get("en") or item.get("say"), item.get("te")) if isinstance(item, dict) else (item, None)
    if ONLY_TE:
        lines.append((key, te or en, "te" if te else "en"))
        return
    lines.append((key, en, "en"))
    if te and TE_VOICE:
        lines.append((key + "t", te, "te"))


for i, t in enumerate(script["intro"]):
    add(f"i{i}", t)
for j in sorted(script["parts"], key=int):
    for k, beat in enumerate(script["parts"][j]):
        add(f"p{j}-{k}", beat)
for i, t in enumerate(script["outro"]):
    add(f"o{i}", t)

times, t0 = {}, 1.0
rate = None
for key, text, lang in lines:
    f = f"{OUT}/audio/{key}.wav"
    if not os.path.exists(f):
        subprocess.run(["piper", "-m", (TE_VOICE or VOICE) if lang == "te" else VOICE, "-f", f, "--sentence-silence", "0.25"], input=text.encode(), check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    with wave.open(f) as w:
        d = w.getnframes() / w.getframerate()
        rate = w.getframerate()
    times[key] = (t0, d)
    t0 += d + GAP
TOTAL = round(t0 + 1.5, 2)
# narration.wav: each clip at its start time
with wave.open(f"{OUT}/narration.wav", "wb") as out:
    out.setnchannels(1)
    out.setsampwidth(2)
    out.setframerate(rate)
    pos = 0
    for key, _, _ in lines:
        st, d = times[key]
        n = int(st * rate)
        out.writeframes(b"\0\0" * (n - pos))
        with wave.open(f"{OUT}/audio/{key}.wav") as w:
            fr = w.readframes(w.getnframes())
        out.writeframes(fr)
        pos = n + len(fr) // 2
    out.writeframes(b"\0\0" * (int(TOTAL * rate) - pos))

# ---- screens -----------------------------------------------------------------------------------------------------
parts = sorted(script["parts"], key=int)
NP = len(parts)
screens = []  # dict(start, end, html, beats=[(key, el_id)])


def block_html(pid, bi, b):
    if b["k"] == "h":
        return f"<div class='sub' id='{pid}-{bi}'>{md(b['x'])}</div>"
    if b["k"] == "t":
        hh = "".join(f"<th>{md(c)}</th>" for c in b["h"])
        rr = "".join(f"<tr id='{pid}-{bi}-{ri}' class='rv'>" + "".join(f"<td>{md(c)}</td>" for c in r) + "</tr>"
                     for ri, r in enumerate(b["r"]))
        return f"<table id='{pid}-{bi}'><tr>{hh}</tr>{rr}</table>"
    if b["k"] == "x":
        return f"<div class='box rv' id='{pid}-{bi}'><span>REMEMBER</span>{md(b['x'])}</div>"
    return f"<div class='pt rv' id='{pid}-{bi}'>{md(b['x'])}</div>"


# intro
def last(k):  # the beat's last line: its Telugu explanation, if any
    return k + "t" if k + "t" in times else k


ik = [f"i{i}" for i in range(len(script["intro"]))]
plan = "".join(f"<li><span class='n'>{n + 1}</span>{md(row['secs'][int(j)]['t'])}</li>" for n, j in enumerate(parts))
screens.append(dict(start=0, end=times[last(ik[-1])][0] + times[last(ik[-1])][1] + GAP, cls="title",
                    html=f"<div class='kicker'>{md(APP)} · {md(subject)}</div><h1>{md(row['title'])}</h1><ol class='plan'>{plan}</ol>",
                    beats=[(k, None) for k in ik]))
for n, j in enumerate(parts):
    blocks = slides[j]
    beats = script["parts"][j]
    # split the page into screens at each heading; each screen shows its blocks, revealed as they are explained
    groups, cur = [], []
    for bi, b in enumerate(blocks):
        if b["k"] == "h" and cur:
            groups.append(cur)
            cur = []
        cur.append(bi)
    if cur:
        groups.append(cur)
    for g in groups:
        bs = [(k, bt) for k, bt in enumerate(beats) if bt["b"] in g]
        if not bs:
            continue
        pid = f"s{n}-{g[0]}"
        body = "".join(block_html(f"p{j}", bi, blocks[bi]) for bi in g)
        keys = [(f"p{j}-{k}", f"p{j}-{bt['b']}" + (f"-{bt['r']}" if bt["r"] is not None else "")) for k, bt in bs]
        st = times[keys[0][0]][0] - 0.3
        en = times[last(keys[-1][0])][0] + times[last(keys[-1][0])][1] + GAP
        screens.append(dict(start=st, end=en, cls="content", part=f"Part {n + 1} of {NP}",
                            ptitle=row["secs"][int(j)]["t"], html=body, beats=keys))
ok = [f"o{i}" for i in range(len(script["outro"]))]
screens.append(dict(start=times[ok[0]][0] - 0.3, end=TOTAL, cls="title end",
                    html=f"<div class='kicker'>Recap · {md(row['title'].split(' – ')[0])}</div><ul class='recap'>"
                         + "".join(f"<li>{md(x)}</li>" for x in (script.get("recap") or re.split(r"(?<=\.)\s+", lines[[k for k, *_ in lines].index("o0")][1])[1:] or [lines[[k for k, *_ in lines].index("o0")][1]]))
                         + f"</ul><div class='cta'>Practise this topic's MCQs in {md(APP)}</div>", beats=[(k, None) for k in ok]))
# close the gaps between screens: each lasts until the next starts
for a, b in zip(screens, screens[1:]):
    a["end"] = b["start"]

# ---- composition ---------------------------------------------------------------------------------------------------
clips, caps, tl = [], [], []
for si, s in enumerate(screens):
    st, du = round(s["start"], 3), round(s["end"] - s["start"], 3)
    bar = f"<div class='bar'><span class='p'>{md(s.get('part', ''))}</span><span class='t'>{md(s.get('ptitle', ''))}</span></div>" if s["cls"] == "content" else ""
    clips.append(f"<section id='sc{si}' class='clip scr {s['cls']}' data-start='{st}' data-duration='{du}' data-track-index='1'>"
                 f"{bar}<div class='inner'><div class='flow'>{s['html']}</div></div></section>")
    tl.append({"sc": f"sc{si}", "st": st, "beats": [{"t": round(times[k][0], 3), "el": el} for k, el in s["beats"]]})
for key, text, lang in lines:
    st, d = times[key]
    caps.append(f"<div class='clip cap{' te' if lang == 'te' else ''}' data-start='{round(st, 3)}' data-duration='{round(d + GAP * 0.8, 3)}' data-track-index='2'>{html.escape(text)}</div>")

doc = f"""<!doctype html>
<html lang="en" data-resolution="landscape">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1920, height=1080" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
<style>
  :root {{ --navy: #1e2a5a; --navy2: #2f3f8f; --amber: #f6a623; --ink: #1f2430; --soft: #fff6e3; --ground: #ffffff }}
  * {{ margin: 0; padding: 0; box-sizing: border-box }}
  html, body {{ width: 1920px; height: 1080px; overflow: hidden; background: var(--ground); font-family: Inter, 'DejaVu Sans', sans-serif; color: var(--ink) }}
  #root {{ position: relative; width: 1920px; height: 1080px; overflow: hidden }}
  .scr {{ position: absolute; inset: 0; background: #fff }}
  .scr.title {{ background: linear-gradient(135deg, #1e2a5a 0%, #2f3f8f 60%, #4458c4 100%); color: #fff; padding: 120px 150px }}
  .scr.title .inner {{ position: static }}
  .kicker {{ font-size: 30px; color: #ffd27a; font-weight: 600; letter-spacing: .02em }}
  .scr.title h1 {{ font-size: 64px; line-height: 1.15; margin: 26px 0 40px; font-weight: 800; max-width: 1600px }}
  ol.plan {{ list-style: none; font-size: 34px; line-height: 1.35 }}
  ol.plan li {{ margin: 0 0 16px; display: flex; align-items: baseline }}
  .n {{ display: inline-flex; width: 52px; height: 52px; border-radius: 50%; background: var(--amber); color: var(--navy); font-weight: 800; font-size: 26px; align-items: center; justify-content: center; margin-right: 22px; flex: none }}
  .cta {{ margin-top: 30px; font-size: 38px; background: rgba(255,255,255,.12); display: inline-block; padding: 22px 34px; border-radius: 18px }}
  .bar {{ height: 92px; background: var(--navy); color: #fff; display: flex; align-items: center; gap: 26px; padding: 0 60px; font-size: 30px }}
  .bar .p {{ color: var(--amber); font-weight: 700; white-space: nowrap }}
  .bar .t {{ white-space: nowrap; overflow: hidden; text-overflow: ellipsis }}
  .content .inner {{ position: absolute; top: 92px; left: 0; right: 0; bottom: 150px; overflow: hidden; padding: 34px 90px 0 }}
  .sub {{ font-size: 44px; font-weight: 800; color: var(--navy); border-left: 10px solid var(--amber); padding-left: 22px; margin: 6px 0 22px }}
  table {{ width: 100%; border-collapse: separate; border-spacing: 0; font-size: 29px; margin: 0 0 22px }}
  th {{ background: var(--navy2); color: #fff; text-align: left; padding: 14px 18px; font-weight: 700 }}
  td {{ padding: 13px 18px; border-bottom: 2px solid #e6e9f2; vertical-align: top; line-height: 1.3 }}
  td b, .pt b, .box b {{ color: var(--navy) }}
  .pt {{ font-size: 31px; line-height: 1.4; margin: 0 0 16px; padding: 10px 18px 10px 44px; position: relative; border-radius: 10px }}
  .pt::before {{ content: ''; position: absolute; left: 16px; top: 26px; width: 12px; height: 12px; border-radius: 50%; background: var(--amber) }}
  .box {{ font-size: 31px; line-height: 1.4; background: var(--soft); border-left: 8px solid var(--amber); padding: 16px 22px; border-radius: 10px; margin: 6px 0 18px }}
  .box span {{ display: inline-block; font-size: 20px; font-weight: 800; background: var(--amber); color: #fff; padding: 3px 10px; border-radius: 6px; margin-right: 14px; vertical-align: middle }}
  .rv {{ opacity: 0 }}
  .rv.on {{ background: #fff3d6 }}
  ul.recap {{ list-style: none; margin: 34px 0 10px; font-size: 36px; line-height: 1.4; max-width: 1600px }}
  ul.recap li {{ margin: 0 0 18px; padding-left: 44px; position: relative }}
  ul.recap li::before {{ content: ''; position: absolute; left: 6px; top: 18px; width: 16px; height: 16px; border-radius: 50%; background: var(--amber) }}
  .cap {{ position: absolute; left: 160px; right: 160px; bottom: 26px; min-height: 100px; display: flex; align-items: center; justify-content: center; text-align: center;
          font-size: 30px; line-height: 1.3; color: #fff; background: rgba(20,26,56,.88); border-radius: 18px; padding: 14px 30px; z-index: 5 }}
  .cap.te {{ font-family: 'Noto Sans Telugu', 'Telugu', sans-serif; font-size: 32px; line-height: 1.5; background: rgba(120,60,0,.9) }}
  @font-face {{ font-family: 'Noto Sans Telugu'; src: url('fonts/telugu.woff2'); }}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1920" data-height="1080">
{''.join(clips)}
{''.join(caps)}
<audio id="vo" class="clip" src="narration.wav" data-start="0" data-duration="{TOTAL}" data-track-index="3"></audio>
</div>
<script>
  window.__timelines = window.__timelines || {{}};
  const tl = gsap.timeline({{ paused: true }});
  const PLAN = {json.dumps(tl)};
  // each beat: its row / point appears and is highlighted; the one before it stays, unhighlighted; a long screen
  // scrolls so the row being explained is in view (layout measured once, deterministic)
  PLAN.forEach(s => {{
    const scr = document.getElementById(s.sc), flow = scr.querySelector('.flow'), inner = scr.querySelector('.inner');
    let prev = null;
    s.beats.forEach(b => {{
      const el = b.el ? document.getElementById(b.el) : null;
      if (!el) return;
      if (el.tagName === 'TABLE') return;  // a line about the whole table: its rows come one by one
      const els = [el];
      els.forEach(e => tl.fromTo(e, {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.45, ease: 'power2.out' }}, b.t));
      if (prev) tl.set(prev, {{ backgroundColor: 'rgba(0,0,0,0)' }}, b.t);
      els.forEach(e => tl.set(e, {{ backgroundColor: '#fff3d6' }}, b.t));
      prev = els;
      const bottom = el.offsetTop + el.offsetHeight, view = inner.clientHeight - 30;
      const y = Math.max(0, bottom - view);
      tl.to(flow, {{ y: -y, duration: 0.6, ease: 'power2.inOut' }}, b.t);
    }});
  }});
  window.__timelines["main"] = tl;
  tl.seek(0);
</script>
</body>
</html>
"""
if TE_FONT:
    import shutil
    os.makedirs(f"{OUT}/fonts", exist_ok=True)
    shutil.copy(TE_FONT, f"{OUT}/fonts/telugu.woff2")
open(f"{OUT}/index.html", "w").write(doc)
print(f"{len(lines)} narration lines, {len(screens)} screens, {TOTAL:.0f} s")
