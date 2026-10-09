"""cast.py - pick the clip's moments and framings for every slot of the template (stdlib; used by pc.py edit).

plan(features, fixes) -> (cast, report)
  cast    {'sources': {alias: path}, 'phrases': {'A': {...}, 'B': {...}}} in the shapes edit.py expects
  report  per slot: alias, t, framing, score, notes; plus warnings

Every slot has a kind (what the template shows there, measured on princess.mp4 with the same face detector):
  shot   full-frame camera on the source: face height f (fraction of the 1080 output) at output position pos
  crop   a w x h window of the source (aspect fixed by the template) with the face at f of its height
  detail crop below the face (outfit, hands), the template's no-face photo beat
  cut    person cut-out (segmentation box = the person box, padded)
Moments: a window [t, t + need] inside one source shot, the hero's face visible at both ends, as sharp as possible,
the framing reachable without upscaling past ZMAX, and 1 s away from every other pick while the clip allows.
Heroes: features.json people (SFace identities, most screen presence first). Both phrases star person #0;
fixes.json {"heroes": {"A": 0, "B": 2}} overrides (card1 shows the phrase-B hero, card2 the phrase-A hero).
"""
import math

OUT = 1080
ZMAX = 2.2          # max upscale of source pixels (normalized sources are 1080 px on the short side)
MIN_GAP = 1.0       # s between picks (soft); shrinks when the hero is on screen only briefly

# name: kind, need (s of live footage), f, pos (x, y) or aspect (w/h) for crops
SLOTS = {
    'drop':      dict(kind='shot', need=0.26, f=0.16, pos=(0.54, 0.32), cut=True),
    'poster':    dict(kind='shot', need=0.62, f=0.19, pos=(0.52, 0.23), zr=(1.0, 1.06)),
    'photo':     dict(kind='crop', need=0.30, f=0.15, aspect=600 / 840, fy=0.20),   # template: a detail; here the
    #              hero head-to-waist in a tall frame (a crop below the face is mush on most clips)
    'col_frame': dict(kind='crop', need=0.66, f=0.22, aspect=560 / 760, fy=0.36),
    'col_cut':   dict(kind='cut', need=0.0, fsrc=(0.10, 0.34)),
    'square':    dict(kind='shot', need=0.72, f=0.36, pos=(0.52, 0.48), bokeh=True),
    'card1':     dict(kind='crop', need=0.0, f=0.36, aspect=630 / 540, fy=0.42),
    'card2':     dict(kind='crop', need=0.0, f=0.40, aspect=640 / 550, fy=0.42),
    'text_cu':   dict(kind='shot', need=0.40, f=0.44, pos=(0.50, 0.40)),
    'name_bg':   dict(kind='shot', need=0.20, f=0.46, pos=(0.50, 0.44)),
    'close1':    dict(kind='shot', need=0.30, f=0.32, pos=(0.54, 0.38)),
    'rack':      dict(kind='shot', need=0.25, f=0.34, pos=(0.52, 0.40)),
    'oval_bg':   dict(kind='shot', need=0.50, f=0.15, pos=(0.50, 0.36)),
    'oval_cut':  dict(kind='cut', need=0.50, fsrc=(0.10, 0.30)),
    'face':      dict(kind='crop', need=0.36, f=0.34, aspect=1.0, fy=0.45),
    'inset':     dict(kind='crop', need=0.30, f=0.32, aspect=900 / 560, fy=0.45),
    'face2':     dict(kind='crop', need=0.40, f=0.30, aspect=520 / 600, fy=0.42),
    'face3':     dict(kind='crop', need=0.40, f=0.42, aspect=460 / 560, fy=0.45),
    'inset2':    dict(kind='crop', need=0.40, f=0.26, aspect=800 / 560, fy=0.45),
}
# greedy order: the beats people remember first
ORDER = ['drop', 'text_cu', 'poster', 'close1', 'oval_cut', 'square', 'card2', 'card1', 'col_cut', 'col_frame',
         'name_bg', 'rack', 'face', 'inset', 'oval_bg', 'face2', 'face3', 'inset2', 'photo']
# timeline neighbours (should not come from the same source shot)
NEIGH = [('drop', 'poster'), ('poster', 'photo'), ('photo', 'col_frame'), ('col_frame', 'square'),
         ('square', 'card1'), ('card1', 'card2'), ('card2', 'text_cu'), ('text_cu', 'name_bg'),
         ('name_bg', 'close1'), ('close1', 'rack'), ('rack', 'oval_bg'), ('oval_bg', 'face'), ('face', 'inset'),
         ('inset', 'face2')]

STICKERS = {
    'A': [['heart', 0.55, 960, 930, 10], ['star', 0.50, 290, 975, -12],
          ['heart', 0.60, 150, 120, -14], ['sparkle', 0.55, 470, 70, 0], ['star', 0.45, 1010, 70, 12],
          ['bow', 0.45, 60, 520, -8], ['heart', 0.32, 610, 1015, 10], ['sparkle', 0.35, 1040, 560, 0]],
    'B': [['bow', 0.50, 300, 985, -10], ['sparkle', 0.50, 1000, 330, 12],
          ['heart', 0.60, 150, 120, -14], ['bow', 0.55, 470, 80, 6], ['star', 0.45, 1010, 70, 12],
          ['sparkle', 0.50, 60, 520, 0], ['heart', 0.32, 640, 1010, 10], ['sparkle', 0.35, 1040, 640, 0]],
}


def clamp(v, lo, hi):
    return lo if hi < lo else min(hi, max(lo, v))


class Src:
    def __init__(self, alias, d):
        self.alias, self.w, self.h = alias, d['w'], d['h']
        self.dur, self.rate = d['dur'], d['rate']
        self.cuts = d['cuts']
        self.s = d['samples']
        sh = sorted(x['sharp'] for x in self.s) or [1.0]
        self.sharp_ref = max(1e-3, sh[int(len(sh) * 0.8)])
        fs = sorted(f[6] for x in self.s for f in x['faces']) or [1.0]
        self.face_sharp_ref = max(1e-3, fs[int(len(fs) * 0.8)])
        self.cover = max(OUT / self.w, OUT / self.h) / (OUT / self.h)     # min zoom (relative to fit-height)

    def shot_id(self, t):
        return sum(1 for c in self.cuts if c <= t + 1e-6)

    def same_shot(self, t0, t1):
        return self.shot_id(t0) == self.shot_id(t1)

    def at(self, t):
        i = clamp(int(round(t * self.rate)), 0, len(self.s) - 1)
        return self.s[i]

    def face(self, t, hero):
        for f in self.at(t)['faces']:
            if hero is None or f[5] == hero:
                return f
        return None


# ----------------------------------------------------------------------------- framing
def frame_shot(src, face, f, pos, person=None):
    """(cx, cy, zoom, penalty) so the face is f of the output height at output position pos."""
    fit = OUT / src.h
    if face:
        fx, fy, fw, fh = face[:4]
        fcx, fcy = fx + fw / 2, fy + fh / 2
        z = f * OUT / fh / fit
    else:   # no face: the person box (or the frame centre) fills ~90 % of the height
        if person:
            fcx, fcy = (person[0] + person[2]) / 2, person[1] + (person[3] - person[1]) * 0.2
            z = 0.9 * OUT / max(1, person[3] - person[1]) / fit
        else:
            fcx, fcy, z = src.w / 2, src.h / 2, src.cover
    pen = 0.0
    zmax = ZMAX / fit
    if z > zmax:
        pen += math.log(z / zmax) * 2.0
        z = zmax
    if z < src.cover:
        pen += math.log(src.cover / z) * 0.6
        z = src.cover
    sc = fit * z
    cx = fcx - (pos[0] - 0.5) * OUT / sc
    cy = fcy - (pos[1] - 0.5) * OUT / sc
    hw, hh = OUT / 2 / sc, OUT / 2 / sc
    cx2, cy2 = clamp(cx, hw, src.w - hw), clamp(cy, hh, src.h - hh)
    pen += (abs(cx2 - cx) + abs(cy2 - cy)) * sc / OUT * 2.0
    return round(cx2, 1), round(cy2, 1), round(z, 4), pen


def frame_crop(src, face, f, aspect, fy=0.45, person=None):
    """(cx, cy, w, h, penalty): a window of the source with the face at f of its height."""
    if face:
        fx, fyy, fw, fh = face[:4]
        fcx, fcy = fx + fw / 2, fyy + fh / 2
        h = fh / f
    elif person:
        fcx, fcy = (person[0] + person[2]) / 2, person[1] + (person[3] - person[1]) * 0.25
        h = (person[3] - person[1]) * 0.8
    else:
        fcx, fcy, h = src.w / 2, src.h / 2, src.h * 0.8
    pen = 0.0
    if h < 320:                     # tiny face: the window would be upscaled into mush
        pen += math.log(320 / h) * 2.0
    h = max(h, 320.0)
    w = h * aspect
    s = min(1.0, src.w / w, src.h / h)
    if s < 1:
        pen += math.log(1 / s) * 1.2
        w, h = w * s, h * s
    cx = clamp(fcx, w / 2, src.w - w / 2)
    cy = clamp(fcy + (0.5 - fy) * h, h / 2, src.h - h / 2)
    pen += (abs(cx - fcx) / w + abs(cy - (fcy + (0.5 - fy) * h)) / h) * 1.5
    return round(cx, 1), round(cy, 1), int(round(w)), int(round(h)), pen


def frame_detail(src, face, person, aspect):
    """No-face beat: a tall window below the face (outfit, hands) or the lower half of the person."""
    if person:
        x0, y0, x1, y1 = person[:4]
    else:
        x0, y0, x1, y1 = 0, 0, src.w, src.h
    top = (face[1] + face[3] * 1.15) if face else y0 + (y1 - y0) * 0.3
    h = clamp(min(src.h - top, (y1 - top) * 1.05), 320, src.h)
    w = h * aspect
    if w > src.w:
        w, h = src.w, src.w / aspect
    cx = clamp((face[0] + face[2] / 2) if face else (x0 + x1) / 2, w / 2, src.w - w / 2)
    cy = clamp(top + h / 2, h / 2, src.h - h / 2)
    return round(cx, 1), round(cy, 1), int(round(w)), int(round(h)), 0.0


def pad_box(src, p, padx=0.18, pady=0.10):
    x0, y0, x1, y1 = p[:4]
    w, h = x1 - x0, y1 - y0
    return [int(clamp(x0 - w * padx, 0, src.w)), int(clamp(y0 - h * pady, 0, src.h)),
            int(clamp(x1 + w * padx, 0, src.w)), int(clamp(y1 + h * pady, 0, src.h))]


# ----------------------------------------------------------------------------- scoring
def candidates(src, lo, hi, need):
    step = 1 / src.rate
    t = lo
    while t + need <= hi + 1e-6:
        yield round(t, 4)
        t += step


def person_has(person, face):
    """True when the matte's main component is the hero (her face centre lies inside it)."""
    cx, cy = face[0] + face[2] / 2, face[1] + face[3] / 2
    return person[0] <= cx <= person[2] and person[1] - face[3] <= cy <= person[3]


def hero_box(src, face, person):
    """Segmentation box around the hero: the person box limited to a band around the hero's face."""
    if not face:
        return pad_box(src, person) if person else None
    fx, fy, fw, fh = face[:4]
    band = [fx + fw / 2 - 2.6 * fw, fy - 0.9 * fh, fx + fw / 2 + 2.6 * fw, src.h]
    if person and person_has(person, face):
        band = [max(band[0], person[0] - 0.15 * fw), max(band[1], person[1] - 0.2 * fh),
                min(band[2], person[2] + 0.15 * fw), band[3]]
    return [int(clamp(band[0], 0, src.w)), int(clamp(band[1], 0, src.h)),
            int(clamp(band[2], 0, src.w)), int(clamp(band[3], 0, src.h))]


def score_slot(src, name, spec, t, hero, fix=None, check_shot=True):
    """(score, framing dict, notes) for a slot starting at source time t; None if unusable."""
    need = spec['need']
    if check_shot and not src.same_shot(t - 0.1, t + need + 0.1):   # sample / cut times are only ~1 frame exact
        return None
    a, b = src.at(t), src.at(t + need)
    face, face_end = src.face(t, hero), src.face(t + need, hero)
    person = a['person']
    kind = spec['kind']
    notes = []
    sharp = min(1.5, (face[6] / src.face_sharp_ref) if face else (a['sharp'] / src.sharp_ref))
    sc = 1.0 + 0.8 * sharp
    if face and any(f[5] != face[5] and f[3] > 0.8 * face[3] for f in a['faces']):
        sc -= 0.8                   # someone else as big as the hero: the beat is not about her
    if hero is not None and not face and any(f[3] > 0.06 * src.h for f in a['faces']):
        sc -= 1.0                   # only other people on screen
    if kind in ('shot', 'crop'):
        if not face:
            sc -= 6.0               # a face beat without the hero is worse than reusing a moment
            notes.append('no face')
        else:
            sc += 0.8 * face[4]
            if not face_end:
                sc -= 1.2
            elif abs((face_end[0] + face_end[2] / 2) - (face[0] + face[2] / 2)) > face[2] * 0.8:
                sc -= 0.6           # the face moves a lot inside the window
        if kind == 'shot':
            f = spec['f']
            if fix and 'zoom' in fix and face:      # a pinned zoom: re-centre the face for that zoom
                f = float(fix['zoom']) * (OUT / src.h) * face[3] / OUT
            cx, cy, z, pen = frame_shot(src, face, f, spec['pos'], person)
            fr = dict(cx=cx, cy=cy, zoom=z)
        else:
            cx, cy, w, h, pen = frame_crop(src, face, spec['f'], spec['aspect'], spec.get('fy', 0.45), person)
            fr = dict(cx=cx, cy=cy, w=w, h=h)
        sc -= pen
        if spec.get('cut') or spec.get('bokeh'):
            if person:
                fr['box'] = hero_box(src, face, person)
            elif spec.get('cut'):
                sc -= 2.0
                notes.append('no person matte')
            if spec.get('cut') and face and person and not person_has(person, face):
                sc -= 1.5
    elif kind == 'detail':
        if not person or (face and not person_has(person, face)):
            sc -= 1.0
        else:       # a full figure (outfit, legs, hands) reads as a detail; a close-up torso is just blur
            sc += 1.2 * clamp((person[3] - person[1]) / src.h - 0.55, 0, 0.45) / 0.45
        if face and face[3] > 0.16 * src.h:
            sc -= (face[3] / src.h - 0.16) * 10
        cx, cy, w, h, pen = frame_detail(src, face, person, spec['aspect'])
        if h < 420:
            sc -= 1.0
        fr = dict(cx=cx, cy=cy, w=w, h=h)
        sc += 0.4 * min(1.0, b['motion'] * 20)       # hands / walking read better than a still torso
    else:   # cut
        if not person or not face:
            return None
        fsrc = face[3] / src.h
        lo, hi = spec['fsrc']
        if fsrc < lo:
            sc -= (lo - fsrc) * 12
        elif fsrc > hi:
            sc -= (fsrc - hi) * 8
        if not person_has(person, face):
            sc -= 4.0               # the main matte is someone else
        if person[0] <= 2 or person[2] >= src.w - 2:
            sc -= 0.4               # cut by the frame edge
        if need and not src.at(t + need)['person']:
            sc -= 1.0
        sc += 0.6 * face[4]
        box = hero_box(src, face, person)
        fr = dict(box=box, y_cut=min(src.h, box[3]))
    if a['luma'] < 0.12:
        sc -= 1.0
        notes.append('dark')
    return sc, fr, notes


def framing_any(src, name, spec, t, hero, fix=None):
    """A pinned moment always gets a framing: the scored one when the window is clean, else the same framing
    without the shot check (the window crosses a source cut), else (cut-out slots with no hero / matte at t) the
    hero / person / whole-frame box. Never raises; the notes say what was relaxed."""
    r = score_slot(src, name, spec, t, hero, fix)
    if r and 'no face' not in r[2]:
        return r
    if hero is not None and src.at(t)['faces'] and not src.face(t, hero):
        # a moment the user chose where the phrase hero is absent: frame the biggest face that is there
        r2 = score_slot(src, name, spec, t, None, fix) or score_slot(src, name, spec, t, None, fix, check_shot=False)
        if r2:
            return r2[0] - 2, r2[1], [n for n in r2[2] if n != 'no face'] + ['framed on another person (not the hero)']
    if r:
        return r
    notes = []
    if not src.same_shot(t - 0.1, t + spec['need'] + 0.1):
        notes.append(f'window {t:.2f}-{t + spec["need"]:.2f}s crosses a source cut')
    r = score_slot(src, name, spec, t, hero, fix, check_shot=False)
    if r:
        return r[0] - 3, r[1], r[2] + notes
    a = src.at(t)
    face, person = src.face(t, hero), a['person']
    box = hero_box(src, face, person) if (face or person) else [0, 0, src.w, src.h]
    return -5.0, dict(box=box, y_cut=min(src.h, box[3])), notes + ['no hero face / person matte at this moment']


def heroes(features, fixes, two):
    people = features.get('people') or []
    if not people:
        return {'A': None, 'B': None}
    h = {'A': people[0]['id'], 'B': people[0]['id']}
    if two and len(people) > 1 and people[1]['presence'] >= 0.25 * people[0]['presence']:
        h['B'] = people[1]['id']
    for k, v in (fixes.get('heroes') or {}).items():
        h[k] = int(v)
    return h


def plan(features, fixes=None, split=None, two_heroes=False):
    fixes = fixes or {}
    srcs = {k: Src(k, v) for k, v in features['sources'].items()}
    hero = heroes(features, fixes, two_heroes)
    aliases = sorted(srcs)
    ranges = {}
    if len(aliases) >= 2:
        ranges['A'] = (aliases[0], 0.0, srcs[aliases[0]].dur, None)
        ranges['B'] = (aliases[1], 0.0, srcs[aliases[1]].dur, None)
    else:
        s = srcs[aliases[0]]
        mid = split if split else s.dur / 2
        near = [c for c in s.cuts if abs(c - mid) < s.dur * 0.15]
        if near and not split:
            mid = min(near, key=lambda c: abs(c - mid))
        ranges['A'] = (aliases[0], 0.0, s.dur, (0.0, mid))
        ranges['B'] = (aliases[0], 0.0, s.dur, (mid, s.dur))
    picked = []          # (alias, t, need)
    phrases, report, warnings = {}, {}, []
    for key in ('A', 'B'):
        alias, lo, hi, pref = ranges[key]
        src = srcs[alias]
        C, R = {}, {}
        hero_s = sum(1 for x in src.s if src.face(x['t'], hero[key]) or hero[key] is None) / src.rate
        gap_s = clamp(hero_s / (2 * len(SLOTS)), 0.25, MIN_GAP)
        fx = {}             # slot pins are applied after the automatic plan (see below), so a fix moves only its slot
        for name in ORDER:
            spec = SLOTS[name]
            need = spec['need']
            best = None
            who = hero['B'] if name == 'card1' else hero['A'] if name == 'card2' else hero[key]
            if name in fx and 't' in fx[name]:
                t = float(fx[name]['t'])
                r = score_slot(src, name, spec, t, who, fx[name]) or (0.0, {}, ['pinned (no analysis fit)'])
                best = (r[0], t, r[1], r[2] + ['pinned'])
            else:
                for t in candidates(src, lo, min(hi, src.dur - 0.05), need):
                    r = score_slot(src, name, spec, t, who)
                    if r is None:
                        continue
                    sc, fr, notes = r
                    if pref and not (pref[0] <= t < pref[1]):
                        sc -= 0.8
                    near, crowd = 0.0, 0    # the closest earlier pick + how crowded the spot already is
                    for (pa, pt, pn) in picked:
                        if pa != alias:
                            continue
                        gap = min(abs(t - pt), abs((t + need) - pt), abs(t - (pt + pn)))
                        overlap = t < pt + pn and pt < t + need
                        if overlap:
                            near = max(near, 2.0)
                            crowd += 1
                        elif gap < gap_s:
                            near = max(near, 1.2 * (1 - gap / gap_s))
                            crowd += 1
                    sc -= near + 0.7 * max(0, crowd - 1)
                    for x, y in NEIGH:
                        other = y if x == name else x if y == name else None
                        if other and other in R and R[other]['alias'] == alias and \
                                src.shot_id(R[other]['t']) == src.shot_id(t):
                            sc -= 0.5
                    if best is None or sc > best[0]:
                        best = (sc, t, fr, notes)
            if best is None:        # nothing fits (very short clip): the middle of the range
                t = round(max(lo, min(hi - need, (lo + hi) / 2)), 4)
                r = score_slot(src, name, dict(spec, need=0), t, who) or (0.0, {}, [])
                best = (r[0] - 5, t, r[1], r[2] + ['fallback'])
                warnings.append(f'{key}.{name}: no clean window, used {t:.2f} s')
            sc, t, fr, notes = best
            fr = dict(fr)
            for k2 in ('cx', 'cy', 'zoom', 'w', 'h', 'box', 'y_cut'):
                if k2 in fx.get(name, {}):
                    fr[k2] = fx[name][k2]
            picked.append((alias, t, max(need, 0.1)))
            R[name] = dict(alias=alias, t=t, hero=who, score=round(sc, 2), **fr, notes=notes)
            if (sc < -2.0 or set(notes) & {'no face', 'no person matte', 'fallback'}) and 'pinned' not in notes:
                warnings.append(f'{key}.{name}: weak pick at {t:.2f} s ({", ".join(notes) or "framing"})')
            C[name] = build(src, name, spec, alias, t, fr)
            if name == 'square' and fr.get('box'):
                C['square_bokeh'] = fr['box']       # portrait-mode look (person sharp, frame blurred)
        C['stickers'] = STICKERS[key]
        for c in ('card1', 'card2'):                # card texts come from texts.json, the crop from here
            C[c + '_crop'] = C.pop(c)
        # pins / framing overrides from fixes.json: only the named slots change, every other pick stays as planned
        for name, f in (fixes.get(key) or {}).items():
            if name not in SLOTS or not isinstance(f, dict):
                warnings.append(f'fixes.{key}.{name}: unknown slot, ignored (slots: {", ".join(ORDER)})')
                continue
            spec = SLOTS[name]
            who = hero['B'] if name == 'card1' else hero['A'] if name == 'card2' else hero[key]
            t = float(f['t']) if 't' in f else R[name]['t']
            t = round(clamp(t, 0.0, max(0.0, src.dur - 0.05)), 4)
            sc, fr, notes = framing_any(src, name, spec, t, who, f)
            fr = dict(fr)
            for k2 in ('cx', 'cy', 'zoom', 'w', 'h', 'box', 'y_cut'):
                if k2 in f:
                    fr[k2] = f[k2]
            if 'zoom' in fr:                    # keep a pinned zoom between cover and the 2.2x upscale cap
                zc = clamp(float(fr['zoom']), src.cover, ZMAX / (OUT / src.h))
                if abs(zc - float(fr['zoom'])) > 1e-6:
                    notes.append(f'zoom {fr["zoom"]} clamped to {zc:.2f}')
                fr['zoom'] = round(zc, 4)
            if 'w' in fr and 'h' in fr:         # crops: at least 320 px high, never larger than the source
                s_ = min(1.0, src.w / float(fr['w']), src.h / float(fr['h']))
                w_, h_ = float(fr['w']) * s_, float(fr['h']) * s_
                if h_ < 320:
                    w_, h_ = w_ * 320 / h_, 320.0
                fr['w'], fr['h'] = int(round(w_)), int(round(h_))
            R[name] = dict(alias=alias, t=t, hero=who, score=round(sc, 2), **fr, notes=notes + ['pinned'])
            ck = name + '_crop' if name in ('card1', 'card2') else name
            C[ck] = build(src, name, spec, alias, t, fr)
            if name == 'square':
                if fr.get('box'):
                    C['square_bokeh'] = fr['box']
                else:
                    C.pop('square_bokeh', None)
            if notes:
                warnings.append(f'{key}.{name}: pinned at {t:.2f} s: {"; ".join(notes)}')
        phrases[key] = C
        report[key] = R
    reuse = sum(1 for i, (a, t, n) in enumerate(picked) for (a2, t2, n2) in picked[:i] if a == a2 and abs(t - t2) < 0.3)
    if reuse > 8:
        warnings.append(f'{reuse} slot pairs reuse nearly the same moment (the hero is on screen only part of the clip)')
    cast = {'sources': {k: features['sources'][k]['path'] for k in aliases}, 'phrases': phrases}
    if hero['A'] is None:
        warnings.append('no faces found: framing follows the person matte / frame centre')
    return cast, {'heroes': hero, 'people': features.get('people', [])[:6],
                  'ranges': {k: [v[0], v[3] or [v[1], v[2]]] for k, v in ranges.items()}, 'picks': report,
                  'warnings': warnings}


def build(src, name, spec, alias, t, fr):
    """Framing -> the tuple edit.py / the original edit expects for this slot."""
    kind = spec['kind']
    if name == 'drop':
        return [alias, t, fr['cx'], fr['cy'], fr['zoom'], fr.get('box') or [0, 0, src.w, src.h]]
    if name == 'poster':
        z0, z1 = spec['zr']
        return [alias, t, fr['cx'], fr['cy'], fr['zoom'] * z0, fr['zoom'] * z1]
    if name == 'square':
        return [alias, t, fr['cx'], fr['cy'], fr['zoom']]
    if kind == 'shot':
        return [alias, t, fr['cx'], fr['cy'], fr['zoom']]
    if name == 'col_cut':
        return [alias, t, fr['box'], fr['y_cut'], []]
    if name == 'oval_cut':
        return [alias, t, fr['box']]
    return [alias, t, fr['cx'], fr['cy'], fr['w'], fr['h']]

