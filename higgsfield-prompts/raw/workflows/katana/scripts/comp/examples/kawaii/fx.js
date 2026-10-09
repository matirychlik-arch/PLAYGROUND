/* Project hooks for the kawaii example (copy to W/comp/fx.js). Shows the two common extension points:
 *  1. a new kawaii doodle shape usable in face_doodles pools ("paw"),
 *  2. a new face-anchored layer ("eye_sparkle": 4-point twinkles on both eyes).
 */
(function () {
  const U = RRC.util;

  // DOODLES.kawaii.<name>(ctx, sizePx, rnd, k): ctx is already translated/rotated/scaled so the shape is drawn in
  // unit space (about -0.5..0.5). k.LAV / k.WH are the line / fill colours, k.lw(px) converts a screen line width.
  RRC.register("DOODLES", "paw", {
    family: "kawaii",
    size: 0.55, // size = default scale in eye units for auto face_doodles
    draw(c, s, r, k) {
      const p = new Path2D(),
        J = (a) => (r() - 0.5) * 2 * a;
      p.ellipse(0, 0.12, 0.3 + J(0.02), 0.24, 0, 0, Math.PI * 2);
      [
        [-0.32, -0.22],
        [-0.11, -0.38],
        [0.11, -0.38],
        [0.32, -0.22],
      ].forEach(([x, y]) => {
        p.moveTo(x + 0.11, y);
        p.ellipse(x, y + J(0.02), 0.11, 0.13, 0, 0, Math.PI * 2);
      });
      c.lineJoin = "round";
      c.lineWidth = k.lw(4.5);
      c.strokeStyle = k.LAV;
      c.stroke(p);
      c.fillStyle = k.WH;
      c.fill(p);
    },
  });

  // fx.eye_sparkle {at, size (eye units), color}: twinkles that pulse on both eyes (face-locked shots only).
  RRC.register("FACE", "eye_sparkle", {
    phase: "over",
    order: 35,
    draw(S, p, x) {
      if (!S.fo || S.lt < (p.at ?? 0)) return;
      const pulse = 0.75 + 0.25 * Math.sin((S.lt - (p.at ?? 0)) * 18),
        s = S.fo.D * (p.size ?? 0.16) * pulse;
      for (const sx of [-0.5, 0.5]) {
        const [cx, cy] = U.fp(S, sx + 0.08, -0.12);
        x.save();
        x.translate(cx, cy);
        x.rotate(S.fo.a);
        x.fillStyle = U.col(p.color ?? "#fff");
        x.shadowColor = "rgba(255,255,255,0.9)";
        x.shadowBlur = U.px(10);
        x.beginPath();
        for (let i = 0; i < 8; i++) {
          const a = (i * Math.PI) / 4,
            rr = i % 2 ? s * 0.18 : s;
          x.lineTo(Math.cos(a) * rr, Math.sin(a) * rr);
        }
        x.closePath();
        x.fill();
        x.restore();
      }
    },
  });
})();
