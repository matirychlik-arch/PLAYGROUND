# Applications: mockups, merchandise, packaging, signage, social, posters, deck, brandbook

Contents:
1. Mockups (planning, anti-slop, logo variant routing, prompt contract, two-stage text route, compositing, per-type guidance)
2. Merchandise
3. Packaging
4. Signage
5. Social media graphics (incl. the 4:5 crop trick)
6. Posters and banners
7. Presentation deck
8. Brandbook outline (seven slides)

Rule for all: copy the Brand Lock block from `intake-and-brand-lock.md` verbatim into every prompt; change only content, format and composition. Produce the editable source (Figma/Illustrator/SVG/PPTX) separately from any rendered presentation image; a mockup is never the editable source.

## 1. Mockups

Create believable applications of the Brand Lock. Preserve the approved logo and colors; do not let the scene generator invent branding.

Require an approved logo. Read palette and visual axes when color/application decisions need them. Require typography only when readable text must appear. Use the exact approved logo file everywhere; never substitute a newer generation or a recreated mark.

Mockups are rendered images, not fully editable layered documents. If the user needs editable source artwork, use that asset's dedicated section first (packaging, social).

### Plan the application from the brand input

Use the approved Brand Lock, user brief, visual axes, preferences, and uploaded references before choosing mockup objects, materials, framing, or art direction.
- Choose applications people in that category credibly use.
- Extract useful composition/material cues from user-provided references.
- Never recreate a reference's exact scene, layout, or branded object.

Each mockup needs one clear art-directed idea tied to this brand. "Put the logo on a generic object" is not a concept.

### Anti-slop rules

Avoid the common synthetic/generic look:
- Arbitrary gradients or neon glows unrelated to the Brand Lock
- Plastic sheen on every material
- Floating products and physically meaningless props
- Excessive bloom, haze, depth of field, or cinematic lighting
- Generic marble/pedestal "luxury" staging
- Fake microcopy, pseudo-labels, invented claims, or decorative UI
- Impossible folds, embossing, reflections, print edges, or scale
- Too many props competing with the branded surface
- Warped logos or a different visual device in every mockup

Prefer believable materials, restrained lighting, purposeful negative space, specific environments, and one focal branded application.

### Model and aspect ratio

Use a photoreal image model for the scene (Nano Banana Pro accepts reference images and renders text well). Use the same model for every mockup in a set. Ask which aspect ratio the user wants unless the request states it; offer common choices such as 1:1, 4:3, 3:4, 4:5, 16:9, 9:16. For several mockups use one ratio for the set unless the user assigns ratios per item. Lock the ratio across every stage.

### Existing photograph

When the user supplies the exact photograph to mock up, pass it as reference image 1 and the logo variant as reference image 2. Preserve subject, camera, lighting, materials, folds, shadows, perspective, crop, background, and selected ratio.

### Logo variant routing

Use one of the exact approved variant files:
- Full-color logo: smooth surfaces and production methods that credibly support accurate multicolor printing.
- Black monochrome logo: light kraft paper, natural cardboard, pale fabric, stamps, dark-ink screen printing, engraving masks, and light uncoated stock.
- White monochrome logo: dark paper, dark boxes, dark fabric, reverse marks, light-ink screen printing, and dark signage.
- Embossing, debossing, foil, laser engraving, and one-color printing always use a monochrome variant. Never send the full-color mark as the application reference for those processes.

Create a monochrome variant (deterministic recolor of the approved vector, see `logo-and-prompt-enhancer.md`) only after the user confirms a mockup whose physical production requires one-color/reverse artwork. Never pre-generate monochrome assets for future mockups. Never ask the image model to invent or recolor them.

### Mockup prompt contract

References are attached images; refer to them by order ("reference image 1", "reference image 2") and state each image's role explicitly. For a new scene, attach the selected logo variant as reference image 1; add approved product/artwork references after it. Use PNG/JPG references (an SVG cannot be attached as a raster reference).

```text
[CREATE ONE FINISHED BRANDED MOCKUP]
<specific object/application, credible setting, camera, material, lighting,
composition, and one brand-specific art-direction idea>

[AUTHORITATIVE LOGO]
<Reference image N> is the exact approved <full-color/black/white> logo. Preserve its
spelling, silhouette, geometry, proportions, internal negative space, and exact
color. Do not redraw, simplify, crop, stretch, outline, or add effects.

[PLACEMENT LOCK]
Target surface: <exact object panel/face/material>.
Position: <exact alignment and location, e.g. horizontally centered, upper
third, optical center aligned to panel>.
Scale: logo occupies <specific proportion> of the target surface while keeping
<specific clear-space margin>.
Orientation: align to <panel edge/seam/baseline>; follow surface perspective
without changing logo proportions.
Color: use the supplied <full-color/black/white> variant exactly. State why it
contrasts correctly with the material/background.

[PHYSICAL APPLICATION]
Render the logo using <credible print/emboss/foil/engraving/ink behavior>.
Respect folds, grain, perspective, occlusion, reflections, scale, and
manufacturing limits.

No extra logos, pseudo-text, invented labels, warped marks, floating print,
unrelated props, arbitrary gradients, plastic sheen, or generic luxury staging.
```

The prompt must contain concrete placement, scale, alignment, clear-space, color-variant, and material-application instructions. "Place the logo on the bag/box" is insufficient.

### Two-stage route when the mockup contains readable text

If the final mockup contains any readable text (wordmark, brand name, tagline, packaging label, signage, product copy, interface text), do not ask the scene generator to render it in the same pass:
1. Stage 1 creates the same-ratio scene with the target surface blank and no logo, letters, pseudo-text, or invented graphics.
2. Stage 2 uses an image model that renders legible text reliably (Nano Banana Pro). Reference image 1 is that exact stage-1 base; reference image 2 is the approved logo/artwork.
3. The stage-2 prompt preserves image 1's camera, crop, objects, lighting, material, folds, shadows, perspective, and background exactly.
4. State the exact literal text (in quotes), logo variant, placement, scale, alignment, clear space, color, and physical print/application behavior.
5. Keep the ratio identical to the user-approved ratio.

If there is no readable text, keep the one-call route. If the logo gets corrupted, retry once with stronger placement, geometry and color constraints and the same references; if it fails again, stop and use deterministic compositing when possible.

### Deterministic compositing (prefer when possible)

Prefer placement in Figma/Photoshop/Illustrator over generative editing when:
- The target is a flat poster, screen, card, sign, or front-facing package
- The source logo already has transparency
- No physical deformation, folds, reflections, or occlusion are required

Scale and place the official logo exactly; preserve clear space and color. Add masks/perspective (Photoshop smart object, Figma perspective) only when they can be controlled reliably.

Use the generator directly when the branding must interact with: fabric folds; curved packaging; embossing/debossing; foil, print texture, reflections, or surface wear; occlusion and realistic perspective.

### Mockup-specific guidance

- **Packaging**: use the actual dieline/package proportions when supplied; preserve material, closure, label area, and required legal/copy regions; do not invent claims, ingredients, certifications, or regulatory text.
- **Apparel/merch**: generate the finished branded person/garment mockup; define print/embroidery location, size, and material behavior; preserve the person and garment between variants.
- **Signage/environment**: respect viewing distance, perspective, mounting, and lighting; use the correct approved logo version for background contrast.
- **Device/screen**: treat the screen graphic as a separate editable asset (Figma), then composite it into the device; do not ask the image model to invent interface copy that should be exact.

### Variant discipline

For several mockups:
- Lock one base scene per mockup family.
- Vary only the requested application or colorway.
- Keep camera, lighting, material, and composition fixed for comparison sets.
- Do not generate a new person or environment for every colorway.

### Mockup QA

Run the mockup checks in `qa.md`. After QA, ask the user to approve the final mockup or set. Generated or model-praised mockups are drafts until the user approves; record what the approved mockup used (`logo`, plus palette/typography only if actually used).

## 2. Merchandise

Create merchandise as soon as the slots its artwork uses are approved. Require the logo. Read palette for spot-color/application decisions and typography only when exact copy appears; do not require unused slots.

Collect: item type, printable area, production method, material color, sizes, quantity of variants, and exact copy.

Create production artwork deterministically in SVG (Illustrator/Figma). Use the exact approved logo and approved graphic devices; do not ask an image model to redraw them. Respect spot-color, embroidery, screen-print, and minimum-stroke constraints provided by the user or supplier.

For a confirmed one-color process, recolor the approved vector to the single ink hex and place that unchanged file. Never invent a knockout, mask, cutout, outline, or Boolean subtraction to retain a contrasting internal detail. A one-color recolor can merge overlapping painted areas: disclose that limitation and ask before changing their topology. Preserve the exact original source.

Use the mockup recipe only for presentation imagery after the production artwork is approved. Keep artwork and mockup as separate deliverables.

Check dimensions, color count, contrast against material, minimum detail size, and artwork/mockup consistency before approval.

## 3. Packaging

Design packaging once the slots used by the requested artwork are approved. Require approved logo and palette. Require typography only when readable copy appears; do not block copy-free packaging on unused typography.

Required inputs:
- package type and dimensions/dieline
- material and printing constraints
- exact product/flavor names
- required legal/regulatory copy
- barcode/nutrition/certification assets
- hierarchy and variants

Do not invent claims, ingredients, certifications, dosage, nutrition, pricing, or regulatory content.

Build:
- Create label/panel artwork deterministically in SVG or another requested editable format (Illustrator is the natural tool).
- Use exact approved logo, fonts, and palette.
- Keep copy editable.
- Preserve dieline folds, cut lines, bleed, and safe zones. Keep technical guides in an explicitly hidden group (for example `display="none"`) in artwork and clean previews; show them only in a separately labeled technical proof when requested. Custom attributes such as `data-print="false"` do not prevent SVG rendering or printing.
- Use one system across variants; vary only approved product information and designated color roles.

For presentation mockups follow section 1 after the packaging artwork is approved. The mockup is not the editable packaging source.

QA: check dimensions, bleed, copy, barcode zones, contrast, variant consistency, and physical plausibility. Inspect the actual preview, not only source attributes.

An RGB SVG with `data-color-mode="CMYK"`, generic `device-cmyk()` declarations, or a formula-derived CMYK table is not a validated CMYK print master. Without the supplier ICC/output profile and conversion/separation proof, label these values provisional and disclose that the editable file still needs color-managed prepress. Do not claim press-ready QA passed from metadata alone; request the missing print profile when a final CMYK master is required.

## 4. Signage

Create signage once its required slots are approved. Require logo and palette; require typography when copy/wayfinding text appears.

Require:
- sign type and environment
- physical dimensions
- viewing distance
- fabrication/illumination constraints
- exact copy and directional information
- supplied site photos or plans

Do not invent wayfinding destinations, measurements, safety information, or fabrication specifications.

Build deterministic editable sign artwork in SVG/PDF-compatible vector form. Use approved logo, fonts, and palette. Prioritize legibility at the required distance over decorative detail.

If a visual-in-context preview is requested, follow section 1; keep the editable sign artwork as a separate source asset.

Check scale, contrast, minimum stroke size, clear space, mounting constraints, and environmental visibility.

## 5. Social media graphics

Create once the slots used by the requested social graphic are approved. Require approved logo and palette for branded no-text graphics; add approved typography only when readable text appears. Never force typography for a no-text post.

Ask once for:
- Platform, aspect ratio, and number of outputs
- Exact text that must appear; "no text" is a valid answer
- Visual mode: plain branded background/poster, or mockup photography/application
- Any supplied photography or product assets

Preserve copy verbatim. Never invent sale language, CTA, claims, prices, contact details, or placeholder copy.

Output contract: social deliverables are flattened PNG/JPG graphics, not editable templates. If the user wants editable templates, build them in Figma separately.

Supported modules: square post; 4:5 feed post; 9:16 story; carousel cover/body/CTA cards; channel banner/cover.

### Plain branded poster

Use a text-capable image model (Nano Banana Pro) for the finished graphic. Attach: the exact approved logo variant (PNG), the approved typography specimen, and any official product/photo reference.

The prompt must state:
- Exact literal copy
- Display/body font family names and which text uses each
- Logo placement, scale, clear space, and color variant
- Text placement, hierarchy, alignment, line breaks, and contrast
- Exact palette roles
- Requested aspect ratio

### 4:5 feed post when the model does not offer 4:5

If the generator lacks an exact 4:5 option, compose with a centered 4:5 safe area, generate at 3:4, then crop only the vertical excess:

```bash
magick generated-3x4.png -gravity center -crop '100%x93.75%+0+0' +repage final-4x5.png
```

(`convert` may replace `magick`; in Photoshop/Figma set a 4:5 crop frame centered.) Verify the final pixel ratio exactly equals 4:5 and that no locked logo or copy crosses the crop boundary.

### Mockup photography/application

1. Create or use the mockup photograph first with its target surface blank (section 1).
2. Attach that exact mockup as reference image 1.
3. Attach the approved logo variant as reference image 2.
4. Attach the approved typography specimen as reference image 3.
5. The text-capable model adds the exact copy, logo, and approved typography to the blank surface.

Preserve image 1's camera, crop, people, pose, lighting, materials, folds, shadows, perspective, environment, and background exactly. Change only the controlled social artwork/application.

### Typography fidelity

The approved typography specimen is mandatory whenever text appears. Name the exact display/body families in the prompt; never infer typography from the logo or palette. After generation, check the output against the specimen. Retry once when the letterform character is visibly substituted. If the model still cannot reproduce the approved typography, report the limitation instead of presenting the output as exact, and set the final text in Figma over a text-free generated background.

### Social QA

- Exact copy, spelling, punctuation, requested line breaks
- Correct platform ratio and requested output count
- Approved logo geometry and color variant
- Approved display/body typography character
- Readable hierarchy and text contrast
- Approved palette only
- No pseudo-text, extra logos, invented CTA, or unsupported claims
- All outputs in one set share the same Brand Lock

## 6. Posters and banners

Create once the slots used by the poster/banner are approved. For text-bearing branded layouts, require separately approved logo, palette, and typography. If a requested asset genuinely omits one of these, read only the slots it uses.

Inputs:
- intended channel/use
- dimensions/aspect ratio
- exact headline/body/CTA
- print or digital
- supplied imagery
- required bleed/safe area

Build:
- Vector/layout-led work: editable SVG (Illustrator/Figma).
- Easy office/editor editing: one-slide PPTX.
- Digital implementation: HTML/CSS when requested.

Typography, logo, shapes, and layout remain deterministic. Image models may create only replaceable photography/background imagery. Never bake the final logo or exact copy into a generated image for this module.

QA: check dimensions, safe areas, spelling, contrast, font rendering, logo source, and print/export requirements. Check every painted part of the placed logo against its immediate background: an unchanged blue mark on a matching blue stripe can disappear even though source geometry is correct. Move the intact logo to a contrasting approved surface; do not recolor or redraw it without approval.

## 7. Presentation deck

Create once logo, palette, and typography are separately approved. Do not ask for another combined approval.

Intake: deck purpose; audience; source content; desired slide count; exact claims/data; requested aspect ratio; existing PPTX template, if any. Do not invent mission, values, market statistics, pricing, claims, contacts, or product variants to fill slides.

Build:
- Existing PPTX: edit its masters/layouts.
- No template: create a small coherent layout family in Figma Slides, PowerPoint or Keynote, or with a PPTX library.
- Use approved logo, palette, and fonts.
- Keep all text/shapes editable.
- Keep imagery replaceable.
- Use generated imagery only as optional supporting assets.
- Do not flatten whole slides into images.

Create only slide types required by the content, such as cover, divider, image/copy, comparison, process, data, quote, and closing.

QA: render slides for inspection, fix, re-render. Check overflow, collisions, alignment, font substitution, contrast, and placeholder residue. Deliver editable PPTX plus PDF when requested.

## 8. Brandbook outline

Create the brandbook when logo, palette, and typography are each approved. Never ask for an additional combined approval. Required inputs: approved logo (vector), palette, display/body typography, brand concept/summary copy supplied by the user, optional approved mockups. Do not invent mission, values, claims, product variants, prices, statistics, or brand-story copy.

Fixed seven-slide structure (build it as a Figma file or PPTX; keep slide size, margins, grids, text-box positions and image zones identical across brands):

1. **Cover**: "Brand Guidelines" + the real brand/product name
2. **Branding concept**: approved concept summary + approved palette rationale
3. **Primary logo**: exact approved SVG
4. **Logo system**: primary logo; show a secondary slot only when the user supplied or explicitly requested an approved alternate/monochrome/reverse version (transparent PNG, no background rectangle). If none is approved, remove its label and slot; do not generate one automatically. Never invent a secondary logo.
5. **Primary palette**: replace every swatch with approved colors, names, RGB values, hex values. Keep each color name, RGB value, and hex value close together directly beneath its swatch. Set each swatch label independently to a readable contrasting color (the darkest swatch uses light text). No swatch borders; add a minimal keyline only when a swatch matches the slide background and would disappear. Fit all colors into the existing grid.
6. **Typography**: approved display font and body font, shown at exactly the same point size in equal-height text boxes with aligned baselines. Never shrink only one specimen; if either overflows, reduce both together or shorten the specimen copy. Check nothing is clipped, substituted, overlapped, or partially off-canvas.
7. **Mockups**: exactly two approved mockups per slide.

Conditional mockup slides:
- No approved mockups: remove slide 7.
- One mockup: use the first image zone and remove the second; do not redesign the grid.
- Two mockups: one mockup slide.
- More than two: duplicate the mockup slide for every additional pair.
- Never place generated-but-unapproved mockups in the brandbook.

Styling rules:
- Replace template colors with approved palette colors; replace template fonts with approved fonts.
- Set every slide title in the approved display font, keep the template's font size, normal letter spacing, no wrapping, one line.
- Choose a title color with at least 3:1 contrast against the slide background.
- Body copy in the approved body font without auto-shrinking.
- Place the exact approved logo into distortion-safe square media slots; never stretch it or regenerate its geometry.
- Crop mockup images to the 3:4 slots before placement; never stretch width and height independently.
- Use approved copy only; preserve readable contrast; add no decorative motifs or sections that are not in the template.

Deliver an editable file plus a matching PDF, and one warning naming the display/body fonts the user must install to view/edit the editable file correctly (with official download links when known).

Before delivery: render every slide; check clipping, overflow, font substitution, image crop, alignment; reject any wrapped/overlapping title or title below 3:1 contrast; verify logo geometry and palette values; confirm the PDF visually matches the editable file; remove all template placeholder text.

Stable file names: `<brand>-brand-guidelines-v<revision>.pptx` / `.pdf`.
