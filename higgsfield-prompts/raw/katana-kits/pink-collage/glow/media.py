"""media.py - ffmpeg/numpy/OpenCV/PIL helpers + analysis CLI (pink-collage). No PyPI installs beyond those.

API:  probe(path) · read_frames(path, fps, size, start, dur) · read_audio(path, sr, mono, start, dur)
      frame_scores(path, size) · detect_cuts(path, ...) · contact_sheet(frames, labels, out, cols, cell_w)
CLI:
  python3 media.py cuts   VIDEO [OUT.json]            cut times (s) and frame numbers; optional JSON list
  python3 media.py shots  VIDEO OUT_PREFIX             shots JSON + sheets (first/middle/last frame per shot)
  python3 media.py frames VIDEO OUT.jpg T0 T1 [EVERY]  every frame at NATIVE fps (measure flashes, text states)
  python3 media.py detail VIDEO OUT_PREFIX STEP T0-T1[:label] ...   frames every STEP s over ranges
  python3 media.py grid   VIDEO OUT.jpg T1 T2 ...      full-res frames with a labelled 100-px grid (crop centres)
"""
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont


def run(args, **kw):
    return subprocess.run(args, check=True, capture_output=True, **kw)


def probe(path):
    out = run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
               'stream=width,height,avg_frame_rate,nb_frames:format=duration', '-of', 'json', path]).stdout
    d = json.loads(out)
    s = d['streams'][0]
    num, den = (int(x) for x in s['avg_frame_rate'].split('/'))
    return dict(width=int(s['width']), height=int(s['height']), fps=num / den if den else 0.0,
                duration=float(d['format']['duration']), nb_frames=int(s.get('nb_frames') or 0))


def thumb_size(info, w=320):
    return w, int(round(w * info['height'] / info['width'] / 2)) * 2


def read_frames(path, fps=None, size=None, start=0.0, dur=None):
    """Yield (t, rgb uint8). fps=None keeps the native rate; size=(w, h) rescales."""
    info = probe(path)
    w, h = size if size else (info['width'], info['height'])
    vf = ([f'fps={fps}'] if fps else []) + ([f'scale={w}:{h}:flags=area'] if size else [])
    args = ['ffmpeg', '-v', 'error'] + (['-ss', f'{start:.4f}'] if start else []) + ['-i', path]
    args += (['-t', f'{dur:.4f}'] if dur else []) + (['-vf', ','.join(vf)] if vf else [])
    p = subprocess.Popen(args + ['-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    rate, n, fsz = fps or info['fps'], 0, w * h * 3
    try:
        while True:
            buf = p.stdout.read(fsz)
            if len(buf) < fsz:
                break
            yield start + n / rate, np.frombuffer(buf, np.uint8).reshape(h, w, 3)
            n += 1
    finally:
        p.stdout.close()
        p.wait()


def read_audio(path, sr=48000, mono=False, start=0.0, dur=None):
    args = ['ffmpeg', '-v', 'error'] + (['-ss', f'{start:.4f}'] if start else []) + ['-i', path]
    args += (['-t', f'{dur:.4f}'] if dur else []) + ['-vn', '-ac', '1' if mono else '2', '-ar', str(sr), '-f', 'f32le', '-']
    a = np.frombuffer(run(args).stdout, np.float32)
    return a if mono else a.reshape(-1, 2)


def frame_scores(path, size=None):
    """Per-frame change score: downscaled luma difference + HSV histogram distance."""
    import cv2
    size = size or thumb_size(probe(path), 192)
    ts, scores, prev, prev_hist = [], [], None, None
    for t, f in read_frames(path, size=size):
        g = cv2.cvtColor(f, cv2.COLOR_RGB2GRAY).astype(np.float32) / 255
        hist = cv2.normalize(cv2.calcHist([cv2.cvtColor(f, cv2.COLOR_RGB2HSV)], [0, 1], None, [24, 16],
                                          [0, 180, 0, 256]), None).flatten()
        s = 0.0 if prev is None else 0.5 * min(1.0, float(np.mean(np.abs(g - prev))) * 4) + \
            0.5 * float(cv2.compareHist(prev_hist, hist, cv2.HISTCMP_BHATTACHARYYA))
        ts.append(t)
        scores.append(s)
        prev, prev_hist = g, hist
    return np.array(ts), np.array(scores)


def median9(x, k=9):
    pad = np.pad(x, k // 2, mode='edge')
    return np.median(np.lib.stride_tricks.sliding_window_view(pad, k), axis=1)


def detect_cuts(path, thresh=0.35, min_gap=0.06, rel=2.5):
    """Cuts = score above an absolute threshold AND well above the local median (motion/flashes inside a shot
    are not cuts). min_gap is small on purpose: edits have 2-4 frame flashes that you want to see."""
    ts, sc = frame_scores(path)
    med = median9(sc)
    cuts = []
    for i in np.where((sc > thresh) & (sc > rel * med + 0.05))[0]:
        if not cuts or ts[i] - cuts[-1] >= min_gap:
            cuts.append(float(ts[i]))
    return cuts, ts, sc


def _font(size):
    fd = os.environ.get('GLOW_FONTS', '')
    for p in [os.path.join(fd, 'DejaVuSans-Bold.ttf'), '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()


def contact_sheet(frames, labels, out, cols=8, cell_w=240, quality=85):
    if not frames:
        return
    h0, w0 = frames[0].shape[:2]
    cell_h = int(round(cell_w * h0 / w0))
    rows = (len(frames) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * cell_w, rows * (cell_h + 18)), (20, 20, 20))
    d, f = ImageDraw.Draw(sheet), _font(13)
    for i, (fr, lb) in enumerate(zip(frames, labels)):
        x, y = (i % cols) * cell_w, (i // cols) * (cell_h + 18)
        sheet.paste(Image.fromarray(fr).resize((cell_w, cell_h), Image.LANCZOS), (x, y + 18))
        d.text((x + 4, y + 2), lb, fill=(255, 230, 120), font=f)
    sheet.save(out, quality=quality)


def grab(path, t, info):
    raw = run(['ffmpeg', '-v', 'error', '-ss', f'{float(t):.4f}', '-i', path, '-frames:v', '1', '-f', 'rawvideo',
               '-pix_fmt', 'rgb24', '-']).stdout
    return np.frombuffer(raw, np.uint8).reshape(info['height'], info['width'], 3).copy()


def cli():
    cmd, path = sys.argv[1], sys.argv[2]
    info = probe(path)
    if cmd == 'cuts':
        cuts, _, _ = detect_cuts(path)
        if len(sys.argv) > 3:
            json.dump(cuts, open(sys.argv[3], 'w'))
        print(f"{info['width']}x{info['height']} {info['fps']:.3f} fps {info['duration']:.3f} s, {len(cuts)} cuts")
        for c in cuts:
            print(f'{c:8.3f}  frame {round(c * info["fps"])}')
    elif cmd == 'shots':
        out = sys.argv[3]
        cuts, _, _ = detect_cuts(path, thresh=0.28, min_gap=0.25, rel=2.2)
        bounds = [0.0] + cuts + [info['duration']]
        shots = [dict(i=k, t0=round(a, 3), t1=round(b, 3)) for k, (a, b) in enumerate(zip(bounds, bounds[1:])) if b - a > 0.05]
        json.dump(shots, open(f'{out}_shots.json', 'w'), indent=1)
        want = sorted([(s['i'], p, s['t0'] + f * (s['t1'] - s['t0'])) for s in shots
                       for p, f in (('a', 0.08), ('m', 0.5), ('z', 0.92))], key=lambda x: x[2])
        frames, j = {}, 0
        for t, f in read_frames(path, size=thumb_size(info)):
            while j < len(want) and want[j][2] <= t + 1e-6:
                frames[want[j][:2]] = f
                j += 1
            if j >= len(want):
                break
        fr, lb = [], []
        for s in shots:
            for p in 'amz':
                if (s['i'], p) in frames:
                    fr.append(frames[(s['i'], p)])
                    lb.append(f"#{s['i']} {s['t0']:.2f}-{s['t1']:.2f}" if p == 'a' else f"#{s['i']} {p}")
        for n in range(0, len(fr), 48):
            contact_sheet(fr[n:n + 48], lb[n:n + 48], f'{out}_sheet_{n // 48:02d}.jpg', cols=6, cell_w=320)
        print(len(shots), 'shots')
    elif cmd == 'frames':
        out, t0, t1 = sys.argv[3], float(sys.argv[4]), float(sys.argv[5])
        every = int(sys.argv[6]) if len(sys.argv) > 6 else 1
        fr, lb = [], []
        for i, (t, f) in enumerate(read_frames(path, size=thumb_size(info, 240), start=t0, dur=t1 - t0)):
            if i % every == 0:
                fr.append(f)
                lb.append(f'{t:.3f} f{round(t * info["fps"])}')
        contact_sheet(fr, lb, out, cols=10, cell_w=240)
        print(len(fr), 'frames')
    elif cmd == 'detail':
        out, step = sys.argv[3], float(sys.argv[4])
        fr, lb = [], []
        for spec in sys.argv[5:]:
            rng, _, label = spec.partition(':')
            a, b = (float(x) for x in rng.split('-'))
            for t, f in read_frames(path, fps=1 / step, size=thumb_size(info), start=a, dur=b - a):
                fr.append(f)
                lb.append(f'{label} {t:.2f}')
        for k in range(0, len(fr), 48):
            contact_sheet(fr[k:k + 48], lb[k:k + 48], f'{out}_{k // 48:02d}.jpg', cols=8, cell_w=240)
        print(len(fr), 'frames')
    elif cmd == 'grid':
        import cv2
        out, fr = sys.argv[3], []
        for t in sys.argv[4:]:
            f = grab(path, t, info)
            for x in range(0, info['width'], 100):
                f[:, x:x + 2] = (255, 0, 0) if x % 500 == 0 else (255, 255, 0)
                cv2.putText(f, str(x), (x + 4, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 0), 2)
            for y in range(0, info['height'], 100):
                f[y:y + 2, :] = (255, 0, 0) if y % 500 == 0 else (0, 255, 255)
                cv2.putText(f, str(y), (4, y + 28), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
            fr.append(f)
        contact_sheet(fr, sys.argv[4:], out, cols=3, cell_w=min(958, info['width']))
    else:
        sys.exit(__doc__)


if __name__ == '__main__':
    cli()
