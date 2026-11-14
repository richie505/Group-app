# usage: bk <path relative to repo>  -> backup once
bk(){ f=/home/user/Group-app/$1; b=/home/user/Group-app/data/notes2026/review/work-b5/orig/$(echo $1|tr / _); mkdir -p $(dirname $b); [ -f $b ] || cp $f $b; echo backed $b; }
# pg <file> <line> -> page
pg(){ awk -v L=$2 'NR<=L && /^=== page/{p=$3} NR==L{print p; exit}' $1; }
