---
name: character-sheet-builder
description: Build a consistent original character for image and video generation - a slot-based character sheet prompt (split-screen, turnaround, expression, outfit or triple-panel sheet) with the anti-AI unretouched realism engine and 5 style presets (photoreal-unretouched, editorial-polished, anime-2d, 3d-stylized, game-concept), plus a consistency kit procedure for reusing the sheet as reference in Nano Banana Pro, KLING, Seedance 2 and Higgsfield. Use this even if the user never says "skill" whenever the same person or mascot must appear in many shots, reels or ads. Trigger on - karta postaci, arkusz postaci, character sheet, turnaround postaci, spójna postać, ta sama postać w różnych ujęciach, konsekwentny bohater, postać do serii, AI influencer, mascot, model sheet, referencja postaci, żeby twarz się nie zmieniała, twarz mi pływa między generacjami, postać do wideo. For a thumbnail with the character use thumbnail-design after this; for product-only visuals use product-shot-recipes.
---

# Character Sheet Builder

Turn a character brief into an internally consistent character sheet prompt, then turn the
chosen sheet into a reusable kit (crops, anchor text, reference roles) that keeps the same
character recognisable across stills and video in any tool.

## When to use / when not

Use when:
- The user needs the same invented character (influencer, mascot, hero, narrator) in many images or videos.
- The user asks for a character sheet, model sheet, turnaround, expression sheet or outfit sheet.
- A character's face or outfit keeps drifting between generations and needs a locked reference.
- The user wants an existing character iterated (new outfit, new hairstyle) without losing the rest.

Do not use when:
- The user wants one-off portraits or a single hero image with no recurrence (write a normal photo prompt).
- The user wants to copy a celebrity or a copyrighted character: build an original character with a loose vibe instead (say so in one line).
- The task is the thumbnail itself (use thumbnail-design after the sheet exists), or product-only visuals (use product-shot-recipes).

## Inputs to collect (ask only for what is missing; sensible defaults otherwise)

Ask at most 1-2 questions that genuinely block assembly (usually style and who/what the character is).

| Input | Default if missing |
|---|---|
| Character: who, age band, skin tone, vibe | required; ask once |
| Style preset | `photoreal-unretouched` |
| Composition | `split-screen` (left full-body standing, right close-up) |
| Wardrobe head to toe | propose one specific outfit and state it; never leave gaps |
| Hair and face details | propose specific values (with hair finish); mark them as proposed |
| Existing character or reference to preserve | none; if iterating, carry every established detail forward |
| Real-person photos as identity source | none; if given, use the photo route in the consistency kit |
| Downstream use (stills, KLING, Seedance 2, Higgsfield) | stills + video; produce the kit either way |
| Generate now or prompt only | prompt only; generate only on an explicit ask |

## Workflow

1. **Read the brief.** Extract identity, wardrobe, style. If a reference character was pasted, preserve every physical detail verbatim. If iterating, restate all established details and change only what was requested.
2. **Pick the style preset** (references/styles.md). It decides the render module, lighting and quality tail. Photoreal presets always include the realism engine (references/realism-engine.md).
3. **Pick the composition preset** (references/slot-architecture.md section 5). It decides the opening clause and the aspect ratio (16:9 or 3:2 for multi-view sheets; 2:3 or 3:4 for a single portrait).
4. **Fill the slots in order** (scaffold below; full table with allowed values and defaults in references/slot-architecture.md). Every detail specific: material, colour, cut, finish. For adults enforce mature facial structure.
5. **Append the negative tail** (framing exclusions for split-screen, photoreal and adult clauses).
6. **Write the character bible and anchor** (consistency kit step 1 and 5, references/consistency-kit.md).
7. **Generate if asked** at the right ratio, render 3-4 candidates, pick one, then run the QA checklist below. Offer one round of targeted fixes (tighten wardrobe, more skin texture, swap right panel to a face close-up).
8. **Build the kit** from the chosen sheet: crops, anchor, manifest line, per-tool recipe for the tools the user named.

### The scaffold (fill in this exact order; image models weight earlier tokens more)

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

### Principles that override any brief

- Photorealism means anti-retouch, never idealized: visible pores, natural asymmetry, matte skin, unevenly worn makeup. Not optional on photoreal presets.
- Original characters only: never a recognisable real person's likeness or a copyrighted character; keep the words "identical original character on all views".
- Adults get mature facial structure (defined jaw and cheekbones), never a babyface.
- Consistency carries forward: change only what was requested and restate the rest.

### The 5 style presets (details in references/styles.md)

`photoreal-unretouched` (default), `editorial-polished`, `anime-2d`, `3d-stylized`, `game-concept`.

### Hard framing rules for split-screen (what breaks most often)

Left panel: standing, head to toe, both feet visible, not cropped, not sitting. Right panel: tight close-up, never a second full body. Exactly one person, empty seamless studio. Put the exclusion string from references/slot-architecture.md section 6 in every split-screen prompt.

## Output format

Deliver three blocks. The prompt block is a single paragraph, comma-separated, ready to paste.

````
## Character bible: <Name>
| Slot | Value |
|---|---|
| Style / composition / ratio | photoreal-unretouched / split-screen / 16:9 |
| Identity | ... |
| Face | ... |
| Eyes | ... |
| Eyebrows | ... |
| Hair (with finish) | ... |
| Imperfection anchors | ... |
| Body | ... |
| Wardrobe | top / layers / bottom / belt / shoes / jewelry / bag |

## Sheet prompt
```
<one paragraph, scaffold order, every [slot] filled, negative tail last>
```

## Consistency kit
- Anchor (60-100 words, reuse verbatim): `<anchor paragraph>`
- Reference manifest: `IMAGE REFERENCES: image 1 = <NAME> face reference (identity); image 2 = <NAME> full-body reference (outfit and proportions).`
- Crops to cut from the chosen sheet: face (square), body front, [3/4, profile, back]
- Tool recipe for: <the tools the user named>
````

Worked example (photoreal split-screen, original character):

```
Split-screen character sheet composition, left side a full-body shot of the character standing upright in a neutral straight standing pose facing the camera with both feet flat on the ground and arms relaxed at the sides, full head-to-toe framing with the whole body and both feet visible, right side a tight close-up chest-up portrait of the same character, identical original female character on both sides, single subject only exactly one person with only the character in frame, pure white seamless studio background, professional character sheet presentation, woman in her early thirties with warm olive skin, oval face with a defined angular jawline, high defined cheekbones, straight nose with a slightly rounded tip, full lips with a natural rosy-nude tint and soft matte-to-satin finish, almond-shaped dark brown eyes with a slight upward tilt and naturally muted catchlights and no artificial glare, softly arched natural brows a shade darker than the hair, dark chestnut hair with warm brown undertones, shoulder-length loose waves with a round-barrel blowout finish and a soft side parting, visible fine skin texture with natural pores, fine lines, subtle asymmetries and texture irregularities, a few faint freckles across the nose, natural visible makeup with slightly uneven foundation blending rather than flawless coverage, faint natural blush, slight natural sheen rather than glossy or dewy retouched finish, no digital smoothing, no beauty filter, no AI-airbrushed look, skin completely free of artificial glare, shine or highlight blooms, matte-to-natural complexion, mature adult bone structure and facial proportions, slender build with balanced proportions, wearing a fitted ivory ribbed cotton tank top, an oversized camel wool-blend blazer with notch lapels, high-waisted charcoal straight-leg trousers with a pressed crease, a thin black leather belt with a small brushed-silver buckle, white minimal leather sneakers, a thin gold chain necklace and small gold hoop earrings, no bag, natural anatomy, high-end but unretouched commercial photography style, soft diffused studio lighting without harsh reflections, cinematic realism, clean white background, 4K quality, sharp focus on skin texture detail, single subject only, exactly one person, only the character in frame, no other people, no duplicate figures, no mannequin, no reflections, no props, no furniture, no background objects, empty seamless studio, left panel standing full-body head-to-toe not cropped not sitting, right panel tight close-up not full body, no babyface, no overly youthful rounded proportions, no beauty filter, no digital smoothing, no airbrushing, no plastic skin, no glossy skin, no text, no watermark, no logos, no frame borders, original character not resembling any real celebrity or existing copyrighted character
```

## Tool adapters

- **Nano Banana Pro:** best fit for the sheet (follows long structured prompts, 16:9 sheets) and for later scenes: attach the face and body crops, put the manifest line first, add the identity-lock sentence from references/consistency-kit.md, describe only what changes. Render at the highest resolution.
- **KLING:** image-to-video with a start frame generated from the sheet; one subject, plain action verbs, camera move in a separate sentence, outfit and hair repeated in a short clause. Not a good tool for making the sheet itself.
- **Seedance 2:** attach the face and body crops as reference images, name them by handle in the prompt, repeat the anchor in every shot; EN+ZH prompts accepted. Short clips hold identity best.
- **Higgsfield (Cinema Studio and image tools):** use the sheet and crops as image references; for a real person with photos, train a persistent identity model from 8-12 varied photos instead (details in the kit).
- **Premiere Pro / After Effects:** keep the sheet and crops in the bin as a continuity board; fix small drift with cutaways and consistent grade.
- **Figma / Illustrator / Photoshop:** lay out a clean presentation board (sheet + bible text) for clients; also the place to cut crops.

## QA checklist

- [ ] Every slot filled with a specific value; no `[...]` left; head-to-toe wardrobe with no gaps (bag stated, or `no bag`).
- [ ] The words "identical original" appear; description written once and applies to all views.
- [ ] Photoreal: realism module verbatim, eye anti-glare clause, photoreal negatives present.
- [ ] Adults: mature structure clause and no-babyface negatives.
- [ ] Split-screen: standing full body with feet visible on the left, tight close-up on the right, one person only.
- [ ] Rendered sheet: face matches across panels, no cropped feet, no extra figures, no text or logos.
- [ ] Kit saved: bible, anchor, face and body crops, manifest line, recipe for the named tools.
- [ ] Original character: no recognisable celebrity or copyrighted likeness.

## References

- references/slot-architecture.md: read at step 3-5 for the full slot table (allowed values, defaults), composition clauses, negative tail and the fill-in skeleton.
- references/realism-engine.md: read for any photoreal sheet, or when skin looks plastic, glossy or too symmetrical (includes the symptom table).
- references/styles.md: read at step 2 for the exact render, lighting and quality-tail text of the 5 presets and how to build a custom one.
- references/consistency-kit.md: read at step 6-8 and whenever the character must be reused in Nano Banana Pro, KLING, Seedance 2 or Higgsfield, or when the character is a real person with photos.
