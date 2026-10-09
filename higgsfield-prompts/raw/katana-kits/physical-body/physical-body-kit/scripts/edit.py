"""edit.py - template slots -> moments of the user's clip -> engine plan (python3 stdlib only).

The template (template/timeline.json) is the physical body edit (the Huntress overlay edit) with every piece of footage replaced by a SLOT:
  items{id: {slot, f0, n, off, speed, zr, aspect, dw, look, ...}}  a placement plays slot frames off + k*speed
  slots{name: {kind, group}}  kind decides what a good moment is and how it is framed:
    eyes     eye ECU (eye distance 45 % of the width)      face     close-up, face 50 % of the height
    profile  face turned away from the camera, 32 %        medium   person in the space, face ~22 %
    figure   whole body / back view (face <= 10 %)         hero     long shot with light and scale (B&W, lyrics)
    detail   no face: hands, objects (crop below the face) glow     the brightest small light source, zoomed
    glint    a highlight on an object, zoomed + bloom      action   strong motion
    run      long strong motion                            whip     the motion peak (fast pan / swing)
    wide     the space itself, few or small faces
  group: panels of one group (cascade, pops, finale tunnel) must differ from each other but may reuse moments of
  full-frame shots (recaps); full-frame shots keep GAP frames apart while the clip has room.
build() picks one window per slot (greedy by kind priority, inside one source shot when possible) and resolves every
item to a camera {cx, cy, z} in working-source px (z = 1 is the 16:9 cover crop), plus one crop box per slot that
pb.py cuts out of the clip with ffmpeg for the engine.
"""
import math

FPS = 30
OUT_W, OUT_H = 1920, 1080
FULL = OUT_W / float(OUT_H)
UPSCALE_MAX = 3.2                 # output px per source px at most (more turns to mush)
GAP = 15                          # frames kept between two full-frame picks while the clip has room
NEAR = 45                         # output frames: picks this close in the edit should not look alike
RELAX = 2.5                       # score a stricter uniqueness level may cost before the scorer relaxes it
PRIORITY = ['hero', 'eyes', 'run', 'profile', 'face', 'glow', 'whip', 'figure', 'medium', 'glint', 'action', 'detail',
            'wide']
FACE_FRAC = {'face': 0.50, 'profile': 0.32, 'medium': 0.22, 'figure': 0.09}
MOTION_PREF = {'eyes': 'low', 'face': 'low', 'profile': 'mid', 'medium': 'mid', 'figure': 'mid', 'hero': 'low',
               'detail': 'low', 'glow': 'any', 'glint': 'any', 'action': 'high', 'run': 'high', 'whip': 'peak',
               'wide': 'mid'}


def clamp(v, a, b):
    return a if v < a else b if v > b else v


def median(v):
    v = sorted(v)
    n = len(v)
    return None if not n else (v[n // 2] if n % 2 else 0.5 * (v[n // 2 - 1] + v[n // 2]))


def main_face(fr):
    return fr['f'][0] if fr.get('f') else None


def frontal(f):
    if not f or len(f.get('eyes') or []) < 2:
        return False
    (x0, y0), (x1, y1) = f['eyes'][0], f['eyes'][-1]
    ed = math.hypot(x1 - x0, y1 - y0) / max(1.0, f['bb'][2])
    yaw = ((x0 + x1) / 2.0 - (f['bb'][0] + f['bb'][2] / 2.0)) / max(1.0, f['bb'][2])
    return ed >= 0.28 and abs(yaw) <= 0.16


def eye_dist(f):
    if not f or len(f.get('eyes') or []) < 2:
        return None
    (x0, y0), (x1, y1) = f['eyes'][0], f['eyes'][-1]
    return math.hypot(x1 - x0, y1 - y0)


def crop_rect(W, H, cx, cy, z, aspect):
    """source rect (x, y, w, h) an item shows: height = cover height / z, the item's aspect, clamped into the source.
    engine/fx.js cropRect() is the same function."""
    hfull = min(H, W / FULL)
    ch = hfull / max(z, 1e-3)
    cw = ch * aspect
    if cw > W:
        cw = W
        ch = cw / aspect
    if ch > H:
        ch = H
        cw = ch * aspect
    x = clamp(cx - cw / 2.0, 0.0, W - cw)
    y = clamp(cy - ch / 2.0, 0.0, H - ch)
    return x, y, cw, ch


def smooth(p):
    p = clamp(p, 0.0, 1.0)
    return p * p * (3 - 2 * p)


class Clip:
    def __init__(self, feats):
        self.F = feats['frames']
        self.n = feats['n']
        self.W, self.H = feats['size']
        self.s0 = max(OUT_W / float(self.W), OUT_H / float(self.H))      # output px per source px at z = 1
        self.zmax = max(1.0, UPSCALE_MAX / self.s0)
        self.hfull = min(self.H, self.W / FULL)
        self.ana_sc = self.W / float(feats.get('ana_w') or self.W)
        self.shot_of = [0] * self.n
        self.shots = feats['shots']
        for s in self.shots:
            for i in range(s['a'], s['b']):
                self.shot_of[i] = s['i']
        sh = sorted(fr['sh'] for fr in self.F)
        self.sharp_ref = max(1e-4, sh[int(0.7 * (len(sh) - 1))])
        mo = sorted(fr['m'] for fr in self.F)
        self.mo50 = max(1e-4, mo[len(mo) // 2])

    def shot_span(self, i):
        s = self.shots[self.shot_of[i]]
        return s['a'], s['b']

    def fsize(self, f):
        return f['bb'][3] / self.hfull

    def bright(self, lo, hi):
        """the strongest bright spot of the window: (x, y) in source px, value, local contrast"""
        best = None
        for i in range(lo, hi):
            fr = self.F[i]
            if fr.get('hv') is None:
                continue
            c = fr['hv'] - fr['y']
            if best is None or c > best[3]:
                best = (fr['hx'] * self.ana_sc, fr['hy'] * self.ana_sc, fr['hv'], c)
        return best

    def cam(self, kind, lo, hi):
        faces = [main_face(self.F[i]) for i in range(lo, hi)]
        faces = [f for f in faces if f]
        if not faces and kind in ('eyes', 'face', 'profile', 'medium', 'figure'):
            near = [main_face(self.F[i]) for i in range(max(0, lo - 15), min(self.n, hi + 15))]
            faces = [f for f in near if f]
        W, H, s0 = self.W, self.H, self.s0
        cx, cy, z = W / 2.0, H / 2.0, 1.0
        k = lambda zz: OUT_H / (s0 * zz)                    # source px per output height at zoom zz
        if faces:
            fcx = median([f['bb'][0] + f['bb'][2] / 2.0 for f in faces])
            fcy = median([f['bb'][1] + f['bb'][3] / 2.0 for f in faces])
            fh = median([f['bb'][3] for f in faces])
            if kind == 'eyes':
                eds = [eye_dist(f) for f in faces if eye_dist(f)]
                if eds:
                    ed = median(eds)
                    ex = median([f['eyes'][0][0] for f in faces if eye_dist(f)])
                    ey = median([0.5 * (f['eyes'][0][1] + f['eyes'][-1][1]) for f in faces if eye_dist(f)])
                    z = 0.45 * OUT_W / (ed * s0)
                    cx = ex + 0.03 * OUT_W / (s0 * z)
                    cy = ey + 0.05 * k(z)
                else:
                    z = 0.95 * OUT_H / (fh * s0)
                    cx, cy = fcx, fcy - 0.08 * fh
            elif kind in FACE_FRAC:
                z = FACE_FRAC[kind] * OUT_H / (fh * s0)
                off = {'face': 0.04, 'profile': 0.06, 'medium': 0.17, 'figure': 0.28}[kind]
                cx, cy = fcx, fcy + off * k(max(z, 1.0))
            elif kind == 'detail':                            # hands / torso: 4 face heights tall, below the face
                z = clamp(self.hfull / (4.0 * fh), 1.5, self.zmax)
                cx, cy = fcx, fcy + 2.0 * fh
            elif kind in ('hero', 'action', 'run', 'whip'):
                z = 1.0 if kind == 'hero' else 1.05
                cx = fcx
            elif kind == 'wide':
                z = 1.0
        elif kind == 'detail':
            z = 1.6
        elif kind in ('eyes', 'face'):
            z = 1.5
        elif kind in ('action', 'run', 'whip'):
            z = 1.05
        if kind in ('glow', 'glint'):
            b = self.bright(lo, hi)
            z = 3.0 if kind == 'glow' else 2.6
            if b:
                zz = min(z, self.zmax)
                if kind == 'glow':
                    cx, cy = b[0] + 0.18 * OUT_W / (s0 * zz), b[1] + 0.08 * k(zz)
                else:
                    cx, cy = b[0], b[1]
        over = max(0.0, z - self.zmax)
        z = clamp(z, 1.0, self.zmax)
        hw, hh = OUT_W / 2.0 / (s0 * z), OUT_H / 2.0 / (s0 * z)
        cx, cy = clamp(cx, hw, W - hw), clamp(cy, hh, H - hh)
        return {'cx': round(cx, 1), 'cy': round(cy, 1), 'z': round(z, 4), 'over': round(over, 3)}

    def window_score(self, kind, lo, hi, cam):
        F = self.F[lo:hi]
        n = len(F)
        notes = []
        if any(fr.get('bad') for fr in F):
            return -99, ['unreadable frames']
        sharp = sum(fr['sh'] for fr in F) / n / self.sharp_ref
        dark = sum(1 for fr in F if fr['p95'] < 0.18) / float(n)
        dead = sum(1 for fr in F if fr['y'] < 0.04 and fr['p95'] < 0.25) / float(n)    # black / credits / fades
        blown = sum(1 for fr in F if fr['y'] > 0.72) / float(n)                         # white flashes
        mo = sum(fr['m'] for fr in F) / n
        faces = [main_face(fr) for fr in F]
        fpres = sum(1 for f in faces if f) / float(n)
        ffront = sum(1 for f in faces if frontal(f)) / float(n)
        fs = median([self.fsize(f) for f in faces if f]) or 0.0
        hw, hh = OUT_W / 2.0 / (self.s0 * cam['z']), OUT_H / 2.0 / (self.s0 * cam['z'])
        crop = (cam['cx'] - hw, cam['cy'] - hh, cam['cx'] + hw, cam['cy'] + hh)
        extra = 0
        for fr, f0 in zip(F, faces):
            for f in fr['f'][1:]:
                fx, fy = f['bb'][0] + f['bb'][2] / 2.0, f['bb'][1] + f['bb'][3] / 2.0
                if crop[0] < fx < crop[2] and crop[1] < fy < crop[3] and f0 and f['bb'][3] > 0.35 * f0['bb'][3]:
                    extra += 1
        extra /= float(n)
        s = 2.0 * min(1.3, sharp) - 3.0 * dark - 8.0 * dead - 3.0 * blown \
            - (2.5 if kind in ('eyes', 'face', 'profile') else 1.0) * extra \
            - (min(8.0, 1.5 * cam['over']) if kind == 'eyes' else min(3.0, 1.2 * cam['over']))
        if dead > 0.3:
            notes.append('black frames in the window')
        rel = mo / self.mo50
        pref = MOTION_PREF[kind]
        if pref == 'high':
            s += 1.2 * min(2.5, rel)
        elif pref == 'peak':
            s += 1.6 * min(4.0, max(fr['m'] for fr in F) / self.mo50)
        elif pref == 'low':
            s -= 0.8 * max(0.0, rel - 1.5)
        elif pref == 'mid':
            s -= 0.5 * abs(math.log(max(rel, 0.05)))
        if kind in ('eyes', 'face'):
            s += 3.0 * fpres + 2.5 * ffront
            if kind == 'eyes':
                s += 2.0 * sum(1 for f in faces if eye_dist(f)) / float(n)
            if fpres < 0.5:
                notes.append('face in %.0f%% of the window' % (100 * fpres))
        elif kind == 'profile':
            s += 2.0 * fpres + 1.5 * (fpres - ffront)
        elif kind == 'medium':
            s += 2.0 * fpres + 0.6 * ffront
        elif kind == 'figure':
            s += 1.5 * fpres - 2.0 * max(0.0, fs - 0.2) / 0.2 + 0.8 * (1.0 - fpres) * min(1.0, rel)
        elif kind == 'hero':
            hl = sum(fr.get('hl', 0) for fr in F) / n
            con = sum(fr['p95'] - fr['p5'] for fr in F) / n
            s += 6.0 * min(0.25, hl) + 2.0 * con + 1.0 * min(1.0, n / 40.0) - (1.5 if fs > 0.35 else 0.0)
        elif kind == 'detail':
            # hands / objects: a person nearby (the camera sits below the face), texture, contrast
            near = fpres > 0.3
            con = sum(fr['p95'] - fr['p5'] for fr in F) / n
            s += 0.6 * near + 0.5 * min(1.3, sharp) + 1.5 * con - 0.8 * ffront - (2.0 if fpres and fs < 0.05 else 0.0)
        elif kind in ('glow', 'glint'):
            b = self.bright(lo, hi)
            hl = sum(fr.get('hl', 0) for fr in F) / n               # a small light source, not a bright frame
            s += (5.0 if kind == 'glow' else 4.0) * (b[3] if b else 0.0) - 8.0 * max(0.0, hl - 0.04) \
                + (0.5 * (1.0 - fpres) if kind == 'glint' else 0.0)
        elif kind == 'run':
            s += 0.5 * fpres
        elif kind == 'wide':
            s += 1.0 - 3.0 * min(1.0, fs / 0.15) * fpres          # the space itself: no face, or a small one
        return s, notes


# ---------------------------------------------------------------------------- demand / positions
def item_need(it):
    return int(it.get('off', 0)) + int(math.ceil((it['n'] - 1) * it.get('speed', 1.0))) + 1


def slot_demand(tl):
    need = {}
    for it in tl['items'].values():
        need[it['slot']] = max(need.get(it['slot'], 0), item_need(it))
    return need


def slot_positions(tl):
    pos = {}
    for it in tl['items'].values():
        pos[it['slot']] = min(pos.get(it['slot'], it['f0']), it['f0'])
    return pos


def zoom_note(kind, cam, clip):
    want = cam['z'] + cam['over']
    note = 'wanted zoom %.1f, capped at %.1f' % (want, clip.zmax)
    if kind in ('eyes', 'face', 'profile') and want > 2.0 * clip.zmax:
        note += ' (tiny or false face: check the tile)'
    return note


def pick_all(tl, clip, fixes, keep=None):
    """keep = {slot: first frame} of a previous solution: unpinned slots stay there unless a pinned window now
    overlaps them, so pinning one slot does not reshuffle the others"""
    need = slot_demand(tl)
    pos = slot_positions(tl)
    slots = tl['slots']
    grp = {k: v.get('group') for k, v in slots.items()}
    order = sorted(need, key=lambda k: (grp[k] is not None, PRIORITY.index(slots[k]['kind']), -need[k], k))
    picks, warns, uses = {}, [], {}
    pins = (fixes or {}).get('slots') or {}
    pinned = [k for k in order if 'frame' in (pins.get(k) or {})]
    order = pinned + [k for k in order if k not in pinned]

    def penalty(k, lo, hi, gap):
        """None = rejected (closer than gap to another pick); else a penalty for sameness"""
        p, sh, gk = 0.0, clip.shot_of[lo], grp.get(k)
        for j, q in picks.items():
            a, b = q['sf'], q['sf'] + q['n']
            gj = grp.get(j)
            if gk is not None and gj != gk:                   # a panel vs anything outside its group: free reuse
                if lo < b and hi > a:
                    p += 0.4
                continue
            if gk is None and gj is not None:
                continue
            if gap is not None and lo < b + gap and hi > a - gap:
                return None
            if lo < b and hi > a:
                p += 3.0
            dt = abs(pos[k] - pos[j])
            if dt < NEAR and clip.shot_of[a] == sh:
                p += 2.5 * (1.0 - dt / float(NEAR)) + (1.5 if min(abs(lo - b), abs(a - hi)) < 45 else 0.0)
        return p + 0.25 * uses.get(sh, 0)

    def commit(k, rec):
        picks[k] = rec
        sh = clip.shot_of[rec['sf']]
        uses[sh] = uses.get(sh, 0) + 1

    for k in order:
        kind, n = slots[k]['kind'], min(need[k], clip.n)
        if k in pins and 'frame' in pins[k]:
            lo = int(clamp(int(pins[k]['frame']), 0, clip.n - n))
            cam = clip.cam(kind, lo, lo + n)
            notes = []
            if cam['over'] > 0 and 'z' not in pins[k]:
                notes.append(zoom_note(kind, cam, clip))
            cam.update({kk: float(pins[k][kk]) for kk in ('cx', 'cy', 'z') if kk in pins[k]})
            if 'z' in pins[k] and cam['z'] > clip.zmax:
                notes.append('pinned zoom %.1f is above the sharp limit %.1f' % (cam['z'], clip.zmax))
            sc, notes2 = clip.window_score(kind, lo, lo + n, cam)
            notes += notes2
            commit(k, {'slot': k, 'kind': kind, 'sf': lo, 'n': n, 'cam': cam, 'score': round(sc, 2), 'pinned': True,
                       'notes': notes})
            if notes:
                warns.append('%s (%s @%d, pinned): %s' % (k, kind, lo, '; '.join(notes)))
            continue
        if keep and k in keep and keep[k] + n <= clip.n and penalty(k, keep[k], keep[k] + n, 0) is not None:
            lo = keep[k]
            cam = clip.cam(kind, lo, lo + n)
            sc, notes = clip.window_score(kind, lo, lo + n, cam)
            if cam['over'] > 0:
                notes.append(zoom_note(kind, cam, clip))
            commit(k, {'slot': k, 'kind': kind, 'sf': lo, 'n': n, 'cam': cam, 'score': round(sc, 2), 'kept': True,
                       'notes': notes})
            if notes:
                warns.append('%s (%s @%d): %s' % (k, kind, lo, '; '.join(notes)))
            continue
        cands = []
        step = 1 if clip.n < 240 else 2
        for lo in range(0, clip.n - n + 1, step):
            cam = clip.cam(kind, lo, lo + n)
            sc, notes = clip.window_score(kind, lo, lo + n, cam)
            cross = lo + n > clip.shot_span(lo)[1]
            if cross:
                sc -= 4.0
                notes = notes + ['crosses a source cut']
            cands.append((sc, lo, cam, notes, cross))
        levels = []
        for gap, xok in ((GAP, False), (0, False), (None, False), (None, True)):   # relax step by step
            best = None
            for sc, lo, cam, notes, cross in cands:
                if cross and not xok:
                    continue
                pen = penalty(k, lo, lo + n, gap)
                if pen is None:
                    continue
                if best is None or sc - pen > best[0]:
                    best = (sc - pen, lo, cam, notes, gap)
            levels.append(best)
        top = max(b[0] for b in levels if b)
        # the strictest level whose best window is not much worse than what relaxing would give
        sc, lo, cam, notes, gap = next(b for b in levels if b and b[0] >= top - RELAX)
        notes = list(notes)
        if gap is None and grp.get(k) is None:
            notes.append('reuses footage (clip too short for unique moments)')
        if cam['over'] > 0:
            notes.append(zoom_note(kind, cam, clip))
        commit(k, {'slot': k, 'kind': kind, 'sf': lo, 'n': n, 'cam': cam, 'score': round(sc, 2), 'notes': notes})
        if notes:
            warns.append('%s (%s @%d): %s' % (k, kind, lo, '; '.join(notes)))
    return picks, warns


# ---------------------------------------------------------------------------- resolve
def sil_hint(clip, sf):
    """silhouette flash: a person box (source px) grown from the face; no face -> a luminance key of the frame"""
    W, H = clip.W, clip.H
    for i in range(sf, min(clip.n, sf + 6)):
        f = main_face(clip.F[i])
        if f:
            x, y, w, h = f['bb']
            return {'mode': 'person', 'hint': [round(max(0, x - 1.4 * w)), round(max(0, y - 0.5 * h)),
                                               round(min(W, x + 2.4 * w)), round(min(H, y + 8.0 * h))]}
    return {'mode': 'luma', 'hint': [round(0.3 * W), round(0.08 * H), round(0.7 * W), round(H)]}


LOOKS = ('bw', 'bw_hard', 'bw_soft', 'teal', 'warm', 'violet', 'color', 'none')
SLOT_KEYS = ('frame', 'cx', 'cy', 'z')
ITEM_KEYS = ('look', 'expo', 'zr', 'sharp', 'tone', 'cx', 'cy', 'z')


def check_fixes(tl, fixes):
    """reject typos instead of silently ignoring them"""
    if not fixes:
        return
    if not isinstance(fixes, dict) or set(fixes) - {'slots', 'items'}:
        raise ValueError('fixes.json: top level must be {"slots": {...}, "items": {...}}')
    for k, v in (fixes.get('slots') or {}).items():
        if k not in tl['slots']:
            raise ValueError('fixes.json: unknown slot %r (slots: %s)' % (k, ', '.join(sorted(tl['slots']))))
        if not isinstance(v, dict) or set(v) - set(SLOT_KEYS):
            raise ValueError('fixes.json: slot %r takes only %s' % (k, ', '.join(SLOT_KEYS)))
        if 'frame' not in v:
            raise ValueError('fixes.json: slot %r: cx/cy/z need "frame" too' % k)
        for kk in v:
            if not isinstance(v[kk], (int, float)):
                raise ValueError('fixes.json: slot %r: %s must be a number' % (k, kk))
    for k, v in (fixes.get('items') or {}).items():
        if k not in tl['items']:
            raise ValueError('fixes.json: unknown item %r (items: %s)' % (k, ', '.join(sorted(tl['items']))))
        if not isinstance(v, dict) or set(v) - set(ITEM_KEYS):
            raise ValueError('fixes.json: item %r takes only %s' % (k, ', '.join(ITEM_KEYS)))
        if 'look' in v and v['look'] not in LOOKS:
            raise ValueError('fixes.json: item %r: look must be one of %s' % (k, ', '.join(LOOKS)))
        for kk in ('expo', 'sharp', 'cx', 'cy', 'z'):
            if kk in v and not isinstance(v[kk], (int, float)):
                raise ValueError('fixes.json: item %r: %s must be a number' % (k, kk))
        for kk in ('zr', 'tone'):
            if kk in v and not (isinstance(v[kk], list) and len(v[kk]) == 2 and all(isinstance(x, (int, float)) for x in v[kk])):
                raise ValueError('fixes.json: item %r: %s must be [a, b]' % (k, kk))


def build(tl, feats, fixes=None):
    check_fixes(tl, fixes)
    clip = Clip(feats)
    if any('frame' in (v or {}) for v in ((fixes or {}).get('slots') or {}).values()):
        base, _ = pick_all(tl, clip, None)                 # the unpinned solution; pins only move what they hit
        picks, warns = pick_all(tl, clip, fixes, keep={k: p['sf'] for k, p in base.items()})
    else:
        picks, warns = pick_all(tl, clip, fixes)
    io = (fixes or {}).get('items') or {}
    items, boxes = {}, {}
    for iid, it in tl['items'].items():
        p = picks[it['slot']]
        cam = p['cam']
        o = dict(io.get(iid) or {})
        zr = o.pop('zr', None) or it.get('zr') or [1.0, 1.0]
        cx, cy = float(o.pop('cx', cam['cx'])), float(o.pop('cy', cam['cy']))
        z = float(o.pop('z', cam['z']))
        c0 = [round(cx, 1), round(cy, 1), round(max(1.0, z * zr[0]), 4)]
        c1 = [round(cx, 1), round(cy, 1), round(max(1.0, z * zr[-1]), 4)]
        rec = {'slot': it['slot'], 'f0': it['f0'], 'n': it['n'], 'k0': int(it.get('off', 0)),
               'speed': it.get('speed', 1.0), 'aspect': it['aspect'], 'c0': c0, 'c1': c1, 'look': it.get('look', 'color'),
               'expo': it.get('expo', 1.0), 'sharp': it.get('sharp', 0.35)}
        for kk in ('look', 'expo', 'sharp', 'tone'):
            if kk in o:
                rec[kk] = o.pop(kk)
        items[iid] = rec
        # union of the rects this item shows, and the resolution it needs
        dw = OUT_W * it.get('dw', 1.0 if abs(it['aspect'] - FULL) < 1e-3 else 0.7)
        bx = boxes.setdefault(it['slot'], [1e9, 1e9, -1e9, -1e9, 0.0])
        for k in range(it['n']):
            u = smooth(k / float(max(1, it['n'] - 1)))
            zz = c0[2] + (c1[2] - c0[2]) * u
            x, y, w, h = crop_rect(clip.W, clip.H, cx, cy, zz, it['aspect'])
            bx[0], bx[1] = min(bx[0], x), min(bx[1], y)
            bx[2], bx[3] = max(bx[2], x + w), max(bx[3], y + h)
            bx[4] = max(bx[4], dw / w)
    crops = {}
    for sl, (x0, y0, x1, y1, e) in boxes.items():
        p = picks[sl]
        x0, y0 = max(0, int(math.floor(x0 / 2.0)) * 2 - 2), max(0, int(math.floor(y0 / 2.0)) * 2 - 2)
        x1, y1 = min(clip.W, int(math.ceil(x1 / 2.0)) * 2 + 2), min(clip.H, int(math.ceil(y1 / 2.0)) * 2 + 2)
        bw, bh = x1 - x0, y1 - y0
        e = min(1.0, e * 1.02)
        ew, eh = max(2, int(round(bw * e / 2.0)) * 2), max(2, int(round(bh * e / 2.0)) * 2)
        crops[sl] = {'dir': 'crops/' + sl, 'sf': p['sf'], 'n': p['n'], 'box': [x0, y0, bw, bh], 'ew': ew, 'eh': eh}
    nf = tl['nf']
    plan = {'fps': FPS, 'w': OUT_W, 'h': OUT_H, 'nf': nf, 'src': {'w': clip.W, 'h': clip.H}, 'crops': crops,
            'items': items, 'segs': tl['segs'], 'caps': tl['caps'], 'tracks': {},
            'sil': sil_hint(clip, picks[tl['items']['open']['slot']]['sf'])}
    summary = ['edit: %d items, %d slots, %d frames (%.2f s), clip %d frames' % (len(items), len(picks), nf, nf / float(FPS), clip.n)]
    for k in sorted(picks, key=lambda k: picks[k]['sf']):
        p = picks[k]
        summary.append('  %-8s %-7s src %4d-%4d (%5.2f s)  z %.2f  score %5.2f%s' % (
            k, p['kind'], p['sf'], p['sf'] + p['n'] - 1, p['sf'] / float(FPS), p['cam']['z'], p['score'],
            '  pinned' if p.get('pinned') else ''))
    if warns:
        summary.append('warnings:')
        summary += ['  ' + w for w in warns]
    report = {'picks': picks, 'warnings': warns, 'summary': summary}
    return plan, report
