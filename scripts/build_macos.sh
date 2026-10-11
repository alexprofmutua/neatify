#!/usr/bin/env bash

set -e

if [ -x "neat/bin/python" ]; then
    PYTHON="neat/bin/python"
elif [ -x ".venv/bin/python" ]; then
    PYTHON=".venv/bin/python"
else
    PYTHON="python3"
fi

"$PYTHON" -m PyInstaller \
    --name Neatify \
    --windowed \
    --clean \
    --noconfirm \
    --icon assets/Neatify.icns \
    --add-data assets:assets \
    gui.py

rm -rf build/dmg
mkdir -p build/dmg release
cp -R dist/Neatify.app build/dmg/
ln -s /Applications build/dmg/Applications

hdiutil create \
    -volname "Neatify" \
    -srcfolder build/dmg \
    -ov \
    -format UDZO \
    release/Neatify-macOS.dmg

echo "Created release/Neatify-macOS.dmg"
