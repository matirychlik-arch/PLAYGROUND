# Slot architecture

Contents:
1. Golden rules and non-negotiable principles
2. The scaffold (slots in exact order)
3. Slot table: every slot with allowed values and defaults
4. Slot notes
5. Composition presets (opening clauses) and hard framing rules
6. Negative tail
7. Reference skeleton (photoreal split-screen), ready to fill

Never freestyle a character-sheet prompt; fill the slots in order. Image models weight earlier
tokens more, so composition and identity go first and the quality tail goes last.

## 1. Golden rules and principles

Golden rules:
- **Consistency is the product.** Always state the character is *identical / the same original character* across every view. Physical description is written **once** and implicitly applies to all views.
- **One paragraph, comma-separated, ordered.** Image models weight earlier tokens more: composition and identity go first, quality tail last.
- **Specificity beats adjectives.** "cream white cropped wide-leg pants with eyelet floral embroidery and drawstring waist" is far better than "nice pants".
- **Head-to-toe wardrobe.** Top, layers, bottom, belt/sash, shoes, jewelry, bag. No gaps.
- **Consistent lighting + seamless background** are what make it read as a *sheet*, not a photo.

Non-negotiable principles (they override any brief and apply to every preset unless the user explicitly changes them):
1. **Photorealism means anti-retouch, never idealized.** "Realistic" is never a synonym for flawless, beauty-filtered, or glamorized. Real means visible pores, natural asymmetry, matte skin with no glare/shine, naturally-worn (slightly uneven) makeup, and zero AI-smoothing artifacts. If a photoreal preset is chosen, the anti-AI realism module (realism-engine.md) is mandatory, not optional.
2. **Original characters only.** Never replicate a recognizable real person's likeness or a copyrighted character/property. Reference images are for *style and mood inspiration*, not direct reproduction. Always describe an **original** character; if the user names a celebrity or existing IP, use it only as a loose vibe and build a distinct original face/identity. Keep the wording "identical **original** character on all views". (Exception: the user's own photo of themselves or a person who consented, used as an identity reference; that is a real-person identity lock, handled in consistency-kit.md, not a sheet invented from a celebrity.)
3. **Mature facial structure for adults.** When a character is meant to read as an adult, actively avoid babyface / youthful rounded proportions. Specify grown-up structure: defined (not soft-round) jaw and cheekbones, longer facial thirds, mature bone structure, adult proportions. This is a recurring correction point: bias toward mature, not cute.
4. **Consistency carries forward.** When iterating on an existing character, **every previously-established detail (face, hair, body, outfit, accessories, jewelry) carries forward unchanged** unless the user explicitly changes it. Change only what's requested; restate the rest so nothing silently drifts.

## 2. The scaffold (slots in exact order)

Bracketed slots are variable; unbracketed text is the reusable scaffold.

```
[COMPOSITION CLAUSE], identical original [subject] on all views,
pure white seamless studio background, professional character sheet presentation,
[IDENTITY: age + ethnicity/skin],
[FACE: face shape, jawline, cheekbones, nose, lips],
[EYES + anti-glare clause],
[EYEBROWS], [HAIR: color, tone, length, style, finish, parting], [HAIR ACCESSORY if any],
[REALISM MODULE — from the chosen preset],
[BODY: body type + proportions],
[WARDROBE: top → layers → bottom → belt/sash → shoes → jewelry → bag],
[LIGHTING MODULE — from the chosen preset],
[QUALITY TAIL — from the chosen preset],
[NEGATIVE TAIL]
```

## 3. Slot table

Source-derived values are the wording from the original recipe; "suggested" marks a default added
for convenience when the brief is silent.

| # | Slot | Allowed values | Default |
|---|---|---|---|
| 1 | COMPOSITION CLAUSE | split-screen, turnaround / model sheet, expression sheet, outfit variations (N outfits), triple panel (section 5) | split-screen |
| 2 | SUBJECT noun | female / male / non-binary character, creature, robot, stylized figure | taken from the brief; always prefixed `identical original` |
| 3 | PRESENTATION | `pure white seamless studio background, professional character sheet presentation`; for non-photoreal presets a clean neutral background | white seamless studio |
| 4 | IDENTITY | age band ("young woman in her early twenties"), skin tone, heritage if relevant; respectful and specific | required from brief; suggested: ask 1 question if absent |
| 5 | FACE | shape (oval / round / heart / square); jaw (soft / angular / delicate); cheekbones; nose; lips (shape + finish, e.g. "full lips, natural rosy-nude tint, soft matte-to-satin finish") | adults: defined jawline and cheekbones, mature bone structure (principle 3) |
| 6 | EYES | shape + tilt + color, then the anti-glare clause | photoreal: `naturally muted catchlights, no oversized specular glare in the iris, eye color muted rather than glowing` |
| 7 | EYEBROWS | shape, thickness, color, grooming ("softly arched, natural fullness, a shade darker than the hair") | suggested: natural, softly arched |
| 8 | HAIR | color + undertone + length + style + **finish** + parting (finish sells realism: "loose voluminous waves, round-barrel blowout finish") | required from brief |
| 9 | HAIR ACCESSORY | clip, band, pins, scarf, none | omit if none |
| 10 | REALISM / RENDER MODULE | one of the 5 style presets (styles.md) | `photoreal-unretouched` |
| 11 | BODY | body type + proportions ("slender athletic build with balanced proportions") | suggested: `balanced proportions` |
| 12 | WARDROBE | top, layers, bottom, belt/sash, shoes, jewelry, bag; name material, cut, color and one detail per item | required from brief; state `no bag` explicitly if none |
| 13 | LIGHTING MODULE | from the chosen preset | photoreal: `soft diffused studio lighting without harsh reflections` |
| 14 | QUALITY TAIL | from the chosen preset | photoreal: `natural anatomy, high-end but unretouched commercial photography style, cinematic realism, clean white background, 4K quality, sharp focus on skin texture detail` |
| 15 | NEGATIVE TAIL | section 6 | `no text, no watermark, no logos, no frame borders` + the situational items |

## 4. Slot notes

- **IDENTITY:** age band ("young woman in her early twenties"), skin tone, heritage if relevant. Be respectful and specific. Original character only, never a real person's likeness (principle 2).
- **FACE:** oval/round/heart/square; jaw (soft/angular/delicate); cheekbones; nose; lips (shape + finish). **For adult characters, enforce mature structure** (principle 3): defined jawline and cheekbones, mature adult bone structure and facial proportions, explicitly *not* a youthful/rounded babyface.
- **EYES:** shape + tilt + color, then **always** the anti-glare clause for realism presets: *"naturally muted catchlights, no oversized specular glare in the iris, eye color muted rather than glowing."*
- **HAIR:** color + undertone + length + style + **finish** ("loose voluminous waves, round-barrel blowout finish") + parting. Finish is what sells realism.
- **WARDROBE:** name material, cut, color, and one detail per item. Jewelry is small and specific ("thin gold bracelet, small delicate gold rings"). State "no bag" explicitly if none.

## 5. Composition presets (opening clauses)

Choose the opening clause. The default is **split-screen**.

- **split-screen** (default): `Split-screen character sheet composition, left side a full-body shot of the character standing upright in a neutral straight standing pose facing the camera with both feet flat on the ground and arms relaxed at the sides, full head-to-toe framing with the whole body and both feet visible, right side a tight close-up chest-up portrait of the same character,`
  - variants for the right side: `close-up face portrait`, `chest-up portrait`, `beauty close-up`.
  - **Hard framing rules (repeat these verbatim; this is what breaks most often):**
    - **Standing, always.** Left panel character is *standing*: never sitting, crouching, leaning, or cropped. Bake in: `standing full-body, head-to-toe, entire body and both feet in frame, not cropped, not sitting`.
    - **Close-up on the right, always.** Right panel is a tight crop (face or chest-up), never a second full body.
    - **Only the character.** Add to the Negative Tail every time: `single subject only, exactly one person, only the character in frame, no other people, no duplicate figures, no mannequin, no reflections, no props, no furniture, no background objects, empty seamless studio`.
- **turnaround / model sheet:** `Character turnaround model sheet, four consistent full-body views in a row — front view, 3/4 view, side profile, and back view, evenly spaced,`
- **expression sheet:** `Character expression sheet, one full-body reference on the left and a grid of head-and-shoulders portraits on the right showing varied expressions (neutral, smiling, serious, surprised),`
- **outfit variations:** `Character wardrobe sheet, the same character shown full-body in [N] different outfits side by side,`
- **triple panel:** `Three-panel character sheet — full body, chest-up portrait, and detail close-up of face and accessories,`

Aspect ratio by composition: split-screen / turnaround / expression / triple go in **16:9** (or 3:2). A single portrait goes in 2:3 or 3:4. Ask the generator for the exact ratio; do not crop afterwards, because crops cut feet.

## 6. Negative tail

Always end with (adjust the situational items):

```
no text, no watermark, no logos, no frame borders
```

Add when relevant: `no bag, no branding, no extra characters, no background props, no harsh shadows, no distorted anatomy, no extra fingers`.

**Always for split-screen sheets** (prevents the recurring breakage): `single subject only, exactly one person, only the character in frame, no other people, no duplicate figures, no mannequin, no reflections, no props, no furniture, no background objects, empty seamless studio, left panel standing full-body head-to-toe not cropped not sitting, right panel tight close-up not full body`.

For adult characters add: `no babyface, no overly youthful rounded proportions`. For photoreal add: `no beauty filter, no digital smoothing, no airbrushing, no plastic skin, no glossy skin`. Always (original-character safety): the character is original; do not resemble any real celebrity or existing copyrighted character.

If the generator has a separate negative-prompt field, put the hard exclusions there; otherwise keep them inline at the end of the prompt.

## 7. Reference skeleton (photoreal split-screen)

Use as a fill-in template when starting from scratch:

> Split-screen character sheet composition, left side a full-body shot of the character standing upright in a neutral straight standing pose facing the camera with both feet flat on the ground and arms relaxed at the sides, full head-to-toe framing with the whole body and both feet visible, right side a tight close-up chest-up portrait of the same character, identical original female character on both sides, single subject only exactly one person with only the character in frame, pure white seamless studio background, professional character sheet presentation, [AGE] with [SKIN TONE], [FACE SHAPE] with [JAW], [CHEEKBONES], [NOSE], [LIPS + finish], [EYE color/shape] with naturally muted catchlights and no artificial glare, [EYEBROWS], [HAIR color/tone/length/style/finish], visible fine skin texture with natural pores and subtle uneven tone, natural visible makeup with visible foundation texture rather than flawless coverage, [BLUSH/CONTOUR], slight natural sheen rather than glossy retouched finish, no digital smoothing, no beauty filter, no AI-airbrushed look, skin free of artificial glare or highlight blooms, matte-to-natural complexion, [BODY TYPE] with balanced proportions, wearing [TOP], [LAYERS], [BOTTOM], [BELT/SASH], [SHOES], [JEWELRY], [BAG or "no bag"], natural anatomy, high-end but unretouched commercial photography style, soft diffused studio lighting without harsh reflections, cinematic realism, clean white background, 4K quality, sharp focus on skin texture detail, single subject only, exactly one person, only the character in frame, no other people, no duplicate figures, no mannequin, no props, no furniture, no background objects, left panel standing full-body head-to-toe not cropped not sitting, right panel tight close-up not full body, no text, no watermark, no logos, no frame borders.

Swap "female" for the character's noun. Every `[...]` must be filled with a specific value
before the prompt ships.
