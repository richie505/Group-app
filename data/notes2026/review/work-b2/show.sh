#!/bin/bash
# usage: show.sh row pattern
cd /home/user/Group-app
f=$(python3 -c "import json;print(json.load(open('data/notes2026/review/book2-notes-files.json'))['$1']['notes'])")
n=$(dirname $(dirname $f))/numbered/row-$1.txt
grep -n -F -- "$2" $n
