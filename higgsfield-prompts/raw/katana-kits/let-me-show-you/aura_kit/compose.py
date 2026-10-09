#!/usr/bin/env python3
"""Aura-edit compositor for the /test-edit run (numpy + PIL + onnxruntime + ffmpeg only).
usage: python3 compose.py plan.json out.mp4 [--stills f1,f2,...] [--half]
Timeline grammar mirrors the reference: matte-swap transitions (incoming subject as
cut-out / cream or dark silhouette over the outgoing shot, then one blank cream frame),
lyric words behind the subject, white halo close-up, light streak + ring iris to black."""
import json, subprocess, sys, os, math, time
from fractions import Fraction
import numpy as np
import onnxruntime as ort
from PIL import Image, ImageDraw, ImageFont, ImageFilter

P = json.load(open(sys.argv[1])); OUT = sys.argv[2]
STILLS = None; HALF = '--half' in sys.argv
if '--stills' in sys.argv: STILLS = [int(x) for x in sys.argv[sys.argv.index('--stills') + 1].split(',')]
W, H, FPS, N = 1920, 1080, 25, P['frames']
if HALF: W, H = 960, 540
S = W / 1920.0
CREAM = np.array(P['cream'] if isinstance(P.get('cream'), list) else [226, 222, 212], np.float32)
DARK = np.array([16, 19, 18], np.float32)
sess = ort.InferenceSession('modnet.onnx', providers=['CPUExecutionProvider'])
t_start = time.time()
def log(*a): print('[%5.1fs]' % (time.time() - t_start), *a, flush=True)

# ---------------- timeline -----------------
segs = P['segments']                       # [f0, f1, shot, overlays]
start = {}                                  # first full frame of each shot
for s in segs:
    if s[2] not in ('blank',) and s[2] not in start: start[s[2]] = s[0]
start.update(P.get('start_override', {}))
def src_t(shot, f):
    sp = P['shots'][shot]
    t = max(sp.get('tmin', 0.0), sp['tin'] + (f - start[shot]) * sp.get('speed', 1.0) / FPS)
    if 'tmax' in sp and t > sp['tmax']:   # past the last clean frame: hold it, or play back from it ("bounce")
        t = max(sp.get('tmin', 0.0), 2 * sp['tmax'] - t) if sp.get('bounce') else sp['tmax']
    return t
need = {}
frames_to_render = STILLS if STILLS else list(range(N))
def plan_of(f):
    for s in segs:
        if s[0] <= f < s[1]: return s
    raise ValueError(f)
for f in frames_to_render:
    s = plan_of(f)
    if s[2] != 'blank': need.setdefault(s[2], set()).add(f)
    for ov in (s[3] if len(s) > 3 else []): need.setdefault(ov[1], set()).add(f)

# ---------------- grade -----------------
def grade(x, g, wb=None):
    x = x.astype(np.float32) / 255.0
    b = g.get('black', 0.0); x = np.clip((x - b) / (1 - b), 0, 1)          # set the black point first
    x = x * np.array(g.get('gain', [1, 1, 1]), np.float32) * g.get('exp', 1.0)
    if wb is not None: x = x * wb
    lum = (x @ np.array([0.2126, 0.7152, 0.0722], np.float32))[..., None]
    x = lum + (x - lum) * g.get('sat', 1.0)
    c = g.get('con', 0.12)
    x = np.clip(x, 0, 1); x = x + c * (x - 0.5) * (1 - np.abs(2 * x - 1))
    lift = g.get('lift', 0.0); x = x * (1 - lift) + lift
    return np.clip(x * 255, 0, 255)
_wb = {}
def auto_wb(shot, frame, matte, g):
    """per-shot gain that maps the clip's backdrop (matte < 0.02) onto the reference backdrop colour"""
    if shot not in _wb:
        tgt = g.get('wb_target')
        if not tgt: _wb[shot] = None
        else:
            sm = np.asarray(Image.fromarray(frame).resize((672, 384), Image.BILINEAR), np.float32)
            bgm = matte < 5
            base = grade(sm, {k: v for k, v in g.items() if k != 'wb_target'})
            med = np.median(base[bgm], axis=0) if bgm.sum() > 500 else None
            _wb[shot] = None if med is None else np.clip(np.array(tgt, np.float32) / np.maximum(med, 1), 0.8, 1.25)
            log('wb', shot, None if med is None else med.round(1), _wb[shot])
    return _wb[shot]

# ---------------- decode + matte -----------------
store = {}   # shot -> (tmin, rate, frames uint8 list, mattes uint8 list)
def matte_of(img):
    x = np.asarray(Image.fromarray(img).resize((672, 384), Image.BILINEAR), np.float32) / 127.5 - 1
    m = sess.run(None, {'input': x.transpose(2, 0, 1)[None]})[0][0, 0]
    return (np.clip(m, 0, 1) * 255).astype(np.uint8)
for shot, fs in need.items():
    sp = P['shots'][shot]; src = P['clips'][sp['clip']]
    ts = [src_t(shot, f) for f in fs]; t0 = max(0.0, min(ts) - 0.05); dur = max(ts) - t0 + 0.15
    rate = float(Fraction(subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                 'stream=r_frame_rate', '-of', 'csv=p=0', src], capture_output=True, text=True).stdout.strip()))
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', '%.3f' % t0, '-i', src, '-t', '%.3f' % dur, '-vf',
                          'scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080' + (',hflip' if sp.get('hflip') else ''),
                          '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, 1080, 1920, 3)
    store[shot] = (t0, rate, fr, {})
    log('decoded', shot, len(fr), 'frames from %.2f' % t0)

def get(shot, f):
    """graded frame (H,W,3 float32) and matte (H,W,1 float32) of shot at output frame f, with zoom crop"""
    sp = P['shots'][shot]; t0, rate, fr, mats = store[shot]
    k = int(round((src_t(shot, f) - t0) * rate)); k = min(max(k, 0), len(fr) - 1)
    if k not in mats: mats[k] = matte_of(fr[k])
    # zoom: linear from z0 at shot start to z1 at shot end frame
    z0, z1 = sp.get('zoom', [1.0, 1.0]); fe = sp.get('zend', start[shot] + 40)
    p = min(max((f - start[shot]) / max(1, fe - start[shot]), 0), 1); p = p * p * (3 - 2 * p) if sp.get('ease') else p
    z = z0 + (z1 - z0) * p
    cx, cy = sp.get('c', [0.5, 0.5])
    cw, ch = 1920 / z, 1080 / z
    x0 = min(max(cx * 1920 - cw / 2, 0), 1920 - cw); y0 = min(max(cy * 1080 - ch / 2, 0), 1080 - ch)
    box = (x0, y0, x0 + cw, y0 + ch)
    img = Image.fromarray(fr[k]).resize((W, H), Image.BICUBIC, box=box)
    mb = (x0 * 672 / 1920, y0 * 384 / 1080, (x0 + cw) * 672 / 1920, (y0 + ch) * 384 / 1080)
    m = Image.fromarray(mats[k]).resize((W, H), Image.BILINEAR, box=mb)
    g = dict(P.get('grade', {})); g.update(sp.get('grade', {}))
    wb = auto_wb(shot, fr[k], mats[k], g)
    return post_grade(grade(np.asarray(img), g, wb)), np.asarray(m, np.float32)[..., None] / 255.0, m


def post_grade(x):
    """look stage applied AFTER the per-shot white balance (so auto-WB cannot cancel it): exposure + extra contrast"""
    po = P.get('post')
    if not po: return x
    x = np.clip(x / 255.0 * po.get('exp', 1.0), 0, 1)
    c = po.get('con', 0.0); x = x + c * (x - 0.5) * (1 - np.abs(2 * x - 1))
    return np.clip(x * 255, 0, 255)

if isinstance(P.get('cream'), str) and P['cream'] in store:   # match blank frames to a shot's graded backdrop
    _i, _m, _ = get(P['cream'], start[P['cream']])
    CREAM = np.median(_i[(_m[..., 0] < 0.02)], axis=0).astype(np.float32); log('cream', CREAM)

CREAM_P = post_grade(CREAM.reshape(1, 1, 3)).reshape(3)   # blank / cream-silhouette fill after the look stage

# ---------------- text -----------------
_wcache = {}
def word_alpha(text):
    """heavy lyric word: per-glyph horizontal squeeze, constant ink gap, then dilated for the reference's weight"""
    if text in _wcache: return _wcache[text]
    T = P['text']; cap = T['cap'] * S; cy = T['cy'] * S; sx = T.get('sx', 1.0)
    f = ImageFont.truetype(T['font'], 400); bb = f.getbbox('H'); size = int(400 * cap / (bb[3] - bb[1]))
    f = ImageFont.truetype(T['font'], size)
    glyphs = []
    for c in text:
        x0, y0, x1, y1 = f.getbbox(c)
        g = Image.new('L', (x1 - x0 + 4, int(size * 1.5)), 0); ImageDraw.Draw(g).text((2 - x0, 0), c, font=f, fill=255)
        g = g.resize((max(1, round(g.width * sx)), g.height), Image.LANCZOS); glyphs.append(g)
    gap = T.get('gap', 0) * S
    inks = [g.width - 4 * sx for g in glyphs]; tw = sum(inks) + gap * (len(glyphs) - 1)
    L = Image.new('L', (W, H), 0); x = (W - tw) / 2; top = cy - cap / 2 - f.getbbox('H')[1]
    for g, iw in zip(glyphs, inks): L.paste(g, (int(round(x - 2 * sx)), int(round(top))), g); x += iw + gap
    bold = int(round(T.get('bold', 0) * S))
    if bold > 0: L = L.filter(ImageFilter.MaxFilter(2 * bold + 1))
    a = np.asarray(L, np.float32)[..., None] / 255.0; _wcache[text] = a; return a
def word_at(f):
    """(word, opacity) at output frame f; an optional {"fade":[t0,t1]} fades the word out"""
    t = f / FPS
    for w in P['words']:
        if w[0] - 1e-6 <= t < w[1] - 1e-6:
            op = 1.0
            if len(w) > 3 and 'fade' in w[3]:
                f0, f1 = w[3]['fade']; op = float(np.clip(1 - (t - f0) / (f1 - f0), 0, 1))
            return w[2], op
    return None, 0.0

# ---------------- fx -----------------
def halo(img, m_pil, m):
    small = m_pil.resize((W // 4, H // 4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(P['halo']['r'] * S / 4))
    g = np.asarray(small.resize((W, H), Image.BILINEAR), np.float32)[..., None] / 255.0
    g = np.clip((g - m) * P['halo']['k'], 0, P['halo']['max'])
    return img * (1 - g) + np.array([250, 249, 244], np.float32) * g
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
dctr = np.sqrt((xx - W / 2) ** 2 + (yy - H * 0.5) ** 2)
ell = np.clip(1 - 0.7 * (((xx - W / 2) / (0.5 * W)) ** 2 + ((yy - H / 2) / (0.5 * H)) ** 2) / 2, 0.3, 1)[..., None]
STREAK_C = np.array([235, 236, 224], np.float32)
RING_CORE = np.array([234, 236, 225], np.float32); RING_GLOW = np.array([166, 236, 219], np.float32)
def kf(table, t):
    ts = [a for a, _ in table]; v = np.array([b for _, b in table], np.float32)
    if v.ndim == 1: return float(np.interp(t, ts, v))
    return np.array([np.interp(t, ts, v[:, i]) for i in range(v.shape[1])], np.float32)
def kf_log(table, t):
    ts = [a for a, _ in table]; v = [math.log(max(b, 1e-6)) for _, b in table]
    return math.exp(float(np.interp(t, ts, v)))
def smoothstep(e0, e1, x): q = np.clip((x - e0) / (e1 - e0), 0, 1); return q * q * (3 - 2 * q)
def streak_band(img, m, t, E):
    """flat cream band sliding down; slit-scan (stretched row) texture where it crosses the subject"""
    keys = E['streak']
    if t < keys[0][0] - 0.01 or t > keys[-1][0] + 0.01: return img
    y0 = kf([[k[0], k[1]] for k in keys], t) * S; y1 = kf([[k[0], k[2]] for k in keys], t) * S; op = kf([[k[0], k[3]] for k in keys], t)
    if op <= 0: return img
    e = 25 * S; a = (smoothstep(y0 - e, y0 + e, yy) * (1 - smoothstep(y1 - e, y1 + e, yy)))[..., None] * op
    C = np.broadcast_to(STREAK_C, img.shape)
    if m is not None:
        yc = int(np.clip((y0 + y1) / 2, 0, H - 1)); slit = np.repeat(img[yc:yc + 1], H, 0)
        sub = (m > 0.5).astype(np.float32)
        C = C * (1 - sub) + (0.5 * STREAK_C + 0.5 * slit) * sub
    return img * (1 - a) + C * a
def end_fx(img, f, m):
    E = P['end']; t = f / FPS + 1e-6
    if t < E['pre'][0][0] - 0.01: return img
    for tp, yp in E['pre']:   # thin light lines sweeping up before the tint (reference 13.04-13.20)
        if abs(t - tp) < 0.02 and yp > 0:
            img = img + (18 * np.exp(-((yy - yp * H) / (0.028 * H)) ** 2) + 25 * np.exp(-((yy - yp * H) / (1.5 * S)) ** 2))[..., None]
    if t >= E['tint0']:       # backdrop darkens into teal, her skin darkens neutrally; corner falloff from 13.44
        gbg = kf(E['tint_bg'], t); gsub = kf(E['tint_sub'], t)
        mm = m if m is not None else np.zeros((H, W, 1), np.float32)
        img = img * ((1 - mm) * gbg + mm * gsub)
        if t >= E['streak'][0][0] - 0.01: img = img * ell
    if t >= E['ring0'] - 0.01:   # eclipse ring with measured radii, thick cream core + broad teal glow
        if t >= E['black0']: return np.zeros_like(img)
        r = kf_log(E['ring_r'], t) * S
        core = np.exp(-((dctr - r) / (0.24 * r)) ** 2)[..., None]
        glow = (0.77 * np.exp(-np.maximum(dctr - r, 0) / (0.9 * r)) * (dctr > r))[..., None]
        inside = kf(E['ring_inside'], t)
        base = img * np.where(dctr[..., None] < r, inside, 0.0)
        img = np.maximum(base, np.maximum(core * RING_CORE, glow * RING_GLOW)) * kf(E['ring_fade'], t)
    img = streak_band(img, m, t, E)
    return np.clip(img, 0, 255)

_edge = None
def shift(img, m, dx, dy, s):
    """scale an overlay layer about the frame centre by s, then move it by (dx, dy) frame fractions;
    the layer's own frame borders are feathered so clipped hair/shoulders never show a straight edge"""
    global _edge
    if _edge is None:
        fw = 90 * S; ex = np.clip(np.minimum(np.arange(W), np.arange(W)[::-1]) / fw, 0, 1); ey = np.clip(np.minimum(np.arange(H), np.arange(H)[::-1]) / fw, 0, 1)
        _edge = (np.broadcast_to(ex[None, :], (H, W)), np.minimum(ex[None, :], ey[:, None]))
    inv = (1 / s, 0, W / 2 - (W / 2 + dx * W) / s, 0, 1 / s, H / 2 - (H / 2 + dy * H) / s)
    li = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).transform((W, H), Image.AFFINE, inv, Image.BILINEAR)
    # only feather borders that actually move into view: x-borders for a sideways shift, all for scale/vertical moves
    m2 = m[..., 0] * (_edge[1] if (dy or s != 1) else _edge[0] if dx else 1)
    lm = Image.fromarray((m2 * 255).astype(np.uint8)).transform((W, H), Image.AFFINE, inv, Image.BILINEAR)
    return np.asarray(li, np.float32), np.asarray(lm, np.float32)[..., None] / 255.0

# ---------------- look: flash-light transitions + film burns -----------------
def flash_amount(f):
    """plan.flash = {"frames": [...], "strength", "pre", "decay"}: 1 frame ramp-in, exponential decay after"""
    F_ = P.get('flash')
    if not F_: return 0.0
    a = 0.0
    for c in F_['frames']:
        d = f - c
        if -F_.get('pre', 1) <= d < 0: v = F_.get('strength', 1.0) * 0.4 * (1 + d / F_.get('pre', 1) + 1e-6)
        elif d >= 0: v = F_.get('strength', 1.0) * math.exp(-d / F_.get('decay', 2.2))
        else: v = 0.0
        a = max(a, v)
    return a if a > 0.02 else 0.0
def flash_fx(img, f):
    a = flash_amount(f)
    if a <= 0: return img
    F_ = P['flash']
    x = img * (1 + 1.6 * a)                                                   # blow the exposure out
    bright = Image.fromarray(np.clip(x - 170, 0, 255).astype(np.uint8)).resize((W // 4, H // 4), Image.BILINEAR)
    bloom = np.asarray(bright.filter(ImageFilter.GaussianBlur(18 * S)).resize((W, H), Image.BILINEAR), np.float32)
    x = x + bloom * F_.get('bloom', 0.8) * a
    col = np.array(F_.get('color', [255, 248, 236]), np.float32)
    return np.clip(x * (1 - 0.7 * a) + col * 0.7 * a, 0, 255)

BW_, BH_ = 240, 135
_byy, _bxx = np.mgrid[0:BH_, 0:BW_].astype(np.float32); _byy /= BH_; _bxx /= BW_
_BSTOP = [0.0, 0.25, 0.5, 0.75, 0.93, 1.0]                                  # dark red -> orange -> amber, white only at the very edge
_BCOL = [[0, 140, 235, 255, 255, 255], [0, 25, 80, 140, 190, 240], [0, 4, 12, 30, 90, 220]]
def _bnoise(seed, t):
    """3 broad octaves only: soft light-leak blobs (a finer octave reads as flames/smoke)"""
    rng_ = np.random.default_rng(seed); acc = np.zeros((BH_, BW_), np.float32); amp, tot = 1.0, 0.0
    for gw, gh in ((3, 2), (6, 4), (12, 7)):
        a = rng_.random((gh, gw)); b = rng_.random((gh, gw)); fld = a * (1 - t) + b * t
        up = np.asarray(Image.fromarray((fld * 255).astype(np.uint8)).resize((BW_, BH_), Image.BICUBIC), np.float32) / 255
        acc += up * amp; tot += amp; amp *= 0.5
    return acc / tot
def burns_fx(img, f):
    """plan.burns = [[start_frame, frames, side, seed, strength], ...]: soft orange film burns / light leaks
    creeping in from an edge or corner, screen-blended plus tinted (plan.burn_tint, default 0.6) so they also read on
    cream/white frames (side: l r t b tl tr bl br)"""
    evs = [e for e in P.get('burns', []) if e[0] <= f < e[0] + e[1]]
    if not evs: return img
    col = np.zeros((BH_, BW_, 3), np.float32); cc = np.zeros_like(col)
    tw = np.zeros((BH_, BW_), np.float32); vmax = np.zeros_like(tw)
    for t0, dur, side, seed, strength in evs:
        p = (f - t0) / dur
        env = float(np.clip(p / 0.3, 0, 1) ** 0.7 * (1 - np.clip((p - 0.55) / 0.45, 0, 1)) ** 1.5)
        dmap = {'l': _bxx, 'r': 1 - _bxx, 't': _byy, 'b': 1 - _byy}
        d = np.minimum.reduce([dmap[ch] for ch in side]) if len(side) == 1 else np.sqrt(sum(dmap[ch] ** 2 for ch in side)) / 1.2
        n = _bnoise(int(seed), p * 0.6)
        v = np.clip(env * 1.1 - d * 2.8 + (n - 0.5) * 0.75, 0, 1); v = v * v * (3 - 2 * v)   # hugs the edge, soft front
        c = np.stack([np.interp(v, _BSTOP, ch) for ch in _BCOL], -1)
        col = np.maximum(col, c * (np.clip(v * 2.0, 0, 1) * strength)[..., None])
        up_ = v > vmax; cc[up_] = c[up_]; vmax = np.maximum(vmax, v)
        tw = np.maximum(tw, P.get('burn_tint', 0.6) * strength * np.clip((v - 0.2) / 0.4, 0, 1))
    def _up(a_):
        im = Image.fromarray(np.clip(a_, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5))
        return np.asarray(im.resize((W, H), Image.BILINEAR), np.float32)
    cu, ccu, twu = _up(col), _up(cc), _up(tw * 255)[..., None] / 255
    x = 255 - (255 - img) * (1 - cu / 255)                                  # screen: hot light on dark frames
    return x * (1 - twu) + ccu * twu                                       # tint: orange still reads on cream/white frames

# ---------------- render loop -----------------
rng = np.random.default_rng(7)
def render(f):
    s = plan_of(f); shot = s[2]; ovs = s[3] if len(s) > 3 else []
    m_pil = None
    if shot == 'blank': img = np.broadcast_to(CREAM_P, (H, W, 3)).copy(); m = None
    else: img, m, m_pil = get(shot, f)
    w, wop = word_at(f); ta = None
    if w and m is not None and wop > 0:
        ta = word_alpha(w) * wop; base = img
        mt = np.clip((m - 0.5) * 3.0 + 0.5, 0, 1)              # crisp occlusion edge against the letters
        img = base * (1 - ta) + np.array(P['text']['color'], np.float32) * ta
        img = img * (1 - mt) + base * mt; ta = ta * (1 - mt)
    if shot in P.get('halo_shots', []): img = halo(img, m_pil, m)
    out0 = img.copy()
    for ov in ovs:
        kind, oshot = ov[0], ov[1]; o = ov[2] if len(ov) > 2 else {}
        oi, om, _ = get(oshot, f)
        if any(k in o for k in ('dx', 'dy', 's')): oi, om = shift(oi, om, o.get('dx', 0.0), o.get('dy', 0.0), o.get('s', 1.0))
        om = np.clip((om - 0.5) / 0.3, 0, 1)   # hard sticker edge (reference f90-92); drops the pale hair fringe
        om = om * o.get('a', 1.0)
        if kind == 'cut': img = img * (1 - om) + oi * om
        elif kind == 'silcream':   # flat backdrop-cream silhouette, optionally ghosting the incoming picture
            gh = o.get('ghost', 0.0); fill = np.minimum(CREAM_P + P.get('sil_lift', 0), 255) * (1 - gh) + oi * gh
            img = img * (1 - om) + fill * om
        elif kind == 'sildark':    # incoming shot crushed to ~11 %: features stay faintly readable
            img = img * (1 - om) + oi * P.get('sildark_k', 0.11) * om
        if o.get('under') and m is not None: img = img * (1 - m) + out0 * m   # outgoing subject stays in front
    img = flash_fx(img, f)
    img = burns_fx(img, f)
    if shot != 'Iend': img = end_fx(img, f, m)
    # grain: fine (1 px) clean luma grain when grain_fine, else the older 2x2 clumped grain
    gs = P.get('grain', 4.0)
    if gs > 0:
        if P.get('grain_fine'): n = rng.normal(0, gs, (H, W)).astype(np.float32)[..., None]
        else:
            n = rng.normal(0, gs, (H // 2 + 1, W // 2 + 1)).astype(np.float32)
            n = np.repeat(np.repeat(n, 2, 0), 2, 1)[:H, :W, None]
        img = img + n * (0.6 + 0.4 * (1 - img / 255.0)) * (1 if ta is None else (1 - 0.7 * ta))
    return np.clip(img, 0, 255).astype(np.uint8)

if STILLS:
    tiles = [Image.fromarray(render(f)).resize((480, 270)) for f in STILLS]
    cols = 4; rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * 480, rows * 270))
    for i, t in enumerate(tiles): sheet.paste(t, ((i % cols) * 480, (i // cols) * 270))
    sheet.save(OUT, quality=82); log('stills', OUT); sys.exit(0)

enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (W, H), '-r', str(FPS),
                        '-i', '-', '-i', P['audio'], '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'medium',
                        '-crf', '16', '-pix_fmt', 'yuv420p', '-af', 'apad', '-c:a', 'aac', '-b:a', '256k', '-t', '%.3f' % (N / FPS),
                        '-movflags', '+faststart', OUT], stdin=subprocess.PIPE)
for f in range(N):
    enc.stdin.write(render(f).tobytes())
    if f % 25 == 0: log('frame', f)
enc.stdin.close(); enc.wait(); log('done', OUT, enc.returncode)
