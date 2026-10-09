#!/usr/bin/env python3
"""ml.py - CLI of the many-lies-edit skill (python3 stdlib only; ffmpeg + headless Chrome do the pixel work).

usage: python3 -I ml.py <command> <job_dir> [options]

  assets                           install the engine pages (engine/*.html.txt -> .html) and download + verify the
                                   binary assets pinned by assets.json (template music, QA reference frames)
  doctor [job]                     environment check (ffmpeg encoders/filters, Chrome, engine, assets, smoke render)
  run <job> --video V|URL [--slug S] [--start s] [--max-dur s] [--glow|--no-glow] [--fixes JSON|@file]
          [--upload-url URL] [--force] [--fresh] [--reset-fixes]
                                   the whole pipeline in one call (init, prep, edit, render, qa, review images, upload);
                                   writes <job>/status.json. A rerun of the same video reuses init+prep, holds every
                                   earlier pick and adds --fixes to the earlier fixes (cumulative); exit 4 = already running
  upload <job> --upload-url URL    PUT out/<slug>.mp4 to a presigned URL (after review)
  picks <job>                      people, every slot's source window / camera / hero share, warnings, source cuts
  init <job> --video V [--slug S] [--start s] [--max-dur s]
                                   normalize the clip: 24 fps CFR, working size (covers 1440x1080, source aspect kept),
                                   <= 60 s, no audio -> shots/v0.mp4, web/src/v0/*.jpg (full), web/ana/v0/*.jpg (480 px)
  prep <job>                       hard cuts (scdet) + per-frame analysis in Chrome (faces/eyes, motion, luma, sharpness,
                                   warm pixels) -> features.json
  edit <job> [--glow] [--no-sheet] template slots -> moments of the clip -> web/plan.json, edit_report.json,
                                   review sheet qa/edit_NN.jpg; <job>/fixes.json pins slots (reference/fixes.md)
  render <job> [--no-qa]           frames in parallel Chrome -> encode with the template music -> out/<slug>.mp4, then qa
  qa <job>                         checks + comparison sheets (template reference | this render) -> qa/qa.json, qa/cmp_NN.jpg
  sheet <job> --f a,b,c [--name N] labelled stills of the plan at output frames a,b,c -> qa/<N>.jpg
  srcsheet <job> [--step N]        contact sheets of the SOURCE clip labelled with source frame numbers (every N
                                   frames, default 6 / 12) -> review/src_NN.jpg, for pinning slots in fixes
  serve <job>                      debug server (index.html: arrows step frames, shift = one beat)
  status <job>                     job summary

Exit codes: 0 ok, 1 problems (prep/render/qa), 2 usage or input error.
Env: ML_CHROME (Chrome binary), ML_PAR (parallel Chrome instances, default 8).
"""
import argparse
import atexit
import fcntl
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

sys.dont_write_bytecode = True
SCRIPTS = os.path.dirname(os.path.abspath(__file__))
SK = os.path.dirname(SCRIPTS)
ENGINE = os.path.join(SK, 'engine')
TEMPLATE = os.path.join(SK, 'template')
ASSETS_JSON = os.path.join(SK, 'assets.json')       # binary assets (CDN archive); see cmd_assets
ASSET_DIRS = ('template/',)                          # the only place assets.json may write to
ENGINE_PAGES = ('index.html', 'ana.html')           # bundled as engine/<page>.txt
YUNET = os.path.join(SK, 'template', 'yunet.onnx')  # face detector for scripts/ana.py (OpenCV Zoo YuNet, MIT)
SFACE = os.path.join(SK, 'template', 'sface.onnx')  # face identity embeddings (OpenCV Zoo SFace, Apache 2.0)
def _find_chrome():
    """ML_CHROME, else Google Chrome on macOS, else a Playwright / system Chromium (Linux hosts, e.g. the sandbox)."""
    if os.environ.get('ML_CHROME'):
        return os.environ['ML_CHROME']
    cands = ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome']
    for base in ('/ms-playwright', os.path.expanduser('~/.cache/ms-playwright')):
        try:
            for d in sorted(os.listdir(base), reverse=True):
                if d.startswith('chromium-'):
                    cands += [os.path.join(base, d, 'chrome-linux64', 'chrome'), os.path.join(base, d, 'chrome-linux', 'chrome')]
        except OSError:
            pass
    cands += [shutil.which(n) or '' for n in ('google-chrome', 'chromium', 'chromium-browser')]
    return next((c for c in cands if c and os.path.isfile(c) and os.access(c, os.X_OK)), cands[0])


CHROME = _find_chrome()
FFMPEG = shutil.which('ffmpeg') or 'ffmpeg'
FFPROBE = shutil.which('ffprobe') or 'ffprobe'
PAR = max(1, int(os.environ.get('ML_PAR', '8') or 8))
FPS, OUT_W, OUT_H = 24, 1440, 1080
CLIP = 'v0'
MAX_DUR, MIN_DUR = 60.0, 4.0
DELIVER_MB = 24.0                                    # final file target (chat upload limit is 30 MB)
ANA_W = 480
SCD_T, SCD_PEAK, SCD_MIN_GAP = 6.0, 3.0, 8           # scdet hard-cut score, x over neighbours, min frames apart
CHROME_FLAGS = ['--window-size=1440,1080', '--no-first-run', '--no-default-browser-check',
                '--disable-background-timer-throttling', '--disable-renderer-backgrounding',
                '--disable-backgrounding-occluded-windows']
if sys.platform == 'darwin':
    CHROME_FLAGS += ['--enable-gpu', '--use-angle=metal']
else:                                               # Linux containers (Higgsfield sandbox): no setuid sandbox, small /dev/shm
    CHROME_FLAGS += ['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
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
        die('no job.json in %s (run: ml.py init <job> --video V)' % job)
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
    """display size (rotation applied), fps, duration, frame count of the first video stream."""
    p = run([FFPROBE, '-v', 'error', '-select_streams', 'v:0', '-show_entries',
             'stream=width,height,r_frame_rate,avg_frame_rate,nb_frames,codec_name:stream_tags=rotate:'
             'stream_side_data=rotation:format=duration', '-of', 'json', path], check=False)
    if p.returncode != 0:
        return None
    try:
        d = json.loads(p.stdout)
        s = d['streams'][0]
    except (ValueError, KeyError, IndexError):
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
            'codec': s.get('codec_name'), 'dur': float((d.get('format') or {}).get('duration') or 0)}


def venc_args(quality='master', dur=None):
    """master: near-lossless working copy. deliver: sized for the chat upload limit (DELIVER_MB incl. 256k audio)."""
    enc = ff('-encoders').stdout
    mb = None
    if quality == 'deliver':
        mb = max(4.0, min(24.0, DELIVER_MB * 8.0 / max(1.0, dur or 15.0) - 0.3))
    if re.search(r'\slibx264\s', enc):
        if mb:
            return ['-c:v', 'libx264', '-preset', 'medium', '-b:v', '%.1fM' % mb, '-maxrate', '%.1fM' % (mb * 1.3),
                    '-bufsize', '%.1fM' % (mb * 2), '-tune', 'grain', '-profile:v', 'high']
        return ['-c:v', 'libx264', '-preset', 'veryfast', '-crf', '15']
    if 'h264_videotoolbox' in enc:
        return ['-c:v', 'h264_videotoolbox', '-b:v', '%.1fM' % mb if mb else '30M', '-profile:v', 'high']
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
            raise RuntimeError('Google Chrome not found at %s (set ML_CHROME)' % CHROME)
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


def capture(job, srv, query, name, timeout=120):
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
            r = subprocess.run(['curl', '-fsSL', '--connect-timeout', '20', '--max-time', '600', '-A', 'ml.py/1',
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
    tmp = tempfile.mkdtemp(prefix='ml_assets_')
    try:
        tgz = J(tmp, 'assets.tar.gz')
        n = _download(arc['url'], tgz)
        if n != arc['bytes']:
            raise RuntimeError('archive is %d bytes, assets.json says %d (re-run ml.py assets; if it persists the '
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
    for f in ('scdet', 'metadata', 'scale', 'fps', 'ebur128'):
        rep(bool(re.search(r'\s%s\s' % f, fil)), 'filter ' + f)
    rep(os.path.exists(CHROME), 'Chrome', CHROME)
    meth = ana_method()
    ready, why = ana_python_ready()
    rep(True if meth == 'chrome' or ready else False, 'frame analysis: %s' % meth,
        why if meth == 'python' else 'Chrome FaceDetector (macOS); python path: %s' % why)
    for f in ('index.html', 'fx.js') + (('ana.html',) if meth == 'chrome' else ()):
        rep(os.path.exists(J(ENGINE, f)), 'engine/' + f,
            '' if os.path.exists(J(ENGINE, f)) or not os.path.exists(J(ENGINE, f + '.txt')) else 'run: ml.py assets')
    rep(os.path.exists(J(TEMPLATE, 'timeline.json')), 'template/timeline.json')
    arc, files, err = read_assets_manifest()
    if err:
        rep(False, 'assets.json', err)
    else:
        probs = asset_problems(files)
        if probs:
            rep(False, 'binary assets missing or invalid', '%d of %d: %s; run: ml.py assets' % (
                len(probs), len(files), ', '.join('%s (%s)' % x for x in probs[:3]) + (' ...' if len(probs) > 3 else '')))
        else:
            rep(True, 'binary assets', '%d files verified (sha256)' % len(files))
    rep(os.path.exists(J(SCRIPTS, 'serve.py')), 'scripts/serve.py')
    rep(os.path.exists(J(SCRIPTS, 'edit.py')), 'scripts/edit.py')
    rep(os.path.exists(J(SCRIPTS, 'ana.py')), 'scripts/ana.py')
    if ok and os.path.exists(CHROME):                       # smoke: serve.py + Chrome + engine render of a solid plan
        tmpjob = tempfile.mkdtemp(prefix='ml_doctor_')
        try:
            jsave(J(tmpjob, 'web', 'plan.json'), {'fps': 24, 'w': 320, 'h': 240, 'src': {},
                                                  'shots': [{'id': 's', 'f0': 0, 'f1': 2, 'solid': 0.5}],
                                                  'ev': [{'type': 'word', 'f0': 0, 'f1': 2, 'text': 'OK', 'size': 80}]})
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
    """source working size: covers OUT_W x OUT_H at zoom 1 with the source aspect kept (16:9 -> 1920x1080)."""
    s = max(OUT_W / float(w), OUT_H / float(h))
    if w / float(h) >= OUT_W / float(OUT_H):           # landscape: height = 1080 (more never helps: crops zoom in)
        s = OUT_H / float(h)
    W, H = int(round(w * s / 2)) * 2, int(round(h * s / 2)) * 2
    return max(W, OUT_W), max(H, OUT_H)


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
    W, H = work_size(g['w'], g['h'])
    for d in ('shots', 'web', 'out', 'qa'):
        os.makedirs(J(job, d), exist_ok=True)
    t0 = time.time()
    v0 = J(job, 'shots', CLIP + '.mp4')
    tmp = v0[:-4] + '.part.mp4'
    vf = 'fps=%d,scale=%d:%d:flags=lanczos,setsar=1,format=yuv420p' % (FPS, W, H)
    args = ['-loglevel', 'error', '-y'] + (['-ss', '%.3f' % start] if start else []) + \
           ['-i', src, '-t', '%.3f' % maxdur, '-map', '0:v:0', '-an', '-sn', '-dn', '-vf', vf, '-r', str(FPS),
            *venc_args(), '-pix_fmt', 'yuv420p', '-color_range', 'tv', '-movflags', '+faststart', tmp]
    ff(*args)
    os.replace(tmp, v0)
    sd, ad = J(job, 'web', 'src', CLIP), J(job, 'web', 'ana', CLIP)
    clear_dir(sd, '.jpg')
    clear_dir(ad, '.jpg')
    ff('-loglevel', 'error', '-y', '-i', v0, '-filter_complex', '[0]split=2[a][b];[b]scale=%d:-2:flags=area[s]' % ANA_W,
       '-map', '[a]', '-q:v', '2', '-start_number', '0', J(sd, '%05d.jpg'),
       '-map', '[s]', '-q:v', '4', '-start_number', '0', J(ad, '%05d.jpg'))
    n = count_files(sd, '.jpg')
    if n != count_files(ad, '.jpg') or n < MIN_DUR * FPS * 0.9:
        die('frame extraction failed (%d full / %d analysis frames)' % (n, count_files(ad, '.jpg')), 1)
    st = {'slug': slug, 'video_src': src, 'start': start, 'src_geometry': g, 'size': [W, H], 'frames': n,
          'created': now_iso(), 'steps': {}}
    save_job(job, st)
    print('init %s: %dx%d %.2f fps %.1f s -> %dx%d, %d frames (%.1f s) in %.1fs' %
          (os.path.basename(src), g['w'], g['h'], g['fps'], g['dur'], W, H, n, n / float(FPS), time.time() - t0))
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
    method = ana_method()
    t1 = time.time()
    if method == 'python':
        ranges = ana_python(job, n)
    else:
        ranges = ana_chrome(job, n)
    frames, aw = [], None
    for a0, b0 in ranges:
        d = jload(J(web, 'track', '%s_%d_%d.json' % (CLIP, a0, b0)))
        aw = aw or d['w']
        frames.extend(d['frames'])
    finish_prep(job, st, n, W, H, t0, t1, cuts, shots, frames, aw, method)
    return 0


def ana_method():
    """'python' (numpy + Pillow + onnxruntime + YuNet; any OS) when available, else 'chrome' (FaceDetector, macOS).
    ML_ANA=python|chrome forces one."""
    forced = os.environ.get('ML_ANA', '').strip().lower()
    if forced in ('python', 'chrome'):
        return forced
    return 'python' if ana_python_ready()[0] else 'chrome'


def ana_python_ready():
    if not os.path.isfile(YUNET):
        return False, 'missing %s (run: ml.py assets)' % os.path.relpath(YUNET, SK)
    p = run([sys.executable, '-I', '-c', 'import numpy, PIL, onnxruntime'], check=False)
    if p.returncode != 0:
        return False, 'python packages numpy, Pillow, onnxruntime not importable'
    return True, 'numpy + Pillow + onnxruntime + YuNet' + (' + SFace identities' if os.path.isfile(SFACE) else ' (no SFace: people by colour only)')


def ana_python(job, n):
    """scripts/ana.py over frame ranges in parallel processes (1 onnx thread each)."""
    web = J(job, 'web')
    k = max(1, min(PAR, os.cpu_count() or 1, n // 24 or 1))
    step = int(math.ceil(n / float(k)))
    ranges = [(a0, min(n, a0 + step)) for a0 in range(0, n, step)]
    procs = []
    for a0, b0 in ranges:
        log = open(J(tmpdir(job), 'ana_%d.log' % a0), 'wb')
        procs.append((a0, b0, subprocess.Popen([sys.executable, '-I', J(SCRIPTS, 'ana.py'), J(web, 'ana', CLIP), str(a0), str(b0),
                                                YUNET, J(web, 'track', '%s_%d_%d.json' % (CLIP, a0, b0)), '1',
                                                J(web, 'src', CLIP), SFACE],
                                               stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL), log))
    bad = []
    for a0, b0, p, log in procs:
        if p.wait() != 0:
            bad.append('%d-%d (see tmp/ana_%d.log)' % (a0, b0, a0))
        log.close()
    if bad:
        die('analysis failed: %s' % ', '.join(bad), 1)
    return ranges


def ana_chrome(job, n):
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
    return [tuple(int(v) for v in re.findall(r'a=(\d+)&b=(\d+)', t['url'])[0]) for t in tasks]


def finish_prep(job, st, n, W, H, t0, t1, cuts, shots, frames, aw, method):
    if len(frames) != n:
        die('analysis has %d frames, expected %d' % (len(frames), n), 1)
    sc = W / float(aw)                                     # analysis px -> working source px
    nf = 0
    for i, fr in enumerate(frames):
        if fr is None:
            frames[i] = {'f': [], 'y': 0, 'p5': 0, 'p95': 0, 'sh': 0, 'm': 0, 'wm': 0, 'we': 0, 'bad': True}
            continue
        for f in fr['f']:
            f['bb'] = [round(v * sc, 1) for v in f['bb']]
            if f.get('eyes'):
                f['eyes'] = [[round(e[0] * sc, 1), round(e[1] * sc, 1)] for e in f['eyes']]
            if f.get('mouth'):
                f['mouth'] = [round(v * sc, 1) for v in f['mouth']]
        nf += bool(fr['f'])
    for s in shots:                                        # motion at a shot's first frame is the cut itself
        if 0 < s['a'] < n - 1:
            frames[s['a']]['m'] = frames[s['a'] + 1]['m']
    if n > 1:
        frames[0]['m'] = frames[1]['m']
    feats = {'version': 1, 'clip': CLIP, 'size': [W, H], 'fps': FPS, 'n': n, 'shots': shots,
             'cuts': [[f, round(s, 2)] for f, s in cuts], 'faces': nf, 'frames': frames}
    jsave(J(job, 'features.json'), feats, indent=None)
    mark_step(job, 'prep', shots=len(shots), faces=nf, method=method, secs=round(time.time() - t0, 1))
    print('analysis (%s): %d frames, face in %d (%.0f%%), %.1fs' % (method, n, nf, 100.0 * nf / n, time.time() - t1))
    if nf < 0.1 * n:
        print('WARNING: faces found in only %d/%d frames: face slots will use fallbacks (check the edit sheet)' % (nf, n))
    print('prep done in %.1fs' % (time.time() - t0))
    return 0


# ============================================================================ edit
def _edit():
    if SCRIPTS not in sys.path:
        sys.path.insert(0, SCRIPTS)
    import edit
    return edit


def sheet_frames(plan, per=24):
    """one frame per shot (its 40 % point), 24 per sheet"""
    fr = [s['f0'] + int((s['f1'] - s['f0']) * 0.4) for s in plan['shots']]
    return [fr[i:i + per] for i in range(0, len(fr), per)]


def cmd_edit(a):
    job = job_path(a.job)
    st = load_job(job)
    if not os.path.exists(J(job, 'features.json')):
        die('run prep first')
    feats = jload(J(job, 'features.json'))
    fixes = jload(J(job, 'fixes.json'), {})
    plan, report = _edit().build(template(), feats, fixes, glow=a.glow)
    jsave(J(job, 'web', 'plan.json'), plan, indent=None)
    jsave(J(job, 'edit_report.json'), report)
    for line in report['summary']:
        print(line)
    mark_step(job, 'edit', glow=bool(a.glow), warnings=len(report.get('warnings', [])))
    if a.no_sheet:
        return 0
    t0 = time.time()
    with Server(job) as srv:
        for k, fr in enumerate(sheet_frames(plan)):
            p = capture(job, srv, 'index.html?sheet=%s&cols=6&div=4&name=edit_%02d' % (','.join(map(str, fr)), k), 'edit_%02d' % k)
            shutil.copy(p, J(job, 'qa', 'edit_%02d.jpg' % k))
            print('sheet %s' % J(job, 'qa', 'edit_%02d.jpg' % k))
    print('sheets in %.1fs' % (time.time() - t0))
    return 0


# ============================================================================ render
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


def encode(job, plan, out):
    tl = template()
    music = J(TEMPLATE, tl.get('music', 'music.m4a'))
    dur = plan['nf'] / float(FPS)
    tmp = out[:-4] + '.part.mp4'
    ff('-loglevel', 'error', '-y', '-framerate', str(FPS), '-i', J(job, 'web', 'frames', '%05d.jpg'), '-i', music,
       '-map', '0:v:0', '-map', '1:a:0', '-vf', 'scale=in_range=pc:out_range=tv,format=yuv420p', *venc_args('deliver', dur),
       '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv',
       '-c:a', 'aac', '-b:a', '256k', '-ar', '48000', '-t', '%.4f' % dur, '-map_metadata', '-1', '-sn', '-dn',
       '-movflags', '+faststart', tmp)
    os.replace(tmp, out)


def cmd_render(a):
    job = job_path(a.job)
    st = load_job(job)
    if not os.path.exists(J(job, 'web', 'plan.json')):
        die('run edit first')
    plan = jload(J(job, 'web', 'plan.json'))
    nf = sum(s['f1'] - s['f0'] for s in plan['shots'])
    out = J(job, 'out', '%s.mp4' % st['slug'])
    t0 = time.time()
    with Server(job) as srv:
        errs, dt = render_frames(job, srv, nf, a.par or PAR, a.timeout or 300)
    if errs:
        for e in errs:
            print('ERROR ' + e)
        die('render failed', 1)
    print('frames: %d in %.1fs' % (nf, dt))
    t1 = time.time()
    plan['nf'] = nf
    encode(job, plan, out)
    print('encoded %s (%.1f MB) in %.1fs, total %.1fs' % (out, os.path.getsize(out) / 1e6, time.time() - t1, time.time() - t0))
    mark_step(job, 'render', out=os.path.relpath(out, job), secs=round(time.time() - t0, 1))
    if a.no_qa:
        return 0
    return cmd_qa(argparse.Namespace(job=a.job))


# ============================================================================ qa
def cmd_qa(a):
    job = job_path(a.job)
    st = load_job(job)
    out = J(job, 'out', '%s.mp4' % st['slug'])
    plan = jload(J(job, 'web', 'plan.json'))
    tl = template()
    checks = []

    def add(name, ok, detail=''):
        checks.append({'check': name, 'status': 'pass' if ok else 'fail', 'detail': detail})
    p = run([FFPROBE, '-v', 'error', '-show_entries', 'stream=codec_type,width,height,nb_frames,duration:format=duration',
             '-of', 'json', out], check=False)
    info = json.loads(p.stdout or '{}') if p.returncode == 0 else {}
    streams = info.get('streams') or []
    v = next((s for s in streams if s.get('codec_type') == 'video'), {})
    au = next((s for s in streams if s.get('codec_type') == 'audio'), {})
    nf = sum(s['f1'] - s['f0'] for s in plan['shots'])
    add('video stream %dx%d' % (OUT_W, OUT_H), (v.get('width'), v.get('height')) == (OUT_W, OUT_H), '%sx%s' % (v.get('width'), v.get('height')))
    add('frames', str(v.get('nb_frames')) == str(nf), '%s / %d' % (v.get('nb_frames'), nf))
    add('audio stream', bool(au), au.get('duration', '-'))
    add('only video + audio streams', len(streams) == 2, '%d streams' % len(streams))
    dur = float((info.get('format') or {}).get('duration') or 0)
    add('duration', abs(dur - nf / float(FPS)) < 0.06, '%.3f s' % dur)
    size = os.path.getsize(out) / 1e6 if os.path.exists(out) else 0
    add('size <= 30 MB (chat upload)', 0 < size <= 30, '%.1f MB' % size)
    # black / blown frames outside the template's own solids
    solid = set()
    for s in plan['shots']:
        if 'solid' in s:
            solid.update(range(s['f0'], s['f1']))
    stats = frame_lumas(out)
    blank = [i for i, y in enumerate(stats) if i not in solid and (y < 0.02 or y > 0.97)]
    add('no unexpected black/white frames', len(blank) <= 2, ('frames %s' % blank[:12]) if len(blank) > 2 else '')
    # comparison sheets: template reference frame | this render
    refs = tl.get('qa_frames') or []
    sheets = []
    if refs:
        sheets = compare_sheets(job, out, refs)
    res = {'at': now_iso(), 'video': os.path.relpath(out, job), 'checks': checks, 'sheets': sheets}
    jsave(J(job, 'qa', 'qa.json'), res)
    bad = [c for c in checks if c['status'] != 'pass']
    for c in checks:
        print('%-4s %s  %s' % (c['status'], c['check'], c['detail']))
    for s in sheets:
        print('sheet ' + s)
    mark_step(job, 'qa', fails=len(bad))
    return 1 if bad else 0


def frame_lumas(path):
    p = subprocess.run([FFMPEG, '-nostdin', '-v', 'error', '-i', path, '-vf', 'scale=32:24,format=gray', '-f', 'rawvideo', '-'],
                       stdout=subprocess.PIPE, stdin=subprocess.DEVNULL)
    b, n = p.stdout, 32 * 24
    return [sum(b[i:i + n]) / (255.0 * n) for i in range(0, len(b) - n + 1, n)]


def compare_sheets(job, out, refs, per=12):
    """pairs reference|render at the template's QA frames, 2 pairs per row, `per` pairs per sheet (ffmpeg only)."""
    d = J(tmpdir(job), 'cmp')
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    sel = '+'.join('eq(n\\,%d)' % f for f in refs)
    ff('-loglevel', 'error', '-y', '-i', out, '-vf', "select='%s',scale=480:360" % sel, '-fps_mode', 'passthrough',
       '-start_number', '0', J(d, 'new_%03d.jpg'))
    sheets = []
    for k in range(0, len(refs), per):
        grp = list(range(k, min(len(refs), k + per)))
        inputs, fc = [], []
        for j, i in enumerate(grp):
            inputs += ['-i', J(TEMPLATE, 'ref', '%05d.jpg' % refs[i]), '-i', J(d, 'new_%03d.jpg' % i)]
            fc.append('[%d]scale=480:360[r%d];[%d]scale=480:360[n%d];[r%d][n%d]hstack[p%d]' % (2 * j, j, 2 * j + 1, j, j, j, j))
        cols = 2
        rows = int(math.ceil(len(grp) / float(cols)))
        while len(grp) < rows * cols:                      # pad the grid with black pairs
            j = len(grp)
            fc.append('color=c=0x333333:s=960x360:d=1[p%d]' % j)
            grp.append(None)
        layout = '|'.join('%d_%d' % (c * 966, r * 366) for r in range(rows) for c in range(cols))
        fc.append('%sxstack=inputs=%d:layout=%s:fill=0x5a5a5a' % (''.join('[p%d]' % j for j in range(len(grp))), len(grp), layout))
        name = J(job, 'qa', 'cmp_%02d.jpg' % (k // per))
        ff('-loglevel', 'error', '-y', *inputs, '-filter_complex', ';'.join(fc), '-frames:v', '1', '-q:v', '3', name)
        sheets.append(name)
    return sheets


# ============================================================================ run (one call, for hosted agents)
def _status(job, **kw):
    p = J(job, 'status.json')
    st = jload(p, {}) if os.path.exists(p) else {}
    st.update(kw)
    st['updated'] = now_iso()
    jsave(p, st)
    return st


def _stage(job, name, fn, timings):
    """run one stage; record timing; turn die()/exceptions into a failed status (returns False)."""
    _status(job, stage=name, state='running')
    t0 = time.time()
    print('== %s' % name, flush=True)
    try:
        rc = fn()
    except SystemExit as e:
        rc = e.code if isinstance(e.code, int) else 1
    except Exception as e:                                  # report, do not hide
        print('ERROR %s: %s' % (name, e), flush=True)
        rc = 1
    timings[name] = round(time.time() - t0, 1)
    _status(job, timings=timings)
    if rc not in (0, None):
        _status(job, stage=name, state='failed', timings=timings,
                error='%s failed (exit %s); see the log above this line' % (name, rc))
        return False
    return True


def review_images(job):
    """small JPEGs for an agent's image viewer (<= ~120 KB each): review/edit_1..2.jpg (one still per shot),
    review/cmp_1..2.jpg (template reference | this render)."""
    d = J(job, 'review')
    os.makedirs(d, exist_ok=True)
    for n in os.listdir(d):
        os.remove(J(d, n))
    out = []
    groups = [('edit', sorted(n for n in os.listdir(J(job, 'qa')) if re.match(r'edit_\d+\.jpg$', n))),
              ('cmp', sorted(n for n in os.listdir(J(job, 'qa')) if re.match(r'cmp_\d+\.jpg$', n)))]
    for kind, names in groups:
        if kind == 'cmp':                                    # 7 sheets -> 4 images of 2 (readable at viewer scale)
            names = [names[i:i + 2] for i in range(0, len(names), 2)]
        else:
            names = [[n] for n in names]
        for k, grp in enumerate(names):
            dst = J(d, '%s_%d.jpg' % (kind, k + 1))
            ins = []
            for n in grp:
                ins += ['-i', J(job, 'qa', n)]
            width = 1000 if kind == 'edit' else 860
            fc = ''.join('[%d]scale=%d:-2[s%d];' % (i, width, i) for i in range(len(grp)))
            fc += ''.join('[s%d]' % i for i in range(len(grp))) + ('vstack=inputs=%d[v]' % len(grp) if len(grp) > 1 else 'null[v]')
            for q in (5, 8, 12, 17, 23, 31):
                ff('-loglevel', 'error', '-y', *ins, '-filter_complex', fc, '-map', '[v]', '-frames:v', '1', '-q:v', str(q), dst)
                if os.path.getsize(dst) <= 120 * 1024:
                    break
            out.append(os.path.relpath(dst, job))
    return out


def _fetch_video(src, job):
    if re.match(r'^https://', src or ''):
        os.makedirs(tmpdir(job), exist_ok=True)
        ext = os.path.splitext(urllib.parse.urlparse(src).path)[1].lower()
        dst = J(tmpdir(job), 'input' + (ext if re.match(r'^\.[a-z0-9]{2,4}$', ext) else '.mp4'))
        p = run(['curl', '-fsSL', '--retry', '3', '--connect-timeout', '20', '--max-time', '600', '-o', dst, src], check=False)
        if p.returncode != 0 or not os.path.isfile(dst) or os.path.getsize(dst) == 0:
            die('cannot download the clip: %s' % (p.stderr.strip()[:200] or 'empty file'))
        return dst
    path = os.path.abspath(os.path.expanduser(src))
    if not os.path.isfile(path):
        die('video not found: %s' % src)
    return path


def _merge_fixes(prev, new):
    """cumulative user fixes: slots / shots merge per key, avoid / hero replace, repick is one-shot (not stored)."""
    out = {'slots': dict(prev.get('slots') or {}), 'shots': {k: dict(v) for k, v in (prev.get('shots') or {}).items()}}
    for k in ('avoid', 'hero'):
        if prev.get(k):
            out[k] = prev[k]
    for k, v in (new.get('slots') or {}).items():
        out['slots'][k] = dict(v) if isinstance(v, dict) else v
    for k, v in (new.get('shots') or {}).items():
        out['shots'].setdefault(k, {}).update(v if isinstance(v, dict) else {})
    for k in ('avoid', 'hero'):
        if k in new:
            if new[k]:
                out[k] = new[k]
            else:
                out.pop(k, None)
    for k in list(new):
        if k not in ('slots', 'shots', 'avoid', 'hero', 'repick'):
            out[k] = new[k]                                # unknown keys reach edit.build, which warns about them
    return out


def cmd_run(a):
    job = job_path(a.job)
    os.makedirs(os.path.dirname(job) or '.', exist_ok=True)
    lockf = open(job + '.lock', 'w')
    try:
        fcntl.flock(lockf, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        print('ALREADY RUNNING: another ml.py run holds %s.lock; poll it instead of starting a second run' % job, flush=True)
        return 4
    try:
        return _run(a, job)
    except BaseException as e:                              # never leave status.json at 'running'
        msg = 'exit %s' % e.code if isinstance(e, SystemExit) else '%s: %s' % (type(e).__name__, e)
        try:
            _status(job, state='failed', error='run aborted (%s); see the log' % msg)
        except Exception:
            pass
        print('RUN FAILED %s' % msg, flush=True)
        if isinstance(e, SystemExit):
            return e.code if isinstance(e.code, int) and e.code else 1
        raise
    finally:
        fcntl.flock(lockf, fcntl.LOCK_UN)
        lockf.close()


def _run(a, job):
    timings, t0 = {}, time.time()
    src = a.video
    new = {}
    if a.fixes:
        raw = a.fixes
        if raw.startswith('@'):
            with open(raw[1:], encoding='utf-8') as f:
                raw = f.read()
        try:
            new = json.loads(raw)
            assert isinstance(new, dict)
        except (ValueError, AssertionError):
            os.makedirs(job, exist_ok=True)
            _status(job, stage='fixes', state='failed', error='--fixes is not a JSON object')
            die('--fixes is not a JSON object')
    reuse, why = False, 'first run'
    if os.path.exists(J(job, 'job.json')) and os.path.exists(J(job, 'features.json')) and not a.force:
        st = jload(J(job, 'job.json'))
        same = (st.get('video_arg') == src, float(st.get('start') or 0) == float(a.start or 0), st.get('max_dur_arg') == a.max_dur)
        reuse = all(same)
        why = 'reusing init + prep' if reuse else 'options changed (%s): full redo' % ', '.join(
            n for n, ok in zip(('video', '--start', '--max-dur'), same) if not ok)
    elif a.force:
        why = '--force: full redo'
    print('run: %s' % why, flush=True)
    prev_user = jload(J(job, 'user_fixes.json'), {}) if reuse and not a.reset_fixes else {}
    prev_pins = (jload(J(job, 'edit_report.json'), {}).get('pins') or {}).get('slots') if reuse and not a.fresh else None
    if not reuse:
        shutil.rmtree(job, ignore_errors=True)
        os.makedirs(job, exist_ok=True)
    _status(job, stage='start', state='running', error=None, out=None, upload=None, review=[], timings={},
            qa_fails=None, warnings=None, fix_warnings=None, grade=None, size_mb=None, people=None, pins=None)
    if not reuse:
        holder = {}

        def fetch():
            holder['path'] = _fetch_video(src, job)
            return 0
        if not _stage(job, 'fetch', fetch, timings):
            return 1
        ia = argparse.Namespace(job=job, video=holder['path'], slug=a.slug, start=a.start, max_dur=a.max_dur, force=True)
        if not _stage(job, 'init', lambda: cmd_init(ia), timings):
            return 1
        st = load_job(job)
        st['video_arg'], st['max_dur_arg'] = src, a.max_dur
        save_job(job, st)
        if not _stage(job, 'prep', lambda: cmd_prep(argparse.Namespace(job=job)), timings):
            return 1
    user = _merge_fixes(prev_user, new)
    tl = template()                                         # store only names that exist (edit.build warns about the rest)
    stored = dict(user)
    stored['slots'] = {k: v for k, v in user.get('slots', {}).items() if k in tl['slots']}
    stored['shots'] = {k: v for k, v in user.get('shots', {}).items() if k in {s['id'] for s in tl['shots']}}
    jsave(J(job, 'user_fixes.json'), stored)
    fx = dict(user)
    if new.get('repick'):
        fx['repick'] = new['repick']
    if prev_pins and not ('hero' in new or 'avoid' in new):
        fx['keep'] = prev_pins                              # hold every earlier pick that this round does not change
    elif prev_pins:
        print('run: hero / avoid changed: every slot is re-picked except your explicit pins', flush=True)
    jsave(J(job, 'fixes.json'), fx)
    st = load_job(job)
    glow = bool(a.glow or (reuse and st.get('glow') and not a.no_glow))
    st['glow'] = glow
    save_job(job, st)
    if not _stage(job, 'edit', lambda: cmd_edit(argparse.Namespace(job=job, glow=glow, no_sheet=False)), timings):
        return 1

    def rend():
        rc = cmd_render(argparse.Namespace(job=job, par=None, timeout=None, no_qa=False))
        return 0 if rc in (0, None) or os.path.exists(J(job, 'qa', 'qa.json')) else rc
    if not _stage(job, 'render', rend, timings):
        return 1
    if not _stage(job, 'review', lambda: (review_images(job), 0)[1], timings):
        return 1
    st = load_job(job)
    out = J(job, 'out', '%s.mp4' % st['slug'])
    qa = jload(J(job, 'qa', 'qa.json'), {})
    fails = [c for c in qa.get('checks', []) if c['status'] != 'pass']
    rep = jload(J(job, 'edit_report.json'), {})
    upload = None
    if a.upload_url:
        upload = _put(job, out, a.upload_url)
    timings['total'] = round(time.time() - t0, 1)
    ok = not fails and (upload is None or upload['http'] == '200')
    review = sorted(os.path.relpath(J(job, 'review', n), job) for n in os.listdir(J(job, 'review')))
    _status(job, stage='done', state='ok' if ok else 'attention', out=os.path.relpath(out, job),
            size_mb=round(os.path.getsize(out) / 1e6, 1), qa_fails=fails, upload=upload, review=review,
            warnings=rep.get('warnings', []), fix_warnings=rep.get('fix_warnings', []), grade=rep.get('grade_notes', []),
            people=rep.get('people', []), pins=rep.get('pins'), glow=glow, timings=timings)
    print('RUN %s total %.1fs out %s%s' % ('OK' if ok else 'ATTENTION', timings['total'], out,
                                         '' if a.upload_url else ' (not uploaded: review, then ml.py upload)'), flush=True)
    return 0 if ok else 3


def _put(job, path, url):
    p = run(['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', '-X', 'PUT', '-H', 'Content-Type: video/mp4',
             '-H', 'If-None-Match: *', '--retry', '2', '--data-binary', '@' + path, url], check=False)
    up = {'http': (p.stdout or '').strip() or None, 'error': (p.stderr or '').strip()[:200] or None,
          'at': now_iso(), 'bytes': os.path.getsize(path)}
    print('upload: HTTP %s' % up['http'], flush=True)
    _status(job, upload=up)
    return up


def cmd_upload(a):
    """PUT the finished mp4 to a presigned URL (after review); prints 'upload: HTTP <code>'."""
    job = job_path(a.job)
    st = load_job(job)
    out = J(job, 'out', '%s.mp4' % st['slug'])
    if not os.path.isfile(out):
        die('no render at %s (run first)' % out)
    up = _put(job, out, a.upload_url)
    return 0 if up['http'] == '200' else 1


def cmd_picks(a):
    """the current edit: people, every slot's source window / camera / hero share, warnings, source cuts."""
    job = job_path(a.job)
    rep = jload(J(job, 'edit_report.json'), {})
    if not rep:
        die('no edit_report.json (run first)')
    for line in rep.get('summary', []):
        print(line)
    feats = jload(J(job, 'features.json'), {})
    if feats:
        print('source: %d frames (%.2f s at 24 fps), size %sx%s, cuts at frames %s' % (
            feats['n'], feats['n'] / 24.0, feats['size'][0], feats['size'][1], [c[0] for c in feats.get('cuts', [])]))
    return 0


# ============================================================================ sheet / serve / status
def cmd_sheet(a):
    job = job_path(a.job)
    fr = [int(v) for v in a.f.split(',') if v.strip()]
    name = a.name or 'sheet_%s' % time.strftime('%H%M%S')
    with Server(job) as srv:
        p = capture(job, srv, 'index.html?sheet=%s&cols=%d&div=%d&name=%s' % (','.join(map(str, fr)), a.cols or min(6, len(fr)), a.div, name), name)
    shutil.copy(p, J(job, 'qa', name + '.jpg'))
    print(J(job, 'qa', name + '.jpg'))
    return 0


def cmd_srcsheet(a):
    """review/src_NN.jpg: every `step`-th source frame, 6x5 tiles, each labelled with its source frame number."""
    job = job_path(a.job)
    st = load_job(job)
    n = int(st['frames'])
    step = max(1, int(a.step)) if a.step else (6 if n <= 240 else 12)
    d = J(job, 'review')
    os.makedirs(d, exist_ok=True)
    for f in os.listdir(d):
        if f.startswith('src_'):
            os.remove(J(d, f))
    fil = ff('-filters').stdout
    font = next((f for f in ('/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf',
                             '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
                             '/System/Library/Fonts/Supplemental/Arial Bold.ttf') if os.path.isfile(f)), None)
    lab = ''
    if re.search(r'\sdrawtext\s', fil):
        lab = "drawtext=%stext='%%{n}':x=4:y=4:fontsize=22:fontcolor=yellow:box=1:boxcolor=black@0.7," % (
            ("fontfile='%s':" % font) if font else '')
    ff('-loglevel', 'error', '-y', '-start_number', '0', '-i', J(job, 'web', 'ana', CLIP, '%05d.jpg'), '-vf',
       "%sselect='not(mod(n\\,%d))',scale=240:-2,tile=6x5:padding=3:color=gray" % (lab, step), '-fps_mode', 'vfr',
       '-q:v', '6', '-start_number', '1', J(d, 'src_%02d.jpg'))
    out = sorted(f for f in os.listdir(d) if f.startswith('src_'))
    print('source sheets (every %d frames = %.2f s; %d frames, %d per sheet%s):' % (
        step, step / float(FPS), n, 30, '' if lab else ', unlabelled: ffmpeg has no drawtext'))
    for i, f in enumerate(out):
        print('  review/%s  frames %d-%d' % (f, i * 30 * step, min(n - 1, (i + 1) * 30 * step - 1)))
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
    print('slug %s  source %s  %sx%s  %s frames' % (st['slug'], st['video_src'], st['size'][0], st['size'][1], st['frames']))
    for k, v in (st.get('steps') or {}).items():
        print('step %-7s %s' % (k, json.dumps(v, ensure_ascii=False)))
    return 0


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except AttributeError:
        pass
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
    s = sub.add_parser('run')
    s.add_argument('job')
    s.add_argument('--video', required=True, help='local file or https URL of the clip')
    s.add_argument('--slug')
    s.add_argument('--start', type=float, default=0.0)
    s.add_argument('--max-dur', type=float)
    s.add_argument('--glow', action='store_true')
    s.add_argument('--fixes', help='fixes.json content as JSON, or @path')
    s.add_argument('--upload-url', help='presigned PUT URL (media_upload, content type video/mp4) for the final mp4')
    s.add_argument('--force', action='store_true', help='redo init + prep even for the same video')
    s.add_argument('--fresh', action='store_true', help='re-pick every slot (keep only explicit pins)')
    s.add_argument('--reset-fixes', action='store_true', help='forget the fixes of earlier runs of this job')
    s.add_argument('--no-glow', action='store_true', help='turn off --glow remembered from an earlier run')
    s = sub.add_parser('upload')
    s.add_argument('job')
    s.add_argument('--upload-url', required=True)
    s = sub.add_parser('picks')
    s.add_argument('job')
    s = sub.add_parser('edit')
    s.add_argument('job')
    s.add_argument('--glow', action='store_true', help='synthetic glowing eyes on the template eye shots')
    s.add_argument('--no-sheet', action='store_true')
    s = sub.add_parser('render')
    s.add_argument('job')
    s.add_argument('--par', type=int)
    s.add_argument('--timeout', type=int)
    s.add_argument('--no-qa', action='store_true')
    s = sub.add_parser('qa')
    s.add_argument('job')
    s = sub.add_parser('sheet')
    s.add_argument('job')
    s.add_argument('--f', required=True)
    s.add_argument('--name')
    s.add_argument('--cols', type=int)
    s.add_argument('--div', type=int, default=3)
    s = sub.add_parser('srcsheet')
    s.add_argument('job')
    s.add_argument('--step', type=int, help='every Nth source frame (default 6 for clips up to 10 s, else 12)')
    s = sub.add_parser('serve')
    s.add_argument('job')
    s = sub.add_parser('status')
    s.add_argument('job')
    a = ap.parse_args()
    return {'run': cmd_run, 'upload': cmd_upload, 'picks': cmd_picks, 'assets': cmd_assets, 'doctor': cmd_doctor, 'init': cmd_init, 'prep': cmd_prep, 'edit': cmd_edit, 'render': cmd_render,
            'qa': cmd_qa, 'sheet': cmd_sheet, 'srcsheet': cmd_srcsheet, 'serve': cmd_serve, 'status': cmd_status}[a.cmd](a)


if __name__ == '__main__':
    sys.exit(main() or 0)
