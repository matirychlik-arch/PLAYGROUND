#!/usr/bin/env bash
# Cut the user's track to 30.0 s from <start> with a 12 ms fade-in and 0.25 s fade-out → audio/score.m4a
# usage: bash tools/cut_music.sh <project_dir> <track> <start_s>
set -euo pipefail; P="$1"; T="$2"; S="$3"
ffmpeg -v error -y -ss "$S" -t 30 -i "$T" -af "afade=t=in:d=0.012,afade=t=out:st=29.75:d=0.25" -ar 48000 -ac 2 -c:a aac -b:a 256k "$P/audio/score.m4a" && echo "wrote $P/audio/score.m4a"
