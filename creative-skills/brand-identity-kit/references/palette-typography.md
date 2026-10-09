# Palette and typography

Contents:
1. Palette: route and option requirements
2. Typography: existing font, Google Fonts pairs, showing the type
3. Keeping the type system simple
4. Deterministic typography rule
5. Editable output caveats

## 1. Palette

Palette creation is part of the essential kit (logo + palette + typography).

### Route

1. Read intake and supplied assets.
2. Run `PROPOSE_PALETTES` from `design-brain.md`.
3. Produce three meaningfully different, defensible options.
4. Present them as a board: a color-block layout per option (build it in Figma as a frame with swatches and role labels, or paste the table below). Do not use an image model to generate the palette board; hex values must be exact.
5. Wait for the user's selection or revision feedback.

Each option must include:
- 3-6 named colors with exact hex values
- explicit roles (background, text, primary, accent, support)
- rationale linked to Creative DNA
- one central visual mechanism
- rough logo-mechanism ideas only when the requested scope includes a later logo stage; omit them entirely for palette-only work
- contrast-safe text/background relationship

Do not select the palette for the user (unless they asked you to choose). When the user selects it, record that exact palette in the Brand Lock as `fixed`. Do not wait for logo, typography, or a combined review.

The palette board shows no typography specimen, placeholder font pairing, or wordmark. Typography appears only after the user selects a logo.

Review message to send after showing the options:

> Take your time reviewing the palettes. Reply with the option you prefer and any colors you want changed, added, or removed.

Do not use a multiple-choice gate; wait for the user's ordinary next message.

Option table template:

```text
Option A - <name>
Rationale (tied to the brief):
| Role       | Name  | Hex     |
| background | ...   | #......|
| text       | ...   | #......|
| primary    | ...   | #......|
| accent     | ...   | #......|
| support    | ...   | #......|
Central mechanism:
Contrast check: text on background = <ratio>:1
Avoids cliche: ...
Logo seeds (only if a logo follows): 1) ... 2) ... 3) ...
```

Check contrast numerically (WCAG ratio) rather than by eye: body text at least 4.5:1, large display text at least 3:1.

## 2. Typography

Build a usable type system, not a list of attractive font names.

### 2.1 Existing or user-owned font

If the user supplies `.otf`, `.ttf`, `.woff`, or `.woff2`:
1. Inspect family/style names, weights, variable axes, language coverage, and metadata with font tools (or Figma/Illustrator font info).
2. Record the file as authoritative in the Brand Lock.
3. Use the font in deterministic SVG/PPTX/HTML/Figma layouts.
4. Tell the user the font must be installed in their editor/device.

Do not redistribute the font, assert that its license permits a use, or package it with final deliverables unless the user explicitly requests that and confirms permission.

If the existing identity names a proprietary font but no file is supplied, preserve the name as an observed rule and propose a Google Fonts substitute or companion. Do not silently claim the substitute is the original.

### 2.2 Google Fonts recommendations

When no usable brand font is supplied, propose 2-3 distinct Google Fonts pairs that fit the brief and any approved palette/logo slots.

Every option must use a unique display/body combination. Do not repeat or swap the same two families across boards.

Verify each family is currently available in Google Fonts. Font discovery is not market research; use the official library rather than trend articles.

Evaluate:
- Match to supplied positioning, audience, and tone
- Display versus body readability
- Distinctiveness without sacrificing practical use
- Available weights, italics, optical sizes, widths, and variable axes
- Required languages and diacritics (for Polish copy confirm ą ć ę ł ń ó ś ź ż render in every weight used)
- Legibility at the intended poster/carousel/deck sizes
- Compatibility between headline and body anatomy
- Whether one family with multiple styles is stronger than an unnecessary second family

Avoid recommending a decorative font for body copy. Do not pair two families that compete in contrast, width, or personality. One family with useful contrast between weights/styles is valid when it is the stronger system.

### 2.3 Show the typography

Run `PROPOSE_TYPOGRAPHY` from `design-brain.md`, then build one specimen per font pair (Figma frame or HTML page) using:
- The proposed display/body pair
- The real brand name and short sample headline/body copy
- The approved palette when available
- The approved mark next to the wordmark treatment when available, so mark/type cohesion is visible
- The same font files used in later work
- One shared text color for both display and body samples; it must differ from the background color

The user-facing result:

```text
Display font:
Body font:
Why this pair:
Google Fonts download links (or supplied-font note):
Install/use caveat:
```

Do not rely on links alone: a rendered specimen is required. Do not use an image model to fake typography. After showing the options, invite the user to take their time and comment; do not use a multiple-choice gate. When the user selects a pair, record it in the Brand Lock.

## 3. Keep the system simple

- Name the display and body/utility family.
- Name the exact files/weights used in the rendered sample.
- Include fallbacks and language coverage only when relevant.
- Use no more than two families.

Do not create a user-facing type-role table, line-height system, letter-spacing specification, or exhaustive scale at this stage. Individual templates may choose practical sizes while preserving the approved pair.

## 4. Deterministic typography rule

If exact typography matters, do not bake final text into a photographic generation. Generate the background/scene without final copy and add text in SVG/PPTX/HTML/Figma using the actual font. Image-model typography is not evidence of font choice or exact letterforms. (Exception: flattened social graphics, where a text-capable image model is used with a type specimen reference; see `applications.md`.)

## 5. Editable output caveats

- PPTX references fonts but does not reliably embed custom fonts.
- SVG text remains editable only when kept as text and the font is installed.
- Outlined SVG preserves appearance but text is no longer editable.
- HTML/CSS can self-host a permitted webfont or use Google Fonts; include fallbacks.
- Imported PPTX/SVG may shift in Canva or Figma.

Include these caveats in delivery when they apply.
