#!/usr/bin/env python3
"""faces.py - YuNet face boxes + 5 landmarks per frame (onnxruntime + numpy), picked, gap-filled, smoothed.

Tracking/inspection only: this helper never swaps, restores, warps, retouches or animates facial pixels.
Landmarks may position whole-plate camera moves or separate observed source graphics, never face edits.

Subcommands
  track W --clip PATH [--name A1] [--every 1] [--pick track|largest|left|center|right] [--sigma 1.5]
        [--max-gap 12] [--score 0.6] [--cuts f1,f2] [--crop x,y,w,h] [--from-raw]
      -> W/faces/<name>.json       [{f, box:[x,y,w,h], score, eyes:[[x,y],[x,y]], nose:[x,y],
                                      mouth:[[x,y],[x,y]], src}]  one entry per frame, clip pixels;
                                      no face: box/eyes/nose/mouth null, score 0, src "none"
         W/faces/<name>.meta.json  clip size/fps, parameters, detection stats, segments
         W/faces/<name>.raw.json   every raw detection per processed frame (re-pick with --from-raw)
         W/faces/<name>_qa.jpg     overlay QA sheet (green = detected, yellow = filled, grey = other faces)
  detect IMG_OR_VIDEO [--frames 0,10] [--overlay out.jpg]   raw detections as JSON (quick check)
  convert-chrome IN.json --out OUT.json (--clip PATH | --w W --h H)   Chrome FaceDetector arrays -> schema
  fetch-model                                                 download + verify the model only

Landmark order follows YuNet: eyes = [subject's right eye, subject's left eye] (image-left first on a
frontal face), nose = tip, mouth = [right corner, left corner]. src: det | interp (linear between
detections, <= --max-gap frames) | hold (clip edge / --cuts boundary, <= --max-gap) | none.

Model: face_detection_yunet_2023mar.onnx (OpenCV zoo, MIT, 232589 bytes, sha256 checked). Looked up in
<scripts>/models/, $RR_CACHE (default /home/user/.rr/cache), W/.cache, ~/.rr/cache; else downloaded once into
the first writable of those caches; --model PATH overrides.
The model's input is a fixed 1x3x640x640 BGR 0-255 tensor: each frame is scaled to fit 640 and
zero-padded right/bottom (OpenCV FaceDetectorYN pads the same way; a dynamic-shape model is padded to a
multiple of 32 instead). Post-processing = OpenCV FaceDetectorYN (2023mar): strides 8/16/32, score =
sqrt(clip(cls)*clip(obj)), cx=(col+dx)*s, cy=(row+dy)*s, w=exp(dw)*s, h=exp(dh)*s,
kps=((col+kx)*s, (row+ky)*s), greedy NMS (IoU 0.3).
Needs onnxruntime (preinstalled in the Higgsfield sandbox).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402

import rrio  # noqa: E402

PROG = "faces.py"
MODEL_NAME = "face_detection_yunet_2023mar.onnx"
MODEL_SHA256 = "8f2383e4dd3cfbb4553ea8718107fc0423210dc964f9f4280604804ed2552fa4"
MODEL_URLS = [
    "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx",
    "https://media.githubusercontent.com/media/opencv/opencv_zoo/main/models/face_detection_yunet/"
    "face_detection_yunet_2023mar.onnx",
    "https://huggingface.co/opencv/face_detection_yunet/resolve/main/face_detection_yunet_2023mar.onnx",
]
STRIDES = (8, 16, 32)


class UsageError(Exception):
    pass


# --------------------------------------------------------------------------------------------------
# model file
# --------------------------------------------------------------------------------------------------
def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def _cache_dirs(W=None):
    out = []
    if os.environ.get("RR_CACHE"):
        out.append(os.environ["RR_CACHE"])
    out.append("/home/user/.rr/cache")
    if W:
        out.append(os.path.join(os.path.abspath(W), ".cache"))
    out.append(os.path.join(os.path.expanduser("~"), ".rr", "cache"))
    seen, res = set(), []
    for d in out:
        if d not in seen:
            seen.add(d)
            res.append(d)
    return res


def ensure_model(model=None, W=None, verify=True, quiet=False):
    """Path of a verified YuNet model; downloads it once into the first writable cache dir."""
    if model:
        if not os.path.exists(model):
            raise UsageError(f"--model not found: {model}")
        return model
    dirs = _cache_dirs(W)
    bundled = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")  # optional, shipped with the bundle
    for d in [bundled] + dirs:
        p = os.path.join(d, MODEL_NAME)
        if os.path.exists(p) and (not verify or _sha256(p) == MODEL_SHA256):
            return p
    target = None
    for d in dirs:
        try:
            os.makedirs(d, exist_ok=True)
            if os.access(d, os.W_OK):
                target = d
                break
        except OSError:
            continue
    if not target:
        raise UsageError(f"no writable cache dir among {dirs}")
    dest = os.path.join(target, MODEL_NAME)
    errs = []
    for url in MODEL_URLS:
        for attempt in range(3):
            part = dest + f".{os.getpid()}.part"
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "katana-faces/1"})
                with urllib.request.urlopen(req, timeout=30) as r, open(part, "wb") as f:
                    while True:
                        b = r.read(1 << 16)
                        if not b:
                            break
                        f.write(b)
                with open(part, "rb") as f:
                    head = f.read(64)
                if head.startswith(b"version https://git-lfs"):
                    raise ValueError("got a git-lfs pointer, not the model")
                sha = _sha256(part)
                if verify and sha != MODEL_SHA256:
                    raise ValueError(f"sha256 mismatch ({sha[:12]}...)")
                os.replace(part, dest)
                if not quiet:
                    print(f"model downloaded: {dest} ({os.path.getsize(dest)} bytes)", file=sys.stderr)
                return dest
            except Exception as e:  # network errors, bad payloads: try again / next mirror
                errs.append(f"{url.split('/')[2]}: {e}")
                try:
                    os.unlink(part)
                except OSError:
                    pass
                if isinstance(e, ValueError):
                    break
                time.sleep(1.5 * (attempt + 1))
    raise RuntimeError("could not download the YuNet model: " + "; ".join(errs[-4:]))


# --------------------------------------------------------------------------------------------------
# runner (onnxruntime). Tests may replace make_runner with another backend returning the same thing.
# --------------------------------------------------------------------------------------------------
def make_runner(model_path, threads=None):
    """-> (run(blob NCHW float32) -> {output_name: ndarray}, input_hw (H, W) or None when dynamic)."""
    try:
        import onnxruntime as ort
    except ImportError:
        raise UsageError("onnxruntime is not installed (the Higgsfield sandbox has it; elsewhere: "
                         "rr_pip onnxruntime)") from None
    so = ort.SessionOptions()
    so.intra_op_num_threads = int(threads or min(8, os.cpu_count() or 4))
    so.inter_op_num_threads = 1
    so.log_severity_level = 3
    sess = ort.InferenceSession(model_path, sess_options=so, providers=["CPUExecutionProvider"])
    inp = sess.get_inputs()[0]
    names = [o.name for o in sess.get_outputs()]
    shp = list(inp.shape)
    hw = None
    if len(shp) == 4 and isinstance(shp[2], int) and isinstance(shp[3], int) and shp[2] > 0 and shp[3] > 0:
        hw = (int(shp[2]), int(shp[3]))

    def run(blob):
        outs = sess.run(names, {inp.name: blob})
        return dict(zip(names, outs))

    return run, hw


# --------------------------------------------------------------------------------------------------
# YuNet decode
# --------------------------------------------------------------------------------------------------
def nms(boxes, scores, thr=0.3, top_k=5000):
    """Greedy NMS on [x,y,w,h] boxes; returns kept indices (score order)."""
    order = np.argsort(-scores, kind="stable")[:top_k]
    x1, y1 = boxes[:, 0], boxes[:, 1]
    x2, y2 = x1 + boxes[:, 2], y1 + boxes[:, 3]
    area = np.maximum(boxes[:, 2], 0) * np.maximum(boxes[:, 3], 0)
    keep = []
    while order.size:
        i = order[0]
        keep.append(int(i))
        if order.size == 1:
            break
        rest = order[1:]
        iw = np.maximum(0.0, np.minimum(x2[i], x2[rest]) - np.maximum(x1[i], x1[rest]))
        ih = np.maximum(0.0, np.minimum(y2[i], y2[rest]) - np.maximum(y1[i], y1[rest]))
        inter = iw * ih
        iou = inter / np.maximum(area[i] + area[rest] - inter, 1e-9)
        order = rest[iou <= thr]
    return keep


def decode(outs, pad_w, pad_h, score_thr=0.6, nms_thr=0.3, top_k=5000):
    """YuNet 2023mar outputs -> N x 15 [x,y,w,h, rex,rey, lex,ley, nx,ny, rmx,rmy, lmx,lmy, score]."""
    rows_all = []
    for s in STRIDES:
        cols, rows = pad_w // s, pad_h // s
        cls = np.asarray(outs[f"cls_{s}"], np.float32).reshape(-1)
        obj = np.asarray(outs[f"obj_{s}"], np.float32).reshape(-1)
        bbox = np.asarray(outs[f"bbox_{s}"], np.float32).reshape(-1, 4)
        kps = np.asarray(outs[f"kps_{s}"], np.float32).reshape(-1, 10)
        if cls.size != rows * cols:
            raise RuntimeError(f"stride {s}: {cls.size} anchors for a {cols}x{rows} grid (input size mismatch)")
        score = np.sqrt(np.clip(cls, 0, 1) * np.clip(obj, 0, 1))
        idx = np.nonzero(score >= score_thr)[0]
        if not idx.size:
            continue
        r = (idx // cols).astype(np.float32)
        c = (idx % cols).astype(np.float32)
        cx = (c + bbox[idx, 0]) * s
        cy = (r + bbox[idx, 1]) * s
        w = np.exp(bbox[idx, 2]) * s
        h = np.exp(bbox[idx, 3]) * s
        kx = (kps[idx, 0::2] + c[:, None]) * s
        ky = (kps[idx, 1::2] + r[:, None]) * s
        k = np.empty((idx.size, 10), np.float32)
        k[:, 0::2], k[:, 1::2] = kx, ky
        rows_all.append(np.concatenate([np.stack([cx - w / 2, cy - h / 2, w, h], 1), k, score[idx, None]], 1))
    if not rows_all:
        return np.zeros((0, 15), np.float32)
    d = np.concatenate(rows_all, 0)
    if len(d) > 1:
        d = d[nms(d[:, :4], d[:, 14], nms_thr, top_k)]
    return d


class YuNet:
    def __init__(self, model_path, score=0.6, nms_thr=0.3, threads=None, runner=None):
        self.run, self.input_hw = runner if runner is not None else make_runner(model_path, threads)
        self.score, self.nms_thr = score, nms_thr

    def fit_size(self, w, h, det_w=640):
        """Size to scale a w x h frame to before detection (fits the model input)."""
        if self.input_hw:
            ih, iw = self.input_hw
            s = min(iw / w, ih / h)
        else:
            s = det_w / max(w, h)
        return max(1, int(round(w * s))), max(1, int(round(h * s)))

    def detect_scaled(self, img, sx=1.0, sy=1.0, ox=0.0, oy=0.0):
        """img: RGB uint8 already scaled to fit; returns dets mapped back: x/sx + ox, y/sy + oy."""
        h, w = img.shape[:2]
        if self.input_hw:
            ph, pw = self.input_hw
            if w > pw or h > ph:
                raise ValueError(f"image {w}x{h} larger than the model input {pw}x{ph}")
        else:
            pw, ph = (w + 31) // 32 * 32, (h + 31) // 32 * 32
        blob = np.zeros((1, 3, ph, pw), np.float32)
        blob[0, :, :h, :w] = img[:, :, ::-1].transpose(2, 0, 1)  # RGB -> BGR, HWC -> CHW, 0..255
        d = decode(self.run(blob), pw, ph, self.score, self.nms_thr)
        if len(d):
            d = d.astype(np.float64)
            d[:, [0, 4, 6, 8, 10, 12]] = d[:, [0, 4, 6, 8, 10, 12]] / sx + ox
            d[:, [1, 5, 7, 9, 11, 13]] = d[:, [1, 5, 7, 9, 11, 13]] / sy + oy
            d[:, 2] /= sx
            d[:, 3] /= sy
        return d

    def detect(self, img):
        """Full-size RGB frame -> dets in frame pixels (resizes in numpy; tracking resizes in ffmpeg)."""
        h, w = img.shape[:2]
        tw, th = self.fit_size(w, h)
        small = img if (tw, th) == (w, h) else rrio.resize(img, tw, th, "area")
        return self.detect_scaled(small, tw / w, th / h)


# --------------------------------------------------------------------------------------------------
# picking, filling, smoothing
# --------------------------------------------------------------------------------------------------
def iou(a, b):
    ax2, ay2, bx2, by2 = a[0] + a[2], a[1] + a[3], b[0] + b[2], b[1] + b[3]
    iw = max(0.0, min(ax2, bx2) - max(a[0], b[0]))
    ih = max(0.0, min(ay2, by2) - max(a[1], b[1]))
    inter = iw * ih
    u = a[2] * a[3] + b[2] * b[3] - inter
    return inter / u if u > 0 else 0.0


def _ctr(d):
    return d[0] + d[2] / 2, d[1] + d[3] / 2


def pick_one(dets, mode, W, H, prev=None, seed=None):
    if not len(dets):
        return None
    areas = dets[:, 2] * dets[:, 3]
    big = dets[areas >= 0.25 * areas.max()]
    if mode == "largest" or (mode == "track" and prev is None and seed is None):
        return dets[int(np.argmax(areas))]
    if mode == "track" and prev is None and seed is not None:
        dd = [math.hypot(_ctr(d)[0] - seed[0], _ctr(d)[1] - seed[1]) for d in dets]
        return dets[int(np.argmin(dd))]
    if mode == "left":
        return big[int(np.argmin(big[:, 0] + big[:, 2] / 2))]
    if mode == "right":
        return big[int(np.argmax(big[:, 0] + big[:, 2] / 2))]
    if mode == "center":
        dd = [math.hypot(_ctr(d)[0] - W / 2, _ctr(d)[1] - H / 2) for d in big]
        return big[int(np.argmin(dd))]
    if mode == "track":
        ious = [iou(prev, d) for d in dets]
        k = int(np.argmax(ious))
        if ious[k] >= 0.3:
            return dets[k]
        pc = _ctr(prev)
        best, bd = None, None
        for d in dets:
            dist = math.hypot(_ctr(d)[0] - pc[0], _ctr(d)[1] - pc[1])
            ratio = (d[2] * d[3]) / max(prev[2] * prev[3], 1e-6)
            if dist <= 0.75 * max(prev[2], 1.0) and 0.4 <= ratio <= 2.5 and (bd is None or dist < bd):
                best, bd = d, dist
        return best
    raise UsageError(f"unknown pick mode {mode}")


def choose_track(raw, frames, mode, W, H, seed=None, reacquire=3, cuts=()):
    """raw: {f: N x 15 array}; frames: processed frame indices in order -> ({f: det or None}, [reacquired f]).
    A frame in `cuts` (a known shot start) resets the track: the next face is picked afresh. A track that
    re-acquires a face after losing it starts a new segment there (no interpolation across)."""
    chosen, prev, lost, reacq = {}, None, 0, []
    cut_set = sorted(int(c) for c in cuts)
    last_f = None
    done = []
    for f in frames:
        if last_f is not None and any(last_f < c <= f for c in cut_set):
            prev, lost = None, 0
        last_f = f
        dets = raw.get(f)
        if dets is None or not len(dets):
            chosen[f] = None
            lost += 1
            done.append(f)
            continue
        d = pick_one(dets, mode, W, H, prev if mode == "track" else None, seed)
        if d is None and mode == "track" and lost >= reacquire:
            d = pick_one(dets, "largest", W, H)
            # walk back over the frames lost since the old face vanished: the new face was often already
            # there (rejected for continuity); give them to the new track and start its segment earlier
            start, cur = f, d
            for g in reversed(done[-lost:] if lost else []):
                if chosen.get(g) is not None or raw.get(g) is None or not len(raw[g]):
                    break
                m = pick_one(raw[g], "track", W, H, prev=cur)
                if m is None:
                    break
                chosen[g], cur, start = m, m, g
            reacq.append(start)
        if d is None:
            lost += 1
        else:
            lost = 0
            prev = d
        chosen[f] = d
        done.append(f)
    return chosen, reacq


def _gauss_runs(vals, valid, sigma):
    """Normalised gaussian smoothing of rows of `vals` over contiguous valid runs."""
    if sigma <= 0:
        return vals
    out = vals.copy()
    n = len(vals)
    r = max(1, int(math.ceil(3 * sigma)))
    k = np.exp(-0.5 * (np.arange(-r, r + 1) / sigma) ** 2)
    i = 0
    while i < n:
        if not valid[i]:
            i += 1
            continue
        j = i
        while j < n and valid[j]:
            j += 1
        seg = vals[i:j]
        L = j - i
        for t in range(L):
            lo, hi = max(0, t - r), min(L, t + r + 1)
            wts = k[lo - t + r:hi - t + r]
            out[i + t] = (seg[lo:hi] * wts[:, None]).sum(0) / wts.sum()
        i = j
    return out


def _is_jump(da, db):
    """Two detections are different faces / a hard cut: no overlap and a big move or a big size change."""
    if iou(da, db) >= 0.1:
        return False
    ca, cb = _ctr(da), _ctr(db)
    ratio = (db[2] * db[3]) / max(da[2] * da[3], 1e-6)
    return math.hypot(ca[0] - cb[0], ca[1] - cb[1]) > 0.6 * max(da[2], db[2]) or not 0.4 <= ratio <= 2.5


def build_track(chosen, f_start, f_end, max_gap=12, sigma=1.5, sigma_size=2.5, cuts=(), breaks=()):
    """chosen: {f: 15-vector or None} for processed frames -> per-frame list (f_start..f_end inclusive).
    cuts: forced shot starts (holds allowed up to them); breaks: segment starts without holds
    (re-acquired tracks)."""
    n = f_end - f_start + 1
    vals = np.zeros((n, 15), np.float64)
    src = ["none"] * n
    for f, d in chosen.items():
        if d is not None and f_start <= f <= f_end:
            vals[f - f_start] = d
            src[f - f_start] = "det"
    det_idx = [i for i in range(n) if src[i] == "det"]
    # segment boundaries: forced cuts + detected jumps (a different face / a hard cut in the plate)
    bounds = sorted({int(c) - f_start for c in cuts if f_start < int(c) <= f_end})
    brk = {int(f) - f_start for f in breaks if f_start < int(f) <= f_end}
    jumps = []
    for a, b in zip(det_idx, det_idx[1:]):
        if any(a < x <= b for x in bounds):
            continue
        if b in brk or _is_jump(vals[a], vals[b]):
            jumps.append((a, b))
    edges = sorted(set(bounds) | {b for _, b in jumps})  # first frame (relative) of each new segment
    seg_id = np.zeros(n, np.int64)
    for e in edges:
        seg_id[e:] += 1
    hard = set(bounds)
    starts = [0] + edges
    ends = [e - 1 for e in edges] + [n - 1]

    # fill gaps inside a segment by linear interpolation (<= max_gap missing frames)
    for a, b in zip(det_idx, det_idx[1:]):
        gap = b - a - 1
        if gap <= 0 or seg_id[a] != seg_id[b] or gap > max_gap:
            continue
        for t in range(a + 1, b):
            u = (t - a) / (b - a)
            vals[t] = vals[a] * (1 - u) + vals[b] * u
            src[t] = "interp"
    # hold the first/last detection of a segment towards the clip edges and forced --cuts boundaries
    # (never across an auto-detected jump: where that cut really is inside the gap is unknown)
    for s0, s1 in zip(starts, ends):
        ds = [i for i in det_idx if s0 <= i <= s1]
        if not ds:
            continue
        fd, ld = ds[0], ds[-1]
        if s0 == 0 or s0 in hard:
            for t in range(max(s0, fd - max_gap), fd):
                if src[t] == "none":
                    vals[t], src[t] = vals[fd], "hold"
        if s1 == n - 1 or (s1 + 1) in hard:
            for t in range(ld + 1, min(s1, ld + max_gap) + 1):
                if src[t] == "none":
                    vals[t], src[t] = vals[ld], "hold"
    valid = np.array([s != "none" for s in src])
    # smooth per segment: centre form for the box
    cform = vals.copy()
    cform[:, 0] = vals[:, 0] + vals[:, 2] / 2
    cform[:, 1] = vals[:, 1] + vals[:, 3] / 2
    out = cform.copy()
    for sid in np.unique(seg_id):
        m = (seg_id == sid) & valid
        if not m.any():
            continue
        sel = np.nonzero(seg_id == sid)[0]
        sub, vm = cform[sel], valid[sel]
        pos_cols = [0, 1] + list(range(4, 14))
        sm = sub.copy()
        sm[:, pos_cols] = _gauss_runs(sub[:, pos_cols], vm, sigma)
        sm[:, [2, 3]] = _gauss_runs(sub[:, [2, 3]], vm, sigma_size)
        out[sel] = sm
    res = out.copy()
    res[:, 0] = out[:, 0] - out[:, 2] / 2
    res[:, 1] = out[:, 1] - out[:, 3] / 2
    rows = []
    r1 = lambda v: round(float(v), 1)  # noqa: E731
    for i in range(n):
        f = f_start + i
        if src[i] == "none":
            rows.append({"f": f, "box": None, "score": 0.0, "eyes": None, "nose": None, "mouth": None, "src": "none"})
            continue
        v = res[i]
        rows.append({"f": f, "box": [r1(v[0]), r1(v[1]), r1(v[2]), r1(v[3])], "score": round(float(vals[i, 14]), 3),
                     "eyes": [[r1(v[4]), r1(v[5])], [r1(v[6]), r1(v[7])]], "nose": [r1(v[8]), r1(v[9])],
                     "mouth": [[r1(v[10]), r1(v[11])], [r1(v[12]), r1(v[13])]], "src": src[i]})
    segments = []
    for sid in np.unique(seg_id):
        sel = np.nonzero(seg_id == sid)[0]
        segments.append([f_start + int(sel[0]), f_start + int(sel[-1])])
    return rows, segments, [[f_start + a, f_start + b] for a, b in jumps]


# --------------------------------------------------------------------------------------------------
# drawing (QA overlays)
# --------------------------------------------------------------------------------------------------
def draw_rect(img, x, y, w, h, color, t=2):
    H, W = img.shape[:2]
    x0, y0, x1, y1 = int(round(x)), int(round(y)), int(round(x + w)), int(round(y + h))
    c = np.asarray(color, img.dtype)
    for (a0, a1, b0, b1) in ((y0, y0 + t, x0, x1), (y1 - t, y1, x0, x1), (y0, y1, x0, x0 + t), (y0, y1, x1 - t, x1)):
        a0, a1, b0, b1 = max(0, a0), min(H, a1), max(0, b0), min(W, b1)
        if a1 > a0 and b1 > b0:
            img[a0:a1, b0:b1] = c


def draw_dot(img, x, y, color, r=2):
    H, W = img.shape[:2]
    x, y = int(round(x)), int(round(y))
    y0, y1, x0, x1 = max(0, y - r), min(H, y + r + 1), max(0, x - r), min(W, x + r + 1)
    if y1 > y0 and x1 > x0:
        img[y0:y1, x0:x1] = np.asarray(color, img.dtype)


def overlay(img, row, others, scale, ox=0.0, oy=0.0):
    """Draw a track row (+ other raw dets) on an image of the clip region starting at (ox, oy), scaled."""
    X = lambda v: (v - ox) * scale  # noqa: E731
    Y = lambda v: (v - oy) * scale  # noqa: E731
    for d in others:
        draw_rect(img, X(d[0]), Y(d[1]), d[2] * scale, d[3] * scale, (150, 150, 150), 1)
    if row and row.get("box"):
        col = (40, 230, 60) if row["src"] == "det" else (255, 215, 0)
        b = row["box"]
        draw_rect(img, X(b[0]), Y(b[1]), b[2] * scale, b[3] * scale, col, 2)
        for q in row.get("eyes") or []:
            draw_dot(img, X(q[0]), Y(q[1]), (0, 255, 255))
        if row.get("nose"):
            draw_dot(img, X(row["nose"][0]), Y(row["nose"][1]), (255, 40, 40))
        for q in row.get("mouth") or []:
            draw_dot(img, X(q[0]), Y(q[1]), (255, 0, 255))


# --------------------------------------------------------------------------------------------------
# commands
# --------------------------------------------------------------------------------------------------
def _parse_xy(spec, W, H):
    if not spec:
        return None
    x, y = (float(v) for v in spec.split(","))
    if x <= 1 and y <= 1:
        x, y = x * W, y * H
    return x, y


def _crop(spec, info):
    if not spec:
        return None
    try:
        c = tuple(int(round(float(v))) for v in spec.split(","))
        assert len(c) == 4
    except (ValueError, AssertionError):
        raise UsageError(f"--crop must be x,y,w,h (got {spec!r})") from None
    x, y, w, h = c
    if x < 0 or y < 0 or w <= 0 or h <= 0 or x + w > info["w"] or y + h > info["h"]:
        raise UsageError(f"--crop {c} outside the {info['w']}x{info['h']} frame")
    return c


def cmd_track(a):
    W = os.path.abspath(a.W)
    if not os.path.isdir(W):
        raise UsageError(f"workspace not found: {W}")
    if not os.path.exists(a.clip):
        raise UsageError(f"clip not found: {a.clip}")
    info = rrio.probe(a.clip)
    CW, CH = info["w"], info["h"]
    name = a.name or os.path.splitext(os.path.basename(a.clip))[0]
    if not name or any(ch in name for ch in "/\\"):
        raise UsageError(f"bad --name {name!r}")
    fdir = os.path.join(W, "faces")
    os.makedirs(fdir, exist_ok=True)
    raw_path = os.path.join(fdir, f"{name}.raw.json")
    every = max(1, int(a.every))
    t0 = time.time()
    crop = _crop(a.crop, info)
    model_path, det_size = None, None
    if a.from_raw:
        rj = rrio.load_json(raw_path)
        raw = {int(k): np.asarray(v, np.float64).reshape(-1, 15) for k, v in rj["frames"].items()}
        frames = sorted(raw)
        f_start, f_end = rj["f_start"], rj["f_end"]
        every = rj.get("every", every)
        det_size = rj.get("det_size")
        if crop is None and rj.get("crop"):
            crop = tuple(int(v) for v in rj["crop"])
    else:
        model_path = ensure_model(a.model, W)
        det = YuNet(model_path, a.score, a.nms, a.threads)
        rw, rh = (crop[2], crop[3]) if crop else (CW, CH)
        tw, th = det.fit_size(rw, rh, a.det_w)
        det_size = [tw, th]
        sx, sy = tw / rw, th / rh
        ox, oy = (crop[0], crop[1]) if crop else (0, 0)
        f_start = max(0, int(a.start or 0))
        raw, frames = {}, []
        kw = dict(scale_w=tw, scale_h=th, crop=crop, every=every, info=info)
        for f, fr in rrio.read_frames(a.clip, f_start, a.count, **kw):
            raw[f] = det.detect_scaled(fr, sx, sy, ox, oy)
            frames.append(f)
        if not frames:
            raise UsageError("no frames decoded (check --start/--count)")
        last_dec = frames[-1]
        if every == 1:
            f_end = last_dec
        else:
            n_total = info["nb_frames"] or last_dec + 1
            f_end = n_total - 1 if not a.count else min(n_total, f_start + int(a.count)) - 1
            f_end = max(f_end, last_dec)
        rrio.save_json(raw_path, {"clip": a.clip, "w": CW, "h": CH, "f_start": f_start, "f_end": f_end,
                                  "every": every, "det_size": det_size, "score_thr": a.score,
                                  "crop": list(crop) if crop else None,
                                  "frames": {str(f): np.round(raw[f], 2).tolist() for f in frames},
                                  "cols": "x,y,w,h,rex,rey,lex,ley,nx,ny,rmx,rmy,lmx,lmy,score"})
    t_det = time.time() - t0
    seed = _parse_xy(a.seed, CW, CH)
    cuts = [int(c) for c in (a.cuts or "").split(",") if c.strip()]
    chosen, reacq = choose_track(raw, frames, a.pick, CW, CH, seed, a.reacquire, cuts)
    max_gap = max(int(a.max_gap), every - 1)
    rows, segments, jumps = build_track(chosen, f_start, f_end, max_gap, a.sigma, a.sigma_size, cuts, reacq)
    out_path = os.path.join(fdir, f"{name}.json")
    rrio.save_json(out_path, rows, indent=None)
    n = len(rows)
    cnt = {k: sum(1 for r in rows if r["src"] == k) for k in ("det", "interp", "hold", "none")}
    n_proc = len(frames)
    n_hit = sum(1 for f in frames if raw.get(f) is not None and len(raw[f]))
    multi = sum(1 for f in frames if raw.get(f) is not None and len(raw[f]) > 1)
    eye_d = [math.hypot(r["eyes"][1][0] - r["eyes"][0][0], r["eyes"][1][1] - r["eyes"][0][1])
             for r in rows if r["eyes"]]
    meta = {"clip": a.clip, "name": name, "w": CW, "h": CH, "fps": info["fps_str"], "frames": n,
            "f_start": f_start, "f_end": f_end, "every": every, "det_size": det_size, "crop": list(crop) if crop else None,
            "model": MODEL_NAME, "sha256": MODEL_SHA256, "score_thr": a.score, "nms": a.nms, "pick": a.pick,
            "seed": seed, "sigma": a.sigma, "sigma_size": a.sigma_size, "max_gap": max_gap, "cuts": cuts,
            "processed": n_proc, "processed_with_face": n_hit, "processed_multi_face": multi, "counts": cnt,
            "segments": segments, "jumps": jumps,
            "eye_dist_px_median": round(float(np.median(eye_d)), 1) if eye_d else None,
            "detect_seconds": round(t_det, 2), "units": "clip pixels (display orientation)",
            "schema": "[{f, box:[x,y,w,h], score, eyes:[[x,y],[x,y]], nose:[x,y], mouth:[[x,y],[x,y]], src}]",
            "landmark_order": "eyes=[subject right, subject left], mouth=[right corner, left corner]"}
    meta_path = os.path.join(fdir, f"{name}.meta.json")
    rrio.save_json(meta_path, meta)
    qa_path = os.path.join(fdir, f"{name}_qa.jpg")
    if a.qa_tiles > 0:
        k = min(a.qa_tiles, n)
        idx = sorted({f_start + int(round(i * (n - 1) / max(1, k - 1))) for i in range(k)})
        qcrop = crop
        rw_ = qcrop[2] if qcrop else CW
        tw_ = min(rw_, 400)
        sc = tw_ / rw_
        qox, qoy = (qcrop[0], qcrop[1]) if qcrop else (0, 0)
        imgs = rrio.read_frames_at(a.clip, idx, scale_w=tw_, crop=qcrop, info=info, strict=False)
        tiles, labels = [], []
        byf = {r["f"]: r for r in rows}
        for f, im in zip(idx, imgs):
            if im is None:
                tiles.append(None)
                labels.append(f"f{f} n/a")
                continue
            im = im.copy()
            r = byf.get(f)
            others = []
            if f in raw and r and r["box"] is not None and len(raw[f]) > 1:
                others = [d for d in raw[f] if iou(d, r["box"]) < 0.5]
            elif f in raw and (not r or r["box"] is None):
                others = list(raw[f])
            overlay(im, r, others, sc, qox, qoy)
            tiles.append(im)
            lab = f"f{f} {f / float(info['fps']):.2f}s {r['src'] if r else ''}"
            if r and r["src"] == "det":
                lab += f" {r['score']:.2f}"
            labels.append(lab)
        rrio.tile_sheet(tiles, labels, cols=a.qa_cols, out_path=qa_path, tile_w=260, max_bytes=a.max_bytes,
                        title=f"faces {name} {CW}x{CH} pick={a.pick} det {cnt['det']} interp {cnt['interp']} "
                              f"hold {cnt['hold']} none {cnt['none']}")
    print(f"{name}: {n} frames (f{f_start}-{f_end}), processed {n_proc} (every {every}), face found in "
          f"{n_hit}/{n_proc}" + (f", >1 face in {multi}" if multi else "") +
          f"; track det {cnt['det']} interp {cnt['interp']} hold {cnt['hold']} none {cnt['none']}; "
          f"{len(segments)} segment(s); median eye distance {meta['eye_dist_px_median']} px; "
          f"detect {t_det:.1f}s")
    if jumps:
        print(f"   jumps (new face / hard cut) between frames: {jumps}")
    print(f"   {out_path}\n   {meta_path}\n   {raw_path}" + (f"\n   QA sheet {qa_path}" if a.qa_tiles > 0 else ""))
    return 0


def cmd_detect(a):
    if not os.path.exists(a.SRC):
        raise UsageError(f"not found: {a.SRC}")
    info = rrio.probe(a.SRC)
    model_path = ensure_model(a.model)
    det = YuNet(model_path, a.score, a.nms, a.threads)
    idx = [int(v) for v in (a.frames or "0").split(",") if v.strip()]
    imgs = [rrio.read_image(a.SRC)] if info.get("is_image") else rrio.read_frames_at(a.SRC, idx, info=info)
    if info.get("is_image"):
        idx = [0]
    res, tiles, labels = [], [], []
    for f, im in zip(idx, imgs):
        d = det.detect(im)
        res.append({"f": f, "faces": [{"box": [round(float(v), 1) for v in r[:4]], "score": round(float(r[14]), 3),
                                       "eyes": [[round(float(r[4]), 1), round(float(r[5]), 1)],
                                                [round(float(r[6]), 1), round(float(r[7]), 1)]],
                                       "nose": [round(float(r[8]), 1), round(float(r[9]), 1)],
                                       "mouth": [[round(float(r[10]), 1), round(float(r[11]), 1)],
                                                 [round(float(r[12]), 1), round(float(r[13]), 1)]]} for r in d]})
        if a.overlay:
            tw_ = min(im.shape[1], 640)
            sc = tw_ / im.shape[1]
            small = rrio.resize(im, tw_, max(1, int(round(im.shape[0] * sc))))
            for fc in res[-1]["faces"]:
                overlay(small, dict(fc, src="det"), [], sc)
            tiles.append(small)
            labels.append(f"f{f} {len(d)} face(s)")
    out = {"src": a.SRC, "w": info["w"], "h": info["h"], "input_hw": det.input_hw, "frames": res}
    txt = json.dumps(out)
    if a.out:
        rrio.save_json(a.out, out)
        print(f"wrote {a.out}")
    else:
        print(txt)
    if a.overlay:
        rrio.tile_sheet(tiles, labels, cols=min(3, len(tiles)), out_path=a.overlay, tile_w=520)
        print(f"overlay {a.overlay}", file=sys.stderr)
    return 0


def convert_chrome(arr, W, H):
    """Chrome FaceDetector per-frame list ({x,y,w,eye,mouth,nose} normalised, or null) -> our schema."""
    rows = []
    r1 = lambda v: round(float(v), 1)  # noqa: E731
    for f, e in enumerate(arr):
        if not e:
            rows.append({"f": f, "box": None, "score": 0.0, "eyes": None, "nose": None, "mouth": None, "src": "none"})
            continue
        bw = e["w"] * W
        bh = bw  # Chrome's box height was not stored; macOS Vision boxes are ~square
        cx, cy = e["x"] * W, e["y"] * H
        eyes = None
        if e.get("eye") and len(e["eye"]) == 2:
            pts = sorted(([p[0] * W, p[1] * H] for p in e["eye"]), key=lambda p: p[0])
            eyes = [[r1(p[0]), r1(p[1])] for p in pts]
        nose = [r1(e["nose"][0] * W), r1(e["nose"][1] * H)] if e.get("nose") else None
        mouth = None
        if e.get("mouth"):
            m = [r1(e["mouth"][0] * W), r1(e["mouth"][1] * H)]
            mouth = [m, list(m)]
        rows.append({"f": f, "box": [r1(cx - bw / 2), r1(cy - bh / 2), r1(bw), r1(bh)], "score": 1.0,
                     "eyes": eyes, "nose": nose, "mouth": mouth, "src": "det"})
    return rows


def cmd_convert_chrome(a):
    arr = rrio.load_json(a.IN)
    if isinstance(arr, dict) and "frames" in arr:
        arr = arr["frames"]
    if not isinstance(arr, list):
        raise UsageError("expected a JSON list (one entry or null per frame)")
    if a.clip:
        info = rrio.probe(a.clip)
        W, H = info["w"], info["h"]
    elif a.w and a.h:
        W, H = a.w, a.h
    else:
        raise UsageError("give --clip PATH or --w W --h H (the size the normalised coords refer to)")
    rows = convert_chrome(arr, W, H)
    rrio.save_json(a.out, rows, indent=None)
    n_ok = sum(1 for r in rows if r["box"])
    print(f"converted {len(rows)} frames ({n_ok} with a face) at {W}x{H} -> {a.out}")
    if a.meta:
        mp = os.path.splitext(a.out)[0] + ".meta.json"
        rrio.save_json(mp, {"src": a.IN, "w": W, "h": H, "frames": len(rows), "with_face": n_ok,
                            "source": "Chrome FaceDetector (Shape Detection API, macOS Vision)",
                            "notes": ["box height assumed = width (not stored by the source)",
                                      "mouth = centre point repeated twice (Chrome gives no corners)",
                                      "eyes sorted image-left first; score 1.0 = detected (no score)"]})
        print(f"   meta {mp}")
    return 0


def cmd_fetch_model(a):
    p = ensure_model(a.model, a.W)
    print(f"{p} ({os.path.getsize(p)} bytes, sha256 {_sha256(p)[:16]}...)")
    return 0


def build_parser():
    ap = argparse.ArgumentParser(prog=PROG, description="YuNet (onnxruntime) face boxes + landmarks per frame, "
                                 "picked, gap-filled and smoothed for face-anchored graphics.",
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p):
        p.add_argument("--model", help="YuNet onnx path (default: cached download)")
        p.add_argument("--score", type=float, default=0.6, help="detection score threshold (default 0.6)")
        p.add_argument("--nms", type=float, default=0.3, help="NMS IoU threshold (default 0.3)")
        p.add_argument("--threads", type=int, help="onnxruntime intra-op threads (default min(8, cpus))")

    p = sub.add_parser("track", help="per-frame face track of a clip -> W/faces/<name>.json")
    p.add_argument("W")
    p.add_argument("--clip", required=True)
    p.add_argument("--name", help="output name (default clip basename)")
    p.add_argument("--every", type=int, default=1, help="detect every Nth frame, interpolate between (default 1)")
    p.add_argument("--start", type=int, default=0)
    p.add_argument("--count", type=int)
    p.add_argument("--pick", default="track", choices=["track", "largest", "left", "center", "right"],
                   help="track (default: largest first, then continuity) | largest | left | center | right "
                        "(left/center/right among faces >= 25%% of the largest)")
    p.add_argument("--seed", help="x,y (px or fractions) of the hero's face to start the track from")
    p.add_argument("--reacquire", type=int, default=3,
                   help="track: processed frames without a match before re-acquiring the largest face")
    p.add_argument("--sigma", type=float, default=1.5, help="gaussian smoothing of positions, frames (0 = off)")
    p.add_argument("--sigma-size", type=float, default=2.5, help="gaussian smoothing of box size, frames")
    p.add_argument("--max-gap", type=int, default=12, help="fill gaps up to N frames (interp/hold)")
    p.add_argument("--cuts", help="frame indices where a new shot starts (no smoothing/interp across)")
    p.add_argument("--crop", help="x,y,w,h: detect inside this region only (coords stay clip pixels)")
    p.add_argument("--det-w", type=int, default=640, help="detection size for dynamic-shape models")
    p.add_argument("--from-raw", action="store_true", help="re-pick/fill/smooth from <name>.raw.json, no detection")
    p.add_argument("--qa-tiles", type=int, default=24, help="tiles on the QA sheet (0 = none)")
    p.add_argument("--qa-cols", type=int, default=6)
    p.add_argument("--max-bytes", type=int, default=500_000)
    common(p)
    p.set_defaults(fn=cmd_track)

    p = sub.add_parser("detect", help="raw detections on an image or video frames (JSON)")
    p.add_argument("SRC")
    p.add_argument("--frames", help="frame indices for a video (default 0)")
    p.add_argument("--out", help="write JSON here instead of stdout")
    p.add_argument("--overlay", help="also write an overlay sheet (.jpg)")
    common(p)
    p.set_defaults(fn=cmd_detect)

    p = sub.add_parser("convert-chrome", help="Chrome FaceDetector JSON (Katana/Yaong) -> faces schema")
    p.add_argument("IN")
    p.add_argument("--out", required=True)
    p.add_argument("--clip", help="clip whose size the normalised coords refer to")
    p.add_argument("--w", type=int)
    p.add_argument("--h", type=int)
    p.add_argument("--meta", action="store_true", help="also write <out>.meta.json")
    p.set_defaults(fn=cmd_convert_chrome)

    p = sub.add_parser("fetch-model", help="download + verify the YuNet model into the cache")
    p.add_argument("--model")
    p.add_argument("--W", help="workspace (W/.cache is a fallback cache dir)")
    p.set_defaults(fn=cmd_fetch_model)
    return ap


def main(argv=None):
    a = build_parser().parse_args(argv)
    try:
        return a.fn(a)
    except (UsageError, FileNotFoundError, ValueError, IndexError, KeyError) as e:
        print(f"{PROG}: error: {e}", file=sys.stderr)
        return 1
    except RuntimeError as e:
        print(f"{PROG}: error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
