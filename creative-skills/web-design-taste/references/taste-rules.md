# Taste rules

Contents:
1. Typography
2. Color and materials
3. Layout, spacing and structure
4. Hero discipline
5. Copy
6. Motion
7. States, forms and UX craft
8. Images, icons, logos
9. Dark mode and themes
10. Performance and accessibility
11. AI tells (forbidden patterns)
12. Design-system routing, stack conventions, glass approximation

Tailwind reference values used below: text-4xl 36 px, text-5xl 48, text-6xl 60, text-7xl 72, text-8xl 96; tracking-tighter -0.05em; leading-none 1, leading-tight 1.25, leading-relaxed 1.625; spacing unit 4 px (`gap-6` 24 px, `py-16` 64, `py-24` 96, `py-32` 128, `py-48` 192, `pt-24` 96); breakpoints sm 640, md 768, lg 1024, xl 1280, 2xl 1536. Plain CSS users: use the px values.

## 1. Typography

- **Display:** `text-4xl md:text-6xl tracking-tighter leading-none` (36 px mobile, 60 px desktop, -0.05em, line-height 1) as the base scale. `text-6xl md:text-7xl` (72 px) only when the headline is 3-5 words. For most heroes the range is `text-4xl md:text-5xl lg:text-6xl`. A 4-line hero headline is a font-size error, never a copy-length error. Plan font size and image size together: a large hero asset plus a headline over 6 words means do not start at `text-7xl/8xl`.
- **Body:** `text-base leading-relaxed max-w-[65ch]` (16 px, 1.625, 65 characters per line max), muted gray rather than black.
- **Control hierarchy with weight and color, not raw scale.** No oversized H1s that just scream.
- **Fonts, sans first.** Pairings: Geist plus Geist Mono; Satoshi plus JetBrains Mono; Cabinet Grotesk plus Inter Tight; Outfit plus IBM Plex Mono; GT America plus IBM Plex Mono; GT Walsheim or PP Neue Montreal plus a mono. Display sans options: Geist Display, ABC Diatype, Sohne Breit, Cabinet Grotesk Display, Migra Sans, GT Walsheim, PP Neue Montreal. Inter as display is banned unless the brief wants neutral, Linear-style or public-sector accessibility.
- **Serif is very discouraged as the default.** "Creative or premium means serif" is the most-tested AI tell. Serif only when the brief names one, or the brand is genuinely editorial, luxury, publication, manuscript, heritage or vintage and you write the justification into the brief. Fraunces and Instrument Serif are banned as defaults. If a serif is justified, rotate (do not reuse across consecutive projects) from: PP Editorial New, GT Sectra Display, Cardinal Grotesque, Reckless Neue, Tiempos Headline, Recoleta, Cormorant Garamond, Playfair Display, EB Garamond, IvyPresto, Migra, Editorial Old, Saol Display, Domaine Display, Canela, Schnyder, Tobias, NB Architekt, ITC Galliard. Not for dashboards.
- **Emphasis inside a headline:** italic or bold of the same family. Never inject a serif word into a sans headline (or the reverse) for visual interest.
- **Italic descender clearance:** italic display words containing y, g, j, p, q need `leading-[1.1]` minimum plus `pb-1` reserve on the wrapper, or the descender clips. Audit every italic word in display headlines.
- **No excessive gradient text** on large headers.
- **Numbers:** `tabular-nums` for counters, prices, timers and table columns; mono for all numbers at density 8+.
- **Polish and other diacritics:** check the font has Latin Extended coverage (ą ć ę ł ń ó ś ź ż) before locking a pairing; a fallback font on one letter looks like a bug.
- **Fonts delivery:** self-host with `@font-face` and `font-display: swap` (or `@fontsource/*`). Do not link Google Fonts via `<link>` in production.
- Wrap rather than truncate; when truncating use `truncate` plus a `title` with the full value.
- Long headings: `text-wrap: balance`; body: `text-wrap: pretty`.

## 2. Color and materials

- **Exactly one accent color**, saturation under 80%, locked page-wide. A rose-accented site does not get a teal badge in the footer. Audit every component before shipping.
- **Neutral base** from one family only (zinc, slate or stone; warm or cool, never both). No pure `#000000` and no pure `#ffffff`: use off-black (zinc-950 or a near-black warm gray) and off-white. Pure values kill depth.
- **No neon or outer glows** by default; use inner borders and subtly tinted shadows. Shadows are tinted to the background hue; no pure-black drop shadows on light backgrounds.
- **No AI-purple/blue glow** (the "Lila rule"): no automatic purple button glows, no random neon gradients. If the brand is purple, embrace it with a consistent palette, harmonized neutrals and restrained gradients.
- **Banned default palette families:** see `design-recipe.md` section 5 (graphite plus orange, near-black plus neon, beige plus brass plus espresso, AI purple, previous build's family). Rotate instead.
- **Page theme lock:** one theme per page. A dark page is dark in every section; tint shifts within the family (`zinc-950` next to `zinc-900`) are fine; a warm-paper section sandwiched into a dark page is broken. Exception: one deliberate, strongly transitioned theme switch ("color block story") once per page.
- **Shape consistency lock:** one corner-radius language: all sharp (0), all soft (12-16 px), or all pill for interactive elements. A mixed system is allowed only with a written rule (for example buttons full-pill, cards 16 px, inputs 8 px) followed everywhere.
- **Materiality:** cards only where elevation communicates hierarchy; otherwise group with `border-t`, `divide-y`, or negative space. For density above 7, generic card containers are banned. No nested card-in-panel-in-frame stacks (anti-nested-box): get depth from ONE surface change.
- **Grain/noise:** only on fixed, `pointer-events-none` pseudo-elements, never on scrolling containers.
- **Contrast:** WCAG AA minimum: 4.5:1 for body, 3:1 for large text (18 px and up). AAA target for hero copy. Button labels, ghost buttons over photos (use a scrim or stroke), form inputs, placeholders, focus rings, helper and error text all pass AA against their own background. White label on white CTA is a gate failure.

## 3. Layout, spacing and structure

- **Containers:** `max-w-[1400px] mx-auto` or `max-w-7xl` (1280 px). Side gutters at least 16 px on mobile (`px-4`).
- **Grid over flex-math:** never `w-[calc(33%-1rem)]`; use `grid grid-cols-1 md:grid-cols-3 gap-6`.
- **Viewport:** `min-h-[100dvh]`, never `h-screen`/`100vh` (mobile URL-bar jump).
- **Rhythm:** section padding by density: airy `py-32` to `py-48` (128-192 px), standard `py-16` to `py-24` (64-96 px), tight at density 8+. Use a consistent scale (4, 8, 12, 16, 24, 32, 48, 64, 96, 128). Generous spacing in a reference never collapses into default tight spacing.
- **Anti-center bias** when variance is above 4: split screen 50/50, left content with right asset, asymmetric white space, scroll-pinned structures. Centered is fine for editorial, manifesto or launch pages where the message is the design.
- **Section-layout repetition ban:** each family (3-col cards, split text+image, full-width quote, bento, marquee, sticky stack...) at most once; 8 sections need at least 4 families.
- **Zigzag cap:** at most 2 consecutive image/text split sections; the third is a failure.
- **No 3-column equal feature cards.** Use a 2-column zigzag (at most 2 in a row), asymmetric grid, scroll-pinned, or horizontal scroll.
- **Bento:** exactly as many cells as content items (3 items means 3 cells; no blank filler), rhythm (alternate full-width feature rows with tile sizes), and 2-3 cells with real visual variation (image, brand gradient, pattern, tint). Six white-on-white text cards read as the AI default.
- **Split-header ban:** "left giant headline plus right floating small paragraph" is banned by default; stack the headline and body vertically (body max 65ch).
- **Eyebrow restraint:** max 1 eyebrow per 3 sections, hero counts. Mechanical check: count small uppercase wide-tracking labels above section headlines; fail if count exceeds ceil(sections / 3). If section A has one, the next two do not. Drop the eyebrow rather than decorate.
- **Long lists need a different component, not a longer list.** More than 5 items: 2-column grouped split, card grid with image and label, tabs or accordion, horizontal scroll-snap pills, carousel (testimonials, logos), or a marquee. A spec table with a hairline under all 10 rows is the worst default: group into 2-3 chunks with sparse dividers, a 2-column card grid (name, large value, one-line "why it matters"), or featured-vs-rest (3-4 large tiles, the rest under "View full specifications"). `border-t` plus `border-b` on every row is banned.
- **No data dumps** on marketing pages: 20-row tables, 30-row award lists. Show top 3-5 plus a link, a marquee, or another page.
- **Nav:** one line at desktop (1024+), height at most 80 px (default 64-72). If items do not fit, condense labels, drop secondary items, or use a hamburger.
- **Mobile collapse:** declare the below-768 px fallback per multi-column section in the same component; asymmetric layouts become `w-full px-4 py-8` single columns.
- **Z-index restraint:** only for systemic layers (sticky nav, modals, overlays, grain), documented as a scale in one constants file. No arbitrary `z-[9999]`.
- Backgrounds vary per section (solid plus asset, duotone image, color-blocked diptych, graded photo, flat block plus detail crop) while the theme stays locked.

## 4. Hero discipline

- Fits the first viewport: headline max 2 lines (desktop), subtext max 20 words and 3-4 lines, CTA visible without scrolling. If the copy is too long: reduce the type scale or cut copy; if you cannot state the value in 20 words, the value is unclear.
- Top padding max `pt-24` (96 px). More means the hero floats halfway down the viewport. Need more air: raise the font scale or the asset size.
- Max 4 text elements: eyebrow OR brand strip OR neither (zero or one), headline, subtext, CTA row (1 primary, max 1 secondary). If an eyebrow and a tagline compete, drop the tagline.
- Banned inside the hero: tagline below the CTAs ("Works with GitHub, GitLab..."), trust micro-strip ("Used by teams at..."), pricing teaser, feature bullets, avatar rows, version labels (`V0.6`, `BETA`, `INVITE-ONLY PREVIEW`, `EARLY ACCESS`), "Brand · No. 01" micro-meta, decoration text strip at the hero bottom (`BRAND. MOTION. SPATIAL.`), scroll cues.
- "Used by / Trusted by" logo wall sits in its own section directly below the hero.
- Real visual required (see section 8). Text plus gradient blob is a placeholder.
- Hero architectures to choose from: asymmetric split, editorial manifesto (large type, no asset, poster-like), video/media mask (type as a mask over video), kinetic type, curtain reveal, scroll-pinned hero.
- Preload the hero image (`<link rel="preload" as="image">`) for LCP.

## 5. Copy

- Headline max 8 words; sub-paragraph max 25 words; per section one visual OR one CTA.
- **Em-dash and en-dash-as-separator are completely banned** anywhere visible: headlines, eyebrows, pills, body, quotes, attribution, captions, buttons, nav, alt text. Use period, comma, colon, parentheses or hyphen (`-`). Date and number ranges use a hyphen (`2018-2026`, `40-80k`). Zero tolerance: a single em-dash character on the page fails the gate. (Code comments are exempt.)
- **One label per CTA intent page-wide.** "Get in touch" plus "Contact us" plus "Let's talk" on one page is a fail; pick one and reuse it in nav, hero and footer. Same for signup intent ("Try free", "Get started", "Sign up free") and portfolio intent. Distinct intents (book vs walk in) may differ.
- Primary CTA max 3 words, one line at desktop (shorten, or widen the button; do not cap `max-width` on CTAs).
- No filler verbs: Elevate, Seamless, Unleash, Next-Gen, Revolutionize. Use concrete verbs.
- No startup-slop names (Acme, Nexus, SmartFlow, Cloudly), no "Jane Doe"/"John Doe"/"Sarah Chan" testimonials, no generic egg avatars; invent contextual, locale-appropriate names and believable photos.
- **No fake-perfect numbers:** avoid `99.99%`, `50%`, `1234567`; avoid invented marketing stats (`92% faster`, `4.1x ROI`, `10k+ teams`) unless real, sourced, or labeled mock. Carve-out: invented product facts (prices, spec values, batch counts, dimensions) are required content for a fictional-brand brochure; keep them plausible and internally consistent. Organic data looks like `47.2%` or `+1 (312) 847-1928`.
- No performative-craftsman labels ("Field notes", "Currently on the bench", "On our desks", "Quietly trusted by", "Quietly in use at"), no "We respect the French ones" mock humility, no micro-meta-sentences under eyebrows, no section numbering (`001 · Capabilities`, `00 / INDEX`), no generic step labels (Stage 1, Step 1, Phase 01, Pass One; name the step: Install, Configure, Ship), no `01 / 4` pagination on tiles, no locale/weather/time strips ("LIS 14:23 · 18°C") unless the brief is about a place, no version footers (`v1.4.2`, `Build 0048`, `last sync 4s ago`) on marketing pages, no "Reservation 412 of 800" counters.
- **Quotes:** max 3 lines of body, real typographic quotes (not straight ASCII), attribution = name plus role (plus optional company), never name only.
- **One copy register per page:** do not mix technical mono, editorial prose and marketing punch unless the brand voice calls for it.
- **Copy self-audit before shipping:** re-read every visible string (headlines, subheads, eyebrows, buttons, body, captions, alt text, footer, errors). Rewrite anything grammatically broken, with unclear referents, that sounds like AI hallucination (cute-but-wrong wordplay, forced metaphors), or like an LLM trying to sound thoughtful. When unsure, use a plain functional sentence. Plain beats cute.
- Middle dot `·`: at most 1 per metadata line. No decorative colored status dots (only for real semantic state, one per section at most).
- No `<br>`-split italicized headlines as a default move, no vertical rotated text unless the brief is explicitly agency/experimental, no crosshair or hairline grid lines as pure decoration.

## 6. Motion

- **One signature/hero effect per page** (chosen from `wow-catalog.md`) plus motivated reveals. Before adding any animation answer "what does this communicate?": hierarchy, storytelling, feedback, or state transition. "It looked cool" means drop it. GSAP everywhere because it is available is amateur.
- **Timings:** micro-interactions 150-300 ms; complex transitions up to 400 ms; exits about 60-70% of enter duration; ease-out on enter, ease-in on exit; stagger list entrances 30-60 ms per item; animate 1-2 key elements per view; never block input while something animates.
- **Easing:** `cubic-bezier(0.16, 1, 0.3, 1)` for reveals; springs `type: "spring", stiffness: 100, damping: 20` over linear. Scroll scrub `scrub: 0.5-1`.
- **Hot path:** animate only `transform` and `opacity`; never `top/left/width/height`; `will-change: transform` sparingly; no layout shift.
- **Reveal defaults:** y offset 24 px, duration 0.6 s, `viewport amount 0.3`, once. Lighter alternative to GSAP for simple "enter on scroll".
- **Cursor and pointer physics** (magnetic buttons, tilt) via `useMotionValue`/`useTransform`, never `useState` (re-renders collapse on mobile). Only at MOTION above 5 and a premium, playful or agency brief.
- **Perpetual loops** (pulse, shimmer, float, carousel) only where the section benefits (live status, feeds); informational sections stay still. Marquees: at most ONE per page.
- **Forbidden:** `window.addEventListener("scroll", ...)`; scroll progress in React state via `window.scrollY`; `requestAnimationFrame` loops touching React state; custom mouse cursors (accessibility- and perf-hostile; allowed only when the brief mandates a spectacle-tier cursor).
- **Libraries:** Motion (`motion/react`) for UI and state-change motion; GSAP plus ScrollTrigger for scrolltelling and pinned scrubs, isolated in leaf components with cleanup; Three.js/WebGL for canvas scenes, lazy-loaded. Never mix GSAP/Three with Motion in one component tree (they fight over frames). Layout transitions: Motion `layout`/`layoutId` only for visible state changes, not "for safety". Stagger via `staggerChildren` or CSS `animation-delay: calc(var(--index) * 100ms)`.
- **Reduced motion is mandatory above MOTION 3:** `useReducedMotion()` or `@media (prefers-reduced-motion: reduce)`; infinite loops, parallax, scroll hijack and magnetic physics collapse to static or instant.
- **Screenshot-safe:** the initial state must be fully rendered. Nothing sits at `opacity: 0` waiting for a viewport trigger; animate from visible states (offset, blur) or fire on mount. Videos need a `poster`.
- If motion cannot be finished properly in scope, ship a clean static page instead of half-wired ScrollTriggers.
- Effects with `useEffect` need strict cleanup.

## 7. States, forms and UX craft

- **Full state cycles, not just the happy path:** skeleton loaders shaped like the final layout (not generic spinners), composed empty states with a way to populate them, inline error states; toasts only for transient messages (3-5 s, with an action when useful, never stealing focus).
- **Tactile feedback:** `:active` uses `-translate-y-[1px]` or `scale-[0.98]`; every clickable element shows hover and pressed feedback within about 100 ms; hover is an enhancement, never the only signal (mobile has no hover).
- **Touch targets** at least 44x44 px, at least 8 px apart. Small icons get padding, not bigger glyphs.
- **Async actions:** disable the trigger and show progress; anything over about 300 ms shows a skeleton; mutations feel instant (optimistic update, reconcile, Undo toast for destructive/bulk operations).
- **Focus and keyboard:** `:focus-visible` ring on every interactive element, never remove outlines, tab order matches visual order, no positive `tabindex`. `Esc` closes the topmost overlay one layer at a time; modals trap focus and restore it to the trigger; icon-only controls carry `aria-label`; decorative images `alt=""`. Do not convey state by color alone (pair with icon or label).
- **Bespoke chrome:** no site-wide shared button style. Each CTA is its own component with its own interaction identity (see garment catalog in `image-to-code.md`). A page of identical pills is a gate failure. No `.btn-primary` global utility.
- **Forms:** label ABOVE input, helper text optional but present in markup, error BELOW the field (`gap-2` input blocks), never placeholder-as-label. Validate on blur or submit, not per keystroke; error states cause plus fix ("Prompt is empty: describe what to generate"); first invalid field gets focus; semantic input types and autocomplete attributes; submit ends in a visible outcome (success state or error with retry; a timeout is an error with retry). Multi-step flows show progress and allow going back; confirm before dismissing unsaved input.
- **Layout craft for app surfaces:** mobile-first; no page-level horizontal scroll (wide content scrolls inside its own `overflow-x-auto`); `min-w-0` plus `truncate` plus `max-w-*` plus `minmax(0,1fr)` so content never overlaps; fixed bars reserve space (`pb-*`) and respect safe areas; one primary CTA per screen, secondary actions visually subordinate; current location always visible; verify at 375 px, tablet and desktop.
- **Charts (dashboards only):** trend is a line, comparison a bar, proportion a donut (5 slices max, else bar); visible legends, tooltips, low-contrast gridlines, `tabular-nums`; skeleton while loading, designed empty state, error with retry.

## 8. Images, icons, logos

- **Priority for visual assets:** (1) bespoke generated or designed assets for each section (hero photography, product shots, textures, mood images) at the right aspect ratio; (2) real brand URLs or assets from the brief; (3) clearly labeled TODO slots (`<!-- TODO: hero product photo, 1600x1200 -->`) and tell the user which placements need images. Placeholder photography: `https://picsum.photos/seed/{descriptive-seed}/{w}/{h}` only as a temporary stand-in, never the final asset. Do not rely on bare Unsplash links (they break).
- **Even minimalist sites need real images:** 2-3 minimum (hero, one product or lifestyle shot, one supporting image). Pure text is incomplete, not minimal. Restrained brief: generate black-and-white minimalist photography.
- **Generation prompts for web assets:** "no text, no logos, no watermark" (IP-safe and lets you set live type in HTML); match palette and mood to the brief; hero images at most about 2000 px wide, cutouts about 800 px; for a monochrome look force grayscale in the prompt and on export.
- **Div-built fake screenshots are banned** (fake task lists, terminals, dashboards, version footers inside fake screenshots). Use a real screenshot, a generated image, a real component preview, or editorial photography, or skip the preview.
- **No pills or labels overlaid on photos** (`Brand · 02`, `PLATE · BRAND`, `Field notes - journal`). Let the image speak or put a one-line functional caption below the image. No decorative photographer attributions (`Field study no. 12 · Ines Caetano`); attribution only for a real photographer with permission.
- **Logo walls:** real SVG marks (Simple Icons CDN `https://cdn.simpleicons.org/{slug}/ffffff`, or the `simple-icons` package; devicon for tech stacks), logos ONLY with no category label under each, working in light and dark. Invented brands get an invented inline-SVG monogram, never a styled `<span>` wordmark.
- **Icons:** one family per project: Phosphor, HugeIcons, Radix Icons or Tabler (priority order); Lucide only on request or when the project already uses it. Never hand-roll SVG icon paths. Standardize `strokeWidth` globally (1.5 or 2.0). Never mix a generated icon set and a library set in one visual zone. Emoji discouraged in code, markup and visible text; allowed sparingly only for an explicitly playful or chat-style vibe; never as icons.
- **Hand-rolled decorative SVG illustrations:** strongly discouraged. Acceptable for one simple geometric mark, a wordmark in display type, or when the brief asks for it.

## 9. Dark mode and themes

- Design dual mode from the start for any consumer-facing page; never ship light-only or dark-only without the user's instruction (exception: print-emulating editorial or a brief that insists on one mode).
- Token strategy: pick one per project. Tailwind `dark:` variants (`bg-white dark:bg-zinc-950`), or CSS variables with semantic tokens (`--surface`, `--surface-elevated`, `--text-primary`, `--accent`) swapped under `[data-theme="dark"]` or `@media (prefers-color-scheme: dark)`.
- Enforce contrast (AA body, AAA target for hero copy), hierarchy parity (a CTA that pops in light pops in dark), brand fidelity (do not desaturate the brand into a dark mode), no pure black or white.
- Respect `prefers-color-scheme` by default; add a manual toggle if either mode would lose key brand expression. Test both modes before finishing.
- Inside design systems with built-in theming (Radix Themes, shadcn/ui `<Theme>`) set the theme once at the root.

## 10. Performance and accessibility

- Core Web Vitals targets: LCP under 2.5 s (preload the hero image), INP under 200 ms, CLS under 0.1 (reserve space for images, fonts, embeds). Run Lighthouse before declaring done.
- Lazy-load anything below the fold and heavy libraries (Three.js is large; Motion is not tiny).
- Dependency check: before importing any library, check `package.json`; if absent, print the install command first. Never assume a package exists.
- SSR safety (React frameworks with server rendering): no `window`, `document`, `localStorage` or `navigator` at module top level or during render; interactive code in isolated client leaves behind a mounted gate; WebGL components additionally `React.lazy`.
- Text alternatives, keyboard access, reduced motion and reduced transparency fallbacks are part of done.

## 11. AI tells (forbidden patterns)

Avoid unless the brief explicitly asks:

- Visual: neon/outer glows; pure black; oversaturated accents; gradient text on large headers; custom mouse cursors; glassmorphism on everything; centered hero over a dark mesh; infinite-loop micro-animations everywhere; Inter plus slate-900 as the whole identity.
- Typography: Inter as display; default serif; serif word in a sans headline; `<br>`-split italic headlines; vertical rotated text.
- Layout: three equal feature cards; mathematically perfect identical paddings with no tension; split-header; floating top-right sub-text in section headings; decoration strip at the hero bottom; scoring/progress bars with filled background tracks as comparison visuals (use a number plus small icon, or a tiny inline bar without a track); crosshair/hairline lines as decoration.
- Content: Jane Doe; Acme/Nexus; filler verbs; fake-precise numbers; section numbering; step labels "Stage 1"; micro-meta sentences; locale/weather strips; scroll cues ("Scroll", "Scroll to explore", mouse-wheel icons); version labels in the hero; version footers; live-stock counters.
- Assets: hand-rolled SVG icons; div-based fake screenshots; broken stock links; pills overlaid on photos; decorative status dots.
- Components: default-state shadcn/ui (customize radii, colors, shadows, typography); duplicate CTA intents; wrapped CTA labels.
- Process: a redesign without an audit; motion claimed but not shown.

## 12. Design-system routing, stack conventions, glass approximation

If the brief reads as an existing system, install and use the official package; do not recreate its CSS by hand and do not import its tokens then override 90% of them. One system per project (no Fluent plus Carbon, no shadcn inside a Material app).

| Brief reads as | Reach for |
|---|---|
| Microsoft / enterprise SaaS / dashboards | `@fluentui/react-components` or `@fluentui/web-components` |
| Google-ish, Material | `@material/web` plus Material 3 tokens |
| IBM-style B2B analytics | `@carbon/react` plus `@carbon/styles` |
| Shopify app surfaces | Polaris web components or Polaris React |
| Atlassian / Jira-style | `@atlaskit/*` plus `@atlaskit/tokens` |
| GitHub-style devtool or community page | `@primer/css` or `@primer/react-brand` |
| UK public-sector service | `govuk-frontend` |
| US public-sector / trust-first | `uswds` |
| Fast local-business or agency MVP | Bootstrap 5.3 |
| Accessible React foundation | `@radix-ui/themes` |
| Modern SaaS where you own the components | shadcn/ui (`bunx shadcn@latest add ...`), never in default state |
| Indie / small-team SaaS and AI marketing | Tailwind v4 utilities plus the `dark:` variant |

Aesthetics without an official system (build with native CSS plus Tailwind and label borrowed inspiration honestly): glassmorphism (`backdrop-filter`, layered borders, highlight overlays, solid fallback for `prefers-reduced-transparency`); bento (CSS Grid, mixed cells); brutalism (monospace, raw borders); editorial (serif, asymmetric grid, generous white space); dark tech (mono plus accent); aurora/mesh (SVG or layered radial gradients); kinetic typography (CSS, scroll-driven animations, GSAP for hijacks).

Stack defaults: React plus Tailwind v4 (with `@tailwindcss/postcss` or the Vite plugin, not the old `tailwindcss` PostCSS plugin) plus Motion (`import { motion } from "motion/react"`). Local state with `useState`/`useReducer`; global state only to avoid deep prop drilling (Zustand, Jotai, context). Continuous values driven by input (mouse, scroll, pointer physics) never in `useState`.

Glass approximation (not Apple's Liquid Glass; there is no official web CSS for it, label it as approximation): `backdrop-filter: blur(24px) saturate(180%) contrast(1.05)`; 1 px border `rgb(255 255 255 / .32)`; background `linear-gradient(135deg, rgb(255 255 255 / .30), rgb(255 255 255 / .08))` over `rgb(255 255 255 / .12)`; `box-shadow: inset 0 1px 0 rgb(255 255 255 / .48), inset 0 -1px 0 rgb(255 255 255 / .12), 0 18px 60px rgb(0 0 0 / .18)`; a `::before` radial highlight at 20% 0%; a dark variant with `rgb(15 23 42 / .42)` fill; under `@media (prefers-reduced-transparency: reduce)` a near-opaque `rgb(255 255 255 / .96)` fill with no blur (browser support is uneven; always keep enough contrast without the blur). Use for premium consumer, Apple-adjacent or media-overlay vibes; not for dashboards, public sector or boring B2B.

Scope: this skill is for marketing surfaces and app surfaces with taste. For dashboards, data tables, multi-step wizards, code editors, native mobile and realtime collaboration UIs say so explicitly and point to the right tool (an official design system, TanStack Table or AG Grid, Monaco/CodeMirror, Apple HIG/Material), applying only the landing and about-page parts here.
