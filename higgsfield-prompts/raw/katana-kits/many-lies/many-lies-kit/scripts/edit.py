"""edit.py - template slots -> moments of the user's clip -> engine plan (python3 stdlib only).

The template (template/timeline.json) is the original edit with every piece of footage replaced by a SLOT reference:
  shots[].slot + off     a footage shot plays slot frames [off, off + f1 - f0)
  shots[].zr = [a, b]    zoom of the shot relative to the slot camera (slow push = [1, 1.06])
  collage / cutouts panels: {slot, off, rect, at, rate, g, border, rot, shadow}; dbl: {slot, off, amt, mode, zr}
  slots{name: {kind, ...}} kind decides framing and what a good moment is:
    eyes    extreme close-up on the eyes (two eyes, frontal)        face   close-up, face ~58 % of the frame
    hero    best frontal close-up, held                             medium face ~20 %, person in the space
    walk    long moving shot (camera or subject motion)             wide   whole frame, action
    detail  no face: hands, clothes, objects (crop below the face)  back   turned away / leaving (finale)
    bright  light footage for video-inside-letters                  profile face, not frontal (talking, shouting)
build() picks one window per slot (greedy by priority, inside one source shot, no reuse closer than 1 s while the
clip allows it) and resolves every reference to {src, sf, cx, cy, z0, z1} for engine/fx.js.

People: faces carry an appearance descriptor (scripts/ana.py 'd'); they are clustered into people and the HERO is the
person with the most face screen time (sum of sqrt(face area)), or the one named by fixes {"hero": {"frame": N[, "x",
"y"]}}. eyes / face / hero slots only frame the hero; profile / medium / walk / back / bright prefer the hero.

fixes (all optional): {"slots": {slot: {"frame", "cx", "cy", "z"}}, "shots": {id: {"g", "gamma", "zr", "mir"}},
  "repick": [slot, ..], "avoid": [[a, b], ..], "hero": {"frame": N, "x": px, "y": px},
  "keep": {slot: {...}} (previous picks to hold; written by ml.py run, not by hand)}
"""
import math

FPS = 24
OUT_W, OUT_H = 1440, 1080
ZMAX = 3.0                       # beyond this a 1080p source turns to mush
GAP = 24                         # frames kept between two picks while the clip has room
PRIORITY = ['hero', 'eyes', 'face', 'back', 'walk', 'profile', 'medium', 'wide', 'bright', 'detail']
FACE_FRAC = {'eyes': None, 'face': 0.58, 'hero': 0.66, 'profile': 0.5, 'medium': 0.2, 'walk': 0.16, 'wide': None,
             'detail': None, 'back': None, 'bright': 0.25}
MOTION_PREF = {'walk': 'high', 'wide': 'high', 'back': 'mid', 'eyes': 'low', 'face': 'low', 'hero': 'low',
               'profile': 'mid', 'medium': 'mid', 'detail': 'low', 'bright': 'any'}
HERO_KINDS = {'eyes', 'face', 'hero'}                          # must show the hero
PERSON_KINDS = {'profile', 'medium', 'walk', 'back', 'bright'}  # a person, preferably the hero
SIM = {'e': (0.40, 0.46),         # SFace identity embeddings: (track joins a person, two people merge)
       'd': (0.90, 0.95)}         # colour descriptors (fallback): conservative, they mostly see the lighting
SHOT_KEYS = {'g', 'gamma', 'zr', 'mir'}


def clamp(v, a, b):
    return a if v < a else b if v > b else v


def median(v):
    v = sorted(v)
    n = len(v)
    return None if not n else (v[n // 2] if n % 2 else 0.5 * (v[n // 2 - 1] + v[n // 2]))


# ---------------------------------------------------------------------------- per-frame helpers
def largest(fr):
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


def _dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def _unit(v):
    n = math.sqrt(sum(x * x for x in v))
    return [x / n for x in v] if n > 1e-9 else v


def _iou(a, b):
    ax0, ay0, aw, ah = a
    bx0, by0, bw, bh = b
    ix = max(0.0, min(ax0 + aw, bx0 + bw) - max(ax0, bx0))
    iy = max(0.0, min(ay0 + ah, by0 + bh) - max(ay0, by0))
    inter = ix * iy
    return inter / max(1e-6, aw * ah + bw * bh - inter)


class People:
    """faces -> tracks (IoU links between consecutive frames of one source shot) -> people (appearance clustering of
    track descriptors, then merging of close clusters). hero = most face screen time, or the override."""

    def __init__(self, F, override=None, warns=None, shot_of=None):
        self.label, self.clusters, self.hero = {}, [], None
        key = 'e' if any(f.get('e') for fr in F for f in (fr.get('f') or [])) else 'd'
        t_join, t_merge = SIM[key]
        self.key = key
        tracks, last = [], {}                                # last: track id -> (frame, bb)
        for i, fr in enumerate(F):
            cur = {}
            for j, f in enumerate(fr.get('f') or []):
                best, bi = None, 0.3
                for t, (pi, pbb) in last.items():
                    if pi == i - 1 and (shot_of is None or shot_of[pi] == shot_of[i]) and t not in cur.values():
                        v = _iou(pbb, f['bb'])
                        if v > bi:
                            best, bi = t, v
                if best is None:
                    tracks.append({'faces': [], 'sum': None, 'w': 0.0})
                    best = len(tracks) - 1
                tr = tracks[best]
                tr['faces'].append((i, j))
                if f.get(key):
                    w = math.sqrt(f['bb'][2] * f['bb'][3])
                    tr['sum'] = [x * w for x in f[key]] if tr['sum'] is None else [a + x * w for a, x in zip(tr['sum'], f[key])]
                    tr['w'] += w
                cur[j] = best
            last = {t: (i, (fr['f'][j]['bb'])) for j, t in cur.items()}
        tracks = [t for t in tracks if t['sum'] is not None]
        if not tracks:
            return
        for t in tracks:
            t['c'] = _unit(t['sum'])
        clusters = []
        for t in sorted(tracks, key=lambda t: -t['w']):
            best, bs = None, t_join
            for k, c in enumerate(clusters):
                sim = _dot(c['c'], t['c'])
                if sim > bs:
                    best, bs = k, sim
            if best is None:
                clusters.append({'sum': [x * t['w'] for x in t['c']], 'w': t['w'], 'tracks': [t]})
                clusters[-1]['c'] = list(t['c'])
            else:
                c = clusters[best]
                c['sum'] = [a + x * t['w'] for a, x in zip(c['sum'], t['c'])]
                c['w'] += t['w']
                c['c'] = _unit(c['sum'])
                c['tracks'].append(t)
        merged = True                                        # merge clusters of the same person seen in other light
        while merged and len(clusters) > 1:
            merged = False
            for a in range(len(clusters)):
                for b in range(a + 1, len(clusters)):
                    if _dot(clusters[a]['c'], clusters[b]['c']) > t_merge:
                        ca, cb = clusters[a], clusters[b]
                        ca['sum'] = [x + y for x, y in zip(ca['sum'], cb['sum'])]
                        ca['w'] += cb['w']
                        ca['c'] = _unit(ca['sum'])
                        ca['tracks'] += cb['tracks']
                        del clusters[b]
                        merged = True
                        break
                if merged:
                    break
        for k, c in enumerate(clusters):
            frames = set()
            for t in c['tracks']:
                for i, j in t['faces']:
                    self.label[(i, j)] = k
                    frames.add(i)
            self.clusters.append({'c': c['c'], 'w': c['w'], 'frames': frames, 'n': sum(len(t['faces']) for t in c['tracks'])})
        self.hero = max(range(len(self.clusters)), key=lambda k: self.clusters[k]['w'])
        if override:
            k = self._pick(F, override, warns if warns is not None else [])
            if k is not None:
                self.hero = k

    def _pick(self, F, ov, warns):
        try:
            i = int(ov.get('frame'))
        except (TypeError, ValueError):
            warns.append('hero: needs "frame"')
            return None
        if not (0 <= i < len(F)) or not F[i].get('f'):
            warns.append('hero: no face detected at source frame %s; kept the automatic hero' % ov.get('frame'))
            return None
        faces = F[i]['f']
        j = 0
        if 'x' in ov and 'y' in ov:
            x, y = float(ov['x']), float(ov['y'])
            j = min(range(len(faces)), key=lambda q: math.hypot(faces[q]['bb'][0] + faces[q]['bb'][2] / 2 - x,
                                                                 faces[q]['bb'][1] + faces[q]['bb'][3] / 2 - y))
        if (i, j) not in self.label:
            warns.append('hero: the face at frame %d has no descriptor; kept the automatic hero' % i)
            return None
        return self.label[(i, j)]

    def is_hero(self, i, j):
        return self.hero is None or self.label.get((i, j), -1) == self.hero

    def summary(self, n):
        out = []
        for k, c in sorted(enumerate(self.clusters), key=lambda t: -t[1]['w']):
            if c['n'] < 3 and k != self.hero:
                continue
            fr = sorted(c['frames'])
            spans, a = [], fr[0]
            for p, q in zip(fr, fr[1:] + [None]):
                if q is None or q - p > 6:
                    spans.append('%d-%d' % (a, p))
                    a = q
            out.append({'person': k, 'hero': k == self.hero, 'frames': len(fr), 'share': round(len(fr) / float(n), 3),
                        'spans': spans[:12]})
        return out


class Clip:
    def __init__(self, feats, hero=None, warns=None):
        self.F = feats['frames']
        self.n = feats['n']
        self.shot_of = [0] * self.n
        for sh in feats['shots']:
            for i in range(sh['a'], sh['b']):
                self.shot_of[i] = sh['i']
        self.people = People(self.F, hero, warns if warns is not None else [], self.shot_of)
        self.W, self.H = feats['size']
        self.zmin = max(OUT_W / float(self.W), OUT_H / float(self.H))
        self.shot_of = [0] * self.n
        self.shots = feats['shots']
        for s in self.shots:
            for i in range(s['a'], s['b']):
                self.shot_of[i] = s['i']
        sh = sorted(fr['sh'] for fr in self.F)
        self.sharp_ref = max(1e-4, sh[int(0.7 * (len(sh) - 1))])
        mo = sorted(fr['m'] for fr in self.F)
        self.mo50 = max(1e-4, mo[len(mo) // 2])
        self.mo90 = max(self.mo50 * 1.5, mo[int(0.9 * (len(mo) - 1))])

    def shot_span(self, i):
        s = self.shots[self.shot_of[i]]
        return s['a'], s['b']

    def hero_face(self, i):
        fr = self.F[i]
        for j, f in enumerate(fr.get('f') or []):
            if self.people.is_hero(i, j):
                return f
        return None

    def face_for(self, kind, i):
        """the face a slot of this kind frames at source frame i: the hero when visible, else the largest face"""
        if kind in HERO_KINDS or kind in PERSON_KINDS:
            return self.hero_face(i) or largest(self.F[i])
        return largest(self.F[i])

    # camera for a window: median face of the window -> cx, cy, z for the kind
    def cam(self, kind, lo, hi):
        faces = [self.face_for(kind, i) for i in range(lo, hi)]
        faces = [f for f in faces if f]
        W, H = self.W, self.H
        if not faces:
            near = [self.face_for(kind, i) for i in range(max(0, lo - 12), min(self.n, hi + 12))]
            faces = [f for f in near if f]
        cx, cy, z = W / 2.0, H / 2.0, self.zmin
        if faces:
            fcx = median([f['bb'][0] + f['bb'][2] / 2.0 for f in faces])
            fcy = median([f['bb'][1] + f['bb'][3] / 2.0 for f in faces])
            fh = median([f['bb'][3] for f in faces])
            fw = median([f['bb'][2] for f in faces])
            cx, cy = fcx, fcy
            if kind == 'eyes':
                eds = [eye_dist(f) for f in faces if eye_dist(f)]
                ey = [0.5 * (f['eyes'][0][1] + f['eyes'][-1][1]) for f in faces if eye_dist(f)]
                ex = [0.5 * (f['eyes'][0][0] + f['eyes'][-1][0]) for f in faces if eye_dist(f)]
                if eds:
                    z = 0.40 * OUT_W / median(eds)
                    cx, cy = median(ex), median(ey) + 0.04 * OUT_H / z
                else:
                    z = 0.95 * OUT_H / fh
                    cy = fcy - 0.08 * fh
            elif kind in ('face', 'hero', 'profile', 'bright'):
                z = FACE_FRAC[kind] * OUT_H / fh
                cy = fcy + 0.04 * OUT_H / z
            elif kind in ('medium', 'walk'):
                z = FACE_FRAC[kind] * OUT_H / fh
                cy = fcy + 0.17 * OUT_H / max(z, self.zmin)
            elif kind == 'detail':
                z = 1.7 * self.zmin
                cy = fcy + 1.8 * fh
            elif kind in ('wide', 'back'):
                z = self.zmin * (1.0 if kind == 'wide' else 1.05)
        elif kind == 'detail':
            z = 1.6 * self.zmin
        elif kind in ('eyes', 'face', 'hero'):
            z = 1.35 * self.zmin
        over = max(0.0, z - ZMAX)
        z = clamp(z, self.zmin, ZMAX)
        hw, hh = OUT_W / 2.0 / z, OUT_H / 2.0 / z
        cx, cy = clamp(cx, hw, W - hw), clamp(cy, hh, H - hh)
        return {'cx': round(cx, 1), 'cy': round(cy, 1), 'z': round(z, 4), 'over': round(over, 3)}

    def window_score(self, kind, lo, hi, cam):
        F = self.F[lo:hi]
        n = len(F)
        notes = []
        if any(fr.get('bad') for fr in F):
            return -99, ['unreadable frames']
        sharp = sum(fr['sh'] for fr in F) / n / self.sharp_ref
        dark = sum(1 for fr in F if fr['p95'] < 0.22) / float(n)
        mo = sum(fr['m'] for fr in F) / n
        rel = mo / self.mo50
        faces = [self.face_for(kind, i) for i in range(lo, hi)]
        fpres = sum(1 for f in faces if f) / float(n)
        ffront = sum(1 for f in faces if frontal(f)) / float(n)
        anyp = sum(1 for fr in F if fr.get('f')) / float(n)
        # other people's faces inside the crop (not the framed face, big enough to compete)
        hw, hh = OUT_W / 2.0 / cam['z'], OUT_H / 2.0 / cam['z']
        crop = (cam['cx'] - hw, cam['cy'] - hh, cam['cx'] + hw, cam['cy'] + hh)
        extra = 0.0
        for k, fr in enumerate(F):
            own = faces[k]
            ref = own['bb'][3] if own else 1e9
            for f in fr.get('f') or []:
                if f is own:
                    continue
                fx, fy = f['bb'][0] + f['bb'][2] / 2.0, f['bb'][1] + f['bb'][3] / 2.0
                if crop[0] < fx < crop[2] and crop[1] < fy < crop[3] and f['bb'][3] > 0.35 * ref:
                    extra += 1.0 if f['bb'][3] < 1.2 * ref else 2.0      # a bigger stranger is worse
        extra /= float(n)
        s = 2.0 * min(1.3, sharp) - 3.0 * dark - 2.5 * extra - min(3.0, 1.2 * cam['over'])
        pref = MOTION_PREF[kind]
        if pref == 'high':
            s += 1.2 * min(2.5, rel)
        elif pref == 'low':
            s -= 0.8 * max(0.0, rel - 1.5)
        elif pref == 'mid':
            s -= 0.5 * abs(math.log(max(rel, 0.05)))
        if kind in HERO_KINDS:
            hpres = sum(1 for i in range(lo, hi) if self.hero_face(i)) / float(n)
            s += 1.5 * fpres + 3.5 * hpres + 2.5 * ffront
            if kind == 'hero':
                s += 1.0 * min(1.0, n / 30.0)
            if hpres < 0.5:
                notes.append('hero in %.0f%% of the window%s' % (100 * hpres, '' if fpres > hpres else ''))
        elif kind in ('profile', 'medium', 'walk', 'bright'):
            s += 2.0 * fpres + (0.6 * ffront if kind != 'profile' else 0.8 * (fpres - ffront))
            if anyp < 0.2:
                s -= 3.0                                                  # nobody on screen
                notes.append('nobody visible')
        elif kind == 'detail':
            s += 0.8 * (1.0 - anyp) + 0.5 * min(1.3, sharp)
        elif kind == 'back':
            present = min(1.0, max(anyp, min(1.0, rel / 0.8) if rel > 0.4 else 0.0))   # a face, or a moving body
            late = lo / float(max(1, self.n - (hi - lo)))
            s += 2.5 * present * (1.0 - ffront) + 1.2 * late + 0.4 * min(2.0, rel)
            if present < 0.25:
                s -= 3.0
                notes.append('nobody visible')
        elif kind == 'wide':
            s += 0.5 * anyp
            if anyp < 0.1 and rel < 0.6:
                s -= 1.5
        if kind == 'bright':
            s += 4.0 * (sum(fr['y'] for fr in F) / n)
        return s, notes


# ---------------------------------------------------------------------------- slot demand
def slot_demand(tl):
    """slot -> frames needed (max over all references of off + length)."""
    need = {}

    def use(slot, off, length):
        need[slot] = max(need.get(slot, 0), int(off) + int(length))
    for s in tl['shots']:
        n = s['f1'] - s['f0']
        if s.get('slot'):
            use(s['slot'], s.get('off', 0), n)
        for p in s.get('collage') or []:
            use(p['slot'], p.get('off', 0), max(1, int((n - p.get('at', 0)) * p.get('rate', 1.0)) + 1))
        if s.get('dbl'):
            use(s['dbl']['slot'], s['dbl'].get('off', 0), n)
    for e in tl.get('ev') or []:
        n = e['f1'] - e['f0']
        for p in e.get('panels') or []:
            use(p['slot'], p.get('off', 0), max(1, int((n - p.get('at', 0)) * p.get('rate', 1.0)) + 1))
    return need


# ---------------------------------------------------------------------------- picking
def slot_positions(tl):
    """slot -> (first output frame that shows it, panel group or None). Panels (collages, cut-outs) are recaps:
    they may reuse moments of full-frame shots and only have to differ inside their own group."""
    pos, grp = {}, {}

    def at(slot, f, g=None):
        pos[slot] = min(pos.get(slot, f), f)
        if g is not None:
            grp[slot] = g
    for s in tl['shots']:
        if s.get('slot'):
            at(s['slot'], s['f0'])
        for p in s.get('collage') or []:
            at(p['slot'], s['f0'] + p.get('at', 0), 'c:' + s['id'])
        if s.get('dbl'):
            at(s['dbl']['slot'], s['f0'])
    for i, e in enumerate(tl.get('ev') or []):
        for p in e.get('panels') or []:
            at(p['slot'], e['f0'] + p.get('at', 0), 'e:%d' % i)
    return pos, grp


NEAR = 36                        # output frames (4 beats): picks this close in the edit should differ


def _ranges(v):
    out = []
    for r in v or []:
        try:
            a, b = int(r[0]), int(r[1])
        except (TypeError, ValueError, IndexError):
            continue
        if b >= a:
            out.append((a, b))
    return out


def pick_all(tl, clip, fixes, fw):
    """fw: list collecting fix warnings (names that do not exist, cx/cy/z without frame, ...)."""
    need = slot_demand(tl)
    pos, grp = slot_positions(tl)
    slots = tl['slots']
    order = sorted(need, key=lambda k: (PRIORITY.index(slots[k]['kind']), -need[k], k))
    picks, warns, uses = {}, [], {}
    fixes = fixes or {}
    user = dict(fixes.get('slots') or {})
    keep = dict(fixes.get('keep') or {})
    repick = set(fixes.get('repick') or [])
    avoid = _ranges(fixes.get('avoid'))
    for k in list(user) + list(repick):
        if k not in slots:
            fw.append('unknown slot "%s" (slot names are case-sensitive: see the slot table)' % k)
    slot_avoid = {}
    for k in repick:                                         # re-pick away from the previous moment
        if k in keep:
            a = int(keep[k].get('frame', 0))
            slot_avoid[k] = [(a - 12, a + need.get(k, 1) + 12)]
    pins = {}
    for k, v in keep.items():
        if k in slots and k not in repick:
            pins[k] = dict(v)
    for k, v in user.items():
        if k not in slots:
            continue
        if 'frame' in v:
            pins[k] = dict(v)
        elif k in pins:                                      # reframe the kept moment
            pins[k].update({kk: v[kk] for kk in ('cx', 'cy', 'z') if kk in v})
        else:
            fw.append('slot "%s": cx/cy/z need "frame" (no previous pick to reframe)' % k)

    def overlaps(lo, hi, rs):
        return any(lo <= b and hi > a for a, b in rs)

    def penalty(k, lo, hi, gap):
        """None = rejected (closer than gap to another pick); else a penalty for sameness."""
        p, sh, gk = 0.0, clip.shot_of[lo], grp.get(k)
        for j, q in picks.items():
            a, b = q['sf'], q['sf'] + q['n']
            if gk is not None and grp.get(j) != gk:          # a panel vs anything outside its group: free reuse
                if lo < b and hi > a:
                    p += 0.3
                continue
            if gk is None and grp.get(j) is not None:        # full-frame shot vs an earlier panel pick: ignore
                continue
            if gap is not None and lo < b + gap and hi > a - gap:
                return None
            if lo < b and hi > a:
                p += 3.0
            dt = abs(pos[k] - pos[j])
            if dt < NEAR and clip.shot_of[a] == sh:
                p += 2.5 * (1.0 - dt / float(NEAR)) + (1.5 if min(abs(lo - b), abs(a - hi)) < 48 else 0.0)
        return p + 0.25 * uses.get(sh, 0)

    def commit(k, rec):
        picks[k] = rec
        sh = clip.shot_of[rec['sf']]
        uses[sh] = uses.get(sh, 0) + 1

    # pinned slots first, so free slots avoid them
    for k in sorted(pins, key=lambda k: order.index(k) if k in order else 999):
        if k not in need:
            continue
        kind, n = slots[k]['kind'], min(need[k], clip.n)
        v = pins[k]
        try:
            lo = int(clamp(int(v['frame']), 0, clip.n - n))
        except (TypeError, ValueError, KeyError):
            fw.append('slot "%s": bad frame %r' % (k, v.get('frame')))
            continue
        cam = clip.cam(kind, lo, lo + n)
        for kk in ('cx', 'cy', 'z'):
            if kk in v:
                try:
                    cam[kk] = float(v[kk])
                except (TypeError, ValueError):
                    fw.append('slot "%s": bad %s %r' % (k, kk, v[kk]))
        cam['z'] = round(clamp(cam['z'], clip.zmin, ZMAX), 4)
        sc, notes = clip.window_score(kind, lo, lo + n, cam)
        rec = {'slot': k, 'kind': kind, 'sf': lo, 'n': n, 'cam': cam, 'score': round(sc, 2),
               'pinned': k in user and 'frame' in user[k], 'kept': k not in user and k in keep, 'notes': notes}
        if overlaps(lo, lo + n, avoid):
            rec['notes'] = notes + ['pinned inside an avoid range']
        commit(k, rec)
        if rec['notes'] and rec['pinned']:
            warns.append('%s (%s @%d, pinned): %s' % (k, kind, lo, '; '.join(rec['notes'])))
    for k in order:
        if k in picks:
            continue
        kind, n = slots[k]['kind'], min(need[k], clip.n)
        bad = avoid + slot_avoid.get(k, [])
        cands = []
        for lo in range(0, clip.n - n + 1, 2):
            cam = clip.cam(kind, lo, lo + n)
            sc, notes = clip.window_score(kind, lo, lo + n, cam)
            cross = lo + n > clip.shot_span(lo)[1]
            if cross:
                sc -= 4.0
                notes = notes + ['crosses a source cut']
            cands.append((sc, lo, cam, notes, cross, overlaps(lo, lo + n, bad)))
        best = None
        for xok, aok in ((False, False), (True, False), (True, True)):   # source cuts, then avoid ranges, relax last
            for sc, lo, cam, notes, cross, inbad in cands:
                if (cross and not xok) or (inbad and not aok):
                    continue
                for gap, cost in ((GAP, 0.0), (8, 0.8), (0, 1.6), (None, 3.0)):   # soft spacing: a better moment
                    pen = penalty(k, lo, lo + n, gap)                          # may sit closer to another pick
                    if pen is not None:
                        break
                tot = sc - pen - cost
                if best is None or tot > best[0]:
                    best = (tot, lo, cam, notes + (['inside an avoid range'] if inbad else []), gap)
            if best is not None:
                break
        sc, lo, cam, notes, gap = best
        notes = list(notes)
        if gap is None and k not in grp:
            notes.append('reuses footage (clip too short for unique moments)')
        if cam['over'] > 0:
            notes.append('wanted zoom %.1f, capped at %.1f' % (cam['z'] + cam['over'], ZMAX))
        commit(k, {'slot': k, 'kind': kind, 'sf': lo, 'n': n, 'cam': cam, 'score': round(sc, 2), 'notes': notes,
                   'repicked': k in repick})
        if notes:
            warns.append('%s (%s @%d): %s' % (k, kind, lo, '; '.join(notes)))
    return picks, warns


# ---------------------------------------------------------------------------- resolve the template
def eye_track(clip, lo, n, z):
    out = []
    for i in range(lo, lo + n):
        f = clip.hero_face(min(i, clip.n - 1))
        pts = []
        if f and frontal(f):                                 # profile landmarks land on the nose: no glow
            r = max(2.5, 0.045 * f['bb'][2])
            pts = [[e[0], e[1], round(r, 1)] for e in (f['eyes'][0], f['eyes'][-1])]
        out.append(pts)
    return out


def pop_ok(clip, lo, n):
    """keep the 'pop' grade only when the footage really has warm saturated eyes and little other warm colour."""
    F = clip.F[lo:lo + n]
    we = sum(fr.get('we', 0) for fr in F) / len(F)
    wo = sum(fr.get('wo', fr.get('wm', 0)) for fr in F) / len(F)
    return we > 0.04 and wo < 0.0015


def resolve_shot(s, picks, clip, glow, notes):
    out = {k: v for k, v in s.items() if k not in ('slot', 'off', 'zr', 'collage', 'dbl', 'note')}
    if s.get('slot'):
        p = picks[s['slot']]
        cam, off, n = p['cam'], s.get('off', 0), s['f1'] - s['f0']
        zr = s.get('zr') or [1.0, 1.0]
        out.update({'src': 'v0', 'sf': p['sf'] + off, 'cx': cam['cx'], 'cy': cam['cy'],
                    'z0': round(cam['z'] * zr[0], 4), 'z1': round(cam['z'] * zr[-1], 4), '_tz': cam['z']})
        if s.get('mir'):
            out['mir'] = True
        if s.get('g') == 'pop' and not pop_ok(clip, p['sf'] + off, n):
            out['g'] = 'bw'
            if glow:
                out['eyes'] = eye_track(clip, p['sf'] + off, n, cam['z'])
            notes.append('%s: pop -> bw%s' % (s['id'], ' + glow' if glow else ''))
    if s.get('collage'):
        out['collage'] = [resolve_panel(p, picks, clip) for p in s['collage']]
    if s.get('dbl'):
        d = s['dbl']
        p = picks[d['slot']]
        zr = d.get('zr') or [1.0, 1.0]
        out['dbl'] = {k: v for k, v in d.items() if k not in ('slot', 'off', 'zr')}
        out['dbl'].update({'src': 'v0', 'sf': p['sf'] + d.get('off', 0), 'cx': p['cam']['cx'], 'cy': p['cam']['cy'],
                           'z0': round(p['cam']['z'] * zr[0], 4), 'z1': round(p['cam']['z'] * zr[-1], 4)})
        if out['dbl'].get('g') == 'pop':
            out['dbl']['g'] = 'bw'
    return out


def resolve_panel(p, picks, clip):
    q = picks[p['slot']]
    cam = q['cam']
    x, y, w, h = p['rect']
    # panel scale s = z * max(w/SW, h/SH) (fx.panelImg); show the same source height as the slot camera does on the
    # full frame (OUT_H / cam z), so a face slot is a face in the panel too
    zp = max(1.0, (h * cam['z'] / float(OUT_H)) / max(w / float(clip.W), h / float(clip.H)))
    out = {k: v for k, v in p.items() if k not in ('slot', 'off', 'zr')}
    out.update({'src': 'v0', 'sf': q['sf'] + p.get('off', 0), 'cx': cam['cx'], 'cy': cam['cy'],
                'z': round(p.get('zr', 1.0) * zp, 4)})
    if out.get('g') == 'pop' and not pop_ok(clip, out['sf'], 4):
        out['g'] = 'bw'
    return out


def build(tl, feats, fixes=None, glow=False):
    fixes = fixes or {}
    fw = []
    for k in fixes:
        if k not in ('slots', 'shots', 'repick', 'avoid', 'hero', 'keep'):
            fw.append('unknown fixes key "%s" (allowed: slots, shots, repick, avoid, hero)' % k)
    clip = Clip(feats, fixes.get('hero'), fw)
    picks, warns = pick_all(tl, clip, fixes, fw)
    notes = []
    shots = [resolve_shot(s, picks, clip, glow, notes) for s in tl['shots']]
    ev = []
    for e in tl.get('ev') or []:
        e2 = dict(e)
        if e.get('panels'):
            e2['panels'] = [resolve_panel(p, picks, clip) for p in e['panels']]
        ev.append(e2)
    # per-shot overrides: {"shots": {"<shot id>": {"g": "bw", "gamma": 0.8, "zr": [1, 1.08], "mir": true}}}
    so = fixes.get('shots') or {}
    ids = {s['id']: s for s in shots}
    for sid, ov in so.items():
        s = ids.get(sid)
        if s is None:
            fw.append('unknown shot id "%s" (shot ids are lowercase, see the timeline table)' % sid)
            continue
        for k, v in (ov or {}).items():
            if k not in SHOT_KEYS:
                fw.append('shot "%s": key "%s" not allowed (only g, gamma, zr, mir)' % (sid, k))
            elif 'z0' not in s:
                fw.append('shot "%s" has no footage of its own (collage / solid): re-pin its panel slots instead' % sid)
            elif k == 'zr':
                try:
                    a, b = float(v[0]), float(v[-1])
                    tz = s.get('_tz', s['z0'])
                    s['z0'], s['z1'] = round(tz * a, 4), round(tz * b, 4)
                except (TypeError, ValueError, IndexError):
                    fw.append('shot "%s": zr must be [start, end]' % sid)
            elif k == 'g' and v not in ('bw', 'color', 'pop', 'orig'):
                fw.append('shot "%s": g must be bw, color, pop or orig' % sid)
            else:
                s[k] = v
                if k == 'g' and v != 'pop':
                    s.pop('eyes', None)
    for s in shots:
        s.pop('_tz', None)
    nf = sum(s['f1'] - s['f0'] for s in shots)
    plan = {'fps': FPS, 'w': OUT_W, 'h': OUT_H, 'nf': nf,
            'src': {'v0': {'n': clip.n, 'w': clip.W, 'h': clip.H, 'dir': 'src/v0'}},
            'shots': shots, 'ev': ev, 'rgb': tl.get('rgb') or {}, 'scan': tl.get('scan') or []}
    people = clip.people.summary(clip.n)
    summary = ['edit: %d shots, %d slots, %d frames (%.2f s)' % (len(shots), len(picks), nf, nf / float(FPS))]
    if people:
        summary.append('people: ' + '; '.join('%s%d in %d frames (%.0f%%) %s' % (
            'HERO ' if p['hero'] else 'person ', p['person'], p['frames'], 100 * p['share'], ','.join(p['spans'][:6]))
            for p in people[:4]))
    for k in sorted(picks, key=lambda k: picks[k]['sf']):
        p = picks[k]
        hf = sum(1 for i in range(p['sf'], p['sf'] + p['n']) if clip.hero_face(i)) / float(max(1, p['n']))
        p['hero_share'] = round(hf, 2)
        summary.append('  %-7s %-7s src %4d-%4d (%5.2f s)  cx %6.0f cy %6.0f z %.2f  hero %3.0f%%  score %5.2f%s' % (
            k, p['kind'], p['sf'], p['sf'] + p['n'] - 1, p['sf'] / float(FPS), p['cam']['cx'], p['cam']['cy'],
            p['cam']['z'], 100 * hf, p['score'],
            '  PINNED' if p.get('pinned') else ('  kept' if p.get('kept') else ('  repicked' if p.get('repicked') else ''))))
    if fw:
        summary.append('FIX WARNINGS:')
        summary += ['  ' + w for w in fw]
    if warns:
        summary.append('warnings:')
        summary += ['  ' + w for w in warns]
    if notes:
        summary.append('grade: ' + ', '.join(notes))
    pins = {'slots': {k: {'frame': p['sf'], 'cx': p['cam']['cx'], 'cy': p['cam']['cy'], 'z': p['cam']['z']}
                      for k, p in picks.items()}}
    for k in ('shots', 'avoid', 'hero'):
        if fixes.get(k):
            pins[k] = fixes[k]
    report = {'picks': picks, 'warnings': warns, 'fix_warnings': fw, 'grade_notes': notes, 'people': people,
              'pins': pins, 'summary': summary}
    return plan, report
