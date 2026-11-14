import sys,json
# usage: rep.py file  (reads JSON list of [old,new] from stdin)
f=sys.argv[1]; s=open(f).read(); n0=s.count('\n')
for old,new in json.load(sys.stdin):
    c=s.count(old)
    if c!=1: sys.exit(f"ERR count={c} for {old[:60]!r}")
    if '\n' in new and '\n' not in old: sys.exit("newline added")
    s=s.replace(old,new)
assert s.count('\n')==n0
open(f,'w').write(s); print("ok",f)
