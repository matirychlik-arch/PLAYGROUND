# Product camera moves (18 master prompts)

Contents:
1. Shared settings and the two-step method
2. Start-frame preparation prompt (shared by all 18)
3. Camera and lens moves (push-in, pull-back, crane, top-down dive, whip pan, macro, texture, detail scan, label trace)
4. Rotation and float (half turn, spin, floating roll)
5. Light and shadow (light sweep, sunrise, shadow motion)
6. Particles and fluids (impact, liquid wrap, paint wave)

## Shared settings and the two-step method

Every master prompt below is verbatim from the source recipes. All 18 were run with the same settings: 6 seconds, silent, 3:4 portrait, 1080p, standard quality mode, high bitrate. Change the aspect ratio to 9:16 for Reels/Shorts/TikTok; keep the duration at 6 s unless you add a second beat (then 8 to 10 s).

Method, in two steps:

1. Make a clean start frame from the real product photo with an image model (the start-frame prompt below). This removes clutter, centers the product at 60 to 70% of the frame and picks a background color from the packaging, which keeps the video model from inventing a different product.
2. Feed that frame as the first frame (image-to-video) together with the move prompt. The video prompt says "the supplied image"; in a tool with a start-frame slot, attach the start frame there. In a tool that only takes a reference image, keep the sentence as is.

Fixed preservation line used by all 18 (already inside each master prompt, repeated here so you can append it to your own moves): *Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text in every frame. Keep motion physically plausible, temporal consistency high, edges stable, and lighting coherent. Do not morph, melt, duplicate, replace, or redesign the product. Do not add people, hands, unsupported claims, extra logos, captions, watermarks, or unrelated products. End on a clean, stable product frame suitable for social media.*

## Start-frame preparation prompt (shared)

Use with an image model that edits from a reference photo (Nano Banana Pro works well). Output aspect ratio = the final video aspect ratio.

```text
Create a clean, premium product-video start frame from the supplied image, treating the visible product as the authoritative reference. Isolate the product and place it centered, upright, fully visible, and uncropped on a seamless single-color studio background with a matching floor-to-wall transition. Select the background hue directly from a distinctive visible color on the product, packaging, label, logo, or material. Prefer a recognizable brand or accent color over neutral black, white, or gray when one is visible. Use a slightly lighter or darker value of that same sampled hue only when needed to maintain clear edge separation and legibility; do not introduce an unrelated color. Scale the product to occupy approximately 60–70% of the frame while leaving balanced motion-safe space around it. Add soft controlled studio lighting and one physically plausible grounding shadow. Preserve the exact product identity, silhouette, proportions, construction, materials, colors, packaging, logo placement, and all readable label text. Do not redesign, simplify, restyle, relabel, crop, rotate, open, duplicate, or deform the product. Do not add props, people, hands, scenery, patterns, gradients, text, captions, borders, watermarks, or extra products. Deliver a photorealistic, stable, high-detail frame suitable as the first frame of a product animation.
```

## Camera and lens moves

### Push In

- Effect: A smooth camera push-in.
- Source id: `push-in`

```text
Create a 6-second silent premium product video using the supplied image as the authoritative starting frame and product reference. Perform one slow, steady camera push toward the product, beginning with environmental context and ending on a strong close hero framing. Preserve perspective, focus behavior, and product geometry. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text in every frame. Keep motion physically plausible, temporal consistency high, edges stable, and lighting coherent. Do not morph, melt, duplicate, replace, or redesign the product. Do not add people, hands, unsupported claims, extra logos, captions, watermarks, or unrelated products. End on a clean, stable product frame suitable for social media.
```

### Pull Back

- Effect: A camera pullback revealing the scene.
- Source id: `pull-back`

```text
Create a 6-second silent premium product video using the supplied image as the authoritative starting frame and product reference. Begin on a close product detail, then pull the camera smoothly backward to reveal the complete product and its environment. Keep the product anchored and sharp throughout the move. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text in every frame. Keep motion physically plausible, temporal consistency high, edges stable, and lighting coherent. Do not morph, melt, duplicate, replace, or redesign the product. Do not add people, hands, unsupported claims, extra logos, captions, watermarks, or unrelated products. End on a clean, stable product frame suitable for social media.
```

### Crane Reveal

- Effect: A vertical camera move revealing the product.
- Source id: `crane-reveal`

```text
Create a 6-second silent premium product video using the supplied image as the authoritative starting frame and product reference. Begin below or behind a simple foreground element and raise the camera vertically to reveal the full product. End with a balanced hero composition and a short stable hold. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text in every frame. Keep motion physically plausible, temporal consistency high, edges stable, and lighting coherent. Do not morph, melt, duplicate, replace, or redesign the product. Do not add people, hands, unsupported claims, extra logos, captions, watermarks, or unrelated products. End on a clean, stable product frame suitable for social media.
```

### Topdown Dive

- Effect: A transition from an overhead view to a close-up.
- Source id: `topdown-dive`

```text
Create a 6-second silent premium product video using the supplied image as the authoritative starting frame and product reference. Start from a clean top-down view, then descend and tilt into a close three-quarter product angle in one continuous move. Keep horizon changes smooth and spatial geometry coherent. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text in every frame. Keep motion physically plausible, temporal consistency high, edges stable, and lighting coherent. Do not morph, melt, duplicate, replace, or redesign the product. Do not add people, hands, unsupported claims, extra logos, captions, watermarks, or unrelated products. End on a clean, stable product frame suitable for social media.
```

### Whip Pan

- Effect: A fast whip-pan to the product.
- Source id: `whip-pan`

```text
Create a 6-second silent premium product video using the supplied image as the authoritative starting frame and product reference. Start on a neutral adjacent area, execute one fast motion-blurred whip pan, and land precisely on the product in sharp focus. The transition should feel energetic but not distort the product. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text in every frame. Keep motion physically plausible, temporal consistency high, edges stable, and lighting coherent. Do not morph, melt, duplicate, replace, or redesign the product. Do not add people, hands, unsupported claims, extra logos, captions, watermarks, or unrelated products. End on a clean, stable product frame suitable for social media.
```

### Macro Glide

- Effect: A smooth camera move across the product's surface.
- Source id: `macro-glide`

```text
Create a 6-second silent premium product video using the supplied image as the authoritative starting frame and product reference. Use a macro lens to glide slowly across the product surface, revealing material, edges, and print detail with shallow depth of field. Keep macro scale believable and focus transitions controlled. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text in every frame. Keep motion physically plausible, temporal consistency high, edges stable, and lighting coherent. Do not morph, melt, duplicate, replace, or redesign the product. Do not add people, hands, unsupported claims, extra logos, captions, watermarks, or unrelated products. End on a clean, stable product frame suitable for social media.
```

### Texture Track

- Effect: A camera move along the material's texture.
- Source id: `texture-track`

```text
Create a 6-second silent premium product video using the supplied image as the authoritative starting frame and product reference. Track closely along one visible material texture with raking light that reveals its depth, then widen slightly to reconnect the texture to the full product. Do not replace or exaggerate the material. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text in every frame. Keep motion physically plausible, temporal consistency high, edges stable, and lighting coherent. Do not morph, melt, duplicate, replace, or redesign the product. Do not add people, hands, unsupported claims, extra logos, captions, watermarks, or unrelated products. End on a clean, stable product frame suitable for social media.
```

### Detail Scan

- Effect: Product details revealed in sequence.
- Source id: `detail-scan`

```text
Create a 6-second silent premium product video using the supplied image as the authoritative starting frame and product reference. Move through two or three important visible product details in a continuous cinematic scan. Use precise focus pulls and finish on the complete product without inventing hidden features. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text in every frame. Keep motion physically plausible, temporal consistency high, edges stable, and lighting coherent. Do not morph, melt, duplicate, replace, or redesign the product. Do not add people, hands, unsupported claims, extra logos, captions, watermarks, or unrelated products. End on a clean, stable product frame suitable for social media.
```

### Label Trace

- Effect: A camera move across the logo and label text.
- Source id: `label-trace`

```text
Create a 6-second silent premium product video using the supplied image as the authoritative starting frame and product reference. Trace the camera smoothly across the real label, logo, and visible typography, keeping letters stable and legible. Finish by pulling focus to the full front of the product. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text in every frame. Keep motion physically plausible, temporal consistency high, edges stable, and lighting coherent. Do not morph, melt, duplicate, replace, or redesign the product. Do not add people, hands, unsupported claims, extra logos, captions, watermarks, or unrelated products. End on a clean, stable product frame suitable for social media.
```

## Rotation and float

### Half Turn

- Effect: A smooth 180-degree product rotation.
- Source id: `half-turn`

```text
Create a 6-second silent premium product video using the supplied image as the authoritative starting frame and product reference. Keep the camera fixed while the product rotates smoothly through 180 degrees, beginning from the supplied view and ending on a clean complementary angle. Use gentle ease-in and ease-out with stable light. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text in every frame. Keep motion physically plausible, temporal consistency high, edges stable, and lighting coherent. Do not morph, melt, duplicate, replace, or redesign the product. Do not add people, hands, unsupported claims, extra logos, captions, watermarks, or unrelated products. End on a clean, stable product frame suitable for social media.
```

### Product Spin

- Effect: A clean 360-degree product rotation.
- Source id: `product-spin`

```text
Create a 6-second silent premium product video using the supplied image as the authoritative starting frame and product reference. Keep the camera locked while the product completes one smooth 360-degree turn on a clean turntable. Use constant angular speed, stable studio lighting, and a subtle grounded shadow. Infer unseen surfaces conservatively and preserve design continuity. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text in every frame. Keep motion physically plausible, temporal consistency high, edges stable, and lighting coherent. Do not morph, melt, duplicate, replace, or redesign the product. Do not add people, hands, unsupported claims, extra logos, captions, watermarks, or unrelated products. End on a clean, stable product frame suitable for social media.
```

### Floating Roll

- Effect: Slow product rotation in zero gravity.
- Source id: `floating-roll`

```text
Create a 6-second silent premium product video using the supplied image as the authoritative starting frame and product reference. Make the product float weightlessly and perform a slow, graceful roll in place. Add minimal vertical drift, soft studio reflections, and physically coherent motion without changing the product shape. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text in every frame. Keep motion physically plausible, temporal consistency high, edges stable, and lighting coherent. Do not morph, melt, duplicate, replace, or redesign the product. Do not add people, hands, unsupported claims, extra logos, captions, watermarks, or unrelated products. End on a clean, stable product frame suitable for social media.
```

## Light and shadow

### Light Sweep

- Effect: A band of light sweeping across the product.
- Source id: `light-sweep`

```text
Create a 6-second silent premium product video using the supplied image as the authoritative starting frame and product reference. Keep the camera and product locked while one controlled band of light sweeps across the surface, revealing contours and materials. Reflections must follow the real geometry and settle into a clean final light. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text in every frame. Keep motion physically plausible, temporal consistency high, edges stable, and lighting coherent. Do not morph, melt, duplicate, replace, or redesign the product. Do not add people, hands, unsupported claims, extra logos, captions, watermarks, or unrelated products. End on a clean, stable product frame suitable for social media.
```

### Sunrise Pass

- Effect: A transition from darkness to warm light.
- Source id: `sunrise-pass`

```text
Create a 6-second silent premium product video using the supplied image as the authoritative starting frame and product reference. Animate a gradual sunrise-like lighting transition from cool darkness to warm directional light. Let the product emerge naturally with moving shadows and finish in a bright premium hero state. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text in every frame. Keep motion physically plausible, temporal consistency high, edges stable, and lighting coherent. Do not morph, melt, duplicate, replace, or redesign the product. Do not add people, hands, unsupported claims, extra logos, captions, watermarks, or unrelated products. End on a clean, stable product frame suitable for social media.
```

### Shadow Motion

- Effect: Moving graphic shadows.
- Source id: `shadow-motion`

```text
Create a 6-second silent premium product video using the supplied image as the authoritative starting frame and product reference. Keep the product fixed while clean graphic shadows move slowly across the background and surface, as if cast by architectural shapes. Maintain one coherent light source and full brand readability. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text in every frame. Keep motion physically plausible, temporal consistency high, edges stable, and lighting coherent. Do not morph, melt, duplicate, replace, or redesign the product. Do not add people, hands, unsupported claims, extra logos, captions, watermarks, or unrelated products. End on a clean, stable product frame suitable for social media.
```

## Particles and fluids

### Impact

- Effect: A burst of particles frozen around the product.
- Source id: `impact`

```text
Create a 6-second silent premium product video using the supplied image as the authoritative starting frame and product reference. Begin with the product still, release a controlled radial burst of neutral particles, then freeze them mid-air while the camera makes a short arc. The impact must never move or damage the product. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text in every frame. Keep motion physically plausible, temporal consistency high, edges stable, and lighting coherent. Do not morph, melt, duplicate, replace, or redesign the product. Do not add people, hands, unsupported claims, extra logos, captions, watermarks, or unrelated products. End on a clean, stable product frame suitable for social media.
```

### Liquid Wrap

- Effect: Liquid flowing around the product.
- Source id: `liquid-wrap`

```text
Create a 6-second silent premium product video using the supplied image as the authoritative starting frame and product reference. Animate a smooth ribbon of liquid wrapping around the product and peeling away again. The fluid should follow believable momentum and surface interaction without staining, bending, or hiding the product. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text in every frame. Keep motion physically plausible, temporal consistency high, edges stable, and lighting coherent. Do not morph, melt, duplicate, replace, or redesign the product. Do not add people, hands, unsupported claims, extra logos, captions, watermarks, or unrelated products. End on a clean, stable product frame suitable for social media.
```

### Paint Wave

- Effect: A wave of colorful paint.
- Source id: `paint-wave`

```text
Create a 6-second silent premium product video using the supplied image as the authoritative starting frame and product reference. Send a sculptural wave of colored paint past and around the product, using colors derived from the packaging. Keep the product clean and stationary, and make the paint motion thick, coherent, and premium. Preserve the exact product identity, silhouette, proportions, materials, colors, logo placement, packaging structure, and readable label text in every frame. Keep motion physically plausible, temporal consistency high, edges stable, and lighting coherent. Do not morph, melt, duplicate, replace, or redesign the product. Do not add people, hands, unsupported claims, extra logos, captions, watermarks, or unrelated products. End on a clean, stable product frame suitable for social media.
```

## Adapting a master prompt

- Keep the first sentence ("Create a 6-second silent premium product video using the supplied image as the authoritative starting frame and product reference."), swap only the middle (the move) and keep the closing preservation block untouched.
- For KLING, shorten to: subject sentence, one move sentence, one end-state sentence, and move the "Do not" list into the negative prompt field.
- For Seedance 2, keep the English text and optionally add a Chinese copy of the move sentence (see SKILL.md adapters).
- Chain two moves only with an 8 to 10 s clip and an explicit mid-point state ("at the midpoint the product is centered and still"); otherwise generate two 6 s clips and join them in the editor.
