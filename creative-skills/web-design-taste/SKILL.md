---
name: web-design-taste
description: "Tool-agnostic design taste for landing pages, web apps and small games that look designed, not AI-generated. Gives a design recipe (brief, dials, reference boards, tokens, build, review), taste rules with numbers (type scale, spacing, one accent, hero composition, motion timings, copy limits), anti-AI-slop ban lists, a wow-effect catalog, a scored review rubric and an image-to-code procedure from Figma or screenshots. Use whenever the user designs or codes a page, app screen or game UI, or says a result looks generic, even if they never name the skill. Trigger on: landing page, strona WWW, strona do apki, hero, typografia, paleta kolorów, \"wygląda jak AI\", AI slop, efekt wow, animacja na scrollu, z Figmy do kodu, screenshot do kodu, review designu, mała gra, UI gry. Route to viral-app-lab for the app concept, thumbnail-design for covers, caption-and-title-systems for video text."
---

# Web Design Taste

Make pages and small apps that read as designed by a person with taste: one clear idea, a locked system (one accent, one radius language, one type pairing), a real hero visual, motion that means something, and copy that sounds human. The rules exist because the default LLM output violates every one of them.

## When to use / when not

Use for: landing pages and portfolios for Mati's viral apps, app screens and tool UIs, marketing sections, redesigns, small browser games (UI and feel), and reviewing any of these. Also for turning a Figma frame or screenshot into code without design drift.

Do not use for: deciding what app to build or the viral moment (viral-app-lab), thumbnails and covers (thumbnail-design), on-video captions (caption-and-title-systems), backend, auth, SEO or infrastructure work. Dense dashboards and data tables have their own design systems: say so, pick an official system (see `references/taste-rules.md`, section 12) and apply this skill only to the marketing surfaces around them.

## Inputs to collect (ask only for what is missing; sensible defaults otherwise)

- Page kind: landing (SaaS, consumer, agency, event), portfolio, redesign, web-app screen, game. Default: landing page for an app.
- Audience and vibe words: "minimalist", "premium consumer", "playful", "Awwwards", "serious B2B", "Linear-style". The audience picks the aesthetic, not your taste.
- References: Figma file or node, screenshots, URLs, competitors. If a Figma design exists, it is the spec.
- Brand assets that exist: logo, colors, fonts, photography. In a redesign these are starting material.
- Stack: default React plus Tailwind (v4) plus Motion; plain HTML/CSS or another stack is fine, the rules carry over with the px values given.
- Quiet constraints (accessibility-first, regulated, kids): these override aesthetic preference.
- The one thing a visitor should remember (the signature moment). For Mati's viral apps this is usually the same moment shown in the video.

Ask at most one clarifying question, and only when the design read genuinely diverges (for example "closer to Linear-clean or Awwwards-experimental?"). Otherwise declare the read and go.

## Workflow

1. **Design Read (one line).** "Reading this as: <page kind> for <audience>, with a <vibe> language, leaning toward <system or aesthetic family>." Then set the three dials (DESIGN_VARIANCE, MOTION_INTENSITY, VISUAL_DENSITY, each 1-10; baseline 8/6/4) from the table in `references/design-recipe.md`.
2. **Commit the combinatorial pick** before any visuals: theme paradigm, background character, type character, hero architecture, section system, four signature components, narrative spine, one second-read moment (`references/design-recipe.md`). Write it into a design brief. A strong consistent combination beats a mash.
3. **Palette and type.** One neutral family (warm or cool), exactly one accent, saturation under 80%, no pure black or white. Pick a font pairing from the allowed list. Check the banned palette families (`references/taste-rules.md`) and differ from the previous build in this chat.
4. **Reference boards.** Design one image per section (Figma frame, or an image model such as Nano Banana Pro using the prompt recipe), landscape 16:9 or 3:2, never one tall full-page image. Look at every board and re-roll the generic ones (`references/design-recipe.md`, section on boards).
5. **Section plan.** One layout family per section, at least 4 distinct families for 6+ sections, eyebrow budget ceil(sections/3), max 2 consecutive image/text splits, a mobile collapse declared per multi-column section.
6. **Assets.** Hero needs a real visual (screenshot, photo, generated image, real component preview). Pure-text pages and div-built fake UI are incomplete. Generate or collect 2-3 real images even for minimalist pages.
7. **Pick the signature wow** from `references/wow-catalog.md` (one Tier-1 effect, defended in a sentence), with a reduced-motion and mobile fallback.
8. **Build faithfully.** From a Figma frame or screenshot follow `references/image-to-code.md`: extract tokens first, analyze each section, code section by section, compare to the board after each section. The board wins when your habit disagrees.
9. **Review.** Score the result with `references/review-rubric.md`; fix every hard-gate failure; do the copy self-audit; test both color modes and 375 px, tablet, desktop.
10. **Deliver** the brief, the code, and the scorecard. Say honestly what was not verified (real devices, Lighthouse, motion feel).

Rules that decide most outcomes:

- One accent color, locked page-wide. One theme per page (a dark page is dark in every section). One corner-radius language.
- Hero: at most 4 text elements (eyebrow or brand strip, headline, subtext, CTA row), headline at most 2 lines on desktop, subtext at most 20 words, CTA visible without scrolling, top padding at most 96 px (`pt-24`).
- Headline at most 8 words; sub-paragraph at most 25 words; quotes at most 3 lines; CTA labels at most 3 words and on one line.
- Never use the em-dash character or the en-dash as a separator anywhere visible on the page. Use period, comma, colon, parentheses or hyphen.
- No 3-column equal feature cards, no centered-hero-over-dark-mesh default, no AI purple glow, no Inter as display font by default, no serif by default.
- Animate transform and opacity only; spring or strong ease-out; every animation answers "what does this communicate?"; honor `prefers-reduced-motion` everywhere.
- Use `min-h-dvh` or `100dvh`, never `100vh`/`h-screen` for full-height sections.
- Copy is plain and specific. No "Elevate", "Seamless", "Unleash", no "Acme", no "Jane Doe", no invented marketing stats (`92% faster`) unless labeled mock.

## Output format

Produce a design brief first (markdown, fixed headings), then the build, then the scorecard.

```
# Design Brief: <project>

## Design Read
Reading this as: <page kind> for <audience>, with a <vibe> language, leaning toward <family>.

## Dials
DESIGN_VARIANCE <n> / MOTION_INTENSITY <n> / VISUAL_DENSITY <n>  (why)

## Identity axes (ledger)
| Axis | Choice | Previous build (if any) |
| Palette family | | |
| Type pairing | | |
| Hero architecture | | |
| Tier-1 wow technique | | |
| CTA garments | | |
| Corner/border language | | |

## Tokens
- Neutrals: bg <hex>, surface <hex>, border <hex>, text <hex>, muted text <hex>
- Accent (one): <hex>  (contrast on bg: <ratio>)
- Type: display <font> / body <font> / mono <font>; scale <px list>; tracking <em>; leading <n>
- Spacing scale: <px list>; section padding <px>
- Radius: <px or sharp or pill>   Shadow: <tinted rule>
- Motion: ease <curve>, durations <ms>, spring <stiffness/damping>

## Hero
<architecture, headline, subtext, CTA, visual asset, mobile behavior>

## Section plan
| # | Section | Job | Layout family | Background mode | Eyebrow? | CTA garment | Mobile collapse |

## Signature wow
<technique ID from the catalog, one-sentence defense, reduced-motion fallback, mobile degradation>

## Assets
| id | role | prompt or source | size/ratio |

## Copy
<exact headline, subtext, CTA labels (one label per intent)>
```

After the build, append the scorecard from `references/review-rubric.md` (hard gates pass/fail, soft items 0-2, total out of 100, top 3 fixes).

## Tool adapters

- **Figma:** the best place to design the section boards and tokens (variables for color, type styles, spacing). With the Figma MCP, read a frame with `get_design_context` and `get_screenshot`, and tokens with `get_variable_defs`; treat the generated code as a reference to adapt to the project's components, not final code. Poor fit for motion and scroll behavior: describe those in the brief.
- **Nano Banana Pro:** hero images, product shots, section plates, OG images. It renders quoted text well, but for web heroes prompt "no text, no logos, no watermark" so type stays live HTML. Also good for the per-section reference boards when no Figma design exists.
- **KLING / Seedance 2 / Higgsfield Cinema Studio:** hero loops and scroll-scrub films. Brief them with the footage contract in `references/wow-catalog.md` (one continuous move, centered subject, copy-safe background, no on-screen text). Poor fit for UI mockups; use Figma or screenshots.
- **Premiere / After Effects:** not for building pages. Useful for recording the finished page into a demo clip (screen recording, then captions via caption-and-title-systems).
- **Claude Code / any coding agent:** implement from the brief plus board images. Give it the brief file, token file and the image-to-code rules; ask it to run the mechanical greps in the rubric before delivering.

## QA checklist

- Design Read declared; dials explicit and reasoned.
- Palette: one accent, neutral base, no banned family, no pure black or white, contrast AA (4.5:1 body, 3:1 for text 18 px and larger).
- Typography: allowed pairing, no Inter display, no default serif, italic descenders cleared, body at most 65ch.
- Hero fits the first viewport with at most 4 text elements and a real visual.
- No em-dash or en-dash separator anywhere visible. Copy self-audit done.
- Layout: no repeated section family, no 3 equal feature cards, no split-header, eyebrow count within budget, nav on one line and at most 80 px.
- Motion: one signature effect, all animation motivated, only transform and opacity, reduced-motion fallback, nothing invisible waiting for a scroll trigger.
- States: loading, empty, error, focus-visible, active; touch targets at least 44 px.
- Both color modes tested (if dual-mode), 375 px / tablet / desktop checked, `dvh` not `vh`.
- Scorecard attached; unverified items named.

## References

- `references/design-recipe.md`: read first on every build; the steps, dials, combinatorial pick, reference boards, palette bans, design-brief fields.
- `references/taste-rules.md`: read while designing or coding; the full rules with numbers (type, color, layout, copy, motion, states, forms, images, icons, dark mode, performance), the AI-tells ban list, design-system routing.
- `references/wow-catalog.md`: read when choosing the signature effect; effect families with when-to-use, footage contract for scroll-scrub films, libraries, anti-convergence ledger.
- `references/review-rubric.md`: read before delivering; scored checklist with grep commands and the scorecard template.
- `references/image-to-code.md`: read when implementing from Figma, a screenshot or a board; token extraction, per-section analysis, anti-drift rules, bespoke CTA garments.
- `references/app-and-game-surfaces.md`: read for web-app screens (layouts, UX craft rules, states) and small games (design laws, feel, performance budget).
