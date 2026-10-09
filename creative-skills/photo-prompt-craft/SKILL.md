---
name: photo-prompt-craft
description: General-purpose photographic prompt writing and refinement for any image generator. Builds a structured prompt (subject, preservation, scene, light, camera, look, text, negatives) with precise lighting, lens, surface, Kelvin and grading vocabulary, a negative-prompt bank, text-in-image rules, and a critique-and-rewrite loop that fixes a generated image against its brief. Use whenever the user wants a better image prompt, says a result looks flat, plastic or stocky, has warped text or hands, wants a photographer style described without names, or asks how to prompt a light or lens, even without naming the skill. Trigger on - prompt do zdjęcia, popraw prompt, słownik fotograficzny, oświetlenie, obiektyw, negative prompt, wygląda plastikowo, krzywy tekst na obrazie, napis na zdjęciu, styl fotografa, analiza wygenerowanego obrazu. For a product photo that must stay on-model use product-shot-recipes; for video scene scripts use cinematic-prompt-builder.
---

# Photo Prompt Craft

Write photographic prompts the way a photographer briefs a shoot: say what is in front of the camera, where the light comes from, which lens sees it, and what the print should feel like. Then judge the result against the brief and rewrite only what failed. The vocabulary is tool-agnostic; the structure works in Nano Banana Pro, Midjourney-style tools, Flux, GPT image models and any other generator that takes a text prompt.

## When to use / when not

Use when:
- The user has an idea ("zdjęcie perfum w stylu luksusowym") and needs a full prompt.
- A generated image looks flat, plastic, over-smooth, stock-like, badly lit, or has warped text, hands or faces, and the prompt needs a rewrite.
- The user wants a specific light, lens, film look, surface, palette or a photographer-like style translated into concrete words.
- The user needs negative prompts, text-in-image handling, or a critique of a result against a brief.

Do not use when:
- The subject is a real product photo that must stay pixel-faithful in label, logo and proportions: use product-shot-recipes (it contains the recipe library and identity rules; this skill supplies the vocabulary behind it).
- The request is a multi-shot video script or storyboard: use cinematic-prompt-builder.
- The request is graphic design (layouts, logos, type systems) with no photographic element: work in Figma or Illustrator.

## Inputs to collect (ask only for what is missing; sensible defaults otherwise)

1. Subject and purpose: what is in the picture and where it will be used (ad, banner, Pinterest, e-commerce, Reel cover).
2. Reference image or description of anything that must stay exact (product, face, logo). Default: none.
3. Aspect ratio. Default by use: Shopify or catalog 1:1, Instagram feed 4:5, Story or Reel 9:16, Pinterest 2:3, web hero 16:9, editorial print 3:4.
4. Mood or look in plain words ("ciepło", "premium", "surowo"). Default: derive from the subject and use.
5. People in frame or not. Default: no people unless asked. People trigger the anti-uncanny negatives and anatomy lines.
6. On-image text: none, exact strings, or "I will add it later". Default: none.
7. Target generator and whether it has a negative-prompt field. Default: single prompt with an `[AVOID]` block at the end.
8. For a refinement: the original prompt and the generated image (or a description of what is wrong).

Ask at most three questions in one message, only for gaps that change the picture. Do not ask about lens or Kelvin; choose them.

## Workflow

### A. Write a prompt

1. State the job in one sentence (subject, use, feeling). Everything else must serve it.
2. Fill the eight blocks below in order. Use specific vocabulary from `references/vocabulary.md`; replace every vague word ("good lighting", "nice background", "high quality") with a direction, a surface or a number.
3. Choose style by descriptors, not names. Look up 2 to 3 compatible entries in `references/photographers.md`, then write only the visual result (palette, light, surface, staging, register). Do not mix opposed sensibilities (surreal with corporate-clean, dark moody with bright lifestyle).
4. Add the negatives that match the situation from `references/negatives.md`, combined into one block without repeated phrases.
5. Handle text with the three-case rule in `references/typography.md`.
6. Run the pre-flight checklist (below), then output the prompt in the Output format.

### The eight blocks

1. Subject: what it is, material and finish, size relationship, what the viewer should notice first. Concrete nouns, no adjectives that mean nothing ("beautiful").
2. Preservation: only if something must stay exact. Name each fixed element: shape, proportions, colors, logo placement, label text (copy, do not translate), face likeness. Add "straighten a tilted reference". Skip the block when nothing is fixed, because empty rules waste attention.
3. Scene: location, surface, background, 3 to 5 grounding objects, time of day, human presence ("no people, traces of presence" is a valid choice).
4. Light: direction, quality, color temperature in Kelvin, shadow behavior. Name a motivated source (window, practical lamp, strobe, skylight). Example: "large softbox 45° camera-left, 5000K, soft falloff with contact shadow only at base".
5. Camera: focal length, aperture, depth of field, angle, framing and placement. Example: "85mm, f/2.8, shallow depth with creamy bokeh, eye-level three-quarter, product on right third".
6. Look: palette (2 to 3 named tones), surface and texture words, atmosphere, grading or film feel, style descriptors, quality markers ("tack-sharp commercial photography", "no AI artifacts").
7. Text: one of the three cases. Exact strings go in quotes; overlay space is described as part of the scene.
8. Negatives: one `[AVOID]` block.

Order matters for readability and for generators that weight the beginning and end of a prompt: subject first, preservation second, negatives last. Keep each block to one to three sentences.

### Pre-flight checklist for any prompt

- Every lighting line has direction, quality and a Kelvin value.
- Lens line has focal length and aperture.
- Palette names colors, not moods.
- No banned vague words ("good lighting", "nice background", "beautiful product", "professional photo", "high quality", "modern style").
- Fixed elements are named and the rule says "never invent, translate, or substitute".
- Text handled by exactly one of the three cases.
- No photographer, publication, retailer or competitor names in the prompt.
- Negatives combined once; anti-uncanny present if people are in frame; anti-text-warp present if any label is visible.

### B. Refinement loop (critique a generated image, rewrite the prompt)

1. Write the brief as a checklist (the eight blocks).
2. Audit the image line by line with the critique table in `references/refinement-pass.md`. Judge only what you can see.
3. Pick the single weakest area (lighting flat, plastic surface, warped text, anatomy, composition, palette drift, stock feel, AI sheen, half-applied style, flat color band).
4. Rewrite: keep every passing line, replace the failing line with the matching fix language from the refinement reference, and add one negative for the observed failure. In a tool with image editing, instead send "Refine the previous image. Keep composition, subject, framing and overall scene identical. Only change: ..." with the last result attached.
5. Regenerate, re-audit, and stop after two refinements per image. Deliver the best version and name the remaining limitation. Text defects that survive two passes move to design software.
6. For sets (carousel, ad pack), audit the set first (palette, light direction, surface, narrative), then fix only the image that breaks the system.

## Output format

Deliver this structure. The prompt is a single fenced block, ready to paste.

````markdown
## Prompt (<aspect ratio>, <generator or "any">)
```text
[SUBJECT] ...
[PRESERVATION] ... (omit when nothing must stay exact)
[SCENE] ...
[LIGHT] ...
[CAMERA] ...
[LOOK] ...
[TEXT] ... (omit for Case 3)
[AVOID] ...
```
Why these choices: <2-3 bullets: the light, the lens and the look tied to the use>
Settings: <aspect ratio, resolution, number of images>
If it goes wrong: <the most likely failure and the one-line fix from the refinement bank>
````

For a refinement, output instead:

````markdown
## Critique
<table: brief line | seen | verdict>
Weakest area: <one category>
## Revised prompt
```text
<full prompt with the changed line marked by a leading ">>" comment line above it>
```
Changed: <one line>
````

If the generator does not understand bracketed section labels, flatten the blocks into one paragraph in the same order and keep the [AVOID] text as a final "Avoid:" sentence.

## Worked example

Brief (Polish, from the user): "Butelka oleju rzepakowego na drewnianym blacie w kuchni, ciepło, na post na Instagramie. Etykieta musi zostać taka sama."

Resolved: image for Instagram feed, aspect ratio 4:5, warm lifestyle, product photo supplied (label must stay exact), no people, no added text.

```text
[SUBJECT] A glass bottle of cold-pressed rapeseed oil with a cream paper label and a dark green cap, standing upright and centered on the right third of the frame, golden oil visible through the glass.
[PRESERVATION] Use the supplied image as the authoritative product reference. Preserve the exact bottle silhouette, proportions, cap, colors, logo placement and every printed label element exactly as in the reference; never invent, translate, or substitute words or characters, and keep unreadable glyphs as faithful shapes. If the reference was shot from a tilted or elevated angle, straighten the bottle and compose it level.
[SCENE] A sunlit home kitchen counter in early morning: raw oak wood grain surface, a linen cloth folded at the left, a small ceramic bowl with a few sprigs of dill, a halved lemon, soft out-of-focus window behind. No people, traces of presence only.
[LIGHT] Soft window light from camera-left at 45°, large diffused source, 4500K mixed window and warm ambient, gentle highlight rolloff on the glass, soft long shadow to the right, contact shadow at the base, golden glow through the oil.
[CAMERA] Shot on 50mm, aperture f/4, medium depth of field with the label tack-sharp and the background softly blurred, eye-level with a slight hero low angle, 4:5 framing with the bottle on the right third and open space on the left.
[LOOK] Palette: warm oak, cream, olive green, soft gold. Realistic wood grain and linen weave, condensation-free dry glass, subtle dust catching light. Warm editorial lifestyle photography, natural color, faithful product colors, tack-sharp commercial photography, no AI artifacts.
[AVOID] no warped product label text, no garbled letters, no fake brand names, no doubled labels, no AI artifacts, no plastic look, no oversaturated HDR, no harsh on-camera flash, no stale stock photography aesthetic, no over-staged feeling, no random unrelated brand logos, no watermarks.
```

Why these choices: window light at 4500K gives a warm, believable morning source; 50mm at f/4 keeps the label sharp while separating the background; the right-third placement leaves breathing room without a reserved empty zone; the palette is named in colors so the generator does not drift.

If the label comes out slightly wrong, the fix is the "Warped text" language from the refinement bank, and after two attempts the real label is composited in Photoshop.

## Tool adapters

- Nano Banana Pro: strong at photoreal scenes and at rendering text. Attach reference images for anything that must stay exact; give exact on-image strings in quotes. It handles the bracketed blocks well. Use the Case 1 typography block when you want words in the image.
- KLING and Seedance 2 (image-to-video): write the still first with this skill, then animate it. For the motion prompt keep one subject, plain action verbs and the camera move in its own sentence; the light and lens lines carry over as the look. Both are poor at exact text, so never rely on them to animate readable small print. Seedance 2 accepts English and Chinese prompts.
- Higgsfield Cinema Studio: use the Camera and Light lines as the look; its camera-move controls handle motion, so keep camera moves out of the still prompt.
- Midjourney-style and other tools without reference or text strength: shorten to one paragraph (subject, scene, light, camera, look), move negatives to the tool's exclusion parameter, and skip the preservation block.
- Premiere Pro and After Effects: not generators; use them after generation for grading to the chosen look, adding text as live type, and compositing real labels over a generated product.
- Figma, Illustrator, Photoshop: the right place for exact copy and layout. Generate the photograph with the Case 2 or Case 3 text rule, then set type there.

## QA checklist

- [ ] The eight blocks are present in order (preservation and text only when needed).
- [ ] Light has direction, quality and Kelvin; camera has focal length and aperture.
- [ ] No vague quality words; palette uses named colors.
- [ ] Style is written as descriptors; no photographer or brand names in the prompt.
- [ ] Negatives combined in one block and matched to the situation (people, labels, ad/lifestyle, restyle).
- [ ] Text handled by exactly one of the three cases; exact strings quoted; diacritics copied.
- [ ] Refinement fixes only one weakest area and keeps passing lines unchanged.
- [ ] Output delivered in the fenced template with a failure fix line.

## References

- `references/vocabulary.md`: read when writing the light, camera, look and palette lines; it holds the lighting directions and qualities, Kelvin table, lenses and apertures, surfaces, shadows, palette and atmosphere phrases, scenario lighting setups, camera angles, film looks and grading terms.
- `references/photographers.md`: read when the user asks for a style or when choosing the look; lookup table by genre, which combinations work, picks by use case and examples of translating names into descriptors.
- `references/negatives.md`: read when building the `[AVOID]` block; universal, uncanny, text-warp, stock-feel, aesthetic-mixing, flat-band and format-specific lists.
- `references/refinement-pass.md`: read when an image fails the brief; critique table, defect categories, fix language per defect, budget and set-level rules.
- `references/typography.md`: read when any text appears in or around the image; the three-case rule and exact-string rules.
- Sibling skill `product-shot-recipes`: use when the subject is a real product photo that must keep label, logo and proportions, or when a ready recipe (hero shot, splash, spin, carousel card) fits.
