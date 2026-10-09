/* Project hooks for the mixed-media example (copy to W/comp/fx.js and edit).
 * Loaded by page.html after engine.js and before RRC.boot() finishes; everything here is optional.
 * Pattern: register new table entries, then reference them by name from edl.json.
 */
(function () {
  const U = RRC.util;

  // A layer used as fx.crown in edl.json: ink crown floating above the tracked face (Katana common.js crown()).
  // params: dy (eye units above the eyes, default -1.9), size (eye units, default 1.1)
  RRC.register("LAYERS", "crown", {
    phase: "over",
    order: 22,
    draw(S, p, x) {
      if (!S.fo) return; // needs faces on the clip (or shot.face.box)
      const [cx, cy] = U.fp(S, 0, p.dy ?? -1.9),
        s = S.fo.D * (p.size ?? 1.1);
      const P = [
        [-1, 0.3],
        [-1.05, -0.55],
        [-0.5, -0.05],
        [0, -0.75],
        [0.5, -0.05],
        [1.05, -0.55],
        [1, 0.3],
      ].map(([u, v]) => [cx + u * s, cy + v * s]);
      U.poly(x, P, { w: 5, color: "$ink", b: S.b, seed: 71, close: true });
      U.poly(
        x,
        P.map((q) => [q[0] + 8, q[1] + 6]),
        { w: 3, color: "$accent2", b: S.b, seed: 72, close: true },
      );
      [
        [-1.05, -0.55],
        [0, -0.75],
        [1.05, -0.55],
      ].forEach(([u, v]) => {
        x.fillStyle = U.col("$accent");
        x.beginPath();
        x.arc(cx + u * s, cy + v * s - 12, 9, 0, Math.PI * 2);
        x.fill();
      });
    },
  });

  // Hooks: init, ready (once, {R, E}); per frame beforeFrame, afterPlate, afterLook, after_back|after_subject|after_over|after_post|after_final, afterFrame ((S, ctx, RRC)).
  RRC.hook("ready", ({ R }) =>
    R.log(`fx.js: ${R.sevt.length} stickers placed, ${R.cutouts.length} cutouts`),
  );
})();
