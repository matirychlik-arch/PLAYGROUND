"""Offline Katana smoke: sandbox stack, rr.sh, reference preservation, bundled face model and Chromium.
usage: smoke.py [--require-baked-whisper]"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
SCRIPTS = ('analyze_ref.py', 'assemble.py', 'audio.py', 'compare.py', 'faces.py', 'fetch_ref.py',
           'frames.py', 'ledger.py', 'matte.py', 'textlayers.py', 'comp/render.py')


def run(*args, **kw):
    return subprocess.run([str(a) for a in args], check=True, capture_output=True, text=True, **kw)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--require-baked-whisper', action='store_true')
    args = parser.parse_args()
    import cv2  # noqa: F401
    import librosa  # noqa: F401
    import numpy  # noqa: F401
    import onnxruntime  # noqa: F401
    import PIL  # noqa: F401
    import scipy  # noqa: F401

    for script in SCRIPTS:
        run(sys.executable, HERE / script, '--help')

    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        clip = work / 'clip.mp4'
        run('ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', 'testsrc2=size=640x360:rate=30',
            '-f', 'lavfi', '-i', 'sine=frequency=440:sample_rate=48000', '-t', '2',
            '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', clip)
        env = dict(os.environ, RR_HOME=str(work))
        out = run('bash', '-c', f'source "{HERE}/rr.sh" && rr_ws smoke && echo "W=$W CHROME=$CHROME"',
                  env=env).stdout
        assert 'W=' in out and 'CHROME=/' in out, out
        ws = out.split('W=')[1].split()[0]
        run(sys.executable, HERE / 'fetch_ref.py', ws, clip)
        ref = json.loads((Path(ws) / 'ref' / 'ref.json').read_text())
        assert (Path(ws) / 'ref' / 'ref.mp4').exists(), ref
        # The bundled model resolves without a network download.
        sys.path.insert(0, str(HERE))
        import faces
        assert Path(faces.ensure_model(quiet=True)).parent == HERE / 'models'

    if args.require_baked_whisper:
        from faster_whisper import WhisperModel
        WhisperModel('small', device='cpu', compute_type='int8',
                     download_root='/opt/whisper-models', local_files_only=True)
    print('katana smoke ok')


if __name__ == '__main__':
    os.environ.setdefault('PYTHONDONTWRITEBYTECODE', '1')
    main()
