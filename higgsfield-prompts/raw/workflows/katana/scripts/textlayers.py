#!/usr/bin/env python3
"""On-screen text rebuilt from the reference's own pixels (never retyped) and laid back at timeline fps.

  python3 $RR/textlayers.py layers $W [--specs plan/text_specs.json] [--cuts c01,c09]
  python3 $RR/textlayers.py check  $W [--video out/base.mp4] [--cuts c01,c09]
  python3 $RR/textlayers.py pass   $W [--base out/base.mp4] [--specs plan/text_pass.json] [--out out/text.mp4]
  python3 $RR/textlayers.py logo   $W --box x,y,w,h [--frames a-b]

Coordinates are WINDOW pixels (frame pixels when the reference has no window); frames are absolute
timeline frames of ref/ref.mp4. The timeline (cuts, window) is read exactly like assemble.py does.
Memory is flat in cut length: layers/check stream the frames and read only the layer boxes (+ margins),
pass reads each matte lazily as uint8 in frame order while the stream is inside its cut.

layers  plan/text_specs.json:
  {"c09": {"layers": [{"name": "main", "box": [x0,y0,x1,y1], "full": [fa, fb],
                       "shape_lo": 225,           # min-channel threshold of the letter shape (190-238)
                       "key": "white",            # or "black" (dark letters)
                       "sat_lo": 30, "sat_hi": 70,  # saturation gate: full below sat_lo, zero above sat_hi
                       "close": 3, "soft": 0.8,     # morphological close (px) and edge blur (sigma)
                       "fade": "auto",              # in | inout | raw | auto (inout when it fades out)
                       "stat": "mean",              # mean | median | max over the fully-on frames (max
                                                    #   recovers letters the actor hides on SOME frames)
                       "repair": [{"op": "mirror_x", "src": [535,284,580,326], "axis": 541}]}]}}
                                                    # copy | mirror_x | mirror_y | extend | fill | erase |
                                                    #   close | open: holes the old actor punched (v3)
  -> text/<cut>/<name>.png   static alpha: key averaged over the fully-on frames (grain and footage average
                             out), saturation-gated, thresholded, closed, softened
     text/<cut>/curves.json  {"schema","cut","f0","n","fps","layers":{name:{"opacity":[per timeline frame],
                             "raw":[...], "full", "box", "fade", "core_px", "ring_px"}}}; opacity = (letter
                             core - surrounding ring) / its fully-on value, forced monotonic
     text/<cut>/layers.json  per layer meta (png, box, full, key, pixels, bbox)
     text/<cut>/preview.png  all layers white on grey (look for holes punched by the old actor)
     qa/text_<cut>.jpg       per layer: reference crop | rebuilt layer | diff (red = only in ref, cyan =
                             only in the layer)
check   per layer recall (reference letter core present in the video) / spurious (extra white around it)
        over the fully-on frames; layers marked behind in text_pass.json ignore pixels under the fitted
        matte. -> text/textcheck.json. FIX when recall < 0.85 or spurious > 0.15.
pass    plan/text_pass.json:
  {"logo": {"png": "text/logo.png", "x": 460, "y": 730},
   "cuts": {"c03": {"layers": [{"name": "sans", "behind": true, "glow": [8, 0.25],
                                "backing": [18, 0.35],   # dark halo under the letters (bright plates)
                                "color": [255,255,255], "shift": 0, "gain": 1.0}],  # shift: frames later
                    "matte": true,                # = mattes/fit/c03.mkv from assemble.py, or a path (video
                                                  #   or PNG dir, white = person); per timeline frame
                    "cleanplate": {"box": [x0,y0,x1,y1], "from": 6, "until": null},
                    "inpaint": {"boxes": [[x0,y0,x1,y1]], "lo": 215, "sat": 40, "frames": [a, b]},
                    "logo": true}}}
  hairfix is disabled: never recolor or repair a face/head with local code. cleanplate/inpaint require
  a complete, cut-aligned exclusion matte for all people, including extras and hair/head silhouettes;
  matte_clip_y is forbidden for these repairs.
  Order per frame: cleanplate (background pixels frozen from rel frame `from`, excluding people in
  both frames), inpaint (background only, with subject protection reapplied after dilation),
  layers (backing darkens, glow = screen of a blurred alpha, then
  the letters; behind = x (1 - person); opacity = curve[rel] from curves.json), logo. Layer alpha is multiplied by the window mask. Frames outside listed cuts
  pass through; audio is stream-copied. -> out/text.mp4
logo    keyed clean white watermark from the frames where the box surroundings are darkest -> text/logo.png
        (RGBA) + qa/logo.jpg, and sets "logo" in plan/text_pass.json (unless --no-update).
"""
from __future__ import annotations

import argparse
import collections
import os
import sys
import threading
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import rrio  # noqa: E402
import assemble as asm  # noqa: E402
from assemble import UsageError, wpath, rel_to, log  # noqa: E402


# --------------------------------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------------------------------
def _box(b, w, h, name="box"):
    if not isinstance(b, (list, tuple)) or len(b) != 4:
        raise UsageError(f"{name} must be [x0,y0,x1,y1], got {b!r}")
    x0, y0, x1, y1 = [int(round(float(v))) for v in b]
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(w, x1), min(h, y1)
    if x1 <= x0 or y1 <= y0:
        raise UsageError(f"{name} {b} is empty inside the {w}x{h} window")
    return x0, y0, x1, y1


CHROMA_PAD = 8         # px kept around every pixel we use: a 4:2:0 crop edge changes chroma upsampling within
#                        ~4 px of it, so reading a sub-rect this far out gives the same pixels as a window read
RING_PAD = 16 + CHROMA_PAD  # around the layer boxes: ring curves (dilate 31 -> 15 px), QA sheets (12 px)
MEDIAN_BYTES = 192 << 20   # stat "median": box rows stacked per decode pass (exact median, bounded memory)


def _union_box(boxes, w, h, pad=0):
    """Union of [x0,y0,x1,y1] window boxes padded by pad, clipped to the w x h window."""
    return (max(0, min(b[0] for b in boxes) - pad), max(0, min(b[1] for b in boxes) - pad),
            min(w, max(b[2] for b in boxes) + pad), min(h, max(b[3] for b in boxes) + pad))


def window_crop_frames(path, tl, info, start, count, ubox):
    """(index, frame) generator of the window sub-rect ubox [x0,y0,x1,y1] (window px) of a canvas-size video,
    decoded frame-exactly and one at a time (never stacked)."""
    X, Y = tl["win"][0], tl["win"][1]
    ux0, uy0, ux1, uy1 = ubox
    return rrio.read_frames(path, start=start, count=count, crop=(X + ux0, Y + uy0, ux1 - ux0, uy1 - uy0), info=info)


def key_planes(F, key="white"):
    """(value, saturation) uint8 planes. white: min(R,G,B); black: 255 - max(R,G,B)."""
    mn = F.min(axis=-1)
    mx = F.max(axis=-1)
    sat = mx - mn
    if key == "black":
        return (255 - mx).astype(np.uint8), sat
    if key != "white":
        raise UsageError(f"unknown key {key!r} (white|black)")
    return mn, sat


def key_soft(val_avg, sat_avg, lo, sat_lo=30.0, sat_hi=70.0):
    k = np.clip((val_avg - lo) / max(1.0, 250.0 - lo), 0, 1)
    g = np.clip(1 - (sat_avg - sat_lo) / max(1.0, sat_hi - sat_lo), 0, 1)
    return (k * g).astype(np.float32)


def full_range(L, cut):
    fa, fb = (int(v) for v in L["full"])
    a0 = max(0, fa - cut["f0"])
    a1 = min(cut["n"] - 1, fb - cut["f0"])
    if a1 < a0:
        raise UsageError(f"{cut['id']}/{L['name']}: full {L['full']} is outside the cut f{cut['f0']}-{cut['f1']}")
    return a0, a1


def load_specs(W, path, what):
    p = wpath(W, path)
    if not os.path.isfile(p):
        raise UsageError(f"{what} not found: {p}")
    d = rrio.load_json(p)
    if not isinstance(d, dict):
        raise UsageError(f"{p}: expected an object")
    return d, p


def fade_curve(raw, a0, a1, mode):
    raw = np.clip(np.asarray(raw, np.float64), 0, 1)
    if mode == "raw":
        return raw
    if mode == "auto":
        tail = raw[a1 + 1:]
        mode = "inout" if len(tail) >= 2 and float(np.mean(tail[-min(3, len(tail)):])) < 0.6 else "in"
    if mode == "in":
        return np.maximum.accumulate(raw)
    if mode == "inout":
        up = np.maximum.accumulate(raw[:a1 + 1])
        down = np.minimum.accumulate(np.r_[1.0, raw[a1 + 1:]])[1:]
        return np.r_[up, down]
    raise UsageError(f"unknown fade {mode!r} (in|inout|raw|auto)")


def load_curves(W, cid):
    p = wpath(W, f"text/{cid}/curves.json")
    if not os.path.isfile(p):
        raise UsageError(f"{cid}: no text/{cid}/curves.json (run textlayers.py layers first)")
    d = rrio.load_json(p)
    if isinstance(d, dict) and "layers" in d:
        return {k: (v["opacity"] if isinstance(v, dict) else v) for k, v in d["layers"].items()}
    return d  # legacy {name: [opacity...]}


class GrayStream:
    """A matte (gray video, or a directory of PNG/JPG frames; white = person) read lazily as uint8 frames in
    order: get(i) for non-decreasing i decodes sequentially, nothing is stacked. n = frame count, (h, w) size.
    Rows >= clip_y are zeroed (matte_clip_y)."""

    def __init__(self, W, path, clip_y=None):
        p = wpath(W, path)
        self.path = p
        self.clip_y = int(clip_y) if clip_y else None
        self.files, self.rd = None, None
        self._i, self._f = None, None
        if os.path.isdir(p):
            self.files = [os.path.join(p, f) for f in sorted(os.listdir(p))
                          if f.lower().endswith((".png", ".jpg", ".jpeg"))]
            if not self.files:
                raise UsageError(f"matte dir {p} has no PNG/JPG frames")
            self.n = len(self.files)
            pi = rrio.probe(self.files[0])
        elif os.path.isfile(p):
            pi = rrio.probe(p, count=True)
            self.n = int(pi.get("nb_frames") or 0)
            if self.n <= 0:
                raise UsageError(f"matte {p} has no frames")
            self.info = pi
        else:
            raise UsageError(f"matte not found: {p}")
        self.h, self.w = int(pi["h"]), int(pi["w"])

    def get(self, i):
        i = int(i)
        if i == self._i:
            return self._f
        if self.files is not None:
            f = rrio.read_image(self.files[i], "gray")
        else:
            if self.rd is None:
                self.rd = asm.SeqReader(self.path, self.info, 0, self.n - 1, gray=True, keep=2)
            f = self.rd.get(i)
        if self.clip_y:
            f = f.copy()
            f[self.clip_y:] = 0
        self._i, self._f = i, f
        return f

    def close(self):
        if self.rd is not None:
            self.rd.close()
            self.rd = None
        self._i, self._f = None, None


def _layer_stat_init(S):
    bw, bh = S["box"][2] - S["box"][0], S["box"][3] - S["box"][1]
    if S["stat"] == "mean":
        S["acc"] = (np.zeros((bh, bw), np.uint32), np.zeros((bh, bw), np.uint32))
    elif S["stat"] == "max":
        S["acc"] = (np.zeros((bh, bw), np.uint8), np.full((bh, bw), 255, np.uint8))
    else:  # median: exact, over row bands of the box that fit MEDIAN_BYTES (band 0 rides on the main pass)
        nf = S["a1"] - S["a0"] + 1
        S["band"] = max(1, min(bh, MEDIAN_BYTES // max(1, nf * bw * 2)))
        S["acc"] = ([], [])
    S["seen"] = 0


def _layer_stat_add(S, val, sat):
    """val/sat: uint8 planes of the layer box for one fully-on frame."""
    A, B = S["acc"]
    if S["stat"] == "mean":
        A += val
        B += sat
    elif S["stat"] == "max":
        np.maximum(A, val, out=A)
        np.minimum(B, sat, out=B)
    else:
        A.append(val[:S["band"]].copy())
        B.append(sat[:S["band"]].copy())
    S["seen"] += 1


def _box_planes(fr, box, ubox, key):
    """uint8 (value, saturation) of window box `box` from a frame of the window sub-rect ubox."""
    x0, y0, x1, y1 = box
    sub = fr[y0 - ubox[1]:y1 - ubox[1], x0 - ubox[0]:x1 - ubox[0]]
    return key_planes(sub, key)


def _layer_stat_finish(S, tl, cut, ubox):
    """-> (avg, savg) float box planes over the fully-on frames [a0, a1]."""
    nf = S["a1"] - S["a0"] + 1
    if S["seen"] != nf:
        raise RuntimeError(f"{cut['id']}/{S['name']}: decoded {S['seen']} of {nf} fully-on frames")
    A, B = S["acc"]
    if S["stat"] == "mean":
        return (A / np.float64(nf)).astype(np.float32), (B / np.float64(nf)).astype(np.float32)
    if S["stat"] == "max":
        return A.astype(np.float32), B.astype(np.float32)
    x0, y0, x1, y1 = S["box"]
    bh = y1 - y0
    avg = np.empty((bh, x1 - x0), np.float32)
    savg = np.empty_like(avg)
    avg[:S["band"]] = np.median(np.stack(A), axis=0)
    savg[:S["band"]] = np.median(np.stack(B), axis=0)
    S["acc"] = None
    r0 = S["band"]
    while r0 < bh:  # further bands: one more decode of the fully-on frames each, box rows only
        r1 = min(bh, r0 + S["band"])
        vs, ss = [], []
        band = (x0, y0 + r0, x1, y0 + r1)
        # read the band with the union box's columns and CHROMA_PAD rows around it: same pixels as pass 1
        rd = (ubox[0], max(ubox[1], band[1] - CHROMA_PAD), ubox[2], min(ubox[3], band[3] + CHROMA_PAD))
        for _, fr in window_crop_frames(tl["src"], tl, tl["info"], cut["f0"] + S["a0"], nf, rd):
            v, s_ = _box_planes(fr, band, rd, S["key"])
            vs.append(v)
            ss.append(s_)
        if len(vs) != nf:
            raise RuntimeError(f"{cut['id']}/{S['name']}: decoded {len(vs)} of {nf} fully-on frames")
        avg[r0:r1] = np.median(np.stack(vs), axis=0)
        savg[r0:r1] = np.median(np.stack(ss), axis=0)
        del vs, ss
        r0 = r1
    return avg, savg


def inpaint_nc(img, hole, sigmas=(2, 4, 8, 16, 32)):
    """Fill `hole` (bool HxW) in float image img (HxWx3, modified in place) by normalized convolution:
    blur(img*valid)/blur(valid) at growing sigma; each hole pixel takes the smallest scale with support."""
    ys, xs = np.nonzero(hole)
    if len(ys) == 0:
        return img
    H, W = hole.shape
    pad = int(3 * sigmas[-1])
    y0, y1 = max(0, ys.min() - pad), min(H, ys.max() + 1 + pad)
    x0, x1 = max(0, xs.min() - pad), min(W, xs.max() + 1 + pad)
    sub = img[y0:y1, x0:x1].astype(np.float32)
    hm = hole[y0:y1, x0:x1]
    valid = (~hm).astype(np.float32)
    if valid.sum() < 1:
        return img
    out = sub.copy()
    todo = hm.copy()
    for s in sigmas:
        den = rrio.gauss_blur(valid, s)
        num = rrio.gauss_blur(sub * valid[..., None], s)
        ok = todo & (den > 0.02)
        out[ok] = num[ok] / den[ok][:, None]
        todo &= ~ok
        if not todo.any():
            break
    if todo.any():
        out[todo] = sub[~hm].mean(0)
    img[y0:y1, x0:x1] = out
    return img


def _bbox_of(a, thr=1e-3, pad=0):
    ys, xs = np.nonzero(a > thr)
    if len(ys) == 0:
        return None
    H, W = a.shape
    return (max(0, ys.min() - pad), min(H, ys.max() + 1 + pad), max(0, xs.min() - pad), min(W, xs.max() + 1 + pad))


def _shift(m, dx, dy):
    out = np.zeros_like(m)
    H, W = m.shape
    xs0, xs1 = max(0, -dx), min(W, W - dx)
    ys0, ys1 = max(0, -dy), min(H, H - dy)
    if xs1 > xs0 and ys1 > ys0:
        out[ys0 + dy:ys1 + dy, xs0 + dx:xs1 + dx] = m[ys0:ys1, xs0:xs1]
    return out


def repair_mask(m, ops, where=""):
    """Glyph repairs on a binary layer, built only from the reference's own letter pixels (Altman v3):
      {"op": "copy", "src": [x0,y0,x1,y1], "dx": 74, "dy": 0}      sibling glyph copied over a hole
      {"op": "mirror_x"|"mirror_y", "src": [x0,y0,x1,y1], "axis": 541.0}   symmetric glyph completed
      {"op": "extend", "row": 280, "x": [374, 394], "to": 400}     repeat a stem cross-section to row `to`
      {"op": "fill"|"erase", "box": [x0,y0,x1,y1]}                 solid bar / remove specks
      {"op": "close"|"open", "px": 3, "box": [x0,y0,x1,y1]?}       morphology (optionally inside a box)"""
    H, W = m.shape
    m = m.copy()
    for i, op in enumerate(ops):
        kind = op.get("op")
        tag = f"{where} repair #{i} ({kind})"
        if kind == "copy" or kind in ("mirror_x", "mirror_y"):
            x0, y0, x1, y1 = _box(op["src"], W, H, tag)
            reg = np.zeros_like(m)
            reg[y0:y1, x0:x1] = m[y0:y1, x0:x1]
            if kind == "copy":
                m |= _shift(reg, int(op.get("dx", 0)), int(op.get("dy", 0)))
            else:
                ys, xs = np.nonzero(reg)
                ax = float(op["axis"])
                if kind == "mirror_x":
                    xs = np.rint(2 * ax - xs).astype(int)
                else:
                    ys = np.rint(2 * ax - ys).astype(int)
                ok = (xs >= 0) & (xs < W) & (ys >= 0) & (ys < H)
                m[ys[ok], xs[ok]] = True
        elif kind == "extend":
            r = int(op["row"])
            xa, xb = (int(v) for v in op["x"])
            row = m[r, xa:xb].copy()
            to = int(op["to"])
            for yy in range(min(r, to), max(r, to) + 1):
                if 0 <= yy < H:
                    m[yy, xa:xb] |= row
        elif kind in ("fill", "erase"):
            x0, y0, x1, y1 = _box(op["box"], W, H, tag)
            m[y0:y1, x0:x1] = kind == "fill"
        elif kind in ("close", "open"):
            px = int(op.get("px", 3))
            if op.get("box"):
                x0, y0, x1, y1 = _box(op["box"], W, H, tag)
            else:
                x0, y0, x1, y1 = 0, 0, W, H
            sub = m[y0:y1, x0:x1]
            sub = rrio.erode(rrio.dilate(sub, px), px) if kind == "close" else rrio.dilate(rrio.erode(sub, px), px)
            m[y0:y1, x0:x1] = sub
        else:
            raise UsageError(f"{tag}: unknown op (copy|mirror_x|mirror_y|extend|fill|erase|close|open)")
    return m


# --------------------------------------------------------------------------------------------------
# layers
# --------------------------------------------------------------------------------------------------
def cmd_layers(a):
    """Two streaming passes per cut over the reference, reading only the layer boxes (+ RING_PAD px):
    1) per-pixel key/saturation statistic of every layer over its fully-on frames (sum, running max/min, or
       an exact banded median) and the QA crops at each layer's middle full frame; 2) per frame letter-core
       mean and ring median for the opacity curves. Memory does not grow with the cut length."""
    W = os.path.abspath(a.W)
    tl = asm.load_timeline(W, a.edl, a.src)
    specs, sp = load_specs(W, a.specs, "text specs")
    byid = {c["id"]: c for c in tl["cuts"]}
    ids = [s.strip() for s in a.cuts.split(",")] if a.cuts else [k for k in specs if not k.startswith("_")]
    x, y, w, h = tl["win"]
    for cid in ids:
        if cid not in byid:
            raise UsageError(f"unknown cut {cid}")
        if cid not in specs or not specs[cid].get("layers"):
            raise UsageError(f"{cid}: no layers in {rel_to(W, sp)}")
    summary = {}
    for cid in ids:
        t0 = time.time()
        cut, spec = byid[cid], specs[cid]
        out = wpath(W, f"text/{cid}")
        os.makedirs(out, exist_ok=True)
        # ---- layer setup (validated before any decode)
        st = []
        for L in spec["layers"]:
            name = L["name"]
            key = L.get("key", "white")
            if key not in ("white", "black"):
                raise UsageError(f"unknown key {key!r} (white|black)")
            stat = L.get("stat", "mean")
            if stat not in ("mean", "median", "max"):
                raise UsageError(f"{cid}/{name}: stat must be mean|median|max")
            box = _box(L["box"], w, h, f"{cid}/{name} box")
            a0, a1 = full_range(L, cut)
            pb = (max(0, box[0] - 12), max(0, box[1] - 12), min(w, box[2] + 12), min(h, box[3] + 12))
            S = {"L": L, "name": name, "key": key, "stat": stat, "box": box, "a0": a0, "a1": a1,
                 "mid": (a0 + a1) // 2, "pbox": pb, "mid_crop": None}
            _layer_stat_init(S)
            st.append(S)
        ubox = _union_box([S["box"] for S in st], w, h, RING_PAD)
        # ---- pass 1: statistics over the fully-on frames (box pixels only) + QA crops
        lo = min(S["a0"] for S in st)
        hi = max(S["a1"] for S in st)
        for f, fr in window_crop_frames(tl["src"], tl, tl["info"], cut["f0"] + lo, hi - lo + 1, ubox):
            rel = f - cut["f0"]
            for S in st:
                if S["a0"] <= rel <= S["a1"]:
                    _layer_stat_add(S, *_box_planes(fr, S["box"], ubox, S["key"]))
                if rel == S["mid"]:
                    px0, py0, px1, py1 = S["pbox"]
                    S["mid_crop"] = fr[py0 - ubox[1]:py1 - ubox[1], px0 - ubox[0]:px1 - ubox[0]].copy()
        masks, meta, rng = {}, {}, {}
        for S in st:
            L, name = S["L"], S["name"]
            x0, y0, x1, y1 = S["box"]
            rng[name] = (S["a0"], S["a1"])
            avg, savg = _layer_stat_finish(S, tl, cut, ubox)
            k = key_soft(avg, savg, float(L.get("shape_lo", 230)), float(L.get("sat_lo", 30)), float(L.get("sat_hi", 70)))
            m = np.zeros((h, w), bool)
            m[y0:y1, x0:x1] = k > 0.5
            c = int(L.get("close", 3))
            if c > 1:
                m = rrio.erode(rrio.dilate(m, c), c)
                box = np.zeros((h, w), bool)
                box[y0:y1, x0:x1] = True
                m &= box
            masks[name] = m
        allm = np.zeros((h, w), bool)
        for m in masks.values():
            allm |= m
        all15 = rrio.dilate(allm, 15)
        # ---- pass 2: per-frame letter core (mean) vs surrounding ring (median) over the whole cut
        cr = {}
        for S in st:
            m = masks[S["name"]]
            core = rrio.erode(m, 3)
            ring = rrio.dilate(m, 31) & ~all15
            S["npx"], S["ncore"], S["nring"] = int(m.sum()), int(core.sum()), int(ring.sum())
            if S["ncore"] >= 30 and S["nring"] >= 30:
                cy, cx = np.nonzero(core)
                ry, rx = np.nonzero(ring)
                cr[S["name"]] = (cy - ubox[1], cx - ubox[0], ry - ubox[1], rx - ubox[0],
                                 np.zeros(cut["n"], np.float32), np.zeros(cut["n"], np.float32))
        if cr:
            got = 0
            keys = {S["key"] for S in st if S["name"] in cr}
            for f, fr in window_crop_frames(tl["src"], tl, tl["info"], cut["f0"], cut["n"], ubox):
                rel = f - cut["f0"]
                vals = {kk: key_planes(fr, kk)[0] for kk in keys}
                for S in st:
                    if S["name"] in cr:
                        cy, cx, ry, rx, cvs, rvs = cr[S["name"]]
                        val = vals[S["key"]]
                        cvs[rel] = val[cy, cx].astype(np.float32).mean()
                        rvs[rel] = np.median(val[ry, rx].astype(np.float32))
                got += 1
            if got != cut["n"]:
                raise RuntimeError(f"{cid}: decoded {got} of {cut['n']} frames")
        curves, repaired = {}, {}
        for S in st:
            L, name = S["L"], S["name"]
            m = masks[name]
            a0, a1 = rng[name]
            npx, ncore, nring = S["npx"], S["ncore"], S["nring"]
            if name not in cr:
                raw = np.ones(cut["n"])
                note = "too few core/ring pixels: opacity 1"
            else:
                cv, rv = cr[name][4], cr[name][5]
                full = float((cv[a0:a1 + 1] - rv[a0:a1 + 1]).mean())
                raw = np.clip((cv - rv) / max(1.0, full), 0, 1)
                note = f"contrast at full {full:.1f}"
                if full < 8:
                    note += " (LOW: check box/full/shape_lo)"
            mode = L.get("fade", "auto")
            op = fade_curve(raw, a0, a1, mode)
            if L.get("repair"):
                m = repair_mask(m, L["repair"], f"{cid}/{name}")
                note += f"; repaired ({len(L['repair'])} ops, {int(m.sum()) - npx:+d} px)"
                repaired[name] = m
            soft = float(L.get("soft", 0.8))
            alpha = rrio.gauss_blur(m.astype(np.float32), soft) if soft > 0 else m.astype(np.float32)
            png = os.path.join(out, f"{name}.png")
            rrio.write_image(png, rrio.to_uint8(alpha * 255))
            bb = _bbox_of(m.astype(np.float32), 0.5)
            curves[name] = {"opacity": [round(float(v), 3) for v in op], "raw": [round(float(v), 3) for v in raw],
                            "full": [int(v) for v in L["full"]], "box": [int(v) for v in L["box"]], "fade": mode,
                            "core_px": ncore, "ring_px": nring}
            meta[name] = {"png": rel_to(W, png), "box": [int(v) for v in L["box"]], "full": [int(v) for v in L["full"]],
                          "key": S["key"], "shape_lo": L.get("shape_lo", 230), "pixels": npx,
                          "bbox": [int(bb[2]), int(bb[0]), int(bb[3]), int(bb[1])] if bb else None, "note": note}
            if npx < 50:
                meta[name]["note"] += "; ALMOST EMPTY: lower shape_lo or fix full/box"
        rrio.save_json(os.path.join(out, "curves.json"),
                       {"schema": "rr.textcurves/1", "cut": cid, "f0": cut["f0"], "n": cut["n"],
                        "fps": rrio.fps_str(tl["fps"]), "layers": curves})
        rrio.save_json(os.path.join(out, "layers.json"), {"schema": "rr.textlayers/1", "cut": cid, "layers": meta})
        final = {n: repaired.get(n, m) for n, m in masks.items()}
        prev = np.full((h, w), 60, np.uint8)
        for m in final.values():
            prev[m] = 255
        rrio.write_image(os.path.join(out, "preview.png"), prev)
        sheet = qa_sheet(W, cid, st, final, cut["f0"])
        summary[cid] = {n: (c["opacity"][0], c["opacity"][len(c["opacity"]) // 2], c["opacity"][-1]) for n, c in curves.items()}
        log(f"{cid}: {len(spec['layers'])} layers in {time.time() - t0:.1f} s -> text/{cid}/ "
            f"({', '.join(str(n) + ' ' + str(meta[n]['pixels']) + 'px' for n in meta)}), sheet {sheet}")
        for n in meta:
            c = curves[n]["opacity"]
            fon = next((i for i, v in enumerate(c) if v > 0.02), None)
            f95 = next((i for i, v in enumerate(c) if v >= 0.95), None)
            log(f"   {n:>10}: opacity first>0 rel {fon}, >=0.95 rel {f95}, end {c[-1]:.2f}; {meta[n]['note']}")
    return 0


def qa_sheet(W, cid, st, masks, f0=0):
    """Per layer: reference crop at its middle full frame | rebuilt layer | diff (from the pass-1 QA crops)."""
    imgs, labs = [], []
    for S in st:
        L, name = S["L"], S["name"]
        x0, y0, x1, y1 = S["pbox"]
        mid = S["mid"]
        ref = S["mid_crop"]
        if ref is None:
            raise RuntimeError(f"{cid}/{name}: frame rel {mid} was not decoded")
        lay = np.full((y1 - y0, x1 - x0, 3), 40, np.uint8)
        lay[masks[name][y0:y1, x0:x1]] = 255
        val, sat = key_planes(ref, S["key"])
        k1 = key_soft(val.astype(np.float32), sat.astype(np.float32),
                      float(L.get("shape_lo", 230)), float(L.get("sat_lo", 30)), float(L.get("sat_hi", 70))) > 0.5
        bx0, by0, bx1, by1 = S["box"]
        inbox = np.zeros((y1 - y0, x1 - x0), bool)
        inbox[by0 - y0:by1 - y0, bx0 - x0:bx1 - x0] = True
        k1 &= inbox
        lm = masks[name][y0:y1, x0:x1]
        diff = np.full((y1 - y0, x1 - x0, 3), 30, np.uint8)
        diff[~inbox] = 12
        diff[k1 & lm] = 255
        diff[k1 & ~lm] = (255, 40, 40)
        diff[~k1 & lm] = (40, 220, 255)
        imgs += [ref, lay, diff]
        labs += [f"{name} REF F{f0 + mid}", f"{name} LAYER", f"{name} DIFF"]
    p = wpath(W, f"qa/text_{cid}.jpg")
    rrio.tile_sheet(imgs, labs, cols=3, out_path=p, tile_w=420, max_bytes=350_000, max_w=1300,
                    title=f"{cid} text layers: ref | rebuilt | red=ref only cyan=layer only")
    return rel_to(W, p)


# --------------------------------------------------------------------------------------------------
# check
# --------------------------------------------------------------------------------------------------
def cmd_check(a):
    """One streaming pass per cut over the video's layer boxes (per-pixel key/saturation sums over each
    layer's fully-on frames) and, for behind layers, one sequential pass over the matte (summed in uint32)."""
    W = os.path.abspath(a.W)
    tl = asm.load_timeline(W, a.edl, a.src)
    specs, _ = load_specs(W, a.specs, "text specs")
    byid = {c["id"]: c for c in tl["cuts"]}
    video = wpath(W, a.video or "out/base.mp4")
    if not os.path.isfile(video):
        raise UsageError(f"video not found: {video}")
    vinfo = rrio.probe(video)
    if (vinfo["w"], vinfo["h"]) != (tl["cw"], tl["ch"]):
        raise UsageError(f"{video} is {vinfo['w']}x{vinfo['h']}, the reference canvas is {tl['cw']}x{tl['ch']}")
    tp = wpath(W, a.pass_specs or "plan/text_pass.json")
    behind, mattes_cfg = {}, {}
    if os.path.isfile(tp):
        for c, v in (rrio.load_json(tp).get("cuts") or {}).items():
            for Ly in v.get("layers", []):
                behind[(c, Ly["name"])] = bool(Ly.get("behind"))
            if v.get("matte"):
                mattes_cfg[c] = (v["matte"], v.get("matte_clip_y"))
    ids = [s.strip() for s in a.cuts.split(",")] if a.cuts else \
        [c for c in specs if not c.startswith("_") and os.path.isfile(wpath(W, f"text/{c}/curves.json"))]
    x, y, w, h = tl["win"]
    out, fixes = {}, []
    for cid in ids:
        if cid not in byid:
            raise UsageError(f"unknown cut {cid}")
        cut = byid[cid]
        res, fix = {}, False
        st = []
        for L in specs[cid]["layers"]:
            name = L["name"]
            png = wpath(W, f"text/{cid}/{name}.png")
            if not os.path.isfile(png):
                continue
            ref = rrio.read_image(png, "gray") > 127
            if ref.sum() < 30:
                continue
            if ref.shape != (h, w):
                raise UsageError(f"{cid}/{name}: layer is {ref.shape[1]}x{ref.shape[0]}, window {w}x{h}")
            a0, a1 = full_range(L, cut)
            S = {"L": L, "name": name, "ref": ref, "a0": a0, "a1": a1, "box": _box(L["box"], w, h),
                 "key": L.get("key", "white"), "stat": "mean"}
            if S["key"] not in ("white", "black"):
                raise UsageError(f"unknown key {S['key']!r} (white|black)")
            _layer_stat_init(S)
            st.append(S)
        if st:
            ubox = _union_box([S["box"] for S in st], w, h, CHROMA_PAD)
            lo = min(S["a0"] for S in st)
            hi = max(S["a1"] for S in st)
            for f, fr in window_crop_frames(video, tl, vinfo, cut["f0"] + lo, hi - lo + 1, ubox):
                rel = f - cut["f0"]
                for S in st:
                    if S["a0"] <= rel <= S["a1"]:
                        _layer_stat_add(S, *_box_planes(fr, S["box"], ubox, S["key"]))
            # behind layers: mean fitted matte over the fully-on frames, summed while the matte streams by
            need = [S for S in st if behind.get((cid, S["name"]))]
            if need and cid in mattes_cfg:
                mp, clip_y = mattes_cfg[cid]
                mp = f"mattes/fit/{cid}.mkv" if mp is True else mp
                gs = None
                try:
                    gs = GrayStream(W, mp, clip_y)
                    if (gs.h, gs.w) != (h, w):
                        raise UsageError(f"matte {rel_to(W, gs.path)} is {gs.w}x{gs.h}, window {w}x{h}")
                    mult = {}
                    for S in need:
                        cnt = collections.Counter(min(gs.n - 1, asm.half_up(r * gs.n / cut["n"]))
                                                  for r in range(S["a0"], S["a1"] + 1))
                        S["msum"] = np.zeros((h, w), np.uint32)
                        S["mcnt"] = S["a1"] - S["a0"] + 1
                        for i, c in cnt.items():
                            mult.setdefault(i, []).append((S, c))
                    for i in sorted(mult):
                        fr = gs.get(i)
                        for S, c in mult[i]:
                            S["msum"] += fr.astype(np.uint32) * np.uint32(c)
                except UsageError as ex:
                    for S in need:
                        S.pop("msum", None)
                    log(f"{cid}: matte unavailable ({ex}); behind layers judged without it")
                finally:
                    if gs is not None:
                        gs.close()
        for S in st:
            L, name, ref = S["L"], S["name"], S["ref"]
            x0, y0, x1, y1 = S["box"]
            box = np.zeros_like(ref)
            box[y0:y1, x0:x1] = True
            gen = np.zeros_like(ref)
            loose = np.zeros_like(ref)
            nodata = S["seen"] == 0
            if not nodata:
                A, B = S["acc"]
                k = key_soft((A / np.float64(S["seen"])).astype(np.float32), (B / np.float64(S["seen"])).astype(np.float32),
                             float(L.get("shape_lo", 230)), float(L.get("sat_lo", 30)), float(L.get("sat_hi", 70)))
                gen[y0:y1, x0:x1] = k > 0.5
                loose[y0:y1, x0:x1] = k > 0.25
                loose = rrio.dilate(loose, 3)
            core = rrio.erode(ref, 3)
            core = core if core.sum() > 0.4 * ref.sum() else ref
            excl = np.zeros_like(ref)
            if "msum" in S:
                excl = S["msum"].astype(np.float64) * 2 > 255.0 * S["mcnt"]
            core = core & ~excl
            hidden = core.sum() < 30
            recall = 1.0 if hidden else float((loose & core).sum() / core.sum())
            spurious = float((gen & ~rrio.dilate(ref, 7)).sum() / ref.sum())
            bad = recall < 0.85 or spurious > 0.15 or nodata
            fix |= bad
            res[name] = {"recall": round(recall, 3), "spurious": round(spurious, 3), "bad": bad, "hidden": hidden}
            if nodata:
                res[name]["note"] = "the video has no frames in this layer's full range"
            log(f"{cid} {name:>10}: recall {recall:.2f} spurious {spurious:.2f} {'<-- FIX' if bad else 'ok'}"
                f"{' (fully behind the person)' if hidden else ''}{' (NO FRAMES in the full range)' if nodata else ''}")
        out[cid] = {"fix": fix, "layers": res}
        if fix:
            fixes.append(cid)
    rrio.save_json(wpath(W, "text/textcheck.json"),
                   {"schema": "rr.textcheck/1", "video": rel_to(W, video), "cuts": out, "fix": fixes})
    log(f"check: {rel_to(W, video)}; cuts to fix: {fixes}; -> text/textcheck.json")
    return 0


# --------------------------------------------------------------------------------------------------
# pass
# --------------------------------------------------------------------------------------------------
class CutPass:
    """One cut of the text pass. Layer alphas (and glow/backing) are kept as crops of their bounding box only;
    the matte is opened when the stream reaches the cut (open()), read as uint8 in frame order, and released
    at the cut's end (close()), so memory does not grow with the number or length of cuts."""

    def __init__(self, W, tl, cid, cut, c, mask_win, logo):
        self.id, self.cut, self.c = cid, cut, c
        self.n = cut["n"]
        h, w = mask_win.shape
        if c.get("hairfix"):
            raise UsageError(f"{cid}: hairfix is disabled; face/head appearance corrections require an authorized generative operation")
        self.cleanup = bool(c.get("cleanplate") or c.get("inpaint"))
        needs_occlusion = any(layer.get("behind") for layer in c.get("layers", []))
        if (self.cleanup or needs_occlusion) and not c.get("matte"):
            raise UsageError(f"{cid}: background cleanup and behind-subject text require a verified subject exclusion matte covering all people")
        if self.cleanup and c.get("matte_clip_y") is not None:
            raise UsageError(f"{cid}: background cleanup requires the complete subject matte; matte_clip_y is unsupported")
        self.layers = []
        if c.get("layers"):
            curves = load_curves(W, cid)
            for spec in c["layers"]:
                name = spec["name"]
                png = wpath(W, f"text/{cid}/{name}.png")
                if not os.path.isfile(png):
                    raise UsageError(f"{cid}: missing {rel_to(W, png)} (run layers)")
                if name not in curves:
                    raise UsageError(f"{cid}: no curve for {name} in text/{cid}/curves.json")
                al = rrio.read_image(png, "gray").astype(np.float32) / 255
                if al.shape != (h, w):
                    raise UsageError(f"{cid}/{name}: layer is {al.shape[1]}x{al.shape[0]}, window {w}x{h}")
                al *= mask_win * float(spec.get("gain", 1.0))
                al = np.clip(al, 0, 1)
                cv = np.clip(np.asarray(curves[name], np.float64), 0, 1)
                sh = int(spec.get("shift", 0))
                if sh > 0:
                    cv = np.r_[np.zeros(sh), cv[:-sh]] if sh < len(cv) else np.zeros_like(cv)
                elif sh < 0:
                    cv = np.r_[cv[-sh:], np.full(-sh, cv[-1])]
                g = spec.get("glow")
                glow = None
                if g:
                    glow = (rrio.gauss_blur(al, float(g[0])) * float(g[1])).astype(np.float32) * mask_win
                bk = spec.get("backing")
                backing = None
                if bk:  # soft dark halo under the letters so white text reads on a bright generated plate
                    backing = (np.clip(rrio.gauss_blur(al, float(bk[0])) * 2.5, 0, 1) * float(bk[1])).astype(np.float32) * mask_win
                ext = al
                for extra in (glow, backing):
                    if extra is not None:
                        ext = np.maximum(ext, extra)
                bb = _bbox_of(ext, 1e-3)

                def crop(v):
                    if v is None or bb is None:
                        return None
                    return np.ascontiguousarray(v[bb[0]:bb[1], bb[2]:bb[3]])
                self.layers.append({"name": name, "a": crop(al), "curve": cv, "behind": bool(spec.get("behind")),
                                    "glow": crop(glow), "backing": crop(backing), "bb": bb,
                                    "color": np.asarray(spec.get("color", [255, 255, 255]), np.float32)})
                del al, glow, backing, ext
        self.matte = None
        if c.get("matte"):
            mp = f"mattes/fit/{cid}.mkv" if c["matte"] is True else c["matte"]
            self.matte = GrayStream(W, mp, c.get("matte_clip_y"))  # probed now; decoded only inside the cut
            if (self.matte.h, self.matte.w) != (h, w):
                raise UsageError(f"{cid}: matte is {self.matte.w}x{self.matte.h}, window {w}x{h}")
            if self.cleanup and self.matte.n != self.n:
                raise UsageError(f"{cid}: cleanup matte must have one aligned frame per cut frame ({self.matte.n} != {self.n})")
        self._pi, self._pf = None, None
        self.logo = logo if c.get("logo") else None
        self.held = None
        self.held_background = None

    def close(self):
        """The stream left this cut: stop the matte decoder and drop the held frames."""
        if self.matte is not None:
            self.matte.close()
        self._pi, self._pf = None, None
        self.held = None
        self.held_background = None

    def person(self, rel):
        """float32 window-size person alpha (0..1) for timeline frame rel of the cut, or None."""
        if self.matte is None:
            return None
        n = self.matte.n
        i = rel if n == self.n else min(n - 1, asm.half_up(rel * n / self.n))
        if i != self._pi:
            self._pi, self._pf = i, self.matte.get(i).astype(np.float32) / 255
        return self._pf

    def apply(self, win, rel):
        """win: window float32 HxWx3 (modified and returned)."""
        c = self.c
        person = self.person(rel)
        protected = rrio.dilate(person > 0, 5) if self.cleanup and person is not None else None
        cp = c.get("cleanplate")
        if cp:
            x0, y0, x1, y1 = cp["box"]
            fr, until = int(cp.get("from", 0)), cp.get("until")
            if rel == fr:
                self.held = win[y0:y1, x0:x1].copy()
                self.held_background = ~protected[y0:y1, x0:x1]
            if rel > fr and self.held is not None and (until is None or rel <= int(until)):
                background = self.held_background & ~protected[y0:y1, x0:x1]
                region = win[y0:y1, x0:x1]
                region[background] = self.held[background]
        ip = c.get("inpaint")
        if ip and (not ip.get("frames") or ip["frames"][0] <= rel <= ip["frames"][1]):
            mn, mx = win.min(axis=2), win.max(axis=2)
            hit = np.zeros(win.shape[:2], bool)
            for x0, y0, x1, y1 in ip["boxes"]:
                hit[y0:y1, x0:x1] = (mn[y0:y1, x0:x1] > float(ip.get("lo", 215))) & \
                                    ((mx - mn)[y0:y1, x0:x1] < float(ip.get("sat", 40)))
            hit &= ~protected
            if hit.any():
                # Expanding a text hole must never expand into a face/person.
                inpaint_nc(win, rrio.dilate(hit, 5) & ~protected)
        for L in self.layers:
            o = float(L["curve"][min(rel, len(L["curve"]) - 1)])
            if o <= 0.002 or L["bb"] is None:
                continue
            y0, y1, x0, x1 = L["bb"]
            sub = win[y0:y1, x0:x1]
            a = L["a"] * o
            gl = L["glow"] * o if L["glow"] is not None else None
            bk = L["backing"] * o if L["backing"] is not None else None
            if L["behind"] and person is not None:
                keep = 1 - person[y0:y1, x0:x1]
                a = a * keep
                gl = gl * keep if gl is not None else None
                bk = bk * keep if bk is not None else None
            if bk is not None:
                sub *= (1 - bk[..., None])
            if gl is not None:
                sub += (255 - sub) * gl[..., None]
            sub *= (1 - a[..., None])
            sub += L["color"] * a[..., None]
        if self.logo is not None:
            lg, lx, ly = self.logo
            hh, ww = lg.shape[:2]
            H, Wd = win.shape[:2]
            xa, ya = max(0, lx), max(0, ly)
            xb, yb = min(Wd, lx + ww), min(H, ly + hh)
            if xb > xa and yb > ya:
                part = lg[ya - ly:yb - ly, xa - lx:xb - lx]
                al = part[..., 3:4] / 255.0
                reg = win[ya:yb, xa:xb]
                reg[...] = reg * (1 - al) + part[..., :3] * al
        return win


def cmd_pass(a):
    W = os.path.abspath(a.W)
    tl = asm.load_timeline(W, a.edl, a.src)
    cfg, cp = load_specs(W, a.specs, "text pass config")
    base = wpath(W, a.base or "out/base.mp4")
    if not os.path.isfile(base):
        raise UsageError(f"base video not found: {base}")
    out = wpath(W, a.out or "out/text.mp4")
    if os.path.abspath(out) == os.path.abspath(base):
        raise UsageError("--out must differ from --base")
    binfo = rrio.probe(base)
    if (binfo["w"], binfo["h"]) != (tl["cw"], tl["ch"]):
        raise UsageError(f"base is {binfo['w']}x{binfo['h']}, the reference canvas is {tl['cw']}x{tl['ch']}")
    mask_win, mask_how = asm.window_mask(W, tl)
    byid = {c["id"]: c for c in tl["cuts"]}
    logo = None
    if cfg.get("logo"):
        lp = wpath(W, cfg["logo"]["png"])
        if not os.path.isfile(lp):
            raise UsageError(f"logo png not found: {lp}")
        logo = (rrio.read_image(lp, "rgba").astype(np.float32), int(cfg["logo"]["x"]), int(cfg["logo"]["y"]))
    cuts = {}
    for cid, c in (cfg.get("cuts") or {}).items():
        if cid.startswith("_"):
            continue
        if cid not in byid:
            raise UsageError(f"text_pass.json: unknown cut {cid}")
        cuts[cid] = CutPass(W, tl, cid, byid[cid], c, mask_win, logo)
    frame_cut = {f: cid for cid, c in cuts.items() for f in range(c.cut["f0"], c.cut["f1"] + 1)}
    x, y, w, h = tl["win"]
    audio_src = base if binfo.get("has_audio") else tl["src"]
    proc, tmp, errf, audio = asm.open_encoder(out, tl["cw"], tl["ch"], tl["fps"], None if a.no_audio else audio_src,
                                              a.crf, a.preset, binfo if audio_src == base else tl["info"], a.threads)
    t0 = time.time()
    nfr = 0
    touched = 0
    cur = None
    try:
        for f, fr in asm.frame_reader(base, binfo, [(0, None)]):
            cid = frame_cut.get(f)
            if cid != cur:  # leaving a cut: release its matte reader before the next one opens
                if cur is not None:
                    cuts[cur].close()
                cur = cid
            if cid:
                cpo = cuts[cid]
                rel = f - cpo.cut["f0"]
                wf = fr[y:y + h, x:x + w].astype(np.float32)
                cpo.apply(wf, rel)
                fr[y:y + h, x:x + w] = np.clip(wf + 0.5, 0, 255).astype(np.uint8)
                touched += 1
            try:
                proc.stdin.write(fr)
            except BrokenPipeError:
                break
            nfr += 1
    except BaseException:
        asm.abort_encoder(proc, tmp, errf)
        raise
    finally:
        for cpo in cuts.values():
            cpo.close()
    asm.close_encoder(proc, tmp, errf, out)
    ref_n = tl["frames"]
    log(f"pass: {rel_to(W, out)}: {nfr} frames ({touched} touched in {len(cuts)} cuts) in {time.time() - t0:.1f} s, "
        f"audio {audio}, mask {mask_how}")
    if ref_n and nfr != ref_n:
        log(f"pass: warning: base has {nfr} frames, reference {ref_n}")
    return 0


# --------------------------------------------------------------------------------------------------
# logo
# --------------------------------------------------------------------------------------------------
def cmd_logo(a):
    W = os.path.abspath(a.W)
    tl = asm.load_timeline(W, a.edl, a.src)
    try:
        bx, by, bw, bh = [int(v) for v in a.box.split(",")]
    except ValueError:
        raise UsageError("--box must be x,y,w,h (window px)") from None
    X, Y, w, h = tl["win"]
    if bw < 8 or bh < 8 or bx < 0 or by < 0 or bx + bw > w or by + bh > h:
        raise UsageError(f"--box {a.box} must lie inside the {w}x{h} window and be at least 8x8")
    start, count = 0, None
    if a.frames:
        fa, fb = [int(v) for v in a.frames.split("-")]
        start, count = fa, fb - fa + 1
    F = np.stack([f for _, f in rrio.read_frames(tl["src"], start=start, count=count, crop=(X + bx, Y + by, bw, bh),
                                                 info=tl["info"])])  # uint8, the small logo box only
    mn = F.min(axis=3).astype(np.float32)
    ring = np.ones((bh, bw), bool)
    ring[3:-3, 3:-3] = False
    bg = np.array([np.median(m[ring]) for m in mn])
    order = np.argsort(bg)
    dark = order[:max(3, len(order) // 10)]
    Lm = np.median(mn[dark], axis=0)
    b = float(np.median(bg[dark]))
    alpha = np.clip((Lm - b) / max(1.0, 255 - b), 0, 1)
    alpha[alpha < 0.04] = 0
    rgba = np.dstack([np.full((bh, bw, 3), 255, np.uint8), rrio.to_uint8(alpha * 255)])
    p = wpath(W, a.out or "text/logo.png")
    rrio.write_image(p, rgba)
    # QA: darkest reference crop | logo on grey | logo on the brightest crop
    bright = order[-1]
    grey = np.full((bh, bw, 3), 90, np.float32)
    on_grey = grey * (1 - alpha[..., None]) + 255 * alpha[..., None]
    on_bright = F[bright].astype(np.float32) * (1 - alpha[..., None]) + 255 * alpha[..., None]
    q = wpath(W, "qa/logo.jpg")
    rrio.tile_sheet([F[dark[0]], on_grey, F[bright], on_bright],
                    [f"REF F{start + int(dark[0])}", "LOGO", f"REF F{start + int(bright)}", "LOGO OVER IT"],
                    cols=4, out_path=q, tile_w=240, max_bytes=200_000)
    if not a.no_update:
        tp = wpath(W, a.pass_specs or "plan/text_pass.json")
        cfg = rrio.load_json(tp) if os.path.isfile(tp) else {"cuts": {}}
        cfg["logo"] = {"png": rel_to(W, p), "x": bx, "y": by}
        rrio.save_json(tp, cfg)
    log(f"logo {bw}x{bh} at {bx},{by} (window px) from {len(dark)} dark frames (bg {b:.0f}), peak alpha "
        f"{alpha.max():.2f} -> {rel_to(W, p)}, qa/logo.jpg" + ("" if a.no_update else ", plan/text_pass.json logo set"))
    return 0


# --------------------------------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(description="Text from the reference's own pixels: static layers + opacity "
                                             "curves, text check, timeline-fps text pass, clean logo.",
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=__doc__.split("\n\n", 1)[1])
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p):
        p.add_argument("W", help="workspace dir")
        p.add_argument("--edl", help="timeline JSON (default plan/edl.json, else analysis/analysis.json)")
        p.add_argument("--src", help="override the reference video")

    p = sub.add_parser("layers", help="build static text layers + opacity curves from the reference")
    common(p)
    p.add_argument("--specs", default="plan/text_specs.json")
    p.add_argument("--cuts", help="comma list (default: every cut in the specs)")
    p = sub.add_parser("check", help="recall/spurious of every layer in a rebuild")
    common(p)
    p.add_argument("--video", help="video to check (default out/base.mp4)")
    p.add_argument("--specs", default="plan/text_specs.json")
    p.add_argument("--pass-specs", help="text pass config for 'behind' + mattes (default plan/text_pass.json)")
    p.add_argument("--cuts")
    p = sub.add_parser("pass", help="lay the text layers (and logo) onto a base video")
    common(p)
    p.add_argument("--base", help="input video (default out/base.mp4)")
    p.add_argument("--specs", default="plan/text_pass.json")
    p.add_argument("--out", help="output (default out/text.mp4)")
    p.add_argument("--crf", type=float, default=14)
    p.add_argument("--preset", default="medium")
    p.add_argument("--threads", type=int, help="x264 threads (default auto)")
    p.add_argument("--no-audio", action="store_true")
    p = sub.add_parser("logo", help="key a clean watermark from the darkest frames")
    common(p)
    p.add_argument("--box", required=True, help="x,y,w,h in window px, a little larger than the logo")
    p.add_argument("--frames", help="a-b timeline frames to use (default all)")
    p.add_argument("--out", help="output PNG (default text/logo.png)")
    p.add_argument("--pass-specs", help="text pass config to update (default plan/text_pass.json)")
    p.add_argument("--no-update", action="store_true", help="do not write the logo into text_pass.json")
    a = ap.parse_args(argv)
    if not os.path.isdir(a.W):
        raise UsageError(f"workspace not found: {a.W}")
    return {"layers": cmd_layers, "check": cmd_check, "pass": cmd_pass, "logo": cmd_logo}[a.cmd](a)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except UsageError as ex:
        print(f"textlayers: error: {ex}", file=sys.stderr)
        sys.exit(2)
    except (RuntimeError, ValueError, KeyError, IndexError, FileNotFoundError) as ex:
        print(f"textlayers: error: {type(ex).__name__}: {ex}", file=sys.stderr)
        sys.exit(1)
