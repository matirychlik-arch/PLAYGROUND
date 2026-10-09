#!/usr/bin/env python3
"""Frame-exact rebuild of a reference whose hero is swapped inside its own footage (Genjutsu family).

  python3 $RR/assemble.py $W --control          # alignment gate BEFORE any paid job (exit 3 when it fails)
  python3 $RR/assemble.py $W --control --dry    # + run every plan/renders.json cut through the generated
                                                #   path with its padded INPUT clip as a stand-in render
  python3 $RR/assemble.py $W                    # plan/renders.json -> out/base.mp4 + out/base_report.json

One streaming pass: the reference is decoded once (rgb24 pipe, frame-exact by index), every timeline frame
is either passed through untouched or gets its generated frame composited into the footage window, and the
result goes straight into one libx264 pipe with the reference audio stream-copied (-c:a copy). No
intermediate PNGs, no concat, no ffmpeg overlay graph (the overlay-onto-a-colour-source 1-frame shift
cannot happen). Output frame count == decoded reference frame count, always.
Memory is flat in cut length: a producer thread decodes each render (and its matte) ONCE, sequentially
(the mapping is non-decreasing), fits/grades/closes a few frames ahead in a small pool, and hands frames
to the compositing loop through a byte-capped queue (PREFETCH_BYTES); nothing per cut is stacked.

TIMELINE (first file that has "cuts"): --edl FILE, else W/plan/edl.json, else W/analysis/analysis.json.
  {"source": "ref/ref.mp4",                     # default ref/ref.mp4; every path is relative to W
   "fps": "60/1", "frames": 862,                # optional (probed; fps is an exact Fraction, never rounded)
   "window": {"x":42,"y":540,"w":996,"h":836,"radius":97}   # or [x,y,w,h]; false or the whole frame =
                                                # full frame; null/absent = from analysis (below);
                                                # "letterbox": {top,bottom,left,right} also accepted;
                                                # radius absent -> measured from the reference
   "window_mask": "analysis/window_mask.png",   # optional canvas-size mask (white = footage), used only
                                                #   when its lit bbox matches the window within 1 px
   "cuts": [{"id":"c01","f0":0,"f1":15,          # inclusive frames ("start"/"end" exclusive also accepted)
             "src_fps":"24/1"}]}                # source cadence of the cut; or "cadence": {"pattern":
                                                #   "pulldown_24in60"|..., "src_fps": ...}; default = timeline fps
  The window falls back to analysis/analysis.json (canvas.crop_used first, exactly like frames.py: a
  full-frame crop_used, e.g. analyze_ref.py --no-window, means NO window), then analysis/breakdown.json
  format_lock.window. Mask: --mask, plan window_mask, plan/window_mask.png, analysis/window_mask.png -
  each only when its lit area (> 50%) has the window's bbox within 1 px (a stale mask from another
  window is skipped with a warning; a mismatching --mask is an error) - else a rounded rect.

RENDERS (W/plan/renders.json, or --renders): {cut_id: entry}. Cuts not listed keep the reference pixels.
  {"c03": {"path": "gen/c03.mp4",               # Genjutsu output / plate / still (png|jpg)
           "pad_json": "gen/c03_pad.json",      # frames.py pad JSON: {orig_frames|src_frames, padded_frames,
                                                #   keep_padded_index, fps, fps_in?, src?, src_timeline_frames?}
           "cut_json": "cuts/c03.json",         # frames.py export JSON (src_index); default: found next to
                                                #   the pad JSON's "src" clip
           "pad_video": "gen/c03_pad.mp4",      # the padded INPUT clip (only used by --control --dry)
           "src_fps": "24/1",                   # override of the cut's source cadence
           "gen_start": 0, "gen_fps": "24/1",   # no pad_json: g = gen_start + round(rel*gen_fps/fps)
           "gen_range": [10, 52],               # no pad_json: stretch the cut over these gen frames (incl.)
           "crop": [88, 0, 1487, 1248],         # gen px region mapped onto the window (default: whole frame)
           "fit": {"scale": 0.67, "offset": [88, 0],      # = crop [ox, oy, W/scale, H/scale]
                   "person_box": [x0,y0,x1,y1],           # OR auto: hero box in WINDOW px of the reference,
                   "gen_box": [x0,y0,x1,y1],              #   gen person box in gen px (else matte bbox)
                   "tilt": 84, "pan": 0,                  # crop drift over the cut in gen px (tilt>0 = up)
                   "zoom": 1.1, "ease": true},            # digital push-in re-done at timeline fps
           "grade_match": 0.5,                  # pull mean/std per channel k of the way to the ref cut
           "blur": [[0, 470, 70, 660]], "blur_sigma": 12,   # window px boxes (stray generated text)
           "matte": "mattes/c03_rb.mp4",        # remove_background of THIS render (person on black),
           "matte_mode": "black"}}              #   "mask" = white-on-black mask video; or a PNG dir
  Frame mapping per timeline frame rel of the cut (all integer maths on Fractions, half-up rounding):
    k = source index: when the exported frames are known (export src_index / src_timeline_frames) the
        exported frame that best MATCHES reference frame f0+rel among its time neighbours (exact for
        pulldown whatever phase the exporter chose); else round(rel * src_fps / fps), src_fps from
        renders > pad (src_fps|fps_in) > the cut's cadence > timeline fps, re-derived from the clip's
        frame count when they disagree
    g = round(keep_padded_index[k] * gen_frames / padded_frames)     (the proven Altman mapping)
  A matte writes W/mattes/fit/<cut>.mkv (ffv1 gray, window size, ONE FRAME PER TIMELINE FRAME of the cut)
  for textlayers.py pass "behind" layers, and qa/fit_<cut>.jpg shows ref | ours with the matte outline.

COMPOSITE: --canvas ref (default) keeps every pixel outside the window from the reference frame and blends
the generated window in with the anti-aliased mask; --canvas black = pad on black and multiply by the mask
(the colleague's gbrp blend multiply, done in numpy). Kept cuts in ref mode are bit-exact pass-through.

OUTPUT: out/base.mp4 (+ out/base_report.json) or out/control.mp4 (+ out/control_report.json,
qa/cadence.json). The report has per-cut window PSNR vs the reference at offsets -1/0/+1 measured on the
ENCODED file (160 px gray), unique-frame counts (cadence) of ref vs ours, the mapping used and warnings.
Control gate: every cut best at +0 and >= 35 dB, else exit 3.
  Fast-content cuts (--dry only): a cut whose content shows more distinct images per second than the export
  rate (frames.py export cuts/<id>.json runs_dropped > 0, or analysis cadence native/mixed with
  unique/of x fps > the export fps) cannot keep every image in ANY 24p export (Altman c02 32.5, c05 34.8,
  c08 33.6, c12 27.6, c15 34.0, c16 30.0 dB). Such a cut needs best +0 and >= its own floor
  max(--gate-fast-db 25, min(--gate-db 35, export match - 2 dB)), where "export match" is the PSNR of the
  exported images content-matched back onto the reference (the best this export can do; the six cuts above
  measure within 0.2 dB of it); the run prints 'fast-content cut: 24p export drops N images (expected)'.
  A flat 25 dB would pass a mis-mapped clip: c05 driven one exported image late is 25.8 dB, still best +0.
qa/cadence.json (control only, an ESTIMATE from frame differences - confirm on a sheet): per cut
  {pattern ("24in60", "native", ...), src_fps, src_timeline_frames (the frames where a new source frame
  starts), sim_fps_filter_at_plan_fps, sim_fps_filter_at_detected, sim_exact_hold}. The sims rebuild the cut
  from the reference itself: a plain `ffmpeg fps=24` export mapped back with round(rel*24/60) vs an export
  of exactly src_timeline_frames held until the next one. On Altman's 2:3-pulldown cuts the plain export
  lands at 22-31 dB (judder: duplicated and skipped source frames), the exact one at 38-48 dB. Export the
  Genjutsu inputs with `frames.py export W --cut ID --fps 24 --crop window` (one frame per source image,
  cuts/<ID>.json src_index, which this script content-matches) and `frames.py pad`; the control prints a
  hint for the cuts where a plain fps=24 export would fail the gate.
Exit codes: 0 ok, 1 runtime/ffmpeg error, 2 bad input, 3 control gate failed.
"""
from __future__ import annotations

import argparse
import bisect
import collections
import json
import math
import os
import queue
import subprocess
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from fractions import Fraction

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import rrio  # noqa: E402

GATE_DB = 35.0
GATE_FAST_DB = 25.0          # absolute floor of a fast-content cut (--dry): content faster than the export fps
FAST_MARGIN_DB = 2.0         # fast-content floor = min(GATE_DB, export match PSNR - this), never below GATE_FAST_DB
PSNR_W = 160
PREFETCH_BYTES = 192 << 20   # generated frames (+ mattes) rendered ahead of the compositing loop, at most
FRAME_WORKERS = max(2, min(4, os.cpu_count() or 2))   # grade/slice/blur and matte closing of upcoming frames
COPY_AUDIO = {"aac", "mp3", "alac", "ac3", "eac3", "opus", "mp2"}


class UsageError(Exception):
    pass


def log(*a):
    print(*a, flush=True)


def half_up(x):
    """Round half up for Fractions/floats (ffmpeg's NEAR_INF for positive values)."""
    if isinstance(x, Fraction):
        return int(math.floor(x + Fraction(1, 2)))
    return int(math.floor(float(x) + 0.5))


def wpath(W, p):
    """Resolve a plan path against the workspace W (absolute paths and ~ stay as they are)."""
    if p is None:
        return None
    p = os.path.expanduser(str(p))
    return p if os.path.isabs(p) else os.path.normpath(os.path.join(W, p))


def rel_to(W, p):
    try:
        r = os.path.relpath(p, W)
        return p if r.startswith("..") else r
    except ValueError:
        return p


# --------------------------------------------------------------------------------------------------
# timeline
# --------------------------------------------------------------------------------------------------
def _rect(v, cw, ch):
    """Window in any of the accepted shapes -> (x, y, w, h, radius|None) or None."""
    if v is None or v is False:
        return None
    if isinstance(v, (list, tuple)) and len(v) >= 4:
        x, y, w, h = [int(round(float(t))) for t in v[:4]]
        return (x, y, w, h, None)
    if isinstance(v, dict):
        if v.get("found") is False:
            return None
        for k in ("rect", "box", "xywh"):
            if isinstance(v.get(k), (list, tuple)) and len(v[k]) >= 4:
                x, y, w, h = [int(round(float(t))) for t in v[k][:4]]
                return (x, y, w, h, v.get("radius"))
        if all(k in v for k in ("x", "y", "w", "h")):
            r = v.get("radius", v.get("r"))
            return (int(round(v["x"])), int(round(v["y"])), int(round(v["w"])), int(round(v["h"])),
                    None if r is None else float(r))
        if all(k in v for k in ("top", "bottom", "left", "right")):  # letterbox
            l, t, r_, b = (int(round(v[k])) for k in ("left", "top", "right", "bottom"))
            return (l, t, cw - l - r_, ch - t - b, 0.0)
    return None


FULL_FRAME = "full frame"


def _doc_window(d, cw, ch):
    """Measured picture area; explicit plan/format lock precedes detected canvas geometry.

    canvas.crop_used describes inspection coverage, never the export/compositing window.
    FULL_FRAME means an explicit full-sized rectangle or window:false; None means unspecified.
    """
    if not isinstance(d, dict):
        return None
    canv = d.get("canvas") if isinstance(d.get("canvas"), dict) else {}
    fl = d.get("format_lock") if isinstance(d.get("format_lock"), dict) else {}

    def full(r):
        return (r[0], r[1], r[2], r[3]) == (0, 0, cw, ch)

    if d.get("window") is False:
        return FULL_FRAME
    for v in (d.get("window"), d.get("letterbox")):
        r = _rect(v, cw, ch)
        if r:
            return FULL_FRAME if full(r) else r
    if fl.get("window") is False:
        return FULL_FRAME
    for v in (fl.get("window"), fl.get("letterbox"), canv.get("window"), canv.get("letterbox")):
        r = _rect(v, cw, ch)
        if r:
            return FULL_FRAME if full(r) else r
    return None


def _snap_fps(f):
    return rrio.parse_fps(float(f)) if f else None


def cut_src_fps(c, T):
    """Source cadence of a cut (Fraction): explicit src_fps on the cut, else from the cadence pattern
    (analyze_ref.py / breakdown vocabulary), else the timeline fps."""
    for k in ("src_fps", "source_fps", "cut_fps"):
        if c.get(k):
            f = rrio.parse_fps(c[k])
            if f:
                return f, k
    cad = c.get("cadence")
    cd = cad if isinstance(cad, dict) else {}
    pat = str(cd.get("pattern") if cd else (cad or "")) or None
    est = rrio.parse_fps(cd.get("src_fps")) if cd.get("src_fps") else None
    ntsc = Fraction(T).denominator == 1001
    if pat and "24in" in pat:  # exact 2:3 / 2:2:2:4 pulldown: 24000/1001 only on an NTSC timeline
        return (Fraction(24000, 1001) if ntsc else Fraction(24)), f"cadence {pat}"
    if pat in ("native", "interp_slowmo", "blend_retime", "mixed", "short", "freeze", "burst", "speed_ramp"):
        return T, f"cadence {pat} -> timeline fps"
    if pat == "stepped":
        if est and float(est) < float(T):
            return est, "cadence stepped (src_fps estimate)"
        if cd.get("unique") and cd.get("of"):
            return _snap_fps(float(T) * cd["unique"] / cd["of"]), "cadence stepped unique/of"
    if est and float(est) <= float(T):
        return est, "cadence.src_fps"
    return T, "timeline fps (default)"


def _parse_cuts(raw, nframes):
    if not raw:
        return []
    if all(isinstance(v, (int, float)) for v in raw):  # a list of cut start frames
        starts = sorted({int(v) for v in raw if 0 <= int(v) < nframes} | {0})
        return [{"id": f"c{i + 1:02d}", "f0": s, "f1": (starts[i + 1] - 1 if i + 1 < len(starts) else nframes - 1)}
                for i, s in enumerate(starts)]
    out = []
    for i, c in enumerate(raw):
        if not isinstance(c, dict):
            raise UsageError(f"cut #{i} is not an object: {c!r}")
        if "f0" in c and "f1" in c:
            f0, f1 = int(c["f0"]), int(c["f1"])
        elif "start" in c and "end" in c:
            f0, f1 = int(c["start"]), int(c["end"]) - 1
        elif "start_frame" in c and "end_frame" in c:
            f0, f1 = int(c["start_frame"]), int(c["end_frame"]) - 1
        elif isinstance(c.get("frames"), (list, tuple)) and len(c["frames"]) == 2:
            f0, f1 = int(c["frames"][0]), int(c["frames"][1])
        else:
            raise UsageError(f"cut #{i} has no f0/f1 (or start/end): {json.dumps(c)[:120]}")
        d = dict(c)
        d["id"] = str(c.get("id") or f"c{i + 1:02d}")
        d["f0"], d["f1"] = f0, f1
        out.append(d)
    return out


def load_timeline(W, edl=None, src=None):
    """Cuts + window + source of the reference. Returns a dict (see module doc)."""
    W = os.path.abspath(W)
    cands = [edl] if edl else ["plan/edl.json", "analysis/analysis.json"]
    doc, docpath = None, None
    for c in cands:
        p = wpath(W, c)
        if p and os.path.isfile(p):
            d = rrio.load_json(p)
            if isinstance(d, dict) and d.get("cuts"):
                doc, docpath = d, p
                break
            if edl:
                raise UsageError(f"{p} has no 'cuts'")
    if doc is None:
        raise UsageError(f"no cut list in {W}: write plan/edl.json or run analyze_ref.py (analysis/analysis.json)")
    s = src or doc.get("source") or (doc.get("ref") or {}).get("path") or "ref/ref.mp4"
    sp = wpath(W, s)
    if not os.path.isfile(sp):
        raise UsageError(f"reference not found: {sp}")
    info = rrio.probe(sp)
    # This legacy timeline maps source frames with a single rational fps.
    # VFR media needs a PTS-aware route; never normalize it implicitly.
    rrio.require_cfr(sp, info)
    T = rrio.parse_fps(doc.get("fps")) or info["fps"]
    if not T:
        raise UsageError(f"{sp}: unknown frame rate")
    if info["fps"] and abs(float(T) - float(info["fps"])) > 1e-6:
        log(f"assemble: note: plan fps {rrio.fps_str(T)} != probed {info['fps_str']}; using the plan's")
    nframes = int(doc.get("frames") or doc.get("nb_frames") or info["nb_frames"] or 0)
    CW, CH = info["w"], info["h"]
    # Automatic analysis is lower priority than the measured breakdown lock.
    analysis_path = wpath(W, "analysis/analysis.json")
    win = None if docpath == analysis_path else _doc_window(doc, CW, CH)
    wsrc = rel_to(W, docpath) if win else None
    if win is None:
        for alt in ("analysis/breakdown.json", "analysis/analysis.json"):
            p = wpath(W, alt)
            if (p != docpath or p == analysis_path) and os.path.isfile(p):
                try:
                    a = rrio.load_json(p)
                except Exception:
                    continue
                win = _doc_window(a, CW, CH)
                if win:
                    wsrc = alt
                    break
    if win is None:
        win, wsrc = (0, 0, CW, CH, 0.0), "full frame"
    elif win == FULL_FRAME:
        win, wsrc = (0, 0, CW, CH, 0.0), f"full frame ({wsrc})"
    x, y, w, h, rad = win
    if w <= 0 or h <= 0 or x < 0 or y < 0 or x + w > CW or y + h > CH:
        raise UsageError(f"window {win[:4]} outside the {CW}x{CH} frame")
    cuts = _parse_cuts(doc["cuts"], nframes or 10 ** 9)
    if not cuts:
        raise UsageError("empty cut list")
    cuts.sort(key=lambda c: c["f0"])
    warns = []
    ap = wpath(W, "analysis/analysis.json")
    if docpath != ap and os.path.isfile(ap):
        try:
            aw = _doc_window(rrio.load_json(ap), CW, CH)
        except Exception:
            aw = None
        if aw is not None:
            ar = (0, 0, CW, CH) if aw == FULL_FRAME else tuple(aw[:4])
            if ar != (x, y, w, h):
                warns.append(f"window {(x, y, w, h)} ({wsrc}) overrides detected picture area {ar}; "
                             "verify the measured plan window against the source")
    prev = -1
    for c in cuts:
        if c["f1"] < c["f0"]:
            raise UsageError(f"cut {c['id']}: f1 {c['f1']} < f0 {c['f0']}")
        if c["f0"] != prev + 1:
            warns.append(f"cut {c['id']} starts at {c['f0']}, previous ended at {prev} "
                         f"({'gap: frames pass through' if c['f0'] > prev + 1 else 'OVERLAP'})")
            if c["f0"] <= prev:
                raise UsageError(warns[-1])
        prev = c["f1"]
        c["n"] = c["f1"] - c["f0"] + 1
        c["src_fps"], c["src_fps_from"] = cut_src_fps(c, T)
    if nframes and prev > nframes - 1:
        raise UsageError(f"last cut ends at {prev} but the reference has {nframes} frames")
    if nframes and prev < nframes - 1:
        warns.append(f"cuts end at {prev}, reference has {nframes} frames: the tail passes through")
    ids = [c["id"] for c in cuts]
    if len(set(ids)) != len(ids):
        raise UsageError("duplicate cut ids")
    mask_png = doc.get("window_mask")
    return {"W": W, "doc": docpath, "src": sp, "src_rel": rel_to(W, sp), "info": info, "fps": T,
            "frames": nframes, "cw": CW, "ch": CH, "win": (x, y, w, h), "radius": rad, "window_from": wsrc,
            "window_mask": wpath(W, mask_png) if mask_png else None, "cuts": cuts, "warnings": warns}


# --------------------------------------------------------------------------------------------------
# window mask
# --------------------------------------------------------------------------------------------------
def rounded_rect_mask(w, h, r):
    """Anti-aliased rounded rectangle coverage (float32 h x w, 1 inside) from a signed distance."""
    r = max(0.0, min(float(r or 0), w / 2.0, h / 2.0))
    if r < 0.5:
        return np.ones((h, w), np.float32)
    ys = np.arange(h, dtype=np.float32)[:, None] + 0.5
    xs = np.arange(w, dtype=np.float32)[None, :] + 0.5
    qx = np.abs(xs - w / 2.0) - (w / 2.0 - r)
    qy = np.abs(ys - h / 2.0) - (h / 2.0 - r)
    d = np.sqrt(np.maximum(qx, 0) ** 2 + np.maximum(qy, 0) ** 2) + np.minimum(np.maximum(qx, qy), 0) - r
    return np.clip(0.5 - d, 0, 1).astype(np.float32)


def measure_radius(src, info, win, every=None):
    """Corner radius of a window from the 'ever lit' area (pixels lit in >= 3 sampled frames).

    Unlit area of a quarter-circle corner of radius r = r^2 (1 - pi/4); median over the 4 corners."""
    x, y, w, h = win
    n = info.get("nb_frames") or 300
    every = every or max(1, n // 120)
    cnt = None
    for _, f in rrio.read_frames(src, crop=(x, y, w, h), every=every, info=info):
        m = f.max(axis=2) > 16
        cnt = m.astype(np.int16) if cnt is None else cnt + m
    if cnt is None:
        return 0.0
    lit = cnt >= 3
    s = max(8, min(w, h) // 3)
    rs = []
    for cx, cy in ((0, 0), (w - s, 0), (0, h - s), (w - s, h - s)):
        unl = int((~lit[cy:cy + s, cx:cx + s]).sum())
        rs.append(math.sqrt(unl / (1 - math.pi / 4)))
    r = float(np.median(rs))
    return round(min(r, min(w, h) / 4.0), 1)


def _lit_bbox(m, thr=0.5):
    """(x0, y0, x1, y1) exclusive of the pixels > thr, or None."""
    rows = np.nonzero((m > thr).any(axis=1))[0]
    if not len(rows):
        return None
    cols = np.nonzero((m > thr).any(axis=0))[0]
    return int(cols[0]), int(rows[0]), int(cols[-1]) + 1, int(rows[-1]) + 1


def window_mask(W, tl, override=None, measure=True):
    """(mask_win float32 h x w in 0..1, description). Order: --mask PNG, plan window_mask, plan/
    window_mask.png, analysis/window_mask.png, rounded rect (radius from the plan or measured, cached in
    plan/window_mask.json). A PNG (canvas size, or window size) is used only when its lit area (> 0.5) has
    the bbox of the window rect within 1 px: a mask left from another window (the plan widened it, or
    --no-window) would cut the picture or keep a strip of old footage. A mismatching --mask is an error,
    a mismatching discovered PNG is skipped with a warning."""
    x, y, w, h = tl["win"]
    cands = [(override, True), (tl.get("window_mask"), False), ("plan/window_mask.png", False),
             ("analysis/window_mask.png", False)]
    seen = set()
    for p, explicit in cands:
        if not p:
            continue
        pp = wpath(W, p)
        if pp in seen:
            continue
        seen.add(pp)
        if not os.path.isfile(pp):
            if explicit:
                raise UsageError(f"--mask not found: {pp}")
            continue
        m = rrio.read_image(pp, "gray").astype(np.float32) / 255.0
        name = rel_to(W, pp)
        canvas_size = m.shape == (tl["ch"], tl["cw"])
        if canvas_size:
            want, desc = (x, y, x + w, y + h), f"png {name}"
        elif m.shape == (h, w):
            want, desc = (0, 0, w, h), f"png {name} (window size)"
        else:
            msg = (f"mask {name} is {m.shape[1]}x{m.shape[0]}, neither the {tl['cw']}x{tl['ch']} canvas nor the "
                   f"{w}x{h} window")
            if explicit:
                raise UsageError(msg)
            log(f"assemble: warning: {msg}: ignored")
            continue
        bb = _lit_bbox(m)
        if bb is not None and max(abs(a_ - b_) for a_, b_ in zip(bb, want)) <= 1:
            return (m[y:y + h, x:x + w].copy() if canvas_size else m), desc
        msg = (f"mask {name}: lit area {bb} does not match the window {want} (x0,y0,x1,y1) within 1 px "
               f"(a mask from another window?)")
        if explicit:
            raise UsageError(msg)
        log(f"assemble: warning: {msg}: ignored, rounded-rect mask instead")
    if (w, h) == (tl["cw"], tl["ch"]):
        return np.ones((h, w), np.float32), "full frame (no window)"
    r = tl.get("radius")
    how = "plan"
    if r is None:
        cache = wpath(W, "plan/window_mask.json")
        c = rrio.load_json(cache, None) if os.path.isfile(cache) else None
        if c and c.get("win") == [x, y, w, h] and c.get("src") == tl["src_rel"]:
            r, how = c["radius"], "measured (cached plan/window_mask.json)"
        elif measure:
            r, how = measure_radius(tl["src"], tl["info"], (x, y, w, h)), "measured"
            try:
                rrio.save_json(cache, {"win": [x, y, w, h], "src": tl["src_rel"], "radius": r})
            except OSError:
                pass
        else:
            r, how = 0.0, "square (not measured)"
    return rounded_rect_mask(w, h, r), f"rounded rect r={r} ({how})"


def edge_leak(src, info, win, cw, ch, band=12):
    """How many px outside each side of the window rect the reference is still lit (max over sampled frames).

    A window detected a few px inside the real footage leaves a strip of the OLD footage around generated
    cuts in --canvas ref mode. Returns {"top","bottom","left","right"} in px (0 = clean edge)."""
    x, y, w, h = win
    if (w, h) == (cw, ch):
        return {"top": 0, "bottom": 0, "left": 0, "right": 0}
    ex0, ey0 = max(0, x - band), max(0, y - band)
    ex1, ey1 = min(cw, x + w + band), min(ch, y + h + band)
    n = info.get("nb_frames") or 300
    mx = None
    for _, f in rrio.read_frames(src, crop=(ex0, ey0, ex1 - ex0, ey1 - ey0), every=max(1, n // 90), gray=True,
                                 info=info):
        mx = f if mx is None else np.maximum(mx, f)
    if mx is None:
        return {}
    mx = mx.astype(np.float32)
    ox, oy = x - ex0, y - ey0
    inner = float(np.median(mx[oy + h // 4:oy + 3 * h // 4, ox + w // 4:ox + 3 * w // 4]))
    m = max(8, w // 6), max(8, h // 6)  # ignore the rounded corners
    profiles = {
        "top": [float(np.median(mx[oy - k, ox + m[0]:ox + w - m[0]])) for k in range(1, oy + 1)],
        "bottom": [float(np.median(mx[oy + h - 1 + k, ox + m[0]:ox + w - m[0]])) for k in range(1, mx.shape[0] - oy - h + 1)],
        "left": [float(np.median(mx[oy + m[1]:oy + h - m[1], ox - k])) for k in range(1, ox + 1)],
        "right": [float(np.median(mx[oy + m[1]:oy + h - m[1], ox + w - 1 + k])) for k in range(1, mx.shape[1] - ox - w + 1)],
    }
    out = {}
    for side, prof in profiles.items():
        if not prof:
            out[side] = 0
            continue
        canvas = min(prof[-3:]) if len(prof) >= 3 else prof[-1]
        thr = canvas + 0.25 * max(0.0, inner - canvas)
        k = 0
        while k < len(prof) and prof[k] > thr:
            k += 1
        out[side] = k
    return out


class Composer:
    """Puts a window-size frame into a canvas frame through the window mask."""

    def __init__(self, tl, mask, mode="ref"):
        self.x, self.y, self.w, self.h = tl["win"]
        self.cw, self.ch = tl["cw"], tl["ch"]
        self.mode = mode
        self.mask = mask
        self.inside = mask >= 0.999
        band = (mask > 0.001) & ~self.inside
        self.band = np.nonzero(band)
        self.mb = mask[self.band][:, None].astype(np.float32)
        self.outside = mask <= 0.001
        self.full = bool(self.inside.all())

    def put(self, frame, new):
        """frame: canvas HxWx3 uint8 (the reference frame, modified in place); new: window HxWx3 uint8."""
        x, y, w, h = self.x, self.y, self.w, self.h
        if self.mode == "black":
            frame[...] = 0
        win = frame[y:y + h, x:x + w]
        if self.full:
            win[...] = new
            return frame
        np.copyto(win, new, where=self.inside[..., None])
        if len(self.band[0]):
            nb = new[self.band].astype(np.float32)
            if self.mode == "black":
                v = nb * self.mb
            else:
                v = win[self.band].astype(np.float32) * (1 - self.mb) + nb * self.mb
            win[self.band] = np.clip(v + 0.5, 0, 255).astype(np.uint8)
        return frame


# --------------------------------------------------------------------------------------------------
# frame mapping
# --------------------------------------------------------------------------------------------------
def match_src_frames(L, base, f0, n, src_tl, T, S=None):
    """Content-matched source index per timeline frame: for timeline frame f0+rel pick the exported frame k
    (itself a reference frame, src_tl[k]) that looks most like reference frame f0+rel among its time
    neighbours. Exact for pulldown/holds whatever phase the exporter chose (frames.py export picks one frame
    per hold run, often mid-run); nearest in time for moving content. L: low-res gray frames, L[i] = frame base+i.
    Returns (ks, mean best MSE)."""
    tl = [int(t) for t in src_tl]
    if S:
        win = int(math.ceil(float(Fraction(T) / Fraction(S)))) + 1
    else:
        gaps = [b - a for a, b in zip(tl, tl[1:]) if b > a]
        win = (int(np.median(gaps)) if gaps else 1) + 1
    ks, best = [], []
    for r in range(n):
        t = f0 + r
        lo = bisect.bisect_left(tl, t - win)
        hi = bisect.bisect_right(tl, t + win)
        cand = list(range(lo, hi)) or [min(range(len(tl)), key=lambda k: abs(tl[k] - t))]
        sc = []
        for k in cand:
            i, j = tl[k] - base, t - base
            m = _mse(L[i], L[j]) if (0 <= i < len(L) and 0 <= j < len(L)) else 1e9
            sc.append((m + 0.25 * abs(tl[k] - t), abs(tl[k] - t), k, m))
        sc.sort()
        ks.append(sc[0][2])
        best.append(sc[0][3])
    return ks, float(np.mean(best)) if best else 0.0


def map_cut(n, T, S=None, src_frames=None, keep=None, padded=None, gen_frames=None, src_tl=None, f0=0,
            gen_start=0, gen_range=None, gen_fps=None, ks=None, ks_how=None):
    """Timeline frame rel (0..n-1) of a cut -> (k source index list, g gen index list, how).
    ks (precomputed source index per timeline frame, e.g. from match_src_frames) wins over src_tl/S."""
    T = Fraction(T)
    rel = range(n)
    how = []
    if ks is not None:
        ks = list(ks)
        how.append(ks_how or "k=given")
    elif src_tl:
        tl = [int(t) - f0 for t in src_tl]
        if any(b < a for a, b in zip(tl, tl[1:])):
            raise UsageError("src_timeline_frames must be increasing")
        ks = [max(0, bisect.bisect_right(tl, r) - 1) for r in rel]
        how.append("k=src_timeline_frames(hold)")
    elif keep is not None or src_frames:
        nsrc = src_frames or len(keep)
        Sx = Fraction(S) if S else T
        exp = n * Sx / T
        if abs(float(exp) - nsrc) > 2 + 0.02 * nsrc:
            # the exporter used another cadence than the plan says: trust the clip's own frame count
            Sx = T * Fraction(nsrc, n)
            how.append(f"src_fps from frame count ({nsrc}/{n} -> {float(Sx):.3f})")
        ks = [half_up(r * Sx / T) for r in rel]
        how.append(f"k=round(rel*{rrio.fps_str(Sx) if Sx.denominator < 10000 else f'{float(Sx):.3f}'}/{rrio.fps_str(T)})")
    else:
        ks = list(rel)
    if src_frames:
        ks = [min(max(k, 0), src_frames - 1) for k in ks]
    if keep is not None:
        P = int(padded or len(keep))
        gN = int(gen_frames or P)
        gs = [min(gN - 1, half_up(Fraction(int(keep[k]) * gN, P))) for k in ks]
        how.append(f"g=round(keep[k]*{gN}/{P})")
    elif gen_range:
        ga, gb = int(gen_range[0]), int(gen_range[1])
        L = gb - ga + 1
        gs = [ga + min(L - 1, (2 * r + 1) * L // (2 * n)) for r in rel]
        how.append(f"g=gen_range {ga}..{gb}")
    else:
        gf = Fraction(gen_fps) if gen_fps else T
        gs = [int(gen_start) + half_up(r * gf / T) for r in rel]
        how.append(f"g={gen_start}+round(rel*{rrio.fps_str(gf)}/{rrio.fps_str(T)})")
    if gen_frames:
        over = sum(1 for g in gs if g > gen_frames - 1)
        if over:
            how.append(f"CLAMPED {over} frames past the render end")
        gs = [min(max(g, 0), gen_frames - 1) for g in gs]
    return ks, gs, "; ".join(how)


# --------------------------------------------------------------------------------------------------
# generated cuts
# --------------------------------------------------------------------------------------------------
_COUNT_CACHE = {}
_PROBE_LOCK = threading.Lock()


def probe_counted(path):
    with _PROBE_LOCK:
        if path not in _COUNT_CACHE:
            p = rrio.probe(path)
            if not p.get("is_image"):
                p = rrio.probe(path, count=True)
            _COUNT_CACHE[path] = p
        return _COUNT_CACHE[path]


def _ease(t):
    return t * t * (3 - 2 * t)


def _bbox(m, thr=0.5, min_px=200):
    ys, xs = np.nonzero(m > thr)
    if len(xs) < min_px:
        return None
    return (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)


def _alpha_from_matte(fr, mode):
    """uint8 alpha (255 = person). black: person on black (remove_background), alpha = (max(RGB)-8)/10;
    mask: white-on-black mask video, alpha = (v-64)/128."""
    if mode == "mask":
        a = fr.astype(np.float32) if fr.ndim == 2 else fr.max(axis=2).astype(np.float32)
        return np.clip((a - 64.0) * (255.0 / 128.0) + 0.5, 0, 255).astype(np.uint8)
    a = fr.astype(np.int16) if fr.ndim == 2 else fr.max(axis=2).astype(np.int16)
    return np.clip((a - 8) * 25.5 + 0.5, 0, 255).astype(np.uint8)


def _read_png_dir(d):
    fs = sorted(f for f in os.listdir(d) if f.lower().endswith((".png", ".jpg", ".jpeg")))
    if not fs:
        raise UsageError(f"{d}: no PNG/JPG files")
    return [os.path.join(d, f) for f in fs]


class SeqReader:
    """Frames lo..hi of a video for (mostly) non-decreasing indices in ONE sequential decode, cropped/scaled
    exactly like rrio.read_frames. The last `keep` decoded frames stay cached, so a short step back is free;
    a longer one restarts the decoder at that index (counted in .restarts). Memory: `keep` frames."""

    def __init__(self, path, info, lo, hi, crop=None, scale_w=None, scale_h=None, gray=False, keep=4):
        self.path, self.info = path, info
        self.lo, self.hi = int(lo), int(hi)
        self.kw = dict(crop=crop, scale_w=scale_w, scale_h=scale_h, gray=gray, info=info)
        self.keep = max(1, int(keep))
        self.cache = collections.OrderedDict()
        self.it = None
        self.pos = None
        self.restarts = 0

    def _open(self, start):
        self.close()
        self.it = rrio.read_frames(self.path, start=start, count=self.hi - start + 1, **self.kw)
        self.pos = start - 1

    def get(self, i):
        i = int(i)
        fr = self.cache.get(i)
        if fr is not None:
            return fr
        if i < self.lo or i > self.hi:
            raise IndexError(f"{self.path}: frame {i} outside the planned range {self.lo}..{self.hi}")
        if self.it is None or i <= self.pos:
            if self.it is not None:
                self.restarts += 1
            self._open(i)
        while self.pos < i:
            try:
                j, fr = next(self.it)
            except StopIteration:
                raise IndexError(f"{self.path}: frame {i} not decodable (stream ended at {self.pos})") from None
            self.pos = j
            if j >= i - self.keep:
                self.cache[j] = fr
                while len(self.cache) > self.keep:
                    self.cache.popitem(last=False)
        return self.cache[i]

    def close(self):
        if self.it is not None:
            self.it.close()  # kills the ffmpeg decoder
            self.it = None


class _Still:
    """SeqReader stand-in for a still image render (one frame for every index)."""

    def __init__(self, img):
        self.img = img
        self.restarts = 0

    def get(self, i):
        return self.img

    def close(self):
        pass


class _MatteStream:
    """Matte of a generated cut read in gen order: index(g) -> matte frame for gen frame g (proportional when
    the counts differ), alpha(i) -> uint8 alpha (255 = person) of matte frame i in the fit region at region
    size. Video mattes are decoded sequentially (SeqReader); PNG directories one file at a time."""

    def __init__(self, cr, full=False):
        self.cr = cr
        mp = wpath(cr.W, cr.e["matte"])
        self.mode = cr.e.get("matte_mode", "black")
        self.region = (0, 0, cr.gw, cr.gh) if full else cr.region
        self.rw, self.rh = (cr.gw, cr.gh) if full else (cr.rw, cr.rh)
        self.files, self.rd = None, None
        if os.path.isdir(mp):
            self.files = _read_png_dir(mp)
            self.mN = len(self.files)
            return
        if not os.path.isfile(mp):
            raise UsageError(f"{cr.id}: matte not found: {mp}")
        mpi = probe_counted(mp)
        self.mN = int(mpi["nb_frames"])
        region = self.region
        if (mpi["w"], mpi["h"]) != (cr.gw, cr.gh):
            # different size than the render: map the region proportionally
            fx, fy = mpi["w"] / cr.gw, mpi["h"] / cr.gh
            x, y, w, h = region
            region = (int(round(x * fx)), int(round(y * fy)), max(1, int(round(w * fx))), max(1, int(round(h * fy))))
            region = (min(region[0], mpi["w"] - region[2]), min(region[1], mpi["h"] - region[3]), region[2], region[3])
            cr.warn.append(f"matte {mpi['w']}x{mpi['h']} != render {cr.gw}x{cr.gh}: scaled")
        if self.mN != cr.gN:
            cr.warn.append(f"matte has {self.mN} frames, render {cr.gN}: mapped proportionally")
        crop = None if region == (0, 0, mpi["w"], mpi["h"]) else region
        self.rd = SeqReader(mp, mpi, self.index(min(cr.gs)), self.index(max(cr.gs)), crop, self.rw, self.rh)

    def index(self, g):
        return min(self.mN - 1, half_up(Fraction(int(g) * self.mN, self.cr.gN)))

    def raw(self, i):
        """Matte frame i (RGB) in the fit region at region size, as decoded (sequential for videos)."""
        if self.files is None:
            return self.rd.get(i)
        cr = self.cr
        fr = rrio.read_image(self.files[i])
        if fr.shape[:2] != (cr.gh, cr.gw):
            fr = rrio.resize(fr, cr.gw, cr.gh)
        x, y, w, h = self.region
        fr = fr[y:y + h, x:x + w]
        if fr.shape[:2] != (self.rh, self.rw):
            fr = rrio.resize(fr, self.rw, self.rh)
        return fr

    def alpha(self, i):
        return _alpha_from_matte(self.raw(i), self.mode)

    def close(self):
        if self.rd is not None:
            self.rd.close()


_END = object()


def _pipeline(items, load, work, pool, depth):
    """Ordered parallel map with bounded look-ahead: load(item) runs in the calling thread (the sequential
    decode), work(loaded, item) in the pool; at most `depth` items are in flight. Yields results in order."""
    it = iter(items)
    pend = collections.deque()
    try:
        while True:
            while len(pend) < depth:
                item = next(it, _END)
                if item is _END:
                    break
                pend.append(pool.submit(work, load(item), item))
            if not pend:
                return
            yield pend.popleft().result()
    finally:
        for fu in pend:
            fu.cancel()


class MatteWriter:
    """ffv1 gray writer, one frame per call; the file appears (atomic rename) only on close()."""

    def __init__(self, out_path, w, h, fps):
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        self.out, self.tmp = out_path, out_path + ".part.mkv"
        cmd = [rrio.FFMPEG, "-hide_banner", "-nostdin", "-loglevel", "error", "-y", "-f", "rawvideo",
               "-pix_fmt", "gray", "-s", f"{int(w)}x{int(h)}", "-framerate", rrio.fps_str(fps), "-i", "pipe:0",
               "-c:v", "ffv1", "-pix_fmt", "gray", self.tmp]
        self.errf = tempfile.TemporaryFile()
        self.p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=self.errf)
        self.n = 0

    def _err(self):
        self.errf.seek(0)
        return self.errf.read().decode("utf-8", "replace")[-600:]

    def write(self, m):
        try:
            self.p.stdin.write(np.ascontiguousarray(m, dtype=np.uint8).data)
        except BrokenPipeError:
            self.p.wait()
            raise RuntimeError(f"matte encode failed: {self._err()}") from None
        self.n += 1

    def close(self):
        try:
            self.p.stdin.close()
        except BrokenPipeError:
            pass
        rc = self.p.wait()
        msg = self._err()
        self.errf.close()
        if rc != 0:
            self.abort()
            raise RuntimeError(f"matte encode failed: {msg}")
        os.replace(self.tmp, self.out)
        return self.out

    def abort(self):
        try:
            if self.p.poll() is None:
                self.p.kill()
            self.p.wait()
        except Exception:
            pass
        try:
            self.errf.close()
        except Exception:
            pass
        try:
            os.unlink(self.tmp)
        except OSError:
            pass


class ByteQueue:
    """FIFO between the generated-cut producer and the compositing loop, capped by BYTES (not items). A put
    blocks while the item would take the queue past cap (an empty queue always takes one item); a set stop
    (threading.Event) unblocks it."""

    def __init__(self, cap):
        self.cap = int(cap)
        self.used = 0
        self.peak = 0
        self.error = None
        self.items = collections.deque()
        self.cv = threading.Condition()

    def put(self, item, nbytes=0, stop=None):
        with self.cv:
            while self.items and self.used + nbytes > self.cap and not (stop is not None and stop.is_set()):
                self.cv.wait(0.1)
            self.items.append((item, nbytes))
            self.used += nbytes
            self.peak = max(self.peak, self.used)
            self.cv.notify_all()

    def get(self):
        with self.cv:
            while not self.items:
                self.cv.wait(0.5)  # timed: stays responsive to Ctrl-C
            item, nb = self.items.popleft()
            self.used -= nb
            self.cv.notify_all()
            return item

    def clear(self):
        with self.cv:
            self.items.clear()
            self.used = 0
            self.cv.notify_all()


class CutRender:
    """One generated cut: mapping, fit (crop/scale/tilt/pan/zoom), grade, blur, matte -> window frames."""

    def __init__(self, W, tl, cut, entry, dry=False):
        self.W, self.tl, self.cut, self.e = W, tl, cut, dict(entry or {})
        self.id, self.n, self.f0 = cut["id"], cut["n"], cut["f0"]
        self.T = tl["fps"]
        self.ww, self.wh = tl["win"][2], tl["win"][3]
        self.warn = []
        self.dry = dry
        self.lut, self.grade, self.matte_out, self.load_secs = None, None, None, None
        e = self.e
        if dry:
            pv = e.get("pad_video")
            if not pv:
                raise UsageError(f"{self.id}: --dry needs 'pad_video' (the padded input clip) in renders.json")
            self.path = wpath(W, pv)
            for k in ("crop", "fit", "grade_match", "blur", "matte"):
                e.pop(k, None)
        else:
            if not e.get("path"):
                raise UsageError(f"{self.id}: renders.json entry has no 'path'")
            self.path = wpath(W, e["path"])
        if not os.path.isfile(self.path):
            raise UsageError(f"{self.id}: render not found: {self.path}")
        if e.get("matte") and not os.path.exists(wpath(W, e["matte"])):  # before the encoder starts
            raise UsageError(f"{self.id}: matte not found: {wpath(W, e['matte'])}")
        self.gp = probe_counted(self.path)
        self.gw, self.gh = self.gp["w"], self.gp["h"]
        self.gN = 1 if self.gp.get("is_image") else int(self.gp["nb_frames"])
        self.pad = None
        self.cut_meta = None     # frames.py export cuts/<id>.json (src_index, runs_in/out/dropped, fps_out)
        self.match_mse = None    # mean MSE of the content match (the export's own best rebuild of the cut)
        self.export_fps = None
        if e.get("pad_json"):
            pj = wpath(W, e["pad_json"])
            if not os.path.isfile(pj):
                raise UsageError(f"{self.id}: pad_json not found: {pj}")
            self.pad = rrio.load_json(pj)
        self._map()
        self._fit_rect()

    # ---- mapping
    def _export_index(self, pad, nsrc):
        """src_index of the cut export the padded clip was made from (frames.py export writes
        cuts/<cut>.json {cut, f0, f1, src_index: [absolute ref frame of every exported frame]})."""
        cands = []
        if self.e.get("cut_json"):
            cands.append((wpath(self.W, self.e["cut_json"]), True))
        if pad and pad.get("src"):
            cands.append((os.path.splitext(wpath(self.W, pad["src"]))[0] + ".json", False))
        for p, explicit in cands:
            if not os.path.isfile(p):
                if explicit:
                    raise UsageError(f"{self.id}: cut_json not found: {p}")
                continue
            try:
                cj = rrio.load_json(p)
            except (ValueError, OSError):
                continue
            si = cj.get("src_index") if isinstance(cj, dict) else None
            if not si:
                continue
            if cj.get("cut") not in (None, self.id):
                self.warn.append(f"{rel_to(self.W, p)} is for cut {cj.get('cut')}, not {self.id}: ignored")
                continue
            if nsrc and len(si) != int(nsrc):
                self.warn.append(f"{rel_to(self.W, p)} lists {len(si)} frames, the pad has {nsrc}: ignored")
                continue
            self.cut_meta = cj
            return [int(v) for v in si], rel_to(self.W, p)
        return None, None

    def _match(self, src_tl, S):
        x, y, w, h = self.tl["win"]
        a0 = min(self.f0, min(src_tl))
        a1 = max(self.cut["f1"], max(src_tl))
        L = [f for _, f in rrio.read_frames(self.tl["src"], start=a0, count=a1 - a0 + 1, crop=(x, y, w, h),
                                            scale_w=PSNR_W, gray=True, info=self.tl["info"])]
        ks, m = match_src_frames(L, a0, self.f0, self.n, src_tl, self.T, S)
        return ks, m

    def _map(self):
        e, pad, cut = self.e, self.pad, self.cut
        S = rrio.parse_fps(e.get("src_fps")) or (rrio.parse_fps(pad.get("src_fps") or pad.get("cut_fps") or pad.get("fps_in"))
                                                  if pad else None)
        S = S or cut["src_fps"]
        src_tl = e.get("src_timeline_frames") or (pad or {}).get("src_timeline_frames")
        tl_from = "renders/pad src_timeline_frames" if src_tl else None
        if self.gp.get("is_image"):
            self.ks, self.gs, self.how = [0] * self.n, [0] * self.n, "still image"
            return
        if pad is not None:
            keep = pad.get("keep_padded_index")
            nsrc = pad.get("src_frames") or pad.get("orig_frames") or (len(keep) if keep else None)
            if not src_tl:
                src_tl, tl_from = self._export_index(pad, nsrc)
            ks = ks_how = None
            if src_tl:
                ks, m = self._match(src_tl, S)
                ks_how = f"k=content match to {tl_from} (mean mse {m:.1f})"
                self.src_tl_from = tl_from
                self.match_mse = m
            self.export_fps = (rrio.parse_fps((self.cut_meta or {}).get("fps_out"))
                               or rrio.parse_fps(pad.get("fps_in") or pad.get("fps")) or S)
            if keep is None:
                if not nsrc:
                    raise UsageError(f"{self.id}: pad_json needs keep_padded_index or src_frames")
                keep = list(range(int(nsrc)))
            P = pad.get("padded_frames")
            if not P:
                raise UsageError(f"{self.id}: pad_json has no padded_frames")
            if self.dry:
                gN = int(self.gN)
                if gN != int(P):
                    self.warn.append(f"pad_video has {gN} frames, pad_json says padded_frames {P}")
            self.ks, self.gs, self.how = map_cut(self.n, self.T, S=S, src_frames=int(nsrc), keep=keep, padded=int(P),
                                                 gen_frames=self.gN, f0=self.f0, ks=ks, ks_how=ks_how)
            if self.gN != int(P):
                self.how += f" (render {self.gN} f vs padded {P} f)"
        else:
            gf = rrio.parse_fps(e.get("gen_fps")) or self.gp.get("fps") or self.T
            if src_tl:
                self.warn.append("src_timeline_frames ignored without pad_json (time mapping used)")
            self.ks, self.gs, self.how = map_cut(self.n, self.T, f0=self.f0,
                                                 gen_start=int(e.get("gen_start", 0)), gen_range=e.get("gen_range"),
                                                 gen_fps=gf, gen_frames=self.gN)
        if "CLAMPED" in self.how:
            self.warn.append("mapping ran past the end of the render (frames held): " + self.how)

    # ---- fit
    def _fit_rect(self):
        e, fit = self.e, dict(self.e.get("fit") or {})
        gw, gh, W_, H_ = self.gw, self.gh, self.ww, self.wh
        self.tilt = float(fit.get("tilt", e.get("tilt", 0)) or 0)
        self.pan = float(fit.get("pan", 0) or 0)
        self.zoom = float(fit.get("zoom", 1) or 1)
        self.ease = bool(fit.get("ease", False))
        how = "stretch whole frame"
        if e.get("crop"):
            x, y, cw, ch = [float(v) for v in e["crop"]]
            how = "crop"
        elif fit.get("scale") and fit.get("offset") is not None:
            s = float(fit["scale"])
            x, y = [float(v) for v in fit["offset"]]
            cw, ch = W_ / s, H_ / s
            how = "fit scale/offset"
        elif fit.get("person_box"):
            gb = fit.get("gen_box")
            if not gb and e.get("matte"):
                gb = self._matte_bbox()
            if not gb:
                raise UsageError(f"{self.id}: fit.person_box needs fit.gen_box or a 'matte' to find the gen person")
            rx0, ry0, rx1, ry1 = [float(v) for v in fit["person_box"]]
            gx0, gy0, gx1, gy1 = [float(v) for v in gb]
            cut_bottom = ry1 >= H_ - 6 or gy1 >= gh - 6
            s = (rx1 - rx0) / max(1.0, gx1 - gx0) if cut_bottom else (ry1 - ry0) / max(1.0, gy1 - gy0)
            cw, ch = W_ / s, H_ / s
            x = (gx0 + gx1) / 2 - ((rx0 + rx1) / 2) / s
            y = gy0 - ry0 / s
            how = f"auto fit (person {'width' if cut_bottom else 'height'}, gen box {[int(v) for v in gb]})"
            self.gen_box = [int(v) for v in gb]
        else:
            x, y, cw, ch = 0.0, 0.0, float(gw), float(gh)
        if cw > gw + 0.5 or ch > gh + 0.5:
            f = min(gw / cw, gh / ch)
            cx, cy = x + cw / 2, y + ch / 2
            cw, ch = cw * f, ch * f
            x, y = cx - cw / 2, cy - ch / 2
            self.warn.append(f"crop larger than the render: shrunk by {f:.3f} (cannot zoom out past the render)")
        a_crop, a_win = cw / ch, W_ / H_
        if abs(a_crop / a_win - 1) > 0.02 and how != "stretch whole frame":
            self.warn.append(f"crop aspect {a_crop:.3f} != window aspect {a_win:.3f}: stretched")
        self.crop = (x, y, cw, ch)
        self.fit_how = how
        # per timeline frame crop rects (gen px, float), kept inside the render
        rects = []
        for r in range(self.n):
            t = r / max(1, self.n - 1)
            te = _ease(t) if self.ease else t
            z = 1 + (self.zoom - 1) * te
            z = max(z, cw / gw, ch / gh)  # a pull-out (zoom < 1) cannot show more than the render has
            w_, h_ = cw / z, ch / z
            cx = x + cw / 2 + self.pan * te
            cy = y + ch / 2 - self.tilt * te
            x0 = min(max(cx - w_ / 2, 0.0), gw - w_)
            y0 = min(max(cy - h_ / 2, 0.0), gh - h_)
            rects.append((x0, y0, w_, h_))
        self.rects = rects
        rx0 = math.floor(min(r[0] for r in rects))
        ry0 = math.floor(min(r[1] for r in rects))
        rx1 = math.ceil(max(r[0] + r[2] for r in rects))
        ry1 = math.ceil(max(r[1] + r[3] for r in rects))
        rx0, ry0 = max(0, rx0), max(0, ry0)
        rx1, ry1 = min(gw, max(rx1, rx0 + 1)), min(gh, max(ry1, ry0 + 1))
        self.region = (rx0, ry0, rx1 - rx0, ry1 - ry0)
        self.sx, self.sy = W_ / cw, H_ / ch          # window px per gen px (at zoom 1)
        self.rw = max(W_, int(round(self.region[2] * self.sx)))
        self.rh = max(H_, int(round(self.region[3] * self.sy)))
        self.static = self.tilt == 0 and self.pan == 0 and self.zoom == 1

    def _matte_bbox(self):
        mid = self.gs[len(self.gs) // 2]
        fr = self._matte_frames([mid], full=True)[mid]
        bb = _bbox(fr, 127)
        if bb is None:
            self.warn.append("matte has no person at the middle frame (auto fit impossible)")
        return bb

    # ---- loading
    def _decode(self, path, info, idx, region, rw, rh):
        rx, ry, rwid, rhei = region
        crop = None if (rx, ry, rwid, rhei) == (0, 0, info["w"], info["h"]) else (rx, ry, rwid, rhei)
        if info.get("is_image"):
            img = rrio.read_image(path)
            if crop:
                img = img[ry:ry + rhei, rx:rx + rwid]
            img = rrio.resize(img, rw, rh) if img.shape[:2] != (rh, rw) else img
            return {i: img for i in idx}
        idx = sorted(set(int(i) for i in idx))
        frs = rrio.read_frames_at(path, idx, crop=crop, scale_w=rw, scale_h=rh, info=info)
        return dict(zip(idx, frs))

    def _matte_frames(self, gidx, full=False):
        """Alpha (uint8, 255 = person) per gen index, in the fit region (or the full render frame). For a few
        frames only (the auto fit); the render loop streams the matte through _MatteStream."""
        ms = _MatteStream(self, full=full)
        try:
            out = {}
            for g in sorted(set(int(v) for v in gidx)):
                if ms.files is None:
                    i = ms.index(g)
                    fr = rrio.read_frames_at(ms.rd.path, [i], crop=ms.rd.kw["crop"], scale_w=ms.rw, scale_h=ms.rh,
                                             info=ms.rd.info)[0]
                    out[g] = _alpha_from_matte(fr, ms.mode)
                else:
                    out[g] = ms.alpha(ms.index(g))
            return out
        finally:
            ms.close()

    def _grade_lut(self, frames):
        """Per-channel LUT pulling mean/std of the generated frames (iterable, region size; every 4th px)
        grade_match of the way to the reference cut. Both sides are streamed."""
        k = float(self.e.get("grade_match", 0) or 0)
        if k <= 0:
            return None, None
        x, y, w, h = self.tl["win"]
        ref = (f for _, f in rrio.read_frames(self.tl["src"], start=self.f0, count=self.n, crop=(x, y, w, h),
                                              scale_w=max(64, w // 4), info=self.tl["info"]))

        def stats(imgs):
            n, s1, s2 = 0, np.zeros(3), np.zeros(3)
            for im in imgs:
                v = im.reshape(-1, 3).astype(np.float64)
                n += len(v)
                s1 += v.sum(0)
                s2 += (v * v).sum(0)
            m = s1 / max(1, n)
            return m, np.sqrt(np.maximum(s2 / max(1, n) - m * m, 0))
        ms, ss = stats(ref)
        mg, sg = stats(f[::4, ::4] for f in frames)
        sg = sg + 1e-3
        a = 1 - k + k * ss / sg
        b = k * (ms - mg * ss / sg)
        v = np.arange(256, dtype=np.float64)[:, None]
        lut = np.clip(np.rint(v * a[None, :] + b[None, :]), 0, 255).astype(np.uint8)  # 256 x 3
        return lut, {"k": k, "ref_mean": ms.round(1).tolist(), "ref_std": ss.round(1).tolist(),
                     "gen_mean": mg.round(1).tolist(), "gen_std": sg.round(1).tolist()}

    def _slice(self, reg, r):
        """Window-size view of region frame `reg` for timeline frame r."""
        x0, y0, w_, h_ = self.rects[r]
        rx, ry = self.region[0], self.region[1]
        if self.zoom == 1:
            ox = int(round((x0 - rx) * self.sx))
            oy = int(round((y0 - ry) * self.sy))
            ox = min(max(ox, 0), reg.shape[1] - self.ww)
            oy = min(max(oy, 0), reg.shape[0] - self.wh)
            return reg[oy:oy + self.wh, ox:ox + self.ww]
        ox, oy = (x0 - rx) * self.sx, (y0 - ry) * self.sy
        sw, sh = w_ * self.sx, h_ * self.sy
        a0, b0 = int(math.floor(ox)), int(math.floor(oy))
        a1, b1 = int(math.ceil(ox + sw)), int(math.ceil(oy + sh))
        a0, b0 = max(0, a0), max(0, b0)
        a1, b1 = min(reg.shape[1], max(a1, a0 + 2)), min(reg.shape[0], max(b1, b0 + 2))
        return rrio.resize(reg[b0:b1, a0:a1], self.ww, self.wh, "bilinear")

    # ---- streaming (one sequential decode of the render and of the matte; nothing per cut is stacked)
    def _gen_reader(self):
        if self.gp.get("is_image"):
            return _Still(self._decode(self.path, self.gp, [0], self.region, self.rw, self.rh)[0])
        crop = None if self.region == (0, 0, self.gw, self.gh) else self.region
        return SeqReader(self.path, self.gp, min(self.gs), max(self.gs), crop, self.rw, self.rh)

    def prepare(self):
        """Grade LUT (grade_match only): one sequential pre-pass over the unique generated frames."""
        if float(self.e.get("grade_match", 0) or 0) <= 0:
            return self
        rd = self._gen_reader()
        try:
            self.lut, self.grade = self._grade_lut(rd.get(g) for g in sorted(set(self.gs)))
        finally:
            rd.close()
        return self

    def frames(self, stop=None):
        """Yield (rel, window frame uint8 h x w x 3, fitted matte uint8 h x w or None) for rel = 0..n-1.

        self.gs is non-decreasing for every mapping assemble builds (a content match can step back a frame:
        SeqReader keeps the last few), so the render and the matte are each decoded ONCE, in order. The
        per-frame work (grade LUT, fit slice, blur boxes; matte alpha, close, soften, slice) runs in a small
        thread pool a few frames ahead (FRAME_WORKERS), so memory holds only those frames, never the cut.
        Call prepare() first (grade LUT). Arrays are shared across held frames: read-only for the consumer."""
        blurs = [tuple(int(v) for v in b) for b in (self.e.get("blur") or [])]
        sig = float(self.e.get("blur_sigma", 12))
        lut = self.lut
        mode = self.e.get("matte_mode", "black")

        def gen_work(reg, item):
            if lut is not None:
                reg = np.stack([lut[reg[..., c], c] for c in range(3)], axis=-1)
            fr = self._slice(reg, item[0])
            if blurs:
                fr = fr.copy()
                for bx0, by0, bx1, by1 in blurs:
                    bx0, by0 = max(0, bx0), max(0, by0)
                    bx1, by1 = min(self.ww, bx1), min(self.wh, by1)
                    if bx1 > bx0 and by1 > by0:
                        fr[by0:by1, bx0:bx1] = rrio.gauss_blur(fr[by0:by1, bx0:bx1], sig)
            return np.ascontiguousarray(fr)

        def mat_work(raw, item):
            a8 = rrio.erode(rrio.dilate(_alpha_from_matte(raw, mode), 5), 5)  # close pinholes
            return np.ascontiguousarray(self._slice(rrio.gauss_blur(a8, 1.2), item[0]))

        gen = self._gen_reader()
        mat = gp = mp = None
        pool = ThreadPoolExecutor(max_workers=FRAME_WORKERS)
        try:
            mat = _MatteStream(self) if self.e.get("matte") else None
            gitems, mitems = [], []      # (rel, index) where a new output frame / matte starts
            lk = lm = _END
            for r, g in enumerate(self.gs):
                key = g if self.static else (g, r)
                if key != lk:
                    gitems.append((r, g))
                    lk = key
                if mat is not None:
                    i = mat.index(g)
                    mk = i if self.static else (i, r)
                    if mk != lm:
                        mitems.append((r, i))
                        lm = mk
            depth = FRAME_WORKERS + 2
            gp = _pipeline(gitems, lambda it: gen.get(it[1]), gen_work, pool, depth)
            if mat is not None:
                mp = _pipeline(mitems, lambda it: mat.raw(it[1]), mat_work, pool, depth)
            gi = mi = 0
            out = m = None
            for r in range(self.n):
                if stop is not None and stop.is_set():
                    return
                if gi < len(gitems) and gitems[gi][0] == r:
                    out = next(gp)
                    gi += 1
                if mp is not None and mi < len(mitems) and mitems[mi][0] == r:
                    m = next(mp)
                    mi += 1
                yield r, out, m
        finally:
            for it in (gp, mp):
                if it is not None:
                    it.close()
            pool.shutdown(wait=True, cancel_futures=True)
            gen.close()
            if mat is not None:
                mat.close()
            if gen.restarts:
                self.warn.append(f"mapping stepped back {gen.restarts}x past the decode cache (render re-decoded)")

    def warnings(self):
        seen, out = set(), []
        for w_ in self.warn:
            if w_ not in seen:
                seen.add(w_)
                out.append(w_)
        return out

    def summary(self):
        d = {"render": rel_to(self.W, self.path), "render_frames": self.gN, "render_size": [self.gw, self.gh],
             "render_fps": rrio.fps_str(self.gp["fps"]) if self.gp.get("fps") else None,
             "mapping": self.how, "src_index": [self.ks[0], self.ks[-1]], "gen_index": [self.gs[0], self.gs[-1]],
             "gen_unique": len(set(self.gs)), "fit": self.fit_how,
             "crop": [round(v, 1) for v in self.crop], "region": list(self.region),
             "tilt": self.tilt, "pan": self.pan, "zoom": self.zoom}
        if self.pad is not None:
            d["padded_frames"] = self.pad.get("padded_frames")
            d["src_frames"] = self.pad.get("src_frames") or self.pad.get("orig_frames") or len(self.pad.get("keep_padded_index") or [])
        if getattr(self, "grade", None):
            d["grade"] = self.grade
        if getattr(self, "gen_box", None):
            d["gen_box"] = self.gen_box
        return d


# --------------------------------------------------------------------------------------------------
# encoder / measurement
# --------------------------------------------------------------------------------------------------
_SETPARAMS = None


def bt709_tags():
    """',setparams=...bt709' for the end of the encoder's -vf: ffmpeg 8 ignores -color_primaries/-color_trc for
    filtered rawvideo frames (the file reads back 'unknown'), so the frames carry the tags themselves. ffmpeg
    5.1 has the same setparams options; a build without them gets '' (the output options apply there)."""
    global _SETPARAMS
    if _SETPARAMS is None:
        try:
            r = subprocess.run([rrio.FFMPEG, "-hide_banner", "-h", "filter=setparams"], capture_output=True,
                               text=True)
            txt = r.stdout or ""
        except FileNotFoundError:
            txt = ""
        _SETPARAMS = (",setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709"
                      if all(k in txt for k in ("color_primaries", "color_trc", "colorspace")) else "")
    return _SETPARAMS


def open_encoder(out, w, h, fps, audio_src=None, crf=14, preset="medium", audio_info=None, threads=None):
    """libx264 pipe (rgb24 in, yuv420p bt709 out). Audio stream-copied from audio_src when the codec fits mp4."""
    cmd = [rrio.FFMPEG, "-hide_banner", "-nostdin", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{w}x{h}", "-framerate", rrio.fps_str(fps), "-i", "pipe:0"]
    audio = "none"
    amap = []
    if audio_src:
        ai = audio_info or rrio.probe(audio_src)
        if ai.get("has_audio"):
            cmd += ["-i", audio_src]
            if (ai.get("audio_codec") or "") in COPY_AUDIO:
                amap = ["-map", "1:a:0", "-c:a", "copy"]
                audio = f"copy {ai.get('audio_codec')}"
            else:
                amap = ["-map", "1:a:0", "-c:a", "aac", "-b:a", "256k"]
                audio = f"aac 256k (source {ai.get('audio_codec')} cannot be copied into mp4)"
    cmd += ["-map", "0:v:0", *amap,
            "-vf", "scale=out_color_matrix=bt709:out_range=tv:flags=accurate_rnd+full_chroma_int" + bt709_tags(),
            "-c:v", "libx264", "-crf", str(crf), "-preset", preset, "-pix_fmt", "yuv420p",
            *(["-threads", str(int(threads))] if threads else []),
            "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv"]
    if out.lower().endswith((".mp4", ".mov", ".m4v")):
        cmd += ["-movflags", "+faststart"]
    os.makedirs(os.path.dirname(os.path.abspath(out)) or ".", exist_ok=True)
    tmp = os.path.join(os.path.dirname(os.path.abspath(out)), "." + os.path.basename(out) + ".part" +
                       os.path.splitext(out)[1])
    errf = tempfile.TemporaryFile()
    proc = subprocess.Popen(cmd + [tmp], stdin=subprocess.PIPE, stderr=errf)
    return proc, tmp, errf, audio


def close_encoder(proc, tmp, errf, out):
    try:
        proc.stdin.close()
    except BrokenPipeError:
        pass
    rc = proc.wait()
    errf.seek(0)
    msg = errf.read().decode("utf-8", "replace")[-1500:]
    errf.close()
    if rc != 0:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise RuntimeError(f"encode failed (rc={rc}): {msg}")
    os.replace(tmp, out)


def abort_encoder(proc, tmp, errf):
    try:
        proc.kill()
        proc.wait()
    except Exception:
        pass
    try:
        errf.close()
    except Exception:
        pass
    try:
        os.unlink(tmp)
    except OSError:
        pass


def produce_cuts(order, jobs, q, stop, W):
    """Producer thread: every generated cut in timeline order -> q items (cid, rel, window frame, matte|None),
    one sequential decode per cut (CutRender.frames); each cut's fitted matte is written to
    W/mattes/fit/<cut>.mkv on the way. Ends with None, or puts the exception for the consumer to raise.
    The grade pre-passes (CutRender.prepare, streaming, one frame in memory) run ahead in a helper thread."""
    ready = {cid: threading.Event() for cid in order}
    perr = {}

    def prep():
        for cid in order:
            try:
                if not stop.is_set():
                    jobs[cid].prepare()
            except BaseException as ex:  # re-raised by the producer when it reaches this cut
                perr[cid] = ex
            finally:
                ready[cid].set()

    threading.Thread(target=prep, daemon=True).start()
    try:
        for cid in order:
            job = jobs[cid]
            t0 = time.time()
            while not ready[cid].wait(0.1):
                if stop.is_set():
                    return
            if cid in perr:
                raise perr[cid]
            mw = None
            it = job.frames(stop)
            try:
                for rel, fr, m in it:
                    if m is not None:
                        if mw is None:
                            mw = MatteWriter(wpath(W, f"mattes/fit/{cid}.mkv"), job.ww, job.wh, job.T)
                        mw.write(m)
                    q.put((cid, rel, fr, m), fr.nbytes + (0 if m is None else m.nbytes), stop)
                    if stop.is_set():
                        return
                if mw is not None:
                    job.matte_out = mw.close()
                    mw = None
            finally:
                it.close()
                if mw is not None:
                    mw.abort()
            job.load_secs = round(time.time() - t0, 2)
        q.put(None, 0, stop)
    except BaseException as ex:  # surfaced in the main thread
        q.error = ex
        q.put(ex, 0, stop)


def frame_reader(path, info, ranges, maxsize=6):
    """Background decoder: yields (frame_index, frame) over the given [(start, count)] ranges."""
    q = queue.Queue(maxsize=maxsize)
    stop = threading.Event()

    def work():
        try:
            for s, n in ranges:
                for i, fr in rrio.read_frames(path, start=s, count=n, info=info):
                    if stop.is_set():
                        return
                    q.put((i, fr))
            q.put(None)
        except BaseException as ex:  # surface decode errors in the main thread
            q.put(ex)

    th = threading.Thread(target=work, daemon=True)
    th.start()
    try:
        while True:
            item = q.get()
            if item is None:
                return
            if isinstance(item, BaseException):
                raise item
            yield item
    finally:
        stop.set()
        while th.is_alive():
            try:
                q.get_nowait()
            except queue.Empty:
                th.join(0.05)


def lowres(path, win, info=None, sw=PSNR_W):
    """Window crop, sw px wide, gray uint8 [N,h,w] (whole video)."""
    frames = [f for _, f in rrio.read_frames(path, crop=win, scale_w=sw, gray=True, info=info)]
    if not frames:
        raise RuntimeError(f"{path}: no frames decoded")
    return np.stack(frames)


def _psnr_mse(m):
    return 100.0 if m <= 1e-9 else min(100.0, 10 * math.log10(255.0 ** 2 / m))


def _mse(a, b):
    d = a.astype(np.float32) - b.astype(np.float32)
    return float((d * d).mean())


def cut_psnr(A, B, idx_out, f0, n):
    """PSNR of output frames (A, indexed by position) vs reference frames B at offsets -1/0/+1."""
    res = {}
    for d in (-1, 0, 1):
        ms = []
        for r in range(n):
            o = idx_out.get(f0 + r)
            fr = f0 + r + d
            if o is None or o >= len(A) or not (0 <= fr < len(B)):
                continue
            ms.append(_mse(A[o], B[fr]))
        res[d] = round(_psnr_mse(float(np.mean(ms))), 2) if ms else None
    vals = {d: v for d, v in res.items() if v is not None}
    best = 0
    if vals:
        top = max(vals.values())
        best = 0 if (0 in vals and vals[0] >= top - 0.05) else max(vals, key=vals.get)
    return res, best


def frame_diffs(L):
    """Mean absolute difference of every frame to the previous one (frame 0 = 99)."""
    d = np.zeros(len(L), np.float32)
    d[0] = 99.0
    for i in range(1, len(L)):
        d[i] = np.abs(L[i].astype(np.int16) - L[i - 1].astype(np.int16)).mean()
    return d


def unique_count(d, f0, n, thr=None):
    dd = d[f0 + 1:f0 + n]
    if len(dd) == 0:
        return 1
    if thr is None:
        thr = 0.5
    return int(1 + (dd > thr).sum())


_FPS_CANDS = [12, 15, 16, 18, 20, 24, 25, 30, 36, 40, 45, 48, 50]


def detect_cadence(d, f0, n, T):
    """Best hold pattern of a cut from its frame differences: which output frames carry a new source frame.

    Tries every source rate S < T (with phases) and keeps the pattern whose 'new' frames differ most from
    its 'held' frames. Informational: confirm on a sheet; analyze_ref.py owns the real cadence call."""
    T = Fraction(T)
    dd = d[f0:f0 + n].astype(np.float64).copy()
    if n < 6:
        return {"pattern": "short", "src_fps": rrio.fps_str(T), "ratio": None}
    dd[0] = np.nan
    cands = sorted({rrio.parse_fps(c) for c in _FPS_CANDS if c < float(T)} |
                   ({Fraction(24000, 1001)} if T.denominator == 1001 else set()))
    best = None
    for S in cands:
        per = float(T / S)
        for ph in np.arange(0, per, 0.5 if per < 3 else 1.0):
            new = np.array([math.floor((r + ph) * float(S / T)) != math.floor((r - 1 + ph) * float(S / T))
                            for r in range(n)])
            new[0] = True
            nn = new[1:]
            v = dd[1:]
            if nn.sum() < 2 or (~nn).sum() < 2:
                continue
            mn, mo = float(np.mean(v[nn])), float(np.mean(v[~nn]))
            ratio = (mn + 0.05) / (mo + 0.05)
            score = ratio * (1 + 0.02 * float(S))  # mild tie-break toward the higher rate
            if best is None or score > best[0]:
                best = (score, ratio, S, float(ph), new, mn, mo)
    med = float(np.nanmedian(dd[1:])) if n > 1 else 0.0
    if best is None or best[1] < 2.2:
        pat = "static" if med < 0.4 else "native"
        return {"pattern": pat, "src_fps": rrio.fps_str(T), "ratio": round(best[1], 2) if best else None,
                "median_diff": round(med, 2)}
    _, ratio, S, ph, new, mn, mo = best
    starts = [f0 + r for r in range(n) if new[r]]
    return {"pattern": f"{float(S):g}in{float(T):g}", "src_fps": rrio.fps_str(S), "ratio": round(ratio, 2),
            "phase": ph, "new_mean": round(mn, 2), "held_mean": round(mo, 2), "src_timeline_frames": starts}


def sim_map_psnr(L, f0, n, T, S=None, src_tl=None):
    """Mapped-control simulation on the reference itself (low-res), no encode:
    S: export with ffmpeg's fps=S filter (keeps the LAST frame of each slot, round(n*S/T) frames; verified on
       ffmpeg 8) and map back with k = round(rel*S/T) -> what a plain 24p export + proportional map gives;
    src_tl: export exactly these timeline frames and hold each until the next -> the cadence-exact export.
    Returns PSNR of that rebuild vs the reference (dB) or None when not applicable."""
    T = Fraction(T)
    if src_tl:
        tl = [int(t) - f0 for t in src_tl]
        pick = [tl[max(0, bisect.bisect_right(tl, r) - 1)] for r in range(n)]
    else:
        if S is None or Fraction(S) >= T:
            return None
        S = Fraction(S)
        nsrc = max(1, half_up(n * S / T))
        slots = [min(half_up(r * S / T), nsrc - 1) for r in range(n)]
        last = {}
        for r in range(n):
            k = half_up(r * S / T)
            if k < nsrc:
                last[k] = r
        pick = [last.get(k, n - 1) for k in slots]
    ms = [_mse(L[f0 + pick[r]], L[f0 + r]) for r in range(n)]
    return round(_psnr_mse(float(np.mean(ms))), 2)


FAST_PATTERNS = ("native", "mixed")


def analysis_cadences(W, tl):
    """{cut id: analyze_ref cadence dict} - from the timeline's own cuts, else from analysis/analysis.json
    cuts with the same frame range (the plan may rename cuts, never re-time them)."""
    out = {c["id"]: c["cadence"] for c in tl["cuts"] if isinstance(c.get("cadence"), dict)}
    ap = wpath(W, "analysis/analysis.json")
    if len(out) < len(tl["cuts"]) and tl["doc"] != ap and os.path.isfile(ap):
        try:
            acuts = _parse_cuts(rrio.load_json(ap).get("cuts") or [], 10 ** 9)
        except (ValueError, OSError, UsageError, AttributeError, TypeError):
            acuts = []
        byrange = {(c["f0"], c["f1"]): c["cadence"] for c in acuts if isinstance(c.get("cadence"), dict)}
        for c in tl["cuts"]:
            if c["id"] not in out and (c["f0"], c["f1"]) in byrange:
                out[c["id"]] = byrange[(c["f0"], c["f1"])]
    return out


def fast_content(cut, T, export_fps=None, cut_meta=None, nsrc=None, cadence=None):
    """Does the cut show more distinct images per second than its export can carry (so ANY export at that rate
    drops images and the dry gate cannot reach GATE_DB)? -> None or {dropped, export_fps, from, ...}.

    frames.py export's cuts/<id>.json is authoritative: runs_dropped > 0 = fast, an empty list = every image
    kept (not fast, whatever the analysis says). Without it: analyze_ref cadence native/mixed with
    unique/of x timeline fps above the export fps; dropped = unique - exported frames (nsrc, else the nominal
    round(n * export_fps / fps))."""
    T = Fraction(T)
    E = Fraction(export_fps) if export_fps else Fraction(24)
    if isinstance(cut_meta, dict) and isinstance(cut_meta.get("runs_dropped"), list):
        nd = len(cut_meta["runs_dropped"])
        if nd <= 0:
            return None
        return {"dropped": nd, "images": cut_meta.get("runs_in"), "kept": cut_meta.get("runs_out"),
                "export_fps": rrio.fps_str(E), "from": "frames.py export runs_dropped"}
    cad = cadence if isinstance(cadence, dict) else None
    if not cad or cad.get("pattern") not in FAST_PATTERNS:
        return None
    try:
        uniq, of = int(cad["unique"]), int(cad["of"])
    except (KeyError, TypeError, ValueError):
        return None
    if of <= 0:
        return None
    rate = float(T) * uniq / of
    if rate <= float(E) + 1e-6:
        return None
    n_exp = int(nsrc) if nsrc else max(1, half_up(int(cut["n"]) * E / T))
    nd = uniq - n_exp
    if nd <= 0:
        return None
    return {"dropped": nd, "images": uniq, "kept": n_exp, "export_fps": rrio.fps_str(E),
            "unique_per_s": round(rate, 2), "from": f"analysis cadence {cad.get('pattern')} {uniq}/{of}"}


def export_meta(W, c):
    """W/cuts/<id>.json of an earlier frames.py export of exactly this cut, else None."""
    p = wpath(W, f"cuts/{c['id']}.json")
    if not os.path.isfile(p):
        return None
    try:
        cj = rrio.load_json(p)
    except (ValueError, OSError):
        return None
    if not isinstance(cj, dict) or cj.get("cut") not in (None, c["id"]):
        return None
    if (cj.get("f0"), cj.get("f1")) != (c["f0"], c["f1"]):
        return None
    return cj


def gate_floor(gate_db, fast=None, match_db=None, fast_db=GATE_FAST_DB, margin=FAST_MARGIN_DB):
    """PSNR floor of one cut: gate_db; a fast-content cut gets max(fast_db, min(gate_db, match_db - margin))
    (fast_db alone when the export match is unknown)."""
    if not fast:
        return gate_db
    if match_db is None:
        return fast_db
    return round(max(fast_db, min(gate_db, match_db - margin)), 2)


def fps_label(f):
    s = rrio.fps_str(Fraction(f))
    return s[:-2] if s.endswith("/1") else f"{float(Fraction(f)):.3f}".rstrip("0").rstrip(".")


def fit_sheet(path, rows, labels):
    imgs, labs = [], []
    for (a, b), (la, lb) in zip(rows, labels):
        imgs += [a, b]
        labs += [la, lb]
    return rrio.tile_sheet(imgs, labs, cols=2, out_path=path, tile_w=640, max_bytes=300_000, max_w=1300)


def outline(img, m, color=(0, 255, 0)):
    if m is None:
        return img
    b = m > 127
    edge = b & ~rrio.erode(b, 3)
    edge = rrio.dilate(edge, 2)
    o = img.copy()
    o[edge] = color
    return o


# --------------------------------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Frame-exact rebuild of a reference with generated cuts mapped into its footage window "
                    "(--control = alignment gate on original pixels).",
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__.split("\n\n", 1)[1])
    ap.add_argument("W", help="workspace dir")
    ap.add_argument("--control", action="store_true", help="rebuild from original pixels + PSNR gate (exit 3 on fail)")
    ap.add_argument("--dry", action="store_true",
                    help="with --control: run renders.json cuts through the generated path using 'pad_video'")
    ap.add_argument("--edl", help="timeline JSON (default plan/edl.json, else analysis/analysis.json)")
    ap.add_argument("--renders", default=None, help="renders JSON (default plan/renders.json)")
    ap.add_argument("--src", help="override the reference video path")
    ap.add_argument("--out", help="output mp4 (default out/base.mp4, control: out/control.mp4)")
    ap.add_argument("--report", help="report JSON (default <out without .mp4>_report.json)")
    ap.add_argument("--only", help="comma list of cut ids: render only these (no audio), for quick review")
    ap.add_argument("--canvas", choices=["ref", "black"], default="ref",
                    help="outside the window: reference pixels (default) or black + mask multiply")
    ap.add_argument("--mask", help="window mask PNG (canvas or window size, white = footage)")
    ap.add_argument("--crf", type=float, default=14)
    ap.add_argument("--preset", default="medium")
    ap.add_argument("--threads", type=int, help="x264 threads (default auto)")
    ap.add_argument("--no-audio", action="store_true")
    ap.add_argument("--no-psnr", action="store_true", help="skip the PSNR/cadence measurement")
    ap.add_argument("--no-sheets", action="store_true", help="skip qa/fit_<cut>.jpg")
    ap.add_argument("--gate-db", type=float, default=GATE_DB)
    ap.add_argument("--gate-fast-db", type=float, default=GATE_FAST_DB,
                    help="--dry: lowest floor of a fast-content cut (content faster than the export fps; the floor "
                         f"is max(this, min(--gate-db, export match - {FAST_MARGIN_DB:g} dB)); default {GATE_FAST_DB:g})")
    a = ap.parse_args(argv)
    t_start = time.time()
    W = os.path.abspath(a.W)
    if not os.path.isdir(W):
        raise UsageError(f"workspace not found: {W}")
    tl = load_timeline(W, a.edl, a.src)
    for wmsg in tl["warnings"]:
        log("assemble: warning:", wmsg)
    T, CW, CH = tl["fps"], tl["cw"], tl["ch"]
    x, y, w, h = tl["win"]
    mask, mask_how = window_mask(W, tl, a.mask)
    comp = Composer(tl, mask, a.canvas)
    cuts = tl["cuts"]
    byid = {c["id"]: c for c in cuts}

    rpath = wpath(W, a.renders or "plan/renders.json")
    renders = {}
    if os.path.isfile(rpath):
        renders = rrio.load_json(rpath)
        if not isinstance(renders, dict):
            raise UsageError(f"{rpath}: expected an object {{cut_id: entry}}")
        renders = {k: v for k, v in renders.items() if not k.startswith("_")}
        bad = [k for k in renders if k not in byid]
        if bad:
            raise UsageError(f"renders.json lists unknown cuts: {bad}")
    elif a.renders:
        raise UsageError(f"renders file not found: {rpath}")
    if a.control and not a.dry:
        use = {}
    elif a.control and a.dry:
        if not renders:
            raise UsageError("--dry needs plan/renders.json entries with pad_video")
        use = renders
    else:
        use = renders
        if not use:
            log("assemble: note: no renders listed - output equals the control rebuild")
    only = None
    if a.only:
        only = [s.strip() for s in a.only.split(",") if s.strip()]
        bad = [s for s in only if s not in byid]
        if bad:
            raise UsageError(f"--only: unknown cuts {bad}")
    sel = [c for c in cuts if only is None or c["id"] in only]
    jobs = {cid: CutRender(W, tl, byid[cid], e, dry=a.control and a.dry) for cid, e in use.items()
            if only is None or cid in only}

    out = wpath(W, a.out or ("out/control.mp4" if a.control else "out/base.mp4"))
    report = wpath(W, a.report) if a.report else os.path.splitext(out)[0] + "_report.json"
    # ---- frames to emit
    if only is None:
        ranges = [(0, None)]
    else:
        ranges = [(c["f0"], c["n"]) for c in sel]
    frame_cut = {}
    for c in cuts:
        for f in range(c["f0"], c["f1"] + 1):
            frame_cut[f] = c["id"]

    log(f"assemble: {rel_to(W, tl['src'])} {CW}x{CH} @{rrio.fps_str(T)} {tl['frames']} f, window {tl['win']} "
        f"[{tl['window_from']}], mask {mask_how}, canvas={a.canvas}, cuts {len(cuts)}, generated {len(jobs)}"
        f"{' (DRY: padded inputs)' if a.dry else ''}")
    order = [c["id"] for c in sel if c["id"] in jobs]
    # generated cuts are rendered by ONE producer thread in timeline order into a byte-capped queue: it runs
    # ahead of the compositing loop (prefetch into the next cut) but never holds more than PREFETCH_BYTES
    q = ByteQueue(PREFETCH_BYTES)
    stop = threading.Event()
    prod = threading.Thread(target=produce_cuts, args=(order, jobs, q, stop, W), daemon=True)
    proc, tmp, errf, audio = open_encoder(out, CW, CH, T, None if (a.no_audio or only) else tl["src"],
                                          a.crf, a.preset, tl["info"], a.threads)
    prod.start()
    emitted = []           # reference frame index of every output frame, in order
    sheets_rows = {}
    want_gen = sum(len(jobs[c].gs) for c in order)
    got_gen = 0
    t0 = time.time()
    try:
        for f, fr in frame_reader(tl["src"], tl["info"], [(s, n) for s, n in ranges]):
            cid = frame_cut.get(f)
            if cid in jobs:
                cr = jobs[cid]
                rel = f - cr.f0
                item = q.get()
                got_gen += 1
                if isinstance(item, BaseException):
                    raise item
                if item is None or item[0] != cid or item[1] != rel:
                    got = "end of stream" if item is None else f"{item[0]} rel {item[1]}"
                    raise RuntimeError(f"internal: generated frames out of step at F{f} ({cid} rel {rel}, got {got})")
                _, _, new, m = item
                sheet = not a.no_sheets and rel in {0, cr.n // 2, cr.n - 1}
                if sheet:
                    ref_win = fr[y:y + h, x:x + w].copy()
                comp.put(fr, new)
                if sheet:
                    ours = fr[y:y + h, x:x + w].copy()
                    sheets_rows.setdefault(cid, []).append(
                        ((ref_win, outline(ours, m)), (f"REF F{f}", f"OURS F{f} G{cr.gs[rel]}")))
                del item, new, m
            elif a.canvas == "black":
                comp.put(fr, fr[y:y + h, x:x + w].copy())
            try:
                proc.stdin.write(fr)
            except BrokenPipeError:
                break
            emitted.append(f)
            if len(emitted) % 240 == 0:
                el = time.time() - t0
                log(f"  {len(emitted)} frames  {len(emitted) / max(el, 1e-6):.1f} fps")
    except BaseException:
        abort_encoder(proc, tmp, errf)
        raise
    finally:
        if got_gen < want_gen:  # stopped early (error, short reference): unblock and stop the producer
            stop.set()
            q.clear()
        prod.join(timeout=300)  # complete run: lets it close the last fitted matte
        q.clear()
    if prod.is_alive() or q.error is not None:
        abort_encoder(proc, tmp, errf)
        if q.error is not None:
            raise q.error
        raise RuntimeError("the generated-cut producer did not finish")
    close_encoder(proc, tmp, errf, out)
    if not a.control:  # a fitted matte left from an earlier run must not leak into the text pass
        for cid, job in jobs.items():
            stale = wpath(W, f"mattes/fit/{cid}.mkv")
            if not job.e.get("matte") and os.path.isfile(stale):
                os.unlink(stale)
                log(f"assemble: removed stale {rel_to(W, stale)} ({cid} has no matte now)")
    enc_secs = time.time() - t0
    if only is None and tl["frames"] and len(emitted) != tl["frames"]:
        log(f"assemble: warning: decoded {len(emitted)} reference frames, plan says {tl['frames']}")
    log(f"assemble: wrote {rel_to(W, out)}: {len(emitted)} frames in {enc_secs:.1f} s, audio {audio}")

    # ---- QA sheets
    sheets = {}
    if not a.no_sheets:
        for cid, rows in sheets_rows.items():
            p = wpath(W, f"qa/fit_{cid}{'_dry' if a.dry else ''}.jpg")
            fit_sheet(p, [r[0] for r in rows], [r[1] for r in rows])
            sheets[cid] = rel_to(W, p)

    # ---- measurement
    rep_cuts = []
    gate_fail = []
    cad = {}
    if not a.no_psnr:
        t1 = time.time()
        res = {}

        def la():
            res["A"] = lowres(out, (x, y, w, h))

        def lb():
            res["B"] = lowres(tl["src"], (x, y, w, h), tl["info"])

        th1, th2 = threading.Thread(target=la), threading.Thread(target=lb)
        th1.start(), th2.start()
        th1.join(), th2.join()
        A, B = res["A"], res["B"]
        if len(A) != len(emitted):
            log(f"assemble: warning: the encoded file decodes to {len(A)} frames, {len(emitted)} were written")
        idx_out = {f: i for i, f in enumerate(emitted)}
        dB, dA = frame_diffs(B), frame_diffs(A)
        meas_secs = time.time() - t1
    leak = None
    cads = {}
    if a.control and not a.no_psnr:
        leak = edge_leak(tl["src"], tl["info"], tl["win"], CW, CH)
        cads = analysis_cadences(W, tl)
    fast_floor = {}
    for c in sel:
        cid = c["id"]
        d = {"id": cid, "f0": c["f0"], "f1": c["f1"], "n": c["n"], "src_fps": rrio.fps_str(c["src_fps"]),
             "src_fps_from": c["src_fps_from"], "source": "gen" if cid in jobs else "ref"}
        if cid in jobs:
            d.update(jobs[cid].summary())
            if jobs[cid].warn:
                d["warnings"] = jobs[cid].warnings()
            if jobs[cid].matte_out:
                d["matte_fit"] = rel_to(W, jobs[cid].matte_out)
            if cid in sheets:
                d["sheet"] = sheets[cid]
        if not a.no_psnr:
            ps, best = cut_psnr(A, B, idx_out, c["f0"], c["n"])
            d["psnr"] = {"-1": ps[-1], "0": ps[0], "+1": ps[1]}
            d["best_offset"] = best
            d["unique_ref"] = unique_count(dB, c["f0"], c["n"])
            outpos = [idx_out[f] for f in range(c["f0"], c["f1"] + 1) if f in idx_out]
            if outpos:
                dd = dA[outpos[1:]] if len(outpos) > 1 else np.zeros(0)
                d["unique_out"] = int(1 + (dd > 0.5).sum())
            floor = a.gate_db
            if a.control:
                job = jobs.get(cid)
                if job is not None:  # --dry: this cut went through its export
                    fast = fast_content(c, T, job.export_fps or job.gp.get("fps"), job.cut_meta,
                                        nsrc=d.get("src_frames"), cadence=cads.get(cid))
                else:                # plain control: what a 24p export of the cut will not carry
                    fast = fast_content(c, T, 24, export_meta(W, c), cadence=cads.get(cid))
                if fast:
                    if job is not None:
                        mdb = round(_psnr_mse(job.match_mse), 2) if job.match_mse is not None else None
                        floor = gate_floor(a.gate_db, fast, mdb, a.gate_fast_db)
                        fast.update(export_match_db=mdb, floor_db=floor)
                        fast_floor[cid] = floor
                    d["fast_content"] = fast
            ok = best == 0 and (ps[0] or 0) >= floor
            if a.control:
                d["ok"] = ok
                if not ok:
                    gate_fail.append(cid)
                cd = detect_cadence(dB, c["f0"], c["n"], T)
                cd["sim_fps_filter_at_plan_fps"] = sim_map_psnr(B, c["f0"], c["n"], T, c["src_fps"])
                if cd.get("src_timeline_frames"):
                    Sd = rrio.parse_fps(cd["src_fps"])
                    cd["sim_fps_filter_at_detected"] = sim_map_psnr(B, c["f0"], c["n"], T, Sd)
                    cd["sim_exact_hold"] = sim_map_psnr(B, c["f0"], c["n"], T, src_tl=cd["src_timeline_frames"])
                cad[cid] = cd
                d["cadence_est"] = {k: v for k, v in cd.items() if k != "src_timeline_frames"}
            elif cid not in jobs:
                d["ok"] = ok
                if not ok:
                    gate_fail.append(cid)
        rep_cuts.append(d)
    doc = {"schema": "rr.assemble/1", "mode": ("control-dry" if a.dry else "control") if a.control else "final",
           "W": W, "out": rel_to(W, out), "ref": tl["src_rel"], "timeline": rel_to(W, tl["doc"]),
           "renders": rel_to(W, rpath) if use else None, "fps": rrio.fps_str(T), "frames_out": len(emitted),
           "frames_ref": tl["frames"], "canvas": [CW, CH], "window": list(tl["win"]), "window_from": tl["window_from"],
           "mask": mask_how, "canvas_mode": a.canvas, "audio": audio, "only": only, "crf": a.crf, "preset": a.preset,
           "secs_encode": round(enc_secs, 1), "warnings": tl["warnings"], "cuts": rep_cuts}
    if not a.no_psnr:
        doc["secs_measure"] = round(meas_secs, 1)
        doc["gate"] = {"db": a.gate_db, "pass": not gate_fail, "failed": gate_fail,
                       "scope": "all cuts" if a.control else "kept (reference) cuts only"}
        if a.control and a.dry:
            doc["gate"].update(fast_db=a.gate_fast_db, fast_margin_db=FAST_MARGIN_DB, fast_cuts=fast_floor)
    if leak is not None:
        doc["window_edge_leak_px"] = leak
    doc["secs_total"] = round(time.time() - t_start, 1)
    rrio.save_json(report, doc)
    if cad:
        cp = wpath(W, "qa/cadence.json")
        prev = rrio.load_json(cp, None) if (only and os.path.isfile(cp)) else None
        allc = dict(prev["cuts"]) if prev and prev.get("fps") == rrio.fps_str(T) else {}
        allc.update(cad)
        rrio.save_json(cp, {"schema": "rr.cadence/1", "fps": rrio.fps_str(T), "cuts": allc})

    # ---- summary
    for d in rep_cuts:
        line = f"{d['id']:>5} {d['source']:3} f{d['f0']}-{d['f1']} ({d['n']:3d})"
        if "psnr" in d:
            p = d["psnr"]
            fmt = lambda v: f"{v:5.1f}" if v is not None else "  n/a"
            if d["source"] == "gen" and not a.dry:
                line += f"  vs ref {fmt(p['0'])} dB (new content)"
            else:
                line += f"  psnr -1:{fmt(p['-1'])} 0:{fmt(p['0'])} +1:{fmt(p['+1'])} best {d['best_offset']:+d}"
            line += f"  uniq ref {d['unique_ref']:2d} ours {d.get('unique_out', 0):2d}"
            if "ok" in d and not d["ok"]:
                line += "  <-- FAIL"
        if d["source"] == "gen":
            line += f"  g {d['gen_index'][0]}..{d['gen_index'][1]} of {d['render_frames']} ({d['mapping']})"
        if "cadence_est" in d:
            ce = d["cadence_est"]
            line += f"  cadence~{ce['pattern']}"
            if ce.get("sim_fps_filter_at_plan_fps") is not None:
                line += f" sim fps-filter@plan {ce['sim_fps_filter_at_plan_fps']}"
            if ce.get("sim_exact_hold") is not None:
                line += f" sim fps-filter@est {ce['sim_fps_filter_at_detected']} exact-hold {ce['sim_exact_hold']}"
        log(line)
        fc = d.get("fast_content")
        if fc:
            msg = f"      fast-content cut: {fps_label(fc['export_fps'])}p export drops {fc['dropped']} images (expected)"
            if "floor_db" in fc:
                msg += (f"; gate: best +0 and >= {fc['floor_db']} dB (export match "
                        f"{fc['export_match_db'] if fc['export_match_db'] is not None else 'n/a'} dB)")
            else:
                msg += (f" [{fc['from']}]; the --dry gate takes it at best +0 and >= max({a.gate_fast_db:g}, "
                        f"export match - {FAST_MARGIN_DB:g}) dB")
            log(msg)
        for wmsg in d.get("warnings", []):
            log(f"      warning: {wmsg}")
    log(f"assemble: report {rel_to(W, report)}" + (f", cadence qa/cadence.json" if cad else "")
        + (f", sheets {', '.join(sheets.values())}" if sheets else ""))
    if leak and max(leak.values()) > 1:
        log(f"assemble: WARNING: the reference footage reaches past the window rect by {leak} px: with --canvas ref "
            f"generated cuts would keep a strip of the old footage there. Widen the window (plan/edl.json) to the lit "
            f"area or use --canvas black")
    elif leak is not None:
        log(f"assemble: window edges clean (lit px outside the rect: {leak})")
    if cad:
        hint = [cid for cid, cd in cad.items()
                if (cd.get("sim_fps_filter_at_detected") or 99) < a.gate_db <= (cd.get("sim_exact_hold") or 0)
                and not ((cid in jobs and jobs[cid].cut_meta) or export_meta(W, byid[cid]))]  # frames.py export done
        if hint:
            log(f"assemble: hint: a plain ffmpeg fps=24 export of {hint} maps back below {a.gate_db} dB: export the "
                f"Genjutsu inputs with `frames.py export W --cut ID --fps 24 --crop window` (one frame per source "
                f"image; it writes cuts/<ID>.json, which this script content-matches), then `frames.py pad`")
    log(f"assemble: total {doc['secs_total']} s")
    if not a.no_psnr:
        fast_txt = ""
        if fast_floor:
            lo, hi = min(fast_floor.values()), max(fast_floor.values())
            rng = f"{lo:g}" if lo == hi else f"{lo:g}-{hi:g}"
            fast_txt = f"; fast-content cut(s) {sorted(fast_floor)} >= their own floor ({rng} dB)"
        if gate_fail:
            log(f"assemble: GATE FAIL ({doc['gate']['scope']}): {gate_fail} (need best offset +0 and >= {a.gate_db} dB"
                f"{fast_txt})")
            if a.control:
                return 3
        else:
            log(f"assemble: gate pass ({doc['gate']['scope']}: best +0, >= {a.gate_db} dB{fast_txt})")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except UsageError as ex:
        print(f"assemble: error: {ex}", file=sys.stderr)
        sys.exit(2)
    except (RuntimeError, ValueError, IndexError, FileNotFoundError) as ex:
        print(f"assemble: error: {ex}", file=sys.stderr)
        sys.exit(1)
