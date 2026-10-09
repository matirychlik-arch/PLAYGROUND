# Image to code

Contents:
1. The rule: the design is the spec
2. Intake: Figma frame, screenshot or board
3. Token extraction (before any section)
4. Deep analysis per section
5. Build order and the compare loop
6. Anti-drift rules
7. Ambiguity resolution
8. Bespoke chrome and the CTA garment catalog
9. Structural hygiene
10. Responsive derivation and verification

The reference images ARE the specification. The number one failure of image-grounded builds is design drift: strong references, generic code. This file is the discipline that prevents it. It applies equally to a Figma frame Mati designed, a screenshot of a site he wants to match in spirit, or a generated reference board.

## 1. The rule

When your habit disagrees with the design, the design wins. The coded page must feel like the same website as the boards. After each section, glance board to code and name one thing you kept faithful.

## 2. Intake

Figma frame (preferred):
- With the Figma MCP: `get_design_context` for the node (fileKey and nodeId come from the URL: convert `-` to `:` in node ids), `get_screenshot` for the pixel reference, `get_variable_defs` for tokens (colors, type, spacing variables). Treat generated code as a reference to adapt to the project's components, tokens and conventions, not as final code. Reuse existing project components; do not duplicate a Button that already exists.
- Without the MCP: ask for exported PNGs per section at 2x, plus the color and type styles as text.
- Read the whole frame list first: which frames are desktop, tablet, mobile, states (hover, empty, error). If only desktop exists, derive mobile using section 10 and say so.

Screenshot or board: read the image again at build time for each section; do not code from memory. If a detail is too small to read, request or generate a closer detail image rather than guessing.

## 3. Token extraction (before any section)

Write these into a tokens file (CSS variables or Tailwind theme) before building a single section:

- Colors: background, panel/surface, border, text primary, text muted, accent, plus any state colors. Exact hex from the design, not nearest Tailwind default. Preserve the palette logic; never sub in generic web defaults.
- Type: families, the scale as ratios between display, heading and body (not guessed px: measure two or three real sizes and keep the ratios), weights, tracking feel (tight display, normal body), line heights, alignment logic, serif/sans behavior, calm vs aggressive register.
- Spacing: headline to subtext distance, text to CTA distance, card gaps, section top and bottom padding, side gutters, image to text distance, overall cadence. Goal: faithful spacing logic. Snap measured values to a scale (4, 8, 12, 16, 24, 32, 48, 64, 96, 128); never collapse a generous design into default tight spacing.
- Radius and borders: the single corner language, border widths, hairline colors.
- Shadows and elevation: tint, blur, offset; most designs get depth from ONE surface change.
- Motion hints: any easing, durations or interactions annotated in the design.

## 4. Deep analysis per section (before coding it)

Extract, per board:

- **Text:** exact headline, sub and CTA wording visible (adapt, do not lorem); line count and wrapping; alignment logic.
- **Typography:** size relationships between display, heading and body; weight contrast; tracking; register.
- **Spacing:** headline to sub, text to CTA, card gaps, section padding, side gutters, image to text.
- **Color:** background, panel, accent placement, text hierarchy colors, border and shadow mood, image tint or grade.
- **Components:** button size, shape, radius, fill vs outline, hierarchy; card structure; badges; dividers; borders; shadows.
- **Rhythm:** repeated motifs that define the design language (hairlines, numerals, crop frames, rail notes). They carry the concept spine.

## 5. Build order and the compare loop

1. Tokens file and base layout shell (container, grid, section wrapper, dark/light switch if needed).
2. Hero first (it sets the language), then sections in page order.
3. For each section: analysis (section 4), build desktop, then compare: render at the design's frame width (for example 1440 px), screenshot, place next to (or overlay at 50% opacity over) the design frame. Fix mismatches in this order: layout structure, spacing, type sizes and weights, color, then details. Tolerance guide (mine, tune per project): spacing within 4 px, type size exact or within 1 px, colors exact hex, radius exact.
4. Add states (hover, pressed, focus-visible, loading, empty, error) from the design or by the rules in `taste-rules.md` section 7.
5. Add motion last, per the brief and the signature wow.
6. Run `review-rubric.md`.

## 6. Anti-drift rules

- Do not simplify distinctive sections into generic rows.
- Do not compress generous spacing into dense layout.
- Do not flatten strong typography into a default hierarchy.
- Do not merge different section systems into one repeating pattern.
- Do not swap the design's palette for tokens you are used to.
- Do not add micro-UI the design does not show: badges, dots, tag pills, version chips, icon confetti. Every small element must exist in the design or serve real content.
- Do not copy design-tool chrome (browser frames, annotation sticky notes) into the page.

## 7. Ambiguity resolution (in order)

1. Preserve the visible design language.
2. Preserve layout and spacing logic.
3. Preserve the component family.
4. Preserve mood and polish level.
5. Ask for (or generate) an extra detail image of the unclear region.
6. Regenerate that section's board fresh.
7. Only then pick the most implementation-friendly faithful reading.

Never fill ambiguity with a generic default first.

## 8. Bespoke chrome and the CTA garment catalog

Boards often render page chrome (nav bar, footer, slivers of neighbor sections) inside a single section's mockup. Only the section's own content is binding. Board-drawn eyebrows beyond the page budget (ceil(sections / 3)) are non-normative: keep the budgeted ones where the board placed them and drop the rest without treating it as drift.

Board vs brief precedence for CTAs: the board wins for composition and placement; the brief's CTA inventory wins for the CTA's garment and interaction identity (boards often render generic default buttons, and that part is not authoritative). Distinct intents (book vs walk in) may carry distinct labels; the one-label rule collapses only same-intent duplicates.

Icons that annotate real content (spec rows, fact tables, feature labels) are not "micro-UI clutter"; do not scatter them decoratively where nothing needs annotating.

No site-wide shared button style. Each CTA is its own component with its own interaction identity. Examples of same voice, different garments:

- Hero: oversized underlined text link, underline draws in, magnetic pull.
- Work row: whole-row hover reveals a preview crop plus a sliding index digit.
- Contact: framed block that fills on hover with a clipped text swap.
- Nav: links with sliding digits or a moving hairline, not pill buttons.

Garment catalog. Three garments converged across builds (drawing underline, hover flood-fill, framed block), so they are rationed: at most ONE of them per page, and zero overlap with the previous build's set. Pick or derive the rest from garments like these, re-expressed through the brief's material world, never copied literally:

- Text link whose arrow travels along a drawn path (route, circuit, seam).
- Label that splits and slides apart revealing the destination underneath.
- CTA embedded in an image cutout (the button is a photographed object or tag).
- Stamp/press: `:active` physically imprints (skew plus texture shift).
- Ticket/coupon with a perforation that "tears" on hover.
- Mono readout that types or decodes the label on hover.
- Circular badge that spins or unrolls; text on a path.
- Magnetic pill with inertia (only if nothing else on the page is a pill).
- Underline that is a waveform, route or thread, animating like the motif.
- Swatch or chip that flips like a material sample.
- Oversized numeral or glyph as the hit area, the label as its caption.
- Row or band CTA where the entire strip shears or shifts grade on hover.
- Corner-bracket target that closes around the label (viewfinder).
- Toggle or switch metaphor for binary intents (listen/read, light/dark).

The test: cover the label. Could you still tell which site this button belongs to? If it could live on any site, it is not done. No `.btn-primary`-style utility classes in the global CSS; style CTAs where they live. Two sections sharing the same nav or CTA shape is a failure even if the palette differs. Every button label still passes AA contrast and fits on one line.

## 9. Structural hygiene

- **Anti-nested-box:** no card-inside-panel-inside-frame stacks the design does not show. Mirror the single surface change.
- **Micro-UI clutter:** nothing the design does not show.
- **Copy discipline:** adapt the board's visible wording into real, specific copy under the copy rules (no filler verbs, no dash characters, no fake numbers, one label per CTA intent).
- **Reading order:** DOM order equals visual order; headings in sequence.

## 10. Responsive derivation and verification

When the design has only desktop:

- Declare the mobile collapse per multi-column section: columns become one column (`w-full px-4 py-8`), asymmetric offsets reset to zero, display type drops one step (for example 60 px to 36 px), horizontal rails become scroll-snap or stacked, hero asset moves below or becomes the background with a scrim.
- Keep the same tokens; change layout only.
- Touch targets at least 44 px; nav collapses to a menu below the width where it no longer fits on one line.

Verify:

- Screenshots at 375, 768 (tablet), 1440 widths; compare with the design where it exists.
- No horizontal page scroll; no clipped text; images sized and not stretched.
- Report remaining deviations honestly in the scorecard ("hover state for X inferred, not in the design").
