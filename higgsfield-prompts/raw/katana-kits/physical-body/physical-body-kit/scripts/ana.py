"""ana.py - per-frame analysis without Chrome's FaceDetector (Linux hosts such as the Higgsfield sandbox).

Same output as engine/ana.html, frame for frame, from the 480 px analysis frames (ffmpeg -> raw RGB):
  f   faces (YuNet ONNX via onnxruntime, up to 3, largest first): bb [x,y,w,h], eyes [[x,y],[x,y]] sorted by x,
      mouth [x,y] (mean of the two mouth corners), all in analysis px
  y   mean luma, p5 / p95, sh sharpness (gradient energy), m motion (mean abs RGB diff vs the previous frame)
  hv / hx / hy  the brightest 5x5 box of the 160 px luma, hl fraction of pixels brighter than 0.88
Needs numpy + onnxruntime and the model file template/models/face_detection_yunet_2023mar.onnx (pb.py assets).
"""
import math
import subprocess

import numpy as np

MODEL_REL = 'template/models/face_detection_yunet_2023mar.onnx'
NET = 640                       # the 2023mar export has a fixed 640x640 input
SCORE, NMS_IOU, TOPK = 0.7, 0.3, 3


class YuNet:
    def __init__(self, path, threads=4):
        import onnxruntime as ort
        so = ort.SessionOptions()
        so.intra_op_num_threads = threads
        so.inter_op_num_threads = 1
        self.sess = ort.InferenceSession(path, sess_options=so, providers=['CPUExecutionProvider'])
        self.inp = self.sess.get_inputs()[0].name
        self.names = [o.name for o in self.sess.get_outputs()]

    def detect(self, rgb):
        """rgb uint8 HxWx3 -> [{bb, eyes, mouth, score}] in rgb px"""
        h, w = rgb.shape[:2]
        s = NET / float(max(w, h))
        nw, nh = max(1, int(round(w * s))), max(1, int(round(h * s)))
        img = resize(rgb, nw, nh)
        canvas = np.zeros((NET, NET, 3), np.float32)
        canvas[:nh, :nw] = img[..., ::-1]                         # BGR, 0..255, no normalisation
        out = dict(zip(self.names, self.sess.run(None, {self.inp: canvas.transpose(2, 0, 1)[None]})))
        boxes, scores, kps = [], [], []
        for stride in (8, 16, 32):
            cols = NET // stride
            cls = np.clip(out['cls_%d' % stride][0, :, 0], 0, 1)
            obj = np.clip(out['obj_%d' % stride][0, :, 0], 0, 1)
            sc = np.sqrt(cls * obj)
            idx = np.nonzero(sc > SCORE)[0]
            if not len(idx):
                continue
            r, c = (idx // cols).astype(np.float32), (idx % cols).astype(np.float32)
            bb = out['bbox_%d' % stride][0, idx]
            cx, cy = (c + bb[:, 0]) * stride, (r + bb[:, 1]) * stride
            bw, bh = np.exp(bb[:, 2]) * stride, np.exp(bb[:, 3]) * stride
            boxes.append(np.stack([cx - bw / 2, cy - bh / 2, bw, bh], 1))
            k = out['kps_%d' % stride][0, idx].reshape(-1, 5, 2)
            kps.append(np.stack([(k[:, :, 0] + c[:, None]) * stride, (k[:, :, 1] + r[:, None]) * stride], 2))
            scores.append(sc[idx])
        if not boxes:
            return []
        boxes, scores, kps = np.concatenate(boxes), np.concatenate(scores), np.concatenate(kps)
        keep = nms(boxes, scores, NMS_IOU)
        faces = []
        for i in keep:
            x, y, bw, bh = boxes[i] / s
            k = kps[i] / s
            eyes = sorted([[float(k[0, 0]), float(k[0, 1])], [float(k[1, 0]), float(k[1, 1])]])
            mouth = [float((k[3, 0] + k[4, 0]) / 2), float((k[3, 1] + k[4, 1]) / 2)]
            # calibrated to Chrome's FaceDetector box (what the scorer's framing targets assume): a square of 1.07 x the
            # YuNet width around the YuNet centre (fit on 372 matched frames of the same clip; width is the stable cue)
            side = 1.07 * float(bw)
            ccx, ccy = float(x + bw / 2), float(y + bh / 2) + 0.012 * float(bh)
            x0, y0 = max(0.0, ccx - side / 2), max(0.0, ccy - side / 2)
            x1, y1 = min(float(w), ccx + side / 2), min(float(h), ccy + side / 2)
            if x1 - x0 < 4 or y1 - y0 < 4:
                continue
            faces.append({'bb': [round(x0, 1), round(y0, 1), round(x1 - x0, 1), round(y1 - y0, 1)],
                          'eyes': [[round(v, 1) for v in e] for e in eyes],
                          'mouth': [round(v, 1) for v in mouth], 'score': round(float(scores[i]), 3)})
        faces.sort(key=lambda f: -f['bb'][2] * f['bb'][3])
        return faces[:TOPK]


def nms(boxes, scores, thr):
    order = np.argsort(-scores)
    keep = []
    while len(order):
        i = order[0]
        keep.append(int(i))
        if len(order) == 1:
            break
        rest = order[1:]
        x0 = np.maximum(boxes[i, 0], boxes[rest, 0])
        y0 = np.maximum(boxes[i, 1], boxes[rest, 1])
        x1 = np.minimum(boxes[i, 0] + boxes[i, 2], boxes[rest, 0] + boxes[rest, 2])
        y1 = np.minimum(boxes[i, 1] + boxes[i, 3], boxes[rest, 1] + boxes[rest, 3])
        inter = np.clip(x1 - x0, 0, None) * np.clip(y1 - y0, 0, None)
        union = boxes[i, 2] * boxes[i, 3] + boxes[rest, 2] * boxes[rest, 3] - inter
        order = rest[inter / np.maximum(union, 1e-6) <= thr]
        if len(keep) >= 10:
            break
    return keep


def resize(rgb, nw, nh):
    """bilinear resize without OpenCV (separable index interpolation)"""
    h, w = rgb.shape[:2]
    if (nw, nh) == (w, h):
        return rgb.astype(np.float32)
    ys = (np.arange(nh) + 0.5) * h / nh - 0.5
    xs = (np.arange(nw) + 0.5) * w / nw - 0.5
    y0 = np.clip(np.floor(ys).astype(int), 0, h - 1)
    x0 = np.clip(np.floor(xs).astype(int), 0, w - 1)
    y1, x1 = np.clip(y0 + 1, 0, h - 1), np.clip(x0 + 1, 0, w - 1)
    wy = np.clip(ys - y0, 0, 1)[:, None, None]
    wx = np.clip(xs - x0, 0, 1)[None, :, None]
    a = rgb.astype(np.float32)
    top = a[y0][:, x0] * (1 - wx) + a[y0][:, x1] * wx
    bot = a[y1][:, x0] * (1 - wx) + a[y1][:, x1] * wx
    return top * (1 - wy) + bot * wy


def stats(rgb, prev160):
    """luma / sharpness / motion / bright-spot stats on a 160 px version (3x3 block mean of the 480 px frame)"""
    h, w = rgb.shape[:2]
    rh, rw = h // 3, w // 3
    small = rgb[:rh * 3, :rw * 3].astype(np.float32).reshape(rh, 3, rw, 3, 3).mean((1, 3))
    Y = (small[..., 0] * 0.2126 + small[..., 1] * 0.7152 + small[..., 2] * 0.0722) / 255.0
    p5, p95 = np.percentile(Y, [5, 95])
    g = Y[1:rh - 1:2, 1:rw - 1:2]
    ge = (np.abs(Y[1:rh - 1:2, 2:rw:2][:g.shape[0], :g.shape[1]] - Y[1:rh - 1:2, 0:rw - 2:2][:g.shape[0], :g.shape[1]])
          + np.abs(Y[2:rh:2, 1:rw - 1:2][:g.shape[0], :g.shape[1]] - Y[0:rh - 2:2, 1:rw - 1:2][:g.shape[0], :g.shape[1]]))
    mo = float(np.abs(small - prev160).mean() / 255.0) if prev160 is not None and prev160.shape == small.shape else 0.0
    ii = np.pad(Y, ((1, 0), (1, 0))).cumsum(0).cumsum(1)
    box = ii[5:, 5:] - ii[:-5, 5:] - ii[5:, :-5] + ii[:-5, :-5]          # 5x5 sums, top-left anchored
    inner = box[2:rh - 6, 2:rw - 6]                                      # centres 4 .. rh-5 like ana.html
    if inner.size:
        k = int(np.argmax(inner))
        hy, hx = divmod(k, inner.shape[1])
        hv, hy, hx = float(inner[hy, hx]) / 25.0, hy + 4, hx + 4
    else:
        hv, hy, hx = float(Y.max()), rh // 2, rw // 2
    r4 = lambda v: round(float(v), 4)
    return small, {'y': r4(Y.mean()), 'p5': r4(p5), 'p95': r4(p95), 'sh': r4(ge.mean() if ge.size else 0.0), 'm': r4(mo),
                   'hv': r4(hv), 'hx': round((hx + 0.5) * 3.0, 1), 'hy': round((hy + 0.5) * 3.0, 1),
                   'hl': r4((Y > 0.88).mean())}


def analyze(video, ffmpeg, ffprobe, aw, model, n_expected=None, threads=4, progress=None):
    """-> {'w': aw, 'h': ah, 'frames': [...]} for every frame of `video` at analysis width aw"""
    probe = subprocess.run([ffprobe, '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                            'stream=width,height', '-of', 'csv=p=0', video], capture_output=True, text=True)
    w, h = [int(v) for v in probe.stdout.strip().split(',')[:2]]
    ah = int(math.ceil(aw * h / float(w) / 2.0)) * 2
    det = YuNet(model, threads)
    p = subprocess.Popen([ffmpeg, '-nostdin', '-v', 'error', '-i', video, '-vf', 'scale=%d:%d:flags=area' % (aw, ah),
                          '-pix_fmt', 'rgb24', '-f', 'rawvideo', '-'], stdout=subprocess.PIPE)
    size = aw * ah * 3
    frames, prev = [], None
    try:
        while True:
            buf = p.stdout.read(size)
            if len(buf) < size:
                break
            rgb = np.frombuffer(buf, np.uint8).reshape(ah, aw, 3)
            prev, st = stats(rgb, prev)
            st['f'] = [{k: v for k, v in f.items() if k != 'score'} for f in det.detect(rgb)]
            frames.append(st)
            if progress and len(frames) % 60 == 0:
                progress(len(frames), n_expected)
    finally:
        p.stdout.close()
        p.wait()
    return {'w': aw, 'h': ah, 'frames': frames}
