"""Render the Telugu-narration lecture videos (tools/lecture_video.py, NARRATION=te, voice te_IN-padmavathi) for every
topic that has a good narration script, into out/videos/<group>/<NN Subject>/<NNN Topic>.mp4 (skips videos already made).

    python3 tools/lecture_video_batch.py group2 [book] [--max N] [--jobs 2]

Needs: piper + voices (PIPER_DIR, default the session scratchpad's hf/voices), hyperframes (HF_DIR: a folder with
node_modules/hyperframes), a Telugu font (TE_FONT).
"""
import concurrent.futures as cf, json, os, re, shutil, subprocess, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lecvideo_jobs as LJ

SP = "/tmp/claude-0/-home-user/4666e051-48dd-5910-831c-f2c172f98923/scratchpad"
VOICES = os.environ.get("PIPER_DIR", f"{SP}/hf/voices")
HF = os.environ.get("HF_DIR", f"{SP}/hf")
FONT = os.environ.get("TE_FONT", os.path.expanduser("~/.fonts/NotoSansTelugu-0.ttf"))
TEMPLATE = f"{HF}/pilot"  # a hyperframes project scaffold (package.json, hyperframes.json, meta.json)

a = sys.argv[1:]
G = a[0]
BOOK = int(a[1]) if len(a) > 1 and a[1].isdigit() else None
MAX = int(a[a.index("--max") + 1]) if "--max" in a else 10 ** 6
JOBS = int(a[a.index("--jobs") + 1]) if "--jobs" in a else 2
A = f"app/src/{G}/assets"
idx = json.load(open(f"{A}/index.json"))["books"]


def safe(t):
    return re.sub(r"[^\w\- ,()&]+", "", t).strip()[:80]


def target(b, i):
    book = idx[b - 1]
    n = 1 + [k for k, r in enumerate(book["rows"]) if not r.get("hide")].index(i)
    return f"out/videos/{G}/{b:02d} {safe(book.get('short') or book['title'])}/{n:03d} {safe(book['rows'][i]['title'])}.mp4"


PUSHED = set(subprocess.run(["git", "ls-files", "out/videos"], capture_output=True, text=True).stdout.splitlines())


def done(out):
    """made already: here, or pushed to GitHub by tools/lecvideo_push.sh (which frees the local copy)"""
    return os.path.exists(out) or out in PUSHED


def one(b, i):
    out = target(b, i)
    if done(out):
        return out, "exists", 0
    w = f"{SP}/vid-work/{G}-{b}-{i}"
    shutil.rmtree(w, ignore_errors=True)
    os.makedirs(w)
    for f in ("package.json", "hyperframes.json", "meta.json"):
        shutil.copy(f"{TEMPLATE}/{f}", w)
    os.symlink(f"{HF}/node_modules", f"{w}/node_modules")
    env = dict(os.environ, NARRATION="te", PIPER_TE_VOICE=f"{VOICES}/te_IN-padmavathi-medium.onnx", TE_FONT=FONT)
    t0 = time.time()
    subprocess.run(["python3", "tools/lecture_video.py", G, str(b), str(i), w, f"{VOICES}/en_US-lessac-medium.onnx"],
                   env=env, check=True, capture_output=True)
    r = subprocess.run(["npx", "hyperframes", "render", "-o", "video.mp4", "--fps", "24", "--crf", "26", "-w", "1", "--quiet"],
                       cwd=w, capture_output=True, text=True)
    if r.returncode or not os.path.exists(f"{w}/video.mp4"):
        return out, "FAILED: " + (r.stderr or r.stdout)[-300:], time.time() - t0
    os.makedirs(os.path.dirname(out), exist_ok=True)
    # 720p for delivery: slides and Telugu captions stay sharp at about 1/3 of the size
    r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{w}/video.mp4", "-vf", "scale=1280:720", "-c:v", "libx264",
                        "-crf", "27", "-preset", "medium", "-tune", "stillimage", "-c:a", "aac", "-b:a", "64k", f"{w}/small.mp4"])
    shutil.move(f"{w}/video.mp4" if r.returncode else f"{w}/small.mp4", out)
    shutil.rmtree(w, ignore_errors=True)
    return out, "ok", time.time() - t0


todo = [(b, i) for b, i, _ in LJ.topics(G) if (BOOK is None or b == BOOK) and not LJ.check_topic(G, b, i)
        and not done(target(b, i))][:MAX]
print(f"{len(todo)} videos to make", flush=True)
with cf.ThreadPoolExecutor(JOBS) as ex:
    for out, st, sec in ex.map(lambda t: one(*t), todo):
        print(f"{st:6s} {sec:5.0f}s  {out}", flush=True)
