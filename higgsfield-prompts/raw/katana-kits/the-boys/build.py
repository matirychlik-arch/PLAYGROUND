#!/usr/bin/env python3
"""the-boys: deterministic 1:1 assembly of the 32.54 s edit from generated clips.

Usage (inside the Higgsfield sandbox, kit unpacked to /home/user/tb/kit):
  python3 /home/user/tb/kit/build.py \
      --clips /home/user/tb/clips --audio /home/user/tb/audio.mp3 \
      --name "HELIARCH" --sub "THE GILDED" --out /home/user/tb/out/final.mp4 [--no-occlusion]

--clips must contain hero/<ID>.mp4 for every hero id in timeline.json (Genjutsu outputs,
named exactly H00, H01, T02, H03, g04, H05 ... H29) and broll/c1.mp4 .. broll/c4.mp4
(the four Seedance chapter generations). Everything else (cut points, speeds, grades,
letterbox, text timing, fonts, title occlusion) comes from timeline.json.
"""
import argparse, json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_FILES = ["Anton-Regular.ttf", "BebasNeue-Regular.ttf", "BarlowCondensed-SemiBoldItalic.ttf",
              "PlayfairDisplay-Italic[wght].ttf", "PlayfairDisplay[wght].ttf", "Inter[opsz,wght].ttf"]


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, stdin=subprocess.DEVNULL)
    if r.returncode:
        sys.exit(f"FAILED: {' '.join(cmd)[:400]}\n{r.stderr[-1500:]}")
    return r.stdout


class Builder:
    def __init__(self, a):
        self.a = a
        self.tl = json.load(open(a.timeline))
        self.W, self.H, self.FPS = self.tl["width"], self.tl["height"], self.tl["fps"]
        self.work = os.path.join(os.path.dirname(os.path.abspath(a.out)), "work")
        os.makedirs(self.work, exist_ok=True)
        self.fonts = a.fonts
        missing = [f for f in FONT_FILES if not os.path.exists(os.path.join(self.fonts, f))]
        if missing:
            sys.exit(f"missing fonts in {self.fonts}: {missing}")
        lb = self.tl["letterbox"]
        pw, ph = lb["picture_scale"]
        self.base = f"scale={pw}:{ph},setsar=1,pad={self.W}:{self.H}:0:{lb['picture_pad_y']}"
        override = json.load(open(a.starts)) if a.starts else {}
        self.starts = {c: override.get(c) or self.detect_starts(c) for c in ("c1", "c2", "c3", "c4")}
        print("[info] b-roll shot starts:", json.dumps(self.starts))

    # ---------- sources ----------
    def path(self, ref):
        if "hero" in ref:
            return os.path.join(self.a.clips, "hero", f"{ref['hero']}.mp4")
        return os.path.join(self.a.clips, "broll", f"{ref['broll']}.mp4")

    def detect_starts(self, chapter):
        planned = self.tl["broll_planned_starts"][chapter]
        p = os.path.join(self.a.clips, "broll", f"{chapter}.mp4")
        out = subprocess.run(["ffmpeg", "-hide_banner", "-i", p, "-vf", "select='gt(scene,0.2)',showinfo", "-an", "-f", "null", "-"],
                             capture_output=True, text=True).stderr
        cuts = sorted(float(x.split(":")[1]) for x in out.split() if x.startswith("pts_time:"))
        cuts = [c for i, c in enumerate(cuts) if i == 0 or c - cuts[i - 1] > 0.25]
        if len(cuts) == len(planned) - 1:
            return [0.0] + cuts
        # tolerant match: snap each planned start to the nearest detected cut within 0.8 s
        snapped = [0.0]
        for s in planned[1:]:
            near = [c for c in cuts if abs(c - s) < 0.8]
            snapped.append(min(near, key=lambda c: abs(c - s)) if near else s)
        print(f"[warn] {chapter}: {len(cuts)} cuts detected for {len(planned)} shots; using snapped plan {snapped}")
        return snapped

    def resolve(self, ref, t0, t1):
        """Return (path, in_point_seconds, speed)."""
        if "broll" in ref:
            st = self.starts[ref["broll"]]
            return self.path(ref), st[ref["shot"] - 1] + ref["offset"], ref.get("speed", 1.0)
        hid, tin, sp = ref["hero"], ref.get("tin", 0.0), ref.get("speed", 1.0)
        meta = self.tl["hero_clips"].get(hid)
        if meta and sp != 1.0:
            seg = t1 - t0
            if seg < 0.6:  # very short reference shot: play the clean middle of the generation
                tin, sp = 0.2, (meta["driver_dur"] - 0.45) / seg
            if meta.get("cut_at"):  # never run into the driver's trailing next-shot frames
                lim = meta["cut_at"] - 0.15
                if tin + seg * sp > lim:
                    sp = max(0.3, (lim - tin) / seg)
        return self.path(ref), tin, sp

    # ---------- segment renderers ----------
    def enc(self, out):
        return ["-c:v", "libx264", "-preset", "veryfast", "-crf", "14", "-pix_fmt", "yuv420p", out]

    def clip(self, ref, t0, t1, n, out):
        src, tin, sp = self.resolve(ref, t0, t1)
        pz = self.tl["punch_zoom"]
        punch = (f",scale=w='trunc({self.W}*(1+{pz['amount']}*max(0\\,1-n/{pz['frames']}))/2)*2':h=-2:eval=frame,crop={self.W}:{self.H}"
                 if n >= pz["min_frames"] else "")
        vf = (f"setpts=PTS/{sp}," if sp != 1.0 else "") + f"{self.base}{punch},{self.tl['fx'][ref['fx']]},fps={self.FPS},tpad=stop_mode=clone:stop_duration=6"
        run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{tin:.4f}", "-i", src, "-vf", vf, "-frames:v", str(n), "-an", *self.enc(out)])

    def color(self, c, n, out):
        run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"color={c}:s={self.W}x{self.H}:r={self.FPS}", "-frames:v", str(n), *self.enc(out)])

    def font(self, name, size, axes=None):
        f = ImageFont.truetype(os.path.join(self.fonts, name), size)
        if axes:
            try:
                vals = []
                for ax in f.get_variation_axes():
                    nm = ax.get("name", b"")
                    nm = (nm.decode() if isinstance(nm, bytes) else nm).lower()
                    if nm.startswith("weight") and "wght" in axes: vals.append(axes["wght"])
                    else: vals.append(ax.get("default", ax["minimum"]))
                f.set_variation_by_axes(vals)
            except Exception:
                pass
        return f

    def block_text(self, text, w, h, fill, gap=0.12):
        lines, outs = text.split("\n"), []
        f = self.font(self.tl["block_text"]["font"], 400)
        first_w = ImageDraw.Draw(Image.new("L", (8, 8))).textlength(lines[0], font=f)
        for s in lines:
            tmp = Image.new("L", (4000, 800), 0); ImageDraw.Draw(tmp).text((50, 50), s, font=f, fill=255)
            m = tmp.crop(tmp.getbbox())
            lw = w if s == lines[0] else int(w * m.width / max(1, first_w))
            outs.append(m.resize((max(1, lw), h), Image.LANCZOS))
        th = sum(o.height for o in outs) + int(h * gap) * (len(outs) - 1)
        canvas = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0)); y = (self.H - th) // 2
        for o in outs:
            solid = Image.new("RGBA", o.size, tuple(fill)); solid.putalpha(o)
            canvas.alpha_composite(solid, ((self.W - o.width) // 2, y)); y += o.height + int(h * gap)
        return canvas

    def card(self, text, box, n, out):
        im = Image.new("RGB", (self.W, self.H), (236, 236, 236))
        layer = self.block_text(text, box[0], box[1], (12, 12, 12, 255)); im.paste(layer, (0, 0), layer)
        p = out + ".png"; im.save(p)
        run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", p, "-vf", f"vignette=PI/5,fps={self.FPS}", "-frames:v", str(n), *self.enc(out)])

    def panels(self, refs, t0, t1, n, out, layout):
        tmp = []
        for k, ref in enumerate(refs):
            p = f"{out}.p{k}.mp4"; self.clip(ref, t0, t1, n, p); tmp.append(p)
        ins = sum([["-i", p] for p in tmp], [])
        W, H, F = self.W, self.H, self.FPS
        if layout == "split":
            pw = W // 3
            fc = "".join(f"[{k}:v]scale={pw}:{H}:force_original_aspect_ratio=increase,crop={pw}:{H}[p{k}];" for k in range(len(tmp)))
            fc += f"color=black:s={W}x{H}:r={F}[bg];"; cur = "bg"
            for k in range(len(tmp)):
                fc += f"[{cur}][p{k}]overlay={k*pw}:0:shortest=1" + ("" if k == len(tmp) - 1 else f"[o{k}];"); cur = f"o{k}"
        elif layout == "split2":
            pw = W // 2
            fc = "".join(f"[{k}:v]scale={pw}:{H}:force_original_aspect_ratio=increase,crop={pw}:{H}[p{k}];" for k in range(2)) + "[p0][p1]hstack=2"
        else:
            fc = "".join(f"[{k}:v]scale={W//2}:{H//2}[p{k}];" for k in range(4)) + "[p0][p1]hstack[a];[p2][p3]hstack[b];[a][b]vstack"
        run(["ffmpeg", "-y", "-loglevel", "error", *ins, "-filter_complex", fc, "-frames:v", str(n), *self.enc(out)])

    # ---------- text ----------
    def text_layer(self, text, style):
        st = self.tl["text_styles"][style]
        if style == "cond_red":
            w, h = self.tl["block_text"]["cond_red_box"]
            layer = self.block_text(text, w, h, st["rgba"])
        else:
            size = st["size"]
            target = self.tl["text_fit_widths"].get(text, st["fit_width"])
            tr = st["tracking_em"]
            def lw(f, s):
                d = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
                return sum(d.textlength(c, font=f) for c in s) + tr * f.size * (len(s) - 1)
            lines = text.split("\n")
            if target:
                f = self.font(st["font"], 200, st["axes"]); size = int(200 * target / max(lw(f, l) for l in lines))
            f = self.font(st["font"], size, st["axes"])
            layer = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0)); ld = ImageDraw.Draw(layer)
            lh = int(f.size * 1.15); y0 = self.H // 2 - lh * len(lines) // 2
            for i, s in enumerate(lines):
                x = (self.W - lw(f, s)) / 2
                for c in s:
                    ld.text((x, y0 + i * lh), c, font=f, fill=tuple(st["rgba"])); x += ld.textlength(c, font=f) + tr * f.size
        if st["glow_rgb"]:
            g = Image.new("RGBA", (self.W, self.H), tuple(st["glow_rgb"]) + (0,))
            g.putalpha(layer.split()[3].filter(ImageFilter.GaussianBlur(15)).point(lambda v: min(255, int(v * 1.55))))
            layer = Image.alpha_composite(g, layer)
        return layer

    # ---------- occlusion (title behind the hero's head) ----------
    def person_mask(self, src, dst):
        import numpy as np, onnxruntime as ort
        model = self.a.seg_model
        if not model or not os.path.exists(model):
            sys.exit("--seg-model is required for title occlusion (or pass --no-occlusion)")
        sess = ort.InferenceSession(model, providers=["CPUExecutionProvider"]); inp = sess.get_inputs()[0].name
        W, H = self.W, self.H
        p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-i", src, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
        o = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "gray", "-s", f"{W}x{H}", "-r", str(self.FPS), "-i", "-",
                              "-c:v", "libx264", "-crf", "12", "-pix_fmt", "yuv420p", dst], stdin=subprocess.PIPE)
        mean, std = np.array([0.485, 0.456, 0.406]), np.array([0.229, 0.224, 0.225])
        while True:
            b = p.stdout.read(W * H * 3)
            if len(b) < W * H * 3: break
            x = np.asarray(Image.frombytes("RGB", (W, H), b).resize((320, 320), Image.BILINEAR), dtype=np.float32) / 255.0
            x = (x / max(x.max(), 1e-6) - mean) / std
            m = sess.run(None, {inp: x.transpose(2, 0, 1)[None].astype(np.float32)})[0][0, 0]
            m = (m - m.min()) / (m.max() - m.min() + 1e-6)
            o.stdin.write(Image.fromarray((m * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR).filter(ImageFilter.GaussianBlur(2)).tobytes())
        o.stdin.close(); o.wait()

    # ---------- build ----------
    def build(self):
        fr = lambda t: int(round(t * self.FPS))
        parts, seg_file = [], {}
        for i, s in enumerate(self.tl["segments"]):
            t0, t1, ty = s["t0"], s["t1"], s["type"]; n = fr(t1) - fr(t0); out = os.path.join(self.work, f"s{i:03d}.mp4")
            if ty in ("hero", "clip"): self.clip(s, t0, t1, n, out)
            elif ty == "white": self.color("0xF0F0F0", n, out)
            elif ty == "black": self.color("0x060606", n, out)
            elif ty == "card": self.card(s["text"], s["box"], n, out)
            elif ty in ("split", "split2", "grid"): self.panels(s["panels"], t0, t1, n, out, ty)
            else: sys.exit(f"unknown segment type {ty}")
            parts.append(out); seg_file[t0] = out
        lst = os.path.join(self.work, "list.txt")
        open(lst, "w").writelines(f"file '{p}'\n" for p in parts)
        pic = os.path.join(self.work, "picture.mp4")
        run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", pic])

        ins, chain, cur = [], [], "g0"
        for k, t in enumerate(self.tl["texts"]):
            txt = t["text"].replace("{NAME}", self.a.name).replace("{SUB}", self.a.sub)
            layer = self.text_layer(txt, t["style"]); bb = layer.getbbox()
            canvas = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
            if bb:
                crop = layer.crop(bb); x = bb[0]
                if t.get("scale", 1.0) != 1.0:
                    crop = crop.resize((int(crop.width * t["scale"]), int(crop.height * t["scale"])), Image.LANCZOS); x = self.W // 2 - crop.width // 2
                canvas.paste(crop, (x, int(t["y"] * self.H) - crop.height // 2), crop)
            p = os.path.join(self.work, f"t{k:02d}.png"); canvas.save(p); ins += ["-i", p]
            chain.append(f"[{cur}][{k+1}:v]overlay=0:0:enable='between(t,{fr(t['t0'])/self.FPS:.4f},{(fr(t['t1'])-0.5)/self.FPS:.4f})'[v{k}]"); cur = f"v{k}"
        A = len(self.tl["texts"]) + 1
        occ_ins = []
        if not self.a.no_occlusion:
            for j, oc in enumerate(self.tl["occlusion"]):
                seg = seg_file[oc["segment_t0"]]; msk = seg.replace(".mp4", ".mask.mp4"); self.person_mask(seg, msk)
                vi, mi = A + 1 + 2 * j, A + 2 + 2 * j; off = oc["segment_t0"]; e0, e1 = oc["enable"]
                occ_ins += ["-i", seg, "-i", msk]
                chain.append(f"[{mi}:v]format=gray,setpts=PTS-STARTPTS+{off}/TB[m{j}];[{vi}:v]vignette=PI/6,setpts=PTS-STARTPTS+{off}/TB[f{j}];[f{j}][m{j}]alphamerge[fg{j}]")
                chain.append(f"[{cur}][fg{j}]overlay=0:0:eof_action=pass:enable='between(t,{e0},{e1})'[o{j}]"); cur = f"o{j}"
        lb = self.tl["letterbox"]
        grade = self.tl["grade"] + f",drawbox=x=0:y=0:w=iw:h={lb['top']}:color=black:t=fill,drawbox=x=0:y={self.H-lb['bottom']}:w=iw:h={lb['bottom']}:color=black:t=fill"
        fc = f"[0:v]{grade}[g0];" + ";".join(chain) + f";[{cur}]null[vout]"
        os.makedirs(os.path.dirname(os.path.abspath(self.a.out)), exist_ok=True)
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", pic, *ins, "-i", self.a.audio, *occ_ins, "-filter_complex", fc,
             "-map", "[vout]", "-map", f"{A}:a", "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p",
             "-r", str(self.FPS), "-c:a", "aac", "-b:a", "256k", "-t", str(self.tl["duration"]), "-movflags", "+faststart", self.a.out])
        print("ok", self.a.out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--timeline", default=os.path.join(HERE, "timeline.json"))
    ap.add_argument("--clips", required=True)
    ap.add_argument("--audio", required=True)
    ap.add_argument("--name", required=True, help="hero name for the title card, e.g. HELIARCH")
    ap.add_argument("--sub", default="", help="small line under the title, e.g. THE GILDED")
    ap.add_argument("--out", required=True)
    ap.add_argument("--fonts", default=os.path.join(HERE, "fonts"))
    ap.add_argument("--seg-model", default=os.path.join(HERE, "u2net_human_seg.onnx"))
    ap.add_argument("--no-occlusion", action="store_true")
    ap.add_argument("--starts", help="optional JSON {c1:[...shot start seconds], ...} overriding cut detection")
    Builder(ap.parse_args()).build()
