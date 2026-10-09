#!/usr/bin/env python3
"""compare.py - katana comparison videos and machine QA (stdlib + numpy + ffmpeg, via rrio).

  sbs      [W] --ref R --ours O --out F [--labels "Original|Ours"] [--audio ref|ours|none]
           side-by-side, panels at the same height, frame-synced on the master (default ours: a
           different-fps input is resampled to ours), 80 px label band, even dims, width <= 3840.
  triptych [W] --a R --b G --c O --out F [--labels "Original|Genjutsu|Ours"] [--audio a|b|c|none]
           standard 3-panel layout (same height, width <= 3840, 80 px band, even dims, audio from a = ref).
  sheet    [W] --ref R --ours O (--times t1,t2 | --every SEC | --frames f1,f2 | breakdown) --out JPG
           "ref | ours" pair tiles labelled with frame index and time, JPEG <= 500 KB (several sheets
           out_01.jpg, out_02.jpg ... when there are more pairs than --per-sheet).
  check    [W] --ref R --ours O [--json OUT] [--audio-mode auto|copy|mix] [--expect-border]
           frame count, fps, duration, size, audio MD5 (stream copy), ebur128 I/LRA/TP of both,
           black-bar edge scan, frozen-frame scan -> JSON; exit 0 = no FAIL, 1 = FAIL, 2 = bad input.
           Bars: an edge bar the reference lacks is a FAIL, except when the frame is meant to have one:
           the workspace EDL (W/comp/edl.json, or --edl) declares post.border or a shot's fx.border /
           layers border (the Katana hand-inked frame), or --expect-border is passed. Then bars up to
           --border-max-frac of the side (default 6 %) are a NOTE; a thicker bar or an all-black
           output still FAILs (VERIFIED live 2026-10-08: the Katana post.border ink frame was a false FAIL).
           Audio (D19, --audio-mode auto): an MD5-equal stream passes; audio that is not bit-identical
           but is the reference's own track (same codec/profile, sample rate, channels, integrated
           loudness within +-0.5 LU, duration within 1 frame) passes as "not bit-identical
           (acceptable)"; anything else is a new mix and gets the true-peak rule (<= --max-tp).

With a workspace W: --ref defaults to W/ref/ref.mp4, --ours to the newest W/out/final_v*.mp4, outputs to
W/qa/ (sheet, check) or W/out/ (sbs, triptych). Labels are drawn with ffmpeg drawtext and an existing
TTF (DejaVu/Liberation/Arial/...; --font to choose); without drawtext or a font the rrio bitmap font is
burned in as a PNG band (--bitmap-labels forces it).
"""
from __future__ import annotations

import argparse
import bisect
import glob
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402

import rrio  # noqa: E402

MAX_W = 3840
BAND = 80
GAP = 16
FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/Library/Fonts/Arial.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
]
FONT_GLOBS = [
    "{hf}/katana/scripts/fonts/*Inter*Bold*.ttf",
    "{hf}/katana/scripts/fonts/*.ttf",
    "/usr/share/fonts/**/Montserrat-Bold.ttf",
    "/usr/share/fonts/**/*Sans*Bold*.ttf",
    "/usr/share/fonts/**/*.ttf",
]
_BAD_FILTER_CHARS = set("':\\,;[]=\"")


class CmpError(Exception):
    pass


# ----------------------------------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------------------------------
def even_down(x):
    return max(2, int(x) // 2 * 2)


def find_font(user=None):
    for c in (user, os.environ.get("RR_FONT")):
        if c:
            if os.path.isfile(c):
                return c
            if c == user:
                raise CmpError(f"--font not found: {c}")
    for c in FONT_CANDIDATES:
        if os.path.isfile(c):
            return c
    hf = os.environ.get("HF_WORKFLOWS", "/home/user/.higgsfield/workflows")
    for g in FONT_GLOBS:
        hits = sorted(glob.glob(g.format(hf=hf), recursive=True))
        if hits:
            return hits[0]
    return None


_FILTERS = None


def has_filter(name):
    global _FILTERS
    if _FILTERS is None:
        try:
            r = subprocess.run([rrio.FFMPEG, "-hide_banner", "-filters"], capture_output=True, text=True)
            _FILTERS = r.stdout
        except FileNotFoundError:
            _FILTERS = ""
    return re.search(rf"\s{re.escape(name)}\s", _FILTERS) is not None


_SETPARAMS = None


def bt709_tags():
    """',setparams=...bt709' for the end of a filtergraph: ffmpeg 8 drops -color_primaries/-color_trc on
    filtered frames (the file reads back 'unknown'), so the frames themselves carry the tags. ffmpeg 5.1
    has the same setparams options; a build without them gets '' (the output options still apply there)."""
    global _SETPARAMS
    if _SETPARAMS is None:
        try:
            r = subprocess.run([rrio.FFMPEG, "-hide_banner", "-h", "filter=setparams"], capture_output=True,
                               text=True)
            txt = r.stdout or ""
        except FileNotFoundError:
            txt = ""
        _SETPARAMS = (",setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709"
                      if all(k in txt for k in ("color_primaries", "color_trc", "colorspace")) else "")
    return _SETPARAMS


def display_aspect(p):
    sar = p.get("sar")
    sn, sd = 1, 1
    if sar and ":" in str(sar):
        try:
            sn, sd = (int(x) for x in str(sar).split(":"))
            if sn <= 0 or sd <= 0:
                sn, sd = 1, 1
        except ValueError:
            sn, sd = 1, 1
    return p["w"] * sn / (p["h"] * sd)


def in_matrix(p):
    try:
        return rrio._in_matrix(p)
    except Exception:
        return None


def safe_tmpdir(near):
    """A temp dir whose path is safe inside an ffmpeg filtergraph (no quotes, colons, commas ...)."""
    d = os.path.dirname(os.path.abspath(near))
    for base in (d, None):
        try:
            t = tempfile.mkdtemp(prefix=".cmp_", dir=base)
        except OSError:
            continue
        if not (set(t) & _BAD_FILTER_CHARS):
            return t
        shutil.rmtree(t, ignore_errors=True)
    raise CmpError("no temp dir with a filtergraph-safe path")


def latest_final(W):
    out = os.path.join(W, "out")
    cands = [p for p in glob.glob(os.path.join(out, "*.mp4"))
             if not re.search(r"compare|triptych|sbs|pairs|_cmp", os.path.basename(p), re.I)]
    if not cands:
        return None
    vers = []
    for p in cands:
        m = re.search(r"final_v(\d+)", os.path.basename(p))
        vers.append((int(m.group(1)) if m else -1, os.path.getmtime(p), p))
    vers.sort()
    return vers[-1][2]


def ws_paths(a, ref_attr="ref", ours_attr="ours"):
    W = os.path.abspath(a.W) if getattr(a, "W", None) else None
    if W and not os.path.isdir(W):
        raise CmpError(f"workspace not found: {W}")
    ref = getattr(a, ref_attr, None) or (os.path.join(W, "ref", "ref.mp4") if W else None)
    ours = getattr(a, ours_attr, None) or (latest_final(W) if W else None)
    for nm, p in ((ref_attr, ref), (ours_attr, ours)):
        if not p:
            raise CmpError(f"--{nm} is required (or give a workspace W)")
        if not os.path.isfile(p):
            raise CmpError(f"{nm} not found: {p}")
    return W, ref, ours


def ff_cmd(args):
    return [rrio.FFMPEG, "-hide_banner", "-nostdin", "-loglevel", "error", "-y", *map(str, args)]


def run(cmd):
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0:
        raise CmpError("ffmpeg failed: " + r.stderr.decode("utf-8", "replace")[-1500:])
    return r


def probe_v(path, count=True):
    p = rrio.probe(path, count=count)
    if not p.get("has_video"):
        raise CmpError(f"{path}: no video stream")
    if not p.get("fps"):
        raise CmpError(f"{path}: unknown frame rate")
    return p


# ----------------------------------------------------------------------------------------------------
# panels (sbs / triptych)
# ----------------------------------------------------------------------------------------------------
def panel_layout(infos, height, max_w, gap):
    aspects = [display_aspect(p) for p in infos]
    k = len(infos)
    H = even_down(height)
    widths = [even_down(round(H * a)) for a in aspects]
    total = sum(widths) + gap * (k - 1)
    if total > max_w:
        H = even_down((max_w - gap * (k - 1)) / sum(aspects))
        widths = [even_down(H * a) for a in aspects]
        total = sum(widths) + gap * (k - 1)
        while total > max_w and H > 2:  # rounding safety
            H -= 2
            widths = [even_down(H * a) for a in aspects]
            total = sum(widths) + gap * (k - 1)
    return H, widths, total + (total % 2)


def bitmap_band(labels, widths, gap, band, total_w):
    img = np.zeros((band, total_w, 3), np.uint8)
    x0 = 0
    for lab, w in zip(labels, widths):
        scale = max(1, int(band * 0.45 / 7))
        while scale > 1 and rrio.text_size(lab, scale, pad=0)[0] > w - 8:
            scale -= 1
        tw, th = rrio.text_size(lab, scale, pad=0)
        rrio.draw_text(img, lab, x0 + (w - tw) // 2, (band - th) // 2, scale, (255, 255, 255), None)
        x0 += w + gap
    return img


def label_fs(band):
    return int(band * 0.5)


def label_baseline(band, fs):
    """Baseline y that centres cap-height text (~0.72 em) in the band."""
    return int(round(band / 2 + 0.36 * fs))


def pil_band(labels, widths, gap, band, total_w, font_path):
    """Label band rendered with Pillow + a TTF (exact shared baseline). Raises when PIL is missing."""
    from PIL import Image, ImageDraw, ImageFont  # optional dependency (sandbox has Pillow)
    img = Image.new("RGB", (total_w, band), (0, 0, 0))
    d = ImageDraw.Draw(img)
    fs0 = label_fs(band)
    base = label_baseline(band, fs0)
    x0 = 0
    for lab, w in zip(labels, widths):
        fs = fs0
        f = ImageFont.truetype(font_path, fs)
        while fs > 12 and f.getlength(lab) > w - 8:
            fs -= 2
            f = ImageFont.truetype(font_path, fs)
        d.text((x0 + w / 2.0, base), lab, font=f, fill=(255, 255, 255), anchor="ms")
        x0 += w + gap
    return np.asarray(img, dtype=np.uint8).copy()


_DT_YALIGN = None


def drawtext_has_yalign():
    global _DT_YALIGN
    if _DT_YALIGN is None:
        try:
            r = subprocess.run([rrio.FFMPEG, "-hide_banner", "-h", "filter=drawtext"], capture_output=True, text=True)
            _DT_YALIGN = "y_align" in (r.stdout or "")
        except FileNotFoundError:
            _DT_YALIGN = False
    return _DT_YALIGN


def pick_label_engine(engine, font):
    """-> (engine, font_path): pil | drawtext | bitmap (auto: Pillow, then drawtext, then bitmap)."""
    if engine == "bitmap":
        return "bitmap", None
    f = find_font(font)
    if not f:
        if engine in ("pil", "drawtext"):
            raise CmpError(f"--label-engine {engine} needs a TTF font (none found; pass --font)")
        return "bitmap", None
    if engine in ("auto", "pil"):
        try:
            import PIL.ImageFont  # noqa: F401
            return "pil", f
        except ImportError:
            if engine == "pil":
                raise CmpError("--label-engine pil: Pillow is not installed")
    if has_filter("drawtext"):
        return "drawtext", f
    if engine == "drawtext":
        raise CmpError("this ffmpeg has no drawtext filter")
    return "bitmap", None


def render_panels(inputs, labels, out, master=0, audio=None, height=None, max_w=MAX_W, band=BAND, gap=GAP,
                  crf=20, preset="medium", font=None, bitmap=False, engine="auto"):
    t0 = time.time()
    k = len(inputs)
    if len(labels) != k:
        raise CmpError(f"{k} inputs but {len(labels)} labels")
    infos = [probe_v(p, count=(i == master)) for i, p in enumerate(inputs)]
    m = infos[master]
    F = Fraction(m["fps"])
    N = int(m["nb_frames"])
    if N <= 0:
        raise CmpError(f"{inputs[master]}: no frames")
    if height is None:
        height = min(1080, max(p["h"] for p in infos))
    H, widths, total_w = panel_layout(infos, height, max_w, gap)
    ext_gap = total_w - (sum(widths) + gap * (k - 1))  # 0 or 1 (odd total fixed on the right)
    tmp = safe_tmpdir(out)
    try:
        mode, font_src = pick_label_engine("bitmap" if bitmap else engine, font)
        font_path = None
        if mode == "drawtext":
            font_path = os.path.join(tmp, "font" + os.path.splitext(font_src)[1].lower())
            try:
                os.symlink(font_src, font_path)
            except OSError:
                shutil.copyfile(font_src, font_path)
        fr = f"{F.numerator}/{F.denominator}"
        idx_pts = f"setpts=N*{F.denominator}/{F.numerator}/TB"
        # every panel ends on the SAME time base (1/F, pts = frame index): hstack's framesync otherwise
        # mixes time bases (fps filter 1/F vs the mp4 timescale) and emits extra frames
        common_tb = f"settb={F.denominator}/{F.numerator},setpts=N"
        parts = []
        for i, p in enumerate(infos):
            ch = []
            Fi = Fraction(p["fps"])
            if Fi == F and not p.get("vfr"):
                ch.append(idx_pts)
            else:
                ch += ["setpts=PTS-STARTPTS", f"fps={fr}"]
            mx = in_matrix(p)
            sc = f"scale={widths[i]}:{H}:flags=bicubic"
            if mx:
                sc += f":in_color_matrix={mx}:out_color_matrix=bt709"
            sc += ":out_range=tv"
            ch += [sc, "setsar=1", "format=yuv420p", f"tpad=stop_mode=clone:stop={N + 2}",
                   f"trim=end_frame={N}", common_tb]
            pad_r = gap if i < k - 1 else ext_gap
            if pad_r:
                ch.append(f"pad=iw+{pad_r}:ih:0:0:black")
            parts.append(f"[{i}:v]" + ",".join(ch) + f"[p{i}]")
        stack_in = "".join(f"[p{i}]" for i in range(k))
        parts.append(f"{stack_in}hstack=inputs={k}[st]")
        extra_inputs = []
        band_img = None
        if mode == "pil":
            try:
                band_img = pil_band(labels, widths, gap, band, total_w, font_src)
            except Exception as ex:  # any Pillow problem: fall back, never fail the comparison
                print(f"compare: Pillow labels failed ({ex}); falling back", file=sys.stderr)
                mode = "drawtext" if has_filter("drawtext") else "bitmap"
                if mode == "drawtext":
                    font_path = os.path.join(tmp, "font" + os.path.splitext(font_src)[1].lower())
                    if not os.path.exists(font_path):
                        shutil.copyfile(font_src, font_path)
        if mode == "drawtext":
            fs = label_fs(band)
            # each drawtext instance measures only its own glyphs, so y_align=text/font give every label a
            # different baseline; y_align=baseline (ffmpeg >= 6.1) pins them all to one line. ffmpeg 5.1
            # has no y_align: best effort with the instance ascent (the sandbox uses Pillow instead).
            base = label_baseline(band, fs)
            ypos = f"{base}:y_align=baseline" if drawtext_has_yalign() else f"{base}-max_glyph_a"
            dts = []
            x0 = 0
            for i, (lab, w) in enumerate(zip(labels, widths)):
                tf = os.path.join(tmp, f"label{i}.txt")
                with open(tf, "w", encoding="utf-8") as fh:
                    fh.write(lab)
                fsi = fs
                est_w = 0.62 * fsi * max(1, len(lab))
                if est_w > w - 8:
                    fsi = max(12, int(fs * (w - 8) / est_w))
                dts.append(f"drawtext=fontfile='{font_path}':textfile='{tf}':expansion=none:fontsize={fsi}:"
                           f"fontcolor=white:x={x0}+({w}-text_w)/2:y={ypos}")
                x0 += w + gap
            parts.append(f"[st]pad=iw:ih+{band}:0:{band}:black," + ",".join(dts) + bt709_tags() + "[v]")
        else:
            band_png = os.path.join(tmp, "band.png")
            if band_img is None:
                band_img = bitmap_band(labels, widths, gap, band, total_w)
            rrio.write_image(band_png, band_img)
            extra_inputs = ["-loop", "1", "-framerate", fr, "-i", band_png]
            parts.append(f"[{k}:v]scale=iw:ih:out_color_matrix=bt709:out_range=tv,format=yuv420p,setsar=1,"
                         f"trim=end_frame={N},{common_tb}[band]")
            parts.append("[band][st]vstack=inputs=2" + bt709_tags() + "[v]")
        vdur = N / float(F)
        maps = ["-map", "[v]"]
        audio_info = {"source": None}
        a_args = []
        if audio is not None:
            ai = infos[audio]
            if ai.get("has_audio"):
                ad = ai.get("audio_duration") or ai.get("format_duration") or 0
                if ad <= vdur + 0.5:
                    maps += ["-map", f"{audio}:a:0"]
                    a_args = ["-c:a", "copy"]
                    audio_info = {"source": inputs[audio], "mode": "stream copy", "duration": ad}
                else:
                    parts.append(f"[{audio}:a:0]atrim=end={vdur:.6f},asetpts=PTS-STARTPTS[a]")
                    maps += ["-map", "[a]"]
                    a_args = ["-c:a", "aac", "-b:a", "192k"]
                    audio_info = {"source": inputs[audio], "mode": f"trimmed to {vdur:.3f} s, AAC 192k",
                                  "duration": vdur}
            else:
                audio_info = {"source": inputs[audio], "mode": "none (input has no audio)"}
        # timestamps are exact N/F from the graph (trim limits video to N frames): passthrough, no -r, no
        # -frames:v (cfr pads frames to the audio end; -frames:v cuts the audio tail and changes its MD5)
        fps_mode = rrio._passthrough()
        ins = []
        for p in inputs:
            ins += ["-i", p]
        part = out + ".part"
        cmd = ff_cmd(ins + extra_inputs + ["-filter_complex", ";".join(parts)] + maps +
                     ["-c:v", "libx264", "-preset", preset, "-crf", str(crf), "-pix_fmt", "yuv420p",
                      "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
                      "-color_range", "tv", *fps_mode] + a_args +
                     ["-movflags", "+faststart", "-f", "mp4", part])
        os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
        try:
            run(cmd)
        except CmpError:
            if os.path.exists(part):
                os.unlink(part)
            raise
        os.replace(part, out)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    po = rrio.probe(out, count=True)
    res = {"out": os.path.abspath(out), "w": po["w"], "h": po["h"], "frames": po["nb_frames"],
           "fps": po["fps_str"], "duration": po["duration"], "bytes": po["size_bytes"],
           "master": inputs[master], "master_frames": N, "panel_h": H, "panel_w": widths, "band": band,
           "gap": gap, "labels": labels, "label_mode": mode, "font": font_src if mode in ("drawtext", "pil") else None,
           "audio": audio_info, "inputs": [{"path": p, "w": i["w"], "h": i["h"], "fps": i["fps_str"],
                                            "frames": i["nb_frames"]} for p, i in zip(inputs, infos)],
           "secs": round(time.time() - t0, 2)}
    if po["nb_frames"] != N:
        res["warning"] = f"output has {po['nb_frames']} frames, master has {N}"
    return res


def parse_labels(s, k, default):
    if not s:
        return default
    labs = [x.strip() for x in s.split("|")]
    if len(labs) != k:
        raise CmpError(f"--labels needs {k} labels separated by '|', got {len(labs)}")
    return labs


def cmd_sbs(a):
    W, ref, ours = ws_paths(a)
    out = a.out or (os.path.join(W, "out", "compare.mp4") if W else None)
    if not out:
        raise CmpError("--out is required")
    labels = parse_labels(a.labels, 2, ["Original", "Ours"])
    master = 0 if a.master == "ref" else 1
    audio = {"ref": 0, "ours": 1, "none": None}[a.audio]
    res = render_panels([ref, ours], labels, out, master=master, audio=audio, height=a.height, max_w=a.max_w,
                        band=a.band, gap=a.gap, crf=a.crf, preset=a.preset, font=a.font, bitmap=a.bitmap_labels,
                        engine=a.label_engine)
    print(json.dumps(rrio.jsonable(res)))
    return 0 if "warning" not in res else 1


def cmd_triptych(a):
    W = os.path.abspath(a.W) if a.W else None
    A = a.a or (os.path.join(W, "ref", "ref.mp4") if W else None)
    C = a.c or (latest_final(W) if W else None)
    if not (A and a.b and C):
        raise CmpError("--a (original), --b (Genjutsu raw) and --c (ours) are required (W fills --a and --c)")
    for nm, p in (("a", A), ("b", a.b), ("c", C)):
        if not os.path.isfile(p):
            raise CmpError(f"--{nm} not found: {p}")
    out = a.out or (os.path.join(W, "out", "triptych.mp4") if W else None)
    if not out:
        raise CmpError("--out is required")
    labels = parse_labels(a.labels, 3, ["Original", "Genjutsu", "Ours"])
    master = {"a": 0, "b": 1, "c": 2, "ref": 0, "ours": 2}[a.master]
    audio = {"a": 0, "b": 1, "c": 2, "ref": 0, "ours": 2, "none": None}[a.audio]
    res = render_panels([A, a.b, C], labels, out, master=master, audio=audio, height=a.height, max_w=a.max_w,
                        band=a.band, gap=a.gap, crf=a.crf, preset=a.preset, font=a.font, bitmap=a.bitmap_labels,
                        engine=a.label_engine)
    print(json.dumps(rrio.jsonable(res)))
    return 0 if "warning" not in res else 1


# ----------------------------------------------------------------------------------------------------
# sheet
# ----------------------------------------------------------------------------------------------------
def _ints(s):
    return [int(x) for x in str(s).replace(";", ",").split(",") if x.strip() != ""]


def _floats(s):
    return [float(x) for x in str(s).replace(";", ",").split(",") if x.strip() != ""]


def breakdown_frames(W):
    bd_path = os.path.join(W, "analysis", "breakdown.json")
    if not os.path.isfile(bd_path):
        return None
    bd = rrio.load_json(bd_path)
    fr = set()
    for c in bd.get("cuts") or []:
        try:
            f0, f1 = int(c["f0"]), int(c["f1"])
        except (KeyError, TypeError, ValueError):
            continue
        fr.update([f0 - 1, f0, (f0 + f1) // 2, f1])
    for t in bd.get("trick_frames") or []:
        try:
            fr.add((int(t[0]) + int(t[1])) // 2)
        except (TypeError, ValueError, IndexError):
            pass
    for f in ((bd.get("look") or {}).get("crop_frames") or []):
        try:
            fr.add(int(f))
        except (TypeError, ValueError):
            pass
    return sorted(x for x in fr if x >= 0)


def make_pair(ref_img, ours_img, half_w, ph, sep=4):
    pair = np.zeros((ph, half_w * 2 + sep, 3), np.uint8)
    pair[:, half_w:half_w + sep] = 255
    for k, im in enumerate((ref_img, ours_img)):
        x = 0 if k == 0 else half_w + sep
        if im is None:
            tile = np.full((ph, half_w, 3), 40, np.uint8)
            rrio.draw_text(tile, "N/A", 4, ph // 2 - 7, 2, (200, 200, 200), None)
        else:
            tile = rrio.fit_into(im, half_w, ph, (0, 0, 0))
        pair[:, x:x + half_w] = tile
        s = 2 if half_w >= 160 else 1
        rrio.draw_text(pair, "REF" if k == 0 else "OURS", x + 3, 3, s, (255, 255, 0), (0, 0, 0))
    return pair


def cmd_sheet(a):
    W, ref, ours = ws_paths(a)
    pr, po = probe_v(ref), probe_v(ours)
    Fr, Fo = Fraction(pr["fps"]), Fraction(po["fps"])
    No, Nr = int(po["nb_frames"]), int(pr["nb_frames"])
    tr, to = rrio.frame_timestamps(ref, pr), rrio.frame_timestamps(ours, po)
    src = None
    if a.frames:
        fo = _ints(a.frames)
        src = "frames"
    elif a.times:
        fo = [max(0, bisect.bisect_right(to["relative_pts"], t) - 1) for t in _floats(a.times)]
        src = "times"
    elif a.every:
        n = int(math.floor(to["duration_s"] / a.every + 1e-9)) + 1
        fo = [max(0, bisect.bisect_right(to["relative_pts"], k * a.every) - 1) for k in range(n)]
        src = f"every {a.every}s"
    else:
        fo = breakdown_frames(W) if W else None
        src = "breakdown"
        if not fo:
            fo = [int(round(x)) for x in np.linspace(0, No - 1, 12)]
            src = "12 evenly spaced"
    fo = sorted(set(min(max(0, f), No - 1) for f in fo)) if a.sort else [min(max(0, f), No - 1) for f in fo]
    if not fo:
        raise CmpError("no frames selected")
    # Match actual presentation intervals, including VFR holds and the final frame.
    fr_map = []
    for f in fo:
        end = to["relative_pts"][f + 1] if f + 1 < No else to["duration_s"]
        if end is None or tr["duration_s"] is None:
            raise CmpError("final frame endpoint unavailable; cannot align a complete pair sheet")
        t = (to["relative_pts"][f] + end) / 2
        r = bisect.bisect_right(tr["relative_pts"], t) - 1
        fr_map.append(r if 0 <= r < Nr and t < tr["duration_s"] else None)
    crop = tuple(_ints(a.crop)) if a.crop else None
    crop_r = tuple(_ints(a.crop_ref)) if a.crop_ref else crop
    crop_o = tuple(_ints(a.crop_ours)) if a.crop_ours else crop
    portrait = (crop_o[3] > crop_o[2]) if crop_o else po["h"] > po["w"]
    ppr = a.pairs_per_row or (4 if portrait else 2)
    gap = 12  # wider than the 4 px white separator inside a pair, so pairs read as units
    tile_w = (a.max_w - (ppr + 1) * gap) // ppr
    sep = 4
    half_w = (tile_w - sep) // 2
    ar_r = (crop_r[3] / crop_r[2]) if crop_r else pr["h"] / pr["w"]
    ar_o = (crop_o[3] / crop_o[2]) if crop_o else po["h"] / po["w"]
    ph = max(2, int(round(half_w * max(ar_r, ar_o))))
    dec_w_r = min((crop_r[2] if crop_r else pr["w"]), half_w * 2)
    dec_w_o = min((crop_o[2] if crop_o else po["w"]), half_w * 2)
    ref_frames = rrio.read_frames_at(ref, [r for r in fr_map if r is not None], scale_w=dec_w_r, crop=crop_r,
                                     info=pr, strict=False)
    rmap = dict(zip([r for r in fr_map if r is not None], ref_frames))
    ours_frames = rrio.read_frames_at(ours, fo, scale_w=dec_w_o, crop=crop_o, info=po, strict=False)
    pairs, labels = [], []
    for f, r, oi in zip(fo, fr_map, ours_frames):
        ri = rmap.get(r) if r is not None else None
        pairs.append(make_pair(ri, oi, half_w, ph, sep))
        lab = f"f{f} {to['relative_pts'][f]:.2f}s"
        if r != f:
            lab += f" r{r if r is not None else '-'}"
        labels.append(lab)
    out = a.out or (os.path.join(W, "qa", "pairs.jpg") if W else None)
    if not out:
        raise CmpError("--out is required")
    per = max(1, a.per_sheet)
    nsheets = (len(pairs) + per - 1) // per
    stem, ext = os.path.splitext(out)
    ext = ext or ".jpg"
    results = []
    for s in range(nsheets):
        path = out if nsheets == 1 else f"{stem}_{s + 1:02d}{ext}"
        chunk = slice(s * per, (s + 1) * per)
        title = (f"REF {pr['w']}x{pr['h']} {pr['fps_str']} {Nr}f | OURS {po['w']}x{po['h']} {po['fps_str']} "
                 f"{No}f" + (f"  [{s + 1}/{nsheets}]" if nsheets > 1 else ""))
        r = rrio.tile_sheet(pairs[chunk], labels[chunk], cols=ppr, out_path=path, tile_w=tile_w,
                            max_bytes=a.max_bytes, max_w=a.max_w, title=title, gap=gap)
        r["frames"] = fo[chunk]
        r["ref_frames"] = fr_map[chunk]
        results.append(r)
    print(json.dumps(rrio.jsonable({"sheets": results, "pairs": len(pairs), "source": src})))
    return 0


# ----------------------------------------------------------------------------------------------------
# check
# ----------------------------------------------------------------------------------------------------
def audio_md5(path):
    r = subprocess.run([rrio.FFMPEG, "-hide_banner", "-nostdin", "-v", "error", "-i", path, "-map", "0:a:0",
                        "-c", "copy", "-f", "md5", "-"], capture_output=True, text=True)
    m = re.search(r"MD5=([0-9a-f]{32})", r.stdout or "")
    return m.group(1) if m else None


def loudness(path):
    r = subprocess.run([rrio.FFMPEG, "-hide_banner", "-nostdin", "-nostats", "-i", path, "-map", "0:a:0",
                        "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True)
    txt = r.stderr or ""
    k = txt.rfind("Summary:")
    if k < 0:
        return None
    s = txt[k:]

    def grab(label):
        m = re.search(rf"{label}:\s*(-?inf|-?\d+(?:\.\d+)?)", s)
        if not m:
            return None
        v = m.group(1)
        return None if "inf" in v else float(v)

    return {"I_lufs": grab("I"), "LRA_lu": grab("LRA"), "TP_dbtp": grab("Peak")}


def audio_stream_info(path):
    """First audio stream: codec, profile, sample rate, channels, layout, duration (s) via ffprobe; None
    without audio. The duration falls back to the container's when the stream has none (mkv/webm)."""
    r = subprocess.run([rrio.FFPROBE, "-v", "error", "-select_streams", "a:0", "-show_entries",
                        "stream=codec_name,profile,sample_rate,channels,channel_layout,duration,start_time:"
                        "format=duration", "-of", "json", path], capture_output=True, text=True)
    try:
        j = json.loads(r.stdout or "{}")
    except ValueError:
        return None
    st = (j.get("streams") or [None])[0]
    if not st:
        return None

    def num(v, cast=float):
        try:
            return cast(v)
        except (TypeError, ValueError):
            return None

    dur = num(st.get("duration"))
    return {"codec": st.get("codec_name"), "profile": st.get("profile"),
            "sample_rate": num(st.get("sample_rate"), int), "channels": num(st.get("channels"), int),
            "channel_layout": st.get("channel_layout"),
            "duration": dur if dur is not None else num((j.get("format") or {}).get("duration")),
            "start_time": num(st.get("start_time"))}


def audio_reuse_match(ai_r, ai_o, ld_r, ld_o, fps, tol_lu=0.5):
    """D19: is ours' audio the reference's own track even though it is not bit-identical (a re-mux or a
    re-encode of the same audio)? Every criterion must hold: codec + profile, sample rate, channels (and
    layout when both name one), integrated loudness within tol_lu, stream duration within one video frame.
    -> (ok, [{"name", "ok", "detail"}])."""
    crit = []

    def add(name, ok, detail):
        crit.append({"name": name, "ok": bool(ok), "detail": detail})

    ai_r, ai_o = ai_r or {}, ai_o or {}
    if not ai_r or not ai_o:
        add("stream", False, "no audio stream info")
        return False, crit
    add("codec", ai_r.get("codec") and ai_o.get("codec") == ai_r.get("codec")
        and (ai_o.get("profile") or None) == (ai_r.get("profile") or None),
        f"{ai_o.get('codec')}/{ai_o.get('profile')} vs ref {ai_r.get('codec')}/{ai_r.get('profile')}")
    add("sample_rate", ai_r.get("sample_rate") and ai_o.get("sample_rate") == ai_r.get("sample_rate"),
        f"{ai_o.get('sample_rate')} Hz vs ref {ai_r.get('sample_rate')} Hz")
    lay_r, lay_o = ai_r.get("channel_layout"), ai_o.get("channel_layout")

    def ch(ai, lay):
        return f"{ai.get('channels')} ch" + (f" {lay}" if lay else "")

    add("channels", ai_r.get("channels") and ai_o.get("channels") == ai_r.get("channels")
        and (not lay_r or not lay_o or lay_r == lay_o), f"{ch(ai_o, lay_o)} vs ref {ch(ai_r, lay_r)}")
    i_r, i_o = (ld_r or {}).get("I_lufs"), (ld_o or {}).get("I_lufs")
    if i_r is None or i_o is None:
        add("loudness", False, f"integrated loudness not measured (ours {i_o}, ref {i_r})")
    else:
        add("loudness", abs(i_o - i_r) <= tol_lu + 1e-9,
            f"I {i_o} vs ref {i_r} LUFS (diff {abs(i_o - i_r):.1f} LU, limit {tol_lu:g})")
    d_r, d_o = ai_r.get("duration"), ai_o.get("duration")
    frame = 1.0 / float(fps) if fps else 0.0
    if d_r is None or d_o is None:
        add("duration", False, f"audio duration unknown (ours {d_o}, ref {d_r})")
    else:
        add("duration", abs(d_o - d_r) <= frame + 1e-4,
            f"{d_o:.4f} s vs ref {d_r:.4f} s (diff {abs(d_o - d_r) * 1000:.1f} ms, limit 1 frame "
            f"{frame * 1000:.1f} ms)")
    return all(c["ok"] for c in crit), crit


def bar_scan(path, info, samples=24, thr=24, frac=0.98, need=0.9):
    """Dark bars at the frame edges (px in display size), consistent over sampled frames."""
    n = int(info["nb_frames"])
    idx = sorted(set(int(round(x)) for x in np.linspace(0, max(0, n - 1), min(samples, max(1, n)))))
    sw = min(int(info["w"]), 2160)  # full resolution up to 4K wide: bar edges are exact pixels
    frames = [f for f in rrio.read_frames_at(path, idx, scale_w=sw, gray=True, info=info, strict=False)
              if f is not None]
    if not frames:
        return None
    st = np.stack(frames)
    dark = st < thr
    rows = (dark.mean(axis=2) >= frac).mean(axis=0) >= need
    cols = (dark.mean(axis=1) >= frac).mean(axis=0) >= need
    h, w = st.shape[1:]

    def run_len(v):
        k = 0
        for x in v:
            if not x:
                break
            k += 1
        return k

    sy, sx = info["h"] / h, info["w"] / w
    res = {"top": run_len(rows) * sy, "bottom": run_len(rows[::-1]) * sy,
           "left": run_len(cols) * sx, "right": run_len(cols[::-1]) * sx,
           "all_dark": bool(rows.all()), "sampled": len(frames)}
    return {k: (round(v, 1) if isinstance(v, float) else v) for k, v in res.items()}


BORDER_FX = ("border",)


def declared_border(W, edl=None):
    """Where the compositor EDL asks for an intentional frame edge (engine.js `border`, final phase): post.border,
    a shot's fx.border or a shot layer of type border. -> list of places ([] = none, no EDL or unreadable)."""
    p = edl if edl else (os.path.join(W, "comp", "edl.json") if W else None)
    if p and not os.path.isabs(p) and W and not os.path.isfile(p):
        p = os.path.join(W, p)
    if not p or not os.path.isfile(p):
        return []
    try:
        E = rrio.load_json(p)
    except (ValueError, OSError):
        return []
    if not isinstance(E, dict):
        return []

    def on(v):
        return v is not None and v is not False and v != 0

    where = []
    post = E.get("post")
    if isinstance(post, dict):
        where += [f"post.{k}" for k in BORDER_FX if on(post.get(k))]
    for i, sh in enumerate(E.get("shots") or []):
        if not isinstance(sh, dict):
            continue
        fx = sh.get("fx")
        if isinstance(fx, dict):
            where += [f"shots[{i}].fx.{k}" for k in BORDER_FX if on(fx.get(k))]
        for lay in sh.get("layers") or []:
            if isinstance(lay, dict) and lay.get("type") in BORDER_FX:
                where.append(f"shots[{i}].layers.{lay['type']}")
    if len(where) > 4:
        where = where[:3] + [f"+{len(where) - 3} more"]
    rel = os.path.relpath(p, W) if W and os.path.abspath(p).startswith(os.path.abspath(W) + os.sep) else p
    return [f"{w} in {rel}" for w in where]


def motion_profile(path, info, w=64):
    prev = None
    diffs = []
    for _, f in rrio.read_frames(path, scale_w=w, gray=True, info=info):
        f = f.astype(np.float32)
        if prev is not None:
            diffs.append(float(np.abs(f - prev).mean()))
        prev = f
    return np.asarray(diffs, np.float32)


def frozen_scan(d_ours, d_ref, fo, fr, still=0.3, moving=1.0, min_run=None, ref_frac=0.3):
    """Held runs in ours (consecutive near-zero diffs) where the reference moves in the same span."""
    fo, fr = float(fo), float(fr)
    if min_run is None:
        min_run = max(3, int(math.ceil(fo / 8)))
    frozen = d_ours < still
    runs = []
    i, n = 0, len(frozen)
    while i < n:
        if frozen[i]:
            j = i
            while j < n and frozen[j]:
                j += 1
            runs.append((i, j))  # diffs i..j-1 -> frames i..j held
            i = j
        else:
            i += 1
    flagged, held_total = [], 0
    for i, j in runs:
        L = j - i + 1
        if L < min_run:
            continue
        held_total += L
        a = int(math.floor((i + 0.5) / fo * fr))
        b = int(math.floor((j + 0.5) / fo * fr))
        if d_ref is None or a >= len(d_ref):
            continue
        seg = d_ref[a:min(b, len(d_ref))]
        changes = int((seg > moving).sum())
        span = max(1, len(seg))
        if changes >= 2 and changes / span >= ref_frac:
            flagged.append({"f0": i, "f1": j, "frames": L, "t0": round(i / fo, 3), "t1": round(j / fo, 3),
                            "ref_f0": a, "ref_f1": b, "ref_changes": changes})
    return {"min_run": min_run, "held_runs": len([1 for i, j in runs if j - i + 1 >= min_run]),
            "held_frames": held_total, "flagged": flagged,
            "unique_ratio": round(float((d_ours >= still).mean()), 3) if len(d_ours) else None}


def cmd_check(a):
    W, ref, ours = ws_paths(a)
    t0 = time.time()
    pr, po = probe_v(ref, count=True), probe_v(ours, count=True)
    expect = {"frames": pr["nb_frames"], "fps": pr["fps_str"], "w": pr["w"], "h": pr["h"], "source": "ref"}
    if W:
        bd_path = os.path.join(W, "analysis", "breakdown.json")
        if os.path.isfile(bd_path):
            try:
                fl = rrio.load_json(bd_path).get("format_lock") or {}
                if fl.get("frames"):
                    expect.update(frames=int(fl["frames"]), source="breakdown.format_lock")
                if fl.get("fps"):
                    expect["fps"] = rrio.fps_str(rrio.parse_fps(fl["fps"]))
                if fl.get("width") and fl.get("height"):
                    expect.update(w=int(fl["width"]), h=int(fl["height"]))
            except (ValueError, TypeError, OSError):
                pass
    if a.expect_frames:
        expect.update(frames=a.expect_frames, source="--expect-frames")
    if a.expect_size:
        w_, h_ = (int(x) for x in a.expect_size.lower().split("x"))
        expect.update(w=w_, h=h_)
    checks = []

    def add(cid, status, detail, **kw):
        d = {"id": cid, "status": status, "detail": detail}
        d.update(kw)
        checks.append(d)

    timing_r = timing_o = None
    try:
        timing_r, timing_o = rrio.frame_timestamps(ref, pr), rrio.frame_timestamps(ours, po)
        rp, op = timing_r["relative_pts"], timing_o["relative_pts"]
        tol = max(timing_r["tolerance_s"], timing_o["tolerance_s"])
        mismatches = [i for i, (r, o) in enumerate(zip(rp, op)) if abs(r - o) > tol]
        endpoint_ok = (timing_r["duration_s"] is not None and timing_o["duration_s"] is not None
                       and abs(timing_r["duration_s"] - timing_o["duration_s"]) <= tol)
        grid_ok = len(rp) == len(op) and not mismatches and endpoint_ok
        detail = "all decoded presentation timestamps and final endpoint match" if grid_ok else (
            f"actual presentation grid differs: first mismatched frames {mismatches[:8]}; "
            f"counts {len(op)}/{len(rp)}, endpoints {timing_o['duration_s']}/{timing_r['duration_s']} s")
        add("presentation_timing", "PASS" if grid_ok else "FAIL", detail,
            tolerance_s=tol, ref_cfr=timing_r["cfr"], ours_cfr=timing_o["cfr"])
    except RuntimeError as exc:
        add("presentation_timing", "FAIL", str(exc))

    # 1 frames
    add("frames", "PASS" if po["nb_frames"] == expect["frames"] else "FAIL",
        f"ours {po['nb_frames']} frames, expected {expect['frames']} ({expect['source']})",
        ours=po["nb_frames"], ref=pr["nb_frames"], expected=expect["frames"])
    # 2 fps
    add("fps", "PASS" if po["fps_str"] == expect["fps"] else "FAIL",
        f"ours {po['fps_str']} (r {po.get('r_fps_str')}, avg {po.get('avg_fps_str')}), expected {expect['fps']}",
        ours=po["fps_str"], ref=pr["fps_str"], vfr=po.get("vfr"))
    # 3 duration
    vd_o = (timing_o or {}).get("duration_s") or po["nb_frames"] / float(po["fps"])
    vd_r = (timing_r or {}).get("duration_s") or pr["nb_frames"] / float(pr["fps"])
    cd_o = po.get("format_duration") or vd_o
    cd_r = pr.get("format_duration") or vd_r
    tail_ok = cd_o <= max(cd_r, vd_o) + 0.05
    dur_status = "PASS" if abs(vd_o - vd_r) < 0.5 / float(po["fps"]) and tail_ok else (
        "FAIL" if abs(vd_o - vd_r) >= 0.5 / float(po["fps"]) else "WARN")
    add("duration", dur_status,
        f"video {vd_o:.3f} s vs ref {vd_r:.3f} s; container {cd_o:.3f} s vs ref {cd_r:.3f} s"
        + ("" if tail_ok else " (container longer than the reference's own audio tail)"),
        ours_video=round(vd_o, 4), ref_video=round(vd_r, 4), ours_container=cd_o, ref_container=cd_r)
    # 4 size / tags
    size_ok = (po["w"], po["h"]) == (expect["w"], expect["h"])
    add("size", "PASS" if size_ok else ("FAIL" if a.expect_size or expect["source"] != "ref" else "WARN"),
        f"ours {po['w']}x{po['h']}, expected {expect['w']}x{expect['h']}", ours=[po["w"], po["h"]],
        ref=[pr["w"], pr["h"]])
    tag_issues = []
    if po.get("pix_fmt") != "yuv420p":
        tag_issues.append(f"pix_fmt {po.get('pix_fmt')}")
    if po.get("sar") not in (None, "1:1", "0:1"):
        tag_issues.append(f"SAR {po.get('sar')}")
    for k in ("color_primaries", "color_transfer", "color_space"):
        if po.get(k) != "bt709":
            tag_issues.append(f"{k} {po.get(k)}")
    add("tags", "PASS" if not tag_issues else "WARN",
        "yuv420p, SAR 1:1, bt709 tags" if not tag_issues else "; ".join(tag_issues))
    # 5 audio
    md5_r = audio_md5(ref) if pr.get("has_audio") else None
    md5_o = audio_md5(ours) if po.get("has_audio") else None
    ld_r = loudness(ref) if pr.get("has_audio") else None
    ld_o = loudness(ours) if po.get("has_audio") else None
    if pr.get("has_audio") and not po.get("has_audio"):
        add("audio_present", "FAIL", "the reference has audio, ours has none")
    else:
        add("audio_present", "PASS" if po.get("has_audio") or not pr.get("has_audio") else "NOTE",
            f"ref {'yes' if pr.get('has_audio') else 'no'}, ours {'yes' if po.get('has_audio') else 'no'}")
    copied = md5_r is not None and md5_r == md5_o
    ai_r = audio_stream_info(ref) if pr.get("has_audio") else None
    ai_o = audio_stream_info(ours) if po.get("has_audio") else None
    reuse_ok, reuse = False, None
    if ai_r and ai_o and not copied:
        reuse_ok, reuse = audio_reuse_match(ai_r, ai_o, ld_r, ld_o, po["fps"], a.reuse_lu)

    def reuse_txt(only_failed=False):
        return "; ".join(c["detail"] for c in reuse or [] if not (only_failed and c["ok"]))

    if ai_r and ai_o and (a.audio_mode == "copy" or copied or (a.audio_mode == "auto" and reuse_ok)):
        starts = (ai_r.get("start_time"), ai_o.get("start_time"),
                  (timing_r or {}).get("pts_seconds", [None])[0],
                  (timing_o or {}).get("pts_seconds", [None])[0])
        if any(value is None for value in starts):
            add("audio_sync", "FAIL", "reused audio/video start timestamps unavailable; exact synchronization unverified")
        else:
            ref_offset, ours_offset = starts[0] - starts[2], starts[1] - starts[3]
            tolerance = max(0.001, 2 / float(ai_r.get("sample_rate") or 48000),
                            2 / float(ai_o.get("sample_rate") or 48000))
            add("audio_sync", "PASS" if abs(ours_offset - ref_offset) <= tolerance else "FAIL",
                f"audio/video start offset {ours_offset:.6f}s vs reference {ref_offset:.6f}s",
                ours_offset_s=ours_offset, ref_offset_s=ref_offset, tolerance_s=tolerance)

    if po.get("has_audio"):
        if a.audio_mode == "copy" or (a.audio_mode == "auto" and copied):
            add("audio_md5", "PASS" if copied else "FAIL",
                "audio stream identical to the reference (stream copy)" if copied else
                "audio stream differs from the reference but --audio-mode copy was asked (mux with -c copy, "
                "no -shortest/-t; copy from the same file you show as Original)"
                + (" - it does match the reference by codec, rate, channels, loudness and duration, which "
                   "--audio-mode auto accepts" if reuse_ok else ""), ref=md5_r, ours=md5_o, reuse=reuse)
        elif a.audio_mode == "auto" and reuse_ok:
            add("audio_md5", "PASS", "not bit-identical (acceptable): the reference's own audio "
                f"({reuse_txt()})", ref=md5_r, ours=md5_o, reuse=reuse)
        elif copied:  # --audio-mode mix on a stream copy
            add("audio_md5", "NOTE", "audio stream identical to the reference (--audio-mode mix)",
                ref=md5_r, ours=md5_o)
        else:
            why = reuse_txt(only_failed=True)
            add("audio_md5", "NOTE", "audio differs from the reference stream (new mix or re-encode): "
                "the true-peak rule applies" + (f" (not the reference's own audio: {why})" if why else ""),
                ref=md5_r, ours=md5_o, reuse=reuse)
        tp = (ld_o or {}).get("TP_dbtp")
        if copied or (a.audio_mode == "auto" and reuse_ok):
            add("true_peak", "NOTE", f"reused reference audio (no limiter/loudnorm on it); TP {tp} dBTP",
                ours=ld_o, ref=ld_r)
        elif tp is None:
            add("true_peak", "WARN", "could not measure ebur128 true peak", ours=ld_o, ref=ld_r)
        else:
            add("true_peak", "PASS" if tp <= a.max_tp else "FAIL",
                f"new mix true peak {tp} dBTP (limit {a.max_tp}); I {ld_o.get('I_lufs')} LUFS "
                f"(ref I {(ld_r or {}).get('I_lufs')}, TP {(ld_r or {}).get('TP_dbtp')})", ours=ld_o, ref=ld_r)
    # 11 bars
    b_r = bar_scan(ref, pr)
    b_o = bar_scan(ours, po)
    # An intentional frame edge (EDL border fx, or --expect-border) turns edge bars into a NOTE, up to
    # --border-max-frac of the side: a thicker bar is a layout fault a border fx does not draw.
    border = (["--expect-border"] if a.expect_border else []) + declared_border(W, getattr(a, "edl", None))
    bar_fail, bar_warn, bar_note = [], [], []
    if b_o and b_r:
        if b_o.get("all_dark"):
            bar_fail.append("ours is (nearly) black in every sampled frame")
        else:
            for edge in ("top", "bottom", "left", "right"):
                dim = "h" if edge in ("top", "bottom") else "w"
                o_rel = b_o[edge] / po[dim]
                r_rel = b_r[edge] / pr[dim] if not b_r.get("all_dark") else 0
                extra = (o_rel - r_rel) * po[dim]
                msg = (f"{edge} bar {b_o[edge]:.0f} px in ours vs {r_rel * po[dim]:.0f} px (scaled) in the "
                       f"reference")
                cap = a.border_max_frac * po[dim]
                if extra >= 2.0 and border and extra <= cap:
                    bar_note.append(msg)
                elif extra >= max(4.0, 0.005 * po[dim]):
                    bar_fail.append(msg + (f" (thicker than an intentional border: > {cap:.0f} px = "
                                           f"{a.border_max_frac:g} of the side)" if border else ""))
                elif extra >= 2.0:
                    bar_warn.append(msg)
    if bar_fail:
        bar_status = "FAIL"
    elif bar_warn:
        bar_status = "WARN"
    elif bar_note:
        bar_status = "NOTE"
    else:
        bar_status = "PASS"
    bar_detail = "; ".join(bar_fail + bar_warn + bar_note) or "no dark edge bars the reference does not have"
    if bar_note:
        bar_detail += f" - intentional border declared ({', '.join(border)}): not a fault"
    add("bars", bar_status, bar_detail, ours=b_o, ref=b_r, border_declared=border or None)
    # 12 frozen
    d_o = motion_profile(ours, po)
    d_r = motion_profile(ref, pr)
    fz = frozen_scan(d_o, d_r, float(po["fps"]), float(pr["fps"]), still=a.still, moving=a.moving)
    fz_r = frozen_scan(d_r, None, float(pr["fps"]), float(pr["fps"]), still=a.still, moving=a.moving)
    nfl = len(fz["flagged"])
    add("frozen", "PASS" if not nfl else "WARN",
        (f"no held runs >= {fz['min_run']} f where the reference moves" if not nfl else
         f"{nfl} held run(s) where the reference moves: "
         + ", ".join(f"f{x['f0']}-{x['f1']} ({x['frames']} f)" for x in fz["flagged"][:8])),
        ours=fz, ref={"held_runs": fz_r["held_runs"], "held_frames": fz_r["held_frames"],
                      "unique_ratio": fz_r["unique_ratio"]})
    fails = [c["id"] for c in checks if c["status"] == "FAIL"]
    warns = [c["id"] for c in checks if c["status"] == "WARN"]
    keep = ("path", "w", "h", "fps_str", "r_fps_str", "avg_fps_str", "vfr", "nb_frames", "duration",
            "format_duration", "codec", "pix_fmt", "sar", "color_space", "color_transfer", "color_primaries",
            "has_audio", "audio_codec", "audio_sr", "audio_channels", "audio_duration", "size_bytes")
    res = {"schema": "katana.check/1", "ok": not fails, "fail": fails, "warn": warns,
           "audio_mode": a.audio_mode,
           "ref": {**{k: pr.get(k) for k in keep}, "audio_md5": md5_r, "audio_stream": ai_r, "loudness": ld_r,
                   "bars": b_r},
           "ours": {**{k: po.get(k) for k in keep}, "audio_md5": md5_o, "audio_stream": ai_o, "loudness": ld_o,
                    "bars": b_o},
           "expect": expect, "checks": checks, "secs": round(time.time() - t0, 2)}
    out = a.json or (os.path.join(W, "qa", f"check_{os.path.splitext(os.path.basename(ours))[0]}.json") if W else None)
    for c in checks:
        print(f"{c['status']:4s} {c['id']:13s} {c['detail']}")
    print(f"{'OK' if not fails else 'FAIL'}: {len(fails)} fail, {len(warns)} warn  ({res['secs']} s)")
    if out:
        rrio.save_json(out, res)
        print(f"wrote {out}")
    else:
        print(json.dumps(rrio.jsonable(res)))
    return 0 if not fails else 1


# ----------------------------------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------------------------------
def build_parser():
    ap = argparse.ArgumentParser(prog="compare.py", description=(
        "katana comparisons: side-by-side / triptych videos, ref|ours pair sheets, machine QA check."),
        epilog=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def video_opts(p):
        p.add_argument("--out", help="output .mp4 (default W/out/compare.mp4 | triptych.mp4)")
        p.add_argument("--height", type=int, help="panel height before the width cap (default min(1080, tallest input))")
        p.add_argument("--max-w", type=int, default=MAX_W, help=f"max total width (default {MAX_W})")
        p.add_argument("--band", type=int, default=BAND, help=f"label band height (default {BAND})")
        p.add_argument("--gap", type=int, default=GAP, help=f"black gap between panels (default {GAP})")
        p.add_argument("--crf", type=int, default=20)
        p.add_argument("--preset", default="medium")
        p.add_argument("--font", help="TTF/TTC for drawtext labels (default: first existing system font)")
        p.add_argument("--label-engine", choices=("auto", "pil", "drawtext", "bitmap"), default="auto",
                       help="auto = Pillow + TTF when installed (sandbox), else ffmpeg drawtext, else bitmap")
        p.add_argument("--bitmap-labels", action="store_true", help="same as --label-engine bitmap")

    p = sub.add_parser("sbs", help="side-by-side Original | Ours video",
                       description="Side-by-side video; master timeline = ours (different fps is resampled to ours).")
    p.add_argument("W", nargs="?")
    p.add_argument("--ref")
    p.add_argument("--ours")
    p.add_argument("--labels", help='default "Original|Ours"')
    p.add_argument("--audio", choices=("ref", "ours", "none"), default="ours")
    p.add_argument("--master", choices=("ref", "ours"), default="ours",
                   help="timeline (fps + frame count) to sync on (default ours)")
    video_opts(p)
    p.set_defaults(fn=cmd_sbs)

    p = sub.add_parser("triptych", help="Original | Genjutsu | Ours video",
                       description="Standard 3-panel video: same height, width <= 3840, 80 px label band, even "
                                   "dims, audio from --a (the reference). Master timeline = --c (ours).")
    p.add_argument("W", nargs="?")
    p.add_argument("--a", help="original / reference")
    p.add_argument("--b", help="raw Genjutsu output on the reference timeline")
    p.add_argument("--c", help="ours")
    p.add_argument("--labels", help='default "Original|Genjutsu|Ours"')
    p.add_argument("--audio", choices=("a", "b", "c", "ref", "ours", "none"), default="a")
    p.add_argument("--master", choices=("a", "b", "c", "ref", "ours"), default="c")
    video_opts(p)
    p.set_defaults(fn=cmd_triptych)

    p = sub.add_parser("sheet", help="ref|ours pair contact sheet(s), JPEG <= 500 KB each",
                       description="Pairs at ours frame indices (--frames), times (--times), every SEC (--every), "
                                   "or W/analysis/breakdown.json key frames (cut f0-1/f0/mid/f1, trick, crop "
                                   "frames); ref frames are matched by time.")
    p.add_argument("W", nargs="?")
    p.add_argument("--ref")
    p.add_argument("--ours")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--times", help="t1,t2,... seconds")
    g.add_argument("--every", type=float, help="one pair every SEC seconds")
    g.add_argument("--frames", help="ours frame indices f1,f2,...")
    p.add_argument("--out", help="output .jpg (default W/qa/pairs.jpg); _01, _02 ... when several sheets")
    p.add_argument("--per-sheet", type=int, default=12, help="pairs per sheet (default 12)")
    p.add_argument("--pairs-per-row", type=int, help="default 4 for portrait, 2 otherwise")
    p.add_argument("--max-bytes", type=int, default=500_000,
                   help="per sheet (500000 for 1 sheet per image_paths call, 120000 for 4)")
    p.add_argument("--max-w", type=int, default=1600)
    p.add_argument("--crop", help="x,y,w,h applied to both (e.g. the window of a window-in-canvas ref)")
    p.add_argument("--crop-ref", help="x,y,w,h for the reference only")
    p.add_argument("--crop-ours", help="x,y,w,h for ours only")
    p.add_argument("--no-sort", dest="sort", action="store_false", help="keep the given order and duplicates")
    p.set_defaults(fn=cmd_sheet)

    p = sub.add_parser("check", help="machine QA of ours vs the reference -> JSON; exit 1 on any FAIL",
                       description="Frame count, fps, duration, size/tags, audio MD5 (stream copy) or reused-"
                                   "audio match (D19), ebur128 I/LRA/TP of both, black-bar edge scan (a NOTE "
                                   "instead of a FAIL when the EDL declares an intentional border or "
                                   "--expect-border is passed), frozen-frame scan.")
    p.add_argument("W", nargs="?")
    p.add_argument("--ref")
    p.add_argument("--ours")
    p.add_argument("--json", help="output JSON (default W/qa/check_<ours>.json; stdout without W)")
    p.add_argument("--audio-mode", choices=("auto", "copy", "mix"), default="auto",
                   help="copy: the reference audio must be stream-copied (MD5 equal); mix: a new mix (true "
                        "peak <= --max-tp); auto (D19): MD5 equal passes; not bit-identical but the "
                        "reference's own audio (same codec/profile, sample rate, channels, integrated "
                        "loudness within --reuse-lu, duration within 1 frame) passes as 'not bit-identical "
                        "(acceptable)'; anything else gets the true-peak rule")
    p.add_argument("--reuse-lu", type=float, default=0.5,
                   help="auto mode: integrated-loudness tolerance (LU) for reused reference audio (default 0.5)")
    p.add_argument("--max-tp", type=float, default=-1.0, help="true-peak limit for a new mix (dBTP)")
    p.add_argument("--expect-frames", type=int, help="expected frame count when the format lock differs from the ref")
    p.add_argument("--expect-size", help="WxH when the format lock differs from the ref (makes size a hard check)")
    p.add_argument("--expect-border", action="store_true",
                   help="the output carries an intentional frame edge (ink border, frame overlay): edge bars "
                        "up to --border-max-frac are a NOTE, not a FAIL. Implied when the EDL declares "
                        "post.border, a shot fx.border or a border layer")
    p.add_argument("--edl", help="EDL that may declare the border (default W/comp/edl.json)")
    p.add_argument("--border-max-frac", type=float, default=0.06,
                   help="thickest bar (fraction of the side) an intentional border excuses (default 0.06)")
    p.add_argument("--still", type=float, default=0.3, help="mean abs diff (0-255, 64 px gray) below = held frame")
    p.add_argument("--moving", type=float, default=1.0, help="reference diff above = the reference moves")
    p.set_defaults(fn=cmd_check)
    return ap


def main(argv=None):
    ap = build_parser()
    a = ap.parse_args(argv)
    try:
        return a.fn(a)
    except (CmpError, FileNotFoundError, ValueError, IndexError, RuntimeError) as e:
        print(f"compare: error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
