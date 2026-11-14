import sys, os, shutil, json
R='/home/user/Group-app/'
W=R+'data/notes2026/review/work-b5/orig/'
def edit(rel, old, new):
    f=R+rel; os.makedirs(W,exist_ok=True)
    b=W+rel.replace('/','_')
    if not os.path.exists(b): shutil.copy(f,b)
    t=open(f).read()
    n=t.count(old)
    assert n==1, (rel, n, old)
    assert '\n' not in old and '\n' not in new
    t2=t.replace(old,new)
    assert t2.count('\n')==t.count('\n')
    open(f,'w').write(t2); print('ok',rel)
if __name__=='__main__':
    for rel,old,new in json.load(open(sys.argv[1])): edit(rel,old,new)
