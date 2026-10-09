#!/usr/bin/env python3
"""frames.py - frame-exact frame tools: key frames per cut, cut clips, Genjutsu padding, plate catalogs.

Subcommands (all frame selection is by decoded frame index, never -ss):
  keyframes W [--which mid|first|last|best|breakdown] [--cuts c01,c05] [--crop window|none|x,y,w,h]
      -> W/keyframes/<cut>.png (full resolution, inside the window/letterbox crop), keyframes.json,
         W/sheets/keyframes.jpg (labelled). 'best' = sharpest of 5 candidates (variance of the Laplacian).
  export W --cut c03[,c05|all] [--fps native|24|<n/d>] [--crop window|none|x,y,w,h] [--edges keep|auto]
      -> W/cuts/<cut>.mp4 (libx264 crf 12, no audio) + W/cuts/<cut>.json (src_index = source frame of every
         output frame). Re-timing (--fps 24 on a 25/30/50/60p reference) keeps one output frame per distinct
         source image where the rate allows (pulldown / irregular holds), the cut's first and last image
         (--edges keep, default), and up to --max-extra 2 extra frames on a cut under 4 s rather than lose an
         image. --phase <number> = the old fixed-phase sampling.
  pad IN OUT [--frames 96] [--fps 24] [--mode auto|pingpong|freeze] [--for replace|mt] [--retime]
      -> OUT (Genjutsu driving clip) + <OUT without ext>.json {orig_frames, padded_frames, keep_padded_index[],
         seq[], billed_seconds_replace, billed_seconds_mt, ...}. IN must already be at --fps (exit 2
         otherwise; --retime overrides). Under --frames (96 = 4.00 s @24): pingpong to exactly 96 frames.
         Longer: freeze-pad to whole seconds (--for replace: ceil, replace bills ceil; --for mt: no pad when
         the fraction is <= 0.1 s, MT bills round). Prints the billed seconds from the probed output.
         Driving clip recipe: export W --cut cNN --fps 24 --crop window, then pad cuts/cNN.mp4 OUT.
  catalog W --clip PATH [--fps 4] [--name A1] [--start S] [--end E]
      -> W/sheets/catalog_<name>[_pN].jpg (tiles labelled 'A1 3.25s f78', <= 500 KB each) + .json
  map --gen-frames N --padded P (--k K | --pad-json OUT.json)
      -> generated-take frame for padded-input frame k: min(N-1, floor(k*N/P + 0.5))
  plate-frames --clip PATH --out DIR [--w 1440]
      -> DIR/f_00000.jpg ... (0-based = source frame index) + DIR/frames.json, for the compositor

Cut list and window come from W/analysis/analysis.json (falls back to W/analysis/breakdown.json). Accepted
shapes: cuts = [{id, f0, f1 (inclusive)}] or [{id, start, end (exclusive)}] or [{frames:[f0,f1]}] or a list
of cut start frames; window = {x,y,w,h} under 'window', 'format_lock.window', 'crop', 'active_area' or
'picture', or 'letterbox' = {top,bottom,left,right}. The video is W/ref/ref.mp4 unless the JSON names one
('ref.path' / 'video' / 'path') or --video is given.
"""
from __future__ import annotations

import argparse
import math
import os
import sys
from collections import Counter
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402

import rrio  # noqa: E402

PROG = "frames.py"
GENJUTSU_MIN_S = 4          # Genjutsu driving clips must be >= 4.00 s


class UsageError(Exception):
    pass


# --------------------------------------------------------------------------------------------------
# analysis.json / breakdown.json loading (tolerant)
# --------------------------------------------------------------------------------------------------
def _num(v):
    try:
        f = float(v)
        return f if math.isfinite(f) else None
    except (TypeError, ValueError):
        return None


def _rect(v):
    """dict {x,y,w,h} / {box|rect:[x,y,w,h]} / [x,y,w,h] -> (x,y,w,h) ints or None."""
    if v is None or v is False:
        return None
    if isinstance(v, (list, tuple)) and len(v) == 4 and all(_num(a) is not None for a in v):
        x, y, w, h = (_num(a) for a in v)
    elif isinstance(v, dict):
        for k in ("box", "rect", "xywh"):
            if k in v:
                return _rect(v[k])
        keys = ("x", "y", "w", "h")
        if not all(_num(v.get(k)) is not None for k in keys):
            if all(_num(v.get(k)) is not None for k in ("x", "y", "width", "height")):
                x, y, w, h = (_num(v[k]) for k in ("x", "y", "width", "height"))
            else:
                return None
        else:
            x, y, w, h = (_num(v[k]) for k in keys)
    else:
        return None
    if w <= 0 or h <= 0:
        return None
    return int(round(x)), int(round(y)), int(round(w)), int(round(h))


def _letterbox_rect(lb, W, H):
    if not isinstance(lb, dict):
        return _rect(lb)
    r = _rect(lb)
    if r:
        return r
    t, b, l, rr = (int(round(_num(lb.get(k)) or 0)) for k in ("top", "bottom", "left", "right"))
    if t == b == l == rr == 0:
        return (0, 0, W, H) if any(k in lb for k in ("top", "bottom", "left", "right")) else None
    return l, t, W - l - rr, H - t - b


def find_window(js, W, H):
    """Picture area (x,y,w,h) from an analysis/breakdown dict, or None (full frame)."""
    if not isinstance(js, dict):
        return None
    cv = js.get("canvas") if isinstance(js.get("canvas"), dict) else {}  # analyze_ref.py (rr.analysis/1)
    if cv and cv.get("kind") == "full" and not cv.get("crop_used"):
        return None
    cands = [js.get("window"), (js.get("format_lock") or {}).get("window"),
             cv.get("window"), cv.get("crop") if cv.get("kind") in ("window", "letterbox")
             else None, js.get("crop"),
             js.get("active_area"), js.get("picture"), js.get("content_box")]
    for c in cands:
        r = _rect(c)
        if r:
            return r
    for lb in (cv.get("letterbox"), js.get("letterbox"), (js.get("format_lock") or {}).get("letterbox")):
        if lb:
            r = _letterbox_rect(lb, W, H)
            if r:
                return r
    return None


def _cut_bounds(c):
    """One cut item -> (f0, f1 inclusive) or None."""
    if isinstance(c, dict):
        if "f0" in c and "f1" in c:
            return int(c["f0"]), int(c["f1"])
        if "first" in c and "last" in c:
            return int(c["first"]), int(c["last"])
        if "frames" in c and isinstance(c["frames"], (list, tuple)) and len(c["frames"]) == 2:
            return int(c["frames"][0]), int(c["frames"][1])
        if "start_frame" in c and "end_frame" in c:      # ffmpeg trim semantics: end exclusive
            return int(c["start_frame"]), int(c["end_frame"]) - 1
        if "start" in c and "end" in c:                  # genjutsu-ref-edit EDL: end exclusive
            return int(c["start"]), int(c["end"]) - 1
    return None


def parse_cuts(js, nb_frames):
    """List of {'id','f0','f1'} (inclusive, sorted) from a JSON dict; [] when none."""
    items = None
    for k in ("cuts", "shots", "segments"):
        v = js.get(k) if isinstance(js, dict) else None
        if isinstance(v, list) and v:
            items = v
            break
    if not items:
        return []
    out = []
    if all(isinstance(c, (int, float)) for c in items) or all(
            isinstance(c, dict) and _cut_bounds(c) is None and ("f" in c or "frame" in c) for c in items):
        starts = sorted({int(c if isinstance(c, (int, float)) else c.get("f", c.get("frame"))) for c in items})
        if not starts or starts[0] != 0:
            starts = [0] + starts
        starts = [s for s in starts if 0 <= s < nb_frames]
        for k, s in enumerate(starts):
            e = (starts[k + 1] - 1) if k + 1 < len(starts) else nb_frames - 1
            out.append({"id": f"c{k + 1:02d}", "f0": s, "f1": e})
        return out
    for k, c in enumerate(items):
        b = _cut_bounds(c)
        if b is None:
            raise UsageError(f"cut #{k} has no recognisable frame range: {str(c)[:120]}")
        cid = str(c.get("id") or f"c{k + 1:02d}")
        out.append({"id": cid, "f0": b[0], "f1": b[1]})
    out.sort(key=lambda c: c["f0"])
    return out


def load_project(W, video=None):
    """-> dict(video, info, cuts, window, source) from W/analysis/{analysis,breakdown}.json."""
    W = os.path.abspath(W)
    if not os.path.isdir(W):
        raise UsageError(f"workspace not found: {W}")
    docs = []
    for name in ("analysis.json", "breakdown.json"):
        p = os.path.join(W, "analysis", name)
        if os.path.exists(p):
            try:
                docs.append((p, rrio.load_json(p)))
            except ValueError as e:
                raise UsageError(f"{p}: invalid JSON ({e})") from None
    vid = video
    if not vid:
        for _, js in docs:
            for cand in ((js.get("ref") or {}).get("path") if isinstance(js.get("ref"), dict) else None,
                         js.get("video"), js.get("path")):
                if isinstance(cand, str) and cand:
                    pth = cand if os.path.isabs(cand) else os.path.join(W, cand)
                    if os.path.exists(pth):
                        vid = pth
                        break
            if vid:
                break
    vid = vid or os.path.join(W, "ref", "ref.mp4")
    if not os.path.exists(vid):
        raise UsageError(f"reference video not found: {vid} (run fetch_ref.py first or pass --video)")
    info = rrio.probe(vid)
    n = info["nb_frames"]
    cuts, window, src = [], None, None
    # An explicit plan/breakdown window takes precedence over detector metadata.
    for name in ("plan/edl.json", "analysis/breakdown.json"):
        explicit_path = os.path.join(W, name)
        if not os.path.isfile(explicit_path):
            continue
        explicit = rrio.load_json(explicit_path)
        candidate = explicit.get("window", (explicit.get("format_lock") or {}).get("window"))
        if candidate is False:
            window = (0, 0, info["w"], info["h"])
            break
        if candidate is not None:
            window = _rect(candidate)
            if window is not None:
                break
        letterbox = explicit.get("letterbox", (explicit.get("format_lock") or {}).get("letterbox"))
        if letterbox is not None:
            window = _letterbox_rect(letterbox, info["w"], info["h"])
            if window is not None:
                break
    for p, js in docs:
        if not cuts:
            cuts = parse_cuts(js, n)
            src = p if cuts else src
        if window is None:
            window = find_window(js, info["w"], info["h"])
    for c in cuts:
        if c["f0"] < 0 or c["f1"] < c["f0"]:
            raise UsageError(f"cut {c['id']}: bad range f0={c['f0']} f1={c['f1']}")
        if c["f1"] >= n:
            print(f"{PROG}: warning: cut {c['id']} ends at f{c['f1']} but the video has {n} frames; clamped",
                  file=sys.stderr)
            c["f1"] = n - 1
    return {"W": W, "video": vid, "info": info, "cuts": cuts, "window": window, "source": src}


def resolve_crop(spec, proj_window, info):
    """'window' | 'none' | 'x,y,w,h' -> (x,y,w,h) or None, validated against the frame."""
    if spec in (None, "", "window"):
        c = proj_window
    elif spec == "none":
        c = None
    else:
        try:
            c = tuple(int(round(float(v))) for v in spec.split(","))
            assert len(c) == 4
        except (ValueError, AssertionError):
            raise UsageError(f"--crop must be window, none or x,y,w,h (got {spec!r})") from None
    if c is None:
        return None
    x, y, w, h = c
    if x < 0 or y < 0 or w <= 0 or h <= 0 or x + w > info["w"] or y + h > info["h"]:
        raise UsageError(f"crop {c} lies outside the {info['w']}x{info['h']} frame")
    if (x, y, w, h) == (0, 0, info["w"], info["h"]):
        return None
    return (x, y, w, h)


def select_cuts(cuts, spec):
    if not cuts:
        raise UsageError("no cut list: write analysis/analysis.json (cuts) or analysis/breakdown.json first")
    if not spec or spec == "all":
        return list(cuts)
    want = [s.strip() for s in spec.split(",") if s.strip()]
    byid = {c["id"]: c for c in cuts}
    miss = [w for w in want if w not in byid]
    if miss:
        raise UsageError(f"unknown cut id(s) {miss}; known: {', '.join(byid)}")
    return [byid[w] for w in want]


# --------------------------------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------------------------------
def laplacian_var(gray):
    g = gray.astype(np.float32)
    if g.shape[0] < 3 or g.shape[1] < 3:
        return 0.0
    lap = 4.0 * g[1:-1, 1:-1] - g[:-2, 1:-1] - g[2:, 1:-1] - g[1:-1, :-2] - g[1:-1, 2:]
    return float(lap.var())


def even_crop(crop, info):
    """yuv420p needs even sizes: shrink an odd crop (or frame) by 1 px on the right/bottom."""
    x, y, w, h = crop if crop else (0, 0, info["w"], info["h"])
    w2, h2 = w - (w % 2), h - (h % 2)
    fixed = (w2, h2) != (w, h)
    if crop is None and not fixed:
        return None, False
    return (x, y, w2, h2), fixed


def fps_index_map(n_in, fps_in, fps_out, phase=0.0):
    """Source index (0..n_in-1) for every output frame when re-timing n_in frames from fps_in to fps_out.

    Output frame k samples the source at its centre time: src = floor((k + 0.5) * fps_in/fps_out + phase).
    n_out = round(n_in * fps_out / fps_in) keeps the duration.
    """
    r = Fraction(fps_in) / Fraction(fps_out)
    n_out = max(1, int(math.floor(n_in / r + Fraction(1, 2))))
    out = []
    for k in range(n_out):
        s = int(math.floor(float((k + Fraction(1, 2)) * r) + phase + 1e-9))
        out.append(min(n_in - 1, max(0, s)))
    return out


def _mad_series(small):
    return np.abs(np.diff(small.astype(np.float32), axis=0)).mean(axis=(1, 2)) if len(small) > 1 else np.zeros(0)


def dup_pairs(small, idx):
    if len(idx) < 2:
        return 0
    thr = hold_threshold(_mad_series(small))
    return sum(1 for a, b in zip(idx, idx[1:])
               if a == b or float(np.abs(small[b].astype(np.float32) - small[a].astype(np.float32)).mean()) < thr)


def hold_threshold(mads):
    """Mean-abs-diff (96 px gray) below which two consecutive frames show the same image."""
    return max(0.15, 0.3 * float(np.percentile(mads, 75))) if len(mads) else 0.15


def hold_runs(small, thr=None):
    """Runs of consecutive frames that show one image (holds, pulldown repeats).
    -> (runs [(a, b) inclusive indices into small], thr, mads)."""
    n = len(small)
    mads = _mad_series(small)
    if thr is None:
        thr = hold_threshold(mads)
    runs, s = [], 0
    for i, v in enumerate(mads):
        if v >= thr:
            runs.append((s, i))
            s = i + 1
    runs.append((s, n - 1))
    return runs, thr, mads


TIME_WEIGHT = (20.0, 0.02)   # squared slot-time error weight = max(20, 0.02 x the cut's median new-image MSE)


def _run_dists(small, runs, smax):
    """dist[o][j] = MSE between the images of runs j and j+o (o = 1..smax), on <= 32 px wide gray thumbnails
    of each run's middle frame."""
    rep = np.stack([small[(a + b) // 2] for a, b in runs]).astype(np.float32)
    f = max(1, rep.shape[2] // 32)
    if f > 1:
        h, w = rep.shape[1] // f * f, rep.shape[2] // f * f
        rep = rep[:, :h, :w].reshape(len(rep), h // f, f, w // f, f).mean(axis=(2, 4))
    U = len(rep)
    return {o: (((rep[o:] - rep[:-o]) ** 2).mean(axis=(1, 2)) if o < U else np.zeros(0))
            for o in range(1, smax + 1)}


def _hold_medoid(small, a, b, t):
    """Frame of the hold a..b closest to all the others (encoders drift a little inside a hold); ties -> the
    one nearest to t."""
    fr = small[a:b + 1].astype(np.float32)
    cost = [round(float(((fr - fr[i]) ** 2).mean()), 3) for i in range(len(fr))]
    return a + min(range(len(fr)), key=lambda i: (cost[i], abs(a + i - t)))


def resample_runs(small, fps_in, fps_out, max_extra=0, cap=None, edges="keep", time_weight=TIME_WEIGHT):
    """Re-time a cut to fps_out keeping as many distinct source images as the output can hold.

    n_out = round(n_in * fps_out / fps_in) output frames (as fps_index_map). When the cut has a few more
    distinct images than that (n_out < images <= n_out + max_extra, e.g. 24p content whose cut points leave a
    1-frame run at each edge) and images <= cap, n_out grows to the image count so none is lost (callers set
    cap = the 96-frame Genjutsu minimum, so the padded clip and its billed seconds do not change).

    The cut is split into hold runs (one run = one distinct image: pulldown repeats, holds). A monotone dynamic
    programme gives every output slot one run:
      - edges='keep': the first slot shows the cut's first image and the last slot its last image (1-frame
        runs at the cut points survive); edges='auto': the edge images are scored like any other;
      - leaving runs out costs, for every source frame of a left-out run, its MSE to the nearer kept neighbour
        image: this is what assemble's content-matched mapping pays, so 24p content in a 25/30/50/60p
        container comes out one frame per image even with irregular holds (3,2,2,3,3,2), and content faster
        than fps_out keeps the images that cover the cut best;
      - each slot pays max(20, 0.02 x the cut's median new-image MSE) x (distance in slots from its centre to
        its run's time span)^2, so repeats land where the content holds and the motion stays near real time.
    A run shown once contributes its medoid frame; a run shown on several slots contributes the frame nearest
    to each slot's time (so a slow drift merged into one run still advances). -> (indices into small, info)."""
    n = len(small)
    r = Fraction(fps_in) / Fraction(fps_out)
    n_nom = max(1, int(math.floor(n / r + Fraction(1, 2))))
    runs, thr, mads = hold_runs(small)
    U = len(runs)
    n_out = n_nom
    if max_extra and n_nom < U <= n_nom + int(max_extra) and (cap is None or U <= cap):
        n_out = U
    q = n_out / float(n)                      # output slots per source frame (the cut fills exactly n_out slots)
    if n_out == 1 or U == 1:
        path = [U // 2] if n_out == 1 else [0] * n_out
    else:
        smax = min(U - 1, max(3, 2 * int(math.ceil((U - 1) / float(n_out - 1))) + 1))
        dist = _run_dists(small, runs, smax)
        dn = float(np.median(dist[1])) if len(dist[1]) else 0.0
        lo = np.array([a for a, _ in runs], np.float64) * q
        hi = np.array([b + 1 for _, b in runs], np.float64) * q
        c = np.arange(n_out, dtype=np.float64) + 0.5
        d = np.maximum(np.maximum(lo[None, :] - c[:, None], c[:, None] - hi[None, :]), 0.0)
        C = max(time_weight[0], time_weight[1] * dn) * d * d
        ln = np.array([b - a + 1 for a, b in runs], np.float64)
        G = {}                                # G[s][j]: cost of jumping from run j to run j+s (runs between lost)
        for st in range(1, smax + 1):
            g = np.zeros(U - st)
            for m in range(1, st):
                g += ln[m:U - st + m] * np.minimum(dist[m][:U - st], dist[st - m][m:U - st + m])
            G[st] = g
        INF = 1e18
        D = np.full(U, INF)
        D[0] = C[0, 0]                        # first slot = first image
        if edges == "auto":                   # ... or a later one, paying for the images before it
            for j0 in range(1, smax + 1):
                D[j0] = C[0, j0] + sum(ln[i] * dist[j0 - i][i] for i in range(j0))
        back = np.zeros((n_out, U), np.int32)
        ids = np.arange(U)
        for k in range(1, n_out):
            best, arg = D.copy(), ids.copy()  # repeat the same image
            for st in range(1, smax + 1):
                cand = D[:-st] + G[st]
                better = cand < best[st:]
                best[st:] = np.where(better, cand, best[st:])
                arg[st:] = np.where(better, ids[:-st], arg[st:])
            D = best + C[k]
            back[k] = arg
        j = U - 1                             # last slot = last image
        if edges == "auto":
            tails = {jl: D[jl] + sum(ln[i] * dist[i - jl][jl] for i in range(jl + 1, U))
                     for jl in range(max(0, U - 1 - smax), U)}
            j = min(tails, key=tails.get)
        path = [0] * n_out
        for k in range(n_out - 1, 0, -1):
            path[k] = j
            j = int(back[k][j])
        path[0] = j
    uses = Counter(path)
    idx = []
    for k, j in enumerate(path):
        a, b = runs[j]
        t = min(b, max(a, int(math.floor((k + 0.5) / q))))
        if uses[j] == 1 and 2 <= b - a + 1 <= 12:
            t = _hold_medoid(small, a, b, t)
        idx.append(t)
    used = set(path)
    dropped = [runs[j] for j in range(U) if j not in used]
    info = {"method": "hold-runs", "edges": edges, "hold_thr": round(float(thr), 3), "frames_nominal": n_nom,
            "extended_by": n_out - n_nom, "runs_in": U, "runs_out": len(used),
            "runs_dropped": [[a, b] for a, b in dropped],
            "first_last_kept": bool(path[0] == 0 and path[-1] == U - 1)}
    return idx, info


def _parse_fps_arg(v, native):
    if v in (None, "", "native"):
        return native
    f = rrio.parse_fps(v)
    if not f:
        raise UsageError(f"bad --fps {v!r} (native, 24, 30000/1001, ...)")
    return f


def _w(path):
    return os.path.relpath(path) if not os.path.isabs(path) else path


# --------------------------------------------------------------------------------------------------
# keyframes
# --------------------------------------------------------------------------------------------------
def cmd_keyframes(a):
    proj = load_project(a.W, a.video)
    info, vid = proj["info"], proj["video"]
    crop = resolve_crop(a.crop, proj["window"], info)
    cuts = select_cuts(proj["cuts"], a.cuts)
    fps = info["fps"]
    bd_key = {}
    if a.which == "breakdown":
        p = os.path.join(proj["W"], "analysis", "breakdown.json")
        bd = rrio.load_json(p, default={}) or {}
        for c in bd.get("cuts", []) or []:
            k = (c.get("route_suggestion") or {}).get("keyframe")
            if isinstance(k, (int, float)) and c.get("id"):
                bd_key[str(c["id"])] = int(k)
    overrides = {}
    for item in (a.frames or "").split(","):
        if item.strip():
            try:
                cid, f = item.split("=")
                overrides[cid.strip()] = int(f)
            except ValueError:
                raise UsageError(f"--frames wants c03=57,c05=120 (got {item!r})") from None
    out_dir = os.path.join(proj["W"], "keyframes")
    os.makedirs(out_dir, exist_ok=True)
    cw = crop[2] if crop else info["w"]
    an_w = min(cw, a.analysis_w)
    picks, records = {}, []
    for c in cuts:
        f0, f1 = c["f0"], c["f1"]
        n = f1 - f0 + 1
        cands = []
        if c["id"] in overrides:
            f = overrides[c["id"]]
            if not f0 <= f <= f1:
                raise UsageError(f"--frames {c['id']}={f} is outside the cut ({f0}-{f1})")
            mode = "manual"
        elif a.which == "first":
            f, mode = f0, "first"
        elif a.which == "last":
            f, mode = f1, "last"
        elif a.which == "breakdown" and c["id"] in bd_key and f0 <= bd_key[c["id"]] <= f1:
            f, mode = bd_key[c["id"]], "breakdown"
        elif a.which == "best":
            idx = sorted({f0 + int(round(fr * (n - 1))) for fr in (0.1, 0.3, 0.5, 0.7, 0.9)})
            grays = rrio.read_frames_at(vid, idx, scale_w=an_w, crop=crop, gray=True, info=info)
            cands = [{"f": i, "sharpness": round(laplacian_var(g), 2)} for i, g in zip(idx, grays)]
            f = max(cands, key=lambda d: (d["sharpness"], -abs(d["f"] - (f0 + f1) / 2)))["f"]
            mode = "best"
        else:
            f, mode = f0 + (n - 1) // 2, "mid"
        picks[c["id"]] = f
        records.append({"id": c["id"], "f0": f0, "f1": f1, "frame": f, "mode": mode,
                        "t": round(rrio.frame_time(f, fps), 4), "candidates": cands})
    order = sorted(set(picks.values()))
    frames = dict(zip(order, rrio.read_frames_at(vid, order, crop=crop, info=info)))
    tiles, labels = [], []
    for r in records:
        img = frames[r["frame"]]
        path = os.path.join(out_dir, f"{r['id']}.png")
        rrio.write_image(path, img)
        r["path"] = os.path.relpath(path, proj["W"])
        tiles.append(img)
        labels.append(f"{r['id']} f{r['frame']} {r['t']:.2f}s")
    meta = {"video": os.path.relpath(vid, proj["W"]) if vid.startswith(proj["W"]) else vid,
            "fps": rrio.fps_str(fps), "crop": list(crop) if crop else None, "which": a.which,
            "cut_source": proj["source"], "w": crop[2] if crop else info["w"],
            "h": crop[3] if crop else info["h"], "cuts": records}
    jpath = os.path.join(out_dir, "keyframes.json")
    rrio.save_json(jpath, meta)
    sheet = os.path.join(proj["W"], "sheets", "keyframes.jpg")
    cols = min(a.cols, len(tiles))
    res = rrio.tile_sheet(tiles, labels, cols=cols, out_path=sheet, tile_w=a.tile_w, max_bytes=a.max_bytes,
                          title=f"keyframes ({a.which}) {os.path.basename(vid)} "
                                f"{meta['w']}x{meta['h']}" + (f" crop {crop[0]},{crop[1]}" if crop else ""))
    for r in records:
        extra = ""
        if r["candidates"]:
            extra = "  sharpness " + " ".join(f"f{d['f']}:{d['sharpness']:.0f}" for d in r["candidates"])
        print(f"{r['id']}: f{r['frame']} ({r['mode']}, cut {r['f0']}-{r['f1']}) -> {r['path']}{extra}")
    print(f"wrote {len(records)} key frames {meta['w']}x{meta['h']}, {jpath}")
    print(f"sheet {sheet} ({res['bytes']} bytes)")
    return 0


# --------------------------------------------------------------------------------------------------
# export
# --------------------------------------------------------------------------------------------------
def export_cut(proj, c, fps_spec, crop_spec, phase_spec, crf, preset, out_path=None, max_extra=2, edges="keep"):
    info, vid = proj["info"], proj["video"]
    rrio.require_cfr(vid, info)
    crop0 = resolve_crop(crop_spec, proj["window"], info)
    crop, fixed = even_crop(crop0, info)
    fps_in = info["fps"]
    fps_out = _parse_fps_arg(fps_spec, fps_in)
    f0, f1 = c["f0"], c["f1"]
    n_in = f1 - f0 + 1
    small = None
    rinfo = {"method": "identity"}
    if fps_out == fps_in:
        idx, phase, dups = list(range(n_in)), 0.0, None
    else:
        small = np.stack([g for _, g in rrio.read_frames(vid, f0, n_in, scale_w=96, crop=crop, gray=True,
                                                         info=info)])
        if len(small) != n_in:
            raise RuntimeError(f"decoded {len(small)} of {n_in} frames for {c['id']}")
        if phase_spec in (None, "", "auto"):
            # extra frames only while the clip stays under the 4 s Genjutsu minimum (it is padded to 4 s anyway)
            cap = int(math.ceil(GENJUTSU_MIN_S * fps_out))
            idx, rinfo = resample_runs(small, fps_in, fps_out, max_extra=max_extra, cap=cap, edges=edges)
            phase = "runs"
            rinfo["runs_dropped"] = [[f0 + a, f0 + b] for a, b in rinfo["runs_dropped"]]
        else:
            try:
                phase = float(phase_spec)
            except ValueError:
                raise UsageError(f"--phase must be auto or a number (got {phase_spec!r})") from None
            idx = fps_index_map(n_in, fps_in, fps_out, phase)
            rinfo = {"method": "fixed-phase"}
        dups = dup_pairs(small, idx)
    cnt = Counter(idx)
    out_path = out_path or os.path.join(proj["W"], "cuts", f"{c['id']}.mp4")
    ow, oh = (crop[2], crop[3]) if crop else (info["w"], info["h"])
    written = 0
    with rrio.VideoWriter(out_path, ow, oh, fps_out, crf=crf, preset=preset) as vw:
        for i, fr in rrio.read_frames(vid, f0, n_in, crop=crop, info=info):
            for _ in range(cnt.get(i - f0, 0)):
                vw.write(fr)
                written += 1
    if written != len(idx):
        raise RuntimeError(f"{c['id']}: wrote {written} frames, expected {len(idx)} (short decode?)")
    meta = {"cut": c["id"], "f0": f0, "f1": f1, "src": vid, "crop": list(crop) if crop else None,
            "crop_even_fix": fixed, "w": ow, "h": oh, "fps_in": rrio.fps_str(fps_in),
            "fps_out": rrio.fps_str(fps_out), "frames_in": n_in, "frames_out": written,
            "duration_s": round(written / float(fps_out), 4), "phase": phase,
            "dup_pairs": dups, **rinfo, "src_index": [f0 + i for i in idx], "crf": crf,
            "note": ("src_index[k] = absolute reference frame shown in output frame k; runs_dropped = "
                     "absolute frame ranges of source images that are not in the export")}
    jpath = os.path.splitext(out_path)[0] + ".json"
    rrio.save_json(jpath, meta)
    return out_path, jpath, meta


def cmd_export(a):
    proj = load_project(a.W, a.video)
    cuts = select_cuts(proj["cuts"], a.cut)
    if a.out and len(cuts) > 1:
        raise UsageError("--out works with a single --cut")
    for c in cuts:
        path, jpath, m = export_cut(proj, c, a.fps, a.crop, a.phase, a.crf, a.preset, a.out, a.max_extra, a.edges)
        warn = ""
        if m.get("method") == "hold-runs":
            nd = len(m["runs_dropped"])
            warn = f"  images {m['runs_out']}/{m['runs_in']}"
            if m["extended_by"]:
                warn += f" (+{m['extended_by']} frame(s) over {m['frames_nominal']} to keep every image)"
            if nd:
                warn += (f" (dropped {nd}: motion faster than {m['fps_out']} fps; first+last kept: "
                         f"{m['first_last_kept']})")
            if m["dup_pairs"]:
                warn += f", {m['dup_pairs']} repeats (content holds longer than one output frame)"
        elif m["dup_pairs"]:
            warn = f"  WARNING {m['dup_pairs']} near-duplicate consecutive frames (pulldown? use --phase auto)"
        if m["crop_even_fix"]:
            warn += "  (odd crop trimmed by 1 px for yuv420p)"
        print(f"{c['id']}: f{m['f0']}-{m['f1']} ({m['frames_in']}f @{m['fps_in']}) -> {m['frames_out']}f "
              f"@{m['fps_out']} {m['w']}x{m['h']} {m['duration_s']:.3f}s phase {m['phase']} -> {path}{warn}")
        print(f"   map {jpath}")
    return 0


# --------------------------------------------------------------------------------------------------
# pad
# --------------------------------------------------------------------------------------------------
def pad_sequence(n, target, mode):
    """Indices into the n source frames for a padded clip of `target` frames (n >= target: identity)."""
    if n <= 0:
        raise UsageError("input clip has no frames")
    if n >= target:
        return list(range(n))
    if mode == "freeze":
        return list(range(n)) + [n - 1] * (target - n)
    cycle = list(range(n)) + list(range(n - 2, 0, -1)) if n > 2 else list(range(n))
    reps = math.ceil(target / len(cycle))
    return (cycle * reps)[:target]


def billed_seconds(frames, fps):
    """Genjutsu billing of a driving clip of `frames` frames at `fps`: replace bills ceil(seconds), motion
    transfer bills round(seconds) (half up). -> (seconds Fraction, replace_s, mt_s)."""
    secs = Fraction(int(frames)) / Fraction(fps)
    rep = int(math.ceil(secs))
    mt = int(math.floor(secs + Fraction(1, 2)))
    return secs, rep, mt


def pad_target(n, min_frames, fps, whole_seconds, job):
    """Output frame count for a clip of n frames: at least min_frames, then whole seconds per job type.
    replace: up to an exact whole second (replace bills ceil). mt: no pad when the fractional second is
    <= 0.1 s (MT bills round(): it drops <= 2 tail frames @24, fill them in code), else up to the next whole
    second. -> (target, why)."""
    base = max(int(n), int(min_frames))
    why = f"padded to the {int(min_frames)}-frame minimum" if n < min_frames else ""
    if not whole_seconds:
        return base, why or "as is (--no-whole-seconds)"
    secs = Fraction(base) / Fraction(fps)
    whole = int(math.floor(secs))
    frac = secs - whole
    if frac == 0:
        return base, why or "already whole seconds"
    if job == "mt" and frac <= Fraction(1, 10):
        return base, ((why + "; ") if why else "") + (f"MT: fractional {float(frac):.3f} s <= 0.1 s -> not "
                                                      f"padded further (fill the lost tail in code)")
    up = int(math.ceil(Fraction(whole + 1) * Fraction(fps) - Fraction(1, 10 ** 9)))
    return max(up, base), f"{'MT' if job == 'mt' else 'replace'}: padded to {whole + 1} whole seconds"


class FpsMismatch(Exception):
    pass


def cmd_pad(a):
    if not os.path.exists(a.IN):
        raise UsageError(f"input not found: {a.IN}")
    info = rrio.probe(a.IN, count=True)
    fps_out = rrio.parse_fps(a.fps)
    if not fps_out:
        raise UsageError(f"bad --fps {a.fps!r}")
    fps_in = info.get("fps")
    retimed = bool(fps_in and fps_in != fps_out)
    near = retimed and abs(float(fps_in / fps_out) - 1.0) <= 0.002      # 23.976 <-> 24: 0.1 %
    min_frames = int(a.frames) if a.frames else int(math.ceil(GENJUTSU_MIN_S * fps_out - Fraction(1, 10 ** 9)))
    if retimed and not near and not a.retime:
        n0 = info["nb_frames"]
        _, r_bad, _ = billed_seconds(max(n0, min_frames), fps_out)
        n24 = int(math.floor(Fraction(n0) * fps_out / fps_in + Fraction(1, 2)))
        _, r_ok, _ = billed_seconds(max(n24, min_frames), fps_out)
        price = f", billed ~{r_bad} s instead of ~{r_ok} s" if r_bad != r_ok else ""
        raise FpsMismatch(
            f"{a.IN} is {rrio.fps_str(fps_in)} fps but --fps is {rrio.fps_str(fps_out)}: padding would play its "
            f"{n0} frames at {rrio.fps_str(fps_out)} (motion x{float(fps_out / fps_in):.3f}{price}). Export the "
            f"cut at the output rate first: frames.py export W --cut <id> --fps {a.fps} (then pad that clip), or "
            f"pass --retime to re-time on purpose.")
    n = info["nb_frames"]
    mode = a.mode
    if mode == "auto":
        mode = "pingpong" if n < min_frames else "freeze"
    target, why = pad_target(n, min_frames, fps_out, a.whole_seconds, a.job)
    seq = pad_sequence(n, target, mode)
    w, h = info["w"], info["h"]
    crop = None
    if w % 2 or h % 2:
        crop = (0, 0, w - w % 2, h - h % 2)
        w, h = crop[2], crop[3]
    need = Counter(seq)
    frames = {}
    # in-order sequences (as is, freeze) stream frame by frame; only a ping-pong (< 4 s) is held in memory
    stream = all(y >= x for x, y in zip(seq, seq[1:]))
    if not stream:
        for i, fr in rrio.read_frames(a.IN, crop=crop, info=info):
            frames[i] = fr
        if len(frames) != n:
            n = len(frames)
            target, why = pad_target(n, min_frames, fps_out, a.whole_seconds, a.job)
            seq = pad_sequence(n, target, mode)
    written = 0
    with rrio.VideoWriter(a.OUT, w, h, fps_out, crf=a.crf, preset=a.preset) as vw:
        if stream:
            for i, fr in rrio.read_frames(a.IN, crop=crop, info=info):
                for _ in range(need.get(i, 0)):
                    vw.write(fr)
                    written += 1
        else:
            for i in seq:
                vw.write(frames[i])
                written += 1
    if written != len(seq):
        raise RuntimeError(f"wrote {written} frames, expected {len(seq)}")
    po = rrio.probe(a.OUT, count=True)                    # price from the PROBED clip, not from the plan
    if po["nb_frames"] != written:
        raise RuntimeError(f"{a.OUT}: probed {po['nb_frames']} frames, wrote {written}")
    if po.get("fps") and po["fps"] != fps_out:
        raise RuntimeError(f"{a.OUT}: probed {rrio.fps_str(po['fps'])} fps, expected {rrio.fps_str(fps_out)}")
    secs, bill_rep, bill_mt = billed_seconds(po["nb_frames"], fps_out)
    whole = secs.denominator == 1
    lost_mt = max(0, written - int(math.ceil(bill_mt * fps_out - Fraction(1, 10 ** 9))))
    meta = {"src": a.IN, "out": a.OUT, "mode": mode, "job": a.job, "orig_frames": n, "padded_frames": written,
            "probed_frames": po["nb_frames"], "fps": rrio.fps_str(fps_out),
            "fps_in": rrio.fps_str(fps_in) if fps_in else None, "retimed": retimed,
            "duration_s": round(float(secs), 4), "whole_seconds": whole, "pad_rule": why,
            "billed_seconds_replace": bill_rep, "billed_seconds_mt": bill_mt, "mt_tail_frames_lost": lost_mt,
            "genjutsu_min_ok": secs >= GENJUTSU_MIN_S, "w": w, "h": h,
            "keep_padded_index": list(range(min(n, written))), "seq": seq,
            "note": ("padded frame k shows source frame seq[k]; frames 0..orig_frames-1 are the original "
                     "motion in order (keep them). Map a generated take back with "
                     "`frames.py map --gen-frames N --padded P --k K` = min(N-1, floor(K*N/P + 0.5)). "
                     "Genjutsu bills replace = ceil(seconds), motion transfer = round(seconds).")}
    jpath = os.path.splitext(a.OUT)[0] + ".json"
    if os.path.abspath(jpath) == os.path.abspath(a.OUT):
        jpath = a.OUT + ".json"
    rrio.save_json(jpath, meta)
    msg = ""
    if retimed and not near:
        msg = (f"  NOTE --retime: input is {rrio.fps_str(fps_in)} fps; frames re-timed to {rrio.fps_str(fps_out)} "
               f"(motion x{float(fps_out / fps_in):.3f}).")
    elif retimed:
        msg = f"  (input {rrio.fps_str(fps_in)} fps ~ {rrio.fps_str(fps_out)}: played at {rrio.fps_str(fps_out)})"
    print(f"{a.IN}: {n} frames -> {written} frames @{rrio.fps_str(fps_out)} = {meta['duration_s']:.3f}s "
          f"({mode}) {w}x{h} -> {a.OUT}{msg}")
    print(f"   {why}")
    print(f"   billed: replace {bill_rep} s, motion transfer {bill_mt} s"
          + (f" (MT returns {bill_mt} s: the last {lost_mt} input frame(s) get no generated frame)" if lost_mt else "")
          + ("" if whole else "  [not whole seconds]"))
    if secs < GENJUTSU_MIN_S:
        print(f"   WARNING {float(secs):.3f} s is under the {GENJUTSU_MIN_S} s Genjutsu minimum")
    if fps_out.denominator != 1 and not whole:
        print(f"   WARNING {rrio.fps_str(fps_out)} fps cannot land on whole seconds: use --fps 24 for driving clips")
    print(f"   meta {jpath}")
    return 0


# --------------------------------------------------------------------------------------------------
# catalog
# --------------------------------------------------------------------------------------------------
def cmd_catalog(a):
    W = os.path.abspath(a.W)
    if not os.path.isdir(W):
        raise UsageError(f"workspace not found: {W}")
    if not os.path.exists(a.clip):
        raise UsageError(f"clip not found: {a.clip}")
    info = rrio.probe(a.clip)
    fps = info["fps"]
    n = info["nb_frames"]
    name = a.name or os.path.splitext(os.path.basename(a.clip))[0]
    if any(ch in name for ch in "/\\") or not name:
        raise UsageError(f"bad --name {name!r}")
    step = Fraction(1) / rrio.parse_fps(a.fps) if rrio.parse_fps(a.fps) else None
    if not step:
        raise UsageError(f"bad --fps {a.fps!r}")
    t0 = Fraction(a.start).limit_denominator(1000) if a.start else Fraction(0)
    dur = Fraction(n) / fps
    t1 = min(dur, Fraction(a.end).limit_denominator(1000)) if a.end is not None else dur
    idx, t = [], t0
    while t < t1 - Fraction(1, 10 ** 6):
        f = min(n - 1, int(math.floor(t * fps + Fraction(1, 10 ** 6))))
        if not idx or f != idx[-1]:
            idx.append(f)
        t += step
    if not idx:
        raise UsageError("no frames in the requested range")
    crop = None
    if a.crop:
        crop = resolve_crop(a.crop, None, info)
    pre_w = min((crop[2] if crop else info["w"]), a.tile_w * 2)
    frames = rrio.read_frames_at(a.clip, idx, scale_w=pre_w, crop=crop, info=info, strict=False)
    per = max(1, a.per_page)
    pages = [list(range(i, min(len(idx), i + per))) for i in range(0, len(idx), per)]
    outs = []
    for pi, page in enumerate(pages):
        suffix = "" if len(pages) == 1 else f"_p{pi + 1}"
        path = os.path.join(W, "sheets", f"catalog_{name}{suffix}.jpg")
        labels = [f"{name} {idx[k] / float(fps):.2f}s f{idx[k]}" for k in page]
        first, last = idx[page[0]], idx[page[-1]]
        title = (f"{name}  {os.path.basename(a.clip)}  {info['w']}x{info['h']} {info['fps_str']}fps {n}f  "
                 f"{first / float(fps):.2f}-{last / float(fps):.2f}s every {float(step):.3g}s"
                 + (f"  page {pi + 1}/{len(pages)}" if len(pages) > 1 else ""))
        res = rrio.tile_sheet([frames[k] for k in page], labels, cols=a.cols, out_path=path, tile_w=a.tile_w,
                              max_bytes=a.max_bytes, max_w=a.max_w, title=title)
        outs.append({"path": path, "bytes": res["bytes"], "frames": [idx[k] for k in page]})
        print(f"sheet {path} ({res['bytes']} bytes, {len(page)} tiles, {res['w']}x{res['h']})")
    meta = {"clip": a.clip, "name": name, "w": info["w"], "h": info["h"], "fps": info["fps_str"], "frames": n,
            "duration_s": round(float(dur), 4), "sample_fps": a.fps,
            "samples": [{"f": f, "t": round(f / float(fps), 4)} for f in idx], "pages": outs,
            "note": "label time = frame start time f/fps; use the frame index for in-points"}
    jpath = os.path.join(W, "sheets", f"catalog_{name}.json")
    rrio.save_json(jpath, meta)
    print(f"{name}: {len(idx)} samples from {n} frames ({float(dur):.2f}s @{info['fps_str']}), index {jpath}")
    return 0


# --------------------------------------------------------------------------------------------------
# map
# --------------------------------------------------------------------------------------------------
def map_index(k, n_gen, n_pad):
    """Generated-take frame for padded-input frame k: min(N-1, floor(k*N/P + 0.5)) (proportional)."""
    if n_gen <= 0 or n_pad <= 0:
        raise UsageError("--gen-frames and --padded must be > 0")
    return int(min(n_gen - 1, max(0, math.floor(Fraction(int(k) * int(n_gen), int(n_pad)) + Fraction(1, 2)))))


def cmd_map(a):
    n_gen = a.gen_frames
    if a.gen_clip:
        n_gen = rrio.probe(a.gen_clip, count=True)["nb_frames"]
    if not n_gen:
        raise UsageError("give --gen-frames N or --gen-clip PATH")
    n_pad = a.padded
    keep = None
    if a.pad_json:
        pj = rrio.load_json(a.pad_json)
        n_pad = n_pad or pj.get("padded_frames")
        keep = pj.get("keep_padded_index")
    if not n_pad:
        raise UsageError("give --padded P or --pad-json OUT.json")
    if a.k is not None:
        print(map_index(a.k, n_gen, n_pad))
        return 0
    if keep is None:
        keep = list(range(n_pad))
    import json
    out = {"gen_frames": n_gen, "padded_frames": n_pad, "formula": "gen = min(N-1, floor(k*N/P + 0.5))",
           "orig_to_gen": [map_index(k, n_gen, n_pad) for k in keep]}
    print(json.dumps(out))
    return 0


# --------------------------------------------------------------------------------------------------
# plate-frames
# --------------------------------------------------------------------------------------------------
def cmd_plate_frames(a):
    if not os.path.exists(a.clip):
        raise UsageError(f"clip not found: {a.clip}")
    info = rrio.probe(a.clip)
    if not info.get("has_video"):
        raise UsageError(f"{a.clip}: no video stream")
    n = info["nb_frames"]
    os.makedirs(a.out, exist_ok=True)
    for fn in os.listdir(a.out):
        if fn.startswith(a.prefix) and fn.endswith(".jpg"):
            os.unlink(os.path.join(a.out, fn))
    ow = int(a.w) if a.w else info["w"]
    oh = int(round(info["h"] * ow / info["w"] / 2)) * 2
    ow -= ow % 2
    m = rrio._in_matrix(info)
    mx = f":in_color_matrix={m}" if m else ""
    chain = []
    start = max(0, int(a.start or 0))
    if start or a.count:
        chain.append(f"trim=start_frame={start}" + (f":end_frame={start + int(a.count)}" if a.count else ""))
    if a.every > 1:
        chain.append(f"select=not(mod(n\\,{a.every}))")
    flags = "lanczos" if ow < info["w"] else "bicubic"
    # JPEG decoders assume BT.601 full range: convert the matrix explicitly (bt709 plates stay true colour)
    chain.append(f"scale={ow}:{oh}:flags={flags}+accurate_rnd+full_chroma_int{mx}"
                 f":out_color_matrix=bt601:out_range=full")
    chain.append("format=yuvj420p")
    pattern = os.path.join(a.out, f"{a.prefix}%05d.jpg")
    first_num = start if a.every == 1 else 0
    rrio.run_ffmpeg(["-i", a.clip, "-map", f"0:{info['stream_index']}", "-an", "-vf", ",".join(chain),
                     *rrio._passthrough(), "-q:v", str(a.q), "-start_number", str(first_num), pattern])
    files = sorted(fn for fn in os.listdir(a.out) if fn.startswith(a.prefix) and fn.endswith(".jpg"))
    end = n if not a.count else min(n, start + int(a.count))
    src_idx = list(range(start, end, a.every))
    if len(files) != len(src_idx):
        print(f"{PROG}: warning: wrote {len(files)} frames, expected {len(src_idx)}", file=sys.stderr)
    meta = {"clip": a.clip, "w": ow, "h": oh, "src_w": info["w"], "src_h": info["h"], "fps": info["fps_str"],
            "frames": len(files), "pattern": f"{a.prefix}%05d.jpg", "start_number": first_num,
            "every": a.every, "src_index": src_idx[:len(files)] if a.every > 1 else None,
            "note": ("file number = source frame index" if a.every == 1 else
                     "files are numbered 0.. in order; src_index gives the source frame of each")}
    rrio.save_json(os.path.join(a.out, "frames.json"), meta)
    tot = sum(os.path.getsize(os.path.join(a.out, f)) for f in files)
    print(f"{a.clip}: {len(files)} JPEG frames {ow}x{oh} q{a.q} -> {pattern} ({tot // 1024} KiB), "
          f"meta {os.path.join(a.out, 'frames.json')}")
    return 0


# --------------------------------------------------------------------------------------------------
def build_parser():
    ap = argparse.ArgumentParser(prog=PROG, description="Frame-exact key frames, cut clips, Genjutsu padding "
                                 "and plate catalogs for katana.",
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("keyframes", help="full-res key frame per cut (+ labelled sheet)")
    p.add_argument("W", help="workspace dir")
    p.add_argument("--which", default="mid", choices=["mid", "first", "last", "best", "breakdown"],
                   help="mid (default) | first | last | best = sharpest of 5 candidates | breakdown = "
                        "route_suggestion.keyframe from breakdown.json (else mid)")
    p.add_argument("--cuts", help="comma list of cut ids (default all)")
    p.add_argument("--frames", help="manual picks, e.g. c03=57,c05=120")
    p.add_argument("--crop", default="window", help="window (default: analysis window/letterbox) | none | x,y,w,h")
    p.add_argument("--video", help="override the reference video path")
    p.add_argument("--analysis-w", type=int, default=640, help="width for the sharpness measure (default 640)")
    p.add_argument("--cols", type=int, default=6)
    p.add_argument("--tile-w", type=int, default=256)
    p.add_argument("--max-bytes", type=int, default=500_000)
    p.set_defaults(fn=cmd_keyframes)

    p = sub.add_parser("export", help="cut -> W/cuts/<cut>.mp4 (exact frames, crf 12, no audio)")
    p.add_argument("W")
    p.add_argument("--cut", required=True, help="cut id, comma list, or all")
    p.add_argument("--fps", default="native", help="native (default) | 24 (Genjutsu driving clips) | any rate; "
                   "re-timing keeps the duration and one output frame per distinct source image where the rate "
                   "allows (see --phase)")
    p.add_argument("--crop", default="window", help="window (default) | none | x,y,w,h")
    p.add_argument("--phase", default="auto", help="auto (default): one output frame per distinct source image "
                   "where possible (hold runs; keeps the cut's first and last image; content faster than --fps "
                   "drops the images its neighbours cover best) | a number: legacy fixed-phase sampling, in "
                   "source frames")
    p.add_argument("--max-extra", type=int, default=2,
                   help="--phase auto only: allow up to N extra output frames so a short cut keeps every distinct "
                   "image (e.g. 1-frame runs at both cut edges); only while the "
                   "clip stays under 4 s, so the 96-frame pad and its price do not change (default 2; 0 = "
                   "strictly round(n*fps_out/fps_in))")
    p.add_argument("--edges", default="keep", choices=["keep", "auto"],
                   help="--phase auto only: keep (default) = the first and last output frames show the cut's "
                   "first and last images; auto = score the edge images like any other (may drop an edge image "
                   "that its neighbour covers; +0.2-1.4 dB on fast-motion cuts in the Altman test)")
    p.add_argument("--crf", type=int, default=12)
    p.add_argument("--preset", default="medium")
    p.add_argument("--out", help="output path (single cut only; default W/cuts/<cut>.mp4)")
    p.add_argument("--video", help="override the reference video path")
    p.set_defaults(fn=cmd_export)

    p = sub.add_parser("pad", help="pad a 24 fps cut export to a Genjutsu driving clip (>= 4 s, whole seconds)")
    p.add_argument("IN", help="the cut exported at --fps (frames.py export W --cut <id> --fps 24)")
    p.add_argument("OUT")
    p.add_argument("--frames", type=int, help="minimum frames (default 4 s at --fps: 96 @24)")
    p.add_argument("--fps", default="24", help="output fps (default 24). The input must already be at this rate "
                   "(exit 2 otherwise) unless --retime")
    p.add_argument("--retime", action="store_true", help="accept an input at another fps: its frames are played "
                   "as-is at --fps (motion speed changes, billed seconds change with it)")
    p.add_argument("--mode", default="auto", choices=["auto", "pingpong", "freeze"],
                   help="auto (default): pingpong when the clip is shorter than --frames, freeze otherwise")
    p.add_argument("--for", dest="job", default="replace", choices=["replace", "mt"],
                   help="whole-second rule: replace (default; bills ceil -> always pad to an exact integer) | mt "
                        "(bills round -> no pad when the fractional second is <= 0.1 s, else pad to ceil)")
    p.add_argument("--whole-seconds", dest="whole_seconds", action="store_true", default=True,
                   help="apply the --for whole-second rule to clips >= --frames (default)")
    p.add_argument("--no-whole-seconds", dest="whole_seconds", action="store_false")
    p.add_argument("--crf", type=int, default=12)
    p.add_argument("--preset", default="medium")
    p.set_defaults(fn=cmd_pad)

    p = sub.add_parser("catalog", help="timestamped contact sheet(s) of a generated plate")
    p.add_argument("W")
    p.add_argument("--clip", required=True)
    p.add_argument("--name", help="label/name (default clip basename)")
    p.add_argument("--fps", default="4", help="samples per second (default 4)")
    p.add_argument("--start", type=float, help="start time s")
    p.add_argument("--end", type=float, help="end time s")
    p.add_argument("--crop", help="x,y,w,h crop of the plate")
    p.add_argument("--cols", type=int, default=8)
    p.add_argument("--per-page", type=int, default=64, help="tiles per sheet (default 64 = 16 s at 4 fps)")
    p.add_argument("--tile-w", type=int, default=196)
    p.add_argument("--max-w", type=int, default=1600)
    p.add_argument("--max-bytes", type=int, default=500_000)
    p.set_defaults(fn=cmd_catalog)

    p = sub.add_parser("map", help="padded-input frame -> generated-take frame: min(N-1, floor(k*N/P + 0.5))")
    p.add_argument("--gen-frames", type=int, help="N = frames in the generated take")
    p.add_argument("--gen-clip", help="read N from this clip instead")
    p.add_argument("--padded", type=int, help="P = frames in the padded input")
    p.add_argument("--k", type=int, help="padded-input frame index (prints one integer)")
    p.add_argument("--pad-json", help="pad meta JSON: prints the mapping for every kept frame")
    p.set_defaults(fn=cmd_map)

    p = sub.add_parser("plate-frames", help="extract JPEG frames for the compositor")
    p.add_argument("--clip", required=True)
    p.add_argument("--out", required=True, help="output dir")
    p.add_argument("--w", type=int, default=1440, help="output width (default 1440; 0 = native)")
    p.add_argument("--q", type=int, default=3, help="mjpeg qscale 2 (best) .. 31 (default 3)")
    p.add_argument("--start", type=int, default=0, help="first frame")
    p.add_argument("--count", type=int, help="number of frames")
    p.add_argument("--every", type=int, default=1)
    p.add_argument("--prefix", default="f_", help="file prefix (default f_ -> f_00000.jpg)")
    p.set_defaults(fn=cmd_plate_frames)
    return ap


def main(argv=None):
    ap = build_parser()
    a = ap.parse_args(argv)
    try:
        return a.fn(a)
    except (UsageError, FileNotFoundError, ValueError, IndexError) as e:
        print(f"{PROG}: error: {e}", file=sys.stderr)
        return 1
    except (RuntimeError, FpsMismatch) as e:
        print(f"{PROG}: error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
