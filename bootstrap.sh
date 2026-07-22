#!/usr/bin/env bash
# Fresh-sandbox bootstrap: run once at the start of each session.
set -e
cd "$(dirname "$0")"
python3 -c "import build123d" 2>/dev/null || \
  pip install --quiet --break-system-packages build123d cairosvg pillow
python3 make.py all
echo "--- environment OK, all outputs regenerated ---"
