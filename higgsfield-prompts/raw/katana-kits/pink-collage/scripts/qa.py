"""qa.py - comparison sheets and frame checks of a render (venv python; run via `pc.py qa`).

usage: qa.py <job> <video.mp4>

Reads template/template.json (qa frames) and template/ref/NNN.jpg, grabs the same frames from the render and
writes <job>/qa/cmp_NN.jpg (pairs: reference | render, 12 pairs per sheet) and prints a JSON line:
  {"black": [...], "white": [...]}  frames where the render is black / white but the reference is not
"""
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

SK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SK)
from glow.media import _font  # noqa: E402

CELL = 300


def grab(video, frames, size):
    sel = '+'.join(f'eq(n\\,{n})' for n in frames)
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', video, '-vf', f"select='{sel}',scale={size}:{size}",
                          '-fps_mode', 'passthrough', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                         capture_output=True, check=True).stdout
    n = size * size * 3
    return [np.frombuffer(raw[i * n:(i + 1) * n], np.uint8).reshape(size, size, 3) for i in range(len(raw) // n)]


def main():
    job, video = sys.argv[1], sys.argv[2]
    tpl = json.load(open(os.path.join(SK, 'template', 'template.json')))
    frames = tpl['qa']
    names = {}
    for s in tpl['slots']:
        for f in range(s['f0'], s['f1']):
            names.setdefault(f, f"{s['phrase']} {s['name']}")
    got = grab(video, frames, CELL)
    out = os.path.join(job, 'qa')
    os.makedirs(out, exist_ok=True)
    black, white, per = [], [], 12
    font = _font(14)
    for si in range(0, len(frames), per):
        part = list(zip(frames, got))[si:si + per]
        cols = 4
        rows = (len(part) + cols - 1) // cols
        sheet = Image.new('RGB', (cols * (2 * CELL + 12), rows * (CELL + 20)), (18, 18, 18))
        d = ImageDraw.Draw(sheet)
        for i, (f, img) in enumerate(part):
            ref = Image.open(os.path.join(SK, 'template', 'ref', f'{f:03d}.jpg')).convert('RGB').resize((CELL, CELL))
            x, y = (i % cols) * (2 * CELL + 12), (i // cols) * (CELL + 20)
            sheet.paste(ref, (x, y + 20))
            sheet.paste(Image.fromarray(img), (x + CELL, y + 20))
            d.text((x + 4, y + 3), f'{f} {names.get(f, "")}  ref | render', fill=(255, 230, 120), font=font)
            lr = float(np.asarray(ref, np.float32).mean()) / 255
            lg = float(img.mean()) / 255
            if lg < 0.03 and lr > 0.08:
                black.append(f)
            if lg > 0.97 and lr < 0.9:
                white.append(f)
        sheet.save(os.path.join(out, f'cmp_{si // per:02d}.jpg'), quality=85)
    print(json.dumps({'frames_checked': len(got), 'black': black, 'white': white}))


if __name__ == '__main__':
    main()
