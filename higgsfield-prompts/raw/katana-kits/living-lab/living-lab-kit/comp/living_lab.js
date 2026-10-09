/* living_lab.js — Living Lab 30 s film, data-driven. All copy, labels, clip slots and anchors come from window.FILM (film_data.js).
 * Timeline: 120 BPM · breath 0–2 · DROP 2.0 · pulse A/B · build 18 · vacuum 19.5 · LIFT 20.0 · climax · FINAL HIT 28.0 · end 30.
 * Slot ids (V_seed, V_roots, …) are fixed; FILM.alias can point a slot at another clip; FILM.stills gives start-frame fallbacks. */
(function () {
  'use strict';
  const { W, H, P, clamp, lerp, prog, E, rng, fx, Frames, bgBlack, bgCream, grain, handles, label, text, measure, circle } = ENG;

  /* ---------------- copy (swap here) ---------------- */
  const F = window.FILM || {};
  const COPY = Object.assign({
    name: 'NAME', tagline: 'What it is, in four words', chip: 'NEW LANGUAGE MODEL',
    open: 'One word.', alive1: 'Everything alive', alive2a: 'starts ', alive2b: 'small.',
    seed: ['A ', 'seed.'], cell: ['A ', 'cell.'], word: ['A ', 'word.'], flash: ['poems.', 'recipes.', 'answers.'],
    bring: ['You bring the ', 'seed.'], toward: ['It grows toward ', 'you.'], leaf: 'Leaf by leaf.', word2: ['Word by ', 'word.'],
    plant: ['Plant a ', 'word.'], watch: 'Watch a', morph: { base: 'word', at: 3, insert: 'l' }, grow: 'grow.',
  }, F.copy || {});
  const LBL = Object.assign({ dormant: 'S00 / DORMANT', split: 'SEED 01 / SPLIT', leaf: 'LEAF 08 / +137.5°', cell: 'CELL 01 → 02 → 04', ring: 'SPECIMEN RING 01 / 8 SITES', input: 'INPUT / YOU', growing: 'SEED 01 / GROWING', contact: 'CONTACT', exhale: 'EXHALE', horizon: 'HORIZON', angle: '∠ 137.5°' }, F.labels || {});
  const ANC = Object.assign({ prof1: [1060, 1360, 330], prof2: [1205, 1510, 330] }, F.anchors || {}); // head x at clip 0 s → 5 s, head y (px, before framing)


  /* ---------------- clips ---------------- */
  const FALLBACK = Object.assign({}, F.stills || {});
  const ALIAS = Object.assign({}, F.alias || {});
  const AVAILABLE = window.CLIPS_AVAILABLE || [];
  const META = window.CLIPS_META || {};
  for (const id of AVAILABLE) Frames.meta[id] = { dir: `../clips/${id}`, frames: (META[id] && META[id].frames) || 121, fps: 24 };
  const RES = (id) => { let k = id, n = 0; while (ALIAS[k] && n++ < 5) k = ALIAS[k]; return k; };
  // returns {img, still} for clip time ct (seconds inside the 5 s clip)
  async function src(id0, ct) {
    const id = RES(id0), m = Frames.meta[id];
    if (m) return { img: await Frames.get(id, clamp(ct, 0, (m.frames - 1) / 24)), still: false };
    const st = FALLBACK[id] || FALLBACK[id0];
    if (st) return { img: await Frames.img(st), still: true };
    return { img: null, still: true };
  }
  function placeholder(ctx, id, rect) {
    const [x, y, w, h] = rect.map(Math.round); if (w <= 2 || h <= 2) return;
    const g = ctx.createLinearGradient(x, y, x + w, y + h); g.addColorStop(0, '#17141A'); g.addColorStop(1, '#2A1F33'); ctx.save(); ctx.fillStyle = g; ctx.fillRect(x, y, w, h);
    ctx.strokeStyle = 'rgba(240,240,240,0.35)'; ctx.setLineDash([6, 8]); ctx.lineWidth = 2; ctx.strokeRect(x + 8, y + 8, w - 16, h - 16); ctx.restore();
    if (w > 160) label(ctx, x + 18, y + h - 52, ['✦ GENERATION · ' + id], { style: 'lime', size: Math.max(12, Math.min(20, w / 40)) });
  }
  // draw a clip into rect; stills get a slow push so the draft still moves
  async function clip(ctx, id, ct, rect, o = {}) {
    const s = await src(id, ct);
    if (!s.img) { placeholder(ctx, id, rect); return; }
    const oo = Object.assign({}, o);
    if (s.still) { oo.zoom = (o.zoom || 1) * (1 + 0.03 * ct); }
    fx(ctx, s.img, rect, oo);
  }
  const FULL = [0, 0, W, H];

  /* ---------------- type helpers ---------------- */
  const SANS = '"Inter Tight", sans-serif', SERIF = '"Instrument Serif", serif';
  const INK = P.creamInk, LIGHT = '#F4F1EC';
  // two-part line: sans + serif italic accent. reveal 0..1 drives a letter-rise across the whole line.
  function line2(ctx, a, b, x, y, o = {}) {
    const size = o.size || 110, col = o.color || LIGHT, acc = o.accent || col;
    const wa = measure(ctx, a, { size, weight: 600, font: SANS, tracking: -0.02 });
    const wb = measure(ctx, b, { size: size * 1.08, weight: 400, font: SERIF, italic: true });
    let x0 = o.align === 'center' ? x - (wa + wb) / 2 : x;
    const n = a.length + b.length, r = o.reveal ?? 1;
    const ra = clamp(r * n / Math.max(1, a.length) * 0.999), rb = clamp((r * n - a.length) / Math.max(1, b.length));
    text(ctx, a, x0, y, { size, weight: 600, font: SANS, tracking: -0.02, color: col, reveal: ra, rise: size * 0.28, alpha: o.alpha, blur: o.blur });
    text(ctx, b, x0 + wa, y, { size: size * 1.08, weight: 400, font: SERIF, italic: true, color: acc, reveal: rb, rise: size * 0.28, alpha: o.alpha, blur: o.blur });
    return wa + wb;
  }
  const rev = (t, t0, dur = 0.35) => E.out3(prog(t, t0, t0 + dur));
  const fadeOut = (t, t1, dur = 0.12) => 1 - prog(t, t1 - dur, t1);

  /* ---------------- specimens (ref4), drawn in code ---------------- */
  const SPEC = (() => {
    const r = rng(77), list = [], cols = [P.orange, P.magenta, P.blue, P.mint, P.apricot, '#9A6BE0', '#7A8F3A', P.pink];
    for (let i = 0; i < 70; i++) {
      const a = r() * Math.PI * 2, d = Math.pow(r(), 0.6) * 760;
      list.push({ a, d, kind: Math.floor(r() * 6), size: 6 + Math.pow(r(), 2.2) * 54, col: cols[Math.floor(r() * cols.length)], col2: cols[Math.floor(r() * cols.length)], rot: r() * 6.28, t: r(), wob: r() });
    }
    return list.sort((p, q) => p.d - q.d);
  })();
  function specimens(ctx, cx, cy, k, t, o = {}) {
    for (let i = 0; i < SPEC.length; i++) {
      const s = SPEC[i]; const appear = clamp((k * 1.25 - (s.d / 760) * 0.9 - s.t * 0.15) * 4);
      if (appear <= 0) continue;
      const sc = appear < 1 ? E.out3(appear) * (1 + 0.15 * Math.sin(appear * Math.PI)) : 1;
      const x = cx + Math.cos(s.a) * s.d * (o.spread || 1), y = cy + Math.sin(s.a) * s.d * 0.62 * (o.spread || 1) + Math.sin(t * 1.3 + s.wob * 6) * 3;
      const z = s.size * sc;
      ctx.save(); ctx.translate(x, y); ctx.rotate(s.rot + t * 0.2 * (s.wob - 0.5)); ctx.globalAlpha = 0.92 * (o.alpha ?? 1);
      switch (s.kind) {
        case 0: ctx.fillStyle = s.col; ctx.beginPath(); ctx.arc(0, 0, z * 0.5, 0, 6.283); ctx.fill(); ctx.fillStyle = s.col2; ctx.beginPath(); ctx.arc(z * 0.1, -z * 0.05, z * 0.2, 0, 6.283); ctx.fill(); break;
        case 1: ctx.strokeStyle = s.col; ctx.lineWidth = Math.max(1.5, z * 0.09); ctx.beginPath(); ctx.arc(0, 0, z * 0.42, 0, 6.283); ctx.stroke(); break;
        case 2: ctx.fillStyle = s.col; ctx.beginPath(); ctx.ellipse(0, 0, z * 0.6, z * 0.32, 0, 0, 6.283); ctx.fill(); break;
        case 3: ctx.strokeStyle = s.col; ctx.lineWidth = 2; ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(-z, 0); ctx.bezierCurveTo(-z * 0.3, -z * 0.8, z * 0.3, z * 0.8, z, 0); ctx.stroke(); break;
        case 4: ctx.strokeStyle = s.col; ctx.lineWidth = 1.6; for (let j = 0; j < 4; j++) { ctx.beginPath(); ctx.arc((j % 2 - 0.5) * z * 0.36, (Math.floor(j / 2) - 0.5) * z * 0.36, z * 0.17, 0, 6.283); ctx.stroke(); } break;
        default: ctx.fillStyle = s.col; ctx.fillRect(-z * 0.18, -z * 0.18, z * 0.36, z * 0.36);
      }
      ctx.restore();
    }
  }

  /* ---------------- phyllotaxis mark ---------------- */
  function phyllo(ctx, cx, cy, n, scale, o = {}) {
    const GA = 137.5 * Math.PI / 180, cols = [P.pink, P.pink, P.apricot, P.butter, P.magenta, P.mint];
    for (let i = 0; i < n; i++) {
      const rr = scale * Math.sqrt(i), th = i * GA;
      const grow = clamp(n - i, 0, 1);
      const size = (2.2 + Math.sqrt(i) * 0.42) * (o.dot || 1) * E.out3(grow);
      const c = i % 23 === 7 ? P.mint : cols[Math.min(cols.length - 2, Math.floor(i / Math.max(1, n) * 4))];
      ctx.fillStyle = c; ctx.beginPath(); ctx.arc(cx + Math.cos(th) * rr, cy + Math.sin(th) * rr, size, 0, 6.283); ctx.fill();
    }
  }

  /* ---------------- grid tile helper ---------------- */
  async function tile(ctx, id, ct, r, o = {}) {
    await clip(ctx, id, ct, r, o);
    if (o.handles !== false) handles(ctx, r[0], r[1], r[2], r[3], { size: 7, color: o.hcol || P.mint, alpha: o.halpha ?? 0.9 });
    if (o.label) label(ctx, r[0] + 10, r[1] + 10, o.label, { style: o.lstyle || 'dark', size: 18 });
  }
  const lerpR = (a, b, k) => a.map((v, i) => lerp(v, b[i], k));

  /* ================= CUTS v2 (120 BPM: beat 0.5 s, bar 2 s; DROP 2.0 · LIFT 20.0 · FINAL 28.0) ================= */
  const cuts = [];
  const C = (t0, t1, draw) => cuts.push({ t0, t1, draw });
  const BARS = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26];
  // zoom punch on every bar downbeat: 1.06 → 1 over 6 frames
  const punch = (t) => { let z = 1; for (const b of BARS) if (t >= b && t < b + 0.25) z = 1 + 0.06 * (1 - E.out3((t - b) / 0.25)); return z; };
  const full = (id, ct, o = {}) => async (ctx, t) => clip(ctx, id, ct, FULL, Object.assign({ grain: 0.05 }, o, { zoom: (o.zoom || 1) * punch(t) }));
  const darkLeft = (ctx, a = 0.85, w = 1150) => { const g = ctx.createLinearGradient(0, 0, w, 0); g.addColorStop(0, `rgba(5,5,5,${a})`); g.addColorStop(0.55, `rgba(5,5,5,${a * 0.65})`); g.addColorStop(1, 'rgba(5,5,5,0)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H); };
  const lightLeft = (ctx, a = 0.75, w = 1100) => { const g = ctx.createLinearGradient(0, 0, w, 0); g.addColorStop(0, `rgba(239,232,222,${a})`); g.addColorStop(0.6, `rgba(239,232,222,${a * 0.5})`); g.addColorStop(1, 'rgba(239,232,222,0)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H); };
  // a sequence of fast sub-cuts inside one cut window: [[t0, drawFn], ...]
  const seq = (parts) => async (ctx, t, k, lt, cut) => { let p = parts[0]; for (const q of parts) if (t >= q[0]) p = q; await p[1](ctx, t, (t - p[0])); };

  // 0.00–2.00 breath: one dormant window; two 2-frame glimpses of what is coming
  C(0, 2.0, async (ctx, t) => {
    bgBlack(ctx, { lineAlpha: E.out3(prog(t, 0, 0.8)) });
    const g = E.out5(prog(t, 0.1, 0.55)), push = 1 + 0.04 * E.in3(prog(t, 1.4, 2.0));
    const cx = 540, cy = 735, w = 480 * g * push, h = 270 * g * push;
    if (g > 0.01) { const r = [cx - w / 2, cy - h / 2, w, h];
      const glimpse = (t >= 1.0 && t < 1.083) ? 'V_iris' : (t >= 1.5 && t < 1.583) ? 'V_ring' : null;
      if (glimpse) await clip(ctx, glimpse, 2.5, r, { dots: glimpse === 'V_iris' ? 1 : 0, cell: 10, dotsGain: 1.4 }); else await clip(ctx, 'V_seed', t * 0.3, r, { grain: 0.05 });
      handles(ctx, r[0], r[1], r[2], r[3], { size: 7, alpha: g }); label(ctx, cx - 240, cy - 135 - 46, [LBL.dormant], { size: 18, alpha: E.out3(prog(t, 0.45, 0.7)) }); }
    const k = rev(t, 0.3, 0.6);
    text(ctx, COPY.open, 1010, 600, { size: 104, weight: 600, font: SANS, tracking: -0.02, color: LIGHT, alpha: k, blur: (1 - k) * 8 });
  });
  // 2.00–2.25 DROP crash-zoom
  C(2.0, 2.25, async (ctx, t, k, lt) => {
    const z = E.expo(prog(lt, 0, 0.16)); bgBlack(ctx, {});
    await clip(ctx, 'V_seed', 1.6 + lt * 3.0, lerpR([540 - 252, 735 - 141, 504, 283], FULL, z), { grain: 0.05 });
    const f = 1 - prog(lt, 0, 0.085); if (f > 0) { ctx.fillStyle = `rgba(255,248,240,${0.8 * f})`; ctx.fillRect(0, 0, W, H); }
  });
  // 2.25–2.50 split photo | dots
  C(2.25, 2.5, async (ctx, t, k, lt) => {
    bgBlack(ctx, {}); const s = E.out5(prog(lt, 0, 0.15));
    const L = lerpR([0, 0, W / 2, H], [120, 160, 828, 760], s), R = lerpR([W / 2, 0, W / 2, H], [972, 160, 828, 760], s), ct = 2.6 + lt * 2;
    await tile(ctx, 'V_seed', ct, L, { handles: s > 0.5 }); await tile(ctx, 'V_seed', ct, R, { dots: 1, cell: 18, dotsGain: 1.25, handles: s > 0.5, label: s > 0.6 ? [LBL.split] : null, lstyle: 'outline' });
  });
  // 2.50–4.00 fast cuts under one held line
  C(2.5, 4.0, async (ctx, t, k, lt) => {
    await seq([
      [2.5, full('V_roots', 0.8 + (t - 2.5) * 1.6)],
      [3.0, async (c, tt, l) => { bgBlack(c, {}); await tile(c, 'V_fern', 2.4 + l * 2, [1100, 90, 560, 900], { label: [LBL.leaf] }); await tile(c, 'V_fern', 2.4 + l * 2, [1680, 470, 200, 200], { dots: 1, cell: 10, dotsGain: 1.3 }); }],
      [3.25, full('V_cherry', 2.2 + (t - 3.25) * 2)],
      [3.5, full('V_roots', 3.2 + (t - 3.5) * 1.5, { zoom: 1.35, focus: [0.5, 0.62] })],
    ])(ctx, t);
    darkLeft(ctx);
    text(ctx, COPY.alive1, 130, 470, { size: 104, weight: 600, font: SANS, tracking: -0.02, color: LIGHT, reveal: rev(t, 2.52, 0.35), rise: 30 });
    line2(ctx, COPY.alive2a, COPY.alive2b, 130, 590, { size: 104, accent: P.pink, reveal: rev(t, 2.8, 0.35) });
  });
  // 4.00–5.00 "A seed." · 5.00–6.00 "A cell." · 6.00–7.00 "A word."
  C(4.0, 5.0, async (ctx, t, k, lt) => { await full('V_clayseed', 1.1 + lt * 1.9)(ctx, t); line2(ctx, COPY.seed[0], COPY.seed[1], 140, 360, { size: 220, color: INK, reveal: rev(t, 4.0, 0.22) }); });
  C(5.0, 6.0, async (ctx, t, k, lt) => { await full('V_cell', 1.2 + lt * 3.6)(ctx, t); line2(ctx, COPY.cell[0], COPY.cell[1], 140, 360, { size: 220, color: INK, reveal: rev(t, 5.0, 0.22) }); label(ctx, 140, 940, [LBL.cell], { style: 'plainDark', size: 20, alpha: rev(t, 5.2, 0.3) }); });
  C(6.0, 7.0, async (ctx, t, k, lt) => { await full('V_dome', 0.6 + lt * 2.2)(ctx, t); line2(ctx, COPY.word[0], COPY.word[1], 110, 230, { size: 190, accent: P.pink, reveal: rev(t, 6.0, 0.22) }); });
  // 7.00–8.00 flash words: what one word grows into
  C(7.0, 8.0, async (ctx, t, k, lt) => {
    const i = Math.min(2, Math.floor((t - 7.0) / (1 / 3)));
    const ids = ['V_ink', 'V_fig', 'V_jelly'], ins = [1.4, 1.6, 1.4];
    const lti = t - 7.0 - i / 3;
    await clip(ctx, ids[i], ins[i] + lti * 2.0, FULL, { grain: 0.05, zoom: 1.08 - 0.08 * E.out3(lti * 3), dots: 0 });
    ctx.fillStyle = 'rgba(5,5,5,0.25)'; ctx.fillRect(0, 0, W, H);
    text(ctx, COPY.flash[i], W / 2, 600, { size: 200, weight: 400, font: SERIF, italic: true, color: LIGHT, align: 'center', revealMode: 'none' });
  });
  // 8.00–10.00 grid flight: windows bud on the beats; glitch at 9.75
  C(8.0, 10.0, async (ctx, t, k, lt) => {
    const cam = 1 + 0.08 * E.inOut3(k), dx = -lt * 34, dy = -lt * 18; bgBlack(ctx, { ox: dx, oy: dy });
    ctx.save(); ctx.translate(W / 2, H / 2); ctx.scale(cam * punch(t), cam * punch(t)); ctx.translate(-W / 2 + dx, -H / 2 + dy);
    const bud = (t0) => E.out5(prog(t, t0, t0 + 0.16));
    const T = [
      ['V_cherry', [170, 190, 640, 360], 8.0, {}, [170 + 320, 190 + 180, 0, 0]],
      ['V_pollen', [830, 110, 470, 264], 8.25, { dots: 1, cell: 14, dotsGain: 1.6 }, [830, 110, 0, 264]],
      ['V_ring', [830, 394, 640, 360], 8.5, { label: [LBL.ring] }, [830, 394, 640, 0]],
      ['V_coral', [1320, 110, 420, 264], 8.75, {}, [1300, 110, 0, 264]],
      ['V_spheregrid', [170, 570, 640, 280], 9.0, {}, [170, 570, 640, 0]],
      ['V_infra', [1490, 394, 300, 360], 9.25, { thermal: 0 }, [1490, 394, 0, 360]],
    ];
    for (const [id, R, t0, o, from] of T) { const b = bud(t0); if (b <= 0) continue; await tile(ctx, id, 1.6 + lt * 1.5, lerpR(from, R, b), Object.assign({ handles: b > 0.9 }, o, { label: b > 0.9 ? o.label : null })); }
    ctx.restore();
  });
  // 10.00–12.00 "You bring the seed." — hand · her inhale · her breath branching into a tree
  C(10.0, 12.0, async (ctx, t, k, lt) => {
    let dark = false;
    if (t < 10.75) await full('V_hand', 0.8 + lt * 2.8)(ctx, t);
    else if (t < 11.375) { const ct = 2.0 + (t - 10.75) * 2.4; await full('V_prof1', ct, { zoom: 1.28, focus: [0, 0.35] })(ctx, t); specimens(ctx, (lerp(ANC.prof1[0], ANC.prof1[1], ct / 5)) * 1.28 - 40, ANC.prof1[2], E.out3((t - 10.75) * 1.6), t, { spread: 0.8 }); }
    else { dark = true; await full('V_breathF', 2.5 + (t - 11.375) * 3.2)(ctx, t); }
    if (dark) darkLeft(ctx, 0.55, 900); else lightLeft(ctx, 0.8, 1000);
    line2(ctx, COPY.bring[0], COPY.bring[1], 120, 300, { size: 100, color: dark ? LIGHT : INK, accent: dark ? P.pink : INK, reveal: rev(t, 10.02, 0.4) });
    label(ctx, 120, 360, [LBL.input], { style: 'lime', size: 20, alpha: rev(t, 10.3, 0.2) });
  });
  // 12.00–14.00 "It grows toward you." — tendril wraps the fingertip · her eye opens in pollen · pollen flies at us
  C(12.0, 14.0, async (ctx, t, k, lt) => {
    let col = LIGHT;
    if (t < 12.75) await clip(ctx, 'V_tendril', 4.95 - lt * 1.6, FULL, { grain: 0.05, zoom: 1.06 * punch(t), focus: [0.62, 0.5] });
    else if (t < 13.5) { col = INK; await full('V_eye', 1.0 + (t - 12.75) * 3.0)(ctx, t); }
    else await full('V_pollen', 2.6 + (t - 13.5) * 3.0, { dots: t >= 13.83 ? 1 : 0, cell: 18, dotsGain: 1.6 })(ctx, t);
    { const g = ctx.createLinearGradient(0, H, 0, H - 380); const c0 = col === INK ? '239,232,222' : '5,5,5'; g.addColorStop(0, `rgba(${c0},${col === INK ? 0.7 : 0.85})`); g.addColorStop(1, `rgba(${c0},0)`); ctx.fillStyle = g; ctx.fillRect(0, H - 380, W, 380); }
    line2(ctx, COPY.toward[0], COPY.toward[1], 120, 975, { size: 96, color: col, accent: col === INK ? P.magenta : P.pink, reveal: rev(t, 12.02, 0.45) });
  });
  // 14.00–16.00 fast montage on the half-beats
  C(14.0, 16.0, seq([
    [14.0, async (c, t, l) => clip(c, 'V_mush', 1.0 + l * 3.0, FULL, { grain: 0.05, zoom: punch(t) })],
    [14.5, async (c, t, l) => clip(c, 'V_murm', 1.4 + l * 2.6, FULL, { grain: 0.05, dots: 1, cell: 16, dotsInv: true, dotsGain: 1.6, dotsBias: -0.42, dotsBg: P.cream, dotsFill: P.magenta, dotsRing: P.blue, dotsTiny: P.blue, sweep: lerp(0.0, 1.15, E.inOut3(l * 2)), sweepSoft: 0.1 })],
    [15.0, async (c, t, l) => clip(c, 'V_fern', 2.6 + l * 3.0, FULL, { grain: 0.05 })],
    [15.5, async (c, t, l) => clip(c, 'V_spheregrid', 1.8 + l * 2.6, FULL, { grain: 0.05 })],
  ]));
  // 16.00–18.00 the layout divides like a cell on the beats — "Leaf by leaf. / Word by word."
  const RG = [720, 180, 1080, 720];
  const L2 = [[720, 180, 532, 720], [1268, 180, 532, 720]];
  const L4 = [[720, 180, 532, 352], [1268, 180, 532, 352], [720, 548, 532, 352], [1268, 548, 532, 352]];
  const L8 = []; for (let r = 0; r < 2; r++) for (let c = 0; c < 4; c++) L8.push([720 + c * 274, 180 + r * 368, 258, 352]);
  const CONT = [
    { id: 'V_roots', o: { dots: 1, cell: 12, dotsGain: 1.4, dotsFill: P.mint, dotsRing: P.pink } }, { id: 'V_fern', o: {} },
    { id: 'V_cherry', o: {} }, { id: 'V_pollen', o: { dots: 1, cell: 12, dotsGain: 1.6 } },
    { id: 'V_cell', o: {} }, { id: 'V_clayseed', o: {} }, { id: 'V_ring', o: {} }, { id: 'V_coral', o: {} },
  ];
  C(16.0, 18.0, async (ctx, t, k, lt) => {
    bgBlack(ctx, {});
    const st = t < 16.5 ? 0 : t < 17.0 ? 1 : t < 17.5 ? 2 : 3, ts = [16.0, 16.5, 17.0, 17.5][st], s = E.out5(prog(t, ts, ts + 0.12));
    let rects, parents, ids;
    if (st === 0) { rects = [RG]; parents = [[RG[0] + RG[2] / 2, RG[1] + RG[3] / 2, 0, 0]]; ids = [0]; }
    if (st === 1) { rects = L2; parents = [RG, RG]; ids = [0, 2]; }
    if (st === 2) { rects = L4; parents = [L2[0], L2[1], L2[0], L2[1]]; ids = [0, 2, 4, 6]; }
    if (st === 3) { rects = L8; parents = L8.map((_, i) => L4[Math.floor(i / 4) * 2 + Math.floor((i % 4) / 2)]); ids = [0, 1, 2, 3, 4, 5, 6, 7]; }
    for (let i = 0; i < rects.length; i++) { const c = CONT[ids[i]]; await tile(ctx, c.id, 1.6 + lt * 1.4 + i * 0.2, lerpR(parents[i], rects[i], s), Object.assign({ handles: s > 0.95, label: i === 0 && st === 0 ? [LBL.growing] : null }, c.o)); }
    if (t < 17.0) text(ctx, COPY.leaf, 120, 590, { size: 96, weight: 600, font: SANS, tracking: -0.02, color: LIGHT, reveal: rev(t, 16.02, 0.3), rise: 26 });
    else line2(ctx, COPY.word2[0], COPY.word2[1], 120, 590, { size: 96, accent: P.pink, reveal: rev(t, 17.02, 0.3) });
  });
  // 18.00–19.50 build: accelerating cuts, then the push into the pupil
  const BUILD = (() => { const a = []; let t = 18.0, d = 0.25; const ids = ['V_ring', 'V_spheregrid', 'V_cherry', 'V_pollen', 'V_coral', 'V_dandelion', 'V_dome', 'V_infra', 'V_fern', 'V_seed', 'V_clayseed', 'V_roots']; let i = 0; while (t < 19.0 - 1e-6) { a.push([t, ids[i % ids.length]]); t += d; d = Math.max(1 / 24 * 2, d * 0.8); i++; } return a; })();
  C(18.0, 19.5, async (ctx, t, k, lt) => {
    if (t < 19.0) { let p = BUILD[0]; for (const q of BUILD) if (t >= q[0]) p = q; const j = BUILD.indexOf(p);
      await clip(ctx, p[1], 2.0 + (t - p[0]) * 2, FULL, { grain: 0.05, zoom: 1.12 - 0.1 * clamp((t - p[0]) * 6), dots: j % 3 === 1 ? 1 : 0, thermal: j % 3 === 2 ? 0.9 : 0, cell: 16, dotsGain: 1.5 }); }
    else { const l = t - 19.0; await clip(ctx, 'V_iris', 3.0 + l * 3.6, FULL, { grain: 0.04, zoom: 1 + 0.35 * E.in3(l * 2) }); const b = prog(t, 19.38, 19.5); if (b > 0) { ctx.fillStyle = `rgba(0,0,0,${b})`; ctx.fillRect(0, 0, W, H); } }
  });
  // 19.50–20.00 vacuum: black, one pink seed-dot appears
  C(19.5, 20.0, async (ctx, t, k, lt) => { ctx.fillStyle = P.black; ctx.fillRect(0, 0, W, H); const r = 9 * E.out5(prog(t, 19.62, 19.8)); if (r > 0) { ctx.fillStyle = P.pink; ctx.beginPath(); ctx.arc(W / 2, H / 2, r, 0, 6.283); ctx.fill(); } });
  // 20.00–22.00 LIFT: the bloom wave and the name
  C(20.0, 22.0, async (ctx, t, k, lt) => {
    const ex = 1 + 0.7 * (1 - E.out3(prog(lt, 0, 0.3)));
    await clip(ctx, 'V_field', 0.8 + lt * 1.9, FULL, { grain: 0.05, expo: ex, zoom: punch(t) });
    const name = COPY.name; let size = 400; ctx.save(); ctx.font = `700 ${size}px ${SANS}`; { const w0 = [...name].reduce((a, c) => a + ctx.measureText(c).width, 0) * 0.97; if (w0 > W * 0.86) size = Math.floor(size * W * 0.86 / w0); } ctx.font = `700 ${size}px ${SANS}`; const ws = [...name].map((c) => ctx.measureText(c).width); ctx.restore();
    const tr = -0.03 * size, total = ws.reduce((a, b) => a + b, 0) + tr * (name.length - 1); let x = W / 2 - total / 2;
    for (let i = 0; i < name.length; i++) { const g = E.out5(prog(t, 20.02 + i * 0.07, 20.02 + i * 0.07 + 0.38)); text(ctx, name[i], x, lerp(H + size * 0.85, 820, g), { size, weight: 700, font: SANS, color: INK, revealMode: 'none' }); x += ws[i] + tr; }
    label(ctx, W / 2 - 170, 880, [COPY.chip], { style: 'dark', size: 22, alpha: rev(t, 20.6, 0.25) });
    const f = 1 - prog(lt, 0, 0.085); if (f > 0) { ctx.fillStyle = `rgba(255,250,244,${0.75 * f})`; ctx.fillRect(0, 0, W, H); }
  });
  // 22.00–24.00 climax montage
  C(22.0, 24.0, seq([
    [22.0, async (c, t, l) => clip(c, 'V_infra', 2.2 + l * 2.6, FULL, { grain: 0.05, zoom: punch(t) })],
    [22.5, async (c, t, l) => clip(c, 'V_tunnel', 1.4 + l * 2.8, FULL, { grain: 0.05 })],
    [23.0, async (c, t, l) => clip(c, 'V_coral', 2.6 + l * 2.6, FULL, { grain: 0.05 })],
    [23.5, async (c, t, l) => { await clip(c, 'V_sunflower', 2.0 + l * 2.0, FULL, { grain: 0.05 }); const a = E.out3(prog(l, 0.02, 0.3)), cx = 960, cy = 540, r = 300;
      c.save(); c.strokeStyle = '#141414'; c.lineWidth = 4; c.setLineDash([10, 10]); c.beginPath(); c.arc(cx, cy, r, -Math.PI / 2, -Math.PI / 2 + a * 137.5 * Math.PI / 180); c.stroke(); c.setLineDash([]);
      c.beginPath(); c.moveTo(cx, cy); c.lineTo(cx, cy - r); c.stroke(); const ea = -Math.PI / 2 + a * 137.5 * Math.PI / 180; c.beginPath(); c.moveTo(cx, cy); c.lineTo(cx + Math.cos(ea) * r, cy + Math.sin(ea) * r); c.stroke(); c.restore();
      label(c, cx + 24, cy - r - 10, [LBL.angle], { style: 'outline', size: 20, alpha: a }); }],
  ]));
  // 24.00–25.50 "Plant a word." — seeds leave the dandelion
  C(24.0, 25.5, async (ctx, t, k, lt) => {
    await full('V_dandelion', 0.4 + lt * 2.4)(ctx, t);
    { const g = ctx.createLinearGradient(W, 0, W - 900, 0); g.addColorStop(0, 'rgba(5,5,5,0.85)'); g.addColorStop(1, 'rgba(5,5,5,0)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H); }
    line2(ctx, COPY.plant[0], COPY.plant[1], 1180, 600, { size: 130, accent: P.pink, reveal: rev(t, 24.02, 0.35) });
  });
  // 25.50–28.00 word → world, over the profile filling with specimens
  C(25.5, 28.0, async (ctx, t, k, lt) => {
    const ct = 2.2 + lt * 1.0; await full('V_prof2', ct)(ctx, t);
    specimens(ctx, lerp(ANC.prof2[0], ANC.prof2[1], clamp((ct - 1) / 3.6)) - 40, ANC.prof2[2], 0.5 + 0.5 * E.out3(k), t, { spread: 1.0, alpha: 0.95 });
    lightLeft(ctx, 0.7, 1000);
    const size = 140, y = 600, x0 = 120, sw = E.out3(prog(t, 25.5, 25.65));
    text(ctx, COPY.watch, x0, y - size * 1.12, { size: size * 0.62, weight: 600, font: SANS, tracking: -0.02, color: INK, alpha: sw, rise: 20, reveal: sw });
    const f = { size: size * 1.08, weight: 400, font: SERIF, italic: true }, M = COPY.morph, A = M.base.slice(0, M.at), Bq = M.base.slice(M.at);
    const wWor = measure(ctx, A, f), wL = measure(ctx, M.insert, f), wD = measure(ctx, Bq, f), g = E.out5(prog(t, 25.6, 26.1));
    text(ctx, A, x0, y, Object.assign({ color: INK, revealMode: 'none' }, f));
    ctx.save(); ctx.beginPath(); ctx.rect(x0 + wWor - 4, y - size * 1.3 * g - 4, wL + 8, size * 1.3 * g + 40); ctx.clip(); text(ctx, M.insert, x0 + wWor, y, Object.assign({ color: P.magenta, revealMode: 'none' }, f)); ctx.restore();
    text(ctx, Bq, x0 + wWor + wL * g, y, Object.assign({ color: INK, revealMode: 'none' }, f));
    text(ctx, COPY.grow, x0 + wWor + wL + wD + 34, y, { size, weight: 600, font: SANS, tracking: -0.02, color: INK, reveal: rev(t, 26.15, 0.4), rise: 30 });
  });
  // 28.00–30.00 FINAL HIT: the mark bursts out of the seed-dot; lockup holds through the tail
  C(28.0, 30.0, async (ctx, t, k, lt) => {
    const pulse = 1 - prog(t, 28.0, 28.25);
    bgBlack(ctx, { lines: false, dot: pulse > 0 ? `rgba(244,154,200,${0.2 + 0.8 * pulse})` : P.gridDot });
    const n = Math.floor(lerp(1, 233, E.out5(prog(t, 28.0, 28.9))));
    ctx.save(); ctx.translate(W / 2, 400); ctx.rotate(lt * 0.12); phyllo(ctx, 0, 0, n, 9.2 * (1 + 0.04 * Math.sin(lt * 3)), { dot: 1.0 }); ctx.restore();
    text(ctx, COPY.name, W / 2, 760, { size: 150, weight: 700, font: SANS, tracking: 0.02, color: LIGHT, align: 'center', reveal: rev(t, 28.08, 0.45), rise: 30 });
    text(ctx, COPY.tagline, W / 2, 840, { size: 50, weight: 400, font: SERIF, italic: true, color: P.pink, align: 'center', alpha: rev(t, 28.4, 0.5), revealMode: 'none' });
    const f = 1 - prog(lt, 0, 0.085); if (f > 0) { ctx.fillStyle = `rgba(255,250,244,${0.6 * f})`; ctx.fillRect(0, 0, W, H); }
    const out = prog(t, 29.75, 30.0); if (out > 0) { ctx.fillStyle = `rgba(5,5,5,${out})`; ctx.fillRect(0, 0, W, H); }
  });

  // ---------- lines & patterns (ref1/ref2 language) ----------
  const D = window.DECO;
  const EV = [
    // [t0, t1, world, fn(ctx, t, k)]  k = local 0..1
    [0.2, 2.0, 'black', (c, t, k) => { D.orbit(c, 540, 735, 330, 205, t, 'black', { k: prog(t, 0.3, 1.1) }); D.ruler(c, 120, 1030, 1680, prog(t, 0.2, 1.6), 'black'); D.constr(c, 540, 735, prog(t, 0.7, 1.4), 'black', { coord: [LBL.dormant.split(' ')[0], ...D.coord(540, 735)] }); }],
    [2.0, 2.7, 'black', (c, t, k) => D.rings(c, 960, 540, k, 'black', { r: 1100 })],
    [2.5, 4.0, 'black', (c, t, k) => { D.constr(c, 1180, 300, prog(t, 2.5, 2.9), 'black', { coord: D.coord(1180, 300) }); D.ruler(c, 1860, 90, 900, prog(t, 2.6, 3.4), 'black', { vertical: true }); }],
    [4.0, 5.0, 'cream', (c, t, k) => { D.orbit(c, 1010, 770, 440, 150, t, 'cream', { k: prog(t, 4.05, 4.5), rot: -0.08 }); D.constr(c, 1010, 770, prog(t, 4.0, 4.35), 'cream', { coord: [LBL.split.split(' /')[0], ...D.coord(1010, 770)] }); }],
    [5.0, 6.0, 'cream', (c, t, k) => { D.arcs(c, 1010, 540, 330, t, 'cream'); D.constr(c, 1010, 540, prog(t, 5.0, 5.35), 'cream', { coord: D.coord(1010, 540) }); D.halftone(c, 1560, 760, 300, 240, t, 'cream', { step: 18, alpha: 0.85 }); }],
    [6.0, 7.0, 'black', (c, t, k) => { D.orbit(c, 930, 820, 760, 300, t, 'black', { k: prog(t, 6.0, 6.5), dot: true }); D.ruler(c, 120, 60, 1680, prog(t, 6.05, 6.6), 'black'); }],
    [7.0, 8.0, 'black', (c, t, k) => { const i = Math.floor((t - 7) * 3); D.scan(c, ((t - 7) * 3) % 1, 'black'); D.constr(c, [1150, 760, 1180][Math.min(2, i)], [480, 560, 520][Math.min(2, i)], ((t - 7) * 3) % 1 * 2, 'black'); }],
    [8.0, 10.0, 'black', (c, t, k) => { D.ruler(c, 60, 1040, 1800, prog(t, 8.0, 8.8), 'black'); D.ruler(c, 40, 60, 960, prog(t, 8.1, 8.9), 'black', { vertical: true }); D.connector(c, 300, 120, 1050, 574, prog(t, 8.55, 8.95), 'black'); D.halftone(c, 1500, 820, 360, 180, t, 'black', { step: 16 }); }],
    [10.0, 10.75, 'cream', (c, t, k) => { D.connector(c, 330, 380, 1270, 560, prog(t, 10.3, 10.65), 'cream'); D.orbit(c, 1270, 560, 260, 110, t, 'cream', { k: prog(t, 10.1, 10.5) }); }],
    [10.75, 11.375, 'cream', (c, t, k) => { D.orbit(c, 1180, 340, 330, 330, t, 'cream', { k: prog(t, 10.75, 11.2), speed: 1.6 }); }],
    [11.375, 12.0, 'black', (c, t, k) => { D.constr(c, 1180, 560, prog(t, 11.375, 11.7), 'black', { coord: [LBL.exhale, ...D.coord(1180, 560)] }); D.ruler(c, 120, 1030, 1000, prog(t, 11.4, 11.9), 'black'); }],
    [12.0, 12.75, 'black', (c, t, k) => { D.rings(c, 1260, 520, prog(t, 12.0, 12.7), 'black', { r: 500, n: 3 }); D.constr(c, 1260, 520, prog(t, 12.0, 12.3), 'black', { coord: [LBL.contact, ...D.coord(1260, 520)] }); }],
    [12.75, 13.5, 'cream', (c, t, k) => { D.arcs(c, 1000, 560, 260, t, 'cream'); D.orbit(c, 1000, 560, 420, 200, t, 'cream', { k: prog(t, 12.75, 13.2) }); }],
    [13.5, 14.0, 'black', (c, t, k) => D.rings(c, 960, 540, prog(t, 13.5, 14.0), 'black', { r: 900, n: 3 })],
    [14.0, 16.0, 'black', (c, t, k) => { const l = ((t - 14) * 2) % 1, i = Math.floor((t - 14) * 2), w = i === 1 ? 'cream' : 'black'; const P2 = [[1000, 600], [1100, 460], [1300, 520], [960, 640]][i]; D.constr(c, P2[0], P2[1], l * 1.8, w, { coord: D.coord(P2[0], P2[1]) }); }],
    [16.0, 18.0, 'black', (c, t, k) => { D.ruler(c, 720, 160, 1080, prog(t, 16.0, 16.5), 'black'); D.ruler(c, 700, 180, 720, prog(t, 16.1, 16.6), 'black', { vertical: true }); D.connector(c, 300, 640, 720, 900, prog(t, 16.2, 16.6), 'black'); }],
    [19.5, 20.0, 'black', (c, t, k) => { D.orbit(c, 960, 540, 90, 90, t, 'black', { k: prog(t, 19.62, 19.95), speed: 3 }); D.orbit(c, 960, 540, 170, 170, -t, 'black', { k: prog(t, 19.7, 19.98), dot: false }); }],
    [20.0, 20.8, 'cream', (c, t, k) => D.rings(c, 960, 540, k, 'cream', { r: 1200, n: 5 })],
    [20.3, 22.0, 'cream', (c, t, k) => { D.ruler(c, 120, 1040, 1680, prog(t, 20.3, 21.0), 'cream'); D.constr(c, 960, 300, prog(t, 20.4, 20.9), 'cream', { coord: [LBL.horizon, ...D.coord(960, 300)] }); }],
    [22.0, 23.5, 'black', (c, t, k) => { const l = ((t - 22) * 2) % 1, i = Math.floor((t - 22) * 2), w = i === 2 ? 'cream' : 'black'; const P2 = [[1100, 520], [960, 520], [1180, 420]][i]; D.constr(c, P2[0], P2[1], l * 1.8, w, { coord: D.coord(P2[0], P2[1]) }); }],
    [23.5, 24.0, 'cream', (c, t, k) => D.arcs(c, 960, 540, 360, t, 'cream')],
    [24.0, 25.5, 'black', (c, t, k) => { D.orbit(c, 720, 540, 470, 470, t, 'black', { k: prog(t, 24.0, 24.6), speed: 0.9 }); D.ruler(c, 1180, 700, 600, prog(t, 24.3, 24.9), 'black'); }],
    [25.5, 28.0, 'cream', (c, t, k) => { D.orbit(c, 1330, 360, 360, 360, t, 'cream', { k: prog(t, 25.6, 26.3), speed: 0.8 }); D.connector(c, 840, 640, 1200, 420, prog(t, 26.2, 26.7), 'cream'); D.ruler(c, 120, 720, 760, prog(t, 26.2, 26.9), 'cream'); }],
    [28.0, 28.9, 'black', (c, t, k) => D.rings(c, 960, 400, k, 'black', { r: 1300, n: 5 })],
    [28.2, 30.0, 'black', (c, t, k) => { D.orbit(c, 960, 400, 200, 200, t, 'black', { k: prog(t, 28.3, 28.9), speed: 1.2 }); D.orbit(c, 960, 400, 250, 250, -t * 0.6, 'black', { k: prog(t, 28.5, 29.1), dot: false }); D.ruler(c, 760, 900, 400, prog(t, 28.6, 29.2), 'black', { step: 20 }); }],
  ];
  // glitch slices on the vocal stutters (bar ends) — 3 frames each
  const GLITCH = [3.75, 5.75, 9.75, 11.75, 13.75, 15.75, 21.75, 23.75, 25.75];
  async function overlay(ctx, t) {
    for (const [t0, t1, w, fn] of EV) if (t >= t0 && t < t1) { ctx.save(); fn(ctx, t, (t - t0) / (t1 - t0)); ctx.restore(); }
    for (const g of GLITCH) if (t >= g && t < g + 0.125) {
      const r = rng(Math.floor(t * 24) + 5), snap = document.createElement('canvas'); snap.width = W; snap.height = H; snap.getContext('2d').drawImage(ctx.canvas, 0, 0);
      for (let i = 0; i < 9; i++) { const y = Math.floor(r() * H), h = 20 + Math.floor(r() * 90), dx = (r() - 0.5) * 140; ctx.drawImage(snap, 0, y, W, h, dx, y, W, h); }
      ctx.save(); ctx.globalCompositeOperation = 'screen'; ctx.globalAlpha = 0.35; ctx.drawImage(snap, 8, 0); ctx.restore();
    }
    grain(ctx, t, 0.05, 'overlay');
  }
  window.SCENES = { duration: 30.0, cuts, overlay, COPY };
})();
