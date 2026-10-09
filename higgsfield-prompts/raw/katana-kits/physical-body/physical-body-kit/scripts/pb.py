#!/usr/bin/env python3
"""pb.py - CLI of the physical-body skill (python3 stdlib only; ffmpeg + headless Chrome do the pixel work).

usage: python3 -I pb.py <command> <job_dir> [options]

  assets                           install the engine pages (engine/*.html.txt -> .html) and download + verify the
                                   binary assets pinned by assets.json (template music, QA reference frames)
  doctor [job]                     environment check (ffmpeg encoders/filters, Chrome, engine, template, smoke render)
  init <job> --video V [--slug S] [--start s] [--max-dur s]
                                   normalize the clip: 30 fps CFR, working size (covers 1920x1080, up to 2160 px on the
                                   short side so close-ups stay sharp), <= 60 s -> shots/v0.mp4, its sound -> shots/a0.wav,
                                   480 px analysis frames -> web/ana/v0/*.jpg
  prep <job>                       hard cuts (scdet) + per-frame analysis in Chrome (faces/eyes, motion, luma, sharpness,
                                   bright spots) -> features.json
  edit <job> [--no-sheet]          template slots -> moments of the clip -> per-slot crops (web/crops), point tracks,
                                   web/plan.json, edit_report.json, review sheets qa/edit_NN.jpg; <job>/fixes.json pins
                                   slots (references/fixes.md)
  render <job> [--sfx|--no-sfx] [--no-qa]
                                   frames in parallel Chrome -> music (+ the clip's own sound, picture-locked) ->
                                   out/<slug>.mp4, then qa
  qa <job>                         checks + comparison sheets (template reference | this render) -> qa/qa.json, qa/cmp_NN.jpg
  sheet <job> --f a,b,c [--name N] labelled stills of the plan at output frames a,b,c -> qa/<N>.jpg
  thumbs <job>                     small copies of the review sheets (<= 125 KB each) -> qa/small/*.jpg
  srcsheet <job>                   source contact sheets for choosing pins (tile i = frame 720*K + 15*i) -> qa/small/src_KK.jpg
  frames <job> N [N ...]           up to 12 chosen source frames side by side -> qa/small/frames.jpg
  serve <job>                      debug server (index.html: arrows step frames, shift = 10 frames)
  status <job>                     job summary

Exit codes: 0 ok, 1 problems (prep/render/qa), 2 usage or input error.
Env: PB_CHROME (Chrome binary), PB_PAR (parallel Chrome instances, default 8).
"""
import argparse
import atexit
import glob
import hashlib
import json
import math
import os
import re
import shutil
import signal
import socket
import subprocess
import sys
import tarfile
import tempfile
import threading
import time
import urllib.parse
import urllib.request
import uuid
from concurrent.futures import ThreadPoolExecutor

sys.dont_write_bytecode = True
SCRIPTS = os.path.dirname(os.path.abspath(__file__))
SK = os.path.dirname(SCRIPTS)
ENGINE = os.path.join(SK, 'engine')
TEMPLATE = os.path.join(SK, 'template')
ASSETS_JSON = os.path.join(SK, 'assets.json')       # binary assets (CDN archive); see cmd_assets
ASSET_DIRS = ('template/',)                          # the only place assets.json may write to
ENGINE_PAGES = ('index.html', 'ana.html')           # bundled as engine/<page>.txt
MAC_CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'


def find_chrome():
    """PB_CHROME, else Google Chrome on macOS, else a Playwright Chromium (Linux hosts such as the Higgsfield sandbox)"""
    if os.environ.get('PB_CHROME'):
        return os.environ['PB_CHROME']
    cands = [MAC_CHROME]
    roots = [os.environ.get('PLAYWRIGHT_BROWSERS_PATH') or '', '/ms-playwright', os.path.expanduser('~/.cache/ms-playwright')]
    for root in [r for r in roots if r]:
        cands += sorted(glob.glob(os.path.join(root, 'chromium-*', 'chrome-linux*', 'chrome')), reverse=True)
        cands += sorted(glob.glob(os.path.join(root, 'chromium_headless_shell-*', 'chrome-linux*', 'headless_shell')),
                        reverse=True)
    cands += [shutil.which(n) or '' for n in ('google-chrome', 'chromium', 'chromium-browser')]
    return next((c for c in cands if c and os.path.exists(c)), MAC_CHROME)


CHROME = find_chrome()
MAC = sys.platform == 'darwin'
# faces: Chrome's FaceDetector exists on macOS only; elsewhere scripts/ana.py runs YuNet (numpy + onnxruntime)
FACES = os.environ.get('PB_FACES') or ('chrome' if MAC else 'yunet')
MODEL = os.path.join(SK, 'template', 'models', 'face_detection_yunet_2023mar.onnx')
FFMPEG = shutil.which('ffmpeg') or 'ffmpeg'
FFPROBE = shutil.which('ffprobe') or 'ffprobe'
PAR = max(1, int(os.environ.get('PB_PAR', '8') or 8))
FPS, OUT_W, OUT_H = 30, 1920, 1080
CLIP = 'v0'
MAX_DUR, MIN_DUR = 60.0, 3.0
MAX_SHORT = 2160                                     # working copy: at most this many px on the short side
DELIVER_MB = 27.0                                    # final file target (chat upload limit is 30 MB)
ANA_W = 480
SR = 48000
SCD_T, SCD_PEAK, SCD_MIN_GAP = 6.0, 3.0, 8           # scdet hard-cut score, x over neighbours, min frames apart
CHROME_FLAGS = ['--window-size=1920,1080', '--no-first-run', '--no-default-browser-check',
                '--disable-background-timer-throttling', '--disable-renderer-backgrounding',
                '--disable-backgrounding-occluded-windows'] + (
    ['--enable-gpu', '--use-angle=metal'] if sys.platform == 'darwin' else
    ['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu', '--no-zygote'])
EXPERIMENTAL = '--enable-experimental-web-platform-features'
SLUG_RE = re.compile(r'^[a-z0-9][a-z0-9_-]{0,47}$')
NAME_RE = re.compile(r'^[A-Za-z0-9_.-]{1,76}$')


# ============================================================================ helpers
def die(msg, code=2):
    print('ERROR: ' + msg, file=sys.stderr)
    sys.exit(code)


def J(*p):
    return os.path.join(*p)


def jload(path, default=None):
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        if default is not None:
            return default
        raise


def jsave(path, obj, indent=1):
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=indent)
        f.write('\n')
    os.replace(tmp, path)


def run(args, cwd=None, check=True, timeout=None):
    p = subprocess.run([str(a) for a in args], cwd=cwd, stdin=subprocess.DEVNULL, capture_output=True, text=True,
                       errors='replace', timeout=timeout)
    if check and p.returncode != 0:
        tail = (p.stderr or p.stdout or '').strip().splitlines()[-8:]
        raise RuntimeError('%s failed (%d): %s' % (os.path.basename(str(args[0])), p.returncode, ' | '.join(tail)))
    return p


def ff(*args, cwd=None, check=True):
    return run([FFMPEG, '-nostdin', '-hide_banner', *args], cwd=cwd, check=check)


def ff_bytes(*args):
    p = subprocess.run([FFMPEG, '-nostdin', '-hide_banner', '-loglevel', 'error', *[str(a) for a in args]],
                       stdin=subprocess.DEVNULL, capture_output=True)
    if p.returncode != 0:
        raise RuntimeError('ffmpeg failed: %s' % p.stderr.decode('utf-8', 'replace').strip()[-400:])
    return p.stdout


def tmpdir(job):
    d = J(job, 'tmp')
    os.makedirs(d, exist_ok=True)
    return d


def count_files(d, ext):
    try:
        return sum(1 for n in os.listdir(d) if n.endswith(ext))
    except FileNotFoundError:
        return 0


def clear_dir(d, ext):
    os.makedirs(d, exist_ok=True)
    for n in os.listdir(d):
        if n.endswith(ext):
            try:
                os.remove(J(d, n))
            except OSError:
                pass


def now_iso():
    return time.strftime('%Y-%m-%dT%H:%M:%S')


def job_path(arg):
    return os.path.abspath(os.path.expanduser(arg))


def load_job(job):
    p = J(job, 'job.json')
    if not os.path.exists(p):
        die('no job.json in %s (run: pb.py init <job> --video V)' % job)
    return jload(p)


def save_job(job, st):
    jsave(J(job, 'job.json'), st)


def mark_step(job, name, **info):
    st = load_job(job)
    st.setdefault('steps', {})[name] = dict(at=now_iso(), **info)
    save_job(job, st)


def template():
    p = J(TEMPLATE, 'timeline.json')
    if not os.path.exists(p):
        die('template/timeline.json missing (skill not installed completely)')
    return jload(p)


def probe_geometry(path):
    """display size (rotation applied), fps, duration, audio presence of a media file."""
    p = run([FFPROBE, '-v', 'error', '-show_entries',
             'stream=codec_type,width,height,r_frame_rate,avg_frame_rate,codec_name:stream_tags=rotate:'
             'stream_side_data=rotation:format=duration', '-of', 'json', path], check=False)
    if p.returncode != 0:
        return None
    try:
        d = json.loads(p.stdout)
        streams = d.get('streams') or []
        s = next(x for x in streams if x.get('codec_type') == 'video')
    except (ValueError, StopIteration):
        return None
    w, h, rot = int(s.get('width') or 0), int(s.get('height') or 0), 0
    try:
        rot = int(float((s.get('tags') or {}).get('rotate') or 0))
    except ValueError:
        pass
    for sd in s.get('side_data_list') or []:
        if 'rotation' in sd:
            try:
                rot = int(float(sd['rotation']))
            except (TypeError, ValueError):
                pass
    if abs(rot) % 180 == 90:
        w, h = h, w

    def rate(v):
        n, _, dd = (v or '0/1').partition('/')
        try:
            return float(n) / float(dd or 1) if float(dd or 1) else 0.0
        except ValueError:
            return 0.0
    return {'w': w, 'h': h, 'fps': rate(s.get('avg_frame_rate')) or rate(s.get('r_frame_rate')),
            'codec': s.get('codec_name'), 'dur': float((d.get('format') or {}).get('duration') or 0),
            'audio': any(x.get('codec_type') == 'audio' for x in streams)}


def venc_args(quality='master', dur=None):
    """master: near-lossless working copy. deliver: sized for the chat upload limit (DELIVER_MB incl. 256k audio)."""
    enc = ff('-encoders').stdout
    mb = None
    if quality == 'deliver':
        mb = max(4.0, min(24.0, DELIVER_MB * 8.0 / max(1.0, dur or 11.8) - 0.3))
    if re.search(r'\slibx264\s', enc):
        if mb:
            return ['-c:v', 'libx264', '-preset', 'slow', '-b:v', '%.1fM' % mb, '-maxrate', '%.1fM' % (mb * 1.3),
                    '-bufsize', '%.1fM' % (mb * 2), '-tune', 'grain', '-profile:v', 'high']
        return ['-c:v', 'libx264', '-preset', 'veryfast', '-crf', '12', '-g', str(FPS)]
    if 'h264_videotoolbox' in enc:
        return ['-c:v', 'h264_videotoolbox', '-b:v', '%.1fM' % mb if mb else '60M', '-profile:v', 'high', '-g', str(FPS)]
    raise RuntimeError('no H.264 encoder (libx264 / h264_videotoolbox) in ffmpeg')


# ============================================================================ server + headless Chrome
_LIVE, _LIVE_LOCK = set(), threading.Lock()


def _cleanup_all():
    with _LIVE_LOCK:
        items = list(_LIVE)
    for obj in items:
        try:
            obj.stop()
        except Exception:
            pass


atexit.register(_cleanup_all)


def _sigterm(signum, frame):
    raise SystemExit(130)


signal.signal(signal.SIGTERM, _sigterm)
_LOCAL = urllib.request.build_opener(urllib.request.ProxyHandler({}))      # never route 127.0.0.1 via a proxy


def _free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()
    return port


class Server:
    """scripts/serve.py on a free port: GET from <job>/web then engine/, POST frames/shots/tracks/log."""

    def __init__(self, job):
        self.job, self.web, self.proc, self.base = job, J(job, 'web'), None, None

    def __enter__(self):
        os.makedirs(self.web, exist_ok=True)
        for _ in range(5):
            port = _free_port()
            log = open(J(tmpdir(self.job), 'serve.log'), 'ab')
            self.proc = subprocess.Popen([sys.executable, '-I', J(SCRIPTS, 'serve.py'), self.web, ENGINE, str(port)],
                                         stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                                         start_new_session=True)
            log.close()
            with _LIVE_LOCK:
                _LIVE.add(self)
            self.base = 'http://127.0.0.1:%d/' % port
            if self._verify():
                return self
            self.stop()
        raise RuntimeError('could not start serve.py; see %s' % J(self.job, 'tmp', 'serve.log'))

    def _verify(self):
        t0 = time.time()
        while time.time() - t0 < 10:
            if self.proc.poll() is not None:
                return False
            try:
                with _LOCAL.open(self.base + '__root', timeout=2) as r:
                    return os.path.realpath(r.read().decode('utf-8', 'replace')) == os.path.realpath(self.web)
            except Exception:
                time.sleep(0.1)
        return False

    def stop(self):
        if self.proc and self.proc.poll() is None:
            for sig in (signal.SIGTERM, signal.SIGKILL):
                try:
                    os.killpg(self.proc.pid, sig)
                except (ProcessLookupError, PermissionError):
                    pass
                try:
                    self.proc.wait(3)
                    break
                except subprocess.TimeoutExpired:
                    continue
        with _LIVE_LOCK:
            _LIVE.discard(self)

    def __exit__(self, *exc):
        self.stop()
        return False


def _ps_kill(marker):
    p = run(['ps', '-axo', 'pid=,command='], check=False)
    me = os.getpid()
    for line in p.stdout.splitlines():
        pid, _, cmd = line.strip().partition(' ')
        if marker in cmd and pid.isdigit() and int(pid) != me:
            try:
                os.kill(int(pid), signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                pass


class Chrome:
    """one headless Chrome with a fresh profile under <job>/tmp; stop() kills it and removes the profile."""

    def __init__(self, job, url, tag='c', extra=()):
        if not os.path.exists(CHROME):
            raise RuntimeError('Google Chrome not found at %s (set PB_CHROME)' % CHROME)
        self.profile = J(tmpdir(job), 'chrome_%s_%s' % (tag, uuid.uuid4().hex[:8]))
        os.makedirs(self.profile)
        self.errlog = self.profile + '.log'
        log = open(self.errlog, 'wb')
        self.proc = subprocess.Popen([CHROME, '--headless=new', '--user-data-dir=' + self.profile, *CHROME_FLAGS, *extra, url],
                                     stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, start_new_session=True)
        log.close()
        with _LIVE_LOCK:
            _LIVE.add(self)

    def alive(self):
        return self.proc.poll() is None

    def stop(self, keep_log=False):
        if self.proc.poll() is None:
            for sig in (signal.SIGTERM, signal.SIGKILL):
                try:
                    os.killpg(self.proc.pid, sig)
                except (ProcessLookupError, PermissionError):
                    pass
                try:
                    self.proc.wait(3)
                    break
                except subprocess.TimeoutExpired:
                    continue
        _ps_kill(self.profile)
        for _ in range(3):
            shutil.rmtree(self.profile, ignore_errors=True)
            if not os.path.exists(self.profile):
                break
            time.sleep(0.3)
        if not keep_log:
            try:
                os.remove(self.errlog)
            except OSError:
                pass
        with _LIVE_LOCK:
            _LIVE.discard(self)


class LogTail:
    """lines appended to web/log.txt after construction."""

    def __init__(self, path):
        self.path, self.buf, self.lines, self.lock = path, '', [], threading.Lock()
        try:
            self.off = os.path.getsize(path)
        except OSError:
            self.off = 0

    def poll(self):
        with self.lock:
            try:
                with open(self.path, 'rb') as f:
                    f.seek(self.off)
                    data = f.read()
            except FileNotFoundError:
                return []
            if not data:
                return []
            self.off += len(data)
            parts = (self.buf + data.decode('utf-8', 'replace')).split('\n')
            self.buf = parts.pop()
            new = [p.rstrip('\r') for p in parts if p.strip()]
            self.lines.extend(new)
            return new

    def has(self, pred):
        return any(pred(l) for l in self.lines)


def run_pages(job, srv, tasks, par=PAR, tail=None, label='chrome'):
    """task: {tag, url, done(tail)->bool, fail(tail)->str|None, timeout, extra, retries, reset()} -> {tag: 'ok'|error}"""
    pending, running, result = list(tasks), {}, {}
    try:
        while pending or running:
            while pending and len(running) < par:
                t = pending.pop(0)
                t['tries'] = t.get('tries', 0) + 1
                if t.get('reset'):
                    t['reset']()
                running[t['tag']] = (t, Chrome(job, srv.base + t['url'], t['tag'], t.get('extra', ())), time.time())
            time.sleep(0.15)
            if tail:
                tail.poll()
            for tag, (t, c, ts) in list(running.items()):
                if t['done'](tail):
                    c.stop()
                    del running[tag]
                    result[tag] = 'ok'
                    continue
                err = t['fail'](tail) if t.get('fail') else None
                why = err or (None if c.alive() else 'chrome exited (log %s)' % c.errlog)
                if not why and time.time() - ts > t.get('timeout', 120):
                    why = 'timeout after %ds' % t.get('timeout', 120)
                if why:
                    c.stop(keep_log=not err)
                    del running[tag]
                    if not err and t['tries'] <= t.get('retries', 1):
                        print('  [%s] %s: %s, retrying' % (label, tag, why))
                        pending.append(t)
                    else:
                        result[tag] = why
    finally:
        for t, c, ts in running.values():
            c.stop()
    return result


def capture(job, srv, query, name, timeout=180):
    """render a page that POSTs /shot/<name>.jpg -> <job>/web/shots/<name>.jpg"""
    if not NAME_RE.match(name):
        raise ValueError('bad capture name %r' % name)
    path = J(job, 'web', 'shots', name + '.jpg')
    tail = LogTail(J(job, 'web', 'log.txt'))
    q = urllib.parse.quote(query.lstrip('/'), safe="/?&=,.:;-_~%+!*'()@$")
    res = run_pages(job, srv, [{'tag': 'cap_' + name, 'url': q, 'timeout': timeout, 'retries': 1,
                                'reset': lambda: os.path.exists(path) and os.remove(path),
                                'done': lambda tl: tl.has(lambda l: l == 'sheet done ' + name) and os.path.exists(path),
                                'fail': lambda tl: next((l for l in tl.lines if l.startswith('ERROR')), None)}],
                    par=1, tail=tail, label='sheet')
    if res.get('cap_' + name) != 'ok':
        raise RuntimeError('capture %s failed: %s' % (name, res.get('cap_' + name)))
    return path


def capture_many(job, srv, jobs, timeout=240):
    """[(query, name)] in parallel Chrome instances -> {name: path}"""
    tail = LogTail(J(job, 'web', 'log.txt'))
    tasks = []
    for query, name in jobs:
        path = J(job, 'web', 'shots', name + '.jpg')
        q = urllib.parse.quote(query.lstrip('/'), safe="/?&=,.:;-_~%+!*'()@$")
        tasks.append({'tag': 'cap_' + name, 'url': q, 'timeout': timeout, 'retries': 1,
                      'reset': (lambda path=path: os.path.exists(path) and os.remove(path)),
                      'done': (lambda tl, name=name, path=path: tl.has(lambda l: l == 'sheet done ' + name) and os.path.exists(path)),
                      'fail': (lambda tl: next((l for l in tl.lines if l.startswith('ERROR')), None))})
    res = run_pages(job, srv, tasks, par=min(PAR, len(tasks)), tail=tail, label='sheet')
    bad = {k: v for k, v in res.items() if v != 'ok'}
    if bad:
        raise RuntimeError('sheets failed: %s' % bad)
    return {name: J(job, 'web', 'shots', name + '.jpg') for _, name in jobs}


def web_errors(lines):
    return [l for l in lines if re.search(r'\bERROR\b', l)]


# ============================================================================ assets
# The workflow bundle serves utf-8 text only, so the binaries (template music, QA reference frames) ship as ONE
# tar.gz on the Higgsfield CDN, pinned by <SK>/assets.json:
#   {"archive": {"url", "format": "tar.gz", "sha256", "bytes"}, "files": {"<rel path>": {"sha256", "bytes"}}}
# The engine's HTML pages ship as engine/<page>.html.txt (the bundle has no .html files) and are installed here.
HEX64 = re.compile(r'^[0-9a-f]{64}$')


def _sha256(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(chunk), b''):
            h.update(b)
    return h.hexdigest()


def _asset_rel_ok(rel):
    """a manifest path: relative POSIX path under template/, no '.', '..' or empty segments"""
    if not isinstance(rel, str) or not rel or '\\' in rel or '\0' in rel or rel.startswith('/'):
        return False
    parts = rel.split('/')
    if any(p in ('', '.', '..') for p in parts):
        return False
    return rel.startswith(ASSET_DIRS) and len(parts) >= 2


def read_assets_manifest():
    """<SK>/assets.json -> (archive, files, None) or (None, None, error)."""
    try:
        m = jload(ASSETS_JSON)
    except FileNotFoundError:
        return None, None, 'missing %s (write assets.json from the workflow bundle next to scripts/)' % ASSETS_JSON
    except ValueError as e:
        return None, None, 'invalid JSON in %s: %s' % (ASSETS_JSON, e)
    arc = m.get('archive') if isinstance(m, dict) else None
    files = m.get('files') if isinstance(m, dict) else None
    if not isinstance(arc, dict) or not isinstance(files, dict) or not files:
        return None, None, '%s needs an "archive" object and a non-empty "files" object' % ASSETS_JSON
    if not (isinstance(arc.get('url'), str) and arc['url'].startswith('https://')
            and HEX64.match(str(arc.get('sha256', ''))) and isinstance(arc.get('bytes'), int) and arc['bytes'] > 0
            and arc.get('format') == 'tar.gz'):
        return None, None, '%s: bad "archive" entry (https url, format tar.gz, sha256, bytes)' % ASSETS_JSON
    for rel, meta in files.items():
        if not (_asset_rel_ok(rel) and isinstance(meta, dict) and HEX64.match(str(meta.get('sha256', '')))
                and isinstance(meta.get('bytes'), int) and meta['bytes'] >= 0):
            return None, None, '%s: bad file entry %r' % (ASSETS_JSON, rel)
    return arc, files, None


def asset_problems(files):
    """[(rel, reason)] for every manifest file that is missing, not a regular file, or has the wrong size/sha256."""
    out = []
    for rel, meta in sorted(files.items()):
        p = J(SK, *rel.split('/'))
        if os.path.islink(p) or not os.path.isfile(p):
            out.append((rel, 'missing'))
        elif os.path.getsize(p) != meta['bytes']:
            out.append((rel, 'size %d != %d' % (os.path.getsize(p), meta['bytes'])))
        elif _sha256(p) != meta['sha256']:
            out.append((rel, 'sha256 mismatch'))
    return out


def install_engine_pages():
    """engine/<page>.html.txt -> engine/<page>.html (byte copy, atomic). Returns (installed, missing)."""
    installed, missing = [], []
    for page in ENGINE_PAGES:
        src, dst = J(ENGINE, page + '.txt'), J(ENGINE, page)
        if not os.path.isfile(src):
            if not os.path.isfile(dst):
                missing.append(page)
            continue
        with open(src, 'rb') as f:
            data = f.read()
        if os.path.isfile(dst) and not os.path.islink(dst):
            with open(dst, 'rb') as f:
                if f.read() == data:
                    continue
        tmp = dst + '.part'
        with open(tmp, 'wb') as f:
            f.write(data)
        os.replace(tmp, dst)
        installed.append(page)
    return installed, missing


def _download(url, dst, tries=4):
    # system curl: python.org builds of Python on macOS ship without root certificates, so urllib fails on HTTPS
    part = dst + '.part'
    last = None
    for k in range(tries):
        try:
            r = subprocess.run(['curl', '-fsSL', '--connect-timeout', '20', '--max-time', '600', '-A', 'pb.py/1',
                                '-o', part, url], capture_output=True, text=True)
            if r.returncode != 0:
                raise IOError('curl exit %d: %s' % (r.returncode, r.stderr.strip()[:200]))
            n = os.path.getsize(part)
            if n == 0:
                raise IOError('empty response')
            os.replace(part, dst)
            return n
        except Exception as e:
            last = e
            time.sleep(2 * (k + 1))
    try:
        os.remove(part)
    except OSError:
        pass
    raise RuntimeError('download failed after %d tries: %s' % (tries, last))


def _extract_assets(tgz, files, wanted):
    """Stream the verified archive; write only the `wanted` manifest files. Every member must be a manifest-listed
    regular file with a safe relative path; anything else (absolute, '..', links, devices, unlisted) aborts."""
    root = os.path.realpath(SK)
    seen, written = set(), 0
    with tarfile.open(tgz, 'r:gz') as tf:
        for m in tf:
            rel = m.name[2:] if m.name.startswith('./') else m.name
            if m.isdir() and any(r.startswith(rel.rstrip('/') + '/') for r in files):
                continue                                    # a parent directory entry: nothing to extract
            if not _asset_rel_ok(rel):
                raise RuntimeError('archive member %r: unsafe path' % m.name)
            if not m.isreg():
                raise RuntimeError('archive member %r: not a regular file (link/device/dir)' % m.name)
            if rel not in files:
                raise RuntimeError('archive member %r is not listed in assets.json' % m.name)
            if rel in seen:
                raise RuntimeError('archive member %r appears twice' % m.name)
            if hasattr(tarfile, 'data_filter'):              # Python >= 3.12 (and patched 3.8-3.11): 'data' filter
                try:
                    tarfile.data_filter(m, root)
                except tarfile.FilterError as e:
                    raise RuntimeError('archive member %r rejected by the tarfile data filter: %s' % (m.name, e))
            seen.add(rel)
            meta = files[rel]
            if m.size != meta['bytes']:
                raise RuntimeError('archive member %r: %d bytes, assets.json says %d' % (m.name, m.size, meta['bytes']))
            if rel not in wanted:
                continue
            dst = J(SK, *rel.split('/'))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if not os.path.realpath(os.path.dirname(dst)).startswith(root + os.sep):
                raise RuntimeError('refusing to write %s: its directory resolves outside %s' % (rel, root))
            if os.path.islink(dst):
                os.remove(dst)
            tmp = dst + '.part'
            h, n = hashlib.sha256(), 0
            src = tf.extractfile(m)
            try:
                with open(tmp, 'wb') as f:
                    for b in iter(lambda: src.read(1 << 20), b''):
                        h.update(b)
                        n += len(b)
                        f.write(b)
                if n != meta['bytes'] or h.hexdigest() != meta['sha256']:
                    raise RuntimeError('%s: extracted bytes do not match assets.json (size %d, sha256 %s)'
                                       % (rel, n, h.hexdigest()[:12]))
                os.chmod(tmp, 0o644)
                os.replace(tmp, dst)
            finally:
                if os.path.exists(tmp):
                    os.remove(tmp)
            written += 1
    gone = sorted(set(wanted) - seen)
    if gone:
        raise RuntimeError('archive lacks %d manifest file(s): %s' % (len(gone), ', '.join(gone[:5])))
    return written


def cmd_assets(a):
    arc, files, err = read_assets_manifest()
    if err:
        die(err)
    installed, missing = install_engine_pages()
    if installed:
        print('engine   installed %s' % ', '.join(installed))
    if missing:
        die('engine page(s) missing: %s (write engine/<page>.html.txt from the workflow bundle, then re-run)'
            % ', '.join(missing))
    bad = sorted(files) if a.force else [rel for rel, _ in asset_problems(files)]
    if not bad:
        print('assets   all %d files verified (sha256); nothing to download' % len(files))
        return 0
    print('assets   %d of %d file(s) %s; downloading %.1f MB' % (len(bad), len(files),
          'forced' if a.force else 'missing or invalid', arc['bytes'] / 1e6))
    tmp = tempfile.mkdtemp(prefix='pb_assets_')
    try:
        tgz = J(tmp, 'assets.tar.gz')
        n = _download(arc['url'], tgz)
        if n != arc['bytes']:
            raise RuntimeError('archive is %d bytes, assets.json says %d (re-run pb.py assets; if it persists the '
                               'CDN copy and assets.json disagree)' % (n, arc['bytes']))
        got = _sha256(tgz)
        if got != arc['sha256']:
            raise RuntimeError('archive sha256 %s does not match assets.json %s' % (got, arc['sha256']))
        written = _extract_assets(tgz, files, set(bad))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    left = asset_problems(files)
    if left:
        raise RuntimeError('%d file(s) still invalid after extraction: %s'
                           % (len(left), ', '.join('%s (%s)' % x for x in left[:5])))
    print('assets   wrote %d file(s); all %d verified (sha256)' % (written, len(files)))
    return 0


# ============================================================================ doctor
def cmd_doctor(a):
    ok = True

    def rep(good, what, detail=''):
        nonlocal ok
        print('%-5s %s%s' % ('ok' if good else ('WARN' if good is None else 'FAIL'), what, ('  ' + detail) if detail else ''))
        if good is False:
            ok = False

    rep(sys.version_info >= (3, 9), 'python %s' % sys.version.split()[0])
    for exe in (FFMPEG, FFPROBE):
        rep(bool(shutil.which(os.path.basename(exe)) or os.path.exists(exe)), os.path.basename(exe), exe)
    try:
        enc, fil = ff('-encoders').stdout, ff('-filters').stdout
    except Exception as e:
        rep(False, 'ffmpeg runs', str(e))
        enc = fil = ''
    venc = 'libx264' if re.search(r'\slibx264\s', enc) else ('h264_videotoolbox' if 'h264_videotoolbox' in enc else None)
    rep(bool(venc), 'H.264 encoder', venc or 'none (need libx264 or h264_videotoolbox)')
    rep(bool(re.search(r'\saac\s', enc)), 'aac encoder')
    for f in ('scdet', 'metadata', 'scale', 'fps', 'crop', 'atrim', 'adelay', 'amix', 'alimiter', 'loudnorm', 'volumedetect'):
        rep(bool(re.search(r'\s%s\s' % f, fil)), 'filter ' + f)
    rep(os.path.exists(CHROME), 'Chrome', CHROME)
    for f in ('index.html', 'fx.js', 'ana.html'):
        rep(os.path.exists(J(ENGINE, f)), 'engine/' + f,
            '' if os.path.exists(J(ENGINE, f)) or not os.path.exists(J(ENGINE, f + '.txt')) else 'run: pb.py assets')
    rep(os.path.exists(J(TEMPLATE, 'timeline.json')), 'template/timeline.json')
    arc, files, err = read_assets_manifest()
    if err:
        rep(False, 'assets.json', err)
    else:
        probs = asset_problems(files)
        if probs:
            rep(False, 'binary assets missing or invalid', '%d of %d: %s; run: pb.py assets' % (
                len(probs), len(files), ', '.join('%s (%s)' % x for x in probs[:3]) + (' ...' if len(probs) > 3 else '')))
        else:
            rep(True, 'binary assets', '%d files verified (sha256)' % len(files))
    for f in ('serve.py', 'edit.py', 'track.py') + (('ana.py',) if FACES == 'yunet' else ()):
        rep(os.path.exists(J(SCRIPTS, f)), 'scripts/' + f)
    if FACES == 'yunet':                                    # Linux: faces via YuNet instead of Chrome's FaceDetector
        try:
            import numpy  # noqa: F401
            import onnxruntime  # noqa: F401
            rep(True, 'numpy + onnxruntime (face analysis)')
        except ImportError as e:
            rep(False, 'numpy + onnxruntime (face analysis)', str(e))
        rep(os.path.exists(MODEL), 'face model', MODEL)
    if ok and os.path.exists(CHROME):                       # smoke: serve.py + Chrome + engine render of a solid plan
        tmpjob = tempfile.mkdtemp(prefix='pb_doctor_')
        try:
            jsave(J(tmpjob, 'web', 'plan.json'), {'fps': FPS, 'w': 320, 'h': 180, 'src': {'w': 320, 'h': 180}, 'crops': {},
                                                  'items': {}, 'tracks': {}, 'caps': [[0, 2, 'ok']],
                                                  'segs': [{'f0': 0, 'f1': 2, 'base': {'t': 'solid', 'v': 0.5}, 'layers': [],
                                                            'fx': [{'t': 'burst', 'v': {'1': 0.3}}], 'trk': []}]})
            t0 = time.time()
            with Server(tmpjob) as srv:
                p = capture(tmpjob, srv, 'index.html?sheet=0,1&cols=2&div=1&name=doctor', 'doctor', 40)
            rep(os.path.getsize(p) > 0, 'serve.py + headless Chrome + engine', '%.1fs' % (time.time() - t0))
        except Exception as e:
            rep(False, 'serve.py + headless Chrome + engine', str(e))
        finally:
            shutil.rmtree(tmpjob, ignore_errors=True)
    print('doctor: %s' % ('OK' if ok else 'PROBLEMS FOUND'))
    return 0 if ok else 1


# ============================================================================ init
def work_size(w, h):
    """working size: covers OUT_W x OUT_H with the source aspect kept; sources above MAX_SHORT on the short side are
    scaled down to it, smaller ones are kept (close-ups crop into them), sources below the cover size are scaled up."""
    cover = max(OUT_W / float(w), OUT_H / float(h))
    s = cover if cover >= 1.0 else max(cover, min(1.0, MAX_SHORT / float(min(w, h))))
    return int(math.ceil(w * s / 2 - 1e-6)) * 2, int(math.ceil(h * s / 2 - 1e-6)) * 2


def cmd_init(a):
    job = job_path(a.job)
    src = os.path.abspath(os.path.expanduser(a.video))
    if not os.path.isfile(src):
        die('video not found: %s' % src)
    g = probe_geometry(src)
    if not g or not g['w'] or not g['h']:
        die('not a readable video: %s' % src)
    start = max(0.0, float(a.start or 0))
    avail = g['dur'] - start
    if avail < MIN_DUR:
        die('the clip is %.1f s after --start; need at least %.0f s' % (avail, MIN_DUR))
    maxdur = min(MAX_DUR, float(a.max_dur or MAX_DUR), avail)
    slug = a.slug or re.sub(r'[^a-z0-9_-]+', '_', os.path.splitext(os.path.basename(job))[0].lower()).strip('_-') or 'edit'
    if not SLUG_RE.match(slug):
        die('bad slug %r (a-z 0-9 _ -, max 48)' % slug)
    if os.path.exists(J(job, 'job.json')) and not a.force:
        die('job exists: %s (use --force to re-init)' % job)
    for p in (J(job, 'features.json'), J(job, 'edit_report.json'), J(job, 'web', 'plan.json')):
        if os.path.exists(p):                              # analysis of a previous init: prep must run again
            os.remove(p)
    if os.path.exists(J(job, 'fixes.json')):
        print('NOTE: %s kept; its frame pins refer to the previous init (check them after prep)' % J(job, 'fixes.json'))
    W, H = work_size(g['w'], g['h'])
    for d in ('shots', 'web', 'out', 'qa'):
        os.makedirs(J(job, d), exist_ok=True)
    t0 = time.time()
    v0 = J(job, 'shots', CLIP + '.mp4')
    tmp = v0[:-4] + '.part.mp4'
    vf = 'fps=%d,scale=%d:%d:flags=lanczos,setsar=1,format=yuv420p' % (FPS, W, H)
    ss = ['-ss', '%.3f' % start] if start else []
    ff('-loglevel', 'error', '-y', *ss, '-i', src, '-t', '%.3f' % maxdur, '-map', '0:v:0', '-an', '-sn', '-dn', '-vf', vf,
       '-r', str(FPS), *venc_args(), '-pix_fmt', 'yuv420p', '-color_range', 'tv', '-movflags', '+faststart', tmp)
    os.replace(tmp, v0)
    a0 = J(job, 'shots', 'a0.wav')
    if os.path.exists(a0):
        os.remove(a0)
    if g.get('audio'):
        ff('-loglevel', 'error', '-y', *ss, '-i', src, '-t', '%.3f' % maxdur, '-map', '0:a:0', '-vn', '-ac', '2',
           '-ar', str(SR), '-c:a', 'pcm_s16le', a0, check=False)
    ad = J(job, 'web', 'ana', CLIP)
    clear_dir(ad, '.jpg')
    ff('-loglevel', 'error', '-y', '-i', v0, '-vf', 'scale=%d:-2:flags=area' % ANA_W, '-q:v', '4', '-start_number', '0',
       J(ad, '%05d.jpg'))
    n = count_files(ad, '.jpg')
    if n < MIN_DUR * FPS * 0.9:
        die('frame extraction failed (%d analysis frames)' % n, 1)
    shutil.rmtree(J(job, 'web', 'crops'), ignore_errors=True)
    st = {'slug': slug, 'video_src': src, 'start': start, 'src_geometry': g, 'size': [W, H], 'frames': n,
          'audio': os.path.exists(a0), 'created': now_iso(), 'steps': {}}
    save_job(job, st)
    print('init %s: %dx%d %.2f fps %.1f s%s -> %dx%d, %d frames (%.1f s) in %.1fs' %
          (os.path.basename(src), g['w'], g['h'], g['fps'], g['dur'], ' +audio' if st['audio'] else ' (no audio)', W, H,
           n, n / float(FPS), time.time() - t0))
    if g['h'] > g['w']:
        print('NOTE: vertical clip; the edit is 16:9, so every shot is a crop of the frame (faces are framed automatically)')
    return 0


# ============================================================================ prep
def scd_scores(job):
    d = tmpdir(job)
    name = 'scd_%s.txt' % CLIP
    try:
        os.remove(J(d, name))
    except FileNotFoundError:
        pass
    ff('-loglevel', 'error', '-y', '-i', J(job, 'shots', CLIP + '.mp4'), '-vf',
       'scale=320:-2,scdet=threshold=%g:sc_pass=0,metadata=print:file=%s' % (SCD_T, name), '-an', '-f', 'null', '-', cwd=d)
    scores, cur = {}, None
    with open(J(d, name), encoding='utf-8', errors='replace') as f:
        for line in f:
            m = re.match(r'frame:(\d+)\s', line)
            if m:
                cur = int(m.group(1))
                scores[cur] = 0.0
                continue
            m = re.match(r'lavfi\.scd\.score=([-\d.]+)', line)
            if m and cur is not None:
                scores[cur] = float(m.group(1))
    return scores


def detect_cuts(sc, n):
    def peak(f, s):
        return s >= SCD_PEAK * max([sc.get(g, 0.0) for g in range(f - 4, f + 5) if g != f] + [0.5])
    keep = []
    for f, s in sorted((f, s) for f, s in sc.items() if s >= SCD_T and 4 <= f <= n - 4 and peak(f, s)):
        if keep and f - keep[-1][0] < SCD_MIN_GAP:
            if s > keep[-1][1]:
                keep[-1] = (f, s)
            continue
        keep.append((f, s))
    return keep


def cmd_prep(a):
    job = job_path(a.job)
    st = load_job(job)
    n = int(st['frames'])
    W, H = st['size']
    t0 = time.time()
    cuts = detect_cuts(scd_scores(job), n)
    starts = [0] + [f for f, _ in cuts]
    shots = [{'i': i, 'a': s, 'b': e} for i, (s, e) in enumerate(zip(starts, starts[1:] + [n]))]
    print('cuts: %d hard cuts -> %d shots (%.1fs)' % (len(cuts), len(shots), time.time() - t0))
    web = J(job, 'web')
    clear_dir(J(web, 'track'), '.json')
    t1 = time.time()
    if FACES == 'yunet':
        frames, aw = analyze_python(job, n)
    else:
        frames, aw = analyze_chrome(job, n)
    if len(frames) != n:
        die('analysis has %d frames, expected %d' % (len(frames), n), 1)

    sc = W / float(aw)                                     # analysis px -> working source px
    return finish_prep(job, st, frames, shots, cuts, sc, t0, t1)


def analyze_python(job, n):
    if not os.path.exists(MODEL):
        die('face model missing: %s (run: pb.py assets on a full kit)' % MODEL, 1)
    ana = _mod('ana')
    d = ana.analyze(J(job, 'shots', CLIP + '.mp4'), FFMPEG, FFPROBE, ANA_W, MODEL, n, threads=max(1, (os.cpu_count() or 4)),
                    progress=lambda k, m: print('  analysis %d/%s' % (k, m), flush=True))
    return d['frames'], d['w']


def analyze_chrome(job, n):
    web = J(job, 'web')
    tail = LogTail(J(web, 'log.txt'))
    step = max(48, int(math.ceil(n / float(PAR))))
    tasks = []
    for a0 in range(0, n, step):
        b0 = min(n, a0 + step)
        tasks.append({'tag': 'ana%d' % a0, 'url': 'ana.html?clip=%s&a=%d&b=%d' % (CLIP, a0, b0), 'extra': [EXPERIMENTAL],
                      'timeout': 300, 'retries': 1,
                      'done': (lambda tl, a0=a0, b0=b0: tl.has(lambda l: l.startswith('ana done %s %d-%d ' % (CLIP, a0, b0)))),
                      'fail': (lambda tl, a0=a0, b0=b0: next((l for l in tl.lines if l.startswith('ana ERROR %s %d-%d' % (CLIP, a0, b0))), None))})
    with Server(job) as srv:
        res = run_pages(job, srv, tasks, par=PAR, tail=tail, label='ana')
    bad = {k: v for k, v in res.items() if v != 'ok'}
    if bad:
        die('analysis failed: %s' % bad, 1)
    frames, aw = [], None
    for t in tasks:
        a0, b0 = [int(v) for v in re.findall(r'a=(\d+)&b=(\d+)', t['url'])[0]]
        d = jload(J(web, 'track', '%s_%d_%d.json' % (CLIP, a0, b0)))
        aw = aw or d['w']
        frames.extend(d['frames'])
    return frames, aw


def finish_prep(job, st, frames, shots, cuts, sc, t0, t1):
    n = int(st['frames'])
    W, H = st['size']
    nf = 0
    for i, fr in enumerate(frames):
        if fr is None:
            frames[i] = {'f': [], 'y': 0, 'p5': 0, 'p95': 0, 'sh': 0, 'm': 0, 'hv': 0, 'hx': W / 2, 'hy': H / 2, 'hl': 0,
                         'bad': True}
            continue
        for f in fr['f']:
            f['bb'] = [round(v * sc, 1) for v in f['bb']]
            if f.get('eyes'):
                f['eyes'] = [[round(e[0] * sc, 1), round(e[1] * sc, 1)] for e in f['eyes']]
            if f.get('mouth'):
                f['mouth'] = [round(v * sc, 1) for v in f['mouth']]
        fr['hx'], fr['hy'] = round(fr['hx'] * sc, 1), round(fr['hy'] * sc, 1)
        nf += bool(fr['f'])
    for s in shots:                                        # motion at a shot's first frame is the cut itself
        if 0 < s['a'] < n - 1:
            frames[s['a']]['m'] = frames[s['a'] + 1]['m']
    if n > 1:
        frames[0]['m'] = frames[1]['m']
    feats = {'version': 1, 'clip': CLIP, 'size': [W, H], 'fps': FPS, 'n': n, 'shots': shots,
             'cuts': [[f, round(s, 2)] for f, s in cuts], 'faces': nf, 'frames': frames}
    jsave(J(job, 'features.json'), feats, indent=None)
    mark_step(job, 'prep', shots=len(shots), faces=nf, secs=round(time.time() - t0, 1))
    print('analysis: %d frames, face in %d (%.0f%%), %.1fs' % (n, nf, 100.0 * nf / n, time.time() - t1))
    if nf < 0.1 * n:
        print('WARNING: faces found in only %d/%d frames: face slots will use fallbacks (check the edit sheet)' % (nf, n))
    print('prep done in %.1fs' % (time.time() - t0))
    return 0


# ============================================================================ edit: plan, crops, tracks, sheets
def _mod(name):
    if SCRIPTS not in sys.path:
        sys.path.insert(0, SCRIPTS)
    return __import__(name)


def extract_crops(job, plan):
    """one JPEG sequence per slot: its window, cropped to the union of what its items show, at the resolution they need"""
    v0 = J(job, 'shots', CLIP + '.mp4')
    root = J(job, 'web', 'crops')
    os.makedirs(root, exist_ok=True)
    keep = set(plan['crops'])
    for d in os.listdir(root):
        if d not in keep:
            shutil.rmtree(J(root, d), ignore_errors=True)

    def one(sl):
        c = plan['crops'][sl]
        d = J(root, sl)
        meta = {'sf': c['sf'], 'n': c['n'], 'box': c['box'], 'ew': c['ew'], 'eh': c['eh'],
                'v0': os.path.getmtime(v0)}
        if jload(J(d, 'meta.json'), {}) == meta and count_files(d, '.jpg') == c['n']:
            return 0
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d)
        x, y, w, h = c['box']
        ff('-loglevel', 'error', '-y', '-ss', '%.4f' % ((c['sf'] - 0.25) / FPS), '-i', v0, '-frames:v', str(c['n']),
           '-vf', 'crop=%d:%d:%d:%d,scale=%d:%d:flags=lanczos' % (w, h, x, y, c['ew'], c['eh']), '-q:v', '2',
           '-start_number', '0', J(d, '%05d.jpg'))
        got = count_files(d, '.jpg')
        if got == 0:
            raise RuntimeError('no frames cut for slot %s' % sl)
        for k in range(got, c['n']):                       # the clip ended: hold the last frame
            shutil.copy(J(d, '%05d.jpg' % (got - 1)), J(d, '%05d.jpg' % k))
        jsave(J(d, 'meta.json'), meta)
        return 1
    with ThreadPoolExecutor(max_workers=min(8, os.cpu_count() or 4)) as ex:
        return sum(ex.map(one, sorted(plan['crops'])))


def gray_frames(path_pat, j0, count, tw):
    """decode crop JPEGs j0..j0+count-1 to raw gray at width tw -> (frames, w, h)"""
    probe = run([FFPROBE, '-v', 'error', '-show_entries', 'stream=width,height', '-of', 'json', path_pat % j0])
    s = json.loads(probe.stdout)['streams'][0]
    th = max(8, int(round(tw * s['height'] / float(s['width']) / 2)) * 2)
    raw = ff_bytes('-start_number', str(j0), '-i', path_pat, '-frames:v', str(count), '-vf',
                   'scale=%d:%d:flags=area,format=gray' % (tw, th), '-f', 'rawvideo', '-')
    n = len(raw) // (tw * th)
    return [raw[i * tw * th:(i + 1) * tw * th] for i in range(n)], tw, th


def compute_tracks(job, plan, feats):
    tr = _mod('track')
    E = _mod('edit')
    specs = {}
    for sg in plan['segs']:
        for t in sg['trk']:
            specs.setdefault(t['id'], t)
    out = {}
    for tid, t in specs.items():
        it = plan['items'][t['item']]
        cr = plan['crops'][it['slot']]
        ks = list(range(t['f0'] - it['f0'], t['f1'] - it['f0']))
        js = [min(cr['n'] - 1, it['k0'] + int(round(max(0, k) * it['speed']))) for k in ks]
        j0, j1 = min(js), max(js)
        pat = J(job, 'web', 'crops', it['slot'], '%05d.jpg')
        frames, tw, th = gray_frames(pat, j0, j1 - j0 + 1, tr.TW)
        bx, by, bw, bh = cr['box']
        sx, sy = bw / float(tw), bh / float(th)                     # gray px -> source px
        # shown region at the first tracked frame (source px) -> gray px, inner 70 %
        u = E.smooth(ks[0] / float(max(1, it['n'] - 1)))
        z = it['c0'][2] + (it['c1'][2] - it['c0'][2]) * u
        x, y, w, h = E.crop_rect(plan['src']['w'], plan['src']['h'], it['c0'][0], it['c0'][1], z, it['aspect'])
        reg = ((x + 0.15 * w - bx) / sx, (y + 0.15 * h - by) / sy, (x + 0.85 * w - bx) / sx, (y + 0.85 * h - by) / sy)
        g0 = frames[js[0] - j0]
        pts = []
        f = E.main_face(feats['frames'][min(feats['n'] - 1, cr['sf'] + js[0])])
        if f:
            fx, fy, fw, fh = f['bb']
            cands = []
            if f.get('eyes'):
                cands.append(f['eyes'][0])
            else:
                cands.append([fx + fw / 2, fy + fh * 0.4])
            cands.append(f.get('mouth') or [fx + fw / 2, fy + fh * 0.8])
            cands.append([fx + fw * 0.8, fy + fh * 1.7])
            for px, py in cands[:t['np']]:
                gx, gy = (px - bx) / sx, (py - by) / sy
                if reg[0] <= gx <= reg[2] and reg[1] <= gy <= reg[3]:
                    pts.append(tr.snap(g0, tw, th, int(gx), int(gy), 6))
        if len(pts) < t['np']:
            pts += tr.corners(g0, tw, th, reg, t['np'] - len(pts), 0.16 * tw, pts)
        if not pts:
            pts = [((reg[0] + reg[2]) / 2, (reg[1] + reg[3]) / 2)]
        uniq = sorted(set(js))
        seq = tr.track([frames[j - j0] for j in uniq], tw, th, pts)
        at = dict(zip(uniq, seq))
        out[tid] = {'f0': t['f0'], 'pts': [[[round(bx + px * sx, 1), round(by + py * sy, 1)] for px, py in at[j]] for j in js]}
    return out


def sheet_frames(plan, per=24):
    """one frame per segment (its 40 % point) plus every layer arrival, 24 per sheet"""
    fr = set()
    for s in plan['segs']:
        fr.add(s['f0'] + int((s['f1'] - s['f0']) * 0.4))
        for l in s['layers']:
            fr.add(min(s['f1'] - 1, l['from'] + 1))
    fr = sorted(fr)
    return [fr[i:i + per] for i in range(0, len(fr), per)]


def cmd_edit(a):
    job = job_path(a.job)
    if not os.path.exists(J(job, 'features.json')):
        die('run prep first')
    feats = jload(J(job, 'features.json'))
    if int(feats.get('n', -1)) != int(load_job(job)['frames']):
        die('features.json is from an older init; run prep first')
    try:
        fixes = jload(J(job, 'fixes.json'), {})
    except ValueError as e:
        die('fixes.json is not valid JSON (%s): double-quoted keys, no trailing commas, numbers unquoted' % e)
    t0 = time.time()
    try:
        plan, report = _mod('edit').build(template(), feats, fixes)
    except ValueError as e:
        die(str(e))
    n = extract_crops(job, plan)
    t1 = time.time()
    plan['tracks'] = compute_tracks(job, plan, feats)
    jsave(J(job, 'web', 'plan.json'), plan, indent=None)
    jsave(J(job, 'edit_report.json'), report)
    for line in report['summary']:
        print(line)
    print('crops: %d slots cut (%d cached), tracks: %d in %.1fs; edit %.1fs' % (
        n, len(plan['crops']) - n, len(plan['tracks']), time.time() - t1, time.time() - t0))
    mark_step(job, 'edit', warnings=len(report.get('warnings', [])))
    if a.no_sheet:
        return 0
    t0 = time.time()
    jobs = [('index.html?sheet=%s&cols=6&div=5&name=edit_%02d' % (','.join(map(str, fr)), k), 'edit_%02d' % k)
            for k, fr in enumerate(sheet_frames(plan))]
    with Server(job) as srv:
        got = capture_many(job, srv, jobs)
    for name, p in sorted(got.items()):
        shutil.copy(p, J(job, 'qa', name + '.jpg'))
        print('sheet %s' % J(job, 'qa', name + '.jpg'))
    print('sheets in %.1fs' % (time.time() - t0))
    return 0


# ============================================================================ render: frames, audio, encode
def render_frames(job, srv, nf, par, timeout):
    frames = J(job, 'web', 'frames')
    clear_dir(frames, '.jpg')
    tail = LogTail(J(job, 'web', 'log.txt'))
    step = int(math.ceil(nf / float(par)))
    tasks = []
    for i in range(par):
        f0, f1 = i * step, min(nf, (i + 1) * step)
        if f0 >= f1:
            continue
        tasks.append({'tag': 'r%d' % i, 'url': 'index.html?render=1&from=%d&to=%d' % (f0, f1), 'timeout': timeout, 'retries': 1,
                      'done': (lambda tl, f0=f0, f1=f1: tl.has(lambda l: l.startswith('render done %d-%d ' % (f0, f1)))),
                      'fail': (lambda tl: next((l for l in tl.lines if l.startswith('ERROR')), None))})
    t0 = time.time()
    res = run_pages(job, srv, tasks, par=par, tail=tail, label='render')
    errs = ['%s: %s' % (k, v) for k, v in res.items() if v != 'ok'] + web_errors(tail.lines)
    have = set(n for n in os.listdir(frames) if n.endswith('.jpg'))
    missing = [f for f in range(nf) if '%05d.jpg' % f not in have]
    if missing:
        errs.append('missing %d frames, e.g. %s' % (len(missing), missing[:5]))
    return errs, time.time() - t0


def media_duration(path):
    p = run([FFPROBE, '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path], check=False)
    try:
        return float(p.stdout.strip())
    except ValueError:
        return 0.0


def mean_db(path):
    err = ff('-i', path, '-af', 'volumedetect', '-f', 'null', '-', check=False).stderr
    m = re.search(r'mean_volume:\s*(-?[\d.]+) dB', err)
    return float(m.group(1)) if m else -91.0


def loudness(path):
    err = ff('-i', path, '-af', 'loudnorm=I=-14:TP=-1.0:print_format=json', '-f', 'null', '-', check=False).stderr
    try:
        js = json.loads(err[err.rindex('{'):err.rindex('}') + 1])
        return float(js['input_i']), float(js['input_tp'])
    except (ValueError, KeyError):
        return -14.0, -1.0


def sfx_track(job, plan, tl, out):
    """each visible item plays the clip's own sound from its matching source time (picture-locked), rings 70 ms past
    its cut, and is ducked 4 dB for every newer layer that starts on top of it"""
    a0 = J(job, 'shots', 'a0.wav')
    segs = tl.get('sfx') or []
    dur = plan['nf'] / float(FPS)
    parts, labels = [], []
    for i, (iid, fa, fb, g) in enumerate(segs):
        it = plan['items'][iid]
        cr = plan['crops'][it['slot']]
        src_f = cr['sf'] + it['k0'] + (fa - it['f0']) * it['speed']
        t0 = src_f / float(FPS)
        L = (fb - fa) / float(FPS)
        starts = sorted({s[1] for s in segs if s[0] != iid and fa < s[1] < fb})
        expr = '%.3f' % g + ''.join('*if(gte(t,%.4f),0.631,1)' % ((s - fa) / float(FPS)) for s in starts)
        parts.append("[0:a]atrim=start=%.4f:duration=%.4f,asetpts=PTS-STARTPTS,afade=t=in:d=0.006,"
                     "afade=t=out:st=%.4f:d=0.07,volume='%s':eval=frame,adelay=%d|%d[s%d]"
                     % (t0, L + 0.07, L, expr, int(round(fa * 1000.0 / FPS)), int(round(fa * 1000.0 / FPS)), i))
        labels.append('[s%d]' % i)
    # adelay pads without timestamps: re-stamp from the sample count before trimming, or atrim cuts the bus at ~0.2 s
    fc = ';'.join(parts) + ';%samix=inputs=%d:normalize=0:dropout_transition=0,asetpts=N/SR/TB,atrim=duration=%.4f[o]' % (
        ''.join(labels), len(labels), dur)
    ff('-loglevel', 'error', '-y', '-i', a0, '-filter_complex', fc, '-map', '[o]', '-ac', '2', '-ar', str(SR),
       '-c:a', 'pcm_f32le', out)


def mix_audio(job, plan, tl, want_sfx):
    """-> (audio file for the mux, description). Music alone is muxed as is; with SFX: music + SFX ~7 dB under it,
    mastered to about -14 LUFS / -1 dBTP with a latency-compensated limiter and a 0.3 s end fade."""
    music = J(TEMPLATE, tl.get('music', 'music.m4a'))
    a0 = J(job, 'shots', 'a0.wav')
    if not want_sfx or not os.path.exists(a0):
        return music, 'template music' + ('' if os.path.exists(a0) or not want_sfx else ' (the clip has no sound)')
    d = tmpdir(job)
    dur = plan['nf'] / float(FPS)
    sfx = J(d, 'sfx.wav')
    sfx_track(job, plan, tl, sfx)
    got = media_duration(sfx)
    if abs(got - dur) > 0.1:
        raise RuntimeError('clip sound bus is %.2f s, expected %.2f s (ffmpeg graph problem); render without --sfx' % (got, dur))
    m_db, s_db = mean_db(music), mean_db(sfx)
    if s_db < -80:
        return music, 'template music (the clip is silent)'
    gain = min(12.0, m_db - 7.0 - s_db)                    # quiet clips stay quiet (no +30 dB room tone)
    raw = J(d, 'mix_raw.wav')
    ff('-loglevel', 'error', '-y', '-i', music, '-i', sfx, '-filter_complex',
       '[1:a]volume=%.2fdB[s];[0:a][s]amix=inputs=2:normalize=0:dropout_transition=0,atrim=duration=%.4f,'
       'afade=t=out:st=%.4f:d=0.3[o]' % (gain, dur, dur - 0.3), '-map', '[o]', '-ar', str(SR), '-c:a', 'pcm_f32le', raw)
    i_in, _ = loudness(raw)
    g2 = max(-12.0, min(12.0, -14.0 - i_in))
    out = J(d, 'mix_master.wav')
    ff('-loglevel', 'error', '-y', '-i', raw, '-af', 'volume=%.2fdB,alimiter=limit=0.87:attack=2:release=60:level=false:'
       'latency=true' % g2, '-c:a', 'pcm_f32le', out)
    i_out, tp = loudness(out)
    return out, 'music + clip SFX (%+.1f dB), %.1f LUFS, %.1f dBTP' % (gain, i_out, tp)


def encode(job, plan, audio, out):
    dur = plan['nf'] / float(FPS)
    tmp = out[:-4] + '.part.mp4'
    acodec = ['-c:a', 'copy'] if audio.endswith('.m4a') else ['-c:a', 'aac', '-b:a', '256k', '-ar', str(SR)]
    ff('-loglevel', 'error', '-y', '-framerate', str(FPS), '-i', J(job, 'web', 'frames', '%05d.jpg'), '-i', audio,
       '-map', '0:v:0', '-map', '1:a:0', '-vf', 'scale=in_range=pc:out_range=tv,format=yuv420p', *venc_args('deliver', dur),
       '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv',
       *acodec, '-t', '%.4f' % dur, '-map_metadata', '-1', '-sn', '-dn', '-movflags', '+faststart', tmp)
    os.replace(tmp, out)


def cmd_render(a):
    job = job_path(a.job)
    st = load_job(job)
    if not os.path.exists(J(job, 'web', 'plan.json')):
        die('run edit first')
    plan = jload(J(job, 'web', 'plan.json'))
    tl = template()
    nf = plan['nf']
    out = J(job, 'out', '%s.mp4' % st['slug'])
    t0 = time.time()
    with Server(job) as srv:
        errs, dt = render_frames(job, srv, nf, a.par or PAR, a.timeout or 600)
    if errs:
        for e in errs:
            print('ERROR ' + e)
        die('render failed', 1)
    print('frames: %d in %.1fs' % (nf, dt))
    t1 = time.time()
    want = tl.get('sfx_default', True) if a.sfx is None else a.sfx
    audio, how = mix_audio(job, plan, tl, want)
    encode(job, plan, audio, out)
    print('audio: %s' % how)
    print('encoded %s (%.1f MB) in %.1fs, total %.1fs' % (out, os.path.getsize(out) / 1e6, time.time() - t1, time.time() - t0))
    mark_step(job, 'render', out=os.path.relpath(out, job), audio=how, secs=round(time.time() - t0, 1))
    if a.no_qa:
        return 0
    return cmd_qa(argparse.Namespace(job=a.job))


# ============================================================================ qa
def frame_lumas(path):
    p = subprocess.run([FFMPEG, '-nostdin', '-v', 'error', '-i', path, '-vf', 'scale=32:18,format=gray', '-f', 'rawvideo', '-'],
                       stdout=subprocess.PIPE, stdin=subprocess.DEVNULL)
    b, n = p.stdout, 32 * 18
    return [sum(b[i:i + n]) / (255.0 * n) for i in range(0, len(b) - n + 1, n)]


def compare_sheets(job, out, refs, per=12):
    """pairs reference|render at the template's QA frames, 2 pairs per row, `per` pairs per sheet (ffmpeg only)."""
    d = J(tmpdir(job), 'cmp')
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    sel = '+'.join('eq(n\\,%d)' % f for f in refs)
    ff('-loglevel', 'error', '-y', '-i', out, '-vf', "select='%s',scale=480:270" % sel, '-fps_mode', 'passthrough',
       '-start_number', '0', J(d, 'new_%03d.jpg'))
    sheets = []
    for k in range(0, len(refs), per):
        grp = list(range(k, min(len(refs), k + per)))
        inputs, fc = [], []
        for j, i in enumerate(grp):
            inputs += ['-i', J(TEMPLATE, 'ref', '%05d.jpg' % refs[i]), '-i', J(d, 'new_%03d.jpg' % i)]
            fc.append('[%d]scale=480:270[r%d];[%d]scale=480:270[n%d];[r%d][n%d]hstack[p%d]' % (2 * j, j, 2 * j + 1, j, j, j, j))
        cols = 2
        rows = int(math.ceil(len(grp) / float(cols)))
        while len(grp) < rows * cols:
            j = len(grp)
            fc.append('color=c=0x333333:s=960x270:d=1[p%d]' % j)
            grp.append(None)
        layout = '|'.join('%d_%d' % (c * 966, r * 276) for r in range(rows) for c in range(cols))
        fc.append('%sxstack=inputs=%d:layout=%s:fill=0x5a5a5a' % (''.join('[p%d]' % j for j in range(len(grp))), len(grp), layout))
        name = J(job, 'qa', 'cmp_%02d.jpg' % (k // per))
        ff('-loglevel', 'error', '-y', *inputs, '-filter_complex', ';'.join(fc), '-frames:v', '1', '-q:v', '3', name)
        sheets.append(name)
    return sheets


def cmd_qa(a):
    job = job_path(a.job)
    st = load_job(job)
    out = J(job, 'out', '%s.mp4' % st['slug'])
    plan = jload(J(job, 'web', 'plan.json'))
    tl = template()
    checks = []

    def add(name, ok, detail=''):
        checks.append({'check': name, 'status': 'pass' if ok else 'fail', 'detail': detail})
    p = run([FFPROBE, '-v', 'error', '-count_frames', '-show_entries',
             'stream=codec_type,width,height,nb_read_frames,duration:format=duration', '-of', 'json', out], check=False)
    info = json.loads(p.stdout or '{}') if p.returncode == 0 else {}
    streams = info.get('streams') or []
    v = next((s for s in streams if s.get('codec_type') == 'video'), {})
    au = next((s for s in streams if s.get('codec_type') == 'audio'), {})
    nf = plan['nf']
    add('video stream %dx%d' % (OUT_W, OUT_H), (v.get('width'), v.get('height')) == (OUT_W, OUT_H), '%sx%s' % (v.get('width'), v.get('height')))
    add('frames', str(v.get('nb_read_frames')) == str(nf), '%s / %d' % (v.get('nb_read_frames'), nf))
    add('audio stream', bool(au), au.get('duration', '-'))
    add('only video + audio streams', len(streams) == 2, '%d streams' % len(streams))
    dur = float((info.get('format') or {}).get('duration') or 0)
    add('duration', abs(dur - nf / float(FPS)) < 0.06, '%.3f s' % dur)
    size = os.path.getsize(out) / 1e6 if os.path.exists(out) else 0
    add('size <= 30 MB (chat upload)', 0 < size <= 30, '%.1f MB' % size)
    expect = set()                                          # solids, the silhouette, highlight-only and faded frames
    for s in plan['segs']:
        if s['base']['t'] in ('solid', 'sil'):
            expect.update(range(s['f0'], s['f1']))
        for f in s['fx']:
            if f['t'] == 'hlkeep':
                expect.update(int(k) for k in f['v'])
            if f['t'] == 'fade':
                expect.update(range(f['f0'] + f['len'] // 2, nf))
    stats = frame_lumas(out)
    blank = [i for i, y in enumerate(stats) if i not in expect and (y < 0.02 or y > 0.97)]
    add('no unexpected black/white frames', len(blank) <= 2, 'frames %s' % blank[:12])
    refs = [f for f in (tl.get('qa_frames') or []) if os.path.exists(J(TEMPLATE, 'ref', '%05d.jpg' % f))]
    sheets = compare_sheets(job, out, refs) if refs else []
    res = {'at': now_iso(), 'video': os.path.relpath(out, job), 'checks': checks, 'sheets': sheets}
    jsave(J(job, 'qa', 'qa.json'), res)
    bad = [c for c in checks if c['status'] != 'pass']
    for c in checks:
        print('%-4s %s  %s' % (c['status'], c['check'], c['detail']))
    for s in sheets:
        print('sheet ' + s)
    mark_step(job, 'qa', fails=len(bad))
    return 1 if bad else 0


# ============================================================================ sheet / serve / status
def cmd_sheet(a):
    job = job_path(a.job)
    fr = [int(v) for v in a.f.split(',') if v.strip()]
    name = a.name or 'sheet_%s' % time.strftime('%H%M%S')
    with Server(job) as srv:
        p = capture(job, srv, 'index.html?sheet=%s&cols=%d&div=%d&name=%s' % (','.join(map(str, fr)), a.cols or min(4, len(fr)), a.div, name), name)
    shutil.copy(p, J(job, 'qa', name + '.jpg'))
    print(J(job, 'qa', name + '.jpg'))
    return 0


def cmd_thumbs(a):
    """small copies of the review sheets (qa/edit_NN.jpg, qa/cmp_NN.jpg) for hosts that show at most ~512 KB of
    images per call: qa/small/<name>.jpg, each <= 125 KB"""
    job = job_path(a.job)
    qa = J(job, 'qa')
    out = J(qa, 'small')
    os.makedirs(out, exist_ok=True)
    names = sorted(n for n in os.listdir(qa) if re.match(r'^(edit|cmp)_\d+\.jpg$', n))
    for n in names:
        dst = J(out, n)
        for width, q in ((1400, 6), (1200, 8), (1000, 10), (800, 12)):
            ff('-loglevel', 'error', '-y', '-i', J(qa, n), '-vf', 'scale=%d:-2:flags=area' % width, '-q:v', str(q), dst)
            if os.path.getsize(dst) <= 125 * 1024:
                break
        print('%s %d KB' % (dst, os.path.getsize(dst) // 1024))
    return 0


def cmd_srcsheet(a):
    """contact sheets of the source for choosing pins: qa/small/src_KK.jpg, 8x6 tiles each; tile i of sheet KK shows
    source frame 15 * (48 * KK + i) (one tile every 0.5 s of the normalized 30 fps clip)"""
    job = job_path(a.job)
    st = load_job(job)
    out = J(job, 'qa', 'small')
    os.makedirs(out, exist_ok=True)
    for n in os.listdir(out):
        if n.startswith('src_'):
            os.remove(J(out, n))
    ff('-loglevel', 'error', '-y', '-framerate', str(FPS), '-start_number', '0', '-i', J(job, 'web', 'ana', CLIP, '%05d.jpg'),
       '-vf', "select='not(mod(n\\,15))',scale=200:112:force_original_aspect_ratio=decrease,"
              "pad=200:112:(ow-iw)/2:(oh-ih)/2,tile=8x6", '-fps_mode', 'vfr', '-q:v', '6', '-start_number', '0',
       J(out, 'src_%02d.jpg'))
    n = int(st['frames'])
    for k, name in enumerate(sorted(x for x in os.listdir(out) if x.startswith('src_'))):
        last = min(n - 1, 15 * (48 * k + 47))
        print('%s  tile i = source frame %d + 15*i  (frames %d-%d, %.1f-%.1f s), %d KB' % (
            J(out, name), 720 * k, 720 * k, last, 720 * k / 30.0, last / 30.0, os.path.getsize(J(out, name)) // 1024))
    return 0


def cmd_frames(a):
    """chosen source frames side by side for checking pin candidates: qa/small/frames.jpg, 4 columns, tiles in the
    order given (left to right, then top to bottom)"""
    job = job_path(a.job)
    n = int(load_job(job)['frames'])
    at = []
    for v in ','.join(a.at).replace(' ', ',').split(','):
        if v:
            if not v.isdigit() or int(v) >= n:
                die('frames: %r is not a source frame (0-%d)' % (v, n - 1))
            at.append(int(v))
    if not 1 <= len(at) <= 12:
        die('frames: give 1-12 source frame numbers')
    out = J(job, 'qa', 'small')
    os.makedirs(out, exist_ok=True)
    tmp = J(job, 'qa', 'frames_tmp')
    shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(tmp)
    for i, f in enumerate(at):
        shutil.copyfile(J(job, 'web', 'ana', CLIP, '%05d.jpg' % f), J(tmp, '%02d.jpg' % i))
    cols = min(4, len(at))
    rows = (len(at) + cols - 1) // cols
    dst = J(out, 'frames.jpg')
    for q in (4, 6, 9, 12):
        ff('-loglevel', 'error', '-y', '-framerate', '1', '-start_number', '0', '-i', J(tmp, '%02d.jpg'), '-vf',
           'scale=400:224:force_original_aspect_ratio=decrease:force_divisible_by=2,pad=400:224:(ow-iw)/2:(oh-ih)/2,tile=%dx%d:padding=4'
           % (cols, rows), '-frames:v', '1', '-q:v', str(q), dst)
        if os.path.getsize(dst) <= 125 * 1024:
            break
    shutil.rmtree(tmp, ignore_errors=True)
    print('%s  %d tiles, %d per row, left to right then top to bottom = source frames %s, %d KB' % (
        dst, len(at), cols, ' '.join(map(str, at)), os.path.getsize(dst) // 1024))
    return 0


def cmd_serve(a):
    job = job_path(a.job)
    with Server(job) as srv:
        print('serving %s at %sindex.html  (Ctrl-C to stop)' % (J(job, 'web'), srv.base))
        try:
            while srv.proc.poll() is None:
                time.sleep(0.5)
        except KeyboardInterrupt:
            pass
    return 0


def cmd_status(a):
    job = job_path(a.job)
    st = load_job(job)
    print('slug %s  source %s  %sx%s  %s frames  audio %s' % (st['slug'], st['video_src'], st['size'][0], st['size'][1],
                                                              st['frames'], st.get('audio')))
    for k, v in (st.get('steps') or {}).items():
        print('step %-7s %s' % (k, json.dumps(v, ensure_ascii=False)))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('assets')
    s.add_argument('--force', action='store_true', help='re-download and rewrite every asset')
    s = sub.add_parser('doctor')
    s.add_argument('job', nargs='?')
    s = sub.add_parser('init')
    s.add_argument('job')
    s.add_argument('--video', required=True)
    s.add_argument('--slug')
    s.add_argument('--start', type=float, default=0.0)
    s.add_argument('--max-dur', type=float)
    s.add_argument('--force', action='store_true')
    s = sub.add_parser('prep')
    s.add_argument('job')
    s = sub.add_parser('edit')
    s.add_argument('job')
    s.add_argument('--no-sheet', action='store_true')
    s = sub.add_parser('render')
    s.add_argument('job')
    s.add_argument('--par', type=int)
    s.add_argument('--timeout', type=int)
    s.add_argument('--no-qa', action='store_true')
    g = s.add_mutually_exclusive_group()
    g.add_argument('--sfx', dest='sfx', action='store_true', default=None, help="mix the clip's own sound under the music")
    g.add_argument('--no-sfx', dest='sfx', action='store_false', help='template music only')
    s = sub.add_parser('qa')
    s.add_argument('job')
    s = sub.add_parser('sheet')
    s.add_argument('job')
    s.add_argument('--f', required=True)
    s.add_argument('--name')
    s.add_argument('--cols', type=int)
    s.add_argument('--div', type=int, default=3)
    s = sub.add_parser('thumbs')
    s.add_argument('job')
    s = sub.add_parser('srcsheet')
    s.add_argument('job')
    s = sub.add_parser('frames')
    s.add_argument('job')
    s.add_argument('at', nargs='+', help='source frame numbers (spaces or commas), 1-12')
    s = sub.add_parser('serve')
    s.add_argument('job')
    s = sub.add_parser('status')
    s.add_argument('job')
    a = ap.parse_args()
    return {'assets': cmd_assets, 'doctor': cmd_doctor, 'init': cmd_init, 'prep': cmd_prep, 'edit': cmd_edit, 'render': cmd_render,
            'qa': cmd_qa, 'sheet': cmd_sheet, 'thumbs': cmd_thumbs, 'srcsheet': cmd_srcsheet, 'frames': cmd_frames, 'serve': cmd_serve, 'status': cmd_status}[a.cmd](a)


if __name__ == '__main__':
    sys.exit(main() or 0)
