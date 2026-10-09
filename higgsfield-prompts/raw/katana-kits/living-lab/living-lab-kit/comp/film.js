/* film.js — timeline runtime. Cuts are declared in scenes.js as {t0, t1, draw: async (ctx, t, k, lt) => {}}.
 * k = local progress 0..1, lt = local seconds. Overlays (copy, labels, flashes, grain) are drawn after the cut.
 */
(function () {
  'use strict';
  const { W, H } = ENG;
  const cv = document.getElementById('c'); const ctx = cv.getContext('2d');
  const FPS = 24, DUR = 30.0;
  window.__comp = { width: W, height: H, fps: FPS, duration: DUR };
  let fontsReady = null;
  async function fonts() {
    if (!fontsReady) fontsReady = Promise.all([
      '600 96px "Inter Tight"', '700 96px "Inter Tight"', '500 96px "Inter Tight"', '800 96px "Inter Tight"',
      'italic 400 96px "Instrument Serif"', '400 96px "Instrument Serif"', '500 22px "JetBrains Mono"',
    ].map((f) => document.fonts.load(f))).then(() => document.fonts.ready);
    return fontsReady;
  }
  window.__seek = async (t) => {
    await fonts();
    const S = window.SCENES; t = Math.min(Math.max(t, 0), DUR - 1e-6);
    const cut = S.cuts.find((c) => t >= c.t0 && t < c.t1) || S.cuts[S.cuts.length - 1];
    ctx.save(); ctx.clearRect(0, 0, W, H);
    await cut.draw(ctx, t, (t - cut.t0) / (cut.t1 - cut.t0), t - cut.t0, cut);
    ctx.restore();
    if (S.overlay) { ctx.save(); await S.overlay(ctx, t, cut); ctx.restore(); }
  };
})();
