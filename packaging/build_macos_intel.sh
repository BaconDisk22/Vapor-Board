#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
if [ "$(uname -s)" != "Darwin" ]; then
  echo "Build requires macOS" >&2
  exit 1
fi
if [ "$(uname -m)" != "x86_64" ]; then
  echo "Build requires an Intel macOS runner (x86_64)" >&2
  exit 1
fi
python3 -m pip install --upgrade pyinstaller
python3 -m PyInstaller --noconfirm --clean --windowed --name "Vapor Board" --paths . --collect-submodules vapor_board --distpath dist --workpath build --specpath build packaging/desktop_entry.py
if [ ! -d "dist/Vapor Board.app" ]; then
  echo "Expected app bundle missing" >&2
  exit 1
fi
hdiutil create -volname "Vapor Board" -srcfolder "dist/Vapor Board.app" -ov -format UDZO "dist/Vapor-Board-Intel.dmg"
