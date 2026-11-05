# APPSC Complete: check doubtful answer keys against reliable sources

Each `## <id>` block is an MCQ whose key looks wrong: its explanation seems to point at another option, or a writer
found the key contradicts the explanation. For EVERY block, decide with a web search (WebSearch / WebFetch) when you
are not certain from the question itself, preferring official or standard sources (government sites, PIB, RBI,
UNESCO, NCERT, Britannica, the official APPSC/UPSC answer keys).

Write one line per block, in the same order, to data/keys/out/<n>.md:

```
<id> | KEEP | <why, short>
<id> | KEY <option number> | <source URL> | <one-line correct fact>
<id> | EXPLAIN | <source URL> | <corrected explanation, one or two sentences>
<id> | UNSURE | <why>
```

- `KEEP`: the key is right (the explanation may say "X, not Y": that is fine).
- `KEY n`: the key is wrong and option n is right, shown by the source. The fact line becomes the new explanation.
- `EXPLAIN`: the key is right but the explanation is wrong or about something else.
- `UNSURE`: sources disagree or nothing reliable found. Never guess.
- A question with an official answer key (APPSC/UPSC) keeps the official answer unless it was officially revised.

Check before you finish: every id of the packet appears once, in order:

```
python3 - <<'Y'
import re; n="<n>"
a=re.findall(r"^## (\S+)", open(f"data/keys/in/{n}.md").read(), re.M)
b=[l.split(" | ")[0] for l in open(f"data/keys/out/{n}.md") if " | " in l]
print("missing", sorted(set(a)-set(b)), "order ok", a==b)
Y
```
Report: KEEP / KEY / EXPLAIN / UNSURE counts and the KEY changes in one line each.
