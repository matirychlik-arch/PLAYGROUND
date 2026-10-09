#!/usr/bin/env python3
"""Canvas compositor runner: prep plates/mattes, serve W, render in sharded headless Chrome, encode + mux.

Subcommands (W = workspace dir; the EDL is W/comp/edl.json, project hooks W/comp/fx.js):
  prep   W VIDEO --clip ID [--width N|--native] [--mask MATTE --mask-mode divide|threshold|luma|alpha]
         -> W/plates/ID/%05d.jpg (+clip.json), W/mattes/ID/%05d.png (white + alpha, +clip.json)
  render W [--jobs N] [--preview] [--stills LIST] [--frames A:B] [--fmt jpg|png] [--audio auto|none|PATH] [--sfx-file PATH] ...
         -> W/out/comp.mp4 (H.264 crf 18, yuv420p, bt709 tags, exact frame count), log W/comp/render.log
         frame dumps: W/comp/frames/ (+ preview/, stills/), all under the one tree rr_save leaves out
  info   W  -> W/comp/info.json + W/comp/sfx_cues.json (validates the EDL in Chrome, plans stickers)
  sfx    W  -> disabled compatibility command; never synthesises audio
  serve  W [--port P]  -> static server for manual preview (prints the URL; never opens a browser)
Python 3.11+, stdlib + numpy; ffmpeg/ffprobe and Chrome/Chromium on PATH or auto-detected.
"""
import argparse
import glob
import http.server
import json
import math
import os
import platform
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
from fractions import Fraction
from urllib.parse import unquote, urlparse

KIT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(KIT))
import rrio  # noqa: E402  (scripts/rrio.py)

LOG_PATH = None


def log(msg):
    line = time.strftime('%H:%M:%S ') + str(msg)
    print(line, flush=True)
    if LOG_PATH:
        try:
            with open(LOG_PATH, 'a', encoding='utf-8') as fh:
                fh.write(line + '\n')
        except OSError:
            pass


def die(msg, code=1):
    log('ERROR ' + msg)
    sys.exit(code)


# ================================================================================ EDL helpers
def load_edl(W, rel):
    p = rel if os.path.isabs(rel) else os.path.join(W, rel)
    if not os.path.isfile(p):
        die(f'EDL not found: {p}')
    try:
        with open(p, encoding='utf-8') as fh:
            return json.load(fh), p
    except json.JSONDecodeError as e:
        die(f'EDL is not valid JSON ({p}): {e}')


def edl_fps(E):
    f = rrio.parse_fps(str((E.get('canvas') or {}).get('fps', 24)))
    if not f:
        die('canvas.fps is invalid')
    return f


def edl_time(v, E, fps):
    """engine.js T(): seconds | 'b<beats>' on edl.beat | 'f<frame>' (same float operations as the page)."""
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip()
    b = E.get('beat') or {}
    if s.startswith('b'):  # JS: beat.t0 + n * (60 / bpm)
        return float(b.get('t0') or 0) + float(s[1:]) * (60.0 / float(b.get('bpm') or 120))
    if s.startswith('f'):
        return float(s[1:]) / float(fps)
    return float(s)


def js_round(x):
    """JavaScript Math.round: the nearest integer, ties toward +infinity (Python round() ties to even)."""
    r = math.floor(x)
    return int(r + 1) if x - r >= 0.5 else int(r)


def edl_frames(E):
    """Frame count exactly as engine.js computes it (canvas.frames > canvas.dur > last shot end).
    render cross-checks it against the count the page reports and aborts on a mismatch."""
    cv = E.get('canvas') or {}
    fps = edl_fps(E)
    if cv.get('frames'):
        return int(cv['frames'])
    if cv.get('dur'):  # JS: cv.dur ? Math.round(T(cv.dur) * fps)
        return js_round(edl_time(cv['dur'], E, fps) * float(fps))
    ends = []
    for s in E.get('shots') or []:
        if s.get('f1') is not None:
            ends.append(int(s['f1']))
        elif s.get('t1') is not None:
            t1 = edl_time(s['t1'], E, fps)
            ends.append(max(0, math.ceil(t1 * float(fps) - 0.5 - 1e-6)))
    if not ends:
        return None
    return max(ends)


def parse_frames_spec(spec, E, nf):
    """'0,12,40' | '1.5s,3s' | 'cuts' (2 frames into every shot) | 'A:B' range, clamped to [0, nf)."""
    fps = float(edl_fps(E))
    out = []
    for tok in str(spec).split(','):
        tok = tok.strip()
        if not tok:
            continue
        if tok == 'cuts':
            starts = []
            for s in E.get('shots') or []:
                t0 = (s['f0'] / fps) if s.get('f0') is not None else edl_time(s.get('t0', 0), E, fps)
                starts.append(max(0, math.ceil(t0 * fps - 0.5 - 1e-6)))
            starts = sorted(set(starts))
            for i, f0 in enumerate(starts):
                f1 = starts[i + 1] if i + 1 < len(starts) else nf
                out.append(min(f1 - 1, f0 + 2) if f1 > f0 else f0)
        elif ':' in tok:
            a, b = tok.split(':')
            out += list(range(int(a or 0), int(b or nf)))
        elif tok.endswith('s'):
            out.append(int(math.floor(float(tok[:-1]) * fps)))
        else:
            out.append(int(tok))
    return sorted(set(f for f in out if 0 <= f < nf))


# ================================================================================ HTTP server
MIME = {'.html': 'text/html; charset=utf-8', '.js': 'application/javascript', '.json': 'application/json',
        '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', '.webp': 'image/webp', '.gif': 'image/gif',
        '.svg': 'image/svg+xml', '.css': 'text/css', '.ttf': 'font/ttf', '.otf': 'font/otf', '.woff': 'font/woff',
        '.woff2': 'font/woff2', '.wav': 'audio/wav', '.mp3': 'audio/mpeg', '.mp4': 'video/mp4', '.txt': 'text/plain'}


class Sink:
    def __init__(self, W, frames_dir, stills_dir, ext='jpg'):
        self.W, self.frames_dir, self.stills_dir, self.ext = W, frames_dir, stills_dir, ext
        self.lock = threading.Lock()
        self.got, self.stills = set(), set()
        self.done, self.fail = {}, {}
        self.info = self.cues = None
        self.last = time.time()
        self.roots = {'/_rr/': KIT}
        hf = os.environ.get('HF_WORKFLOWS') or '/home/user/.higgsfield/workflows'
        if os.path.isdir(hf):
            self.roots['/_hf/'] = hf


def _safe_join(root, rel):
    """Lexical containment (blocks '..'); symlinks the user placed inside the root are followed."""
    root = os.path.abspath(root)
    p = os.path.normpath(os.path.join(root, rel.lstrip('/')))
    return p if (p == root or p.startswith(root + os.sep)) else None


def make_handler(sink):
    class H(http.server.BaseHTTPRequestHandler):
        protocol_version = 'HTTP/1.1'

        def log_message(self, *a):
            pass

        def _send(self, code, body=b'', ctype='text/plain'):
            self.send_response(code)
            self.send_header('Content-Type', ctype)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            if self.command != 'HEAD' and body:
                self.wfile.write(body)

        def _resolve(self):
            path = unquote(urlparse(self.path).path)
            for pre, root in sink.roots.items():
                if path.startswith(pre):
                    return _safe_join(root, path[len(pre):])
            return _safe_join(sink.W, path)

        def do_GET(self):
            p = self._resolve()
            if not p or not os.path.isfile(p):
                return self._send(404, b'not found')
            try:
                with open(p, 'rb') as fh:
                    data = fh.read()
            except OSError:
                return self._send(500, b'read error')
            self._send(200, data, MIME.get(os.path.splitext(p)[1].lower(), 'application/octet-stream'))

        do_HEAD = do_GET

        def do_POST(self):
            n = int(self.headers.get('Content-Length') or 0)
            data = self.rfile.read(n) if n else b''
            parts = urlparse(self.path).path.strip('/').split('/')
            try:
                if len(parts) == 2 and parts[0] in ('frame', 'still') and parts[1].isdigit():
                    i = int(parts[1])
                    d = sink.frames_dir if parts[0] == 'frame' else sink.stills_dir
                    os.makedirs(d, exist_ok=True)
                    ext = 'png' if data[:4] == b'\x89PNG' else 'jpg'
                    dst = os.path.join(d, f'{i:05d}.{ext}')
                    tmp = dst + f'.{threading.get_ident()}.part'
                    with open(tmp, 'wb') as fh:
                        fh.write(data)
                    os.replace(tmp, dst)
                    with sink.lock:
                        (sink.got if parts[0] == 'frame' else sink.stills).add(i)
                        sink.last = time.time()
                elif parts == ['log']:
                    log('page: ' + data.decode('utf-8', 'replace')[:2000])
                elif parts == ['info']:
                    sink.info = json.loads(data or b'{}')
                elif parts == ['cues']:
                    sink.cues = json.loads(data or b'[]')
                elif len(parts) == 2 and parts[0] == 'done':
                    with sink.lock:
                        sink.done[parts[1]] = json.loads(data or b'{}')
                elif len(parts) == 2 and parts[0] == 'fail':
                    with sink.lock:
                        sink.fail[parts[1]] = data.decode('utf-8', 'replace')
                else:
                    return self._send(404, b'unknown endpoint')
            except Exception as e:  # keep the server alive
                return self._send(500, str(e).encode())
            self._send(200, b'ok')
    return H


class _HTTPD(http.server.ThreadingHTTPServer):
    daemon_threads = True

    def handle_error(self, request, client_address):  # a killed Chrome resets its sockets: one line, no traceback
        e = sys.exc_info()[1]
        if not isinstance(e, (ConnectionError, BrokenPipeError, TimeoutError)):
            log(f'server: {type(e).__name__}: {e}')


class Server:
    def __init__(self, sink, port=0):
        self.httpd = _HTTPD(('127.0.0.1', port), make_handler(sink))
        self.httpd.daemon_threads = True
        self.port = self.httpd.server_address[1]
        self.t = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.t.start()

    def close(self):
        self.httpd.shutdown()
        self.httpd.server_close()


# ================================================================================ Chrome
def find_chrome(explicit=None):
    cands = [explicit, os.environ.get('CHROME')]
    for pat in ('/ms-playwright/chromium-*/chrome-linux64/chrome', '/ms-playwright/chromium-*/chrome-linux/chrome',
                '/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell'):
        cands += sorted(glob.glob(pat), reverse=True)
    cands += ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '/Applications/Chromium.app/Contents/MacOS/Chromium']
    for n in ('chromium', 'chromium-browser', 'google-chrome', 'google-chrome-stable', 'chrome'):
        w = shutil.which(n)
        if w:
            cands.append(w)
    for c in cands:
        if c and os.path.isfile(c) and os.access(c, os.X_OK):
            return c
    return None


def chrome_cmd(chrome, url, udd, gpu=False):
    a = [chrome, '--headless=new', f'--user-data-dir={udd}', '--window-size=1280,720', '--no-first-run',
         '--no-default-browser-check', '--disable-background-timer-throttling', '--disable-renderer-backgrounding',
         '--disable-backgrounding-occluded-windows', '--disable-extensions', '--disable-component-update',
         '--disable-sync', '--mute-audio', '--hide-scrollbars', '--force-color-profile=srgb',
         '--disable-features=Translate,MediaRouter,OptimizationHints', '--js-flags=--max-old-space-size=2048']
    if platform.system() == 'Linux':
        a += ['--no-sandbox', '--disable-dev-shm-usage']
    if not gpu:
        a += ['--disable-gpu']
    a += [x for x in os.environ.get('RR_CHROME_FLAGS', '').split() if x]
    return a + [url]


class Browser:
    def __init__(self, chrome, url, tag, gpu):
        self.udd = tempfile.mkdtemp(prefix=f'rrchrome_{tag}_')
        self.errlog = os.path.join(self.udd, 'chrome.log')
        self.fh = open(self.errlog, 'wb')
        self.p = subprocess.Popen(chrome_cmd(chrome, url, self.udd, gpu), stdout=self.fh, stderr=self.fh,
                                  stdin=subprocess.DEVNULL, start_new_session=True)

    def alive(self):
        return self.p.poll() is None

    def tail(self, n=600):
        try:
            with open(self.errlog, 'rb') as fh:
                return fh.read()[-n:].decode('utf-8', 'replace')
        except OSError:
            return ''

    def kill(self):
        if self.p.poll() is None:
            try:
                os.killpg(self.p.pid, signal.SIGTERM)
            except (ProcessLookupError, PermissionError):
                self.p.terminate()
            try:
                self.p.wait(4)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(self.p.pid, signal.SIGKILL)
                except (ProcessLookupError, PermissionError):
                    self.p.kill()
                self.p.wait(4)
        self.fh.close()
        shutil.rmtree(self.udd, ignore_errors=True)


def page_url(port, **q):
    from urllib.parse import urlencode
    return f'http://127.0.0.1:{port}/_rr/page.html?' + urlencode({k: v for k, v in q.items() if v is not None})


def run_pages(W, sink, chrome, jobs_spec, gpu=False, timeout=1800, stall=120, label='render', expect=None, kind='frame'):
    """jobs_spec: list of (shard_id, frames list, extra query dict). Waits until every shard posts /done.
    One relaunch per shard for frames still missing after a crash or stall."""
    srv = Server(sink)
    browsers, retries = {}, {}
    total = sum(len(fr) if fr else 0 for _, fr, _ in jobs_spec)
    t0 = time.time()

    def launch(sid, frames, extra):
        q = dict(extra)
        if frames is not None:
            if frames and frames == list(range(frames[0], frames[-1] + 1)):
                q.update(**{'from': frames[0], 'to': frames[-1] + 1})
            else:
                q['frames'] = ','.join(map(str, frames))
        q['shard'] = sid
        browsers[sid] = Browser(chrome, page_url(srv.port, **q), sid, gpu)

    spec = {sid: (fr, ex) for sid, fr, ex in jobs_spec}
    for sid, (fr, ex) in spec.items():
        launch(sid, fr, ex)
    log(f'{label}: {len(spec)} Chrome instance(s), {total} item(s), server 127.0.0.1:{srv.port}')
    last_log, ok = 0, False
    got_set = (lambda: sink.got) if kind == 'frame' else (lambda: sink.stills)
    try:
        while True:
            time.sleep(0.25)
            now = time.time()
            if sink.fail:
                sid, msg = next(iter(sink.fail.items()))
                raise RuntimeError(f'page error in shard {sid}: {msg[:1500]}')
            with sink.lock:
                n = len(got_set())
                done = set(sink.done)
            if all(s in done for s in spec):
                ok = True
                break
            if now - last_log > 3:
                el = now - t0
                rate = n / el if el > 0 else 0
                eta = (total - n) / rate if rate > 0 else -1
                log(f'{label}: {n}/{total} in {el:.0f}s ({rate:.1f}/s, eta {eta:.0f}s)')
                last_log = now
            for sid, (fr, ex) in spec.items():
                b = browsers[sid]
                stalled = (now - sink.last > stall) and (now - t0 > stall)
                if sid in done or (b.alive() and not stalled):
                    continue
                with sink.lock:
                    have = set(got_set())
                missing = [f for f in (fr or []) if f not in have] if fr is not None else None
                if retries.get(sid):
                    raise RuntimeError(f'shard {sid} {"stalled" if stalled else "exited"} twice; chrome log tail: {b.tail()}')
                retries[sid] = 1
                log(f'{label}: shard {sid} {"stalled" if stalled else "exited"} - relaunching '
                    f'({len(missing) if missing is not None else "all"} item(s) left)')
                b.kill()
                sink.last = time.time()
                if missing == []:
                    sink.done[sid] = {'n': 0, 'relaunch': 'nothing missing'}
                    continue
                launch(sid, missing, ex)
            if now - t0 > timeout:
                raise RuntimeError(f'{label}: timeout after {timeout}s ({n}/{total})')
    finally:
        for b in browsers.values():
            b.kill()
        srv.close()
    el = time.time() - t0
    log(f'{label}: done {total} item(s) in {el:.1f}s ({total / el if el else 0:.1f}/s)')
    return ok, el


# ================================================================================ prep (plates + mattes)
def _range_flag(p):
    cr = (p.get('color_range') or '').lower()
    pix = (p.get('pix_fmt') or '').lower()
    return 'pc' if (cr in ('pc', 'jpeg') or pix.startswith('yuvj')) else 'tv'


def cmd_prep(a):
    W = os.path.abspath(a.W)
    src = os.path.abspath(a.video)
    if not os.path.isfile(src):
        die(f'video not found: {src}')
    if a.clip in ('.', '..') or not re.fullmatch(r'[A-Za-z0-9._-]+', a.clip):
        die('--clip must be [A-Za-z0-9._-]+')
    p = rrio.probe(src)
    if not p.get('has_video'):
        die(f'no video stream in {src}')
    # The canvas engine indexes plates on a constant-rate grid. Refuse VFR here
    # before deleting old plates; flattening PTS would silently change the edit.
    rrio.require_cfr(src, p)
    sw, sh = p['w'], p['h']
    if a.width:
        ow = int(a.width) // 2 * 2
        oh = int(round(sh * ow / sw / 2)) * 2
    elif a.height:
        oh = int(a.height) // 2 * 2
        ow = int(round(sw * oh / sh / 2)) * 2
    else:
        ow, oh = sw // 2 * 2, sh // 2 * 2
    fps = p['fps']
    trim = ''
    if a.start or a.count:
        end = f':end_frame={a.start + a.count}' if a.count else ''
        trim = f'trim=start_frame={a.start}{end},setpts=PTS-STARTPTS,'
    pdir = os.path.join(W, 'plates', a.clip)
    os.makedirs(pdir, exist_ok=True)
    for f in glob.glob(os.path.join(pdir, '*.jpg')):
        os.remove(f)
    m = rrio._in_matrix(p) or 'bt709'
    pre = (a.vf.rstrip(',') + ',') if a.vf else ''
    vf = (f'{trim}{pre}scale={ow}:{oh}:flags=lanczos+accurate_rnd+full_chroma_int:in_color_matrix={m}:out_color_matrix=bt601'
          f':in_range={_range_flag(p)}:out_range=pc,format=yuvj420p')
    t = time.time()
    rrio.run_ffmpeg(['-i', src, '-map', f"0:{p['stream_index']}", '-an', '-vf', vf, '-q:v', str(a.quality),
                     *rrio._passthrough(), '-start_number', '0', os.path.join(pdir, '%05d.jpg')])
    n = len(glob.glob(os.path.join(pdir, '*.jpg')))
    info = {'n': n, 'fps': float(fps), 'fps_str': rrio.fps_str(fps), 'w': ow, 'h': oh, 'pattern': '%05d.jpg', 'start': 0,
            'src': os.path.relpath(src, W) if src.startswith(W + os.sep) else src, 'src_w': sw, 'src_h': sh,
            'src_start_frame': a.start or 0}
    # Lean state restores must repeat the actual preparation, including filters and
    # matte morphology, rather than reconstructing an approximation from dimensions.
    prep_args = [info['src'], '--clip', a.clip]
    prep_args += ['--width', str(a.width)] if a.width else (['--height', str(a.height)] if a.height else ['--native'])
    prep_args += ['--quality', str(a.quality), '--start', str(a.start), '--count', str(a.count)]
    if a.vf:
        prep_args += ['--vf', a.vf]
    if a.mask:
        msrc = os.path.abspath(a.mask)
        prep_args += ['--mask', os.path.relpath(msrc, W) if msrc.startswith(W + os.sep) else msrc,
                      '--mask-mode', a.mask_mode, '--thr', str(a.thr), '--close', str(a.close)]
        if a.mask_width is not None:
            prep_args += ['--mask-width', str(a.mask_width)]
    info['prep_args'] = prep_args
    rrio.save_json(os.path.join(pdir, 'clip.json'), info)
    log(f'prep {a.clip}: {n} plates {ow}x{oh} @{rrio.fps_str(fps)} -> {pdir} ({time.time() - t:.1f}s)')
    if a.mask:
        prep_mask(a, W, src, p, ow, oh, trim, n)


def prep_mask(a, W, src, p, ow, oh, trim, n_plates):
    msrc = os.path.abspath(a.mask)
    if not os.path.isfile(msrc):
        die(f'mask video not found: {msrc}')
    mp = rrio.probe(msrc)
    rrio.require_cfr(msrc, mp)
    mw = int(a.mask_width or ow // 2) // 2 * 2
    mh = int(round(oh * mw / ow / 2)) * 2
    mdir = os.path.join(W, 'mattes', a.clip)
    os.makedirs(mdir, exist_ok=True)
    for f in glob.glob(os.path.join(mdir, '*.png')):
        os.remove(f)
    rate = rrio.fps_str(mp['fps'] or p['fps'])
    close = ''
    if a.close:
        close = ',' + ','.join(['dilation'] * a.close + ['erosion'] * a.close)
    mode = a.mask_mode
    out = os.path.join(mdir, '%05d.png')
    white = f'color=white:s={mw}x{mh}:r={rate}'
    if mode == 'divide':  # remove_background output (subject on black, no alpha): alpha = matte / original
        fc = (f'[0:v]{trim}scale={mw}:{mh},format=gray[c];[1:v]{trim}scale={mw}:{mh},format=gray[o];'
              f"[c][o]blend=all_expr='if(lt(B,34),if(gt(A,10),255,0),clip((A*255/B-70)*1.9,0,255))'{close},gblur=sigma=0.7[a];"
              f'[2:v][a]alphamerge=shortest=1,format=rgba')
        args = ['-i', msrc, '-i', src, '-f', 'lavfi', '-i', white, '-filter_complex', fc, '-shortest']
    elif mode in ('threshold', 'luma'):
        expr = f"if(gt(val,{a.thr}),255,0)" if mode == 'threshold' else 'clip((val-16)*255/219,0,255)'
        fc = (f"[0:v]{trim}scale={mw}:{mh},format=gray,lut=y='{expr}'{close},gblur=sigma=0.7[a];"
              f'[1:v][a]alphamerge=shortest=1,format=rgba')
        args = ['-i', msrc, '-f', 'lavfi', '-i', white, '-filter_complex', fc, '-shortest']
    elif mode == 'alpha':
        fc = (f'[0:v]{trim}scale={mw}:{mh},format=rgba,alphaextract{close}[a];[1:v][a]alphamerge=shortest=1,format=rgba')
        args = ['-i', msrc, '-f', 'lavfi', '-i', white, '-filter_complex', fc, '-shortest']
    else:
        die(f'unknown --mask-mode {mode}')
    t = time.time()
    rrio.run_ffmpeg(args + [*rrio._passthrough(), '-start_number', '0', out])
    n = len(glob.glob(os.path.join(mdir, '*.png')))
    rrio.save_json(os.path.join(mdir, 'clip.json'), {'n': n, 'w': mw, 'h': mh, 'pattern': '%05d.png', 'start': 0,
                                                     'mode': mode, 'src': os.path.relpath(msrc, W) if msrc.startswith(W + os.sep) else msrc,
                                                     'fps': float(mp['fps'] or p['fps'])})
    if n != n_plates:
        log(f'WARN mask frames {n} != plate frames {n_plates} (engine clamps the mask index)')
    log(f'prep {a.clip}: {n} mattes {mw}x{mh} ({mode}) -> {mdir} ({time.time() - t:.1f}s)')


# ================================================================================ encode + audio
def encode(frames_dir, start, n, fps, out, crf=18, preset='medium', ext='jpg'):
    tmp = out + '.part.mp4'
    vf = 'scale=in_color_matrix=bt601:out_color_matrix=bt709:in_range=pc:out_range=tv:flags=accurate_rnd+full_chroma_int,format=yuv420p'
    if ext == 'png':
        vf = 'scale=out_color_matrix=bt709:out_range=tv:flags=accurate_rnd+full_chroma_int,format=yuv420p'
    rrio.run_ffmpeg(['-framerate', rrio.fps_str(fps), '-start_number', str(start), '-i', os.path.join(frames_dir, f'%05d.{ext}'),
                     '-frames:v', str(n), '-vf', vf, '-c:v', 'libx264', '-preset', preset, '-crf', str(crf),
                     '-pix_fmt', 'yuv420p', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709',
                     '-color_range', 'tv', '-bsf:v', 'h264_metadata=colour_primaries=1:transfer_characteristics=1:matrix_coefficients=1',
                     '-r', rrio.fps_str(fps), '-movflags', '+faststart', '-an', tmp])
    os.replace(tmp, out)


def loudness(path):
    """Integrated LUFS and true peak (dBTP) of the first audio stream via ebur128."""
    r = subprocess.run([rrio.FFMPEG, '-hide_banner', '-nostats', '-nostdin', '-i', path, '-map', '0:a:0',
                        '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True)
    err = r.stderr
    i = re.findall(r'I:\s+(-?[\d.]+|-inf) LUFS', err)
    pk = re.findall(r'Peak:\s+(-?[\d.]+|-inf) dBFS', err)
    f = lambda v: float('-inf') if v == '-inf' else float(v)  # noqa: E731
    return (f(i[-1]) if i else None), (f(pk[-1]) if pk else None)


def resolve_audio(W, E, a):
    au = E.get('audio') or {}
    spec = a.audio if a.audio != 'auto' else (au.get('src') or 'auto')
    if spec in ('none', '', None):
        return None
    if spec == 'auto':
        for c in ('ref/ref.mp4', 'ref/ref.m4a', 'ref/audio.wav', 'ref/audio.m4a'):
            pth = os.path.join(W, c)
            if os.path.isfile(pth) and rrio.probe(pth).get('has_audio'):
                return pth
        return None
    pth = spec if os.path.isabs(spec) else os.path.join(W, spec)
    if not os.path.isfile(pth):
        die(f'audio source not found: {pth}')
    if not rrio.probe(pth).get('has_audio'):
        die(f'no audio stream in {pth}')
    return pth


def audio_md5(path):
    """MD5 of the first audio stream's packets (stream copy, no decode): equal MD5 = bit-identical audio."""
    r = subprocess.run([rrio.FFMPEG, '-hide_banner', '-nostdin', '-v', 'error', '-i', path, '-map', '0:a:0', '-c', 'copy',
                        '-f', 'md5', '-'], capture_output=True, text=True)
    m = re.search(r'MD5=([0-9a-f]{32})', r.stdout or '')
    return m.group(1) if m else None


WHOLE_TAIL_S = 0.5  # retain this short source tail through copying, mixing or required transcoding


def mux(video, out, dur, audio=None, start=0.0, sfx_wav=None, sfx_gain=0.6, limit=0.79, force_aac=False,
        sfx_start=0.0, preserve_tail=True):
    """Stream-copy the reference audio when there is no SFX; otherwise mix + alimiter(level=disabled) + AAC
    256k with a true-peak check (AAC overshoot) that lowers the limiter until the peak is <= -1 dBTP.
    An MD5-equal stream copy is preferred. With preserve_tail, a track starting at 0 and at most
    WHOLE_TAIL_S longer than the picture is retained whole, including through mixing/transcoding.
    Longer tracks and selected offsets use the measured edit interval. A packet-MD5 mismatch is a
    fidelity difference: investigate/report it and never claim exact audio from codec or loudness alone."""
    dur_s = f'{dur:.6f}'
    if not audio and not sfx_wav:
        shutil.copyfile(video, out)
        return {'audio': 'none'}
    tmp = out + '.part.mp4'
    if audio and not sfx_wav:
        ap = rrio.probe(audio)
        copy = (ap.get('audio_codec') or '') in (('aac',) if force_aac else ('aac', 'mp3'))
        adur = ap.get('audio_duration') or ap.get('format_duration')
        whole = not start and adur is not None and adur <= dur + (WHOLE_TAIL_S if preserve_tail else 0)
        args = ['-i', video] + (['-ss', f'{start:.6f}'] if start else []) + ['-i', audio, '-map', '0:v:0', '-map', '1:a:0',
                                                                              '-c:v', 'copy']
        args += ['-c:a', 'copy'] if copy else ['-c:a', 'aac', '-b:a', '256k']
        rrio.run_ffmpeg(args + ([] if whole else ['-t', dur_s]) + ['-movflags', '+faststart', tmp])
        os.replace(tmp, out)
        lufs, pk = loudness(out)
        res = {'audio': 'copy' if copy else 'aac', 'src': audio, 'start': start, 'trimmed': not whole,
               'codec': ap.get('audio_codec'), 'sr': ap.get('audio_sr'), 'lufs': lufs, 'true_peak': pk}
        if copy:
            ms, mo = audio_md5(audio), audio_md5(out)
            res.update(md5_src=ms, md5_out=mo, md5_equal=bool(ms and ms == mo))
            log(f"audio: stream copy of {os.path.basename(audio)} ({'whole' if whole else 'trimmed to ' + dur_s + ' s'}), "
                f"MD5 {'equal to' if res['md5_equal'] else 'differs from'} the source"
                + ('' if res['md5_equal'] else ' (audio fidelity differs; investigate and report, not 1:1)'))
        return res
    mix_dur = dur
    if audio and preserve_tail and not start:
        ap = rrio.probe(audio)
        adur = ap.get('audio_duration') or ap.get('format_duration')
        if adur is not None and dur < adur <= dur + WHOLE_TAIL_S:
            mix_dur = adur
    # Preserve an existing short source-audio tail when adding recorded SFX, without
    # adding video frames or carrying the whole song beyond the selected edit.
    mix_dur_s = f'{mix_dur:.6f}'
    res = {}
    for attempt in range(4):
        lim = f'alimiter=limit={limit:.4f}:attack=1:release=40:level=disabled'
        if audio:
            ins = ['-i', video] + (['-ss', f'{start:.6f}'] if start else []) + ['-i', audio] + (['-ss', f'{sfx_start:.6f}'] if sfx_start else []) + ['-i', sfx_wav]
            fc = (f'[1:a]aresample=48000,atrim=0:{mix_dur_s},asetpts=PTS-STARTPTS,apad=whole_dur={mix_dur_s}[m];'
                  f'[2:a]aresample=48000,volume={sfx_gain}[s];[m][s]amix=inputs=2:normalize=0:duration=first,{lim}[a]')
        else:
            ins = ['-i', video] + (['-ss', f'{sfx_start:.6f}'] if sfx_start else []) + ['-i', sfx_wav]
            fc = f'[1:a]aresample=48000,volume={sfx_gain},atrim=0:{dur_s},apad=whole_dur={dur_s},{lim}[a]'
        rrio.run_ffmpeg(ins + ['-filter_complex', fc, '-map', '0:v:0', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac',
                               '-b:a', '256k', '-ar', '48000', '-t', mix_dur_s, '-movflags', '+faststart', tmp])
        lufs, pk = loudness(tmp)
        res = {'audio': 'mix', 'src': audio, 'start': start, 'sfx': sfx_wav, 'sfx_gain': sfx_gain, 'limit': round(limit, 4),
               'lufs': lufs, 'true_peak': pk, 'attempts': attempt + 1, 'audio_window': mix_dur}
        if pk is None or pk <= -1.0 or pk == float('-inf'):
            break
        limit *= 10 ** ((-1.3 - pk) / 20)
        log(f'audio: AAC true peak {pk:.2f} dBTP > -1.0, lowering limiter to {limit:.3f}')
    os.replace(tmp, out)
    return res


# ================================================================================ recorded SFX

def resolve_sfx(W, E, a):
    """Use an existing, timeline-aligned recorded bed; never create synthetic sound."""
    au = E.get('audio') or {}
    if au.get('beat'):
        die('audio.beat synthesis is disabled; select an existing track and set audio.src')
    spec = getattr(a, 'sfx_file', None) or au.get('sfx_src')
    enabled = a.sfx if a.sfx is not None else bool(spec or au.get('sfx', False))
    if not enabled:
        return None
    if not isinstance(spec, str) or not spec.strip():
        die('recorded SFX bed missing; use --sfx-file or audio.sfx_src with a real aligned recording')
    path = spec if os.path.isabs(spec) else os.path.join(W, spec)
    if not os.path.isfile(path) or not rrio.probe(path).get('has_audio'):
        die(f'recorded SFX bed is unavailable or has no audio: {path}')
    return path


# ================================================================================ commands
def setup_ws(W):
    global LOG_PATH
    W = os.path.abspath(W)
    if not os.path.isdir(W):
        die(f'workspace not found: {W}')
    os.makedirs(os.path.join(W, 'comp'), exist_ok=True)
    LOG_PATH = os.path.join(W, 'comp', 'render.log')
    return W


def dump_dir(W, kind=''):
    """Every frame dump lives under W/comp/frames/ (the full render itself, preview/, stills/), the one tree
    rr_save prunes, so a state archive never carries frames that the next render recreates for free."""
    return os.path.join(W, 'comp', 'frames', kind) if kind else os.path.join(W, 'comp', 'frames')


DUMP_RE = re.compile(r'(\d+)\.(jpg|png)')


def clear_dump(d, lo=None, hi=None):
    """Delete frame files (NNNNN.jpg|png, and stale .part files) in d, only [lo, hi) when given; subdirs stay."""
    for f in glob.glob(os.path.join(d, '*')):
        b = os.path.basename(f)
        if not os.path.isfile(f):
            continue
        m = DUMP_RE.fullmatch(b)
        if b.endswith('.part') or (m and (lo is None or lo <= int(m.group(1)) < hi)):
            try:
                os.remove(f)
            except OSError:
                pass


def info_pass(W, a, chrome, rs=1.0):
    sink = Sink(W, dump_dir(W, 'unused'), dump_dir(W, 'stills'))
    ok, _ = run_pages(W, sink, chrome, [('info', None, {'mode': 'info', 'edl': '/' + a.edl.lstrip('/'), 'fx': a.fx, 'rs': rs})],
                      gpu=a.gpu, timeout=a.timeout, stall=a.stall, label='info')
    return sink.info or {}, sink.cues or []


def cmd_info(a):
    W = setup_ws(a.W)
    load_edl(W, a.edl)
    chrome = find_chrome(a.chrome) or die('no Chrome/Chromium found (set CHROME=/path or --chrome)')
    inf, cues = info_pass(W, a, chrome)
    rrio.save_json(os.path.join(W, 'comp', 'info.json'), inf)
    rrio.save_json(os.path.join(W, 'comp', 'sfx_cues.json'), cues)
    log(f"info: {inf.get('w')}x{inf.get('h')} @{inf.get('fps')} {inf.get('frames')} frames, {inf.get('shots')} shots, "
        f"stickers {((inf.get('stickers') or {}).get('placed'))}, {len(cues)} sfx cues, {len(inf.get('warnings') or [])} warnings")
    for w in inf.get('warnings') or []:
        log('  WARN ' + w)
    print(json.dumps({'info': os.path.join(W, 'comp', 'info.json'), 'cues': os.path.join(W, 'comp', 'sfx_cues.json'),
                      'frames': inf.get('frames'), 'warnings': len(inf.get('warnings') or [])}))


def cmd_sfx(a):
    die('procedural SFX synthesis is disabled; align actual stock recordings and use --sfx-file or audio.sfx_src')


def cmd_serve(a):
    W = setup_ws(a.W)
    sink = Sink(W, dump_dir(W, 'serve'), dump_dir(W, 'stills'))
    srv = Server(sink, a.port)
    print(f'serving {W} at http://127.0.0.1:{srv.port}/_rr/page.html  (open it yourself; Ctrl-C to stop)', flush=True)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        srv.close()


def cmd_render(a):
    W = setup_ws(a.W)
    E, edl_path = load_edl(W, a.edl)
    fps = edl_fps(E)
    sfx_wav = None if a.stills else resolve_sfx(W, E, a)
    chrome = find_chrome(a.chrome) or die('no Chrome/Chromium found (set CHROME=/path or --chrome)')
    rs = 0.5 if a.preview else float(a.rs)
    nf = edl_frames(E)
    ext = 'png' if a.fmt == 'png' else 'jpg'
    t_all = time.time()
    log(f'render: W={W} edl={os.path.relpath(edl_path, W)} chrome={chrome} rs={rs} dump={ext}')
    if not (E.get('canvas') or {}).get('frames'):
        log('render: canvas.frames is not set; the frame count comes from canvas.dur / the last shot '
            '(set canvas.frames = the reference video frame count)')
    if nf is None:
        inf, _ = info_pass(W, a, chrome, rs)
        nf = inf.get('frames')
        if not nf:
            die('could not determine the frame count (set canvas.frames)')
    au = E.get('audio') or {}
    # ---------------------------------------------------------------- stills
    if a.stills:
        frames = parse_frames_spec(a.stills, E, nf)
        if not frames:
            die('no valid frames in --stills')
        sd = dump_dir(W, 'stills')
        os.makedirs(sd, exist_ok=True)
        for f in frames:  # a stale still of the other format must not satisfy the sheet
            for e in ('jpg', 'png'):
                if os.path.isfile(os.path.join(sd, f'{f:05d}.{e}')):
                    os.remove(os.path.join(sd, f'{f:05d}.{e}'))
        sink = Sink(W, dump_dir(W, 'unused'), sd)
        q = {'mode': 'stills', 'edl': '/' + a.edl.lstrip('/'), 'fx': a.fx, 'rs': rs, 'q': a.quality, 'cues': '1',
             'fmt': 'png' if ext == 'png' else None}
        n = max(1, min(a.jobs or 2, len(frames) // 4 or 1))
        chunks = [frames[i::n] for i in range(n)]
        run_pages(W, sink, chrome, [(f's{i}', c, q) for i, c in enumerate(chunks) if c], gpu=a.gpu, timeout=a.timeout,
                  stall=a.stall, label='stills', kind='still')
        paths = [os.path.join(sd, f'{f:05d}.{ext}') for f in frames]
        lost = [f for f, pth in zip(frames, paths) if not os.path.isfile(pth)]
        if lost:
            die(f'{len(lost)} still(s) missing after the stills pass, e.g. {lost[:10]}')
        labels = [f'f{f} {f / float(fps):.2f}s' for f in frames]
        sheet = a.sheet if a.sheet else os.path.join(W, 'qa', 'comp_stills.jpg')
        sheet = sheet if os.path.isabs(sheet) else os.path.join(W, sheet)
        os.makedirs(os.path.dirname(sheet), exist_ok=True)
        cols = a.cols or (2 if len(frames) <= 4 else 3 if len(frames) <= 9 else 4)
        res = rrio.tile_sheet(paths, labels, cols=cols, out_path=sheet, tile_w=a.tile_w or 400, max_bytes=a.max_bytes,
                              max_w=1600, title=f'{os.path.basename(W)} stills ({len(frames)})')
        _report_page(sink)
        log(f"stills: {len(frames)} -> {sd}; sheet {sheet} ({res['bytes']} bytes)")
        print(json.dumps({'stills': paths, 'sheet': sheet, 'sheet_bytes': res['bytes']}))
        return
    # ---------------------------------------------------------------- frames
    if a.frames:
        sel = parse_frames_spec(a.frames, E, nf)
        if not sel or sel != list(range(sel[0], sel[-1] + 1)):
            die('--frames must be a contiguous range A:B inside the edit')
        f0, f1 = sel[0], sel[-1] + 1
    else:
        f0, f1 = 0, nf
    fdir = dump_dir(W, 'preview') if a.preview else dump_dir(W)
    os.makedirs(fdir, exist_ok=True)
    if a.frames:
        clear_dump(fdir, f0, f1)
    else:
        clear_dump(fdir)
    total = f1 - f0
    # each Chrome costs ~1-3 s to start + boot, and renders ~10-25 frames/s on its own: about 1 instance per 40 frames,
    # at most half the CPUs and 6 (8 vCPU sandbox -> 4)
    jobs = a.jobs or max(1, min((os.cpu_count() or 4) // 2, 6, math.ceil(total / 40)))
    jobs = max(1, min(jobs, math.ceil(total / 12)))
    step = math.ceil(total / jobs)
    spec = []
    q = {'mode': 'render', 'edl': '/' + a.edl.lstrip('/'), 'fx': a.fx, 'rs': rs, 'q': a.quality,
         'fmt': 'png' if ext == 'png' else None}
    for i in range(jobs):
        a0, a1 = f0 + i * step, min(f1, f0 + (i + 1) * step)
        if a0 < a1:
            spec.append((str(i), list(range(a0, a1)), dict(q, cues='1') if i == 0 else q))
    sink = Sink(W, fdir, dump_dir(W, 'stills'))
    try:
        _, r_secs = run_pages(W, sink, chrome, spec, gpu=a.gpu, timeout=a.timeout, stall=a.stall, label='render')
    except RuntimeError as e:
        die(str(e))
    _report_page(sink)
    if sink.info:
        log(f"render: page boot {sink.info.get('boot_ms')} ms; in-page loop per shard (s): "
            f"{[round(v.get('secs', 0), 2) for v in sink.done.values()]}")
    if sink.info and sink.info.get('frames') != nf:
        die(f"frame count mismatch: render.py computed {nf}, engine says {sink.info.get('frames')}")
    missing = [f for f in range(f0, f1) if not os.path.isfile(os.path.join(fdir, f'{f:05d}.{ext}'))]
    if missing:
        die(f'{len(missing)} frame(s) missing after render, e.g. {missing[:10]}')
    if sink.cues is not None:
        rrio.save_json(os.path.join(W, 'comp', 'sfx_cues.json'), sink.cues)
    # ---------------------------------------------------------------- encode
    out = a.out or os.path.join('out', 'comp_preview.mp4' if a.preview else ('comp_part.mp4' if a.frames else 'comp.mp4'))
    out = out if os.path.isabs(out) else os.path.join(W, out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    t = time.time()
    vtmp = out + '.video.mp4'
    encode(fdir, f0, total, fps, vtmp, crf=a.crf, preset=a.preset, ext=ext)
    e_secs = time.time() - t
    log(f'encode: {total} {ext} frames -> x264 crf {a.crf} {a.preset} in {e_secs:.1f}s')
    dur = total / float(fps)
    audio = resolve_audio(W, E, a)
    start = a.audio_start if a.audio_start is not None else float(au.get('start', 0))
    start += f0 / float(fps)
    gain = a.sfx_gain if a.sfx_gain is not None else float(au.get('sfx_gain', 0.6))
    ares = mux(vtmp, out, dur, audio, start, sfx_wav, gain, float(au.get('limit', 0.79)),
               a.aac or au.get('codec') == 'aac', sfx_start=f0 / float(fps), preserve_tail=not bool(a.frames))
    os.remove(vtmp)
    pr = rrio.probe(out, count=True)
    if pr.get('frames') != total:
        die(f"encoded frame count {pr.get('frames')} != {total}")
    if a.clean:  # otherwise the dump stays until the next render (rr_save leaves out comp/frames/)
        clear_dump(fdir)
    summary = {'out': out, 'frames': total, 'fps': rrio.fps_str(fps), 'w': pr.get('w'), 'h': pr.get('h'),
               'duration': round(dur, 4), 'dump': ext, 'render_s': round(r_secs, 1), 'render_fps': round(total / r_secs, 2) if r_secs else None,
               'encode_s': round(e_secs, 1), 'total_s': round(time.time() - t_all, 1), 'jobs': len(spec), 'audio': ares,
               'warnings': (sink.info or {}).get('warnings', [])}
    rrio.save_json(os.path.join(W, 'comp', 'render_summary.json'), summary)
    au_s = ares.get('audio')
    if ares.get('true_peak') is not None:
        au_s += f" {ares.get('lufs')} LUFS / {ares.get('true_peak')} dBTP"
    log(f"render: done -> {out} ({total} frames, {pr.get('w')}x{pr.get('h')}, {summary['render_fps']} fps render, "
        f"audio {au_s}, total {summary['total_s']}s)")
    print(json.dumps(summary))


def _report_page(sink):
    inf = sink.info or {}
    st = inf.get('stickers') or {}
    for line in st.get('log') or []:
        log('  ' + line)
    for w in inf.get('warnings') or []:
        log('  WARN ' + w)


def main(argv=None):
    ap = argparse.ArgumentParser(description='Canvas compositor runner: prep plates, render the EDL in headless Chrome, encode + mux.')
    sp = ap.add_subparsers(dest='cmd', required=True)

    def common(p):
        p.add_argument('W', help='workspace dir')
        p.add_argument('--edl', default='comp/edl.json', help='EDL path relative to W (default comp/edl.json)')
        p.add_argument('--fx', default='/comp/fx.js', help='project hooks URL path ("" to disable)')
        p.add_argument('--chrome', help='Chrome/Chromium binary (default: $CHROME or auto-detect)')
        p.add_argument('--gpu', action='store_true', help='do not pass --disable-gpu (local Macs only)')
        p.add_argument('--timeout', type=int, default=1800, help='overall timeout in seconds')
        p.add_argument('--stall', type=int, default=120, help='relaunch a shard after N s without a new frame')

    p = sp.add_parser('prep', help='extract plates (JPEG) and mattes (PNG alpha) for one clip')
    p.add_argument('W')
    p.add_argument('video')
    p.add_argument('--clip', required=True, help='clip id (folder name under plates/ and mattes/)')
    g = p.add_mutually_exclusive_group()
    g.add_argument('--width', type=int, help='plate width (keeps aspect); default: native size')
    g.add_argument('--height', type=int)
    g.add_argument('--native', action='store_true', help='native size (default; keep it for face-lock headroom)')
    p.add_argument('--quality', type=int, default=3, help='JPEG qscale 2..31 (default 3)')
    p.add_argument('--start', type=int, default=0, help='first source frame')
    p.add_argument('--count', type=int, default=0, help='number of frames (0 = to the end)')
    p.add_argument('--mask', help='matte video (remove_background output, SAM mask or alpha video)')
    p.add_argument('--mask-mode', default='divide', choices=['divide', 'threshold', 'luma', 'alpha'])
    p.add_argument('--mask-width', type=int, help='matte width (default plate width / 2)')
    p.add_argument('--thr', type=int, default=26, help='threshold for --mask-mode threshold (tv-range luma)')
    p.add_argument('--close', type=int, default=0, help='morphological close (dilate N, erode N) before the blur')
    p.add_argument('--vf', help='extra ffmpeg filters applied to the plates before scaling (bake a grade, e.g. a lut3d)')
    p.set_defaults(fn=cmd_prep)

    p = sp.add_parser('render', help='render frames in headless Chrome and encode out/comp.mp4')
    common(p)
    p.add_argument('--jobs', type=int, default=0, help='Chrome instances (default min(8, cpus/2))')
    p.add_argument('--preview', action='store_true', help='half resolution -> out/comp_preview.mp4')
    p.add_argument('--rs', default='1', help='resolution scale (preview = 0.5)')
    p.add_argument('--stills', help="frames to render as stills + QA sheet: '0,24,60' | '1.5s' | 'cuts' | 'A:B'")
    p.add_argument('--sheet', help='stills sheet path (default W/qa/comp_stills.jpg)')
    p.add_argument('--cols', type=int, default=0)
    p.add_argument('--tile-w', type=int, default=0)
    p.add_argument('--max-bytes', type=int, default=500_000)
    p.add_argument('--frames', help='render + encode only the contiguous range A:B (out/comp_part.mp4)')
    p.add_argument('--out', help='output mp4 (default out/comp.mp4)')
    p.add_argument('--crf', type=int, default=18)
    p.add_argument('--preset', default='medium')
    p.add_argument('--quality', type=float, default=0.93, help='JPEG quality of the frame dump (0..1)')
    p.add_argument('--fmt', choices=['jpg', 'png'], default='jpg',
                   help='frame dump format: jpg (default, fast) or png (lossless, ~5-10x bigger and slower; '
                        'for pixel QA, or frames you grade further)')
    p.add_argument('--audio', default='auto', help="'auto' (edl.audio.src or ref/ref.mp4), 'none', or a path")
    p.add_argument('--audio-start', type=float, default=None, help='seconds into the audio source')
    p.add_argument('--sfx', dest='sfx', action='store_true', default=None, help='mix the recorded bed specified by --sfx-file or audio.sfx_src')
    p.add_argument('--sfx-file', help='existing aligned recorded SFX bed; source from stock/reference audio')
    p.add_argument('--no-sfx', dest='sfx', action='store_false')
    p.add_argument('--sfx-gain', type=float, default=None)
    p.add_argument('--aac', action='store_true', help='re-encode a non-AAC reference track to AAC 256k instead of copying it')
    p.add_argument('--clean', action='store_true', help='delete the frame dump after encoding')
    p.set_defaults(fn=cmd_render)

    p = sp.add_parser('info', help='validate the EDL in Chrome, write comp/info.json + comp/sfx_cues.json')
    common(p)
    p.set_defaults(fn=cmd_info)

    p = sp.add_parser('sfx', help='disabled legacy synthesis command; use a recorded SFX bed')
    p.add_argument('W')
    p.add_argument('--edl', default='comp/edl.json')
    p.add_argument('--cues', default='comp/sfx_cues.json')
    p.add_argument('--out', default='comp/sfx.wav')
    p.set_defaults(fn=cmd_sfx)

    p = sp.add_parser('serve', help='serve W for a manual preview (prints the URL)')
    p.add_argument('W')
    p.add_argument('--port', type=int, default=0)
    p.set_defaults(fn=cmd_serve)

    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] not in ('prep', 'render', 'info', 'sfx', 'serve', '-h', '--help') and os.path.isdir(argv[0]):
        argv.insert(0, 'render')  # `render.py W ...` == `render.py render W ...`
    a = ap.parse_args(argv)
    if getattr(a, 'fx', None) == '':
        a.fx = ''
    try:
        a.fn(a)
    except RuntimeError as e:
        die(str(e))


if __name__ == '__main__':
    main()
