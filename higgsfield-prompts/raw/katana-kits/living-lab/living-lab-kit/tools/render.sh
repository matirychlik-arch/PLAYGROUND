#!/usr/bin/env bash
# Living Lab render: clips → score (unless audio/score.m4a exists) → 720 frames → H.264/AAC MP4.
# usage: bash tools/render.sh <project_dir> <out.mp4> [score_query] [fresh]   (relative paths resolve from the caller's directory)
#   idempotent: clips, score and finished frames are reused after a timeout/recycle; pass "fresh" after changing film_data.js (re-renders all frames)
set -euo pipefail
P="$(cd "${1:-.}" && pwd)"; OUT="${2:-$P/film.mp4}"; case "$OUT" in /*) ;; *) OUT="$PWD/$OUT" ;; esac; Q="${3:-preset=arrival&bpm=120&dur=30&drop=2&vac=19.5&lift=20&end=28&key=0&seed=7}"; FRESH="${4:-}"
cd "$P"
echo "[1/4] clips"; python3 tools/fetch.py "$P"
echo "[2/4] score"; if [ ! -s audio/score.m4a ]; then node tools/cap_audio.js "audio/score.html?$Q" audio/score.wav && ffmpeg -v error -y -i audio/score.wav -c:a aac -b:a 256k audio/score.m4a; fi
echo "[3/4] frames"; FR="$P/.frames"; [ "$FRESH" = fresh ] && rm -rf "$FR"; mkdir -p "$FR"; DUR=30; N=6
pids=(); for i in $(seq 0 $((N-1))); do A=$(python3 -c "print(round($DUR*$i/$N,4))"); B=$(python3 -c "print(round($DUR*($i+1)/$N,4))"); node tools/cap.js comp/index.html "$FR" "$A" "$B" > "$FR.log$i" 2>&1 & pids+=($!); sleep 1; done
trap 'kill ${pids[@]} 2>/dev/null || true' EXIT INT TERM
for p in "${pids[@]}"; do wait "$p" || true; done
for pass in 1 2; do MISS=$(python3 - "$FR" <<'PY'
import os, sys
d = sys.argv[1]; have = {int(f[2:7]) for f in os.listdir(d) if f.startswith('f_')}
miss = [i for i in range(720) if i not in have]; runs = []
for i in miss:
    if runs and i == runs[-1][1] + 1: runs[-1][1] = i
    else: runs.append([i, i])
print(' '.join(f'{a/24:.4f}:{(b+1)/24:.4f}' for a, b in runs))
PY
); [ -z "$MISS" ] && break; echo "re-capturing $MISS"; for r in $MISS; do node tools/cap.js comp/index.html "$FR" "${r%%:*}" "${r##*:}" >> "$FR.retry" 2>&1; done; done
CNT=$(ls "$FR" | grep -c '^f_' || true); echo "frames $CNT/720"; grep -h "page errors\|FAILED" "$FR".log* 2>/dev/null | head -3 || true
[ "$CNT" -ge 720 ] || { echo "RENDER INCOMPLETE"; exit 1; }
echo "[4/4] encode"; ffmpeg -v error -y -framerate 24 -i "$FR/f_%05d.jpg" -i audio/score.m4a -map 0:v -map 1:a -c:v libx264 -preset medium -crf 16 -pix_fmt yuv420p -c:a aac -b:a 256k -shortest -movflags +faststart "$OUT"
ffprobe -v error -show_entries format=duration:stream=codec_name,width,height -of compact "$OUT"; echo "DONE $OUT"
