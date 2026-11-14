#!/bin/bash
# pg.sh file pattern -> matching lines with page
awk -v P="$2" '/^=== page/{p=$3} tolower($0) ~ tolower(P){print "p." p ": " NR ": " $0}' "$1" | head -${3:-20}
