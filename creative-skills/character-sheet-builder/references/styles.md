# Style presets (5)

Contents:
1. How presets plug into the slots
2. photoreal-unretouched (default)
3. editorial-polished
4. anime-2d
5. 3d-stylized
6. game-concept
7. Custom style recipe and choosing quickly

## 1. How presets plug into the slots

Each preset supplies three modules: **Realism/Render**, **Lighting**, **Quality Tail**.
They fill slots 10, 13 and 14 of the scaffold (slot-architecture.md). The composition clause,
the consistency wording ("identical original character on all views") and the negative tail
stay the same across presets. Default preset is `photoreal-unretouched`, the signature look.

## 2. photoreal-unretouched (default / signature)

- **Realism module (the anti-AI engine; this is the whole trick):**
  `visible fine skin texture with natural pores, fine lines, subtle asymmetries and texture irregularities, natural visible makeup with slightly uneven foundation blending rather than flawless coverage, faint natural blush, slight natural sheen rather than glossy or dewy retouched finish, no digital smoothing, no beauty filter, no AI-airbrushed look, skin completely free of artificial glare, shine or highlight blooms, matte-to-natural complexion`
  plus optional imperfection anchors: `a few faint freckles, a small mole near the collarbone`.
- **Lighting:** `soft diffused studio lighting without harsh reflections`.
- **Quality tail:** `natural anatomy, high-end but unretouched commercial photography style, cinematic realism, clean white background, 4K quality, sharp focus on skin texture detail`.

## 3. editorial-polished

Same photoreal base, but allow refined glam: `flawless-but-natural skin with fine texture retained, soft dewy highlight on cheekbones, editorial beauty lighting with a soft key and gentle fill`.
Quality tail: `high-end fashion editorial photography, magazine cover quality, cinematic realism, 4K`.

## 4. anime-2d

- **Render module:** `clean anime illustration, crisp lineart, cel-shaded flat color with soft gradient shadows, expressive large eyes with detailed iris highlights, consistent character model-sheet style`
- **Lighting:** `even flat lighting, soft ambient shading`
- **Quality tail:** `high-quality anime key visual, clean vector-like linework, sharp, 4K`
- Drop the skin-texture / pores clauses; they do not apply.

## 5. 3d-stylized (Pixar / DreamWorks feel)

- **Render module:** `stylized 3D character render, appealing exaggerated proportions, smooth subsurface-scattering skin, soft rounded features, detailed hair strands and cloth simulation`
- **Lighting:** `soft global illumination, three-point studio lighting, gentle rim light`
- **Quality tail:** `high-end 3D animation studio quality, octane/Unreal-style render, clean neutral background, 4K`

## 6. game-concept

- **Render module:** `painterly game concept art, semi-realistic rendering, orthographic model sheet, clear silhouette, material callouts implied through detail`
- **Lighting:** `neutral even concept-art lighting`
- **Quality tail:** `professional character concept art, artstation quality, sharp, 4K`

## 7. Custom style recipe and choosing quickly

If the user's style does not match a preset, build a custom render module in the same shape
(Render + Lighting + Quality tail) and keep the composition + consistency scaffold intact.

| The user wants | Preset |
|---|---|
| A believable person for ads, UGC, AI influencer, live-action look | photoreal-unretouched |
| Fashion / beauty / magazine look | editorial-polished |
| Anime or 2D cartoon | anime-2d |
| Animated-feature mascot or kids' content | 3d-stylized |
| Game, RPG, concept art, orthographic design | game-concept |

For video work, choose the preset that matches the medium of the final video, so the sheet and the clips share one look.
