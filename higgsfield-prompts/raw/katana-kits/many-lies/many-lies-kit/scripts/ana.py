#!/usr/bin/env python3
"""ana.py - per-frame analysis of web/ana/<clip>/NNNNN.jpg without a browser (numpy + Pillow + onnxruntime).

Same records as engine/ana.html (which needs Chrome's FaceDetector, macOS only), for hosts with Python
packages but no FaceDetector, e.g. the Higgsfield sandbox (Linux, Playwright Chromium):
  f   faces, largest first (at most 3): bb [x, y, w, h], eyes [[x, y], [x, y]] sorted by x, mouth [x, y]  (ana px),
      e   identity embedding (SFace, 128-d unit vector) from the aligned face in the full-size source frame, when
          the SFace model is given; else d = a coarse appearance descriptor (head + hair colours)
  y   mean luma, p5 / p95, sh sharpness (gradient energy), m motion (mean abs RGB diff vs the previous frame)
  wm  fraction of saturated warm pixels, we the same inside the eye boxes, wo warm pixels outside them
Faces come from YuNet (OpenCV Zoo face_detection_yunet_2023mar.onnx, MIT licence), decoded here in numpy; identity
embeddings from SFace (OpenCV Zoo face_recognition_sface_2021dec.onnx, Apache 2.0) on 5-point aligned 112x112 crops.

usage: python3 ana.py <frames_dir> <a> <b> <yunet.onnx> <out.json> [threads] [<src_frames_dir> <sface.onnx>]
       (frames a..b-1, 0-based; src frames = the same frames at full working size, for the embeddings)
"""
import json
import os
import sys

import numpy as np
from PIL import Image

RW = 160                                   # stats raster width (as ana.html)
IN = 640                                   # YuNet input size (fixed in the 2023mar model)
SCORE_MIN, NMS_IOU, MAX_FACES = 0.7, 0.3, 3


def r4(v):
    return round(float(v), 4)


class YuNet:
    def __init__(self, path, threads=1):
        import onnxruntime as ort
        so = ort.SessionOptions()
        so.intra_op_num_threads = max(1, int(threads))
        so.inter_op_num_threads = 1
        so.log_severity_level = 3
        self.s = ort.InferenceSession(path, sess_options=so, providers=['CPUExecutionProvider'])
        self.inp = self.s.get_inputs()[0].name
        self.names = [o.name for o in self.s.get_outputs()]
        self.grid = {}
        for st in (8, 16, 32):
            n = IN // st
            r, c = np.divmod(np.arange(n * n), n)
            self.grid[st] = (c.astype(np.float32), r.astype(np.float32))

    def detect(self, rgb):
        """rgb uint8 HxWx3 -> [(score, x, y, w, h, kps[5x2])] in the image's px"""
        h, w = rgb.shape[:2]
        sc = IN / float(max(w, h))
        nw, nh = max(1, int(round(w * sc))), max(1, int(round(h * sc)))
        im = np.asarray(Image.fromarray(rgb).resize((nw, nh), Image.BILINEAR), np.float32)
        pad = np.zeros((IN, IN, 3), np.float32)
        pad[:nh, :nw] = im[..., ::-1]                                      # RGB -> BGR, 0..255
        out = dict(zip(self.names, self.s.run(None, {self.inp: pad.transpose(2, 0, 1)[None]})))
        boxes, scores, kpss = [], [], []
        for st in (8, 16, 32):
            cls, obj = out['cls_%d' % st][0, :, 0], out['obj_%d' % st][0, :, 0]
            score = np.sqrt(np.clip(cls, 0, 1) * np.clip(obj, 0, 1))
            keep = score >= SCORE_MIN
            if not keep.any():
                continue
            gc, gr = self.grid[st][0][keep], self.grid[st][1][keep]
            bb, kp = out['bbox_%d' % st][0][keep], out['kps_%d' % st][0][keep]
            cx, cy = (gc + bb[:, 0]) * st, (gr + bb[:, 1]) * st
            bw, bh = np.exp(bb[:, 2]) * st, np.exp(bb[:, 3]) * st
            boxes.append(np.stack([cx - bw / 2, cy - bh / 2, bw, bh], 1))
            k = kp.reshape(-1, 5, 2).copy()
            k[:, :, 0] = (k[:, :, 0] + gc[:, None]) * st
            k[:, :, 1] = (k[:, :, 1] + gr[:, None]) * st
            kpss.append(k)
            scores.append(score[keep])
        if not boxes:
            return []
        boxes, scores, kpss = np.concatenate(boxes), np.concatenate(scores), np.concatenate(kpss)
        order, keep = np.argsort(-scores), []
        while order.size and len(keep) < MAX_FACES * 3:
            i = order[0]
            keep.append(i)
            x1 = np.maximum(boxes[i, 0], boxes[order[1:], 0])
            y1 = np.maximum(boxes[i, 1], boxes[order[1:], 1])
            x2 = np.minimum(boxes[i, 0] + boxes[i, 2], boxes[order[1:], 0] + boxes[order[1:], 2])
            y2 = np.minimum(boxes[i, 1] + boxes[i, 3], boxes[order[1:], 1] + boxes[order[1:], 3])
            inter = np.clip(x2 - x1, 0, None) * np.clip(y2 - y1, 0, None)
            iou = inter / (boxes[i, 2] * boxes[i, 3] + boxes[order[1:], 2] * boxes[order[1:], 3] - inter + 1e-6)
            order = order[1:][iou <= NMS_IOU]
        res = []
        for i in keep:
            x, y, bw, bh = boxes[i] / sc
            if x + bw <= 0 or y + bh <= 0 or x >= w or y >= h:
                continue
            res.append((float(scores[i]), x, y, bw, bh, kpss[i] / sc))
        return res


def descriptor(rgb, x, y, w, h):
    """unit vector: 3x3 mean RGB of the head box (with hair, x 1.5 / y 1.6) + saturation-weighted 12-bin hue histogram.
    Cheap identity cue: separates people by hair / skin / clothing colour, not a face recogniser."""
    H, W = rgb.shape[:2]
    x0, x1 = int(max(0, x - 0.25 * w)), int(min(W, x + 1.25 * w))
    y0, y1 = int(max(0, y - 0.45 * h)), int(min(H, y + 1.15 * h))
    if x1 - x0 < 4 or y1 - y0 < 4:
        return None
    c = np.asarray(Image.fromarray(rgb[y0:y1, x0:x1]).resize((12, 12), Image.BILINEAR), np.float32) / 255.0
    grid = c.reshape(3, 4, 3, 4, 3).mean(axis=(1, 3)).ravel()                       # 3x3 cells x RGB
    v, mn = c.max(-1), c.min(-1)
    df = v - mn
    sat = np.where(v > 0, df / np.maximum(v, 1e-6), 0)
    R, G, B = c[..., 0], c[..., 1], c[..., 2]
    hue = np.where(v == R, 60 * (G - B) / np.maximum(df, 1e-6),
                   np.where(v == G, 120 + 60 * (B - R) / np.maximum(df, 1e-6), 240 + 60 * (R - G) / np.maximum(df, 1e-6)))
    hue = np.mod(hue, 360)
    wgt = sat * (v > 0.12)
    hist = np.bincount(np.minimum(11, (hue / 30).astype(np.int32)).ravel(), weights=wgt.ravel(), minlength=12)
    hist = hist / max(1e-6, hist.sum()) * min(1.0, wgt.mean() * 4)                   # grey heads: weak hue vote
    vec = np.concatenate([grid - grid.mean(), hist * 1.5, [c.mean() * 0.5]])
    n = float(np.linalg.norm(vec))
    return [round(float(t), 3) for t in vec / n] if n > 1e-6 else None


def faces_of(det, rgb=None):
    out = []
    for score, x, y, w, h, k in sorted(det, key=lambda d: -(d[3] * d[4]))[:MAX_FACES]:
        eyes = sorted([[round(float(k[0, 0]), 1), round(float(k[0, 1]), 1)], [round(float(k[1, 0]), 1), round(float(k[1, 1]), 1)]])
        mouth = [round(float(k[3, 0] + k[4, 0]) / 2, 1), round(float(k[3, 1] + k[4, 1]) / 2, 1)]
        rec = {'bb': [round(float(v), 1) for v in (x, y, w, h)], 'eyes': eyes, 'mouth': mouth, 'score': round(score, 3),
               '_kps': k}
        if rgb is not None:
            d = descriptor(rgb, x, y, w, h)
            if d:
                rec['d'] = d
        out.append(rec)
    return out


DST5 = np.array([[38.2946, 51.6963], [73.5318, 51.5014], [56.0252, 71.7366], [41.5493, 92.3655], [70.7299, 92.2041]],
                np.float64)                          # SFace / ArcFace 112x112 landmark template (image-left eye first)


def similarity(src, dst):
    """least-squares similarity transform (Umeyama, no reflection): returns 2x3 matrix mapping src -> dst."""
    ms, md = src.mean(0), dst.mean(0)
    sc, dc = src - ms, dst - md
    cov = dc.T @ sc / len(src)
    U, S, Vt = np.linalg.svd(cov)
    D = np.diag([1.0, np.sign(np.linalg.det(U @ Vt)) or 1.0])
    R = U @ D @ Vt
    scale = np.trace(np.diag(S) @ D) / max(1e-9, (sc ** 2).sum(1).mean())
    t = md - scale * R @ ms
    return np.hstack([scale * R, t[:, None]])


class SFace:
    def __init__(self, path, threads=1):
        import onnxruntime as ort
        so = ort.SessionOptions()
        so.intra_op_num_threads = max(1, int(threads))
        so.inter_op_num_threads = 1
        so.log_severity_level = 3
        self.s = ort.InferenceSession(path, sess_options=so, providers=['CPUExecutionProvider'])
        self.inp = self.s.get_inputs()[0].name

    def embed(self, img, kps):
        """img: PIL RGB full-size frame; kps: 5x2 landmarks in its px -> 128-d unit vector or None"""
        M = similarity(np.asarray(kps, np.float64), DST5)
        A, t = M[:, :2], M[:, 2]
        try:
            Ai = np.linalg.inv(A)
        except np.linalg.LinAlgError:
            return None
        ti = -Ai @ t
        crop = img.transform((112, 112), Image.AFFINE, (Ai[0, 0], Ai[0, 1], ti[0], Ai[1, 0], Ai[1, 1], ti[1]),
                             resample=Image.BILINEAR)
        x = np.asarray(crop, np.float32).transpose(2, 0, 1)[None]          # RGB 0..255, NCHW
        f = self.s.run(None, {self.inp: x})[0].reshape(-1)
        n = float(np.linalg.norm(f))
        return (f / n) if n > 1e-9 else None


def stats(rgb, faces, prev):
    h, w = rgb.shape[:2]
    rh = max(2, int(round(RW * h / float(w))))
    d = np.asarray(Image.fromarray(rgb).resize((RW, rh), Image.BILINEAR), np.float32) / 255.0
    R, G, B = d[..., 0], d[..., 1], d[..., 2]
    Y = R * 0.2126 + G * 0.7152 + B * 0.0722
    hist = np.bincount(np.minimum(255, (Y * 256).astype(np.int32)).ravel(), minlength=256)
    cum = np.cumsum(hist)
    n = Y.size

    def pct(q):
        return float(np.searchsorted(cum, q * (n - 1), side='right')) / 255.0
    v, mn = d.max(-1), d.min(-1)
    df = v - mn
    sat = np.where(v > 0, df / np.maximum(v, 1e-6), 0)
    hue = np.zeros_like(v)
    nz = df > 0
    rmax, gmax = nz & (v == R), nz & (v == G) & (v != R)
    bmax = nz & ~rmax & ~gmax
    hue[rmax] = 60 * (G - B)[rmax] / df[rmax]
    hue[gmax] = 120 + 60 * (B - R)[gmax] / df[gmax]
    hue[bmax] = 240 + 60 * (R - G)[bmax] / df[bmax]
    hue[hue < 0] += 360
    warm = (sat > 0.55) & (v > 0.25) & nz & ((hue >= 335) | (hue < 40))
    eye = np.zeros(Y.shape, bool)
    s = RW / float(w)
    yy, xx = np.mgrid[0:rh, 0:RW]
    for f in faces:
        r2 = f['bb'][2] * 0.14 * s
        for ex, ey in f.get('eyes') or []:
            eye |= (xx >= ex * s - r2) & (xx <= ex * s + r2) & (yy >= ey * s - r2) & (yy <= ey * s + r2)
    wm, we, wn = int(warm.sum()), int((warm & eye).sum()), int(eye.sum())
    ys, xs = np.arange(1, rh - 1, 2), np.arange(1, RW - 1, 2)          # every 2nd row/col, as ana.html
    ge = (np.abs(Y[np.ix_(ys, xs + 1)] - Y[np.ix_(ys, xs - 1)]).sum()
          + np.abs(Y[np.ix_(ys + 1, xs)] - Y[np.ix_(ys - 1, xs)]).sum())
    cnt = len(ys) * len(xs)
    mo = float(np.abs(d - prev).mean()) if prev is not None and prev.shape == d.shape else 0.0
    rec = {'f': faces, 'y': r4(Y.mean()), 'p5': r4(pct(0.05)), 'p95': r4(pct(0.95)), 'sh': r4(ge / max(1, cnt)),
           'm': r4(mo), 'wm': r4(wm / float(n)), 'we': r4(we / float(wn)) if wn else 0, 'wo': r4((wm - we) / float(n))}
    return rec, d


def load(fdir, i):
    try:
        return np.asarray(Image.open(os.path.join(fdir, '%05d.jpg' % i)).convert('RGB'))
    except (OSError, ValueError):
        return None


def main():
    fdir, a, b, model, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], sys.argv[5]
    threads = int(sys.argv[6]) if len(sys.argv) > 6 else 1
    sdir = sys.argv[7] if len(sys.argv) > 8 else None
    rec_model = SFace(sys.argv[8], threads) if len(sys.argv) > 8 and os.path.isfile(sys.argv[8]) else None
    det = YuNet(model, threads)
    frames, found, size = [], 0, None
    prev = None
    if a > 0:                                          # motion of frame a needs frame a-1
        pr = load(fdir, a - 1)
        if pr is not None:
            _, prev = stats(pr, [], None)
    for i in range(a, b):
        rgb = load(fdir, i)
        if rgb is None:
            frames.append(None)
            prev = None
            continue
        size = size or [rgb.shape[1], rgb.shape[0]]
        faces = faces_of(det.detect(rgb), rgb)
        if faces and rec_model is not None and sdir:
            try:
                big = Image.open(os.path.join(sdir, '%05d.jpg' % i)).convert('RGB')
                k = big.size[0] / float(rgb.shape[1])
                for f in faces:
                    if f['bb'][3] * k >= 36:                 # too small faces give noise, not identity
                        e = rec_model.embed(big, np.asarray(f['_kps']) * k)
                        if e is not None:
                            f['e'] = [round(float(t), 3) for t in e]
                            f.pop('d', None)
            except (OSError, ValueError):
                pass
        for f in faces:
            f.pop('_kps', None)
        found += bool(faces)
        rec, prev = stats(rgb, faces, prev)
        frames.append(rec)
    tmp = out + '.part'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump({'w': size[0] if size else 0, 'h': size[1] if size else 0, 'frames': frames,
                   'method': 'yunet+sface' if rec_model else 'yunet'}, f)
    os.replace(tmp, out)
    print('ana done %d-%d %d/%d' % (a, b, found, b - a), flush=True)


if __name__ == '__main__':
    main()
