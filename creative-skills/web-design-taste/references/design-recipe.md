# Design recipe

Contents:
1. Step order and what each step produces
2. Brief inference and the three dials
3. The combinatorial pick (commit before visuals)
4. Reference boards (design the page as images first)
5. Palette bans and what to reach for
6. Hero and section rules in short form
7. Anti-convergence ledger

This is the short, always-read version of the craft rules. `taste-rules.md` holds the long form. When the two disagree, this file wins.

## 1. Step order

| Step | Produces | Done when |
|---|---|---|
| 0. Brief inference | One-line Design Read, dial values | A reader could guess the page from the line |
| 1. Combinatorial pick | Choices per category written in the brief | Every category has exactly one pick |
| 2. Tokens | Palette (hex), type pairing, spacing, radius, motion | One accent, one radius language, contrast checked |
| 3. Boards | One image per section (Figma or image model) | Each board answers "what does the build copy from this?" |
| 4. Section plan | Table: section, job, layout family, background, CTA | At least 4 distinct families for 6+ sections |
| 5. Assets | Hero visual, 2-3 real images, icons, logos, OG image | Hero is a real visual, not a gradient blob |
| 6. Build | Code, section by section, faithful to the boards | Each section compared to its board |
| 7. Wow | One signature effect, built fully | Reduced-motion and mobile fallbacks exist |
| 8. Review | Scorecard from `review-rubric.md` | All hard gates pass |

Write the brief file first; code that is not traceable to the brief drifts.

## 2. Brief inference and dials

### Read the room before touching anything

Signals: page kind (landing SaaS/consumer/agency/event, portfolio dev/designer/studio, redesign preserve/overhaul, editorial); vibe words the user used; reference signals (URLs, screenshots, competitors); audience (B2B procurement vs design-conscious consumer vs recruiter scanning); existing brand assets; quiet constraints (accessibility-first, public sector, regulated, kids) which override preference.

State the Design Read in one line before generating anything. If the brief is ambiguous, ask exactly one question and only when the read genuinely diverges.

### The three dials

- `DESIGN_VARIANCE` 1 = perfect symmetry, 10 = artsy chaos. Baseline 8.
- `MOTION_INTENSITY` 1 = static, 10 = cinematic physics. Baseline 6.
- `VISUAL_DENSITY` 1 = art gallery, 10 = cockpit. Baseline 4.

Baseline 8 / 6 / 4 unless the read overrides it.

| Signal | VARIANCE | MOTION | DENSITY |
|---|---|---|---|
| minimalist, clean, calm, editorial, Linear-style | 5-6 | 3-4 | 2-3 |
| premium consumer, Apple-y, luxury, brand | 7-8 | 5-7 | 3-4 |
| playful, wild, Dribbble, Awwwards, experimental, agency | 9-10 | 8-10 | 3-4 |
| landing page, portfolio, marketing site (default) | 7-9 | 6-8 | 3-5 |
| trust-first, public sector, regulated, accessibility-critical | 3-4 | 2-3 | 4-5 |
| redesign, preserve | match existing | +1 | match existing |
| redesign, overhaul | +2 | +2 | match existing |

Use-case presets (VARIANCE / MOTION / DENSITY): SaaS landing 7/6/4; agency or creative landing 9/8/3; premium consumer landing 7/6/3; designer or studio portfolio 8/7/3; developer portfolio 6/5/4; editorial or blog 6/4/3; public-sector service 3/2/5.

What the dials mean in practice:

- VARIANCE 1-3: symmetrical 12-col grid, equal paddings, centered. 4-7: overlaps (`margin-top: -2rem`), mixed aspect ratios (4:3 next to 16:9), left-aligned headers over centered data. 8-10: masonry, fractional grids (`2fr 1fr 1fr`), large empty zones (`padding-left: 20vw`). For levels 4-10, asymmetric layouts collapse to a strict single column below 768 px.
- MOTION 1-3: no automatic animation, only hover and active states. 4-7: fluid CSS, `transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1)`, cascaded load-ins on transform and opacity. 8-10: scroll-triggered choreography, parallax, scroll-driven animation. Motion claimed must be motion shown: a static page that claims 7 is broken; if you cannot ship working motion, drop the dial to 3 and ship a clean static page.
- DENSITY 1-3: huge section gaps (`py-32` to `py-48`, 128-192 px). 4-7: standard (`py-16` to `py-24`, 64-96 px). 8-10: tight paddings, no card boxes, 1 px lines separate data, mono font for all numbers.

Redesigns: detect the mode first (greenfield, preserve, overhaul). Audit before touching: brand tokens, information architecture, content blocks, patterns to keep and retire, dial reading of the old site, SEO baseline. Never change silently: URLs and slugs, primary nav labels, form field names and order, the logo, legal/consent copy. Modernization levers in order: typography refresh, spacing and rhythm, color recalibration, motion layer, hero recomposition, full block replacement.

## 3. The combinatorial pick

Pick ONE option per category, write the pick into the brief, hold it across all boards and sections. Do not mash categories.

- **Theme paradigm:** Pristine Light (paper, off-white, dark ink) / Deep Dark (charcoal, graphite; most overused, needs a twist) / Bold Studio Solid (oxblood, royal blue, forest, vermilion, emerald fields) / Quiet Premium Neutral (bone, sand, taupe, stone, smoke).
- **Background character:** technical grid or dot field / solid with soft ambient depth / full-bleed cinematic imagery / tactile paper or material texture.
- **Typography character:** clean grotesk (Satoshi-like) / refined grotesk (Neue-Montreal-like) / expressive display (Cabinet or Clash-like) / compressed statement (Monument-like) / editorial serif plus sans pairing / Swiss rational sans with hard hierarchy.
- **Hero architecture:** cinematic centered minimalist / asymmetric split / floating polaroid scatter / inline typography behemoth / editorial offset / massive image-first with restrained text.
- **Section system (dominant):** modular bento rhythm / alternating editorial blocks / poster-stacked storytelling / gallery-led cadence / Swiss grid discipline / asymmetric premium flow.
- **Signature components (pick 4):** diagonal staggered masonry / 3D cascading card deck / hover-accordion slices / gapless bento / brand marquee / turning polaroid arc / vertical rhythm lines / off-grid editorial / product UI panel stack / split testimonial wall / oversized metrics strip / layered image crop frames.
- **Narrative spine (pick 1, thread everywhere):** artifact or collectible / journey or waypoints / tool or precision instrument / living system or garden / stage or spotlight / archive or dossier.
- **Second-read moment (pick exactly 1, place once):** asymmetric bleed / one oversized numeral or punctuation as structure / one material switch / narrow vertical side-rail note / macro crop carrying the brand color.

Per-section variety is mandatory: each board picks its own composition anchor (centered statement, top-left lead, bottom-left over image, off-grid offset, stacked center, image-as-canvas, inverted classic); at least 3 distinct anchors across the site; the hero does not open on left-text/right-image unless it is genuinely best (that is the most overused AI pattern; use it at most once). Background mode varies per section (solid plus inline asset, duotone image, color-blocked diptych, graded atmospheric photo, flat block plus detail crop). CTA garments vary per section (see `image-to-code.md`).

For Mati's viral apps: the narrative spine is usually the app's single trick (the "artifact" or "tool" spines fit best), and the second-read moment should echo the shareable output.

## 4. Reference boards

The boards are the design. A generic board guarantees a generic site and no code craft recovers from it.

Rules:
- One horizontal image per section (16:9 or 3:2). 6 sections means 6 boards. Never one tall full-page image (detail goes mushy and composition variety dies).
- Source: your Figma frames (best), or an image model run at its highest quality setting. Name the real content in the prompt (the actual headline) so type sits believably.
- Prompt recipe per board: "website design mockup, desktop landing page section, [SECTION ROLE], [theme paradigm + exact palette words], [typography character] typography, [hero architecture / composition anchor], [background mode], [narrative spine motif], professional layout, clear hierarchy and spacing, award-winning web design, no watermark, no browser chrome".
- Re-roll rule: look at every board and ask "would this survive on a studio's portfolio page, or does it read as a template?" Generic means: centered dark hero, glowing gradient blob, default card trio, dashboard spam, beige serif "luxury". Re-roll with an escalated direction (push the composition anchor harder or swap the background mode). Budget: up to 2 re-rolls per board; a board that fails twice means change the category pick, not just the wording.
- Hero-board minimalism: at most 4 text elements (eyebrow or nothing, headline, one sub-line, CTA); no feature lists, no floating UI clutter; typography is the design; one focal visual or decisive negative space; no fake dashboards unless the product has a UI.
- Each board must communicate: layout grid, section hierarchy, spacing rhythm, type scale relationships, palette and accent placement, CTA priority, component styling, image treatment. A board that cannot answer "what does the build copy from this?" is mood art; re-roll it.
- Page chrome inside a section board (nav bars, footer fragments, slivers of neighbor sections) is non-normative; only the section's own content binds. Boards also draw too many uppercase eyebrows; the page's eyebrow budget wins.

## 5. Palette bans

Banned as default reaches (override only when the user's brand names those colors, justified in the brief):

1. Graphite or near-black plus orange/amber/ember accent (`#ff5c1a #ff6b35 #e8590c #f97316 #ea580c #d9480f` on `#0a0a0a`-family grounds).
2. Near-black plus neon cyan/blue/green accent (`#00e5ff #22d3ee #00ff88 #4ade80`, or `#3b82f6`-glow on dark; `#00FFC2` too).
3. Beige/cream plus brass/clay/oxblood plus espresso. Banned backgrounds `#f5f1ea #f7f5f1 #fbf8f1 #efeae0 #ece6db #faf7f1 #e8dfcb`; accents `#b08947 #b6553a #9a2436 #9c6e2a #bc7c3a #7d5621`; text `#1a1714 #1a1814 #1b1814`.
4. AI purple or violet glow (`#8b5cf6 #a855f7 #7c3aed` gradients).
5. The palette family of your previous build in the same chat.

Reach for instead (examples, not a menu; derive from the brief's material world first, and do not default to the first item): Cold Luxury (silver, chrome, smoke); Forest (deep green, bone, amber); Black and Tan; Cobalt plus Cream; Terracotta plus Slate; Olive plus Brick plus Paper; monochrome plus one saturated pop; Bold Studio Solid fields (bottle green, oxblood, royal blue, vermilion); chromatic lights (limestone, celadon, warm grey plus one unexpected saturated accent: chartreuse, vermilion-pink, ultramarine); duotone photographic palettes. One accent, decisive, defended in one line in the brief.

"Heritage" for a serif means a real editorial, luxury or legacy institution. A business being a few years old ("est. 2015") or in a traditional trade (barber, bakery, tailor) does not qualify; those default to sans.

## 6. Hero and section rules (short form)

- Hero fits the initial viewport: headline max 2 lines on desktop, subtext max 20 words and 3-4 lines, CTA visible without scrolling, top padding max `pt-24` (96 px).
- Hero text elements, max 4: (0-1) eyebrow or brand strip, (1) headline, (1) subtext, (1) CTA row (1 primary plus max 1 secondary). Banned in the hero: tagline under the CTAs, trust micro-strip, pricing teaser, feature bullets, avatar rows, version labels (`BETA`, `v2.0`), "Brand · No. 01" micro-meta. Logo walls live in their own section below.
- The hero needs a real visual. Div-built fake product UI (fake task list, fake terminal, fake dashboard) is the number one LLM tell: use a real screenshot, generated image, real component preview, or nothing.
- Anti-center bias: unless the brief is editorial or a manifesto, prefer split 50/50, left content with right asset, or asymmetric composition over the centered stack.
- Section-layout repetition ban: each layout family at most once per page; 6+ sections need at least 4 families; at most 2 consecutive image/text zigzag splits.
- Eyebrow ration: max 1 eyebrow per 3 sections (hero counts). Prefer dropping the eyebrow.
- No 3 equal feature cards. Bento has exactly as many cells as content items and 2-3 cells with real visual variation.
- Cards only where elevation means hierarchy; otherwise `border-t`, `divide-y` or negative space. One radius language per page.
- Nav on a single line at desktop, height at most 80 px (default 64-72). Mobile collapse declared per multi-column section.

## 7. Anti-convergence ledger

Before the brief locks, list what the previous build in this chat used for six identity axes, then differ on at least four: (1) palette family, (2) type pairing (no repeat of the exact display face two builds running), (3) hero architecture, (4) Tier-1 wow technique, (5) CTA garment set (zero overlap), (6) corner and border language (sharp, soft, pill, hairline-ruled). First build in a chat: derive all six from the brief's material world (the nouns the business actually touches: steel, paper, steam, moss, vinyl) and say so. With no previous build, the enemy is the model's own statistical default: if a choice would look at home in a generic template, re-roll it.
