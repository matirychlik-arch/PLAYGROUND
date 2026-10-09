# Logo system and prompt enhancer

Contents:
1. Logo routes (existing, partial, new)
2. Exactly three comparable candidates
3. Candidate input to the enhancer
4. Where the colors go, and what to do with the result (selection, vectorizing, variants, export)
5. Clear space, minimum size, deliverables, logo QA
6. Prompt enhancer grammar (verbatim contract) and an illustrative example

A request for other branded graphics does not authorize a logo redesign. Use this module only when the user asks to create, extend, document, or apply a logo.

## 1. Routes

### Existing official logo

Use the supplied file as authoritative.
1. Analyze source geometry, variants, colors, clear space, and minimum-size guidance from source files/brandbook.
2. Record the file in the Brand Lock once; reuse that exact file everywhere.
3. Reuse or deterministically place the exact asset.
4. Generate only requested variants/applications.

Never ask an image model to redraw a logo merely to change its background, size, placement, or colorway. Use SVG/PPTX/image compositing (Figma, Illustrator, Photoshop) when the source supports it. Never run the prompt enhancer when an official logo exists.

### Partial logo system

Examples: only a primary logo exists; no monochrome/reverse version, symbol, clear-space rule, or lockup.
- Preserve the primary mark.
- Propose only missing variants.
- Derive variants from source geometry rather than inventing a second style.
- Ask before separating a symbol from a wordmark if the source does not demonstrate that they may be used independently.

### New logo

Run only when explicitly requested.

1. In an interactive new-identity flow, complete the palette review first (`palette-typography.md`, `design-brain.md`). Require a user-selected palette before generating logo candidates. Color/style preferences from intake are not palette selection. Only when the user asked you to choose for them may you select the palette yourself.
2. Run the logo-mechanism step from `design-brain.md` (`PROPOSE_LOGO_MECHANISMS`) with the brief, references, visual axes, and selected palette.
3. Require exactly three distinct symbol-only candidate specifications.
4. Apply the enhancer grammar (section 6) exactly once per candidate, building one complete structured candidate input per application.
5. Generate the three candidates with identical parameters (same aspect ratio, same palette/background, same quality). One prompt per candidate; never merge the three into one request, never use "3 variations" in a single prompt.
6. Show all three together with a short rationale each, then invite the user to review and comment. When the user selects one, record it in the Brand Lock as `fixed`. Continue to typography only when the original request requires text/type; a logo-only request does not.

In auto mode (the user said to choose for them), score the three candidates for brief fit, distinctiveness, and legibility and select the strongest; say that you did.

If prompt enhancement or generation fails, retry once with the same candidate specification. If it fails again, stop and report the problem.

## 2. Exactly three comparable candidates

All three must:
- Come from the same generator with identical parameters
- Use the same aspect ratio, palette parameters, background, and quality
- Belong to the selected draft palette and user-defined direction
- Differ in mark construction, not presentation quality
- Stay simple enough to reproduce faithfully with vector geometry
- Express one visual concept only; never fuse two metaphors unless the user's own request explicitly described that exact fusion
- Include one concrete distinctive silhouette, negative-space device, motif treatment, or unexpected locked color-role pairing
- Preserve any explicit user-requested style in the candidate and enhanced prompt
- Use one, two, or three logo colors as the concept requires; three is a maximum, not a default, unless the user explicitly requested more
- Avoid generic swooshes, arbitrary initials, stock startup symbols, tiny details, gradients/effects unless concept-critical, and mockup scenes

Typography is selected afterward. Every enhancer prompt must include "no text" in its constraint tail. Monograms may contain only their explicitly requested initials.

During typography selection, the mark and wordmark must feel like one lockup:
- Match stroke/weight and corner character
- Balance mark height against cap/x-height
- Use deliberate gap and optical alignment
- Avoid a detailed/heavy mark beside a weak or unrelated wordmark

Never reproduce or cite a reference mark as the target.

## 3. Candidate input to the enhancer

For each of the three mechanisms, assemble the complete structured candidate input (field meanings are defined in section 6):

```text
{
  brand_context: { name, offering, industry, positioning, audience, values },
  visual_axes: { restrained_expressive, geometric_organic, familiar_experimental },
  candidate: {
    mark_type, central_idea, visual_mechanism, distinctive_element,
    shape_logic, treatment, style_register, user_style_directive, composition
  },
  palette: { count, user_requested_more_than_three, roles },
  reference_signals,
  forbidden_elements
}
```

Use only the resulting enhanced prompt as that candidate's logo prompt.

Set `user_requested_more_than_three: true` only when the user explicitly asks for a logo with more than three colors. Otherwise pass exactly the one, two, or three logo colors the concept requires, even if the broader brand palette contains more. Never add colors merely to reach three.

## 4. Colors, vectorizing, variants, export

Exact hex colors never enter the enhanced prompt prose. Pass them through the generator's color parameters when it has them, or on a separate `Colors:` line after the prompt. If the generator ignores them, recolor the result in Figma/Illustrator to the exact Brand Lock hex values; that is a deterministic edit, not a new concept.

Raster-only generators (for example an image model such as Nano Banana Pro) give you a concept picture, not an editable logo. Treat the picked concept as a reference: redraw or Image Trace it in Illustrator/Figma, then compare the vector against the concept at large and at 16 px.

Variants:
- Logo approval requires only the selected color version. Monochrome/reverse variants are optional. Do not announce, prepare or generate them unless the user explicitly requested them or the confirmed production method needs them (emboss, deboss, foil, engraving, one-color print, stamps).
- Make variants deterministically from the approved color vector: same geometry, recolored (Figma/Illustrator), never a new concept and never an image-model recolor.
- For a requested solid one-color variant, recolor every actual paint to the single target hex. Do not reinterpret filled shapes as holes, add masks/knockouts, change fill rules, or convert strokes to paths to preserve contrast. If overlapping paints merge in one color, disclose that outcome; topology changes require separate explicit approval.
- Export the approved color vector as SVG plus a transparent 2048x2048 PNG (the PNG is what you attach as a reference image to image generators; an SVG cannot be attached as a raster reference).
- Never regenerate, redraw, normalize, or "clean up" the geometry of an approved vector. If a color-only change is needed, recolor; do not call the generator again.

## 5. Clear space, minimum size, deliverables, QA

### Clear space and minimum size

For an existing identity, copy official rules. If none exist, propose rules and mark them `inferred`:
- Define a repeatable unit `x` from a stable feature (symbol width, cap height, or dominant stroke), not an arbitrary pixel count.
- Apply `x` consistently around each lockup.
- Test at intended digital and print sizes.
- Create a simplified small-size treatment only with user approval; do not silently remove details from the primary mark.

### System deliverables (produce only requested items)

- Primary horizontal lockup
- Secondary/stacked lockup
- Symbol/monogram
- Wordmark
- Small-size/favicon treatment
- Clear-space diagram
- Minimum-size guidance
- Approved backgrounds
- Incorrect-use examples

Editable output: the three original candidates, the approved vector source, full-color SVG and 2048x2048 PNG exports, black/white variants only when requested or production-required, brand-guide pages when requested. SVG wordmarks remain editable text and require the approved font to be installed. Do not promise native Figma/Canva/PSD files from a generator.

### Logo QA

- Exact spelling and glyph order
- No altered proportions or invented details
- No unintended gradients, shadows, bevels, or effects
- Correct palette and contrast
- Black and white variants have the exact approved geometry and one solid color
- Exactly three candidates generated with identical parameters
- Selected mark and later wordmark treatment look optically complete together
- Legible silhouette at small size
- Clear-space and minimum-size examples match the actual asset
- Every mockup/template uses the approved anchor, not a regenerated copy

## Prompt enhancer grammar (verbatim contract)

This is the final prompt-construction layer between the logo mechanisms (from `design-brain.md`) and a vector logo generator. Apply it yourself, exactly once per candidate, converting one structured logo-candidate specification into one precise prompt with the highest possible first-pass success rate.

Design decisions are already made. Do not replace, reinterpret, broaden, or add a second concept. Do not narrate this step to the user.

## Input contract

Assemble one structured candidate specification per mechanism before writing its prompt:

```json
{
  "brand_context": {
    "name": "context only; never render it",
    "offering": "...",
    "industry": "...",
    "positioning": "...",
    "audience": "...",
    "values": ["..."]
  },
  "visual_axes": {
    "restrained_expressive": 50,
    "geometric_organic": 50,
    "familiar_experimental": 50
  },
  "candidate": {
    "mark_type": "lettermark_monogram | pictorial | abstract | mascot | emblem",
    "central_idea": "...",
    "visual_mechanism": "...",
    "distinctive_element": "specific silhouette, negative-space device, motif treatment, or unexpected locked color pairing",
    "shape_logic": "...",
    "treatment": "flat_vector | monoline | vector_gradient | hand_drawn_vector",
    "style_register": "...",
    "user_style_directive": "explicit user-requested style, or null",
    "composition": "..."
  },
  "palette": {
    "count": "1, 2, or 3 as required by the locked concept; greater only when user_requested_more_than_three is true",
    "user_requested_more_than_three": false,
    "roles": ["primary", "accent", "background"]
  },
  "reference_signals": ["formal qualities only"],
  "forbidden_elements": ["..."]
}
```

Treat supplied creative decisions as authoritative. If a nonessential detail is missing, infer the smallest sensible default without changing the central idea.

## Output contract

The result of this step is exactly one continuous enhanced logo prompt string per candidate, with no bullet points inside the prompt, no explanation, no debug text.

The prompt must follow this order:

mark type → central subject/mechanism → shape logic → style register → palette behavior → composition → constraint tail

Every clause must materially affect the drawing.

The central subject/mechanism portion must state exactly one visual idea in one clause. Do not add a second metaphor, alternative, “and/or” construction, or hybrid concept.

## Stage boundary: symbol only

This flow creates a symbol/mark before typography selection.

Never include:

- brand name
- wordmark
- tagline
- descriptor
- invented letters
- any other readable words

The only exception is a lettermark/monogram candidate: the explicitly supplied initials inside `candidate.visual_mechanism` are permitted. For lettermarks and monograms, “no text” means no additional words, taglines, descriptors, or unrelated lettering.

Every candidate constraint tail must include the exact phrase “no text.” It does not need to be the final phrase.

## Mark type

Preserve `candidate.mark_type` exactly.

Allowed types:

- lettermark_monogram: explicitly supplied initials or interwoven letterforms
- pictorial: one recognizable literal object
- abstract: a concept rendered as nonrepresentational geometry
- mascot: one character/creature with a clear scalable expression
- emblem: a text-free symbol contained within a badge/seal boundary

If `mark_type` is unexpectedly missing, infer it from `visual_mechanism`. Default to abstract, never wordmark or combination mark.

## Treatment

Preserve `candidate.treatment` exactly.

Preserve `candidate.style_register` and `candidate.user_style_directive`. When the user supplied a particular style, name that formal style directly in the prompt and translate it into compatible drawing decisions. Do not dilute it into a generic “modern,” “minimal,” or “premium” treatment. Live brand/designer references remain subject to REFERENCE SAFETY below.

- **flat_vector:** Solid fills, clean SVG paths, no surface effects.
- **monoline:** Uniform stroke weight, rounded caps, no fills.
- **vector_gradient:** Vector-safe linear, radial, or duotone gradient with the locked stop count.
- **hand_drawn_vector:** Allowed only when supplied explicitly. Preserve intentional stroke variation and a clear silhouette. Do not promise minimal anchor points.

Dimensional/3D treatment is forbidden.

## Structural priorities

Define:

1. one dominant unified silhouette
2. concrete geometric or organic construction logic
3. symmetry or intentional asymmetry
4. positive and negative-space behavior
5. stroke/fill behavior
6. internal detail limit
7. small-size scalability
8. centered isolated presentation

Prefer one coherent mechanism over several decorative ideas.

## Distinctiveness and complexity floor

Every enhanced prompt must contain at least one concrete distinctive element:

- a specifically described silhouette
- a specific negative-space device
- a particular motif treatment
- an unexpected but locked color-role pairing

Generic adjectives do not satisfy this requirement. “Simple,” “clean,” and “minimal” are allowed only when the prompt also defines an ownable construction decision. Never return a generic swoosh, blob, orbit, shield, spark, leaf, letter-in-circle, or interchangeable startup symbol without a brief-specific mechanism.

Describe the distinctive element concretely enough that another designer could sketch its structure without guessing.

Preserve `candidate.distinctive_element` and make it explicit in the prompt.

## One concept per logo

The prompt must express one central visual idea only. Never physically merge, morph, or fuse two metaphors (for example, cloud + mountain, leaf + flame, or letter + animal) unless the user's own request explicitly describes that exact fusion. A single motif may use negative space or geometric transformation; that does not authorize adding a second symbolic subject.

## Visual axes

Translate axes into drawing decisions:

- `restrained_expressive` controls intensity, contrast, and detail density
- `geometric_organic` controls construction, curves, and regularity
- `familiar_experimental` controls category recognition and novelty

Do not print values or mention axes in the output.

## Palette

The palette is locked. Do not invent, replace, expand, or reinterpret it.

Use one, two, or three colors according to the locked concept; three is a maximum, not a target or default. Never add colors merely to reach three. Count the background when it participates visually. More than three are allowed only when `palette.user_requested_more_than_three` is true. Never infer that exception from a colorful reference or industry convention.

Exact hex values are passed separately through the generator's color parameters (`colors`, `background_color`), or, if the tool has none, in a separate `Colors:` line placed outside the prompt prose. Never put hex, RGB, Pantone, or other color codes in the prompt.

State:

- strict color count
- role relationships
- solid or gradient behavior
- background relationship

Use role language such as “locked primary tone,” “locked accent,” and “locked background.” Do not invent color names that were not supplied.

## Reference safety

Never output a live brand, studio, artist, or designer name.

Translate `reference_signals` into formal qualities only: geometry, contrast, density, rhythm, form register, material impression, energy.

Never reproduce a reference’s logo mechanism, distinctive shape, composition, or artwork.

## Vector language

For flat_vector, monoline, and vector_gradient, never use: lens, camera, lighting, depth of field, photorealistic, cinematic, material rendering, grain, paper texture, shadows, mockup, scene.

Define drawing logic, not presentation photography.

## Constraint tails

- **flat_vector:** Flat vector design, clean lines, no shadows, no texture, no text. Clean editable vector paths, SVG-friendly, minimal anchor points.
- **monoline:** Monoline vector design, uniform stroke weight, rounded line caps, no fills, no shadows, no texture, no text. Clean editable vector paths, SVG-friendly, minimal anchor points.
- **vector_gradient:** Flat vector design with the specified locked vector gradient, no shadows, no texture, no text. Clean editable vector paths, SVG-friendly, minimal anchor points.
- **hand_drawn_vector:** Intentional hand-drawn vector strokes, approved surface variation, clear scalable silhouette, no shadows, no text.

## Forbidden elements

Honor every `forbidden_elements` entry literally. Never replace one forbidden cliché with another generic symbol.

## Silent validation

Before submitting each logo request, silently verify:

- prompt follows the supplied `central_idea` and `visual_mechanism`
- central mechanism is one visual idea stated in one clause
- no metaphors are fused unless the user explicitly requested that exact fusion
- `mark_type` and `treatment` are unchanged
- explicit user style is present and not generalized away
- there is one coherent mechanism
- at least one concrete distinctive element clears the complexity floor
- no brand/designer names appear
- no words appear except explicitly permitted monogram initials
- exact phrase “no text” appears in the constraint tail
- palette uses at most three colors unless the explicit user override is true
- palette is not padded with unnecessary colors
- palette count and role behavior are strict
- geometry is practical for SVG/vector reproduction
- forbidden elements are absent
- no camera or unsupported texture language appears

If any check fails, rewrite the prompt before submitting it.

## Illustrative example (shows the grammar; not part of the contract)

Candidate: abstract mark for a Polish cold-brew coffee brand, flat_vector, two logo colors, geometric 70.

```text
Abstract symbol mark: a single drop silhouette built from two stacked quarter-circles that meet on a diagonal seam, the lower quarter cut as negative space so the seam reads as a poured stream; bilateral asymmetry with the drop leaning right; crisp geometric construction with constant radii and no tangent breaks; flat solid fills, modern restrained register; strictly two colors, a locked primary tone for the drop and a locked background tone showing through the seam, no gradients; one centered isolated mark with generous margin, readable at 16 px. Flat vector design, clean lines, no shadows, no texture, no text. Clean editable vector paths, SVG-friendly, minimal anchor points.
Colors: <hex list kept out of the prose>
```

Note the order (mark type, mechanism, shape logic, style register, palette behavior, composition, constraint tail), the one concrete distinctive element (the seam as negative space), and the exact phrase "no text" in the tail.
