"""edit.py - the Pink Collage edit, re-filled with a job's footage (venv python; run via pc.py).

The slot code is the original Princess Glow Up Y2K aura edit (scripts/dev/princess_glow_up_y2k.orig.py).

The template is the delivered edit princess.mp4: the original code (scripts/dev/princess_glow_up_y2k.orig.py)
rendered from the first drop (the pastel intro is cut) to the end of the final fade: output frame 0 = timeline
frame 114 (1.900 s), 795 frames at 60 fps = 13.25 s, 1080x1080.

The template plays one visual phrase per drop of a 16-beat music loop; phrase A (drop 1) and phrase B (drop 2)
each have 40 slots (SCHED). Every slot is fn(t, u, d) -> frame (u = time since the slot began, d = its length).
What fills the slots comes from the job, not from code:
  <job>/cast.json   per phrase the shot choices (written by `pc.py edit` from the clip analysis + fixes.json)
                    shot (alias, t_in, cx, cy, zoom) · crop (alias, t, cx, cy, w, h) · cut-out (alias, t, box[, excl])
  <job>/texts.json  {"text": "..."}: the prompt box. Every lettering beat of the template shows this one text
                    (see texts()); empty = an edit with no lettering at all (the beats keep their footage and
                    graphics). The episode label, blurb and credit line of the original are not used.

usage: edit.py <job> segs
       edit.py <job> stills OUT.jpg t1[:label] t2 ...   output times (s) -> labelled contact sheet
       edit.py <job> warm [k/n]                         precompute the cut-out masks (share k of n)
       edit.py <job> chunk OUT.mp4 f0 f1                video-only output frames [f0, f1) (lossless-ish x264)
"""
import functools
import json
import math
import os
import subprocess
import sys
import time

import cv2
import numpy as np

SK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SK)
from glow import engine as E  # noqa: E402
from glow.engine import PINK, WHITE, CREAM, Seg, canvas, clamp01, ease_out, lerp, smooth  # noqa: E402
from glow import y2k as Y  # noqa: E402

JOB = os.path.abspath(sys.argv[1])
W, H, FPS = E.W, E.H, E.FPS
BPM = 136.15
P = 60 / BPM
G0 = 0.168                      # first beat of the sound (after removing the 50 ms mp3 priming)
D1 = G0 + 4 * P                 # drop 1 = 1.931 s
D2 = D1 + 16 * P                # drop 2 = 8.982 s (the music loop is exactly 16 beats)
FADE0, FADE1 = D2 + 5.97, D2 + 6.17
F = 1 / FPS
N0 = 114                        # first output frame on the original timeline (drop cut-out, D1 - 0.031 s)
NF = 795                        # output frames: timeline frames 114..908 (end of the final fade) = 13.25 s
T0 = N0 / FPS

# Phrase schedule: slot start offsets (seconds from the drop beat), read off the reference frame by frame.
SCHED = [
    (-0.031, 'drop'), (0.169, 'dots'), (0.202, 'poster'), (0.769, 'dip'), (0.802, 'whip'), (0.886, 'photo'),
    (1.136, 'pix'), (1.169, 'darkblur'), (1.202, 'collage'), (1.836, 'whipW'), (1.886, 'square'),
    (2.036, 'closeup'), (2.569, 'blurC'), (2.602, 'starflash'), (2.636, 'card1'), (2.869, 'mesh'),
    (2.902, 'whip2'), (2.969, 'card2'), (3.286, 'bars'), (3.352, 'textcu'), (3.702, 'nametype'),
    (3.769, 'namebold'), (3.852, 'close1'), (4.119, 'whip3'), (4.202, 'rack'), (4.419, 'pixbar'),
    (4.502, 'slices'), (4.536, 'oval'), (5.002, 'blur4'), (5.036, 'pix4'), (5.069, 'dark4'), (5.102, 'face'),
    (5.436, 'blur5'), (5.469, 'inset'), (5.736, 'pix5'), (5.769, 'dark5'), (5.802, 'collage2'),
    (6.169, 'pinkwhip'), (6.186, 'bigtext'), (6.702, 'black'),
]


def _tup(x):
    """JSON lists -> tuples (shot specs are lru_cache keys)."""
    return tuple(_tup(v) for v in x) if isinstance(x, list) else x


def _load():
    cast = json.load(open(os.path.join(JOB, 'cast.json')))
    tx = json.load(open(os.path.join(JOB, 'texts.json')))
    for alias, path in cast['sources'].items():
        E.register(alias, path if os.path.isabs(path) else os.path.join(JOB, path))
    T = texts(tx.get('text') or '')
    out = {}
    for key, alt in (('A', 0), ('B', 1)):
        C = {k: _tup(v) for k, v in cast['phrases'][key].items()}
        C.update(alt=alt, words=T['words'], name=T['name'], oval_word=T['oval_word'],
                 big=T['big'] if key == 'A' else '')
        for which in ('card1', 'card2'):             # crop + card texts -> the template's card tuple
            C[which] = C[which + '_crop'] + (T['card_name'], '', '', '', '')
        C['stickers'] = _tup(C.get('stickers', []))
        out[key] = C
    return out, T


def two_lines(t):
    """Titles over ~10 characters break at the space nearest the middle (the template's 'Princess / Glow Up')."""
    if len(t) <= 10 or ' ' not in t:
        return t
    mid = len(t) / 2
    i = min((i for i, c in enumerate(t) if c == ' '), key=lambda i: abs(i - mid))
    return t[:i] + '\n' + t[i + 1:]


def texts(t):
    """The prompt box text -> every lettering beat. '' everywhere = no lettering."""
    t = ' '.join(t.split())
    ws = t.split(' ') if t else []
    if len(ws) >= 3:            # word by word on the close-up: w1, 'w1 w2', then the rest as the punchline
        words = (ws[0], ws[1], ' '.join(ws[2:]))
    elif len(ws) == 2:
        words = (ws[0], '', ws[1])
    else:
        words = (t, '', t)
    return dict(title=two_lines(t), footer=t.lower(), card_bg=t, words=words, name=t, oval_word=t,
                big=two_lines(t), card_name=t)


CAST, TX = _load()

# ----------------------------------------------------------------------------- footage helpers
def foot(img):
    """Footage grade (camera pixels only, not graphics)."""
    return E.grade(img, pink=0.07, contrast=1.07, sat=1.06, lift=0.02)


def live(spec, u, zoom_mul=1.0, rot=0.0):
    alias, t_in, cx, cy, zoom = spec[:5]
    return foot(E.shot(alias, t_in + u, cx, cy, zoom * zoom_mul, rot))


def crop(spec, u=0.0):
    alias, t_in, cx, cy, w, h = spec[:6]
    return foot(E.crop_rgb(alias, t_in + u, cx, cy, w, h))



# ----------------------------------------------------------------------------- Y2K lettering
NEON_LIGHT = (('core', (1.0, 0.40, 0.74)), ('glow', (1.0, 0.62, 0.86)), ('halo', (1.0, 0.82, 0.93)), ('strength', 0.8))
CRAYON_SCALE = 0.72          # Twinkle Star reads bigger than Mea Culpa at the same point size
WHITE_T = (1.0, 0.97, 0.99)
INK_LIGHT = (1.0, 0.95, 0.98)   # pencil ornaments drawn in white on the dark glitter board


def style_for(C, k):
    """k-th text beat of a phrase: neon script and crayon alternate, phrase B starts on the other one."""
    return ('neon', 'crayon')[(k + C['alt']) % 2]


@functools.lru_cache(maxsize=160)
def lettering(style, text, size, stars=0, seed=0, color=None, light=False, outline=False):
    if not text or not text.strip():
        return None             # no prompt-box text: put_t draws nothing
    if style == 'neon':
        kw = dict(NEON_LIGHT) if light else {}
        return Y.neon_text(text, int(size), stars=stars, seed=seed, **kw)
    col = np.array(color, np.float32) if color is not None else Y.HOT
    asset = Y.crayon_text(text.lower(), int(size * CRAYON_SCALE), color=col, stars=stars, dots=stars, seed=seed)
    return Y.outlined(asset, px=max(4, int(size * 0.045))) if outline else asset


def put_t(img, asset, x, y, anchor='mm', scale=1.0, rot=0.0, opacity=1.0, shadow=0.0, fit=True):
    if asset is None:
        return img
    rgb, a = asset
    h, w = a.shape
    if fit:     # longer prompt-box texts shrink to stay inside the frame (template texts already fit)
        room = W * 0.95 - x if anchor[0] == 'l' else W * 0.96
        if w * scale > room > 0:
            scale = room / w
    ax = {'l': 0, 'm': w / 2, 'r': w}[anchor[0]]
    ay = {'t': 0, 'm': h / 2, 'b': h}[anchor[1]]
    if shadow > 0:
        E.place(img, np.zeros_like(rgb), E.gauss(a, max(2.0, h * 0.025)) * shadow, ax - 4 / scale, ay - 6 / scale, scale,
                rot, x, y, opacity)
    return E.place(img, rgb, a, ax, ay, scale, rot, x, y, opacity)


def put_band(img, top, bh, seed=0):
    """Pink star band where the template had a flat pink bar."""
    bh = int(bh)
    if bh <= 0:
        return img
    b = Y.star_band(W, bh, seed=seed)
    y0, y1 = max(0, int(top)), min(H, int(top) + bh)
    if y1 > y0:
        img[y0:y1] = b[y0 - int(top):y1 - int(top)]
    return img


@functools.lru_cache(maxsize=4)
def dot_strip(n, horizontal=True):
    """Row of pink dots (separators in the intro bars)."""
    L = W if horizontal else H
    a = np.zeros((7, L), np.float32)
    for x in range(4, L, 11):
        cv2.circle(a, (x, 3), 3 if (x // 11) % 2 else 2, 1.0, -1, cv2.LINE_AA)
    rgb = np.empty((7, L, 3), np.float32)
    rgb[:] = (1.0, 0.55, 0.82)
    return (rgb, a) if horizontal else (rgb.transpose(1, 0, 2).copy(), a.T.copy())


def harden(a, lo=0.38, hi=0.62):
    return np.clip((a - lo) / (hi - lo), 0, 1).astype(np.float32)


@functools.lru_cache(maxsize=8)
def _cut(alias, k, box, excl, kind):
    s = E.src(alias)
    rgb, a = E.cut_smooth(alias, (k + 0.5) / s.fps, box, kind)
    if excl:
        a = a.copy()
        for item in excl:
            if len(item) == 4 and not isinstance(item[0], tuple):
                x0, y0, x1, y1 = item
                a[y0:y1, x0:x1] = 0
            else:   # polygon given as a tuple of (x, y) points
                m = np.zeros(a.shape, np.uint8)
                cv2.fillPoly(m, [np.array(item, np.int32)], 1, lineType=cv2.LINE_AA)
                a[m > 0] = 0
    return foot(rgb), harden(a)


def cut_at(alias, t, box, excl=(), kind='person'):
    return _cut(alias, E.src(alias).index(t), box, tuple(excl), kind)


# ----------------------------------------------------------------------------- stickers
@functools.lru_cache(maxsize=16)
def vec_sticker(kind, size=150):
    w = h = int(size * 2.4)
    cx, cy = w / 2, h / 2
    if kind == 'heart':
        m = E.poly_mask(E.heart_points(cx, cy + size * 0.08, size * 0.9), (w, h))
        col = (1.0, 0.42, 0.72)
    elif kind == 'sparkle':
        m = E.poly_mask(E.star_points(cx, cy, size * 0.95, size * 0.22, n=4), (w, h))
        col = (1.0, 0.86, 0.95)
    elif kind == 'star':
        m = E.poly_mask(E.star_points(cx, cy, size * 0.95, size * 0.42, n=5), (w, h))
        col = (1.0, 0.74, 0.88)
    else:  # bow
        s = size
        lobes = [[(cx, cy), (cx - s, cy - s * 0.65), (cx - s * 1.05, cy + s * 0.6)],
                 [(cx, cy), (cx + s, cy - s * 0.65), (cx + s * 1.05, cy + s * 0.6)]]
        m = np.maximum(E.poly_mask(lobes[0], (w, h)), E.poly_mask(lobes[1], (w, h)))
        m = np.maximum(m, E.ellipse_mask(cx, cy, s * 0.22, s * 0.26, (w, h)))
        tails = [(cx - s * 0.1, cy), (cx - s * 0.55, cy + s * 1.0), (cx - s * 0.25, cy + s * 1.05), (cx, cy + s * 0.2),
                 (cx + s * 0.25, cy + s * 1.05), (cx + s * 0.55, cy + s * 1.0), (cx + s * 0.1, cy)]
        m = np.maximum(m, E.poly_mask(tails, (w, h)))
        col = (1.0, 0.55, 0.78)
    rgb = np.empty((h, w, 3), np.float32)
    rgb[:] = col
    rgb = rgb * (0.80 + 0.20 * E.gauss(m, size * 0.12)[..., None])
    return E.sticker(rgb, m, stroke=max(7, size // 14))


@functools.lru_cache(maxsize=32)
def obj_sticker(alias, t, box):
    rgb, a = E.cut(alias, t, box, 'isnet')
    a = harden(a)
    x0, y0, x1, y1 = E.bbox(a, pad=24)
    return E.sticker(foot(rgb[y0:y1, x0:x1].copy()), a[y0:y1, x0:x1].copy(), stroke=10)


def draw_stickers(dst, stickers, u):
    for i, st in enumerate(stickers):
        if st[0] == 'obj':
            _, alias, t, box, scale, x, y, rot = st
            rgb, a = obj_sticker(alias, t, box)
        else:
            kind, scale, x, y, rot = st
            rgb, a = vec_sticker(kind)
        bob = math.sin(u * 7 + i * 1.7) * 5
        E.place_sticker(dst, rgb, a, rgb.shape[1] / 2, rgb.shape[0] / 2, scale, rot + math.sin(u * 5 + i) * 3,
                        x, y + bob, shadow=0.25)
    return dst


# ----------------------------------------------------------------------------- cached backgrounds
@functools.lru_cache(maxsize=8)
def oval_asset(rx, ry):
    return Y.mirror_frame(rx, ry)


@functools.lru_cache(maxsize=8)
def pixels_bg(seed):
    return Y.halftone_bg(seed)


@functools.lru_cache(maxsize=8)
def glitter_bg(seed):
    return E.confetti_tris(E.bg_glitter(seed), seed=seed + 5, n=9)


@functools.lru_cache(maxsize=8)
def card_asset(key, which):
    alias, t, cx, cy, w, h, name, stat, tag, ability, desc = CAST[key][which]
    photo = foot(E.crop_rgb(alias, t, cx, cy, w, h))
    theme = (1.0, 0.42, 0.70) if which == 'card2' else (0.55, 0.62, 1.0)   # card2 = phrase hero (pink)
    return Y.card(photo, name.lower(), stat.lower(), tag, ability, desc.lower(), TX['footer'], theme=theme,
                  seed=3 if which == 'card2' else 0)


@functools.lru_cache(maxsize=4)
def card_bg(seed):
    bg = Y.halftone_bg(seed + 11, base=(1.0, 0.88, 0.94), dot=(1.0, 0.72, 0.87)).copy()
    put_t(bg, lettering('neon', TX['card_bg'], 300, light=True), W * 0.5, H * 0.52, rot=-8, opacity=0.5)
    return bg


@functools.lru_cache(maxsize=4)
def dark_board(seed):
    img = canvas((0.06, 0.02, 0.05))
    rng = np.random.default_rng(seed)
    tex = cv2.resize(rng.random((40, 40)).astype(np.float32), (W, H), interpolation=cv2.INTER_CUBIC)
    img *= (0.6 + 0.8 * tex)[..., None]
    for _ in range(14):   # faint vertical scratches
        x = int(rng.uniform(0, W))
        img[:, x:x + 2] *= 1.6
    img[int(H * 0.497):int(H * 0.503)] = np.array([0.75, 0.25, 0.55], np.float32)
    return np.clip(img, 0, 1)

# ----------------------------------------------------------------------------- slots
def r_drop(C, u, d):
    alias, t_in, cx, cy, zoom, box = C['drop']
    k = u / d
    z = zoom * (1 + 0.04 * k)
    base = foot(E.shot(alias, t_in + u, cx, cy, z)) * 0.80
    rgb, a = cut_at(alias, t_in + u, box)
    M = E.affine(cx, cy, E.fit_scale(E.src(alias).h) * z, 0, W / 2, H / 2)
    wa = E.warp(a, M)
    wr = E.warp(rgb, M)
    ys, xs = np.where(wa > 0.5)
    sx, sy = (xs.mean(), ys.mean() - 60) if len(xs) else (W / 2, H / 2)
    img = base
    if k < 0.85:   # big pink star behind the subject, shrinking into the outline
        sc = lerp(1.25, 0.92, ease_out(k / 0.4)) if k < 0.4 else lerp(0.92, 0.0, smooth((k - 0.4) / 0.45))
        star = E.poly_mask(E.star_points(sx, sy, W * 0.62 * sc, W * 0.62 * sc * 0.36, n=6, rot=8 * k))
        if k < 0.15:
            star = E.gauss(star, 10)
        E.over(img, np.broadcast_to(PINK, img.shape).copy(), star * 0.95)
    if k > 0.3:
        E.over(img, np.broadcast_to(PINK, img.shape).copy(), E.grow(wa, 14 * smooth((k - 0.3) / 0.3)))
    E.over(img, wr, wa)
    if u < 3 * F:
        img = E.zoom_blur(img, 0.10 * (1 - u / (3 * F)), sx, sy)
    return img


def r_poster(C, u, d=1.0, text=True):
    alias, t_in, cx, cy, z0, z1 = C['poster']
    img = foot(E.shot(alias, t_in + u, cx, cy, lerp(z0, z1, clamp01(u / 0.6))))
    if u < 0.10:
        img = E.gauss(img, 14 * (1 - u / 0.10))
    img = E.bloom(E.pink_edges(img, 0.95, seed=3), 0.75, 0.25, 14)
    if not text:
        return img
    st = style_for(C, 0)
    y = H * 0.57
    s = lerp(1.05, 1.0, ease_out(u / 0.2))
    put_t(img, lettering(st, TX['title'], 175, stars=3, seed=1, outline=True), W / 2, y, scale=s,
          shadow=0.45 if st == 'crayon' else 0.0)
    if u < 2 * F:
        m = E.poly_mask(E.star_points(W * 0.45, H * 0.62, W * 0.55, W * 0.2, n=6))
        E.over(img, np.broadcast_to(PINK, img.shape).copy(), m * 0.85)
    return img


@functools.lru_cache(maxsize=4)
def dotted_title(style):
    if style == 'neon':
        m = Y.script_mask(TX['title'], Y._pil_font(Y.NEON_FONT, 230), stroke=8, line_gap=0.8, indent=0.35)
    else:
        m = Y.crayon_letters(TX['title'].lower(), int(230 * CRAYON_SCALE), seed=3, thick=0.03)
    m = np.pad(m, 20)
    return Y._crop_alpha(*Y.dotted(m, cell=9, color=(1.0, 0.62, 0.86), shadow=(0.55, 0.1, 0.35)))


def r_dots(C, u, d):
    img = Y.dotify(r_poster(C, 0.12, text=False), 22) * 0.5
    if not TX['title']:
        return img
    rgb, a = dotted_title(style_for(C, 0))
    sc = min(1.0, W * 0.96 / a.shape[1])
    E.over(img, np.broadcast_to(np.array([1.0, 0.55, 0.82], np.float32), img.shape).copy(),
           E.warp(E.gauss(a, 6), E.affine(a.shape[1] / 2, a.shape[0] / 2, sc, 0, W / 2, H / 2)) * 0.5)
    return put_t(img, (rgb, a), W / 2, H / 2, scale=sc, fit=False)


def r_photo(C, u, d=0.25, seed=11):
    bg = pixels_bg(seed + int(u * 30) % 2).copy()
    rgb, a = Y.ornate_photo(crop(C['photo'], u), 'swirl', border=12)
    k = clamp01(u / max(d, 1e-3))
    sc = lerp(0.98, 1.04, k) * min(W * 0.84 / rgb.shape[1], H * 0.97 / rgb.shape[0])
    x = lerp(W * 0.20, W * 0.53, (u + F) / (3 * F)) if u < 2 * F else W * 0.53
    E.place(bg, np.zeros_like(rgb), E.gauss(a, 10) * 0.30, rgb.shape[1] / 2, rgb.shape[0] / 2, sc, lerp(-6, -3.5, k),
            x + 10, H * 0.5 + 14)
    return E.place(bg, rgb, a, rgb.shape[1] / 2, rgb.shape[0] / 2, sc, lerp(-6, -3.5, k), x, H * 0.5)


def r_collage(C, u, d=0.6, seed=21):
    img = pixels_bg(seed).copy() * 0.94 + np.array([1.0, 0.86, 0.93], np.float32) * 0.06
    rgb, a = Y.ornate_photo(crop(C['col_frame'], u), 'dots', border=8)
    E.place_sticker(img, rgb, a, rgb.shape[1] / 2, rgb.shape[0] / 2,
                    min(W * 0.56 / rgb.shape[1], H * 0.90 / rgb.shape[0]), 5, W * 0.29, H * 0.50)
    alias, t_in, box, y_cut, excl = C['col_cut']
    crgb, ca = cut_at(alias, t_in, box, excl)          # frozen frame = clean sticker, no mask flicker
    srgb, sa = E.sticker(crgb, ca, stroke=9)
    x0, y0, x1, y1 = E.bbox(ca)
    sc = (H * 0.86) / max(1, (y_cut - y0))
    bob = math.sin(u * 6) * 4
    E.place_sticker(img, srgb, sa, (x0 + x1) / 2, y_cut, sc * lerp(1.03, 1.0, ease_out(u / 0.15)), 0,
                    W * 0.70, H + 14 + bob)
    draw_stickers(img, C['stickers'], u)
    if u < 3 * F:
        img = E.zoom_blur(img, 0.06 * (1 - u / (3 * F)))
    return img


def bokeh_shot(alias, t, cx, cy, zoom, box, sigma=13):
    """Portrait-mode look: subject (person matte, temporally smoothed) sharp over a blurred frame."""
    rgb, a = cut_at(alias, t, box)
    s = E.src(alias)
    M = E.affine(cx, cy, E.fit_scale(s.h) * zoom, 0, W / 2, H / 2)
    sharp = E.warp(rgb, M, interp=cv2.INTER_CUBIC)
    wa = E.gauss(E.warp(a, M), 1.5)
    soft = E.gauss(sharp, sigma) * 0.92
    return soft * (1 - wa[..., None]) + sharp * wa[..., None]


def r_square(C, u, full_k=0.0):
    alias, t_in, cx, cy, zoom = C['square']
    bg = E.bg_sunburst(angle=u * 25)
    if C.get('square_bokeh'):
        full = bokeh_shot(alias, t_in + u, cx, cy, zoom, C['square_bokeh'])
    else:
        full = foot(E.shot(alias, t_in + u, cx, cy, zoom))
    if full_k >= 1:
        return full
    rgb, a = Y.ornate_photo(full, 'dots', border=10)
    rot = lerp(0, -5, min(1, full_k * 3)) if full_k > 0 else math.sin(u * 40) * 1.2
    s = lerp(0.34, 1.0, full_k) * W / (W + 20)
    E.place(bg, np.zeros_like(rgb), E.gauss(a, 12) * 0.3, rgb.shape[1] / 2, rgb.shape[0] / 2, s, rot, W / 2 + 8, H / 2 + 12)
    return E.place(bg, rgb, a, rgb.shape[1] / 2, rgb.shape[0] / 2, s, rot, W / 2, H / 2)


def r_card(C, u, d, which):
    img = card_bg(0).copy()
    k = clamp01(u / max(d, 1e-3))
    if which == 'card2':
        r1, a1 = card_asset(C['_key'], 'card1')
        E.place_sticker(img, r1, a1, r1.shape[1] / 2, r1.shape[0] / 2, 1.0, 7, W * 0.92, H * 0.55)
        rgb, a = card_asset(C['_key'], 'card2')
        rot = lerp(-14, -6, ease_out(k / 0.35)) if k < 0.35 else lerp(-6, -5, (k - 0.35) / 0.65)
        sc, x = lerp(1.10, 1.0, ease_out(k / 0.3)) * 1.02, W * 0.42
    else:
        rgb, a = card_asset(C['_key'], 'card1')
        rot = lerp(-26, -9, ease_out(k / 0.35)) if k < 0.35 else lerp(-9, -8, (k - 0.35) / 0.65)
        sc, x = lerp(1.16, 1.05, ease_out(k / 0.3)), W * 0.50
    E.place_sticker(img, rgb, a, rgb.shape[1] / 2, rgb.shape[0] / 2, sc, rot, x, H * 0.52)
    if u < 2 * F:
        img = E.flash(E.dir_blur(img, 160, 40), 0.35)
    return img


def r_bars(C, u, d):
    """Card -> close-up: the close-up wipes up from the bottom behind a pink bar."""
    top = r_card(C, 0.33, 0.33, 'card2')
    bot = live(C['text_cu'], 0) * 0.55
    k = ease_out(u / d)
    y = int(H * lerp(0.62, 0.0, k))
    img = top.copy()
    img[y:] = bot[y:]
    bh = int(H * 0.08)
    return put_band(img, y - bh, bh)


def r_textcu(C, u, d):
    w1, w2, w3 = C['words']
    st = style_for(C, 1)
    size = 140
    x, y = W * 0.07, H * 0.84
    if u < 2 * F:   # dark frame, small first word
        img = live(C['text_cu'], u) * 0.18
        put_t(img, lettering(st, w1, 84, color=WHITE_T), x, y, 'lm')
        return img
    img = live(C['text_cu'], u)
    if u < 5 * F:
        put_t(img, lettering(st, w1, size, color=WHITE_T), x, y, 'lm', shadow=0.5)
    elif u < 12 * F:
        put_t(img, lettering(st, f'{w1} {w2}'.strip(), size, color=WHITE_T), x, y, 'lm', shadow=0.5)
        bh = int(H * 0.11)
        put_band(img, int(lerp(0, -bh, ease_out((u - 5 * F) / (4 * F)))), bh)
    elif u < 16 * F:
        put_t(img, lettering(st, ' '.join(w3) if st == 'crayon' and len(w3) <= 12 else w3, 92, color=WHITE_T),
              W * 0.12, y, 'lm',
              shadow=0.5)
    else:
        put_t(img, lettering(st, w3, size * 1.12, stars=2, seed=5, color=WHITE_T), x, y, 'lm', shadow=0.5)
    return img


def r_nametype(C, u, d):
    alias, t, cx, cy, zoom = C['name_bg']
    img = E.gauss(foot(E.shot(alias, t, cx, cy, zoom)), 6) * 0.20
    if u < 2 * F:
        put_band(img, 0, int(H * 0.15), seed=1)
        put_band(img, int(H * 0.92), H - int(H * 0.92), seed=2)
        return img
    st = style_for(C, 2)
    name = C['name']
    n = min(len(name), 2 + int((u - 2 * F) * FPS * 1.5))
    txt = ' '.join(name[:n]) if st == 'crayon' and len(name) <= 12 else name[:n]
    put_t(img, lettering(st, txt, 100, color=WHITE_T), W / 2, H * 0.80)
    return img


def r_namebold(C, u, d):
    alias, t, cx, cy, zoom = C['name_bg']
    img = E.gauss(foot(E.shot(alias, t + u, cx, cy, zoom * 1.04)), 7)
    put_band(img, 0, int(H * 0.15), seed=1)
    put_t(img, lettering(style_for(C, 3), C['name'], 200, stars=3, seed=6, outline=True), W / 2, H * 0.78, shadow=0.45)
    return img


def r_close(C, u, d):
    img = live(C['close1'], u, zoom_mul=1 + 0.03 * u / max(d, 1e-3))
    if u < 0.10:
        bh = int(H * 0.12)
        put_band(img, int(lerp(0, -bh, ease_out(u / 0.10))), bh, seed=3)
    return img


def r_rack(C, u, d=0.22):
    img = live(C['rack'], u, zoom_mul=1 + 0.06 * clamp01(u / d))
    return E.gauss(img, 16 * (1 - smooth(u / (0.7 * d))))


@functools.lru_cache(maxsize=8)
def word_asset(style, word):
    return lettering(style, word, 150, stars=2, seed=8, color=WHITE_T)


def r_oval(C, u, d=0.47):
    alias, t, cx, cy, zoom = C['oval_bg']
    img = E.gauss(foot(E.shot(alias, t + u, cx, cy, zoom)), 9) * 0.62
    rx, ry = 250, 347
    inside = E.ellipse_mask(W / 2, H / 2, rx, ry)
    img = img * (1 - inside[..., None]) + np.minimum(1, img * 1.45 + 0.08) * inside[..., None]
    E.over(img, np.broadcast_to(CREAM, img.shape).copy(),
           E.poly_mask(E.heart_points(W * 0.61, H / 2 + ry * 0.33, rx * 0.74)) * inside * 0.97)
    a_, t_in, box = C['oval_cut']
    crgb, ca = cut_at(a_, t_in + u, box)
    x0, y0, x1, y1 = E.bbox(ca)
    sc = (2 * ry * 1.02) / max(1, (y1 - y0))
    M = E.affine((x0 + x1) / 2, y0, sc, 0, W / 2, H / 2 - ry + 26)
    E.over(img, E.warp(crgb, M, interp=cv2.INTER_AREA), E.warp(ca, M, interp=cv2.INTER_AREA) * inside)
    frgb, fa, (fx, fy) = oval_asset(rx, ry)
    E.place(img, frgb, fa, fx, fy, 1.0, 0, W / 2, H / 2)
    k = clamp01(u / d)
    st = style_for(C, 4)
    if not C['oval_word']:
        return img
    wr, wa = word_asset(st, C['oval_word'])
    room = W * 0.95 - W * 0.20
    if wa.shape[1] * 1.25 > room:   # long prompt-box text: shrink the word (and its swirl) to fit
        k2 = room / (wa.shape[1] * 1.25)
        wr = cv2.resize(wr, (int(wr.shape[1] * k2), int(wr.shape[0] * k2)), interpolation=cv2.INTER_AREA)
        wa = cv2.resize(wa, (wr.shape[1], wr.shape[0]), interpolation=cv2.INTER_AREA)
    f = clamp01((k - 0.12) / (0.08 * len(C['oval_word']) + 0.05))
    if f > 0:
        h, w = wa.shape
        xs = np.arange(w, dtype=np.float32)
        reveal = np.clip((f * (w + 60) - xs) / 60, 0, 1)[None, :]
        s = lerp(1.25, 1.0, ease_out(clamp01((k - 0.12) / 0.15)))
        x0w, yw = W * 0.20, H * 0.63
        ur, ua = Y.divider('swirl', int(w * 1.05), int(w * 0.22), seed=2, ink=(1.0, 1.0, 1.0))
        uw = ua.shape[1]
        ureveal = np.clip((f * (uw + 60) - np.arange(uw, dtype=np.float32)) / 60, 0, 1)[None, :]
        E.place(img, ur, ua * ureveal, 0, ua.shape[0] / 2, s, 0, x0w - 0.03 * w * s, yw + h * 0.42 * s)
        put_t(img, (wr, wa * reveal), x0w, yw, 'lm', scale=s, shadow=0.5, fit=False)
    return img


def r_board(C, u, d, stage, seed=31):
    """Glitter board: 0 = tilted face photo, 1 = + inset sliding in, 2 = face collage (all in Y2K frames)."""
    img = glitter_bg(seed + (stage > 1)).copy()
    if stage < 2:
        rgb, a = Y.ornate_photo(crop(C['face'], u), 'notes', border=8, ink=INK_LIGHT)
        sc = lerp(1.0, 1.05, clamp01(u / max(d, 1e-3))) * min(W * 0.86 / rgb.shape[1], H * 0.92 / rgb.shape[0])
        E.place_sticker(img, rgb, a, rgb.shape[1] / 2, rgb.shape[0] / 2, sc, 8, W * 0.47, H * 0.55)
        if stage == 1:
            r2, a2 = Y.ornate_photo(crop(C['inset'], u), 'swirl', border=8, border_col=(1.0, 0.62, 0.85), ink=INK_LIGHT)
            E.place_sticker(img, r2, a2, r2.shape[1] / 2, r2.shape[0] / 2, W * 0.56 / r2.shape[1], -7,
                            lerp(W * 1.2, W * 0.72, ease_out(u / 0.08)), H * 0.25)
        return img
    for spec, style, wf, rot, x, y, col in ((C['face2'], 'dots', 0.66, 4, 0.52, 0.50, WHITE),
                                            (C['face3'], 'swirl', 0.40, -7, 0.22, 0.75, WHITE),
                                            (C['inset2'], 'wings', 0.46, 7, 0.76, 0.24, (1.0, 0.62, 0.85))):
        r, a = Y.ornate_photo(crop(spec, u), style, border=8, border_col=col, ink=INK_LIGHT)
        E.place_sticker(img, r, a, r.shape[1] / 2, r.shape[0] / 2, W * wf / r.shape[1], rot, W * x, H * y)
    return img


def r_bigtext(C, u, d):
    """Big text beat, styles alternating state by state: huge -> gap -> centre + echoes -> small -> huge -> dim."""
    text = C['big']
    if not text:    # no prompt-box text: the glitter-board collage holds (frozen, like the whip into it) and dims
        img = r_board(C, 0.37, 1, 2)
        return img * lerp(1.0, 0.35, smooth((u - 25 * F) / (6 * F))) if u >= 25 * F else img
    img = dark_board(5).copy()
    s1, s2 = style_for(C, 5), style_for(C, 6)
    if u < 3 * F:
        put_t(img, lettering(s1, text, 400, color=(1.0, 0.43, 0.78)), W * 0.40, H * 0.50)
    elif 6 * F <= u < 11 * F:
        asset = lettering(s2, text, 210, color=WHITE_T)
        w = min(asset[1].shape[1], W * 0.96)
        sc = w / asset[1].shape[1]
        for dx in (-w * 0.95, w * 0.95):
            put_t(img, asset, W / 2 + dx, H / 2, scale=sc, opacity=0.32, fit=False)
        put_t(img, asset, W / 2, H / 2)
    elif 13 * F <= u < 17 * F:
        put_t(img, lettering(s1, text, 110, color=WHITE_T), W / 2, H / 2)
    elif 19 * F <= u < 25 * F:
        put_t(img, lettering(s2, text, 430, stars=3, seed=9, color=(1.0, 0.43, 0.78)), W * 0.62, H * 0.52)
    elif u >= 25 * F:
        k = smooth((u - 25 * F) / (6 * F))
        img = img * lerp(1.0, 0.35, k)
        put_t(img, lettering(s1, text, 110, color=(0.62, 0.55, 0.6)), W / 2, H / 2, opacity=1 - k)
    return img


# ----------------------------------------------------------------------------- phrase assembly
def _pixbar(C):
    img = Y.dotify(r_rack(C, 0.22), 30)
    y0, y1 = int(H * 0.45), int(H * 0.53)
    band = Y.star_band(int(W * 0.34), y1 - y0, seed=4)
    img[y0:y1, int(W * 0.18):int(W * 0.18) + band.shape[1]] = band
    return img


def build_slots(C):
    sq_end = 0.15
    cu_end = sq_end + 0.533
    c1d, ovd, fd, i5 = 0.233, 0.466, 0.334, 0.267

    def closeup(t, u, d):
        grow = 0.07
        return r_square(C, sq_end + u, full_k=ease_out(u / grow) if u < grow else 1.0)

    def starflash(t, u, d):
        k = u / d
        img = canvas(WHITE) * (E.gauss(r_square(C, cu_end, 1.0), 18) * 0.25 + 0.75)
        m = E.poly_mask(E.star_points(W / 2, H / 2, W * lerp(0.25, 0.6, k), W * lerp(0.08, 0.2, k), n=6, rot=20 * k))
        return E.over(img, np.broadcast_to(np.array([1.0, 0.62, 0.86], np.float32), img.shape).copy(), m * 0.9)

    return {
        'drop': lambda t, u, d: r_drop(C, u, d),
        'dots': lambda t, u, d: r_dots(C, u, d),
        'poster': lambda t, u, d: r_poster(C, u, d),
        'dip': lambda t, u, d: r_poster(C, 0.567) * 0.12,
        'whip': lambda t, u, d: E.flash(E.dir_blur(r_photo(C, 0), lerp(340, 80, u / d), 0), lerp(0.8, 0.35, u / d)),
        'photo': lambda t, u, d: r_photo(C, u, d),
        'pix': lambda t, u, d: Y.dotify(r_photo(C, 0.25), int(lerp(26, 56, u / d))),
        'darkblur': lambda t, u, d: E.gauss(r_collage(C, 0), 16) * 0.3,
        'collage': lambda t, u, d: r_collage(C, u, d),
        'whipW': lambda t, u, d: E.flash(E.dir_blur(r_collage(C, 0.63), 300, 0), lerp(0.5, 0.9, u / d)),
        'square': lambda t, u, d: r_square(C, u),
        'closeup': closeup,
        'blurC': lambda t, u, d: E.dir_blur(r_square(C, cu_end, 1.0), 260, 30),
        'starflash': starflash,
        'card1': lambda t, u, d: r_card(C, u, d, 'card1'),
        'mesh': lambda t, u, d: Y.dotify(r_card(C, c1d, c1d, 'card1'), 14, bg=(0.25, 0.08, 0.18)),
        'whip2': lambda t, u, d: E.flash(E.dir_blur(r_card(C, 0.0, 0.32, 'card2'), lerp(260, 40, u / d), 0),
                                         lerp(0.2, 0.8, u / d), (1.0, 0.75, 0.9)),
        'card2': lambda t, u, d: r_card(C, u, d, 'card2'),
        'bars': lambda t, u, d: r_bars(C, u, d),
        'textcu': lambda t, u, d: r_textcu(C, u, d),
        'nametype': lambda t, u, d: r_nametype(C, u, d),
        'namebold': lambda t, u, d: r_namebold(C, u, d),
        'close1': lambda t, u, d: r_close(C, u, d),
        'whip3': lambda t, u, d: E.dir_blur(r_rack(C, 0), lerp(380, 120, u / d), 0),
        'rack': lambda t, u, d: r_rack(C, u, d),
        'pixbar': lambda t, u, d: _pixbar(C),
        'slices': lambda t, u, d: E.glitch_slices(r_oval(C, 0), [-70, 50, -30]) * 0.8,
        'oval': lambda t, u, d: r_oval(C, u, d),
        'blur4': lambda t, u, d: E.dir_blur(r_oval(C, ovd), 220, 0),
        'pix4': lambda t, u, d: Y.dotify(r_board(C, 0, fd, 0), 28),
        'dark4': lambda t, u, d: r_board(C, 0, fd, 0) * 0.25,
        'face': lambda t, u, d: r_board(C, u, d, 0),
        'blur5': lambda t, u, d: E.dir_blur(r_board(C, fd, fd, 0), 200, 0),
        'inset': lambda t, u, d: r_board(C, u, d, 1),
        'pix5': lambda t, u, d: Y.dotify(r_board(C, i5, i5, 1), 26),
        'dark5': lambda t, u, d: r_board(C, 0, 1, 2) * 0.25,
        'collage2': lambda t, u, d: r_board(C, u, d, 2),
        'pinkwhip': lambda t, u, d: E.flash(E.dir_blur(r_board(C, 0.37, 1, 2), 300, 0), 0.55, PINK),
        'bigtext': lambda t, u, d: r_bigtext(C, u, d),
        'black': lambda t, u, d: canvas((0, 0, 0)),
    }


def phrase(D, key, last=False):
    C = dict(CAST[key])
    C['_key'] = key
    slots = build_slots(C)
    starts = [(D + off, name) for off, name in SCHED]
    segs = []
    for i, (t0, name) in enumerate(starts):
        t1 = starts[i + 1][0] if i + 1 < len(starts) else D + 7.0
        if last and name == 'collage2':
            def tail(t, u, d, fn=slots['collage2']):
                return fn(t, u, d) * (1 - smooth((t - FADE0) / (FADE1 - FADE0)))
            segs.append(Seg(t0, FADE1 + 1, tail, 'collage2_fade'))
            break
        segs.append(Seg(t0, t1, slots[name], name))
    return segs


def timeline():
    a = phrase(D1, 'A')
    b = phrase(D2, 'B', last=True)
    a[-1].t1 = b[0].t0      # phrase A's black runs until drop 2
    for s in a + b:
        s.key = 'A' if s in a else 'B'
    return a + b


def post(img, t, fi):
    return E.grain(img, 0.022, seed=fi)


def frame(segs, k):
    """Output frame k (0..NF-1) as uint8 RGB."""
    fi = N0 + k
    return E.to_u8(E.frame_at(fi / FPS, segs, [], post, fi))


# slots whose renderers call cut_at (person mattes): warm computes their masks once, before parallel chunks
CUT_SLOTS = ('drop', 'collage', 'square', 'closeup', 'oval')


def warm_frames(segs):
    ks = []
    for s in segs:
        if s.name in CUT_SLOTS:
            ks += [k for k in range(NF) if s.t0 <= (N0 + k) / FPS < s.t1]
    return ks


def warm_cuts():
    """Every cut_at() call the cut-out slots make, at source-frame resolution (masks only, no compositing):
    drop (live, 0.2 s), collage sticker (frozen), square portrait mode (live, square + closeup = 0.68 s), oval (live,
    0.47 s). Same arguments as the slot code, so the disk cache keys match what render needs."""
    calls = []

    def live(alias, t0, dur, box, excl=()):
        fps = E.src(alias).fps
        n = int(math.ceil(dur * fps)) + 1
        calls.extend((alias, t0 + j / fps, box, excl) for j in range(n))

    for key in ('A', 'B'):
        C = CAST[key]
        alias, t_in, _, _, _, box = C['drop']
        live(alias, t_in, 0.22, box)
        alias, t_in, box, _, excl = C['col_cut']
        calls.append((alias, t_in, box, excl))
        if C.get('square_bokeh'):
            live(C['square'][0], C['square'][1], 0.70, C['square_bokeh'])
        alias, t_in, box = C['oval_cut']
        live(alias, t_in, 0.48, box)
    return calls


def chunk(segs, out, k0, k1):
    cmd = ['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
           '-i', '-', *json.loads(os.environ.get('GLOW_CHUNK_VENC') or '["-c:v", "libx264", "-crf", "12"]'), out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t_start = time.time()
    for k in range(k0, k1):
        p.stdin.write(frame(segs, k).tobytes())
        if (k - k0) % 60 == 0:
            print(f'  frame {k - k0}/{k1 - k0} {time.time() - t_start:6.1f}s', flush=True)
    p.stdin.close()
    if p.wait():
        sys.exit('ffmpeg failed on ' + out)


def main():
    segs = timeline()
    mode = sys.argv[2]
    if mode == 'segs':
        for s in segs:
            print(f'{s.key} {s.name:14s} {(s.t0 - T0):7.3f} {(min(s.t1, FADE1) - T0):7.3f}')
    elif mode == 'stills':
        from glow.media import contact_sheet
        frs, labels = [], []
        for arg in sys.argv[4:]:
            t, _, lb = arg.partition(':')
            k = min(NF - 1, max(0, int(round(float(t) * FPS))))
            frs.append(frame(segs, k))
            labels.append(f'{k / FPS:.2f} {lb}'.strip())
        contact_sheet(frs, labels, sys.argv[3], cols=int(os.environ.get('GLOW_COLS', 6)), cell_w=320)
    elif mode == 'warm':      # precompute the cut-out mattes (one process, all threads: the models are big)
        part, _, n = (sys.argv[3] if len(sys.argv) > 3 else '0/1').partition('/')
        calls = warm_cuts()[int(part)::int(n)]
        t_start = time.time()
        for i, (alias, t, box, excl) in enumerate(calls):
            cut_at(alias, t, box, excl)
            if i % 20 == 0:
                print(f'  mattes {i}/{len(calls)} {time.time() - t_start:6.1f}s', flush=True)
        print(f'warm: {len(calls)} cut-out frames ({time.time() - t_start:.0f}s)')
    elif mode == 'chunk':
        chunk(segs, sys.argv[3], int(sys.argv[4]), int(sys.argv[5]))
    else:
        sys.exit(__doc__)


if __name__ == '__main__':
    main()
