#!/usr/bin/env bash
# Contact sheet (≤ 500 KB JPEG) for visual review via sandbox image_paths.
# usage: bash tools/sheet.sh <out.jpg> <img1> [img2 …]   (labels = file names)
set -euo pipefail; OUT="$1"; shift
montage "$@" -thumbnail 360x203 -tile 4x -geometry +6+6 -background '#0a0a0a' -fill '#dddddd' -font /usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf -pointsize 13 -set label '%t' "$OUT" && convert "$OUT" -quality 80 "$OUT" && ls -la "$OUT"
