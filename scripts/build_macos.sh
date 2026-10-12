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

if [ -n "${MACOS_SIGN_IDENTITY:-}" ]; then
    echo "Signing Neatify.app with identity: $MACOS_SIGN_IDENTITY"
    codesign \
        --force \
        --deep \
        --options runtime \
        --timestamp \
        --sign "$MACOS_SIGN_IDENTITY" \
        dist/Neatify.app
else
    echo "Skipping macOS code signing. Set MACOS_SIGN_IDENTITY to sign the app."
fi

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

if [ -n "${MACOS_SIGN_IDENTITY:-}" ]; then
    echo "Signing release/Neatify-macOS.dmg"
    codesign \
        --force \
        --timestamp \
        --sign "$MACOS_SIGN_IDENTITY" \
        release/Neatify-macOS.dmg
fi

if [ -n "${APPLE_ID:-}" ] && [ -n "${APPLE_TEAM_ID:-}" ] && [ -n "${APPLE_APP_PASSWORD:-}" ]; then
    echo "Submitting release/Neatify-macOS.dmg for notarization"
    xcrun notarytool submit release/Neatify-macOS.dmg \
        --apple-id "$APPLE_ID" \
        --team-id "$APPLE_TEAM_ID" \
        --password "$APPLE_APP_PASSWORD" \
        --wait

    echo "Stapling notarization ticket"
    xcrun stapler staple release/Neatify-macOS.dmg
else
    echo "Skipping notarization. Set APPLE_ID, APPLE_TEAM_ID, and APPLE_APP_PASSWORD to notarize."
fi

echo "Created release/Neatify-macOS.dmg"
