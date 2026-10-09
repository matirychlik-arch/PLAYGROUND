# Review rubric

Contents:
1. How to run the review
2. Hard gates (pass or fail, run by grep and code inspection)
3. Scored checklist (10 categories x 10 points)
4. Scorecard template
5. Pre-flight matrix (last filter)

Run section 2 before delivering. It is a completion gate, not a suggestion: most items are verified by grep or code inspection, so there is no excuse for skipping them. Then score section 3 honestly (an item you did not check scores 0, not 1). Replace `app/src/` in the commands with your source directory.

## 1. How to run the review

1. Run the hard gates. Fix every failure and re-run; do not hand over a build with a failed gate.
2. Read the page as a visitor at 375 px, tablet and desktop width, in light and dark if dual-mode. Look at the actual render, not only the code.
3. Score section 3, write the top three fixes, apply them, re-score only the touched categories.
4. Say in the scorecard what you could not verify (real devices, Lighthouse run, motion feel, screen reader).
5. Perceptual quality (composition, animation feel, real delight) needs human eyes. Say so plainly instead of overclaiming.

## 2. Hard gates

| # | Gate | How to verify |
|---|---|---|
| G1 | Placeholders: no `<...>` tokens, `lorem`, `REMOVE_THIS`, empty `src=""` | `grep -rniE 'lorem ipsum\|REMOVE_THIS\|TODO' app/src/` and scan quoted strings for leftover `<brand name>` style tokens |
| G2 | Dash ban: no em-dash or en-dash separator in user-visible strings (code comments exempt) | `grep -rn $'\xe2\x80\x94\|\xe2\x80\x93' app/src/` (bash; the two byte sequences are the em-dash and en-dash characters); must return nothing visible |
| G3 | Banned default palette absent from tokens | Check the CSS tokens against the banned families in `design-recipe.md` section 5, and against the previous build's family. Overridable only by the user's explicit brand colors, justified in the brief |
| G4 | No `h-screen` / `100vh` for full-height sections | `grep -rn 'h-screen\|100vh' app/src/` must be empty (use `dvh`) |
| G5 | Reduced motion: every animation source (Motion, GSAP, registry components, CSS keyframes) has a `prefers-reduced-motion` guard or static fallback | grep for `motion/react`, `gsap`, `@keyframes`, then confirm guards |
| G6 | Hero: real visual, fits the first viewport, max 4 text elements, CTA visible without scroll | Inspect the render at 1440x900 and 390x844 |
| G7 | Screenshot-safe reveals: nothing at `opacity: 0` that depends on a viewport or scroll trigger to become visible; videos have a `poster` | `grep -rn 'opacity-0\|opacity: 0' app/src/` then classify; hover-state decorations are fine. A full-page headless screenshot must show every section |
| G8 | CTA integrity: one label per intent page-wide; primary CTA max ~3 words and one line; no shared site-wide button style | Grep CTA labels; grep for a repeated CTA class string or one `Button` component reused across sections |
| G9 | Contrast AA: body 4.5:1, large text 3:1, every button label against its own background, form placeholders and focus rings | Check with a contrast tool; white-on-white is an automatic fail |
| G10 | SSR safety (server-rendered React only): no `window`/`document`/`localStorage`/`navigator` at module top level or in render; client-only and WebGL parts behind a mounted gate, WebGL also lazy | `grep -rn 'window\.\|document\.\|localStorage' app/src/` and check each hit is inside an effect or handler |
| G11 | Signature wow built (not claimed), defended by a catalog ID, with reduced-motion and mobile fallbacks | Compare brief to code; if scroll-scrub film: clip, poster and mobile encode exist and every path in the scenes file resolves |
| G12 | Assets referenced: every file in the public/assets folder is referenced by a route or component; the hero references a real asset (no picsum, stock or CSS-gradient-only hero); icons come from one family | List files vs grep references |
| G13 | Head kit complete: favicon (ico/svg plus png sizes), apple-touch-icon, 192/512 and maskable icons with `site.webmanifest`, `theme-color`, full OG and twitter card block with absolute image URLs | Inspect `<head>`; the scaffold's default favicon is a fail |
| G14 | Section plan honored: the built page matches the brief's section plan (families, order, no consecutive family repeats); if it changed, the brief was updated | Compare |
| G15 | Copy self-audit done: every visible string re-read; nothing grammatically broken, referent-unclear, filler-verb ("Elevate", "Seamless") or fake-precise (`92%`, `4.1x` without a source) | Read the page aloud |
| G16 | Eyebrow ration: eyebrow-position labels (small uppercase or mono kicker directly above a section's display headline) at most ceil(sections / 3) | `grep -rn 'uppercase tracking' app/src/` then classify by position; spec strips, table captions and footer column heads are exempt |
| G17 | Anti-convergence: the brief lists the previous build's six axes and this build differs on at least four; rationed garments (drawing underline, hover flood-fill, framed block) appear at most once page-wide combined | Check the ledger in the brief |

## 3. Scored checklist (10 categories x 10 points)

Score each sub-item 0 (fails), 1 (partial), 2 (clean).

**A. Typography (10)**
1. Allowed pairing, no Inter display, no default serif or banned serif.
2. Display scale fits the headline length (3-5 words may use 72 px; otherwise 36-60 px); no 4-line hero headline.
3. Body is 16 px, leading about 1.625, measure at most 65ch.
4. Italic descenders cleared; same-family emphasis only; numbers tabular.
5. Font loading self-hosted with `swap`; Polish/other diacritics render in the chosen face.

**B. Color and materials (10)**
1. Exactly one accent, saturation under 80%, used identically across all sections.
2. One neutral family; no pure black or white.
3. One theme across the page (no inverted mid-page section).
4. One radius language; shadows tinted; no glows.
5. Cards only where hierarchy needs them; no nested-box stacks.

**C. Hero (10)**
1. Fits the viewport; headline max 2 lines; subtext max 20 words.
2. At most 4 text elements; none of the banned hero items (tagline, trust strip, pricing teaser, bullets, avatars, version label).
3. Real, bespoke visual; no div-built fake UI.
4. Non-default composition (not centered-over-mesh; split/asymmetric/image-first unless editorial).
5. Top padding at most 96 px; nav single line and at most 80 px.

**D. Layout and structure (10)**
1. At least 4 distinct section families for 6+ sections; no repeated family.
2. No 3 equal feature cards; bento cell count equals content count with visual variation.
3. At most 2 consecutive image/text splits; no split-header.
4. Long lists use the right component, not a ruled `ul`.
5. Mobile collapse declared and checked at 375 px; no page-level horizontal scroll.

**E. Copy (10)**
1. Headlines at most 8 words, sub-paragraphs at most 25 words.
2. Zero dash characters; one label per CTA intent.
3. No filler verbs, slop names, Jane Doe, fake-precise numbers.
4. None of the performative tells (section numbers, step labels, locale strips, scroll cues, version footers, "Field notes").
5. Quotes at most 3 lines, typographic quotes, name plus role.

**F. Motion (10)**
1. One signature effect plus motivated reveals; every animation justified in one sentence.
2. Only transform and opacity on the hot path; springs or strong ease-out; durations in range (150-300 ms micro, up to 400 ms complex).
3. Reduced-motion fallback on every animated element.
4. No scroll listeners, no `useState` per frame, no custom cursor, at most one marquee.
5. Motion claimed equals motion shown; cleanup in every effect.

**G. States, forms, interaction (10)**
1. Skeleton, empty and error states designed.
2. Active feedback (`translate-y-[1px]` or `scale-[0.98]`), hover plus pressed within about 100 ms, hover never the only signal.
3. Focus-visible ring on all interactive elements; Esc closes overlays; icon-only controls labeled.
4. Forms: label above, error below, validate on blur or submit, first invalid field focused.
5. Touch targets at least 44 px; bespoke CTA per intent, no global button style.

**H. Images and assets (10)**
1. Hero and 2-3 supporting images are real; none from picsum in the final.
2. Images sized (hero at most ~2000 px), preloaded hero, no layout shift.
3. Logo wall (if any) uses real SVG marks, logos only, no captions.
4. One icon family with a standard stroke; no hand-rolled paths; no emoji icons.
5. No pills over photos, no decorative attributions.

**I. Signature wow (10)**
1. Chosen from the catalog and defended against the concept spine.
2. Built fully, first paint complete.
3. Input-to-response feels physical (scrub 0.5-1, springs); no layout animation.
4. Reduced-motion static composed fallback exists and works.
5. Mobile degradation declared and implemented.

**J. Responsive, accessibility, performance (10)**
1. Works at 375 px, tablet and desktop; `dvh` not `vh`.
2. Dark/light tokens tested (if dual mode); AA contrast both ways.
3. LCP under 2.5 s plausible (hero preloaded, sized), CLS under 0.1 (space reserved), INP under 200 ms (no heavy main-thread work).
4. Semantic landmarks and heading order; alt text; keyboard path through the page.
5. Heavy libraries lazy-loaded; dependencies checked against `package.json`.

Grading: 90-100 ship; 75-89 fix the top three issues first; below 75 rework before showing it. Any failed hard gate overrides the score.

## 4. Scorecard template

```
# Scorecard: <project> (<date>)

Hard gates: G1 pass | G2 pass | ... | G17 pass   (failures: none | list)

| Category | Score /10 | Note |
|---|---|---|
| A Typography | | |
| B Color and materials | | |
| C Hero | | |
| D Layout and structure | | |
| E Copy | | |
| F Motion | | |
| G States and interaction | | |
| H Images and assets | | |
| I Signature wow | | |
| J Responsive, a11y, perf | | |
| Total | /100 | |

Top 3 fixes: 1) ... 2) ... 3) ...
Not verified: <real devices, Lighthouse, screen reader, motion feel, ...>
```

## 5. Pre-flight matrix (last filter before output)

Tick every box honestly; one false box means not done.

- Design Read declared; dials explicit and reasoned (not silently baseline).
- Design system chosen from `taste-rules.md` section 12 if applicable, or the aesthetic is labeled honestly; one system per project.
- Redesign mode detected and audit done (if applicable).
- Page theme lock, color consistency lock, shape consistency lock.
- Button contrast and form contrast pass AA; CTA labels do not wrap.
- Serif discipline (not Fraunces or Instrument Serif; a different serif from the previous project); premium-consumer palette check against the beige-brass family.
- Italic descender clearance.
- Hero fits the viewport, top padding at most 96 px, at most 4 text elements.
- Eyebrow count within budget; no split-header; no zigzag run of 3; no duplicate CTA intent; logo wall is logos only and sits below the hero.
- Bento background diversity and exact cell count; long lists use the right component.
- Real images used; no fake screenshots, no pills over images, no decorative attributions, no version footers, no micro-meta sentences, no hero-bottom strip, no floating top-right sub-text, no filled-track progress bars, no locale strips, no scroll cues, no hero version label, no section numbering, no decorative dots.
- Content density sane (no 20-row tables), quotes at most 3 lines.
- Motion motivated; one marquee at most; motion claimed equals motion shown; sticky-stack and horizontal-pan follow the canonical skeletons; no scroll listener; reduced motion wrapped; effect cleanups present.
- Dark mode tokens tested; mobile collapse explicit; `dvh` used; empty/loading/error provided; cards omitted where spacing works; icons from an allowed family; motion isolated in client leaves.
- No AI tells from `taste-rules.md` section 11; Core Web Vitals plausibly hit.
