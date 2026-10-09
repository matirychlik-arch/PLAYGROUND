"""Subject segmentation (cut-outs) with ONNX models from rembg's release set.

- isnet-general-use (1024x1024): best edges, works for people AND objects (plush, bows, boxes).
- u2net_human_seg (320x320): people only, faster.

API
    seg = Segmenter('isnet')            # or 'human'
    alpha = seg(rgb_uint8, box=None)     # float32 HxW in [0,1]
    box = (x0, y0, x1, y1) restricts the model to a crop (better detail for small subjects).
Masks are cached on disk by (source, time, box, model) so re-renders are free.
"""
import hashlib
import os

import cv2
import numpy as np

MODEL_DIR = os.environ.get('GLOW_MODELS', os.path.join(os.path.dirname(__file__), '..', 'assets', 'models'))
CACHE_DIR = os.environ.get('GLOW_MASK_CACHE', os.path.join(os.path.dirname(__file__), '..', 'cache', 'masks'))

_SPECS = {
    'isnet': ('isnet-general-use.onnx', 1024, (0.5, 0.5, 0.5), (1.0, 1.0, 1.0)),
    'human': ('u2net_human_seg.onnx', 320, (0.485, 0.456, 0.406), (0.229, 0.224, 0.225)),
}


class Segmenter:
    def __init__(self, kind='isnet'):
        self.fname, self.size, self.mean, self.std = _SPECS[kind]
        self.kind = kind
        self.sess = None            # loaded on the first cache miss: a render that only reads cached masks never
                                    # pays the ~1 GB per model

    def _load(self):
        import onnxruntime as ort
        opts = ort.SessionOptions()
        opts.intra_op_num_threads = int(os.environ.get('GLOW_THREADS', 0)) or max(1, os.cpu_count() or 1)
        self.sess = ort.InferenceSession(os.path.join(MODEL_DIR, self.fname), opts, providers=['CPUExecutionProvider'])
        self.inp = self.sess.get_inputs()[0].name

    def _run(self, rgb):
        if self.sess is None:
            self._load()
        h, w = rgb.shape[:2]
        x = cv2.resize(rgb, (self.size, self.size), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0
        if self.kind == 'human':
            x = x / max(1e-6, x.max())
        x = (x - np.array(self.mean, np.float32)) / np.array(self.std, np.float32)
        x = x.transpose(2, 0, 1)[None]
        y = self.sess.run(None, {self.inp: x})[0][0, 0]
        y = (y - y.min()) / max(1e-6, y.max() - y.min())
        return cv2.resize(y.astype(np.float32), (w, h), interpolation=cv2.INTER_LINEAR)

    def __call__(self, rgb, box=None, key=None):
        if key is not None:
            os.makedirs(CACHE_DIR, exist_ok=True)
            hid = hashlib.sha1(f'{self.kind}|{key}|{box}'.encode()).hexdigest()[:20]
            path = os.path.join(CACHE_DIR, hid + '.png')
            if os.path.exists(path):
                m = cv2.imread(path, cv2.IMREAD_UNCHANGED)
                if m is not None and m.shape[:2] == rgb.shape[:2]:
                    return m.astype(np.float32) / 255.0
        if box is None:
            a = self._run(rgb)
        else:
            x0, y0, x1, y1 = (int(v) for v in box)
            a = np.zeros(rgb.shape[:2], np.float32)
            a[y0:y1, x0:x1] = self._run(rgb[y0:y1, x0:x1])
        a = refine(a)
        if key is not None:   # atomic: parallel render chunks share the cache
            tmp = f'{path}.{os.getpid()}.png'
            cv2.imwrite(tmp, (a * 255).astype(np.uint8))
            os.replace(tmp, path)
        return a


def refine(a, lo=0.25, hi=0.75):
    """Contrast-stretch the soft mask and drop tiny islands, keeping hair wisps soft."""
    a = np.clip((a - lo) / (hi - lo), 0, 1)
    hard = (a > 0.5).astype(np.uint8)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(hard, 8)
    if n > 2:
        areas = stats[1:, cv2.CC_STAT_AREA]
        keep = np.zeros(n, bool)
        keep[1:] = areas >= max(400, 0.04 * areas.max())
        island = ~keep[lab] & (hard > 0)
        a[island] = 0
    return a.astype(np.float32)


def outline(alpha, px, feather=1.5):
    """Sticker outline: alpha of the subject grown by `px` pixels (rounded)."""
    k = max(1, int(px))
    hard = (alpha > 0.5).astype(np.uint8)
    ker = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * k + 1, 2 * k + 1))
    grown = cv2.dilate(hard, ker).astype(np.float32)
    if feather > 0:
        grown = cv2.GaussianBlur(grown, (0, 0), feather)
    return np.maximum(grown, alpha)
