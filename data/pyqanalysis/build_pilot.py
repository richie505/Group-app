"""Pilot sample for the PYQ word-by-word analysis: ~300 APPSC PYQs (2022+ first), every pattern, every subject.
Writes data/pyqanalysis/pilot/job-K.json (items with question, options, key, explanation, the linked notes lines)."""
import json, re, random, os, glob
from collections import defaultdict
A = "app/src/complete/assets"
random.seed(11)
links = json.load(open(f"{A}/notelinks.json"))

def pat(q):
    s = q['s'].lower()
    if q.get('k') == 'f': return 'flashcard'
    if 'assertion' in s: return 'assertion'
    if 'match' in s or 'list-i' in s or 'list i' in s: return 'match'
    if re.search(r'statement|which of the above|following is/are|correct\?', s) and '\n' in q['s']: return 'statements'
    if re.search(r'chronolog|sequence|correct order', s): return 'sequence'
    if re.search(r'\bnot\b|incorrect|false|except', s): return 'NOT'
    return 'one-liner'

# notes lines: book:row:sub:line -> text, from the topic runs' numbered files
files = {}
for b in range(1, 7):
    m = json.load(open(f"data/notes2026/review/book{b}-notes-files.json"))
    for r, v in m.items():
        d = os.path.dirname(os.path.dirname(v["notes"]))
        files[(b, int(r))] = f"{d}/numbered/row-{r}.txt"
cache = {}
def line(ref):
    b, r, s, l = ref.split(":", 3)
    f = files.get((int(b), int(r)))
    if not f or not os.path.exists(f): return None
    if f not in cache:
        cache[f] = {}
        for t in open(f):
            m = re.match(r"\[(\d+):([\d.]+)\]\s*(.*)", t)
            if m: cache[f][f"{m.group(1)}:{m.group(2)}"] = m.group(3).strip()
    return cache[f].get(f"{s}:{l}")

pool = defaultdict(list)
for b in range(1, 7):
    m = json.load(open(f"{A}/mcq{b}.json"))
    for r, l in m['rows'].items():
        for q in l:
            if not (isinstance(q, dict) and q['id'].startswith('y') and 'APPSC' in q.get('src', '')): continue
            if q.get('k') in ('f', 'u') or q.get('a', -1) < 0: continue
            y = re.search(r'(20[0-2]\d)', q['src']); y = int(y.group(1)) if y else 0
            pool[pat(q)].append((y >= 2022, b, int(r), q))
want = {'statements': 70, 'match': 45, 'assertion': 30, 'sequence': 20, 'NOT': 45, 'one-liner': 90}
items = []
for p, n in want.items():
    lst = pool[p]; random.shuffle(lst)
    lst.sort(key=lambda t: not t[0])           # 2022+ first
    # spread over the six subjects
    picked, per = [], defaultdict(int)
    for t in lst:
        if len(picked) >= n: break
        if per[t[1]] < max(4, n // 5): picked.append(t); per[t[1]] += 1
    for t in lst:
        if len(picked) >= n: break
        if t not in picked: picked.append(t)
    for recent, b, r, q in picked:
        refs = links.get(q['id'], [])
        items.append({"id": q['id'], "pattern": p, "book": b, "row": r, "exam": q.get('src', ''),
                      "q": q['s'], "options": q['o'], "key": q['a'], "key_text": q['o'][q['a']],
                      "explanation": q.get('x', ''), "tags": q.get('tg', []),
                      "notes": [{"ref": x, "text": line(x)} for x in refs[:4]]})
random.shuffle(items)
os.makedirs("data/pyqanalysis/pilot", exist_ok=True)
k = 4
for j in range(k):
    json.dump(items[j::k], open(f"data/pyqanalysis/pilot/job-{j+1}.json", "w"), ensure_ascii=False, indent=1)
from collections import Counter
print(len(items), Counter(i['pattern'] for i in items), Counter(i['book'] for i in items),
      sum(1 for i in items if any(n['text'] for n in i['notes'])), "with notes text")
