// fx.js - the edit engine: a canvas port of editlib.py + fx.py (beat-synced-edit).
// Integer-frame timeline at 24 fps. A plan is {fps, w, h, nf, src, shots, ev, rgb, scan} (see reference/plan.md):
//   shots: contiguous [f0, f1) items: footage shot | solid | collage | knock (video inside letters)
//   ev:    overlay events on output frames (word, marquee, lower, labels, stack, kinetic, cutouts, frame, counter,
//          leak, slices, wipe, shake)
//   rgb:   {frame: px} RGB split, scan: [[f0, f1], ..] scanline ranges
// Colours are [r, g, b] in 0..1 like the python original. Everything is deterministic per output frame, so any frame
// range can be rendered by any Chrome instance.
"use strict";
// exported as a page global for engine/index.html (plain <script>, no modules)
globalThis.FX = (() => {
  let W = 1440,
    H = 1080,
    FPS = 24,
    PLAN = null;
  const RED = [0.88, 0.07, 0.09],
    WHITE = [1, 1, 1],
    BLACK = [0, 0, 0];
  const FONT = 'Arial, "Liberation Sans", Helvetica, sans-serif';
  const clamp = (v, a = 0, b = 1) => (v < a ? a : v > b ? b : v);
  const css = (c, a = 1) =>
    `rgba(${Math.round(clamp(c[0]) * 255)},${Math.round(clamp(c[1]) * 255)},${Math.round(clamp(c[2]) * 255)},${a})`;
  function mk(w = W, h = H, rf = true) {
    const c = document.createElement("canvas");
    c.width = Math.max(1, Math.round(w));
    c.height = Math.max(1, Math.round(h));
    c.x = c.getContext("2d", rf ? { willReadFrequently: true } : undefined);
    c.x.imageSmoothingQuality = "high";
    return c;
  }
  function copyOf(c) {
    const o = mk(c.width, c.height);
    o.x.drawImage(c, 0, 0);
    return o;
  }
  // deterministic rng (mulberry32)
  function rng(seed) {
    let a = seed >>> 0 || 1;
    return () => {
      a |= 0;
      a = (a + 0x6d2b79f5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  const rint = (r, a, b) => a + Math.floor(r() * (b - a)); // [a, b)
  const runi = (r, a, b) => a + r() * (b - a);

  // ------------------------------------------------------------------ sources
  const IMG = new Map();
  function srcInfo(s) {
    const i = PLAN.src[s];
    if (!i) throw new Error("unknown source " + s);
    return i;
  }
  function frameUrl(s, k) {
    const i = srcInfo(s);
    k = clamp(Math.round(k), 0, i.n - 1);
    return `${i.dir || "src/" + s}/${String(k).padStart(5, "0")}.jpg`;
  }
  function load(s, k) {
    const u = frameUrl(s, k);
    let p = IMG.get(u);
    if (!p) {
      p = new Promise((res, rej) => {
        const im = new Image();
        im.onload = () => res(im);
        im.onerror = () => rej(new Error("cannot load " + u));
        im.src = u;
      });
      IMG.set(u, p);
      if (IMG.size > 260) IMG.delete(IMG.keys().next().value);
    }
    return p;
  }
  const startFrame = (o) => (o.sf !== undefined ? o.sf : Math.ceil(o.t * FPS - 1e-6)); // ffmpeg -ss t: first frame at/after t

  // ------------------------------------------------------------------ grade (editlib.grade / levels)
  const LV = new Map();
  async function levels(s, k0) {
    // partial stretch keeps dark moods
    const key = s + ":" + k0;
    if (LV.has(key)) return LV.get(key);
    const im = await load(s, k0),
      w = 480,
      h = Math.max(2, Math.round((480 * im.height) / im.width)),
      c = mk(w, h);
    c.x.drawImage(im, 0, 0, w, h);
    const d = c.x.getImageData(0, 0, w, h).data,
      hist = new Uint32Array(1024);
    for (let i = 0; i < d.length; i += 4)
      hist[
        Math.min(
          1023,
          Math.floor(((d[i] * 0.2126 + d[i + 1] * 0.7152 + d[i + 2] * 0.0722) / 255) * 1023.999),
        )
      ]++;
    const pct = (q) => {
      const tgt = (q / 100) * (w * h - 1);
      let a = 0;
      for (let b = 0; b < 1024; b++) {
        a += hist[b];
        if (a > tgt) return (b + 0.5) / 1024;
      }
      return 1;
    };
    const lo = pct(0.8),
      hi = pct(99.7),
      r = [lo * 0.7, hi + (1 - hi) * 0.35];
    LV.set(key, r);
    return r;
  }
  const scurve = (x, a) => (1 - a) * x + a * (0.5 - 0.5 * Math.cos(Math.PI * clamp(x)));
  const BW_LUT = new Float32Array(4097);
  for (let i = 0; i <= 4096; i++) BW_LUT[i] = Math.pow(scurve(i / 4096, 0.45), 1.06);
  const POP_HUES = {
    warm: [
      [335, 361],
      [0, 40],
    ],
    yellow: [[35, 75]],
  };
  function blurArr(arr, w, h, sigma, ch = 1) {
    // gaussian blur of a float field (0..1) via canvas
    const c = mk(w, h),
      id = c.x.createImageData(w, h),
      d = id.data;
    for (let p = 0, i = 0; p < w * h; p++, i += 4) {
      if (ch === 1) {
        d[i] = d[i + 1] = d[i + 2] = 255;
        d[i + 3] = arr[p] * 255;
      } else {
        d[i] = arr[p * 3] * 255;
        d[i + 1] = arr[p * 3 + 1] * 255;
        d[i + 2] = arr[p * 3 + 2] * 255;
        d[i + 3] = 255;
      }
    }
    c.x.putImageData(id, 0, 0);
    const o = mk(w, h);
    if (ch === 3) {
      o.x.drawImage(c, 0, 0);
    }
    o.x.filter = `blur(${sigma}px)`;
    o.x.drawImage(c, 0, 0);
    o.x.filter = "none";
    const od = o.x.getImageData(0, 0, w, h).data,
      out = new Float32Array(w * h * ch);
    for (let p = 0, i = 0; p < w * h; p++, i += 4) {
      if (ch === 1) out[p] = od[i + 3] / 255;
      else {
        out[p * 3] = od[i] / 255;
        out[p * 3 + 1] = od[i + 1] / 255;
        out[p * 3 + 2] = od[i + 2] / 255;
      }
    }
    return out;
  }
  function grade(c, g, lo, hi, gamma = 1, pop = "warm") {
    // in place on canvas c (any size)
    if (g === "orig" && lo === 0 && hi === 1) return c;
    const w = c.width,
      h = c.height,
      id = c.x.getImageData(0, 0, w, h),
      d = id.data,
      sc = 1 / Math.max(hi - lo, 1e-3),
      N = w * h;
    const lev = (v) => {
      let x = (v / 255 - lo) * sc;
      x = x < 0 ? 0 : x > 1 ? 1 : x;
      return gamma !== 1 ? Math.pow(x, gamma) : x;
    };
    const L = new Float32Array(256);
    for (let v = 0; v < 256; v++) L[v] = lev(v);
    if (g === "pop") {
      const hues = POP_HUES[pop] || POP_HUES.warm,
        m0 = new Float32Array(N),
        H6 = new Float32Array(N),
        S6 = new Float32Array(N),
        V6 = new Float32Array(N);
      let any = 0;
      for (let p = 0, i = 0; p < N; p++, i += 4) {
        const r = d[i] / 255,
          gg = d[i + 1] / 255,
          b = d[i + 2] / 255,
          v = Math.max(r, gg, b),
          mn = Math.min(r, gg, b),
          df = v - mn;
        const s = v > 0 ? df / v : 0;
        let hh = 0;
        if (df > 0) {
          hh =
            v === r
              ? (60 * (gg - b)) / df
              : v === gg
                ? 120 + (60 * (b - r)) / df
                : 240 + (60 * (r - gg)) / df;
          if (hh < 0) hh += 360;
        }
        H6[p] = hh;
        S6[p] = s;
        V6[p] = v;
        if (s > 0.55 && v > 0.25) {
          for (const [a0, a1] of hues)
            if (hh >= a0 && hh < a1) {
              m0[p] = 1;
              any++;
              break;
            }
        }
      }
      const bw = new Float32Array(N);
      for (let p = 0, i = 0; p < N; p++, i += 4)
        bw[p] =
          BW_LUT[
            Math.round((L[d[i]] * 0.2126 + L[d[i + 1]] * 0.7152 + L[d[i + 2]] * 0.0722) * 4096)
          ];
      if (!any) {
        for (let p = 0, i = 0; p < N; p++, i += 4) {
          const v = bw[p] * 255;
          d[i] = d[i + 1] = d[i + 2] = v;
        }
        c.x.putImageData(id, 0, 0);
        return c;
      }
      const m = blurArr(m0, w, h, 1.5, 1),
        col = new Float32Array(N * 3);
      for (let p = 0; p < N; p++) {
        if (m[p] <= 0.002) continue;
        const hh = H6[p] / 60,
          s = Math.min(1, S6[p] * 1.5),
          v = Math.min(1, V6[p] * 1.9),
          k = Math.floor(hh) % 6,
          f = hh - Math.floor(hh);
        const P = v * (1 - s),
          Q = v * (1 - s * f),
          T = v * (1 - s * (1 - f));
        const rgb = [
          [v, T, P],
          [Q, v, P],
          [P, v, T],
          [P, Q, v],
          [T, P, v],
          [v, P, Q],
        ][k];
        col[p * 3] = rgb[0] * m[p];
        col[p * 3 + 1] = rgb[1] * m[p];
        col[p * 3 + 2] = rgb[2] * m[p];
      }
      const glow = blurArr(col, w, h, 7, 3);
      for (let p = 0, i = 0; p < N; p++, i += 4) {
        for (let ch = 0; ch < 3; ch++) {
          const o = bw[p] * (1 - m[p]) + col[p * 3 + ch];
          d[i + ch] = (1 - (1 - o) * (1 - 0.9 * glow[p * 3 + ch])) * 255;
        }
      }
      c.x.putImageData(id, 0, 0);
      return c;
    }
    for (let i = 0; i < d.length; i += 4) {
      const r = L[d[i]],
        gg = L[d[i + 1]],
        b = L[d[i + 2]];
      if (g === "bw") {
        const v = BW_LUT[Math.round((r * 0.2126 + gg * 0.7152 + b * 0.0722) * 4096)] * 255;
        d[i] = d[i + 1] = d[i + 2] = v;
      } else if (g === "color") {
        // muted, cool
        const Y = r * 0.2126 + gg * 0.7152 + b * 0.0722,
          t = (1 - Y) ** 3;
        d[i] = scurve(clamp((Y + 0.5 * (r - Y)) * 0.93 - 0.012 * t), 0.25) * 255;
        d[i + 1] = scurve(clamp((Y + 0.5 * (gg - Y)) * 1.0 + 0.004 * t), 0.25) * 255;
        d[i + 2] = scurve(clamp((Y + 0.5 * (b - Y)) * 1.07 + 0.028 * t), 0.25) * 255;
      } else {
        d[i] = r * 255;
        d[i + 1] = gg * 255;
        d[i + 2] = b * 255;
      }
    }
    c.x.putImageData(id, 0, 0);
    return c;
  }

  // ------------------------------------------------------------------ post (editlib.post)
  let VIG = null,
    NOISE = null;
  function initPost() {
    VIG = mk(W, H);
    const id = VIG.x.createImageData(W, H),
      d = id.data;
    for (let y = 0; y < H; y++)
      for (let x = 0; x < W; x++) {
        const r =
          Math.sqrt(((x - W / 2) / (W / 2)) ** 2 + ((y - H / 2) / (H / 2)) ** 2) / Math.SQRT2;
        const v = (1 - 0.38 * r ** 2.2) * 255,
          i = (y * W + x) * 4;
        d[i] = d[i + 1] = d[i + 2] = v;
        d[i + 3] = 255;
      }
    VIG.x.putImageData(id, 0, 0);
    const hw = W >> 1,
      hh = H >> 1,
      r = rng(7),
      half = new Float32Array(hw * hh);
    for (let i = 0; i < half.length; i += 2) {
      // Box-Muller normals at half res
      const u = Math.max(1e-9, r()),
        v = r(),
        m = Math.sqrt(-2 * Math.log(u));
      half[i] = m * Math.cos(2 * Math.PI * v);
      if (i + 1 < half.length) half[i + 1] = m * Math.sin(2 * Math.PI * v);
    }
    NOISE = new Float32Array(W * H); // bilinear up to full res, scaled to 8-bit units
    for (let y = 0; y < H; y++) {
      const fy = Math.min(hh - 1, Math.max(0, (y + 0.5) / 2 - 0.5)),
        y0 = Math.floor(fy),
        y1 = Math.min(hh - 1, y0 + 1),
        ty = fy - y0;
      for (let x = 0; x < W; x++) {
        const fx = Math.min(hw - 1, Math.max(0, (x + 0.5) / 2 - 0.5)),
          x0 = Math.floor(fx),
          x1 = Math.min(hw - 1, x0 + 1),
          tx = fx - x0;
        const a = half[y0 * hw + x0] * (1 - tx) + half[y0 * hw + x1] * tx,
          b = half[y1 * hw + x0] * (1 - tx) + half[y1 * hw + x1] * tx;
        NOISE[y * W + x] = (a * (1 - ty) + b * ty) * 0.032 * 255;
      }
    }
  }
  function post(c, flash, alpha, g) {
    const o = mk(W, H);
    o.x.drawImage(c, 0, 0);
    o.x.filter = "blur(0.65px)";
    o.x.drawImage(c, 0, 0);
    o.x.filter = "none"; // soften AI crispness
    const qw = W >> 2,
      qh = H >> 2,
      q = mk(qw, qh);
    q.x.drawImage(o, 0, 0, qw, qh); // bloom at 1/4 res
    const qd = q.x.getImageData(0, 0, qw, qh),
      d = qd.data;
    for (let i = 0; i < d.length; i += 4) {
      const Y = (d[i] * 0.2126 + d[i + 1] * 0.7152 + d[i + 2] * 0.0722) / 255,
        k = clamp((Y - 0.62) / 0.38);
      d[i] *= k;
      d[i + 1] *= k;
      d[i + 2] *= k;
    }
    q.x.putImageData(qd, 0, 0);
    const qb = mk(qw, qh);
    qb.x.fillRect(0, 0, qw, qh);
    qb.x.filter = "blur(4px)";
    qb.x.drawImage(q, 0, 0);
    qb.x.filter = "none";
    o.x.globalCompositeOperation = "screen";
    o.x.globalAlpha = 0.42;
    o.x.drawImage(qb, 0, 0, W, H);
    o.x.globalAlpha = 1;
    o.x.globalCompositeOperation = "multiply";
    o.x.drawImage(VIG, 0, 0);
    o.x.globalCompositeOperation = "source-over";
    if (flash) {
      o.x.globalAlpha = clamp(flash);
      o.x.fillStyle = "#fff";
      o.x.fillRect(0, 0, W, H);
      o.x.globalAlpha = 1;
    }
    if (alpha < 1) {
      o.x.globalAlpha = clamp(1 - alpha);
      o.x.fillStyle = "#000";
      o.x.fillRect(0, 0, W, H);
      o.x.globalAlpha = 1;
    }
    const id = o.x.getImageData(0, 0, W, H),
      dd = id.data,
      N = W * H,
      off = Math.floor(rng(g * 7919 + 13)() * N); // film grain
    for (let p = 0, i = 0; p < N; p++, i += 4) {
      let k = p + off;
      if (k >= N) k -= N;
      const n = NOISE[k];
      dd[i] += n;
      dd[i + 1] += n;
      dd[i + 2] += n;
    }
    o.x.putImageData(id, 0, 0);
    return o;
  }

  // ------------------------------------------------------------------ text (fx.tmask / paste / text_c)
  const TM = new Map(),
    TT = new Map(),
    MC = mk(8, 8);
  function tmask(text, size, outline = 0) {
    // white ink on transparent, 2 px pad (PIL tmask)
    const key = text + "|" + size + "|" + outline;
    if (TM.has(key)) return TM.get(key);
    MC.x.font = `bold ${size}px ${FONT}`;
    const m = MC.x.measureText(text),
      o = outline;
    const l = m.actualBoundingBoxLeft,
      r = m.actualBoundingBoxRight,
      a = m.actualBoundingBoxAscent,
      ds = m.actualBoundingBoxDescent;
    const w = Math.ceil(l + r) + 4 + 2 * o,
      h = Math.ceil(a + ds) + 4 + 2 * o,
      c = mk(w, h, false);
    c.x.font = MC.x.font;
    c.x.fillStyle = "#fff";
    c.x.strokeStyle = "#fff";
    c.x.lineJoin = "round";
    const X = 2 + o + l,
      Y = 2 + o + a;
    if (o) {
      c.x.lineWidth = 2 * o;
      c.x.strokeText(text, X, Y);
      c.x.fillText(text, X, Y);
      c.x.globalCompositeOperation = "destination-out";
      c.x.fillText(text, X, Y);
      c.x.globalCompositeOperation = "source-over";
    } else c.x.fillText(text, X, Y);
    c.adv = m.width;
    TM.set(key, c);
    return c;
  }
  function tint(m, color) {
    const key = m;
    let byC = TT.get(key);
    if (!byC) {
      byC = new Map();
      TT.set(key, byC);
    }
    const ck = color.join(",");
    if (byC.has(ck)) return byC.get(ck);
    const c = mk(m.width, m.height, false);
    c.x.drawImage(m, 0, 0);
    c.x.globalCompositeOperation = "source-in";
    c.x.fillStyle = css(color);
    c.x.fillRect(0, 0, c.width, c.height);
    byC.set(ck, c);
    return c;
  }
  function paste(x, m, x0, y0, color, alpha = 1, scale = 1, blur = 0) {
    if (alpha <= 0) return;
    const t = tint(m, color);
    x.x.globalAlpha = clamp(alpha);
    if (blur) x.x.filter = `blur(${blur}px)`;
    if (scale !== 1)
      x.x.drawImage(t, Math.round(x0), Math.round(y0), m.width * scale, m.height * scale);
    else x.x.drawImage(t, Math.round(x0), Math.round(y0));
    x.x.filter = "none";
    x.x.globalAlpha = 1;
  }
  function rect(x, x0, y0, x1, y1, color, alpha = 1) {
    x0 = Math.round(Math.max(0, x0));
    y0 = Math.round(Math.max(0, y0));
    x1 = Math.round(Math.min(W, x1));
    y1 = Math.round(Math.min(H, y1));
    if (x1 > x0 && y1 > y0) {
      x.x.globalAlpha = clamp(alpha);
      x.x.fillStyle = css(color);
      x.x.fillRect(x0, y0, x1 - x0, y1 - y0);
      x.x.globalAlpha = 1;
    }
  }
  function textC(
    x,
    text,
    size,
    cx,
    cy,
    color = WHITE,
    alpha = 1,
    shadow = 0.55,
    scale = 1,
    outline = 0,
  ) {
    const m = tmask(text, size, outline),
      w = m.width * scale,
      h = m.height * scale;
    if (shadow) paste(x, m, cx - w / 2 + 3, cy - h / 2 + 5, BLACK, shadow * alpha, scale, 7);
    paste(x, m, cx - w / 2, cy - h / 2, color, alpha, scale);
    return [w, h];
  }
  function shadowPaste(x, m, cx, cy, a = 0.5) {
    paste(x, m, cx - m.width / 2 + 3, cy - m.height / 2 + 5, BLACK, a, 1, 7);
  }

  // ------------------------------------------------------------------ overlay events
  const EVH = {};
  EVH.word = (x, e, k, _n) => {
    // big centred word, pops in; optional box wiping in
    const size = e.size || 200,
      m = tmask(e.text, size, e.outline || 0),
      w = m.width,
      h = m.height;
    const s = 1 + 0.18 * Math.max(0, 1 - k / 3) ** 2,
      cy = (e.y ?? 0.5) * H;
    if (e.box) {
      const bw = w * s + 80,
        bh = h * s + 52,
        grow = Math.min(1, (k + 1) / 3);
      rect(x, W / 2 - bw / 2, cy - bh / 2, W / 2 - bw / 2 + bw * grow, cy + bh / 2, e.box);
      if (k >= 1) textC(x, e.text, size, W / 2, cy, e.color || WHITE, 1, 0, s);
    } else
      textC(
        x,
        e.text,
        size,
        (e.x ?? 0.5) * W,
        cy,
        e.color || WHITE,
        1,
        e.shadow ?? 0.55,
        s,
        e.outline || 0,
      );
  };
  EVH.marquee = (x, e, k, _n) => {
    // rows of repeated text scrolling
    for (let row of e.rows) {
      if (Array.isArray(row))
        row = { y: row[0], v: row[1], size: row[2], color: row[3], alpha: row[4], band: row[5] };
      const text = row.text ?? e.text,
        m = tmask(text, row.size, row.outline || 0),
        adv = Math.round(m.adv),
        cy = row.y * H,
        v = row.v;
      if (row.band) rect(x, 0, cy - row.size * 0.8, W, cy + row.size * 0.8, row.band, 0.9);
      const xp = v < 0 ? -((((-v * k) % adv) + adv) % adv) : -adv + ((v * k) % adv);
      for (let i = 0; i < 14 && xp + i * adv < W; i++)
        paste(x, m, xp + i * adv, cy - m.height / 2, row.color || WHITE, row.alpha ?? 1);
    }
  };
  EVH.lower = (x, e, k, _n) => {
    // centred label box that wipes in
    const size = e.size || 58,
      m = tmask(e.text, size),
      w = m.width,
      h = m.height,
      cy = (e.y ?? 0.8) * H;
    const bw = w + 56,
      grow = Math.min(1, (k + 1) / 4);
    rect(
      x,
      W / 2 - bw / 2,
      cy - h / 2 - 18,
      W / 2 - bw / 2 + bw * grow,
      cy + h / 2 + 18,
      e.box || RED,
    );
    if (k >= 2) paste(x, m, W / 2 - w / 2, cy - h / 2, e.color || WHITE);
  };
  EVH.stack = (x, e, k, _n) => {
    // wall of repeated lines scrolling up, every 3rd boxed
    const size = e.size || 46,
      gap = e.gap || 72,
      v = e.speed || 6,
      texts = e.texts || [e.text],
      cx = (e.x ?? 0.5) * W;
    for (let r = 0; r < Math.floor(H / gap) + 3; r++) {
      const idx = r + Math.floor(Math.floor(v * k) / gap),
        cy = r * gap - ((v * k) % gap),
        m = tmask(texts[idx % texts.length], size),
        w = m.width,
        h = m.height;
      const hot = idx % 3 === 1;
      if (hot) rect(x, cx - w / 2 - 16, cy - h / 2 - 9, cx + w / 2 + 16, cy + h / 2 + 9, RED);
      paste(x, m, cx - w / 2, cy - h / 2, WHITE, hot ? 1 : 0.38);
    }
  };
  EVH.frame = (x, e, k, _n) => {
    // viewfinder brackets, blinking dot, timecode, label
    const ins = 48,
      L = 84,
      th = 4,
      c = x.x;
    c.strokeStyle = "#fff";
    c.lineWidth = th;
    c.lineCap = "butt";
    for (const [cx, cy, sx, sy] of [
      [ins, ins, 1, 1],
      [W - ins, ins, -1, 1],
      [ins, H - ins, 1, -1],
      [W - ins, H - ins, -1, -1],
    ]) {
      c.beginPath();
      c.moveTo(cx, cy);
      c.lineTo(cx + sx * L, cy);
      c.moveTo(cx, cy);
      c.lineTo(cx, cy + sy * L);
      c.stroke();
    }
    if (Math.floor(k / 6) % 2 === 0) {
      c.fillStyle = css(e.dot || RED);
      c.beginPath();
      c.arc(ins + 34, ins + 44, 11, 0, 2 * Math.PI);
      c.fill();
    }
    if (e.notext) return;
    const g = e.f0 + k,
      tc = `00:00:${String(Math.floor(g / 24)).padStart(2, "0")}:${String(g % 24).padStart(2, "0")}`;
    paste(x, tmask(tc, 30), ins + 58, ins + 30, WHITE, 0.92);
    if (e.label) {
      const m = tmask(e.label, 30);
      paste(x, m, W - ins - 24 - m.width, ins + 30, WHITE, 0.92);
    }
  };
  EVH.counter = (x, e, k, _n) => {
    const m = tmask(
      `${e.label ?? "REC"} ${String(Math.floor((e.n0 ?? 1) + k * (e.rate ?? 13))).padStart(5, "0")}`,
      e.size || 30,
    );
    x.x.fillStyle = css(e.dot || RED);
    x.x.beginPath();
    x.x.arc(W - 92 - m.width, H - 76, 9, 0, 2 * Math.PI);
    x.x.fill();
    paste(x, m, W - 70 - m.width, H - 92, WHITE, 0.95);
  };
  EVH.leak = (x, e, k, n) => {
    // light leak drifting across (screen blend of a gaussian blob)
    const u = k / Math.max(n - 1, 1),
      x0 = e.x0 ?? -0.2,
      x1 = e.x1 ?? 1.2,
      cx = (x0 + (x1 - x0) * u) * W,
      cy = (e.y ?? 0.3) * H;
    const amt = (e.amt ?? 0.5) * (0.85 + 0.15 * Math.sin(k * 0.9)),
      col = e.color || [1, 0.22, 0.08];
    const c = x.x;
    c.save();
    c.globalCompositeOperation = "screen";
    c.translate(cx, cy);
    c.scale(0.42 * W, 0.55 * H);
    const gr = c.createRadialGradient(0, 0, 0, 0, 0, 3);
    for (let i = 0; i <= 24; i++) {
      const r = i / 8,
        gv = Math.exp(-r * r) * amt;
      gr.addColorStop(
        r / 3,
        `rgb(${clamp(gv * col[0]) * 255},${clamp(gv * col[1]) * 255},${clamp(gv * col[2]) * 255})`,
      );
    }
    c.fillStyle = gr;
    c.fillRect(-3, -3, 6, 6);
    c.restore();
  };
  EVH.slices = (x, e, k, n) => {
    // frame cut into bands that slide into place
    const nb = e.bands || 6,
      amp = (e.amp ?? 0.4) * W,
      u = Math.max(0, 1 - k / Math.max(n - 1, 1)) ** 3;
    if (u <= 0) return;
    const src = copyOf(x),
      hb = Math.floor(H / nb);
    x.x.fillStyle = "#000";
    x.x.fillRect(0, 0, W, H);
    for (let i = 0; i < nb; i++) {
      const d = Math.round((i % 2 === 0 ? 1 : -1) * amp * u),
        y0 = i * hb,
        y1 = i === nb - 1 ? H : (i + 1) * hb;
      x.x.drawImage(src, 0, y0, W, y1 - y0, d, y0, W, y1 - y0);
    }
  };
  EVH.wipe = (x, e, k, n) => {
    const bw = 0.35 * W,
      x0 = -bw + ((W + bw) * (k + 1)) / n;
    rect(x, x0, 0, x0 + bw, H, e.color || RED);
  };
  EVH.shake = (x, e, k, n) => {
    // decaying camera shake (reflect border approximated by a 1 % overscan)
    const a = (e.amp ?? 18) * (1 - k / n) ** 1.5,
      r = rng(e.f0 * 7 + k),
      dx = runi(r, -1, 1) * a,
      dy = runi(r, -1, 1) * a;
    const src = copyOf(x),
      s = 1 + (2 * (Math.abs(dx) + Math.abs(dy))) / Math.min(W, H);
    x.x.save();
    x.x.translate(W / 2 + dx, H / 2 + dy);
    x.x.scale(s, s);
    x.x.drawImage(src, -W / 2, -H / 2);
    x.x.restore();
  };
  EVH.kinetic = (x, e, k, _n) => {
    // words slide in from alternating sides and stack
    for (const [text, size, yf, frm, at, box] of e.lines) {
      if (k < at) continue;
      const ease = 1 - (1 - Math.min(1, (k - at) / 5)) ** 3,
        m = tmask(text, size),
        w = m.width,
        h = m.height;
      let cx = W / 2,
        cy = yf * H;
      if (frm === "L") cx = -w / 2 + (W / 2 + w / 2) * ease;
      else if (frm === "R") cx = W + w / 2 - (W / 2 + w / 2) * ease;
      else if (frm === "B") cy = H + h + (yf * H - H - h) * ease;
      if (box) rect(x, cx - w / 2 - 26, cy - h / 2 - 16, cx + w / 2 + 26, cy + h / 2 + 16, box);
      else shadowPaste(x, m, cx, cy, 0.5);
      paste(x, m, cx - w / 2, cy - h / 2, WHITE);
    }
  };
  EVH.labels = (x, e, k, _n) => {
    // captions at points, pop in at their own frame
    for (const [text, size, cx, cy, at, box] of e.items) {
      if (k < at) continue;
      const m = tmask(text, size),
        sc = 1 + 0.18 * Math.max(0, 1 - (k - at) / 3) ** 2,
        w = m.width * sc,
        h = m.height * sc;
      if (box) rect(x, cx - w / 2 - 22, cy - h / 2 - 13, cx + w / 2 + 22, cy + h / 2 + 13, box);
      else paste(x, m, cx - w / 2 + 3, cy - h / 2 + 5, BLACK, 0.5, sc, 7);
      paste(x, m, cx - w / 2, cy - h / 2, WHITE, 1, sc);
    }
  };
  EVH.cutouts = async (x, e, k, n) => {
    if (!e._cache) e._cache = await loadPanels(e.panels, n);
    drawPanels(x, e.panels, e._cache, k);
  };

  // ------------------------------------------------------------------ panels (collages, cut-outs)
  async function loadPanels(panels, n) {
    const out = [];
    for (const p of panels) {
      const cnt = Math.max(1, Math.floor((n - (p.at || 0)) * (p.rate ?? 1)) + 1),
        k0 = startFrame(p),
        fr = [];
      for (let j = 0; j < cnt; j++) fr.push(await load(p.src, k0 + j));
      out.push({ fr, lohi: await levels(p.src, k0 + (cnt >> 1)) });
    }
    return out;
  }
  function panelImg(p, im, lohi) {
    const [, , w, h] = p.rect,
      sw = im.width,
      sh = im.height,
      s = (p.z ?? 1) * Math.max(w / sw, h / sh),
      hw = w / 2 / s,
      hh = h / 2 / s;
    const cx = clamp(p.cx ?? sw / 2, hw, sw - hw),
      cy = clamp(p.cy ?? sh / 2, hh, sh - hh),
      c = mk(w, h);
    c.x.drawImage(im, cx - hw, cy - hh, 2 * hw, 2 * hh, 0, 0, w, h);
    return grade(c, p.g || "bw", lohi[0], lohi[1], 1, p.pop || "warm");
  }
  function place(x, im, X, Y, border = 0, rot = 0, shadow = false, flash = 0) {
    let c = im;
    if (flash) {
      c = copyOf(im);
      c.x.globalAlpha = flash;
      c.x.fillStyle = "#fff";
      c.x.fillRect(0, 0, c.width, c.height);
      c.x.globalAlpha = 1;
    }
    if (border) {
      const b = mk(c.width + 2 * border, c.height + 2 * border);
      b.x.fillStyle = css([0.96, 0.96, 0.94]);
      b.x.fillRect(0, 0, b.width, b.height);
      b.x.drawImage(c, border, border);
      c = b;
    }
    let w = c.width,
      h = c.height,
      nw = w,
      nh = h;
    if (rot) {
      const a = (rot * Math.PI) / 180,
        co = Math.abs(Math.cos(a)),
        si = Math.abs(Math.sin(a));
      nw = Math.floor(h * si + w * co) + 2;
      nh = Math.floor(h * co + w * si) + 2;
    }
    X = Math.round(X);
    Y = Math.round(Y);
    if (shadow) {
      // blurred alpha, offset (+8, +12), 60 % black
      x.x.save();
      x.x.filter = "blur(10px)";
      x.x.globalAlpha = 0.6;
      x.x.translate(X + 8 + nw / 2, Y + 12 + nh / 2);
      x.x.rotate((-(rot || 0) * Math.PI) / 180);
      x.x.fillStyle = "#000";
      x.x.fillRect(-w / 2, -h / 2, w, h);
      x.x.restore();
    }
    x.x.save();
    x.x.translate(X + nw / 2, Y + nh / 2);
    x.x.rotate((-(rot || 0) * Math.PI) / 180);
    x.x.drawImage(c, -w / 2, -h / 2);
    x.x.restore();
  }
  function drawPanels(x, panels, cache, k) {
    panels.forEach((p, i) => {
      const at = p.at || 0;
      if (k < at) return;
      const { fr, lohi } = cache[i],
        j = Math.min(fr.length - 1, Math.floor((k - at) * (p.rate ?? 1)));
      place(
        x,
        panelImg(p, fr[j], lohi),
        p.rect[0],
        p.rect[1],
        p.border || 0,
        p.rot || 0,
        !!p.shadow,
        k === at ? 0.55 : 0,
      );
    });
  }

  // ------------------------------------------------------------------ shots
  function camOf(sw, sh, cx, cy, z) {
    // editlib.xform clamps: never show outside the source
    z = Math.max(z, W / sw, H / sh);
    const hw = W / 2 / z,
      hh = H / 2 / z;
    return { z, cx: clamp(cx ?? sw / 2, hw, sw - hw), cy: clamp(cy ?? sh / 2, hh, sh - hh) };
  }
  function xform(im, cx, cy, z, out) {
    const t = camOf(im.width, im.height, cx, cy, z),
      c = out || mk(W, H);
    c.x.setTransform(t.z, 0, 0, t.z, W / 2 - t.z * t.cx, H / 2 - t.z * t.cy);
    c.x.drawImage(im, 0, 0);
    c.x.setTransform(1, 0, 0, 1, 0, 0);
    c.cam = t;
    return c;
  }
  function glitch(c, seed) {
    // vertical slit glitch
    const r = rng(seed),
      src = copyOf(c),
      n = rint(r, 5, 10);
    c.x.imageSmoothingEnabled = false;
    for (let i = 0; i < n; i++) {
      const w = rint(r, 16, 130),
        x0 = rint(r, 0, W - w),
        sx = clamp(x0 + rint(r, -160, 160), 0, W - w);
      if (r() < 0.45) c.x.drawImage(src, sx, 0, 1, H, x0, 0, w, H);
      else c.x.drawImage(src, sx, 0, w, H, x0, 0, w, H);
    }
    c.x.imageSmoothingEnabled = true;
    return c;
  }
  function rgbSplit(c, d) {
    const id = c.x.getImageData(0, 0, W, H),
      s = new Uint8ClampedArray(id.data),
      o = id.data;
    for (let y = 0; y < H; y++) {
      const row = y * W;
      for (let x = 0; x < W; x++) {
        const i = (row + x) * 4;
        o[i] = s[(row + ((x + d + W) % W)) * 4];
        o[i + 2] = s[(row + ((x - d + W * 2) % W)) * 4 + 2];
      }
    }
    c.x.putImageData(id, 0, 0);
  }
  function scan(c) {
    c.x.globalAlpha = 0.14;
    c.x.fillStyle = "#000";
    for (let y = 0; y < H; y += 4) c.x.fillRect(0, y, W, 2);
    c.x.globalAlpha = 1;
  }

  class Shot {
    constructor(sh) {
      this.sh = sh;
      this.n = sh.f1 - sh.f0;
    }
    async init() {
      const sh = this.sh;
      if (sh.collage) this.cache = await loadPanels(sh.collage, this.n);
      else if (sh.src) {
        this.k0 = startFrame(sh);
        this.lohi = sh.lv || (await levels(sh.src, this.k0 + (this.n >> 1)));
      }
      if (sh.dbl) {
        this.dk0 = startFrame(sh.dbl);
        this.dlohi = await levels(sh.dbl.src, this.dk0 + (this.n >> 1));
      }
      return this;
    }
    async pre(i) {
      // fx.shot_pre
      const sh = this.sh,
        n = this.n;
      let z = sh.z0 + ((sh.z1 - sh.z0) * i) / Math.max(n - 1, 1);
      if (sh.punch) z *= 1 + sh.punch * Math.max(0, 1 - i / 5) ** 2;
      const im = await load(sh.src, this.k0 + i),
        x = xform(im, sh.cx, sh.cy, z);
      if (sh.mir) {
        const t = copyOf(x);
        x.x.setTransform(-1, 0, 0, 1, W, 0);
        x.x.drawImage(t, 0, 0);
        x.x.setTransform(1, 0, 0, 1, 0, 0);
      }
      grade(x, sh.g || "bw", this.lohi[0], this.lohi[1], sh.gamma ?? 1, sh.pop || "warm");
      if (sh.eyes) eyeGlow(x, sh.eyes, i, sh, x.cam);
      if (sh.neg) {
        x.x.globalCompositeOperation = "difference";
        x.x.fillStyle = "#fff";
        x.x.fillRect(0, 0, W, H);
        x.x.globalCompositeOperation = "source-over";
      }
      if ((sh.glitch || []).includes(i)) glitch(x, sh.f0 * 31 + i);
      let a = 1;
      const fi = sh.fi || 0,
        fo = sh.fo || 0;
      if (fi && i < fi) a = Math.min(a, (i + 1) / (fi + 1));
      if (fo && i >= n - fo) a = Math.min(a, (n - i) / (fo + 1));
      const fl = sh.flash || [];
      return [x, i < fl.length ? fl[i] : 0, a];
    }
    async frame(i, g) {
      // fx.Shot.frame
      const sh = this.sh;
      let x,
        fl = 0,
        a = 1;
      if (sh.solid !== undefined) {
        x = mk(W, H);
        x.x.fillStyle = css([sh.solid, sh.solid, sh.solid]);
        x.x.fillRect(0, 0, W, H);
      } else if (sh.collage) {
        x = mk(W, H);
        const b = sh.bg ?? 0;
        x.x.fillStyle = css(Array.isArray(b) ? b : [b, b, b]);
        x.x.fillRect(0, 0, W, H);
        drawPanels(x, sh.collage, this.cache, i);
      } else if (sh.knock) {
        let foot;
        [foot, fl, a] = await this.pre(i);
        const sc = 1 + 0.2 * Math.max(0, 1 - i / Math.max(this.n - 1, 1)) ** 2,
          m = knockMask(sh.knock.lines);
        const t = copyOf(foot);
        t.x.globalCompositeOperation = "destination-in";
        t.x.setTransform(sc, 0, 0, sc, (W / 2) * (1 - sc), (H / 2) * (1 - sc));
        t.x.drawImage(m, 0, 0);
        x = mk(W, H);
        const b = sh.knock.bg || BLACK;
        x.x.fillStyle = css(Array.isArray(b) ? b : [b, b, b]);
        x.x.fillRect(0, 0, W, H);
        x.x.drawImage(t, 0, 0);
      } else {
        [x, fl, a] = await this.pre(i);
        if (sh.echo) {
          // trail from frames -3 and -6
          const [x3] = await this.pre(Math.max(0, i - 3)),
            [x6] = await this.pre(Math.max(0, i - 6));
          const A = x.x.getImageData(0, 0, W, H),
            B = x3.x.getImageData(0, 0, W, H).data,
            C = x6.x.getImageData(0, 0, W, H).data,
            d = A.data;
          for (let j = 0; j < d.length; j++) {
            if ((j & 3) === 3) continue;
            const v = d[j],
              m = 0.62 * v + 0.24 * B[j] + 0.14 * C[j] + 0.1 * Math.max(B[j], C[j]);
            d[j] = Math.max(v, m);
          }
          x.x.putImageData(A, 0, 0);
        }
      }
      if (sh.dbl) {
        // double exposure
        const d = sh.dbl,
          u = i / Math.max(this.n - 1, 1),
          z0 = d.z0 ?? 1,
          z = z0 + ((d.z1 ?? z0) - z0) * u;
        const y = grade(
          xform(await load(d.src, this.dk0 + i), d.cx, d.cy, z),
          d.g || "bw",
          this.dlohi[0],
          this.dlohi[1],
          1,
          d.pop || "warm",
        );
        x.x.save();
        if (d.flip) {
          x.x.translate(W, 0);
          x.x.scale(-1, 1);
        }
        if (d.mode === "mix") {
          x.x.globalAlpha = d.amt ?? 0.45;
        } else {
          x.x.globalCompositeOperation = "screen";
          x.x.globalAlpha = d.amt ?? 0.6;
        }
        x.x.drawImage(y, 0, 0);
        x.x.restore();
      }
      const evs = PLAN.ev.filter((e) => e.f0 <= g && g < e.f1);
      for (const e of evs) {
        const h = EVH[e.type];
        if (!h) throw new Error("unknown event " + e.type);
        await h(x, e, g - e.f0, e.f1 - e.f0);
      }
      if (PLAN.rgb && PLAN.rgb[g]) rgbSplit(x, PLAN.rgb[g]);
      if ((PLAN.scan || []).some(([a0, a1]) => a0 <= g && g < a1)) scan(x);
      if (sh.solid === 0 && !evs.length) return x; // pure black: no grain / vignette
      return post(x, fl, a, g);
    }
  }
  const KB = new Map();
  function knockMask(lines) {
    const key = JSON.stringify(lines);
    if (KB.has(key)) return KB.get(key);
    const c = mk(W, H, false),
      gap = 26;
    c.x.fillStyle = "#fff";
    const ms = lines.map(([t, sz]) => {
      c.x.font = `bold ${sz}px ${FONT}`;
      const m = c.x.measureText(t);
      return { t, sz, m, h: m.actualBoundingBoxAscent + m.actualBoundingBoxDescent };
    });
    let y = (H - ms.reduce((s, q) => s + q.h, 0) - gap * (ms.length - 1)) / 2;
    for (const q of ms) {
      c.x.font = `bold ${q.sz}px ${FONT}`;
      const iw = q.m.actualBoundingBoxLeft + q.m.actualBoundingBoxRight;
      c.x.fillText(q.t, (W - iw) / 2 + q.m.actualBoundingBoxLeft, y + q.m.actualBoundingBoxAscent);
      y += q.h + gap;
    }
    KB.set(key, c);
    return c;
  }
  // synthetic glowing eyes for footage without them: warm glow at tracked eye centres in source px
  // (sh.eyes = per shot frame [[x, y, r], ..], empty where no eyes were found); sh.eyecol overrides the colour
  function eyeGlow(x, eyes, i, sh, cam) {
    const pts = eyes[Math.min(i, eyes.length - 1)] || [];
    if (!pts.length) return;
    const c = x.x,
      col = sh.eyecol || [1, 0.32, 0.08],
      m = sh.mir ? -1 : 1;
    for (const [ex, ey, er] of pts) {
      if (![ex, ey, er].every(Number.isFinite)) continue;
      const X = W / 2 + m * (ex - cam.cx) * cam.z,
        Y = H / 2 + (ey - cam.cy) * cam.z,
        R = Math.max(2, er * cam.z);
      c.save();
      c.globalCompositeOperation = "screen";
      for (const [rr, a, cc] of [
        [R * 2.2, 0.28, col],
        [R, 0.9, col],
        [R * 0.45, 0.95, [1, 0.75, 0.45]],
      ]) {
        const gr = c.createRadialGradient(X, Y, 0, X, Y, rr);
        gr.addColorStop(0, css(cc, a));
        gr.addColorStop(0.55, css(cc, a * 0.6));
        gr.addColorStop(1, css(cc, 0));
        c.fillStyle = gr;
        c.fillRect(X - rr, Y - rr, 2 * rr, 2 * rr);
      }
      c.restore();
    }
  }

  // ------------------------------------------------------------------ driver
  function check(plan) {
    let f = 0;
    for (const sh of plan.shots) {
      if (sh.f0 !== f || !(sh.f1 > sh.f0))
        throw new Error(`gap/overlap at ${sh.id} ${sh.f0} expected ${f}`);
      f = sh.f1;
    }
    return f;
  }
  function setPlan(p) {
    PLAN = p;
    W = p.w || 1440;
    H = p.h || 1080;
    FPS = p.fps || 24;
    p.ev = p.ev || [];
    p.nf = check(p);
    for (const sh of p.shots) {
      // defaults like editlib.SH
      if (sh.z0 === undefined) sh.z0 = 1;
      if (sh.z1 === undefined) sh.z1 = sh.z0;
      if (sh.src) {
        const i = srcInfo(sh.src);
        if (sh.cx === undefined) sh.cx = i.w / 2;
        if (sh.cy === undefined) sh.cy = i.h / 2;
      }
    }
    initPost();
  }
  const SHOTS = new Map();
  async function renderFrame(g) {
    const sh = PLAN.shots.find((s) => s.f0 <= g && g < s.f1);
    if (!sh) throw new Error("no shot at frame " + g);
    let s = SHOTS.get(sh.id);
    if (!s) {
      s = await new Shot(sh).init();
      SHOTS.set(sh.id, s);
      if (SHOTS.size > 6) SHOTS.delete(SHOTS.keys().next().value);
    }
    return s.frame(g - sh.f0, g);
  }
  return {
    setPlan,
    renderFrame,
    mk,
    tmask,
    get W() {
      return W;
    },
    get H() {
      return H;
    },
    get plan() {
      return PLAN;
    },
  };
})();
