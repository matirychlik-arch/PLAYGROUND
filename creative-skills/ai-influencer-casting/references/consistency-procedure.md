# Consistency procedure for an AI persona

Contents:
1. What to lock, what may vary
2. Persona bible template
3. Reference set (how many images, which angles, quality rules)
4. Using the persona in stills and video
5. Realism module (anti-AI look) and adult/original-character rules
6. Drift audit and repair
7. Training an identity model (when the tool supports it)

Sources: the identity-training photo guide and troubleshooting notes, the character-sheet principles, and the character consistency practices for reference images. Where the source is silent, this file says "practice" rather than claiming a tool feature.

## 1. What to lock, what may vary

Lock across every generation (write these once and restate them verbatim, or let the reference image carry them):
- Face geometry: head shape, jawline, cheekbones, nose shape, lips, eye shape, eye colour, eye spacing, brow shape, skin tone and undertone, marks (freckles, mole, scar) with their positions.
- Hair: colour, undertone, length, style, finish ("loose voluminous waves, round-barrel blowout finish"), parting. Hair accessory if any.
- Body: build, height, proportions, age band.
- The SIGNATURE feature (the one loud thing the persona is built around).
- Wardrobe anchors: 3-5 signature pieces with material, cut and colour, ONE metal family for jewelry, one deliberate imperfection (sleeves shoved to elbows, one strap slipping, loose strands).
- Persona sentence (attitude, cadence; accent only if approved) and the camera/light standard.

May vary per shot: expression, pose, action, location, props, time of day, framing. Change ONE of the locked items at a time and only on purpose (a new outfit for a new episode); everything previously established carries forward unchanged and the prompt restates it so nothing drifts silently.

## 2. Persona bible template (save next to the reference images)

```markdown
# Persona bible: [fictional name] v1
- Role / channel / audience: [host | mascot | ad creator | brand ambassador] | [niche] | [platform, language]
- Tier and style: [normal | freak | total] | [Retro | Sporty | Y2K | Theatre | Goth | Suits | Streetstyle | Casual]
- Traits (labels): gender / age / build / height / ethnicity / skin tone / hair style / hair colour / eye shape / eye colour / facial hair / features (<= 4) / distinctive (<= 2) / accessories (<= 3) / proportions (<= 2)
- Signature (one): [...]
- Face lock sentence: [one paragraph, face only]
- Hair lock sentence: [...]
- Body lock sentence: [...]
- Wardrobe anchors: [3-5 pieces] | metal: [silver | gold] | imperfection: [...]
- Persona sentence (voice): [one sentence, no energy words under the natural default]
- World: [locations, palette (one dominant, one secondary, at most one loud accent)]
- Light and camera standard: [neutral daylight, direction | phone-selfie look | casting-photo look]
- Do-nots: [list; includes "no text, no logos, no watermark", "not resembling any real person or existing character"]
- Seed(s) and generator: [numbers, tool, date]
- Reference files: sheet_v1.png (two panels), face_front.png, face_34L.png, face_34R.png, face_profile.png, body_front.png, + expression/lighting set
- Version log: v1 [date] created; v1.1 [date] new outfit for episode X (only wardrobe changed)
```

## 3. Reference set

- Start from the two-panel casting sheet (close-up portrait + full-body standing shot). A clean, well-lit sheet used directly as the FIRST reference image outperforms several casual photos.
- Derive a small reference set from it: a frontal head shot (primary identity anchor), a 3/4 view (dimension), a side profile (silhouette: hair, ear, jawline), and one full-body standing image. Two to three clear, well-lit references is the working minimum for a generator that takes image inputs.
- Identity-training tools want more: 5-20 face images, 8-12 is the sweet spot. Variety beats quantity:
  - Angles: front, 3/4 left, 3/4 right, slight up and slight down.
  - Lighting: indoor, outdoor, soft, harsh.
  - Expressions: neutral, smiling, talking.
  - Distances: head shot, head-and-shoulders, full body.
  - Quality: sharp, in focus, at least 1024 x 1024, JPEG or PNG; clear face, eyes visible; single person per image.
  - Avoid: group photos, heavy makeup not normally worn, costumes or cosplay, hats covering the face, the same pose repeated, sunglasses and heavy filters.
- Training fails when there are too few images (<5) or they are too uniform, when the face is heavily occluded (sunglasses, hats), when group photos confuse identity, or when the uploads are the wrong type (video instead of images). Fix by swapping in better images and retraining.
- For a generated persona, build the 8-12 set by generating variations from the sheet (different angles, light, expressions, distances) and keeping only those where the face matches the sheet; reject near-misses, they teach drift.

## 4. Using the persona

Stills (Nano Banana Pro or any image model with image inputs):
- Attach the sheet or the frontal reference first; add a second reference for a needed angle.
- Write the identity block once: `The same person as the reference image, identical face, hair, body and identity. Same outfit as the reference unless stated.` Then describe the ACTION and the setting. Do not re-describe the face in words; re-description competes with the reference.
- Outfit specificity when you do change clothes: materials, colours, distinctive details ("fitted olive-green cotton t-shirt, dark indigo slim jeans, white leather sneakers with red accents"), never "casual clothes".
- Two characters in one shot: reference each separately with distinct tags ("@Image1 as Character A, @Image2 as Character B") and give each a fixed one-line description repeated verbatim.

Video (KLING, Seedance 2, Cinema Studio, any image-to-video):
- Use a still of the persona as the start frame or reference image. The reference already carries the look, so describe action and camera only: wrong = "a woman with curly brown hair and green eyes wearing a red jacket walks through the park"; right = "she walks through the park, pausing to look up at the falling leaves; camera: slow tracking alongside".
- If features drift between shots, use the character sheet directly as the primary reference image for tighter anchoring.
- Restate the persona sentence verbatim in every clip prompt when speech or acting style matters (clips generated apart drift accents and mannerisms).
- Prompt pattern for a content series: "The persona [name] is in [location]. [Action, props]. [Expression]. Camera: [move]. Style: [look], 9:16 vertical."

Seed: where the tool exposes a seed, keep it with the prompt so the exact sheet can be reproduced and slightly modified; use fixed settings rather than randomization when you want an exact re-run. A seed alone does not hold identity across different scenes; the reference images do.

## 5. Realism module, adult and original-character rules

Photorealism means anti-retouch, never idealized. For a photoreal persona the realism module is mandatory:
`visible fine skin texture with natural pores, fine lines, subtle asymmetries and texture irregularities, natural visible makeup with slightly uneven foundation blending rather than flawless coverage, faint natural blush, slight natural sheen rather than glossy or dewy retouched finish, no digital smoothing, no beauty filter, no AI-airbrushed look, skin completely free of artificial glare, shine or highlight blooms, matte-to-natural complexion` plus optional imperfection anchors (`a few faint freckles, a small mole near the collarbone`). Lighting: `soft diffused studio lighting without harsh reflections`. Tail: `natural anatomy, high-end but unretouched commercial photography style, cinematic realism, clean white background, 4K quality, sharp focus on skin texture detail`. Eyes: `naturally muted catchlights, no oversized specular glare in the iris, eye color muted rather than glowing`.

Rules:
- Original characters only. Never replicate a recognizable real person or a copyrighted character; a celebrity or existing IP named by the user is a loose vibe at most, with a distinct original face. Keep the wording "identical original character on all views". Add: do not resemble any real celebrity or existing copyrighted character.
- Adults. The taxonomy offers only Adult, Mature and Senior ages. For an adult read, avoid babyface proportions: defined jaw and cheekbones, longer facial thirds, mature bone structure; add `no babyface, no overly youthful rounded proportions` to the negatives.
- Disclosure. An AI persona is a brand/character asset, not a customer. Do not present it as a real person with lived experience, and use the platform's AI-content label where required.

## 6. Drift audit and repair

After each batch compare against the sheet:
1. Face landmarks: head shape, jaw, nose, lips, eye shape and spacing, brow shape.
2. Skin tone and marks: tone, undertone, freckle/mole positions.
3. Hair: colour, length, style, finish, parting.
4. Body: build, height, proportions.
5. Signature feature present and the right size.
6. Wardrobe anchors, jewelry metal, accessories count.
7. Light and colour cast; no accidental stylization.
Repair, in this order: (a) re-attach the sheet or frontal reference as the FIRST image and shorten the prompt; (b) delete any face re-description from the prompt; (c) reduce competing instructions (one signature, <= 4 features); (d) crop the head from the sheet and add it as a second reference; (e) regenerate with the same settings and a new seed, keep only matches; (f) if a model keeps drifting on a specific angle, add that angle to the reference set, or switch the shot to a framing that hides it. Never "fix" drift by adding more adjectives about the face.

## 7. Training an identity model

When the tool supports training on a face (a personal ID or LoRA-style model): choose a variant by downstream use (still-image generation vs cinematic/video work), upload the 8-12 varied images, wait for training (minutes; a long job is normal), then pass the returned reference id with every generation. A trained identity is for faces you are authorized to use (your own, a consenting person, or a fully generated persona), never a real person without consent. For a persona already defined by a clean sheet and references, training is optional.
