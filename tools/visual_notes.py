"""Visual notes: a page of the notes as a hand-drawn notebook-style infographic (OpenAI image API, key in
OPENAI_API_KEY). Only the page's own facts; the model draws, it does not add facts.

    python3 tools/visual_notes.py <pages.json> <out dir> [model=gpt-image-2]
pages.json: [[topic, page title, [lines...]], ...]
"""
import base64, json, os, sys, urllib.request, concurrent.futures

PROMPT = """Create a hand-drawn study-notes page, like a neat, colourful notebook page made by a top student for exam revision
(lined notebook paper, blue/black pen handwriting, yellow highlighter behind headings, small doodle icons, coloured boxes,
arrows, simple drawings that illustrate the facts). Portrait page. Clear, large, legible handwriting.

Title at the top: "{title}"
Small subtitle (copy it exactly, in full): "{topic}"

Arrange the facts below into visually distinct sections (boxes, bullet lists, a small table or diagram where the facts
are a list, sequence or comparison): as many sections as the facts need and no more. Use ONLY these facts, word for
word where possible. STRICT: do not add any section, heading, fact, number, name, date, example or slogan that is not
below. If there are few facts, draw them larger and fill the space with simple drawings of those same facts, never
with new text. Spell every name and number exactly as written.

FACTS:
{facts}
"""


def gen(job):
    i, (topic, title, lines), out, model = job
    facts = "\n".join(lines).replace("⚠ ", "Trap: ")
    body = json.dumps({"model": model, "prompt": PROMPT.format(title=title, topic=topic, facts=facts),
                       "size": "1024x1536", "quality": "high", "n": 1}).encode()
    req = urllib.request.Request("https://api.openai.com/v1/images/generations", body,
                                 {"Authorization": "Bearer " + os.environ["OPENAI_API_KEY"], "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        d = json.load(r)
    path = f"{out}/page{i}.png"
    open(path, "wb").write(base64.b64decode(d["data"][0]["b64_json"]))
    return path, d.get("usage")


if __name__ == "__main__":
    pages = json.load(open(sys.argv[1]))
    out = sys.argv[2]
    model = sys.argv[3] if len(sys.argv) > 3 else "gpt-image-2"
    os.makedirs(out, exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(4) as ex:
        for res in ex.map(gen, [(i, p, out, model) for i, p in enumerate(pages)]):
            print(res)
