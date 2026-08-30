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
    gui.py
