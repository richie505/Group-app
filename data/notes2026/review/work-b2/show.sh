#!/bin/bash
cd /home/user/Group-app
f=$(python3 -c "import json;print(json.load(open('data/notes2026/review/book2-notes-files.json'))['$1']['notes'])")
grep -n -F -- "$2" $f
