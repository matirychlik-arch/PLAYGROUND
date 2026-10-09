#!/usr/bin/env python3
"""pc.py - CLI of the pink-collage skill (python3 stdlib; the pixel work runs in the skill's venv).

usage: python3 -I pc.py <command> [job_dir] [options]

  assets [--force]                 template music + QA frames (pinned CDN archive) into the kit, fonts + ONNX models
                                   into PC_HOME (default ~/.cache/pink-collage); everything sha256-verified, via curl
  setup [--sandbox]                venv in PC_HOME with the pinned requirements (Socket firewall index); --sandbox: on a
                                   host with numpy/Pillow/onnxruntime (Higgsfield sandbox) only the pinned opencv wheel
  doctor [job]                     environment check (ffmpeg, venv, assets, template, a lettering smoke test)
  init <job> --video V [--video V2] [--slug S] [--start s] [--max-dur s] [--text T]
                                   normalize the clip(s) (short side 1080, <= 30 fps, no audio) -> src/v0.mp4 [v1.mp4];
                                   texts.json = the prompt box ({"text": T}; empty = no lettering in the edit)
  prep <job>                       cuts + per-frame faces, person box, sharpness, motion -> features.json
  edit <job> [--split s] [--no-sheet]
                                   template slots -> moments + framings -> cast.json, edit_report.json, review sheets
                                   qa/edit_A.jpg, qa/edit_B.jpg; <job>/fixes.json pins slots (references/fixes.md)
  render <job> [--par N] [--no-qa] masks, parallel chunks, music, 2-pass H.264 -> out/<slug>.mp4, then qa
  qa <job>                         checks + comparison sheets (template | render) -> qa/qa.json, qa/cmp_NN.jpg
  sheet <job> --t a,b,c [--name N] labelled stills of the edit at output times (s) -> qa/<N>.jpg
  src <job> [--alias v0] [--t0 s] [--t1 s] [--every s]
                                   contact sheet of raw source frames labelled with source time -> qa/src_<alias>.jpg
  status <job>                     job summary
  sandbox review|render REQUEST.json
                                   one-call pipeline for an ephemeral host (the Higgsfield sandbox): assets, setup
                                   --sandbox, clip download, init, prep, edit (+ review sheets, then hold the host alive
                                   for the review) | render, qa, upload to a presigned URL; progress in <job>/status.json

Exit codes: 0 ok, 1 problems (render/qa), 2 usage or input error.
Env: PC_HOME (venv + assets), PC_PAR (parallel render processes, default min(8, cpus/2, free RAM / 1.6 GB)).
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time

sys.dont_write_bytecode = True
SCRIPTS = os.path.dirname(os.path.abspath(__file__))
SK = os.path.dirname(SCRIPTS)
sys.path.insert(0, SCRIPTS)
import cast as CASTER  # noqa: E402

PC_HOME = os.path.expanduser(os.environ.get('PC_HOME', '~/.cache/pink-collage'))
VENV = os.path.join(PC_HOME, 'venv')
VPY = os.path.join(VENV, 'bin', 'python')
PIP_INDEX = 'https://socket.higgsfield.xyz/pypi/simple'       # every package goes through the Socket firewall
FFMPEG = shutil.which('ffmpeg') or 'ffmpeg'
FFPROBE = shutil.which('ffprobe') or 'ffprobe'
CPUS = os.cpu_count() or 4
PROC_GB = 1.6        # peak RAM of one render chunk process (source frame cache + cut-out models), measured


def mem_gb():
    """Available RAM in GB (Linux MemAvailable, macOS physical memory), 8 when unknown."""
    try:
        with open('/proc/meminfo') as f:
            for line in f:
                if line.startswith('MemAvailable:'):
                    return int(line.split()[1]) / 1e6
    except OSError:
        pass
    try:
        return int(subprocess.run(['sysctl', '-n', 'hw.memsize'], capture_output=True, text=True).stdout) / 1e9
    except (ValueError, OSError):
        return 8.0


PAR = max(1, int(os.environ.get('PC_PAR', '0') or 0)
          or min(8, max(1, CPUS // 2), max(1, int((mem_gb() - 1.0) / PROC_GB))))
MAX_DUR, MIN_DUR = 60.0, 4.0
DELIVER_MB = 30.0
KBPS = 13000
TEMPLATE = os.path.join(SK, 'template')

TEXT_MAX = 24        # prompt box: one optional Latin text, written into every lettering beat


# ============================================================================ helpers
LAST_ERROR = ['']
PROGRESS = [None]      # sandbox: callback(step, message) so status.json follows long commands


def progress(step, message):
    print(f'{step}: {message}', flush=True)
    if PROGRESS[0]:
        PROGRESS[0](step, message)


def die(msg, code=2):
    LAST_ERROR[0] = msg
    print('error: ' + msg, file=sys.stderr)
    sys.exit(code)


def J(*p):
    return os.path.join(*p)


def jload(path, default=None):
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        if default is not None:
            return default
        raise
    except json.JSONDecodeError as e:
        die(f'{path}: bad JSON ({e})')


def jsave(path, obj, indent=1):
    tmp = path + '.tmp'
    with open(tmp, 'w') as f:
        json.dump(obj, f, indent=indent, ensure_ascii=False)
    os.replace(tmp, path)


def run(args, check=True, env=None, capture=True):
    r = subprocess.run(args, capture_output=capture, text=True, env=env)
    if check and r.returncode:
        tail = ((r.stderr or '') + (r.stdout or '')).strip()[-1500:] if capture else ''
        die(f'command failed ({r.returncode}): {" ".join(args[:4])} ...\n{tail}', 1)
    return r


def venv_env(job=None, threads=None):
    env = dict(os.environ, GLOW_FONTS=J(PC_HOME, 'fonts'), GLOW_MODELS=J(PC_HOME, 'models'),
               PYTHONDONTWRITEBYTECODE='1', GLOW_SRC_CACHE='60')
    if job:
        env['GLOW_MASK_CACHE'] = J(job, 'cache', 'masks')
    if threads:
        env['GLOW_THREADS'] = str(threads)
        env['OMP_NUM_THREADS'] = str(threads)
    return env


def vrun(script, *args, job=None, threads=None, check=True, capture=True):
    if not os.path.exists(VPY):
        die('venv missing: run `pc.py setup` first')
    return run([VPY, '-I', J(SCRIPTS, script), *args], check=check, env=venv_env(job, threads), capture=capture)


def vpopen(script, *args, job=None, threads=None, log=None):
    out = open(log, 'w') if log else subprocess.DEVNULL
    env = venv_env(job, threads)
    env['GLOW_CHUNK_VENC'] = json.dumps(venc('chunk'))
    return subprocess.Popen([VPY, '-I', J(SCRIPTS, script), *args], stdout=out, stderr=subprocess.STDOUT, env=env)


def job_path(arg):
    return os.path.abspath(os.path.expanduser(arg))


def load_job(job):
    st = jload(J(job, 'job.json'), {})
    if not st:
        die(f'not a job dir (no job.json): {job}  - run `pc.py init` first')
    return st


def mark(job, step, **info):
    st = load_job(job)
    st.setdefault('steps', {})[step] = dict(at=time.strftime('%Y-%m-%dT%H:%M:%S'), **info)
    jsave(J(job, 'job.json'), st)


def template():
    return jload(J(TEMPLATE, 'template.json'))


def probe(path):
    r = run([FFPROBE, '-v', 'error', '-show_entries',
             'stream=codec_type,width,height,avg_frame_rate,nb_frames:stream_side_data=rotation:format=duration,size',
             '-of', 'json', path])
    return json.loads(r.stdout)


_ENC = None


def venc(kind):
    """H.264 encoder args: libx264 when ffmpeg has it, else VideoToolbox (macOS ffmpeg builds without GPL x264).
    kind: 'src' (normalized source, short GOP for seeking), 'chunk' (near-lossless intermediate), 'deliver'."""
    global _ENC
    if _ENC is None:
        enc = run([FFMPEG, '-hide_banner', '-encoders'], check=False).stdout or ''
        _ENC = 'libx264' if re.search(r'\slibx264\s', enc) else 'h264_videotoolbox' if 'h264_videotoolbox' in enc else ''
    if not _ENC:
        die('ffmpeg has no H.264 encoder (libx264 or h264_videotoolbox)', 1)
    x = _ENC == 'libx264'
    if kind == 'src':
        return (['-c:v', 'libx264', '-preset', 'fast', '-crf', '16', '-bf', '0'] if x else
                ['-c:v', 'h264_videotoolbox', '-b:v', '40M', '-bf', '0']) + ['-g', '12', '-pix_fmt', 'yuv420p']
    if kind == 'chunk':
        return (['-c:v', 'libx264', '-preset', 'medium', '-crf', '12'] if x else
                ['-c:v', 'h264_videotoolbox', '-b:v', '80M']) + ['-pix_fmt', 'yuv420p']
    k = KBPS
    rate = ['-b:v', f'{k}k', '-maxrate', f'{k * 3 // 2}k', '-bufsize', f'{k * 2}k']
    return (['-c:v', 'libx264', '-preset', 'slow', '-profile:v', 'high', *rate, '-x264-params', 'keyint=60'] if x else
            ['-c:v', 'h264_videotoolbox', '-profile:v', 'high', *rate, '-g', '60']) + ['-pix_fmt', 'yuv420p']


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


# ============================================================================ assets / setup / doctor
HEX64 = re.compile(r'^[0-9a-f]{64}$')
ASSET_DIRS = ('template/',)          # the only kit paths the archive may write
HOME_DIRS = ('fonts/', 'models/', 'wheels/')    # the only PC_HOME paths the downloads may write


def host_platform():
    """'linux-x86_64', 'darwin-arm64', ... (downloads with a "platform" field are fetched only on that host)."""
    import platform
    m = platform.machine().lower()
    return f'{sys.platform}-{"x86_64" if m in ("amd64", "x86_64") else "arm64" if m in ("arm64", "aarch64") else m}'


def _rel_ok(rel, prefixes):
    """a manifest path: relative POSIX path under one of prefixes, no '.', '..' or empty segments"""
    if not isinstance(rel, str) or not rel or '\\' in rel or '\0' in rel or rel.startswith('/'):
        return False
    parts = rel.split('/')
    return not any(p in ('', '.', '..') for p in parts) and rel.startswith(prefixes) and len(parts) >= 2


def manifest():
    """<SK>/assets.json -> (archive, files, downloads); dies with a clear message when it is missing or malformed."""
    try:
        m = jload(J(SK, 'assets.json'))
    except FileNotFoundError:
        die('missing assets.json next to scripts/ (write it from the workflow bundle)')
    arc, files, dls = (m.get(k) if isinstance(m, dict) else None for k in ('archive', 'files', 'downloads'))
    if not (isinstance(arc, dict) and isinstance(files, dict) and files and isinstance(dls, dict) and dls):
        die('assets.json needs "archive", "files" and "downloads"')
    if not (str(arc.get('url', '')).startswith('https://') and HEX64.match(str(arc.get('sha256', '')))
            and isinstance(arc.get('bytes'), int) and arc.get('format') == 'tar.gz'):
        die('assets.json: bad "archive" entry (https url, format tar.gz, sha256, bytes)')
    for rel, meta in files.items():
        if not (_rel_ok(rel, ASSET_DIRS) and HEX64.match(str(meta.get('sha256', ''))) and isinstance(meta.get('bytes'), int)):
            die(f'assets.json: bad file entry {rel!r}')
    for rel, meta in dls.items():
        if not (_rel_ok(rel, HOME_DIRS) and str(meta.get('url', '')).startswith('https://')
                and HEX64.match(str(meta.get('sha256', ''))) and isinstance(meta.get('bytes'), int)
                and (not meta.get('gz') or HEX64.match(str(meta.get('gz_sha256', ''))))):
            die(f'assets.json: bad download entry {rel!r}')
    here = host_platform()
    dls = {r: m for r, m in dls.items() if m.get('platform') in (None, here)}
    return arc, files, dls


def file_ok(path, meta, full=True):
    if os.path.islink(path) or not os.path.isfile(path) or os.path.getsize(path) != meta['bytes']:
        return False
    return not full or sha256(path) == meta['sha256']


def curl(url, dst, tries=4):
    """System curl: python.org builds of Python on macOS ship without root certificates (urllib fails on HTTPS)."""
    part, last = dst + '.part', None
    for k in range(tries):
        r = subprocess.run(['curl', '-fsSL', '--connect-timeout', '20', '--max-time', '900', '-A', 'pc.py/1',
                            '-o', part, url], capture_output=True, text=True)
        if r.returncode == 0 and os.path.getsize(part) > 0:
            os.replace(part, dst)
            return
        last = r.stderr.strip()[:200] or 'empty response'
        time.sleep(2 * (k + 1))
    if os.path.exists(part):
        os.remove(part)
    die(f'download failed after {tries} tries: {url}: {last}', 1)


def write_member(tf, m, dst, meta):
    """Stream one archive member to dst, verifying size + sha256 before it replaces anything."""
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.islink(dst):
        os.remove(dst)
    tmp, h, n = dst + '.part', hashlib.sha256(), 0
    try:
        with tf.extractfile(m) as src, open(tmp, 'wb') as f:
            for b in iter(lambda: src.read(1 << 20), b''):
                h.update(b)
                n += len(b)
                f.write(b)
        if n != meta['bytes'] or h.hexdigest() != meta['sha256']:
            die(f'{dst}: extracted bytes do not match assets.json', 1)
        os.chmod(tmp, 0o644)
        os.replace(tmp, dst)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def install_archive(arc, files, wanted):
    """Download the pinned template archive and write only the `wanted` manifest files into the kit. Every member
    must be a manifest-listed regular file with a safe relative path; anything else aborts."""
    root = os.path.realpath(SK)
    with tempfile.TemporaryDirectory(prefix='pc_assets_') as td:
        tgz = J(td, 'assets.tar.gz')
        curl(arc['url'], tgz)
        if os.path.getsize(tgz) != arc['bytes'] or sha256(tgz) != arc['sha256']:
            die('template archive: size / sha256 differ from assets.json (re-run pc.py assets --force)', 1)
        seen = set()
        with tarfile.open(tgz, 'r:gz') as tf:
            for m in tf:
                rel = m.name[2:] if m.name.startswith('./') else m.name
                if m.isdir() and any(r.startswith(rel.rstrip('/') + '/') for r in files):
                    continue
                if not (_rel_ok(rel, ASSET_DIRS) and m.isreg() and rel in files and rel not in seen):
                    die(f'archive member {m.name!r}: unsafe, not a regular file, unlisted or repeated', 1)
                seen.add(rel)
                if rel in wanted:
                    dst = J(SK, *rel.split('/'))
                    if not os.path.realpath(os.path.dirname(dst) or SK).startswith(root):
                        die(f'refusing to write {rel}: resolves outside the kit', 1)
                    write_member(tf, m, dst, files[rel])
        if set(wanted) - seen:
            die(f'archive lacks {len(set(wanted) - seen)} manifest file(s)', 1)


def install_download(rel, meta):
    """One pinned download into PC_HOME. "gz": the CDN copy is gzip-compressed; its sha256 is checked before it is
    decompressed, and the file's own sha256 after."""
    import gzip
    dst = J(PC_HOME, *rel.split('/'))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if not meta.get('gz'):
        curl(meta['url'], dst)
    else:
        with tempfile.TemporaryDirectory(prefix='pc_dl_', dir=PC_HOME) as td:
            gz = J(td, 'download.gz')
            curl(meta['url'], gz)
            if sha256(gz) != meta['gz_sha256']:
                die(f'{rel}: the CDN copy does not match gz_sha256 in assets.json', 1)
            tmp = dst + '.part'
            with gzip.open(gz, 'rb') as src, open(tmp, 'wb') as out:
                shutil.copyfileobj(src, out, 1 << 20)
            os.replace(tmp, dst)
    if not file_ok(dst, meta):
        os.remove(dst)
        die(f'{rel}: size / sha256 mismatch after download', 1)


def cmd_assets(a):
    arc, files, dls = manifest()
    bad = sorted(files) if a.force else [r for r, m in files.items() if not file_ok(J(SK, *r.split('/')), m)]
    if bad:
        print(f'assets   template: {len(bad)} of {len(files)} file(s) to install, archive {arc["bytes"] / 1e6:.1f} MB')
        install_archive(arc, files, set(bad))
    todo = [r for r, m in dls.items() if a.force or not file_ok(J(PC_HOME, *r.split('/')), m)]
    for rel in todo:
        print(f'assets   {rel} ({dls[rel]["bytes"] / 1e6:.1f} MB) -> {PC_HOME}')
        install_download(rel, dls[rel])
    left = [r for r, m in files.items() if not file_ok(J(SK, *r.split('/')), m)]
    left += [r for r, m in dls.items() if not file_ok(J(PC_HOME, *r.split('/')), m)]
    if left:
        die(f'{len(left)} asset(s) still invalid: {", ".join(left[:5])}', 1)
    print(f'assets: OK  ({len(files)} template files + {len(dls)} fonts/models/wheels verified, sha256)')


def cmd_setup(a):
    """The venv for the pixel work.
    default:   exact pins from requirements.txt, through the Socket firewall index (needs the corporate network).
    --sandbox: a host that already has numpy, Pillow and onnxruntime (the Higgsfield sandbox): the venv sees the
               system packages and gets only the sha256-pinned opencv wheel from assets (no package index at all)."""
    os.makedirs(PC_HOME, exist_ok=True)
    if a.sandbox:
        base = shutil.which('python3')
        probe_ = run([base, '-I', '-c', 'import numpy, PIL, onnxruntime; print(numpy.__version__, PIL.__version__, '
                      'onnxruntime.__version__)'], check=False)
        if probe_.returncode:
            die('--sandbox needs numpy, Pillow and onnxruntime preinstalled for python3 on this host', 1)
        wheels = [J(PC_HOME, *r.split('/')) for r in manifest()[2] if r.startswith('wheels/')]
        if not wheels or not all(os.path.isfile(w) for w in wheels):
            die('no pinned wheel for this platform in PC_HOME/wheels (run: pc.py assets first)', 1)
        if not os.path.exists(VPY):
            print(f'venv: {VENV} ({base}, system site-packages: {probe_.stdout.strip()})')
            run([base, '-m', 'venv', '--system-site-packages', VENV])
        ok = run([VPY, '-I', '-c', 'import cv2; print(cv2.__version__)'], check=False)
        if ok.returncode:
            env = dict(os.environ, PIP_DISABLE_PIP_VERSION_CHECK='1', PIP_NO_INDEX='1')
            run([VPY, '-m', 'pip', 'install', '-q', '--no-index', '--no-deps', *wheels], env=env)
        print('setup: OK (sandbox: system numpy / Pillow / onnxruntime + pinned opencv wheel)')
        return
    if not os.path.exists(VPY):
        base = next((p for p in (shutil.which(f'python3.{v}') for v in (13, 12, 11, 10)) if p), None)
        if not base:
            die('needs Python 3.10 or newer (python3.10 .. python3.13 on PATH) for the venv')
        print(f'venv: {VENV} ({base})')
        run([base, '-m', 'venv', VENV])
    env = dict(os.environ, PIP_INDEX_URL=PIP_INDEX, PIP_DISABLE_PIP_VERSION_CHECK='1')
    print('pip: requirements.txt via the Socket firewall index')
    r = run([VPY, '-m', 'pip', 'install', '-q', '--index-url', PIP_INDEX, '-r', J(SK, 'requirements.txt')],
            check=False, env=env)
    if r.returncode:
        die('pip install failed (Socket index unreachable? it needs the corporate VPN; never switch to public '
            'PyPI):\n' + (r.stderr or r.stdout)[-1200:], 1)
    print('setup: OK')


def cmd_doctor(a):
    ok = True

    def rep(cond, what, info=''):
        nonlocal ok
        ok &= bool(cond)
        print(f'  {"ok " if cond else "BAD"} {what}{"  " + info if info else ""}')

    rep(shutil.which('ffmpeg'), 'ffmpeg', FFMPEG)
    rep(shutil.which('ffprobe'), 'ffprobe', FFPROBE)
    enc = run([FFMPEG, '-hide_banner', '-encoders'], check=False).stdout or ''
    h264 = 'libx264' if re.search(r'\slibx264\s', enc) else 'h264_videotoolbox' if 'h264_videotoolbox' in enc else ''
    rep(h264 and re.search(r'\baac\b', enc), 'ffmpeg encoders H.264 + aac', h264)
    rep(shutil.which('curl'), 'curl')
    rep(os.path.exists(VPY), 'venv', VENV + ('' if os.path.exists(VPY) else '  (run: pc.py setup)'))
    if os.path.exists(VPY):
        r = run([VPY, '-I', '-c', 'import cv2, numpy, PIL, onnxruntime; print(cv2.__version__, numpy.__version__, '
                 'PIL.__version__, onnxruntime.__version__, hasattr(cv2, "FaceDetectorYN"))'], check=False)
        rep(r.returncode == 0 and r.stdout.strip().endswith('True'), 'venv packages', (r.stdout or r.stderr).strip()[-200:])
    arc, files, dls = manifest()
    miss = [r for r, m in files.items() if not file_ok(J(SK, *r.split('/')), m, full=False)]
    miss += [r for r, m in dls.items() if not file_ok(J(PC_HOME, *r.split('/')), m, full=False)]
    rep(not miss, f'assets ({len(files)} template files, {len(dls)} fonts/models/wheels)',
        f'{len(miss)} missing or invalid, e.g. {miss[0]}  (run: pc.py assets)' if miss else '')
    tpl = template()
    rep(tpl['frames'] == 795 and all(f'template/ref/{f:03d}.jpg' in files for f in tpl['qa']),
        'template (795 frames, QA frames listed)')
    if ok:
        code = ('import sys; sys.path.insert(0, %r); from glow import y2k as Y; '
                'r, a = Y.neon_text("Pink Collage", 120, stars=2); c = Y.crayon_text("pink collage", 90); '
                'f = Y.mirror_frame(250, 347); print(a.shape, c[1].shape)') % SK
        t0 = time.time()
        r = run([VPY, '-I', '-c', code], check=False, env=venv_env())
        rep(r.returncode == 0, 'engine smoke (neon, crayon, mirror frame)',
            f'{time.time() - t0:.1f}s' if r.returncode == 0 else (r.stderr or '')[-400:])
    if a.job:
        job = job_path(a.job)
        st = jload(J(job, 'job.json'), {})
        print(f'  job {job}: steps {", ".join(st.get("steps", {})) or "-"}')
    print('doctor: OK' if ok else 'doctor: PROBLEMS (see BAD lines)')
    sys.exit(0 if ok else 1)


# ============================================================================ init
ALLOWED = re.compile(r"^[A-Za-z0-9 .,!?'&@#:;()\-_/+*~\n]*$")


def check_text(field, s):
    if s is None:
        return
    if not ALLOWED.match(s):
        bad = sorted({c for c in s if not ALLOWED.match(c)})
        die(f'{field}: the template fonts are Latin only; unsupported characters {"".join(bad)!r}')


def prompt_text(t):
    """The prompt box: '' (no lettering) or one Latin text <= TEXT_MAX characters, case kept as typed."""
    t = ' '.join((t or '').replace('\\n', ' ').split())
    check_text('text', t)
    if len(t) > TEXT_MAX:
        die(f'text is {len(t)} characters, max {TEXT_MAX}')
    return t


def normalize(src, dst, start, max_dur):
    info = probe(src)
    vs = [s for s in info['streams'] if s.get('codec_type') == 'video']
    if not vs:
        die(f'no video stream: {src}')
    dur = float(info['format'].get('duration') or 0)
    use = min(max_dur, dur - start)
    if use < MIN_DUR:
        die(f'clip too short: {use:.1f} s usable (need >= {MIN_DUR:.0f} s): {src}')
    w, h = int(vs[0]['width']), int(vs[0]['height'])
    rot = 0
    for sd in vs[0].get('side_data_list', []) or []:
        rot = int(sd.get('rotation', 0) or 0)
    if rot % 180:
        w, h = h, w
    num, _, den = vs[0].get('avg_frame_rate', '30/1').partition('/')
    fps = float(num) / float(den or 1) if float(den or 1) else 30.0
    scale = 'scale=-2:1080' if w >= h else 'scale=1080:-2'
    vf = f'{scale}:flags=lanczos,setsar=1' + (',fps=30' if fps > 30.5 or fps < 1 else '')
    run([FFMPEG, '-v', 'error', '-y', '-ss', f'{start:.3f}', '-i', src, '-t', f'{use:.3f}', '-an', '-sn', '-dn',
         '-vf', vf, *venc('src'), '-movflags', '+faststart', dst])
    return use, w, h, fps


def cmd_init(a):
    job = job_path(a.job)
    vids = [os.path.abspath(os.path.expanduser(v)) for v in a.video]
    if not 1 <= len(vids) <= 2:
        die('give one clip (--video) or two (phrase A, phrase B)')
    for v in vids:
        if not os.path.isfile(v):
            die(f'no such file: {v}')
    if os.path.abspath(job).startswith(SK + os.sep):
        die('the job dir must not be inside the skill')
    os.makedirs(J(job, 'src'), exist_ok=True)
    for d in ('qa', 'out', 'cache', 'logs'):
        os.makedirs(J(job, d), exist_ok=True)
    tx = {'text': prompt_text(a.text)}
    srcs = []
    for i, v in enumerate(vids):
        print(f'normalize v{i}: {os.path.basename(v)}')
        use, w, h, fps = normalize(v, J(job, 'src', f'v{i}.mp4'), a.start, a.max_dur)
        srcs.append(dict(alias=f'v{i}', file=v, used_s=round(use, 3), src_size=[w, h], src_fps=round(fps, 3)))
    slug = a.slug or re.sub(r'[^a-z0-9]+', '-', os.path.splitext(os.path.basename(vids[0]))[0].lower()).strip('-')
    now = time.strftime('%Y-%m-%dT%H:%M:%S')
    jsave(J(job, 'job.json'), dict(slug=f'{slug or "clip"}_pink_collage', sources=srcs, created=now,
                                   steps={'init': {'at': now}}))
    jsave(J(job, 'texts.json'), tx)
    used = ', '.join('%s %.1fs' % (s['alias'], s['used_s']) for s in srcs)
    print(f'init: {job}  ({used}), text: {tx["text"]!r}' + ('' if tx['text'] else ' (no lettering)'))


# ============================================================================ prep / edit
def cmd_prep(a):
    job = job_path(a.job)
    load_job(job)
    t0 = time.time()
    r = vrun('analyze.py', job, job=job)
    print(r.stdout.strip())
    mark(job, 'prep', secs=round(time.time() - t0, 1))
    print(f'prep: features.json ({time.time() - t0:.0f}s)')


def check_texts(tx):
    t = tx.get('text', '')
    if not isinstance(t, str) or set(tx) - {'text'}:
        die('texts.json must be {"text": "..."} (the prompt box); re-run init with --text')
    prompt_text(t)


def cmd_edit(a):
    job = job_path(a.job)
    st = load_job(job)
    feats = jload(J(job, 'features.json'), {})
    if not feats:
        die('no features.json: run `pc.py prep` first')
    tx = jload(J(job, 'texts.json'))
    check_texts(tx)
    fixes = jload(J(job, 'fixes.json'), {})
    cast, rep = CASTER.plan(feats, fixes if isinstance(fixes, dict) else {}, a.split)
    print('  heroes: A #%s, B #%s  (people: %s)' % (rep['heroes']['A'], rep['heroes']['B'], ', '.join(
        f'#{p["id"]} first at {p["first"][0]} {p["first"][1]:.1f}s' for p in rep['people'][:4]) or 'none'))
    jsave(J(job, 'cast.json'), cast)
    jsave(J(job, 'edit_report.json'), rep)
    for w in rep['warnings']:
        print('  warn: ' + w)
    for key in ('A', 'B'):
        line = ' '.join(f'{n}@{p["t"]:.1f}' for n, p in rep['picks'][key].items())
        print(f'  {key} [{rep["ranges"][key][0]} {rep["ranges"][key][1][0]:.1f}-{rep["ranges"][key][1][1]:.1f}s]: {line}')
    mark(job, 'edit', warnings=len(rep['warnings']))
    if not a.no_sheet:
        t0 = time.time()
        # cut-out mattes first, in one process (the segmentation models are big); the two sheet processes then
        # read them from the disk cache, and so does render
        vrun('edit.py', job, 'warm', '0/1', job=job, threads=CPUS)
        tpl = template()
        shows = {s_['name']: s_.get('shows', []) for s_ in tpl['slots']}
        two = mem_gb() >= 4.0                   # both sheets at once only when the RAM allows it
        bad = []
        procs = []
        for key in ('A', 'B'):
            args = []
            for r_ in tpl['review']:
                if r_['phrase'] != key:
                    continue
                own = {'inset': ['inset'], 'card2': ['card2']}.get(r_['name'], shows.get(r_['name']) or [])
                parts = [f'{n_} {rep["picks"][key][n_]["t"]:.1f}' for n_ in own if n_ in rep['picks'][key]]
                src_t = f' [{", ".join(parts)}]' if parts else ''     # cast slot + its source second
                args.append(f'{r_["f"] / 60:.4f}:{key} {r_["name"]}{src_t}')
            procs.append(vpopen('edit.py', job, 'stills', J(job, 'qa', f'edit_{key}.jpg'), *args, job=job,
                                threads=max(1, CPUS // (2 if two else 1)), log=J(job, 'logs', f'sheet_{key}.log')))
            if not two:
                bad.append(procs[-1].wait())
        bad += [p_.wait() for p_ in procs] if two else []
        if any(bad):
            die('review sheet failed: see ' + J(job, 'logs', 'sheet_A.log'), 1)
        print(f'edit: cast.json + qa/edit_A.jpg, qa/edit_B.jpg ({time.time() - t0:.0f}s)')
    else:
        print('edit: cast.json')


# ============================================================================ render / qa
def cmd_render(a):
    job = job_path(a.job)
    st = load_job(job)
    if not os.path.exists(J(job, 'cast.json')):
        die('no cast.json: run `pc.py edit` first')
    nsrc = len(st.get('sources', [])) or 1
    # one render process: ~1.2 GB (frames, buffers, its x264 encoder) + ~0.4 GB of frame cache per source
    par = a.par or min(PAR, max(1, int((mem_gb() - 1.0) / (1.2 + 0.4 * nsrc))))
    tpl = template()
    nf = tpl['frames']
    t0 = time.time()
    nw = 1 if mem_gb() < 12 else min(2, par)      # each mask process holds both segmentation models (~2 GB)
    progress('render', f'cut-out masks ({nw} process)')
    procs = [vpopen('edit.py', job, 'warm', f'{i}/{nw}', job=job, threads=max(1, CPUS // nw),
                    log=J(job, 'logs', f'warm_{i}.log')) for i in range(nw)]
    if any(p.wait() for p in procs):
        die('mask pass failed: see ' + J(job, 'logs', 'warm_0.log'), 1)
    progress('render', f'{nf} frames in {par} parallel chunks ({time.time() - t0:.0f}s so far)')
    bounds = [round(i * nf / par) for i in range(par + 1)]
    chunks = [J(job, 'cache', f'chunk_{i:02d}.mp4') for i in range(par)]
    procs = [vpopen('edit.py', job, 'chunk', chunks[i], str(bounds[i]), str(bounds[i + 1]), job=job,
                    threads=max(1, CPUS // par), log=J(job, 'logs', f'chunk_{i:02d}.log')) for i in range(par)]
    while any(p_.poll() is None for p_ in procs):     # progress: frames done across the chunks
        time.sleep(8)
        done = 0
        for i in range(par):
            try:
                with open(J(job, 'logs', f'chunk_{i:02d}.log')) as f:
                    last = [ln for ln in f.read().splitlines() if ln.strip().startswith('frame ')]
                done += int(last[-1].split()[1].split('/')[0]) if last else 0
            except (OSError, ValueError, IndexError):
                pass
        progress('render', f'{min(nf, done)}/{nf} frames ({par} parallel chunks, {time.time() - t0:.0f}s so far)')
    if any(p.wait() for p in procs):
        die('chunk render failed: see ' + J(job, 'logs'), 1)
    progress('encode', f'2-pass H.264 + template music ({time.time() - t0:.0f}s so far)')
    out = J(job, 'out', f'{st["slug"]}.mp4')
    finish(job, chunks, out, nf, tpl['fps'])
    for c in chunks:
        os.remove(c)
    mark(job, 'render', secs=round(time.time() - t0, 1), out=out)
    print(f'render: {out} ({os.path.getsize(out) / 1e6:.1f} MB, {time.time() - t0:.0f}s)')
    if not a.no_qa:
        sys.exit(do_qa(job))


def finish(job, chunks, out, nf, fps):
    lst = J(job, 'cache', 'chunks.txt')
    with open(lst, 'w') as f:
        f.writelines(f"file '{c}'\n" for c in chunks)
    video = J(job, 'cache', 'video.mp4')
    run([FFMPEG, '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', video])
    dur = nf / fps
    common = [*venc('deliver'), '-r', str(fps)]
    log = J(job, 'cache', 'x264')
    two = ['-pass', '2', '-passlogfile', log] if 'libx264' in common else []
    if two:     # 2-pass x264 (VideoToolbox is single pass)
        run([FFMPEG, '-v', 'error', '-y', '-i', video, *common, '-pass', '1', '-passlogfile', log, '-an',
             '-f', 'mp4', os.devnull])
    tmp = out + '.part.mp4'
    run([FFMPEG, '-v', 'error', '-y', '-i', video, '-i', J(TEMPLATE, 'music.m4a'), '-map', '0:v', '-map', '1:a',
         *common, *two, '-af', f'afade=t=out:st={dur - 0.08:.3f}:d=0.08',
         '-c:a', 'aac', '-b:a', '256k', '-ar', '48000', '-t', f'{dur:.4f}', '-map_metadata', '-1',
         '-movflags', '+faststart', tmp])
    os.replace(tmp, out)
    for f in (lst, video, log + '-0.log', log + '-0.log.mbtree'):
        if os.path.exists(f):
            os.remove(f)


def do_qa(job):
    st = load_job(job)
    out = st.get('steps', {}).get('render', {}).get('out') or J(job, 'out', f'{st["slug"]}.mp4')
    if not os.path.exists(out):
        die(f'no render: {out}')
    tpl = template()
    checks = {}
    n = run([FFPROBE, '-v', 'error', '-count_frames', '-select_streams', 'v:0', '-show_entries',
             'stream=nb_read_frames,width,height,r_frame_rate', '-of', 'json', out]).stdout
    v = json.loads(n)['streams'][0]
    info = probe(out)
    types = [s['codec_type'] for s in info['streams']]
    dur = float(info['format']['duration'])
    size_mb = int(info['format']['size']) / 1e6
    checks['frames'] = [int(v['nb_read_frames']), tpl['frames'], int(v['nb_read_frames']) == tpl['frames']]
    checks['size'] = [f'{v["width"]}x{v["height"]}', '1080x1080', (v['width'], v['height']) == (1080, 1080)]
    checks['fps'] = [v['r_frame_rate'], '60/1', v['r_frame_rate'] == '60/1']
    checks['duration'] = [round(dur, 3), tpl['duration'], abs(dur - tpl['duration']) < 0.05]
    checks['streams'] = [types, ['video', 'audio'], types == ['video', 'audio']]
    checks['file_mb'] = [round(size_mb, 1), DELIVER_MB, size_mb <= DELIVER_MB]
    r = vrun('qa.py', job, out, job=job)
    fr = json.loads(r.stdout.strip().splitlines()[-1])
    checks['stray_black'] = [fr['black'], [], not fr['black']]
    checks['stray_white'] = [fr['white'], [], not fr['white']]
    ok = all(c[-1] for c in checks.values())
    jsave(J(job, 'qa', 'qa.json'), dict(video=out, ok=ok, checks=checks))
    for k, c in checks.items():
        print(f'  {"ok " if c[-1] else "BAD"} {k}: {c[0]}')
    print(f'qa: {"OK" if ok else "PROBLEMS"}  sheets qa/cmp_*.jpg')
    return 0 if ok else 1


def cmd_qa(a):
    sys.exit(do_qa(job_path(a.job)))


def cmd_sheet(a):
    job = job_path(a.job)
    load_job(job)
    ts = [t for t in a.t.split(',') if t.strip()]
    out = J(job, 'qa', f'{a.name}.jpg')
    vrun('edit.py', job, 'stills', out, *ts, job=job, threads=CPUS)
    print(f'sheet: {out}')


def cmd_src(a):
    job = job_path(a.job)
    load_job(job)
    path = J(job, 'src', f'{a.alias}.mp4')
    if not os.path.exists(path):
        die(f'no source {a.alias}')
    dur = float(probe(path)['format']['duration'])
    t1 = min(dur - 0.05, a.t1 if a.t1 is not None else dur)
    ts, t = [], a.t0
    while t <= t1 and len(ts) < 120:
        ts.append(round(t, 3))
        t += a.every
    out = J(job, 'qa', f'src_{a.alias}.jpg')
    code = ('import sys; sys.path.insert(0, %r); from glow import media as M; p = %r; info = M.probe(p); '
            'ts = %r; M.contact_sheet([M.grab(p, t, info) for t in ts], ["%%s %%.2f" %% (%r, t) for t in ts], %r, '
            'cols=8, cell_w=240)') % (SK, path, ts, a.alias, out)
    run([VPY, '-I', '-c', code], env=venv_env(job))
    small = shrink(out, out[:-4] + '.small.jpg', max_w=1200, max_kb=240)
    print(f'src: {out} + {small}  ({len(ts)} frames, {a.t0:.2f}-{t1:.2f}s every {a.every}s)')


def cmd_status(a):
    job = job_path(a.job)
    st = load_job(job)
    print(json.dumps(st, indent=1, ensure_ascii=False))
    rep = jload(J(job, 'edit_report.json'), {})
    for w in rep.get('warnings', []):
        print('  warn: ' + w)
    qa = jload(J(job, 'qa', 'qa.json'), {})
    if qa:
        print(f'  qa: {"OK" if qa["ok"] else "PROBLEMS"} {qa["video"]}')


# ============================================================================ sandbox orchestration
def shrink(src, dst, max_w=1100, max_kb=230):
    """JPEG copy small enough for a model to look at (sandbox image_paths: <= 512 KiB per call)."""
    code = ('import sys; from PIL import Image\n'
            'im = Image.open(sys.argv[1]).convert("RGB"); w = int(sys.argv[3]); kb = int(sys.argv[4])\n'
            'if im.width > w: im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)\n'
            'q = 82\n'
            'while True:\n'
            '    im.save(sys.argv[2], quality=q, optimize=True)\n'
            '    import os\n'
            '    if os.path.getsize(sys.argv[2]) <= kb * 1024 or q <= 40:\n'
            '        break\n'
            '    q -= 8\n'
            '    if q <= 58: im = im.resize((int(im.width * 0.85), int(im.height * 0.85)), Image.LANCZOS)\n')
    run([VPY, '-I', '-c', code, src, dst, str(max_w), str(max_kb)], env=venv_env())
    return dst


class Stage:
    """status.json writer for `sandbox`: the agent polls it with `cat <job>/status.json`."""

    def __init__(self, job, stage, run_id=''):
        self.job, self.stage, self.t0 = job, stage, time.time()
        self.data = dict(stage=stage, run_id=run_id, state='running', step='start', message='', started=int(self.t0),
                         pid=os.getpid())
        self.closed = False         # a holder that handed over must never write status.json again
        os.makedirs(job, exist_ok=True)

    def set(self, **kw):
        if self.closed:
            return
        self.data.update(kw)
        self.data['elapsed_s'] = round(time.time() - self.t0)
        self.data['updated'] = int(time.time())
        jsave(J(self.job, 'status.json'), self.data)
        if 'step' in kw or 'message' in kw:
            print(f'[{self.data["elapsed_s"]:4d}s] {self.data["state"]} {self.data["step"]}: {self.data.get("message", "")}',
                  flush=True)


def ns(**kw):
    return argparse.Namespace(**kw)


def sbx_request(path):
    try:
        req = json.load(open(path))
    except (OSError, ValueError) as e:
        die(f'request {path}: not readable JSON ({e})')
    if not isinstance(req, dict):
        die('request: must be one JSON object')
    clips = req.get('clips') or []
    if not (isinstance(clips, list) and 1 <= len(clips) <= 2 and all(str(c).startswith('https://') for c in clips)):
        die('request: "clips" must list 1 or 2 https URLs (the Higgsfield media URLs of the clips)')
    notes = []
    if len(clips) == 2 and clips[0] == clips[1]:
        req['clips'] = clips[:1]
        notes.append('the same clip was given twice: used once (drop 1 from its first half, drop 2 from its second)')
    req.setdefault('job', J(os.path.dirname(PC_HOME.rstrip('/')), 'job'))
    req['text'] = prompt_text(req.get('text') or '')
    req['start'] = float(req.get('start') or 0.0)
    req['max_dur'] = min(MAX_DUR, float(req.get('max_dur') or MAX_DUR))
    req['fixes'] = req.get('fixes') or {}
    if not isinstance(req['fixes'], dict):
        die('request: "fixes" must be an object like {"A": {"text_cu": {"t": 8.4}}}')
    req.setdefault('slug', 'pink_collage')
    req['_notes'] = notes
    return req


def eta_review_s(used_s, sheets=True):
    """Measured in the Higgsfield sandbox: analysis ~3.6 s per used source second, plus downloads/setup/edit."""
    return int(45 + 3.6 * used_s + (55 if sheets else 15))


def sbx_prepare(req, st, sheets):
    """Idempotent part shared by both stages: assets, setup, clips, init, prep, fixes, edit."""
    job = req['job']
    st.set(step='assets', message='template archive, fonts, models, opencv wheel (Higgsfield CDN, sha256)')
    cmd_assets(ns(force=False))
    st.set(step='setup', message='venv on the sandbox python (numpy / Pillow / onnxruntime) + opencv wheel')
    cmd_setup(ns(sandbox=True))
    key = dict(clips=list(req['clips']), start=round(req['start'], 3), max_dur=round(req['max_dur'], 3))
    applied = jload(J(job, 'request.applied.json'), {})
    if applied.get('key') != key or not os.path.exists(J(job, 'job.json')):
        st.set(step='clips', message=f'{len(req["clips"])} clip(s) from their URLs (new clips or start/max_dur)')
        for d in ('in', 'src', 'cache', 'qa', 'out'):
            shutil.rmtree(J(job, d), ignore_errors=True)
        for f in ('job.json', 'features.json', 'cast.json', 'edit_report.json', 'fixes.json'):
            if os.path.exists(J(job, f)):
                os.remove(J(job, f))
        os.makedirs(J(job, 'in'), exist_ok=True)
        local = []
        for k, url in enumerate(req['clips']):
            dst = J(job, 'in', f'clip{k}' + (os.path.splitext(url.split('?')[0])[1][:5] or '.mp4'))
            curl(url, dst)
            local.append(dst)
        st.set(step='init', message='normalize the clip(s): short side 1080, <= 30 fps, no audio')
        cmd_init(ns(job=job, video=local, slug=req['slug'], start=req['start'], max_dur=req['max_dur'], text=req['text']))
        jsave(J(job, 'request.applied.json'), dict(key=key))
    jst = load_job(job)
    used = sum(x['used_s'] for x in jst['sources'])
    st.set(sources=[dict(alias=x['alias'], used_s=x['used_s']) for x in jst['sources']])
    jsave(J(job, 'texts.json'), {'text': req['text']})
    if not os.path.exists(J(job, 'features.json')):
        st.set(step='prep', message=f'cuts, faces, identities, person matte (~{int(3.6 * used)} s for {used:.0f} s of clip)')
        cmd_prep(ns(job=job))
    if req['fixes']:
        jsave(J(job, 'fixes.json'), req['fixes'])
    elif os.path.exists(J(job, 'fixes.json')):
        os.remove(J(job, 'fixes.json'))
    st.set(step='edit', message='slots -> moments' + (' + cut-out masks + review sheets' if sheets else ''))
    cmd_edit(ns(job=job, split=req.get('split'), no_sheet=not sheets))
    return jload(J(job, 'edit_report.json'))


def sbx_review_info(job, rep, rev):
    """Everything an agent needs to judge the sheets and write fixes, without reading other files."""
    feats = jload(J(job, 'features.json'))
    small = [shrink(J(job, 'qa', f'edit_{k}.jpg'), J(job, 'qa', f'edit_{k}.small.jpg')) for k in ('A', 'B')]
    keep = ('t', 'score', 'notes', 'cx', 'cy', 'zoom', 'w', 'h', 'box', 'y_cut', 'alias')
    picks = {k: {n: {f: p[f] for f in keep if f in p} for n, p in v.items()} for k, v in rep['picks'].items()}
    return dict(rev=rev, sheets=small, warnings=rep['warnings'], heroes=rep['heroes'], people=rep['people'][:4],
                ranges=rep['ranges'], picks=picks,
                sources={a: dict(w=v['w'], h=v['h'], dur=round(v['dur'], 2), cuts=v['cuts'])
                         for a, v in feats['sources'].items()},
                slot_need_s={n: sp['need'] for n, sp in CASTER.SLOTS.items()})


def other_holders(job, me):
    """Stop an older `sandbox` process of this job (a review holder or a stale run) before this one starts."""
    old = jload(J(job, 'status.json'), {}) if os.path.exists(J(job, 'status.json')) else {}
    pid = old.get('pid')
    if not pid or pid == me:
        return
    try:                                 # only ever signal our own `pc.py sandbox` process (pids get reused)
        with open(f'/proc/{int(pid)}/cmdline', 'rb') as f:
            cmd = f.read().replace(b'\0', b' ').decode(errors='replace')
        if 'pc.py' in cmd and ' sandbox ' in cmd:
            try:
                os.killpg(int(pid), 15)          # the stage and all its workers (edit.py, analyze.py, ffmpeg)
            except OSError:
                os.kill(int(pid), 15)
            time.sleep(2)
    except (OSError, ValueError):
        pass


def cmd_sandbox(a):
    try:
        os.setpgrp()                             # own process group: a newer run can stop us with every worker
    except OSError:
        pass
    req_path = os.path.abspath(a.request)
    try:
        raw = json.load(open(req_path))
    except (OSError, ValueError):
        raw = {}
    job = raw.get('job') if isinstance(raw, dict) and isinstance(raw.get('job'), str) else \
        J(os.path.dirname(PC_HOME.rstrip('/')), 'job')
    os.makedirs(job, exist_ok=True)
    # a review holder hands over to a newer run: RELEASE for a polite stop, then SIGTERM for a busy one
    open(J(job, 'RELEASE'), 'w').close()
    time.sleep(3)
    other_holders(job, os.getpid())
    for f in ('RELEASE', 'DONE_ACK', 'status.json'):
        if os.path.exists(J(job, f)):
            os.remove(J(job, f))
    st = Stage(job, a.stage, str(raw.get('run_id', '')) if isinstance(raw, dict) else '')
    lease_end = time.time() + float(raw.get('lease_s', 840) if isinstance(raw, dict) else 840)
    PROGRESS[0] = lambda step, message: st.set(step=step, message=message)

    def heartbeat():                     # elapsed_s / updated move every 10 s even inside long steps
        while True:
            time.sleep(10)
            try:
                st.set()
            except Exception:  # noqa: BLE001
                pass
    import threading
    threading.Thread(target=heartbeat, daemon=True).start()
    try:
        st.set(step='request', message='checking the request')
        mtime = os.path.getmtime(req_path)       # a rewrite during preparation is applied once the sheets are ready
        req = sbx_request(req_path)
        if req['_notes']:
            st.set(notes=req['_notes'])
        if a.stage == 'review':
            rev = int(req.get('rev', 0) or 0)
            rep = sbx_prepare(req, st, sheets=True)
            st.set(state='review_ready', step='review', message='look at review.sheets; to fix, rewrite the request '
                   'with fixes / text and a higher "rev" while this holds', review=sbx_review_info(job, rep, rev))
            first = dict(clips=req['clips'], start=req['start'], max_dur=req['max_dur'])
            while time.time() < lease_end - 5:
                if os.path.exists(J(job, 'RELEASE')):
                    st.closed = True        # a newer run owns status.json now
                    print('review hold released: a newer run took over', flush=True)
                    return
                if os.path.exists(req_path) and os.path.getmtime(req_path) != mtime:
                    time.sleep(1)
                    mtime = os.path.getmtime(req_path)
                    try:
                        req = sbx_request(req_path)
                        if dict(clips=req['clips'], start=req['start'], max_dur=req['max_dur']) != first:
                            die('a hold rewrite may change only "fixes", "text" and "rev"; for another clip, start '
                                'or max_dur start a new review stage (new run_id, empty fixes)')
                        rev = int(req.get('rev', rev + 1) or rev + 1)
                        st.set(state='running', step='re-edit', message=f'request changed (rev {rev}): re-applying')
                        rep = sbx_prepare(req, st, sheets=True)
                        st.set(state='review_ready', step='review', message=f'updated sheets ready (rev {rev})',
                               review=sbx_review_info(job, rep, rev))
                    except SystemExit:
                        # a bad request / fix: report it and keep holding with the last good sheets
                        st.set(state='review_ready', step='review', message='the new request was NOT applied: '
                               + (LAST_ERROR[0] or 'error')[-600:] + ' (fix the request and rewrite it again)')
                time.sleep(2)
            st.set(state='expired', step='review', message='hold ended (lease); run the render stage, it re-prepares '
                   'everything if the sandbox was recycled')
            return
        # ---------------------------------------------------------------- render
        if not str(req.get('upload_url', '')).startswith('https://'):
            die('request: render needs "upload_url" (a new media_upload presigned PUT URL for the mp4)')
        sbx_prepare(req, st, sheets=False)
        for f in os.listdir(J(job, 'qa')):
            if f.startswith('cmp_'):
                os.remove(J(job, 'qa', f))
        st.set(step='render', message=f'795 frames, then 2-pass H.264 + music')
        try:
            cmd_render(ns(job=job, par=None, no_qa=True))
        except SystemExit as e:
            if e.code:
                raise
        st.set(step='qa', message='frame count, size, fps, duration, streams, stray frames + comparison sheets')
        qa_code = do_qa(job)
        qa = jload(J(job, 'qa', 'qa.json'))
        cmps = sorted(f for f in os.listdir(J(job, 'qa')) if re.match(r'cmp_\d\d\.jpg$', f))
        small = [shrink(J(job, 'qa', f), J(job, 'qa', f[:-4] + '.small.jpg'), max_w=1000, max_kb=120) for f in cmps]
        out = qa['video']
        result = dict(file=out, mb=round(os.path.getsize(out) / 1e6, 1), qa_ok=qa['ok'], qa=qa['checks'],
                      cmp_sheets=small, upload_http=None)
        if qa_code != 0:            # nothing is uploaded when QA fails: the same upload_url stays usable
            st.set(state='error', step='qa', message='QA failed (see result.qa); nothing uploaded', result=result)
        else:
            st.set(step='upload', message='PUT the mp4 to the presigned URL')
            ctype = req.get('upload_content_type') or 'video/mp4'
            r = subprocess.run(['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', '-X', 'PUT', '-H',
                                f'Content-Type: {ctype}', '-H', 'If-None-Match: *', '--upload-file', out,
                                req['upload_url']], capture_output=True, text=True)
            result['upload_http'] = r.stdout.strip()
            ok = result['upload_http'] == '200'
            st.set(state='done' if ok else 'error', step='done' if ok else 'upload',
                   message=f'upload HTTP {result["upload_http"]}' + ('' if ok else ' (412 = this upload_url was '
                           'already used: create a new media_upload and upload result.file again)'), result=result)
        hold_end = min(lease_end, time.time() + float(req.get('post_hold_s', 300)))
        while time.time() < hold_end and not os.path.exists(J(job, 'DONE_ACK')) \
                and not os.path.exists(J(job, 'RELEASE')):
            time.sleep(2)                    # keep the host alive so the agent can look at the cmp sheets
    except SystemExit as e:
        if e.code:
            st.set(state='error', message=(LAST_ERROR[0] or f'stopped (exit {e.code})')[-900:])
            sbx_error_hold(job, lease_end)
            raise
    except Exception as e:  # noqa: BLE001 - report every failure through status.json
        st.set(state='error', message=f'{type(e).__name__}: {e}')
        sbx_error_hold(job, lease_end)
        raise


def sbx_error_hold(job, lease_end, hold_s=240):
    """After an error keep the sandbox alive a few minutes (the agent polls every 20-30 s and must be able to read
    status.json and the logs); a newer run (RELEASE) or DONE_ACK ends it at once."""
    end = min(lease_end, time.time() + hold_s)
    while time.time() < end and not os.path.exists(J(job, 'RELEASE')) and not os.path.exists(J(job, 'DONE_ACK')):
        time.sleep(2)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('setup')
    s.add_argument('--sandbox', action='store_true', help='use the host numpy/Pillow/onnxruntime + the pinned opencv wheel')
    s = sub.add_parser('assets')
    s.add_argument('--force', action='store_true', help='re-download and re-verify everything')
    s = sub.add_parser('doctor')
    s.add_argument('job', nargs='?')
    s = sub.add_parser('init')
    s.add_argument('job')
    s.add_argument('--video', action='append', required=True)
    s.add_argument('--slug')
    s.add_argument('--start', type=float, default=0.0)
    s.add_argument('--max-dur', type=float, default=MAX_DUR)
    s.add_argument('--text', default='', help='prompt box (Latin, <= 24 chars); empty = no lettering')
    sub.add_parser('prep').add_argument('job')
    sub.add_parser('qa').add_argument('job')
    sub.add_parser('status').add_argument('job')
    s = sub.add_parser('edit')
    s.add_argument('job')
    s.add_argument('--split', type=float, help='one clip: where phrase B footage starts (s)')
    s.add_argument('--no-sheet', action='store_true')
    s = sub.add_parser('render')
    s.add_argument('job')
    s.add_argument('--par', type=int)
    s.add_argument('--no-qa', action='store_true')
    s = sub.add_parser('sheet')
    s.add_argument('job')
    s.add_argument('--t', required=True)
    s.add_argument('--name', default='sheet')
    s = sub.add_parser('sandbox')
    s.add_argument('stage', choices=('review', 'render'))
    s.add_argument('request')
    s = sub.add_parser('src')
    s.add_argument('job')
    s.add_argument('--alias', default='v0')
    s.add_argument('--t0', type=float, default=0.0)
    s.add_argument('--t1', type=float)
    s.add_argument('--every', type=float, default=0.5)
    a = ap.parse_args()
    if getattr(a, 'max_dur', MAX_DUR) > MAX_DUR:
        a.max_dur = MAX_DUR
    globals()['cmd_' + a.cmd](a)


if __name__ == '__main__':
    main()
