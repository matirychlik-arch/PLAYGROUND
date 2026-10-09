/* katana canvas compositor engine (RRC) - deterministic, EDL-driven Canvas2D renderer.
 *
 * Loaded by page.html in headless Chromium: engine.js -> RRC.boot({edl, fx}) -> window.renderFrame(i).
 * - Coordinates: logical canvas px (EDL canvas.w x canvas.h). The physical canvas is logical * rs
 *   (rs=0.5 for --preview). Every drawing context carries the base transform rs; use px(v) for
 *   lengths the transform does not scale (ctx.filter blur, shadow blur/offset).
 * - Time: frame f is sampled at t = (f + 0.5) / fps. A shot covers frames whose sample time is in
 *   [t0, t1). Local time lt = t - shot.t0. Source frame si = floor((src + lt*speed) * clip.fps).
 *   Slow motion (0.3 <= |speed| < 1, shot.blend not false): the plate is the two neighbouring source
 *   frames blended by the fractional index x = (src + lt*speed) * clip.fps - 0.5 (never before the
 *   in-point); below 0.3, blend:false, freezes (speed 0) and stutters show whole frames. srcPick().
 * - Randomness: only hash(a,b,c) / rng(seed) seeded by frame, boil step b = floor(f / boil) and
 *   effect seeds, so any frame renders identically in any process, in any order.
 * - Effects live in tables: LOOKS, CAMERA, LAYERS, TRANSITIONS, FACE, TEXT, STICKERS, DOODLES,
 *   SPECIALS. Project code (comp/fx.js) adds entries with RRC.register(table, name, entry) and hooks
 *   with RRC.hook(name, fn). Full schema and parameters: references/compositing.md.
 */
(function (G) {
  "use strict";
  const RRC = (G.RRC = G.RRC || {});
  RRC.version = "1.0.0";

  // ============================================================ math, randomness, easing
  function hash(a, b = 0, c = 0) {
    let h =
      Math.imul((a | 0) ^ 0x9e3779b9, 0x85ebca6b) ^
      Math.imul((b | 0) + 0x632be5ab, 0xc2b2ae35) ^
      Math.imul((c | 0) + 0x7f4a7c15, 0x27d4eb2f);
    h ^= h >>> 15;
    h = Math.imul(h, 0x2c1b3c6d);
    h ^= h >>> 12;
    h = Math.imul(h, 0x297a2d39);
    h ^= h >>> 15;
    return (h >>> 0) / 4294967296;
  }
  const hs = (a, b, c) => hash(a, b, c) * 2 - 1;
  function rng(seed) {
    let s = Math.imul(Math.round(seed * 1000) | 0, 2654435761) >>> 0 || 1;
    return () => (s = (Math.imul(s, 1664525) + 1013904223) >>> 0) / 4294967296;
  }
  const clamp = (v, a = 0, b = 1) => (v < a ? a : v > b ? b : v);
  const lerp = (a, b, t) => a + (b - a) * t;
  const TAU = Math.PI * 2;
  const EASE = {
    lin: (t) => t,
    in2: (t) => t * t,
    in3: (t) => t * t * t,
    out2: (t) => 1 - (1 - t) * (1 - t),
    out3: (t) => 1 - Math.pow(1 - t, 3),
    inout: (t) => t * t * (3 - 2 * t),
    outback: (t) => {
      const c = 1.70158;
      return 1 + (c + 1) * Math.pow(t - 1, 3) + c * Math.pow(t - 1, 2);
    },
  };
  const ease = (name, t) => (EASE[name] || EASE.lin)(clamp(t));
  const easeOut = (t) => 1 - Math.pow(1 - clamp(t), 3);
  // smooth 1-D noise in [-1,1] (sum of three hashed sines) - handheld drift
  const noise1 = (seed, t, hz = 1) => {
    let v = 0;
    for (let i = 0; i < 3; i++) {
      const f = hz * (0.6 + hash(seed, i, 1) * 1.1) * (1 + i * 0.9);
      v += Math.sin(TAU * (f * t + hash(seed, i, 2))) / (1 + i);
    }
    return v / 1.83;
  };
  const hit = (a, b) => a[0] < b[2] && a[2] > b[0] && a[1] < b[3] && a[3] > b[1];
  const padR = (r, p) => [r[0] - p, r[1] - p, r[2] + p, r[3] + p];
  const unionR = (Rs) => [
    Math.min(...Rs.map((r) => r[0])),
    Math.min(...Rs.map((r) => r[1])),
    Math.max(...Rs.map((r) => r[2])),
    Math.max(...Rs.map((r) => r[3])),
  ];

  // ============================================================ render context
  const R = {
    W: 1440,
    H: 1080,
    fps: 24,
    nf: 0,
    rs: 1,
    PW: 1440,
    PH: 1080,
    boil: 2,
    E: null,
    clips: {},
    shots: [],
    specials: [],
    shotOf: null,
    specOf: null,
    palette: {},
    ctx: null,
    canvas: null,
    L: {},
    beat: { t0: 0, dur: 0.5 },
    warnings: [],
    stickers: [],
    cutouts: [],
    sevt: [],
    texts: [],
    hooks: {},
    fonts: {},
    log: (m) => console.log(m),
  };
  RRC.R = R;
  const PALETTE = {
    ink: "#0b0b0b",
    paper: "#ffffff",
    accent: "#b6ff1f",
    accent2: "#6fd600",
    white: "#ffffff",
    black: "#000000",
    lav: "#c98be0",
    lavl: "#efdcf8",
    pink: "#f6c6ef",
    blush: "#ff92cf",
    earin: "#ffb6e1",
    outline: "rgb(226,176,240)",
    bigfill: "rgba(246,200,242,0.96)",
    bigstroke: "#e9a3e6",
    magenta: "rgba(236,70,190,1)",
    magenta2: "rgba(255,150,225,1)",
  };
  const FONTS = {
    heavy:
      '"Arial Black", "Montserrat", "Metropolis", "Helvetica Neue", "Liberation Sans", "DejaVu Sans", sans-serif',
    sans: '"Helvetica Neue", "Montserrat", "Metropolis", Arial, "Liberation Sans", "DejaVu Sans", sans-serif',
  };
  const warned = new Set();
  function warn(m) {
    if (warned.has(m)) return;
    warned.add(m);
    R.warnings.push(m);
    R.log("WARN " + m);
  }

  // colour: '#hex', 'rgb()', [r,g,b(,a)], '$palette' reference
  function col(c, fb) {
    if (c === undefined || c === null || c === false) return fb;
    if (Array.isArray(c))
      return c.length > 3
        ? `rgba(${c[0]},${c[1]},${c[2]},${c[3]})`
        : `rgb(${c[0]},${c[1]},${c[2]})`;
    if (typeof c === "string" && c[0] === "$") {
      const v = R.palette[c.slice(1)];
      return v === undefined ? fb : col(v, fb);
    }
    return c;
  }
  function rgbOf(c, fb = [0, 0, 0]) {
    if (Array.isArray(c)) return c.slice(0, 3);
    const s = col(c, null);
    if (!s) return fb;
    let m = /^#([0-9a-f]{6})$/i.exec(s);
    if (m) {
      const v = parseInt(m[1], 16);
      return [v >> 16, (v >> 8) & 255, v & 255];
    }
    m = /^#([0-9a-f]{3})$/i.exec(s);
    if (m) return [...m[1]].map((h) => parseInt(h + h, 16));
    m = /rgba?\(([^)]+)\)/.exec(s);
    if (m)
      return m[1]
        .split(",")
        .slice(0, 3)
        .map((v) => parseFloat(v));
    return fb;
  }
  const withAlpha = (c, a) => {
    const [r, g, b] = rgbOf(c);
    return `rgba(${r | 0},${g | 0},${b | 0},${a})`;
  };

  // ============================================================ canvases
  function mk(w, h, rf) {
    const c = document.createElement("canvas");
    c.width = Math.max(1, Math.round(w));
    c.height = Math.max(1, Math.round(h));
    c.x = c.getContext("2d", rf ? { willReadFrequently: true } : undefined);
    return c;
  }
  const pmk = (rf) => mk(R.PW, R.PH, rf);
  function reset(x) {
    x.setTransform(R.rs, 0, 0, R.rs, 0, 0);
    x.globalAlpha = 1;
    x.globalCompositeOperation = "source-over";
    x.filter = "none";
    x.shadowColor = "rgba(0,0,0,0)";
    x.shadowBlur = 0;
    x.shadowOffsetX = 0;
    x.shadowOffsetY = 0;
    x.setLineDash([]);
    x.lineCap = "butt";
    x.lineJoin = "miter";
    x.imageSmoothingEnabled = true;
    x.textAlign = "start";
    x.textBaseline = "alphabetic";
  }
  // copy a physical-size canvas 1:1 (ignores the base transform)
  function copyFull(dst, src, op, alpha, filter) {
    dst.save();
    dst.setTransform(1, 0, 0, 1, 0, 0);
    if (op) dst.globalCompositeOperation = op;
    if (alpha !== undefined) dst.globalAlpha = alpha;
    if (filter) dst.filter = filter;
    dst.drawImage(src.canvas || src, 0, 0);
    dst.restore();
  }
  const px = (v) => v * R.rs;
  const setM = (x, M, s = R.rs) =>
    x.setTransform(M[0] * s, M[1] * s, M[2] * s, M[3] * s, M[4] * s, M[5] * s);
  const mapM = (M, X, Y) => [M[0] * X + M[2] * Y + M[4], M[1] * X + M[3] * Y + M[5]];

  // ============================================================ loading
  const IMG = new Map(),
    PIN = new Map();
  const IMG_MAX = 80;
  const wurl = (p) => (/^(https?:|data:|blob:|\/)/.test(p) ? p : "/" + p);
  async function loadBitmap(url) {
    try {
      const r = await fetch(wurl(url), { cache: "no-store" });
      if (!r.ok) return null;
      const b = await r.blob();
      return await createImageBitmap(b);
    } catch (e) {
      return null;
    }
  }
  function img(url, pin) {
    if (!url) return Promise.resolve(null);
    let p = PIN.get(url);
    if (p) return p;
    p = IMG.get(url);
    if (p) {
      IMG.delete(url);
      IMG.set(url, p);
      return p;
    }
    p = loadBitmap(url);
    (pin ? PIN : IMG).set(url, p);
    if (!pin && IMG.size > IMG_MAX) IMG.delete(IMG.keys().next().value);
    return p;
  }
  async function fetchJSON(url) {
    try {
      const r = await fetch(wurl(url), { cache: "no-store" });
      if (!r.ok) return null;
      return await r.json();
    } catch (e) {
      return null;
    }
  }
  const fmtPat = (pat, i) => pat.replace(/%0?(\d*)d/, (m, w) => String(i).padStart(+w || 0, "0"));
  const framePath = (C, i) =>
    `${C.frames_dir}/${fmtPat(C.pattern, clamp(i, 0, C.n - 1) + C.start)}`;
  const maskPath = (C, i) =>
    C.mask_dir
      ? `${C.mask_dir}/${fmtPat(C.mask_pattern, clamp(i, 0, C.mask_n - 1) + C.mask_start)}`
      : null;

  // ============================================================ EDL normalisation
  // absolute time fields accept seconds, "b8.5" (beats on edl.beat) or "f59" (frame start)
  function T(v) {
    if (v === undefined || v === null) return undefined;
    if (typeof v === "number") return v;
    if (typeof v === "string") {
      const s = v.trim();
      if (s[0] === "b") return R.beat.t0 + parseFloat(s.slice(1)) * R.beat.dur;
      if (s[0] === "f") return parseFloat(s.slice(1)) / R.fps;
      return parseFloat(s);
    }
    return undefined;
  }
  const firstFrame = (t) => Math.max(0, Math.ceil(t * R.fps - 0.5 - 1e-6));
  RRC.T = T;
  RRC.firstFrame = firstFrame;
  // animated parameter {from,to,ease,over}: evaluated on the shot's local progress
  function av(v, S) {
    if (v && typeof v === "object" && !Array.isArray(v) && "from" in v && "to" in v) {
      const d = (v.over ?? 1) * (S && S.dur ? S.dur : 1),
        u = S ? (S.lt - (v.at ?? 0)) / Math.max(1e-6, d) : 0;
      if (Array.isArray(v.from))
        return v.from.map((a, i) => lerp(a, v.to[i], ease(v.ease || "lin", u)));
      return lerp(v.from, v.to, ease(v.ease || "lin", u));
    }
    return v;
  }
  function resolveParams(p, S) {
    const o = {};
    for (const k in p) o[k] = av(p[k], S);
    return o;
  }

  async function initClips(E) {
    for (const [id, c0] of Object.entries(E.clips || {})) {
      const c = { id, ...c0 };
      c.frames_dir = (c.frames_dir || c.dir || `plates/${id}`).replace(/\/$/, "");
      if (c.mask_dir === undefined && c.mask === true) c.mask_dir = `mattes/${id}`;
      if (c.mask_dir) c.mask_dir = c.mask_dir.replace(/\/$/, "");
      if (!c.n || !c.fps || !c.w || !c.h || !c.pattern) {
        const m = await fetchJSON(c.frames_dir + "/clip.json");
        if (m)
          for (const k of [
            "n",
            "fps",
            "w",
            "h",
            "pattern",
            "start",
            "src_w",
            "src_h",
            "src_start_frame",
          ])
            if (c[k] === undefined && m[k] !== undefined) c[k] = m[k];
      }
      c.pattern = c.pattern || "%05d.jpg";
      c.start = c.start || 0;
      if (typeof c.fps === "string") {
        const [a, b] = c.fps.split("/").map(Number);
        c.fps = b ? a / b : a;
      }
      if (c.mask_dir) {
        const mm = await fetchJSON(c.mask_dir + "/clip.json");
        c.mask_pattern = c.mask_pattern || (mm && mm.pattern) || "%05d.png";
        c.mask_n = c.mask_n || (mm && mm.n) || c.n;
        c.mask_start = c.mask_start ?? (mm && mm.start) ?? 0;
      }
      if (!c.n || !c.w || !c.h || !c.fps)
        throw new Error(
          `clip ${id}: n/fps/w/h unknown - run render.py prep (writes ${c.frames_dir}/clip.json) or set them in the EDL`,
        );
      if (c.faces) {
        const F = await fetchJSON(c.faces),
          meta =
            F && Array.isArray(F)
              ? await fetchJSON(c.faces.replace(/\.json$/, ".meta.json"))
              : null;
        if (F) {
          c.facesRaw = normFaces(c, F, meta);
          c.track = buildTrack(c, c.facesRaw);
          if (!c.track) warn(`clip ${id}: faces file has no usable faces`);
        } else warn(`clip ${id}: faces file ${c.faces} not found`);
      }
      R.clips[id] = c;
    }
  }

  // ---------------------------------------------------------------- faces: tolerant reader
  // Accepts per-frame entries in any of: {f, box:[x,y,w,h], eyes:[[x,y],[x,y]], nose, mouth}
  // (pixel or normalised), YuNet-style {box, kps:[re,le,nose,rm,lm]}, Chrome FaceDetector dumps
  // {x,y,w (centre, normalised), eye:[[x,y],[x,y]], mouth, nose} and {bb, lm:{eye:[poly,poly], mouth:[poly]}}.
  // Top level: list, or {w,h,units:'px'|'norm', frames:[...]}. Pixel coords are scaled by clip.w / file w.
  const isNum = (v) => typeof v === "number" && isFinite(v);
  const ptOf = (v) =>
    !v
      ? null
      : isNum(v[0])
        ? v
        : Array.isArray(v[0]) && isNum(v[0][0])
          ? [v.reduce((a, p) => a + p[0], 0) / v.length, v.reduce((a, p) => a + p[1], 0) / v.length]
          : Array.isArray(v[0])
            ? ptOf(v[0])
            : null;
  function normFaces(c, F, meta) {
    const arr = Array.isArray(F) ? F : F.frames || F.faces || F.track || [];
    let maxv = 0,
      seen = 0;
    const scan = (v) => {
      if (isNum(v)) maxv = Math.max(maxv, Math.abs(v));
      else if (Array.isArray(v)) v.forEach(scan);
      else if (v && typeof v === "object")
        for (const k of ["box", "bb", "bbox", "eyes", "eye", "x", "y", "mouth", "nose", "kps"])
          if (k in v) scan(v[k]);
    };
    for (const e of arr) {
      if (e && seen < 40) {
        scan(e);
        seen++;
      }
    }
    const units = F.units || (maxv <= 2.0 ? "norm" : "px");
    // pixel files: size from the file, its faces.py .meta.json or clip.faces_size; otherwise plate pixels, unless the
    // coordinates overflow the plate and prep recorded a larger source size (faces.py run on the original video)
    let maxx = 0;
    arr.forEach((e) => {
      if (e) {
        const b = e.box || e.bb;
        if (Array.isArray(b) && isNum(b[0])) maxx = Math.max(maxx, b[0] + (b[2] || 0));
      }
    });
    let fw = F.w || F.width || (meta && meta.w) || (c.faces_size && c.faces_size[0]),
      fh = F.h || F.height || (meta && meta.h) || (c.faces_size && c.faces_size[1]);
    if (!fw && units === "px" && c.src_w && c.src_w !== c.w && maxx > c.w * 1.02) {
      fw = c.src_w;
      fh = c.src_h;
      warn(
        `clip ${c.id}: faces look like source pixels (${c.src_w}x${c.src_h}); set clips.${c.id}.faces_size to be explicit`,
      );
    }
    const off = c.src_start_frame || 0;
    const sx = units === "norm" ? c.w : fw ? c.w / fw : 1,
      sy = units === "norm" ? c.h : fh ? c.h / fh : 1;
    const out = Array.from({ length: c.n }, () => null);
    arr.forEach((e, i) => {
      if (!e) return;
      const f = (e.f ?? e.frame ?? i) - off;
      if (f < 0 || f >= c.n) return;
      const n = normFace(e, sx, sy);
      if (n) out[f] = n;
    });
    return out;
  }
  function normFace(e, sx, sy) {
    const P = (p) => (p ? [p[0] * sx, p[1] * sy] : null);
    let box = e.box || e.bb || e.bbox || null;
    if (box && !Array.isArray(box)) box = [box.x, box.y, box.w ?? box.width, box.h ?? box.height];
    if (box) box = [box[0] * sx, box[1] * sy, box[2] * sx, box[3] * sy];
    else if (isNum(e.x) && isNum(e.w)) {
      const w = e.w * sx,
        h = isNum(e.h) ? e.h * sy : w;
      box = [e.x * sx - w / 2, e.y * sy - h / 2, w, h];
    }
    const lm = e.lm || e.landmarks || {};
    let kps = e.kps || (Array.isArray(e.landmarks) ? e.landmarks : null);
    let eyes = e.eyes || e.eye || lm.eye || lm.eyes || (kps ? [kps[0], kps[1]] : null);
    eyes = eyes && eyes.length >= 2 ? [P(ptOf(eyes[0])), P(ptOf(eyes[1]))] : null;
    if (eyes && (!eyes[0] || !eyes[1])) eyes = null;
    if (eyes && eyes[0][0] > eyes[1][0]) eyes = [eyes[1], eyes[0]];
    const nose = P(ptOf(e.nose || lm.nose || (kps ? kps[2] : null)));
    let m = e.mouth || lm.mouth || (kps ? [kps[3], kps[4]] : null),
      mouth = null,
      mouthL = null,
      mouthR = null;
    if (m) {
      if (isNum(m[0])) mouth = P(m);
      else if (Array.isArray(m[0]) && Array.isArray(m[0][0])) m = m[0];
      if (!mouth && Array.isArray(m[0]) && isNum(m[0][0])) {
        const pts = m.map(P);
        mouth = [
          pts.reduce((a, p) => a + p[0], 0) / pts.length,
          pts.reduce((a, p) => a + p[1], 0) / pts.length,
        ];
        if (pts.length >= 2) {
          mouthL = pts.reduce((a, p) => (p[0] < a[0] ? p : a));
          mouthR = pts.reduce((a, p) => (p[0] > a[0] ? p : a));
        }
      }
    }
    if (!box && !eyes) return null;
    return { box, eyes, nose, mouth, mouthL, mouthR, score: e.score ?? e.conf ?? 1 };
  }
  // Yaong-style track: eye midpoint (cx,cy), eye distance d, roll a, mouth (mx,my), gaps filled,
  // Gaussian-smoothed over +-7 source frames. ok=false where no detection within +-6 frames.
  function buildTrack(c, faces) {
    const raw = faces.map((F) => {
      if (!F) return null;
      let cx, cy, d, a;
      if (F.eyes) {
        const [p, q] = F.eyes;
        cx = (p[0] + q[0]) / 2;
        cy = (p[1] + q[1]) / 2;
        d = Math.hypot(q[0] - p[0], q[1] - p[1]);
        a = Math.atan2(q[1] - p[1], q[0] - p[0]);
      } else {
        const [x, y, w, h] = F.box;
        cx = x + w / 2;
        cy = y + h * 0.4;
        d = w * 0.42;
        a = 0;
      }
      if (!(d > 1)) return null;
      const mx = F.mouth ? F.mouth[0] : cx - Math.sin(a) * d * 1.1,
        my = F.mouth ? F.mouth[1] : cy + Math.cos(a) * d * 1.1;
      const mc =
          F.mouthL && F.mouthR
            ? Math.hypot(F.mouthR[0] - F.mouthL[0], F.mouthR[1] - F.mouthL[1])
            : 0,
        mw = mc > d * 0.3 ? mc : d * 0.85;
      const b = F.box || [cx - d * 1.25, cy - d * 1.35, d * 2.5, d * 3.0];
      return { cx, cy, d, a, mx, my, mw, bx: b[0], by: b[1], bw: b[2], bh: b[3] };
    });
    const n = raw.length;
    if (!raw.some(Boolean)) return null;
    const near = new Int32Array(n).fill(1e9);
    let last = -1e9;
    for (let i = 0; i < n; i++) {
      if (raw[i]) last = i;
      near[i] = i - last;
    }
    last = 1e9;
    for (let i = n - 1; i >= 0; i--) {
      if (raw[i]) last = i;
      near[i] = Math.min(near[i], last - i);
    }
    const filled = raw.slice();
    for (let i = 0; i < n; i++)
      if (!filled[i]) {
        for (let k = 1; k < n; k++) {
          const g = raw[i - k] || raw[i + k];
          if (g) {
            filled[i] = { ...g };
            break;
          }
        }
      }
    const sig = {
      cx: 1.4,
      cy: 1.4,
      d: 2.6,
      a: 2.6,
      mx: 1.4,
      my: 1.4,
      mw: 2.6,
      bx: 1.4,
      by: 1.4,
      bw: 2.6,
      bh: 2.6,
    };
    return filled.map((_, i) => {
      const o = { ok: near[i] <= 6 };
      for (const k in sig) {
        let s = 0,
          ws = 0;
        for (let j = -7; j <= 7; j++) {
          const g = filled[i + j];
          if (!g) continue;
          const w = Math.exp((-j * j) / (2 * sig[k] * sig[k]));
          s += g[k] * w;
          ws += w;
        }
        o[k] = s / ws;
      }
      return o;
    });
  }

  const SPECIAL_CLIPS = { FLASH: "flash", WHITE: "white", BLACK: "black", COLLAGE: "collage" };
  function normEDL(E) {
    const cv = E.canvas || {};
    R.W = cv.w || 1440;
    R.H = cv.h || 1080;
    R.fps = cv.fps || 24;
    if (typeof R.fps === "string") {
      const [a, b] = R.fps.split("/").map(Number);
      R.fps = b ? a / b : a;
    }
    R.boil = cv.boil || 2;
    R.beat = { t0: (E.beat && E.beat.t0) || 0, dur: 60 / ((E.beat && E.beat.bpm) || 120) };
    R.palette = { ...PALETTE, ...E.palette };
    Object.assign(FONTS, E.font_stacks || {});
    R.camDefault = E.cam || {};
    const shots = (E.shots || [])
      .map((s, i) => {
        const o = { ...s, i, fx: { ...s.fx } };
        o.t0 = s.f0 !== undefined ? s.f0 / R.fps : T(s.t0 ?? 0);
        o.t1 = s.f1 !== undefined ? s.f1 / R.fps : T(s.t1);
        if (o.clip && SPECIAL_CLIPS[o.clip] && !E.clips?.[o.clip]) {
          o.special = o.special || SPECIAL_CLIPS[o.clip];
        }
        if (typeof o.special === "string") o.special = { type: o.special };
        // transition sugar: in/out -> fx entries
        for (const side of ["in", "out"]) {
          const tr = s[side];
          if (!tr) continue;
          (Array.isArray(tr) ? tr : [tr]).forEach((t0) => {
            const t = typeof t0 === "string" ? { type: t0 } : t0;
            const name = (TR_SUGAR[t.type] || {})[side];
            if (name) o.fx[name] = { ...t, side };
            else warn(`shot ${i}: unknown ${side} transition ${t.type}`);
          });
        }
        return o;
      })
      .sort((a, b) => a.t0 - b.t0 || a.i - b.i);
    const end = cv.frames ? cv.frames / R.fps : cv.dur ? T(cv.dur) : undefined;
    shots.forEach((s, k) => {
      s.k = k;
      if (s.t1 === undefined) s.t1 = k + 1 < shots.length ? shots[k + 1].t0 : end;
      if (s.t1 === undefined) throw new Error("canvas.frames (or the last shot t1) is required");
      s.f0 = firstFrame(s.t0);
      s.f1 = firstFrame(s.t1);
      s.dur = Math.max(1e-6, s.t1 - s.t0);
      s.speed = s.speed ?? 1;
      if (s.srcf !== undefined && s.src === undefined) s.srcFrame = s.srcf;
      s.src = s.src ?? 0;
    });
    R.nf =
      cv.frames ||
      (cv.dur ? Math.round(T(cv.dur) * R.fps) : Math.max(0, ...shots.map((s) => s.f1)));
    R.shots = shots;
    R.shotOf = new Int32Array(R.nf).fill(-1);
    shots.forEach((s) => {
      for (let f = s.f0; f < Math.min(s.f1, R.nf); f++) R.shotOf[f] = s.k;
    });
    R.specials = (E.specials || []).map((sp, i) => {
      const o = { ...sp, i, type: sp.type || "flash" };
      o.t0 = sp.f0 !== undefined ? sp.f0 / R.fps : T(sp.t0);
      o.t1 =
        sp.f1 !== undefined
          ? sp.f1 / R.fps
          : sp.n !== undefined
            ? (firstFrame(o.t0) + sp.n) / R.fps
            : sp.d !== undefined
              ? o.t0 + sp.d
              : T(sp.t1);
      if (o.t1 === undefined) o.t1 = (firstFrame(o.t0) + 1) / R.fps;
      o.f0 = firstFrame(o.t0);
      o.f1 = Math.max(o.f0 + 1, firstFrame(o.t1));
      return o;
    });
    R.specOf = new Int32Array(R.nf).fill(-1);
    R.specials.forEach((s, i) => {
      for (let f = s.f0; f < Math.min(s.f1, R.nf); f++) R.specOf[f] = i;
    });
  }

  // ============================================================ frame state + camera
  function wrapIdx(si, C, mode) {
    if (mode === "loop") si = ((si % C.n) + C.n) % C.n;
    else if (mode === "pingpong") {
      const p = 2 * (C.n - 1) || 1;
      si = ((si % p) + p) % p;
      if (si >= C.n) si = p - si;
    }
    return clamp(si, 0, C.n - 1);
  }
  // Source frame(s) for a shot-like object o {src|srcFrame, speed, speed1, dur, loop, blend, fx.stutter} at local
  // time lt (k = output frames since the shot start, for stutter). Returns {si, blend, v}: si = the whole source
  // frame (faces, mattes, trail and fx.js key on it); blend = {i0, i1, w} when the plate is drawn as
  // (1 - w) * frame i0 + w * frame i1; v = playback speed at lt.
  // Slow-mo rule: 0.3 <= |v| < 1 blends the two neighbouring source frames by the fractional index (default);
  // blend:true forces it for any 0 < |v| < 1; blend:false or |v| < 0.3 = nearest frame (fast limbs / very slow
  // shots, where a blend reads as a ghost or a matte halo); speed 0 (freeze) and stutter hold whole frames.
  const BLEND_MIN = 0.3;
  function srcPick(o, C, lt, k = 0) {
    const fr = C.fps,
      s0 = o.speed ?? 1,
      mode = o.loop || "clamp",
      stt = (o.fx || {}).stutter;
    const base = o.srcFrame !== undefined ? o.srcFrame / fr + 1e-7 : (o.src ?? 0);
    let st = base + lt * s0,
      v = s0;
    if (o.speed1 !== undefined) {
      const u = clamp(lt / Math.max(1e-6, o.dur || 1));
      st = base + lt * (s0 + ((o.speed1 - s0) * u) / 2);
      v = s0 + (o.speed1 - s0) * u;
    }
    const b0 = Math.floor(base * fr + 1e-6);
    if (stt) {
      const p = stt === true ? {} : stt,
        n = p.n || 3;
      return { si: wrapIdx(b0 + (k % n) * (p.step || 1), C, mode), blend: null, v: 0 };
    }
    const si = wrapIdx(Math.floor(st * fr + 1e-6), C, mode),
      a = Math.abs(v);
    let blend = null;
    if (
      o.blend !== false &&
      a > 1e-6 &&
      a < 1 - 1e-9 &&
      (o.blend === true || a >= BLEND_MIN - 1e-9)
    ) {
      let x = st * fr - 0.5; // frame i is centred on (i + 0.5) / fps, so round(x) == si
      if (v > 0 && x < b0) x = b0; // never mix in the frame before the in-point
      const lo = Math.floor(x + 1e-9),
        w = x - lo;
      if (w > 1 / 512 && w < 1 - 1 / 512) {
        const i0 = wrapIdx(lo, C, mode),
          i1 = wrapIdx(lo + 1, C, mode);
        if (i0 !== i1) blend = { i0, i1, w };
      }
    }
    return { si, blend, v };
  }
  // draw the picked source frame(s) with the current transform; returns the nearest frame's bitmap
  async function drawPick(x, C, pk) {
    const [im, a, b] = await Promise.all([
      img(framePath(C, pk.si)),
      pk.blend ? img(framePath(C, pk.blend.i0)) : null,
      pk.blend ? img(framePath(C, pk.blend.i1)) : null,
    ]);
    if (pk.blend && a && b) {
      const ga = x.globalAlpha;
      x.drawImage(a, 0, 0, C.w, C.h);
      x.globalAlpha = ga * pk.blend.w;
      x.drawImage(b, 0, 0, C.w, C.h);
      x.globalAlpha = ga;
    } else if (im) x.drawImage(im, 0, 0, C.w, C.h);
    return im;
  }
  function stateAt(f) {
    const t = (f + 0.5) / R.fps,
      b = Math.floor(f / R.boil);
    const S = { f, t, b, W: R.W, H: R.H, fps: R.fps, k: -1, kind: "empty", keep: [] };
    const k = R.shotOf[f];
    S.k = k;
    const sh = k >= 0 ? R.shots[k] : null;
    S.shot = sh;
    if (sh) {
      S.lt = t - sh.t0;
      S.dur = sh.dur;
      S.u = clamp(S.lt / sh.dur);
      S.fx = sh.fx;
    } else {
      S.lt = 0;
      S.dur = 1;
      S.u = 0;
      S.fx = {};
    }
    const si = R.specOf[f];
    if (si >= 0) {
      const sp = R.specials[si];
      S.kind = "special";
      S.special = sp;
      S.lt = t - sp.t0;
      S.dur = sp.t1 - sp.t0;
      S.u = clamp(S.lt / S.dur);
      S.fx = {};
      return S;
    }
    if (!sh) return S;
    if (sh.special) {
      S.kind = "special";
      S.special = sh.special;
      return S;
    }
    const C = R.clips[sh.clip];
    if (!C) {
      S.kind = "missing";
      warn(`shot ${sh.i}: unknown clip ${sh.clip}`);
      return S;
    }
    const pk = srcPick(sh, C, S.lt, f - sh.f0);
    S.kind = "plate";
    S.clip = C;
    S.si = pk.si;
    S.blend = pk.blend;
    S.speed = pk.v;
    camera(S);
    return S;
  }
  RRC.stateAt = stateAt;

  const CAM_ORDER = ["zoom", "push", "punch", "ladder", "pan", "tilt", "roll", "handheld", "shake"];
  // camera settings for a shot: edl.cam < clips.<id>.cam < shot.cam (or an explicit override)
  const camOf = (sh, C, camOverride) => ({
    ...R.camDefault,
    ...(C && C.cam),
    ...(camOverride || (sh && sh.cam)),
  });
  // crop centre [x, y] (0..1 of the source) or y alone -> null | [x, y]
  const cropOf = (cam) =>
    cam.crop === undefined || cam.crop === null || cam.crop === false
      ? null
      : Array.isArray(cam.crop)
        ? [cam.crop[0] ?? 0.5, cam.crop[1] ?? 0.5]
        : [0.5, +cam.crop];
  function camera(S, camOverride) {
    const sh = S.shot,
      C = S.clip,
      cam = camOf(sh, C, camOverride);
    const fit = cam.fit || "cover",
      crop = cropOf(cam);
    const k0 =
      fit === "contain"
        ? Math.min(R.W / C.w, R.H / C.h)
        : fit === "width"
          ? R.W / C.w
          : fit === "height"
            ? R.H / C.h
            : Math.max(R.W / C.w, R.H / C.h);
    // crop: [x, y] = the source point shown at the screen centre, clamped so no plate edge shows (Genjutsu 4:3 take
    // cover-cropped to 16:9: y 0.3-0.4 keeps heads in; anything <= 0.375 means "top of the take")
    const g = {
      ax: (crop ? crop[0] : (cam.ax ?? 0.5)) * C.w,
      ay: (crop ? crop[1] : (cam.ay ?? 0.5)) * C.h,
      tx: (cam.sx ?? 0.5) * R.W,
      ty: (cam.sy ?? 0.5) * R.H,
      k: k0 * (cam.z ?? 1),
      th: cam.rot || 0,
      mir: !!cam.mir,
      cover: !!cam.cover || !!crop,
      dx: 0,
      dy: 0,
      k0,
    };
    if ((cam.type === "facelock" || cam.lock) && C.track) CAMERA.facelock.apply(S, cam, g);
    else if ((cam.type === "facelock" || cam.lock) && !C.track)
      warn(`shot ${sh.i}: facelock without faces for clip ${C.id}`);
    for (const name of CAM_ORDER) {
      let p = cam[name];
      if (p === undefined && sh.fx) p = sh.fx[name];
      if (p === undefined || p === null || p === false || !CAMERA[name]) continue;
      CAMERA[name].apply(S, p === true ? {} : typeof p === "number" ? { v: p } : p, g, cam);
    }
    for (const [name, ent] of Object.entries(CAMERA)) {
      if (CAM_ORDER.includes(name) || name === "facelock" || !ent.custom) continue;
      const p = cam[name];
      if (p !== undefined && p !== false) ent.apply(S, p === true ? {} : p, g, cam);
    }
    if (g.cover) coverFix(C, g);
    g.tx += g.dx;
    g.ty += g.dy;
    S.cam = g;
    S.M = buildM(g);
    faceOnScreen(S);
  }
  function buildM(g) {
    const c = Math.cos(g.th) * g.k,
      s = Math.sin(g.th) * g.k;
    let a = c,
      b = s,
      cc = -s,
      d = c,
      e = g.tx - (a * g.ax + cc * g.ay),
      f = g.ty - (b * g.ax + d * g.ay);
    if (g.mir) {
      a = -a;
      cc = -cc;
      e = R.W - e;
    }
    return [a, b, cc, d, e, f];
  }
  // enlarge/shift so the plate covers the whole canvas (port of the Yaong lockX loop)
  function coverFix(C, g) {
    const cs = Math.cos(g.th),
      sn = Math.sin(g.th);
    for (let it = 0; it < 6; it++) {
      let x0 = 1e9,
        x1 = -1e9,
        y0 = 1e9,
        y1 = -1e9;
      for (const [ox0, oy] of [
        [0, 0],
        [R.W, 0],
        [0, R.H],
        [R.W, R.H],
      ]) {
        const ox = g.mir ? R.W - ox0 : ox0,
          dx = (ox - g.tx - g.dx) / g.k,
          dy = (oy - g.ty - g.dy) / g.k;
        const sx = cs * dx + sn * dy + g.ax,
          sy = -sn * dx + cs * dy + g.ay;
        x0 = Math.min(x0, sx);
        x1 = Math.max(x1, sx);
        y0 = Math.min(y0, sy);
        y1 = Math.max(y1, sy);
      }
      const need = Math.max((x1 - x0) / C.w, (y1 - y0) / C.h);
      if (need > 1.0001) {
        g.k *= need * 1.003;
        continue;
      }
      if (x0 < 0) g.ax -= x0;
      else if (x1 > C.w) g.ax -= x1 - C.w;
      if (y0 < 0) g.ay -= y0;
      else if (y1 > C.h) g.ay -= y1 - C.h;
      break;
    }
  }
  // face model on screen: eye midpoint (x,y), eye distance D, roll a, mouth, box. fp() maps eye units.
  function faceOnScreen(S) {
    const sh = S.shot,
      C = S.clip;
    let tr = null;
    S.fo = null;
    if (sh.face === false) return;
    if (sh.face && sh.face.box) {
      const [x0, y0, x1, y1] = sh.face.box,
        w = x1 - x0,
        h = y1 - y0;
      tr = {
        cx: x0 + w / 2,
        cy: y0 + h * 0.42,
        d: w * 0.4,
        a: 0,
        mx: x0 + w / 2,
        my: y0 + h * 0.78,
        mw: w * 0.34,
        bx: x0,
        by: y0,
        bw: w,
        bh: h,
        ok: true,
      };
    } else if (C.track) tr = C.track[S.si];
    if (!tr) return;
    const M = S.M,
      ca = Math.cos(tr.a),
      sa = Math.sin(tr.a);
    let e0 = mapM(M, tr.cx - (ca * tr.d) / 2, tr.cy - (sa * tr.d) / 2),
      e1 = mapM(M, tr.cx + (ca * tr.d) / 2, tr.cy + (sa * tr.d) / 2);
    if (e1[0] < e0[0]) [e0, e1] = [e1, e0];
    const x = (e0[0] + e1[0]) / 2,
      y = (e0[1] + e1[1]) / 2,
      D = Math.hypot(e1[0] - e0[0], e1[1] - e0[1]),
      a = Math.atan2(e1[1] - e0[1], e1[0] - e0[0]);
    const [mx, my] = mapM(M, tr.mx, tr.my);
    const cs = [
      [tr.bx, tr.by],
      [tr.bx + tr.bw, tr.by],
      [tr.bx, tr.by + tr.bh],
      [tr.bx + tr.bw, tr.by + tr.bh],
    ].map((p) => mapM(M, p[0], p[1]));
    const box = [
      Math.min(...cs.map((p) => p[0])),
      Math.min(...cs.map((p) => p[1])),
      Math.max(...cs.map((p) => p[0])),
      Math.max(...cs.map((p) => p[1])),
    ];
    S.fo = { x, y, D, a, mx, my, mw: tr.mw * S.cam.k, w: D * 2.4, box, ok: tr.ok, e0, e1 };
  }
  function fp(S, ox, oy) {
    const F = S.fo || foOr(S);
    const ca = Math.cos(F.a),
      sa = Math.sin(F.a);
    return [F.x + (ox * ca - oy * sa) * F.D, F.y + (ox * sa + oy * ca) * F.D];
  }
  // face model for effects that need one even without a track (screen centre fallback)
  const foOr = (S) =>
    S.fo || {
      x: R.W / 2,
      y: R.H * 0.42,
      D: R.W * 0.1,
      a: 0,
      mx: R.W / 2,
      my: R.H * 0.55,
      mw: R.W * 0.08,
      w: R.W * 0.24,
      box: [R.W * 0.38, R.H * 0.25, R.W * 0.62, R.H * 0.65],
      ok: false,
    };

  // ============================================================ CAMERA table
  // apply(S, p, g, cam) mutates g = {ax, ay (source anchor px), tx, ty (screen target px), k (scale), th (roll), mir, cover, dx, dy (screen offsets)}
  const CAMERA = {
    facelock: {
      apply(S, cam, g) {
        // Yaong hard face-lock: eyes midpoint -> (lx,ly), eye distance -> ld*W, roll levelled, never reveals edges
        const tr = S.clip.track[S.si],
          u = S.lt,
          dur = S.dur;
        const zf =
          lerp(cam.z0 ?? 1, cam.z1 ?? 1.04, ease("out3", u / dur)) *
          (1 + (cam.kick ?? 0.035) * Math.exp(-u * (cam.kick_rate ?? 14)));
        g.k = (((cam.ld ?? 0.12) * R.W) / tr.d) * zf;
        g.th = -tr.a * (cam.lockRot ?? 1);
        g.ax = tr.cx;
        g.ay = tr.cy;
        g.tx = (cam.lx ?? 0.5) * R.W;
        g.ty = (cam.ly ?? 0.4) * R.H;
        g.cover = cam.cover !== false;
      },
    },
    zoom: {
      apply(S, p, g) {
        g.k *= lerp(p.z0 ?? 1, p.z1 ?? 1.08, ease(p.ease || "out3", S.lt / S.dur));
      },
    },
    push: {
      apply(S, p, g) {
        g.k *= 1 + (p.v ?? p.rate ?? 0.1) * S.lt;
      },
    },
    punch: {
      apply(S, p, g) {
        const d = p.d ?? 0.25,
          a = p.v ?? p.amt ?? 0.07;
        if (S.lt < d) g.k *= 1 + a * Math.pow(1 - S.lt / d, p.curve ?? 2);
      },
    },
    ladder: {
      apply(S, p, g) {
        const st = p.steps || p.v || [1, 1.12, 1.24, 1.36];
        g.k *= st[Math.min(st.length - 1, Math.floor(S.u * st.length))];
      },
    },
    pan: {
      apply(S, p, g) {
        g.dx += (p.dx ?? p.v ?? 0) * R.W * S.lt;
        g.dy += (p.dy ?? 0) * R.H * S.lt;
      },
    },
    tilt: {
      apply(S, p, g) {
        g.dy += (p.v ?? 0) * R.H * S.lt;
      },
    },
    roll: {
      apply(S, p, g) {
        g.th += (p.v ?? 0) + (p.rate ?? 0) * S.lt;
      },
    },
    handheld: {
      apply(S, p, g) {
        const a = p.amp ?? p.v ?? 6,
          hz = p.hz ?? 0.7,
          sd = p.seed ?? 7;
        g.dx += noise1(sd, S.t, hz) * a;
        g.dy += noise1(sd + 1, S.t, hz) * a * 0.8;
        g.th += noise1(sd + 2, S.t, hz * 0.8) * (p.rot ?? 0.004);
      },
    },
    shake: {
      apply(S, p, g) {
        // Katana: boil-stepped offsets that decay over d (half as long on freezes)
        const d = p.d ?? (S.shot.speed === 0 ? 0.125 : 0.25),
          kk = clamp(1 - S.lt / d),
          amp = p.amp || [16, 12];
        const b = Math.floor(S.f / (p.every || R.boil));
        g.dx += hs(b, 1, 77) * amp[0] * kk;
        g.dy += hs(b, 2, 77) * (amp[1] ?? amp[0]) * kk;
      },
    },
  };

  // ============================================================ LOOKS (plate grades)
  const LOOK_PRESETS = {
    clean: { type: "none" },
    x: { type: "xerox", key: true },
    xl: { type: "xerox", key: true, black: 0, white: 0.5 },
    duo: { type: "duotone" },
    neg: { type: "neg" },
    kawaii: {
      type: "grade",
      filter: "brightness(1.08) contrast(1.02) saturate(1.12)",
      layers: [
        { op: "soft-light", color: "rgba(255,160,210,0.24)" },
        { op: "screen", color: "rgba(255,240,248,0.03)" },
      ],
    },
    bw: { type: "grade", filter: "grayscale(1) contrast(1.22) brightness(1.04)" },
  };
  let NOISE = null;
  function noiseTable() {
    const N = R.PW * R.PH;
    if (!NOISE || NOISE.length !== N) {
      NOISE = new Float32Array(N);
      for (let i = 0; i < N; i++) NOISE[i] = hash(i, 911) - 0.5;
    }
    return NOISE;
  }
  const LOOKS = {
    none: (S, src) => src,
    // Katana xerox: S-curve levels -> threshold mixed with boiling grain; optional accent key keeps one colour (hair) as a 2-tone ramp
    xerox(S, src, p) {
      const W = R.PW,
        H = R.PH,
        N = W * H,
        NZ = noiseTable();
      const black = p.black ?? 0.13,
        white = p.white ?? 0.8,
        grit = p.grit ?? 0.42,
        hard = p.hard ?? 0.62,
        inv = p.invert ? 1 : 0;
      const ink = rgbOf(p.ink ?? [10, 10, 10]),
        paper = rgbOf(p.paper ?? [255, 255, 255]);
      let key = p.key === true ? {} : p.key || null;
      if (key && key.amt === 0) key = null;
      const K = key
        ? {
            mode: key.mode || (key.hue ? "hue" : "channel"),
            ch: { r: 0, g: 1, b: 2 }[key.channel || "g"],
            lo: key.lo ?? 0.06,
            width: key.width ?? 0.09,
            vmin: key.vmin ?? 0.16,
            vw: key.vw ?? 0.16,
            h0: (key.hue || [60, 110])[0],
            h1: (key.hue || [60, 110])[1],
            soft: key.soft ?? 15,
            sat: key.sat ?? 0.25,
            val: key.val ?? 0.16,
            dark: rgbOf(key.dark ?? [10, 38, 0]),
            light: rgbOf(key.light ?? [196, 255, 52]),
            amt: key.amt ?? 1,
            stoch: key.stoch ?? 0.8,
            mix: key.mix ?? 0.4,
            lift: key.lift ?? 0.12,
            gain: key.gain ?? 1.1,
          }
        : null;
      const out = R.L.look,
        x = out.x;
      x.setTransform(1, 0, 0, 1, 0, 0);
      x.globalCompositeOperation = "copy";
      x.drawImage(src.canvas || src, 0, 0);
      x.globalCompositeOperation = "source-over";
      const id = x.getImageData(0, 0, W, H),
        d = id.data;
      const off = (Math.floor(S.f / (p.grain_every || 1)) * 7919) % N,
        sc = 1 / Math.max(1e-3, white - black);
      for (let q0 = 0, i = 0; q0 < N; q0++, i += 4) {
        const r = d[i],
          g = d[i + 1],
          b = d[i + 2];
        let L = (r * 0.3 + g * 0.59 + b * 0.11) / 255;
        L = (L - black) * sc;
        L = L < 0 ? 0 : L > 1 ? 1 : L;
        L = L * L * (3 - 2 * L);
        let q = q0 + off;
        if (q >= N) q -= N;
        const n = NZ[q];
        const th = L + n * grit > 0.5 ? 1 : 0;
        let v = L + (th - L) * hard;
        v = v < 0 ? 0 : v > 1 ? 1 : v;
        if (inv) v = 1 - v;
        let R_ = paper[0] + (ink[0] - paper[0]) * (1 - v),
          G_ = paper[1] + (ink[1] - paper[1]) * (1 - v),
          B_ = paper[2] + (ink[2] - paper[2]) * (1 - v);
        if (K) {
          let hk = 0;
          if (K.mode === "channel") {
            const c = K.ch === 0 ? r : K.ch === 1 ? g : b,
              m = K.ch === 0 ? (g > b ? g : b) : K.ch === 1 ? (r > b ? r : b) : r > g ? r : g,
              e = (c - m) / 255;
            hk = (e - K.lo) / K.width;
            hk = hk < 0 ? 0 : hk > 1 ? 1 : hk;
            let gv = (c / 255 - K.vmin) / K.vw;
            gv = gv < 0 ? 0 : gv > 1 ? 1 : gv;
            hk *= gv * K.amt;
          } else {
            const mx = r > g ? (r > b ? r : b) : g > b ? g : b,
              mn = r < g ? (r < b ? r : b) : g < b ? g : b,
              dd = mx - mn;
            if (dd > 0 && mx > 0) {
              let h =
                mx === r
                  ? 60 * (((g - b) / dd) % 6)
                  : mx === g
                    ? 60 * ((b - r) / dd + 2)
                    : 60 * ((r - g) / dd + 4);
              if (h < 0) h += 360;
              let h0 = K.h0,
                h1 = K.h1;
              if (h0 > h1) {
                h1 += 360;
                if (h < h0) h += 360;
              }
              let wh = (Math.min(h - h0, h1 - h) + K.soft) / K.soft;
              wh = wh < 0 ? 0 : wh > 1 ? 1 : wh;
              let ws = (dd / mx - K.sat) / 0.1;
              ws = ws < 0 ? 0 : ws > 1 ? 1 : ws;
              let wv = (mx / 255 - K.val) / 0.1;
              wv = wv < 0 ? 0 : wv > 1 ? 1 : wv;
              hk = wh * ws * wv * K.amt;
            }
          }
          if (hk > 0) {
            hk = hk + n * K.stoch > 0.5 ? 1 : 0;
            if (hk) {
              let hv = L * K.gain + K.lift + n * 0.34;
              hv = hv < 0 ? 0 : hv > 1 ? 1 : hv;
              const ht = hv + n * grit > 0.5 ? 1 : 0;
              hv = hv + (ht - hv) * K.mix;
              R_ = K.dark[0] + (K.light[0] - K.dark[0]) * hv;
              G_ = K.dark[1] + (K.light[1] - K.dark[1]) * hv;
              B_ = K.dark[2] + (K.light[2] - K.dark[2]) * hv;
            }
          }
        }
        d[i] = R_;
        d[i + 1] = G_;
        d[i + 2] = B_;
        d[i + 3] = 255;
      }
      x.putImageData(id, 0, 0);
      return out;
    },
    duotone: (S, src, p) =>
      LOOKS.xerox(S, src, {
        grit: 0.5,
        ...p,
        key: false,
        paper: p.paper ?? "$accent",
        ink: p.ink ?? [8, 12, 4],
      }),
    neg: (S, src, p) => LOOKS.xerox(S, src, { ...p, key: p.key ?? false, invert: true }),
    levels: (S, src, p) => LOOKS.xerox(S, src, { hard: 0.85, ...p }),
    threshold: (S, src, p) => LOOKS.xerox(S, src, { grit: 0, hard: 1, black: 0, white: 1, ...p }),
    // ctx.filter grade + colour layers (soft-light/screen/multiply washes)
    grade(S, src, p) {
      const out = R.L.look,
        x = out.x;
      x.setTransform(1, 0, 0, 1, 0, 0);
      x.globalCompositeOperation = "copy";
      x.filter = p.filter || "none";
      x.drawImage(src.canvas || src, 0, 0);
      x.filter = "none";
      x.globalCompositeOperation = "source-over";
      for (const L of p.layers || []) {
        x.globalCompositeOperation = L.op || "soft-light";
        x.globalAlpha = L.alpha ?? 1;
        x.fillStyle = col(L.color, "rgba(0,0,0,0)");
        x.fillRect(0, 0, R.PW, R.PH);
      }
      x.globalCompositeOperation = "source-over";
      x.globalAlpha = 1;
      return out;
    },
    filter: (S, src, p) => LOOKS.grade(S, src, { filter: p.filter || p.v, layers: p.layers }),
  };
  function lookSpec(spec) {
    if (spec === undefined || spec === null || spec === false) return { type: "none" };
    if (typeof spec === "string") spec = { preset: spec };
    let s = { ...spec };
    for (let i = 0; i < 4 && s.preset; i++) {
      const pr = (R.E.looks || {})[s.preset] || LOOK_PRESETS[s.preset];
      const name = s.preset;
      delete s.preset;
      if (pr) s = { ...pr, ...s };
      else if (LOOKS[name]) s = { type: name, ...s };
      else {
        warn("unknown look " + name);
        s = { type: "none" };
      }
    }
    if (!s.type) s.type = "none";
    return s;
  }
  async function applyLook(S, src, spec) {
    const s = lookSpec(spec),
      fn = LOOKS[s.type];
    if (!fn) {
      warn("unknown look type " + s.type);
      return src;
    }
    return (await fn(S, src, resolveParams(s, S))) || src;
  }

  // ============================================================ mask helpers: occupancy, contour, cutout
  const CELL = 16;
  function occFromMask(mim, M, C) {
    const OGW = R.OGW,
      OGH = R.OGH,
      x = R.L.occ.x;
    x.setTransform(1, 0, 0, 1, 0, 0);
    x.clearRect(0, 0, OGW, OGH);
    x.setTransform(M[0] / CELL, M[1] / CELL, M[2] / CELL, M[3] / CELL, M[4] / CELL, M[5] / CELL);
    x.drawImage(mim, 0, 0, C.w, C.h);
    const d = x.getImageData(0, 0, OGW, OGH).data,
      g = new Uint8Array(OGW * OGH);
    for (let i = 0; i < OGW * OGH; i++) g[i] = d[i * 4 + 3] > 76 ? 1 : 0;
    return g;
  }
  function dilateG(g, r) {
    const OGW = R.OGW,
      OGH = R.OGH,
      o = new Uint8Array(OGW * OGH);
    for (let y = 0; y < OGH; y++)
      for (let X = 0; X < OGW; X++) {
        if (!g[y * OGW + X]) continue;
        for (let j = -r; j <= r; j++)
          for (let i = -r; i <= r; i++) {
            const yy = y + j,
              xx = X + i;
            if (yy >= 0 && yy < OGH && xx >= 0 && xx < OGW) o[yy * OGW + xx] = 1;
          }
      }
    return o;
  }
  const occFrac = (g, Rr) => {
    if (!g) return 0;
    const OGW = R.OGW,
      OGH = R.OGH;
    let n = 0,
      m = 0;
    for (
      let y = Math.max(0, Math.floor(Rr[1] / CELL));
      y < Math.min(OGH, Math.ceil(Rr[3] / CELL));
      y++
    )
      for (
        let X = Math.max(0, Math.floor(Rr[0] / CELL));
        X < Math.min(OGW, Math.ceil(Rr[2] / CELL));
        X++
      ) {
        m++;
        n += g[y * OGW + X];
      }
    return m ? n / m : 0;
  };
  function lumaGrid(src) {
    const OGW = R.OGW,
      OGH = R.OGH,
      x = R.L.lum.x;
    x.setTransform(1, 0, 0, 1, 0, 0);
    x.drawImage(src.canvas || src, 0, 0, OGW, OGH);
    const d = x.getImageData(0, 0, OGW, OGH).data,
      g = new Float32Array(OGW * OGH);
    for (let i = 0; i < OGW * OGH; i++)
      g[i] = (d[i * 4] * 0.3 + d[i * 4 + 1] * 0.59 + d[i * 4 + 2] * 0.11) / 255;
    return g;
  }
  async function occAt(S) {
    if (!S.clip || !S.clip.mask_dir) return null;
    const m = await img(maskPath(S.clip, S.si));
    return m ? occFromMask(m, S.M, S.clip) : null;
  }

  // marching squares on a 1/4-res grid of the mask (Katana contours)
  const GS = 4;
  function contours(mim, M, C, blur = 2.2) {
    const GW = R.GW,
      GH = R.GH,
      x = R.L.grid.x;
    x.setTransform(1, 0, 0, 1, 0, 0);
    x.clearRect(0, 0, GW, GH);
    x.filter = `blur(${blur}px)`;
    x.setTransform(M[0] / GS, M[1] / GS, M[2] / GS, M[3] / GS, M[4] / GS, M[5] / GS);
    x.drawImage(mim, 0, 0, C.w, C.h);
    x.filter = "none";
    const d = x.getImageData(0, 0, GW, GH).data,
      VW = GW + 2,
      V = new Float32Array(VW * (GH + 2));
    for (let j = 0; j < GH; j++)
      for (let i = 0; i < GW; i++) V[(j + 1) * VW + i + 1] = d[(j * GW + i) * 4 + 3] / 255;
    const th = 0.5,
      segs = [],
      NHg = GH + 2,
      pt = {},
      adj = new Map();
    const hid = (i, j) => j * VW + i,
      vid = (i, j) => VW * NHg + j * VW + i;
    const hp = (i, j) => {
      const a = V[j * VW + i],
        b = V[j * VW + i + 1];
      return [i + (th - a) / (b - a || 1e-6), j];
    };
    const vp = (i, j) => {
      const a = V[j * VW + i],
        b = V[(j + 1) * VW + i];
      return [i, j + (th - a) / (b - a || 1e-6)];
    };
    const add = (e1, p1, e2, p2) => {
      const s = segs.length;
      segs.push([e1, e2]);
      pt[e1] = p1;
      pt[e2] = p2;
      [e1, e2].forEach((e) => {
        const l = adj.get(e);
        if (l) l.push(s);
        else adj.set(e, [s]);
      });
    };
    for (let j = 0; j < NHg - 1; j++)
      for (let i = 0; i < VW - 1; i++) {
        const a = V[j * VW + i] > th,
          b = V[j * VW + i + 1] > th,
          c = V[(j + 1) * VW + i + 1] > th,
          dd = V[(j + 1) * VW + i] > th,
          k = (a << 3) | (b << 2) | (c << 1) | dd;
        if (k === 0 || k === 15) continue;
        const T_ = () => [hid(i, j), hp(i, j)],
          R_ = () => [vid(i + 1, j), vp(i + 1, j)],
          B_ = () => [hid(i, j + 1), hp(i, j + 1)],
          L_ = () => [vid(i, j), vp(i, j)];
        const S_ = (e, f) => {
          const A = e(),
            Bq = f();
          add(A[0], A[1], Bq[0], Bq[1]);
        };
        switch (k) {
          case 1:
          case 14:
            S_(L_, B_);
            break;
          case 2:
          case 13:
            S_(B_, R_);
            break;
          case 3:
          case 12:
            S_(L_, R_);
            break;
          case 4:
          case 11:
            S_(T_, R_);
            break;
          case 5:
            S_(T_, R_);
            S_(L_, B_);
            break;
          case 6:
          case 9:
            S_(T_, B_);
            break;
          case 7:
          case 8:
            S_(T_, L_);
            break;
          case 10:
            S_(T_, L_);
            S_(R_, B_);
            break;
        }
      }
    const used = new Uint8Array(segs.length),
      lines = [];
    for (let s0 = 0; s0 < segs.length; s0++) {
      if (used[s0]) continue;
      used[s0] = 1;
      const chain = [segs[s0][0], segs[s0][1]];
      let e = segs[s0][1];
      for (let guard = 0; guard < 20000; guard++) {
        const l = adj.get(e) || [];
        const nx = l.find((s) => !used[s]);
        if (nx === undefined) break;
        used[nx] = 1;
        e = segs[nx][0] === e ? segs[nx][1] : segs[nx][0];
        chain.push(e);
      }
      if (chain.length > 36)
        lines.push(
          chain.map((id) => {
            const p = pt[id];
            return [(p[0] - 1) * GS, (p[1] - 1) * GS];
          }),
        );
    }
    return { lines, V, VW };
  }
  const gridAt = (Gd, X, Y) => {
    const i = Math.round(X / GS) + 1,
      j = Math.round(Y / GS) + 1;
    return i < 0 || j < 0 || i >= Gd.VW || j >= R.GH + 2 ? 0 : Gd.V[j * Gd.VW + i];
  };

  // ============================================================ drawing primitives
  function poly(x, pts, { w = 4, color = "$ink", b = 0, seed = 0, jit = 1.6, close = false } = {}) {
    x.save();
    x.lineCap = "round";
    x.lineJoin = "round";
    x.strokeStyle = col(color, "#000");
    x.lineWidth = w;
    x.beginPath();
    pts.forEach((p, i) => {
      const X = p[0] + hs(seed, b * 53 + i, 1) * jit,
        Y = p[1] + hs(seed, b * 53 + i, 2) * jit;
      if (i) x.lineTo(X, Y);
      else x.moveTo(X, Y);
    });
    if (close) x.closePath();
    x.stroke();
    x.restore();
  }
  function zigzag(cx, cy, len, amp, ang, n) {
    const c = Math.cos(ang),
      s = Math.sin(ang),
      P = [];
    for (let i = 0; i <= n; i++) {
      const u = (i / n - 0.5) * len,
        v = (i % 2 ? 1 : -1) * amp;
      P.push([cx + c * u - s * v, cy + s * u + c * v]);
    }
    return P;
  }
  function crPts(P, k = 7) {
    // Catmull-Rom densify
    if (P.length < 3) {
      const o = [];
      for (let i = 0; i < P.length - 1; i++)
        for (let s = 0; s < k; s++) {
          const t = s / k;
          o.push([P[i][0] + (P[i + 1][0] - P[i][0]) * t, P[i][1] + (P[i + 1][1] - P[i][1]) * t]);
        }
      o.push(P[P.length - 1]);
      return o;
    }
    const o = [];
    for (let i = 0; i < P.length - 1; i++) {
      const p0 = P[i - 1] || P[i],
        p1 = P[i],
        p2 = P[i + 1],
        p3 = P[i + 2] || P[i + 1];
      for (let s = 0; s < k; s++) {
        const t = s / k,
          t2 = t * t,
          t3 = t2 * t;
        o.push(
          [0, 1].map(
            (j) =>
              0.5 *
              (2 * p1[j] +
                (-p0[j] + p2[j]) * t +
                (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2 +
                (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3),
          ),
        );
      }
    }
    o.push(P[P.length - 1]);
    return o;
  }
  const strokeLen = (s) => {
    let L = 0;
    for (let i = 1; i < s.length; i++)
      L += Math.hypot(s[i][0] - s[i - 1][0], s[i][1] - s[i - 1][1]);
    return L;
  };
  function drawStrokes(
    x,
    strokes,
    {
      u = 1,
      w = 10,
      color = "$ink",
      b = 0,
      seed = 0,
      jit = 2.2,
      alpha = 1,
      taper = true,
      k = 7,
    } = {},
  ) {
    const dense = strokes.map((s, si) =>
      crPts(
        s.map((p, i) => [
          p[0] + hs(seed + si * 7, b * 131 + i, 1) * jit,
          p[1] + hs(seed + si * 7, b * 131 + i, 2) * jit,
        ]),
        k,
      ),
    );
    const lens = dense.map(strokeLen),
      tot = lens.reduce((a, c) => a + c, 0);
    let rem = clamp(u) * tot;
    x.save();
    x.lineCap = "round";
    x.lineJoin = "round";
    x.strokeStyle = x.fillStyle = col(color, "#000");
    x.globalAlpha = alpha;
    dense.forEach((pts0, si) => {
      if (rem <= 0) return;
      const L = lens[si],
        take = Math.min(1, rem / Math.max(L, 1e-3));
      rem -= L;
      if (L < 16) {
        x.beginPath();
        x.arc(pts0[0][0], pts0[0][1], w * 0.72, 0, TAU);
        x.fill();
        return;
      }
      const pts = pts0.slice(0, Math.max(2, Math.ceil(pts0.length * take)));
      if (!taper) {
        x.lineWidth = w;
        x.beginPath();
        pts.forEach((p, i) => (i ? x.lineTo(p[0], p[1]) : x.moveTo(p[0], p[1])));
        x.stroke();
        return;
      }
      for (let i = 1; i < pts.length; i++) {
        const t = i / (pts0.length - 1),
          kk = t < 0.1 ? 0.7 + t * 3 : t > 0.82 ? Math.max(0.35, 1 - (t - 0.82) * 3.2) : 1;
        x.lineWidth = Math.max(1, w * kk);
        x.beginPath();
        x.moveTo(pts[i - 1][0], pts[i - 1][1]);
        x.lineTo(pts[i][0], pts[i][1]);
        x.stroke();
      }
    });
    x.restore();
  }
  const partialP = (P, u) => (u >= 1 ? P : P.slice(0, Math.max(2, Math.floor(P.length * u))));

  // ============================================================ DOODLES: shape library
  // DOODLES.ink.<type>(x, X, Y, s, S, seed, opt)  - Katana marker doodles (boil with S.b), colours from palette
  // DOODLES.kawaii.<type>(x, s, r)                - Yaong outline+white-fill shapes in unit space (see kawaiiDoodle)
  function splat(x, cx, cy, r, S, seed, color = "$accent2") {
    x.save();
    x.fillStyle = col(color);
    for (let i = 0; i < 16; i++) {
      const a = hash(seed, i, 1) * TAU,
        d = r * Math.pow(hash(seed, i, 2), 0.7) * 1.6,
        rr = r * (0.05 + hash(seed, i, 3) * 0.17) * (i < 3 ? 2.2 : 1);
      x.beginPath();
      x.arc(cx + Math.cos(a) * d, cy + Math.sin(a) * d, rr, 0, TAU);
      x.fill();
    }
    x.beginPath();
    x.arc(cx, cy, r * 0.42, 0, TAU);
    x.fill();
    x.restore();
  }
  function splatField(x, X, Y, Rr, S, seed, n, c1 = "$accent2", c2 = "$ink") {
    x.save();
    for (let i = 0; i < n; i++) {
      const a = hash(seed, i, 1) * TAU,
        d = Rr * Math.sqrt(hash(seed, i, 2)),
        r = 3 + Math.pow(hash(seed, i, 3), 2) * 21;
      x.fillStyle = col(hash(seed, i, 4) < 0.7 ? c1 : c2);
      x.beginPath();
      x.arc(X + Math.cos(a) * d, Y + Math.sin(a) * d, r, 0, TAU);
      x.fill();
    }
    x.restore();
  }
  function sparkle(x, cx, cy, r, S, seed, color = "$ink") {
    const P = [];
    for (let i = 0; i <= 16; i++) {
      const a = (i / 16) * TAU,
        rr = i % 4 === 0 ? r : i % 2 === 0 ? r * 0.18 : r * 0.32;
      P.push([cx + Math.cos(a) * rr, cy + Math.sin(a) * rr]);
    }
    poly(x, P, { w: 3.4, color, b: S.b, seed, jit: 1.2, close: true });
  }
  function crossP(cx, cy, s, rot = 0) {
    const a = 0.11,
      R2 = [
        [0, -0.62],
        [a * 1.6, -0.5],
        [a, -0.42],
        [a, -a],
        [0.42, -a],
        [0.5, -a * 1.6],
        [0.6, 0],
        [0.5, a * 1.6],
        [0.42, a],
        [a, a],
        [a, 0.86],
        [a * 1.6, 0.96],
        [0, 1.1],
        [-a * 1.6, 0.96],
        [-a, 0.86],
        [-a, a],
        [-0.42, a],
        [-0.5, a * 1.6],
        [-0.6, 0],
        [-0.5, -a * 1.6],
        [-0.42, -a],
        [-a, -a],
        [-a, -0.42],
        [-a * 1.6, -0.5],
      ];
    const c = Math.cos(rot),
      sn = Math.sin(rot);
    return R2.map(([u, v]) => [cx + (u * c - v * sn) * s, cy + (u * sn + v * c) * s]);
  }
  function crossDoodle(x, cx, cy, s, S, seed) {
    const P = crossP(cx, cy, s, hs(seed, 0, 1) * 0.25);
    x.save();
    x.fillStyle = col("$accent");
    x.beginPath();
    P.forEach((p, i) =>
      i
        ? x.lineTo(p[0] + hs(seed, S.b * 7 + i, 3), p[1] + hs(seed, S.b * 7 + i, 4))
        : x.moveTo(p[0], p[1]),
    );
    x.closePath();
    x.fill();
    x.restore();
    poly(x, P, { w: 3.5, b: S.b, seed, jit: 1.8, close: true });
  }
  function hatch(x, cx, cy, s, S, seed) {
    for (let i = 0; i < 4; i++) {
      const u = (i - 1.5) * s * 0.22;
      poly(
        x,
        [
          [cx + u - s * 0.12, cy - s * 0.5],
          [cx + u + s * 0.12, cy + s * 0.5],
        ],
        { w: 4, color: "$accent2", b: S.b, seed: seed + i },
      );
      poly(
        x,
        [
          [cx - s * 0.5, cy + u - s * 0.1],
          [cx + s * 0.5, cy + u + s * 0.1],
        ],
        { w: 4, color: "$accent2", b: S.b, seed: seed + 9 + i },
      );
    }
  }
  function rays(x, cx, cy, r, S, seed) {
    for (let i = 0; i < 9; i++) {
      const a = -2.6 + i * 0.27 + hs(seed, i, 1) * 0.05,
        r0 = r * (0.55 + hash(seed, i, 2) * 0.2),
        r1 = r * (0.95 + hash(seed, i, 3) * 0.35);
      poly(
        x,
        [
          [cx + Math.cos(a) * r0, cy + Math.sin(a) * r0],
          [cx + Math.cos(a) * r1, cy + Math.sin(a) * r1],
        ],
        { w: 4, color: i % 3 ? "$ink" : "$accent2", b: S.b, seed: seed + i },
      );
    }
  }
  function arrow(x, A, B, bend, S, seed, { w = 5, color = "$ink", u = 1 } = {}) {
    const m = [(A[0] + B[0]) / 2 + (B[1] - A[1]) * bend, (A[1] + B[1]) / 2 - (B[0] - A[0]) * bend];
    const P = [
      A,
      [lerp(A[0], m[0], 0.6), lerp(A[1], m[1], 0.6)],
      m,
      [lerp(m[0], B[0], 0.5), lerp(m[1], B[1], 0.5)],
      B,
    ];
    drawStrokes(x, [P], { u, w, color, b: S.b, seed, jit: 2, taper: false });
    if (u < 1) return;
    const d = crPts(P),
      q = d[d.length - 4],
      ang = Math.atan2(B[1] - q[1], B[0] - q[0]);
    [0.5, -0.5].forEach((da, k) =>
      poly(x, [[B[0] - Math.cos(ang + da) * 26, B[1] - Math.sin(ang + da) * 26], B], {
        w,
        color,
        b: S.b,
        seed: seed + 5 + k,
      }),
    );
  }
  function scratch(x, X, Y, len, ang, S, seed, u, color = "$accent") {
    const m = 3 + Math.floor(hash(seed, 1, 1) * 3),
      pk = 8 + Math.floor(hash(seed, 1, 2) * 3),
      sp = 14 + hash(seed, 1, 3) * 8;
    for (let j = 0; j < m; j++) {
      const ox = -Math.sin(ang) * sp * (j - (m - 1) / 2),
        oy = Math.cos(ang) * sp * (j - (m - 1) / 2),
        L = len * (0.8 + 0.2 * hash(seed, j, 4));
      poly(
        x,
        partialP(
          zigzag(
            X + ox + Math.cos(ang) * hs(seed, j, 5) * 20,
            Y + oy + Math.sin(ang) * hs(seed, j, 5) * 20,
            L,
            L * 0.06,
            ang,
            pk,
          ),
          u,
        ),
        { w: 3 + hash(seed, j, 6) * 1.5, color, b: S.b, seed: seed + j },
      );
    }
  }
  const DOODLES = {
    ink: {
      zig: (x, X, Y, s, S, seed, o) =>
        poly(
          x,
          partialP(
            zigzag(X, Y, s * 3.2, s * 0.55, o.ang, 6 + Math.floor(hash(seed, 0, 8) * 4)),
            o.u,
          ),
          { w: 5.5, color: o.color, b: S.b, seed },
        ),
      scratch: (x, X, Y, s, S, seed, o) =>
        scratch(
          x,
          X,
          Y,
          250 + hash(seed, 0, 8) * 150,
          o.ang,
          S,
          seed,
          o.u,
          o.color === "$ink" ? "$ink" : "$accent",
        ),
      splat: (x, X, Y, s, S, seed) =>
        splatField(x, X, Y, s * 1.2, S, seed, 12 + Math.floor(hash(seed, 0, 8) * 9)),
      rays: (x, X, Y, s, S, seed, o) => {
        if (o.u > 0.5) rays(x, X, Y, s * 1.1, S, seed);
      },
      arrow: (x, X, Y, s, S, seed, o) =>
        arrow(
          x,
          [X, Y],
          [X + Math.cos(o.ang) * s * 1.6, Y + Math.sin(o.ang) * s * 1.6],
          0.25,
          S,
          seed,
          { w: 5, color: o.color, u: o.u },
        ),
      spark: (x, X, Y, s, S, seed, o) => sparkle(x, X, Y, s * 0.6, S, seed, o.color),
      cross: (x, X, Y, s, S, seed) => crossDoodle(x, X, Y, s * 1.1, S, seed),
      hatch: (x, X, Y, s, S, seed) => hatch(x, X, Y, s * 1.3, S, seed),
      star: (x, X, Y, s, S, seed, o) => {
        const P = [];
        for (let j = 0; j <= 10; j++) {
          const a = (j / 10) * TAU - 1.57,
            r = j % 2 ? s * 0.35 : s * 0.8;
          P.push([X + Math.cos(a) * r, Y + Math.sin(a) * r]);
        }
        poly(x, partialP(P, o.u), { w: 4, color: o.color, b: S.b, seed });
      },
      xx: (x, X, Y, s, S, seed, o) => {
        poly(
          x,
          [
            [X - s * 0.4, Y - s * 0.4],
            [X + s * 0.4, Y + s * 0.4],
          ],
          { w: 5, color: o.color, b: S.b, seed },
        );
        poly(
          x,
          [
            [X + s * 0.4, Y - s * 0.4],
            [X - s * 0.4, Y + s * 0.4],
          ],
          { w: 5, color: o.color, b: S.b, seed: seed + 1 },
        );
      },
      bolt: (x, X, Y, s, S, seed, o) =>
        poly(
          x,
          [
            [0.2, -1],
            [-0.35, 0.05],
            [0.1, 0.05],
            [-0.25, 1],
            [0.45, -0.2],
            [0, -0.2],
            [0.35, -1],
          ].map(([a, c]) => [X + a * s, Y + c * s]),
          { w: 4, color: o.color, b: S.b, seed, close: true },
        ),
      bang: (x, X, Y, s, S, seed, o) => {
        poly(
          x,
          [
            [X, Y - s * 0.8],
            [X - s * 0.06, Y + s * 0.3],
          ],
          { w: 7, color: o.color, b: S.b, seed },
        );
        x.save();
        x.fillStyle = col(o.color);
        x.beginPath();
        x.arc(X - s * 0.08, Y + s * 0.62, 6, 0, TAU);
        x.fill();
        x.restore();
      },
    },
    kawaii: {}, // filled below (shapePath / linePath based)
  };
  const INK_GESTURES = new Set(["zig", "scratch", "splat", "arrow", "rays"]);

  // ---------------------------------------------------------------- kawaii (Yaong) doodles
  const jit = (r, a) => (r() - 0.5) * 2 * a;
  function shapePath(type, r) {
    const p = new Path2D(),
      J = (a) => jit(r, a);
    switch (type) {
      case "heart":
        p.moveTo(0, 0.35 + J(0.03));
        p.bezierCurveTo(-0.55 + J(0.03), -0.05, -0.5, -0.55 + J(0.03), -0.25, -0.5);
        p.bezierCurveTo(-0.08, -0.48, 0, -0.35, 0, -0.25);
        p.bezierCurveTo(0, -0.35, 0.08, -0.48, 0.25, -0.5);
        p.bezierCurveTo(0.5, -0.55 + J(0.03), 0.55 + J(0.03), -0.05, 0, 0.35 + J(0.03));
        p.closePath();
        break;
      case "spark": {
        const k = 0.16 + J(0.02);
        p.moveTo(0, -0.55 + J(0.03));
        p.quadraticCurveTo(k * 0.4, -k * 0.4, 0.5 + J(0.03), 0);
        p.quadraticCurveTo(k * 0.4, k * 0.4, 0, 0.55 + J(0.03));
        p.quadraticCurveTo(-k * 0.4, k * 0.4, -0.5 + J(0.03), 0);
        p.quadraticCurveTo(-k * 0.4, -k * 0.4, 0, -0.55 + J(0.03));
        p.closePath();
        break;
      }
      case "star":
        for (let i = 0; i < 10; i++) {
          const a = -Math.PI / 2 + (i * Math.PI) / 5,
            rr = (i % 2 ? 0.22 : 0.5) + J(0.025);
          if (i) p.lineTo(Math.cos(a) * rr, Math.sin(a) * rr);
          else p.moveTo(Math.cos(a) * rr, Math.sin(a) * rr);
        }
        p.closePath();
        break;
      case "ear":
        p.moveTo(-0.5, 0.3);
        p.quadraticCurveTo(-0.42 + J(0.03), -0.45, 0.02 + J(0.04), -0.75);
        p.quadraticCurveTo(0.42 + J(0.03), -0.4, 0.5, 0.3);
        p.quadraticCurveTo(0, 0.18, -0.5, 0.3);
        p.closePath();
        break;
      case "earIn":
        p.moveTo(-0.27, 0.18);
        p.quadraticCurveTo(-0.22, -0.3, 0.02, -0.5);
        p.quadraticCurveTo(0.22, -0.26, 0.27, 0.18);
        p.closePath();
        break;
      case "bow":
        p.moveTo(0, 0);
        p.bezierCurveTo(-0.3, -0.35 + J(0.03), -0.6, -0.3, -0.55, 0);
        p.bezierCurveTo(-0.6, 0.3, -0.3, 0.35 + J(0.03), 0, 0);
        p.bezierCurveTo(0.3, -0.35 + J(0.03), 0.6, -0.3, 0.55, 0);
        p.bezierCurveTo(0.6, 0.3, 0.3, 0.35 + J(0.03), 0, 0);
        p.closePath();
        p.ellipse(0, 0, 0.1, 0.12, 0, 0, TAU);
        break;
    }
    return p;
  }
  function linePath(type, r) {
    const p = new Path2D(),
      J = (a) => jit(r, a);
    switch (type) {
      case "squig":
        p.moveTo(-0.3, -0.45);
        p.bezierCurveTo(0.2 + J(0.04), -0.7, 0.45, -0.15, 0.05, -0.02);
        p.bezierCurveTo(0.5 + J(0.04), 0.05, 0.45, 0.55, -0.25, 0.45);
        break;
      case "swirl":
        for (let i = 0; i <= 40; i++) {
          const a = (i / 40) * Math.PI * 3.6,
            rr = 0.05 + (i / 40) * 0.45 + J(0.01);
          if (i) p.lineTo(Math.cos(a) * rr, Math.sin(a) * rr);
          else p.moveTo(Math.cos(a) * rr, Math.sin(a) * rr);
        }
        break;
      case "arrow":
        p.moveTo(-0.5, 0.35);
        p.quadraticCurveTo(-0.1 + J(0.05), -0.45, 0.45, -0.2);
        p.moveTo(0.22, -0.42 + J(0.03));
        p.lineTo(0.47, -0.2);
        p.lineTo(0.2, -0.02 + J(0.03));
        break;
      case "whisk":
        for (let k = -1; k <= 1; k++) {
          p.moveTo(0, k * 0.16);
          p.quadraticCurveTo(0.45, k * 0.24 + J(0.02), 0.95, k * 0.36 + 0.02 + J(0.03));
        }
        break;
      case "dash3":
        for (let k = 0; k < 3; k++) {
          const a = -0.9 + k * 0.45;
          p.moveTo(Math.cos(a) * 0.28, Math.sin(a) * 0.28);
          p.lineTo(Math.cos(a) * (0.58 + J(0.04)), Math.sin(a) * (0.58 + J(0.04)));
        }
        break;
      case "cross":
        p.moveTo(-0.4, J(0.03));
        p.lineTo(0.4, J(0.03));
        p.moveTo(J(0.03), -0.4);
        p.lineTo(J(0.03), 0.4);
        break;
    }
    return p;
  }
  function noteGlyph(c, s, dbl) {
    const p = new Path2D(),
      head = (hx, hy) => p.ellipse(hx, hy, s * 0.34, s * 0.24, -0.4, 0, TAU);
    head(0, 0);
    p.rect(s * 0.24, -s * 1.15, s * 0.11, s * 1.15);
    if (dbl) {
      head(s * 0.95, -s * 0.18);
      p.rect(s * 1.19, -s * 1.33, s * 0.11, s * 1.15);
      p.moveTo(s * 0.24, -s * 1.15);
      p.lineTo(s * 1.3, -s * 1.33);
      p.lineTo(s * 1.3, -s * 1.08);
      p.lineTo(s * 0.24, -s * 0.9);
      p.closePath();
    } else {
      p.moveTo(s * 0.35, -s * 1.15);
      p.bezierCurveTo(s * 0.75, -s * 0.95, s * 0.85, -s * 0.6, s * 0.6, -s * 0.35);
      p.bezierCurveTo(s * 0.7, -s * 0.7, s * 0.55, -s * 0.85, s * 0.35, -s * 0.85);
      p.closePath();
    }
    c.lineWidth = 4;
    c.strokeStyle = col("$lav");
    c.lineJoin = "round";
    c.stroke(p);
    c.fillStyle = col("$white");
    c.fill(p);
  }
  // kawaii doodle at (x,y), size s px, boiling every 3 frames; sc = pop scale
  function kawaiiDoodle(c, type, x, y, s, rot, f, seed, sc = 1, alpha = 1, colors = {}) {
    if (sc <= 0.01) return;
    const r = rng(seed * 131 + Math.floor(f / 3)),
      LAV = col(colors.line ?? "$lav"),
      WH = col(colors.fill ?? "$white");
    c.save();
    c.globalAlpha = alpha;
    c.translate(x, y);
    c.rotate(rot + jit(r, 0.035));
    c.scale(s * sc, s * sc);
    const lw = (v) => v / (s * sc);
    const custom = DOODLES.kawaii[type];
    if (custom) custom(c, s * sc, r, { LAV, WH, lw });
    else if (type === "note" || type === "note2") {
      c.scale(1 / (s * sc), 1 / (s * sc));
      c.translate(-s * sc * 0.3, s * sc * 0.45);
      noteGlyph(c, s * sc * 0.7, type === "note2");
    } else if (["heart", "spark", "star", "bow"].includes(type)) {
      const p = shapePath(type, r);
      c.lineJoin = "round";
      c.lineWidth = lw(4.5);
      c.strokeStyle = LAV;
      c.stroke(p);
      c.fillStyle = WH;
      c.fill(p);
    } else if (type === "blush") {
      const p = shapePath("heart", r);
      c.lineJoin = "round";
      c.lineWidth = lw(5);
      c.strokeStyle = col("$white");
      c.stroke(p);
      c.fillStyle = col(colors.blush ?? "$blush");
      c.fill(p);
    } else if (type === "heartO") {
      const p = shapePath("heart", r);
      c.lineJoin = "round";
      c.lineWidth = lw(11);
      c.strokeStyle = LAV;
      c.stroke(p);
      c.lineWidth = lw(5.5);
      c.strokeStyle = WH;
      c.stroke(p);
    } else if (type === "ear") {
      const p = shapePath("ear", r);
      c.lineJoin = "round";
      c.lineWidth = lw(5);
      c.strokeStyle = LAV;
      c.stroke(p);
      c.fillStyle = WH;
      c.fill(p);
      c.fillStyle = col("$earin");
      c.fill(shapePath("earIn", r));
    } else if (type === "dots") {
      [
        [-0.3, 0.1, 0.11],
        [0.05, -0.2, 0.08],
        [0.32, 0.12, 0.13],
      ].forEach(([dx, dy, rr]) => {
        c.beginPath();
        c.arc(dx + jit(r, 0.02), dy + jit(r, 0.02), rr, 0, TAU);
        c.lineWidth = lw(4);
        c.strokeStyle = LAV;
        c.stroke();
        c.fillStyle = WH;
        c.fill();
      });
    } else {
      const p = linePath(type, r);
      c.lineCap = "round";
      c.lineJoin = "round";
      const w = type === "whisk" ? 6 : 12;
      c.lineWidth = lw(w + 6);
      c.strokeStyle = LAV;
      c.stroke(p);
      c.lineWidth = lw(w);
      c.strokeStyle = WH;
      c.stroke(p);
    }
    c.restore();
  }
  const KAWAII_SIZE = {
    note: 1.0,
    note2: 0.9,
    heart: 0.62,
    heartO: 0.7,
    bow: 0.75,
    spark: 0.55,
    star: 0.62,
    dots: 0.6,
    swirl: 0.6,
    squig: 0.7,
    arrow: 0.75,
    cross: 0.45,
    dash3: 0.7,
    blush: 0.4,
    ear: 0.9,
    whisk: 0.9,
  };
  const popIn = (S, at, d = 0.1) => {
    const v = clamp((S.lt - at) / d);
    return v < 1 ? easeOut(v) * (1 + 0.25 * Math.sin(v * Math.PI)) : 1;
  };
  function asterisk(c, x, y, s, rot, colors = {}) {
    c.save();
    c.translate(x, y);
    c.rotate(rot);
    c.lineCap = "round";
    for (const [lw, cl] of [
      [s * 0.34, colors.line ?? "$lav"],
      [s * 0.2, colors.fill ?? "$white"],
    ]) {
      c.lineWidth = lw;
      c.strokeStyle = col(cl);
      c.beginPath();
      for (let k = 0; k < 3; k++) {
        const a = (k * Math.PI) / 3;
        c.moveTo(Math.cos(a) * s, Math.sin(a) * s);
        c.lineTo(-Math.cos(a) * s, -Math.sin(a) * s);
      }
      c.stroke();
    }
    c.restore();
  }

  // ============================================================ text helpers
  function fontStr(p, size, kind) {
    if (p.font) return p.font.replace("{S}", Math.round(size)).replace("{size}", Math.round(size));
    const st = p.style ?? (kind === "thin" ? "" : "italic"),
      wt = p.weight ?? (kind === "thin" ? 300 : kind === "heavy" ? 900 : 800);
    const fam = p.family
      ? `"${p.family}", ${FONTS.sans}`
      : kind === "heavy"
        ? FONTS.heavy
        : FONTS.sans;
    return `${st} ${wt} ${Math.round(size)}px ${fam}`.trim();
  }
  function shadowOf(c, sh) {
    if (!sh) return;
    if (sh === "dark") {
      c.shadowColor = "rgba(0,0,0,0.45)";
      c.shadowBlur = px(8);
      return;
    }
    if (sh === true || sh === "glow") {
      c.shadowColor = "rgba(190,110,220,0.55)";
      c.shadowBlur = px(14);
      return;
    }
    if (typeof sh === "object") {
      c.shadowColor = col(sh.color, "rgba(0,0,0,0.5)");
      c.shadowBlur = px(sh.blur ?? 10);
      c.shadowOffsetX = px(sh.dx ?? 0);
      c.shadowOffsetY = px(sh.dy ?? 0);
    }
  }
  function outlinedText(
    c,
    txt,
    x,
    y,
    font,
    fill = "$white",
    stroke = "$lav",
    lw = 5,
    rot = 0,
    sc = 1,
    align = "center",
    shadow = true,
  ) {
    c.save();
    c.translate(x, y);
    c.rotate(rot);
    c.scale(sc, sc);
    c.font = font;
    c.textAlign = align;
    c.textBaseline = "middle";
    c.lineJoin = "round";
    shadowOf(c, shadow);
    if (stroke) {
      c.lineWidth = lw;
      c.strokeStyle = col(stroke);
      c.strokeText(txt, 0, 0);
    }
    c.shadowColor = "rgba(0,0,0,0)";
    c.shadowBlur = 0;
    c.fillStyle = col(fill, "#fff");
    c.fillText(txt, 0, 0);
    c.restore();
  }
  function typeWord(c, parts, x, y, size, nShow, rot, p = {}) {
    const fontOf = (k) => fontStr(p, size, k);
    let total = 0;
    parts.forEach(([t, k]) => {
      c.font = fontOf(k);
      total += c.measureText(t).width;
    });
    let cx = -total / 2,
      shown = 0;
    c.save();
    c.translate(x, y);
    c.rotate(rot || 0);
    c.textBaseline = "middle";
    c.textAlign = "left";
    c.lineJoin = "round";
    for (const [t, k] of parts) {
      c.font = fontOf(k);
      for (const ch of t) {
        const w = c.measureText(ch).width;
        if (shown < nShow) {
          shadowOf(c, p.shadow ?? "glow");
          c.lineWidth = k === "thin" ? 4 : 5;
          c.strokeStyle = col(p.stroke ?? "$lav");
          c.strokeText(ch, cx, 0);
          c.shadowColor = "rgba(0,0,0,0)";
          c.shadowBlur = 0;
          c.fillStyle = col(p.fill ?? "$white");
          c.fillText(ch, cx, 0);
        }
        shown++;
        cx += w;
      }
    }
    c.restore();
  }

  // ============================================================ graffiti (Katana chisel-marker caps)
  // glyph units: cap height 1, y=0 top, y=1 baseline; strokes overshoot on purpose. dot: stroke indices drawn as dots.
  const GCAPS = {
    A: {
      adv: 0.6,
      s: [
        [
          [0.0, 1.07],
          [0.14, 0.5],
          [0.29, -0.07],
        ],
        [
          [0.25, -0.04],
          [0.4, 0.5],
          [0.54, 1.07],
        ],
        [
          [-0.02, 0.62],
          [0.28, 0.6],
          [0.58, 0.58],
        ],
      ],
      longBar: [
        [-0.12, 0.63],
        [0.3, 0.61],
        [0.7, 0.58],
      ],
    },
    B: {
      adv: 0.6,
      s: [
        [
          [0.02, -0.06],
          [0.01, 0.5],
          [0.0, 1.07],
        ],
        [
          [0.0, 0.0],
          [0.32, -0.02],
          [0.48, 0.1],
          [0.46, 0.36],
          [0.28, 0.47],
          [0.04, 0.48],
        ],
        [
          [0.06, 0.48],
          [0.4, 0.5],
          [0.56, 0.66],
          [0.54, 0.92],
          [0.34, 1.02],
          [0.0, 1.02],
        ],
      ],
    },
    C: {
      adv: 0.6,
      s: [
        [
          [0.56, 0.12],
          [0.42, 0.0],
          [0.22, 0.01],
          [0.06, 0.18],
          [0.0, 0.5],
          [0.06, 0.84],
          [0.24, 1.01],
          [0.44, 1.0],
          [0.58, 0.88],
        ],
      ],
    },
    D: {
      adv: 0.64,
      s: [
        [
          [0.02, -0.06],
          [0.01, 0.5],
          [0.0, 1.07],
        ],
        [
          [0.0, 0.0],
          [0.3, 0.0],
          [0.52, 0.16],
          [0.58, 0.5],
          [0.5, 0.86],
          [0.28, 1.02],
          [0.0, 1.02],
        ],
      ],
    },
    E: {
      adv: 0.6,
      s: [
        [
          [0.09, -0.04],
          [0.08, 0.5],
          [0.06, 1.06],
        ],
        [
          [0.06, 0.03],
          [0.3, 0.01],
          [0.56, -0.01],
        ],
        [
          [0.06, 0.51],
          [0.26, 0.5],
          [0.48, 0.48],
        ],
        [
          [0.05, 1.03],
          [0.3, 1.01],
          [0.58, 0.99],
        ],
      ],
    },
    F: {
      adv: 0.56,
      s: [
        [
          [0.08, -0.04],
          [0.07, 0.5],
          [0.05, 1.08],
        ],
        [
          [0.05, 0.03],
          [0.3, 0.01],
          [0.56, -0.01],
        ],
        [
          [0.05, 0.5],
          [0.26, 0.49],
          [0.46, 0.47],
        ],
      ],
    },
    G: {
      adv: 0.64,
      s: [
        [
          [0.56, 0.12],
          [0.42, 0.0],
          [0.22, 0.01],
          [0.06, 0.18],
          [0.0, 0.5],
          [0.06, 0.84],
          [0.24, 1.01],
          [0.46, 1.0],
          [0.58, 0.86],
          [0.58, 0.58],
        ],
        [
          [0.32, 0.58],
          [0.46, 0.57],
          [0.64, 0.56],
        ],
      ],
    },
    H: {
      adv: 0.62,
      s: [
        [
          [0.0, -0.07],
          [0.0, 0.5],
          [0.01, 1.08],
        ],
        [
          [0.5, -0.08],
          [0.51, 0.5],
          [0.52, 1.08],
        ],
        [
          [-0.03, 0.51],
          [0.27, 0.5],
          [0.56, 0.48],
        ],
      ],
    },
    I: {
      adv: 0.28,
      s: [
        [
          [0.12, -0.08],
          [0.11, 0.5],
          [0.09, 1.08],
        ],
      ],
    },
    J: {
      adv: 0.54,
      s: [
        [
          [0.48, -0.08],
          [0.47, 0.5],
          [0.44, 0.86],
          [0.3, 1.02],
          [0.12, 1.0],
          [0.0, 0.86],
        ],
      ],
    },
    K: {
      adv: 0.62,
      s: [
        [
          [0.04, -0.1],
          [0.02, 0.5],
          [0.0, 1.1],
        ],
        [
          [0.68, -0.12],
          [0.38, 0.22],
          [0.04, 0.58],
        ],
        [
          [0.14, 0.44],
          [0.42, 0.76],
          [0.7, 1.08],
        ],
      ],
    },
    L: {
      adv: 0.56,
      s: [
        [
          [0.06, -0.08],
          [0.05, 0.5],
          [0.04, 1.04],
        ],
        [
          [0.03, 1.02],
          [0.28, 1.0],
          [0.54, 0.98],
        ],
      ],
    },
    M: {
      adv: 0.76,
      s: [
        [
          [0.0, 1.08],
          [0.01, 0.5],
          [0.03, -0.05],
        ],
        [
          [0.03, -0.04],
          [0.2, 0.5],
          [0.36, 0.8],
        ],
        [
          [0.36, 0.8],
          [0.52, 0.4],
          [0.68, -0.06],
        ],
        [
          [0.68, -0.05],
          [0.69, 0.5],
          [0.7, 1.08],
        ],
      ],
    },
    N: {
      adv: 0.62,
      s: [
        [
          [0.0, 1.07],
          [0.01, 0.5],
          [0.02, -0.03],
        ],
        [
          [0.03, -0.02],
          [0.27, 0.5],
          [0.5, 1.02],
        ],
        [
          [0.52, 1.07],
          [0.53, 0.5],
          [0.55, -0.1],
        ],
      ],
    },
    O: {
      adv: 0.64,
      s: [
        [
          [0.3, 0.0],
          [0.08, 0.12],
          [0.0, 0.5],
          [0.08, 0.88],
          [0.3, 1.01],
          [0.52, 0.88],
          [0.6, 0.5],
          [0.52, 0.12],
          [0.32, -0.01],
          [0.22, 0.04],
        ],
      ],
    },
    P: {
      adv: 0.58,
      s: [
        [
          [0.02, 1.08],
          [0.01, 0.5],
          [0.03, -0.05],
        ],
        [
          [0.03, 0.0],
          [0.34, -0.01],
          [0.5, 0.13],
          [0.48, 0.38],
          [0.3, 0.52],
          [0.05, 0.52],
        ],
      ],
    },
    Q: {
      adv: 0.66,
      s: [
        [
          [0.3, 0.0],
          [0.08, 0.12],
          [0.0, 0.5],
          [0.08, 0.88],
          [0.3, 1.01],
          [0.52, 0.88],
          [0.6, 0.5],
          [0.52, 0.12],
          [0.32, -0.01],
          [0.22, 0.04],
        ],
        [
          [0.34, 0.72],
          [0.5, 0.9],
          [0.66, 1.1],
        ],
      ],
    },
    R: {
      adv: 0.62,
      s: [
        [
          [0.0, 1.08],
          [0.01, 0.5],
          [0.03, -0.05],
        ],
        [
          [0.03, 0.0],
          [0.34, -0.01],
          [0.5, 0.13],
          [0.48, 0.36],
          [0.3, 0.49],
          [0.05, 0.49],
        ],
        [
          [0.24, 0.49],
          [0.4, 0.78],
          [0.56, 1.07],
        ],
      ],
    },
    S: {
      adv: 0.58,
      s: [
        [
          [0.56, 0.06],
          [0.3, 0.0],
          [0.06, 0.03],
          [0.03, 0.07],
          [0.06, 0.4],
          [0.44, 0.56],
          [0.52, 0.64],
          [0.5, 0.95],
          [0.44, 1.0],
          [0.18, 1.01],
          [-0.02, 0.96],
        ],
      ],
    },
    T: {
      adv: 0.56,
      s: [
        [
          [-0.04, 0.05],
          [0.3, 0.01],
          [0.62, -0.03],
        ],
        [
          [0.31, 0.0],
          [0.3, 0.55],
          [0.28, 1.1],
        ],
      ],
    },
    U: {
      adv: 0.64,
      s: [
        [
          [0.02, -0.08],
          [0.01, 0.5],
          [0.04, 0.84],
          [0.2, 1.01],
          [0.38, 1.01],
          [0.54, 0.84],
          [0.56, 0.5],
          [0.56, -0.08],
        ],
      ],
    },
    V: {
      adv: 0.6,
      s: [
        [
          [-0.02, -0.08],
          [0.14, 0.5],
          [0.29, 1.07],
        ],
        [
          [0.27, 1.06],
          [0.42, 0.5],
          [0.58, -0.08],
        ],
      ],
    },
    W: {
      adv: 0.8,
      s: [
        [
          [-0.02, -0.08],
          [0.1, 0.5],
          [0.2, 1.07],
        ],
        [
          [0.2, 1.06],
          [0.3, 0.6],
          [0.38, 0.25],
        ],
        [
          [0.38, 0.25],
          [0.47, 0.6],
          [0.56, 1.07],
        ],
        [
          [0.56, 1.06],
          [0.66, 0.5],
          [0.78, -0.08],
        ],
      ],
    },
    X: {
      adv: 0.6,
      s: [
        [
          [-0.02, -0.08],
          [0.28, 0.5],
          [0.58, 1.08],
        ],
        [
          [0.58, -0.08],
          [0.28, 0.5],
          [-0.02, 1.08],
        ],
      ],
    },
    Y: {
      adv: 0.6,
      s: [
        [
          [-0.02, -0.08],
          [0.14, 0.25],
          [0.28, 0.52],
        ],
        [
          [0.58, -0.08],
          [0.42, 0.25],
          [0.28, 0.52],
          [0.27, 0.8],
          [0.26, 1.08],
        ],
      ],
    },
    Z: {
      adv: 0.6,
      s: [
        [
          [0.0, 0.02],
          [0.3, 0.0],
          [0.58, -0.02],
        ],
        [
          [0.56, 0.0],
          [0.28, 0.5],
          [0.0, 1.0],
        ],
        [
          [0.0, 1.02],
          [0.3, 1.0],
          [0.6, 0.98],
        ],
      ],
    },
    0: {
      adv: 0.56,
      s: [
        [
          [0.26, 0.0],
          [0.06, 0.14],
          [0.0, 0.5],
          [0.06, 0.88],
          [0.26, 1.01],
          [0.46, 0.88],
          [0.52, 0.5],
          [0.46, 0.12],
          [0.27, -0.01],
        ],
      ],
    },
    1: {
      adv: 0.44,
      s: [
        [
          [0.04, 0.18],
          [0.2, 0.06],
          [0.3, -0.06],
        ],
        [
          [0.3, -0.06],
          [0.29, 0.5],
          [0.28, 1.08],
        ],
      ],
    },
    2: {
      adv: 0.58,
      s: [
        [
          [0.02, 0.2],
          [0.12, 0.04],
          [0.3, -0.01],
          [0.48, 0.08],
          [0.52, 0.28],
          [0.4, 0.52],
          [0.0, 1.0],
        ],
        [
          [0.0, 1.02],
          [0.3, 1.0],
          [0.58, 0.98],
        ],
      ],
    },
    3: {
      adv: 0.58,
      s: [
        [
          [0.04, 0.08],
          [0.26, -0.01],
          [0.46, 0.06],
          [0.5, 0.24],
          [0.4, 0.42],
          [0.2, 0.48],
        ],
        [
          [0.22, 0.48],
          [0.46, 0.56],
          [0.54, 0.76],
          [0.46, 0.95],
          [0.24, 1.02],
          [0.0, 0.94],
        ],
      ],
    },
    4: {
      adv: 0.62,
      s: [
        [
          [0.4, -0.06],
          [0.2, 0.4],
          [0.0, 0.72],
          [0.36, 0.7],
          [0.62, 0.68],
        ],
        [
          [0.46, 0.3],
          [0.45, 0.7],
          [0.44, 1.08],
        ],
      ],
    },
    5: {
      adv: 0.58,
      s: [
        [
          [0.54, 0.0],
          [0.3, 0.01],
          [0.08, 0.02],
        ],
        [
          [0.08, 0.0],
          [0.05, 0.44],
          [0.3, 0.38],
          [0.5, 0.5],
          [0.54, 0.74],
          [0.44, 0.95],
          [0.22, 1.02],
          [0.0, 0.94],
        ],
      ],
    },
    6: {
      adv: 0.58,
      s: [
        [
          [0.48, 0.02],
          [0.28, 0.06],
          [0.1, 0.26],
          [0.02, 0.6],
          [0.08, 0.9],
          [0.26, 1.02],
          [0.46, 0.94],
          [0.54, 0.72],
          [0.44, 0.52],
          [0.24, 0.48],
          [0.06, 0.6],
        ],
      ],
    },
    7: {
      adv: 0.58,
      s: [
        [
          [0.0, 0.02],
          [0.3, 0.0],
          [0.6, -0.02],
          [0.4, 0.4],
          [0.22, 1.08],
        ],
      ],
    },
    8: {
      adv: 0.58,
      s: [
        [
          [0.28, 0.47],
          [0.08, 0.36],
          [0.06, 0.14],
          [0.28, -0.01],
          [0.48, 0.12],
          [0.46, 0.34],
          [0.28, 0.48],
          [0.04, 0.64],
          [0.04, 0.9],
          [0.28, 1.02],
          [0.52, 0.9],
          [0.52, 0.66],
          [0.3, 0.49],
        ],
      ],
    },
    9: {
      adv: 0.58,
      s: [
        [
          [0.5, 0.38],
          [0.3, 0.5],
          [0.1, 0.42],
          [0.04, 0.2],
          [0.2, 0.0],
          [0.42, 0.02],
          [0.52, 0.24],
          [0.5, 0.6],
          [0.36, 0.94],
          [0.1, 1.04],
        ],
      ],
    },
    "!": {
      adv: 0.3,
      s: [
        [
          [0.13, -0.1],
          [0.11, 0.35],
          [0.08, 0.76],
        ],
        [
          [0.06, 0.95],
          [0.1, 1.0],
        ],
      ],
      dot: [1],
    },
    "?": {
      adv: 0.52,
      s: [
        [
          [0.04, 0.14],
          [0.18, 0.0],
          [0.38, 0.02],
          [0.48, 0.2],
          [0.4, 0.4],
          [0.24, 0.52],
          [0.22, 0.74],
        ],
        [
          [0.2, 0.95],
          [0.24, 1.0],
        ],
      ],
      dot: [1],
    },
    ".": {
      adv: 0.24,
      s: [
        [
          [0.06, 0.95],
          [0.1, 1.0],
        ],
      ],
      dot: [0],
    },
    ",": {
      adv: 0.24,
      s: [
        [
          [0.12, 0.9],
          [0.06, 1.14],
        ],
      ],
    },
    ":": {
      adv: 0.26,
      s: [
        [
          [0.1, 0.35],
          [0.13, 0.4],
        ],
        [
          [0.08, 0.92],
          [0.11, 0.97],
        ],
      ],
      dot: [0, 1],
    },
    "-": {
      adv: 0.46,
      s: [
        [
          [0.02, 0.55],
          [0.22, 0.54],
          [0.42, 0.53],
        ],
      ],
    },
    "'": {
      adv: 0.22,
      s: [
        [
          [0.1, -0.06],
          [0.08, 0.24],
        ],
      ],
    },
    "/": {
      adv: 0.5,
      s: [
        [
          [0.5, -0.08],
          [0.0, 1.08],
        ],
      ],
    },
    "+": {
      adv: 0.6,
      s: [
        [
          [0.3, 0.22],
          [0.29, 0.82],
        ],
        [
          [0.0, 0.52],
          [0.6, 0.5],
        ],
      ],
    },
    "*": {
      adv: 0.56,
      s: [
        [
          [0.25, 0.15],
          [0.25, 0.75],
        ],
        [
          [0.0, 0.3],
          [0.5, 0.6],
        ],
        [
          [0.5, 0.3],
          [0.0, 0.6],
        ],
      ],
    },
    "#": {
      adv: 0.62,
      s: [
        [
          [0.18, 0.1],
          [0.12, 1.0],
        ],
        [
          [0.44, 0.1],
          [0.38, 1.0],
        ],
        [
          [0.0, 0.38],
          [0.6, 0.36],
        ],
        [
          [-0.04, 0.72],
          [0.56, 0.7],
        ],
      ],
    },
    "&": {
      adv: 0.66,
      s: [
        [
          [0.6, 1.05],
          [0.2, 0.5],
          [0.12, 0.3],
          [0.2, 0.06],
          [0.36, 0.02],
          [0.44, 0.16],
          [0.36, 0.36],
          [0.08, 0.6],
          [0.04, 0.86],
          [0.2, 1.02],
          [0.4, 0.98],
          [0.62, 0.62],
        ],
      ],
    },
    " ": { adv: 0.64, s: [] },
  };
  // layout -> {strokes:[{pts,kind,li,ch,lcx,under}], bb, cap, nLetters}
  function gLayout(
    str,
    {
      x = 0,
      y = 0,
      cap = 300,
      track = null,
      slant = 0.1,
      rot = -0.05,
      seed = 1,
      bounce = 0.11,
      under = true,
      underFrom = null,
      longbar = false,
      first = 1.18,
    } = {},
  ) {
    str = str.toUpperCase();
    const nl = str.replace(/[^A-Z0-9!?&#]/g, "").length;
    if (track === null) track = nl <= 2 ? 0.1 : nl >= 4 ? 0.05 : 0;
    const st = [];
    let cx = 0;
    const cr = Math.cos(rot),
      sr = Math.sin(rot);
    const tf = (u, v) => {
      const gx = u - v * slant;
      return [x + (gx * cr - v * sr) * cap, y + (gx * sr + v * cr) * cap];
    };
    const lastA = str.lastIndexOf("A");
    let li = 0;
    [...str].forEach((ch, ci) => {
      const g = GCAPS[ch] || (ch === " " ? GCAPS[" "] : null);
      if (!g) {
        warn("graffiti: no glyph for " + JSON.stringify(ch));
        cx += GCAPS[" "].adv + track;
        return;
      }
      if (ch === " ") {
        cx += g.adv + track;
        return;
      }
      const by = hs(seed, ci, 3) * bounce,
        sc = (1 + hs(seed, ci, 4) * 0.12) * (li === 0 ? first : 1),
        lr = hs(seed, ci, 5) * 0.02,
        bx = (g.adv * sc) / 2;
      g.s.forEach((s0, k) => {
        const s = longbar && ch === "A" && k === 2 && ci === lastA ? g.longBar : s0;
        st.push({
          pts: s.map(([u, v]) => {
            const uu = u * sc - bx,
              vv = (v - 1) * sc,
              ru = uu * Math.cos(lr) - vv * Math.sin(lr),
              rv = uu * Math.sin(lr) + vv * Math.cos(lr);
            return tf(cx + bx + ru, 1 + rv + by);
          }),
          kind: (g.dot || []).includes(k) ? "dot" : "stroke",
          li,
          ch,
          lcx: tf(cx + bx, 0.5)[0],
        });
      });
      cx += g.adv * sc + track;
      li++;
    });
    const w = cx - track,
      wu = /[!?.]$/.test(str) ? w - GCAPS[str[str.length - 1]].adv - track + 0.02 : w,
      u0 = underFrom !== null ? underFrom : -0.06;
    if (under && str.trim().length > 1) {
      // heavy underline kinking back into a zigzag
      st.push({
        pts: [tf(u0, 1.2), tf((u0 + wu) * 0.5, 1.17), tf(wu + 0.04, 1.12)],
        kind: "stroke",
        under: 0,
      });
      st.push({
        pts: [tf(u0 + (wu - u0) * 0.86, 1.14), tf(u0 + (wu - u0) * 0.3, 1.33)],
        kind: "thin",
        under: 1,
      });
      st.push({
        pts: [tf(u0 + (wu - u0) * 0.3, 1.33), tf(u0 + (wu - u0) * 0.7, 1.3)],
        kind: "stroke",
        under: 2,
      });
    }
    const P = st.flatMap((s) => s.pts);
    if (!P.length) return { strokes: [], bb: [x, y, x + 1, y + 1], cap, nLetters: 0 };
    return {
      strokes: st,
      bb: [
        Math.min(...P.map((p) => p[0])),
        Math.min(...P.map((p) => p[1])),
        Math.max(...P.map((p) => p[0])),
        Math.max(...P.map((p) => p[1])),
      ],
      cap,
      nLetters: li,
    };
  }
  const mvG = (Gq, dx, dy) => ({
    ...Gq,
    strokes: Gq.strokes.map((st) => ({
      ...st,
      lcx: st.lcx !== undefined ? st.lcx + dx : undefined,
      pts: st.pts.map((p) => [p[0] + dx, p[1] + dy]),
    })),
    bb: [Gq.bb[0] + dx, Gq.bb[1] + dy, Gq.bb[2] + dx, Gq.bb[3] + dy],
  });
  const gLen = (p) => {
    let L = 0;
    for (let i = 1; i < p.length; i++)
      L += Math.hypot(p[i][0] - p[i - 1][0], p[i][1] - p[i - 1][1]);
    return L;
  };
  function nibFill(x, pts, w, th, taper = true) {
    const nx = (Math.cos(th) * w) / 2,
      ny = (Math.sin(th) * w) / 2,
      n = pts.length;
    x.beginPath();
    for (let i = 1; i < n; i++) {
      const t0 = (i - 1) / (n - 1),
        t1 = i / (n - 1),
        k = (t) => (!taper ? 1 : t < 0.04 ? 0.92 : t > 0.94 ? 0.96 : 1);
      const a = pts[i - 1],
        b = pts[i],
        ka = k(t0),
        kb = k(t1);
      x.moveTo(a[0] + nx * ka, a[1] + ny * ka);
      x.lineTo(b[0] + nx * kb, b[1] + ny * kb);
      x.lineTo(b[0] - nx * kb, b[1] - ny * kb);
      x.lineTo(a[0] - nx * ka, a[1] - ny * ka);
      x.closePath();
    }
    x.fill();
  }
  function gDraw(
    x,
    Gq,
    {
      u = 1,
      prog = null,
      b = 0,
      seed = 0,
      nib = 0.14,
      th = -0.62,
      ink = "rgba(17,17,17,.92)",
      halo = "#fff",
      haloK = 0.02,
      echo = "$accent",
      echoD = [14, 10],
      jitk = 0.008,
      streaks = true,
      streakEvery = 1,
      dashes = true,
      alpha = 1,
    } = {},
  ) {
    const cap = Gq.cap,
      w = cap * nib,
      J = cap * jitk;
    ink = col(ink);
    halo = col(halo, null);
    echo = col(echo, null);
    const dense = Gq.strokes.map((s, si) => ({
      ...s,
      d: crPts(
        s.pts.map((p, i) => [
          p[0] + hs(seed + si, b * 17 + i, 1) * J,
          p[1] + hs(seed + si, b * 17 + i, 2) * J,
        ]),
        9,
      ),
    }));
    let cut;
    if (prog) cut = dense.map((s, i) => clamp(prog[i] ?? 1));
    else {
      const lens = dense.map((s) => gLen(s.d)),
        tot = lens.reduce((a, c) => a + c, 0);
      cut = [];
      let rem = clamp(u) * tot;
      dense.forEach((s, i) => {
        const L = lens[i];
        cut.push(rem <= 0 ? 0 : Math.min(1, rem / Math.max(L, 1e-3)));
        rem -= L;
      });
    }
    const part = (s, i) =>
      cut[i] <= 0 ? null : s.d.slice(0, Math.max(2, Math.ceil(s.d.length * cut[i])));
    const wOf = (s) => (s.kind === "thin" ? w * 0.28 : s.kind === "dot" ? w * 1.3 : w);
    x.save();
    x.globalAlpha = alpha;
    x.lineCap = "round";
    x.lineJoin = "round";
    if (halo) {
      x.fillStyle = halo;
      x.strokeStyle = halo;
      dense.forEach((s, i) => {
        const p = part(s, i);
        if (!p) return;
        x.lineWidth = wOf(s) * 0.22 + cap * haloK;
        x.beginPath();
        p.forEach((q, k) => (k ? x.lineTo(q[0], q[1]) : x.moveTo(q[0], q[1])));
        x.stroke();
        nibFill(x, p, wOf(s) + cap * haloK, th, false);
      });
    }
    if (echo) {
      x.fillStyle = echo;
      dense.forEach((s, i) => {
        const p = part(s, i);
        if (!p) return;
        nibFill(
          x,
          p.map((q) => [q[0] + (echoD[0] * cap) / 300, q[1] + (echoD[1] * cap) / 300]),
          wOf(s) * 0.9,
          th,
          s.kind !== "dot",
        );
      });
    }
    x.fillStyle = ink;
    x.strokeStyle = ink;
    dense.forEach((s, i) => {
      const p = part(s, i);
      if (!p) return;
      if (s.kind === "thin") {
        x.lineWidth = wOf(s);
        x.beginPath();
        p.forEach((q, k) => (k ? x.lineTo(q[0], q[1]) : x.moveTo(q[0], q[1])));
        x.stroke();
      } else nibFill(x, p, wOf(s), th, s.kind !== "dot");
    });
    if (streaks) {
      x.strokeStyle = halo || "#fff";
      x.globalAlpha = alpha * 0.8;
      dense.forEach((s, i) => {
        const p = part(s, i);
        if (!p || s.kind !== "stroke" || p.length < 8 || i % streakEvery) return;
        const nx = Math.cos(th),
          ny = Math.sin(th),
          m = 2 + Math.floor(hash(seed + i, 3, 21) * 3);
        for (let k = 0; k < m; k++) {
          const sg = k % 2 ? 1 : -1,
            off = sg * (0.3 + 0.12 * hash(seed + i, k, 22)) * w,
            i0 = Math.floor(p.length * (0.55 + hash(seed + i, k, 23) * 0.2)),
            i1 = p.length;
          if (i1 - i0 < 2) continue;
          x.lineWidth = Math.max(1, cap * 0.0035);
          x.beginPath();
          for (let q = i0; q < i1; q++) {
            const pt = p[q];
            if (q === i0) x.moveTo(pt[0] + nx * off, pt[1] + ny * off);
            else x.lineTo(pt[0] + nx * off, pt[1] + ny * off);
          }
          x.stroke();
        }
      });
      x.globalAlpha = alpha;
    }
    if (dashes) {
      const few = (Gq.nLetters || 9) <= 3;
      dense.forEach((s, i) => {
        const p = part(s, i);
        if (!p || s.kind !== "stroke" || s.li === undefined || p.length < 6) return;
        const a = s.d[0],
          z = s.d[s.d.length - 1],
          dx = z[0] - a[0],
          dy = z[1] - a[1];
        if (Math.abs(dx) > 0.35 * Math.abs(dy)) return;
        if (!(few && (s.ch === "I" || s.ch === "!")) && hash(seed, i, 9) > 0.6) return;
        const top = dy > 0 ? s.d : s.d.slice().reverse(),
          side = s.ch === "I" || s.ch === "!" ? 1 : Math.sign((a[0] + z[0]) / 2 - s.lcx || 1),
          off = w * 0.72 * side;
        const n = top.length,
          j = 1 + hs(seed, i, 14) * 0.3,
          i0 = Math.floor(n * 0.06),
          i1 = Math.floor(n * 0.55);
        if (i1 - i0 < 2) return;
        const path = () => {
          x.beginPath();
          for (let q = i0; q < i1; q++) {
            const pt = top[q];
            if (q === i0) x.moveTo(pt[0] + off, pt[1]);
            else x.lineTo(pt[0] + off, pt[1]);
          }
        };
        x.lineCap = "butt";
        x.setLineDash([w * 0.9 * j, w * 0.5, w * 0.4 * j, w * 0.5]);
        x.lineDashOffset = hash(seed, i, 3) * w;
        if (halo) {
          x.strokeStyle = halo;
          x.lineWidth = w * 0.3 + cap * 0.02;
          path();
          x.stroke();
        }
        x.strokeStyle = ink;
        x.lineWidth = w * 0.3;
        path();
        x.stroke();
        x.setLineDash([]);
        x.lineCap = "round";
      });
    }
    x.restore();
  }
  const REGIONS = {
    left: [0.03, 0.07, 0.5, 0.93],
    right: [0.5, 0.07, 0.97, 0.93],
    top: [0.04, 0.05, 0.96, 0.47],
    bottom: [0.04, 0.53, 0.96, 0.95],
    center: [0.08, 0.16, 0.92, 0.84],
    full: [0.03, 0.05, 0.97, 0.95],
    leftwide: [0.05, 0.05, 0.62, 0.95],
    rightwide: [0.4, 0.05, 0.94, 0.95],
    tl: [0.02, 0.06, 0.3, 0.5],
    tr: [0.7, 0.06, 0.98, 0.5],
    bl: [0.02, 0.5, 0.3, 0.94],
    br: [0.7, 0.5, 0.98, 0.94],
    tl2: [0.04, 0.12, 0.32, 0.55],
    lower: [0.02, 0.27, 0.98, 0.975],
    title: [0.02, 0.21, 0.98, 0.965],
  };
  // fit one or more lines into a region; returns array of laid-out lines
  function fitGraffiti(T) {
    const box = Array.isArray(T.region)
        ? T.region
        : REGIONS[T.region || "center"] || REGIONS.center,
      bx = [box[0] * R.W, box[1] * R.H, box[2] * R.W, box[3] * R.H],
      bw = bx[2] - bx[0],
      bh = bx[3] - bx[1];
    const lines = T.lines || String(T.word || T.text || "").split("\n"),
      cap = T.cap ?? 300,
      seed = T.seed ?? 7;
    const n = lines.length,
      lead = T.leading ?? 0.25,
      dxs = T.line_dx || lines.map(() => 0),
      rots = T.line_rot || lines.map((_, i) => -0.03 - 0.02 * i),
      lsc = T.line_scale || lines.map((_, i) => (i ? 0.92 : 1));
    const unders =
      T.under === false
        ? lines.map(() => false)
        : Array.isArray(T.under)
          ? T.under
          : lines.map((_, i) => i === n - 1);
    const mkL = (c) =>
      lines.map((s, i) =>
        gLayout(s, {
          cap: c * lsc[i],
          seed: seed + i * 3,
          under: unders[i],
          rot: n > 1 ? rots[i] : (T.rot ?? -0.05),
          slant: T.slant ?? 0.1,
          longbar: !!T.longbar,
          bounce: T.bounce ?? 0.11,
        }),
      );
    const hgt = (Gq) => Gq.bb[3] - Gq.bb[1],
      wid = (Gq) => Gq.bb[2] - Gq.bb[0];
    let L = mkL(cap);
    const totalH = (Ls) => Ls.reduce((a, Gq, i) => a + hgt(Gq) * (i ? 1 - lead : 1), 0);
    const s = Math.min(
      1,
      (bw - (n > 1 ? 0.07 * R.W : 0) - 0.1 * cap) / Math.max(...L.map(wid)),
      bh / totalH(L),
    );
    if (s < 1) L = mkL(cap * s);
    const cx = (bx[0] + bx[2]) / 2;
    let top = (bx[1] + bx[3]) / 2 - totalH(L) / 2;
    const out = [];
    L.forEach((Gq, i) => {
      const y0 = i ? out[i - 1].bb[3] - hgt(Gq) * lead : top;
      out.push(mvG(Gq, cx - (Gq.bb[0] + Gq.bb[2]) / 2 + dxs[i] * R.W, y0 - Gq.bb[1]));
    });
    const U = unionR(out.map((g) => g.bb)),
      m = 0.012 * cap;
    let dx = 0;
    if (U[2] - U[0] > bw - 2 * m) dx = cx - (U[0] + U[2]) / 2;
    else dx = U[2] + m > bx[2] ? bx[2] - U[2] - m : U[0] - m < bx[0] ? bx[0] - U[0] + m : 0;
    return dx ? out.map((g) => mvG(g, dx, 0)) : out;
  }
  // per-stroke write-on locked to keys: letter li writes between wkeys[li] and wkeys[li+1]; underline chains after
  function strokeTimes(Gq, wkeys) {
    const out = [],
      n = Gq.nLetters,
      K = wkeys,
      cnt = {},
      idx = {};
    Gq.strokes.forEach((s) => {
      if (s.li !== undefined) cnt[s.li] = (cnt[s.li] || 0) + 1;
    });
    let ut = K[Math.min(n, K.length - 1)];
    Gq.strokes.forEach((s) => {
      if (s.li !== undefined) {
        const k0 = K[Math.min(s.li, K.length - 1)],
          k1 = K[s.li + 1] ?? k0 + 0.2,
          m = cnt[s.li],
          j = (idx[s.li] = (idx[s.li] || 0) + 1) - 1,
          d = Math.min(2 / R.fps, (k1 - k0) / m);
        out.push([k0 + j * d, d]);
      } else {
        const d = s.under === 0 ? 2 / R.fps : 1 / R.fps;
        out.push([ut, d]);
        ut += d;
      }
    });
    return out;
  }

  // ============================================================ TEXT: global text events (edl.text[])
  // entry: {init(T) -> void, draw(S, T, x), cues(T) -> [{t,k,d}]}; T has t0/t1 (s) and bbox for avoidance
  const TEXT = {
    graffiti: {
      init(T, i) {
        T.seed = T.seed ?? 7 + i * 13;
        T.G = fitGraffiti(T);
        const letters = (T.lines ? T.lines.join("") : String(T.word || T.text || "")).replace(
          /[^A-Z0-9!?&#]/gi,
          "",
        ).length;
        T.wdur = T.wdur ?? Math.min(Math.max(0.2, (T.t1 - T.t0) * 0.75), 0.12 + 0.22 * letters);
        if (T.wkeys) {
          T.wk = T.wkeys.map((T_) => RRC.T(T_));
          T.ST = T.G.map((g) => strokeTimes(g, T.wk));
        }
        T.bbox = unionR(T.G.map((g) => g.bb));
        T.pad = 0.12 * (T.cap ?? 300) + 30;
        T.capv = T.cap ?? 300;
      },
      draw(S, T, x, ti) {
        const spec = S.kind === "special" ? S.special.type : null,
          Gs = T.G,
          age = S.t - T.t0,
          fr = Math.floor(age * R.fps + 1e-6),
          hold = T.mode === "hold";
        let prog = null,
          u = 1;
        if (T.mode === "write") {
          if (T.ST) prog = T.ST.map((st) => st.map(([s, d]) => clamp((S.t - s) / d)));
          else u = clamp(age / T.wdur);
        }
        const SC = T.sc || [1.3, 0.9, 1.06, 1];
        let sc = T.mode === "slam" ? SC[Math.min(fr, SC.length - 1)] : 1;
        const sh =
            T.mode === "slam" && fr < 5 ? [hs(S.f, 1, ti) * 12, hs(S.f, 2, ti) * 10] : [0, 0],
          sk = hold ? [0, 0] : [hs(S.k, 1, ti + 40) * 7, hs(S.k, 2, ti + 40) * 6];
        const U = unionR(Gs.map((g) => g.bb));
        let ax = (U[0] + U[2]) / 2,
          ay = (U[1] + U[3]) / 2;
        const face = S.fo && !spec ? S.fo.box : null;
        if (face) {
          const fcx = (face[0] + face[2]) / 2;
          if (face[3] < U[1]) ay = U[1];
          else ax = (U[0] + U[2]) / 2 < fcx ? U[2] : U[0];
          const F2 = padR(face, 10);
          while (sc > 1.001) {
            const Sx = [
              ax + (U[0] - ax) * sc,
              ay + (U[1] - ay) * sc,
              ax + (U[2] - ax) * sc,
              ay + (U[3] - ay) * sc,
            ];
            if (!hit(Sx, F2)) break;
            sc = Math.max(1, sc - 0.05);
          }
        }
        while (sc > 1.001) {
          const Sx = [
            ax + (U[0] - ax) * sc,
            ay + (U[1] - ay) * sc,
            ax + (U[2] - ax) * sc,
            ay + (U[3] - ay) * sc,
          ];
          if (
            Sx[0] >= 0.03 * R.W &&
            Sx[2] <= 0.97 * R.W &&
            Sx[1] >= 0.03 * R.H &&
            Sx[3] <= 0.97 * R.H
          )
            break;
          sc = Math.max(1, sc - 0.05);
        }
        sh[0] = clamp(sh[0], 0.03 * R.W - U[0], 0.97 * R.W - U[2]);
        sh[1] = clamp(sh[1], 0.03 * R.H - U[1], 0.97 * R.H - U[3]);
        x.save();
        x.translate(ax + sh[0] + sk[0], ay + sh[1] + sk[1]);
        x.scale(sc, sc);
        x.translate(-ax, -ay);
        const nib = T.nib || 0.14;
        Gs.forEach((Gq, gi) =>
          gDraw(x, Gq, {
            u,
            prog: prog ? prog[gi] : null,
            b: hold ? 0 : S.b,
            seed: T.seed + gi * 5,
            halo: spec === "flash" ? null : (T.halo_color ?? "#fff"),
            haloK: T.halo ?? 0.02,
            nib,
            streakEvery: nib > 0.15 ? 2 : 1,
            ink: T.ink ?? "rgba(17,17,17,.92)",
            echo: T.echo ?? "$accent",
          }),
        );
        x.restore();
      },
      cues(T) {
        if (T.mode === "slam") return [{ t: T.t0, k: "slam" }];
        if (T.mode !== "write") return [];
        if (T.ST) return T.ST.flat().map(([s, d]) => ({ t: s, k: "marker", d }));
        return [{ t: T.t0, k: "marker", d: T.wdur }];
      },
    },
    // generic font text: {text, pos:[x,y] | anchor:'face', o:[dx,dy] (eye units), size | size_eu, anim:'pop'|'slam'|'fade'|'type'|'none'}
    font: {
      init(T) {
        if (T.anchor !== "face" && T.pos) {
          const c = R.L.tmp.x;
          reset(c);
          const size = T.size ?? 96;
          c.font = fontStr(T, size, T.kind);
          const w = c.measureText(T.text || "").width;
          const [X, Y] = [T.pos[0] * R.W, T.pos[1] * R.H];
          const al = T.align || "center";
          const x0 = al === "center" ? X - w / 2 : al === "right" ? X - w : X;
          T.bbox = [x0, Y - size * 0.6, x0 + w, Y + size * 0.6];
          T.pad = 24;
        }
      },
      draw(S, T, x) {
        drawFontText(S, T, x, S.t - T.t0, T.t1 - T.t0);
      },
      cues(T) {
        return T.sfx ? [{ t: T.t0, k: T.sfx }] : [];
      },
    },
  };
  function drawFontText(S, T, x, age, dur) {
    let X,
      Y,
      size = T.size ?? 96,
      rot = T.rot ?? 0;
    if (T.anchor === "face") {
      const F = foOr(S);
      [X, Y] = fp(S, ...(T.o || [0, 1.05]));
      if (T.size_eu) size = clamp(F.D * T.size_eu, T.min ?? 0, T.max ?? 1e9);
      rot += F.a;
    } else {
      const p = T.pos || [0.5, 0.5];
      X = p[0] * R.W;
      Y = p[1] * R.H;
    }
    const anim = T.anim || "none",
      d = T.anim_d ?? (anim === "fade" ? 0.15 : 0.1);
    let sc = 1,
      alpha = T.alpha ?? 1,
      txt = String(T.text ?? "");
    if (anim === "pop") {
      const k = clamp(age * R.fps, 0, 3);
      sc = 1 + (T.pop ?? 0.18) * (1 - k / 3);
    } else if (anim === "slam") {
      const SC = T.sc || [1.3, 0.9, 1.06, 1];
      sc = SC[Math.min(Math.floor(age * R.fps + 1e-6), SC.length - 1)];
    } else if (anim === "fade") alpha *= clamp(age / d);
    else if (anim === "grow") sc = 0.85 + 0.15 * easeOut(age / d);
    if (T.fade_out) alpha *= clamp((dur - age) / T.fade_out);
    if (T.boil) {
      X += hs(S.b, 1, T.seed || 3) * T.boil;
      Y += hs(S.b, 2, T.seed || 3) * T.boil;
    }
    if (anim === "type" || T.parts) {
      const parts = T.parts || [[txt, T.kind || "bold"]],
        nAll = parts.reduce((a, [s]) => a + s.length, 0);
      const n =
        anim === "type"
          ? Math.min(nAll, Math.floor(age / (T.dt ?? 0.05)) + 1 + (T.base ?? 0))
          : nAll;
      x.save();
      x.globalAlpha = alpha;
      typeWord(x, parts, X, Y, size, n, rot, T);
      x.restore();
      return;
    }
    x.save();
    x.globalAlpha = alpha;
    outlinedText(
      x,
      txt,
      X,
      Y,
      fontStr(T, size, T.kind),
      T.fill ?? "$white",
      T.stroke === undefined ? "$lav" : T.stroke,
      T.lw ?? 5,
      rot,
      sc,
      T.align || "center",
      T.shadow ?? "glow",
    );
    x.restore();
  }
  TEXT.word = TEXT.font;
  TEXT.caption = TEXT.font;

  // ============================================================ LAYERS / FACE / TRANSITIONS tables
  // entry: {phase:'back'|'subject'|'over'|'post'|'final', order, draw(S, p, x)} or {phases:{back:{order,draw}, over:{...}}}
  // p: params object (`true` -> {}, a number -> {v: n}); timing fields `at`/`d` are seconds from the shot start.
  const win = (S, p, dflt = 1e9) => {
    const d = p.d ?? dflt,
      at = p.at ?? (p.side === "out" ? S.dur - d : 0);
    return S.lt >= at && S.lt < at + d ? (S.lt - at) / d : -1;
  };
  function mosaic(S, x, block, region) {
    const cw = Math.max(1, Math.round(R.W / block)),
      ch = Math.max(1, Math.round(R.H / block)),
      t = R.L.tmp.x;
    t.setTransform(1, 0, 0, 1, 0, 0);
    t.globalCompositeOperation = "copy";
    t.imageSmoothingEnabled = true;
    t.drawImage(R.canvas, 0, 0, cw, ch);
    t.globalCompositeOperation = "source-over";
    x.save();
    x.imageSmoothingEnabled = false;
    if (region) x.clip(region);
    x.drawImage(R.L.tmp, 0, 0, cw, ch, 0, 0, R.W, R.H);
    x.restore();
  }
  function glitchBlocks(S, x, seed, amt, fo, rad, tile = 64, block = 22) {
    const r = rng(seed + Math.floor(S.f / 2) * 31),
      reg = new Path2D(),
      wash = new Path2D();
    for (let y = 0; y < R.H; y += tile)
      for (let X = 0; X < R.W; X += tile) {
        if (fo && Math.hypot(X + tile / 2 - fo.x, (y + tile / 2 - fo.y) * 1.2) > rad) continue;
        const v = r();
        if (v < amt) reg.rect(X, y, tile, tile);
        else if (v < amt + 0.14) wash.rect(X, y, tile, tile);
      }
    mosaic(S, x, block, reg);
    x.save();
    x.fillStyle = "rgba(255,250,255,0.6)";
    x.fill(wash);
    x.restore();
  }
  function blurFrame(S, x, rad, frame) {
    const t = R.L.tmp.x;
    t.setTransform(1, 0, 0, 1, 0, 0);
    t.globalCompositeOperation = "copy";
    t.drawImage(R.canvas, 0, 0);
    t.globalCompositeOperation = "source-over";
    x.save();
    x.filter = `blur(${px(rad)}px)`;
    x.drawImage(R.L.tmp, -20, -15, R.W + 40, R.H + 30);
    x.restore();
    if (frame) {
      x.save();
      x.strokeStyle = "rgba(55,45,60,0.8)";
      x.lineWidth = 5;
      x.strokeRect(5, 5, R.W - 10, R.H - 10);
      const g = x.createRadialGradient(R.W / 2, R.H / 2, R.H * 0.45, R.W / 2, R.H / 2, R.H * 0.85);
      g.addColorStop(0, "rgba(0,0,0,0)");
      g.addColorStop(1, "rgba(30,20,35,0.22)");
      x.fillStyle = g;
      x.fillRect(0, 0, R.W, R.H);
      x.restore();
    }
  }
  // flashlight burn (Yaong): exposure blow-out where darks survive + white bloom from the face + pixel blocks
  function flashlight(S, x, k, seed, blocks) {
    if (k <= 0) return;
    const fo = foOr(S),
      t = R.L.tmp.x;
    t.setTransform(1, 0, 0, 1, 0, 0);
    t.globalCompositeOperation = "copy";
    t.drawImage(R.canvas, 0, 0);
    t.globalCompositeOperation = "source-over";
    x.save();
    x.setTransform(1, 0, 0, 1, 0, 0);
    x.filter = `brightness(${1 + 1.35 * k}) contrast(${1 + 0.3 * k}) saturate(${1 - 0.45 * k})`;
    x.drawImage(R.L.tmp, 0, 0);
    x.restore();
    const g = x.createRadialGradient(fo.x, fo.y, 0, fo.x, fo.y, fo.D * (2 + 6 * k));
    g.addColorStop(0, `rgba(255,255,255,${0.5 * k})`);
    g.addColorStop(0.45, `rgba(255,245,252,${0.3 * k})`);
    g.addColorStop(1, "rgba(255,255,255,0)");
    x.save();
    x.globalCompositeOperation = "screen";
    x.fillStyle = g;
    x.fillRect(0, 0, R.W, R.H);
    x.restore();
    if (blocks && k > 0.3) glitchBlocks(S, x, seed, 0.18 + 0.2 * k, fo, fo.D * 3.2);
  }
  function starburst(c, cx, cy, Rr, seed, f, rot, p = {}) {
    const r = rng(seed * 97 + Math.floor(f / 3)),
      n = p.points ?? 15,
      pts = [];
    for (let i = 0; i < n; i++) {
      const a = rot + (i / n) * TAU + (r() - 0.5) * 0.12,
        ai = a + Math.PI / n + (r() - 0.5) * 0.1;
      pts.push([
        cx + Math.cos(a) * Rr * (0.86 + r() * 0.34),
        cy + Math.sin(a) * Rr * (0.86 + r() * 0.34),
      ]);
      pts.push([
        cx + Math.cos(ai) * Rr * (0.5 + r() * 0.12),
        cy + Math.sin(ai) * Rr * (0.5 + r() * 0.12),
      ]);
    }
    const P = new Path2D();
    pts.forEach(([X, Y], i) => (i ? P.lineTo(X, Y) : P.moveTo(X, Y)));
    P.closePath();
    c.save();
    c.fillStyle = col(p.fill ?? "$lavl");
    c.fill(P);
    c.clip(P);
    for (let i = 0; i < pts.length; i += 4) {
      const q = new Path2D();
      q.moveTo(cx, cy);
      q.lineTo(...pts[i]);
      q.lineTo(...pts[(i + 2) % pts.length]);
      q.closePath();
      c.fillStyle = col(p.rays ?? "rgba(255,255,255,0.55)");
      c.fill(q);
    }
    c.restore();
    c.lineWidth = p.lw ?? 3;
    c.strokeStyle = col(p.stroke ?? "$lav");
    c.lineJoin = "miter";
    c.stroke(P);
  }
  function slashes(c, cx, cy, fs, ang, prog, f, seed, p = {}) {
    const r = rng(seed + Math.floor(f / 2) * 13);
    c.save();
    c.translate(cx, cy);
    c.rotate(ang - 0.36);
    const grow = easeOut(prog * 3);
    for (let k = 0; k < (p.n ?? 4); k++) {
      const yoff = (k - 1.5) * fs * 0.16 + (r() - 0.5) * 10,
        len = fs * (2.6 + r() * 0.9) * grow,
        x0 = -fs * 1.3 + (r() - 0.5) * 50,
        wmax = fs * (0.035 + r() * 0.035),
        seg = 9,
        top = [],
        bot = [];
      for (let i = 0; i <= seg; i++) {
        const v = i / seg,
          X = x0 + v * len,
          w = wmax * Math.sin(Math.PI * Math.pow(v, 0.7)) * (0.7 + r() * 0.6),
          j = (r() - 0.5) * wmax * 0.8;
        top.push([X, yoff - w + j]);
        bot.push([X, yoff + w * 0.5 + j]);
      }
      const q = new Path2D();
      top.forEach(([X, Y], i) => (i ? q.lineTo(X, Y) : q.moveTo(X, Y)));
      bot.reverse().forEach(([X, Y]) => q.lineTo(X, Y));
      q.closePath();
      c.shadowColor = "rgba(255,255,255,0.9)";
      c.shadowBlur = px(16);
      c.fillStyle = col(p.fill ?? "rgba(255,255,255,0.96)");
      c.fill(q);
      c.shadowBlur = 0;
      c.lineWidth = 2;
      c.strokeStyle = col(p.stroke ?? "rgba(205,150,230,0.8)");
      c.stroke(q);
    }
    c.restore();
  }
  function penContour(x, Gd, S, { dist = 12, w = 4.2, color = "$ink", zigs = 5, seed = 0 } = {}) {
    const b = S.b;
    color = col(color);
    Gd.lines.forEach((L0, li) => {
      const L = L0.filter((p, i) => i % 2 === 0);
      if (L.length < 12) return;
      const n = L.length;
      const nrm = L.map((p, i) => {
        const a = L[(i - 2 + n) % n],
          c = L[(i + 2) % n];
        const tx = c[0] - a[0],
          ty = c[1] - a[1],
          l = Math.hypot(tx, ty) || 1;
        return [-ty / l, tx / l];
      });
      let vote = 0;
      for (let i = 0; i < n; i += 3) {
        const p = L[i],
          q = nrm[i];
        vote +=
          gridAt(Gd, p[0] + q[0] * 8, p[1] + q[1] * 8) <
          gridAt(Gd, p[0] - q[0] * 8, p[1] - q[1] * 8)
            ? 1
            : -1;
      }
      const sg = vote >= 0 ? 1 : -1;
      let i = Math.floor(hash(seed + li, b, 1) * 6),
        ch = 0;
      x.save();
      x.lineCap = "round";
      x.lineJoin = "round";
      x.strokeStyle = color;
      while (i < n - 2) {
        const len = 8 + Math.floor(hash(seed + li, b * 31 + ch, 2) * 26),
          gap = 1 + Math.floor(hash(seed + li, b * 31 + ch, 3) * 4),
          dd = dist * (0.8 + 0.5 * hash(seed + li, b * 31 + ch, 4));
        const pts = [];
        for (let k = i; k < Math.min(n, i + len); k++) {
          const p = L[k],
            q = nrm[k];
          pts.push([
            p[0] + q[0] * sg * dd + hs(seed, b * 7 + k, 5) * 1.4,
            p[1] + q[1] * sg * dd + hs(seed, b * 7 + k, 6) * 1.4,
          ]);
        }
        x.lineWidth = w * (0.7 + 0.5 * hash(seed + li, b * 31 + ch, 7));
        x.beginPath();
        pts.forEach((p, k) => (k ? x.lineTo(p[0], p[1]) : x.moveTo(p[0], p[1])));
        x.stroke();
        if (hash(seed + li, b * 31 + ch, 8) < 0.18) {
          x.lineWidth = w * 0.55;
          x.beginPath();
          pts.forEach((p, k) => {
            const q = nrm[Math.min(n - 1, i + k)];
            const X = p[0] + q[0] * sg * 7,
              Y = p[1] + q[1] * sg * 7;
            if (k) x.lineTo(X, Y);
            else x.moveTo(X, Y);
          });
          x.stroke();
        }
        i += len + gap;
        ch++;
      }
      for (let z = 0; z < zigs; z++) {
        const k = Math.floor(hash(seed + li, z, 9 + Math.floor(S.f / 12)) * n),
          p = L[k],
          q = nrm[k];
        const t = [q[1], -q[0]],
          c = [p[0] + q[0] * sg * (dist + 16), p[1] + q[1] * sg * (dist + 16)];
        const zz = [];
        for (let m = 0; m < 6; m++) {
          const u = (m / 5 - 0.5) * 42,
            v = (m % 2 ? 1 : -1) * 7;
          zz.push([
            c[0] + t[0] * u + q[0] * sg * v + hs(seed, b * 3 + m, z) * 1.5,
            c[1] + t[1] * u + q[1] * sg * v + hs(seed, b * 3 + m, z + 5) * 1.5,
          ]);
        }
        x.lineWidth = w * 0.8;
        x.beginPath();
        zz.forEach((p, m) => (m ? x.lineTo(p[0], p[1]) : x.moveTo(p[0], p[1])));
        x.stroke();
      }
      x.restore();
    });
  }
  // ink doodles hugging the silhouette (Katana): ring around the dilated mask, trailing the motion, avoiding faces/text
  async function inkDoodles(S, x, n, avoid, force, p = {}) {
    const k = S.k,
      cl = S.dur,
      u = cl > 0.6 ? clamp(S.lt / 0.8) : clamp((S.lt * R.fps + 1) / 3),
      OGW = R.OGW,
      OGH = R.OGH;
    const occ = S.occ,
      lum = S.lum,
      occD = occ ? dilateG(occ, 2) : null,
      ring = [];
    if (occD) {
      const big = dilateG(occD, 9);
      for (let i = 0; i < OGW * OGH; i++) if (big[i] && !occD[i]) ring.push(i);
    }
    const colAt = (X, Y, h) => {
      if (p.mono) return "$ink";
      const L = lum
        ? lum[
            clamp(Math.floor(Y / CELL), 0, OGH - 1) * OGW + clamp(Math.floor(X / CELL), 0, OGW - 1)
          ]
        : 1;
      if (L < 0.35) return "$accent";
      return h < 0.55 ? "$ink" : "$accent2";
    };
    const inOcc = (X, Y) =>
      occD &&
      occD[clamp(Math.floor(Y / CELL), 0, OGH - 1) * OGW + clamp(Math.floor(X / CELL), 0, OGW - 1)];
    const motion = S.motion,
      ang0 = motion ? Math.atan2(motion[1], motion[0]) : null;
    let inside = 0,
      placed = 0;
    let cen = null;
    if (occD) {
      let sx = 0,
        sy = 0,
        m = 0;
      for (let q = 0; q < OGW * OGH; q++)
        if (occD[q]) {
          sx += q % OGW;
          sy += Math.floor(q / OGW);
          m++;
        }
      if (m) cen = [sx / m, sy / m];
    }
    const pick = (i, trailing) => {
      for (let t = 0; t < 12; t++) {
        const r = hash(k, i * 13 + t, 9);
        let X, Y;
        if (ring.length && r < 0.7) {
          const c = ring[Math.floor(hash(k, i * 13 + t, 1) * ring.length)];
          X = ((c % OGW) + 0.5) * CELL;
          Y = (Math.floor(c / OGW) + 0.5) * CELL;
          if (
            trailing &&
            motion &&
            cen &&
            (X / CELL - cen[0]) * motion[0] + (Y / CELL - cen[1]) * motion[1] > 0
          )
            continue;
        } else {
          X = (0.04 + hash(k, i * 13 + t, 1) * 0.92) * R.W;
          Y = (0.06 + hash(k, i * 13 + t, 2) * 0.88) * R.H;
        }
        if (avoid.some(([a, b, c, d]) => X > a && X < c && Y > b && Y < d)) continue;
        return [X, Y];
      }
      return null;
    };
    const sizeOf = (ty, i) =>
      INK_GESTURES.has(ty) ? 90 + hash(k, i, 5) * 70 : 30 + hash(k, i, 5) * 50;
    const angOf = (i) => (ang0 !== null ? ang0 + hs(k, i, 6) * 0.3 : hs(k, i, 6) * 1.2);
    const ext = (ty, X, Y, i) => {
      const g = INK_GESTURES.has(ty),
        s = sizeOf(ty, i),
        a = angOf(i);
      const L = ty === "zig" ? s * 3.2 : ty === "scratch" ? 420 : ty === "arrow" ? s * 1.6 : 0,
        r = ty === "splat" ? s * 1.2 : ty === "zig" ? s * 0.6 : ty === "scratch" ? 40 : s * 0.8;
      for (let j = 0; j <= 10; j++) {
        const uu = ty === "arrow" ? j / 10 : j / 10 - 0.5,
          px_ = X + Math.cos(a) * L * uu,
          py = Y + Math.sin(a) * L * uu;
        if (avoid.some(([A, B, Cc, D]) => px_ > A - r && px_ < Cc + r && py > B - r && py < D + r))
          return true;
        if (g && ty !== "splat" && inOcc(px_, py)) return true;
      }
      return false;
    };
    const types = p.types || [
      "zig",
      "zig",
      "scratch",
      "splat",
      "arrow",
      "rays",
      "hatch",
      "cross",
      "spark",
      "xx",
      "bolt",
      "bang",
      "star",
    ];
    const textOn = R.texts.some((Tg) => S.t >= Tg.t0 && S.t < Tg.t1);
    const draw = (ty, X, Y, i, color) => {
      const fn = DOODLES.ink[ty];
      if (fn) fn(x, X, Y, sizeOf(ty, i), S, k * 97 + i, { ang: angOf(i), u, color });
    };
    for (let f = 0; f < force; f++)
      for (let tr = 0; tr < 4; tr++) {
        const q = pick(500 + f * 7 + tr, true);
        if (q && !ext("scratch", q[0], q[1], 500 + f * 7 + tr) && !inOcc(q[0], q[1])) {
          draw("scratch", q[0], q[1], 500 + f * 7 + tr, "$accent");
          break;
        }
      }
    for (let i = 0; i < n * 8 && placed < n; i++) {
      const ty = types[Math.floor(hash(k, i, 3) * types.length)];
      if (ty === "bang" && textOn) continue;
      const q = pick(i, ty === "zig" || ty === "scratch");
      if (!q) continue;
      if (ext(ty, q[0], q[1], i)) continue;
      const [X, Y] = q;
      if (inOcc(X, Y)) {
        if (inside > 0 || !(ty === "hatch" || ty === "cross")) continue;
        inside++;
      }
      placed++;
      draw(ty, X, Y, i, colAt(X, Y, hash(k, i, 4)));
    }
  }
  // auto layout of kawaii doodles in eye units around a face-locked subject (port of the Yaong edl.py planner)
  const FD_CACHE = new Map();
  function genFaceDoodles(S, p) {
    const key = S.k + ":" + JSON.stringify(p);
    if (FD_CACHE.has(key)) return FD_CACHE.get(key);
    const cam = { ...R.camDefault, ...S.shot.cam },
      r = rng(p.seed ?? S.k * 13 + 1),
      D = (p.ld ?? cam.ld ?? 0.15) * R.W,
      ly = p.ly ?? cam.ly ?? 0.47,
      pool = p.pool || ["heart", "spark", "star", "note", "dots", "squig"];
    const xmax = (R.W / 2 - 70) / D,
      ymin = -(ly * R.H - 70) / D,
      ymax = ((1 - ly) * R.H - 80) / D,
      out = [];
    let tries = 0;
    while (out.length < (p.n ?? 6) && tries < 800) {
      tries++;
      const X = lerp(-xmax, xmax, r()),
        Y = lerp(ymin, ymax, r());
      if (Math.abs(X) < 1.35 && Y > -1.4 && Y < 2.05) continue;
      if (p.ears && Math.abs(X) < 1.9 && Y < -1.0) continue;
      if (p.avoid_top && Y < -1.2 && Math.abs(X) < 2.2) continue;
      if (out.some((o) => Math.hypot(X - o.o[0], Y - o.o[1]) < (p.spacing ?? 1.35))) continue;
      const t = pool[out.length % pool.length];
      out.push({
        t,
        o: [X, Y],
        s: (KAWAII_SIZE[t] ?? 0.6) * lerp(0.85, 1.2, r()),
        r: lerp(-0.5, 0.5, r()),
        at: lerp(0, 0.12, r()),
      });
    }
    FD_CACHE.set(key, out);
    return out;
  }
  // subject cutout over back graphics (+ offset outline drawn first)
  function drawOutline(S, x, p) {
    if (!S.mask) return;
    const C = S.clip,
      M = S.M,
      o = R.L.outl,
      oc = o.x,
      s = R.rs / 2,
      rad = p.r ?? 14;
    oc.setTransform(1, 0, 0, 1, 0, 0);
    oc.globalCompositeOperation = "source-over";
    oc.clearRect(0, 0, o.width, o.height);
    for (let k = 0; k < 12; k++) {
      const a = (k / 12) * TAU;
      oc.setTransform(
        M[0] * s,
        M[1] * s,
        M[2] * s,
        M[3] * s,
        (M[4] + Math.cos(a) * rad) * s,
        (M[5] + Math.sin(a) * rad) * s,
      );
      oc.drawImage(S.mask, 0, 0, C.w, C.h);
    }
    oc.setTransform(1, 0, 0, 1, 0, 0);
    oc.globalCompositeOperation = "source-in";
    oc.fillStyle = col(p.color ?? "$outline");
    oc.fillRect(0, 0, o.width, o.height);
    oc.globalCompositeOperation = "source-over";
    x.save();
    x.filter = `blur(${px(p.blur ?? 3)}px)`;
    x.globalAlpha = p.alpha ?? 0.95;
    x.drawImage(o, p.dx ?? 16, p.dy ?? 6, R.W, R.H);
    x.restore();
  }
  function drawCutout(S, x) {
    if (!S.mask) return;
    const cc = R.L.cut.x;
    cc.setTransform(1, 0, 0, 1, 0, 0);
    cc.globalCompositeOperation = "source-over";
    cc.clearRect(0, 0, R.PW, R.PH);
    setM(cc, S.M);
    cc.drawImage(S.mask, 0, 0, S.clip.w, S.clip.h);
    cc.setTransform(1, 0, 0, 1, 0, 0);
    cc.globalCompositeOperation = "source-in";
    cc.drawImage(S.looked.canvas || S.looked, 0, 0);
    cc.globalCompositeOperation = "source-over";
    copyFull(x, R.L.cut);
  }
  let GRAIN = null;
  function grainTiles(p) {
    const n = p.tiles ?? 4,
      cell = p.cell ?? 2,
      w = Math.ceil(R.PW / cell),
      h = Math.ceil(R.PH / cell),
      key = `${n}:${cell}:${w}:${h}:${p.mono !== false}`;
    if (GRAIN && GRAIN.key === key) return GRAIN.t;
    const t = [];
    for (let k = 0; k < n; k++) {
      const g = mk(w, h),
        gc = g.x,
        d = gc.createImageData(w, h),
        r = rng(k + 5);
      for (let i = 0; i < d.data.length; i += 4) {
        const v = 128 + (r() + r() + r() - 1.5) * 120;
        d.data[i] = v;
        d.data[i + 1] = p.mono === false ? 128 + (r() - 0.5) * 120 : v;
        d.data[i + 2] = p.mono === false ? 128 + (r() - 0.5) * 120 : v;
        d.data[i + 3] = 255;
      }
      gc.putImageData(d, 0, 0);
      t.push(g);
    }
    GRAIN = { key, t };
    return t;
  }

  const LAYERS = {
    // ---- back (behind the subject; force a cutout re-draw of the subject on top)
    big: {
      phase: "back",
      order: 20,
      cut: true,
      draw(S, p, x) {
        // giant letters behind the subject (Yaong DUL)
        const s = p.size ?? 600,
          k = easeOut(clamp((S.lt - (p.at ?? 0)) / 0.06)),
          chars = String(p.text || p.v || "").split(""),
          n = chars.length;
        chars.forEach((ch, i) => {
          const X =
              R.W * lerp(p.x0 ?? 0.17, p.x1 ?? 0.83, n > 1 ? i / (n - 1) : 0.5) +
              S.lt * 30 * (i - 1),
            Y = R.H * (p.y ?? 0.55) + (i % 2 ? -40 : 30);
          outlinedText(
            x,
            ch,
            X,
            Y,
            fontStr(p, s, "heavy"),
            p.fill ?? "$bigfill",
            p.stroke ?? "$bigstroke",
            p.lw ?? 8,
            (i - 1) * 0.06 - 0.03,
            0.85 + 0.15 * k,
            "center",
            false,
          );
        });
      },
    },
    stairs: {
      phase: "back",
      order: 30,
      draw(S, p, x) {
        // pixel stair pattern (Yaong), top-left by default
        const r = rng((p.seed ?? 3) + Math.floor(S.f / 4)),
          sz = p.size ?? 34,
          cells = p.cells || [
            [0, 0],
            [1, 0],
            [0, 1],
            [2, 1],
            [1, 2],
            [3, 2],
            [2, 3],
            [0, 3],
            [4, 3],
          ],
          ox = (p.x ?? 0.025) * R.W,
          oy = (p.y ?? 0.028) * R.H;
        cells.forEach(([i, j]) => {
          if (r() < 0.12) return;
          x.fillStyle =
            r() < 0.35 ? col(p.color2 ?? "rgba(244,196,240,0.6)") : col(p.color ?? "$pink");
          x.fillRect(ox + i * sz * 1.25, oy + j * sz * 1.25, sz, sz);
        });
      },
    },
    // ---- subject
    outline: { phase: "subject", order: 10, draw: (S, p, x) => drawOutline(S, x, p) },
    cutout: { phase: "subject", order: 20, draw: (S, p, x) => drawCutout(S, x) },
    glow: {
      phase: "subject",
      order: 90,
      draw(S, p, x) {
        // soft screen glow of the whole frame (Yaong 0.14)
        const sm = R.L.small,
          sc = sm.x;
        sc.setTransform(1, 0, 0, 1, 0, 0);
        sc.clearRect(0, 0, sm.width, sm.height);
        sc.filter = `blur(${px(p.blur ?? 5)}px)`;
        sc.drawImage(R.canvas, 0, 0, sm.width, sm.height);
        sc.filter = "none";
        x.save();
        x.globalCompositeOperation = "screen";
        x.globalAlpha = p.v ?? p.amt ?? 0.14;
        x.drawImage(sm, 0, 0, R.W, R.H);
        x.restore();
      },
    },
    // ---- over: graphics on top of the subject
    contour: {
      phase: "over",
      order: 10,
      draw(S, p, x) {
        // pen contour from the mask (Katana)
        if (!S.mask) return;
        const Gd = contours(S.mask, S.M, S.clip, p.blur ?? 2.2),
          neg = p.color === undefined && lookSpec(S.shot.look ?? R.E.look).invert;
        const c =
          p.color ?? (neg || lookSpec(S.shot.look ?? R.E.look).type === "neg" ? "#fff" : "$ink");
        penContour(x, Gd, S, {
          dist: p.dist ?? 12,
          w: p.w ?? 4.2,
          zigs: p.zigs ?? 5,
          color: c,
          seed: S.k * 13 + (p.seed ?? 0),
        });
        if (p.echo)
          penContour(x, Gd, S, {
            dist: p.echo_dist ?? 26,
            w: 3,
            zigs: 9,
            color: c,
            seed: S.k * 13 + 5,
          });
      },
    },
    glint: {
      phase: "over",
      order: 25,
      draw(S, p, x) {
        // accent star sweeping across (Katana katana-glint)
        const d = p.d ?? 0.28,
          u = clamp((S.lt - (p.at ?? 0)) / d);
        if (S.lt < (p.at ?? 0)) return;
        const mp = (q) => (p.src ? mapM(S.M, q[0], q[1]) : [q[0] * R.W, q[1] * R.H]);
        const a = mp(p.from || [0.18, 0.4]),
          bb = mp(p.to || [0.54, 0.4]),
          X = lerp(a[0], bb[0], u),
          Y = lerp(a[1], bb[1], u),
          r = (p.r ?? 175) * (1 - 0.3 * u);
        const P = [];
        for (let i = 0; i <= 16; i++) {
          const an = (i / 16) * TAU,
            rr = i % 4 === 0 ? r : i % 2 === 0 ? r * 0.18 : r * 0.32;
          P.push([X + Math.cos(an) * rr, Y + Math.sin(an) * rr]);
        }
        x.save();
        x.fillStyle = col(p.color ?? "$accent");
        x.beginPath();
        P.forEach((q, i) => (i ? x.lineTo(q[0], q[1]) : x.moveTo(q[0], q[1])));
        x.closePath();
        x.fill();
        x.restore();
        poly(x, P, { w: 6, b: S.b, seed: 71, close: true });
        x.save();
        x.fillStyle = "#fff";
        x.beginPath();
        x.arc(X, Y, r * 0.14, 0, TAU);
        x.fill();
        x.restore();
        if (S.lt < 0.25 || Math.floor(S.lt * R.fps) % 2 === 0) rays(x, X, Y, 240, S, 72);
      },
    },
    doodles: {
      phase: "over",
      order: 30,
      async draw(S, p, x) {
        // ink doodles around the silhouette; v: density 0..3 (0,5,10,16) or n
        const lvl = p.n !== undefined ? p.n : [0, 5, 10, 16][clamp(Math.round(p.v ?? 1), 0, 3)];
        const cm = S.shot.cam || {},
          force =
            (p.scratch || 0) + (S.fx.punch || cm.punch ? (S.fx.shake || cm.shake ? 2 : 1) : 0);
        if (!lvl && !force) return;
        const avoid = [];
        if (S.fo) {
          const b = S.fo.box;
          avoid.push([b[0] - 40, b[1] - 40, b[2] + 40, b[3] + 60]);
        }
        R.texts.forEach((Tg) => {
          if (S.t >= Tg.t0 && S.t < Tg.t1 && Tg.bbox)
            avoid.push(padR(Tg.bbox, 0.35 * (Tg.capv || 200)));
        });
        await ensureOccLum(S, true);
        await inkDoodles(S, x, lvl, avoid, force, p);
      },
    },
    face_doodles: {
      phase: "over",
      order: 40,
      draw(S, p, x) {
        // kawaii stickers in eye units around the face (Yaong)
        if (!S.fo) return;
        const items = p.items || genFaceDoodles(S, p);
        items.forEach((st, i) => {
          const s = popIn(S, st.at ?? 0, 0.09);
          if (s <= 0) return;
          const wob = Math.sin((S.t + i) * 5.5) * 0.06,
            [X, Y] = fp(
              S,
              st.o[0] + Math.sin(S.t * 3 + i) * 0.05,
              st.o[1] + Math.cos(S.t * 2.6 + i) * 0.05,
            );
          kawaiiDoodle(
            x,
            st.t,
            X,
            Y,
            S.fo.D * st.s,
            S.fo.a + (st.r ?? 0) + wob,
            S.f,
            100 + i * 7 + (S.shot.seed ?? S.k * 13),
            s,
            1,
            p.colors,
          );
        });
      },
    },
    doodle: {
      phase: "over",
      order: 41,
      draw(S, p, x) {
        // one kawaii doodle at a screen position: {t, pos:[x,y], size, rot, at}
        const s = popIn(S, p.at ?? 0, 0.09);
        kawaiiDoodle(
          x,
          p.t || "heart",
          (p.pos || [0.5, 0.5])[0] * R.W,
          (p.pos || [0.5, 0.5])[1] * R.H,
          p.size ?? 80,
          p.rot ?? 0,
          S.f,
          p.seed ?? 11,
          s,
          p.alpha ?? 1,
          p.colors,
        );
      },
    },
    word: {
      phase: "over",
      order: 57,
      draw(S, p, x) {
        // word on the face (Yaong HANA/SET): size = clamp(D*k, 78, 150)
        if (S.lt < (p.at ?? 0)) return;
        const F = foOr(S),
          k = clamp((S.lt - (p.at ?? 0)) * R.fps, 0, 3),
          sc = R.W / 1440,
          size = clamp(F.D * (p.k ?? 0.8), (p.min ?? 78) * sc, (p.max ?? 150) * sc),
          [X, Y] = S.fo ? fp(S, p.dx ?? 0, p.dy ?? 1.05) : [R.W / 2, R.H * 0.6];
        outlinedText(
          x,
          String(p.text ?? p.v ?? ""),
          X,
          Y,
          fontStr(p, size, "bold"),
          p.fill ?? "$white",
          p.stroke ?? "rgba(201,139,224,0.85)",
          p.lw ?? 4,
          F.a,
          1 + 0.18 * (1 - k / 3),
          "center",
          p.shadow ?? "glow",
        );
      },
    },
    type: {
      phase: "over",
      order: 59,
      draw(S, p, x) {
        // typewriter (Yaong SARANG+HAE): parts [[text,'bold'|'thin']], dt per char
        if (S.lt < (p.at ?? 0)) return;
        const F = foOr(S),
          parts = p.parts || [[String(p.text ?? ""), "bold"]],
          nAll = parts.reduce((a, [s]) => a + s.length, 0),
          n = Math.min(nAll, Math.floor((S.lt - (p.at ?? 0)) / (p.dt ?? 0.05)) + 1 + (p.base ?? 0));
        const sc = R.W / 1440,
          [X, Y] = S.fo
            ? fp(S, p.dx ?? 0, p.dy ?? 1.15)
            : [(p.pos || [0.5, 0.7])[0] * R.W, (p.pos || [0.5, 0.7])[1] * R.H];
        typeWord(
          x,
          parts,
          X,
          Y,
          Math.round(clamp(F.D * (p.k ?? 0.86), (p.min ?? 80) * sc, (p.max ?? 140) * sc)),
          n,
          F.a,
          p,
        );
      },
    },
    text: {
      phase: "over",
      order: 58,
      draw(S, p, x) {
        // generic font text inside a shot: one item or {items:[...]}; timing at/d relative to the shot
        (p.items || [p]).forEach((T) => {
          const age = S.lt - (T.at ?? 0),
            d = T.d ?? S.dur;
          if (age < 0 || age >= d) return;
          drawFontText(S, T, x, age, d);
        });
      },
    },
    graffiti: {
      phase: "over",
      order: 61,
      draw(S, p, x) {
        // graffiti tag inside one shot (timing relative to the shot)
        if (!p._T) {
          p._T = {
            ...p,
            mode: p.mode || "write",
            t0: S.shot.t0 + (p.at ?? 0),
            t1: S.shot.t0 + (p.at ?? 0) + (p.d ?? S.dur),
          };
          TEXT.graffiti.init(p._T, 99 + S.k);
        }
        if (S.t >= p._T.t0 && S.t < p._T.t1) TEXT.graffiti.draw(S, p._T, x, 99 + S.k);
      },
    },
    slash: {
      phase: "over",
      order: 58,
      draw(S, p, x) {
        if (S.lt < (p.at ?? 0)) return;
        const F = foOr(S),
          [X, Y] = S.fo ? fp(S, p.dx ?? 0, p.dy ?? 0.75) : [R.W / 2, R.H / 2];
        slashes(x, X, Y, F.w, F.a, S.lt - (p.at ?? 0), S.f, p.seed ?? 4, p);
      },
    },
    sparkle: {
      phase: "over",
      order: 45,
      draw(S, p, x) {
        sparkle(
          x,
          (p.pos || [0.62, 0.4])[0] * R.W,
          (p.pos || [0.62, 0.4])[1] * R.H,
          p.r ?? 60,
          S,
          p.seed ?? 9,
          p.color ?? "$ink",
        );
      },
    },
    splat: {
      phase: "over",
      order: 45,
      draw(S, p, x) {
        (p.items || [p]).forEach((q, i) =>
          splatField(
            x,
            (q.pos || [0.7, 0.35])[0] * R.W,
            (q.pos || [0.7, 0.35])[1] * R.H,
            q.r ?? 160,
            S,
            q.seed ?? 7 + i,
            q.n ?? 16,
            q.color ?? "$accent2",
            q.color2 ?? "$ink",
          ),
        );
      },
    },
    // ---- post: full-frame treatments
    bw: {
      phase: "post",
      order: 20,
      draw(S, p, x) {
        copyFull(R.L.tmp.x, R.canvas, "copy");
        x.save();
        x.setTransform(1, 0, 0, 1, 0, 0);
        x.filter = p.filter || "grayscale(1) contrast(1.22) brightness(1.04)";
        x.drawImage(R.L.tmp, 0, 0);
        x.restore();
        if (p.bars) {
          x.fillStyle = col(p.color ?? "#000");
          x.fillRect(0, 0, R.W, p.bars[0]);
          x.fillRect(0, R.H - p.bars[1], R.W, p.bars[1]);
        }
      },
    },
    letterbox: {
      phase: "post",
      order: 70,
      draw(S, p, x) {
        const t = (p.top ?? p.v ?? 0.1) * R.H,
          b = (p.bottom ?? p.v ?? 0.1) * R.H;
        x.fillStyle = col(p.color ?? "#000");
        x.fillRect(0, 0, R.W, t);
        x.fillRect(0, R.H - b, R.W, b);
      },
    },
    tint: {
      phase: "post",
      order: 51,
      draw(S, p, x) {
        x.save();
        x.globalCompositeOperation = p.op || "screen";
        x.fillStyle = withAlpha(
          p.color ?? "rgb(255,120,220)",
          (p.v ?? p.amt ?? 0.3) * (p.d ? 1 - clamp(S.lt / p.d) : 1),
        );
        x.fillRect(0, 0, R.W, R.H);
        x.restore();
      },
    },
    tag: {
      phase: "post",
      order: 40,
      draw(S, p, x) {
        // small watermark-like handle (Yaong nabi.cam*)
        let X, Y;
        if (p.pos === "bottom" || !S.fo) {
          Y = R.H * (p.by ?? 0.9) - (S.fx.bw ? 20 : 0);
          X = R.W * (p.bx ?? 0.5);
        } else {
          const F = S.fo;
          Y = F.y + F.w * 0.05;
          X = F.x + (p.dx ?? -0.45) * F.w;
        }
        outlinedText(
          x,
          p.text ?? p.v ?? "",
          X,
          Y,
          fontStr({ style: "", weight: 500, ...p }, p.size ?? 34, "regular"),
          p.fill ?? "rgba(255,255,255,0.92)",
          null,
          0,
          0,
          1,
          "center",
          "dark",
        );
      },
    },
    invert: {
      phase: "post",
      order: 16,
      draw(S, p, x) {
        if (win(S, p) < 0) return;
        copyFull(R.L.tmp.x, R.canvas, "copy");
        x.save();
        x.setTransform(1, 0, 0, 1, 0, 0);
        x.filter = "invert(1)";
        x.globalAlpha = p.amt ?? 1;
        x.drawImage(R.L.tmp, 0, 0);
        x.restore();
      },
    },
    rgbsplit: {
      phase: "post",
      order: 15,
      draw(S, p, x) {
        // channel offset: red one way, green+blue the other (additive recombine)
        if (win(S, p) < 0) return;
        const v = (p.v ?? 6) * R.rs * (p.decay ? 1 - clamp(S.lt / p.decay) : 1),
          a = R.L.tmp,
          b = R.L.cut;
        for (const [c, tint] of [
          [a, "#ff0000"],
          [b, "#00ffff"],
        ]) {
          const cx = c.x;
          cx.setTransform(1, 0, 0, 1, 0, 0);
          cx.globalCompositeOperation = "copy";
          cx.drawImage(R.canvas, 0, 0);
          cx.globalCompositeOperation = "multiply";
          cx.fillStyle = tint;
          cx.fillRect(0, 0, R.PW, R.PH);
          cx.globalCompositeOperation = "source-over";
        }
        x.save();
        x.setTransform(1, 0, 0, 1, 0, 0);
        x.globalCompositeOperation = "copy";
        x.drawImage(b, -v, 0, R.PW + 2 * v, R.PH);
        x.globalCompositeOperation = "lighter";
        x.drawImage(a, 0, 0, R.PW + 2 * v, R.PH);
        x.restore();
      },
    },
    strobe: {
      phase: "post",
      order: 63,
      draw(S, p, x) {
        if (win(S, p) < 0) return;
        const k = Math.floor((S.f - (S.shot ? S.shot.f0 : 0)) / (p.every ?? 2));
        if (k % 2) return;
        x.fillStyle = withAlpha(p.color ?? "#fff", p.amt ?? 1);
        x.fillRect(0, 0, R.W, R.H);
      },
    },
    leak: {
      phase: "post",
      order: 52,
      draw(S, p, x) {
        // light leak: drifting warm radial wash
        if (win(S, p) < 0) return;
        const dr = p.drift ?? 0.1,
          X = R.W * ((p.x ?? 0.85) + Math.sin(S.t * 1.3 + (p.seed ?? 0)) * dr),
          Y = R.H * ((p.y ?? 0.2) + Math.cos(S.t * 0.9 + (p.seed ?? 0)) * dr),
          r = R.W * (p.r ?? 0.6);
        const g = x.createRadialGradient(X, Y, 0, X, Y, r);
        g.addColorStop(0, withAlpha(p.color ?? "rgb(255,140,40)", p.amt ?? 0.55));
        g.addColorStop(0.5, withAlpha(p.color2 ?? "rgb(255,60,30)", (p.amt ?? 0.55) * 0.35));
        g.addColorStop(1, "rgba(0,0,0,0)");
        x.save();
        x.globalCompositeOperation = p.op || "screen";
        x.fillStyle = g;
        x.fillRect(0, 0, R.W, R.H);
        x.restore();
      },
    },
    // ---- final: texture on top of everything
    vignette: {
      phase: "final",
      order: 5,
      draw(S, p, x) {
        const g = x.createRadialGradient(
          R.W / 2,
          R.H / 2,
          R.H * (p.r0 ?? 0.45),
          R.W / 2,
          R.H / 2,
          R.H * (p.r1 ?? 0.95),
        );
        g.addColorStop(0, "rgba(0,0,0,0)");
        g.addColorStop(1, withAlpha(p.color ?? "#000", p.v ?? p.amt ?? 0.35));
        x.fillStyle = g;
        x.fillRect(0, 0, R.W, R.H);
      },
    },
    grain: {
      phase: "final",
      order: 10,
      draw(S, p, x) {
        // 4 pre-baked noise tiles, soft-light, offset per frame (Yaong 0.32)
        const tl = grainTiles(p),
          g = tl[S.f % tl.length],
          gx = (S.f * 37) % 50,
          gy = (S.f * 53) % 40;
        x.save();
        x.globalCompositeOperation = p.op || "soft-light";
        x.globalAlpha = p.v ?? p.amt ?? 0.32;
        x.drawImage(g, -gx, -gy, R.W + 50, R.H + 40);
        x.restore();
      },
    },
    dust: {
      phase: "final",
      order: 20,
      draw(S, p, x) {
        const f = S.f;
        x.save();
        for (let i = 0; i < (p.n ?? 14); i++) {
          const X = hash(f, i, 1) * R.W,
            Y = hash(f, i, 2) * R.H;
          x.fillStyle = hash(f, i, 4) < 0.75 ? "rgba(10,10,10,.75)" : "rgba(255,255,255,.9)";
          x.beginPath();
          x.arc(X, Y, 0.8 + hash(f, i, 6) * 2, 0, TAU);
          x.fill();
        }
        x.restore();
      },
    },
    border: {
      phase: "final",
      order: 30,
      draw(S, p, x) {
        // hand-inked frame edge (Katana): ragged top/bottom bands + side strokes
        const b = S.b;
        x.save();
        x.fillStyle = col(p.color ?? "$ink");
        const band = (y0, dir, seed) => {
          x.beginPath();
          x.moveTo(-10, y0 - dir * 40);
          for (let X = -10; X <= R.W + 10; X += 24) {
            const th =
              7 + 8 * Math.max(0, Math.sin(X * 0.004 + seed)) + hash(seed, b * 97 + X, 1) * 4;
            x.lineTo(X, y0 + dir * th);
          }
          x.lineTo(R.W + 10, y0 - dir * 40);
          x.closePath();
          x.fill();
        };
        band(0, 1, 1);
        band(R.H, -1, 3);
        x.lineCap = "round";
        [
          [0, 1],
          [R.W, -1],
        ].forEach(([X0, d], k) => {
          for (let s = 0; s < 5; s++) {
            const y0 = hash(9 + k, b * 11 + s, 1) * R.H,
              len = 60 + hash(9 + k, b * 11 + s, 2) * 200;
            x.lineWidth = 3 + hash(9 + k, b * 11 + s, 3) * 3;
            x.strokeStyle = col(p.color ?? "$ink");
            x.beginPath();
            x.moveTo(X0 + d * (2 + hash(k, s, b) * 4), y0);
            x.lineTo(X0 + d * (3 + hash(k, s, b + 1) * 5), y0 + len);
            x.stroke();
          }
        });
        x.restore();
      },
    },
  };

  // FACE: graphics locked to the tracked face (need a faces file on the clip or shot.face.box)
  const FACE = {
    cheeks: {
      phase: "over",
      order: 20,
      draw(S, p, x) {
        // Katana zigzag cheek marks
        if (!S.fo || (!S.fo.ok && !p.force)) return;
        const F = S.fo,
          ed = F.D;
        if (ed < 30) return;
        const ang = F.a,
          dn = [-Math.sin(ang), Math.cos(ang)],
          ax = [Math.cos(ang), Math.sin(ang)];
        [F.e0, F.e1].forEach((e, k) => {
          const out = k ? 1 : -1,
            c = [
              e[0] + dn[0] * ed * 0.6 + ax[0] * out * ed * 0.08,
              e[1] + dn[1] * ed * 0.6 + ax[1] * out * ed * 0.08,
            ];
          const Z = zigzag(c[0], c[1], ed * 0.36, ed * 0.055, ang, 5);
          poly(
            x,
            Z.map((q) => [q[0] + 3, q[1] + 4]),
            { w: Math.max(1.6, ed * 0.012), color: "$ink", b: S.b, seed: 44 + k, jit: ed * 0.006 },
          );
          poly(x, Z, {
            w: Math.max(3, ed * 0.032),
            color: p.color ?? "$accent2",
            b: S.b,
            seed: 40 + k,
            jit: ed * 0.006,
          });
        });
      },
    },
    fangs: {
      phase: "over",
      order: 21,
      draw(S, p, x) {
        // two accent fangs under the upper lip
        if (!S.fo || (!S.fo.ok && !p.force)) return;
        const F = S.fo,
          mw = F.mw;
        x.save();
        x.translate(F.mx, F.my);
        x.rotate(F.a);
        [0.3, 0.7].forEach((u, k) => {
          const rx = lerp(-mw / 2, mw / 2, u),
            ry = -mw * 0.06 + (p.dy ?? 0) * mw,
            L = mw * (p.len ?? 0.3),
            hw = mw * 0.07,
            P = [
              [rx - hw, ry],
              [rx + hw * 0.15, ry + L],
              [rx + hw, ry],
            ];
          x.fillStyle = col(p.color ?? "$accent");
          x.beginPath();
          P.forEach((q, i) => (i ? x.lineTo(q[0], q[1]) : x.moveTo(q[0], q[1])));
          x.closePath();
          x.fill();
          poly(x, P, { w: Math.max(2.5, mw * 0.02), b: S.b, seed: 60 + k, jit: 1.2 });
        });
        x.restore();
      },
    },
    ears: {
      phase: "over",
      order: 32,
      draw(S, p, x) {
        // kawaii cat ears, clamped inside the frame
        if (!S.fo) return;
        const s = popIn(S, p.at ?? 0);
        for (const sx of [-1, 1]) {
          const es = S.fo.D * (p.size ?? 0.9),
            [X, y0] = fp(S, sx * (p.dx ?? 1.25), p.dy ?? -1.72),
            Y = Math.max(y0, es * 0.8);
          kawaiiDoodle(x, "ear", X, Y, es, S.fo.a + sx * 0.33, S.f, 40 + sx, s, 1, p.colors);
        }
      },
    },
    whisk: {
      phase: "over",
      order: 33,
      draw(S, p, x) {
        // whiskers
        if (!S.fo) return;
        const s = popIn(S, p.at ?? 0.03);
        for (const sx of [-1, 1]) {
          const [X, Y] = fp(S, sx * (p.dx ?? 1.05), p.dy ?? 1.05);
          x.save();
          x.translate(X, Y);
          x.scale(sx, 1);
          kawaiiDoodle(x, "whisk", 0, 0, S.fo.D * 0.95, sx * S.fo.a, S.f, 50 + sx, s, 1, p.colors);
          x.restore();
        }
      },
    },
    blush: {
      phase: "over",
      order: 34,
      draw(S, p, x) {
        // blush hearts on the cheeks
        if (!S.fo) return;
        const s = popIn(S, p.at ?? 0.05);
        for (const sx of [-1, 1]) {
          const [X, Y] = fp(S, sx * (p.dx ?? 0.78), p.dy ?? 0.72);
          kawaiiDoodle(
            x,
            "blush",
            X,
            Y,
            S.fo.D * (p.size ?? 0.36),
            S.fo.a + sx * 0.18,
            S.f,
            60 + sx,
            s,
            1,
            p.colors,
          );
        }
      },
    },
    ast: {
      phase: "over",
      order: 56,
      draw(S, p, x) {
        if (!S.fo) return;
        const [X, Y] = fp(S, p.dx ?? 0.02, p.dy ?? 0.72);
        asterisk(
          x,
          X,
          Y,
          S.fo.D * (p.size ?? 0.38) * (0.7 + 0.3 * easeOut(clamp(S.lt / 0.06))),
          S.lt * 1.5 + S.fo.a,
          p.colors,
        );
      },
    },
    burst: {
      phases: {
        // starburst behind the subject + arc letters in front (Yaong YAONG)
        back: {
          order: 10,
          cut: true,
          draw(S, p, x) {
            const F = foOr(S),
              [cx, cy] = S.fo ? fp(S, p.dx ?? 0, p.dy ?? 0.4) : [R.W / 2, R.H / 2],
              Rr = (p.r ?? 3.5) * F.D,
              k = easeOut(clamp(S.lt / 0.08));
            starburst(
              x,
              cx,
              cy,
              Rr * (0.6 + 0.4 * k) * (1 + 0.04 * S.lt),
              p.seed ?? 1,
              S.f,
              (p.rot ?? 0) + S.lt * 0.25 + F.a,
              p,
            );
          },
        },
        over: {
          order: 55,
          draw(S, p, x) {
            const F = foOr(S),
              [cx, cy] = S.fo ? fp(S, p.dx ?? 0, p.dy ?? 0.4) : [R.W / 2, R.H / 2],
              letters = String(p.letters ?? "").split(""),
              n = letters.length,
              lsz = Math.round(F.D * (p.ls ?? 0.88));
            letters.forEach((ch, i) => {
              const a = lerp(p.a0 ?? -2.85, p.a1 ?? -0.05, n > 1 ? i / (n - 1) : 0.5) + F.a,
                rr = (p.lr ?? 2.95) * F.D;
              const kk = easeOut(clamp((S.lt - 0.02 * i) / 0.07)),
                pp = kk < 1 ? kk * 1.12 : 1,
                jr = rng(i * 7 + Math.floor(S.f / 3) + (p.seed ?? 1) * 3);
              const lx = clamp(cx + Math.cos(a) * rr, lsz * 0.55, R.W - lsz * 0.55),
                ly = clamp(cy + Math.sin(a) * rr * (p.ry ?? 0.66), lsz * 0.62, R.H - lsz * 0.6);
              outlinedText(
                x,
                ch,
                lx,
                ly,
                fontStr(p, lsz, "heavy"),
                p.fill ?? "$white",
                p.stroke ?? "$lav",
                5,
                a + Math.PI / 2 + (jr() - 0.5) * 0.25 - (a > -Math.PI / 2 ? 0.2 : -0.2),
                pp,
              );
            });
          },
        },
      },
    },
  };

  // TRANSITIONS: time-windowed treatments at a shot's head/tail (shot.in / shot.out sugar or fx names)
  const TRANSITIONS = {
    fin: {
      phase: "post",
      order: 30,
      draw(S, p, x) {
        const q = clamp(S.lt / (p.d ?? 0.14));
        if (q < 1)
          flashlight(S, x, Math.pow(1 - q, 1.4) * (p.k ?? 1), 17 + S.f, p.blocks !== false);
      },
    },
    fout: {
      phase: "post",
      order: 31,
      draw(S, p, x) {
        const d = p.d ?? 0.07,
          q = clamp((S.lt - (S.dur - d)) / d);
        if (q > 0) flashlight(S, x, q * (p.k ?? 0.8), 29 + S.f, !!p.blocks);
      },
    },
    glitch: {
      phase: "post",
      order: 10,
      draw(S, p, x) {
        if (win(S, p, 0.1) >= 0) glitchBlocks(S, x, p.seed ?? 9, p.amt ?? 0.55);
      },
    },
    mosaic: {
      phase: "post",
      order: 11,
      draw(S, p, x) {
        const q = win(S, p, 0.08);
        if (q >= 0)
          mosaic(
            S,
            x,
            Math.max(
              2,
              Math.round(lerp(p.from ?? 56, p.to ?? 4, easeOut(p.side === "out" ? 1 - q : q))),
            ),
          );
      },
    },
    blur: {
      phase: "post",
      order: 12,
      draw(S, p, x) {
        const q = win(S, p, 0.12);
        if (q >= 0) blurFrame(S, x, (p.max ?? 16) * Math.sin(Math.PI * q), p.frame !== false);
      },
    },
    blurIn: {
      phase: "post",
      order: 13,
      draw(S, p, x) {
        const q = clamp(S.lt / (p.d ?? 0.12));
        if (q < 1) blurFrame(S, x, (p.max ?? 14) * (1 - easeOut(q)), q < 0.6 && p.frame !== false);
      },
    },
    blurOut: {
      phase: "post",
      order: 14,
      draw(S, p, x) {
        const at = p.at ?? (p.side === "out" ? S.dur - (p.d ?? 0.5) : 0.05);
        if (S.lt < at) return;
        const q = clamp((S.lt - at) / (p.d ?? 0.5));
        blurFrame(S, x, 2 + (p.max ?? 22) * easeOut(q), q > 0.3);
        x.fillStyle = withAlpha(p.color ?? "rgb(255,248,252)", 0.25 * q);
        x.fillRect(0, 0, R.W, R.H);
      },
    },
    magenta: {
      phase: "post",
      order: 50,
      draw(S, p, x) {
        // colour-washed mosaic entry (Yaong): mosaic 40->4 under multiply+screen washes
        const q = win(S, p, 0.2);
        if (q < 0) return;
        const a = 1 - q;
        mosaic(S, x, Math.round(lerp(4, p.from ?? 40, a)));
        x.save();
        x.globalCompositeOperation = "multiply";
        x.fillStyle = withAlpha(p.color ?? "$magenta", 0.75 * a);
        x.fillRect(0, 0, R.W, R.H);
        x.globalCompositeOperation = "screen";
        x.fillStyle = withAlpha(p.color2 ?? "$magenta2", 0.55 * a);
        x.fillRect(0, 0, R.W, R.H);
        x.restore();
      },
    },
    white: {
      phase: "post",
      order: 60,
      draw(S, p, x) {
        if (win(S, p, 0.067) >= 0) {
          x.fillStyle = col(p.color ?? "#fff");
          x.fillRect(0, 0, R.W, R.H);
        }
      },
    },
    flash: {
      phase: "post",
      order: 61,
      draw(S, p, x) {
        const at = p.side === "out" ? S.dur - (p.d ?? 0.1) : (p.at ?? 0);
        if (S.lt < at) return;
        let a = 1 - clamp((S.lt - at) / (p.d ?? 0.1));
        if (p.side === "out") a = 1 - a;
        if (a > 0) {
          x.fillStyle = withAlpha(p.color ?? "#fff", a * (p.amt ?? 1));
          x.fillRect(0, 0, R.W, R.H);
        }
      },
    },
    dip: {
      phase: "post",
      order: 62,
      draw(S, p, x) {
        const d = p.d ?? 0.15;
        let a = p.side === "out" ? clamp((S.lt - (S.dur - d)) / d) : 1 - clamp(S.lt / d);
        if (a > 0) {
          x.fillStyle = withAlpha(p.color ?? "#000", a);
          x.fillRect(0, 0, R.W, R.H);
        }
      },
    },
  };
  // shot.in / shot.out {type} -> fx name
  const TR_SUGAR = {
    flashlight: { in: "fin", out: "fout" },
    mosaic: { in: "mosaic", out: "mosaic" },
    magenta: { in: "magenta" },
    blur: { in: "blurIn", out: "blurOut" },
    white: { in: "white", out: "white" },
    flash: { in: "flash", out: "flash" },
    dip: { in: "dip", out: "dip" },
    glitch: { in: "glitch", out: "glitch" },
  };

  // ============================================================ STICKERS: graphic stickers + die-cut cutouts, planner, draw
  async function loadStickers() {
    const A = R.E.assets || {};
    let list = A.stickers || [];
    if (list && !Array.isArray(list)) {
      const d = list;
      list = [];
      for (let i = d.start ?? 1; i < (d.start ?? 1) + (d.n || 0); i++)
        list.push(`${d.dir}/${fmtPat(d.pattern || "s%02d.png", i)}`);
    }
    for (let i = 0; i < list.length; i++) {
      const im = await img(list[i], true);
      if (!im) {
        warn("sticker missing: " + list[i]);
        continue;
      }
      const c = mk(im.width, im.height, true);
      c.x.drawImage(im, 0, 0);
      const d = c.x.getImageData(0, 0, c.width, c.height).data;
      let x0 = c.width,
        y0 = c.height,
        x1 = 0,
        y1 = 0;
      for (let y = 0; y < c.height; y += 2)
        for (let X = 0; X < c.width; X += 2)
          if (d[(y * c.width + X) * 4 + 3] > 40) {
            if (X < x0) x0 = X;
            if (X > x1) x1 = X;
            if (y < y0) y0 = y;
            if (y > y1) y1 = y;
          }
      if (x1 <= x0) continue;
      x0 = Math.max(0, x0 - 6);
      y0 = Math.max(0, y0 - 6);
      x1 = Math.min(c.width, x1 + 6);
      y1 = Math.min(c.height, y1 + 6);
      const o = mk(x1 - x0, y1 - y0);
      o.x.drawImage(c, x0, y0, o.width, o.height, 0, 0, o.width, o.height);
      if (A.sticker_look) {
        // run the sticker through a plate look (e.g. xerox) on white, keep its own alpha
        const P = R.L.plate,
          px_ = P.x;
        px_.setTransform(1, 0, 0, 1, 0, 0);
        px_.fillStyle = "#fff";
        px_.fillRect(0, 0, R.PW, R.PH);
        const k = Math.min(1, R.PW / o.width, R.PH / o.height);
        px_.drawImage(o, 0, 0, o.width * k, o.height * k);
        const L = await applyLook({ f: i, b: 0, lt: 0, dur: 1, k: -1 }, P, A.sticker_look);
        const g = mk(o.width, o.height);
        g.x.drawImage(L.canvas || L, 0, 0, o.width * k, o.height * k, 0, 0, o.width, o.height);
        g.x.globalCompositeOperation = "destination-in";
        g.x.drawImage(o, 0, 0);
        R.stickers.push(g);
      } else R.stickers.push(o);
    }
  }
  async function buildCutouts() {
    // die-cut stickers of the subject: frame + mask -> look -> white border ring -> trimmed canvas
    const A = R.E.assets || {},
      list = A.cutouts || [];
    if (!list.length) return;
    const P0 = Math.round(32 * R.rs),
      PW = R.PW + 2 * P0,
      PH = R.PH + 2 * P0,
      bw = (A.cutout_border ?? 16) * R.rs;
    for (const cdef of list) {
      const C = R.clips[cdef.clip];
      if (!C || !C.mask_dir) {
        warn("cutout needs a clip with mask_dir: " + cdef.clip);
        continue;
      }
      const i = cdef.f !== undefined ? cdef.f : Math.round(T(cdef.t ?? cdef.src ?? 0) * C.fps);
      const [fim, mim] = await Promise.all([img(framePath(C, i)), img(maskPath(C, i))]);
      if (!fim || !mim) continue;
      const S = {
        f: i,
        b: 0,
        lt: 0,
        dur: 1,
        k: -1,
        shot: { cam: cdef.cam || {}, fx: {}, i: -1 },
        clip: C,
        si: i,
      };
      camera(S, cdef.cam || {});
      const pl = R.L.plate.x;
      pl.setTransform(1, 0, 0, 1, 0, 0);
      pl.fillStyle = "#fff";
      pl.fillRect(0, 0, R.PW, R.PH);
      setM(pl, S.M);
      pl.drawImage(fim, 0, 0, C.w, C.h);
      const L = await applyLook(S, R.L.plate, cdef.look ?? A.cutout_look ?? A.sticker_look ?? null);
      const Pc = mk(PW, PH);
      Pc.x.drawImage(L.canvas || L, P0, P0);
      Pc.x.globalCompositeOperation = "destination-in";
      Pc.x.setTransform(
        S.M[0] * R.rs,
        S.M[1] * R.rs,
        S.M[2] * R.rs,
        S.M[3] * R.rs,
        S.M[4] * R.rs + P0,
        S.M[5] * R.rs + P0,
      );
      Pc.x.drawImage(mim, 0, 0, C.w, C.h);
      const Mk = mk(PW, PH, true);
      for (let k = 0; k < 24; k++) {
        const a = (k / 24) * TAU;
        Mk.x.setTransform(
          S.M[0] * R.rs,
          S.M[1] * R.rs,
          S.M[2] * R.rs,
          S.M[3] * R.rs,
          S.M[4] * R.rs + P0 + Math.cos(a) * bw,
          S.M[5] * R.rs + P0 + Math.sin(a) * bw,
        );
        Mk.x.drawImage(mim, 0, 0, C.w, C.h);
      }
      Mk.x.setTransform(1, 0, 0, 1, 0, 0);
      Mk.x.globalCompositeOperation = "source-in";
      Mk.x.fillStyle = col(A.cutout_border_color ?? "#fffdf8");
      Mk.x.fillRect(0, 0, PW, PH);
      Mk.x.globalCompositeOperation = "source-over";
      Mk.x.drawImage(Pc, 0, 0);
      const d = Mk.x.getImageData(0, 0, PW, PH).data;
      let x0 = PW,
        y0 = PH,
        x1 = 0,
        y1 = 0;
      for (let y = 0; y < PH; y += 4)
        for (let X = 0; X < PW; X += 4)
          if (d[(y * PW + X) * 4 + 3] > 40) {
            if (X < x0) x0 = X;
            if (X > x1) x1 = X;
            if (y < y0) y0 = y;
            if (y > y1) y1 = y;
          }
      if (x1 <= x0) continue;
      const Cc = mk(x1 - x0 + 8, y1 - y0 + 8);
      Cc.x.drawImage(Mk, x0 - 4, y0 - 4, Cc.width, Cc.height, 0, 0, Cc.width, Cc.height);
      Cc.lw = Cc.width / R.rs;
      Cc.lh = Cc.height / R.rs;
      R.cutouts.push(Cc);
    }
  }
  const imW = (im) => im.lw || im.width,
    imH = (im) => im.lh || im.height;
  const frameAtT = (t) => clamp(firstFrame(t), 0, R.nf - 1);
  async function planStickers() {
    const evs = (R.E.stickers || [])
      .map((e, i) => ({ ...e, i, t0: T(e.t0), t1: T(e.t1) }))
      .sort((a, b) => a.t0 - b.t0);
    R.sevt = [];
    R.stickerLog = [];
    let gi = 0,
      cb = 0;
    const sc = R.W / 1440;
    const SL = [
      [0.12, 0.15],
      [0.88, 0.15],
      [0.1, 0.85],
      [0.9, 0.85],
      [0.07, 0.5],
      [0.93, 0.5],
      [0.5, 0.09],
      [0.5, 0.92],
    ];
    const faceR = (f) => {
      const S = stateAt(f);
      if (S.kind !== "plate" || !S.fo) return null;
      const b = S.fo.box;
      return padR(b, 0.15 * (b[2] - b[0]));
    };
    for (let ei = 0; ei < evs.length; ei++) {
      const e = evs[ei],
        n = Math.max(1, Math.round(e.n || 1)),
        cbase = cb;
      if (e.kind === "cutout") cb += n;
      let placed = 0;
      for (let i = 0; i < n; i++) {
        const tIn = e.mode === "hold" ? e.t0 : e.t0 + i * (e.step ?? R.beat.dur / 4);
        if (tIn >= e.t1 - 1e-3) continue;
        const kind = e.kind === "cutout" && R.cutouts.length ? "cutout" : "graphic";
        let im;
        if (kind === "cutout") im = R.cutouts[(cbase + i) % R.cutouts.length];
        else {
          if (!R.stickers.length) continue;
          const ns = R.stickers.length;
          im = e.ids
            ? R.stickers[(((e.ids[i % e.ids.length] - 1) % ns) + ns) % ns]
            : R.stickers[(gi * 7 + ei * 3) % ns];
        }
        let size;
        if (e.size) size = lerp(e.size[0], e.size[1], hash(ei, i, 5));
        else if (kind === "cutout") size = (340 + hash(ei, i, 5) * 120) * sc;
        else size = ((i === 0 ? 340 : 210) + hash(ei, i, 5) * 80) * sc;
        if (i === 0 && e.hero && !e.size && kind === "graphic") size = Math.max(size, 380 * sc);
        const avoid = (e.avoid || []).map((r) => [r[0] * R.W, r[1] * R.H, r[2] * R.W, r[3] * R.H]);
        R.texts.forEach((Tg) => {
          if (Tg.t0 < e.t1 && Tg.t1 > tIn && Tg.bbox) avoid.push(padR(Tg.bbox, Tg.pad ?? 30));
        });
        const fIn = frameAtT(tIn);
        [fIn, Math.min(R.nf - 1, fIn + Math.round(0.15 * R.fps))].forEach((f) => {
          const r = faceR(f);
          if (r) avoid.push(r);
        });
        let S0 = stateAt(fIn);
        if (S0.kind !== "plate") {
          const sh = R.shots[S0.k + 1];
          if (sh) S0 = stateAt(Math.min(R.nf - 1, sh.f0));
        }
        const occ = S0.kind === "plate" ? await occAt(S0) : null;
        const live = R.sevt.filter((s) => s.tIn < e.t1 && s.tOut > tIn),
          area = live.reduce((a, s) => a + s.w * s.h, 0);
        const slots = e.slots || SL;
        const tryAt = (scl) => {
          const kk = (size * scl) / Math.max(imW(im), imH(im)),
            w = imW(im) * kk,
            h = imH(im) * kk,
            cand = [];
          for (let q = 0; q < slots.length; q++) {
            const sl =
              slots[e.slots ? (i + q) % slots.length : (ei * 3 + (i + q) * 3) % slots.length];
            let cx = (sl[0] + (e.slots ? 0 : hs(ei, i, 7) * 0.035)) * R.W,
              cy = (sl[1] + (e.slots ? 0 : hs(ei, i, 8) * 0.035)) * R.H;
            cx = clamp(cx, 0.03 * R.W + w / 2, 0.97 * R.W - w / 2);
            cy = clamp(cy, 0.03 * R.H + h / 2, 0.97 * R.H - h / 2);
            const Rr = [cx - w * 0.475, cy - h * 0.475, cx + w * 0.475, cy + h * 0.475];
            let bad =
              avoid.reduce(
                (a, r) =>
                  a +
                  (hit(Rr, r)
                    ? ((Math.min(Rr[2], r[2]) - Math.max(Rr[0], r[0])) *
                        (Math.min(Rr[3], r[3]) - Math.max(Rr[1], r[1]))) /
                      (w * h)
                    : 0),
                0,
              ) + Math.max(0, occFrac(occ, Rr) - (e.occ_ok ?? 0.25));
            if (
              live
                .concat(R.sevt.filter((s) => s.ei === ei))
                .some(
                  (s) =>
                    Math.hypot(s.cx - cx, s.cy - cy) <
                    (0.8 * (Math.max(s.w, s.h) + Math.max(w, h))) / 2,
                )
            )
              bad += 1;
            cand.push({ cx, cy, w, h, R: Rr, bad });
          }
          return cand;
        };
        let cands = tryAt(1),
          best = cands.find((c) => c.bad === 0);
        if (!best) {
          cands = tryAt(0.75).sort((a, b) => a.bad - b.bad);
          if (cands[0] && cands[0].bad < 0.35) best = cands[0];
        }
        if (!best || area + best.w * best.h > (e.max_area ?? 0.25) * R.W * R.H) continue;
        let tOut = e.t1;
        for (let k = S0.k + 1; k < R.shots.length && R.shots[k].t0 < tOut; k++) {
          const sh = R.shots[k];
          if (sh.t0 <= tIn) continue;
          const r = faceR(Math.min(R.nf - 1, sh.f0));
          if (r && hit(best.R, padR(r, 40))) {
            tOut = sh.t0;
            break;
          }
        }
        if (tOut - tIn < 0.08) continue;
        if (kind === "graphic") gi++;
        placed++;
        R.sevt.push({
          im,
          kind,
          cx: best.cx,
          cy: best.cy,
          w: best.w,
          h: best.h,
          rot: hs(ei, i, 6) * (e.rot ?? 0.3),
          tIn,
          tOut,
          seed: ei * 31 + i,
          ei,
          shadow: e.shadow,
        });
      }
      R.stickerLog.push(`stickers t=${e.t0.toFixed(3)} placed ${placed}/${n}`);
    }
  }
  function drawStickers(S, x) {
    const keep = [];
    if (S.fo) keep.push(padR(S.fo.box, 40));
    R.texts.forEach((Tg) => {
      if (S.t >= Tg.t0 && S.t < Tg.t1 && Tg.bbox) keep.push(Tg.bbox);
    });
    R.sevt.forEach((s) => {
      if (S.t < s.tIn - 1e-6 || S.t >= s.tOut - 1e-6) return;
      const age = Math.floor((S.t - s.tIn) * R.fps + 1e-6),
        sc = [1.4, 0.9, 1.05, 1][Math.min(age, 3)];
      let cx = s.cx + hs(S.k, s.seed, 1) * 10 + hs(S.b, s.seed, 2) * 1.5,
        cy = s.cy + hs(S.k, s.seed, 3) * 10 + hs(S.b, s.seed, 4) * 1.5;
      const r = s.rot + hs(S.k, s.seed, 5) * 0.05;
      const hw = (Math.abs(s.w * Math.cos(r)) + Math.abs(s.h * Math.sin(r))) / 2,
        hh = (Math.abs(s.w * Math.sin(r)) + Math.abs(s.h * Math.cos(r))) / 2;
      let ok = true;
      for (let step = 0; step <= 12; step++) {
        const Rr = [cx - hw, cy - hh, cx + hw, cy + hh],
          b = keep.find((kb) => hit(Rr, kb));
        if (!b) {
          ok = true;
          break;
        }
        ok = false;
        if (step === 12) break;
        let vx = cx - (b[0] + b[2]) / 2,
          vy = cy - (b[1] + b[3]) / 2,
          L = Math.hypot(vx, vy);
        if (L < 1) {
          vx = Math.sign(s.cx / R.W - 0.5) || 1;
          vy = 0;
          L = 1;
        }
        cx += (vx / L) * 24;
        cy += (vy / L) * 24;
        cx = clamp(cx, 0.04 * R.W + hw, 0.96 * R.W - hw);
        cy = clamp(cy, 0.04 * R.H + hh, 0.96 * R.H - hh);
      }
      if (!ok) return;
      x.save();
      x.translate(cx, cy);
      x.rotate(r);
      x.scale(sc, sc);
      if (s.shadow !== false) {
        x.shadowColor = "rgba(0,0,0,.85)";
        x.shadowBlur = 0;
        x.shadowOffsetX = px(5);
        x.shadowOffsetY = px(7);
      }
      x.drawImage(s.im, -s.w / 2, -s.h / 2, s.w, s.h);
      x.restore();
    });
  }
  const STICKERS = {
    load: loadStickers,
    cutouts: buildCutouts,
    plan: planStickers,
    draw: drawStickers,
  };

  // ============================================================ SPECIALS: whole-frame inserts (shots with special/clip FLASH|WHITE|BLACK|COLLAGE, or edl.specials[])
  // entry: {allow: [global layers + final fx names drawn on top], draw(S, p, x)}
  const SPECIALS = {
    flash: {
      allow: ["text", "border"],
      draw(S, p, x) {
        x.fillStyle = col(p.color ?? "$accent");
        x.fillRect(0, 0, R.W, R.H);
        if (p.splat !== false) splat(x, R.W * 0.3, R.H * 0.3, 46, S, 5);
        if (p.bigsplat) splatField(x, R.W * 0.82, R.H * 0.78, 180, S, 6, 16);
      },
    },
    white: {
      allow: ["stickers", "text", "dust", "border"],
      draw(S, p, x) {
        x.fillStyle = col(p.color ?? "#fff");
        x.fillRect(0, 0, R.W, R.H);
        if (p.splat !== false) {
          splatField(x, R.W * 0.7, R.H * 0.35, 160, S, 7, 16);
          splatField(x, R.W * 0.22, R.H * 0.7, 110, S, 8, 12);
        }
      },
    },
    black: {
      allow: ["border"],
      draw(S, p, x) {
        x.fillStyle = col(p.color ?? "#000");
        x.fillRect(0, 0, R.W, R.H);
        if (p.sparkle !== false && S.t < R.nf / R.fps - 0.05)
          sparkle(x, R.W * 0.62, R.H * 0.4, 60, S, 9, "#fff");
      },
    },
    color: {
      allow: ["text", "stickers"],
      draw(S, p, x) {
        x.fillStyle = col(p.color ?? "#000");
        x.fillRect(0, 0, R.W, R.H);
      },
    },
    collage: {
      allow: ["stickers", "text", "dust", "border"],
      async draw(S, p, x) {
        // panels [{clip, src, speed, rect:[x,y,w,h] (0..1), cam}] composed then graded together
        const pl = R.L.plate.x;
        reset(pl);
        pl.fillStyle = col(p.bg ?? "#fff");
        pl.fillRect(0, 0, R.W, R.H);
        for (const pn of p.panels || []) {
          const C = R.clips[pn.clip];
          if (!C) {
            warn("collage: unknown clip " + pn.clip);
            continue;
          }
          const pk = srcPick(
            { src: pn.src, srcFrame: pn.srcf, speed: pn.speed, blend: pn.blend, loop: pn.loop },
            C,
            S.lt,
          );
          const Sx = {
            ...S,
            clip: C,
            si: pk.si,
            blend: pk.blend,
            shot: { cam: pn.cam || {}, fx: {}, i: -1, speed: pn.speed ?? 1 },
          };
          camera(Sx, pn.cam || {});
          const r = pn.rect || [0, 0, 1, 1];
          pl.save();
          reset(pl);
          pl.beginPath();
          pl.rect(r[0] * R.W, r[1] * R.H, r[2] * R.W, r[3] * R.H);
          pl.clip();
          setM(pl, Sx.M);
          await drawPick(pl, C, pk);
          pl.restore();
          if (p.brackets !== false) {
            const X0 = r[0] * R.W - 22,
              Y0 = r[1] * R.H - 22,
              X1 = (r[0] + r[2]) * R.W + 22,
              Y1 = (r[1] + r[3]) * R.H + 22,
              br = (X, Y, dx, dy, s) =>
                poly(
                  x,
                  [
                    [X + dx * 60, Y],
                    [X, Y],
                    [X, Y + dy * 60],
                  ],
                  { w: 5, b: S.b, seed: s },
                );
            S._brk = (S._brk || []).concat([
              () => {
                br(X0, Y0, 1, 1, 1);
                br(X1, Y0, -1, 1, 2);
                br(X0, Y1, 1, -1, 3);
                br(X1, Y1, -1, -1, 4);
              },
            ]);
          }
        }
        const lk = await applyLook(
          S,
          R.L.plate,
          p.duo_head && S.lt < p.duo_head ? "duo" : (p.look ?? R.E.look),
        );
        copyFull(x, lk);
        (S._brk || []).forEach((fn) => fn());
        (p.lines || []).forEach((L, i) =>
          poly(
            x,
            L.map((q) => [q[0] * R.W, q[1] * R.H]),
            { w: 6, b: S.b, seed: 9 + i },
          ),
        );
        if (p.doodles) {
          S.occ = null;
          S.lum = null;
          S.motion = null;
          await inkDoodles(
            S,
            x,
            p.doodles,
            (p.keep || []).map((r) => [r[0] * R.W, r[1] * R.H, r[2] * R.W, r[3] * R.H]),
            0,
            {},
          );
        }
      },
    },
  };

  // ============================================================ render pipeline
  const PHASES = ["back", "subject", "over", "post", "final"];
  let FXI = {}; // merged per-frame lookup built at boot (LAYERS + FACE + TRANSITIONS)
  function normEntry(name, e) {
    if (e.phases)
      return {
        name,
        cut: !!e.cut,
        phases: Object.entries(e.phases).map(([ph, d]) => ({
          phase: ph,
          order: d.order ?? 50,
          draw: d.draw,
          cut: !!d.cut,
        })),
      };
    return {
      name,
      cut: !!e.cut,
      phases: [{ phase: e.phase || "over", order: e.order ?? 50, draw: e.draw, cut: !!e.cut }],
    };
  }
  function buildFXI() {
    FXI = {};
    for (const tb of [LAYERS, FACE, TRANSITIONS])
      for (const [n, e] of Object.entries(tb)) FXI[n] = normEntry(n, e);
  }
  const NON_LAYER_FX = new Set(["stutter", "trail", "stickers", "text", ...CAM_ORDER]);
  function fxItems(S, allowOnly) {
    const fx = S.fx || {},
      list = [];
    const add = (name, p, ord, phase) => {
      if (p === undefined || p === null || p === false) return;
      if (allowOnly && !allowOnly.includes(name)) return;
      const ent = FXI[name];
      if (!ent) {
        if (!NON_LAYER_FX.has(name) && !CAMERA[name]) warn("unknown fx " + name);
        return;
      }
      const pp = p === true ? {} : typeof p === "number" || typeof p === "string" ? { v: p } : p;
      if (pp.enabled === false) return;
      ent.phases.forEach((d) =>
        list.push({
          name,
          p: pp,
          phase: phase || d.phase,
          order: ord ?? d.order,
          draw: d.draw,
          cut: d.cut,
        }),
      );
    };
    for (const [name, p] of Object.entries(R.E.post || {})) if (!(name in fx)) add(name, p);
    for (const [name, p] of Object.entries(fx)) add(name, p);
    ((S.shot && S.kind === "plate" && S.shot.layers) || []).forEach((L, i) =>
      add(L.type, L, L.order ?? 100 + i, L.phase),
    );
    if (!allowOnly || allowOnly.includes("stickers"))
      if (fx.stickers !== false && R.sevt.length)
        list.push({
          name: "stickers",
          p: {},
          phase: "over",
          order: 50,
          draw: (S_, p, x) => drawStickers(S_, x),
        });
    if (!allowOnly || allowOnly.includes("text"))
      if (fx.text !== false && R.texts.length)
        list.push({ name: "text*", p: {}, phase: "over", order: 60, draw: drawTexts });
    return list;
  }
  function drawTexts(S, p, x) {
    R.texts.forEach((Tq, ti) => {
      if (S.t < Tq.t0 - 1e-6 || S.t >= Tq.t1 - 1e-6) return;
      if (S.kind === "special" && Tq.on_specials === false) return;
      reset(x);
      Tq.ent.draw(S, Tq, x, ti);
    });
  }
  async function runPhases(S, items) {
    const x = R.ctx;
    for (const ph of PHASES) {
      if (ph === "subject" && S.kind === "plate" && S.mask) {
        const fx = S.fx || {};
        if (S.backCut || fx.outline || fx.cutout) {
          if (!items.some((i) => i.name === "outline") && S.backCut && fx.outline !== false)
            items.push({
              name: "outline",
              p: {},
              phase: "subject",
              order: 10,
              draw: LAYERS.outline.draw,
            });
          if (!items.some((i) => i.name === "cutout") && fx.cutout !== false)
            items.push({
              name: "cutout",
              p: {},
              phase: "subject",
              order: 20,
              draw: LAYERS.cutout.draw,
            });
        }
      }
      const its = items.filter((i) => i.phase === ph).sort((a, b) => a.order - b.order);
      for (const it of its) {
        reset(x);
        await it.draw(S, it.p, x);
        if (it.cut) S.backCut = true;
      }
      await runHooks("after_" + ph, S);
    }
    reset(x);
  }
  async function ensureOccLum(S, motion) {
    if (S._occDone) return;
    S._occDone = true;
    if (S.mask) {
      S.occ = occFromMask(S.mask, S.M, S.clip).slice();
      if (motion && S.shot.speed !== 0) {
        const m3 = await img(maskPath(S.clip, Math.min(S.si + 3, S.clip.mask_n - 1)));
        if (m3) {
          const o3 = occFromMask(m3, S.M, S.clip),
            cen = (g) => {
              let sx = 0,
                sy = 0,
                m = 0;
              for (let q = 0; q < g.length; q++)
                if (g[q]) {
                  sx += q % R.OGW;
                  sy += Math.floor(q / R.OGW);
                  m++;
                }
              return m ? [sx / m, sy / m] : null;
            };
          const c0 = cen(S.occ),
            c3 = cen(o3);
          if (c0 && c3 && Math.hypot(c3[0] - c0[0], c3[1] - c0[1]) > 0.3)
            S.motion = [c3[0] - c0[0], c3[1] - c0[1]];
        }
      }
    }
    S.lum = S.looked ? lumaGrid(S.looked) : null;
    if (!S.mask && S.lum) {
      S.occ = new Uint8Array(R.OGW * R.OGH);
      for (let i = 0; i < S.occ.length; i++) S.occ[i] = S.lum[i] < 0.5 ? 1 : 0;
    }
  }
  async function renderFrame(f) {
    f = clamp(Math.floor(f), 0, Math.max(0, R.nf - 1));
    const S = stateAt(f),
      x = R.ctx;
    reset(x);
    await runHooks("beforeFrame", S);
    if (S.kind === "special") {
      const sp = S.special,
        ent = SPECIALS[sp.type];
      if (!ent) {
        warn("unknown special " + sp.type);
        x.fillStyle = "#f0f";
        x.fillRect(0, 0, R.W, R.H);
        return S;
      }
      S.fo = null;
      const allow = sp.allow || ent.allow || [];
      await ent.draw(S, resolveParams(sp, S), x);
      reset(x);
      await runPhases(S, fxItems(S, allow));
    } else if (S.kind === "plate") {
      const C = S.clip,
        sh = S.shot;
      const mp = C.mask_dir ? img(maskPath(C, S.si)) : null; // mattes (and faces) stay on the whole frame si
      const pc = R.L.plate.x;
      reset(pc);
      pc.fillStyle = col(sh.bg ?? (R.E.canvas || {}).bg, "#fff");
      pc.fillRect(0, 0, R.W, R.H);
      pc.save();
      setM(pc, S.M);
      const im = await drawPick(pc, C, S);
      pc.restore(); // slow-mo blend lives in drawPick
      const mm = mp ? await mp : null;
      if (!im) warn(`missing frame ${framePath(C, S.si)}`);
      const nx = (S.blend ? Math.max(S.blend.i0, S.blend.i1) : S.si) + 1;
      if (nx < C.n) img(framePath(C, nx)); // prefetch
      S.plate = im;
      S.mask = mm;
      const tr = sh.fx && sh.fx.trail;
      if (tr) {
        // ghost trail: earlier source frames over the plate with falling opacity (before the look)
        const p = tr === true ? {} : tr,
          n = p.n ?? 3,
          st = p.step ?? 2,
          ims = await Promise.all(
            Array.from({ length: n }, (_, k) =>
              img(framePath(C, Math.max(0, S.si - (k + 1) * st))),
            ),
          );
        pc.save();
        setM(pc, S.M);
        pc.globalCompositeOperation = p.op || "source-over";
        for (let k = n - 1; k >= 0; k--)
          if (ims[k]) {
            pc.globalAlpha = (p.alpha ?? 0.35) * (1 - k / (n + 1));
            pc.drawImage(ims[k], 0, 0, C.w, C.h);
          }
        pc.restore();
      }
      S.plateCanvas = R.L.plate;
      await runHooks("afterPlate", S);
      S.looked = await applyLook(S, R.L.plate, sh.look ?? R.E.look);
      await runHooks("afterLook", S);
      copyFull(x, S.looked);
      await runPhases(S, fxItems(S));
    } else {
      x.fillStyle = col((R.E.canvas || {}).bg, "#000");
      x.fillRect(0, 0, R.W, R.H);
      if (S.kind === "missing") {
        x.fillStyle = "#f0f";
        x.fillRect(0, 0, R.W, R.H);
      }
    }
    await runHooks("afterFrame", S);
    reset(x);
    return S;
  }
  async function runHooks(name, S) {
    const L = R.hooks[name];
    if (L) for (const fn of L) await fn(S, R.ctx, RRC);
  }

  // ============================================================ Visual timing cues (map to actual recorded SFX when requested)
  function cues() {
    const out = [],
      E = R.E,
      sfx = E.sfx || {};
    (sfx.cues || []).forEach((c) =>
      out.push({ ...c, t: c.f !== undefined ? c.f / R.fps : T(c.t), src: "edl" }),
    );
    if (sfx.auto !== false) {
      R.texts.forEach((Tq) => {
        if (Tq.ent.cues) Tq.ent.cues(Tq).forEach((c) => out.push({ ...c, src: "text" }));
      });
      [...new Set(R.sevt.map((s) => +s.tIn.toFixed(3)))].forEach((t, i) =>
        out.push({ t, k: "slap", i, src: "sticker" }),
      );
      R.shots.forEach((s) => {
        if (s.special) {
          if (s.special.type === "flash") out.push({ t: s.t0, k: "flash", src: "special" });
          if (s.special.type === "white") out.push({ t: s.t0, k: "white", src: "special" });
        }
        const fx = s.fx || {};
        if (fx.fin)
          out.push({ t: s.t0, k: (fx.fin.k ?? 1) > 1 ? "flashBig" : "flash", src: "fin" });
        if (fx.white)
          out.push({
            t:
              s.t0 + (fx.white.at ?? (fx.white.side === "out" ? s.dur - (fx.white.d ?? 0.067) : 0)),
            k: "white",
            src: "white",
          });
        if (fx.magenta) out.push({ t: s.t0 + (fx.magenta.at ?? 0), k: "sparkle", src: "magenta" });
        if (fx.mosaic) out.push({ t: s.t0 + (fx.mosaic.at ?? 0), k: "glitch", src: "mosaic" });
        if (fx.glint) out.push({ t: s.t0 + (fx.glint.at ?? 0), k: "shing", src: "glint" });
        if (fx.slash)
          out.push({ t: s.t0 + (fx.slash.at ?? 0), k: "whoosh", d: 0.18, src: "slash" });
        if (fx.punch && fx.shake && sfx.hits) out.push({ t: s.t0, k: "hit", src: "punch" });
      });
      R.specials.forEach((s) => {
        if (s.type === "flash") out.push({ t: s.t0, k: "flash", src: "special" });
        if (s.type === "white") out.push({ t: s.t0, k: "white", src: "special" });
      });
    }
    const dur = R.nf / R.fps;
    return out
      .filter((c) => c.t !== undefined && c.t >= 0 && c.t < dur && !(sfx.mute || []).includes(c.k))
      .sort((a, b) => a.t - b.t)
      .filter((c, i, a) => !(i && a[i - 1].k === c.k && Math.abs(a[i - 1].t - c.t) < 0.02));
  }

  // ============================================================ boot + API
  // fonts[]: {family, url, weight, style}: a font file (workspace path such as comp/fonts/X.ttf, /_hf/katana/scripts/
  // fonts/..., or a CORS-enabled https URL such as raw.githubusercontent.com/google/fonts/...), or {family, css, weight,
  // style}: a stylesheet with @font-face rules (a Google Fonts css2 URL, or a workspace .css). Every Chrome shard loads
  // them, so files copied into comp/fonts/ are the robust choice; a failed or missing font is a warning, never silent.
  const withTimeout = (p, ms, what) =>
    Promise.race([
      p,
      new Promise((_, rej) =>
        setTimeout(() => rej(new Error(`${what} timed out after ${ms} ms`)), ms),
      ),
    ]);
  async function loadFonts(E) {
    for (const f of E.fonts || []) {
      const fam = f.family,
        wt = f.weight || "normal",
        st = f.style || "normal",
        ms = f.timeout_ms ?? 15000,
        spec = `${st} ${wt} 48px "${fam}"`;
      try {
        if (f.css) {
          await withTimeout(
            new Promise((res, rej) => {
              const l = document.createElement("link");
              l.rel = "stylesheet";
              l.href = wurl(f.css);
              l.onload = res;
              l.onerror = () => rej(new Error("stylesheet did not load"));
              document.head.appendChild(l);
            }),
            ms,
            "stylesheet",
          );
          if (fam) {
            const got = await withTimeout(document.fonts.load(spec), ms, "font");
            if (!got || !got.length) warn(`font ${fam}: no @font-face for it in ${f.css}`);
          }
        } else {
          const ff = new FontFace(fam, `url(${wurl(f.url)})`, { weight: wt, style: st });
          await withTimeout(ff.load(), ms, "font");
          document.fonts.add(ff);
        }
      } catch (e) {
        warn(`font ${fam || f.css || f.url} failed: ${e && e.message}`);
      }
    }
    try {
      await document.fonts.ready;
    } catch (e) {
      /* ignore */
    }
  }
  async function boot(opts = {}) {
    const tb = performance.now();
    R.log = opts.log || R.log;
    const E =
      typeof opts.edl === "object" ? opts.edl : await fetchJSON(opts.edl || "/comp/edl.json");
    if (!E) throw new Error("EDL not found: " + (opts.edl || "/comp/edl.json"));
    R.E = E;
    normEDL(E);
    R.rs = opts.rs || 1;
    R.PW = Math.max(2, Math.round((R.W * R.rs) / 2) * 2);
    R.PH = Math.max(2, Math.round((R.H * R.rs) / 2) * 2);
    R.canvas = opts.canvas || document.createElement("canvas");
    R.canvas.width = R.PW;
    R.canvas.height = R.PH;
    R.ctx = R.canvas.getContext("2d", { willReadFrequently: false });
    R.OGW = Math.ceil(R.W / CELL);
    R.OGH = Math.ceil(R.H / CELL);
    R.GW = Math.ceil(R.W / GS);
    R.GH = Math.ceil(R.H / GS);
    R.L = {
      plate: pmk(),
      look: pmk(true),
      tmp: pmk(),
      cut: pmk(),
      outl: mk(R.PW / 2, R.PH / 2),
      small: mk(R.PW / 4, R.PH / 4),
      grid: mk(R.GW, R.GH, true),
      occ: mk(R.OGW, R.OGH, true),
      lum: mk(R.OGW, R.OGH, true),
    };
    if (opts.fx) {
      // project hooks: comp/fx.js (optional)
      const ok = await fetch(wurl(opts.fx), { method: "HEAD", cache: "no-store" })
        .then((r) => r.ok)
        .catch(() => false);
      if (ok)
        await new Promise((res, rej) => {
          const s = document.createElement("script");
          s.src = wurl(opts.fx) + "?v=" + Date.now();
          s.onload = res;
          s.onerror = () => rej(new Error("fx.js failed to load"));
          document.head.appendChild(s);
        });
    }
    buildFXI();
    await loadFonts(E);
    await initClips(E);
    await runHooks("init", { R, E });
    R.texts = (E.text || [])
      .map((Tq, i) => {
        const o = {
          ...Tq,
          t0: Tq.f0 !== undefined ? Tq.f0 / R.fps : T(Tq.t0),
          t1: Tq.f1 !== undefined ? Tq.f1 / R.fps : T(Tq.t1),
        };
        o.type = o.type || "graffiti";
        o.ent = TEXT[o.type];
        if (!o.ent) {
          warn("unknown text type " + o.type);
          return null;
        }
        if (o.t1 === undefined) o.t1 = R.nf / R.fps;
        if (o.ent.init) o.ent.init(o, i);
        return o;
      })
      .filter(Boolean);
    await loadStickers();
    await buildCutouts();
    await planStickers();
    await runHooks("ready", { R, E });
    // validation
    R.shots.forEach((s) => {
      if (s.special) return;
      const C = R.clips[s.clip];
      if (!C) {
        warn(`shot ${s.i}: unknown clip ${s.clip}`);
        return;
      }
      const end =
        (s.srcFrame !== undefined ? s.srcFrame / C.fps : s.src) +
        s.dur * Math.max(s.speed, s.speed1 ?? s.speed);
      if (s.speed > 0 && end * C.fps > C.n + 1 && !s.loop)
        warn(
          `shot ${s.i} (${s.clip}) runs past the clip end (${end.toFixed(2)}s > ${(C.n / C.fps).toFixed(2)}s): last frame holds`,
        );
    });
    for (const s of R.shots)
      for (const name of Object.keys(s.fx || {}))
        if (!FXI[name] && !NON_LAYER_FX.has(name) && !CAMERA[name])
          warn(`shot ${s.i}: unknown fx ${name}`);
    // a taller-than-canvas take (Genjutsu 4:3 -> 16:9) cover-cropped at the default centre cuts heads off
    const cropWarned = new Set();
    R.shots.forEach((s) => {
      const C = s.special ? null : R.clips[s.clip];
      if (!C || cropWarned.has(C.id)) return;
      const cam = camOf(s, C);
      if (
        cam.type === "facelock" ||
        cam.lock ||
        (cam.fit && cam.fit !== "cover") ||
        cropOf(cam) ||
        cam.ay !== undefined
      )
        return;
      const vis = R.H / Math.max(R.W / C.w, R.H / C.h) / C.h; // aspect only (a deliberate cam.z punch-in is fine)
      if (vis < 0.85) {
        cropWarned.add(C.id);
        warn(
          `shot ${s.i}: clip ${C.id} (${C.w}x${C.h}) is cover-cropped to ${R.W}x${R.H} at the default centre, ${Math.round((1 - vis) * 100)}% of its height is cut: set clips.${C.id}.cam.crop (e.g. [0.5, 0.35]) or the shot's cam.crop / cam.ay so heads stay in frame`,
        );
      }
    });
    R.bootMs = Math.round(performance.now() - tb);
    return info();
  }
  function info() {
    return {
      version: RRC.version,
      w: R.W,
      h: R.H,
      fps: R.fps,
      frames: R.nf,
      rs: R.rs,
      shots: R.shots.length,
      specials: R.specials.length,
      clips: Object.keys(R.clips),
      texts: R.texts.length,
      stickers: {
        assets: R.stickers.length,
        cutouts: R.cutouts.length,
        placed: R.sevt.length,
        log: R.stickerLog,
      },
      boot_ms: R.bootMs,
      warnings: R.warnings.slice(),
    };
  }
  function register(table, name, entry) {
    const T_ = { LOOKS, CAMERA, LAYERS, FACE, TRANSITIONS, TEXT, SPECIALS, LOOK_PRESETS }[table];
    if (table === "DOODLES") {
      const fam = entry.family || "kawaii";
      DOODLES[fam][name] = entry.draw || entry;
      if (fam === "kawaii" && entry.size) KAWAII_SIZE[name] = entry.size;
      return;
    }
    if (!T_) throw new Error("RRC.register: unknown table " + table);
    if (table === "CAMERA" && entry.custom === undefined) entry.custom = true;
    T_[name] = entry;
    if (FXI && (table === "LAYERS" || table === "FACE" || table === "TRANSITIONS"))
      FXI[name] = normEntry(name, entry);
  }
  function hook(name, fn) {
    (R.hooks[name] = R.hooks[name] || []).push(fn);
  }
  function toBlob(type = "image/jpeg", q = 0.92) {
    return new Promise((res) => R.canvas.toBlob(res, type, q));
  }

  Object.assign(RRC, {
    boot,
    renderFrame,
    cues,
    info,
    register,
    hook,
    toBlob,
    stateAt,
    LOOKS,
    LOOK_PRESETS,
    CAMERA,
    LAYERS,
    FACE,
    TRANSITIONS,
    TEXT,
    STICKERS,
    DOODLES,
    SPECIALS,
    REGIONS,
    GCAPS,
    PALETTE,
    FONTS,
    util: {
      hash,
      hs,
      rng,
      clamp,
      lerp,
      ease,
      easeOut,
      noise1,
      col,
      rgbOf,
      withAlpha,
      mk,
      reset,
      copyFull,
      px,
      setM,
      mapM,
      img,
      fetchJSON,
      framePath,
      maskPath,
      fp,
      foOr,
      popIn,
      poly,
      zigzag,
      crPts,
      drawStrokes,
      splat,
      splatField,
      sparkle,
      rays,
      arrow,
      scratch,
      crossDoodle,
      hatch,
      kawaiiDoodle,
      asterisk,
      starburst,
      slashes,
      outlinedText,
      typeWord,
      fontStr,
      drawFontText,
      gLayout,
      gDraw,
      fitGraffiti,
      mosaic,
      glitchBlocks,
      blurFrame,
      flashlight,
      contours,
      penContour,
      occFromMask,
      lumaGrid,
      applyLook,
      drawCutout,
      drawOutline,
      padR,
      hit,
      unionR,
      win,
      av,
      T,
      srcPick,
      drawPick,
      camOf,
    },
  });
  Object.defineProperty(RRC, "nf", { get: () => R.nf, enumerable: true });
  Object.defineProperty(RRC, "fps", { get: () => R.fps, enumerable: true });
})(typeof window !== "undefined" ? window : globalThis);
