---
name: brand-identity-kit
description: >-
  Builds or extends a brand identity and its applications, tool-agnostic: brand intake interview, Brand Lock (what is fixed vs proposed), 3 palette options, 3 logo concepts with ready-to-paste logo prompts (enhancer grammar), typography pairs, concept boards, then application prompts for mockups, merchandise, packaging, signage, social graphics, posters and a presentation deck, plus a brandbook outline and a QA loop. Use whenever the user wants a logo, visual identity, brand kit, brand guidelines, palette or font pairing, or wants an existing logo applied consistently onto physical or digital assets, even if they do not say "brand kit". Output is prompts and briefs ready to paste into Nano Banana Pro, plus Figma/Illustrator build steps. Trigger on: logo, identyfikacja wizualna, brandbook, księga znaku, manual marki, paleta kolorów, dobór fontów, makieta, mockup, opakowanie, szyld, gadżety, wizytówka, zrób mi branding, stwórz markę, zastosuj logo na, brand kit, brand guidelines. Not for ad creatives with copy (use static-ad-creatives), not for unbranded product photography or video; route those to the matching sibling skill.
---

# Brand Identity Kit

Create a consistent system of graphic materials. Treat the user's brand facts and supplied assets as constraints, not raw material to reinterpret. The craft here comes from one idea: decide the brand once (the Brand Lock), then make every asset consume the same lock, changing only content, format and composition.

## When to use / when not

Use for:
- a new logo or visual identity (only when the user explicitly wants one created)
- extending a partial identity (has a logo, needs palette or type, or the reverse)
- applying an existing identity onto mockups, merch, packaging, signage, social graphics, posters, decks
- a brandbook outline, palette or font recommendations, concept boards

Do not use for:
- ad creatives with headline/primary text/CTA: use `static-ad-creatives`
- unbranded product photography or packshots: use a product photography skill
- brand strategy (mission, values, naming, tone of voice) unless the user explicitly asks for it. Default to graphic production, not strategy.
- website implementation or video

Scope guard: use supplied positioning, audience, tone, copy, logo, colors, fonts and references as authoritative. Do not invent or rewrite them. Create a new logo only when asked.

## Inputs to collect (ask only for what is missing; sensible defaults otherwise)

Parse the first message and any attachments before asking anything. Ask ONE compact message with only the genuinely blocking gaps; never repeat what was already answered and never run a full questionnaire for a partial task. Gap checklist (full wording in `references/intake-and-brand-lock.md`):

1. Brand or product name (exact spelling)
2. What it offers, who for, key values or positioning
3. Route: new identity, or existing assets to keep and extend (if existing: which files are official logo, fonts, palette, guidelines)
4. Visual preferences and three sliders: Restrained to Expressive, Geometric to Organic, Familiar to Experimental (0 to 100, 50 if unsure)
5. Deliverables, formats, quantities, exact copy that must appear ("no text" is a valid answer)
6. For mockups and social: aspect ratio. For packaging, signage, merch: dimensions, material, production method.

Defaults when unanswered: sliders 50/50/50, one aspect ratio per set, flat vector logo treatment, two font families maximum.

## Workflow

1. **Classify the request.** `apply-existing` (new graphics from supplied assets), `extend-partial` (fill only missing visual decisions), `create-identity` (only on explicit request). Keep the deliverables named in the first message in scope until finished; do not ask the user to choose scope again.
2. **Intake** per the gap checklist. Normalize slider language to 0-100: strongly first = 0, mostly first = 25, balanced = 50, mostly second = 75, strongly second = 100.
3. **Analyze supplied assets** (read `references/intake-and-brand-lock.md`). Inventory, assign one role per asset, label evidence (source-declared, measured, visually-observed, inferred), and lock every user-declared official logo, palette and typography slot immediately. Official assets are never redrawn.
4. **Write the Brand Lock** (template below and in the reference). It is the single source of truth. Every field is `fixed`, `proposed`, `not_applicable` or `unknown`.
5. **Determine the minimum slots the output needs.** Never demand a full kit by default:
   - logo only: logo (a new logo needs a palette first)
   - palette only: palette
   - typography only: typography
   - symbol mockup, merch, copy-free packaging: logo (add palette if color decisions matter)
   - text-bearing social, packaging, poster, signage: logo + palette + typography
   - brandbook or deck: logo + palette + typography
6. **Build only the missing slots, in this order for a new identity: palette, then logo, then typography.** Each is a review with 2-3 options (palette), exactly 3 (logo) or 2-3 (type). After each review STOP and wait for the user's choice. A color preference in the intake is not a selected palette. Skip the stop only if the user said to choose for them ("dobierz sam"); then pick the strongest and say so. Read `references/design-brain.md` for how to generate options, `references/palette-typography.md`, `references/logo-and-prompt-enhancer.md`.
7. **Record each approval as soon as the user picks.** Update the Brand Lock file: chosen element becomes `fixed`. Changing one slot invalidates only the downstream outputs that used it; never touch unrelated slots.
8. **Produce the requested applications** (read `references/applications.md`): paste-ready prompt blocks, with the Brand Lock block copied verbatim into every prompt.
9. **QA and repair** (read `references/qa.md`). Fix only the failing asset; prefer a small deterministic correction in Figma/Illustrator over regenerating.

Process rules: keep the internal reasoning (Creative DNA, mechanisms, enhancer steps) private. Show finished options with a short rationale, not the machinery. One short status line per batch is enough. After the user picks an option, acknowledge in a few words and move to the next visible output.

## Output format

Produce these blocks as needed. Always fenced and paste-ready.

**Brand Lock (keep in a file such as `brand-lock.md` next to the project):**
```text
[BRAND LOCK - DO NOT DEVIATE]
Brand spelling: <exact>
Authoritative logo: <file name / which reference image + preservation instruction>
Palette: <exact hex + role, e.g. #0B1F3A background, #F4F1EA text, #FF5A36 accent>
Typography: <display family + weight>, <body family + weight>
Layout: <grid / alignment / spacing>
Shape language: <radius / border / forms>
Graphic device: <motif / pattern rule>
Must preserve: <fixed invariants>
Never: <forbidden treatments, at least two>
```

**Palette review (2-3 options):** name, 3-6 named colors with hex, role per color (background, text, primary, accent, support), one-sentence rationale, one central visual mechanism, contrast-safe text/background pair, 2-3 logo mechanism seeds (only if a logo follows).

**Logo candidates (exactly 3):** per candidate the structured spec, then ONE enhanced prompt in a code block (grammar in `references/logo-and-prompt-enhancer.md`), plus the color list to set separately.

**Type review:** `Display font / Body font / Why this pair / Download links / Install caveat`, with a sample line set in the brand name.

**Application prompt (mockup):**
```text
[CREATE ONE FINISHED BRANDED MOCKUP]
<object, setting, camera, material, lighting, composition, one brand-specific idea>

[AUTHORITATIVE LOGO]
Reference image 1 is the exact approved <full-color/black/white> logo. Preserve its spelling, silhouette, geometry, proportions, internal negative space and exact color. Do not redraw, simplify, crop, stretch, outline or add effects.

[PLACEMENT LOCK]
Target surface / Position / Scale / Orientation / Color

[PHYSICAL APPLICATION]
<print / emboss / foil / engraving behavior>

No extra logos, pseudo-text, invented labels, warped marks, floating print, unrelated props, arbitrary gradients, plastic sheen, or generic luxury staging.
```

**Delivery manifest:**
```text
Brand Lock version:
Concept:
Editable files (Figma/Illustrator):
Preview/final files:
Generated assets (prompts used):
Required fonts:
Known limitations:
Variant names (so the user can say "revise carousel card 3"):
```

## Tool adapters

- **Nano Banana Pro:** the generator for mockups, palette/mood boards and text-bearing posters. It renders text well: give exact strings in quotes. Attach the approved logo PNG as a reference image and label each reference by role ("reference image 1: official logo"). Poor fit for exact logo geometry: never ask it to redraw an official logo, place the real file instead. For brand-new logo exploration it gives raster only; vectorize afterwards.
- **Figma / Illustrator (source of truth):** build the Brand Lock as color styles + text styles (Figma variables), place the official SVG exactly, set type with real fonts, build templates for social/poster/deck/brandbook. Use Image Trace (Illustrator) or a redraw on grid to turn a chosen raster logo concept into clean vectors; verify against the concept.
- **Photoshop:** smart-object mockups when the surface is flat or lightly curved and the logo must stay pixel-exact; use generated scenes as the base layer.
- **Premiere Pro + After Effects:** brand motion only after the static system is locked (logo reveal, lower-third, end card). Import the SVG/AI directly; use the Brand Lock colors and fonts.
- **KLING / Seedance 2 / Higgsfield Cinema Studio:** poor fit for identity work. Use only to animate an already-approved still (logo sting, product-in-scene), one subject, camera move in a separate sentence. Seedance 2 accepts EN+ZH prompts. Never let a video model re-render the logo; composite it in After Effects instead.

## QA checklist

Run the full checklist in `references/qa.md`. Minimum before delivery:
- [ ] Exact brand spelling in every asset
- [ ] Official/approved logo geometry untouched, correct colorway for the surface
- [ ] Palette roles consistent (exact hex, not "approximately blue")
- [ ] Approved font pair only; exact copy, no pseudo-text, no invented claims
- [ ] Grid, margin, radius, border and motif follow the Brand Lock; differences are documented format overrides
- [ ] Correct aspect ratio and dimensions
- [ ] No generic AI-brand clichés (see anti-slop list in `references/design-brain.md`)
- [ ] Editable vs flattened clearly labeled; font install caveat stated
- [ ] A failing asset is repaired alone; the Brand Lock stays unchanged unless the user changes a rule

## References

- `references/intake-and-brand-lock.md`: read at the start of any job: full intake questions, asset analysis method, evidence labels, source precedence, Brand Lock shape and prompt lock block, per-format overrides, change handling.
- `references/logo-and-prompt-enhancer.md`: read when creating or extending a logo: routes (existing, partial, new), the three-candidate rules, the structured candidate input, and the logo prompt enhancer grammar verbatim; export and variant rules, clear space, logo QA.
- `references/palette-typography.md`: read when proposing or auditing colors and fonts: option requirements, font-pair evaluation, deterministic typography rule, editable-output caveats.
- `references/design-brain.md`: read before generating any option set: Creative DNA, the four action modes (palettes, logo mechanisms, typography, critique, revise), anti-slop rules, one-expressive-move rule, scoring rubric, concept-board sequence.
- `references/applications.md`: read when producing mockups, merchandise, packaging, signage, social graphics, posters/banners, a presentation deck or a brandbook: prompt recipes, logo variant routing, text/detail two-stage route, brandbook slide outline.
- `references/qa.md`: read before delivering and whenever something looks off: preflight, set-level consistency matrix, module checks, repair strategy, stop conditions, naming.
