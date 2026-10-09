#!/usr/bin/env python3
"""Get the reference video into the workspace: W/ref/ref.mp4 + W/ref/ref.json (+ meta.json for page links).

SOURCE can be
  - a page link (Instagram / TikTok / YouTube / X ...): downloaded with yt-dlp; the existing pinned,
    hash-checked Socket install is used if the deployed package is unavailable,
  - a direct media URL (Higgsfield result URL or another authorized HTTPS media URL),
  - a local path inside the sandbox.

Fetch into a staging directory and replace workspace reference files only after successful verification.
ref.mp4 is a legacy canonical filename: its bytes, actual container, codecs, dimensions, timestamps,
color and audio remain exactly those of the acquired source. ffmpeg probes its actual container.
Never crop, tone-map, transcode or normalize the reference master on import. An optional processing
preview must be separate and cannot become the fidelity source. --keep-src retains a duplicate of
downloaded media under its original extension. Local source files are never removed.
ref.json records actual metadata, preservation status and any processing limitations.

Stdlib only, plus ffmpeg/ffprobe.
"""
import argparse
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from fractions import Fraction

PYLIB = os.environ.get("RR_PYLIB", "/home/user/pylib")
PIP_INDEX = "https://socket-firewall.higgsfield.xyz/pypi/simple"
YTDLP_REQUIREMENT = ("yt-dlp==2026.8.19 "
                     "--hash=sha256:1d57897e94c6665a0a6f9bc54b34e584284e32c034ffab3a7df25d8f7b24eedf")
PAGE_HOSTS = ("instagram.com", "tiktok.com", "youtube.com", "youtu.be", "x.com", "twitter.com",
              "vimeo.com", "facebook.com", "fb.watch", "threads.net", "pinterest.", "vk.com", "reddit.com")
MEDIA_EXT = (".mp4", ".mov", ".m4v", ".webm", ".mkv")
OK_PIX = ("yuv420p", "yuvj420p")
HDR_TRC = ("arib-std-b67", "smpte2084")



def fail(msg):
    sys.exit(f"fetch_ref: {msg}")


def _tail(text, n=4):
    lines = [ln for ln in (text or "").strip().splitlines() if ln.strip()]
    return " | ".join(lines[-n:]) or "(no output)"


def run(cmd, what=None, **kw):
    """subprocess.run(check) that exits with a readable message instead of a traceback."""
    try:
        return subprocess.run(cmd, check=True, text=True, capture_output=True, **kw)
    except FileNotFoundError:
        fail(f"required executable unavailable: {cmd[0]}; use an existing authorized processing route")
    except subprocess.CalledProcessError as e:
        fail(f"{what or os.path.basename(cmd[0])} failed (rc={e.returncode}): {_tail(e.stderr or e.stdout)}")


def ensure_ytdlp():
    env = dict(os.environ)
    env["PYTHONPATH"] = PYLIB + os.pathsep + env.get("PYTHONPATH", "")
    probe_ = subprocess.run([sys.executable, "-c", "import yt_dlp"], env=env, capture_output=True)
    if probe_.returncode != 0:
        os.makedirs(PYLIB, exist_ok=True)
        # Pinned and hash-checked, resolved through the Higgsfield Socket firewall, never the public index.
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as req:
            req.write(f"{YTDLP_REQUIREMENT}\n")
        install_env = {key: value for key, value in os.environ.items() if not key.startswith("PIP_")}
        install_env["PIP_CONFIG_FILE"] = os.devnull
        try:
            r = subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--disable-pip-version-check",
                                "--index-url", PIP_INDEX, "--only-binary=:all:", "--no-deps", "--require-hashes",
                                "--target", PYLIB, "-r", req.name], env=install_env, capture_output=True, text=True)
        finally:
            os.unlink(req.name)
        if r.returncode != 0:
            fail("could not install yt-dlp through the package firewall. Use an existing authorized retrieval "
                 "route or an already attached video. Details: " + _tail(r.stderr or r.stdout))
    return env


def is_page(src):
    s = src.lower()
    if not s.startswith("http"):
        return False
    path = s.split("?")[0]
    if path.endswith(MEDIA_EXT):
        return False
    return any(h in s for h in PAGE_HOSTS)


def download_page(src, refdir):
    env = ensure_ytdlp()
    meta = subprocess.run([sys.executable, "-m", "yt_dlp", "--no-playlist", "-j", src],
                          env=env, capture_output=True, text=True)
    if meta.returncode == 0 and meta.stdout.strip():
        try:
            m = json.loads(meta.stdout.splitlines()[0])
        except ValueError:
            m = {}
        keep = {k: m.get(k) for k in ("title", "uploader", "channel", "uploader_id", "description", "duration",
                                      "width", "height", "fps", "track", "artist", "upload_date",
                                      "like_count", "view_count", "webpage_url")}
        with open(os.path.join(refdir, "meta.json"), "w") as f:
            json.dump(keep, f, ensure_ascii=False, indent=1)
    out_tpl = os.path.join(refdir, "src.%(ext)s")
    r = subprocess.run([sys.executable, "-m", "yt_dlp", "--no-playlist", "-f", "bv*+ba/b",
                        "--merge-output-format", "mp4", "--force-overwrites", "--no-simulate",
                        "--print", "after_move:filepath", "-o", out_tpl, src],
                       env=env, capture_output=True, text=True)
    if r.returncode != 0:
        fail("yt-dlp could not access this source. Use another existing authorized retrieval method; "
             "if this exact source remains inaccessible, report the limitation without requesting input. Details: "
             + _tail(r.stderr or r.stdout, 3))
    lines = [ln.strip() for ln in (r.stdout or "").splitlines() if ln.strip()]
    if lines and os.path.isfile(lines[-1]):
        return lines[-1]
    cands = sorted((p for p in glob.glob(os.path.join(glob.escape(refdir), "src.*"))
                    if not p.endswith((".part", ".ytdl"))), key=os.path.getmtime)
    if cands:
        return cands[-1]
    fail("yt-dlp reported success but no file was written")


def download_media(src, refdir):
    ext = os.path.splitext(src.split("?")[0])[1].lower() or ".mp4"
    dst = os.path.join(refdir, "src" + (ext if ext in MEDIA_EXT else ".mp4"))
    part = dst + ".part"
    req = urllib.request.Request(src, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp, open(part, "wb") as f:
            shutil.copyfileobj(resp, f)
    except (urllib.error.URLError, OSError, ValueError) as e:
        if os.path.exists(part):
            os.unlink(part)
        fail(f"download failed for {src.split('?')[0]}: {e}")
    if os.path.getsize(part) == 0:
        os.unlink(part)
        fail(f"download of {src.split('?')[0]} returned 0 bytes")
    os.replace(part, dst)
    return dst


def probe(path):
    p = json.loads(run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format",
                        "-show_streams", path], what="ffprobe").stdout or "{}")
    streams = p.get("streams", [])
    v = next((s for s in streams if s.get("codec_type") == "video"
              and not (s.get("disposition") or {}).get("attached_pic")), None)
    a = next((s for s in streams if s.get("codec_type") == "audio"), None)
    if v is None:
        fail("no video stream in " + path)
    rot = 0
    for sd in v.get("side_data_list", []) or []:
        if "rotation" in sd:
            try:
                rot = int(float(sd["rotation"]))
            except (TypeError, ValueError):
                pass
    try:
        rot = int(float(v.get("tags", {}).get("rotate", rot)))
    except (TypeError, ValueError):
        pass
    cw, ch = int(v["width"]), int(v["height"])
    w, h = (ch, cw) if abs(rot) % 180 == 90 else (cw, ch)

    def _fr(s):
        try:
            f = Fraction(s or "0/1")
            return f if f > 0 else None
        except (ValueError, ZeroDivisionError):
            return None
    rf, af = _fr(v.get("r_frame_rate")), _fr(v.get("avg_frame_rate"))
    fps = af or rf or Fraction(30)
    nb = v.get("nb_frames")
    if not nb or nb == "N/A":
        c = run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0",
                 "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", path], what="ffprobe").stdout.strip()
        nb = c.split(",")[0]
    dur = float(p.get("format", {}).get("duration") or 0)
    return {
        "path": os.path.basename(path), "width": w, "height": h, "coded_width": cw, "coded_height": ch,
        "rotation": rot, "fps": f"{fps.numerator}/{fps.denominator}", "fps_float": round(float(fps), 5),
        "vfr": bool(rf and af and abs(float(rf) - float(af)) > 0.002 * float(af)),
        "nb_frames": int(nb), "duration": round(dur, 4),
        "video_duration": float(v["duration"]) if v.get("duration") not in (None, "N/A") else None,
        "format_name": p.get("format", {}).get("format_name"),
        "vcodec": v.get("codec_name"), "pix_fmt": v.get("pix_fmt"),
        "color_transfer": v.get("color_transfer"), "color_primaries": v.get("color_primaries"),
        "color_space": v.get("color_space"), "color_range": v.get("color_range"),
        "has_audio": a is not None,
        "acodec": a.get("codec_name") if a else None,
        "sample_rate": int(a["sample_rate"]) if a and a.get("sample_rate") else None,
        "channels": a.get("channels") if a else None,
        "audio_duration": float(a["duration"]) if a and a.get("duration") not in (None, "N/A") else None,
        "aspect": f"{w}:{h}",
    }


def normalise(src_path, refdir):
    """Compatibility name: preserve source bytes; never normalize the master."""
    info = probe(src_path)
    dst = os.path.join(refdir, "ref.mp4")
    tmp = os.path.join(refdir, ".ref_tmp.mp4")
    shutil.copyfile(src_path, tmp)
    os.replace(tmp, dst)
    notes = []
    if info.get("vfr"):
        notes.append("Possible VFR source preserved; inspect actual presentation timestamps. "
                     "Constant-rate processing helpers must not flatten its timing.")
    if info.get("color_transfer") in HDR_TRC:
        notes.append("HDR master preserved. Use a verified HDR-capable route; any SDR preview stays separate.")
    if info["coded_width"] % 2 or info["coded_height"] % 2:
        notes.append("Odd source dimensions preserved; do not crop the reference to fit an encoder.")
    if info["vcodec"] not in ("h264", "hevc") or info.get("pix_fmt") not in OK_PIX:
        notes.append("Source codec/pixel format preserved; select a compatible processing route.")
    return dst, {"action": "preserve", "reasons": [], "byte_exact": True}, notes


def main():
    ap = argparse.ArgumentParser(description="Fetch the reference video into W/ref/ref.mp4 and probe it.")
    ap.add_argument("W", help="workspace dir")
    ap.add_argument("source", help="page link, direct media URL, or sandbox path")
    ap.add_argument("--keep-src", action="store_true",
                    help="keep a duplicate downloaded source with its original extension; the master bytes are always preserved")
    a = ap.parse_args()
    refdir = os.path.join(a.W, "ref")
    os.makedirs(refdir, exist_ok=True)
    src = a.source
    # Failed retrieval leaves the previously verified reference intact. Staged data
    # is never consumed as a successful new reference until all probes pass.
    with tempfile.TemporaryDirectory(prefix=".ref-fetch-", dir=os.path.abspath(a.W)) as stage:
        if os.path.exists(src):
            local = os.path.abspath(src)
        elif is_page(src):
            local = download_page(src, stage)
        elif src.startswith(("http://", "https://")):
            local = download_media(src, stage)
        else:
            fail("source not found: " + src)
        staged_ref, how, notes = normalise(local, stage)
        info = probe(staged_ref)
        info["source"] = src.split("?")[0] if src.startswith("http") and not is_page(src) else src
        info["normalise"] = how
        info["notes"] = notes
        downloaded = os.path.dirname(os.path.abspath(local)) == stage
        info["source_file"] = {"name": os.path.basename(local) if downloaded else local,
                               "bytes": os.path.getsize(local), "deleted": downloaded and not a.keep_src,
                               "master_preserved": True}
        with open(os.path.join(stage, "ref.json"), "w", encoding="utf-8") as f:
            json.dump(info, f, indent=1)
        # Keep local input paths intact, even when a caller supplied W/ref/src.*.
        ref = os.path.join(refdir, "ref.mp4")
        os.replace(staged_ref, ref)
        os.replace(os.path.join(stage, "ref.json"), os.path.join(refdir, "ref.json"))
        meta = os.path.join(stage, "meta.json")
        if os.path.isfile(meta):
            os.replace(meta, os.path.join(refdir, "meta.json"))
        elif os.path.isfile(os.path.join(refdir, "meta.json")):
            os.unlink(os.path.join(refdir, "meta.json"))
        if downloaded and a.keep_src:
            shutil.copyfile(local, os.path.join(refdir, os.path.basename(local)))
    print(f"ref: {ref}")
    print(f"  {info['width']}x{info['height']} @ {info['fps']} ({info['fps_float']} fps), "
          f"{info['nb_frames']} frames = {info['video_duration']} s video, audio={info['acodec']} "
          f"{info['sample_rate']} Hz dur={info['audio_duration']}")
    print(f"  {how['action']}" + (f": {'; '.join(how['reasons'])}" if how["reasons"] else ""))
    sf = info["source_file"]
    if sf["deleted"]:
        print(f"  temporary download copy {sf['name']} removed; its identical bytes remain in ref/ref.mp4")
    for n in notes:
        print(f"  NOTE {n}")
    ad, vd = info["audio_duration"], info["video_duration"]
    if ad and vd and abs(ad - vd) > 0.05:
        print("  note: audio and video lengths differ; the edit length is the VIDEO frame count")
    if os.path.exists(os.path.join(refdir, "meta.json")):
        print(f"  meta: {os.path.join(refdir, 'meta.json')}")


if __name__ == "__main__":
    main()
