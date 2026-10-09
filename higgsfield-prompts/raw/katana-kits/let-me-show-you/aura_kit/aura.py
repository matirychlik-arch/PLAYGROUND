#!/usr/bin/env python3
"""aura-recreate sandbox kit: every tool the aura-recreate pipeline needs, run inside the Higgsfield sandbox.

Needs only what the sandbox ships: /usr/local/bin/python3 (numpy, Pillow, onnxruntime), ffmpeg/ffprobe, curl, unzip.
Never pip-install anything. The sandbox may be wiped between calls, so every command downloads what it needs from
the Higgsfield CDN (sha256-checked) and uploads its result in the same call.

  python3 aura.py split  PHOTO OUT [--seam X[,X2] | --seam-y Y[,Y2]] [--keep i,j] [--put URL]...
        collage photo -> OUT/panel_1.jpg ... panel_N.jpg (left->right; stacked only with --seam-y) + OUT/preview.jpg
        (seams boxed in red, panels numbered). Side-by-side seams are auto-detected; a single photo is reported as kind
        "single". With --put (one per kept panel, in --keep order) the panels are uploaded.
  python3 aura.py crop   PHOTO OUT.jpg --box x0,y0,x1,y1 [--put URL]       pixels or fractions; e.g. a tighter crop
  python3 aura.py qa     CONFIG.json OUT [--detail]
        reference|ours pairs at 4 moments inside the range the edit uses, per shot -> OUT/qa_1.jpg (A-E), OUT/qa_2.jpg (F-I);
        --detail: ours only, one 960x540 frame per shot (middle of the used range) -> OUT/detail_1.jpg (A-E),
        OUT/detail_2.jpg (F-I), plus the user's photo as an extra tile when CONFIG has "photo": "<url>"
  python3 aura.py sheet  VIDEO OUT.jpg [--n 8] [--cols 4] [--frames f1,f2,...] [--crop x0,y0,x1,y1]
        contact sheet of any video (e.g. the uploaded compare.mp4), sized for image_paths (<= ~250 KiB); --crop zooms
        into a full-resolution region with a coordinate grid
  python3 aura.py tiles  SHOT OUT.jpg [--every N] [--zoom x0,y0,x1,y1]
        registry-driver frames (incl. the last of the forward pass) labelled 'driver n = ref r'; --zoom = full-res
        region with a 1920x1080 coordinate grid (measure jewellery positions directly)
  python3 aura.py clean  SHOT SPEC.json OUT [--zoom x0,y0,x1,y1] [--put URL]
        paint jewellery out of the registry driver. Without --put: fast preview only (OUT/prev.jpg; with --zoom it shows
        before|after pairs of that region at 6 frames), prints PREVIEW_DONE. With --put: the full cleaned driver
        OUT/drive_<SHOT>_clean.mp4 + prev.jpg, uploaded, prints CLEAN_DONE.
  python3 aura.py render CONFIG.json OUT
        full render: OUT/edit.mp4 (1920x1080/25, 14.2 s, reference audio) + OUT/compare.mp4 (reference on top,
        ours below), probes, PUTs both. Prints RUN_DONE on success.
  python3 aura.py vertical EDIT OUT.mp4 [--mode fill|crop] [--put URL]
        9:16 1080x1920 version of a finished edit (fill = blurred background, keeps everything; crop = centre crop)

PHOTO / VIDEO may be an https URL or a local path.
CONFIG.json: {"clips": {"A": "<genjutsu result_url>", ..., "I": "..."},
              "put_edit": "<media_upload upload_url>", "put_compare": "<media_upload upload_url>",
              "label": "HIGGSFIELD GENJUTSU",            # optional caption on the bottom half of compare.mp4
              "plan_overrides": {...}}                    # optional, deep-merged into plan_template.json
qa needs only "clips" (any subset of A..I), the optional "plan_overrides" and, for --detail, the optional "photo"."""
import concurrent.futures as cf
import hashlib, json, os, re, shutil, subprocess, sys, time, zipfile

KIT = os.path.dirname(os.path.abspath(__file__))
CDN = 'https://d2ol7oe51mr4n9.cloudfront.net/user_3BtsEcww7blE0e9EKFuXmUaobas/'
ASSETS = {
    'ref': (CDN + '5c6833fc-7d77-4482-8a90-7210f8586aa3.mp4', '22915541b21bcaef1054bd222043651e3a59475cea5125eab9dd59159bb635f3'),
    'models': (CDN + 'e2f0a660-a4b7-43f8-bc87-13f4318d8ed0.zip', '0b77645622783342bac65e615be317bd1330e1d401ca14821bd0505c0121b42f'),
    'A': (CDN + 'f6f9769c-0d66-47cc-9f56-cb54d8f4937a.mp4', '8cc1864a21cb075777bbbd9ff2d2906ca1c4dd5f75b26ed1fa5af912958a437d'),
    'B': (CDN + '6b6bb6f5-e9e7-42e4-be9d-e364a65f7e38.mp4', 'edec51c01eba433391fc8cebc466d08c4a220149afcf0c9bc2ceaa127e4ef4b2'),
    'C': (CDN + 'fae7bdf3-dded-4c80-bfc7-9474affcf975.mp4', '4f703099619cbca7546a8bb48e3e55a4fec71d0d8f8e2bf7f28afe13a64915f0'),
    'D': (CDN + '8934a3c8-c625-436d-b6b9-ceb6b21f05f2.mp4', 'fab643c7b907f96aa2986891d29402921eaa4ca3e560f3e1688ef3971ce91b83'),
    'E': (CDN + '4faf5fe0-7a59-41e6-bb22-3a36f4e6440b.mp4', 'd55f8d732d31e5578310e66b9ead0e5e3ee97cfc7b7c59fc118d627816f65520'),
    'F': (CDN + 'ca0005a9-b018-49b3-b262-bb003cae58d1.mp4', 'b1e7faeda2e0c8e4864fc56884cf615bc5543d3735bc9ed4d58253218c861d64'),
    'G': (CDN + 'b38d59be-67df-432b-9f8d-7cb276b8d708.mp4', 'd925c816f46e6e0dbc3350e6f0e241b19e90da75a5e513d9312b85295403ea9e'),   # choker + earrings painted out (clean_specs/G.json)
    'H': (CDN + '5acd3404-ea95-4ff6-8a6b-b52088e8d196.mp4', '1bf23c2e4d700ccac3f3798993ed873f9ed5f2cc081201017069bd63590d161d'),
    'I': (CDN + '36781d47-1bbb-4cc3-8801-09a0e5e79fd1.mp4', 'c5228eb96120c9a36409fb4d9b0ccdf949a90a302f95aff2867595b522d71134'),
}
SHOTS = 'ABCDEFGHI'
# clean reference range (25 fps) each bundled driver was cut from; ping-pong padded (fwd, back, fwd...) to >= 80 frames.
# Driver frame n = reference frame SEQ[n]; during the first forward pass that is FIRST + n.
SH = {'A': (0, 73), 'B': (77, 89), 'C': (94, 128), 'D': (133, 160), 'E': (165, 195), 'F': (199, 230), 'G': (235, 265),
      'H': (270, 302), 'I': (306, 332)}
LABEL_FONT = '/usr/share/fonts/truetype/higgsfield/Montserrat-ExtraBold.ttf'
T0 = time.time()


def log(*a):
    print('[%5.1fs]' % (time.time() - T0), *a, flush=True)


def die(msg):
    print('ERROR: ' + msg, flush=True); sys.exit(1)


def sh(*a, **kw):
    return subprocess.run(list(a), check=True, **kw)


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''): h.update(chunk)
    return h.hexdigest()


def fetch(src, dst, sha=None):
    """https URL or local path -> dst; verifies sha256 when given."""
    if re.match(r'https?://', src):
        r = subprocess.run(['curl', '-fsSL', '--retry', '3', '--retry-delay', '2', '-o', dst, src], capture_output=True, text=True)
        if r.returncode: die('download failed (%s): %s %s' % (r.returncode, src, r.stderr.strip()[:200]))
    else:
        if not os.path.exists(src): die('no such file: ' + src)
        if os.path.abspath(src) != os.path.abspath(dst): shutil.copy(src, dst)
    if sha and sha256(dst) != sha: die('sha256 mismatch for %s (%s): the CDN copy changed' % (dst, src))
    return dst


def fetch_many(jobs):
    """jobs: [(src, dst, sha)] downloaded in parallel."""
    with cf.ThreadPoolExecutor(8) as ex:
        for f in [ex.submit(fetch, *j) for j in jobs]: f.result()


def put(path, url, ctype):
    if not url.startswith('https://upload.higgsfield.ai/'): die('not a media_upload upload_url: ' + url[:60])
    r = subprocess.run(['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', '-X', 'PUT', '-H', 'Content-Type: ' + ctype,
                        '-H', 'If-None-Match: *', '--retry', '2', '--upload-file', path, url], capture_output=True, text=True)
    code = r.stdout.strip()
    print('PUT %s %s' % (os.path.basename(path), code), flush=True)
    return code == '200'


def deep_merge(base, over):
    for k, v in over.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict): deep_merge(base[k], v)
        else: base[k] = v
    return base


def load_plan(cfg):
    plan = json.load(open(os.path.join(KIT, 'plan_template.json')))
    return deep_merge(plan, cfg.get('plan_overrides') or {})


def arg(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def font(size):
    from PIL import ImageFont
    for p in (LABEL_FONT, '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'):
        if os.path.exists(p): return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def tag(img, text, size=18, bottom=False):
    """small white-on-black label in the top-left (or bottom-left) corner (PIL image, in place)"""
    from PIL import ImageDraw
    d = ImageDraw.Draw(img); f = font(size)
    y = img.height - size - 12 if bottom else 4
    x0, y0, x1, y1 = d.textbbox((6, y), text, font=f)
    d.rectangle((x0 - 4, y0 - 3, x1 + 4, y1 + 3), fill=(0, 0, 0)); d.text((6, y), text, font=f, fill=(255, 255, 255))
    return img


def save_small(img, path, budget=250 * 1024):
    """JPEG under `budget` bytes, so 2 sheets always fit image_paths' 512 KiB total (lower quality first, then downscale)"""
    from PIL import Image
    while True:
        for q in (85, 78, 70, 62, 55, 48):
            img.save(path, quality=q, optimize=True)
            if os.path.getsize(path) <= budget: return path
        img = img.resize((max(1, int(img.width * 0.85)), max(1, int(img.height * 0.85))), Image.LANCZOS)


def frames_at(video, idx, size):
    """decoded frames at the given frame indices (any order, duplicates ok) -> {index: PIL image}"""
    from PIL import Image
    want = sorted(set(int(i) for i in idx))
    expr = '+'.join('eq(n\\,%d)' % i for i in want)
    w, h = size
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', video, '-vf', "select='%s',scale=%d:%d" % (expr, w, h), '-fps_mode', 'passthrough',
                          '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True, check=True).stdout
    n = len(raw) // (w * h * 3)
    imgs = [Image.frombytes('RGB', (w, h), raw[i * w * h * 3:(i + 1) * w * h * 3]) for i in range(n)]
    out = {}
    for k, i in enumerate(want):
        out[i] = imgs[min(k, n - 1)] if n else Image.new('RGB', (w, h), (255, 0, 255))
    return out


def video_size(video):
    r = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', video],
                       capture_output=True, text=True).stdout.strip().split(',')
    return int(r[0]), int(r[1])


def parse_box(v):
    b = [int(round(float(x))) for x in v.split(',')]
    if len(b) != 4 or b[2] <= b[0] or b[3] <= b[1]: die('box must be x0,y0,x1,y1 with x1>x0, y1>y0: %r' % v)
    return b


def grid_crop(img, box, scale, grid=True):
    """crop box (source px) from a PIL image, scale it, and draw a coordinate grid in SOURCE pixels:
    faint lines every 50 px, labelled every 100 px, so positions can be read off directly in 1920x1080 coordinates."""
    from PIL import Image, ImageDraw
    x0, y0, x1, y1 = box
    c = img.crop(box).resize((max(1, round((x1 - x0) * scale)), max(1, round((y1 - y0) * scale))), Image.LANCZOS)
    if not grid: return c
    d = ImageDraw.Draw(c, 'RGBA'); f = font(13)
    for gx in range((x0 // 50 + 1) * 50, x1, 50):
        X = round((gx - x0) * scale); d.line((X, 0, X, c.height), fill=(255, 255, 0, 110 if gx % 100 == 0 else 55), width=1)
        if gx % 100 == 0: d.text((X + 2, 2), str(gx), font=f, fill=(255, 255, 0, 230))
    for gy in range((y0 // 50 + 1) * 50, y1, 50):
        Y = round((gy - y0) * scale); d.line((0, Y, c.width, Y), fill=(0, 255, 255, 110 if gy % 100 == 0 else 55), width=1)
        if gy % 100 == 0: d.text((2, Y + 2), str(gy), font=f, fill=(0, 255, 255, 230))
    return c


def probe_frames(video):
    r = subprocess.run(['ffprobe', '-v', 'error', '-count_packets', '-select_streams', 'v:0', '-show_entries', 'stream=nb_read_packets',
                        '-of', 'csv=p=0', video], capture_output=True, text=True)
    try: return int(r.stdout.strip().split(',')[0])
    except ValueError: return 0


# ---------------------------------------------------------------- split
def args_all(name):
    return [sys.argv[i + 1] for i, v in enumerate(sys.argv[:-1]) if v == name]


def detect_seams(g, near=None):
    """Vertical panel seams of a side-by-side collage. g: float32 grayscale (h x w).
    A seam is perfectly straight over the full height, so the image is box-blurred along it first: the seam survives,
    slanted natural edges (hair, limbs) smear out; frac = share of rows with a > 3 grey-level step between x and x+1.
    Measured on the mint diptych: seam 0.94, best natural edge 0.51. Also catches flat gutters (white separators).
    near: approximate seam x positions (from looking at the photo), each refined within +-40 px.
    Returns (cuts, runner_up): cuts = [(a, b, score)], columns a..b are dropped between panels."""
    import numpy as np
    h, w = g.shape
    k = 31; c = np.cumsum(np.pad(g, ((k // 2 + 1, k // 2), (0, 0)), mode='edge'), axis=0); gv = (c[k:] - c[:-k]) / k
    frac = (np.abs(np.diff(gv, axis=1)) > 3).mean(0)
    flat = g.std(0) < 2.0
    cuts = []; x = int(w * 0.08)
    while x < w - int(w * 0.08):
        if flat[x]:
            s0 = x
            while x < w and flat[x]: x += 1
            if x - s0 >= 2: cuts.append((s0 - 1, x + 1, 1.0))
        x += 1
    if near:
        for n in near:
            if any(a - 12 <= n <= b + 12 for a, b, _ in cuts): continue
            lo, hi = max(1, n - 40), min(w - 2, n + 40)
            x = lo + int(np.argmax(frac[lo:hi])); cuts.append((x - 1, x + 3, round(float(frac[x]), 3)))
        return sorted(cuts), None
    lo, hi = int(w * 0.08), int(w * 0.92)
    peaks = []
    for x in (np.argsort(-frac[lo:hi]) + lo):
        if frac[x] < 0.8: break
        if all(abs(x - p) > w * 0.12 for p in peaks) and not any(a - 12 <= x <= b + 12 for a, b, _ in cuts): peaks.append(int(x))
    keep = np.ones(w, bool)
    for p in peaks: keep[max(0, p - 12):p + 13] = False
    for a, b, _ in cuts: keep[max(0, a - 12):b + 13] = False
    runner = float(frac[lo:hi][keep[lo:hi]].max()) if keep[lo:hi].any() else 0.0
    cuts += [(p - 1, p + 3, round(float(frac[p]), 3)) for p in peaks if frac[p] >= 1.4 * runner]   # drop blended columns
    return sorted(cuts), round(runner, 3)


def cmd_split():
    """split PHOTO OUT [--seam X[,X2..] | --seam-y Y[,Y2..]] [--keep i,j] [--put URL]...
    Call 1 (no --put): detect and preview. Call 2: same args + --keep + one --put per kept panel (in order)."""
    import numpy as np
    from PIL import Image, ImageDraw
    src, out = sys.argv[2], sys.argv[3]; os.makedirs(out, exist_ok=True)
    ext = os.path.splitext(src.split('?')[0])[1] or '.img'
    p = fetch(src, os.path.join(out, 'source' + ext))
    im = Image.open(p).convert('RGB'); W_, H_ = im.size
    g = np.asarray(im.convert('L'), np.float32)
    sx, sy = arg('--seam'), arg('--seam-y')
    if sy:                                    # horizontal seams (stacked panels): only on request, never auto
        axis = 0; cuts, runner = detect_seams(g.T, [int(round(float(v))) for v in sy.split(',')])
    elif sx:
        axis = 1; cuts, runner = detect_seams(g, [int(round(float(v))) for v in sx.split(',')])
    else:
        axis = 1; cuts, runner = detect_seams(g) if W_ / H_ > 1.15 else ([], None)
    pv = im.copy()
    if not cuts:
        pv.thumbnail((960, 960)); save_small(pv, os.path.join(out, 'preview.jpg'))
        print(json.dumps({'kind': 'single', 'size': [W_, H_], 'runner_up': runner, 'preview': os.path.join(out, 'preview.jpg'),
                          'hint': 'if this IS a collage, rerun with --seam X[,X2] (or --seam-y Y) at the approximate seam(s)'})); return
    L = W_ if axis == 1 else H_
    edges = [0] + [v for a, b, _ in cuts for v in (a, b)] + [L]
    spans = [(edges[i], edges[i + 1]) for i in range(0, len(edges), 2) if edges[i + 1] - edges[i] > 16]
    d = ImageDraw.Draw(pv); lw = max(3, max(W_, H_) // 400)
    for a, b, _ in cuts:
        d.rectangle((a - 2, 0, b + 2, H_) if axis == 1 else (0, a - 2, W_, b + 2), outline=(255, 0, 0), width=lw)
    panels = []
    for i, (a, b) in enumerate(spans, 1):
        box = (a, 0, b, H_) if axis == 1 else (0, a, W_, b)
        pth = os.path.join(out, 'panel_%d.jpg' % i); im.crop(box).save(pth, quality=95)
        panels.append({'n': i, 'file': pth, 'size': [box[2] - box[0], box[3] - box[1]]})
        tx, ty = ((a + 12, 12) if axis == 1 else (12, a + 12))
        d.rectangle((tx, ty, tx + 60, ty + 60), fill=(0, 0, 0)); d.text((tx + 18, ty + 6), str(i), font=font(44), fill=(255, 255, 0))
    pv.thumbnail((960, 960)); save_small(pv, os.path.join(out, 'preview.jpg'))
    seam_flag = '--seam' if axis == 1 else '--seam-y'
    print(json.dumps({'kind': 'collage', 'panels_found': len(panels), 'axis': 'side by side' if axis == 1 else 'stacked',
                      'reuse': '%s %s' % (seam_flag, ','.join(str((a + b) // 2) for a, b, _ in cuts)),
                      'cuts': [[a, b] for a, b, _ in cuts], 'scores': [s_ for _, _, s_ in cuts], 'runner_up': runner,
                      'panels': panels, 'preview': os.path.join(out, 'preview.jpg')}))
    puts = args_all('--put')
    if puts:
        keep = [int(v) for v in arg('--keep', ','.join(str(q['n']) for q in panels)).split(',')]
        if len(puts) != len(keep): die('%d --put URLs for %d kept panels %s' % (len(puts), len(keep), keep))
        ok = True
        for n, u in zip(keep, puts):
            if not 1 <= n <= len(panels): die('no panel %d' % n)
            ok = put(panels[n - 1]['file'], u, 'image/jpeg') and ok
        if not ok: die('panel upload failed')


# ---------------------------------------------------------------- crop
def cmd_crop():
    """crop PHOTO OUT.jpg --box x0,y0,x1,y1 [--put URL]   (pixels, or fractions 0..1 of width/height)"""
    from PIL import Image
    src, dst = sys.argv[2], sys.argv[3]
    tmp = os.path.join(os.path.dirname(os.path.abspath(dst)), '_crop_src' + (os.path.splitext(src.split('?')[0])[1] or '.img'))
    im = Image.open(fetch(src, tmp)).convert('RGB'); W_, H_ = im.size
    bx = [float(v) for v in (arg('--box') or die('--box x0,y0,x1,y1 is required')).split(',')]
    if all(v <= 1.0 for v in bx): bx = [bx[0] * W_, bx[1] * H_, bx[2] * W_, bx[3] * H_]
    box = tuple(int(round(v)) for v in bx)
    c = im.crop(box); c.save(dst, quality=95); os.remove(tmp)
    pv = c.copy(); pv.thumbnail((960, 960)); pvp = os.path.splitext(dst)[0] + '_preview.jpg'; save_small(pv, pvp)
    print(json.dumps({'crop': dst, 'preview': pvp, 'source_size': [W_, H_], 'box': box, 'size': [box[2] - box[0], box[3] - box[1]]}))
    if arg('--put') and not put(dst, arg('--put'), 'image/jpeg'): die('upload failed')


# ---------------------------------------------------------------- qa
def cmd_qa():
    from PIL import Image
    cfg = json.load(open(sys.argv[2])); out = sys.argv[3]; os.makedirs(out, exist_ok=True)
    plan = load_plan(cfg); clips = cfg.get('clips', {})
    todo = [k for k in SHOTS if k in clips]
    if not todo: die('config has no clips')
    jobs = [(ASSETS['ref'][0], os.path.join(out, 'ref.mp4'), ASSETS['ref'][1])]
    jobs += [(clips[k], os.path.join(out, k + '.mp4'), None) for k in todo]
    fetch_many(jobs); log('downloaded', len(jobs), 'files')
    TW, TH = 240, 135
    pick = {}
    for k in todo:
        sp = plan['shots'][k]; lo = round(sp.get('tin', 0.0) * 24); hi = round(sp['tmax'] * 24)
        pick[k] = [lo + round(q * (hi - lo)) for q in (0.0, 0.33, 0.67, 1.0)]
    ref_idx = [SH[k][0] + i for k in todo for i in pick[k]]
    refs = frames_at(os.path.join(out, 'ref.mp4'), ref_idx, (TW, TH))
    rows = {}
    with cf.ThreadPoolExecutor(6) as ex:
        futs = {k: ex.submit(frames_at, os.path.join(out, k + '.mp4'), pick[k], (TW, TH)) for k in todo}
        ours = {k: f.result() for k, f in futs.items()}
    for k in todo:
        row = Image.new('RGB', (TW * 8 + 6 * 3, TH + 4), (220, 0, 0))
        for j, i in enumerate(pick[k]):
            r = refs[SH[k][0] + i].copy(); o = ours[k][i].copy()
            tag(r, '%s ref %d' % (k, SH[k][0] + i), 14); tag(o, '%s ours %.2fs%s' % (k, i / 24, ' LAST' if j == 3 else ''), 14)
            x = j * (TW * 2 + 6); row.paste(r, (x, 0)); row.paste(o, (x + TW, 0))
        rows[k] = row
    written = []
    for k in todo:
        n = probe_frames(os.path.join(out, k + '.mp4'))
        log('%s: %d frames (%.2f s at 24 fps), edit uses frames %d..%d' % (k, n, n / 24, pick[k][0], pick[k][3]))
    if '--detail' in sys.argv:     # ours only, one frame per shot (middle of the used range) at 960x540: jewellery check
        mids = {k: (pick[k][0] + pick[k][3]) // 2 for k in todo}
        photo = None
        if cfg.get('photo'):
            pp = fetch(cfg['photo'], os.path.join(out, '_photo' + (os.path.splitext(cfg['photo'].split('?')[0])[1] or '.img')))
            ph = Image.open(pp).convert('RGB'); ph.thumbnail((960, 540)); photo = Image.new('RGB', (960, 540), (40, 40, 40))
            photo.paste(ph, ((960 - ph.width) // 2, (540 - ph.height) // 2)); tag(photo, 'USER PHOTO (reference for own jewellery)', 20)
        with cf.ThreadPoolExecutor(6) as ex:
            futs = {k: ex.submit(frames_at, os.path.join(out, k + '.mp4'), [mids[k]], (960, 540)) for k in todo}
            big = {k: f.result()[mids[k]] for k, f in futs.items()}
        for name, group in (('detail_1.jpg', 'ABCDE'), ('detail_2.jpg', 'FGHI')):
            ks = [k for k in group if k in big]
            if not ks: continue
            tiles_ = [(big[k].copy(), '%s ours %.2fs' % (k, mids[k] / 24)) for k in ks] + ([(photo.copy(), None)] if photo else [])
            sheet = Image.new('RGB', (1920, 540 * ((len(tiles_) + 1) // 2)), (0, 0, 0))
            for j, (t, lab) in enumerate(tiles_):
                if lab: tag(t, lab, 22)
                sheet.paste(t, ((j % 2) * 960, (j // 2) * 540))
            written.append(save_small(sheet, os.path.join(out, name)))
        print(json.dumps({'sheets': written})); return
    for name, group in (('qa_1.jpg', 'ABCDE'), ('qa_2.jpg', 'FGHI')):
        rs = [rows[k] for k in group if k in rows]
        if not rs: continue
        sheet = Image.new('RGB', (rs[0].width, sum(r.height for r in rs)), (0, 0, 0)); y = 0
        for r in rs: sheet.paste(r, (0, y)); y += r.height
        written.append(save_small(sheet, os.path.join(out, name)))
    print(json.dumps({'sheets': written}))


# ---------------------------------------------------------------- sheet
def cmd_sheet():
    from PIL import Image
    src, dst = sys.argv[2], sys.argv[3]
    tmp = os.path.join(os.path.dirname(os.path.abspath(dst)), '_sheet_src.mp4'); fetch(src, tmp)
    n_all = probe_frames(tmp)
    cols = int(arg('--cols', 4))
    if arg('--frames'): idx = [int(x) for x in arg('--frames').split(',')]
    else:
        n = int(arg('--n', 8)); idx = [round(i * (n_all - 1) / max(1, n - 1)) for i in range(n)]
    w, h = video_size(tmp); tw = 1920 // cols
    if arg('--crop'):                         # zoom: full-resolution region with a coordinate grid
        box = parse_box(arg('--crop')); full = frames_at(tmp, idx, (w, h)); sc = tw / (box[2] - box[0])
        fr = {i: grid_crop(full[i], box, sc) for i in full}; th = fr[idx[0]].height
    else:
        th = round(tw * h / w / 2) * 2; fr = frames_at(tmp, idx, (tw, th))
    rows = (len(idx) + cols - 1) // cols
    sheet = Image.new('RGB', (tw * cols, th * rows), (0, 0, 0))
    for j, i in enumerate(idx):
        t = fr[i].copy(); tag(t, 'f%d' % i, 16, bottom=True); sheet.paste(t, ((j % cols) * tw, (j // cols) * th))
    save_small(sheet, dst); os.remove(tmp)
    print(json.dumps({'sheet': dst, 'frames': n_all, 'size': [w, h]}))


# ---------------------------------------------------------------- driver tools
def driver_seq(shot, n):
    a, b = SH[shot]; seq = list(range(a, b + 1)); fwd = True
    while len(seq) < n:
        fwd = not fwd; seq += list(range(b - 1, a - 1, -1)) if not fwd else list(range(a + 1, b + 1))
    return seq


def cmd_tiles():
    """tiles SHOT OUT.jpg [--every N] [--zoom x0,y0,x1,y1]: registry-driver frames over the shot's forward pass (always
    including the last one), labelled 'driver n = ref r'. --zoom shows a full-resolution region with a coordinate grid in
    1920x1080 pixels (lines every 50, labels every 100): read jewellery positions off it directly."""
    from PIL import Image
    shot, dst = sys.argv[2].upper(), sys.argv[3]
    tmp = os.path.join(os.path.dirname(os.path.abspath(dst)), '_driver_%s.mp4' % shot); fetch(ASSETS[shot][0], tmp, ASSETS[shot][1])
    a, b = SH[shot]; n = b - a + 1; seq = driver_seq(shot, n)
    every = max(1, int(arg('--every', 8)))
    zoom = parse_box(arg('--zoom')) if arg('--zoom') else None
    cap = 12 if zoom else 16
    while len(range(0, n, every)) + 1 > cap: every += 1
    idx = list(range(0, n, every))
    if idx[-1] != n - 1: idx.append(n - 1)
    if zoom:
        full = frames_at(tmp, idx, (1920, 1080)); cw = zoom[2] - zoom[0]
        sc = min(2.0, 960.0 / cw); tw = round(cw * sc); cols = max(1, 1920 // tw)
        tiles = [grid_crop(full[i], zoom, sc) for i in idx]
    else:
        fr = frames_at(tmp, idx, (480, 270)); cols = 4; tiles = [fr[i] for i in idx]
    tw, th = tiles[0].size
    sheet = Image.new('RGB', (tw * cols, th * ((len(idx) + cols - 1) // cols)), (0, 0, 0))
    for j, (i, t) in enumerate(zip(idx, tiles)):
        t = t.copy(); tag(t, 'driver %d = ref %d' % (i, seq[i]), 15, bottom=True); sheet.paste(t, ((j % cols) * tw, (j // cols) * th))
    save_small(sheet, dst); os.remove(tmp)
    print(json.dumps({'tiles': dst, 'shot': shot, 'ref_range': [a, b], 'ref_frames': [seq[i] for i in idx],
                      'coords': 'grid labels are 1920x1080 px' if zoom else 'tiles are 1/4 scale: tile px x4 = 1920x1080 px'}))


def _lerp(keys, r):
    import numpy as np
    ks = sorted(int(k) for k in keys); vals = [keys[str(k)] for k in ks]
    return np.array([np.interp(r, ks, [v[i] for v in vals]) for i in range(len(vals[0]))])


def _inpaint(img, mask, W, H, it=260, seed=0):
    import numpy as np
    from PIL import Image, ImageFilter
    ys, xs = np.nonzero(mask)
    if len(ys) == 0: return img
    y0, y1 = max(ys.min() - 8, 0), min(ys.max() + 9, H); x0, x1 = max(xs.min() - 8, 0), min(xs.max() + 9, W)
    c = img[y0:y1, x0:x1].astype(np.float32); m = mask[y0:y1, x0:x1]
    hw = (max(1, (x1 - x0) // 2), max(1, (y1 - y0) // 2))
    sm = np.asarray(Image.fromarray(c.astype(np.uint8)).resize(hw), np.float32).copy()
    mm = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).resize(hw)) > 64
    sm[mm] = sm[~mm].mean(0)
    for _ in range(it):
        a = (np.roll(sm, 1, 0) + np.roll(sm, -1, 0) + np.roll(sm, 1, 1) + np.roll(sm, -1, 1)) / 4; sm[mm] = a[mm]
    up = np.asarray(Image.fromarray(np.clip(sm, 0, 255).astype(np.uint8)).resize((x1 - x0, y1 - y0), Image.BILINEAR), np.float32)
    up = up + np.random.default_rng(seed).normal(0, 3, up.shape)
    soft = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(4)), np.float32)[..., None] / 255
    out = img.copy(); out[y0:y1, x0:x1] = np.clip(c * (1 - soft) + up * soft, 0, 255).astype(np.uint8); return out


def cmd_clean():
    """spec (1920x1080 px, keyed by REFERENCE frame number, linearly interpolated):
      frames:   [first, last]  optional, defaults to the shot's SH range (must equal it)
      ellipses: [{"keys": {"<ref frame>": [cx, cy], ...}, "axes": [ax, ay]}]         diffusion-inpainted (earrings)
      bands:    [{"keys": {"<ref frame>": [x0, x1, y_top], ...}, "fill": [r,g,b]}]   flat fill below y_top (choker)"""
    import numpy as np
    from PIL import Image, ImageFilter
    shot, spec, out = sys.argv[2].upper(), json.load(open(sys.argv[3])), sys.argv[4]; os.makedirs(out, exist_ok=True)
    src = fetch(ASSETS[shot][0], os.path.join(out, 'driver_%s.mp4' % shot), ASSETS[shot][1])
    W, H = 1920, 1080
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', src, '-vf', 'scale=%d:%d' % (W, H), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                         capture_output=True, check=True).stdout
    F = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
    if tuple(spec.get('frames', SH[shot])) != SH[shot]: die('spec.frames must be %s for shot %s' % (list(SH[shot]), shot))
    seq = driver_seq(shot, len(F)); yy, xx = np.mgrid[0:H, 0:W]
    dst = os.path.join(out, 'drive_%s_clean.mp4' % shot)
    zoom = parse_box(arg('--zoom')) if arg('--zoom') else None
    nf = SH[shot][1] - SH[shot][0] + 1
    probe = sorted(set(round(q * (nf - 1)) for q in (0, 0.2, 0.4, 0.6, 0.8, 1.0))) if zoom else [0, len(F) // 6, len(F) // 3]
    preview_only = not arg('--put')           # preview: paint only the preview frames, no video (a few seconds)

    def paint(j):
        r = seq[j]; img = F[j].copy()
        for e in spec.get('ellipses', []):
            cx, cy = _lerp(e['keys'], r); ax, ay = e['axes']
            img = _inpaint(img, ((xx - cx) / ax) ** 2 + ((yy - cy) / ay) ** 2 <= 1, W, H, seed=j)
        for band in spec.get('bands', []):
            x0, x1, yt = _lerp(band['keys'], r)
            cm = (yy >= yt) & (xx >= x0) & (xx <= x1)
            soft = np.asarray(Image.fromarray((cm * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(10)), np.float32)[..., None] / 255
            img = np.clip(img * (1 - soft) + np.array(band.get('fill', [22, 20, 20]), np.float32) * soft, 0, 255).astype(np.uint8)
        return img

    keep = {}
    if preview_only:
        for j in probe: keep[j] = (F[j], paint(j)) if zoom else paint(j)
    else:
        p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (W, H), '-r', '25', '-i', '-',
                              '-c:v', 'libx264', '-crf', '14', '-pix_fmt', 'yuv420p', dst], stdin=subprocess.PIPE)
        for j in range(len(F)):
            img = paint(j); p.stdin.write(img.tobytes())
            if j in probe: keep[j] = (F[j], img) if zoom else img
            if j % 20 == 0: log('cleaned frame', j, '/', len(F))
        p.stdin.close(); p.wait()
        if p.returncode: die('ffmpeg encode failed')
    if zoom:      # before | after pairs of the zoom region at 6 frames across the forward pass, 2 pairs per row
        sc = 480.0 / (zoom[2] - zoom[0]); pairs = []
        for j in sorted(keep):
            bf, af = keep[j]; l = grid_crop(Image.fromarray(bf), zoom, sc); r = grid_crop(Image.fromarray(af), zoom, sc)
            tag(l, 'ref %d before' % seq[j], 14, bottom=True); tag(r, 'after', 14, bottom=True)
            pr = Image.new('RGB', (l.width * 2, l.height)); pr.paste(l, (0, 0)); pr.paste(r, (l.width, 0)); pairs.append(pr)
        pw, ph = pairs[0].size; prev = Image.new('RGB', (pw * 2, ph * ((len(pairs) + 1) // 2)), (0, 0, 0))
        for k, pr in enumerate(pairs): prev.paste(pr, ((k % 2) * pw, (k // 2) * ph))
    else:
        prev = Image.fromarray(np.concatenate([keep[k] for k in sorted(keep)], 1)).resize((1440, 270))
    save_small(prev, os.path.join(out, 'prev.jpg'))
    if preview_only:
        print('PREVIEW_DONE (no video written; add --put to render and upload the cleaned driver)', flush=True); return
    log('frames', len(F), '->', dst)
    if not put(dst, arg('--put'), 'video/mp4'): die('upload failed')
    print('CLEAN_DONE', flush=True)


# ---------------------------------------------------------------- render
def cmd_render():
    cfg = json.load(open(sys.argv[2])); W_ = os.path.abspath(sys.argv[3])
    missing = [k for k in SHOTS if k not in cfg.get('clips', {})]
    if missing: die('config.clips is missing shots: ' + ','.join(missing))
    for k in ('put_edit', 'put_compare'):
        if not str(cfg.get(k, '')).startswith('https://upload.higgsfield.ai/'): die('config.%s must be a media_upload upload_url' % k)
    for k, u in cfg['clips'].items():
        if not re.fullmatch(r'https://[A-Za-z0-9.-]+/[A-Za-z0-9_./%-]+\.mp4', u): die('clip %s: unexpected URL %r' % (k, u))
    if os.path.exists(W_): shutil.rmtree(W_)
    os.makedirs(os.path.join(W_, 'clips'))
    jobs = [(cfg['clips'][k], os.path.join(W_, 'clips', k + '.mp4'), None) for k in SHOTS]
    jobs += [(ASSETS['ref'][0], os.path.join(W_, 'ref.mp4'), ASSETS['ref'][1]),
             (ASSETS['models'][0], os.path.join(W_, 'models.zip'), ASSETS['models'][1])]
    fetch_many(jobs); log('downloaded clips, reference and models (sha256 OK)')
    with zipfile.ZipFile(os.path.join(W_, 'models.zip')) as z:
        for name, dst in (('aura_models/modnet.onnx', 'modnet.onnx'), ('aura_models/ArchivoBlack-Regular.ttf', 'ArchivoBlack.ttf')):
            with z.open(name) as s, open(os.path.join(W_, dst), 'wb') as d: shutil.copyfileobj(s, d)
    shutil.copy(os.path.join(KIT, 'compose.py'), W_)
    plan = load_plan(cfg)
    json.dump(plan, open(os.path.join(W_, 'plan.json'), 'w'))
    log('rendering %d frames (about 3 min)' % plan['frames'])
    with open(os.path.join(W_, 'render.log'), 'w') as rl:
        p = subprocess.Popen([sys.executable, 'compose.py', 'plan.json', 'edit.mp4'], cwd=W_, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in p.stdout:
            rl.write(line); rl.flush()
            if re.search(r'frame \d+|done|Error|Traceback', line): print('  compose ' + line.rstrip(), flush=True)
        p.wait()
    if p.returncode:
        print(open(os.path.join(W_, 'render.log')).read()[-3000:]); die('compose failed')
    label = re.sub(r'[^A-Za-z0-9 +.-]', ' ', cfg.get('label') or 'HIGGSFIELD GENJUTSU')[:60]
    lf = LABEL_FONT if os.path.exists(LABEL_FONT) else '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    lab = 'x=36:y=30:fontsize=30:fontcolor=white:box=1:boxcolor=black@0.45:boxborderw=12'
    log('building compare.mp4')
    sh('ffmpeg', '-v', 'error', '-y', '-i', 'ref.mp4', '-i', 'edit.mp4', '-filter_complex',
       "[0:v]fps=25,scale=1920:1080,setsar=1,drawtext=fontfile=%s:text='REFERENCE':%s[a];"
       "[1:v]setsar=1,drawtext=fontfile=%s:text='%s':%s[b];[a][b]vstack=inputs=2[v]" % (lf, lab, lf, label, lab),
       '-map', '[v]', '-map', '1:a', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac',
       '-b:a', '256k', '-t', '14.2', '-movflags', '+faststart', 'compare.mp4', cwd=W_)
    for f in ('edit.mp4', 'compare.mp4'):
        r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_type,width,height,duration', '-of', 'compact',
                            os.path.join(W_, f)], capture_output=True, text=True)
        print(f, r.stdout.strip().replace('\n', ' | '), flush=True)
    ok = put(os.path.join(W_, 'edit.mp4'), cfg['put_edit'], 'video/mp4')
    ok = put(os.path.join(W_, 'compare.mp4'), cfg['put_compare'], 'video/mp4') and ok
    if not ok: die('upload failed: reserve two fresh slots and re-run render (do not reuse either upload_url)')
    print('RUN_DONE', flush=True)


# ---------------------------------------------------------------- vertical
def cmd_vertical():
    """vertical EDIT OUT.mp4 [--mode fill|crop] [--put URL]
    fill (default): the full 16:9 picture centred on a blurred, darkened copy of itself, 1080x1920 (keeps the lyric words
    and the ring). crop: centre 608x1080 crop scaled to 1080x1920 (bigger subject, cuts the words)."""
    src, dst = sys.argv[2], os.path.abspath(sys.argv[3])
    tmp = os.path.join(os.path.dirname(dst), '_vert_src.mp4'); fetch(src, tmp)
    if arg('--mode', 'fill') == 'crop':
        fc = '[0:v]crop=608:1080:(iw-608)/2:0,scale=1080:1920:flags=lanczos,setsar=1,format=yuv420p[v]'
    else:
        fc = ('[0:v]split=2[a][b];[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=40:2,'
              'eq=brightness=-0.06[bg];[b]scale=1080:-2:flags=lanczos[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1,format=yuv420p[v]')
    log('encoding', arg('--mode', 'fill'))
    sh('ffmpeg', '-v', 'error', '-y', '-i', tmp, '-filter_complex', fc, '-map', '[v]', '-map', '0:a?', '-c:v', 'libx264', '-preset', 'veryfast',
       '-crf', '18', '-c:a', 'copy', '-movflags', '+faststart', dst)
    os.remove(tmp)
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_type,width,height,duration', '-of', 'compact', dst],
                       capture_output=True, text=True)
    print(os.path.basename(dst), r.stdout.strip().replace('\n', ' | '), flush=True)
    if arg('--put') and not put(dst, arg('--put'), 'video/mp4'): die('upload failed')
    print('VERTICAL_DONE', flush=True)


if __name__ == '__main__':
    cmds = {'split': cmd_split, 'crop': cmd_crop, 'qa': cmd_qa, 'sheet': cmd_sheet, 'tiles': cmd_tiles, 'clean': cmd_clean,
            'render': cmd_render, 'vertical': cmd_vertical}
    if len(sys.argv) < 3 or sys.argv[1] not in cmds: print(__doc__); sys.exit(2)
    cmds[sys.argv[1]]()
