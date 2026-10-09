#!/usr/bin/env bash
# Start-frame or clip review sheets: downloads images (or takes frame 60 of each fetched clip) and labels them by slot id.
# usage: bash tools/keysheet.sh <work_dir> <manifest.json {"V_x": "https://…png|mp4", …}>   → <work_dir>/keys_N.jpg (8 per sheet)
set -euo pipefail; D="$1"; M="$(cd "$(dirname "$2")" && pwd)/$(basename "$2")"; mkdir -p "$D/k"; cd "$D"; rm -f k/s*.txt keys_*.jpg
python3 - "$M" <<'PY'
import json, subprocess, sys
for k, u in json.load(open(sys.argv[1])).items():
    out = f'k/{k}.jpg'
    if u.endswith('.mp4'):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '2.5', '-i', u, '-frames:v', '1', '-vf', 'scale=480:-2', out])
    else:
        subprocess.run(['curl', '-fsSL', '-o', f'k/{k}.src', u]); subprocess.run(['convert', f'k/{k}.src', '-resize', '480x', out])
PY
ls k/*.jpg | sort > k/list.txt; n=0; i=1
while read -r f; do echo "$f" >> "k/s$i.txt"; n=$((n+1)); [ $((n % 8)) -eq 0 ] && i=$((i+1)); done < k/list.txt
for s in k/s*.txt; do b=$(basename "$s" .txt); montage $(cat "$s") -thumbnail 320x180 -tile 4x -geometry +4+4 -background '#0a0a0a' -fill '#dddddd' -font /usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf -pointsize 12 -set label '%t' -quality 72 "keys_${b#s}.jpg"; done; ls -la keys_*.jpg
