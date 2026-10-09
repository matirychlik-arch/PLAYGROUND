#!/usr/bin/env python3
"""Find the best N-second window of a music track for a film cut, and map its structure.

usage:
  music_window.py <track.mp3|wav|m4a> --len 30 [--after 60] [--before 150] [--start 106.4] [--json out.json]
  music_window.py <score.wav> --sections 0.3-1.7,2.5-9.9,10.3-17.9,19.55-19.95,20.3-27.9   (loudness check per section)

  --after/--before limit where the window may START (seconds). --start evaluates one fixed window instead of searching.
Prints the top candidates with: breath (dip) → DROP hit → LIFT (step up) → strong accents → final hit / outro,
all in film time (0 = window start), so cuts can be placed on them. Pure stdlib; decodes with macOS afconvert (or ffmpeg).
"""
import argparse, array, json, math, os, shutil, subprocess, sys, tempfile, wave

def decode(path, sr):
    tmp = tempfile.NamedTemporaryFile(suffix='.wav', delete=False).name
    if shutil.which('afconvert'):
        subprocess.run(['afconvert', '-f', 'WAVE', '-d', f'LEI16@{sr}', '-c', '1', path, tmp], check=True)
    elif shutil.which('ffmpeg'):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', path, '-ac', '1', '-ar', str(sr), tmp], check=True)
    else:
        sys.exit('need afconvert (macOS) or ffmpeg to decode audio')
    w = wave.open(tmp, 'rb'); a = array.array('h', w.readframes(w.getnframes())); w.close(); os.unlink(tmp)
    return [v / 32768.0 for v in a]

def envelopes(x, sr):
    def onepole(x, fc):
        k = math.exp(-2 * math.pi * fc / sr); y = 0.0; out = [0.0] * len(x)
        for i, v in enumerate(x): y = (1 - k) * v + k * y; out[i] = y
        return out
    lo = onepole(x, 120.0); hop = sr // 100; n = len(x) // hop
    E, B = [], []
    for f in range(n):
        s, e = f * hop, f * hop + hop
        E.append(10 * math.log10(1e-9 + sum(v * v for v in x[s:e]) / hop))
        B.append(10 * math.log10(1e-9 + sum(v * v for v in lo[s:e]) / hop))
    O = [0.0] + [max(0.0, E[i] - E[i - 1]) + max(0.0, B[i] - B[i - 1]) for i in range(1, n)]
    return E, O  # 100 fps

def mean(a): return sum(a) / max(1, len(a))

def analyse(E, O, fps=100):
    n = len(E); sm = [mean(E[max(0, i - 10):i + 10]) for i in range(n)]  # 0.2 s smoothing
    drops, lifts, accents = [], [], []
    for i in range(4 * fps, n - fps):
        dip = mean(sm[i - int(1.2 * fps):i - 5]); before = mean(sm[i - 4 * fps:i - int(1.5 * fps)]); after = mean(sm[i:i + fps // 2])
        if before - dip >= 3.5 and after - dip >= 6.0 and O[i] == max(O[i - 30:i + 30]):
            if not drops or i - drops[-1][0] > 3 * fps: drops.append((i, round(after - dip, 1)))
    for i in range(3 * fps, n - 3 * fps, 5):
        a, b = mean(sm[i - 2 * fps:i]), mean(sm[i:i + 2 * fps])
        if b - a >= 2.0 and all(abs(i - d) > 2 * fps for d, _ in drops):
            j = max(range(i - 30, i + 30), key=lambda k: O[k])
            if not lifts or j - lifts[-1][0] > 4 * fps: lifts.append((j, round(b - a, 1)))
    thr = sorted(O)[int(len(O) * 0.97)]
    for i in range(8, n - 8):
        if O[i] >= thr and O[i] == max(O[i - 8:i + 9]): accents.append(i)
    return sm, drops, lifts, accents

def describe(start, L, sm, drops, lifts, accents, fps=100):
    s, e = int(start * fps), int((start + L) * fps)
    rel = lambda i: round(i / fps - start, 2)
    d = [(rel(i), g) for i, g in drops if s <= i < e]; l = [(rel(i), g) for i, g in lifts if s <= i < e]
    acc = [rel(i) for i in accents if s <= i < e]
    seg = sm[s:e]; loud = mean(seg)
    tail_hit = [a for a in acc if L - 0.9 <= a <= L - 0.1]
    return {'start': round(start, 2), 'end': round(start + L, 2), 'mean_db': round(loud, 1), 'drops': d, 'lifts': l,
            'final_hit': tail_hit[-1] if tail_hit else None, 'accents': acc}

def score(desc, L):
    sc = desc['mean_db']
    if any(0.03 * L <= t <= 0.25 * L for t, _ in desc['drops']): sc += 8          # a breath + drop near the top
    if any(0.5 * L <= t <= 0.85 * L for t, _ in desc['lifts'] + desc['drops']): sc += 5   # a lift into the climax
    if desc['final_hit'] is not None: sc += 4                                       # a hit to end on
    return sc

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('track'); ap.add_argument('--len', type=float, default=30)
    ap.add_argument('--after', type=float, default=0); ap.add_argument('--before', type=float, default=None)
    ap.add_argument('--start', type=float, default=None); ap.add_argument('--json'); ap.add_argument('--top', type=int, default=3)
    ap.add_argument('--sections', default=None, help='loudness per range, e.g. 0.3-1.7,2.5-9.9,20.3-27.9')
    a = ap.parse_args()
    x = decode(a.track, 11025); dur = len(x) / 11025; E, O = envelopes(x, 11025); sm, drops, lifts, accents = analyse(E, O)
    if a.sections:
        for r in a.sections.split(','):
            x0, x1 = (float(v) for v in r.split('-')); seg = sm[int(x0 * 100):int(x1 * 100)]
            print(f'section {x0:>6.2f}–{x1:<6.2f}  mean {mean(seg):6.1f} dB')
        return
    print(f'track {dur:.1f}s · drops at {[round(i/100,2) for i,_ in drops]} · lifts at {[round(i/100,2) for i,_ in lifts]}')
    if a.start is not None:
        cands = [describe(a.start, a.len, sm, drops, lifts, accents)]
    else:
        hi = min(dur - a.len, a.before if a.before is not None else dur); cands = []
        t = a.after
        while t <= hi:
            d = describe(t, a.len, sm, drops, lifts, accents); d['score'] = round(score(d, a.len), 2); cands.append(d); t += 0.1
        cands.sort(key=lambda d: -d['score']); picked = []
        for c in cands:
            if all(abs(c['start'] - p['start']) > a.len * 0.4 for p in picked): picked.append(c)
            if len(picked) >= a.top: break
        cands = picked
    for c in cands:
        m, s = divmod(c['start'], 60)
        print(f"\nwindow {int(m)}:{s:04.1f}–{int((c['end'])//60)}:{c['end']%60:04.1f}  mean {c['mean_db']} dB  score {c.get('score','-')}")
        print(f"  drops (film time, gain dB): {c['drops']}\n  lifts: {c['lifts']}\n  final hit: {c['final_hit']}")
        print(f"  strong accents: {c['accents'][:40]}")
    if a.json: json.dump(cands, open(a.json, 'w'), indent=1); print(f'\nwrote {a.json}')

if __name__ == '__main__': main()
