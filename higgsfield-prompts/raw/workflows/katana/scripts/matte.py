#!/usr/bin/env python3
"""matte.py - matte video -> alpha PNG sequence / mask video, subject bbox tracks, edge previews.

Higgsfield mattes come back WITHOUT alpha, so alpha is rebuilt here (all-ffmpeg fast path):
  remove_background (video_background_remover) -> H.264 person on black:
      --mode divide     alpha from matte / original (Katana/Yaong blend expression, white-cyc tuned):
                        if(lt(B,34), if(gt(A,10),255,0), clip((A*255/B-70)*1.9, 0, 255))
                        A = matte gray, B = original gray. Needs --orig (the clip the matte was made from).
      --mode threshold  no original at hand: alpha = clip((max(R,G,B) - 8) / 10) (person on black).
  sam_3_video -> binary white-on-black mask (or a cut-out on black: use --thresh 9):
      --mode binary     alpha = max(R,G,B) > --thresh (default 127).
Then: --close N  dilation xN + erosion xN (fills holes in hair/dark clothes; Yaong needed 8),
      --blur S   gblur sigma (soft edge, default 0.6), optional --keep-x x0:x1 (zero alpha outside a
      column range: SAM grabs rails and mics).

Subcommands
  alpha   --matte M.mp4 [--orig O.mp4] --mode divide|threshold|binary (--out DIR | --video OUT.mp4)
          [--size WxH] [--close 8] [--blur 0.6] [--fps F] [--format gray|rgba|cutout]
          -> DIR/a_00000.png ... (0-based = plate frame index; gray, or RGBA) + DIR/alpha.json
             and/or a mask video (gray in yuv420p, H.264 crf 10)
  bbox    SRC --out OUT.json [--src-mode alpha|threshold] [--thresh 128] [--sigma 0]
          -> per-frame subject box + alpha-weighted centroid + top point (cheap tracking without faces)
  preview --alpha DIR|MASK.mp4 --orig O.mp4 --frames 0,120,240 --out sheet.jpg [--bg magenta]
          -> orig composited over a flat colour with the alpha, next to the alpha: check edges at 100%

ffmpeg gotchas handled here: blend/alphamerge use shortest=1 (otherwise the lavfi colour source or the
longer input runs on); the colour source gets r=<plate fps> (its default 25 fps drifts against 24p
plates); both inputs are re-based with setpts=PTS-STARTPTS before blending.
"""
from __future__ import annotations

import argparse
import glob
import math
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402

import rrio  # noqa: E402

PROG = "matte.py"
DIVIDE_EXPR = "if(lt(B,34),if(gt(A,10),255,0),clip((A*255/B-70)*1.9,0,255))"


class UsageError(Exception):
    pass


def _size(spec, info):
    if not spec:
        return info["w"], info["h"]
    m = re.fullmatch(r"(\d+)[x:](\d+)", spec.strip())
    if not m:
        raise UsageError(f"--size must be WxH (got {spec!r})")
    w, h = int(m.group(1)), int(m.group(2))
    if w < 2 or h < 2:
        raise UsageError("--size too small")
    return w, h


def _keep_x(spec, w):
    if not spec:
        return None
    try:
        a, b = (float(v) for v in re.split(r"[:,]", spec))
    except ValueError:
        raise UsageError(f"--keep-x wants x0:x1 as fractions 0..1 or pixels (got {spec!r})") from None
    if a <= 1.0 and b <= 1.0:
        a, b = a * w, b * w
    x0, x1 = max(0, int(round(a))), min(w, int(round(b)))
    if x1 - x0 < 2:
        raise UsageError("--keep-x range is empty")
    return x0, x1


def build_alpha_graph(mode, w, h, close, blur, thresh, soft, keep, has_orig):
    """filter_complex producing [m] (gray alpha). Inputs: 0 = matte, 1 = original (divide)."""
    sc = f"scale={w}:{h}:flags=bilinear"
    g = []
    if mode == "divide":
        if not has_orig:
            raise UsageError("--mode divide needs --orig (the clip the matte was made from)")
        g.append(f"[0:v]setpts=PTS-STARTPTS,{sc},format=gray[ma]")
        g.append(f"[1:v]setpts=PTS-STARTPTS,{sc},format=gray[mb]")
        g.append(f"[ma][mb]blend=all_expr='{DIVIDE_EXPR}':shortest=1,format=gray[m0]")
    elif mode in ("threshold", "binary"):
        t = 8 if thresh is None and mode == "threshold" else (127 if thresh is None else thresh)
        s = (10 if mode == "threshold" else 1) if soft is None else soft
        s = max(1e-3, float(s))
        g.append(f"[0:v]setpts=PTS-STARTPTS,{sc},format=gbrp,extractplanes=g+b+r[pg][pb][pr]")
        g.append("[pg][pb]blend=all_mode=lighten[pgb]")
        lut = f"clip((val-{t})*255/{s},0,255)" if mode == "threshold" or s > 1 else f"if(gt(val,{t}),255,0)"
        g.append(f"[pgb][pr]blend=all_mode=lighten,format=gray,lut=y='{lut}'[m0]")
    else:
        raise UsageError(f"unknown mode {mode}")
    post = []
    post += ["dilation"] * int(close) + ["erosion"] * int(close)
    if keep:
        x0, x1 = keep
        post += [f"crop={x1 - x0}:{h}:{x0}:0", f"pad={w}:{h}:{x0}:0:black"]
    if blur and blur > 0:
        post.append(f"gblur=sigma={blur}")
    post.append("format=gray")
    g.append("[m0]" + ",".join(post) + "[m]")
    return g


def cmd_alpha(a):
    if not os.path.exists(a.matte):
        raise UsageError(f"matte not found: {a.matte}")
    if a.orig and not os.path.exists(a.orig):
        raise UsageError(f"original not found: {a.orig}")
    if not a.out and not a.video:
        raise UsageError("give --out DIR (PNG sequence) and/or --video OUT.mp4 (mask video)")
    mi = rrio.probe(a.matte)
    oi = rrio.probe(a.orig) if a.orig else None
    ref = oi or mi
    w, h = _size(a.size, ref)
    if a.video and (w % 2 or h % 2):
        raise UsageError(f"--video needs an even size, got {w}x{h} (use --size)")
    fps = rrio.parse_fps(a.fps) if a.fps else ref["fps"]
    if not fps:
        raise UsageError("cannot tell the fps: pass --fps")
    warns = []
    if oi:
        if mi["fps"] != oi["fps"]:
            warns.append(f"matte fps {mi['fps_str']} != original fps {oi['fps_str']} (blend syncs by time)")
        if mi["nb_frames"] != oi["nb_frames"]:
            warns.append(f"matte has {mi['nb_frames']} frames, original {oi['nb_frames']} (output = shorter)")
        if (mi["w"], mi["h"]) != (oi["w"], oi["h"]):
            warns.append(f"matte {mi['w']}x{mi['h']} != original {oi['w']}x{oi['h']} (both scaled to {w}x{h})")
    keep = _keep_x(a.keep_x, w)
    fmt = a.format
    if fmt == "cutout" and not a.orig:
        raise UsageError("--format cutout needs --orig")
    g = build_alpha_graph(a.mode, w, h, a.close, a.blur, a.thresh, a.soft, keep,
                          has_orig=bool(a.orig) and a.mode == "divide")
    inputs = ["-i", a.matte]
    orig_idx = None
    if a.orig and (a.mode == "divide" or fmt == "cutout"):
        inputs += ["-i", a.orig]
        orig_idx = 1
    if a.start or a.count:
        # frame range: trim every input identically (by index)
        rng = f"trim=start_frame={int(a.start or 0)}" + (f":end_frame={int(a.start or 0) + int(a.count)}"
                                                          if a.count else "")
        g = [s.replace("setpts=PTS-STARTPTS", f"{rng},setpts=PTS-STARTPTS", 1) if s.startswith("[0:v]")
             or s.startswith("[1:v]") else s for s in g]
    outs = []
    if a.out and a.video:
        g.append("[m]split=2[mo][mv]")
        tag_png, tag_vid = "mo", "mv"
    else:
        tag_png = tag_vid = "m"
    if a.out:
        if fmt == "rgba":
            g.append(f"color=c=white:s={w}x{h}:r={rrio.fps_str(fps)},format=rgba[white]")
            g.append(f"[white][{tag_png}]alphamerge=shortest=1,format=rgba[po]")
            tag_png = "po"
        elif fmt == "cutout":
            src = f"[{orig_idx}:v]" if orig_idx is not None else "[0:v]"
            rng = ""
            if a.start or a.count:
                rng = f"trim=start_frame={int(a.start or 0)}" + (
                    f":end_frame={int(a.start or 0) + int(a.count)}" if a.count else "") + ","
            g.append(f"{src}{rng}setpts=PTS-STARTPTS,scale={w}:{h}:flags=bicubic,format=rgba[orgb]")
            g.append(f"[orgb][{tag_png}]alphamerge=shortest=1,format=rgba[po]")
            tag_png = "po"
        os.makedirs(a.out, exist_ok=True)
        for fn in glob.glob(os.path.join(a.out, "a_*.png")):
            os.unlink(fn)
        outs += ["-map", f"[{tag_png}]", *rrio._passthrough(), "-pix_fmt", "rgba" if fmt != "gray" else "gray",
                 "-start_number", str(int(a.start or 0)), "-f", "image2", os.path.join(a.out, "a_%05d.png")]
    if a.video:
        os.makedirs(os.path.dirname(os.path.abspath(a.video)), exist_ok=True)
        outs += ["-map", f"[{tag_vid}]", *rrio._passthrough(), "-c:v", "libx264",
                 "-crf", str(a.crf), "-preset", "medium", "-pix_fmt", "yuv420p",
                 "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
                 "-movflags", "+faststart", a.video]
    rrio.run_ffmpeg([*inputs, "-filter_complex", ";".join(g), *outs])
    n_png = 0
    if a.out:
        n_png = len(glob.glob(os.path.join(a.out, "a_*.png")))
    expect = min(mi["nb_frames"], oi["nb_frames"]) if (oi and orig_idx is not None) else mi["nb_frames"]
    if a.start or a.count:
        expect = max(0, min(expect - int(a.start or 0), int(a.count) if a.count else 10 ** 9))
    res = {"matte": a.matte, "orig": a.orig, "mode": a.mode, "format": fmt, "w": w, "h": h,
           "fps": rrio.fps_str(fps), "close": a.close, "blur": a.blur, "thresh": a.thresh, "soft": a.soft,
           "keep_x": list(keep) if keep else None, "frames": n_png or None, "expected_frames": expect,
           "start_number": int(a.start or 0), "pattern": "a_%05d.png" if a.out else None,
           "video": a.video, "warnings": warns,
           "note": "a_<n>.png = plate frame n (0-based). 255 = subject. Composite: out = fg*a + bg*(1-a)."}
    if a.video:
        vi = rrio.probe(a.video, count=True)
        res["video_frames"] = vi["nb_frames"]
        if vi["nb_frames"] != expect:
            warns.append(f"mask video has {vi['nb_frames']} frames, expected {expect}")
    if a.out:
        if n_png != expect:
            warns.append(f"wrote {n_png} PNGs, expected {expect}")
        rrio.save_json(os.path.join(a.out, "alpha.json"), res)
        smp = None
        if n_png:
            mid = os.path.join(a.out, "a_%05d.png" % (int(a.start or 0) + n_png // 2))
            smp = rrio.read_image(mid, "gray") if fmt == "gray" else rrio.read_image(mid, "rgba")[..., 3]
        cov = f", mid-frame coverage {float((smp > 127).mean()) * 100:.1f}%" if smp is not None else ""
        print(f"{a.mode}: {n_png} alpha PNGs {w}x{h} ({fmt}) -> {os.path.join(a.out, 'a_%05d.png')}{cov}")
        print(f"   meta {os.path.join(a.out, 'alpha.json')}")
    if a.video:
        print(f"{a.mode}: mask video {res['video_frames']} frames {w}x{h} -> {a.video}")
    for wmsg in warns:
        print(f"{PROG}: warning: {wmsg}", file=sys.stderr)
    return 0


# --------------------------------------------------------------------------------------------------
# bbox
# --------------------------------------------------------------------------------------------------
def _open_src(src):
    """Alpha dir (a_*.png) / mask video / matte video -> dict(kind, path, first, n, w, h, fps, info)."""
    if os.path.isdir(src):
        files = sorted(glob.glob(os.path.join(src, "a_*.png")))
        if not files:
            raise UsageError(f"{src}: no a_*.png files")
        first = int(re.search(r"a_(\d+)\.png$", files[0]).group(1))
        p0 = rrio.probe(files[0])
        return {"kind": "seq", "path": os.path.join(src, "a_%05d.png"), "first": first, "n": len(files),
                "w": p0["w"], "h": p0["h"], "fps": None, "info": None}
    if not os.path.exists(src):
        raise UsageError(f"not found: {src}")
    info = rrio.probe(src)
    return {"kind": "video", "path": src, "first": 0, "n": info["nb_frames"], "w": info["w"], "h": info["h"],
            "fps": info["fps_str"], "info": info}


def _iter_src(s, scale_w=None, gray=True):
    """(frame_index, frame) over an _open_src() source; gray HxW or RGB HxWx3."""
    if s["kind"] == "video":
        yield from rrio.read_frames(s["path"], scale_w=scale_w, gray=gray, info=s["info"])
        return
    ow = int(scale_w) if scale_w else s["w"]
    oh = max(1, int(round(s["h"] * ow / s["w"])))
    ch = 1 if gray else 3
    cmd = [rrio.FFMPEG, "-hide_banner", "-nostdin", "-loglevel", "error", "-start_number", str(s["first"]),
           "-i", s["path"], "-vf", f"scale={ow}:{oh}:flags=area,format={'gray' if gray else 'rgb24'}",
           *rrio._passthrough(), "-f", "rawvideo", "-pix_fmt", "gray" if gray else "rgb24", "pipe:1"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    fb = ow * oh * ch
    k = 0
    try:
        while True:
            buf = proc.stdout.read(fb)
            if not buf or len(buf) < fb:
                break
            a = np.frombuffer(buf, np.uint8).copy()
            yield s["first"] + k, (a.reshape(oh, ow) if gray else a.reshape(oh, ow, 3))
            k += 1
    finally:
        proc.stdout.close()
        err = proc.stderr.read().decode("utf-8", "replace")
        proc.stderr.close()
        rc = proc.wait()
    if rc != 0:
        raise RuntimeError(f"reading {s['path']} failed: {err[-600:]}")


def _read_src_at(s, idx, gray=True):
    if s["kind"] == "video":
        return rrio.read_frames_at(s["path"], idx, gray=gray, info=s["info"])
    return [rrio.read_image(s["path"] % i, "gray" if gray else "rgb") for i in idx]


def _gauss_smooth(vals, valid, sigma, seg=None):
    """Gaussian smoothing over valid rows, never across segment boundaries (seg = segment id per row)."""
    if sigma <= 0:
        return vals
    out = vals.copy()
    n = len(vals)
    r = int(math.ceil(3 * sigma))
    k = np.exp(-0.5 * (np.arange(-r, r + 1) / sigma) ** 2)
    seg = np.zeros(n, np.int64) if seg is None else np.asarray(seg)
    for i in range(n):
        if not valid[i]:
            continue
        lo, hi = max(0, i - r), min(n, i + r + 1)
        m = valid[lo:hi] & (seg[lo:hi] == seg[i])
        wts = k[lo - i + r:hi - i + r][m]
        out[i] = (vals[lo:hi][m] * wts[:, None]).sum(0) / wts.sum()
    return out


def cmd_bbox(a):
    s = _open_src(a.SRC)
    W0, H0 = s["w"], s["h"]
    if a.to:
        W0, H0 = _size(a.to, s)  # report in another frame size (e.g. the plate's, for a half-res alpha)
    sw = min(s["w"], a.scale_w)
    sx = W0 / sw
    thr = a.thresh
    if a.src_mode == "threshold" and thr is None:
        thr = 8
    thr = 128 if thr is None else thr
    rows = []
    gray = a.src_mode != "threshold"
    yy = xx = None
    for f, fr in _iter_src(s, scale_w=sw, gray=gray):
        if a.src_mode == "threshold":
            al = fr.max(axis=2).astype(np.float32)
            m = al > thr
            wgt = np.clip((al - thr) / 10.0, 0, 1)
        else:
            al = fr.astype(np.float32)
            m = al >= thr
            wgt = al / 255.0
        if not m.any():
            rows.append({"f": f, "box": None, "cx": None, "cy": None, "area": 0.0, "top": None})
            continue
        if yy is None or yy.shape != fr.shape[:2]:
            yy, xx = np.mgrid[0:fr.shape[0], 0:fr.shape[1]]
        ys, xs = np.nonzero(m)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        tot = float(wgt.sum())
        cx = float((wgt * (xx + 0.5)).sum() / tot) if tot > 0 else (x0 + x1) / 2
        cy = float((wgt * (yy + 0.5)).sum() / tot) if tot > 0 else (y0 + y1) / 2
        top_row = np.nonzero(m[y0])[0]
        sy = H0 / fr.shape[0]
        rows.append({"f": f, "box": [round(x0 * sx, 1), round(y0 * sy, 1), round((x1 - x0) * sx, 1),
                                     round((y1 - y0) * sy, 1)],
                     "cx": round(cx * sx, 1), "cy": round(cy * sy, 1), "area": round(float(m.mean()), 5),
                     "top": [round((float(top_row.mean()) + 0.5) * sx, 1), round(y0 * sy, 1)]})
    if a.sigma > 0 and rows:
        valid = np.array([r["box"] is not None for r in rows])
        vals = np.array([(r["box"] + [r["cx"], r["cy"]] + r["top"]) if r["box"] else [0.0] * 8 for r in rows],
                        np.float64)
        # segments: split where the subject jumps (a hard cut in the plate) or at --cuts
        seg = np.zeros(len(rows), np.int64)
        cut_set = {int(c) for c in (a.cuts or "").split(",") if c.strip()}
        prev = None
        for i, r in enumerate(rows):
            seg[i] = seg[i - 1] if i else 0
            if r["f"] in cut_set:
                seg[i] += 1
            elif r["box"] and prev is not None:
                ratio = r["area"] / max(prev["area"], 1e-9)
                if not 0.67 <= ratio <= 1.5 or abs(r["cx"] - prev["cx"]) > 0.15 * W0:
                    seg[i] += 1
            if r["box"]:
                prev = r
        sm = _gauss_smooth(vals, valid, a.sigma, seg)
        for r, v, ok in zip(rows, sm, valid):
            if ok:
                r["box"] = [round(float(x), 1) for x in v[:4]]
                r["cx"], r["cy"] = round(float(v[4]), 1), round(float(v[5]), 1)
                r["top"] = [round(float(v[6]), 1), round(float(v[7]), 1)]
    n_ok = sum(1 for r in rows if r["box"])
    res = {"src": a.SRC, "src_mode": a.src_mode, "w": W0, "h": H0, "src_w": s["w"], "src_h": s["h"],
           "fps": s["fps"], "n": len(rows), "with_subject": n_ok,
           "thresh": thr, "sigma": a.sigma, "analysis_w": sw, "frames": rows,
           "note": "px in source coords; box=[x,y,w,h] of alpha>=thresh; cx,cy alpha-weighted centroid; "
                   "top = topmost subject point (head top); area = covered fraction"}
    rrio.save_json(a.out, res)
    areas = [r["area"] for r in rows if r["box"]]
    print(f"bbox: {len(rows)} frames, subject in {n_ok}, median area "
          f"{(float(np.median(areas)) * 100 if areas else 0):.1f}% -> {a.out}")
    return 0


# --------------------------------------------------------------------------------------------------
# preview
# --------------------------------------------------------------------------------------------------
_BG = {"magenta": (255, 0, 255), "green": (0, 255, 0), "black": (0, 0, 0), "white": (255, 255, 255),
       "blue": (0, 0, 255)}


def cmd_preview(a):
    s = _open_src(a.alpha)
    oi = rrio.probe(a.orig)
    idx = [int(v) for v in a.frames.split(",") if v.strip()]
    if not idx:
        raise UsageError("--frames is empty")
    bg = _BG.get(a.bg) or tuple(int(v) for v in a.bg.split(","))
    origs = rrio.read_frames_at(a.orig, idx, info=oi)
    alphas = _read_src_at(s, idx, gray=True)
    tiles, labels = [], []
    crop = None
    if a.crop:
        crop = tuple(int(v) for v in a.crop.split(","))
    for i, o, al in zip(idx, origs, alphas):
        if al.shape != o.shape[:2]:
            al = rrio.resize(al, o.shape[1], o.shape[0], "bilinear")
        af = al.astype(np.float32)[..., None] / 255.0
        comp = rrio.to_uint8(o.astype(np.float32) * af + np.asarray(bg, np.float32) * (1 - af))
        av = np.repeat(al[..., None], 3, 2)
        if crop:
            x, y, w, h = crop
            comp, av = comp[y:y + h, x:x + w], av[y:y + h, x:x + w]
        tiles += [comp, av]
        labels += [f"f{i} over {a.bg}", f"f{i} alpha"]
    res = rrio.tile_sheet(tiles, labels, cols=a.cols, out_path=a.out, tile_w=a.tile_w, max_bytes=a.max_bytes,
                          title=f"matte check {os.path.basename(a.orig)}" + (f" crop {a.crop}" if crop else ""))
    print(f"preview {a.out} ({res['bytes']} bytes, {len(idx)} frames)")
    return 0


# --------------------------------------------------------------------------------------------------
def build_parser():
    ap = argparse.ArgumentParser(prog=PROG, description="Rebuild alpha from Higgsfield mattes (no-alpha "
                                 "person-on-black / SAM masks), subject bbox tracks, edge previews.",
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("alpha", help="matte video -> alpha PNG sequence and/or mask video")
    p.add_argument("--matte", required=True, help="remove_background / sam_3_video output")
    p.add_argument("--orig", help="the clip the matte was made from (needed for divide and cutout)")
    p.add_argument("--mode", required=True, choices=["divide", "threshold", "binary"])
    p.add_argument("--out", help="output dir for a_00000.png ...")
    p.add_argument("--video", help="also/instead write a mask video (.mp4)")
    p.add_argument("--size", help="WxH output size (default: the original's size)")
    p.add_argument("--close", type=int, default=8, help="dilation/erosion passes (default 8; 0 = off)")
    p.add_argument("--blur", type=float, default=0.6, help="gblur sigma (default 0.6; 0 = off)")
    p.add_argument("--thresh", type=float, help="threshold/binary level (defaults 8 / 127)")
    p.add_argument("--soft", type=float, help="ramp width above --thresh (defaults 10 / 1 = hard)")
    p.add_argument("--keep-x", help="zero alpha outside x0:x1 (fractions 0..1 or px)")
    p.add_argument("--fps", help="fps for the colour source (default: original/matte fps)")
    p.add_argument("--format", default="gray", choices=["gray", "rgba", "cutout"],
                   help="gray alpha (default) | rgba = white + alpha | cutout = original RGB + alpha")
    p.add_argument("--start", type=int, help="first frame (index)")
    p.add_argument("--count", type=int, help="number of frames")
    p.add_argument("--crf", type=int, default=10, help="mask video crf (default 10)")
    p.set_defaults(fn=cmd_alpha)

    p = sub.add_parser("bbox", help="per-frame subject bbox + centroid JSON from alpha/mask/matte")
    p.add_argument("SRC", help="alpha dir (a_*.png), mask video, or person-on-black matte (--src-mode threshold)")
    p.add_argument("--out", required=True)
    p.add_argument("--src-mode", default="alpha", choices=["alpha", "threshold"],
                   help="alpha = gray alpha/mask (default) | threshold = max(RGB) of a person-on-black matte")
    p.add_argument("--thresh", type=float, help="subject level (alpha default 128, threshold default 8)")
    p.add_argument("--scale-w", type=int, default=480, help="analysis width (default 480)")
    p.add_argument("--sigma", type=float, default=0.0, help="temporal gaussian smoothing in frames (default 0)")
    p.add_argument("--cuts", help="frame indices where a new shot starts (smoothing never crosses them; "
                   "big area/centroid jumps split too)")
    p.add_argument("--to", help="WxH: report coordinates in this frame size (default: the source's own size)")
    p.set_defaults(fn=cmd_bbox)

    p = sub.add_parser("preview", help="edge check sheet: original over a flat colour + alpha")
    p.add_argument("--alpha", required=True, help="alpha dir (a_*.png) or mask video")
    p.add_argument("--orig", required=True)
    p.add_argument("--frames", required=True, help="comma list of frame indices")
    p.add_argument("--out", required=True)
    p.add_argument("--bg", default="magenta", help="magenta | green | black | white | blue | r,g,b")
    p.add_argument("--crop", help="x,y,w,h crop for a 100%% edge look")
    p.add_argument("--cols", type=int, default=2)
    p.add_argument("--tile-w", type=int, default=780)
    p.add_argument("--max-bytes", type=int, default=500_000)
    p.set_defaults(fn=cmd_preview)
    return ap


def main(argv=None):
    a = build_parser().parse_args(argv)
    try:
        return a.fn(a)
    except (UsageError, FileNotFoundError, ValueError, IndexError) as e:
        print(f"{PROG}: error: {e}", file=sys.stderr)
        return 1
    except RuntimeError as e:
        print(f"{PROG}: error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
