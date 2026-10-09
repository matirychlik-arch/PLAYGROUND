// fx.js - the physical body edit engine (the Huntress overlay edit): a canvas port of edkit.lib (the numpy renderer of the original edit).
// plan.json (scripts/edit.py) = the template timeline with every footage item resolved to a crop of the user's clip:
//   crops{slot: {dir, sf, n, box: [x, y, w, h] (source px), ew, eh}}   frames cut by ffmpeg, crops/<slot>/NNNNN.jpg
//   items{id: {slot, f0, n, k0, speed, aspect, c0: [cx, cy, z], c1, look, expo, sharp}}  z = 1 is the 16:9 cover crop
//   segs[{f0, f1, base, layers, fx, trk}], caps[[f0, f1, word]], tracks{id: {f0, pts}}, sil{hint}
// Every output frame is a pure function of the plan, so any frame range renders in any Chrome instance.
"use strict";
globalThis.FX = (() => {
  let W = 1920,
    H = 1080,
    SC = 1,
    PLAN = null;
  const FONT = '"Liberation Sans", Arial, Helvetica, sans-serif';
  const clamp = (v, a = 0, b = 1) => (v < a ? a : v > b ? b : v);
  const smooth = (p) => {
    p = clamp(p);
    return p * p * (3 - 2 * p);
  };
  const pad = (n) => String(n).padStart(5, "0");
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
  function filled(v, w = W, h = H) {
    const c = mk(w, h);
    const g = Math.round(clamp(v) * 255);
    c.x.fillStyle = `rgb(${g},${g},${g})`;
    c.x.fillRect(0, 0, w, h);
    return c;
  }
  function rng(seed) {
    // mulberry32
    let a = seed >>> 0 || 1;
    return () => {
      a |= 0;
      a = (a + 0x6d2b79f5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  const runi = (r, a, b) => a + r() * (b - a);
  const rint = (r, a, b) => a + Math.floor(r() * (b - a)); // [a, b)
  const luma = (r, g, b) => 0.2126 * r + 0.7152 * g + 0.0722 * b;
  const scurve = (L, k) => clamp(L + k * (L - 0.5) * (1 - Math.abs(2 * L - 1)));

  // ------------------------------------------------------------------ sources (per-slot crops)
  const IMG = new Map();
  function load(url) {
    let p = IMG.get(url);
    if (!p) {
      p = new Promise((res, rej) => {
        const im = new Image();
        im.onload = () => res(im);
        im.onerror = () => rej(new Error("cannot load " + url));
        im.src = url;
      });
      IMG.set(url, p);
      if (IMG.size > 40) IMG.delete(IMG.keys().next().value);
    }
    return p;
  }
  function cropRect(cx, cy, z, aspect) {
    // = edit.py crop_rect
    const SW = PLAN.src.w,
      SH = PLAN.src.h,
      hfull = Math.min(SH, SW / (W / H));
    let ch = hfull / Math.max(z, 1e-3),
      cw = ch * aspect;
    if (cw > SW) {
      cw = SW;
      ch = cw / aspect;
    }
    if (ch > SH) {
      ch = SH;
      cw = ch * aspect;
    }
    return [clamp(cx - cw / 2, 0, SW - cw), clamp(cy - ch / 2, 0, SH - ch), cw, ch];
  }
  function camAt(it, k) {
    const u = smooth(k / Math.max(1, it.n - 1)),
      a = it.c0,
      b = it.c1;
    return [a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u, a[2] + (b[2] - a[2]) * u];
  }
  function srcIndex(it, k) {
    const cr = PLAN.crops[it.slot];
    return clamp(it.k0 + Math.round(Math.max(0, k) * (it.speed || 1)), 0, cr.n - 1);
  }
  async function raw(id, k, dw, dh) {
    // ungraded crop of item `id` at item frame k, drawn at dw x dh
    const it = PLAN.items[id],
      cr = PLAN.crops[it.slot];
    k = clamp(k, 0, it.n - 1);
    const [cx, cy, z] = camAt(it, k),
      r = cropRect(cx, cy, z, it.aspect);
    const im = await load(`${cr.dir}/${pad(srcIndex(it, k))}.jpg`),
      ex = cr.ew / cr.box[2],
      ey = cr.eh / cr.box[3];
    const c = mk(dw, dh);
    c.x.drawImage(
      im,
      (r[0] - cr.box[0]) * ex,
      (r[1] - cr.box[1]) * ey,
      r[2] * ex,
      r[3] * ey,
      0,
      0,
      dw,
      dh,
    );
    c.crop = r;
    return c;
  }

  // ------------------------------------------------------------------ tone & looks (edkit tone_params / look)
  const TONE = new Map();
  async function tone(id) {
    if (TONE.has(id)) return TONE.get(id);
    const it = PLAN.items[id];
    let t = it.tone;
    if (!t) {
      const s = await raw(id, it.n >> 1, 320, Math.max(2, Math.round((320 / it.aspect) | 0))),
        d = s.x.getImageData(0, 0, s.width, s.height).data,
        hist = new Uint32Array(1024);
      for (let i = 0; i < d.length; i += 4)
        hist[Math.min(1023, Math.floor((luma(d[i], d[i + 1], d[i + 2]) / 255) * 1023.999))]++;
      const N = d.length / 4,
        pct = (q) => {
          const tg = (q / 100) * (N - 1);
          let a = 0;
          for (let b = 0; b < 1024; b++) {
            a += hist[b];
            if (a > tg) return (b + 0.5) / 1024;
          }
          return 1;
        };
      const p98 = pct(98.5),
        p50 = pct(50),
        g = clamp(0.92 / Math.max(p98, 1e-3), 0.85, 2.2),
        m = p50 * g;
      let gam = 1;
      if (m < 0.24) gam = Math.max(0.62, Math.log(0.24) / Math.log(Math.max(m, 1e-3)));
      else if (m > 0.44) gam = Math.min(1.35, Math.log(0.44) / Math.log(m));
      t = [g, gam];
    }
    t = [t[0] * (it.expo ?? 1), t[1]];
    TONE.set(id, t);
    return t;
  }
  const BW = { bw_hard: [0.04, 0.9, 0.55], bw_soft: [0.02, 0.95, 0.25], bw: [0.03, 0.93, 0.4] };
  function grade(c, look, g, gam, sharp) {
    const w = c.width,
      h = c.height,
      id = c.x.getImageData(0, 0, w, h),
      d = id.data,
      gs = g / 255,
      bw = BW[look];
    const GAM = new Float32Array(1025);
    if (Math.abs(gam - 1) > 1e-3)
      for (let i = 0; i <= 1024; i++) GAM[i] = Math.pow(Math.max(i / 1024, 1e-4), gam);
    for (let i = 0; i < d.length; i += 4) {
      let r = Math.min(1, d[i] * gs),
        gg = Math.min(1, d[i + 1] * gs),
        b = Math.min(1, d[i + 2] * gs);
      if (Math.abs(gam - 1) > 1e-3) {
        const L = Math.max(luma(r, gg, b), 1e-4),
          f = GAM[Math.min(1024, Math.round(L * 1024))] / L;
        r = Math.min(1, r * f);
        gg = Math.min(1, gg * f);
        b = Math.min(1, b * f);
      }
      const L = luma(r, gg, b);
      if (bw) {
        const L2 = scurve(clamp((L - bw[0]) / bw[1]), bw[2]),
          t = (1 - L2) * L2;
        d[i] = (L2 - 0.01 * t) * 255;
        d[i + 1] = (L2 + 0.004 * t) * 255;
        d[i + 2] = (L2 + 0.018 * t) * 255;
        continue;
      }
      let s = 1.06,
        k = 0.2;
      if (look === "teal") {
        const sh = clamp(1 - L / 0.45),
          hi = clamp((L - 0.55) / 0.45);
        r += -0.02 * sh + 0.025 * hi;
        gg += 0.018 * sh;
        b += 0.035 * sh - 0.02 * hi;
        s = 1.08;
        k = 0.22;
      } else if (look === "warm") {
        const sh = clamp(1 - L / 0.45),
          hi = clamp((L - 0.5) / 0.5);
        r += -0.01 * sh + 0.04 * hi;
        gg += 0.01 * sh + 0.005 * hi;
        b += 0.025 * sh - 0.035 * hi;
        s = 1.1;
        k = 0.25;
      } else if (look === "violet") {
        const sh = clamp(1 - L / 0.5);
        r += 0.035 * sh;
        gg -= 0.01 * sh;
        b += 0.06 * sh;
        s = 1.12;
        k = 0.25;
      } else if (look === "none") {
        d[i] = r * 255;
        d[i + 1] = gg * 255;
        d[i + 2] = b * 255;
        continue;
      }
      const Ls = luma(r, gg, b);
      r = clamp(Ls + (r - Ls) * s);
      gg = clamp(Ls + (gg - Ls) * s);
      b = clamp(Ls + (b - Ls) * s);
      const Ly = luma(r, gg, b),
        f = (scurve(Ly, k) + 1e-4) / (Ly + 1e-4);
      d[i] = r * f * 255;
      d[i + 1] = gg * f * 255;
      d[i + 2] = b * f * 255;
    }
    c.x.putImageData(id, 0, 0);
    if (sharp) {
      // unsharp mask, sigma 1
      const bl = mk(w, h);
      bl.x.filter = "blur(1px)";
      bl.x.drawImage(c, 0, 0);
      const bd = bl.x.getImageData(0, 0, w, h).data,
        o = c.x.getImageData(0, 0, w, h),
        od = o.data;
      for (let i = 0; i < od.length; i++)
        if ((i & 3) !== 3) od[i] = od[i] + sharp * (od[i] - bd[i]);
      c.x.putImageData(o, 0, 0);
    }
    return c;
  }
  const GC = new Map();
  async function img(id, k, dw = W, dh = H) {
    // graded picture of item `id` at item frame k (small LRU: echo taps reuse earlier frames)
    const it = PLAN.items[id];
    k = clamp(k, 0, it.n - 1);
    const key = `${id}|${srcIndex(it, k)}|${k}|${Math.round(dw)}x${Math.round(dh)}`;
    if (GC.has(key)) return GC.get(key);
    const [g, gam] = await tone(id),
      c = grade(await raw(id, k, dw, dh), it.look || "color", g, gam, it.sharp ?? 0.35);
    c.crop = cropRect(...camAt(it, k), it.aspect);
    GC.set(key, c);
    if (GC.size > 10) GC.delete(GC.keys().next().value);
    return c;
  }

  // ------------------------------------------------------------------ effects
  function pixels(c) {
    return c.x.getImageData(0, 0, c.width, c.height);
  }
  function blurred(c, sigma) {
    const o = mk(c.width, c.height);
    o.x.fillStyle = "#000";
    o.x.fillRect(0, 0, o.width, o.height);
    o.x.filter = `blur(${sigma}px)`;
    o.x.drawImage(c, 0, 0);
    o.x.filter = "none";
    return o;
  }
  function addLight(x, src, amt) {
    // x += amt * src (additive, clamped)
    x.x.save();
    x.x.globalCompositeOperation = "lighter";
    while (amt > 1e-3) {
      x.x.globalAlpha = Math.min(1, amt);
      x.x.drawImage(src, 0, 0);
      amt -= 1;
    }
    x.x.restore();
  }
  function bloom(x, thr = 0.6, amt = 0.8, s1 = 12, s2 = 40) {
    const hl = mk(x.width, x.height),
      id = pixels(x),
      d = id.data,
      t = thr * 255;
    for (let i = 0; i < d.length; i += 4) {
      d[i] = Math.max(0, d[i] - t);
      d[i + 1] = Math.max(0, d[i + 1] - t);
      d[i + 2] = Math.max(0, d[i + 2] - t);
      d[i + 3] = 255;
    }
    hl.x.putImageData(id, 0, 0);
    addLight(x, blurred(hl, s1 * SC), amt);
    addLight(x, blurred(hl, s2 * SC), 0.7 * amt);
    return x;
  }
  function burst(x, a) {
    const id = pixels(x),
      d = id.data,
      m = 1 + 1.6 * a,
      o = 0.1 * a * 255;
    for (let i = 0; i < d.length; i += 4) {
      d[i] = d[i] * m + o;
      d[i + 1] = d[i + 1] * m + o;
      d[i + 2] = d[i + 2] * m + o;
    }
    x.x.putImageData(id, 0, 0);
    return bloom(x, 0.55 - 0.25 * a, 1.6 * a + 0.2, 16, 60);
  }
  function zoomBlur(x, strength, cx = 0.5, cy = 0.5, steps = 10) {
    if (strength <= 1e-3) return x;
    const src = copyOf(x);
    for (let i = 1; i < steps; i++) {
      const s = 1 + (strength * i) / (steps - 1);
      x.x.save();
      x.x.globalAlpha = 1 / (i + 1);
      x.x.translate(cx * W, cy * H);
      x.x.scale(s, s);
      x.x.drawImage(src, -cx * W, -cy * H);
      x.x.restore();
    }
    return x;
  }
  function motionBlur(x, length) {
    const L = Math.max(1, length * SC),
      taps = Math.min(24, Math.max(2, Math.round(L / 3))),
      src = copyOf(x);
    for (let i = 1; i < taps; i++) {
      const dx = -L / 2 + (L * i) / (taps - 1);
      x.x.globalAlpha = 1 / (i + 1);
      x.x.drawImage(src, dx, 0);
    }
    x.x.globalAlpha = 1;
    return x;
  }
  function highlightKeep(x, p, dim = 1) {
    const id = pixels(x),
      d = id.data,
      thr = 0.45 + 0.45 * p,
      ex = 1 + 1.5 * p,
      base = (1 - p) * 0.6 * (1 - p);
    for (let i = 0; i < d.length; i += 4) {
      const L = luma(d[i], d[i + 1], d[i + 2]) / 255,
        m = Math.pow(clamp((L - thr) / (1 - thr + 1e-3)), ex),
        f = (m + base * (1 - m)) * dim;
      d[i] *= f;
      d[i + 1] *= f;
      d[i + 2] *= f;
    }
    x.x.putImageData(id, 0, 0);
    return x;
  }
  function rgbSplit(x, dx) {
    const d0 = Math.round(dx * SC),
      id = pixels(x),
      s = new Uint8ClampedArray(id.data),
      o = id.data;
    for (let y = 0; y < H; y++) {
      const row = y * W;
      for (let xx = 0; xx < W; xx++) {
        const i = (row + xx) * 4;
        o[i] = s[(row + ((xx - d0 + W) % W)) * 4];
        o[i + 2] = s[(row + ((xx + d0) % W)) * 4 + 2];
      }
    }
    x.x.putImageData(id, 0, 0);
  }
  function screenOn(x, layer, alpha = 1) {
    x.x.save();
    x.x.globalCompositeOperation = "screen";
    x.x.globalAlpha = alpha;
    x.x.drawImage(layer, 0, 0);
    x.x.restore();
  }
  function glitch(x, seed, amt = 1) {
    const r = rng(seed);
    rgbSplit(x, 10 * amt + runi(r, 0, 8));
    const src = copyOf(x);
    for (let i = 0; i < Math.floor(6 * amt); i++) {
      const h = rint(r, Math.max(2, (H / 60) | 0), Math.max(4, (H / 14) | 0)),
        y0 = rint(r, 0, H - h),
        sh = rint(r, -((W / 12) | 0), (W / 12) | 0);
      x.x.drawImage(src, 0, y0, W, h, sh, y0, W, h);
      x.x.drawImage(src, 0, y0, W, h, sh - Math.sign(sh) * W, y0, W, h);
    }
    const st = mk(W, H);
    st.x.fillStyle = "#000";
    st.x.fillRect(0, 0, W, H);
    const th = Math.max(1, (H / 540) | 0);
    for (let i = 0; i < Math.floor(140 * amt); i++) {
      const yy = rint(r, 0, H),
        xx = rint(r, 0, W),
        ln = rint(r, (W / 80) | 0, (W / 20) | 0),
        v = runi(r, 0.4, 1) * 0.8;
      st.x.fillStyle = `rgb(${255 * v},${0.9 * 255 * v},${0.85 * 255 * v})`;
      st.x.fillRect(xx, yy, ln, th);
    }
    screenOn(x, st);
    return x;
  }
  function pixelNoise(x, seed, density = 0.012) {
    const r = rng(seed),
      qw = W >> 2,
      qh = H >> 2,
      q = mk(qw, qh),
      id = q.x.createImageData(qw, qh),
      d = id.data,
      k = Math.floor(qw * qh * density),
      tint = runi(r, 0.7, 1);
    for (let i = 3; i < d.length; i += 4) d[i] = 255;
    for (let i = 0; i < k; i++) {
      const p = (rint(r, 0, qh) * qw + rint(r, 0, qw)) * 4,
        v = runi(r, 0.4, 1) * 255;
      d[p] = v;
      d[p + 1] = 0.9 * v;
      d[p + 2] = tint * v;
    }
    q.x.putImageData(id, 0, 0);
    const big = mk(W, H);
    big.x.imageSmoothingEnabled = false;
    big.x.drawImage(q, 0, 0, W, H);
    const L = Math.max(1, Math.round(W / 400)) * 3,
      col = mk(W, H);
    col.x.fillStyle = "#000";
    col.x.fillRect(0, 0, W, H);
    for (let i = 0; i < L; i++) {
      col.x.globalAlpha = 1 / (i + 1);
      col.x.drawImage(big, i - (L >> 1), 0);
    }
    col.x.globalAlpha = 1;
    const base = mk(W, H);
    base.x.fillStyle = "#000";
    base.x.fillRect(0, 0, W, H);
    base.x.globalAlpha = 0.25;
    base.x.drawImage(x, 0, 0);
    base.x.globalAlpha = 1;
    screenOn(base, col);
    x.x.drawImage(base, 0, 0);
    return x;
  }
  function lightLeak(x, a, cx = 0.5) {
    const id = pixels(x),
      d = id.data,
      gx = new Float32Array(W),
      wx = new Float32Array(W);
    for (let xx = 0; xx < W; xx++) {
      const u = xx / W - cx;
      gx[xx] = Math.exp(-((u / 0.07) ** 2));
      wx[xx] = Math.exp(-((u / 0.3) ** 2));
    }
    for (let y = 0; y < H; y++) {
      const ys = y / H,
        gy = 0.55 + 0.45 * Math.exp(-(((ys - 0.62) / 0.35) ** 2));
      for (let xx = 0; xx < W; xx++) {
        const i = (y * W + xx) * 4,
          add = a * (1.15 * gx[xx] * gy + 0.35 * wx[xx] * gy) * 255,
          m = 1 + 0.6 * a;
        d[i] = d[i] * m + add;
        d[i + 1] = d[i + 1] * m + add;
        d[i + 2] = d[i + 2] * m + add;
      }
    }
    x.x.putImageData(id, 0, 0);
    return x;
  }
  function echo(frames, w) {
    const o = copyOf(frames[0]);
    let acc = w[0];
    for (let i = 1; i < frames.length; i++) {
      acc += w[i];
      o.x.globalAlpha = w[i] / acc;
      o.x.drawImage(frames[i], 0, 0);
    }
    o.x.globalAlpha = 1;
    return o;
  }
  function jaggedWipe(a, b, p, seed = 3) {
    // dark smeared `a` on the left gives way to `b` along a zig-zag edge moving right -> left
    const r = rng(seed),
      ph = [
        [0.11, 0.05, runi(r, 0, 1)],
        [0.047, 0.022, runi(r, 0, 1)],
        [0.021, 0.01, runi(r, 0, 1)],
      ];
    const o = mk(W, H);
    o.x.filter = `blur(${3 * SC}px)`;
    o.x.drawImage(b, 0, 0);
    o.x.filter = "none";
    const sm = motionBlur(copyOf(a), 60);
    o.x.save();
    o.x.beginPath();
    o.x.moveTo(0, 0);
    for (let y = 0; y <= H; y += 2) {
      let teeth = 0;
      for (const [per, amp, off] of ph) {
        const t = (y / H / per + off) % 1;
        teeth += amp * (Math.abs(2 * t - 1) - 0.5);
      }
      o.x.lineTo((0.78 - 0.48 * p + 0.1 * (y / H - 0.5) + teeth) * W, y);
    }
    o.x.lineTo(0, H);
    o.x.closePath();
    o.x.clip();
    o.x.fillStyle = "#000";
    o.x.fillRect(0, 0, W, H);
    o.x.globalAlpha = 0.55;
    o.x.drawImage(sm, 0, 0);
    o.x.restore();
    return o;
  }
  function sparkLayer(p, n) {
    const c = mk(W, H);
    c.x.fillStyle = "#000";
    c.x.fillRect(0, 0, W, H);
    c.x.globalCompositeOperation = "lighter";
    c.x.fillStyle = "#fff";
    c.x.strokeStyle = "#fff";
    c.x.lineWidth = Math.max(1, SC);
    const [l0, l1] = p.life,
      reg = p.region || [0, 0, 1, 1];
    for (let b = n - l1 + 1; b <= n; b++) {
      const r = rng(((p.seed * 100003 + b * 7919) & 0x7fffffff) >>> 0);
      for (let i = 0; i < p.rate; i++) {
        const x = runi(r, reg[0], reg[2]),
          y = runi(r, reg[1], reg[3]),
          rad = runi(r, 0.8, 2.6) * p.size,
          I = runi(r, 0.4, 1),
          star = r() < p.star_p,
          life = rint(r, l0, l1 + 1),
          age = n - b;
        if (age >= life) continue;
        const a = I * (0.35 + (0.65 * (life - age)) / life),
          cx = x * W,
          cy = (y - p.rise * age) * H;
        c.x.globalAlpha = a;
        c.x.beginPath();
        c.x.arc(cx, cy, Math.max(0.8, rad * SC), 0, 2 * Math.PI);
        c.x.fill();
        if (star) {
          const L = rad * SC * 7;
          c.x.globalAlpha = a * 0.55;
          c.x.beginPath();
          c.x.moveTo(cx - L, cy);
          c.x.lineTo(cx + L, cy);
          c.x.moveTo(cx, cy - L);
          c.x.lineTo(cx, cy + L);
          c.x.stroke();
        }
      }
    }
    const o = mk(W, H);
    o.x.fillStyle = "#000";
    o.x.fillRect(0, 0, W, H);
    const b1 = blurred(c, 0.9 * SC),
      b2 = blurred(c, 4 * SC);
    addLight(o, b1, 1.7 * p.scale);
    addLight(o, b2, 0.8 * p.scale);
    o.x.globalCompositeOperation = "multiply";
    o.x.fillStyle = `rgb(${p.col.map((v) => Math.round(clamp(v) * 255)).join(",")})`;
    o.x.fillRect(0, 0, W, H);
    o.x.globalCompositeOperation = "source-over";
    return o;
  }
  const SIL = new Map();
  async function silhouette(id, k) {
    // white subject silhouette on black (the matte flash): colour models of the hinted person box vs the border,
    // nearest-centroid labelling, smoothing, largest component
    const key = id + ":" + k;
    if (SIL.has(key)) return SIL.get(key);
    const sw = 240,
      sh = Math.round((sw * H) / W),
      s = await raw(id, k, sw, sh),
      d = s.x.getImageData(0, 0, sw, sh).data,
      N = sw * sh;
    if (PLAN.sil && PLAN.sil.mode === "luma") {
      // no person found: key the brightest quarter of the frame (a graphic matte of the shot)
      const Y = new Float32Array(N);
      for (let p = 0; p < N; p++) Y[p] = luma(d[p * 4], d[p * 4 + 1], d[p * 4 + 2]);
      const thr = Float32Array.from(Y).sort()[Math.floor(N * 0.72)],
        m = mk(sw, sh),
        md = m.x.createImageData(sw, sh);
      for (let p = 0; p < N; p++) {
        const v = Y[p] > thr ? 255 : 0;
        md.data[p * 4] = md.data[p * 4 + 1] = md.data[p * 4 + 2] = v;
        md.data[p * 4 + 3] = 255;
      }
      m.x.putImageData(md, 0, 0);
      const o = mk(W, H);
      o.x.filter = `blur(${2 * SC}px)`;
      o.x.drawImage(m, 0, 0, W, H);
      o.x.filter = "none";
      addLight(o, blurred(o, 18 * SC), 0.35);
      SIL.set(key, o);
      return o;
    }
    const crop = s.crop,
      hb = (PLAN.sil && PLAN.sil.hint) || [0, 0, PLAN.src.w, PLAN.src.h];
    const tx = (v) => ((v - crop[0]) / crop[2]) * sw,
      ty = (v) => ((v - crop[1]) / crop[3]) * sh;
    let bx0 = clamp(tx(hb[0]), 0, sw),
      by0 = clamp(ty(hb[1]), 0, sh),
      bx1 = clamp(tx(hb[2]), 0, sw),
      by1 = clamp(ty(hb[3]), 0, sh);
    if (bx1 - bx0 < 8 || by1 - by0 < 8) {
      bx0 = sw * 0.3;
      bx1 = sw * 0.7;
      by0 = sh * 0.08;
      by1 = sh;
    }
    const cxb = (bx0 + bx1) / 2,
      cyb = (by0 + by1) / 2,
      hw = (bx1 - bx0) / 2,
      hh = (by1 - by0) / 2;
    const col = (p) => [d[p * 4], d[p * 4 + 1], d[p * 4 + 2]];
    const lab = new Int8Array(N); // 1 fg, 0 bg, -1 unknown (inside the expanded box)
    for (let y = 0; y < sh; y++)
      for (let x = 0; x < sw; x++) {
        const u = Math.abs(x - cxb) / hw,
          v = Math.abs(y - cyb) / hh;
        lab[y * sw + x] = u < 0.45 && v < 0.6 ? 1 : u > 1.25 || v > 1.25 ? 0 : -1;
      }
    const kmeans = (pts, k2) => {
      if (!pts.length) return [];
      const r = rng(11);
      let cs = [];
      for (let i = 0; i < k2; i++) cs.push(col(pts[Math.floor(r() * pts.length)]));
      for (let it = 0; it < 6; it++) {
        const acc = cs.map(() => [0, 0, 0, 0]);
        for (const p of pts) {
          const c = col(p);
          let bi = 0,
            bd = 1e18;
          cs.forEach((q, i) => {
            const dd = (c[0] - q[0]) ** 2 + (c[1] - q[1]) ** 2 + (c[2] - q[2]) ** 2;
            if (dd < bd) {
              bd = dd;
              bi = i;
            }
          });
          acc[bi][0] += c[0];
          acc[bi][1] += c[1];
          acc[bi][2] += c[2];
          acc[bi][3]++;
        }
        cs = acc.map((a, i) => (a[3] ? [a[0] / a[3], a[1] / a[3], a[2] / a[3]] : cs[i]));
      }
      return cs;
    };
    const dmin = (c, cs) => {
      let m = 1e18;
      for (const q of cs)
        m = Math.min(m, (c[0] - q[0]) ** 2 + (c[1] - q[1]) ** 2 + (c[2] - q[2]) ** 2);
      return Math.sqrt(m);
    };
    let fgm = new Float32Array(N);
    for (let round = 0; round < 3; round++) {
      const fg = [],
        bg = [];
      for (let p = 0; p < N; p += round ? 1 : 2) {
        const l = round ? (fgm[p] > 0.5 ? 1 : lab[p] === 0 ? 0 : -1) : lab[p];
        if (l === 1) fg.push(p);
        else if (l === 0 || (round && fgm[p] <= 0.5 && lab[p] !== 1)) bg.push(p);
      }
      const cf = kmeans(
          fg.filter((_, i) => i % 3 === 0),
          5,
        ),
        cb = kmeans(
          bg.filter((_, i) => i % 3 === 0),
          6,
        );
      const sc = new Float32Array(N);
      for (let p = 0; p < N; p++) {
        if (lab[p] === 0) {
          sc[p] = 0;
          continue;
        }
        const c = col(p),
          a = dmin(c, cf),
          b = dmin(c, cb);
        sc[p] = lab[p] === 1 ? 0.5 + 0.5 * (b / (a + b + 1e-3)) : b / (a + b + 1e-3);
      }
      // smooth (two 3x3 box passes) -> probability
      for (let pass = 0; pass < 2; pass++) {
        const t = new Float32Array(N);
        for (let y = 1; y < sh - 1; y++)
          for (let x = 1; x < sw - 1; x++) {
            let s2 = 0;
            for (let oy = -1; oy <= 1; oy++)
              for (let ox = -1; ox <= 1; ox++) s2 += sc[(y + oy) * sw + x + ox];
            t[y * sw + x] = s2 / 9;
          }
        sc.set(t);
      }
      fgm = sc;
    }
    // largest connected component of fgm > 0.5
    const seen = new Uint8Array(N),
      keep = new Uint8Array(N);
    let best = [];
    for (let p0 = 0; p0 < N; p0++) {
      if (seen[p0] || fgm[p0] <= 0.5) continue;
      const comp = [p0];
      seen[p0] = 1;
      for (let qi = 0; qi < comp.length; qi++) {
        const p = comp[qi],
          x = p % sw,
          y = (p / sw) | 0;
        for (const [nx, ny] of [
          [x + 1, y],
          [x - 1, y],
          [x, y + 1],
          [x, y - 1],
        ]) {
          if (nx < 0 || ny < 0 || nx >= sw || ny >= sh) continue;
          const q = ny * sw + nx;
          if (!seen[q] && fgm[q] > 0.5) {
            seen[q] = 1;
            comp.push(q);
          }
        }
      }
      if (comp.length > best.length) best = comp;
    }
    for (const p of best) keep[p] = 1;
    const m = mk(sw, sh),
      md = m.x.createImageData(sw, sh);
    for (let p = 0; p < N; p++) {
      const v = keep[p] ? 255 : 0;
      md.data[p * 4] = md.data[p * 4 + 1] = md.data[p * 4 + 2] = v;
      md.data[p * 4 + 3] = 255;
    }
    m.x.putImageData(md, 0, 0);
    const up = mk(W, H);
    up.x.filter = `blur(${1.2 * SC}px)`;
    up.x.drawImage(m, 0, 0, W, H);
    up.x.filter = "none";
    const ud = pixels(up); // re-threshold: closes small gaps, keeps a clean edge
    for (let i = 0; i < ud.data.length; i += 4) {
      const v = clamp((ud.data[i] - 110) / 40) * 255;
      ud.data[i] = ud.data[i + 1] = ud.data[i + 2] = v;
    }
    up.x.putImageData(ud, 0, 0);
    const o = blurred(up, 3 * SC);
    addLight(o, blurred(up, 18 * SC), 0.35);
    SIL.set(key, o);
    return o;
  }
  let VIG = null,
    NOISE = null;
  function initPost() {
    VIG = mk(W, H);
    const id = VIG.x.createImageData(W, H),
      d = id.data;
    for (let y = 0; y < H; y++)
      for (let x = 0; x < W; x++) {
        const v =
            Math.min(
              1,
              Math.sqrt(((x - W / 2) / (W / 2)) ** 2 + ((y - H / 2) / (H / 2)) ** 2) / 1.414,
            ) ** 2,
          i = (y * W + x) * 4;
        d[i] = d[i + 1] = d[i + 2] = (1 - 0.16 * v) * 255;
        d[i + 3] = 255;
      }
    VIG.x.putImageData(id, 0, 0);
    const hw = W >> 1,
      hh = H >> 1,
      r = rng(1000),
      half = new Float32Array(hw * hh);
    for (let i = 0; i < half.length; i += 2) {
      const u = Math.max(1e-9, r()),
        v = r(),
        m = Math.sqrt(-2 * Math.log(u));
      half[i] = m * Math.cos(2 * Math.PI * v);
      if (i + 1 < half.length) half[i + 1] = m * Math.sin(2 * Math.PI * v);
    }
    NOISE = new Float32Array(W * H);
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
        NOISE[y * W + x] = (a * (1 - ty) + b * ty) * 0.016 * 255;
      }
    }
  }
  function finish(x, n) {
    // vignette 0.16 + mid-tone weighted grain 0.016 (edkit vignette / grain)
    x.x.globalCompositeOperation = "multiply";
    x.x.drawImage(VIG, 0, 0);
    x.x.globalCompositeOperation = "source-over";
    const id = pixels(x),
      d = id.data,
      N = W * H,
      off = Math.floor(rng(1000 + n * 7919)() * N);
    for (let p = 0, i = 0; p < N; p++, i += 4) {
      let k = p + off;
      if (k >= N) k -= N;
      const L = luma(d[i], d[i + 1], d[i + 2]) / 255,
        g = NOISE[k] * (0.35 + 0.65 * (1 - Math.abs(2 * L - 1)));
      d[i] += g;
      d[i + 1] += g;
      d[i + 2] += g;
    }
    x.x.putImageData(id, 0, 0);
    return x;
  }

  // ------------------------------------------------------------------ text: captions + tracking overlay
  function maskOverlay(x, m, shadowA, shadowBlur, ink = "#fff") {
    // y = x * (1 - shadowA * blur(m)); out = y * (1 - m) + ink * m
    const sh = mk(W, H);
    sh.x.filter = `blur(${shadowBlur}px)`;
    sh.x.drawImage(m, 0, 0);
    sh.x.filter = "none";
    sh.x.globalCompositeOperation = "source-in";
    sh.x.fillStyle = "#000";
    sh.x.fillRect(0, 0, W, H);
    x.x.globalAlpha = shadowA;
    x.x.drawImage(sh, 0, 0);
    x.x.globalAlpha = 1;
    if (ink !== "#fff") {
      const t = mk(W, H);
      t.x.drawImage(m, 0, 0);
      t.x.globalCompositeOperation = "source-in";
      t.x.fillStyle = ink;
      t.x.fillRect(0, 0, W, H);
      m = t;
    }
    x.x.drawImage(m, 0, 0);
  }
  function caption(x, text, size = 52) {
    const m = mk(W, H, false),
      f = `${Math.round(size * SC)}px ${FONT}`;
    m.x.font = f;
    const mt = m.x.measureText(text),
      asc = mt.fontBoundingBoxAscent || size * SC * 0.905;
    m.x.fillStyle = "#fff";
    m.x.fillText(
      text,
      0.5 * W -
        (mt.actualBoundingBoxLeft + mt.actualBoundingBoxRight) / 2 +
        mt.actualBoundingBoxLeft,
      0.5 * H + 0.38 * asc,
    );
    maskOverlay(x, m, 0.35, 3 * SC, "rgb(247,247,247)");
  }
  function arcBetween(a, b, bend) {
    const c = [(a[0] + b[0]) / 2 - (b[1] - a[1]) * bend, (a[1] + b[1]) / 2 + (b[0] - a[0]) * bend];
    return c;
  }
  function overlay(x, P, n, st) {
    const m = mk(W, H, false),
      c = m.x;
    c.strokeStyle = "#fff";
    c.fillStyle = "#fff";
    c.lineCap = "round";
    c.lineJoin = "round";
    c.font = `${Math.round(26 * SC)}px ${FONT}`;
    c.textBaseline = "top";
    P.forEach(([px, py], i) => {
      if (st.dots) {
        c.globalAlpha = 1;
        c.beginPath();
        c.arc(px, py, 3.2 * SC, 0, 2 * Math.PI);
        c.fill();
      }
      if (st.labels && (st.nlab == null || i < st.nlab)) {
        const j = (n * 7 + i * 13) % 9,
          vx = Math.floor((px / SC) * 0.56 + 180 + j),
          vy = Math.floor((py / SC) * 0.62 + 560 + j);
        c.globalAlpha = 230 / 255;
        c.fillText(`x: ${vx}   y: ${vy}`, px + 14 * SC, py - 34 * SC);
      }
    });
    const curve = (a, b, bend, w, al, arrow) => {
      const q = arcBetween(a, b, bend);
      c.globalAlpha = al;
      c.lineWidth = w * SC;
      c.beginPath();
      c.moveTo(a[0], a[1]);
      c.quadraticCurveTo(q[0], q[1], b[0], b[1]);
      c.stroke();
      if (arrow) {
        const ang = Math.atan2(b[1] - q[1], b[0] - q[0]),
          L = 13 * SC;
        c.beginPath();
        for (const s of [-1, 1]) {
          c.moveTo(b[0], b[1]);
          c.lineTo(
            b[0] + L * Math.cos(ang + Math.PI + s * 0.45),
            b[1] + L * Math.sin(ang + Math.PI + s * 0.45),
          );
        }
        c.stroke();
      }
    };
    if (st.arcs)
      for (let i = 0; i < P.length - 1; i++)
        curve(P[i], P[i + 1], i % 2 === 0 ? 0.35 : -0.45, 2, 235 / 255);
    if (st.circles && P.length >= 3) {
      const a0 = (((n * 9) % 360) * Math.PI) / 180;
      c.globalAlpha = 220 / 255;
      c.lineWidth = 2 * SC;
      c.beginPath();
      c.arc(P[0][0], P[0][1], 230 * SC, a0, a0 + (300 * Math.PI) / 180);
      c.stroke();
      c.globalAlpha = 200 / 255;
      c.lineWidth = 1.8 * SC;
      c.beginPath();
      c.arc(P[1][0], P[1][1], 120 * SC, (30 * Math.PI) / 180, (330 * Math.PI) / 180);
      c.stroke();
      curve(P[0], P[2], 0.6, 2, 235 / 255, true);
    }
    maskOverlay(x, m, 0.25, 2.5 * SC);
  }

  // ------------------------------------------------------------------ composition
  const at = (map, n) => (map ? map[String(n)] : undefined);
  function rectPx(r) {
    return [
      Math.round(r[0] * W),
      Math.round(r[1] * H),
      Math.max(2, Math.round((r[2] - r[0]) * W)),
      Math.max(2, Math.round((r[3] - r[1]) * H)),
    ];
  }
  async function cosmic(id, k, stars) {
    const o = copyOf(await img(id, k));
    if (stars)
      screenOn(
        o,
        sparkLayer(
          Object.assign({ rate: stars, region: [0, 0, 1, 1], scale: 1.1 }, STAR_P),
          PLAN.items[id].f0 + k,
        ),
      );
    return o;
  }
  const STAR_P = {
    seed: 5,
    size: 1.0,
    col: [0.95, 0.92, 1.0],
    life: [4, 8],
    rise: 0,
    star_p: 0.55,
  };
  async function base(b, n, drawn) {
    const it = (id) => PLAN.items[id];
    if (b.t === "solid") return filled(b.v);
    if (b.t === "item") {
      drawn[b.id] = [0, 0, W, H];
      return copyOf(await img(b.id, n - it(b.id).f0));
    }
    if (b.t === "cosmic") {
      drawn[b.id] = [0, 0, W, H];
      return cosmic(b.id, n - it(b.id).f0, 0);
    }
    if (b.t === "sil") {
      const o = filled(0);
      o.x.drawImage(await silhouette(b.id, n - it(b.id).f0), 0, 0);
      return o;
    }
    if (b.t === "echo") {
      drawn[b.id] = [0, 0, W, H];
      const k = n - it(b.id).f0;
      if (n < (b.from ?? 0)) return copyOf(await img(b.id, k));
      const fr = [];
      for (const t of b.taps) fr.push(await img(b.id, k - t));
      return echo(fr, b.w);
    }
    if (b.t === "wipe") {
      drawn[b.a] = drawn[b.b] = [0, 0, W, H];
      return jaggedWipe(
        await img(b.a, n - it(b.a).f0),
        await img(b.b, n - it(b.b).f0),
        at(b.p, n) ?? 0.5,
      );
    }
    throw new Error("unknown base " + b.t);
  }
  async function applyFx(x, f, n) {
    const v = f.v ? at(f.v, n) : undefined;
    if (f.v && v === undefined) return x;
    if (!f.v && f.f1 !== undefined && !(f.f0 <= n && n < f.f1)) return x;
    switch (f.t) {
      case "spark":
        screenOn(x, sparkLayer(f, n), f.amt ?? 1);
        return x;
      case "cosmic":
        screenOn(x, await cosmic(f.id, n - PLAN.items[f.id].f0, f.stars || 0), f.amt ?? 0.55);
        return x;
      case "burst":
        return burst(x, v);
      case "zblur":
        return zoomBlur(x, v);
      case "noise":
        return pixelNoise(x, v);
      case "glitch":
        return glitch(x, 1000 + n * 31, v);
      case "hlkeep":
        return highlightKeep(x, v, at(f.dim, n) ?? 1);
      case "bloom":
        return bloom(x, f.thr, f.amt);
      case "mblur":
        return motionBlur(x, v);
      case "leak":
        return lightLeak(x, v);
      case "fade": {
        const u = Math.max(0, (n - f.f0) / f.len);
        if (u > 0) {
          x.x.globalAlpha = clamp(f.k * u ** f.pow);
          x.x.fillStyle = "#000";
          x.x.fillRect(0, 0, W, H);
          x.x.globalAlpha = 1;
        }
        return x;
      }
    }
    throw new Error("unknown fx " + f.t);
  }
  async function compose(n) {
    const sg = PLAN.segs.find((s) => s.f0 <= n && n < s.f1);
    if (!sg) throw new Error("no segment at frame " + n);
    const drawn = {};
    let x = await base(sg.base, n, drawn);
    for (const f of sg.fx) if (f.at === "base") x = await applyFx(x, f, n);
    for (const l of sg.layers) {
      if (n < l.from || n >= (l.until ?? sg.f1)) continue;
      let r;
      if (l.rect) r = rectPx(l.rect);
      else {
        const s = at(l.scale, n);
        if (s === undefined) continue;
        const ox = l.ox || 0,
          oy = l.oy || 0;
        r = rectPx([0.5 - s / 2 + ox, 0.5 - s / 2 + oy, 0.5 + s / 2 + ox, 0.5 + s / 2 + oy]);
      }
      const p = await img(l.id, n - PLAN.items[l.id].f0, r[2], r[3]);
      x.x.drawImage(p, r[0], r[1]);
      drawn[l.id] = r;
    }
    for (const f of sg.fx) if (f.at !== "base") x = await applyFx(x, f, n);
    for (const t of sg.trk) {
      if (n < t.f0 || n >= t.f1) continue;
      const tr = PLAN.tracks[t.id],
        r = drawn[t.item];
      if (!tr || !r) continue;
      const pts = tr.pts[clamp(n - tr.f0, 0, tr.pts.length - 1)],
        it = PLAN.items[t.item],
        cr = cropRect(...camAt(it, clamp(n - it.f0, 0, it.n - 1)), it.aspect);
      const P = pts
        .map(([sx, sy]) => [
          r[0] + ((sx - cr[0]) / cr[2]) * r[2],
          r[1] + ((sy - cr[1]) / cr[3]) * r[3],
        ])
        .filter(
          ([px, py]) =>
            px > r[0] - 4 && px < r[0] + r[2] + 4 && py > r[1] - 4 && py < r[1] + r[3] + 4,
        );
      if (P.length) overlay(x, P, n, t);
    }
    for (const [a, b, word] of PLAN.caps) if (a <= n && n < b) caption(x, word, 52);
    return finish(x, n);
  }
  function setPlan(p) {
    PLAN = p;
    W = p.w || 1920;
    H = p.h || 1080;
    SC = W / 1920;
    let f = 0;
    for (const s of p.segs) {
      if (s.f0 !== f || !(s.f1 > s.f0))
        throw new Error(`segment gap/overlap at ${s.f0}, expected ${f}`);
      f = s.f1;
    }
    p.nf = f;
    initPost();
  }
  return {
    setPlan,
    renderFrame: compose,
    mk,
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
