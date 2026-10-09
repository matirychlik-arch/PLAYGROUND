"""analyze.py - per-frame analysis of a job's sources (venv python; run via `pc.py prep`).

usage: analyze.py <job>

For every source in <job>/src (v0.mp4 [, v1.mp4]) writes <job>/features.json:
  cuts     hard cuts (s), from glow.media.detect_cuts on every frame
  samples  every 1/RATE s: faces (YuNet, source px [x, y, w, h, score, person id, face sharpness], largest
           first), person box (u2net human
           matte at 320 px: [x0, y0, x1, y1, area fraction]), sharpness (Laplacian variance, 480 px luma),
           motion (mean abs luma diff to the previous sample), luma
  people   identities (SFace embeddings clustered over all sources), most screen presence first:
           [{id, samples, presence, first_t}]; a face's id is its index here
"""
import json
import os
import sys

import cv2
import numpy as np

SK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SK)
from glow import media  # noqa: E402

RATE = 8.0
SAME = 0.40        # SFace cosine similarity: same person (OpenCV's reference threshold is 0.363)
MODELS = os.environ.get('GLOW_MODELS', '')
ANA_W = 640


def person_box(seg, rgb):
    a = seg._run(rgb)                        # raw human matte, same size as rgb
    m = (a > 0.5).astype(np.uint8)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(m, 8)
    if n < 2:
        return None
    i = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    x, y, w, h, area = stats[i]
    if area < 0.01 * m.size:
        return None
    return [int(x), int(y), int(x + w), int(y + h), float(area) / m.size]


def analyze(path, rec, embs):
    from glow.seg import Segmenter
    info = media.probe(path)
    sw, sh = info['width'], info['height']
    aw = ANA_W
    ah = int(round(aw * sh / sw / 2)) * 2
    k = sw / aw
    det = cv2.FaceDetectorYN.create(os.path.join(MODELS, 'face_detection_yunet_2023mar.onnx'), '', (aw, ah),
                                    0.75, 0.3, 50)
    seg = Segmenter('human')
    cuts, _, _ = media.detect_cuts(path)
    samples, prev = [], None
    for t, rgb in media.read_frames(path, fps=RATE, size=(aw, ah)):
        bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
        _, f = det.detect(bgr)
        faces = []
        if f is not None:
            for r in sorted(f.tolist(), key=lambda r: -r[2] * r[3] * r[-1])[:4]:
                x, y, w, h = (float(v) * k for v in r[:4])
                if w * h <= (0.025 * sh) ** 2:   # ignore specks (< 2.5 % of the frame height)
                    continue
                e = rec.feature(rec.alignCrop(bgr, np.array(r, np.float32)))[0]
                embs.append(e / max(1e-6, float(np.linalg.norm(e))))
                fx0, fy0 = max(0, int(r[0])), max(0, int(r[1]))
                patch = cv2.cvtColor(bgr[fy0:fy0 + int(r[3]), fx0:fx0 + int(r[2])], cv2.COLOR_BGR2GRAY)
                fsharp = float(cv2.Laplacian(cv2.resize(patch, (96, 96)), cv2.CV_32F).var()) if patch.size else 0.0
                faces.append([round(x, 1), round(y, 1), round(w, 1), round(h, 1), round(float(r[-1]), 3),
                              len(embs) - 1, round(fsharp, 1)])
        pb = person_box(seg, rgb)
        if pb:
            pb = [int(pb[0] * k), int(pb[1] * k), int(pb[2] * k), int(pb[3] * k), round(pb[4], 4)]
        g = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
        g4 = cv2.resize(g, (480, int(480 * ah / aw)), interpolation=cv2.INTER_AREA).astype(np.float32)
        sharp = float(cv2.Laplacian(g4, cv2.CV_32F).var())
        motion = 0.0 if prev is None else float(np.mean(np.abs(g4 - prev))) / 255
        prev = g4
        samples.append(dict(t=round(t, 4), faces=faces[:4], person=pb, sharp=round(sharp, 2),
                            motion=round(motion, 4), luma=round(float(g4.mean()) / 255, 4)))
    return dict(w=sw, h=sh, fps=info["fps"], dur=info["duration"], rate=RATE,
                cuts=[round(c, 4) for c in cuts], samples=samples)


def cluster(embs, sizes):
    """Greedy identity clusters, biggest faces first (they embed best). Returns a label per embedding."""
    order = sorted(range(len(embs)), key=lambda i: -sizes[i])
    cents, members, lab = [], [], [0] * len(embs)
    for i in order:
        best, bs = -1, SAME
        for c, m in enumerate(cents):
            s = float(np.dot(embs[i], m / max(1e-6, float(np.linalg.norm(m)))))
            if s > bs:
                best, bs = c, s
        if best < 0:
            cents.append(embs[i].copy())
            members.append(1)
            best = len(cents) - 1
        else:
            cents[best] += embs[i]
            members[best] += 1
        lab[i] = best
    return lab


def main():
    job = os.path.abspath(sys.argv[1])
    rec = cv2.FaceRecognizerSF.create(os.path.join(MODELS, 'face_recognition_sface_2021dec.onnx'), '')
    embs = []
    out = {}
    for name in sorted(os.listdir(os.path.join(job, 'src'))):
        if name.endswith('.mp4'):
            alias = name[:-4]
            out[alias] = analyze(os.path.join(job, 'src', name), rec, embs)
            out[alias]['path'] = f'src/{name}'
            s = out[alias]['samples']
            print(f'{alias}: {len(s)} samples, {len(out[alias]["cuts"])} cuts, '
                  f'faces in {sum(1 for x in s if x["faces"])}, person in {sum(1 for x in s if x["person"])}',
                  flush=True)
    sizes = [0.0] * len(embs)
    refs = []
    for alias, d in out.items():
        for s in d['samples']:
            for fc in s['faces']:
                sizes[fc[5]] = fc[3] / d['h']
                refs.append((alias, s['t'], fc))
    lab = cluster(embs, sizes)
    stats = {}
    for alias, t, fc in refs:
        st = stats.setdefault(lab[fc[5]], dict(samples=0, presence=0.0, first=(alias, t)))
        st['samples'] += 1
        st['presence'] += sizes[fc[5]] * fc[4]
    rank = sorted(stats, key=lambda c: -stats[c]['presence'])
    new = {c: i for i, c in enumerate(rank)}
    for alias, t, fc in refs:
        fc[5] = new[lab[fc[5]]]
    people = [dict(id=new[c], samples=stats[c]['samples'], presence=round(stats[c]['presence'], 2),
                   first=[stats[c]['first'][0], stats[c]['first'][1]]) for c in rank]
    print('people: ' + ', '.join(f'#{p["id"]} {p["samples"]} samples (first {p["first"][0]} {p["first"][1]:.1f}s)'
                                 for p in people[:5]))
    with open(os.path.join(job, 'features.json'), 'w') as f:
        json.dump({'sources': out, 'people': people}, f, separators=(',', ':'))


if __name__ == '__main__':
    main()
