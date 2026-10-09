#!/usr/bin/env python3
"""analyze_ref - deconstruct a reference video for free: cuts, flashes, window/letterbox, cadence, look, sheets.

    python3 analyze_ref.py W                 # reads W/ref/ref.mp4
    python3 analyze_ref.py W --ref clip.mp4  # any video; outputs still go to W
    python3 analyze_ref.py W --review-size   # every sheet <= 125 KB, so 4 fit in one image_paths call

Writes
  W/analysis/analysis.json   cut proposals with confidence, bursts, flashes, solids, inverts, canvas
                             (window/letterbox), cadence, motion and look stats per cut, text-region
                             candidates, reference-level look, sheet index      (schema rr.analysis/1)
  W/analysis/frames.json     per-frame curves (diff, structure, histogram, luma, saturation, holds)
  W/analysis/window_mask.png anti-aliased mask of a detected window (only when there is one)
  W/sheets/overview_pNN.jpg  one mid frame per cut, labelled 'c03 f120-151' (<= 40 tiles per page)
  W/sheets/ef_NNN.jpg        EVERY frame at native fps, labelled with the absolute frame index;
                             detector marks: red bar = cut, orange = low-confidence cut, magenta =
                             burst sub-cut, yellow = flash/solid frame, violet = invert, grey '?' = near miss,
                             '=' = repeat of the previous frame
  W/sheets/timeline.png      score / structure / histogram / luma curves with cut markers, frame ticks and
                             thumbnails (.jpg instead when the PNG would exceed the byte cap)
  W/sheets/layout.jpg        full canvas with the detected window/bars outlined (when found)
  W/sheets/detail_A_B[_pN].jpg  --detail A:B: frames A..B, <= 12 per sheet, native pixels when the
                             region fits 4 across (pick the region with --detail-crop x,y,w,h)

Detectors only PROPOSE: the every-frame pages are the ground truth. Correct the cut list by hand
(analysis.json "cuts"), then re-run with --cuts-from analysis/analysis.json to recompute per-cut stats
and sheets for the corrected cuts.
Only stdlib + numpy + ffmpeg/ffprobe (through rrio.py next to this file).
"""
from __future__ import annotations

import argparse
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np  # noqa: E402

import rrio  # noqa: E402

SCHEMA = "rr.analysis/1"
VERSION = 1

AN_W = 160          # analysis width (px) of the per-frame features
CO_W = 80           # coarse width for structure / motion-compensated matching
MC_R = 6            # block-matching search radius in coarse px
MC_B = 8            # block size in coarse px
MAX_FLASH = 4       # a spike that returns to the same shot within this many frames is a flash
SOLID_SD = 7.0      # luma std (0-255, analysis res) below which a frame is a solid colour
NEAR_SD = 20.0      # near-white / near-black frames below this std are treated like solids

COL_CUT = (235, 40, 40)
COL_LOW = (255, 150, 0)
COL_SUB = (225, 70, 225)
COL_FLASH = (255, 225, 0)
COL_INV = (150, 90, 255)
COL_MAYBE = (150, 150, 150)


def log(msg):
    print(msg, flush=True)


def clamp01(x):
    return float(min(1.0, max(0.0, x)))


# ==================================================================================================
# canvas: window / letterbox / pillarbox
# ==================================================================================================
def _runs_bool(mask):
    """[(start, end_exclusive)] of True runs."""
    m = np.concatenate([[False], np.asarray(mask, bool), [False]])
    d = np.diff(m.astype(np.int8))
    s = np.nonzero(d == 1)[0]
    e = np.nonzero(d == -1)[0]
    return list(zip(s.tolist(), e.tolist()))


def _main_band(frac, dense=0.3, loose=0.05):
    """Largest contiguous run where frac > dense, extended while frac > loose. None if nothing dense."""
    runs = _runs_bool(frac > dense)
    if not runs:
        return None
    s, e = max(runs, key=lambda r: (frac[r[0]:r[1]].sum(), r[1] - r[0]))
    while s > 0 and frac[s - 1] > loose:
        s -= 1
    while e < len(frac) and frac[e] > loose:
        e += 1
    return s, e


def _subpix_cross(profile, thr, rising=True):
    """First index where profile crosses thr (sub-pixel, linear). profile is 1-D float."""
    p = np.asarray(profile, np.float64)
    idx = np.nonzero(p >= thr)[0] if rising else np.nonzero(p < thr)[0]
    if len(idx) == 0:
        return None
    k = int(idx[0])
    if k == 0:
        return 0.0
    a, b = p[k - 1], p[k]
    return float(k - 1 + (thr - a) / (b - a)) if b != a else float(k)


def _bilinear(img, xs, ys):
    """Sample img (index coords, pixel centres at integers) at float positions."""
    H, W = img.shape
    x = np.clip(np.asarray(xs, np.float64), 0, W - 1.0001)
    y = np.clip(np.asarray(ys, np.float64), 0, H - 1.0001)
    x0 = np.floor(x).astype(int)
    y0 = np.floor(y).astype(int)
    fx, fy = x - x0, y - y0
    f = img.astype(np.float64)
    return ((f[y0, x0] * (1 - fx) + f[y0, x0 + 1] * fx) * (1 - fy)
            + (f[y0 + 1, x0] * (1 - fx) + f[y0 + 1, x0 + 1] * fx) * fy)


def _halfmax_edges(mx, x0, y0, x1, y1, thr):
    """Sub-pixel picture edges (continuous coords) where the max image crosses thr; median over the
    middle half of every side. Returns (left, top, right, bottom) or None, plus the 10-90% ramp width."""
    H, W = mx.shape
    pad = max(6, int(0.03 * max(x1 - x0, y1 - y0)))
    ys = list(range(y0 + (y1 - y0) // 4, y1 - (y1 - y0) // 4, max(1, (y1 - y0) // 80)))
    xs = list(range(x0 + (x1 - x0) // 4, x1 - (x1 - x0) // 4, max(1, (x1 - x0) // 80)))

    def side(profiles, rev):
        vals = []
        for prof in profiles:
            q = prof[::-1] if rev else prof
            v = _subpix_cross(q, thr)
            if v is not None:
                vals.append(v)
        return float(np.median(vals)) if len(vals) >= 3 else None

    la, lb = max(0, x0 - pad), min(W, x0 + pad)
    ra, rb = max(0, x1 - pad), min(W, x1 + pad)
    ta, tb = max(0, y0 - pad), min(H, y0 + pad)
    ba, bb = max(0, y1 - pad), min(H, y1 + pad)
    L = side([mx[y, la:lb].astype(np.float64) for y in ys], False)
    R = side([mx[y, ra:rb].astype(np.float64) for y in ys], True)
    T_ = side([mx[ta:tb, x].astype(np.float64) for x in xs], False)
    B_ = side([mx[ba:bb, x].astype(np.float64) for x in xs], True)
    if None in (L, R, T_, B_):
        return None, None
    edges = (la + L + 0.5, ta + T_ + 0.5, rb - R - 0.5, bb - B_ - 0.5)
    # ramp width on the left edge (10% -> 90% of canvas..plateau)
    lo_v = float(np.median(mx[ys, la]))
    hi_v = float(np.median(mx[ys, min(W - 1, lb + pad)]))
    ramps = []
    for y in ys:
        prof = mx[y, la:min(W, lb + pad)].astype(np.float64)
        a10 = _subpix_cross(prof, lo_v + 0.1 * (hi_v - lo_v))
        a90 = _subpix_cross(prof, lo_v + 0.9 * (hi_v - lo_v))
        if a10 is not None and a90 is not None and a90 >= a10:
            ramps.append(a90 - a10)
    return edges, (float(np.median(ramps)) if ramps else None)


def _corner_radius(mx, edges, thr):
    """Rounded-corner radius measured along each corner's 45-degree diagonal from the half-max corner.
    A circle corner of radius r leaves s = r(1 - 1/sqrt 2) unlit along the diagonal."""
    L, T_, R, B_ = edges
    lim = max(4.0, min(R - L, B_ - T_) / 3.0)
    s = np.arange(0, lim, 0.5)
    est = []
    for cx, cy, sx, sy in ((L, T_, 1, 1), (R, T_, -1, 1), (L, B_, 1, -1), (R, B_, -1, -1)):
        prof = _bilinear(mx, cx + sx * s - 0.5, cy + sy * s - 0.5)
        k = _subpix_cross(prof, thr)
        if k is None:
            continue
        est.append(k * 0.5 / (1 - 1 / math.sqrt(2)))
    if not est:
        return 0, []
    r = float(np.median(est))
    return (int(round(r)) if r >= 2.5 else 0), [round(v, 1) for v in est]


def window_mask(W, H, x, y, w, h, r):
    """Anti-aliased rounded-rect mask (uint8 HxW, 255 inside) with corner radius r."""
    yy = np.arange(H, dtype=np.float32)[:, None] + 0.5
    xx = np.arange(W, dtype=np.float32)[None, :] + 0.5
    cx, cy = x + w / 2.0, y + h / 2.0
    hw, hh = w / 2.0 - r, h / 2.0 - r
    qx = np.abs(xx - cx) - hw
    qy = np.abs(yy - cy) - hh
    out = np.sqrt(np.maximum(qx, 0) ** 2 + np.maximum(qy, 0) ** 2) + np.minimum(np.maximum(qx, qy), 0) - r
    cov = np.clip(0.5 - out, 0, 1)
    return (cov * 255 + 0.5).astype(np.uint8)


def detect_canvas(path, info, n, samples=90):
    """Find a window / letterbox / pillarbox from the per-pixel max and min luma over sampled frames.

    active = pixels whose luma ever changes (max - min > 24): footage. Static canvas, static captions
    and bars are inactive. The main dense band of active rows/cols is the picture area; its edges are
    refined on the lit mask (max > half plateau) and the corner radius is measured on the diagonals.
    """
    W, H = info["w"], info["h"]
    every = max(1, n // samples)
    mx = mn = None
    k = 0
    for _, g in rrio.read_frames(path, count=n, every=every, gray=True, info=info):
        if mx is None:
            mx, mn = g.copy(), g.copy()
        else:
            np.maximum(mx, g, out=mx)
            np.minimum(mn, g, out=mn)
        k += 1
    res = {"kind": "full", "window": None, "letterbox": None, "crop": {"x": 0, "y": 0, "w": W, "h": H},
           "radius": 0, "confidence": 1.0, "samples": k, "every": every, "notes": []}
    if mx is None:
        res["notes"].append("no frames decoded for canvas detection")
        return res, None
    act = (mx.astype(np.int16) - mn.astype(np.int16)) > 24
    rows = _main_band(act.mean(1))
    if rows is None:
        res["notes"].append("no changing pixels found (still image?) - using the full frame")
        return res, mx
    ry0, ry1 = rows
    cols = _main_band(act[ry0:ry1].mean(0))
    if cols is None:
        return res, mx
    cx0, cx1 = cols
    # refine on the lit mask inside the band neighbourhood (soft edges count as picture)
    inner = mx[ry0 + (ry1 - ry0) // 4: ry1 - (ry1 - ry0) // 4, cx0 + (cx1 - cx0) // 4: cx1 - (cx1 - cx0) // 4]
    plateau = float(np.median(inner)) if inner.size else 128.0
    border_lvl = float(np.median(np.concatenate([mx[:max(1, ry0)].ravel(), mx[ry1:].ravel(),
                                                  mx[:, :max(1, cx0)].ravel(), mx[:, cx1:].ravel()])))
    thr = max(28.0, border_lvl + 0.5 * max(0.0, plateau - border_lvl)) if plateau > border_lvl + 20 else None
    x0, y0, x1, y1 = cx0, ry0, cx1, ry1
    outer = None
    edges = None
    ramp = None
    if thr is not None:
        lit = mx >= min(thr, border_lvl + 20) if border_lvl < 60 else act
        pad = max(4, int(0.02 * max(W, H)))
        sy0, sy1 = max(0, ry0 - pad), min(H, ry1 + pad)
        sx0, sx1 = max(0, cx0 - pad), min(W, cx1 + pad)
        sub = lit[sy0:sy1, sx0:sx1]
        rr_ = np.nonzero(sub.mean(1) > 0.05)[0]
        cc_ = np.nonzero(sub.mean(0) > 0.05)[0]
        if len(rr_) and len(cc_):
            y0, y1 = sy0 + int(rr_[0]), sy0 + int(rr_[-1]) + 1
            x0, x1 = sx0 + int(cc_[0]), sx0 + int(cc_[-1]) + 1
        outer = {"x": int(x0), "y": int(y0), "w": int(x1 - x0), "h": int(y1 - y0)}
        edges, ramp = _halfmax_edges(mx, x0, y0, x1, y1, thr)
        if edges is not None:
            ex0, ey0, ex1, ey1 = (int(round(v)) for v in edges)
            # an edge that sits on the frame border stays there
            x0 = 0 if x0 <= 1 else ex0
            y0 = 0 if y0 <= 1 else ey0
            x1 = W if x1 >= W - 1 else ex1
            y1 = H if y1 >= H - 1 else ey1
    top, bot, left, right = y0, H - y1, x0, W - x1
    tol_y, tol_x = max(2, int(0.01 * H)), max(2, int(0.01 * W))
    has = {"top": top > tol_y, "bottom": bot > tol_y, "left": left > tol_x, "right": right > tol_x}
    if not any(has.values()):
        return res, mx
    if (x1 - x0) * (y1 - y0) < 0.15 * W * H:
        res["notes"].append(f"active area only {x1 - x0}x{y1 - y0}: too small for a window, using the full frame")
        return res, mx
    if all(has.values()):
        kind = "window"
    elif not has["left"] and not has["right"]:
        kind = "letterbox"
    elif not has["top"] and not has["bottom"]:
        kind = "pillarbox"
    else:
        kind = "bars"
    # bars must be static: the inactive border may not contain changing pixels in bulk
    border = np.ones_like(act)
    border[y0:y1, x0:x1] = False
    moving_border = float(act[border].mean()) if border.any() else 0.0
    conf = 0.9 if moving_border < 0.01 else 0.6 if moving_border < 0.05 else 0.3
    if moving_border >= 0.05:
        res["notes"].append(f"{moving_border:.0%} of the border pixels change: blurred/animated background? "
                            "check sheets/layout.jpg")
    bar_lvl = float(np.median(mx[border])) if border.any() else 0.0
    graphic = (np.abs(mx.astype(np.int16) - int(round(bar_lvl))) > 40) & ~act & border
    static_lit = float(graphic[border].mean()) if border.any() else 0.0
    if static_lit > 0.002:
        ys, xs = np.nonzero(graphic)
        res["notes"].append(f"static graphics on the canvas outside the picture (bbox x {xs.min()}-{xs.max()}, "
                            f"y {ys.min()}-{ys.max()}): caption/logo baked into the canvas")
    r, rest = 0, []
    if kind == "window" and thr is not None and edges is not None:
        r, rest = _corner_radius(mx, edges, thr)
        if rest and (max(rest) - min(rest)) > 0.25 * max(rest) + 3:
            res["notes"].append(f"corner radii disagree {rest}: check the corners on sheets/layout.jpg")
    w, h = x1 - x0, y1 - y0
    if conf < 0.6:
        res["notes"].append(f"weak {kind} candidate {w}x{h}@{x0},{y0} (border not static): analysing the full "
                            "frame; force it with --window x,y,w,h if the sheets show real bars")
        res["candidate"] = {"kind": kind, "x": int(x0), "y": int(y0), "w": int(w), "h": int(h), "confidence": conf}
        return res, mx
    res.update({"kind": kind, "crop": {"x": int(x0), "y": int(y0), "w": int(w), "h": int(h)},
                "radius": int(r), "radius_corners": rest, "confidence": conf, "outer": outer,
                "edge_ramp_px": round(ramp, 2) if ramp is not None else None,
                "edge_rule": "picture edge = where the per-pixel max luma crosses half way between canvas and plateau",
                "plateau": round(plateau, 1), "canvas_level": round(border_lvl, 1),
                "moving_border_share": round(moving_border, 4)})
    if kind == "window":
        res["window"] = {"x": int(x0), "y": int(y0), "w": int(w), "h": int(h), "radius": int(r)}
    else:
        res["letterbox"] = {"top": int(top), "bottom": int(bot), "left": int(left), "right": int(right)}
    return res, mx


# ==================================================================================================
# per-frame features
# ==================================================================================================
def _hist(fr, bins=32):
    """Per-channel normalised histograms, shape (3, bins)."""
    q = (fr.reshape(-1, 3) >> (8 - int(math.log2(bins)))).astype(np.int64)
    out = np.empty((3, bins), np.float32)
    n = q.shape[0]
    for c in range(3):
        out[c] = np.bincount(q[:, c], minlength=bins)[:bins] / n
    return out


def _hdist(a, b):
    return float(0.5 * np.abs(a - b).sum() / 3.0)


def _coarse(y, ch):
    return rrio.resize(y, CO_W, ch, "area").astype(np.float32)


def _z(y):
    m = float(y.mean())
    s = float(y.std())
    return (y - m) / max(s, 6.0)


def mc_match(a, b, want_inv=True, R=MC_R, B=MC_B):
    """Block matching of z-normalised coarse luma a (current) against b (previous).

    Returns dict: res (mean best-match residual over textured blocks), res_inv (same against -b,
    i.e. polarity-inverted), dx, dy (median block motion, coarse px), zoom (divergence estimate),
    vec_spread. res ~0 for holds, ~0.1-0.3 for motion, >0.45 for unrelated pictures.
    """
    from numpy.lib.stride_tricks import sliding_window_view as swv
    H, W = a.shape
    Hb, Wb = (H // B) * B, (W // B) * B
    nby, nbx = Hb // B, Wb // B
    aa = a[:Hb, :Wb]
    bp = np.pad(b, R, mode="edge")
    V = swv(bp, (H, W))[:, :, :Hb, :Wb]
    ab = aa.reshape(nby, B, nbx, B).std((1, 3))
    bb = b[:Hb, :Wb].reshape(nby, B, nbx, B).std((1, 3))
    tex = (ab > 0.15) | (bb > 0.15)
    if tex.sum() < 3:
        tex = np.ones_like(tex)
    out = {}
    for key, sgn in (("res", 1.0), ("res_inv", -1.0)):
        if key == "res_inv" and not want_inv:
            out[key] = 9.0
            continue
        D = np.abs(aa[None, None] - sgn * V).reshape(2 * R + 1, 2 * R + 1, nby, B, nbx, B).mean((3, 5))
        D = D.reshape(-1, nby, nbx)
        k = D.argmin(0)
        mn = np.take_along_axis(D, k[None], 0)[0]
        out[key] = float(mn[tex].mean())
        if key == "res":
            dy = (k // (2 * R + 1) - R).astype(np.float32)
            dx = (k % (2 * R + 1) - R).astype(np.float32)
            # b shifted by (dy,dx) matches a  ->  content moved by (-dx,-dy)?  V[oy,ox] = b[y+oy-R, x+ox-R]
            # a(y,x) ~ b(y+dy, x+dx) -> motion from b to a is (-dx, -dy)
            mvx, mvy = -dx[tex], -dy[tex]
            out["dx"] = float(np.median(mvx))
            out["dy"] = float(np.median(mvy))
            gy, gx = np.mgrid[0:nby, 0:nbx]
            rx = ((gx + 0.5) * B - Wb / 2.0)[tex]
            ry = ((gy + 0.5) * B - Hb / 2.0)[tex]
            den = float((rx * rx).sum() + (ry * ry).sum())
            out["zoom"] = float(((mvx - out["dx"]) * rx + (mvy - out["dy"]) * ry).sum() / den) if den > 0 else 0.0
            out["spread"] = float(np.median(np.abs(mvx - out["dx"]) + np.abs(mvy - out["dy"])))
    return out


class Features:
    """Per-frame features of the analysis crop at AN_W px, plus a pair-distance cache."""

    def __init__(self, frames, fps):
        self.F = frames                                    # list of uint8 HxWx3 (analysis res)
        self.N = len(frames)
        self.fps = fps
        h, w = frames[0].shape[:2]
        self.ch = max(8, int(round(CO_W * h / w)))
        N = self.N
        self.L = np.zeros(N, np.float32)                   # mean luma 0-255
        self.SD = np.zeros(N, np.float32)                  # luma std
        self.SAT = np.zeros(N, np.float32)                 # mean HSV saturation 0-1
        self.SHARP = np.zeros(N, np.float32)               # high-pass energy / contrast (blur -> low)
        self.RGB = np.zeros((N, 3), np.float32)
        self.H = np.zeros((N, 3, 32), np.float32)
        self.HS = np.zeros((N, 64), np.float32)            # hue (16) x saturation (4) histogram
        self.Z = []
        self.Yc = []
        for i, fr in enumerate(frames):
            y = rrio.luma(fr)
            self.L[i] = y.mean()
            self.SD[i] = y.std()
            f = fr.astype(np.float32)
            mxc, mnc = f.max(-1), f.min(-1)
            self.SAT[i] = float(((mxc - mnc) / np.maximum(mxc, 1.0)).mean())
            self.SHARP[i] = float(np.abs(y - rrio.box_blur(y, 1)).mean()) / max(float(self.SD[i]), 8.0)
            self.RGB[i] = f.reshape(-1, 3).mean(0)
            self.H[i] = _hist(fr)
            hsv = rrio.rgb_to_hsv(fr).reshape(-1, 3)
            keep = hsv[:, 2] > 0.15
            if keep.any():
                hb = (hsv[keep, 0] // 22.5).astype(np.int64) % 16 * 4 + np.minimum(3, (hsv[keep, 1] * 4).astype(np.int64))
                self.HS[i] = np.bincount(hb, minlength=64)[:64] / float(len(hsv))
            yc = _coarse(y, self.ch)
            self.Yc.append(yc)
            self.Z.append(_z(yc))
        self.solid = self.SD < SOLID_SD
        self.near = (self.SD < NEAR_SD) & ((self.L > 200) | (self.L < 30))
        self.flat = self.solid | self.near
        # adjacent pairs (index i = pair (i-1, i))
        self.d = np.zeros(N, np.float32)
        self.c = np.ones(N, np.float32)
        self.m = np.zeros(N, np.float32)
        self.minv = np.full(N, 9.0, np.float32)
        self.h = np.zeros(N, np.float32)
        self.hinv = np.zeros(N, np.float32)
        self.hsv_d = np.zeros(N, np.float32)
        self.dx = np.zeros(N, np.float32)
        self.dy = np.zeros(N, np.float32)
        self.zoom = np.zeros(N, np.float32)
        self.hold = np.zeros(N, bool)
        self._cache = {}
        prev = None
        for i, fr in enumerate(frames):
            cur = fr.astype(np.int16)
            if prev is not None:
                self.d[i] = float(np.abs(cur - prev).mean())
                self.c[i] = float((self.Z[i] * self.Z[i - 1]).mean())
                self.h[i] = _hdist(self.H[i], self.H[i - 1])
                self.hinv[i] = _hdist(self.H[i], self.H[i - 1][:, ::-1])
                self.hsv_d[i] = float(0.5 * np.abs(self.HS[i] - self.HS[i - 1]).sum())
                if self.d[i] >= 0.25:
                    mm = mc_match(self.Z[i], self.Z[i - 1], want_inv=self.c[i] < 0.3)
                    self.m[i], self.minv[i] = mm["res"], mm["res_inv"]
                    self.dx[i], self.dy[i], self.zoom[i] = mm["dx"], mm["dy"], mm["zoom"]
            prev = cur
        # holds (repeated frames): pixel diff near the local noise floor, or structurally identical
        # (re-grained / re-encoded duplicates: correlation ~1 and no residual after matching)
        for i in range(1, N):
            lo, hi = max(1, i - 6), min(N, i + 7)
            lvl = float(np.percentile(self.d[lo:hi], 75))     # typical size of a real frame change here
            d = float(self.d[i])
            self.hold[i] = (d < 0.3 or (d < 0.3 * lvl and d < 4.0)
                            or ((1 - self.c[i]) < 0.0015 and self.m[i] < 0.04 and d < 0.5 * lvl))
        self.pd = 1.0 - np.abs(self.c)
        self.mpa = np.minimum(self.m, self.minv)
        self.g = np.sqrt(np.maximum(self.mpa, 0) * np.maximum(self.pd, 0))
        self.hpa = np.minimum(self.h, self.hinv)
        self.inv = (self.c < -0.5) & (self.minv < 0.75 * self.m)
        self.g[0] = 0
        self.hpa[0] = 0

    def pair(self, a, b):
        """Distance between any two frames: {'g','h','c','m'} (polarity-agnostic g/h)."""
        if b == a + 1:
            return {"g": float(self.g[b]), "h": float(self.hpa[b]), "c": float(self.c[b]), "m": float(self.mpa[b])}
        key = (a, b)
        if key not in self._cache:
            c = float((self.Z[a] * self.Z[b]).mean())
            mm = mc_match(self.Z[b], self.Z[a], want_inv=c < 0.3)
            m = min(mm["res"], mm["res_inv"])
            hp = min(_hdist(self.H[b], self.H[a]), _hdist(self.H[b], self.H[a][:, ::-1]))
            self._cache[key] = {"g": math.sqrt(max(m, 0) * max(1 - abs(c), 0)), "h": hp, "c": c, "m": m}
        return self._cache[key]


# ==================================================================================================
# cut detection
# ==================================================================================================
def _baseline(vals, ok, i, W, excl=1):
    lo, hi = max(1, i - W), min(len(vals), i + W + 1)
    idx = [j for j in range(lo, hi) if ok[j] and abs(j - i) > excl]
    if len(idx) < 3:
        return None
    return float(np.percentile(vals[idx], 35))


def _uniq_frames(fe, start, step, k=3, span=12):
    """Up to k distinct (non-hold, non-flat) frames walking from start in direction step."""
    out = []
    j = start
    while 0 <= j < fe.N and abs(j - start) < span and len(out) < k:
        if not fe.flat[j]:
            if step < 0:
                # frame j is distinct from j+1 if j+1 is not a hold of j
                if not out or not fe.hold[out[-1]]:
                    out.append(j)
                else:
                    out[-1] = j
            else:
                if not out or not fe.hold[j]:
                    out.append(j)
        j += step
    return out


def _hist_window(fe, i, k=3):
    """Histogram distance between the mean of k distinct frames before i and k from i on."""
    bef = _uniq_frames(fe, i - 1, -1, k)
    aft = _uniq_frames(fe, i, 1, k)
    if not bef or not aft:
        return 0.0
    a = fe.H[bef].mean(0)
    b = fe.H[aft].mean(0)
    return min(_hdist(a, b), _hdist(a, b[:, ::-1]))


def _refine_in_transitions(fe, cuts, info, look=4):
    """A cut proposed at the ONSET of a burn / dark / blur transition (same picture getting brighter,
    darker or softer) is moved to the first frame inside the transition that matches the next shot
    better than the previous one (Yaong: the burn starts f19, the new pose shows at f22).
    Returns (cuts, {cut: transition info})."""
    N = fe.N
    full = [0] + list(cuts) + [N]
    out, trans = [], {}
    for k, f in enumerate(cuts):
        n = full[k + 2]
        if f in info or f < 1:
            out.append(f)
            continue
        a = f - 1
        c_af = float((fe.Z[a] * fe.Z[f]).mean())
        dl = float(fe.L[f] - fe.L[a])
        typ = None
        if c_af > 0.5:
            if dl > 20:
                typ = "burn"
            elif dl < -20:
                typ = "dark"
            elif fe.SHARP[f] < 0.6 * fe.SHARP[a]:
                typ = "blur"
        if typ is None:
            out.append(f)
            continue
        b = None
        for j in range(f + look + 1, min(n, f + look + 6)):
            if not fe.hold[j] and not fe.flat[j]:
                b = j
                break
        if b is None:
            out.append(f)
            continue
        new = None
        for j in range(f, b):
            if fe.hold[j] or fe.flat[j]:
                continue
            if fe.pair(j, b)["g"] < fe.pair(a, j)["g"]:
                new = j
                break
        if new is None:
            new = f
        t_end = f
        for j in range(f, b):
            if abs(float(fe.L[j] - fe.L[a])) > 12 or fe.SHARP[j] < 0.75 * fe.SHARP[a]:
                t_end = j
        tinfo = {"transition": {"f0": f, "f1": max(t_end, new), "type": typ}}
        if new != f:
            tinfo["moved_from"] = f
        trans[new] = tinfo
        out.append(new)
    return sorted(set(out)), trans


def activity_zones(fe, fps, thr=0.28):
    """Runs where most frame changes are big (whip pans, strobe cutting, fast action): read every
    frame there, detectors are least reliable."""
    N = fe.N
    W = max(4, int(round(0.4 * fps)))
    use = np.zeros(N, bool)
    use[1:] = ~fe.hold[1:] & ~fe.flat[1:] & ~fe.flat[:-1]
    big = use & (fe.g >= thr)  # noqa
    hot = np.zeros(N, bool)
    for i in range(1, N):
        lo, hi = max(1, i - W), min(N, i + W + 1)
        nu = int(use[lo:hi].sum())
        if nu >= 4 and big[lo:hi].sum() >= 0.55 * nu:
            hot[i] = True
    zones = []
    for s0, e0 in _runs_bool(hot):
        if e0 - s0 >= max(4, int(0.3 * fps)):
            zones.append({"f0": int(s0), "f1": int(e0 - 1), "big_changes": int(big[s0:e0].sum())})
    return zones


def detect_cuts(fe, sensitivity=1.0):
    """Propose cuts. Returns dict with cuts (list of starts), flashes, solids, inverts, maybes, scores."""
    N, fps = fe.N, fe.fps
    sens = max(0.2, float(sensitivity))
    W = max(8, int(round(0.45 * fps)))
    # pairs usable for baselines: not holds, neither frame flat
    ok = np.zeros(N, bool)
    ok[1:] = ~fe.hold[1:] & ~fe.flat[1:] & ~fe.flat[:-1]
    gall = fe.g[ok] if ok.any() else np.array([0.1])
    hall = fe.hpa[ok] if ok.any() else np.array([0.02])
    g_glob, h_glob = float(np.median(gall)), float(np.median(hall))
    Bg = np.zeros(N, np.float32)
    Bh = np.zeros(N, np.float32)
    Bw = np.zeros(N, np.float32)
    S = np.zeros(N, np.float32)
    HW = np.zeros(N, np.float32)
    T = 2.2 / sens
    for i in range(1, N):
        HW[i] = _hist_window(fe, i)
    w_glob = float(np.median(HW[ok])) if ok.any() else 0.03
    for i in range(1, N):
        bg = _baseline(fe.g, ok, i, W)
        bh = _baseline(fe.hpa, ok, i, W)
        bw = _baseline(HW, ok, i, W)
        # local baselines, capped so a dense run of cuts (burst/strobe) cannot raise its own bar
        Bg[i] = min(g_glob if bg is None else bg, max(0.15, 3 * g_glob))
        Bh[i] = min(h_glob if bh is None else bh, max(0.04, 3 * h_glob))
        Bw[i] = min(w_glob if bw is None else bw, max(0.06, 3 * w_glob))
        if fe.hold[i]:
            continue
        rg = fe.g[i] / max(Bg[i], 0.06)
        rh = fe.hpa[i] / max(Bh[i], 0.012)
        S[i] = math.sqrt(max(rg, 0) * max(rh, 0))
    # peakiness: a cut is a one-time step, so it stands out from the nearest non-hold pairs on both
    # sides; sustained change (whip pans, fast foreground motion, morphs) does not
    usable = [j for j in range(1, N) if ok[j]]
    pos = {j: k for k, j in enumerate(usable)}
    P = np.zeros(N, np.float32)
    for i in usable:
        k = pos[i]
        nb = [usable[q] for q in (k - 2, k - 1, k + 1, k + 2) if 0 <= q < len(usable) and abs(usable[q] - i) <= W]
        nb = [j for j in nb if not (fe.g[j] >= 0.6 and fe.hpa[j] >= 0.05)]
        if not nb:
            P[i] = 3.0
            continue
        pg = fe.g[i] / max(max(fe.g[j] for j in nb), 0.03)
        ph = fe.hpa[i] / max(max(fe.hpa[j] for j in nb), 0.008)
        P[i] = math.sqrt(max(pg, 0) * max(ph, 0))
    if os.environ.get("RR_DEBUG"):
        print("   i      d      g      h     hw     Bg     Bh     Bw   S/T    c     P")
        for i in range(1, N):
            if fe.hold[i] or (S[i] < 0.6 * T and fe.g[i] < 0.5):
                continue
            print(f"{i:4d} {fe.d[i]:6.1f} {fe.g[i]:6.3f} {fe.hpa[i]:6.3f} {HW[i]:6.3f} {Bg[i]:6.3f} {Bh[i]:6.3f} "
                  f"{Bw[i]:6.3f} {S[i] / T:5.2f} {fe.c[i]:6.3f} {P[i]:5.2f}{'  FLAT' if fe.flat[i] or fe.flat[i - 1] else ''}")

    def same(a, b):
        """a, b content frames of the same shot?"""
        p = fe.pair(a, b)
        bgl = max(float(Bg[min(b, N - 1)]), 0.05)
        bhl = max(float(Bh[min(b, N - 1)]), 0.01)
        return p["g"] <= max(0.30, 1.8 * bgl) / sens ** 0.5 and p["h"] <= max(0.07, 3.0 * bhl) / sens ** 0.5

    def is_cut_pair(i):
        if fe.hold[i] or fe.flat[i] or fe.flat[i - 1]:
            return False
        g, h = float(fe.g[i]), float(fe.hpa[i])
        # strong: big structural + colour change that is either a clean break (low global correlation),
        # a peak over its neighbours, or very large; sustained whip/foreground motion fails all three
        strong = ((g >= 0.55 / sens and h >= 0.06 / sens and (fe.c[i] < 0.4 or P[i] >= 1.2 or g >= 0.65 / sens))
                  or (g >= 0.45 / sens and h >= 0.3 / sens))
        if fe.inv[i]:
            return strong          # a polarity flip of the same picture is an effect, not a cut
        return strong or (S[i] >= T and P[i] >= 1.3 / sens ** 0.5 and g >= 0.2 / sens ** 0.5
                          and h >= 0.02 / sens ** 0.5)

    cand = {i for i in range(1, N) if is_cut_pair(i)}
    flashes, solids, cut_info = [], [], {}

    # --- flat (solid / near-white / near-black) runs: flash between same-shot frames or a cut
    runs = _runs_bool(fe.flat)
    max_flat = max(8, int(round(0.3 * fps)))
    for s, e in runs:            # frames s..e-1
        L = float(fe.L[s:e].mean())
        rgb = fe.RGB[s:e].mean(0)
        hexc = "#%02x%02x%02x" % tuple(int(round(v)) for v in rgb)
        kind = "white" if L > 200 else "black" if L < 35 else "solid"
        solids.append({"f0": s, "f1": e - 1, "kind": kind, "color": hexc, "luma": round(L / 255, 3)})
        for j in range(s, min(e + 1, N)):
            cand.discard(j)
        a, b = s - 1, e
        if a < 0 or b >= N:
            if a >= 0 and b >= N:
                flashes.append({"f0": s, "f1": e - 1, "type": kind, "note": "ends the video"})
            elif a < 0 and b < N:
                flashes.append({"f0": s, "f1": e - 1, "type": kind, "note": "opens the video"})
            continue
        if e - s > max_flat:
            cand.add(s)
            cand.add(b)
            cut_info[s] = {"type": "solid_segment", "solid": [s, e - 1]}
            cut_info[b] = {"type": "after_solid_segment", "solid": [s, e - 1]}
            continue
        # the flash may decay over 1-2 more frames (same picture, washed out): bridge to e+k
        back_to = None
        for k in range(0, 3):
            bb = b + k
            if bb >= N or fe.flat[bb]:
                break
            pq = fe.pair(a, bb)
            if same(a, bb) or (k > 0 and pq["g"] <= 0.22):
                back_to = bb
                break
        if back_to is not None:
            flashes.append({"f0": s, "f1": back_to - 1, "type": kind, "note": "same shot on both sides"})
            for j in range(s, back_to + 1):
                cand.discard(j)
        else:
            cand.add(s)
            cut_info[s] = {"type": f"{kind}_flash", "flash": [s, e - 1]}
            flashes.append({"f0": s, "f1": e - 1, "type": kind, "note": "hides/marks a cut", "cut_at": s})

    # --- spikes that come back to the same shot within MAX_FLASH frames: flash / insert, not a cut
    for i in sorted(cand):
        if i not in cand or i in cut_info:
            continue
        for k in range(1, MAX_FLASH + 1):
            b = i + k
            if b >= N:
                break
            if fe.flat[b]:
                continue
            # the spike must jump back: b differs from the run's last frame (not a hold, real change)
            back = fe.pair(b - 1, b)
            jump = (not fe.hold[b]) and (back["g"] >= 0.5 * fe.g[i] or back["h"] >= 0.5 * fe.hpa[i])
            if jump and same(i - 1, b):
                p = fe.pair(i - 1, i)
                dl = float(fe.L[i:b].mean() - fe.L[i - 1])
                typ = ("invert" if p["c"] < -0.5 else "exposure" if (p["c"] > 0.6 and abs(dl) > 18)
                       else "insert")
                flashes.append({"f0": i, "f1": b - 1, "type": typ, "note": "returns to the same shot",
                                "luma_jump": round(dl / 255, 3)})
                for j in range(i, b + 1):
                    cand.discard(j)
                break

    # --- adjacent candidates: a single in-between frame that is a blend of both sides is a dissolve
    #     frame, not a 1-frame shot (ghost blends, mixes)
    for i in sorted(cand):
        if i in cand and (i + 1) in cand and i not in cut_info and (i + 1) not in cut_info:
            a, mid, b = fe.Yc[i - 1], fe.Yc[i], fe.Yc[i + 1] if i + 1 < N else None
            if b is None:
                continue
            best, alpha = 1e9, 0.5
            for al in (0.2, 0.35, 0.5, 0.65, 0.8):
                e_ = float(np.abs(mid - (al * a + (1 - al) * b)).mean())
                if e_ < best:
                    best, alpha = e_, al
            ref = min(float(np.abs(mid - a).mean()), float(np.abs(mid - b).mean()))
            if best < 0.6 * ref:
                keep = i + 1 if alpha >= 0.5 else i
                drop = i if keep == i + 1 else i + 1
                cand.discard(drop)
                cut_info[keep] = {"type": "blend", "blend_frame": i, "alpha_old": alpha}

    # --- polarity inverts (relative to the previous frame); toggled state per shot
    inv_frames = [i for i in range(1, N) if fe.inv[i] and not fe.flat[i] and not fe.flat[i - 1]]

    cuts, trans = _refine_in_transitions(fe, sorted(cand), cut_info)
    moved = {}
    for f, tinfo in trans.items():
        cut_info[f] = dict(cut_info.get(f, {}), type=cut_info.get(f, {}).get("type", "in_transition"), **tinfo)
        if "moved_from" in tinfo:
            moved[f] = tinfo["moved_from"]
    cand = set(cuts)
    maybes = []
    for i in range(1, N):
        if i in cand or fe.hold[i] or fe.flat[i] or fe.flat[i - 1]:
            continue
        if ((S[i] >= 0.75 * T and P[i] >= 1.0) or (fe.g[i] >= 0.45 and fe.hpa[i] >= 0.04)) \
                and fe.g[i] >= 0.15 and fe.hpa[i] >= 0.015:
            if any(fl["f0"] <= i <= fl["f1"] + 1 for fl in flashes):
                continue
            maybes.append({"f": i, "score": round(float(S[i] / T), 2)})
    return {"cuts": cuts, "info": cut_info, "flashes": sorted(flashes, key=lambda x: x["f0"]),
            "solids": solids, "inv_frames": inv_frames, "maybes": maybes, "S": S, "T": T, "Bg": Bg, "Bh": Bh,
            "P": P, "HW": HW, "moved": moved}


def cut_confidence(fe, det, i):
    """0-1 confidence for a cut starting at frame i."""
    N = fe.N
    info = det["info"].get(i, {})
    if info.get("type", "").endswith("flash") or "solid" in info.get("type", ""):
        a = i - 1
        b = (info.get("flash") or info.get("solid") or [i, i])[1] + 1
        if a < 0 or b >= N:
            return 0.5
        p = fe.pair(a, b)
        return round(clamp01(0.4 + p["g"] + 2 * p["h"]), 2)
    S, T, P = float(det["S"][i]), det["T"], float(det["P"][i])
    g, h = float(fe.g[i]), float(fe.hpa[i])
    conf = (0.25 + 0.3 * clamp01((S / T - 1) / 1.5) + 0.25 * clamp01((g - 0.25) / 0.4)
            + 0.2 * clamp01((P - 1.3) / 1.2))
    # histogram before/after windows (3 content frames each) confirm a persistent change
    bef = [j for j in range(max(0, i - 4), i) if not fe.flat[j]][-3:]
    aft = [j for j in range(i, min(N, i + 5)) if not fe.flat[j]][:3]
    if bef and aft:
        hw = _hdist(fe.H[bef].mean(0), fe.H[aft].mean(0))
        conf += 0.1 if hw > 0.08 else -0.15 if hw < 0.025 else 0
    if g >= 0.55 and h >= 0.06:
        conf = max(conf, 0.9)
    return round(clamp01(conf), 2)


# ==================================================================================================
# segments, bursts, cadence, motion, look
# ==================================================================================================
def build_cuts(starts, N, min_cut, conf, info):
    """Starts -> contiguous cut list; runs of >= 3 consecutive segments shorter than min_cut become one
    'burst' cut with its sub-cuts listed."""
    starts = sorted(set([0] + [s for s in starts if 0 < s < N]))
    segs = [(s, (starts[k + 1] if k + 1 < len(starts) else N) - 1) for k, s in enumerate(starts)]
    out = []
    k = 0
    while k < len(segs):
        j = k
        while j < len(segs) and segs[j][1] - segs[j][0] + 1 < min_cut:
            j += 1
        if j - k >= 3:
            f0, f1 = segs[k][0], segs[j - 1][1]
            out.append({"f0": f0, "f1": f1, "kind": "burst",
                        "sub_cuts": [s for s, _ in segs[k:j]],
                        "sub_lengths": [e - s + 1 for s, e in segs[k:j]]})
            k = j
        else:
            s, e = segs[k]
            out.append({"f0": s, "f1": e, "kind": "cut" if s > 0 else "start"})
            k += 1
    for c in out:
        c["confidence"] = 1.0 if c["f0"] == 0 else conf.get(c["f0"], 0.5)
        if c["kind"] == "burst":
            subs = [conf.get(s, 0.5) for s in c["sub_cuts"][1:]]
            c["sub_confidence"] = [round(v, 2) for v in subs]
        bi = info.get(c["f0"])
        if bi:
            c["boundary"] = bi
    return out


_STD_SRC = [12, 15, 18, 20, 23.976, 24, 25, 29.97, 30, 48, 50, 59.94, 60]


def cadence(fe, f0, f1, fps):
    """Unique frames, source-fps estimate and hold pattern of frames f0..f1."""
    n = f1 - f0 + 1
    holds = [bool(fe.hold[i]) for i in range(f0 + 1, f1 + 1)]
    unique = 1 + sum(1 for h in holds if not h)
    lens, cur = [], 1
    for h in holds:
        if h:
            cur += 1
        else:
            lens.append(cur)
            cur = 1
    lens.append(cur)
    flen = max(6, int(round(0.25 * fps)))
    freezes = []
    pos = f0
    for L_ in lens:
        if L_ >= flen:
            freezes.append([pos, pos + L_ - 1])
        pos += L_
    core = [L_ for L_ in lens if L_ < flen]
    # drop the partial first/last hold (cut can start mid-pattern)
    inner = core[1:-1] if len(core) > 4 else core
    mean_len = float(np.mean(inner)) if inner else 1.0
    src = fps / mean_len if mean_len > 0 else fps
    snap = min(_STD_SRC, key=lambda s: abs(s - src))
    src_snap = snap if abs(snap - src) <= 0.07 * snap else round(src, 2)
    # blend frames: frame ~ average of its neighbours while the neighbours differ (frame-blend retime / dissolve)
    blends = 0
    moving = 0
    for i in range(f0 + 1, f1):
        if fe.hold[i] or fe.hold[i + 1] or fe.flat[i]:
            continue
        a, mid, b = fe.Yc[i - 1], fe.Yc[i], fe.Yc[i + 1]
        ref = min(float(np.abs(mid - a).mean()), float(np.abs(mid - b).mean()))
        if ref < 2.0:
            continue
        moving += 1
        if float(np.abs(mid - 0.5 * (a + b)).mean()) < 0.45 * ref:
            blends += 1
    ratio = unique / n
    cnt = {}
    for L_ in inner:
        cnt[L_] = cnt.get(L_, 0) + 1
    pat = ",".join(str(x) for x in lens[:12]) + ("..." if len(lens) > 12 else "")
    fr = float(fps)
    cv = float(np.std(inner) / np.mean(inner)) if inner else 0.0
    if n < 4:
        kind = "short"
    elif freezes and sum(b - a + 1 for a, b in freezes) >= 0.6 * n:
        kind = "freeze"
    elif ratio >= 0.84:
        kind = "native"
    elif fr >= 50 and 2.3 <= mean_len <= 2.7 and cnt.get(2, 0) and cnt.get(3, 0):
        kind = "pulldown_24in60"
    elif 27 <= fr <= 31 and 1.15 <= mean_len <= 1.35 and set(cnt) <= {1, 2}:
        kind = "pulldown_24in30"
    elif mean_len >= 1.35 and cv <= 0.45:
        kind = "stepped"
    else:
        kind = "mixed"
    note = ""
    if kind == "mixed":
        note = ("irregular holds (%s): overlays animating at a different rate than the footage, a retime, "
                "or a partial freeze - count on the sheet" % pat)
    if kind == "native" and fr >= 50:
        note = ("every frame unique at %g fps: native high-frame-rate, interpolated slow-mo, a digital move "
                "or an overlay animating every frame" % fr)
    if moving >= 4 and blends >= 0.3 * moving:
        note = (note + "; " if note else "") + f"{blends}/{moving} moving frames look like blends of their neighbours (frame-blend retime or dissolve)"
    return {"unique": unique, "of": n, "ratio": round(ratio, 3), "src_fps": src_snap, "pattern": kind,
            "holds": pat, "freezes": freezes, "blend_frames": blends, "note": note}


def motion(fe, f0, f1, fps, an_w):
    """Motion energy and global camera motion of frames f0..f1 (from the block matcher)."""
    idx = [i for i in range(f0 + 1, f1 + 1) if not fe.hold[i] and not fe.flat[i] and not fe.flat[i - 1]]
    if not idx:
        return {"energy": 0.0, "energy_unique": 0.0, "pan_x": 0.0, "pan_y": 0.0, "zoom": 0.0, "shake": 0.0,
                "move": "static" if f1 > f0 else "n/a"}
    span = list(range(f0 + 1, f1 + 1))
    energy = float(np.mean(fe.d[span])) if span else 0.0
    eu = float(np.mean(fe.d[idx]))
    sc = AN_W / CO_W / an_w                     # coarse px -> fraction of the picture width
    dx = fe.dx[idx] * sc
    dy = fe.dy[idx] * sc
    n_t = (f1 - f0) / float(fps) if f1 > f0 else 1.0
    pan_x = float(dx.sum() / n_t) if n_t else 0.0     # fraction of width per second
    pan_y = float(dy.sum() / n_t) if n_t else 0.0
    zoom = float(fe.zoom[idx].sum() / n_t) if n_t else 0.0  # relative scale change per second
    if len(dx) >= 3:
        k = np.ones(3) / 3
        sx = dx - np.convolve(dx, k, mode="same")
        sy = dy - np.convolve(dy, k, mode="same")
        shake = float(np.sqrt(sx ** 2 + sy ** 2).mean())
    else:
        shake = 0.0
    resid = float(np.mean(fe.mpa[idx]))
    move = "static"
    if shake > 0.012:
        move = "shake"
    elif abs(zoom) > 0.08:
        move = "push_in" if zoom > 0 else "pull_out"
    elif abs(pan_x) > 0.08 and abs(pan_x) >= abs(pan_y):
        move = "pan"
    elif abs(pan_y) > 0.08:
        move = "tilt"
    elif shake > 0.005:
        move = "handheld"
    elif eu > 6:
        move = "subject_motion"
    return {"energy": round(energy, 2), "energy_unique": round(eu, 2), "pan_x": round(pan_x, 3),
            "pan_y": round(pan_y, 3), "zoom": round(zoom, 3), "shake": round(shake, 4),
            "residual": round(resid, 3), "move": move}


_HUES = [(15, "red"), (45, "orange"), (70, "yellow"), (160, "green"), (195, "cyan"), (255, "blue"),
         (290, "purple"), (335, "magenta"), (360, "red")]


def hue_name(h):
    for lim, name in _HUES:
        if h < lim:
            return name
    return "red"


def look_stats(frames):
    """Colour/tone stats of a list of uint8 RGB frames (analysis res)."""
    f = np.stack([fr.astype(np.float32) / 255.0 for fr in frames])
    lum = f[..., 0] * 0.2126 + f[..., 1] * 0.7152 + f[..., 2] * 0.0722
    mx, mn = f.max(-1), f.min(-1)
    sat = np.where(mx > 0.04, (mx - mn) / np.maximum(mx, 1e-6), 0.0)
    p = np.percentile(lum, [1, 5, 50, 95, 99])
    hsv = rrio.rgb_to_hsv(f.reshape(-1, f.shape[-2], 3)).reshape(-1, 3)
    wgt = hsv[:, 1] * hsv[:, 2] * ((hsv[:, 1] > 0.2) & (hsv[:, 2] > 0.15))
    dom, dom_share = None, 0.0
    if wgt.sum() > 0.002 * len(wgt):
        hist = np.bincount((hsv[:, 0] // 10).astype(np.int64) % 36, weights=wgt, minlength=36)
        sm = hist + 0.5 * (np.roll(hist, 1) + np.roll(hist, -1))
        k = int(sm.argmax())
        dom = k * 10 + 5
        dom_share = float(sm[k] / (2 * hist.sum()))
    colorful_px = float((sat > 0.25).mean())
    sat_mean = float(sat.mean())
    bw = sat_mean < 0.06 and colorful_px < 0.03
    accent_only = (not bw) and sat_mean < 0.1 and 0.003 < colorful_px < 0.2 and dom is not None
    bimodal = float(((lum < 0.12) | (lum > 0.88)).mean())
    rgbm = f.reshape(-1, 3).mean(0)
    # dark bars inside this cut (letterboxed shot inside a full-frame edit)
    rowmax = lum.mean(2).max(0)
    colmax = lum.mean(1).max(0)
    def run(v):
        k = 0
        while k < len(v) // 3 and v[k] < 0.04:
            k += 1
        return k
    bars = {"top": run(rowmax) / len(rowmax), "bottom": run(rowmax[::-1]) / len(rowmax),
            "left": run(colmax) / len(colmax), "right": run(colmax[::-1]) / len(colmax)}
    return {
        "mean_rgb": [round(float(v), 3) for v in rgbm],
        "luma_mean": round(float(lum.mean()), 3),
        "luma_p1_p5_p50_p95_p99": [round(float(v), 3) for v in p],
        "luma_p1_p50_p99": [round(float(p[0]), 3), round(float(p[2]), 3), round(float(p[4]), 3)],
        "contrast_p5_p95": round(float(p[3] - p[1]), 3),
        "sat_mean": round(sat_mean, 3),
        "colorful_share": round(colorful_px, 3),
        "bw": bool(bw),
        "accent_only": bool(accent_only),
        "threshold_look": bool(bimodal > 0.8),
        "bimodal_share": round(bimodal, 3),
        "warmth": round(float(rgbm[0] - rgbm[2]), 3),
        "tint_g": round(float(rgbm[1] - 0.5 * (rgbm[0] + rgbm[2])), 3),
        "dominant_hue": dom, "dominant_hue_name": hue_name(dom) if dom is not None else None,
        "dominant_hue_share": round(dom_share, 3),
        "bars": {k: round(v, 3) for k, v in bars.items() if v > 0},
    }


def grain_stats(y):
    """Spatial noise of a native-res luma crop: robust std of the high-pass in the flattest blocks."""
    y = y.astype(np.float32)
    hp = y - rrio.box_blur(y, 1)
    B = 8
    H, W = (y.shape[0] // B) * B, (y.shape[1] // B) * B
    if H < B or W < B:
        return None
    blk_std = y[:H, :W].reshape(H // B, B, W // B, B).std((1, 3))
    hp_std = hp[:H, :W].reshape(H // B, B, W // B, B).std((1, 3))
    flat = blk_std <= np.percentile(blk_std, 40)
    if not flat.any():
        return None
    return float(np.median(hp_std[flat]))


def text_candidates(fr, max_boxes=5):
    """Rough boxes of overlay-text-like regions: near-white (or near-black) strokes packed next to
    strong edges, in cells, merged with 8-connectivity. Returns [{'x','y','w','h','polarity','score'}]
    as fractions of the analysed picture. A hint for where to look, not OCR: verify on the sheets."""
    f = fr.astype(np.float32)
    y = rrio.luma(fr)
    edge = np.abs(y - rrio.box_blur(y, 2)) > 30
    near_edge = rrio.dilate(edge, 5)
    lo, hi = f.min(-1), f.max(-1)
    H, W = y.shape
    C = max(8, W // 48)
    gh, gw = H // C, W // C
    if gh < 2 or gw < 2:
        return []
    ed = edge[:gh * C, :gw * C].reshape(gh, C, gw, C).mean((1, 3))
    out = []
    for pol, stroke in (("white", lo >= 200), ("black", hi <= 45)):
        st = stroke[:gh * C, :gw * C].reshape(gh, C, gw, C).mean((1, 3))
        m = (stroke & near_edge)[:gh * C, :gw * C].reshape(gh, C, gw, C).mean((1, 3))
        txt = (m >= 0.08) & (ed >= 0.06) & (st <= 0.85)
        seen = np.zeros_like(txt)
        for sy in range(gh):
            for sx in range(gw):
                if not txt[sy, sx] or seen[sy, sx]:
                    continue
                stack, comp = [(sy, sx)], []
                seen[sy, sx] = True
                while stack:
                    cy, cx = stack.pop()
                    comp.append((cy, cx))
                    for dy in (-1, 0, 1):
                        for dx in (-2, -1, 0, 1, 2):
                            ny, nx = cy + dy, cx + dx
                            if 0 <= ny < gh and 0 <= nx < gw and txt[ny, nx] and not seen[ny, nx]:
                                seen[ny, nx] = True
                                stack.append((ny, nx))
                if len(comp) < 3:
                    continue
                ys = [q[0] for q in comp]
                xs = [q[1] for q in comp]
                bx0, bx1, by0, by1 = min(xs) * C, (max(xs) + 1) * C, min(ys) * C, (max(ys) + 1) * C
                area = (bx1 - bx0) * (by1 - by0)
                fill = len(comp) * C * C / area
                if area > 0.45 * W * H or fill < 0.25:
                    continue
                sc = float(np.mean([m[q] for q in comp]) * min(1.0, fill * 1.5))
                if pol == "black" and sc < 0.25:      # dark strokes: mostly hair/shadow edges unless strong
                    continue
                out.append({"x": round(bx0 / W, 3), "y": round(by0 / H, 3), "w": round((bx1 - bx0) / W, 3),
                            "h": round((by1 - by0) / H, 3), "polarity": pol, "score": round(sc, 2),
                            "cells": len(comp)})
    out.sort(key=lambda b: -b["score"] * b["cells"])
    return out[:max_boxes]


# ==================================================================================================
# drawing helpers for sheets
# ==================================================================================================
def _bar(img, color, h=5):
    img[:h] = color
    return img


def _vline(img, x, y0, y1, color, w=1):
    H, W = img.shape[:2]
    x = int(x)
    if 0 <= x < W:
        img[max(0, int(y0)):min(H, int(y1)), x:min(W, x + w)] = color


def _rect(img, x0, y0, x1, y1, color):
    H, W = img.shape[:2]
    img[max(0, int(y0)):min(H, int(y1)), max(0, int(x0)):min(W, int(x1))] = color


def _frame_rect(img, x0, y0, x1, y1, color, t=2):
    _rect(img, x0, y0, x1, y0 + t, color)
    _rect(img, x0, y1 - t, x1, y1, color)
    _rect(img, x0, y0, x0 + t, y1, color)
    _rect(img, x1 - t, y0, x1, y1, color)


def _plot(img, xs, vals, y0, h, vmax, color):
    """Polyline of vals (0..vmax) in the band [y0, y0+h) at x positions xs; filled per column."""
    if not len(vals):
        return
    v = np.clip(np.asarray(vals, np.float64) / vmax, 0, 1)
    ys = (y0 + h - 1 - v * (h - 1)).astype(int)
    for k in range(len(xs)):
        x = int(xs[k])
        ya = ys[k]
        yb = ys[k - 1] if k else ya
        _vline(img, x, min(ya, yb), max(ya, yb) + 1, color, 1)
        if k + 1 < len(xs):
            xn = int(xs[k + 1])
            img[ya, x:max(x + 1, xn)] = color if 0 <= ya < img.shape[0] else img[0, 0]


# ==================================================================================================
# main
# ==================================================================================================
def _even_crop(c):
    """Decode crop aligned to even pixels (odd crops force a slow full-frame RGB conversion in ffmpeg);
    shrinks by at most 1 px per side. Used only for analysis/sheets, never for reported geometry."""
    x0, y0 = c["x"] + (c["x"] % 2), c["y"] + (c["y"] % 2)
    x1, y1 = c["x"] + c["w"], c["y"] + c["h"]
    x1 -= (x1 - x0) % 2
    y1 -= (y1 - y0) % 2
    if x1 - x0 < 8 or y1 - y0 < 8:
        return (c["x"], c["y"], c["w"], c["h"])
    return (x0, y0, x1 - x0, y1 - y0)


def parse_span(s):
    a, b = s.split(":")
    return int(a), int(b)


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Deconstruct a reference video (free): cut proposals, flashes, window/letterbox, cadence, "
                    "motion, look stats, every-frame contact sheets -> W/analysis/analysis.json + W/sheets/.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("\n", 2)[2])
    ap.add_argument("W", nargs="?", help="workspace dir (reads W/ref/ref.mp4; writes W/analysis, W/sheets)")
    ap.add_argument("--ref", help="video to analyse instead of W/ref/ref.mp4 (W defaults to the current dir)")
    ap.add_argument("--min-cut", type=int, default=None,
                    help="segments shorter than this (frames) in runs of >=3 form one 'burst' cut "
                         "(default round(0.17 s * fps), min 3)")
    ap.add_argument("--sensitivity", type=float, default=1.0,
                    help="cut sensitivity multiplier: >1 more proposals (strobe/whip refs), <1 fewer (grainy refs)")
    ap.add_argument("--max-seconds", type=float, default=None, help="analyse only the first N seconds")
    ap.add_argument("--no-every-frame", action="store_true", help="skip the every-frame pages")
    ap.add_argument("--detail", action="append", default=[], metavar="A:B",
                    help="sheet(s) of frames A..B inclusive: <= 12 frames per sheet, native pixels when the region "
                         "fits 4 across, spans > 48 frames are sampled; repeatable")
    ap.add_argument("--detail-crop", default=None, metavar="x,y,w,h",
                    help="region for every --detail, in display pixels (default: the picture area)")
    ap.add_argument("--review-size", action="store_true",
                    help="cap every sheet at 125 KB so 4 fit in one image_paths call (512 KiB)")
    ap.add_argument("--page-bytes", type=int, default=None, help="explicit byte cap per sheet (default 500000)")
    ap.add_argument("--window", default=None, metavar="x,y,w,h", help="force the picture area (skip detection)")
    ap.add_argument("--no-window", action="store_true", help="analyse the full frame even if a window is found")
    ap.add_argument("--cuts-from", default=None, metavar="JSON",
                    help="use the cut list (cuts[].f0) of this analysis.json / breakdown.json instead of detecting")
    ap.add_argument("--tile-w", type=int, default=None, help="every-frame tile width (default 194 landscape, 154 portrait)")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    t_start = time.time()
    timing = {}
    if not args.W and not args.ref:
        ap.error("give a workspace W (with ref/ref.mp4) or --ref PATH")
    W = os.path.abspath(args.W or ".")
    src = os.path.abspath(args.ref) if args.ref else os.path.join(W, "ref", "ref.mp4")
    if not os.path.isfile(src):
        print(f"analyze_ref: error: reference not found: {src}", file=sys.stderr)
        return 1
    try:
        info = rrio.probe(src)
    except Exception as e:  # noqa: BLE001
        print(f"analyze_ref: error: cannot probe {src}: {e}", file=sys.stderr)
        return 1
    if not info.get("has_video") or not info.get("fps"):
        print(f"analyze_ref: error: {src} has no usable video stream", file=sys.stderr)
        return 1
    fps = info["fps"]
    fpsf = float(fps)
    source_timing = rrio.frame_timestamps(src, info)
    if source_timing["duration_s"] is None:
        raise RuntimeError("final decoded frame endpoint unavailable; full timeline analysis cannot be claimed")
    boundaries = source_timing["relative_pts"] + [source_timing["duration_s"]]
    n_hdr = int(info.get("nb_frames") or 0)
    n_lim = None
    if args.max_seconds:
        n_lim = max(2, sum(t < args.max_seconds for t in source_timing["relative_pts"]))
    adir, sdir = os.path.join(W, "analysis"), os.path.join(W, "sheets")
    os.makedirs(adir, exist_ok=True)
    os.makedirs(sdir, exist_ok=True)
    page_bytes = args.page_bytes or (125_000 if args.review_size else 500_000)
    say = (lambda *a: None) if args.quiet else log

    # ---------------------------------------------------------------- canvas
    t0 = time.time()
    n_scan = n_lim or n_hdr or int((info.get("duration") or 0) * fpsf) or 3000
    if args.window:
        try:
            x, y, w, h = [int(v) for v in args.window.split(",")]
            if w < 8 or h < 8 or x < 0 or y < 0 or x + w > info["w"] or y + h > info["h"]:
                raise ValueError
        except ValueError:
            print(f"analyze_ref: error: --window wants x,y,w,h inside the {info['w']}x{info['h']} frame, "
                  f"got {args.window!r}", file=sys.stderr)
            return 1
        canvas = {"kind": "window" if (w, h) != (info["w"], info["h"]) else "full",
                  "crop": {"x": x, "y": y, "w": w, "h": h}, "window": {"x": x, "y": y, "w": w, "h": h, "radius": 0},
                  "letterbox": None, "radius": 0, "confidence": 1.0, "method": "user --window", "notes": []}
    else:
        canvas, _ = detect_canvas(src, info, n_scan)
        canvas["method"] = "max/min luma over sampled frames"
    full_crop = {"x": 0, "y": 0, "w": info["w"], "h": info["h"]}
    if args.no_window:
        canvas["notes"].append(f"--no-window: analysing the full frame (detected {canvas['kind']} ignored)")
        canvas["crop_used"] = full_crop
    else:
        canvas["crop_used"] = canvas["crop"]
    crop = canvas["crop_used"]
    crop_t = None if crop == full_crop else _even_crop(crop)
    timing["canvas"] = round(time.time() - t0, 2)

    # ---------------------------------------------------------------- features
    t0 = time.time()
    an_w = min(AN_W, crop["w"])
    frames = [fr for _, fr in rrio.read_frames(src, count=n_lim, scale_w=an_w, crop=crop_t, info=info)]
    N = len(frames)
    expected_frames = min(n_lim or source_timing["frames"], source_timing["frames"])
    if N != expected_frames:
        raise RuntimeError(f"decoded frame coverage differs: {N} images versus {expected_frames} timestamps")
    if N < 2:
        print(f"analyze_ref: error: decoded only {N} frame(s) from {src} - a still image? analyze_ref needs a "
              "video (route photo-series refs as STILL)", file=sys.stderr)
        return 1
    fe = Features(frames, fpsf)
    timing["features"] = round(time.time() - t0, 2)

    # ---------------------------------------------------------------- cuts
    t0 = time.time()
    min_cut = args.min_cut or max(3, int(round(0.17 * fpsf)))
    det = detect_cuts(fe, args.sensitivity)
    conf = {i: cut_confidence(fe, det, det["moved"].get(i, i)) for i in det["cuts"]}
    zones = activity_zones(fe, fpsf)
    cuts_source = "detector"
    if args.cuts_from:
        try:
            ext = rrio.load_json(args.cuts_from)
            ext_cuts = ext["cuts"] if isinstance(ext, dict) else ext
            ext_cuts = sorted(ext_cuts, key=lambda c: int(c["f0"] if "f0" in c else c["start"]))
        except Exception as e:  # noqa: BLE001
            print(f"analyze_ref: error: cannot read cuts from {args.cuts_from}: {e}", file=sys.stderr)
            return 1
        cut_list = []
        starts_ext = []
        for c in ext_cuts:
            f0 = int(c["f0"] if "f0" in c else c["start"])
            if 0 <= f0 < N and f0 not in starts_ext:
                starts_ext.append(f0)
                cc = {"f0": f0, "kind": "cut" if f0 > 0 else "start", "confidence": 1.0,
                      "source_id": c.get("id")}
                subs = c.get("sub_cuts")
                if isinstance(subs, list) and len(subs) > 1:
                    cc["kind"] = "burst"
                    cc["sub_cuts"] = [int(v) for v in subs]
                cut_list.append(cc)
        if not cut_list or cut_list[0]["f0"] != 0:
            cut_list.insert(0, {"f0": 0, "kind": "start", "confidence": 1.0})
        for k, c in enumerate(cut_list):
            c["f1"] = (cut_list[k + 1]["f0"] if k + 1 < len(cut_list) else N) - 1
            if c["kind"] == "burst":
                c["sub_cuts"] = [v for v in c["sub_cuts"] if c["f0"] <= v <= c["f1"]] or [c["f0"]]
                bounds = c["sub_cuts"] + [c["f1"] + 1]
                c["sub_lengths"] = [bounds[q + 1] - bounds[q] for q in range(len(bounds) - 1)]
        cuts_source = os.path.relpath(os.path.abspath(args.cuts_from), W)
    else:
        cut_list = build_cuts(det["cuts"], N, min_cut, conf, det["info"])
    # attach flashes / solids / inverts to cuts and per-cut stats
    for k, c in enumerate(cut_list):
        c["id"] = f"c{k + 1:02d}" if len(cut_list) < 100 else f"c{k + 1:03d}"
    def cut_of(f):
        for c in cut_list:
            if c["f0"] <= f <= c["f1"]:
                return c["id"]
        return None
    for fl in det["flashes"]:
        fl["cut"] = cut_of(fl["f0"])
    # inverts: toggled polarity state inside each cut
    # (the majority polarity of a cut counts as normal; the minority frames are reported as inverted)
    inverts = []
    invset = set(det["inv_frames"])
    for c in cut_list:
        state, st = 0, []
        for f in range(c["f0"], c["f1"] + 1):
            if f > c["f0"] and f in invset:
                state ^= 1
            st.append(state)
        if sum(st) > len(st) / 2:
            st = [1 - v for v in st]
        for a_, b_ in _runs_bool(np.array(st, bool)):
            inverts.append({"f0": c["f0"] + a_, "f1": c["f0"] + b_ - 1, "cut": c["id"]})
    timing["cuts"] = round(time.time() - t0, 2)

    # ---------------------------------------------------------------- per-cut stats (analysis res)
    t0 = time.time()
    flash_frames = set()
    for fl in det["flashes"]:
        flash_frames.update(range(fl["f0"], fl["f1"] + 1))
    for s in det["solids"]:
        flash_frames.update(range(s["f0"], s["f1"] + 1))
    all_look_frames = []
    for c in cut_list:
        f0, f1 = c["f0"], c["f1"]
        c["n"] = f1 - f0 + 1
        c["t0"] = round(boundaries[f0], 6)
        c["t1"] = round(boundaries[f1 + 1], 6)
        c["dur_s"] = round(boundaries[f1 + 1] - boundaries[f0], 6)
        c["conf_label"] = "high" if c["confidence"] >= 0.75 else "medium" if c["confidence"] >= 0.5 else "low"
        c["cadence"] = cadence(fe, f0, f1, fpsf)
        c["motion"] = motion(fe, f0, f1, fpsf, an_w)
        pool = [f for f in range(f0, f1 + 1) if f not in flash_frames] or list(range(f0, f1 + 1))
        pick = [pool[int(round(q))] for q in np.linspace(0, len(pool) - 1, min(8, len(pool)))]
        c["look"] = look_stats([fe.F[f] for f in pick])
        all_look_frames += [(f, c["n"] / len(pick)) for f in pick]
        c["flashes"] = [[fl["f0"], fl["f1"], fl["type"]] for fl in det["flashes"] if f0 <= fl["f0"] <= f1]
        c["inverts"] = [[iv["f0"], iv["f1"]] for iv in inverts if iv["cut"] == c["id"]]
        c["mid"] = pool[len(pool) // 2]
        c["keyframe"] = c["mid"]
    timing["per_cut"] = round(time.time() - t0, 2)

    # ---------------------------------------------------------------- native-res samples: grain + text
    t0 = time.time()
    want = sorted({c["mid"] for c in cut_list})
    gw_ = min(384, crop["w"])
    gh_ = min(384, crop["h"])
    gx_ = crop["x"] + (crop["w"] - gw_) // 2
    gy_ = crop["y"] + (crop["h"] - gh_) // 2
    grain = {}
    texts = {}
    try:
        for f, fr in rrio.iter_frames_at(src, want, crop=crop_t, info=info):
            yy = rrio.luma(fr)
            oy, ox = gy_ - crop["y"], gx_ - crop["x"]
            grain[f] = grain_stats(yy[oy:oy + gh_, ox:ox + gw_])
            tw = min(480, fr.shape[1])
            small = rrio.resize(fr, tw, max(8, int(round(fr.shape[0] * tw / fr.shape[1]))), "area")
            texts[f] = text_candidates(small)
    except Exception as e:  # noqa: BLE001
        say(f"  (native-res samples failed: {e})")
    for c in cut_list:
        gv = grain.get(c["mid"])
        c["look"]["grain_sigma"] = round(gv, 2) if gv is not None else None
        c["look"]["grain"] = (None if gv is None else "none" if gv < 1.5 else "light" if gv < 3.5 else
                              "medium" if gv < 7 else "heavy")
        c["text_candidates"] = texts.get(c["mid"], [])
        if c["text_candidates"]:
            c["text_candidates_frame"] = c["mid"]
    timing["native_samples"] = round(time.time() - t0, 2)

    # reference-level look (weighted by cut length)
    fl_ = [fe.F[f] for f, _ in all_look_frames][:400]
    ref_look = look_stats(fl_) if fl_ else {}
    gvals = [v for v in grain.values() if v is not None]
    if ref_look:
        ref_look["grain_sigma_median"] = round(float(np.median(gvals)), 2) if gvals else None
        ref_look["bw_cut_share"] = round(sum(1 for c in cut_list if c["look"]["bw"]) / len(cut_list), 3)
        ref_look["threshold_cut_share"] = round(sum(1 for c in cut_list if c["look"]["threshold_look"]) / len(cut_list), 3)
        ref_look.pop("bars", None)

    # ---------------------------------------------------------------- sheets
    t0 = time.time()
    portrait = crop["h"] > crop["w"] * 1.05
    tile_w = args.tile_w or (154 if portrait else 194)
    cols = 10 if portrait else 8
    tile_h = int(round(tile_w * crop["h"] / crop["w"]))
    rows = max(2, min(6, (1500 - 40) // (tile_h + 4)))
    per_page = cols * rows
    lab_scale = 2 if tile_w >= 110 else 1
    sheets = {"overview": [], "every_frame": [], "timeline": None, "layout": None, "detail": []}
    base = os.path.basename(src)
    canvas_txt = ""
    if canvas["kind"] != "full" and not args.no_window:
        canvas_txt = f"  {canvas['kind'].upper()} {crop['w']}X{crop['h']}@{crop['x']},{crop['y']}"

    # markers per frame
    starts = {c["f0"]: c for c in cut_list if c["f0"] > 0}
    subs = {}
    for c in cut_list:
        for s in c.get("sub_cuts", [])[1:]:
            subs[s] = c
    flash_mark = {}
    for fl in det["flashes"]:
        for f in range(fl["f0"], fl["f1"] + 1):
            flash_mark[f] = fl["type"]
    for s in det["solids"]:
        for f in range(s["f0"], s["f1"] + 1):
            flash_mark.setdefault(f, s["kind"])
    inv_mark = set()
    for iv in inverts:
        inv_mark.update(range(iv["f0"], iv["f1"] + 1))
    maybe_mark = {m["f"] for m in det["maybes"]} if cuts_source == "detector" else set()
    short = {"white": "WH", "black": "BK", "solid": "SOL", "exposure": "EXP", "invert": "INV", "insert": "INS"}

    def mark(f, img):
        lab = f"f{f}"
        if f in starts:
            c = starts[f]
            low = c["confidence"] < 0.5
            _bar(img, COL_LOW if low else COL_CUT, 6)
            _rect(img, 0, 0, 4, img.shape[0], COL_LOW if low else COL_CUT)
            lab += " " + c["id"].upper() + ("?" if low else "")
            if c["kind"] == "burst":
                lab += "B"
        elif f in subs:
            _bar(img, COL_SUB, 5)
            _rect(img, 0, 0, 3, img.shape[0], COL_SUB)
            lab += " +"
        elif f in maybe_mark:
            _bar(img, COL_MAYBE, 4)
            lab += " ?"
        if f in flash_mark:
            img[-5:] = COL_FLASH
            lab += " " + short.get(flash_mark[f], "FL")
        if f in inv_mark:
            img[6:10] = COL_INV
            if f not in flash_mark:
                lab += " INV"
        if f > 0 and fe.hold[f] and f not in starts:
            lab += " ="
        return lab

    # pages from an earlier run would no longer match this analysis
    for fn in os.listdir(sdir):
        if (fn.startswith("ef_") or fn.startswith("overview_p")) and fn.endswith(".jpg"):
            try:
                os.remove(os.path.join(sdir, fn))
            except OSError:
                pass
    mids = {c["mid"]: c for c in cut_list}
    over_tiles = {}
    t_page = time.time()
    if True:  # one decode pass at tile width: every-frame pages + overview tiles
        page, pf0 = [], 0
        q_guess = 80
        npages = int(math.ceil(N / per_page))
        for f, fr in rrio.read_frames(src, count=N, scale_w=tile_w, crop=crop_t, info=info):
            if f in mids:
                over_tiles[f] = fr.copy()
            if args.no_every_frame:
                continue
            img = fr.copy()
            lab = mark(f, img)
            page.append((img, lab))
            if len(page) == per_page or f == N - 1:
                pno = len(sheets["every_frame"]) + 1
                fA, fB = pf0, f
                title = (f"{base}  F{fA}-{fB}  {rrio.tc(boundaries[fA])}-{rrio.tc(boundaries[fB + 1])}  "
                         f"{info['fps_str']}FPS  P{pno}/{npages}{canvas_txt}")
                out = os.path.join(sdir, f"ef_{pno:03d}.jpg")
                r = rrio.tile_sheet([p[0] for p in page], [p[1] for p in page], cols, out, tile_w, page_bytes,
                                    1600, title=title, quality=q_guess, label_scale=lab_scale)
                q_guess = min(80, (r["quality"] or 80) + 6)
                sheets["every_frame"].append({"path": os.path.relpath(out, W), "f0": fA, "f1": fB,
                                              "bytes": r["bytes"], "w": r["w"], "h": r["h"]})
                page, pf0 = [], f + 1
    timing["every_frame"] = round(time.time() - t_page, 2)

    # overview pages (<= 40 tiles each)
    ov_cols = 10 if portrait else 8
    ov_per = 40
    for p0 in range(0, len(cut_list), ov_per):
        chunk = cut_list[p0:p0 + ov_per]
        imgs, labs = [], []
        for c in chunk:
            im = over_tiles.get(c["mid"])
            imgs.append(im)
            lab = f"{c['id']} f{c['f0']}-{c['f1']}"
            l2 = f"{c['dur_s']:.2f}S"
            if c["kind"] == "burst":
                l2 += f" B{len(c['sub_cuts'])}"
            if c["confidence"] < 0.5:
                l2 += " ?"
            pat = c["cadence"]["pattern"]
            if pat not in ("native", "short"):
                l2 += " " + {"pulldown_24in60": "24P", "pulldown_24in30": "24P", "stepped": "STEP",
                             "freeze": "FRZ", "mixed": "MIX"}.get(pat, "")
            labs.append(lab + "\n" + l2)
        pno = p0 // ov_per + 1
        npg = int(math.ceil(len(cut_list) / ov_per))
        title = (f"OVERVIEW {pno}/{npg}  {base}  {info['w']}X{info['h']}  {info['fps_str']}FPS  {N}F  "
                 f"{len(cut_list)} CUTS{canvas_txt}")
        out = os.path.join(sdir, f"overview_p{pno:02d}.jpg")
        r = rrio.tile_sheet(imgs, labs, ov_cols, out, tile_w, page_bytes, 1600, title=title, quality=82,
                            label_scale=lab_scale)
        sheets["overview"].append({"path": os.path.relpath(out, W), "cuts": [chunk[0]["id"], chunk[-1]["id"]],
                                   "bytes": r["bytes"]})

    # layout (full canvas with the picture area outlined)
    if canvas["kind"] != "full":
        try:
            mid_f = cut_list[len(cut_list) // 2]["mid"]
            full = rrio.read_frame(src, mid_f, info=info)
            sc = min(1.0, 900.0 / max(full.shape[:2]))
            lw, lh = max(2, int(full.shape[1] * sc)), max(2, int(full.shape[0] * sc))
            lay = rrio.resize(full, lw, lh, "area")
            cx0, cy0 = int(crop["x"] * sc), int(crop["y"] * sc)
            cx1, cy1 = int((crop["x"] + crop["w"]) * sc), int((crop["y"] + crop["h"]) * sc)
            if canvas["kind"] == "window":
                mk = window_mask(lw, lh, crop["x"] * sc, crop["y"] * sc, crop["w"] * sc, crop["h"] * sc,
                                 canvas.get("radius", 0) * sc)
                edge = (mk > 40) & (mk < 215)
                edge = rrio.dilate(edge, 2)
                lay[edge] = (0, 255, 120)
            else:
                _frame_rect(lay, cx0, cy0, cx1, cy1, (0, 255, 120), 2)
            # bar colour
            mask = np.ones(full.shape[:2], bool)
            mask[crop["y"]:crop["y"] + crop["h"], crop["x"]:crop["x"] + crop["w"]] = False
            if mask.any():
                bc = np.median(full[mask], axis=0)
                canvas["bar_color"] = "#%02x%02x%02x" % tuple(int(v) for v in bc)
            rrio.draw_text(lay, f"{canvas['kind']} {crop['w']}x{crop['h']}@{crop['x']},{crop['y']} r{canvas.get('radius', 0)}",
                           4, 4, 2, (0, 255, 120), (0, 0, 0))
            out = os.path.join(sdir, "layout.jpg")
            rrio.write_image(out, lay, 85)
            sheets["layout"] = os.path.relpath(out, W)
        except Exception as e:  # noqa: BLE001
            canvas["notes"].append(f"layout sheet failed: {e}")
        if canvas["kind"] == "window" and canvas.get("window"):
            try:
                wd = canvas["window"]
                m = window_mask(info["w"], info["h"], wd["x"], wd["y"], wd["w"], wd["h"], canvas.get("radius", 0))
                ramp = canvas.get("edge_ramp_px") or 0
                if ramp > 1.5:
                    m = rrio.gauss_blur(m, min(8.0, ramp / 2.56))
                mp = os.path.join(adir, "window_mask.png")
                rrio.write_image(mp, m)
                canvas["mask"] = os.path.relpath(mp, W)
            except Exception as e:  # noqa: BLE001
                canvas["notes"].append(f"window mask failed: {e}")

    # timeline
    try:
        sheets["timeline"] = draw_timeline(fe, det, cut_list, inverts, fpsf, os.path.join(sdir, "timeline.png"),
                                           page_bytes, base, info, W)
    except Exception as e:  # noqa: BLE001
        say(f"  (timeline failed: {e})")

    # detail sheets
    for spec in args.detail:
        try:
            A, B = parse_span(spec)
        except ValueError:
            print(f"analyze_ref: error: --detail wants A:B, got {spec!r}", file=sys.stderr)
            return 1
        A, B = max(0, A), min(N - 1, B)
        if B < A:
            continue
        idx = list(range(A, B + 1))
        if len(idx) > 48:
            step = int(math.ceil(len(idx) / 48))
            idx = idx[::step]
        if args.detail_crop:
            try:
                dx_, dy_, dw_, dh_ = [int(v) for v in args.detail_crop.split(",")]
                if dw_ < 2 or dh_ < 2 or dx_ < 0 or dy_ < 0 or dx_ + dw_ > info["w"] or dy_ + dh_ > info["h"]:
                    raise ValueError
            except ValueError:
                print(f"analyze_ref: error: --detail-crop wants x,y,w,h inside the {info['w']}x{info['h']} frame, "
                      f"got {args.detail_crop!r}", file=sys.stderr)
                return 1
            dcrop = (dx_, dy_, dw_, dh_)
        else:
            dcrop = crop_t
            dw_ = crop["w"]
        dh_px = dh_ if args.detail_crop else crop["h"]
        # <= 12 frames per sheet: native pixels when the region fits 4 across, else scaled to 1600 px
        chunks = [idx[q:q + 12] for q in range(0, len(idx), 12)]
        for ci, ch_idx in enumerate(chunks):
            dcols = max(1, min(len(ch_idx), 1600 // max(1, dw_ + 4), 6))
            if dcols < min(4, len(ch_idx)):
                dcols = min(4, len(ch_idx)) if dh_px <= 1.3 * dw_ else min(6, len(ch_idx))
            dtw = min(dw_, (1600 - (dcols + 1) * 4) // dcols)
            fr_ = rrio.read_frames_at(src, ch_idx, crop=dcrop, info=info, strict=False)
            labs = [f"f{i} {boundaries[i]:.3f}s" for i in ch_idx]
            suffix = f"_p{ci + 1}" if len(chunks) > 1 else ""
            out = os.path.join(sdir, f"detail_{A}_{B}{suffix}.jpg")
            title = (f"DETAIL F{ch_idx[0]}-{ch_idx[-1]}  {base}  "
                     f"{'crop %d,%d,%dx%d' % dcrop if dcrop else 'full frame'}")
            r = rrio.tile_sheet(fr_, labs, dcols, out, dtw, page_bytes, 1600, title=title, quality=88,
                                label_scale=2)
            sheets["detail"].append({"path": os.path.relpath(out, W), "f0": ch_idx[0], "f1": ch_idx[-1],
                                     "bytes": r["bytes"], "scale": round(dtw / dw_ * r["scale"], 3)})
    timing["sheets"] = round(time.time() - t0, 2)

    # ---------------------------------------------------------------- JSON
    for c in cut_list:
        c.pop("mid", None)
    ndet = sum(1 for c in cut_list if c["f0"] > 0)
    nsub = sum(max(0, len(c.get("sub_cuts", [])) - 1) for c in cut_list)
    pats = {}
    for c in cut_list:
        pats.setdefault(c["cadence"]["pattern"], []).append(c["id"])
    srcs = {}
    for c in cut_list:
        if c["cadence"]["pattern"] not in ("short",):
            srcs.setdefault(str(c["cadence"]["src_fps"]), 0)
            srcs[str(c["cadence"]["src_fps"])] += c["n"]
    an = {
        "schema": SCHEMA, "tool": "analyze_ref.py", "version": VERSION,
        "created": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "ref": {"path": os.path.relpath(src, W) if src.startswith(W + os.sep) else src,
                "width": info["w"], "height": info["h"], "fps": info["fps_str"], "fps_float": round(fpsf, 6),
                "nb_frames": N if n_lim is None else None, "nb_frames_header": n_hdr,
                "analysed_frames": N, "video_duration": source_timing["duration_s"] if n_lim is None else None,
                "container_duration": info.get("format_duration"), "audio_duration": info.get("audio_duration"),
                "has_audio": info.get("has_audio"), "rotation": info.get("rotation"), "vfr": not source_timing["cfr"],
                "codec": info.get("codec"), "pix_fmt": info.get("pix_fmt")},
        "analysed": {"frames": [0, N - 1], "max_seconds": args.max_seconds, "analysis_w": an_w,
                     "analysis_h": fe.F[0].shape[0], "crop": crop},
        "canvas": canvas,
        "params": {"sensitivity": args.sensitivity, "min_cut": min_cut, "cuts_source": cuts_source,
                   "threshold_T": round(det["T"], 3)},
        "summary": {"cuts": len(cut_list), "detected_boundaries": ndet, "burst_sub_cuts": nsub,
                    "bursts": sum(1 for c in cut_list if c["kind"] == "burst"),
                    "low_confidence": [c["id"] for c in cut_list if c["confidence"] < 0.5],
                    "flashes": len(det["flashes"]), "solids": len(det["solids"]), "inverts": len(inverts),
                    "maybes": len(det["maybes"]), "cadence_patterns": pats, "src_fps_frames": srcs},
        "cuts": cut_list,
        "flashes": det["flashes"],
        "solids": det["solids"],
        "inverts": inverts,
        "maybes": det["maybes"],
        "activity_zones": zones,
        "look": ref_look,
        "sheets": sheets,
        "frames_file": "analysis/frames.json",
        "notes": [
            "cuts[].f0/f1 are inclusive absolute frame indices; cut times and frames.json PTS use decoded presentation boundaries",
            "CFR-only detector/cadence rates and timeline second ticks are approximate on VFR; use frames.json relative_pts for timing",
            "detector proposals only: confirm every cut on the every-frame pages (sheets/ef_*.jpg)",
            "flashes/inserts/solids/inverts are NOT cuts unless a cut lists them in its 'boundary'",
        ] + (["--max-seconds: only the first %d frames were analysed" % N] if n_lim else []),
        "timing_s": timing,
    }
    if n_hdr and n_lim is None and n_hdr != N:
        an["notes"].append(f"container says {n_hdr} frames, {N} decoded: use {N}")
    ap_ = os.path.join(adir, "analysis.json")
    if os.path.exists(ap_):
        try:
            os.replace(ap_, os.path.join(adir, "analysis.prev.json"))
        except OSError:
            pass
    frames_json = {"fps": info["fps_str"], "n": N,
                   "relative_pts": source_timing["relative_pts"][:N], "duration_s": boundaries[N],
                   "time_base": source_timing["time_base"], "verified_cfr": source_timing["cfr"],
                   "legend": {"pair values at index i": "frame i-1 -> i (index 0 is 0)",
                              "d": "mean abs RGB diff 0-255 (analysis res)",
                              "g": "structure distance sqrt(motion-compensated residual * (1-|corr|)), polarity-agnostic",
                              "h": "RGB histogram distance 0-1, polarity-agnostic", "hsv": "hue/sat histogram distance 0-1",
                              "c": "coarse luma correlation (-1 = inverted picture)",
                              "score": "cut score / threshold (>= 1 proposes a cut, with gates)",
                              "luma": "mean luma 0-1", "sat": "mean saturation 0-1", "hold": "1 = repeat of the previous frame",
                              "flat": "1 = solid / near-white / near-black frame",
                              "dx,dy": "global block motion in coarse px (80 px wide picture)"},
                   "d": [round(float(v), 2) for v in fe.d], "g": [round(float(v), 3) for v in fe.g],
                   "h": [round(float(v), 3) for v in fe.hpa], "hsv": [round(float(v), 3) for v in fe.hsv_d],
                   "c": [round(float(v), 3) for v in fe.c],
                   "score": [round(float(v / det["T"]), 3) for v in det["S"]],
                   "luma": [round(float(v) / 255, 3) for v in fe.L], "sat": [round(float(v), 3) for v in fe.SAT],
                   "hold": [int(v) for v in fe.hold], "flat": [int(v) for v in fe.flat],
                   "dx": [round(float(v), 2) for v in fe.dx], "dy": [round(float(v), 2) for v in fe.dy]}
    rrio.save_json(os.path.join(adir, "frames.json"), frames_json, indent=None)
    timing["total"] = round(time.time() - t_start, 2)
    rrio.save_json(ap_, an)

    # ---------------------------------------------------------------- summary
    say(f"analyze_ref: {an['ref']['path']}  {info['w']}x{info['h']}  {info['fps_str']} fps  {N} frames "
        f"({boundaries[N]:.3f} s){'  [first %d only]' % N if n_lim else ''}  audio {'yes' if info.get('has_audio') else 'no'}")
    if canvas["kind"] == "full":
        say("canvas: full frame (no window/letterbox found)")
    else:
        extra = f" radius {canvas.get('radius', 0)}" if canvas["kind"] == "window" else ""
        dc = canvas["crop"]
        say(f"canvas: {canvas['kind']} {dc['w']}x{dc['h']} @{dc['x']},{dc['y']}{extra} "
            f"(conf {canvas.get('confidence')}){'  [IGNORED: --no-window]' if args.no_window else ''}")
    for nt in canvas.get("notes", []):
        say(f"  note: {nt}")
    lows = an["summary"]["low_confidence"]
    say(f"cuts: {len(cut_list)} ({ndet} boundaries; {an['summary']['bursts']} burst(s) holding {nsub} sub-cuts; "
        f"{len(lows)} low-confidence{': ' + ','.join(lows[:12]) if lows else ''})  source: {cuts_source}")
    say(f"flashes/inserts: {len(det['flashes'])}  solid frames runs: {len(det['solids'])}  invert runs: {len(inverts)}  "
        f"near misses: {len(det['maybes'])}")
    if zones:
        say("high-activity zones (whip/strobe/fast action - read every frame): " +
            ", ".join(f"f{z['f0']}-{z['f1']}" for z in zones))
    mv = [f"{c['id']} f{c['f0']} (onset f{c['boundary']['moved_from']}, {c['boundary']['transition']['type']})"
          for c in cut_list if c.get("boundary", {}).get("moved_from") is not None]
    if mv:
        say("cuts placed inside a transition: " + "; ".join(mv))
    cad = ", ".join(f"{k} {len(v)}" for k, v in sorted(pats.items(), key=lambda kv: -len(kv[1])))
    top_src = sorted(srcs.items(), key=lambda kv: -kv[1])[:4]
    say(f"cadence: {cad};  main source rates (fps:frames): " + ", ".join(f"{k}:{v}" for k, v in top_src))
    for c in cut_list:
        if c["cadence"]["note"] or c["cadence"]["freezes"]:
            say(f"  {c['id']} f{c['f0']}-{c['f1']}: {c['cadence']['pattern']} {c['cadence']['unique']}/{c['cadence']['of']} unique"
                f"{'; freezes ' + str(c['cadence']['freezes']) if c['cadence']['freezes'] else ''}"
                f"{'; ' + c['cadence']['note'] if c['cadence']['note'] else ''}")
    if ref_look:
        say(f"look: {'B/W' if ref_look['bw'] else 'colour'}  luma p1/p50/p99 {ref_look['luma_p1_p50_p99']}  "
            f"sat {ref_look['sat_mean']}  warmth {ref_look['warmth']:+.3f}  "
            f"hue {ref_look.get('dominant_hue_name')}  grain sigma {ref_look.get('grain_sigma_median')}")
    say("sheets (look at them with image_paths, <= 4 files and 512 KiB per call):")
    for s in sheets["overview"]:
        say(f"  overview     {s['path']}  ({s['bytes'] // 1024} KB, {s['cuts'][0]}-{s['cuts'][1]})")
    if sheets["every_frame"]:
        ef = sheets["every_frame"]
        say(f"  every-frame  {ef[0]['path']} .. {ef[-1]['path']}  ({len(ef)} pages, {per_page} frames each, "
            f"max {max(e['bytes'] for e in ef) // 1024} KB)")
    if sheets["timeline"]:
        say(f"  timeline     {sheets['timeline']['path']}  ({sheets['timeline']['bytes'] // 1024} KB)")
    if sheets["layout"]:
        say(f"  layout       {sheets['layout']}")
    for s in sheets["detail"]:
        say(f"  detail       {s['path']}  ({s['bytes'] // 1024} KB, scale {s['scale']})")
    say(f"wrote {os.path.relpath(ap_, W)}, analysis/frames.json  ({timing['total']:.1f} s)")
    return 0


# ==================================================================================================
# timeline sheet
# ==================================================================================================
def draw_timeline(fe, det, cut_list, inverts, fps, out, max_bytes, base, info, W):
    N = fe.N
    WMAX = 1580
    per_band = min(N, 520)
    nb = int(math.ceil(N / per_band))
    per_band = int(math.ceil(N / nb))
    px = max(1, min(10, WMAX // per_band))
    bw = per_band * px
    thumb_h = 44
    th0 = fe.F[0]
    thumb_w = max(8, int(round(thumb_h * th0.shape[1] / th0.shape[0])))
    curve_h, luma_h, axis_h, gap = 110, 46, 26, 14
    band_h = 16 + thumb_h + 4 + curve_h + 4 + luma_h + axis_h
    left = 40
    Wimg = left + bw + 12
    top = 52
    Himg = top + nb * (band_h + gap)
    img = np.full((Himg, Wimg, 3), 22, np.uint8)
    rrio.draw_text(img, f"TIMELINE  {base}  {info['fps_str']}FPS  {N}F  {len(cut_list)} CUTS", 6, 6, 2,
                   (230, 230, 230), None)
    legend = [("SCORE", (255, 110, 200)), ("STRUCTURE", (80, 150, 255)), ("HIST", (90, 220, 110)),
              ("PIXEL DIFF", (150, 150, 150)), ("CUT", COL_CUT), ("LOW CONF", COL_LOW), ("SUB-CUT", COL_SUB),
              ("FLASH", COL_FLASH), ("INVERT", COL_INV), ("LUMA", (235, 235, 235)), ("SAT", (255, 150, 40))]
    lx = 6
    for name, col in legend:
        w_, _ = rrio.text_size(name, 1)
        if lx + w_ + 14 > Wimg:
            break
        _rect(img, lx, 30, lx + 8, 38, col)
        rrio.draw_text(img, name, lx + 10, 30, 1, (220, 220, 220), None)
        lx += w_ + 22
    S = det["S"] / det["T"]
    dmax = max(20.0, float(np.percentile(fe.d, 99)) if N > 2 else 20.0)
    starts = {c["f0"]: c for c in cut_list}
    subs = {s for c in cut_list for s in c.get("sub_cuts", [])[1:]}
    for b in range(nb):
        f0 = b * per_band
        f1 = min(N, f0 + per_band)
        y0 = top + b * (band_h + gap)
        xs = left + (np.arange(f0, f1) - f0) * px + px // 2
        ty = y0 + 16
        cy = ty + thumb_h + 4
        ly = cy + curve_h + 4
        ay = ly + luma_h
        _rect(img, left, cy, left + bw, cy + curve_h, (34, 34, 40))
        _rect(img, left, ly, left + bw, ly + luma_h, (30, 30, 30))
        # burst spans + flash shading
        for c in cut_list:
            if c["kind"] == "burst" and c["f1"] >= f0 and c["f0"] < f1:
                a, z = max(c["f0"], f0), min(c["f1"] + 1, f1)
                _rect(img, left + (a - f0) * px, cy, left + (z - f0) * px, cy + curve_h, (60, 30, 60))
        for fl in det["flashes"]:
            for f in range(max(fl["f0"], f0), min(fl["f1"] + 1, f1)):
                _rect(img, left + (f - f0) * px, cy + curve_h - 8, left + (f - f0 + 1) * px, cy + curve_h, (230, 210, 0))
        for iv in inverts:
            for f in range(max(iv["f0"], f0), min(iv["f1"] + 1, f1)):
                _rect(img, left + (f - f0) * px, cy, left + (f - f0 + 1) * px, cy + 4, (150, 90, 255))
        # threshold line (score = 1)
        yth = cy + curve_h - 1 - int((1.0 / 3.0) * (curve_h - 1))
        img[yth, left:left + bw:3] = (200, 60, 60)
        _plot(img, xs, fe.d[f0:f1], cy, curve_h, dmax, (120, 120, 120))
        _plot(img, xs, np.minimum(S[f0:f1], 3.0), cy, curve_h, 3.0, (255, 110, 200))
        _plot(img, xs, fe.g[f0:f1], cy, curve_h, 1.2, (80, 150, 255))
        _plot(img, xs, fe.hpa[f0:f1], cy, curve_h, 0.8, (90, 220, 110))
        _plot(img, xs, fe.SAT[f0:f1], ly, luma_h, 1.0, (255, 150, 40))
        _plot(img, xs, fe.L[f0:f1], ly, luma_h, 255.0, (235, 235, 235))
        # holds as small ticks
        for f in range(f0, f1):
            if fe.hold[f]:
                x = left + (f - f0) * px
                _rect(img, x, ly + luma_h - 3, x + max(1, px - 1), ly + luma_h, (110, 110, 110))
        # thumbnails
        step = max(1, int(math.ceil((thumb_w + 2) / px)))
        for f in range(f0, f1, step):
            t = rrio.resize(fe.F[f], thumb_w, thumb_h, "area")
            x = left + (f - f0) * px
            w_ = min(thumb_w, Wimg - x)
            if w_ > 0:
                img[ty:ty + thumb_h, x:x + w_] = t[:, :w_]
        # cut lines
        for f in range(f0, f1):
            x = left + (f - f0) * px
            if f in starts and f > 0:
                c = starts[f]
                col = COL_CUT if c["confidence"] >= 0.5 else COL_LOW
                _vline(img, x, ty - 2, ay, col, 2 if px > 2 else 1)
                rrio.draw_text(img, c["id"][1:], x + 2, y0 + 2, 1, col, (0, 0, 0))
            elif f in subs:
                _vline(img, x, cy, ay, COL_SUB, 1)
        # axis
        for f in range(f0, f1):
            x = left + (f - f0) * px
            if f % 10 == 0:
                _vline(img, x, ay, ay + (8 if f % 50 == 0 else 4), (200, 200, 200))
            if f % 50 == 0:
                rrio.draw_text(img, str(f), x + 2, ay + 8, 1, (220, 220, 220), None)
        secs = int(math.floor(f0 / fps)) + 1
        while secs * fps < f1:
            x = left + int(round(secs * fps - f0)) * px
            _vline(img, x, ay + 10, ay + 22, (120, 200, 255))
            rrio.draw_text(img, f"{secs}s", x + 2, ay + 16, 1, (120, 200, 255), None)
            secs += 1
        rrio.draw_text(img, f"{f0}", 2, cy + 2, 1, (200, 200, 200), None)
        rrio.draw_text(img, "LUMA", 2, ly + 2, 1, (200, 200, 200), None)
    fmt_png = out
    data = rrio.encode_image(img, "png")
    path = fmt_png
    if len(data) > max_bytes:
        path = os.path.splitext(out)[0] + ".jpg"
        r = rrio.tile_sheet([img], None, 1, path, img.shape[1], max_bytes, 1600, quality=90, gap=0)
        if os.path.exists(fmt_png):
            os.remove(fmt_png)
        return {"path": os.path.relpath(path, W), "bytes": r["bytes"], "bands": nb, "px_per_frame": px}
    rrio._atomic_write_bytes(path, data)
    stale = os.path.splitext(out)[0] + ".jpg"
    if os.path.exists(stale):
        os.remove(stale)
    return {"path": os.path.relpath(path, W), "bytes": len(data), "bands": nb, "px_per_frame": px}


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except (FileNotFoundError, ValueError, IndexError, RuntimeError) as e:
        print(f"analyze_ref: error: {e}", file=sys.stderr)
        sys.exit(1)
