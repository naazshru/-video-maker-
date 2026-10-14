#!/usr/bin/env bash
# Rebuild the trailer: renders frames with headless Chromium + Three.js, synthesises music, muxes MP4.
set -euo pipefail
cd "$(dirname "$0")"
FR=${FRAMES_DIR:-/tmp/rose_frames}; mkdir -p "$FR"
[ -e node_modules ] || ln -s /opt/node-tools/node_modules node_modules   # needs playwright
python3 -m http.server 8765 >/dev/null 2>&1 & SRV=$!; trap 'kill $SRV' EXIT; sleep 1
for k in 0 1 2 3; do node render.mjs "$FR" 30 $((k*225)) $((k*225+225)) & done; wait
python3 music.py music.wav
ffmpeg -y -framerate 30 -i "$FR/f%05d.jpg" -i music.wav -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -shortest -movflags +faststart ../Ushvika_Rose_Tea_Trailer.mp4
