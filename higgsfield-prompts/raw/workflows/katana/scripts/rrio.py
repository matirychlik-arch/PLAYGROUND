#!/usr/bin/env python3
"""rrio - shared IO + numpy helpers for every katana script (stdlib + numpy + ffmpeg/ffprobe).

Import from a script that lives next to this file:
    import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import rrio
(rr.sh also puts $RR on PYTHONPATH; under `python3 -I` PYTHONPATH is ignored, hence the insert.)

Contents
  probe(path, count=False)                 ffprobe -> dict (rotation-corrected w/h, exact Fraction fps, ...)
  read_frames(path, start, count, ...)     generator of (index, HxWx3 uint8), frame-exact (trim/select by index)
  read_frames_at(path, indices, ...)       list of frames for sparse indices, in the requested order
  iter_frames_at / read_frame / read_all   variants
  read_image / encode_image / write_image  still images through ffmpeg pipes (png / jpg)
  VideoWriter                              rgb24 frames -> H.264 (bt709 tagged) through an ffmpeg pipe
  draw_text / text_size                    built-in 5x7 bitmap font (no system fonts needed)
  tile_sheet / video_sheet                 labelled contact sheets, JPEG auto-sized under max_bytes
  resize, box_blur, gauss_blur, dilate, erode, to_gray, luma, rgb_to_hsv, hsv_to_rgb, saturation,
  mse, psnr, fit_into, to_uint8            numpy image helpers
  load_json / save_json / jsonable         JSON (atomic write, Fraction/numpy aware)
  frame_time / time_to_frame / tc / parse_fps / fps_str   time helpers

CLI:  python3 rrio.py probe|frame|sheet|font ...   (see --help)
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import subprocess
import sys
import tempfile
from fractions import Fraction

import numpy as np

FFMPEG = os.environ.get("RR_FFMPEG", "ffmpeg")
FFPROBE = os.environ.get("RR_FFPROBE", "ffprobe")

__all__ = [
    "probe", "read_frames", "read_frames_at", "iter_frames_at", "read_frame", "read_all", "count_frames",
    "read_image", "encode_image", "write_image", "VideoWriter", "draw_text", "text_size", "tile_sheet",
    "video_sheet", "resize", "box_blur", "gauss_blur", "dilate", "erode", "to_gray", "luma", "rgb_to_hsv",
    "hsv_to_rgb", "saturation", "mse", "psnr", "fit_into", "to_uint8", "load_json", "save_json", "jsonable",
    "frame_time", "time_to_frame", "frame_timestamps", "require_cfr", "tc", "parse_fps", "fps_str", "run_ffmpeg", "FFMPEG", "FFPROBE",
]


# --------------------------------------------------------------------------------------------------
# ffmpeg plumbing
# --------------------------------------------------------------------------------------------------
_FF_VERSION = None


def ffmpeg_version():
    """(major, minor) of the ffmpeg binary; git builds report (99, 0)."""
    global _FF_VERSION
    if _FF_VERSION is None:
        try:
            out = subprocess.run([FFMPEG, "-hide_banner", "-version"], capture_output=True, text=True).stdout
        except FileNotFoundError:
            raise RuntimeError(f"ffmpeg not found ({FFMPEG}); set RR_FFMPEG") from None
        m = re.search(r"ffmpeg version n?(\d+)\.(\d+)", out)
        _FF_VERSION = (int(m.group(1)), int(m.group(2))) if m else (99, 0)
    return _FF_VERSION


def _passthrough():
    # -fps_mode exists since 5.1 (sandbox has 5.1, local 8.0); older builds only know -vsync.
    return ["-fps_mode", "passthrough"] if ffmpeg_version() >= (5, 1) else ["-vsync", "passthrough"]


def _tail(fh, n=1500):
    try:
        fh.seek(0)
        return fh.read().decode("utf-8", "replace")[-n:].strip()
    except Exception:
        return ""


def run_ffmpeg(args, check=True):
    """Run `ffmpeg -hide_banner -nostdin -loglevel error -y <args>`; raise RuntimeError with stderr on failure."""
    cmd = [FFMPEG, "-hide_banner", "-nostdin", "-loglevel", "error", "-y", *map(str, args)]
    r = subprocess.run(cmd, capture_output=True)
    if check and r.returncode != 0:
        raise RuntimeError("ffmpeg failed: " + r.stderr.decode("utf-8", "replace")[-1500:])
    return r


# --------------------------------------------------------------------------------------------------
# time / fps helpers
# --------------------------------------------------------------------------------------------------
_STD_RATES = [Fraction(24000, 1001), Fraction(24), Fraction(25), Fraction(30000, 1001), Fraction(30),
              Fraction(48), Fraction(50), Fraction(60000, 1001), Fraction(60), Fraction(90),
              Fraction(120000, 1001), Fraction(120), Fraction(15), Fraction(12), Fraction(20)]


def parse_fps(v):
    """'30000/1001' | '29.97' | 30 | Fraction -> Fraction (None for 0/0 or garbage)."""
    if v is None:
        return None
    if isinstance(v, Fraction):
        return v
    if isinstance(v, (int, np.integer)):
        return Fraction(int(v))
    if isinstance(v, (float, np.floating)):
        return _float_fps(float(v))
    s = str(v).strip()
    try:
        if "/" in s:
            n, d = s.split("/", 1)
            n, d = int(n), int(d)
            return Fraction(n, d) if n > 0 and d > 0 else None
        return _float_fps(float(s))
    except (ValueError, ZeroDivisionError):
        return None


def _float_fps(f):
    """Decimal fps -> Fraction; 29.97/23.976/59.94 snap to their exact NTSC rationals."""
    if not math.isfinite(f) or f <= 0:
        return None
    for s in _STD_RATES:
        if abs(f - float(s)) <= 0.0005 * float(s):
            return s
    return Fraction(f).limit_denominator(1001)


def fps_str(fps):
    """Fraction(30000,1001) -> '30000/1001' (always n/d, never rounded)."""
    f = parse_fps(fps)
    return f"{f.numerator}/{f.denominator}" if f else "0/1"


def frame_time(f, fps, center=True):
    """Time of frame f. center=True -> (f+0.5)/fps (sampling instant); False -> f/fps (frame start)."""
    fr = parse_fps(fps)
    return float((Fraction(int(f)) + (Fraction(1, 2) if center else 0)) / fr)


def time_to_frame(t, fps):
    """Index of the frame that is on screen at time t (floor(t*fps), robust to float noise)."""
    return int(math.floor(float(t) * float(parse_fps(fps)) + 1e-6))


def tc(t, decimals=2):
    """Seconds -> 'M:SS.ss'."""
    t = max(0.0, float(t))
    m = int(t // 60)
    return f"{m}:{t - 60 * m:0{3 + decimals}.{decimals}f}"


def _snap_rate(r):
    for s in _STD_RATES:
        if abs(float(r) - float(s)) <= 0.004 * float(s):
            return s
    return Fraction(float(r)).limit_denominator(1001)


# --------------------------------------------------------------------------------------------------
# probe
# --------------------------------------------------------------------------------------------------
_IMAGE_CODECS = {"png", "mjpeg", "jpeg2000", "webp", "bmp", "tiff", "gif", "jpegls", "ppm", "pgm"}


def count_frames(path, stream_index=None):
    """Decoded video frame count (ffprobe -count_frames; decodes the whole stream)."""
    sel = f"{stream_index}" if stream_index is not None else "v:0"
    r = subprocess.run([FFPROBE, "-v", "error", "-count_frames", "-select_streams", sel, "-show_entries",
                        "stream=nb_read_frames", "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    m = re.search(r"\d+", r.stdout or "")
    if r.returncode != 0 or not m:
        raise RuntimeError(f"count_frames failed for {path}: {r.stderr.strip()[-400:]}")
    return int(m.group(0))


def probe(path, count=False):
    """ffprobe a media file.

    Returns a dict (JSON-safe via jsonable()) with:
      path, w, h (display size, rotation-corrected), width, height (aliases), coded_w, coded_h,
      rotation (clockwise degrees 0/90/180/270), fps (Fraction, exact e.g. 30000/1001), fps_float,
      fps_str, r_fps_str, avg_fps_str, vfr (r_frame_rate != avg_frame_rate), nb_frames, frames (alias),
      nb_frames_src ('header'|'counted'|'estimated'|'image'), duration (video seconds),
      format_duration, has_audio, audio_codec, audio_sr (alias sample_rate), audio_channels,
      audio_duration, codec, profile, pix_fmt, bit_depth, color_space, color_range, color_transfer,
      color_primaries, sar, bit_rate, size_bytes, format_name, is_image, stream_index, start_time.
    count=True forces a decoded frame count (exact but decodes everything); it is also used
    automatically when the container has no nb_frames.
    """
    path = str(path)
    if "://" not in path and not os.path.exists(path):
        raise FileNotFoundError(path)
    r = subprocess.run([FFPROBE, "-v", "error", "-show_streams", "-show_format", "-of", "json", path],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"ffprobe failed for {path}: {r.stderr.strip()[-600:]}")
    j = json.loads(r.stdout or "{}")
    streams = j.get("streams", [])
    fmt = j.get("format", {})
    vids = [s for s in streams if s.get("codec_type") == "video"
            and not (s.get("disposition") or {}).get("attached_pic")]
    auds = [s for s in streams if s.get("codec_type") == "audio"]
    if not vids:
        vids = [s for s in streams if s.get("codec_type") == "video"]
    out = {"path": path, "format_name": fmt.get("format_name"),
           "size_bytes": int(fmt["size"]) if str(fmt.get("size", "")).isdigit() else None,
           "format_duration": _f(fmt.get("duration")), "bit_rate": _i(fmt.get("bit_rate"))}
    a = auds[0] if auds else None
    out.update({"has_audio": a is not None,
                "audio_codec": a.get("codec_name") if a else None,
                "audio_sr": _i(a.get("sample_rate")) if a else None,
                "audio_channels": _i(a.get("channels")) if a else None,
                "audio_duration": _f(a.get("duration")) if a else None,
                "audio_bitrate": _i(a.get("bit_rate")) if a else None})
    out["sample_rate"] = out["audio_sr"]
    if not vids:
        out.update({"w": None, "h": None, "width": None, "height": None, "fps": None, "fps_float": None,
                    "nb_frames": 0, "frames": 0, "duration": out["audio_duration"] or out["format_duration"],
                    "has_video": False})
        return out
    v = vids[0]
    rot = 0
    tags = v.get("tags") or {}
    if "rotate" in tags:
        try:
            rot = int(float(tags["rotate"])) % 360
        except ValueError:
            rot = 0
    for sd in v.get("side_data_list") or []:
        if "rotation" in sd:
            try:
                # display-matrix rotation is counter-clockwise; express it as clockwise like the old tag
                rot = int(round(-float(sd["rotation"]))) % 360
            except (TypeError, ValueError):
                pass
    rot = int(round(rot / 90.0)) * 90 % 360
    cw, ch = _i(v.get("width")), _i(v.get("height"))
    w, h = (ch, cw) if rot in (90, 270) else (cw, ch)
    codec = v.get("codec_name")
    is_image = codec in _IMAGE_CODECS and (fmt.get("format_name", "").endswith("_pipe")
                                          or fmt.get("format_name") == "image2")
    rf, af = parse_fps(v.get("r_frame_rate")), parse_fps(v.get("avg_frame_rate"))
    if rf and af and abs(float(rf) - float(af)) <= 0.002 * float(af):
        fps, vfr = rf, False
    elif af or rf:
        base = af or rf
        fps, vfr = _snap_rate(base), bool(rf and af)
    else:
        fps, vfr = None, False
    dur = _f(v.get("duration")) or out["format_duration"]
    nb, src = _i(v.get("nb_frames")), "header"
    if is_image:
        nb, src = 1, "image"
    elif count or not nb:
        try:
            nb, src = count_frames(path, v.get("index")), "counted"
        except RuntimeError:
            if dur and fps:
                nb, src = int(round(dur * float(fps))), "estimated"
    pix = v.get("pix_fmt") or ""
    bd = _i(v.get("bits_per_raw_sample"))
    if not bd:
        m = re.search(r"p(9|10|12|14|16)(le|be)?$", pix)
        bd = int(m.group(1)) if m else (8 if pix else None)
    out.update({
        "has_video": True, "stream_index": v.get("index"), "codec": codec, "profile": v.get("profile"),
        "pix_fmt": pix or None, "bit_depth": bd, "w": w, "h": h, "width": w, "height": h,
        "coded_w": cw, "coded_h": ch, "rotation": rot,
        "fps": fps, "fps_float": float(fps) if fps else None, "fps_str": fps_str(fps) if fps else None,
        "r_fps_str": v.get("r_frame_rate"), "avg_fps_str": v.get("avg_frame_rate"), "vfr": vfr,
        "nb_frames": nb, "frames": nb, "nb_frames_src": src, "duration": dur,
        "time_base": v.get("time_base"), "stream_duration": _f(v.get("duration")),
        "start_time": _f(v.get("start_time")), "is_image": is_image,
        "color_space": v.get("color_space"), "color_range": v.get("color_range"),
        "color_transfer": v.get("color_transfer"), "color_primaries": v.get("color_primaries"),
        "sar": v.get("sample_aspect_ratio"), "video_bit_rate": _i(v.get("bit_rate")),
    })
    return out


def frame_timestamps(path, info=None):
    """Decode actual presentation timestamps; do not infer VFR timing from average fps.

    Times are seconds. relative_pts normalizes only the initial timestamp. A one-tick
    tolerance accommodates container quantization without accepting frame-sized drift.
    Missing or non-monotonic timestamps are an explicit unsupported timing state.
    """
    p = info or probe(path)
    if not p.get("has_video"):
        raise RuntimeError(f"{path}: no video timing to inspect")
    tb = parse_fps(p.get("time_base"))
    if tb is None or tb <= 0:
        raise RuntimeError(f"{path}: missing valid video time_base; timing cannot be verified")
    result = subprocess.run(
        [FFPROBE, "-v", "error", "-select_streams", str(p["stream_index"]),
         "-show_frames", "-show_entries",
         "frame=best_effort_timestamp,pts,duration,pkt_duration", "-of", "json", str(path)],
        capture_output=True, text=True,
    )
    if result.returncode:
        raise RuntimeError(f"{path}: frame timing probe failed: {result.stderr.strip()[-600:]}")
    records = json.loads(result.stdout or "{}").get("frames", [])
    if not records:
        raise RuntimeError(f"{path}: no decoded frame timestamps")
    points, durations = [], []
    for index, record in enumerate(records):
        tick = record.get("best_effort_timestamp", record.get("pts"))
        try:
            point = int(tick) * tb
        except (TypeError, ValueError):
            raise RuntimeError(f"{path}: missing presentation timestamp at frame {index}") from None
        if points and point <= points[-1]:
            raise RuntimeError(f"{path}: non-monotonic presentation timestamp at frame {index}")
        points.append(point)
        ticks = _i(record.get("duration", record.get("pkt_duration")))
        durations.append(float(ticks * tb) if ticks is not None and ticks > 0 else None)
    relative = [float(point - points[0]) for point in points]
    fps = p.get("fps")
    step = float(1 / fps) if fps and fps > 0 else None
    intervals = [b - a for a, b in zip(relative, relative[1:]) if b > a]
    if step is not None:
        intervals.append(step)
    cap = min(intervals) * 0.1 if intervals else 1e-3
    tolerance = max(min(float(tb) * 1.1, cap), 1e-8)
    issues = []
    if step is None:
        issues.append("no usable nominal frame rate")
    else:
        first = next((i for i, value in enumerate(relative) if abs(value - i * step) > tolerance), None)
        if first is not None:
            issues.append(f"frame {first} PTS {relative[first]:.9f}s differs from CFR grid {first * step:.9f}s")
    duration = p.get("stream_duration")
    if duration is None and durations[-1] is not None:
        duration = relative[-1] + durations[-1]
    if duration is not None and (not math.isfinite(duration) or duration <= relative[-1]):
        duration = None
    if duration is None:
        issues.append("final frame endpoint is unavailable")
    elif step is not None and abs(duration - len(points) * step) > tolerance:
        issues.append("final frame endpoint differs from the CFR grid")
    return {"frames": len(points), "pts_seconds": [float(point) for point in points],
            "relative_pts": relative, "frame_durations": durations, "duration_s": duration,
            "time_base": str(tb), "tolerance_s": tolerance, "expected_step_s": step,
            "cfr": not issues, "issues": issues}


def require_cfr(path, info=None):
    """Return verified CFR timing or reject this CFR-only processing branch."""
    timing = frame_timestamps(path, info)
    if not timing["cfr"]:
        raise RuntimeError(f"{path}: variable or unverified frame timing is unsupported by this CFR-only helper; "
                           "preserve the original stream or use a verified PTS-aware route. " + "; ".join(timing["issues"]))
    return timing


def _f(x):
    try:
        v = float(x)
        return v if math.isfinite(v) else None
    except (TypeError, ValueError):
        return None


def _i(x):
    try:
        return int(x)
    except (TypeError, ValueError):
        return None


def _in_matrix(p):
    """Colour matrix for YUV->RGB so local ffmpeg 8 and sandbox ffmpeg 5.1 decode identically."""
    cs = (p.get("color_space") or "").lower()
    pix = (p.get("pix_fmt") or "").lower()
    if pix.startswith(("rgb", "bgr", "gbr", "rgba", "bgra", "argb", "abgr", "gray", "ya", "pal")):
        return None
    if pix.startswith("yuvj"):
        return "smpte170m"
    table = {"bt709": "bt709", "smpte170m": "smpte170m", "bt470bg": "bt470", "bt2020nc": "bt2020",
             "bt2020c": "bt2020", "smpte240m": "smpte240m", "fcc": "fcc"}
    if cs in table:
        return table[cs]
    w, h = p.get("w") or 0, p.get("h") or 0
    return "bt709" if max(w, h) >= 1280 or min(w, h) >= 720 else "smpte170m"


# --------------------------------------------------------------------------------------------------
# frame readers
# --------------------------------------------------------------------------------------------------
def _norm_crop(crop, W, H):
    if crop is None:
        return None
    if isinstance(crop, dict):
        x, y, w, h = crop["x"], crop["y"], crop["w"], crop["h"]
    else:
        x, y, w, h = crop
    x, y, w, h = int(round(x)), int(round(y)), int(round(w)), int(round(h))
    if w <= 0 or h <= 0 or x < 0 or y < 0 or x + w > W or y + h > H:
        raise ValueError(f"crop (x={x},y={y},w={w},h={h}) outside the {W}x{H} frame")
    return x, y, w, h


def _geometry(p, crop=None, scale_w=None, scale_h=None):
    W, H = p["w"], p["h"]
    c = _norm_crop(crop, W, H)
    cw, ch = (c[2], c[3]) if c else (W, H)
    if scale_w and scale_h:
        ow, oh = int(scale_w), int(scale_h)
    elif scale_w:
        ow = int(scale_w)
        oh = max(1, int(round(ch * ow / cw)))
    elif scale_h:
        oh = int(scale_h)
        ow = max(1, int(round(cw * oh / ch)))
    else:
        ow, oh = cw, ch
    return c, cw, ch, ow, oh


def _post_chain(p, c, cw, ch, ow, oh, gray):
    chain = []
    m = _in_matrix(p)
    mx = f":in_color_matrix={m}" if m else ""
    flags = "area" if (ow < cw or oh < ch) else "bicubic"
    if c and not gray and m and any(v % 2 for v in c):
        # odd crop on subsampled YUV would shift chroma by half a pixel: convert to RGB first, then crop
        chain += [f"scale=iw:ih:flags=accurate_rnd+full_chroma_int{mx}", "format=rgb24",
                  f"crop={c[2]}:{c[3]}:{c[0]}:{c[1]}"]
        if (ow, oh) != (cw, ch):
            chain.append(f"scale={ow}:{oh}:flags={flags}+accurate_rnd")
        chain.append("format=rgb24")
        return chain
    if c:
        chain.append(f"crop={c[2]}:{c[3]}:{c[0]}:{c[1]}:exact=1")
    chain.append(f"scale={ow}:{oh}:flags={flags}+accurate_rnd+full_chroma_int{mx}")
    chain.append("format=gray" if gray else "format=rgb24")
    return chain


def _pipe(path, p, vf, ow, oh, gray, max_frames=None):
    """Yield raw frames (np.uint8 HxWx3 or HxW) from ffmpeg. Raises RuntimeError on ffmpeg failure."""
    ch_n = 1 if gray else 3
    cmd = [FFMPEG, "-hide_banner", "-nostdin", "-loglevel", "error", "-i", str(path),
           "-map", f"0:{p['stream_index']}", "-an", "-sn", "-dn", "-vf", vf, *_passthrough()]
    if max_frames is not None:
        cmd += ["-frames:v", str(int(max_frames))]
    cmd += ["-f", "rawvideo", "-pix_fmt", "gray" if gray else "rgb24", "pipe:1"]
    errf = tempfile.TemporaryFile()
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=errf, bufsize=0)
    fb = ow * oh * ch_n
    finished = False
    try:
        while True:
            buf = bytearray(fb)
            mv = memoryview(buf)
            got = 0
            while got < fb:
                n = proc.stdout.readinto(mv[got:])
                if not n:
                    break
                got += n
            if got == 0:
                finished = True
                break
            if got < fb:
                raise RuntimeError(f"truncated frame from ffmpeg ({got}/{fb} bytes): {_tail(errf)}")
            a = np.frombuffer(buf, np.uint8)
            yield a.reshape(oh, ow) if gray else a.reshape(oh, ow, 3)
    finally:
        if proc.poll() is None and not finished:
            proc.kill()
        try:
            proc.stdout.close()
        except Exception:
            pass
        rc = proc.wait()
        msg = _tail(errf)
        errf.close()
    if finished and rc != 0:
        raise RuntimeError(f"ffmpeg decode failed (rc={rc}) for {path}: {msg}")


def read_frames(path, start=0, count=None, scale_w=None, crop=None, every=1, gray=False, scale_h=None,
                info=None):
    """Generator of (frame_index, frame) decoded frame-exactly.

    start/count are frame indices of the decoded stream (trim=start_frame/end_frame, never -ss);
    every=N keeps every Nth frame (start, start+N, ...). crop=(x, y, w, h) in display pixels
    (after rotation) is applied before scaling; scale_w (and/or scale_h) resizes (area filter when
    shrinking). Frames are RGB uint8 HxWx3 (HxW with gray=True), writable.
    info: a probe() dict to skip the ffprobe call.
    """
    p = info or probe(path)
    if not p.get("has_video"):
        raise ValueError(f"{path}: no video stream")
    start, every = max(0, int(start)), max(1, int(every))
    c, cw, ch, ow, oh = _geometry(p, crop, scale_w, scale_h)
    chain = []
    end = None if count is None else start + int(count)
    if count is not None and int(count) <= 0:
        return
    if start > 0 or end is not None:
        chain.append(f"trim=start_frame={start}" + (f":end_frame={end}" if end is not None else ""))
    if every > 1:
        chain.append(f"select=not(mod(n\\,{every}))")
    chain += _post_chain(p, c, cw, ch, ow, oh, gray)
    max_frames = None if count is None else (int(count) + every - 1) // every
    for k, fr in enumerate(_pipe(path, p, ",".join(chain), ow, oh, gray, max_frames)):
        yield start + k * every, fr


def _runs(sorted_idx):
    runs = []
    for i in sorted_idx:
        if runs and i == runs[-1][1] + 1:
            runs[-1][1] = i
        else:
            runs.append([i, i])
    return runs


def iter_frames_at(path, indices, scale_w=None, crop=None, gray=False, scale_h=None, info=None):
    """Generator of (index, frame) for the sorted unique indices (select filter, exact)."""
    p = info or probe(path)
    if not p.get("has_video"):
        raise ValueError(f"{path}: no video stream")
    uniq = sorted({int(i) for i in indices})
    if not uniq:
        return
    if uniq[0] < 0:
        raise ValueError("negative frame index")
    runs = _runs(uniq)
    c, cw, ch, ow, oh = _geometry(p, crop, scale_w, scale_h)
    if len(runs) > 1500:  # select expression would get huge: decode the span, pick in python
        want = set(uniq)
        for i, fr in read_frames(path, uniq[0], uniq[-1] - uniq[0] + 1, scale_w, crop, 1, gray, scale_h, p):
            if i in want:
                yield i, fr
        return
    expr = "+".join(f"eq(n\\,{a})" if a == b else f"between(n\\,{a}\\,{b})" for a, b in runs)
    chain = [f"trim=end_frame={uniq[-1] + 1}", f"select={expr}"] + _post_chain(p, c, cw, ch, ow, oh, gray)
    for k, fr in enumerate(_pipe(path, p, ",".join(chain), ow, oh, gray, len(uniq))):
        yield uniq[k], fr


def read_frames_at(path, indices, scale_w=None, crop=None, gray=False, scale_h=None, info=None, strict=True):
    """List of frames for `indices` in the given order (duplicates allowed, each a separate copy).

    strict=True raises IndexError when an index is past the end; strict=False puts None there.
    """
    indices = [int(i) for i in indices]
    got = dict(iter_frames_at(path, indices, scale_w, crop, gray, scale_h, info))
    missing = sorted({i for i in indices if i not in got})
    if missing and strict:
        raise IndexError(f"{path}: frames {missing[:10]}{'...' if len(missing) > 10 else ''} not decodable "
                         f"(video has {len(got) and max(got) + 1 or 0}+ frames)")
    out, seen = [], set()
    for i in indices:
        fr = got.get(i)
        if fr is not None and i in seen:
            fr = fr.copy()
        seen.add(i)
        out.append(fr)
    return out


def read_frame(path, index, **kw):
    """One frame by index (exact)."""
    return read_frames_at(path, [index], **kw)[0]


def read_all(path, **kw):
    """All (or start/count/every-selected) frames stacked to N x H x W x 3. Mind the RAM."""
    frames = [fr for _, fr in read_frames(path, **kw)]
    return np.stack(frames) if frames else np.zeros((0, 0, 0, 3), np.uint8)


# --------------------------------------------------------------------------------------------------
# still images
# --------------------------------------------------------------------------------------------------
def _img_pix_fmt(arr):
    if arr.ndim == 2:
        return "gray"
    if arr.ndim == 3 and arr.shape[2] == 3:
        return "rgb24"
    if arr.ndim == 3 and arr.shape[2] == 4:
        return "rgba"
    if arr.ndim == 3 and arr.shape[2] == 1:
        return "gray"
    raise ValueError(f"unsupported image shape {arr.shape}")


def _jpeg_qscale(quality):
    q = max(1, min(100, int(quality)))
    return int(round(min(31.0, max(2.0, 2 + (100 - q) * 29 / 80))))


def encode_image(arr, fmt="png", quality=85):
    """Encode an image array to PNG or JPEG bytes through ffmpeg.

    arr: uint8 HxW, HxWx3 (RGB) or HxWx4 (RGBA; alpha dropped for JPEG). quality 1-100 (JPEG only;
    mapped to the mjpeg qscale 2..31).
    """
    a = np.asarray(arr)
    if a.dtype != np.uint8:
        a = to_uint8(a)
    if a.ndim == 3 and a.shape[2] == 1:
        a = a[:, :, 0]
    fmt = fmt.lower().lstrip(".")
    if fmt in ("jpg", "jpeg"):
        if a.ndim == 2:
            a = np.repeat(a[:, :, None], 3, axis=2)
        elif a.shape[2] == 4:
            a = a[:, :, :3]
    a = np.ascontiguousarray(a)
    h, w = a.shape[:2]
    pf = _img_pix_fmt(a)
    cmd = [FFMPEG, "-hide_banner", "-nostdin", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", pf,
           "-s", f"{w}x{h}", "-i", "pipe:0", "-frames:v", "1"]
    if fmt in ("jpg", "jpeg"):
        cmd += ["-c:v", "mjpeg", "-q:v", str(_jpeg_qscale(quality)), "-pix_fmt", "yuvj420p",
                "-f", "image2pipe", "pipe:1"]
    elif fmt == "png":
        cmd += ["-c:v", "png", "-pix_fmt", pf, "-f", "image2pipe", "pipe:1"]
    else:
        raise ValueError(f"unsupported image format {fmt!r} (png|jpg)")
    r = subprocess.run(cmd, input=a.tobytes(), capture_output=True)
    if r.returncode != 0 or not r.stdout:
        raise RuntimeError("image encode failed: " + r.stderr.decode("utf-8", "replace")[-800:])
    return r.stdout


_UMASK = os.umask(0o022)
os.umask(_UMASK)


def _atomic_write_bytes(path, data):
    path = str(path)
    d = os.path.dirname(os.path.abspath(path))
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix="." + os.path.basename(path) + ".", suffix=".tmp", dir=d)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        os.chmod(tmp, 0o666 & ~_UMASK)  # mkstemp creates 0600; give the file normal permissions
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def write_image(path, arr, quality=88):
    """Write PNG/JPEG (by extension) atomically; returns the byte size."""
    ext = os.path.splitext(str(path))[1].lower().lstrip(".") or "png"
    data = encode_image(arr, ext, quality)
    _atomic_write_bytes(path, data)
    return len(data)


def read_image(path, mode="rgb"):
    """Read an image (or the first frame of a video). mode: 'rgb' (HxWx3), 'rgba' (HxWx4), 'gray' (HxW)."""
    p = probe(path)
    if not p.get("has_video"):
        raise ValueError(f"{path}: not an image")
    pf = {"rgb": "rgb24", "rgba": "rgba", "gray": "gray"}[mode]
    ch = {"rgb": 3, "rgba": 4, "gray": 1}[mode]
    m = _in_matrix(p)
    vf = "scale=iw:ih" + (f":in_color_matrix={m}" if m else "") + f",format={pf}"
    cmd = [FFMPEG, "-hide_banner", "-nostdin", "-loglevel", "error", "-i", str(path), "-map",
           f"0:{p['stream_index']}", "-frames:v", "1", "-vf", vf, "-f", "rawvideo", "-pix_fmt", pf, "pipe:1"]
    r = subprocess.run(cmd, capture_output=True)
    w, h = p["w"], p["h"]
    if r.returncode != 0 or len(r.stdout) < w * h * ch:
        raise RuntimeError(f"read_image failed for {path}: " + r.stderr.decode("utf-8", "replace")[-600:])
    a = np.frombuffer(bytearray(r.stdout[: w * h * ch]), np.uint8)
    return a.reshape(h, w) if ch == 1 else a.reshape(h, w, ch)


# --------------------------------------------------------------------------------------------------
# video writer
# --------------------------------------------------------------------------------------------------
class VideoWriter:
    """Write RGB uint8 frames to an H.264 (default) mp4 through an ffmpeg pipe, tagged bt709.

        with VideoWriter('out/x.mp4', 1080, 1920, '30000/1001', crf=16) as vw:
            vw.write(frame)      # HxWx3 uint8 RGB, exactly (h, w)
    yuv420p needs even w/h (ValueError otherwise). No audio: mux audio in a separate ffmpeg step.
    """

    def __init__(self, path, w, h, fps, crf=16, preset="medium", codec="libx264", pix_fmt="yuv420p",
                 extra=None, input_pix_fmt="rgb24"):
        self.path, self.w, self.h = str(path), int(w), int(h)
        if pix_fmt.startswith(("yuv420", "yuv422")) and (self.w % 2 or self.h % 2):
            raise ValueError(f"{pix_fmt} needs even size, got {self.w}x{self.h}")
        os.makedirs(os.path.dirname(os.path.abspath(self.path)), exist_ok=True)
        self.n = 0
        self._ch = 4 if input_pix_fmt == "rgba" else 3
        cmd = [FFMPEG, "-hide_banner", "-nostdin", "-loglevel", "error", "-y", "-f", "rawvideo",
               "-pix_fmt", input_pix_fmt, "-s", f"{self.w}x{self.h}", "-framerate", fps_str(fps),
               "-i", "pipe:0", "-vf",
               "scale=out_color_matrix=bt709:out_range=tv:flags=accurate_rnd+full_chroma_int",
               "-c:v", codec, "-pix_fmt", pix_fmt]
        if codec in ("libx264", "libx265"):
            cmd += ["-crf", str(crf), "-preset", preset]
        if codec == "libx265":
            cmd += ["-tag:v", "hvc1"]
        cmd += ["-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
                "-color_range", "tv"]
        if self.path.lower().endswith((".mp4", ".mov", ".m4v")):
            cmd += ["-movflags", "+faststart"]
        cmd += list(extra or []) + [self.path]
        self._err = tempfile.TemporaryFile()
        self.proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=self._err)

    def write(self, frame):
        a = np.asarray(frame)
        if a.dtype != np.uint8:
            a = to_uint8(a)
        if a.shape[:2] != (self.h, self.w) or (a.ndim == 3 and a.shape[2] != self._ch):
            raise ValueError(f"frame {a.shape} != ({self.h}, {self.w}, {self._ch})")
        try:
            self.proc.stdin.write(np.ascontiguousarray(a).tobytes())
        except BrokenPipeError:
            self.proc.wait()
            raise RuntimeError("ffmpeg encoder died: " + _tail(self._err)) from None
        self.n += 1

    def close(self):
        if self.proc is None:
            return
        try:
            self.proc.stdin.close()
        except BrokenPipeError:
            pass
        rc = self.proc.wait()
        msg = _tail(self._err)
        self._err.close()
        self.proc = None
        if rc != 0:
            raise RuntimeError(f"ffmpeg encode failed (rc={rc}): {msg}")

    def __enter__(self):
        return self

    def __exit__(self, et, ev, tb):
        if et is not None and self.proc is not None:
            self.proc.kill()
            self.proc.wait()
            self.proc = None
            return False
        self.close()
        return False


# --------------------------------------------------------------------------------------------------
# bitmap font (5x7, 1 px spacing) - labels never depend on system fonts
# --------------------------------------------------------------------------------------------------
_GLYPHS = {
    "0": ".###.|#...#|#..##|#.#.#|##..#|#...#|.###.", "1": "..#..|.##..|..#..|..#..|..#..|..#..|.###.",
    "2": ".###.|#...#|....#|...#.|..#..|.#...|#####", "3": "#####|...#.|..#..|...#.|....#|#...#|.###.",
    "4": "...#.|..##.|.#.#.|#..#.|#####|...#.|...#.", "5": "#####|#....|####.|....#|....#|#...#|.###.",
    "6": "..##.|.#...|#....|####.|#...#|#...#|.###.", "7": "#####|....#|...#.|..#..|.#...|.#...|.#...",
    "8": ".###.|#...#|#...#|.###.|#...#|#...#|.###.", "9": ".###.|#...#|#...#|.####|....#|...#.|.##..",
    "A": ".###.|#...#|#...#|#####|#...#|#...#|#...#", "B": "####.|#...#|#...#|####.|#...#|#...#|####.",
    "C": ".###.|#...#|#....|#....|#....|#...#|.###.", "D": "###..|#..#.|#...#|#...#|#...#|#..#.|###..",
    "E": "#####|#....|#....|####.|#....|#....|#####", "F": "#####|#....|#....|####.|#....|#....|#....",
    "G": ".###.|#...#|#....|#.###|#...#|#...#|.####", "H": "#...#|#...#|#...#|#####|#...#|#...#|#...#",
    "I": ".###.|..#..|..#..|..#..|..#..|..#..|.###.", "J": "..###|...#.|...#.|...#.|...#.|#..#.|.##..",
    "K": "#...#|#..#.|#.#..|##...|#.#..|#..#.|#...#", "L": "#....|#....|#....|#....|#....|#....|#####",
    "M": "#...#|##.##|#.#.#|#.#.#|#...#|#...#|#...#", "N": "#...#|#...#|##..#|#.#.#|#..##|#...#|#...#",
    "O": ".###.|#...#|#...#|#...#|#...#|#...#|.###.", "P": "####.|#...#|#...#|####.|#....|#....|#....",
    "Q": ".###.|#...#|#...#|#...#|#.#.#|#..#.|.##.#", "R": "####.|#...#|#...#|####.|#.#..|#..#.|#...#",
    "S": ".####|#....|#....|.###.|....#|....#|####.", "T": "#####|..#..|..#..|..#..|..#..|..#..|..#..",
    "U": "#...#|#...#|#...#|#...#|#...#|#...#|.###.", "V": "#...#|#...#|#...#|#...#|#...#|.#.#.|..#..",
    "W": "#...#|#...#|#...#|#.#.#|#.#.#|#.#.#|.#.#.", "X": "#...#|#...#|.#.#.|..#..|.#.#.|#...#|#...#",
    "Y": "#...#|#...#|.#.#.|..#..|..#..|..#..|..#..", "Z": "#####|....#|...#.|..#..|.#...|#....|#####",
    " ": ".....|.....|.....|.....|.....|.....|.....", ".": ".....|.....|.....|.....|.....|.##..|.##..",
    ":": ".....|.##..|.##..|.....|.##..|.##..|.....", "-": ".....|.....|.....|#####|.....|.....|.....",
    "_": ".....|.....|.....|.....|.....|.....|#####", "/": ".....|....#|...#.|..#..|.#...|#....|.....",
    "|": "..#..|..#..|..#..|..#..|..#..|..#..|..#..", "+": ".....|..#..|..#..|#####|..#..|..#..|.....",
    "#": ".#.#.|.#.#.|#####|.#.#.|#####|.#.#.|.#.#.", "(": "...#.|..#..|.#...|.#...|.#...|..#..|...#.",
    ")": ".#...|..#..|...#.|...#.|...#.|..#..|.#...", ",": ".....|.....|.....|.....|.##..|..#..|.#...",
    "'": "..#..|..#..|.#...|.....|.....|.....|.....", "!": "..#..|..#..|..#..|..#..|..#..|.....|..#..",
    "?": ".###.|#...#|....#|...#.|..#..|.....|..#..", "=": ".....|.....|#####|.....|#####|.....|.....",
    "%": "##...|##..#|...#.|..#..|.#...|#..##|...##", "<": "...#.|..#..|.#...|#....|.#...|..#..|...#.",
    ">": ".#...|..#..|...#.|....#|...#.|..#..|.#...", "[": ".###.|.#...|.#...|.#...|.#...|.#...|.###.",
    "]": ".###.|...#.|...#.|...#.|...#.|...#.|.###.", "*": ".....|..#..|#.#.#|.###.|#.#.#|..#..|.....",
    "@": ".###.|#...#|#.###|#.#.#|#.###|#....|.###.", "&": ".##..|#..#.|#.#..|.#...|#.#.#|#..#.|.##.#",
    ";": ".....|.##..|.##..|.....|.##..|..#..|.#...", '"': ".#.#.|.#.#.|.#.#.|.....|.....|.....|.....",
    "~": ".....|.....|.#...|#.#.#|...#.|.....|.....", "^": "..#..|.#.#.|#...#|.....|.....|.....|.....",
    "$": "..#..|.####|#.#..|.###.|..#.#|####.|..#..", "\\": ".....|#....|.#...|..#..|...#.|....#|.....",
}
GLYPH_W, GLYPH_H, ADV_X, ADV_Y = 5, 7, 6, 9
_FONT = {k: np.array([[c == "#" for c in row] for row in v.split("|")], dtype=bool) for k, v in _GLYPHS.items()}


def _glyph(ch):
    g = _FONT.get(ch)
    if g is None:
        g = _FONT.get(ch.upper(), _FONT["?"])
    return g


def text_mask(text, scale=2):
    """Boolean mask (H x W) of `text` rendered with the bitmap font; '\\n' starts a new line."""
    lines = str(text).split("\n")
    ncol = max((len(l) for l in lines), default=0)
    if ncol == 0:
        return np.zeros((GLYPH_H * scale, 0), bool)
    H = (len(lines) - 1) * ADV_Y + GLYPH_H
    W = ncol * ADV_X - 1
    m = np.zeros((H, W), bool)
    for li, line in enumerate(lines):
        for ci, ch in enumerate(line):
            y0, x0 = li * ADV_Y, ci * ADV_X
            m[y0:y0 + GLYPH_H, x0:x0 + GLYPH_W] |= _glyph(ch)
    s = max(1, int(scale))
    if s > 1:
        m = np.repeat(np.repeat(m, s, axis=0), s, axis=1)
    return m


def text_size(text, scale=2, pad=None, bg=True):
    """(w, h) of the box draw_text would cover."""
    m = text_mask(text, scale)
    p = (max(1, int(scale)) if pad is None else int(pad)) if bg is not None else 0
    return m.shape[1] + 2 * p, m.shape[0] + 2 * p


def _color_for(img, color):
    if img.ndim == 2:
        if isinstance(color, (tuple, list, np.ndarray)):
            c = np.asarray(color, float)[:3]
            return np.uint8(round(float(c.mean()))) if c.size else np.uint8(255)
        return np.uint8(color)
    nch = img.shape[2]
    c = np.atleast_1d(np.asarray(color, np.float64))
    if c.size == 1:
        c = np.repeat(c, 3)
    c = list(c[:nch])
    if nch == 4 and len(c) == 3:
        c.append(255)
    return np.asarray(c, np.float64).clip(0, 255).round().astype(img.dtype if img.dtype == np.uint8 else np.float64)


def draw_text(img, text, x, y, scale=2, color=(255, 255, 255), bg=(0, 0, 0), pad=None, outline=None):
    """Draw `text` in place with the built-in 5x7 bitmap font. Top-left of the box at (x, y).

    scale: integer pixel multiplier (glyph = 5s x 7s px). bg: box colour or None (transparent).
    outline: colour of a 1-glyph-pixel halo around the strokes (use with bg=None on busy frames).
    pad: box padding in px (default = scale; also used for the outline). Clipped at the image edges;
    lowercase is drawn as uppercase, unknown characters as '?'. Works on HxW, HxWx3, HxWx4 (uint8 or
    float) images. Returns (w, h) of the box.
    """
    m = text_mask(text, scale)
    p = (max(1, int(scale)) if pad is None else int(pad)) if (bg is not None or outline is not None) else 0
    if outline is not None:
        mp = np.zeros((m.shape[0] + 2 * p, m.shape[1] + 2 * p), bool)
        mp[p:p + m.shape[0], p:p + m.shape[1]] = m
        halo = dilate(mp, 2 * p + 1) & ~mp
        H0, W0 = img.shape[:2]
        x0, y0 = max(0, int(x)), max(0, int(y))
        x1, y1 = min(W0, int(x) + mp.shape[1]), min(H0, int(y) + mp.shape[0])
        if bg is None and x1 > x0 and y1 > y0:
            region = img[y0:y1, x0:x1]
            region[halo[y0 - int(y):y1 - int(y), x0 - int(x):x1 - int(x)]] = _color_for(img, outline)
    bw, bh = m.shape[1] + 2 * p, m.shape[0] + 2 * p
    H, W = img.shape[:2]
    x, y = int(x), int(y)
    if bg is not None:
        x0, y0, x1, y1 = max(0, x), max(0, y), min(W, x + bw), min(H, y + bh)
        if x1 > x0 and y1 > y0:
            img[y0:y1, x0:x1] = _color_for(img, bg)
    tx, ty = x + p, y + p
    x0, y0 = max(0, tx), max(0, ty)
    x1, y1 = min(W, tx + m.shape[1]), min(H, ty + m.shape[0])
    if x1 > x0 and y1 > y0:
        sub = m[y0 - ty:y1 - ty, x0 - tx:x1 - tx]
        region = img[y0:y1, x0:x1]
        region[sub] = _color_for(img, color)
    return bw, bh


# --------------------------------------------------------------------------------------------------
# numpy image helpers
# --------------------------------------------------------------------------------------------------
def to_uint8(a):
    """Round + clip to uint8."""
    a = np.asarray(a)
    if a.dtype == np.uint8:
        return a.copy()
    return np.clip(np.rint(a.astype(np.float64)), 0, 255).astype(np.uint8)


def _area_axis(a, n_out, axis):
    n_in = a.shape[axis]
    a = np.moveaxis(a, axis, 0)
    cs = np.concatenate([np.zeros((1,) + a.shape[1:], np.float64), np.cumsum(a, axis=0, dtype=np.float64)], 0)
    edges = np.linspace(0.0, n_in, n_out + 1)
    i0 = np.floor(edges).astype(np.int64)
    fr = (edges - i0).reshape((-1,) + (1,) * (a.ndim - 1))
    i0c = np.minimum(i0, n_in - 1)
    val = cs[i0] + fr * a[i0c]
    out = (val[1:] - val[:-1]) * (n_out / n_in)
    return np.moveaxis(out, 0, axis)


def _lin_axis(a, n_out, axis):
    n_in = a.shape[axis]
    xs = np.clip((np.arange(n_out) + 0.5) * (n_in / n_out) - 0.5, 0, n_in - 1)
    i0 = np.floor(xs).astype(np.int64)
    i1 = np.minimum(i0 + 1, n_in - 1)
    f = (xs - i0).reshape([-1 if d == axis else 1 for d in range(a.ndim)])
    return np.take(a, i0, axis) * (1 - f) + np.take(a, i1, axis) * f


def _near_axis(a, n_out, axis):
    n_in = a.shape[axis]
    idx = np.minimum(((np.arange(n_out) + 0.5) * (n_in / n_out)).astype(np.int64), n_in - 1)
    return np.take(a, idx, axis)


def resize(img, w, h, method="area"):
    """Resize HxW[xC] to (h, w). method: 'area' (box average when shrinking, bilinear when growing),
    'bilinear', 'nearest'. uint8 in -> uint8 out; float in -> float64 out."""
    a = np.asarray(img)
    w, h = int(w), int(h)
    if a.shape[0] == h and a.shape[1] == w:
        return a.copy()
    is_u8 = a.dtype == np.uint8
    if method == "nearest":
        out = _near_axis(_near_axis(a, h, 0), w, 1)
        return out
    f = a.astype(np.float64)
    for axis, n in ((0, h), (1, w)):
        if f.shape[axis] == n:
            continue
        if method == "area" and n < f.shape[axis]:
            f = _area_axis(f, n, axis)
        else:
            f = _lin_axis(f, n, axis)
    return to_uint8(f) if is_u8 else f


def _box_axis(a, r, axis):
    if r <= 0:
        return a
    a = np.moveaxis(a, axis, 0)
    n = a.shape[0]
    p = np.concatenate([np.repeat(a[:1], r, 0), a, np.repeat(a[-1:], r, 0)], 0)
    cs = np.concatenate([np.zeros((1,) + a.shape[1:], np.float64), np.cumsum(p, 0, dtype=np.float64)], 0)
    out = (cs[2 * r + 1:2 * r + 1 + n] - cs[:n]) / (2 * r + 1)
    return np.moveaxis(out, 0, axis)


def box_blur(img, r, iterations=1):
    """Separable box blur, window 2r+1, edge-replicate. uint8 in -> uint8 out."""
    a = np.asarray(img)
    r = int(r)
    if r <= 0:
        return a.copy()
    f = a.astype(np.float64)
    for _ in range(max(1, int(iterations))):
        f = _box_axis(_box_axis(f, r, 0), r, 1)
    return to_uint8(f) if a.dtype == np.uint8 else f


def _conv_axis(a, k, axis):
    r = len(k) // 2
    a = np.moveaxis(a, axis, 0)
    n = a.shape[0]
    p = np.concatenate([np.repeat(a[:1], r, 0), a, np.repeat(a[-1:], r, 0)], 0)
    out = np.zeros_like(a, dtype=np.float64)
    for i, wgt in enumerate(k):
        out += wgt * p[i:i + n]
    return np.moveaxis(out, 0, axis)


def gauss_blur(img, sigma):
    """Separable Gaussian blur (exact kernel for sigma < 3, 3-pass box approximation above)."""
    a = np.asarray(img)
    s = float(sigma)
    if s <= 0:
        return a.copy()
    f = a.astype(np.float64)
    if s < 3.0:
        r = int(math.ceil(3 * s))
        x = np.arange(-r, r + 1, dtype=np.float64)
        k = np.exp(-0.5 * (x / s) ** 2)
        k /= k.sum()
        f = _conv_axis(_conv_axis(f, k, 0), k, 1)
    else:
        n = 3
        wi = math.sqrt(12 * s * s / n + 1)
        wl = int(math.floor(wi))
        if wl % 2 == 0:
            wl -= 1
        wu = wl + 2
        m = round((12 * s * s - n * wl * wl - 4 * n * wl - 3 * n) / (-4 * wl - 4))
        for i in range(n):
            r = ((wl if i < m else wu) - 1) // 2
            f = _box_axis(_box_axis(f, r, 0), r, 1)
    return to_uint8(f) if a.dtype == np.uint8 else f


def _slide(a, k, axis, fn, padval):
    r0 = k // 2
    r1 = k - 1 - r0
    a = np.moveaxis(a, axis, 0)
    n = a.shape[0]
    pad_shape0 = (r0,) + a.shape[1:]
    pad_shape1 = (r1,) + a.shape[1:]
    p = np.concatenate([np.full(pad_shape0, padval, a.dtype), a, np.full(pad_shape1, padval, a.dtype)], 0)
    out = p[0:n].copy()
    for s in range(1, k):
        fn(out, p[s:s + n], out=out)
    return np.moveaxis(out, 0, axis)


def _morph(mask, size, iterations, fn, extreme):
    a = np.asarray(mask)
    k = (max(1, int(size)) - 1) * max(1, int(iterations)) + 1  # square iterated n times == bigger square
    if k <= 1:
        return a.copy()
    if a.dtype == bool:
        padval = extreme != "max"  # dilate pads False, erode pads True (the border has no effect)
    elif np.issubdtype(a.dtype, np.integer):
        info = np.iinfo(a.dtype)
        padval = info.min if extreme == "max" else info.max
    else:
        padval = -np.inf if extreme == "max" else np.inf
    out = _slide(a, k, 0, fn, padval)
    return _slide(out, k, 1, fn, padval)


def dilate(mask, size=3, iterations=1):
    """Grey/binary dilation with a size x size square (iterations compose into a bigger square)."""
    return _morph(mask, size, iterations, np.maximum, "max")


def erode(mask, size=3, iterations=1):
    """Grey/binary erosion with a size x size square; the image border does not erode."""
    return _morph(mask, size, iterations, np.minimum, "min")


_LUMA = {"709": (0.2126, 0.7152, 0.0722), "601": (0.299, 0.587, 0.114)}


def luma(img, std="709"):
    """Float32 luma 0..255 (Rec.709 weights by default; std='601' for cv2-like gray)."""
    a = np.asarray(img)
    if a.ndim == 2:
        return a.astype(np.float32)
    r, g, b = _LUMA[std]
    a = a[..., :3].astype(np.float32)
    return a[..., 0] * r + a[..., 1] * g + a[..., 2] * b


def to_gray(img, std="709"):
    """uint8 HxW gray image."""
    return to_uint8(luma(img, std))


def rgb_to_hsv(img):
    """RGB (uint8 0..255 or float 0..1) -> float32 HxWx3 with H in degrees [0,360), S and V in [0,1]."""
    a = np.asarray(img)[..., :3].astype(np.float32)
    if np.asarray(img).dtype == np.uint8:
        a = a / 255.0
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx = a.max(-1)
    mn = a.min(-1)
    d = mx - mn
    s = np.where(mx > 0, d / np.maximum(mx, 1e-12), 0.0)
    safe = np.maximum(d, 1e-12)
    h = np.where(mx == r, ((g - b) / safe) % 6.0,
                 np.where(mx == g, (b - r) / safe + 2.0, (r - g) / safe + 4.0))
    h = np.where(d > 0, h * 60.0, 0.0) % 360.0
    return np.stack([h, s, mx], -1).astype(np.float32)


def hsv_to_rgb(hsv, as_uint8=True):
    """Inverse of rgb_to_hsv (H degrees, S/V 0..1). Returns uint8 0..255 (or float 0..1)."""
    h, s, v = hsv[..., 0] % 360.0 / 60.0, hsv[..., 1], hsv[..., 2]
    i = np.floor(h).astype(np.int64) % 6
    f = h - np.floor(h)
    p, q, t = v * (1 - s), v * (1 - s * f), v * (1 - s * (1 - f))
    r = np.choose(i, [v, q, p, p, t, v])
    g = np.choose(i, [t, v, v, q, p, p])
    b = np.choose(i, [p, p, t, v, v, q])
    out = np.stack([r, g, b], -1)
    return to_uint8(out * 255.0) if as_uint8 else out.astype(np.float32)


def saturation(img):
    """HSV saturation 0..1 (float32 HxW)."""
    return rgb_to_hsv(img)[..., 1]


def mse(a, b, mask=None):
    d = np.asarray(a, np.float64) - np.asarray(b, np.float64)
    d = d * d
    if mask is not None:
        m = np.asarray(mask).astype(bool)
        if d.ndim == 3 and m.ndim == 2:
            m = np.broadcast_to(m[..., None], d.shape)
        return float(d[m].mean()) if m.any() else 0.0
    return float(d.mean())


def psnr(a, b, mask=None, peak=255.0):
    """PSNR in dB (100.0 for identical inputs, so it stays JSON-safe)."""
    e = mse(a, b, mask)
    return 100.0 if e <= 1e-12 else float(min(100.0, 10 * math.log10(peak * peak / e)))


def fit_into(img, w, h, bg=(0, 0, 0), method="area"):
    """Letterbox `img` into a w x h canvas keeping aspect (centered)."""
    a = np.asarray(img)
    ih, iw = a.shape[:2]
    s = min(w / iw, h / ih)
    nw, nh = max(1, int(round(iw * s))), max(1, int(round(ih * s)))
    r = resize(a, nw, nh, method)
    shape = (h, w) + a.shape[2:]
    canvas = np.empty(shape, a.dtype)
    canvas[...] = _color_for(canvas, bg)
    y, x = (h - nh) // 2, (w - nw) // 2
    canvas[y:y + nh, x:x + nw] = r
    return canvas


# --------------------------------------------------------------------------------------------------
# contact sheets
# --------------------------------------------------------------------------------------------------
def tile_sheet(images, labels=None, cols=6, out_path=None, tile_w=256, max_bytes=500_000, max_w=1600,
               title=None, quality=82, gap=4, bg=(24, 24, 24), label_scale=None, min_quality=30):
    """Lay out images in a grid with bitmap-font labels and write a JPEG (or PNG) under max_bytes.

    images: arrays (HxWx3/HxW/HxWx4) or image paths; None -> blank tile. labels: str per tile (may
    contain '\\n') or None. Tiles keep their aspect (resized to tile_w wide, rows as tall as the
    tallest tile). The sheet is never wider than max_w (tile_w shrinks). JPEG quality steps down from
    `quality` to `min_quality`; if still too big the sheet is downscaled until it fits.
    Sizing for sandbox image_paths (<=4 files, <=512 KiB total): 1 sheet/call -> 500_000,
    2 -> 250_000, 4 -> 120_000.
    Returns {'path','bytes','quality','w','h','cols','rows','tile_w','tiles','scale'}; the encoded
    bytes are also in result['data'] when out_path is None.
    """
    imgs = [read_image(i) if isinstance(i, (str, os.PathLike)) else i for i in images]
    n = len(imgs)
    if n == 0:
        raise ValueError("tile_sheet: no images")
    labels = list(labels) if labels is not None else [None] * n
    labels += [None] * (n - len(labels))
    cols = max(1, min(int(cols), n))
    tile_w = int(tile_w)
    if cols * tile_w + (cols + 1) * gap > max_w:
        tile_w = max(16, (max_w - (cols + 1) * gap) // cols)
    rows = (n + cols - 1) // cols
    ls = int(label_scale) if label_scale else (1 if tile_w < 180 else 2 if tile_w < 420 else 3)
    tiles = []
    for im in imgs:
        if im is None:
            tiles.append(None)
            continue
        a = np.asarray(im)
        if a.dtype != np.uint8:
            a = to_uint8(a)
        if a.ndim == 2:
            a = np.repeat(a[:, :, None], 3, 2)
        elif a.shape[2] == 4:
            al = a[:, :, 3:4].astype(np.float32) / 255.0
            a = to_uint8(a[:, :, :3] * al + np.asarray(bg, np.float32) * (1 - al))
        th = max(1, int(round(a.shape[0] * tile_w / a.shape[1])))
        tiles.append(resize(a, tile_w, th, "area"))
    default_h = next((t.shape[0] for t in tiles if t is not None), tile_w)
    row_h = []
    for r in range(rows):
        hs = [t.shape[0] for t in tiles[r * cols:(r + 1) * cols] if t is not None]
        row_h.append(max(hs) if hs else default_h)
    title_h = 0
    tscale = 2 if tile_w * cols < 900 else 3
    if title:
        title_h = text_size(title, tscale)[1] + gap
    W = cols * tile_w + (cols + 1) * gap
    H = title_h + sum(row_h) + (rows + 1) * gap
    W += W % 2
    H += H % 2
    sheet = np.empty((H, W, 3), np.uint8)
    sheet[...] = np.asarray(bg, np.uint8)
    if title:
        draw_text(sheet, title, gap, gap, tscale, (255, 255, 255), (0, 0, 0))
    y = title_h + gap
    for r in range(rows):
        for c in range(cols):
            k = r * cols + c
            if k >= n:
                break
            x = gap + c * (tile_w + gap)
            t = tiles[k]
            if t is not None:
                oy = y + (row_h[r] - t.shape[0]) // 2
                sheet[oy:oy + t.shape[0], x:x + t.shape[1]] = t
            lab = labels[k]
            if lab:
                maxc = max(1, (tile_w - 2 * ls) // (ADV_X * ls))
                lines = [ln[:maxc] for ln in str(lab).split("\n")]
                txt = "\n".join(lines)
                tw, th_ = text_size(txt, ls)
                ty = y + row_h[r] - th_
                draw_text(sheet, txt, x, ty, ls, (255, 255, 255), (0, 0, 0))
        y += row_h[r] + gap
    fmt = "png" if out_path and str(out_path).lower().endswith(".png") else "jpg"
    scale = 1.0
    img = sheet
    while True:
        q = int(quality)
        data = encode_image(img, fmt, q)
        while fmt == "jpg" and len(data) > max_bytes and q > min_quality:
            q = max(min_quality, q - 8)
            data = encode_image(img, fmt, q)
        if len(data) <= max_bytes or img.shape[1] < 200:
            break
        f = math.sqrt(max_bytes / len(data)) * 0.95
        scale *= f
        nw = max(2, int(sheet.shape[1] * scale) // 2 * 2)
        nh = max(2, int(sheet.shape[0] * scale) // 2 * 2)
        img = resize(sheet, nw, nh, "area")
    res = {"path": str(out_path) if out_path else None, "bytes": len(data), "quality": q if fmt == "jpg" else None,
           "w": int(img.shape[1]), "h": int(img.shape[0]), "cols": cols, "rows": rows, "tile_w": tile_w,
           "tiles": n, "scale": round(scale, 4)}
    if out_path:
        _atomic_write_bytes(out_path, data)
    else:
        res["data"] = data
    return res


def video_sheet(path, out_path, indices=None, start=0, end=None, every=None, max_tiles=48, cols=8,
                tile_w=192, max_bytes=500_000, max_w=1600, crop=None, title=None, label_fmt="f{f} {t:.2f}s"):
    """Contact sheet of a video: explicit `indices`, or start..end (exclusive) every N frames
    (default N so that at most max_tiles tiles). Labels show frame index and start time f/fps."""
    p = probe(path)
    fps = p["fps"]
    if indices is None:
        n = p["nb_frames"]
        end = n if end is None else min(int(end), n)
        start = max(0, int(start))
        span = max(0, end - start)
        if every is None:
            every = max(1, math.ceil(span / max_tiles))
        indices = list(range(start, end, int(every)))
    if not indices:
        raise ValueError("video_sheet: no frames selected")
    pre_w = min(p["w"] if not crop else _norm_crop(crop, p["w"], p["h"])[2], tile_w * 2)
    frames = read_frames_at(path, indices, scale_w=pre_w, crop=crop, info=p, strict=False)
    labs = [label_fmt.format(f=i, t=i / float(fps)) if fr is not None else f"f{i} N/A"
            for i, fr in zip(indices, frames)]
    if title is None:
        title = f"{os.path.basename(str(path))}  {p['w']}x{p['h']}  {p['fps_str']}fps  {p['nb_frames']}f"
    res = tile_sheet(frames, labs, cols, out_path, tile_w, max_bytes, max_w, title=title)
    res["indices"] = list(indices)
    return res


# --------------------------------------------------------------------------------------------------
# JSON
# --------------------------------------------------------------------------------------------------
def jsonable(o):
    """Recursively convert Fractions ('n/d'), numpy types, tuples/sets, paths and NaN/inf (None)."""
    if isinstance(o, dict):
        return {str(k): jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple, set, frozenset)):
        return [jsonable(v) for v in o]
    if isinstance(o, Fraction):
        return f"{o.numerator}/{o.denominator}"
    if isinstance(o, np.ndarray):
        return jsonable(o.tolist())
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, (float, np.floating)):
        v = float(o)
        return v if math.isfinite(v) else None
    if isinstance(o, os.PathLike):
        return os.fspath(o)
    if isinstance(o, bytes):
        return o.decode("utf-8", "replace")
    return o


def save_json(path, obj, indent=1):
    """Atomic JSON write (UTF-8, indent). Also accepts the legacy order save_json(obj, path)."""
    if not isinstance(path, (str, os.PathLike)) and isinstance(obj, (str, os.PathLike)):
        path, obj = obj, path
    elif isinstance(path, str) and isinstance(obj, str) and not path.endswith(".json") and obj.endswith(".json"):
        path, obj = obj, path
    data = json.dumps(jsonable(obj), indent=indent, ensure_ascii=False) + "\n"
    _atomic_write_bytes(path, data.encode("utf-8"))
    return str(path)


_MISSING = object()


def load_json(path, default=_MISSING):
    """Load JSON; return `default` when the file is missing (raises if no default given)."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        if default is _MISSING:
            raise
        return default


# --------------------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------------------
def _font_chart(scale):
    rows = ["0123456789", "ABCDEFGHIJKLM", "NOPQRSTUVWXYZ", ".:-_/|+#()", ",'!?=%<>[]*@&;\"~^$\\",
            "f123 0:04.25 LOCK 1080X1920", "lowercase -> UPPER; unknown: é Ж"]
    txt = "\n".join(rows)
    w, h = text_size(txt, scale)
    img = np.full((h + 20, w + 20, 3), 40, np.uint8)
    draw_text(img, txt, 10, 10, scale, (255, 255, 255), (0, 0, 0))
    return img


def main(argv=None):
    ap = argparse.ArgumentParser(description="rrio: probe / frame / sheet / font helpers (ffmpeg + numpy).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("probe", help="print probe() JSON")
    a.add_argument("path")
    a.add_argument("--count", action="store_true", help="count decoded frames (exact, slower)")
    a = sub.add_parser("frame", help="export frame(s) by index to png/jpg")
    a.add_argument("path")
    a.add_argument("indices", help="comma list, e.g. 0,12,250")
    a.add_argument("out", help="output file; with several indices use a pattern containing {f}")
    a.add_argument("--scale-w", type=int)
    a.add_argument("--quality", type=int, default=90)
    a = sub.add_parser("sheet", help="labelled contact sheet of a video")
    a.add_argument("path")
    a.add_argument("out")
    a.add_argument("--start", type=int, default=0)
    a.add_argument("--end", type=int)
    a.add_argument("--every", type=int)
    a.add_argument("--indices", help="comma list (overrides start/end/every)")
    a.add_argument("--max-tiles", type=int, default=48)
    a.add_argument("--cols", type=int, default=8)
    a.add_argument("--tile-w", type=int, default=192)
    a.add_argument("--max-bytes", type=int, default=500_000)
    a.add_argument("--max-w", type=int, default=1600)
    a.add_argument("--crop", help="x,y,w,h")
    a.add_argument("--title")
    a = sub.add_parser("font", help="render the bitmap font chart (legibility check)")
    a.add_argument("out")
    a.add_argument("--scale", type=int, default=3)
    args = ap.parse_args(argv)

    if args.cmd == "probe":
        print(json.dumps(jsonable(probe(args.path, count=args.count)), indent=1))
    elif args.cmd == "frame":
        idx = [int(x) for x in args.indices.split(",") if x.strip()]
        frames = read_frames_at(args.path, idx, scale_w=args.scale_w)
        for i, fr in zip(idx, frames):
            out = args.out.format(f=i) if "{f" in args.out else args.out
            nb = write_image(out, fr, args.quality)
            print(f"wrote {out} ({fr.shape[1]}x{fr.shape[0]}, {nb} bytes)")
    elif args.cmd == "sheet":
        idx = [int(x) for x in args.indices.split(",")] if args.indices else None
        crop = [int(x) for x in args.crop.split(",")] if args.crop else None
        r = video_sheet(args.path, args.out, idx, args.start, args.end, args.every, args.max_tiles, args.cols,
                        args.tile_w, args.max_bytes, args.max_w, crop, args.title)
        r.pop("data", None)
        print(json.dumps(jsonable(r)))
    elif args.cmd == "font":
        nb = write_image(args.out, _font_chart(args.scale))
        print(f"wrote {args.out} ({nb} bytes)")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (FileNotFoundError, ValueError, IndexError, RuntimeError) as e:
        print(f"rrio: error: {e}", file=sys.stderr)
        sys.exit(1)
