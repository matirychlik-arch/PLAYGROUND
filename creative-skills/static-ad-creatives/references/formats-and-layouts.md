# Formats, layouts, image prompts, marketplace cards

Contents:
1. Placements, ratios and pixel sizes
2. Safe zones
3. Layout zones per format (percent of canvas)
4. Type and contrast minimums
5. Visual system and per-variant image prompt template
6. Text handling: three cases, bold overlay headline, negative prompts
7. Saturation guidance
8. Marketplace cards (scopes, main image, secondary images, A+ modules)

Provenance: platform ratios, the visual-system and per-variant prompt template, the three-case typography rule, the negative-prompt blocks, the caption safe-zone percentages, the 4:5 crop command and the marketplace scopes/asset list come from the source workflows. Pixel sizes, layout zones, type minimums and the marketplace image conventions are standard practice added here; re-check platform specs before a large run.

## 1. Placements, ratios and pixel sizes

| Platform / placement | Aspect ratio | Canvas (px) | Notes |
|---|---|---|---|
| Instagram Feed | `4:5` | 1080x1350 | Most important format |
| Instagram Story / Reels cover | `9:16` | 1080x1920 | Full-screen vertical |
| Facebook Feed | `1:1` | 1080x1080 | Some legacy 1.91:1 (1200x628) |
| TikTok Feed | `9:16` | 1080x1920 | Native-feel content wins |
| Pinterest Promoted Pin | `2:3` | 1000x1500 | Same as organic pin |
| Google Performance Max (Square) | `1:1` | 1200x1200 | |
| Google Performance Max (Landscape) | `16:9` | 1200x675 | (1.91:1 also accepted) |
| LinkedIn Sponsored | `1:1` | 1080x1080 | |
| Marketplace main image | `1:1` | 2000x2000 | See section 8 |

Frames commonly offered by image generators: `1:1` (default square feed), `9:16` (stories, reels), `16:9` (landscape), `3:4` (portrait feed). Some generators do not offer `4:5`. Offer `3:4` as the nearest portrait frame, or do the exact crop:

Compose with a centered 4:5 safe area, generate at 3:4, then crop only the vertical excess:

```bash
magick generated-3x4.png -gravity center -crop '100%x93.75%+0+0' +repage final-4x5.png
```

(`convert` may replace `magick`; in Figma or Photoshop use a centered 4:5 crop frame.) Verify the final pixel ratio exactly equals 4:5 and that no locked logo or copy crosses the crop boundary. Always state the frame; never leave it to a default.

Export: sRGB, PNG for text-heavy statics, high-quality JPG for photographic ones; keep each file under the platform limit (Meta image ads: 30 MB max).

## 2. Safe zones

From the source (caption-safe placement for portrait video, which is the same overlay UI that sits on a story/reel ad):
- Portrait (9:16): keep top 10%, bottom 17% (IG Reels spec: bottom 16.7% of height) and sides 11% of width clear.
- Landscape or square: keep bottom 10% and sides 7.5% clear.
- Never cover a face or the product label to hold a fixed text position.

Recommended working defaults for ads (more conservative because ad UI adds a CTA bar and profile row):
- Stories/Reels/TikTok 1080x1920: no text or logo in the top 14% (about 270 px) and bottom 20% (about 384 px); on TikTok also keep the right-hand ~15% clear of key content, where the like/share column sits.
- Feed 4:5 and 1:1: keep text and logo at least 6% (about 65 px) from every edge; Meta may crop 4:5 slightly in some surfaces, so keep the focal subject and headline inside the central 90% of the height.

## 3. Layout zones per format (percent of canvas)

Boxes are `x, y, width, height` in percent from the top-left. They are defaults; adjust to the composition but keep the hierarchy: product or hero image first, headline second, CTA third, logo last.

**4:5 feed (1080x1350)**
```text
Margins:        6% all sides
Headline:       6, 6, 88, 18        (max 2-3 lines, top)
Hero / product: 8, 26, 84, 50       (focal point near thirds)
Proof / offer:  6, 78, 88, 7        (one line: rating, discount, shipping)
Logo:           6, 90, 22, 5        (bottom-left)
CTA button:     58, 88, 36, 7       (bottom-right, rounded rect)
```

**1:1 feed (1080x1080)**
```text
Margins:        6% all sides
Headline:       6, 6, 88, 20
Hero / product: 10, 28, 80, 46
Proof / offer:  6, 76, 88, 7
Logo:           6, 88, 22, 6
CTA button:     58, 86, 36, 8
```

**9:16 story / reel / TikTok (1080x1920)**
```text
Unsafe bands:   top 14%, bottom 20%, sides 6% (TikTok right ~15%)
Headline:       8, 15, 84, 16
Hero / product: 6, 33, 88, 40
Proof / offer:  8, 74, 84, 5
Logo:           8, 79, 24, 4       (above the bottom band)
CTA line:       20, 82, 60, 6      (a CTA line, not the platform button; the platform button sits in the bottom band)
```

**2:3 pin (1000x1500)**
```text
Headline:       8, 6, 84, 20
Hero / product: 6, 28, 88, 50
CTA / logo row: 8, 84, 84, 8
```

Text mode determines how the zones are used:
- *Baked:* the image prompt names the exact strings and where they sit.
- *Overlay:* the image prompt asks for a tonally calm area at the headline zone (section 6, case 2); Figma sets the type in those boxes.

## 4. Type and contrast minimums

Defaults for phone viewing at 1080 px wide (scale proportionally):
- Headline: at least 64 px (about 6% of canvas height on 1:1); 2-6 words on image.
- Offer / proof line: at least 40 px.
- CTA text: at least 40 px, bold, on a button with at least 4.5:1 contrast between text and fill.
- Any other on-image text: at least 32 px; if it needs to be smaller, it belongs in the primary text.
- Contrast of text against its actual background (sample the pixels under the text): at least 4.5:1 for text under 24 pt equivalent, 3:1 for large display text.
- Line length: headline lines of 12-24 characters; break by phrase, not mid-phrase.
- One display font and one body font from the brand; never more than two families.

## 5. Visual system and per-variant image prompt

Lock the visual system once; every variant uses the same values. Different hooks, same brand DNA.

```text
[VISUAL SYSTEM - applies across the pack]

Palette: {{2-3 dominant brand-aligned tones, with one HIGH-SATURATION accent for scroll-stopping}}
Surface/backdrop: {{specific texture or color used across variants}}
Lighting baseline: {{key direction and quality, can vary slightly per hook}}
Composition rule: {{rule of thirds with strong focal hierarchy}}
Style reference: {{concrete craft descriptors extracted from 2-3 matching photographer entries - same across pack; never include their names}}
Brand colors: {{from known brand context}}
```

Per-variant prompt template:

```text
[VISUAL SYSTEM]
{{Locked specifications copied verbatim}}

[VARIANT {{N}}: {{Hook Angle}} - {{Aspect Ratio}}]

[HOOK VISUAL]
{{Specific visual that delivers the chosen hook angle}}.

[COMPOSITION]
{{Variant-specific framing}}, {{focal anchor placement using rule of thirds}}, strong eye-leading hierarchy.

[LIGHTING]
{{Lighting tuned to deliver the hook - dramatic for problem-solution, warm aspirational for lifestyle, clean clinical for feature-zoom}}.

[CONTRAST & SATURATION]
Higher saturation and contrast than organic content - must fight the feed. Bold tonal range, deep shadows, bright highlights.

[STYLE REFERENCE]
{{Locked style references from visual system}}.

[QUALITY MARKERS]
Scroll-stopping, magazine-quality, hyper-detailed, performance-ad ready.

[AVOID]
{{universal + anti-stock-feel}}
no inconsistent palette across variants, no flat lighting, no synthetic stock look.

resolution: 2k
```

(Use `resolution: 2k` only if the tool has a resolution setting; otherwise ask for 2K output in words.)

When a product reference photo exists, attach the same image to every variant so the product stays identical across hook angles, and add: "Reference image 1 is the exact product. Preserve its shape, color, label and packaging exactly."

Style reference by category (describe the craft, do not name the photographers in the prompt):
- DTC / lifestyle ads: natural window light, tactile surfaces, candid hands
- Premium product ads: controlled studio light, deep tonal range, precise reflections
- Beauty ads: soft sculpted light, skin-true texture, clean backdrops
- Food / beverage ads: side or backlight, steam/condensation, close macro
- Tech / SaaS ads: clean surfaces, cool gradient light, crisp device edges
- Fashion ads: editorial posing, directional light, confident negative space
- Bold direct-response ads: high contrast, saturated color blocks, direct flash look controlled

## 6. Text handling

### Three cases

There are exactly three cases. The default for the image model is to compose freely, without artificially carving out empty space; forced "reserved zones" make the model draw flat color bands or dull gradients, which always look bad.

**Case 1: the user gave concrete text to include.** Include the text directly in the prompt as part of the composition:
```text
[TYPOGRAPHY]
Integrated typography in the scene reads "New Drop" - set in {{font style: bold sans-serif / elegant serif / hand-lettered / clean modern}}, positioned {{naturally within the composition}}, color {{contrasting with background for legibility}}.
```
For ads this is the baked mode. Put each string in quotes, keep to one headline and one short CTA, and name the zone (for example "upper third").

**Case 2: the user will overlay text themselves (Figma, Canva, Photoshop).** Only then, instruct the composition to leave a tonally uniform area:
```text
[COMPOSITION FOR TEXT OVERLAY]
Leave one area of the frame visually calm and tonally uniform - natural soft gradient, atmospheric blur, or smooth surface - so the user can overlay typography in post-production. This area must still feel like part of the scene (sky, blurred background, surface), NOT a hard-edged empty rectangle.
```
Key phrase: tonally uniform area within the natural scene. Never "clean negative space" or "reserved white space"; those trigger flat bands. Also append the anti-flat-band block below.

**Case 3: nothing said about text.** Do not mention text or overlay zones. For ads this case rarely applies, since an ad has copy: choose case 1 or 2 and say which.

### Bold overlay headline (for busy photos)

When the headline sits on a busy photo and must read at thumbnail size, use the sticker stack (drawn in Figma or HTML, not by the image model):

| Trait | Value |
|---|---|
| Font | a heavy condensed grotesk (for example Anton), one weight |
| Case | all caps |
| Stroke | thick (8-14% of cap size), drawn under the fill (Figma: stroke outside / "paint-order: stroke fill") |
| Shadow | hard, dark, offset down |
| Color | white, or one punchy accent from the brand palette |
| Tracking / leading | tight (-0.01 to -0.02em), line-height 0.9 |

Placement: 2-4 words max; not on the face or product label; in a free quarter. Cap height for ads about 6-10% of canvas height (the 12-18% figure in the source is for 16:9 thumbnails).

### Negative prompts

Append one `[AVOID]` block that combines, without duplicate phrases: universal (always), anti-uncanny (if humans, hands, faces), anti-text-warp (if product labels visible), anti-stock-feel (ads, hero, lifestyle), anti-flat-band (only for case 2), plus format-specific negatives.

Universal:
```text
[AVOID]
no AI artifacts, no warped or smeared text, no fake words baked into the image,
no plastic look, no waxy surface, no cartoonish rendering,
no extra fingers, no extra limbs, no melted geometry, no doubled subjects,
no oversaturated HDR, no HDR halos, no oversharpened look,
no flat fluorescent lighting, no harsh on-camera flash,
no generic stock photography poses, no cliché compositions,
no random unrelated brand logos, no watermarks, no signatures,
no AI sheen on hair or skin, no doll-like rendering, no airbrush look,
no flat solid color bands, no empty rectangular areas, no dull gradient zones
that look out of place from the rest of the scene.
```

Anti-uncanny (humans in frame):
```text
no AI uncanny faces, no warped facial geometry, no asymmetric eyes,
no extra teeth, no melted facial features, no warped fingers or hands,
no plastic skin, no orange-tan skin, no over-smoothed retouching,
no doll eyes, no misaligned facial features, no rubber-like skin texture,
no warped jewelry or glasses, no stiff unnatural posture.
```

Anti-text-warp (product has labels or branding):
```text
no warped product label text, no garbled letters, no fake brand names,
no melted typography, no doubled labels, no fictional logos.
```

Anti-stock-feel (ads, hero, lifestyle):
```text
no stale stock photography aesthetic, no synthetic stock-photo look,
no over-staged feeling, no unrealistically clean environments,
no perfect symmetry where natural asymmetry should be,
no clipart elements, no flat illustration mixed with photo,
no obviously composited backgrounds.
```

Anti-flat-band (only with case 2):
```text
the calm area must blend naturally into the scene as part of the actual environment
(sky, blurred background, surface texture, atmospheric gradient),
NOT a hard-edged solid-color rectangle, NOT an artificial flat band,
NOT a cropped-looking empty zone disconnected from the rest of the image.
```

## 7. Saturation guidance

Performance ads need to be slightly louder than organic. In the prompt:
- "High saturation, vivid color, strong contrast - scroll-stopping in busy feed"
- "Bold tonal range - deep shadows and bright highlights"
- "Clean clear focal hierarchy - eye lands on subject in 0.5 seconds"

But not so loud it looks cheap: avoid neon-tinted oversaturation, HDR halos, and the stock photo synthetic look.

## 8. Marketplace cards

Marketplace-ready product visuals: a compliant main image, secondary product images, and A+ style content modules. Marketplace rules differ and change (Allegro, Amazon, Etsy, Shopify stores); confirm the current rules of the target marketplace before final export, and treat the conventions below as defaults.

### Scopes

| Scope | Creates |
|---|---|
| `main` | 1 marketplace main image |
| `product-images` | main image + 5 secondary images |
| `aplus` | main image + 7 A+ modules |
| `full-set` | main image + 5 secondary images + 7 A+ modules |

Custom subsets pick from these asset types:
- `main_image`
- `infographic`
- `multi_angle`
- `detail_shot`
- `lifestyle`
- `whats_in_box`
- `aplus_hero_banner`
- `aplus_pain_points`
- `aplus_features`
- `aplus_ingredients`
- `aplus_efficacy`
- `aplus_how_to_use`
- `aplus_endorsement`

### Inputs and flow

1. Prefer a real product image. If the user provides only text or a URL, proceed only when the product details are clear; otherwise ask.
2. Collect short context: product context, brand context (palette, tone), category, visual style. Ask at most one concise confirmation question before producing prompts.
3. Build the main image first. Once the user accepts it, attach that exact accepted main image as a reference for every secondary image and A+ module so the product stays identical.
4. Respond and write copy in the user's language (Polish for Allegro).
5. Deliver a labeled list: `Main image: <prompt/file>`, `Infographic: ...`, `Lifestyle: ...`. Keep each prompt in its own code block.

### Main image (convention defaults)

- 1:1, 2000x2000 px (at least 1000 px on the longest side so zoom works), sRGB
- Pure white background (RGB 255,255,255) with a soft contact shadow, product only
- Product fills about 85% of the frame, centered, fully in frame, as sold
- No text, badges, logos that are not on the product, watermarks, props or promotional graphics
- Label and packaging exact; one product (or the exact set sold)

```text
[MARKETPLACE MAIN IMAGE]
Reference image 1 is the exact product. Preserve its shape, color, label text and packaging exactly.
Studio packshot of <product> centered on a pure white (RGB 255,255,255) seamless background, soft natural contact shadow beneath, the product fills about 85% of a square frame, fully visible, slight three-quarter angle showing the front label, even soft lighting, accurate colors, crisp edges.
No text overlays, no badges, no props, no watermark, no extra objects.
[AVOID] <universal + anti-text-warp>
```

### Secondary images

| Asset | Purpose | Layout and prompt guidance |
|---|---|---|
| `infographic` | state 3-5 key features at a glance | product hero on a clean palette background; 3-5 short callouts with simple icons and thin leader lines; callout strings given exactly in quotes; legible at thumbnail size; no claim the user did not supply |
| `multi_angle` | show form from several sides | front, side, back/top views on a consistent background, same lighting, same scale; or a 2x2 grid |
| `detail_shot` | prove quality | macro close-up of a texture, seam, mechanism, port or material; shallow depth of field, accurate material rendering |
| `lifestyle` | show use and scale | the product in a believable setting with a person/hands if relevant; product clearly the hero; no competing logos |
| `whats_in_box` | set expectations | everything included laid out flat/knolling on a clean surface, each item distinct and labeled in short text if needed (strings in quotes) |

Prompt skeleton for any secondary image:
```text
[MARKETPLACE <ASSET TYPE>]
Reference image 1 is the accepted main image: the exact product; preserve shape, color, label and packaging exactly.
<asset-specific scene and layout from the table>
Palette: <brand hex roles>. Square 1:1 (or the marketplace's secondary ratio). Text, if any, exactly: "<string 1>", "<string 2>".
[AVOID] <universal + anti-text-warp + anti-stock-feel>
```

### A+ style modules

Common default: a wide header banner of 970x600 px; other module widths and image sizes vary by marketplace and module type, so check the marketplace's current module spec before final export.

| Asset | Purpose | Content |
|---|---|---|
| `aplus_hero_banner` | brand/product hero at top of the description | product + one benefit headline + brand logo; wide composition with product off-center and text space |
| `aplus_pain_points` | name the problems the product solves | 3 short pain statements with simple visuals, then the product as the answer; customer's words |
| `aplus_features` | features and benefits | product with 3-4 labeled features, each feature paired with its benefit (FAB) |
| `aplus_ingredients` | composition / materials / what is inside | ingredients or materials with short true descriptions; macro textures; only supplied facts |
| `aplus_efficacy` | evidence of results | only user-supplied numbers, test results or certifications, shown as clean stat blocks; if none supplied, skip the module |
| `aplus_how_to_use` | usage steps | 3-4 numbered steps with one image per step, short verbs |
| `aplus_endorsement` | trust and proof | user-supplied quotes, awards or certifications; skip if none supplied |

Each module: one idea, headline plus at most 3 short blocks, brand palette and fonts from the Brand Card, product identical to the accepted main image, and all strings quoted exactly in the prompt (or set in Figma over a text-free generated background).
