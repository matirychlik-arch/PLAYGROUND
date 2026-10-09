# Consistency kit: reuse one character across images and video

Contents:
1. What the kit contains
2. Build procedure (bible, sheet, crops, anchor)
3. Per-tool recipes (Nano Banana Pro, KLING, Seedance 2, Higgsfield)
4. Real-person characters (photo-based identity)
5. Drift loop and repair prompts
6. Expanding the character (outfits, expressions, ages)

## 1. What the kit contains

Save these as a folder named after the character, so any tool can be fed the same inputs:

| File | Purpose |
|---|---|
| `<name>_bible.md` | the slot values as text; the single source of truth |
| `<name>_anchor.txt` | the 60-100 word identity paragraph reused verbatim in every prompt |
| `<name>_sheet.png` | the chosen full sheet (16:9) |
| `<name>_face.png` | tight face crop, square, from the sheet right panel |
| `<name>_body_front.png` | full-body front crop (head to toe, both feet visible) |
| `<name>_body_34.png`, `<name>_profile.png`, `<name>_back.png` | extra angles (turnaround sheets only) |
| `<name>_outfits/` | later outfit variants, one file each |

## 2. Build procedure

1. **Write the bible.** Fill every slot from slot-architecture.md with specific values: identity, face, eyes, eyebrows, hair (with finish), body, wardrobe head to toe, 1-3 imperfection anchors. Nothing generic.
2. **Generate the sheet.** Split-screen for a single hero look; turnaround when the character will be seen from several angles or in motion. Render 3-4 candidates; pick the one whose face you would recognise at a glance.
3. **Check the sheet** with the QA list in SKILL.md (standing, feet visible, one person, matching panels). Re-roll or repair rather than accepting a flawed base, because every later render inherits its flaws.
4. **Cut the crops** (face, body front, other angles) at full resolution. Do not upscale-then-crop. A clean face crop is the strongest identity reference you have.
5. **Write the anchor.** Compress the bible into one paragraph that names the unchanging identifiers (age band, skin tone, face shape and jaw, eye colour and shape, brow, hair colour + length + style, body type, the imperfection anchors) and the current outfit in one clause. Reuse it unchanged, in the same order, in every prompt.

Anchor template:

```
<Name>: <age band> <noun>, <skin tone>, <face shape> with <jaw> and <cheekbones>, <eye colour and shape>, <eyebrows>, <hair colour, length, style, finish>, <imperfection anchors>, <body type>. Outfit: <one-clause wardrobe>.
```

6. **Declare the reference roles** at the top of every prompt that uses attached images:

```
IMAGE REFERENCES: image 1 = <NAME> face reference (identity); image 2 = <NAME> full-body reference (outfit and proportions).
```

## 3. Per-tool recipes

**Nano Banana Pro (stills):** attach the face crop and the body crop, put the manifest line first, then the anchor, then the new scene. Add an identity-lock sentence: `Reproduce this exact person with a photographic identity match — same bone structure, eye shape, nose, lips, jawline, skin tone, hairline and hair texture as the reference. Do NOT beautify, do NOT average with other faces, do NOT restyle the face.` Describe only what changes (scene, pose, light). To change the outfit, restate the anchor with a new `Outfit:` clause and say the face and body stay identical.

**KLING (image-to-video):** use the full-body or waist-up still of the character in the new scene as the start frame, generated first with the image model from the sheet. Keep the prompt to plain action verbs for one subject, with the camera move in its own sentence. Repeat the outfit and hair in a short clause so the model does not reinvent them. If the version you use accepts multiple reference images, add the face crop as a second reference; check what your version supports.

**Seedance 2 (video, EN+ZH prompts):** attach the face crop and the body crop as reference images, name each in the prompt by its handle (image 1, image 2) in the same role-manifest style, and keep the anchor in the prompt. For multi-shot sequences repeat the anchor in every shot's description. Keep shot lengths short, because identity holds better over short clips; stitch in the edit.

**Higgsfield:** for an invented character, use the sheet and crops as image references in the image and video tools, and in Cinema Studio shots keep the same anchor text. For a real person with photos, train a persistent identity model (Soul) from 8-12 varied photos, then use it instead of the sheet (section 4).

**Premiere Pro / After Effects:** the sheet is a casting board for the editor: keep it in the project bin, and use the crops to compare against each generated shot while cutting. Fix small face drift between shots with consistent grade and cutaways, not by regenerating the whole scene.

**Figma / Illustrator / Photoshop:** lay out the final deliverable (the sheet as a PDF or board) with the bible text beside the images, for clients or teammates.

## 4. Real-person characters (photo-based identity)

When the character is a real person (Mati himself, or someone who consented) the identity
comes from photos, not from a sheet invented by the model:
- Collect **5-20 face photos; 8-12 is the sweet spot** (identity-model training minimum 5, maximum 20).
- Content: clear face, eyes visible, one person per photo, no heavy filters, no sunglasses.
- Variety raises identity capture: angles (front, 3/4 left, 3/4 right, slight up and down), lighting (indoor, outdoor, soft, harsh), expressions (neutral, smiling, talking), distances (head shot, head-and-shoulders, full body).
- Quality: sharp, in focus, at least 1024x1024, JPEG or PNG.
- Avoid: group photos, makeup not normally worn, costumes, hats covering the face, the same pose repeated.
- If an identity model fails to train, the usual causes are too few or too uniform photos, occlusion (sunglasses, hats), group photos, or uploading video instead of images. Swap in better photos and retrain.
- Without training, attach 2-3 of the best photos as references and use the identity-lock sentence from section 3 in every prompt.
- Do not use this route for celebrities or other people who have not consented; for those build an original character (principle 2).

## 5. Drift loop and repair prompts

Compare every output with `<name>_face.png` and the bible, in this order: face shape and jaw,
eyes, brows, hair colour and length, imperfection anchors, body type, outfit. If any item is
off:
1. Regenerate from the sheet and crops, not from the last output (copying a drifted output makes the drift permanent).
2. Add the failing attribute to the prompt in plain words (`jaw stays angular, eyes dark brown almond shape`).
3. If the problem is one attribute in an otherwise good frame, run a narrow edit:
   `Change ONLY <attribute> to <value>. Keep identity, face structure, hair, pose, body, clothing and background EXACTLY unchanged, pixel-faithful.`
4. After two failed attempts, re-roll the scene composition; the scene may be fighting the identity (profile views and extreme angles are the usual cause, so add the profile crop as a reference).

## 6. Expanding the character

- **New outfit:** copy the bible, change only the wardrobe slot, keep every other slot byte-identical (principle 4). Generate with the outfit-variations composition or a single full-body portrait with the face crop attached.
- **Expression range:** use the expression-sheet composition once; reuse the best expressions as references for dialogue shots.
- **Different age or hairstyle:** state the change explicitly and list what stays the same (face structure, eyes, anchors).
- **New angle needed:** generate that angle with the turnaround composition using the existing face crop as reference, then save it into the kit.
