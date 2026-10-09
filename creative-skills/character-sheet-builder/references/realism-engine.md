# Realism engine (anti-AI / unretouched)

Contents:
1. Why it exists and when it is mandatory
2. The realism module, verbatim
3. Imperfection anchors
4. Eye anti-glare clause
5. Hair finish and mature-structure clauses
6. Photoreal negative tail
7. Editorial variant and what to drop for non-photoreal styles
8. Diagnosis table: symptom to added clause

## 1. Why it exists

Image models drift toward an airbrushed, beauty-filtered, glossy look. "Realistic" alone does
not stop that. This module is the whole trick behind the signature `photoreal-unretouched`
look: it replaces idealized skin with visible texture, matte finish and natural asymmetry.
It is mandatory for every photoreal preset and is omitted only for anime / 3D / game styles
(styles.md), where the skin-texture clauses do not apply.

Principle: **photorealism means anti-retouch, never idealized.** Real means visible pores,
natural asymmetry, matte skin with no glare/shine, naturally-worn (slightly uneven) makeup,
and zero AI-smoothing artifacts.

## 2. The realism module, verbatim

Paste into the REALISM MODULE slot (it follows hair, precedes body):

```
visible fine skin texture with natural pores, fine lines, subtle asymmetries and texture irregularities, natural visible makeup with slightly uneven foundation blending rather than flawless coverage, faint natural blush, slight natural sheen rather than glossy or dewy retouched finish, no digital smoothing, no beauty filter, no AI-airbrushed look, skin completely free of artificial glare, shine or highlight blooms, matte-to-natural complexion
```

Paired lighting (soft light prevents specular blooms on skin):

```
soft diffused studio lighting without harsh reflections
```

Paired quality tail:

```
natural anatomy, high-end but unretouched commercial photography style, cinematic realism, clean white background, 4K quality, sharp focus on skin texture detail
```

Shorter in-skeleton form used inside the reference skeleton (slot-architecture.md section 7):
`visible fine skin texture with natural pores and subtle uneven tone, natural visible makeup with visible foundation texture rather than flawless coverage, [BLUSH/CONTOUR], slight natural sheen rather than glossy retouched finish, no digital smoothing, no beauty filter, no AI-airbrushed look, skin free of artificial glare or highlight blooms, matte-to-natural complexion`

## 3. Imperfection anchors (optional, add after the module)

Small, specific, believable marks make a face individual and make it repeatable across
generations. Examples from the recipe: `a few faint freckles, a small mole near the collarbone`.
Rule: choose 1-3 anchors, place them identically in the character bible, and never move them
between iterations. Anchors double as consistency markers when checking later renders.

## 4. Eye anti-glare clause (always on realism presets)

```
naturally muted catchlights, no oversized specular glare in the iris, eye color muted rather than glowing
```

Write eye shape + tilt + colour first, then this clause.

## 5. Hair finish and mature-structure clauses

- Hair: colour + undertone + length + style + **finish** + parting. Finish is what sells realism: "loose voluminous waves, round-barrel blowout finish".
- Adults: specify `defined (not soft-round) jawline and cheekbones, mature adult bone structure and facial proportions, longer facial thirds`, and in the negative tail `no babyface, no overly youthful rounded proportions`. This is a recurring correction point: bias toward mature, not cute.

## 6. Photoreal negative tail

```
no beauty filter, no digital smoothing, no airbrushing, no plastic skin, no glossy skin
```

Combine with the base tail `no text, no watermark, no logos, no frame borders` and the
framing exclusions from slot-architecture.md section 6.

## 7. Editorial variant and non-photoreal styles

`editorial-polished` keeps the photoreal base but allows refined glam: `flawless-but-natural skin with fine texture retained, soft dewy highlight on cheekbones, editorial beauty lighting with a soft key and gentle fill`. Use it only when the user asks for glamour; the anti-AI negatives stay except `no glossy skin`.

For `anime-2d`, `3d-stylized` and `game-concept`, drop the skin-texture / pores / foundation
clauses and the photoreal negatives; keep the consistency scaffold and the framing exclusions.

## 8. Diagnosis table: symptom to added clause

| Symptom in the render | Add or strengthen |
|---|---|
| Plastic, smooth skin | `visible fine skin texture with natural pores`, `no digital smoothing, no airbrushing, no plastic skin` |
| Shiny forehead / cheeks | `skin completely free of artificial glare, shine or highlight blooms, matte-to-natural complexion`; soften the lighting to `soft diffused studio lighting without harsh reflections` |
| Glowing or glassy eyes | the eye anti-glare clause (section 4) |
| Perfect symmetry, doll face | `subtle asymmetries and texture irregularities` plus 1-3 imperfection anchors |
| Flawless makeup | `natural visible makeup with slightly uneven foundation blending rather than flawless coverage` |
| Looks 16 when adult intended | mature-structure clause and the no-babyface negatives |
| Sitting, cropped feet, second person | the hard framing rules and exclusions in slot-architecture.md section 5 and 6 |
