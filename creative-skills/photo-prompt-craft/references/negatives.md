# Negative prompt bank

Contents:
- Universal block (always)
- Anti-uncanny (people, hands, faces)
- Anti-text-warp (labels, branding)
- Anti-stock-feel (ads, hero, lifestyle)
- Anti-aesthetic-mixing (restyle)
- Anti-flat-band (text-overlay space)
- Format-specific extras
- How to assemble

Append one `[AVOID]` block to the prompt. The universal list applies to every generation; the situational lists extend it. If the generator has a separate negative-prompt field, paste the block there; if it only takes one prompt, keep the block at the end as written (the "no ..." phrasing works in both).

## Universal (always include)

```
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

## Anti-uncanny (include when humans are in frame)

Append for any generation with people, hands, or faces:

```
no AI uncanny faces, no warped facial geometry, no asymmetric eyes,
no extra teeth, no melted facial features, no warped fingers or hands,
no plastic skin, no orange-tan skin, no over-smoothed retouching,
no doll eyes, no misaligned facial features, no rubber-like skin texture,
no warped jewelry or glasses, no stiff unnatural posture.
```

## Anti-text-warp (include when product has labels or branding)

```
no warped product label text, no garbled letters, no fake brand names,
no melted typography, no doubled labels, no fictional logos.
```

## Anti-stock-feel (include for ad, hero, lifestyle modes)

```
no stale stock photography aesthetic, no synthetic stock-photo look,
no over-staged feeling, no unrealistically clean environments,
no perfect symmetry where natural asymmetry should be,
no clipart elements, no flat illustration mixed with photo,
no obviously composited backgrounds.
```

## Anti-aesthetic-mixing (include for restyle mode)

```
no aesthetic mixing — commit fully to the chosen preset,
no half-applied style transformation,
no source image style bleeding through unchanged.
```

## Anti-flat-band (include when user explicitly wants text overlay space)

When the user has said they will overlay text in post-production AND the prompt asks for a tonally calm area:

```
the calm area must blend naturally into the scene as part of the actual environment
(sky, blurred background, surface texture, atmospheric gradient),
NOT a hard-edged solid-color rectangle, NOT an artificial flat band,
NOT a cropped-looking empty zone disconnected from the rest of the image.
```

## Format-specific extras

Collected from the product format guides; add to the combined block when the format applies.

- Pinterest pin: no oversaturated colors, no neon, no Instagram-grid square framing, no horizontal-leaning compositions, no dated stock photo aesthetics, no sterile feel.
- Hero banner: no symmetric framing if asymmetric requested, no flat lighting.
- Carousel: no inconsistent palette across slides, no varying lighting between slides, no different surfaces between slides, no broken visual continuity.
- Ad pack: no inconsistent palette across variants, no flat lighting, no synthetic stock look.
- Closeup with person: no full face dominating the frame, no person taking focus from product, no plastic skin, no airbrush look, no warped fingers, no over-staged feeling, no clinical sterile feel where warmth needed.
- Virtual model try-on: no clothing items that fight the featured product, no oversexualized poses, no warped product geometry, no altered product color.
- Conceptual / surreal: no cartoonish render, no obvious AI tells, no plastic look on product, no half-committed surreal (fully surreal or fully realistic, never in-between), no cluttered composition, no random floating objects without intent, no logos or text other than the product's own branding, no warped product geometry, no melted product details.
- Restyle: no change to subject identity, no change to composition, no change to product appearance.

## How to assemble

For any prompt, append a single `[AVOID]` block combining:
1. Universal (always)
2. Anti-uncanny (if humans / hands / faces)
3. Anti-text-warp (if product labels visible)
4. Anti-stock-feel (if the image is an ad, hero or lifestyle)
5. Anti-aesthetic-mixing (if restyling)
6. Anti-flat-band (only if the user explicitly wants text-overlay space; see typography.md)
7. Format-specific extras (above)

Combine into one block and do not duplicate phrases. Only add situational lists that apply; an overlong negative list dilutes the positive prompt.
