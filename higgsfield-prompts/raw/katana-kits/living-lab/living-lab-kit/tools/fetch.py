#!/usr/bin/env python3
"""Download clips listed in clips.json ({"V_seed": "https://…mp4", …}), extract 24 fps JPEG frames, write comp/clips.js.
Idempotent: finished clips are skipped. Usage: python3 tools/fetch.py <project_dir>   (Python 3.11, stdlib + ffmpeg)"""
import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
P = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '.')
manifest = json.load(open(os.path.join(P, 'clips.json')))
os.makedirs(os.path.join(P, 'clips'), exist_ok=True)
def one(item):
    cid, url = item
    d = os.path.join(P, 'clips', cid); meta = d + '.json'; mp4 = d + '.mp4'
    if os.path.exists(meta): return cid, json.load(open(meta))['frames'], 'cached'
    for attempt in range(4):
        r = subprocess.run(['curl', '-fsSL', '--retry', '3', '--max-time', '240', '-o', mp4, url])
        if r.returncode == 0: break
    else: return cid, 0, 'download failed'
    os.makedirs(d, exist_ok=True)
    r = subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', mp4, '-vf', "fps=24,scale='min(1920,iw)':-2", '-start_number', '0', '-q:v', '3', os.path.join(d, 'f_%04d.jpg')])
    if r.returncode != 0: return cid, 0, 'extract failed'
    n = len([f for f in os.listdir(d) if f.startswith('f_')])
    json.dump({'frames': n}, open(meta, 'w')); return cid, n, 'ok'
with ThreadPoolExecutor(max_workers=6) as ex: res = list(ex.map(one, sorted(manifest.items())))
meta = {c: {'frames': n} for c, n, s in res if n > 0}
open(os.path.join(P, 'comp', 'clips.js'), 'w').write('window.CLIPS_AVAILABLE=%s;window.CLIPS_META=%s;' % (json.dumps(sorted(meta)), json.dumps(meta)))
for c, n, s in res: print(f'{c}: {s} ({n} frames)')
bad = [c for c, n, s in res if n == 0]
if bad: print('FAILED:', ' '.join(bad)); sys.exit(1)
