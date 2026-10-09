# Intake, asset analysis and Brand Lock

Contents:
1. Intake (gap checklist, brief template, slider normalization)
2. Asset analysis (inventory, roles, evidence labels, precedence, measurement)
3. Consistency matrix and analysis output order
4. Brand Lock (states, shape, minimum, prompt lock block, overrides)
5. Handling revisions

## 1. Intake

Parse the user's first message, attachments and already approved slots before asking anything. Treat the fields below as a gap checklist, not a mandatory questionnaire.

Ask one compact question set (a single chat message) containing only unanswered fields that materially block the requested output. Never repeat information from the first message. If there are no blocking gaps, skip core intake entirely. Invite only the uploads still relevant after considering files already attached.

### Core gap checklist

1. **Name**
   > What is the name of your brand or product?
2. **Offering, audience, and positioning**
   > What does the brand or product offer, who is it for, and what are its key values or positioning?
3. **Identity route**
   > Are we creating a new visual identity, or do you already have some brand assets you want to keep and extend?
   Options: New identity / I have existing brand assets
4. **Preferences**
   > Do you have any visual preferences? Describe your vision, colors, fonts, mood, or examples. You can optionally indicate where it should sit on these scales: Restrained <-> Expressive, Geometric <-> Organic, Familiar <-> Experimental. Example: "Expressive 70, Organic 60, Familiar 40." Say "balanced" or leave the scales blank if unsure.

Filter this list to missing questions only; never send all four automatically.

### Conditional upload step (existing or partial identity)

If the first message did not already include the needed official assets, ask once, listing only the relevant slots. Keep each role separate; never mix inspiration into the official-assets list.

1. Official logos and marks: SVG preferred; PNG, JPG, WebP, or PDF accepted.
2. Official fonts: TTF, OTF, WOFF, or WOFF2.
3. Palette and guidelines: PDF, PPTX, CSS, JSON, SVG, or images.
4. Other official brand materials: packaging, templates, graphics, or application examples.
5. Inspiration references: visually useful but never authoritative.

After analysis, immediately mark every user-declared official logo, palette and typography slot as `fixed` in the Brand Lock. Do not wait for a combined approval.

For a new identity, offer one optional inspiration/reference upload only when inspiration would materially help and none was attached. Do not ask for official logo/font/palette unless the user changes route.

### Internal brief

```text
name:
offering:
industry/category:
audience:
positioning/key values:
identity route:
visual preferences:
visual_axes:
  restrained_expressive:
  geometric_organic:
  familiar_experimental:
uploaded official logo assets:
uploaded official font assets:
uploaded official palette/guideline assets:
uploaded other official assets:
uploaded inspiration:
```

Normalize scale language to 0-100:
- Strongly first = 0
- Mostly first = 25
- Balanced/unspecified = 50
- Mostly second = 75
- Strongly second = 100

Do not ask what the user specifically likes or dislikes about every reference. If they provide no explanation, use the reference's overall visual character as a taste signal without copying its logo, layout, artwork, or distinctive device.

### Route

- **New identity**: create only the foundation slots needed by the deliverables named in the first message.
- **Existing/partial identity**: analyze and independently lock every supplied official element, then identify only missing slots required by the requested deliverables.
- If the user chose the existing-assets route but uploaded nothing, ask them to upload what they want preserved before proceeding.

Describe the specific missing elements naturally. Example: "You already have an official logo and fonts. Would you like me to develop a matching color palette while keeping those assets unchanged?" Never use "fill in the blanks" as fixed copy.

Keep the first-message deliverables in scope. Once their required slots are approved, continue them without asking the user to choose scope again.

## 2. Asset analysis

Analyze supplied assets before concepting or generation. The goal is a usable visual specification, not an impressionistic description.

### 2.1 Inventory and assign roles

Build an inventory:

```text
id | filename/source | format | dimensions/pages | likely role | authority
```

Use one role per asset:
- `official-logo`
- `logo-variant`
- `font-file`
- `palette`
- `brandbook`
- `template`
- `representative-visual`
- `style-reference`
- `content-only`
- `unknown`

Ask the user only when confusing two roles would change the output, for example an official logo versus a visual reference. Never treat inspiration as an official asset without confirmation.

### 2.2 Inspirational references

For every `style-reference` or `representative-visual`, separate reusable taste signals from protected/distinctive design:

```text
Reference:
User specifically likes:
Palette behavior:
Typography character:
Composition/grid:
Shape/material language:
Overall mood:
Do not copy:
```

Ask what specifically inspires the user when they have not said. Offer palette, typography, composition, shape language, material, and overall aesthetic plus a free-text option. If they do not answer, use the overall aesthetic character as a taste signal. Do not reproduce the reference's logo, distinctive layout, illustration, pattern, or artwork, and do not pass it into logo generation.

### 2.3 Evidence labels

Attach one evidence label to every extracted rule:
- **source-declared**: explicit in SVG/CSS/PPTX/PDF/font metadata or written brand guidelines.
- **measured**: deterministically calculated from source pixels or geometry.
- **visually-observed**: clear to visual analysis but not available as source data.
- **inferred**: a plausible interpretation or recommendation.

Keep exact values and inferred matches separate. Never call an inferred font, radius, grid, or color role exact.

### 2.4 Source precedence

Resolve conflicts in this order:
1. User's explicit correction
2. Official editable source or font file
3. Written brandbook rule
4. Repeated value across multiple official assets
5. Deterministic measurement
6. Visual observation
7. Inference

Record conflicts instead of averaging them away. A social campaign may intentionally use a different treatment from the core identity.

### 2.5 Raster image analysis

Read images semantically and compositionally; analyze several related images together to detect repeated rules. For deterministic measurement use the eyedropper and measure tools (Figma, Photoshop, Illustrator) or ImageMagick/Pillow, and measure:
- Pixel dimensions, color mode, alpha, and resolution metadata
- Dominant and repeated colors, with exact sampled hex values
- Background versus foreground color candidates
- Logo bounding box and clear-space ratios
- Margins, gutters, column alignment, and repeated spacing
- Border thickness and approximate corner radius
- Text-block positions, alignment, scale relationships, and line counts
- Repeated motif size, density, and rotation
- Image crop, focal point, balance, and negative-space distribution

For anti-aliased pixels, cluster near-identical colors rather than reporting hundreds of false palette entries. Ignore photographic colors when extracting the graphic palette unless the image clearly uses them as deliberate overlays or surfaces.

Font recognition from pixels is never exact. Describe anatomy first (grotesk/humanist/geometric/serif, width, contrast, terminals, x-height, weight), then list possible matches with confidence.

### 2.6 SVG, CSS, and token files

Parse source directly before rendering:
- `viewBox`, width, height, and aspect ratio
- Fill/stroke colors and opacity
- Stroke widths, line caps, and joins
- Paths, groups, transforms, masks, and clipping
- Repeated geometry and spacing
- `font-family`, weight, style, letter spacing, and text anchors
- CSS variables and semantic token names
- Corner radii, shadows, borders, and gradients

Render a preview and compare it with the source parse. Preserve the original file as the authoritative logo whenever possible; do not regenerate it.

### 2.7 PDF and PPTX

For `.pptx`: unpack the OOXML (`unzip`) when exact theme/font/shape data matters; render slide thumbnails (export to PDF, then to PNG) for visual reading. Capture slide size, master/layout structure, theme colors, font families, weights, positions, shape geometry, borders, fills, radii, image crops, alignment, and recurring page types.

For PDF: `pdftotext` for declared rules and copy; `pdffonts` for embedded font families; `pdftoppm`/`pdfimages` for page and image evidence of hierarchy, palette, spacing, composition. In Illustrator or Acrobat you can inspect fonts and swatches directly.

If the document cannot be parsed (corrupt, encrypted, or scanned without OCR value), say so and ask for page images or source files instead of improvising.

PDF geometry may be flattened or outlined. Mark recovered text/font data as source-declared only when the file exposes it; otherwise use measured or visually-observed.

### 2.8 Font files

For `.otf`, `.ttf`, `.woff`, `.woff2`, inspect with `fc-scan` or FontTools (or the font info panel in Figma/Illustrator):
- Family and style names
- Weight and width classes
- Italic/oblique status
- Variable axes
- Character/language coverage (check Polish diacritics: ą ć ę ł ń ó ś ź ż)
- License/name table metadata when present

Do not make a legal conclusion from metadata. Do not redistribute the file. For editable outputs, note that the recipient must install the font; PPTX does not reliably embed custom fonts.

## 3. Consistency matrix and analysis output

After per-asset analysis, build a consistency matrix:

```text
Property | Core/official rule | Repeated variants | Exceptions | Confidence
```

Cover:
- Logo usage and exclusion zone
- Palette and role frequency
- Type roles and hierarchy
- Grid, margins, gutters, and alignment
- Border, corner-radius, and shadow language
- Composition and focal hierarchy
- Shapes, motifs, patterns, and textures
- Photography/render treatment only when it appears in supplied materials
- Format-specific exceptions

Return analysis in this order:
1. **Authoritative assets**
2. **Measured visual tokens**
3. **Typography findings**
4. **Layout and composition rules**
5. **Graphic devices**
6. **Format-specific exceptions**
7. **Unknowns/conflicts**
8. **Safe extension rules**

Feed these findings into the Brand Lock. Do not generate until the lock distinguishes what must be preserved from what may be proposed.

## 4. Brand Lock

The Brand Lock is the single source of truth for every requested graphic. Create it after intake and asset analysis, before any generation. It is not a brand strategy document: it records supplied context, measured rules, and the minimum proposed visual decisions needed for this job.

### Lock states

Mark each field as one of:
- `fixed`: supplied or approved; never change without explicit permission.
- `proposed`: fills a missing visual rule; may be revised.
- `not_applicable`: intentionally absent.
- `unknown`: unresolved and unsafe to invent.

Also attach an evidence label from section 2.3.

### Canonical shape

Use this structure. Keep it compact enough to copy relevant blocks verbatim into generation prompts.

```json
{
  "version": 1,
  "brand_context": {
    "name": "",
    "offering": "",
    "industry": "",
    "positioning": "",
    "audience": "",
    "tone": []
  },
  "concept": {
    "name": "",
    "visual_premise": "",
    "research_principles": [],
    "reference_preferences": [],
    "avoid": []
  },
  "visual_axes": {
    "restrained_expressive": 50,
    "geometric_organic": 50,
    "familiar_experimental": 50
  },
  "authoritative_assets": {
    "logo": {
      "origin": "user_supplied | generated",
      "source": "",
      "file": "",
      "variants": {
        "color": "",
        "black": "",
        "white": ""
      },
      "status": "fixed"
    },
    "fonts": [],
    "references": []
  },
  "palette": {
    "origin": "user_supplied | generated",
    "primary": [],
    "accent": [],
    "neutral": [],
    "semantic_roles": {},
    "forbidden": []
  },
  "typography": {
    "origin": "user_supplied | generated",
    "display": {},
    "body": {},
    "fallbacks": [],
    "font_links": []
  },
  "layout": {
    "grid": "",
    "margins": "",
    "spacing_scale": [],
    "alignment": "",
    "density": ""
  },
  "shape_language": {
    "corner_radii": [],
    "borders": [],
    "shadows": [],
    "forms": []
  },
  "graphic_devices": {
    "motifs": [],
    "patterns": [],
    "textures": [],
    "rules": []
  },
  "composition": {
    "hierarchy": "",
    "logo_placement": [],
    "image_behavior": "",
    "text_behavior": ""
  },
  "applications": {},
  "unknowns": []
}
```

For each exact token, retain its state, evidence, and source when ambiguity exists. Do not bloat every obvious field with metadata.

### Required minimum

Before generation, the lock must contain:
- Exact brand/product spelling
- Requested deliverables and formats
- Logo source or an explicit `not_applicable`
- Palette behavior (exact colors when supplied)
- One approved display/body typography system and a rendered specimen
- Composition/hierarchy rule
- Shape/border/radius rule
- At least two concrete avoid rules

If a missing value would materially affect a generation, ask once. If it only affects a reversible layout detail, make a `proposed` decision.

### Prompt lock block

For every image-model call, include one compact block:

```text
[BRAND LOCK - DO NOT DEVIATE]
Brand spelling: <exact>
Authoritative logo: <reference image and preservation instruction>
Palette: <exact hex + role>
Typography: <exact font/style when rendered>
Layout: <grid/alignment/spacing>
Shape language: <radius/border/forms>
Graphic device: <motif/pattern rule>
Must preserve: <fixed invariants>
Never: <forbidden treatments>
```

Repeat the block verbatim across related assets. Change only the asset-specific content, dimensions, and composition section.

### Reference discipline

- Use each authoritative file once and reuse the same file for every output (same exact PNG, same exact SVG).
- When one generation builds on another, attach the earlier output as a reference image rather than re-describing it.
- Label references by role in prompts: `Reference image 1: official logo`, `Reference image 2: approved base scene`.
- State what each reference controls and what it must not control.
- For an existing logo, require exact preservation of spelling, geometry, proportions, and colors. Prefer deterministic placement/compositing (Figma, Illustrator, Photoshop) when the logo does not need to interact physically with the scene.

### Per-format overrides

Store format differences under `applications`, not by changing core tokens. Examples:
- A carousel may use tighter spacing than a deck.
- A poster may use the display font at extreme scale.
- A light kraft/paper/cardboard mockup uses the approved black logo.
- A dark mockup uses the approved white reverse logo.
- Embossing, debossing, foil, stamps, engraving, and one-color printing use an approved monochrome logo, never the full-color mark.

An override must name its format and cannot contradict a fixed core rule.

## 5. Handling revisions

Keep the Brand Lock as a file the user can open. When the user revises one rule:
1. Change only the revised slot in the lock (bump the version).
2. Keep every unrelated approved slot unchanged.
3. Identify actual dependents by which slots each output used (record "required slots" next to each finished asset: for example `logo`, or `logo + palette`, or `logo + palette + typography`).
4. Regenerate or recompose only affected outputs and ask for approval again.

Do not infer approval from silence, from a successful generation, from the newest generation, or from your own visual assessment. Approval is the user's explicit choice.

A generated logo depends on the palette it was made with: if the palette changes, discard that logo and run the three-candidate step again. A typography change does not invalidate the symbol mark, but rebuild the wordmark/lockup. A user-supplied official logo is never regenerated.
