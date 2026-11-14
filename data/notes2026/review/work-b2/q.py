import json,glob,sys
ids=sys.argv[1:]
seen=set()
for f in glob.glob('/home/user/Group-app/data/notes2026/runs/b2-*/all-mcqs.json'):
    try: d=json.load(open(f))
    except: continue
    items=d if isinstance(d,list) else d.get('mcqs',d.values() if isinstance(d,dict) else [])
    for q in items:
        if isinstance(q,dict) and q.get('id') in ids and q['id'] not in seen:
            seen.add(q['id']); print(f.split('/')[-2], json.dumps(q,ensure_ascii=False)[:700]); print()
