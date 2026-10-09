"""glow.y2k - Y2K / coquette design layer for the girly edits.

Lettering
  neon_text(text, size, ...)    calligraphic script as a glowing neon tube (white core, pink halo, little stars)
  crayon_text(text, size, ...)  bouncy hand-drawn crayon lettering (curly font, ragged waxy edges, grain, stars)
Frames, ornaments, backgrounds (all procedural originals drawn in the style of dotted / pencil Y2K art)
  mirror_frame(rx, ry)          dotted ornate oval mirror frame with scrolls and a bow
  dotted_rect(w, h)             dotted rectangular frame with corner scrolls
  divider(kind, w, h)           pencil ornaments: 'swirl', 'stars', 'notes', 'pixel', 'wings'
  ornate_photo(photo, style)    photo + frame + ornaments (RGBA, photo centred)
  halftone_bg(), star_band(w, h), dotify(img, cell)
"""
import functools
import math

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from glow import engine as E

NEON_FONT = 'MeaCulpa-Regular.ttf'
CRAYON_FONT = 'TwinkleStar-Regular.ttf'
MUSIC_FONT = 'NotoMusic-Regular.ttf'      # treble clef (OFL, Google Fonts)
NOTE_FONT_SYSTEM = f'{E.FONT_DIR}/DejaVuSans-Bold.ttf'   # notes (the reference render used DejaVu); falls back to Noto Music
HOT = np.array([1.0, 0.43, 0.78], np.float32)        # crayon pink
NEON_GLOW = np.array([1.0, 0.42, 0.82], np.float32)
NEON_HALO = np.array([0.98, 0.62, 0.92], np.float32)
GRAPHITE = np.array([0.20, 0.17, 0.21], np.float32)
PENCIL_PINK = np.array([1.0, 0.62, 0.82], np.float32)
PAPER = np.array([1.0, 0.975, 0.985], np.float32)


# ----------------------------------------------------------------------------- small helpers
def _pil_font(name, size):
    return ImageFont.truetype(name if name.startswith('/') else f'{E.FONT_DIR}/{name}', int(size))


def _ro(*arrs):
    """Cached assets are shared between frames: make them read-only so nothing edits them in place."""
    for x in arrs:
        x.flags.writeable = False
    return arrs


def _crop_alpha(rgb, a, margin=4):
    ys, xs = np.where(a > 0.004)
    if len(xs) == 0:
        return rgb[:1, :1], a[:1, :1]
    y0, y1 = max(0, ys.min() - margin), min(a.shape[0], ys.max() + margin + 1)
    x0, x1 = max(0, xs.min() - margin), min(a.shape[1], xs.max() + margin + 1)
    return rgb[y0:y1, x0:x1].copy(), a[y0:y1, x0:x1].copy()


def _noise(h, w, scale, seed):
    rng = np.random.default_rng(seed)
    n = rng.random((max(2, int(h / scale) + 2), max(2, int(w / scale) + 2))).astype(np.float32)
    return cv2.resize(n, (w, h), interpolation=cv2.INTER_CUBIC)


def star_pts(cx, cy, r, inner=0.45, rot=0.0, n=5):
    return E.star_points(cx, cy, r, r * inner, n=n, rot=rot)


def place(dst, rgb, a, x, y, scale=1.0, rot=0.0, opacity=1.0):
    """Place an RGBA asset by its centre."""
    return E.place(dst, rgb, a, a.shape[1] / 2, a.shape[0] / 2, scale, rot, x, y, opacity)


# ----------------------------------------------------------------------------- lettering
def _line_mask(line, fnt, stroke, pad):
    """Whole-line glyph mask (keeps kerning / script joins); returns mask and baseline-left origin."""
    l, t, r, b = fnt.getbbox(line, stroke_width=stroke)
    w, h = int(r - l + 2 * pad), int(b - t + 2 * pad)
    img = Image.new('L', (max(1, w), max(1, h)), 0)
    ImageDraw.Draw(img).text((pad - l, pad - t), line, font=fnt, fill=255, stroke_width=stroke, stroke_fill=255)
    return np.asarray(img).astype(np.float32) / 255, (pad - l, pad - t)


def script_mask(text, fnt, stroke=0, line_gap=0.78, align='center', indent=0.0):
    """Multi-line script text mask. indent shifts each next line right (by em) like hand-set script."""
    asc, desc = fnt.getmetrics()
    lh = (asc + desc) * line_gap
    pad = int(fnt.size * 0.6)
    lines = text.split('\n')
    masks = [_line_mask(ln, fnt, stroke, pad) for ln in lines]
    widths = [fnt.getlength(ln) for ln in lines]
    W_ = int(max(widths) + fnt.size * (abs(indent) * len(lines) + 1.4) + 2 * pad)
    H_ = int(lh * len(lines) + fnt.size * 1.4 + 2 * pad)
    out = np.zeros((H_, W_), np.float32)
    for i, ((m, (ox, oy)), wd) in enumerate(zip(masks, widths)):
        if align == 'center':
            x = (W_ - wd) / 2
        elif align == 'right':
            x = W_ - wd - pad
        else:
            x = pad
        x += (i - (len(lines) - 1) / 2) * indent * fnt.size
        y = pad + fnt.size * 0.6 + i * lh
        X, Y = int(round(x - ox)), int(round(y - oy))
        h, w = m.shape
        xa, ya = max(0, X), max(0, Y)
        xb, yb = min(W_, X + w), min(H_, Y + h)
        if xb > xa and yb > ya:
            out[ya:yb, xa:xb] = np.maximum(out[ya:yb, xa:xb], m[ya - Y:yb - Y, xa - X:xb - X])
    return out


def _add_stars(mask, size, n, seed, inner=0.42, scale=1.0, dots=0):
    """Sprinkle little 5-point stars (and dots) around the text block."""
    if n <= 0 and dots <= 0:
        return mask
    rng = np.random.default_rng(seed)
    h, w = mask.shape
    pad = int(size * 0.35)
    m = np.pad(mask, pad)
    H_, W_ = m.shape
    ys, xs = np.where(mask > 0.5)
    if len(xs) == 0:
        return m
    x0, x1, y0, y1 = xs.min() + pad, xs.max() + pad, ys.min() + pad, ys.max() + pad
    occ = cv2.dilate((m > 0.3).astype(np.uint8), np.ones((int(size * 0.18) | 1,) * 2, np.uint8))
    spots = []
    tries = 0
    while len(spots) < n + dots and tries < 400:
        tries += 1
        side = rng.integers(4)
        if side == 0:
            x, y = rng.uniform(x0, x1), rng.uniform(y0 - size * 0.25, y0 + size * 0.1)
        elif side == 1:
            x, y = rng.uniform(x0, x1), rng.uniform(y1 - size * 0.1, y1 + size * 0.25)
        elif side == 2:
            x, y = rng.uniform(x0 - size * 0.3, x0 + size * 0.1), rng.uniform(y0, y1)
        else:
            x, y = rng.uniform(x1 - size * 0.1, x1 + size * 0.3), rng.uniform(y0, y1)
        if not (0 < x < W_ and 0 < y < H_) or occ[int(y), int(x)]:
            continue
        if any((x - a) ** 2 + (y - b) ** 2 < (size * 0.35) ** 2 for a, b, _ in spots):
            continue
        spots.append((x, y, len(spots) < n))
    img = Image.fromarray((m * 255).astype(np.uint8))
    d = ImageDraw.Draw(img)
    for x, y, is_star in spots:
        if is_star:
            r = size * rng.uniform(0.07, 0.12) * scale
            d.polygon(star_pts(x, y, r, inner, rot=rng.uniform(-20, 20)), fill=255)
        else:
            r = size * rng.uniform(0.018, 0.03) * scale
            d.ellipse((x - r, y - r, x + r, y + r), fill=255)
    return np.asarray(img).astype(np.float32) / 255


def neon_glow(mask, size, core=(1.0, 0.97, 0.995), glow=NEON_GLOW, halo=NEON_HALO, strength=1.0, tube=True):
    """Neon tube look from a text mask: white core with a faint pink rim, pink inner glow, wide halo."""
    pad = int(size * 0.45)
    m = np.pad(mask, pad)
    if tube:   # tube shading: centre of the stroke whiter, edges pinker
        dist = cv2.distanceTransform((m > 0.5).astype(np.uint8), cv2.DIST_L2, 3)
        rim = np.clip(1 - dist / max(1.0, size * 0.018), 0, 1) * (m > 0.5)
    else:
        rim = np.zeros_like(m)
    inner = E.gauss(m, size * 0.035) * 0.95 * strength
    outer = E.gauss(m, size * 0.14) * 0.85 * strength
    core = np.asarray(core, np.float32)
    core_col = core * (1 - rim[..., None] * 0.35) + np.asarray(glow, np.float32) * rim[..., None] * 0.35
    a1 = m
    a2 = np.clip(inner, 0, 1) * (1 - a1)
    a3 = np.clip(outer, 0, 1) * (1 - a1 - a2)
    a = np.clip(a1 + a2 + a3, 0, 1)
    pm = core_col * a1[..., None] + np.asarray(glow, np.float32) * a2[..., None] + np.asarray(halo, np.float32) * a3[..., None]
    rgb = pm / np.maximum(a, 1e-4)[..., None]
    return _crop_alpha(rgb.astype(np.float32), a.astype(np.float32))


def neon_text(text, size, stars=0, seed=0, line_gap=0.8, indent=0.35, thick=0.022, font=NEON_FONT, **kw):
    fnt = _pil_font(font, size)
    m = script_mask(text, fnt, stroke=max(1, int(size * thick)), line_gap=line_gap, indent=indent)
    m = _add_stars(m, size, stars, seed, inner=0.45)
    return neon_glow(m, size, **kw)


def crayon_letters(text, size, seed=0, bounce=1.0, tracking=0.03, line_gap=0.9, thick=0.016, font=CRAYON_FONT):
    """Letter-by-letter mask with a hand-set bounce (size, tilt and baseline vary per letter)."""
    fnt = _pil_font(font, size)
    rng = np.random.default_rng(seed)
    stroke = max(1, int(size * thick))
    asc, desc = fnt.getmetrics()
    lh = (asc + desc) * line_gap
    lines = text.split('\n')
    pad = int(size * 0.5)
    widths = [sum(fnt.getlength(c) + stroke for c in ln) + tracking * size * max(0, len(ln) - 1) for ln in lines]
    W_ = int(max(widths) * 1.12 + 2 * pad)
    H_ = int(lh * len(lines) + size * 0.5 + 2 * pad)
    out = np.zeros((H_, W_), np.float32)
    for li, ln in enumerate(lines):
        x = (W_ - widths[li] * 1.06) / 2
        base = pad + asc + li * lh
        for ch in ln:
            adv = fnt.getlength(ch)
            if ch.strip():
                s = 1 + rng.uniform(-0.05, 0.07) * bounce
                rot = rng.uniform(-6, 6) * bounce
                dy = rng.uniform(-0.06, 0.06) * size * bounce
                gm, (ox, oy) = _line_mask(ch, fnt, stroke, int(size * 0.3))
                gh, gw = gm.shape
                M = cv2.getRotationMatrix2D((ox + adv / 2, oy + asc - 0.3 * size), rot, s)
                M[0, 2] += x - ox
                M[1, 2] += base + dy - oy
                warped = cv2.warpAffine(gm, M, (W_, H_), flags=cv2.INTER_LINEAR)
                out = np.maximum(out, warped)
                x += adv * s + stroke + tracking * size
            else:
                x += adv + tracking * size
    return out


def crayon_paint(mask, size, color=HOT, seed=0, grain=1.0):
    """Waxy crayon: ragged edges, speckles where the paper shows through, slight colour variation."""
    h, w = mask.shape
    n_mid = _noise(h, w, max(2.0, size * 0.045), seed)
    n_fine = np.random.default_rng(seed + 1).random((h, w)).astype(np.float32)
    soft = E.gauss(mask, max(0.8, size * 0.008))
    a = np.clip((soft - 0.5 + 0.22 * (n_mid - 0.5)) * 3.2 + 0.5, 0, 1)
    edge = np.clip(1 - np.abs(soft - 0.5) * 2.2, 0, 1)                # waxy, broken edges
    speck = (E.gauss(n_fine, 0.7) < 0.30).astype(np.float32)          # paper tooth
    a = a * (1 - grain * speck * (0.18 + 0.5 * edge))
    streak = cv2.GaussianBlur(n_fine, (0, 0), sigmaX=3.0, sigmaY=0.5)
    tone = 0.92 + 0.16 * (n_mid - 0.5) + 0.10 * (streak - 0.5)
    rgb = np.clip(np.asarray(color, np.float32) * tone[..., None] + 0.06 * speck[..., None], 0, 1)
    return _crop_alpha(rgb.astype(np.float32), a.astype(np.float32))


def crayon_text(text, size, color=HOT, stars=0, dots=0, seed=0, bounce=1.0, tracking=0.03, line_gap=0.9, thick=0.016,
                grain=1.0, font=CRAYON_FONT):
    m = crayon_letters(text, size, seed, bounce, tracking, line_gap, thick, font)
    m = _add_stars(m, size, stars, seed + 7, inner=0.48, dots=dots)
    return crayon_paint(m, size, color, seed, grain)


# ----------------------------------------------------------------------------- curves
def turtle(x, y, heading, length, k0, k1, n=220, kpow=1.0):
    """Curve from (x, y): heading in radians, curvature (1/px) ramps k0 -> k1 (clothoid: ends in a curl)."""
    s = np.linspace(0, 1, n)
    k = k0 + (k1 - k0) * s ** kpow
    ds = length / (n - 1)
    th = heading + np.concatenate([[0.0], np.cumsum(k[:-1]) * ds])
    xs = x + np.concatenate([[0.0], np.cumsum(np.cos(th[:-1])) * ds])
    ys = y + np.concatenate([[0.0], np.cumsum(np.sin(th[:-1])) * ds])
    return np.stack([xs, ys], 1)


def bez(p0, p1, p2, p3, n=90):
    p0, p1, p2, p3 = (np.asarray(p, np.float64) for p in (p0, p1, p2, p3))
    t = np.linspace(0, 1, n)[:, None]
    return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3


def normals(P):
    d = np.gradient(P, axis=0)
    d /= np.maximum(1e-6, np.linalg.norm(d, axis=1))[:, None]
    return np.stack([-d[:, 1], d[:, 0]], 1)


def taper(P, wmax, profile='both', wmin=0.6):
    """Polygon of a calligraphic stroke along P with tapered width."""
    s = np.linspace(0, 1, len(P))
    if profile == 'both':
        w = wmin + (wmax - wmin) * np.sin(np.pi * s) ** 0.8
    elif profile == 'end':        # thick start -> thin curl
        w = wmin + (wmax - wmin) * (1 - s) ** 0.9
    else:
        w = wmin + (wmax - wmin) * s ** 0.9
    N = normals(P)
    L, R = P + N * w[:, None] / 2, P - N * w[:, None] / 2
    return np.concatenate([L, R[::-1]], 0)


def mirror_x(P, cx):
    Q = np.array(P, np.float64).copy()
    Q[:, 0] = 2 * cx - Q[:, 0]
    return Q


# ----------------------------------------------------------------------------- pencil sketch canvas
class Sketch:
    """Graphite + pink layers drawn at 2x and combined like a misregistered two-colour print."""

    def __init__(self, w, h, ss=2, seed=0):
        self.w, self.h, self.ss = int(w), int(h), ss
        self.rng = np.random.default_rng(seed)
        self.layers = {k: Image.new('L', (self.w * ss, self.h * ss), 0) for k in ('g', 'fill', 'p')}
        self.d = {k: ImageDraw.Draw(v) for k, v in self.layers.items()}

    def _pts(self, P, jitter):
        P = np.asarray(P, np.float64)
        if jitter > 0 and len(P) > 3:
            n = len(P)
            k = max(2, n // 12)
            ctrl = self.rng.normal(0, jitter, (k, 2))
            P = P + np.stack([np.interp(np.linspace(0, k - 1, n), np.arange(k), ctrl[:, i]) for i in (0, 1)], 1)
        return [tuple(p) for p in (P * self.ss)]

    def line(self, P, width=2.0, layer='g', jitter=0.5, passes=2, value=235, offset=(0, 0)):
        P = np.asarray(P, np.float64) + np.asarray(offset, np.float64)
        for i in range(passes):
            self.d[layer].line(self._pts(P, jitter * (1 + i)), fill=value if i == 0 else int(value * 0.55),
                               width=max(1, int(width * self.ss * (1 if i == 0 else 0.6))), joint='curve')

    def poly(self, P, layer='fill', value=255, offset=(0, 0), outline=True, width=1.8):
        Q = np.asarray(P, np.float64) + np.asarray(offset, np.float64)
        self.d[layer].polygon(self._pts(Q, 0), fill=value)
        if outline and layer != 'p':
            self.line(np.concatenate([Q, Q[:1]], 0), width=width, layer='g', jitter=0.35, passes=2)

    def star(self, x, y, r, rot=0.0, fill_layer='fill', inner=0.45, width=2.0, pink=(5, 4)):
        P = np.array(star_pts(x, y, r, inner, rot=rot) + [star_pts(x, y, r, inner, rot=rot)[0]])
        if pink:
            self.d['p'].polygon(self._pts(P + np.asarray(pink), 0), fill=200)
        if fill_layer:
            self.d[fill_layer].polygon(self._pts(P, 0), fill=255)
        self.line(P, width=width, jitter=0.4)

    def render(self, fill_col=(1.0, 1.0, 1.0), fill_alpha=0.92, graphite=GRAPHITE, pink=PENCIL_PINK, g_alpha=0.95,
               p_alpha=0.85, grain=True):
        def get(k):
            a = np.asarray(self.layers[k]).astype(np.float32) / 255
            return cv2.resize(a, (self.w, self.h), interpolation=cv2.INTER_AREA)
        g, f, p = get('g'), get('fill'), get('p')
        if grain:
            n = 0.82 + 0.18 * np.random.default_rng(int(self.rng.integers(1 << 30))).random(g.shape).astype(np.float32)
            g = g * n
        out = np.zeros((self.h, self.w, 3), np.float32)
        a = np.zeros((self.h, self.w), np.float32)
        for col, al in ((np.asarray(pink, np.float32), p * p_alpha), (np.asarray(fill_col, np.float32), f * fill_alpha),
                        (np.asarray(graphite, np.float32), g * g_alpha)):
            out = out * (1 - al[..., None]) + col * al[..., None]
            a = a + al * (1 - a)
        rgb = out / np.maximum(a, 1e-4)[..., None]
        return rgb.astype(np.float32), np.clip(a, 0, 1).astype(np.float32)


# ----------------------------------------------------------------------------- pencil ornaments (refs: Y2K tattoo dividers)
def _thorns(sk, P, every, size, side=1, start=0.15, stop=0.8, pink=(4, 3)):
    n = len(P)
    N = normals(P) * side
    D = np.gradient(P, axis=0)
    D /= np.maximum(1e-6, np.linalg.norm(D, axis=1))[:, None]
    for i in range(int(n * start), int(n * stop), every):
        base, nn, dd = P[i], N[i], D[i]
        tri = np.array([base - dd * size * 0.45, base + nn * size * 1.3 + dd * size * 0.6, base + dd * size * 0.45])
        sk.poly(tri, 'p', 200, offset=pink, outline=False)
        sk.poly(tri, 'g', 240, outline=False)


def _swirl_parts(cx, cy, w, s):
    """Left-half filigree: long thorny tendril ending in a curl, a big C-scroll by the centre, a lower curl."""
    tendril = turtle(cx - 30 * s, cy + 12 * s, math.pi, w * 0.42, -0.004 / s, 0.09 / s, kpow=3.0)
    cscroll = turtle(cx - 22 * s, cy + 6 * s, math.pi + 1.0, 250 * s, 0.002 / s, 0.085 / s, kpow=2.2)
    lower = turtle(cx - w * 0.17, cy + 16 * s, math.pi - 0.55, 130 * s, -0.003 / s, -0.085 / s, kpow=2.0)
    upper = turtle(cx - w * 0.30, cy + 4 * s, math.pi + 0.75, 110 * s, 0.0, 0.10 / s, kpow=2.0)
    return tendril, cscroll, lower, upper


@functools.lru_cache(maxsize=64)
def divider(kind, w, h, seed=0, ink=None):
    """Symmetric pencil ornament about w x h (cropped to its ink): 'swirl', 'stars', 'notes', 'pixel', 'wings'."""
    mg = int(h * 0.6)
    sk = Sketch(w + 2 * mg, h + 2 * mg, seed=seed)
    cx, cy = w / 2 + mg, h / 2 + mg
    s = h / 160.0
    if kind == 'swirl':
        for side in (1, -1):
            def m(P):
                return P if side == 1 else mirror_x(P, cx)
            tendril, cscroll, lower, upper = _swirl_parts(cx, cy, w, s)
            poly = taper(tendril, 15 * s, 'end', 1.4 * s)
            sk.poly(m(poly), 'p', 210, offset=(6 * s, 5 * s), outline=False)
            sk.poly(m(poly), 'g', 245, outline=False)
            sk.line(m(cscroll), 2.2 * s)
            sk.line(m(cscroll), 2.0 * s, layer='p', offset=(6 * s, 5 * s), passes=1)
            sk.line(m(cscroll + normals(cscroll) * 7 * s), 1.2 * s, passes=1, value=180)
            sk.line(m(lower), 1.8 * s)
            sk.line(m(upper), 1.8 * s)
            sk.line(m(upper), 1.6 * s, layer='p', offset=(5 * s, 4 * s), passes=1)
            _thorns(sk, m(tendril), 22, 6 * s, side=-1 if side == 1 else 1, start=0.10, stop=0.55)
        heart = np.array(E.heart_points(cx, cy + 4 * s, 16 * s))
        sk.poly(heart, 'p', 220, offset=(4 * s, 4 * s), outline=False)
        sk.poly(heart, 'fill', 255, width=1.8 * s)
        sk.star(cx, cy - 30 * s, 8 * s)
    elif kind == 'stars':
        n = max(5, int(w / (h * 0.62)))
        xs = np.linspace(cx - w * 0.42, cx + w * 0.42, n)
        rng = np.random.default_rng(seed)
        wave = bez((cx - w * 0.48, cy + h * 0.1), (cx - w * 0.2, cy + h * 0.35), (cx + w * 0.2, cy - h * 0.15), (cx + w * 0.48, cy + h * 0.1))
        sk.line(wave, 1.6 * s, layer='p', offset=(0, 10 * s), passes=1)
        for i, x in enumerate(xs):
            big = 1.0 - 0.45 * abs(i - (n - 1) / 2) / ((n - 1) / 2)
            r = h * (0.20 + 0.18 * big) * rng.uniform(0.9, 1.1)
            y = cy + math.sin(i * 1.3) * h * 0.06
            sk.star(x, y, r, rot=rng.uniform(-14, 14), width=2.2 * s, pink=(5 * s, 5 * s))
            sk.star(x, y, r * 0.62, rot=rng.uniform(-10, 10), fill_layer=None, width=1.4 * s, pink=None)
    elif kind == 'notes':
        clef = _pil_font(MUSIC_FONT, h * 0.95 * sk.ss)
        try:
            notes = ImageFont.truetype(NOTE_FONT_SYSTEM, int(h * 0.36 * sk.ss))
        except OSError:
            notes = _pil_font(MUSIC_FONT, h * 0.62 * sk.ss)
        for side in (1, -1):
            def m(P):
                return P if side == 1 else mirror_x(P, cx)
            t1 = turtle(cx - 10 * s, cy + 22 * s, math.pi, w * 0.40, -0.002 / s, 0.07 / s, kpow=3.0)
            t2 = turtle(cx - 16 * s, cy + 30 * s, math.pi - 0.2, w * 0.30, 0.002 / s, -0.08 / s, kpow=2.5)
            sk.line(m(t1), 1.8 * s, layer='p', offset=(3 * s, 3 * s))
            sk.line(m(t1), 1.5 * s)
            sk.line(m(t2), 1.6 * s, layer='p')
        for x, ch, fnt, dy in ((cx - w * 0.2, '\U0001D11E', clef, -0.04), (cx + w * 0.2, '\U0001D11E', clef, -0.04),
                               (cx - w * 0.38, '\u266b', notes, 0.0), (cx - 0.06 * w, '\u266a', notes, -0.08),
                               (cx + 0.06 * w, '\u266a', notes, -0.08), (cx + w * 0.38, '\u266b', notes, 0.0)):
            bb = fnt.getbbox(ch)
            X = x * sk.ss - (bb[0] + bb[2]) / 2
            Y = (cy + dy * h) * sk.ss - (bb[1] + bb[3]) / 2
            sk.d['p'].text((X + 4 * s * sk.ss, Y + 4 * s * sk.ss), ch, font=fnt, fill=170)
            sk.d['g'].text((X, Y), ch, font=fnt, fill=245)
        for x, y in ((cx - w * 0.29, cy - h * 0.30), (cx + w * 0.29, cy - h * 0.30), (cx, cy + h * 0.25)):
            sk.star(x, y, h * 0.07, width=1.4 * s)
    elif kind == 'pixel':
        cell = max(6, int(h / 15))
        gh, gw = int((h + 2 * mg) / cell) + 1, int((w + 2 * mg) / cell) + 1
        grid = np.zeros((gh, gw), np.uint8)
        for side in (1, -1):
            for j, P in enumerate(_swirl_parts(cx, cy, w, s)):
                P = P if side == 1 else mirror_x(P, cx)
                for x, y in P:
                    gx, gy = int(x / cell), int(y / cell)
                    if 0 <= gy < gh and 0 <= gx < gw:
                        grid[gy, gx] = 1
        grid[int(cy / cell) - 1:int(cy / cell) + 2, int(cx / cell) - 1:int(cx / cell) + 1] = 1
        rng = np.random.default_rng(seed)
        ys, xs = np.where(grid)
        for _ in range(int(w / cell / 5)):
            gx = rng.integers(xs.min() - 2, xs.max() + 3)
            gy = rng.integers(ys.min() - 2, ys.max() + 3)
            if 0 <= gy < gh and 0 <= gx < gw and not grid[max(0, gy - 1):gy + 2, max(0, gx - 1):gx + 2].any():
                grid[gy, gx] = 2
        for gy, gx in zip(*np.where(grid)):
            x0, y0 = gx * cell, gy * cell
            sq = np.array([(x0, y0), (x0 + cell - 1, y0), (x0 + cell - 1, y0 + cell - 1), (x0, y0 + cell - 1)], np.float64)
            sk.poly(sq, 'p', 255, offset=(2, 2), outline=False)
            sk.poly(sq, 'fill', 255, outline=False)
            sk.line(np.concatenate([sq, sq[:1]]), 1.3, jitter=0, passes=1, value=215)
        return _ro(*_crop_alpha(*sk.render(graphite=ink or (0.66, 0.30, 0.50), p_alpha=0.7)))
    elif kind == 'wings':
        for side in (1, -1):
            def m(P):
                return P if side == 1 else mirror_x(P, cx)
            root = np.array([cx - 18 * s, cy + h * 0.18])
            for j, (ang, ln) in enumerate(((1.02, 0.47), (1.10, 0.42), (1.18, 0.35), (1.26, 0.27))):
                tip = root + np.array([math.cos(math.pi * ang), math.sin(math.pi * ang)]) * w * ln * np.array([1, 0.55])
                upper = bez(root, root + (tip - root) * 0.35 + np.array([0, -h * 0.28]), tip + np.array([w * 0.06, -h * 0.12]), tip, 60)
                lower = bez(tip, tip + np.array([w * 0.08, h * 0.10]), root + (tip - root) * 0.45 + np.array([0, h * 0.10]), root, 60)
                lobe = np.concatenate([upper, lower], 0)
                sk.poly(m(lobe), 'p', 190, offset=(5 * s, 5 * s), outline=False)
                sk.poly(m(lobe), 'fill', 255, width=1.8 * s)
                for t in (0.3, 0.55):
                    P = bez(root + (tip - root) * 0.15, root + (tip - root) * t + np.array([0, -h * 0.05]),
                            root + (tip - root) * (t + 0.2), root + (tip - root) * (t + 0.3), 30)
                    sk.line(m(P), 1.0 * s, passes=1, value=150)
            rib = turtle(cx - 4 * s, cy + h * 0.24, math.pi * 0.92, w * 0.36, 0.003 / s, -0.05 / s, kpow=2)
            sk.line(m(rib), 1.6 * s)
            sk.line(m(rib), 1.6 * s, layer='p', offset=(4 * s, 3 * s), passes=1)
        sk.star(cx, cy + h * 0.16, h * 0.08, width=1.6 * s)
    return _ro(*_crop_alpha(*sk.render(graphite=ink or GRAPHITE)))


# ----------------------------------------------------------------------------- dot-matrix frames (ref: dotted mirror frame)
def dotted(mask, cell=6, radius=None, thr=0.28, color=(1.0, 1.0, 1.0), shadow=(1.0, 0.45, 0.75), shadow_off=2,
           square=False):
    """Render a shape mask as a grid of dots: thin lines become dotted lines, filled areas dense dot fields."""
    h, w = mask.shape
    gw, gh = max(1, w // cell), max(1, h // cell)
    cov = cv2.resize(mask[:gh * cell, :gw * cell], (gw, gh), interpolation=cv2.INTER_AREA)
    on = np.where(cov > thr)
    r = radius or cell * 0.36
    img = Image.new('L', (w * 2, h * 2), 0)
    d = ImageDraw.Draw(img)
    for gy, gx in zip(*on):
        x, y = (gx + 0.5) * cell * 2, (gy + 0.5) * cell * 2
        if square:
            d.rectangle((x - r * 2, y - r * 2, x + r * 2, y + r * 2), fill=255)
        else:
            d.ellipse((x - r * 2, y - r * 2, x + r * 2, y + r * 2), fill=255)
    a = cv2.resize(np.asarray(img).astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)
    sh = np.roll(np.roll(a, shadow_off, 0), shadow_off, 1) * 0.85 if shadow is not None else np.zeros_like(a)
    sh = sh * (1 - a)
    al = np.clip(a + sh, 0, 1)
    rgb = (np.asarray(color, np.float32) * a[..., None] + np.asarray(shadow if shadow is not None else color, np.float32)
           * sh[..., None]) / np.maximum(al, 1e-4)[..., None]
    return rgb.astype(np.float32), al.astype(np.float32)


def _draw_poly(d, P, fill=255):
    d.polygon([tuple(p) for p in np.asarray(P)], fill=fill)


def _draw_line(d, P, width, fill=255):
    d.line([tuple(p) for p in np.asarray(P)], fill=fill, width=max(1, int(width)), joint='curve')


def bezchain(pts, n=60):
    """Cubic Bezier chain through [p0, c, c, p1, c, c, p2, ...]."""
    out = []
    for i in range(0, len(pts) - 3, 3):
        seg = bez(pts[i], pts[i + 1], pts[i + 2], pts[i + 3], n)
        out.append(seg if not out else seg[1:])
    return np.concatenate(out, 0)


def offset_curve(P, d):
    return P + normals(P) * d


def mirror_frame_mask(rx, ry):
    """Original ornate oval mirror: double rim, lyre-shaped side scrolls with curls and leaves, crest, bow."""
    W_, H_ = int(2 * rx * 1.75), int(2 * ry * 1.62)
    cx, cy = W_ / 2, H_ * 0.47
    img = Image.new('L', (W_, H_), 0)
    d = ImageDraw.Draw(img)
    u = rx / 300.0
    for k, (ax, ay) in enumerate(((rx, ry), (rx * 1.075, ry * 1.055))):
        d.ellipse((cx - ax, cy - ay, cx + ax, cy + ay), outline=255, width=max(2, int(7 * u)))
    for side in (1, -1):
        def m(P):
            return np.asarray(P) if side == -1 else mirror_x(P, cx)

        def X(fx):
            return cx - fx * rx

        def Y(fy):
            return cy + fy * ry
        lyre = bezchain([(X(0.70), Y(-1.02)), (X(1.30), Y(-1.18)), (X(1.62), Y(-0.40)), (X(1.16), Y(-0.02)),
                         (X(0.92), Y(0.20)), (X(1.62), Y(0.42)), (X(1.30), Y(0.88)),
                         (X(1.18), Y(1.05)), (X(0.95), Y(1.10)), (X(0.62), Y(1.07))])
        _draw_line(d, m(lyre), 8 * u)
        _draw_line(d, m(offset_curve(lyre, 15 * u)), 5 * u)
        # curls at both ends and at the waist
        e0 = lyre[0]
        c0 = turtle(e0[0], e0[1], math.pi * 1.95, 170 * u, 0.0, -0.075 / u, kpow=2.2)
        _draw_line(d, m(c0), 8 * u)
        wi = int(len(lyre) * 0.5)
        cw = turtle(lyre[wi][0], lyre[wi][1], math.pi * 0.98, 150 * u, 0.0, -0.09 / u, kpow=2.0)
        _draw_line(d, m(cw), 8 * u)
        e1 = lyre[-1]
        c1 = turtle(e1[0], e1[1], -0.15, 120 * u, 0.0, -0.10 / u, kpow=2.0)
        _draw_line(d, m(c1), 8 * u)
        # leaves on the bulges (dense dot fields)
        for t, ang, kk in ((0.22, math.pi * 0.75, 0.05), (0.40, math.pi * 1.15, -0.05), (0.70, math.pi * 1.05, 0.05),
                           (0.86, math.pi * 0.70, -0.04)):
            pp = lyre[int(t * len(lyre))]
            leaf = turtle(pp[0], pp[1], ang, 95 * u, 0.0, kk / u, kpow=1.5)
            _draw_poly(d, m(taper(leaf, 26 * u, 'both', 2 * u)))
        # crest scroll rising from the top of the rim
        cs = turtle(X(0.05), Y(-1.08), -math.pi * 0.72, 210 * u, 0.0, -0.07 / u, kpow=2.4)
        _draw_line(d, m(cs), 9 * u)
        _draw_poly(d, m(taper(cs[:int(len(cs) * 0.45)], 20 * u, 'both', 4 * u)))
        # bow loop + notched tail
        loop = bezchain([(cx, Y(1.10)), (X(0.22), Y(0.90)), (X(0.55), Y(1.00)), (X(0.42), Y(1.20)),
                         (X(0.32), Y(1.32)), (X(0.10), Y(1.22)), (cx, Y(1.12))])
        _draw_line(d, m(loop), 11 * u)
        tail = bez((cx - 8 * u, Y(1.14)), (X(0.10), Y(1.28)), (X(0.24), Y(1.34)), (X(0.30), Y(1.48)))
        _draw_poly(d, m(taper(tail, 30 * u, 'start', 12 * u)))
        notch = np.array([tail[-1] + (-16 * u, 8 * u), tail[-1] + (6 * u, -4 * u), tail[-1] + (14 * u, 18 * u)])
        _draw_poly(d, m(notch))
    d.ellipse((cx - 22 * u, Y(1.12) - 18 * u, cx + 22 * u, Y(1.12) + 18 * u), fill=255)     # bow knot
    d.polygon(star_pts(cx, Y(-1.30), 24 * u, 0.45), fill=255)                                 # crest star
    return np.asarray(img).astype(np.float32) / 255, (cx, cy)


@functools.lru_cache(maxsize=8)
def mirror_frame(rx, ry, cell=None, color=(1.0, 1.0, 1.0)):
    m, (cx, cy) = mirror_frame_mask(rx, ry)
    rgb, a = dotted(m, cell or max(4, int(rx / 46)), color=color)
    return _ro(rgb, a) + ((cx, cy),)


def dotted_rect_mask(w, h, gap=18):
    """Rectangular frame around a w x h photo: double rule, corner curls, crest star, small bow."""
    pad = int(min(w, h) * 0.22) + gap
    W_, H_ = w + 2 * pad, h + 2 * pad
    img = Image.new('L', (W_, H_), 0)
    d = ImageDraw.Draw(img)
    u = min(w, h) / 500.0
    x0, y0, x1, y1 = pad - gap, pad - gap, pad + w + gap, pad + h + gap
    d.rectangle((x0, y0, x1, y1), outline=255, width=max(2, int(6 * u)))
    o = 16 * u
    d.rectangle((x0 - o, y0 - o, x1 + o, y1 + o), outline=255, width=max(2, int(5 * u)))
    for sx, sy, (X, Y) in ((1, 1, (x0 - o, y0 - o)), (-1, 1, (x1 + o, y0 - o)), (1, -1, (x0 - o, y1 + o)),
                           (-1, -1, (x1 + o, y1 + o))):
        head = math.atan2(-sy, -sx)
        c1 = turtle(X, Y, head + 0.5 * sx * sy, 120 * u, 0.0, 0.09 / u * sx * sy, kpow=2.0)
        c2 = turtle(X, Y, head - 0.5 * sx * sy, 120 * u, 0.0, -0.09 / u * sx * sy, kpow=2.0)
        _draw_line(d, c1, 9 * u)
        _draw_line(d, c2, 9 * u)
        d.ellipse((X - 12 * u, Y - 12 * u, X + 12 * u, Y + 12 * u), fill=255)
    cxm = W_ / 2
    for side in (1, -1):
        cs = turtle(cxm, y0 - o - 4 * u, -math.pi / 2 + side * 0.9, 150 * u, 0.0, side * 0.075 / u, kpow=2.2)
        _draw_line(d, cs, 9 * u)
        lp = bez((cxm, y1 + o + 10 * u), (cxm + side * 50 * u, y1 + o - 25 * u), (cxm + side * 95 * u, y1 + o + 10 * u),
                 (cxm + side * 60 * u, y1 + o + 34 * u))
        _draw_line(d, np.concatenate([lp, [(cxm, y1 + o + 10 * u)]]), 9 * u)
        tl = bez((cxm, y1 + o + 12 * u), (cxm + side * 20 * u, y1 + o + 40 * u), (cxm + side * 40 * u, y1 + o + 60 * u),
                 (cxm + side * 45 * u, y1 + o + 80 * u))
        _draw_line(d, tl, 10 * u)
    d.polygon(star_pts(cxm, y0 - o - 40 * u, 26 * u, 0.45), fill=255)
    return np.asarray(img).astype(np.float32) / 255, pad


@functools.lru_cache(maxsize=16)
def dotted_rect(w, h, cell=None, color=(1.0, 1.0, 1.0)):
    m, pad = dotted_rect_mask(w, h)
    rgb, a = dotted(m, cell or max(4, int(min(w, h) / 80)), color=color)
    return _ro(rgb, a) + (pad,)


# ----------------------------------------------------------------------------- photos, backgrounds, transitions
def ornate_photo(photo, style='dots', border=8, border_col=(1.0, 1.0, 1.0), seed=0, ink=None):
    """Photo with a decorative frame; the photo stays centred in the returned RGBA."""
    ph, pw = photo.shape[:2]
    bw = border
    framed = np.empty((ph + 2 * bw, pw + 2 * bw, 3), np.float32)
    framed[:] = border_col
    framed[bw:bw + ph, bw:bw + pw] = photo
    fh, fw = framed.shape[:2]
    if style == 'dots':
        rgb, a, pad = dotted_rect(fw, fh)
        out_rgb, out_a = rgb.copy(), a.copy()
        y, x = pad, pad
        out_rgb[y:y + fh, x:x + fw] = framed
        out_a[y:y + fh, x:x + fw] = 1.0
        return out_rgb, out_a
    top, bottom = {'swirl': ('swirl', 'stars'), 'wings': ('notes', 'wings'), 'notes': ('notes', 'stars'),
                   'pixel': ('pixel', 'stars')}[style]
    t_rgb, t_a = divider(top, int(fw * 1.05), int(fw * 0.24), seed=seed, ink=ink)
    b_rgb, b_a = divider(bottom, int(fw * (1.25 if bottom == 'wings' else 0.9)), int(fw * 0.18), seed=seed + 1, ink=ink)
    ext = int(max(t_a.shape[0], b_a.shape[0]) * 0.75)
    side = int(max(0, (max(t_a.shape[1], b_a.shape[1]) - fw) / 2)) + 4
    H_, W_ = fh + 2 * ext, fw + 2 * side
    out_rgb = np.zeros((H_, W_, 3), np.float32)
    out_a = np.zeros((H_, W_), np.float32)
    out_rgb[ext:ext + fh, side:side + fw] = framed
    out_a[ext:ext + fh, side:side + fw] = 1.0

    def paste(rgb, a, cx, cy):
        h, w = a.shape
        X, Y = int(cx - w / 2), int(cy - h / 2)
        xa, ya, xb, yb = max(0, X), max(0, Y), min(W_, X + w), min(H_, Y + h)
        sub_a = a[ya - Y:yb - Y, xa - X:xb - X][..., None]
        out_rgb[ya:yb, xa:xb] = out_rgb[ya:yb, xa:xb] * (1 - sub_a) + rgb[ya - Y:yb - Y, xa - X:xb - X] * sub_a
        out_a[ya:yb, xa:xb] = out_a[ya:yb, xa:xb] + sub_a[..., 0] * (1 - out_a[ya:yb, xa:xb])
    paste(t_rgb, t_a, W_ / 2, ext - t_a.shape[0] * 0.22)
    paste(b_rgb, b_a, W_ / 2, ext + fh + b_a.shape[0] * 0.22)
    return out_rgb, out_a


@functools.lru_cache(maxsize=8)
def halftone_bg(seed=0, base=PAPER, dot=(1.0, 0.76, 0.89), cell=16, swirls=True, stars=True, amount=0.36):
    """Light paper with a rotated pink halftone whose dot size drifts across the frame, plus faint pencil swirls."""
    W_, H_ = E.W, E.H
    y, x = np.mgrid[0:H_, 0:W_].astype(np.float32)
    u, v = (x + y) / math.sqrt(2), (y - x) / math.sqrt(2)
    fu, fv = (u / cell) % 1 - 0.5, (v / cell) % 1 - 0.5
    dist = np.sqrt(fu * fu + fv * fv) * cell
    field = np.clip(_noise(H_, W_, 260, seed) * 0.7 + 0.3 * (y / H_), 0, 1)
    r = cell * amount * np.clip(field ** 1.6, 0.06, 1.0)
    m = np.clip(r - dist + 0.5, 0, 1)
    img = np.asarray(base, np.float32) * (1 - m[..., None]) + np.asarray(dot, np.float32) * m[..., None]
    if swirls or stars:
        sk = Sketch(W_, H_, seed=seed)
        rng = np.random.default_rng(seed)
        if swirls:
            for _ in range(4):
                P = turtle(rng.uniform(0, W_), rng.uniform(0, H_), rng.uniform(0, 2 * math.pi), rng.uniform(300, 520),
                           rng.uniform(-0.004, 0.004), rng.choice([-1, 1]) * 0.05, kpow=2.6)
                sk.line(P, 2.2, layer='p', passes=1)
        if stars:
            for _ in range(7):
                sk.star(rng.uniform(40, W_ - 40), rng.uniform(40, H_ - 40), rng.uniform(10, 22), rot=rng.uniform(-20, 20),
                        width=1.5, pink=(3, 3))
        rgb, a = sk.render(g_alpha=0.55, p_alpha=0.55)
        img = img * (1 - a[..., None]) + rgb * a[..., None]
    return _ro(img.astype(np.float32))[0]


@functools.lru_cache(maxsize=8)
def star_band(w, h, seed=0, base=(1.0, 0.56, 0.80)):
    """Replaces flat pink bars: pink band with a lighter halftone and a white pencil star chain."""
    band = np.empty((h, w, 3), np.float32)
    band[:] = base
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    cell = max(8, h // 7)
    fu, fv = (x / cell) % 1 - 0.5, (y / cell) % 1 - 0.5
    m = np.clip(cell * 0.22 - np.sqrt(fu * fu + fv * fv) * cell + 0.5, 0, 1) * 0.35
    band = band * (1 - m[..., None]) + np.ones(3, np.float32) * m[..., None]
    rgb, a = divider('stars', int(w * 0.9), int(h * 0.62), seed=seed)
    sc = min(w * 0.92 / a.shape[1], h * 0.86 / a.shape[0])
    a2 = cv2.resize(a, (int(a.shape[1] * sc), int(a.shape[0] * sc)), interpolation=cv2.INTER_AREA)
    r2 = cv2.resize(rgb, (a2.shape[1], a2.shape[0]), interpolation=cv2.INTER_AREA)
    Y0, X0 = (h - a2.shape[0]) // 2, (w - a2.shape[1]) // 2
    sub = band[Y0:Y0 + a2.shape[0], X0:X0 + a2.shape[1]]
    sub[:] = sub * (1 - a2[..., None]) + r2 * a2[..., None]
    return _ro(band)[0]


def dotify(img, cell, bg=(0.10, 0.03, 0.08), gain=1.15):
    """LED / halftone dots instead of square pixels (transition frames)."""
    h, w = img.shape[:2]
    gw, gh = max(1, w // cell), max(1, h // cell)
    small = cv2.resize(img, (gw, gh), interpolation=cv2.INTER_AREA)
    up = cv2.resize(small, (gw * cell, gh * cell), interpolation=cv2.INTER_NEAREST)
    yy, xx = np.mgrid[0:cell, 0:cell].astype(np.float32)
    tile = np.clip(cell * 0.42 - np.sqrt((xx - cell / 2 + 0.5) ** 2 + (yy - cell / 2 + 0.5) ** 2) + 0.5, 0, 1)
    mask = np.tile(tile, (gh, gw))
    out = np.empty_like(img)
    out[:] = bg
    H2, W2 = min(h, gh * cell), min(w, gw * cell)
    out[:H2, :W2] = np.asarray(bg, np.float32) * (1 - mask[:H2, :W2, None]) + \
        np.clip(up[:H2, :W2] * gain, 0, 1) * mask[:H2, :W2, None]
    return out


def card(photo, name, stat, tag, ability, desc, footer='', theme=(1.0, 0.45, 0.75), seed=0):
    """Y2K collectible card (640 x 900): halftone paper, pencil double border with corner curls, photo in a dotted
    frame under a swirl crown, crayon name, neon-script ability, star chain along the bottom."""
    cw, ch = 640, 900
    theme = np.asarray(theme, np.float32)
    rgb = np.empty((ch, cw, 3), np.float32)
    rgb[:] = PAPER
    y, x = np.mgrid[0:ch, 0:cw].astype(np.float32)
    cell = 14
    fu, fv = ((x + y) / 1.414 / cell) % 1 - 0.5, ((y - x) / 1.414 / cell) % 1 - 0.5
    field = np.clip(1.2 - np.minimum.reduce([x, y, cw - x, ch - y]) / 140, 0, 1)
    dm = np.clip(cell * 0.42 * field - np.sqrt(fu * fu + fv * fv) * cell + 0.5, 0, 1)
    rgb = rgb * (1 - dm[..., None]) + (theme * 0.35 + 0.65) * dm[..., None]
    a = np.zeros((ch, cw), np.float32)
    r = 30
    cv2.rectangle(a, (r, 0), (cw - r, ch), 1, -1)
    cv2.rectangle(a, (0, r), (cw, ch - r), 1, -1)
    for cxy in [(r, r), (cw - r, r), (r, ch - r), (cw - r, ch - r)]:
        cv2.circle(a, cxy, r, 1, -1, cv2.LINE_AA)
    sk = Sketch(cw, ch, seed=seed)
    for o, wd in ((18, 2.4), (28, 1.4)):
        P = np.array([(o, o + 14), (o, ch - o - 14), (o + 14, ch - o), (cw - o - 14, ch - o), (cw - o, ch - o - 14),
                      (cw - o, o + 14), (cw - o - 14, o), (o + 14, o), (o, o + 14)], np.float64)
        sk.line(P, wd)
        sk.line(P, wd, layer='p', offset=(4, 4), passes=1)
    for sx, sy, X, Y in ((1, 1, 30, 30), (-1, 1, cw - 30, 30), (1, -1, 30, ch - 30), (-1, -1, cw - 30, ch - 30)):
        c1 = turtle(X, Y, math.atan2(sy, sx), 70, 0.0, 0.16 * sx * sy, kpow=2.0)
        sk.line(c1, 1.8)
    srgb, sa = sk.render()
    rgb = rgb * (1 - sa[..., None]) + srgb * sa[..., None]
    # photo in a dotted frame
    pw, ph = 440, 360
    p = cv2.resize(photo, (pw, ph), interpolation=cv2.INTER_AREA)
    frgb, fa, pad = dotted_rect(pw, ph, color=(1.0, 1.0, 1.0))
    sc = (cw - 70) / fa.shape[1]
    frgb = cv2.resize(frgb, (int(fa.shape[1] * sc), int(fa.shape[0] * sc)), interpolation=cv2.INTER_AREA)
    fa = cv2.resize(fa, (frgb.shape[1], frgb.shape[0]), interpolation=cv2.INTER_AREA)
    pad_s = int(pad * sc)
    ph2, pw2 = int(ph * sc), int(pw * sc)
    p = cv2.resize(p, (pw2, ph2), interpolation=cv2.INTER_AREA)
    X0, Y0 = (cw - frgb.shape[1]) // 2, 138
    deep = np.clip(theme * 0.75, 0, 1)
    sub = rgb[Y0:Y0 + frgb.shape[0], X0:X0 + frgb.shape[1]]
    h_, w_ = sub.shape[:2]
    sub[:] = sub * (1 - fa[:h_, :w_, None]) + (frgb[:h_, :w_] * 0.0 + deep) * fa[:h_, :w_, None]
    rgb[Y0 + pad_s:Y0 + pad_s + ph2, X0 + pad_s:X0 + pad_s + pw2] = p
    # texts
    def put(asset, x, y, anchor='mm', maxw=None):
        r_, a_ = asset
        if maxw and r_.shape[1] > maxw:
            s_ = maxw / r_.shape[1]
            r_ = cv2.resize(r_, (int(r_.shape[1] * s_), int(r_.shape[0] * s_)), interpolation=cv2.INTER_AREA)
            a_ = cv2.resize(a_, (r_.shape[1], r_.shape[0]), interpolation=cv2.INTER_AREA)
        h, w = a_.shape
        X = int(x - (w / 2 if anchor[0] == 'm' else (0 if anchor[0] == 'l' else w)))
        Y = int(y - h / 2)
        xa, ya, xb, yb = max(0, X), max(0, Y), min(cw, X + w), min(ch, Y + h)
        if xb <= xa or yb <= ya:
            return
        s_a = a_[ya - Y:yb - Y, xa - X:xb - X][..., None]
        rgb[ya:yb, xa:xb] = rgb[ya:yb, xa:xb] * (1 - s_a) + r_[ya - Y:yb - Y, xa - X:xb - X] * s_a
    # every text field is optional (an empty field leaves the card's paper and ornaments only)
    if name.strip():
        put(crayon_text(name, 92, color=deep, seed=seed + 1, grain=0.6), 54, 92, 'lm', maxw=380)
    if stat.strip():
        put(crayon_text(stat, 40, color=deep, seed=seed + 2, grain=0.5), cw - 50, 96, 'rm')
    lt = (1.0, 0.40, 0.74)
    if tag.strip():
        put(neon_text(tag, 54, core=lt, glow=(1.0, 0.62, 0.86), halo=(1.0, 0.82, 0.93), strength=0.8), cw / 2,
            650, 'mm', maxw=520)
    if ability.strip():
        put(neon_text(ability, 72, core=(0.55, 0.12, 0.38), glow=(1.0, 0.55, 0.82), halo=(1.0, 0.80, 0.92),
                      strength=0.7), cw / 2, 718, 'mm', maxw=540)
    if desc.strip():
        put(crayon_text(desc, 30, color=(0.40, 0.12, 0.30), seed=seed + 3, bounce=0.4, grain=0.35), cw / 2,
            784, 'mm', maxw=520)
    br, ba = divider('stars', 500, 60, seed=seed)
    put((br, ba), cw / 2, ch - 50, 'mm', maxw=400)
    if footer:
        put(crayon_text(footer, 20, color=(0.45, 0.2, 0.38), bounce=0.2, grain=0.2), cw / 2, ch - 16, 'mm')
    return rgb.astype(np.float32), a


def outlined(asset, px=7, color=(1.0, 1.0, 1.0), shadow=0.0):
    """Sticker-style outline under a lettering asset (keeps crayon titles readable on busy footage)."""
    rgb, a = asset
    pad = px + 4
    a2 = np.pad(a, pad)
    r2 = np.pad(rgb, ((pad, pad), (pad, pad), (0, 0)))
    ker = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * px + 1, 2 * px + 1))
    o = E.gauss(cv2.dilate((a2 > 0.35).astype(np.float32), ker), 1.2)
    out_a = np.maximum(o, a2)
    out = np.asarray(color, np.float32) * (1 - a2[..., None]) + r2 * a2[..., None]
    out = np.where(out_a[..., None] > 0, out, 0)
    return out.astype(np.float32), out_a.astype(np.float32)
