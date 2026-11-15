#!/bin/bash
# prints the next job id to launch and advances the counter
cd /home/user/Group-app/data/pyqanalysis/full; n=$(cat NEXT); n=$((n+1)); [ $n -gt 218 ] && { echo NONE; exit; }; echo $n > NEXT; printf "job-%03d\n" $n
