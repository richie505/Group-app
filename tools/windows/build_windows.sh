#!/usr/bin/env bash
# Builds the Windows app on Linux:
#   APPSC-Prep-Setup.exe        installer (Start menu + desktop shortcut, uninstaller)
#   APPSC-Prep-Windows.zip      portable copy: unzip and double-click "APPSC Prep.exe"
# Needs: gcc-mingw-w64-x86-64, nsis, unzip, zip, curl.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
HERE="$ROOT/tools/windows"
WORK="$ROOT/desktop/build/windows"
VERSION="$(sed -n 's/^val appVersion = "\(.*\)"/\1/p' "$ROOT/desktop/build.gradle.kts")"
MAJOR="${VERSION%%.*}"; MINOR="${VERSION#*.}"; MINOR="${MINOR%%.*}"
STAGE="$WORK/APPSC Prep"
JRE_ZIP="$WORK/jre17-windows-x64.zip"

echo "== app jars (version $VERSION)"
"$ROOT/gradlew" -q -p "$ROOT" :desktop:windowsApp -Ptarget=windows

echo "== Java runtime for Windows"
if [ ! -s "$JRE_ZIP" ]; then
  curl -sSfL -o "$JRE_ZIP" "https://api.adoptium.net/v3/binary/latest/17/ga/windows/x64/jre/hotspot/normal/eclipse"
fi
rm -rf "$STAGE" "$WORK/jre"
mkdir -p "$STAGE" "$WORK/jre"
unzip -q "$JRE_ZIP" -d "$WORK/jre"
mv "$WORK"/jre/*/ "$STAGE/runtime"
cp -r "$WORK/app" "$STAGE/app"

echo "== trim the icon library to the icons the app uses"
python3 - "$STAGE/app" <<'PY'
import re, sys, zipfile, pathlib
app = pathlib.Path(sys.argv[1])
ours = next(app.glob("appsc-prep-*.jar"))
used = set()
with zipfile.ZipFile(ours) as z:
    for n in z.namelist():
        if n.endswith(".class"):
            used |= set(re.findall(rb"androidx/compose/material/icons/[a-z/]+/[A-Za-z0-9_]+Kt", z.read(n)))
used = {u.decode() for u in used}
big = next(app.glob("material-icons-extended-*.jar"))
tmp = big.with_suffix(".tmp")
with zipfile.ZipFile(big) as src, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as dst:
    for n in src.namelist():
        base = n.split("$")[0].removesuffix(".class")
        if not n.endswith(".class") or base in used:
            dst.writestr(src.getinfo(n), src.read(n))
tmp.replace(big)
print(f"   kept {len(used)} icons")
PY

echo "== launcher"
sed "s/@VERSION@/$VERSION/g; s/@MAJOR@/$MAJOR/g; s/@MINOR@/$MINOR/g" "$HERE/launcher.rc.in" > "$WORK/launcher.rc"
cp "$HERE/app.ico" "$WORK/app.ico"
x86_64-w64-mingw32-windres "$WORK/launcher.rc" -O coff -o "$WORK/launcher.res"
x86_64-w64-mingw32-gcc -O2 -s -municode -mwindows -o "$STAGE/APPSC Prep.exe" "$HERE/launcher.c" "$WORK/launcher.res"

echo "== installer"
makensis -V2 -DVERSION="$VERSION" -DSRC="$STAGE" -DOUT="$ROOT/APPSC-Prep-Setup.exe" "-X!cd $HERE" "$HERE/installer.nsi"

echo "== portable zip"
rm -f "$ROOT/APPSC-Prep-Windows.zip"
(cd "$WORK" && zip -qr -9 "$ROOT/APPSC-Prep-Windows.zip" "APPSC Prep")

ls -la "$ROOT/APPSC-Prep-Setup.exe" "$ROOT/APPSC-Prep-Windows.zip"
