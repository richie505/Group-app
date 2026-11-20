#!/usr/bin/env bash
# Builds APPSC Lectures for Windows on Linux (the APPSC Lectures and RocketOne decks in one desktop app):
#   out/desktop-lectures/APPSC-Lectures-Setup.exe      installer (Start menu + desktop shortcut, uninstaller, no admin)
#   out/desktop-lectures/APPSC-Lectures-Windows.zip    portable copy: unzip and double-click "APPSC Lectures.exe"
# Needs: gcc-mingw-w64-x86-64, nsis, zip. The phone apps' decks must be built first
# (tools/lecture_app.py and tools/rocketone.py build).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
HERE="$ROOT/desktop-lectures/windows"
OUT="$ROOT/out/desktop-lectures"
VERSION="${1:-1.0}"
MAJOR="${VERSION%%.*}"; MINOR="${VERSION#*.}"; MINOR="${MINOR%%.*}"
STAGE="$OUT/APPSC Lectures"

echo "== the app (HTML)"
(cd "$ROOT" && python3 tools/desklec_build.py)

echo "== launcher"
sed "s/@VERSION@/$VERSION/g; s/@MAJOR@/$MAJOR/g; s/@MINOR@/$MINOR/g" "$HERE/launcher.rc.in" > "$OUT/launcher.rc"
cp "$ROOT/tools/windows/app.ico" "$OUT/app.ico"
(cd "$OUT" && x86_64-w64-mingw32-windres launcher.rc -O coff -o launcher.res)
x86_64-w64-mingw32-gcc -O2 -s -municode -mwindows -Wall -o "$STAGE/APPSC Lectures.exe" "$HERE/launcher.c" "$OUT/launcher.res" -lshell32 -ladvapi32
cat > "$STAGE/Read me.txt" <<TXT
APPSC Lectures $VERSION (with RocketOne)

Double-click "APPSC Lectures.exe". It opens in its own window using Microsoft Edge (already on Windows 10 and 11)
or Google Chrome. Everything works offline.

If the window does not open, open the file app\\index.html in any browser: it is the same app.
TXT

echo "== installer"
makensis -V2 -DVERSION="$VERSION" -DSRC="$STAGE" -DOUT="$OUT/APPSC-Lectures-Setup.exe" -DASSETS="$ROOT/tools/windows" "$HERE/installer.nsi"

echo "== portable zip"
rm -f "$OUT/APPSC-Lectures-Windows.zip"
(cd "$OUT" && zip -qr -9 "APPSC-Lectures-Windows.zip" "APPSC Lectures")
ls -la "$OUT"/APPSC-Lectures-Setup.exe "$OUT"/APPSC-Lectures-Windows.zip
