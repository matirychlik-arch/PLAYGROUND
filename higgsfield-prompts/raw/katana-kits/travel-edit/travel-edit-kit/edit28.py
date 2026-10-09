#!/usr/bin/env python3
"""edit28.py - BRAZIL 28 s edit template (1916x1078 preset, 20 fps, 560 frames, 180 slots). Deps: ffmpeg, numpy, PIL, Chromium.
  texts  TEXTS.json TEXTDIR                 30 transparent text layers at the measured positions
  castv  REELDIR PLAN.json                  vibe mode: REELDIR/r1..r14.mp4 generated per REELS below -> slot plan
  analyze SRC.mp4 WORK                      footage mode: 5 fps scan (talking head / b-roll / captions / graphics)
  casts  WORK PLAN.json                     footage mode: plan from the scan (+ WORK/exclude.json [[t0,t1],..])
  qa     PLAN.json qa.jpg                   one labelled tile per content slot
  render PLAN.json PRESET.mp4 TEXTDIR OUT.mp4 [VIBE.png]
         per frame: luminance rhythm from the preset frame at the same index; colour from the vibe photo
         (vibe mode) or the preset itself (footage mode); preset FX frames kept; text + watermark; preset audio
  sheet  OUT.mp4 sheet.jpg                  4 fps contact sheet of the result
  patch  PLAN.json PATCH.json               apply {"S040":{"src":"r4.mp4","t":3.2,"z":1.2,"cx":.5,"cy":.45},..} to a plan
Kit v2 (Katana): fonts load from ./fonts next to this file (no runtime downloads); user text is HTML-escaped."""
import html, json, math, os, random, subprocess, sys, glob
import numpy as np

FPS = 20
# ---- TEMPLATE: id n section class fx text textf   (f0 = running sum of n; section "." = colour/FX slot whose
# frames come from the preset, its fx column then holds the colour; class e=eye c=close k=close(footage only)
# w=wide m=medium, "+" = continues the previous slot's moment; textf = frameIndex:layer[+layer],...)
TPL = """
001 1 . - black - -
002 3 hook m - - -
003 2 hook c - - -
004 2 hook w - - -
005 2 hook m - - -
006 2 hook m - - -
007 2 hook m - - -
008 2 hook m - - -
009 2 hook w - - -
010 3 detail c bleach:3 - -
011 7 detail c - - -
012 1 detail m+ smear:0:120 - -
013 5 ground m smear:10:30 - -
014 4 ground m - - -
015 2 ground w - - -
016 2 ground m smear:0:150 - -
017 1 . - 0xfbf4e8 - -
018 2 ground m smear:0:150 - -
019 1 ground m smear:0:150+dark:0.15 - -
020 4 district w - - -
021 2 district w - - -
022 1 district m smear:0:90 - -
023 1 district m+ - - -
024 1 district m - ar_big -
025 1 district m - arg_0 -
026 5 landmark w - - 0:arg_1,1:arg_2,2:arg_3,3:arg_4,4:arg_5
027 1 . - 0x0b0705 arg_6 -
028 3 portraits m smear:0:150+dark:0.2 - -
029 2 portraits m chroma:4 - -
030 1 portraits c - - -
031 1 portraits c - - -
032 1 portraits m - - -
033 1 . - black - -
034 3 portraits k - - -
035 4 texture m soft:6 - -
036 4 texture c - - -
037 1 texture m+ smear:0:150 - -
038 8 archive c - - -
039 1 archive m+ smear:0:150 - -
040 11 window m - - -
041 1 window m+ smear:0:150 - -
042 2 rooftops w - - -
043 1 . - black - -
044 5 rooftops w - - -
045 1 sky w - dean_scr -
046 8 sky w - dean_blunt -
047 3 sky m - dean_blunt -
048 1 sky m+ - blunt_only -
049 3 sky m+ - - -
050 4 play w - - -
051 3 play c+ - - -
052 1 play m - - -
053 1 play m+ smear:0:150 - -
054 1 . - black - -
055 2 icon m bleach:2 - -
056 8 icon m - - -
057 1 icon m - - -
058 1 icon m+ smear:0:150 - -
059 1 icon m - - -
060 1 . - 0xf2e6cf - -
061 2 eye e - - -
062 4 eye e - - -
063 1 eye e - - -
064 1 eye e - - -
065 1 eye e - - -
066 2 eye e - - -
067 5 night m - - -
068 3 night m+ - - -
069 1 . - black - -
070 1 night m - - -
071 1 . - 0xf0e2c4 - -
072 1 night m - - -
073 1 night w - - -
074 2 night m - - -
075 1 night m+ smear:0:150 - -
076 1 . - 0xf0e2c4 - -
077 1 dust m smear:0:40 diez_tall -
078 2 dust w - - 0:diez_wide,1:diez_wide2
079 1 dust m - - -
080 5 dust m - rio -
081 1 dust m+ smear:0:120 rio_ghost -
082 2 dust m smear:0:60 - -
083 3 dust m - - -
084 2 dust m - - -
085 2 dust m smear:0:150 - -
086 1 dust c - - -
087 5 alley m - - -
088 1 alley m - - -
089 1 alley m - - -
090 1 alley m - - -
091 2 alley m - - -
092 7 alley m+ - - -
093 1 alley m smear:0:150 - -
094 1 alley m soft:12 - -
095 1 . - white - -
096 3 . - 0x090605 - -
097 1 . - 0xf0e2c4 - -
098 5 sea w - - -
099 1 sea m+ scratch - -
100 1 sea c - - -
101 4 . - 0x07100a - -
102 1 . - black - -
103 12 smoke m - - -
104 2 . - black - -
105 2 smoke m - - -
106 6 smoke m - - -
107 4 . - black - -
108 2 smoke c - - -
109 1 smoke m - - -
110 1 smoke m bright:0.25 - -
111 10 smoke w - - -
112 2 . - 0x070a14 - -
113 1 . - black - -
114 3 . - black - -
115 2 . - black - -
116 1 facade m - - -
117 4 facade w - - -
118 1 . - 0x050a06 - -
119 3 facade m - - -
120 1 . - black - -
121 12 facade m - - -
122 10 lowangle m - - 0:scr_1a,1:scr_1a,2:scr_1,3:scr_1,4:scr_1,5:scr_1,6:scr_1,7:scr_1,8:scr_1,9:scr_1
123 2 lowangle m+ - scr_1 -
124 7 lowangle m+ - - 0:scr_2a,1:scr_2a,2:scr_2,3:scr_2,4:scr_2,5:scr_2,6:scr_2
125 5 lowangle m - scr_2 -
126 1 lowangle w - scr_3a -
127 1 lowangle m - scr_3 -
128 1 lowangle m - scr_3 -
129 1 lowangle m glitch scr_3 -
130 5 lowangle m - - 0:scr_3g
131 1 lowangle m glitch - -
132 1 lowangle m+ smear:0:150 - -
133 3 dusk w - - -
134 3 dusk w - - -
135 4 dusk m - - -
136 1 dusk m bright:0.3 - -
137 2 dusk w - - -
138 1 dusk m dark:0.2 - -
139 2 dusk w raw:colorbalance=rm=0.25:bm=0.15 - -
140 9 dusk w - - -
141 6 water w - - -
142 1 water m - - -
143 11 water m - - -
144 1 water m smear:0:150+dark:0.2 - -
145 3 train m smear:0:150 - -
146 1 . - black - -
147 2 train m smear:0:120 - -
148 1 . - 0x0a0a0a - -
149 1 train m smear:0:80 - -
150 6 train w - - -
151 1 train m glitch - -
152 2 action m+ smear:0:90 - -
153 10 action m echo:6 - -
154 8 action m echo:3+scratch - -
155 4 action m - - -
156 2 action m noise:40 - -
157 1 action m dark:0.25 - -
158 1 action m - - -
159 4 action m - - -
160 2 action m+ - - -
161 1 action m dark:0.3 - -
162 7 waves m - - -
163 1 waves m+ smear:0:150 - -
164 1 waves m smear:0:150 - -
165 1 waves m smear:20:150 - -
166 5 waves m - - -
167 1 waves m raw:colorbalance=rm=0.3 - -
168 1 waves w - - -
169 2 kiss m soft:6 - -
170 1 kiss m - - -
171 6 kiss w - - -
172 2 ending m smear:20:60 - -
173 2 ending m - - -
174 2 . - black - -
175 5 ending w - - -
176 2 ending m poster - -
177 2 ending w - - -
178 1 ending m - - -
179 1 ending m - - -
180 82 . - 0x050404 - END
"""
# ---- REELS: 14 generated multi-shot clips, shot order = prompt order, section:seconds (durations as written in the prompt)
REELS = """
R1 12 hook:1.5 hook:1.2 hook:1.2 hook:1.2 hook:1.2 hook:1.5 detail:2.5
R2 12 ground:2 ground:1 district:2.5 district:2 landmark:3
R3 12 portraits:1.5 portraits:1.2 portraits:1.2 portraits:1.2 portraits:1.5 texture:2 texture:2
R4 13 archive:2.5 window:4 rooftops:3 rooftops:3
R5 13 sky:3 sky:2 play:3 icon:5
R6 12 eye:3 night:3 night:3 night:3
R7 12 dust:2 dust:3 dust:2 dust:2.5 dust:2
R8 12 alley:3 alley:4 sea:4
R9 15 smoke:5 smoke:3 smoke:3 smoke:4
R10 14 facade:3 facade:4 lowangle:3 lowangle:4
R11 13 dusk:3 dusk:4 water:2 water:4
R12 10 train:2 train:8
R13 13 action:4 action:3 action:2 action:4
R14 15 waves:3 waves:2 kiss:3 ending:2 ending:2 ending:3
"""


def tpl():
    out, f0 = [], 0
    for ln in TPL.strip().splitlines():
        i, n, sec, cl, fx, tx, tf = ln.split()
        s = dict(id='S' + i, f0=f0, n=int(n), kind='color' if sec == '.' else 'content')
        f0 += int(n)
        if sec == '.':
            s['color'] = fx
        else:
            s.update(sec=sec, cls=cl.rstrip('+'), same=cl.endswith('+'), fx=[] if fx == '-' else fx.split('+'))
        if tx != '-':
            s['text'] = tx.split('+')
        if tf == 'END':                                  # end card: 6 boiling states, 3 frames each
            s['textf'] = {str(k): ['end_%d' % (k // 3 % 6)] for k in range(int(n))}
        elif tf != '-':
            s['textf'] = {a.split(':')[0]: a.split(':')[1].split('+') for a in tf.split(',')}
        out.append(s)
    assert f0 == 560 and len(out) == 180
    return out


def reels():
    return [[(a.split(':')[0], float(a.split(':')[1])) for a in ln.split()[2:]] for ln in REELS.strip().splitlines()]


def sh(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, **kw)


def probe(p):
    o = json.loads(sh(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                       'stream=width,height:format=duration', '-of', 'json', p]).stdout)
    return o['streams'][0]['width'], o['streams'][0]['height'], float(o['format']['duration'])


# ------------------------------------------------------------------ text layers
def texts(texts_json, outdir):
    T = json.load(open(texts_json))
    OUT = os.path.abspath(outdir); os.makedirs(OUT, exist_ok=True)
    FONTS = os.environ.get('E28_FONTS') or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
    for fn in ('Montserrat.ttf', 'Pinyon.ttf'):
        if not os.path.exists(os.path.join(FONTS, fn)):
            raise SystemExit('missing font %s in %s (kit not unpacked?)' % (fn, FONTS))
    E = lambda x: html.escape(str(x), quote=True)
    hexc = lambda k, d: T[k] if isinstance(T.get(k), str) and len(T[k]) == 7 and T[k][0] == '#' and all(c in '0123456789abcdefABCDEF' for c in T[k][1:]) else d
    A, B = hexc('color_a', '#e9a92a'), hexc('color_b', '#6aa9e0')
    CREAM, GOLD = '#f4ede2', hexc('accent', '#e9a92a')
    CSS = ("@font-face{font-family:Mont;src:url('%s/Montserrat.ttf')}@font-face{font-family:Pinyon;src:url('%s/Pinyon.ttf')}"
           "html,body{margin:0;width:1920px;height:1080px;background:transparent;overflow:hidden}.a{position:absolute}") % (FONTS, FONTS)
    div = lambda st, t: '<div class=a style="%s">%s</div>' % (st, t)
    mont = lambda w, fs, c, x='': 'font-family:Mont;font-weight:%d;font-size:%dpx;color:%s;line-height:1;white-space:nowrap;%s' % (w, fs, c, x)
    J = {'ar_big': div('left:0;width:1920px;top:338px;text-align:center;' + mont(500, 310, CREAM, 'letter-spacing:-4px'), E(T['big']))}
    W = T['title']; L = len(W); fs = min(120, int(1500 / (0.745 * L))); wid = 0.745 * fs * L
    grad = ('background:linear-gradient(103deg,%s 0,%s %dpx,%s %dpx,%s 100%%);-webkit-background-clip:text;'
            'background-clip:text;color:transparent;' % (A, A, int(wid * .5), B, int(wid * .5), B))
    for i, f in enumerate([.45, .55, .67, .78, .89, .78, 1.0]):
        J['arg_%d' % i] = div('left:%dpx;top:455px;width:%dpx;%s%s' % (int(960 - wid / 2), int(wid) + 40, mont(600, fs, '#fff', 'letter-spacing:1px;'), grad), E(W[:max(1, math.ceil(L * f))]))
    c1, c2 = T['credit']; c1, c2 = E(c1), E(c2)
    J['dean_blunt'] = div('left:1392px;top:731px;' + mont(600, 82, CREAM), c1) + div('left:1446px;top:821px;' + mont(300, 82, '#fbf8f2'), c2)
    J['dean_scr'] = div('left:1040px;top:780px;transform:scaleX(2.6);transform-origin:left;' + mont(500, 72, CREAM, 'letter-spacing:6px;opacity:.9'), E(T.get('scramble', T['credit'][0][:2] + T['credit'][1][:3])))
    J['blunt_only'] = div('left:1446px;top:821px;' + mont(300, 82, '#fbf8f2'), c2)
    q = E(T['squash'])
    J['diez_tall'] = div('left:118px;top:470px;transform:scale(0.42,2.05);transform-origin:left top;' + mont(400, 96, '#fff'), q)
    J['diez_wide'] = div('left:48px;top:288px;transform:scale(1.9,0.42);transform-origin:left top;' + mont(400, 92, '#fff', 'letter-spacing:22px'), q)
    J['diez_wide2'] = div('left:52px;top:330px;transform:scale(1.9,0.42);transform-origin:left top;' + mont(400, 92, '#fff', 'letter-spacing:22px;opacity:.85'), q)
    p1, p2 = T['place']; p1, p2 = E(p1), E(p2)
    J['rio'] = div('left:78px;top:384px;' + mont(400, 100, 'rgba(255,255,255,.92)', 'letter-spacing:3px'), p1) + div('left:30px;top:486px;' + mont(300, 56, GOLD), p2)
    J['rio_ghost'] = div('left:78px;top:384px;' + mont(400, 100, 'rgba(255,255,255,.55)', 'letter-spacing:3px'), p1)
    l1, l2 = T['script']; w1, w2 = l1.split(), l2.split()

    def scr(a, b, fade=None):
        g = 'text-shadow:0 0 8px rgba(255,255,255,.35);'
        s = div('left:214px;top:604px;font-family:Pinyon;font-size:50px;color:#f3eee8;%s' % g, E(a))
        if b:
            if fade:
                b = '%s<span style="opacity:.45">%s</span>' % (E(b[:-len(fade)]), E(fade))
            else:
                b = E(b)
            s += div('left:262px;top:640px;font-family:Pinyon;font-size:92px;color:#f3eee8;%s' % g, b)
        return s
    head = ' '.join(w2[:-1]) or w2[0]
    J.update(scr_1a=scr(w1[0], None), scr_1=scr(l1, None), scr_2a=scr(l1, head, fade=head[-3:]), scr_2=scr(l1, head),
             scr_3a=scr(l1, l2, fade=w2[-1]), scr_3=scr(l1, l2), scr_3g='<div style="opacity:.35">' + scr(l1, l2) + '</div>')
    J['wm'] = div('left:0;width:1920px;top:1040px;text-align:center;' + mont(600, 17, 'rgba(255,255,255,.82)', 'letter-spacing:0.5px'), E(T['watermark']))

    def loop(seed):
        r = random.Random(seed)
        pts = ['%.1f,%.1f' % (960 + 120 * math.cos(2 * math.pi * k / 59 * 1.15) + r.uniform(-2.5, 2.5),
                              470 + 46 * math.sin(2 * math.pi * k / 59 * 1.15) + r.uniform(-2.5, 2.5)) for k in range(60)]
        return ("<svg class=a style='left:0;top:0' width=1920 height=1080><polyline points='%s' fill='none' stroke='white' "
                "stroke-width='2.2' stroke-linecap='round' opacity='.9'/></svg>" % ' '.join(pts))
    e1, e2 = T['end']; e1, e2 = E(e1), E(e2)
    end = (div('left:0;width:1920px;top:640px;text-align:center;' + mont(300, 54, CREAM, 'letter-spacing:14px'), e1) +
           div('left:0;width:1920px;top:722px;text-align:center;' + mont(300, 30, GOLD, 'letter-spacing:6px'), e2) +
           div('left:0;width:1920px;top:1040px;text-align:center;' + mont(500, 15, 'rgba(255,255,255,.7)', 'letter-spacing:2.5px'), E(T.get('end_small', ''))))
    for k in range(6):
        J['end_%d' % k] = loop(k) + end
    chrome = os.environ.get('CHROME') or sorted(glob.glob('/ms-playwright/chromium-*/chrome-linux*/chrome') +
                                                glob.glob(os.path.expanduser('~/.cache/ms-playwright/chromium-*/chrome-linux*/chrome')))[-1]
    hp = os.path.join(OUT, '_t.html')
    for k, body in J.items():
        open(hp, 'w').write("<html><head><meta charset='utf-8'><style>%s</style></head><body>%s</body></html>" % (CSS, body))
        sh([chrome, '--headless=new', '--no-sandbox', '--disable-gpu', '--hide-scrollbars', '--force-device-scale-factor=1',
            '--default-background-color=00000000', '--window-size=1920,1080', '--virtual-time-budget=1500',
            '--screenshot=' + os.path.join(OUT, k + '.png'), 'file://' + hp])
    os.remove(hp)
    print('texts', len(J), 'layers ->', OUT)


# ------------------------------------------------------------------ vibe cast (generated reels -> slots)
def cuts(src):
    err = subprocess.run(['ffmpeg', '-hide_banner', '-i', src, '-vf', "select='gt(scene,0.3)',showinfo", '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    return [float(x.split(':')[1]) for x in err.split() if x.startswith('pts_time:')]


def shot_ranges(src, shots):
    dur = probe(src)[2]; scale = dur / sum(d for _, d in shots); c = cuts(src); out, t = [], 0.0
    for i, (sec, d) in enumerate(shots):
        end = t + d * scale if i < len(shots) - 1 else dur
        if i < len(shots) - 1 and c:
            near = min(c, key=lambda x: abs(x - end))
            if abs(near - end) < .7:
                end = near
        out.append(dict(sec=sec, src=os.path.abspath(src), t0=t + .08, t1=end - .08)); t = end
    return out


def castv(reeldir, plan_out):
    by = {}
    for k, shots in enumerate(reels(), 1):
        for s in shot_ranges(os.path.join(reeldir, 'r%d.mp4' % k), shots):
            by.setdefault(s['sec'], []).append(s)
    T = tpl(); plan = []
    secs = {}
    for s in T:
        if s['kind'] == 'content':
            secs.setdefault(s['sec'], []).append(s['id'])
    place = {}
    for sec, ids in secs.items():
        shots, cur = by[sec], {}
        for i, sid in enumerate(ids):
            j = min(len(shots) - 1, i * len(shots) // len(ids)); sh_ = shots[j]
            n = next(x['n'] for x in T if x['id'] == sid)
            t = cur.get(j, sh_['t0'])
            if t + n / FPS > sh_['t1']:
                t = sh_['t0']
            cur[j] = t + n / FPS
            cl = next(x['cls'] for x in T if x['id'] == sid)
            place[sid] = dict(src=sh_['src'], t=round(t, 3), z={'e': 1.6, 'c': 1.25}.get(cl, 1.0), cx=.5, cy=.45)
    for s in T:
        p = {k: s[k] for k in ('id', 'f0', 'n', 'kind', 'sec', 'fx', 'color', 'text', 'textf') if k in s}
        p.update(place.get(s['id'], {})); plan.append(p)
    json.dump(plan, open(plan_out, 'w'), indent=0)
    print('castv', len(place), 'content slots from', sum(map(len, by.values())), 'shots')


# ------------------------------------------------------------------ footage mode (any video -> slots)
def analyze(src, work):
    os.makedirs(work, exist_ok=True)
    a = np.frombuffer(sh(['ffmpeg', '-v', 'error', '-threads', '8', '-i', src, '-vf', 'fps=5,scale=160:90', '-an', '-f', 'rawvideo',
                          '-pix_fmt', 'rgb24', '-']).stdout, np.uint8).reshape(-1, 90, 160, 3).astype(np.float32) / 255
    L = a.mean(-1); lum = L.mean((1, 2)); blue = a[..., 2].mean((1, 2)) - a[..., 0].mean((1, 2))
    dist = np.abs(a - np.median(a[::25], 0)).mean((1, 2, 3)); diff = np.r_[1, np.abs(a[1:] - a[:-1]).mean((1, 2, 3))]
    reg = a[:, 52:82, 35:125]; cap = ((reg[..., 0] > reg[..., 1] * 1.35) & (reg.mean(-1) < .22)).mean((1, 2))
    br, dk = L > .82, L < .25; adj = np.zeros_like(br)
    for dy, dx in [(0, 2), (0, -2), (2, 0), (-2, 0)]:
        adj |= np.roll(np.roll(dk, dy, 1), dx, 2)
    wtxt = (br & adj)[:, 4:86, 4:156].mean((1, 2)); navy = ((a[..., 2] > a[..., 0] + .12) & (L < .32)).mean((1, 2))
    clean = ~(((blue > .06) & (lum < .3)) | (navy > .12)) & (cap < .08) & (wtxt < .0002) & (lum > .08)
    clean &= np.convolve(clean, np.ones(5), 'same') >= 5
    np.savez(os.path.join(work, 'scan.npz'), diff=diff, clean=clean, th=dist < .16, src=os.path.abspath(src))
    print('frames %d clean %.0f%% talking-head %.0f%%' % (len(a), clean.mean() * 100, (dist < .16).mean() * 100))


def runs(mask, diff, cut=.12):
    out, s = [], None
    for i in range(len(mask)):
        if mask[i] and (s is None or diff[i] < cut):
            s = i if s is None else s
        else:
            if s is not None and i - s >= 2:
                out.append((s, i))
            s = i if mask[i] else None
    if s is not None and len(mask) - s >= 2:
        out.append((s, len(mask)))
    return out


def casts(work, plan_out):
    S = np.load(os.path.join(work, 'scan.npz')); src = str(S['src']); clean = S['clean'].copy()
    ex = os.path.join(work, 'exclude.json')
    if os.path.exists(ex):
        for a, b in json.load(open(ex)):
            clean[int(a * 5):int(b * 5) + 1] = False
    th = [r for r in runs(clean & S['th'], S['diff']) if r[1] - r[0] >= 3]
    br = sorted([r for r in runs(clean & ~S['th'], S['diff']) if r[1] - r[0] >= 3], key=lambda r: r[0] - r[1])
    T = tpl(); content = [s for s in T if s['kind'] == 'content']
    bmap = dict(zip([s['id'] for s in content if s['cls'] == 'w'], br))
    step = max(1, len(th) // max(1, len(content) - len(bmap))); plan, k = [], 0
    for s in T:
        p = {key: s[key] for key in ('id', 'f0', 'n', 'kind', 'sec', 'fx', 'color', 'text', 'textf') if key in s}
        if s['kind'] == 'content':
            if s['id'] not in bmap and s['same'] and plan and plan[-1]['kind'] == 'content':
                q = plan[-1]; p.update(src=q['src'], t=round(q['t'] + q['n'] / FPS, 3), z=q['z'], cx=q['cx'], cy=q['cy'])
            else:
                if s['id'] in bmap:
                    r = bmap[s['id']]
                else:
                    r = th[min(len(th) - 1, k * step)]; k += 1
                p.update(src=src, t=round(r[0] / 5 + .2, 3), cx=.5, cy=.3)
                p['z'] = 3.0 if s['cls'] == 'e' else 2.0 if s['cls'] in 'ck' else 1.0 if s['id'] in bmap else [1.15, 1.45, 1.7][k % 3]
                if s['id'] in bmap:
                    p['cy'] = .5
                if s['cls'] == 'e':
                    p['cy'] = .27
        plan.append(p)
    json.dump(plan, open(plan_out, 'w'), indent=0)
    print('casts content %d b-roll %d talking-head runs %d' % (len(content), len(bmap), len(th)))


def qa(plan_json, out_jpg):
    from PIL import Image, ImageDraw
    P = [p for p in json.load(open(plan_json)) if p['kind'] == 'content']; tiles = []
    for p in P:
        im = Image.frombytes('RGB', (240, 135), sh(['ffmpeg', '-v', 'error', '-ss', '%.3f' % (p['t'] + p['n'] / 40), '-i', p['src'], '-frames:v', '1',
                                                    '-vf', 'scale=240:135', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']).stdout)
        ImageDraw.Draw(im).text((4, 4), '%s %s %.1fs' % (p['id'], p.get('sec', ''), p['t']), fill=(255, 255, 0)); tiles.append(im)
    sheet = Image.new('RGB', (12 * 242, ((len(tiles) + 11) // 12) * 137))
    for i, im in enumerate(tiles):
        sheet.paste(im, ((i % 12) * 242, (i // 12) * 137))
    sheet.save(out_jpg, quality=85); print('qa', out_jpg, len(tiles))


# ------------------------------------------------------------------ render
M = np.array([[.4124, .3576, .1805], [.2126, .7152, .0722], [.0193, .1192, .9505]], np.float32)
WP = np.array([.95047, 1., 1.08883], np.float32)


def to_lab(rgb):
    c = rgb.astype(np.float32) / 255
    c = np.where(c > .04045, ((c + .055) / 1.055) ** 2.4, c / 12.92)
    xyz = c @ M.T / WP
    f = np.where(xyz > .008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def to_rgb(lab):
    fy = (lab[..., 0] + 16) / 116
    f = np.stack([fy + lab[..., 1] / 500, fy, fy - lab[..., 2] / 200], -1)
    c = np.clip(np.where(f ** 3 > .008856, f ** 3, (f - 16 / 116) / 7.787) * WP @ np.linalg.inv(M).T, 0, 1)
    c = np.where(c > .0031308, 1.055 * c ** (1 / 2.4) - .055, 12.92 * c)
    return (np.clip(c, 0, 1) * 255 + .5).astype(np.uint8)


def look(src, ref, vibe_ab=None, pull=.5):
    """L mean/std from the preset frame; a/b from the preset (footage mode) or source pulled toward the vibe palette"""
    s, r = to_lab(src), to_lab(ref); o = s.copy()
    for c in range(3):
        if c == 0 or vibe_ab is None:
            m_, sd = r[..., c].mean(), r[..., c].std()
        else:
            vm, vs = vibe_ab[c - 1]
            m_, sd = (1 - pull) * s[..., c].mean() + pull * vm, (1 - pull) * s[..., c].std() + pull * vs
        o[..., c] = (s[..., c] - s[..., c].mean()) * (sd + 1e-6) / (s[..., c].std() + 1e-6) + m_
    return to_rgb(o)


def fx_chain(fx):
    out = []
    for e in fx or []:
        k, *a = e.split(':')
        if k == 'smear':
            out.append('dblur=angle=%s:radius=%d' % (a[0] if a else 0, min(int(a[1]) if len(a) > 1 else 90, 80)))
        elif k == 'echo':
            out.append('tmix=frames=%s' % a[0])
        elif k == 'soft':
            out.append('gblur=sigma=%s' % (a[0] if a else 2))
        elif k == 'chroma':
            v = int(a[0]) if a else 6; out.append('rgbashift=rh=%d:bh=%d' % (v, -v))
        elif k == 'glitch':
            out.append('rgbashift=rh=-28:bh=28:gv=6,noise=alls=40:allf=t')
        elif k == 'poster':
            out.append("lutrgb=r='floor(val/56)*56':g='floor(val/56)*56':b='floor(val/56)*56'")
        elif k == 'noise':
            out.append('noise=alls=%s:allf=t' % (a[0] if a else 30))
        elif k == 'bleach':
            kf = int(a[0]) if a else 3
            out.append("eq=brightness='max(0,0.45*(1-n/%d))':contrast='min(1,0.55+0.45*n/%d)':eval=frame" % (kf, kf))
    return ','.join(out)


def src_frames(p, W, H):
    z = p.get('z', 1.0); sw, shh = int(W * z) // 2 * 2, int(H * z) // 2 * 2
    vf = ("fps=%d,scale=%d:%d:force_original_aspect_ratio=increase:flags=lanczos,crop=%d:%d,crop=%d:%d:'(iw-%d)*%f':'(ih-%d)*%f'"
          % (FPS, sw, shh, sw, shh, W, H, W, min(max(p.get('cx', .5), 0), 1), H, min(max(p.get('cy', .5), 0), 1)))
    extra = p.get('vf') or fx_chain(p.get('fx'))
    vf += (',' + extra) if extra else ''
    fr = np.frombuffer(sh(['ffmpeg', '-v', 'error', '-ss', '%.3f' % p['t'], '-i', p['src'], '-vf', vf, '-frames:v', str(p['n']),
                           '-an', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']).stdout, np.uint8).reshape(-1, H, W, 3)
    return np.concatenate([fr, np.repeat(fr[-1:], p['n'] - len(fr), 0)]) if len(fr) < p['n'] else fr


def render(plan_json, preset, textdir, out, vibe=None):
    from PIL import Image
    from concurrent.futures import ThreadPoolExecutor
    P = json.load(open(plan_json)); W, H, _ = probe(preset); cache = {}
    vab = None
    if vibe:
        v = to_lab(np.asarray(Image.open(vibe).convert('RGB').resize((480, 270))))
        vab = [(v[..., c].mean(), v[..., c].std()) for c in (1, 2)]

    def layer(nm):
        if nm not in cache:
            a = np.asarray(Image.open(os.path.join(textdir, nm + '.png')).convert('RGBA').resize((W, H), Image.LANCZOS)).astype(np.float32)
            cache[nm] = (a[..., :3], a[..., 3:] / 255)
        return cache[nm]
    comp = lambda f, l: (f * (1 - l[1]) + l[0] * l[1]).astype(np.uint8)
    dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', preset, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (W, H), '-r', str(FPS),
                            '-i', '-', '-i', preset, '-map', '0:v', '-map', '1:a?', '-c:v', 'libx264', '-crf', '16', '-preset', 'medium',
                            '-pix_fmt', 'yuv420p', '-c:a', 'copy', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    end_f0 = max(p['f0'] for p in P); ex = ThreadPoolExecutor(4)
    futs = {p['id']: ex.submit(src_frames, p, W, H) for p in P if p['kind'] == 'content'}
    for p in P:
        refs = [np.frombuffer(dec.stdout.read(W * H * 3), np.uint8).reshape(H, W, 3) for _ in range(p['n'])]
        if p['kind'] == 'content':
            g = futs.pop(p['id']).result(); frames = [look(g[i], refs[i], vab) for i in range(p['n'])]
        elif p['f0'] == end_f0 or p.get('text') or p.get('textf'):
            col = [5, 4, 8] if vab else [5, 4, 4]
            if not vab and str(p.get('color', '')).startswith('0x'):
                c = int(p['color'], 16); col = [c >> 16 & 255, c >> 8 & 255, c & 255]
            frames = [np.zeros((H, W, 3), np.uint8) + np.array(col, np.uint8) for _ in range(p['n'])]
        else:
            frames = [look(r, r, vab, .8) for r in refs] if vab else refs
        for i in range(p['n']):
            f = frames[i]
            for nm in list(p.get('text') or []) + list((p.get('textf') or {}).get(str(i), [])):
                f = comp(f, layer(nm))
            if p['f0'] != end_f0:
                f = comp(f, layer('wm'))
            enc.stdin.write(np.ascontiguousarray(f).tobytes())
    dec.wait(); enc.stdin.close(); enc.wait(); print('rendered ->', out)


def patch(plan_json, patch_json):
    """agent-side slot fixes, kept as a separate file so castv/casts stay re-runnable"""
    P = json.load(open(plan_json)); X = json.load(open(patch_json)); by = {p['id']: p for p in P}; base = os.path.dirname(os.path.abspath(plan_json))
    for sid, ch in X.items():
        if sid not in by or by[sid]['kind'] != 'content':
            raise SystemExit('patch: %s is not a content slot' % sid)
        for k, v in ch.items():
            if k not in ('src', 't', 'z', 'cx', 'cy'):
                raise SystemExit('patch: field %s not allowed' % k)
            by[sid][k] = os.path.abspath(os.path.join(base, v)) if k == 'src' else float(v)
    json.dump(P, open(plan_json, 'w'), indent=0); print('patch', len(X), 'slots')


def sheet(video, out_jpg):
    sh(['ffmpeg', '-v', 'error', '-y', '-i', video, '-vf', 'fps=4,scale=240:-2,tile=14x8', '-frames:v', '1', out_jpg]); print('sheet', out_jpg)


if __name__ == '__main__':
    {'texts': texts, 'castv': castv, 'analyze': analyze, 'casts': casts, 'qa': qa, 'render': render, 'sheet': sheet, 'patch': patch}[sys.argv[1]](*sys.argv[2:])
