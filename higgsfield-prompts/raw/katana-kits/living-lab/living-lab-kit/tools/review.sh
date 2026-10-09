#!/usr/bin/env bash
# Review stills → 3 contact sheets (review/sheet1..3.jpg, each < 170 KB) for sandbox image_paths.
# usage: bash tools/review.sh <project_dir>
set -euo pipefail; P="$(cd "$1" && pwd)"; cd "$P"; rm -rf review; mkdir -p review
node tools/cap.js comp/index.html review 0 0 --stills 1.5,2.4,3.2,4.5,5.5,6.5,7.2,7.8,9.3,10.4,11.1,11.7,12.4,13.1,13.7,14.3,15.3,17.8,20.6,22.7,23.7,24.7,26.6,28.6 >/dev/null
mk() { montage "$@" -thumbnail 320x180 -tile 4x -geometry +4+4 -background '#0a0a0a' -fill '#dddddd' -font /usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf -pointsize 12 -set label '%t' -quality 72 "$OUT"; }
cd review; ls still_*.jpg | sort -t_ -k2 -n > list.txt
OUT=sheet1.jpg mk $(sed -n 1,8p list.txt); OUT=sheet2.jpg mk $(sed -n 9,16p list.txt); OUT=sheet3.jpg mk $(sed -n 17,24p list.txt)
ls -la sheet*.jpg
