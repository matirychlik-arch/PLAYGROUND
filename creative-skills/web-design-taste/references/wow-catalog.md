# Wow catalog

Contents:
1. Selection rules
2. The catalog (families A-D, plus signature builds)
3. Scroll-scrub film: concept, footage contract, delivery
4. Implementation contracts
5. Canonical scroll skeletons (sticky stack, horizontal pan, reveal)
6. Libraries and "I need X" index
7. Anti-convergence ledger

The Tier-1 mechanic is the thing a visitor remembers. One per page, chosen in the brief, fully executed, and chosen from this catalog rather than from the first idea that comes to mind. The wow is bespoke media responding to input, not a CSS trick. For Mati's viral apps the best wow usually reproduces the app's own trick on the page (try it right there) or turns its output into the hero.

## 1. Selection rules (mechanical)

1. Pick the technique that pays off the concept spine: the mechanic should enact the site's idea. A "calibration" spine wants focus/precision physics, an "ascent" spine wants climbing and parallax depth, an "archive" spine wants leafing and stacking. Write one sentence defending the pairing.
2. Never reuse the previous build's technique (see the ledger in section 7). If the spine truly demands a repeat, change the expression: different subject, different axis, different payoff.
3. Tiers: Cinema = one Tier-1 from the catalog plus motivated reveals. Spectacle = one Tier-1 plus a second beat mid-page from a different technique family plus a brief-mandated custom cursor.
4. Every technique must be screenshot-safe (initial state fully rendered) and reduced-motion-safe (a static composed fallback).
5. Banned as Tier-1: autoplay ambient loop alone (passive), generic fade-in reveals, particles-behind-text with no interaction, marquee strips, tilt-on-hover cards. They may exist as seasoning, never as the answer to "what's the wow".
6. Restraint is not an escape: a "clean", "minimal" or "trustworthy" brief still gets a wow; restraint means the effect is calm and deliberate (slower camera, quieter scenes), not absent. If motion cannot be finished properly in scope, ship a clean static page and say so.

## 2. The catalog

### A. Film scrub family (scroll plays a generated or shot video)

| ID | Technique | When to use |
|---|---|---|
| A1 | Single-shot hero scrub. One ~5 s clip from the approved hero still (push-in, rack focus, subject turn, light sweep; start differs from end), extracted to about 100 frames or a seekable MP4, bound to pin progress | Proven baseline; any product or brand with one subject |
| A2 | Long-form chaptered scrub. 2-4 clips with the same grade and different beats (wide establishing, detail macro, reveal) across a long pin (300-500 vh). Between chapters: pinned text cards, layered cutouts or metric readouts. Frames scrub, headline stages swap per chapter, a progress rail tracks the journey | The awwwards-style centerpiece; budget it only when the page has few other heavy beats |
| A3 | Product turntable. Multi-angle shots of the same product (reference-driven so identity holds) or a short orbit clip; scroll rotates the product | Physical-product briefs |
| A4 | Seam-locked scroll scrub (the "animated website"). A full-site camera journey through 4-7 scenes: chain each leg from the previous leg's actual boundary frame, or join miniature/isometric dives with start/end-frame-locked aerial connectors. Scrub optimized MP4 segments directly while chapter copy stays in normal document flow | A site that is a journey (browse through an industry, a diorama fly-through). Section 3 below |

### B. Layered depth family (one image becomes a 3D-feeling scene)

| ID | Technique | When to use |
|---|---|---|
| B1 | Cutout parallax rig. Remove the background of the hero subject, build a clean background plate behind it (optional mid layer: fog, foliage, particles as transparent PNGs). Stack 3-5 layers moving at different rates on scroll and subtly on cursor | Cheap, robust, dramatic; hero feels volumetric |
| B2 | Grade-shift interaction pair. Two renders of the same composition (dark/dormant and lit/alive), crossfaded by cursor spotlight (mask follows pointer) or by scroll | "The site notices you" effect |
| B3 | 3D subject scene. Approved hero image converted to a GLB, rendered in an R3F scene with scroll-driven camera orbit and cursor tilt | Spectacle tier; product or character with a strong silhouette |

### C. Canvas and pixel family (the image itself is alive)

| ID | Technique | When to use |
|---|---|---|
| C1 | Displacement/liquid hover. Hero image on a WebGL plane; the cursor ripples/distorts it (three.js displacement or OGL) | Editorial-compatible when subtle |
| C2 | Particle dissolve. Hero image sampled into canvas particles that assemble on load and scatter/reform with scroll or cursor | Data, tech and AI spines |
| C3 | Scroll-driven mask reveal. The page opens inside giant display type or a shape; scrolling expands the mask until the media goes full-bleed (clip-path or canvas) | Strong opener for editorial and cinema hybrids |

### D. Spatial layout family (the page itself moves unusually)

| ID | Technique | When to use |
|---|---|---|
| D1 | Horizontal cinema rail. A pinned section pans horizontally through a wide panorama (outpaint the hero sideways) or a sequence of scene plates; content cards ride the rail | The scroll axis rotation is the surprise |
| D2 | Sticky-stack chapters. Full-bleed chapters stack/peel over each other, each with its own plate or loop; type pinned per chapter | Reliable, editorial-friendly |
| D3 | Kinetic type opener. Massive display type choreographed on scroll (per-character stagger, weight/width axis animation on a variable font, lines sliding on different tracks) over a plate | When the brand voice is typography |

### E. Signature builds (patterns to adapt, combine or reinvent)

| Name | Mechanism | Fits |
|---|---|---|
| Particle-morph hero [WebGL] | About 4-6k Three.js instanced points morphing through the scroll (sphere, then the product's silhouette, then disperse), recolored/relit per stage; scroll-driven lerp between precomputed target positions | Premium product or brand (perfume, spirits, jewelry, tech); tune shape, finish and env color to the niche |
| Fluid plus smooth-scroll studio [WebGL] | Fixed WebGL fluid/gradient backdrop with a rotating point cloud, weighty Lenis scroll, GSAP ScrollTrigger reveals, staggered 2-column video grid (not a carousel) | Studios, agencies |
| Camera-dolly product switcher [WebGL] | The active product dollies toward the camera while the next approaches from depth and the background color lerps; drag/wheel/tabs, spring snap, autoplay; scenes as data | Multi-variant or flavor showcases |
| Hold-to-spin 3D showroom [WebGL] | Clay/toy-look turntable on a stepped platform; hold to spin with inertia; click hotspots for detail | Apparel, physical products, collectibles |
| Cursor X-ray reveal | Full-screen photo with an aligned "X-ray" substrate beneath; a feathered lens follows the cursor and dissolves the cover (CSS `mask-image` at the cursor, no 3D). Strictly black-and-white plus one breathing accent reads most premium | "Look inside" stories, editorial deep-dives |
| Scroll-scrub film | About 15 s generated film extracted to frames on a canvas, scrubbed by scroll, caption cards fading in | High-impact brand reveals and launches (dark, cinematic) |
| Frosted-card scrubber | Warm, light variant: a lifestyle film scrubs behind translucent frosted cards, then resolves into content panels | Boutiques, cafes, florists, ateliers |
| Magnetic gallery wall | Infinite draggable wall of tiles with magnetic hover, 3D tilt, burst intro, click-to-zoom; one shared pointer-physics handler plus inertia plus modulo wrap | Portfolios, galleries, visual merch |
| Kinetic portfolio | Lenis smooth scroll, GSAP reveals plus scroll-velocity skew, magnetic elements, custom cursor plus hero spotlight, one marquee, a vinyl-style carousel, live clock | Personal sites, creative showcases |
| Try-it-live demo (viral apps) | The app's core interaction embedded in the hero (upload, type, drop an image), result appears in place; share artifact visible | Mati's viral apps: the page is the demo |

Pair every effect with real generated or designed assets and the SSR guards below.

## 3. Scroll-scrub film (concept)

The visitor's scroll plays a film forward and backward at scroll speed and holds any frame as a still when they pause; chapter copy reads over it in normal document flow.

### Journey shape

- **Single-shot (default):** one continuous ~15 s film in one generation, scrubbed end to end. No seams. Chapters (3-6, each a focal point, one short headline, one sentence, 0-3 proof tags) are HTML over the film. Choose for a brand, product, service, portfolio or launch whose story is one subject seen ever more closely. When in doubt, single-shot.
- **Multi-leg:** 4-7 distinct worlds, each leg generated strictly sequentially from the previous leg's real last frame, plus a per-leg encode and inspection. "It would look cooler with more scenes" is not a reason; a tight single-shot film beats a loosely seamed chain.
- Write into the brief: journey shape, the chapters, a world grammar (one byte-identical style preamble, perspective, palette, light direction, surface finish, background behavior; for multi-leg change only the subject and focal action between legs), mobile framing (focal points inside the center-safe area), delivery budget.

### The footage contract (what makes a scrub look expensive)

Direct it like a high-end product film; the scrub looks broken regardless of render quality if these are not obeyed.

- **One continuous move, no hard cuts.** A cut becomes a jarring jump mid-scrub. One unbroken camera move (slow orbit, push-in, rise, fly-through) or one continuous transformation. Connect beats with continuous motion.
- **One hero subject, kept centered, with clean negative space** where the chapter copy sits. The video fills the viewport and crops the edges (`cover`), so keep the subject center-safe and edges expendable.
- **A background the copy can survive.** Dark, seamless, low-detail (studio black or charcoal, a soft gradient, the subject emerging from darkness). A bright busy full-frame environment behind body copy is the most common reason a beautiful film reads as unusable.
- **Slow, steady motion.** Constant speed, gentle ease only at the very start and end; the scroll supplies the pacing.
- **Locked exposure and white balance, no flicker; minimal motion blur.** Every frame is shown as a still, so exposure pumping shimmers and heavy blur smears.
- **Resolves at both ends.** First frame is the establishing shot, last is the closing beauty state. Start state differs from end state, or the scrub has no payoff.
- **No on-screen text, logos or watermarks.** All type is HTML over the video so it stays crisp, selectable and translatable.

Subjects that scrub beautifully: a product slowly orbiting on black; an exploded-view assembly; a macro detail traveling along a surface; a transformation or morph; a hero object emerging from darkness. Avoid: cuts, fast pans, handheld shake, busy bright backgrounds, color/exposure flicker.

Generating the film with any video model (Seedance 2, KLING, Higgsfield Cinema Studio): prompt one continuous camera move, one subject, state the start and end frames, ask for locked exposure and no text; chain legs from the actual last frame of the previous clip. Video models are poor at text, so keep all lettering in HTML.

### Delivery and QA

- Delivery budget: at most 32 MiB for all desktop clips and at most 16 MiB for all mobile clips; shorten or re-encode before relaxing it. Ship desktop and lighter mobile encodes.
- Scrub optimized MP4 or Blob URLs directly (seekable); every segment has a first-frame poster extracted from the exact deployed (encoded) clip; allow `blob:` in the CSP `media-src`; no second scroll timeline driving the same media.
- Chapter copy is server-rendered in semantic document flow (not hidden until a viewport callback); headings in DOM order; route buttons keyboard accessible; active state not hover-only.
- `prefers-reduced-motion`: no video fetch, the complete static story shown.
- Initialization only in an effect; teardown aborts fetches, removes listeners and video nodes, cancels RAF, revokes Blob URLs.
- Multi-leg only: seams use actual boundary frames; camera velocity does not reverse accidentally across a seam.

## 4. Implementation contracts (all families)

- **Initial paint is complete:** frame 1 / layer stack / unmasked state renders before any JS-driven interaction; a headless full-page screenshot shows a finished hero.
- **Input to response feels physical:** scrub via ScrollTrigger progress (`scrub: 0.5-1`); cursor via `useMotionValue` plus springs. Never `useState` per frame, never animate layout properties.
- **Reduced motion:** the composed final state, static, no pin.
- **Mobile:** the technique degrades deliberately (shorter pin, cursor effects replaced by scroll equivalents, turntable becomes a swipeable sequence); declare the degradation in the brief.
- One signature effect per page; do not stack two.
- Marquee: at most once per page.

## 5. Canonical scroll skeletons

Sticky stack (cards pin and the previous card shrinks as the next arrives):

```tsx
useEffect(() => {
  if (reduce || !ref.current) return;
  const ctx = gsap.context(() => {
    const cards = gsap.utils.toArray<HTMLElement>(".stack-card");
    cards.forEach((card, i) => {
      if (i === cards.length - 1) return;
      ScrollTrigger.create({
        trigger: card, start: "top top",
        endTrigger: cards[cards.length - 1], end: "top top",
        pin: true, pinSpacing: false,
      });
      gsap.to(card, {
        scale: 0.92, opacity: 0.55, ease: "none",
        scrollTrigger: { trigger: cards[i + 1], start: "top bottom", end: "top top", scrub: true },
      });
    });
  }, ref);
  return () => ctx.revert();
}, [reduce]);
// each card: className="stack-card sticky top-0 min-h-[100dvh] flex items-center justify-center"
```

Critical points: `start: "top top"` (not `"top center"` or `"top 80%"`, which fire halfway through scroll), `pin: true`, every card except the last pinned, the scale/opacity driven by the NEXT card's trigger.

Horizontal pan (vertical scroll becomes a horizontal track):

```tsx
const distance = track.current!.scrollWidth - window.innerWidth;
gsap.to(track.current, {
  x: -distance, ease: "none",
  scrollTrigger: {
    trigger: wrap.current, start: "top top",
    end: () => `+=${distance}`, pin: true, scrub: 1, invalidateOnRefresh: true,
  },
});
// wrapper: className="relative overflow-hidden"; track: className="flex h-[100dvh] items-center"
```

Critical points: `start: "top top"` so the animation never starts before the section is pinned; scroll length equals horizontal travel; wrap in `gsap.context` with `ctx.revert()` cleanup and a reduced-motion guard.

Scroll reveal stagger (no pinning; lighter than GSAP): Motion `whileInView` with `initial={{ opacity: 0, y: 24 }}`, `viewport={{ once: true, amount: 0.3 }}`, `transition={{ duration: 0.6, delay: i * 0.06, ease: [0.16, 1, 0.3, 1] }}`, and `initial={reduce ? false : ...}` for reduced motion. Keep the visible-state rule: nothing waits invisible for a trigger in the screenshot state.

## 6. Libraries and "I need X" index

| Library | Adds | Notes |
|---|---|---|
| `motion` (`motion/react`) | enter/exit, layout/FLIP, springs, `useScroll`/`useInView`, gestures | Client-only |
| `gsap` plus `@gsap/react` | ScrollTrigger pinned/scrubbed sequences, timelines, SplitText; use `useGSAP()` | Isolate in leaf components, cleanup |
| `lenis` | weighted smooth scroll | |
| `three`, `@react-three/fiber`, `@react-three/drei` | real-time 3D, GLTF/PBR, glass, particle fields, camera flythroughs | Lazy-load; use a self-hosted HDRI, not `preset=` (it fetches a CDN at runtime) |
| `@react-three/postprocessing` | bloom, DOF, glitch, chromatic aberration | |
| `@shadergradient/react` | animated 3D gradient backdrop | |
| `@tsparticles/slim`, `@tsparticles/confetti` | particle fields, confetti | |
| `cobe` | 5 KB rotating WebGL globe | |
| `ogl` | custom-shader hero without three.js bulk | |
| `animejs` v4 | SVG line-draw/morph, staggers, timelines | |
| `@number-flow/react` | animated odometer numbers and prices | |
| `split-type` | split text to lines/words/chars | |
| `swiper` | touch sliders, coverflow | |

| I need | Reach for |
|---|---|
| Animated hero backdrop | `@shadergradient/react`, three plus R3F, Magic UI light-rays / warp-background / retro-grid, Kokonut beams-background, `cobe`, or a generated hero image/video |
| Animated headline | Magic UI aurora-text / morphing-text / hyper-text, motion-primitives text effects, `split-type` plus GSAP |
| Scroll reveal | motion-primitives in-view / animated-group, Magic UI blur-fade / text-reveal, Motion `useInView`, GSAP ScrollTrigger |
| Marquee / logo strip | Magic UI marquee, motion-primitives infinite-slider |
| Card with flair | Magic UI magic-card, motion-primitives tilt / border-trail |
| Nav / dock / command | shadcn navigation-menu / command, motion-primitives dock |
| Animated numbers | `@number-flow/react`, Magic UI number-ticker |
| Magnetic / cursor | motion-primitives magnetic / cursor |
| Full marketing sections | Tailark blocks (hero, features, pricing, testimonials, CTA, footer) |
| App shell / dashboard / auth / table / chart | shadcn blocks |
| Confetti / celebration | `@tsparticles/confetti`, Magic UI confetti |
| 3D scene / particle field | three plus R3F plus drei |

Component registries (Magic UI, Cult UI, SmoothUI, motion-primitives, Kokonut UI, Tailark, Animata, Eldora UI) copy source into the repo through `npx shadcn@latest add <url or @registry/name>`; verify a registry URL before relying on it. Prefer reaching into these over hand-rolling generic sections.

SSR pattern for client-only and WebGL parts: render children after mount (a `ClientOnly` wrapper using `useEffect` to set a mounted flag), and wrap WebGL components in `React.lazy` inside `Suspense` inside the mounted gate so three/shader code never enters the server render. Gate motion behind `useReducedMotion()` or `matchMedia("(prefers-reduced-motion: reduce)")` and render the static fallback when set.

## 7. Anti-convergence ledger

Before the brief locks, list the previous build's six identity axes and differ on at least four: palette family, type pairing, hero architecture, Tier-1 technique, CTA garment set (zero overlap), corner and border language. If two consecutive builds both use the animated-journey default (A4), differ on world/subject, journey shape and the remaining axes instead. First build in a chat: derive all six from the brief's material world and say so; the enemy is the model's own statistical default.
