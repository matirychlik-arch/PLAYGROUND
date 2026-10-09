"""glow.engine - a small frame-exact compositing engine for TikTok-style "aura" edits.

Everything is float32 RGB in [0, 1] on a square or vertical canvas (default 1080x1080 @ 60 fps, set with
GLOW_W / GLOW_H / GLOW_FPS). An edit is a list of Seg(t0, t1, fn) where fn(t, u, d) returns the frame
(u = time since the segment started, d = its length), plus a global post() (grain). Sources are decoded on
demand with an LRU frame cache, so 24 fps footage maps cleanly onto a 60 fps timeline.
"""
import math
import os
import subprocess
from collections import OrderedDict

import cv2
import numpy as np
from PIL import ImageFont

W = int(os.environ.get('GLOW_W', 1080))
H = int(os.environ.get('GLOW_H', 1080))
FPS = int(os.environ.get('GLOW_FPS', 60))
FONT_DIR = os.environ.get('GLOW_FONTS', os.path.join(os.path.dirname(__file__), '..', 'assets', 'fonts'))

PINK = np.array([1.0, 0.36, 0.69], np.float32)       # hot pink  #FF5CB0
SOFT_PINK = np.array([1.0, 0.80, 0.90], np.float32)  # #FFCCE6
DEEP = np.array([0.16, 0.03, 0.12], np.float32)      # plum black
WHITE = np.array([1.0, 1.0, 1.0], np.float32)
CREAM = np.array([1.0, 0.95, 0.86], np.float32)


# ----------------------------------------------------------------------------- sources
class Source:
    """A video file with an LRU cache of decoded frames (uint8 RGB, native size)."""

    def __init__(self, path, cache_frames=int(os.environ.get('GLOW_SRC_CACHE', 96))):
        self.path = path
        out = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                              'stream=width,height,avg_frame_rate:format=duration', '-of',
                              'default=nw=1', path], capture_output=True, text=True, check=True).stdout
        kv = dict(line.split('=', 1) for line in out.strip().splitlines())
        self.w, self.h = int(kv['width']), int(kv['height'])
        a, b = kv['avg_frame_rate'].split('/')
        self.fps = float(a) / float(b)
        self.duration = float(kv['duration'])
        self.n = int(self.duration * self.fps)
        self.cache = OrderedDict()
        self.cap = cache_frames

    def _decode(self, k, count=None):
        # keep the batch well below the cache size, or slots that read several places per frame thrash
        count = count or max(8, min(36, self.cap // 4))
        t = max(0.0, (k - 0.25) / self.fps)
        raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t:.5f}', '-i', self.path, '-frames:v', str(count),
                              '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True, check=True).stdout
        sz = self.w * self.h * 3
        for i in range(len(raw) // sz):
            self.cache[k + i] = np.frombuffer(raw[i * sz:(i + 1) * sz], np.uint8).reshape(self.h, self.w, 3)
            self.cache.move_to_end(k + i)
        while len(self.cache) > self.cap:
            self.cache.popitem(last=False)

    def index(self, t):
        return int(min(self.n - 1, max(0, math.floor(t * self.fps + 1e-6))))

    def frame(self, t):
        k = self.index(t)
        if k not in self.cache:
            self._decode(k)
        if k not in self.cache:  # past the end: hold last decodable frame
            while k > 0 and k not in self.cache:
                k -= 1
                if k not in self.cache:
                    self._decode(k, 1)
        self.cache.move_to_end(k)
        return self.cache[k]


SOURCES = {}


def src(alias):
    return SOURCES[alias]


def register(alias, path):
    SOURCES[alias] = Source(path)
    return SOURCES[alias]


# ----------------------------------------------------------------------------- math helpers
def clamp01(x):
    return min(1.0, max(0.0, x))


def smooth(x):
    x = clamp01(x)
    return x * x * (3 - 2 * x)


def ease_out(x, p=3):
    return 1 - (1 - clamp01(x)) ** p


def lerp(a, b, x):
    return a + (b - a) * x


def f32(img):
    return img.astype(np.float32) / 255.0 if img.dtype == np.uint8 else img


def canvas(color=(0, 0, 0)):
    c = np.empty((H, W, 3), np.float32)
    c[:] = color
    return c


# ----------------------------------------------------------------------------- placement
def affine(cx, cy, scale, rot, ox, oy):
    """Matrix mapping source point (cx, cy) to output (ox, oy), scaled and rotated (deg, ccw+)."""
    M = cv2.getRotationMatrix2D((float(cx), float(cy)), float(rot), float(scale))
    M[0, 2] += ox - cx
    M[1, 2] += oy - cy
    return M


def warp(img, M, size=None, interp=cv2.INTER_LINEAR):
    w, h = size or (W, H)
    return cv2.warpAffine(img, M, (w, h), flags=interp, borderMode=cv2.BORDER_CONSTANT, borderValue=0)


def over(dst, rgb, a):
    """Alpha-composite rgb (HxWx3) with alpha a (HxW) over dst, in place, returns dst."""
    a3 = a[..., None]
    dst *= (1 - a3)
    dst += rgb * a3
    return dst


def place(dst, rgb, a, cx, cy, scale, rot=0.0, ox=None, oy=None, opacity=1.0):
    """Place an RGBA image (any size) onto dst: its point (cx, cy) lands at (ox, oy)."""
    ox = W / 2 if ox is None else ox
    oy = H / 2 if oy is None else oy
    M = affine(cx, cy, scale, rot, ox, oy)
    interp = cv2.INTER_AREA if scale < 0.7 else cv2.INTER_LINEAR
    wr = warp(rgb, M, interp=interp)
    wa = warp(a if a is not None else np.ones(rgb.shape[:2], np.float32), M, interp=interp)
    return over(dst, wr, np.clip(wa * opacity, 0, 1))


# ----------------------------------------------------------------------------- shots
def fit_scale(sh):
    return H / sh


def shot(alias, t, cx=None, cy=None, zoom=1.0, rot=0.0, ox=None, oy=None, dst=None):
    """Full-frame shot: source frame at time t, point (cx, cy) centred, zoom relative to fit-height."""
    s = src(alias)
    fr = f32(s.frame(t))
    cx = s.w / 2 if cx is None else cx
    cy = s.h / 2 if cy is None else cy
    M = affine(cx, cy, fit_scale(s.h) * zoom, rot, W / 2 if ox is None else ox, H / 2 if oy is None else oy)
    out = warp(fr, M, interp=cv2.INTER_CUBIC if zoom > 1.05 else cv2.INTER_LINEAR)
    if dst is None:
        return out
    a = warp(np.ones(fr.shape[:2], np.float32), M)
    return over(dst, out, a)


_SEG = {}


def segmenter(kind='isnet'):
    if kind not in _SEG:
        from .seg import Segmenter
        _SEG[kind] = Segmenter(kind)
    return _SEG[kind]


def matte(alias, t, box=None, kind='isnet'):
    """Alpha matte of the subject in the source frame at time t (cached on disk).

    kind='person': isnet edges limited to a dilated human-segmentation mask, which drops furniture and
    props that the general model sometimes keeps (chairs, railings) while keeping hair detail."""
    s = src(alias)
    k = s.index(t)
    fr = s.frame(t)
    key = f'{os.path.basename(s.path)}#{k}'
    if kind == 'person':
        a = segmenter('isnet')(fr, box=box, key=key)
        h = segmenter('human')(fr, box=box, key=key)
        ker = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (41, 41))
        hd = cv2.dilate((h > 0.3).astype(np.uint8), ker).astype(np.float32)
        hd = cv2.GaussianBlur(hd, (0, 0), 6)
        return np.clip(a * hd, 0, 1)
    return segmenter(kind)(fr, box=box, key=key)


def cut(alias, t, box=None, kind='isnet'):
    s = src(alias)
    return f32(s.frame(t)), matte(alias, t, box, kind)


def cut_smooth(alias, t, box=None, kind='isnet', radius=1):
    """Cut-out with a temporal median over +-radius source frames (kills mask flicker on live cut-outs)."""
    s = src(alias)
    k = s.index(t)
    ms = [matte(alias, (j + 0.5) / s.fps, box, kind) for j in range(max(0, k - radius), min(s.n, k + radius + 1))]
    a = np.median(np.stack(ms), 0) if len(ms) > 1 else ms[0]
    return f32(s.frame(t)), a.astype(np.float32)


def grow(a, px, feather=1.2):
    k = max(1, int(round(px)))
    hard = (a > 0.5).astype(np.uint8)
    ker = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * k + 1, 2 * k + 1))
    g = cv2.dilate(hard, ker).astype(np.float32)
    if feather > 0:
        g = cv2.GaussianBlur(g, (0, 0), feather)
    return np.maximum(g, a)


def sticker(rgb, a, stroke=10, color=WHITE):
    """Sticker look: subject over a solid outline grown from its matte. Returns (rgb, alpha)."""
    o = grow(a, stroke) if stroke > 0 else a
    out = np.empty_like(rgb)
    out[:] = color
    over(out, rgb, a)
    return out, o


def place_sticker(dst, rgb, a, cx, cy, scale, rot=0.0, ox=None, oy=None, shadow=0.35, opacity=1.0):
    """Place a sticker with a soft drop shadow."""
    if shadow > 0:
        sh = gauss(a, 6) * shadow
        place(dst, np.zeros_like(rgb), sh, cx - 6 / max(scale, 1e-3), cy - 8 / max(scale, 1e-3), scale, rot,
              ox, oy, opacity)
    return place(dst, rgb, a, cx, cy, scale, rot, ox, oy, opacity)


def bbox(a, thr=0.3, pad=0):
    ys, xs = np.where(a > thr)
    if len(xs) == 0:
        return 0, 0, a.shape[1], a.shape[0]
    return max(0, xs.min() - pad), max(0, ys.min() - pad), min(a.shape[1], xs.max() + pad), min(a.shape[0], ys.max() + pad)


# ----------------------------------------------------------------------------- effects
def gauss(img, sigma):
    if sigma < 0.3:
        return img
    return cv2.GaussianBlur(img, (0, 0), sigma)


def dir_blur(img, dx, dy, n=14):
    """Directional motion blur by averaging shifted copies (dx, dy = total smear in px)."""
    if abs(dx) + abs(dy) < 1:
        return img
    acc = np.zeros_like(img)
    for i in range(n):
        f = i / (n - 1) - 0.5
        M = np.float32([[1, 0, dx * f], [0, 1, dy * f]])
        acc += cv2.warpAffine(img, M, (img.shape[1], img.shape[0]), borderMode=cv2.BORDER_REFLECT)
    return acc / n


def zoom_blur(img, amount, cx=None, cy=None, n=12):
    """Radial zoom blur: amount = fractional scale spread (0.1 = 10%)."""
    if amount < 0.004:
        return img
    h, w = img.shape[:2]
    cx = w / 2 if cx is None else cx
    cy = h / 2 if cy is None else cy
    acc = np.zeros_like(img)
    for i in range(n):
        s = 1 + amount * i / (n - 1)
        M = cv2.getRotationMatrix2D((cx, cy), 0, s)
        acc += cv2.warpAffine(img, M, (w, h), borderMode=cv2.BORDER_REFLECT)
    return acc / n


def glitch_slices(img, shifts, n=None):
    """Horizontal slice offsets: shifts = list of dx per band (bands are equal height)."""
    n = n or len(shifts)
    out = img.copy()
    h = img.shape[0]
    for i, dx in enumerate(shifts):
        y0, y1 = i * h // n, (i + 1) * h // n
        out[y0:y1] = np.roll(img[y0:y1], int(dx), axis=1)
    return out


def flash(img, a, color=WHITE):
    if a <= 0:
        return img
    return img * (1 - a) + np.asarray(color, np.float32) * a


def radial(w=None, h=None, cx=0.5, cy=0.5, aspect=1.0):
    w = w or W
    h = h or H
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    dx = (x / w - cx) * 2
    dy = (y / h - cy) * 2 / aspect
    return np.sqrt(dx * dx + dy * dy)


_RAD = {}


def rad_cached():
    if (W, H) not in _RAD:
        _RAD[(W, H)] = radial()
    return _RAD[(W, H)]


def pink_edges(img, strength=1.0, seed=0, t=0.0):
    """Poster look: hot-pink light leaking in from the edges, black between leak and subject."""
    r = rad_cached()
    rng = np.random.default_rng(seed)
    blobs = np.zeros((9, 9), np.float32)
    blobs[:] = rng.uniform(0.55, 1.0, (9, 9))
    blobs = cv2.resize(blobs, (W, H), interpolation=cv2.INTER_CUBIC)
    edge = np.clip((r - 0.62) / 0.55, 0, 1) ** 1.3 * blobs
    dark = np.clip((r - 0.45) / 0.5, 0, 1) * 0.55
    out = img * (1 - dark[..., None] * strength)
    leak = PINK * 1.15
    out = out + (leak - out) * (edge[..., None] * strength)
    return np.clip(out, 0, 1)


def bloom(img, thr=0.72, amt=0.35, sigma=18):
    hi = np.clip((img - thr) / (1 - thr), 0, 1)
    b = cv2.GaussianBlur(hi, (0, 0), sigma)
    return np.clip(img + b * amt, 0, 1)


def grade(img, pink=0.06, contrast=1.06, sat=1.08, lift=0.015):
    """Unifying grade: gentle S-curve, plum shadows, pink highlights."""
    x = np.clip(img, 0, 1)
    x = 0.5 + (x - 0.5) * contrast
    lum = (x[..., 0] * 0.299 + x[..., 1] * 0.587 + x[..., 2] * 0.114)[..., None]
    x = lum + (x - lum) * sat
    hi = np.clip((lum - 0.45) / 0.55, 0, 1)
    lo = 1 - np.clip(lum / 0.4, 0, 1)
    x = x + pink * hi * (np.array([1.0, 0.55, 0.8], np.float32) - x) * 0.5
    x = x + 0.04 * lo * (np.array([0.35, 0.05, 0.3], np.float32) - x)
    x = lift + x * (1 - lift)
    return np.clip(x, 0, 1)


_GRAIN = {}


def grain(img, amt=0.025, seed=0):
    key = (seed % 8, W, H)
    if key not in _GRAIN:
        rng = np.random.default_rng(1000 + seed % 8)
        n = rng.standard_normal((H // 2, W // 2)).astype(np.float32)
        _GRAIN[key] = cv2.resize(n, (W, H), interpolation=cv2.INTER_LINEAR)[..., None]
    return np.clip(img + _GRAIN[key] * amt, 0, 1)


# ----------------------------------------------------------------------------- shapes
def poly_mask(points, size=None, blur=0.0, ss=2):
    w, h = size or (W, H)
    m = np.zeros((h * ss, w * ss), np.uint8)
    pts = np.round(np.asarray(points, np.float64) * ss).astype(np.int32)
    cv2.fillPoly(m, [pts], 255, lineType=cv2.LINE_AA)
    m = cv2.resize(m, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    return gauss(m, blur) if blur > 0 else m


def star_points(cx, cy, r_out, r_in, n=6, rot=0.0):
    pts = []
    for i in range(2 * n):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot) + i * math.pi / n - math.pi / 2
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def heart_points(cx, cy, s, n=120):
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((cx + x * s / 17, cy - y * s / 17))
    return pts


def ellipse_mask(cx, cy, rx, ry, size=None, blur=0.0):
    w, h = size or (W, H)
    m = np.zeros((h, w), np.float32)
    cv2.ellipse(m, (int(cx), int(cy)), (int(rx), int(ry)), 0, 0, 360, 1.0, -1, cv2.LINE_AA)
    return gauss(m, blur) if blur > 0 else m


# ----------------------------------------------------------------------------- backgrounds
def bg_glitter(seed=0, t=0.0, tint=(0.20, 0.08, 0.17)):
    rng = np.random.default_rng(seed)
    base = canvas(tint)
    tex = rng.random((H // 4, W // 4)).astype(np.float32)
    tex = cv2.resize(tex, (W, H), interpolation=cv2.INTER_LINEAR)
    base *= (0.55 + 0.6 * tex)[..., None]
    sp = rng.random((H, W)) > 0.9975
    tw = (np.sin(t * 9 + rng.random((H, W)) * 6.28) * 0.5 + 0.5)
    spark = (sp * tw).astype(np.float32)
    glow = cv2.GaussianBlur(spark, (0, 0), 2.2) * 6 + spark
    col = np.array([1.0, 0.7, 0.9], np.float32)
    out = base + glow[..., None] * col * 0.8
    # pink streaks (vertical drips like the reference board)
    for _ in range(9):
        x = int(rng.uniform(0, W))
        y0 = int(rng.uniform(0, H * 0.7))
        cv2.line(out, (x, y0), (x, y0 + int(rng.uniform(60, 260))), (0.85, 0.3, 0.6), 2, cv2.LINE_AA)
    return np.clip(out, 0, 1)


def confetti_tris(dst, seed=0, n=10, color=(1.0, 0.42, 0.75), t=0.0):
    rng = np.random.default_rng(seed)
    for _ in range(n):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        s = rng.uniform(14, 34)
        a = rng.uniform(0, 360) + t * rng.uniform(-40, 40)
        pts = [(x + s * math.cos(math.radians(a + k * 120)), y + s * 1.6 * math.sin(math.radians(a + k * 120))) for k in range(3)]
        m = poly_mask(pts)
        over(dst, np.broadcast_to(np.array(color, np.float32), dst.shape).copy(), m)
    return dst


def bg_sunburst(angle=0.0, n=14, c1=WHITE, c2=(1.0, 0.72, 0.88), cx=None, cy=None):
    cx = W / 2 if cx is None else cx
    cy = H / 2 if cy is None else cy
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    th = np.arctan2(y - cy, x - cx) + math.radians(angle)
    s = (np.sin(th * n) > 0.25).astype(np.float32)
    s = gauss(s, 1.2)
    r = np.sqrt((x - cx) ** 2 + (y - cy) ** 2) / (0.75 * W)
    s *= np.clip(r * 1.6, 0, 1)
    c1, c2 = np.asarray(c1, np.float32), np.asarray(c2, np.float32)
    return c1 * (1 - s[..., None]) + c2 * s[..., None]


# ----------------------------------------------------------------------------- text
_FONTS = {}


def font(name, size, wght=None, wdth=None):
    key = (name, int(size), wght, wdth)
    if key not in _FONTS:
        f = ImageFont.truetype(os.path.join(FONT_DIR, name), int(size))
        if wght is not None or wdth is not None:
            try:
                axes = f.get_variation_axes()
                vals = []
                for ax in axes:
                    nm = ax.get('name', b'')
                    nm = nm.decode() if isinstance(nm, bytes) else str(nm)
                    if 'eight' in nm and wght is not None:
                        vals.append(wght)
                    elif 'idth' in nm and wdth is not None:
                        vals.append(wdth)
                    else:
                        vals.append(ax.get('default', ax['minimum']))
                f.set_variation_by_axes(vals)
            except Exception:
                pass
        _FONTS[key] = f
    return _FONTS[key]


# ----------------------------------------------------------------------------- cards & frames
def crop_rgb(alias, t, cx, cy, w, h, zoom_out=None):
    """Crop a w x h window (source px) centred at (cx, cy); resized to (w, h) or zoom_out size."""
    fr = f32(src(alias).frame(t))
    sh, sw = fr.shape[:2]
    x0 = int(round(cx - w / 2))
    y0 = int(round(cy - h / 2))
    M = np.float32([[1, 0, -x0], [0, 1, -y0]])
    c = cv2.warpAffine(fr, M, (int(w), int(h)), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    if zoom_out:
        c = cv2.resize(c, zoom_out, interpolation=cv2.INTER_AREA)
    return c


# ----------------------------------------------------------------------------- timeline
class Seg:
    def __init__(self, t0, t1, fn, name=''):
        self.t0, self.t1, self.fn, self.name = t0, t1, fn, name


def frame_at(t, segs, fxs, post=None, fi=0):
    img = None
    for s in segs:
        if s.t0 <= t < s.t1:
            img = s.fn(t, t - s.t0, s.t1 - s.t0)
            break
    if img is None:
        img = canvas()
    for f in fxs:
        if f.t0 <= t < f.t1:
            img = f.fn(img, t, t - f.t0, f.t1 - f.t0)
    if post is not None:
        img = post(img, t, fi)
    return np.clip(img, 0, 1)


def to_u8(img):
    return (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)


def render(segs, fxs, duration, out, post=None, t0=0.0, t1=None, audio=None, crf=14, preset='slow', log_every=60):
    t1 = duration if t1 is None else t1
    n0, n1 = int(round(t0 * FPS)), int(round(t1 * FPS))
    cmd = ['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
           '-i', '-']
    if audio:
        cmd += ['-ss', f'{t0:.4f}', '-i', audio, '-map', '0:v', '-map', '1:a', '-c:a', 'aac', '-b:a', '256k', '-shortest']
    cmd += ['-c:v', 'libx264', '-preset', preset, '-crf', str(crf), '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    import time
    t_start = time.time()
    for fi in range(n0, n1):
        t = fi / FPS
        img = frame_at(t, segs, fxs, post, fi)
        p.stdin.write(to_u8(img).tobytes())
        if log_every and (fi - n0) % log_every == 0:
            el = time.time() - t_start
            print(f'  frame {fi - n0}/{n1 - n0} t={t:6.2f} {el:6.1f}s', flush=True)
    p.stdin.close()
    p.wait()
    return out


def stills(segs, fxs, times, out, post=None, cols=4, cell=420):
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
    from media import contact_sheet
    fr = [to_u8(frame_at(t, segs, fxs, post, int(round(t * FPS)))) for t in times]
    contact_sheet(fr, [f'{t:.3f}' for t in times], out, cols=cols, cell_w=cell)
