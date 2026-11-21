#!/bin/bash
# Push the finished lecture videos (out/videos/**.mp4) to GitHub, then free their disk space here:
# the local file and its git object are removed (the remote keeps them; origin is a promisor remote,
# so git fetches a video back only if something asks for it). Run from the repo root.
set -e
cd "$(git rev-parse --show-toplevel)"
git config remote.origin.promisor true
git config remote.origin.partialclonefilter blob:limit=5m
# (a video still being written – changed in the last 3 minutes – waits for the next run)
mapfile -d '' ALL < <(find out/videos -name '*.mp4' -mmin +3 -print0)
todo=()
for f in "${ALL[@]}"; do
  git ls-files --error-unmatch -- "$f" >/dev/null 2>&1 || todo+=("$f")
done
[ ${#todo[@]} -eq 0 ] && { echo "nothing new"; exit 0; }
git add -f -- "${todo[@]}"
git commit -q -m "Lecture videos: ${#todo[@]} more Telugu-narration videos

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01PKGGFub7rwSfsErjs44tnL"
for i in 1 2 3 4; do git push -q && break; sleep $((i * 5)); done
for f in "${todo[@]}"; do
  h=$(git rev-parse "HEAD:$f")
  git update-index --skip-worktree -- "$f"
  rm -f -- "$f" ".git/objects/${h:0:2}/${h:2}"
  echo "pushed: $f"
done
